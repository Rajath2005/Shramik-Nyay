from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from audio_pacer import (
    BIAS_SCORE,
    PRISMA_SEED_WORDS,
    PrismaRealtimeStreamer,
    sanitize_bias_words,
)
from eshram_mock_db import lookup_eshram_uan
from evon_legal_engine import EvonLegalEngine, FormAClaimSlots, missing_fields
from form_a_pdf_generator import compile_form_a
from locality_vocab import locality_terms_in
from live_guard import LiveCallBlocked, LiveCreditGuard
from language_support import (
    LANGUAGE_NAMES,
    MOCK_TRANSCRIPTS,
    SUPPORTED_LANGUAGES,
    followup_for,
    match_consent_intent,
    prisma_language_code,
    resolve_language,
    validate_language,
)
from samadhan_payload import build_samadhan_mapped_draft
from timbre_tts_client import synthesize_timbre_audio

load_dotenv(Path(__file__).with_name(".env"))
CLAIMS_DIR = Path(__file__).with_name("claims")
REPLAY_FIXTURE = Path(__file__).with_name("fixtures") / "replay_recorded_call.pcm"
MAX_CONSENT_AUDIO_BYTES = 1_000_000

app = FastAPI(title="Shramik-Nyay API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": os.getenv("SHRAMIK_MODE", "MOCK_REPLAY")}


@app.get("/api/demo-profile/{uan}")
async def demo_profile(uan: str) -> dict:
    profile = lookup_eshram_uan(uan)
    return {"found": bool(profile), **({"profile": profile} if profile else {})}


@app.get("/api/claims/{claim_id}/form-a.pdf")
async def download_form_a(claim_id: str):
    path = CLAIMS_DIR / Path(claim_id).name / "form-a-claim.pdf"
    if not path.exists():
        raise HTTPException(404, "Claim not found")
    return FileResponse(path, media_type="application/pdf", filename="form-a-claim.pdf")


@app.get("/api/claims/{claim_id}/form-a.json")
async def download_samadhan_mapped_draft_json(claim_id: str):
    path = CLAIMS_DIR / Path(claim_id).name / "samadhan-mapped-draft.json"
    if not path.exists():
        raise HTTPException(404, "Claim not found")
    return FileResponse(path, media_type="application/json", filename="samadhan-mapped-draft.json")


class Session:
    """One worker conversation. Every outbound message is a typed JSON event the UI can render."""

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws
        self.mode = os.getenv("SHRAMIK_MODE", "MOCK_REPLAY").upper()
        self.live_guard = LiveCreditGuard()
        self.key = os.getenv("GNANI_API_KEY", "")
        base_url = (os.getenv("GNANI_API_BASE_URL") or "https://api.vachana.ai").rstrip("/")
        endpoint = os.getenv(
            "EVON_ENDPOINT_URL",
            f"{base_url}/llm/evon-v3.3/chat/completions",
        )
        self.engine = EvonLegalEngine(endpoint, self.key, self.mode)
        self.slots = FormAClaimSlots()
        self.audit: dict | None = None
        self.streamer: PrismaRealtimeStreamer | None = None
        self.stt_task: asyncio.Task | None = None
        self.replay_task: asyncio.Task | None = None
        self.frames = 0
        self._send_lock = asyncio.Lock()
        self._turn_lock = asyncio.Lock()
        self._transcript_tasks: set[asyncio.Task] = set()
        self._pending_bias_request_id: str | None = None
        self._pending_bias_words: list[str] = []
        self.language_preference = "auto"
        self.detected_language: str | None = None
        self.last_utterance = ""
        self.awaiting_consent = False
        self.consent_state = "not_requested"
        self.consent_audio_buffer = bytearray()
        self.consent_audio_overflowed = False
        self.voice_consent_audio: bytes | None = None

    @property
    def active_language(self) -> str:
        return resolve_language(
            self.language_preference,
            detected=self.detected_language,
            text=self.last_utterance,
        )

    async def send(self, event: dict) -> None:
        async with self._send_lock:
            await self.ws.send_json(event)

    async def send_audio(self, audio: bytes) -> None:
        async with self._send_lock:
            await self.ws.send_bytes(audio)

    async def send_pipeline_latency(self, stage: str, started_at: float) -> None:
        await self.send({
            "type": "pipeline_latency",
            "stage": stage,
            "latency_ms": round((time.perf_counter() - started_at) * 1000, 1),
            "source": "live" if self.mode == "LIVE" else "mock",
        })

    async def send_language_status(self) -> None:
        effective = self.detected_language if self.language_preference == "auto" else self.language_preference
        await self.send({
            "type": "language_status",
            "language_preference": self.language_preference,
            "effective_language": effective,
            "language_name": LANGUAGE_NAMES[effective] if effective else LANGUAGE_NAMES["auto"],
            "prisma_language_code": prisma_language_code(self.language_preference),
        })

    async def send_credit_usage(self) -> None:
        await self.send({
            "type": "credit_usage",
            "usage": {
                provider: {"used": usage.used, "limit": usage.limit}
                for provider, usage in self.live_guard.snapshot().items()
            },
        })

    async def _live_call(self, provider: str, operation):
        if self.mode != "LIVE":
            return await operation()
        self.live_guard.reserve(provider)
        await self.send_credit_usage()
        try:
            result = await operation()
        except LiveCallBlocked:
            raise
        except Exception:
            if self.live_guard.record_failure(provider):
                self.mode = "MOCK_REPLAY"
                self.engine.mode = self.mode
                await self.send({
                    "type": "notice",
                    "message": f"{provider.title()} failed twice. Switched to MOCK_REPLAY so the demo can continue.",
                })
            raise
        else:
            if isinstance(result, dict) and result.get("live_call_failed"):
                if self.live_guard.record_failure(provider):
                    self.mode = "MOCK_REPLAY"
                    self.engine.mode = self.mode
                    await self.send({
                        "type": "notice",
                        "message": f"{provider.title()} failed twice. Switched to MOCK_REPLAY so the demo can continue.",
                    })
            else:
                self.live_guard.record_success(provider)
            return result

    async def run(self) -> None:
        await self.send({"type": "session_started", "mode": self.mode})
        await self.send_credit_usage()
        try:
            while True:
                message = await self.ws.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if message.get("bytes") is not None:
                    await self.on_audio(message["bytes"])
                elif message.get("text"):
                    try:
                        await self.on_command(message["text"])
                    except Exception as error:               # one bad command must not kill the call
                        await self.send({"type": "error", "message": str(error)})
        finally:
            tasks = [task for task in self._transcript_tasks]
            if self.stt_task:
                tasks.append(self.stt_task)
            if self.replay_task:
                tasks.append(self.replay_task)
            for task in tasks:
                task.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def on_audio(self, chunk: bytes) -> None:
        self.frames += 1
        if self.awaiting_consent and not self.consent_audio_overflowed:
            if len(self.consent_audio_buffer) + len(chunk) <= MAX_CONSENT_AUDIO_BYTES:
                self.consent_audio_buffer.extend(chunk)
            else:
                self.consent_audio_buffer.clear()
                self.consent_audio_overflowed = True
        if self.streamer:
            self.streamer.push_pcm_bytes(chunk)
        if self.frames % 8 == 0:                              # throttle UI telemetry
            await self.send({"type": "prisma_telemetry", "frame_bytes": 1024, "cadence_ms": 64,
                             "sample_rate_hz": 8000, "vad_threshold": 0.72, "source": "live"})

    async def on_command(self, text: str) -> None:
        if text.startswith("transcript:"):                    # legacy typed fallback
            return await self.on_utterance(text.removeprefix("transcript:"))
        try:
            cmd = json.loads(text)
        except json.JSONDecodeError:
            cmd = {"type": text}
        kind = cmd.get("type")
        if kind == "demo":
            await self.run_demo()
        elif kind == "replay_recorded_call":
            await self.start_recorded_call_replay()
        elif kind == "start_mic":
            await self.start_stt()
        elif kind == "set_language":
            await self.set_language(cmd.get("language"))
        elif kind == "stop_mic":
            if self.streamer:
                await self.streamer.commit_and_close()
        elif kind == "utterance":
            await self.on_utterance(cmd.get("text", ""))
        elif kind == "uan":
            await self.apply_uan(str(cmd.get("value", "")))
        elif kind == "confirm":
            await self.finalize()

    # ---- speech in -------------------------------------------------------
    async def set_language(self, language: object) -> None:
        preference = validate_language(language)
        if self.streamer and self.streamer.running:
            raise ValueError("Stop the microphone before changing the language.")
        self.language_preference = preference
        self.detected_language = None
        self.last_utterance = ""
        await self.send_language_status()

    async def start_stt(self) -> None:
        if self.mode != "LIVE":
            return await self.send({"type": "notice", "message": "MOCK mode: type or run the replay."})
        if self.streamer and (self.streamer.running or self.streamer.connecting):
            return await self.send({"type": "notice", "message": "The microphone stream is already active."})
        try:
            self.live_guard.reserve("prisma")
        except LiveCallBlocked as error:
            return await self.send({"type": "error", "message": str(error)})
        await self.send_credit_usage()
        self.streamer = PrismaRealtimeStreamer(
            self.key,
            self.on_prisma_event,
            lang_code=prisma_language_code(self.language_preference),
            seed_words=PRISMA_SEED_WORDS,
        )
        self.streamer.connecting = True
        self.stt_task = asyncio.create_task(self._run_prisma_stream(self.streamer))

    async def start_recorded_call_replay(self) -> None:
        if self.mode != "LIVE":
            return await self.send({
                "type": "notice",
                "message": "Recorded-call replay is available only in LIVE mode.",
            })
        if self.replay_task and not self.replay_task.done():
            return await self.send({"type": "notice", "message": "The recorded call is already replaying."})
        if self.streamer and (self.streamer.running or self.streamer.connecting):
            return await self.send({"type": "notice", "message": "Stop the active microphone stream first."})
        if not REPLAY_FIXTURE.is_file():
            raise RuntimeError(f"Recorded-call fixture is missing: {REPLAY_FIXTURE.name}")
        try:
            self.live_guard.reserve("prisma")
        except LiveCallBlocked as error:
            return await self.send({"type": "error", "message": str(error)})
        await self.send_credit_usage()
        self.streamer = PrismaRealtimeStreamer(
            self.key,
            self.on_prisma_event,
            lang_code=prisma_language_code(self.language_preference),
            seed_words=PRISMA_SEED_WORDS,
        )
        self.streamer.connecting = True
        self.stt_task = asyncio.create_task(self._run_prisma_stream(self.streamer))
        self.replay_task = asyncio.create_task(self._stream_recorded_call(self.streamer))

    async def _stream_recorded_call(self, streamer: PrismaRealtimeStreamer) -> None:
        try:
            await asyncio.wait_for(streamer.connected.wait(), timeout=10.0)
            pcm = await asyncio.to_thread(REPLAY_FIXTURE.read_bytes)
            if len(pcm) == 0 or len(pcm) % 2:
                raise RuntimeError("Recorded-call fixture must contain non-empty 16-bit PCM.")
            streamer.push_pcm_bytes(pcm)
            await self.send({
                "type": "replay_started",
                "sample_rate_hz": 8000,
                "channels": 1,
                "frame_bytes": 1024,
                "cadence_ms": 64,
                "source": "live",
                "synthetic": True,
            })
            await self.send({
                "type": "prisma_telemetry",
                "frame_bytes": 1024,
                "cadence_ms": 64,
                "sample_rate_hz": 8000,
                "vad_threshold": 0.72,
                "source": "live",
            })
            await streamer.commit_and_close()
            await self.send({"type": "replay_finished", "source": "live", "synthetic": True})
        except asyncio.CancelledError:
            raise
        except Exception as error:
            await self.send({"type": "error", "message": f"Recorded-call replay failed: {error}"})
            await self.send({"type": "replay_finished", "source": "live", "synthetic": True, "failed": True})
        finally:
            self.replay_task = None

    async def _run_prisma_stream(self, streamer: PrismaRealtimeStreamer) -> None:
        try:
            await streamer.connect_and_run()
        except asyncio.CancelledError:
            raise
        except Exception as error:
            if self.live_guard.record_failure("prisma"):
                self.mode = "MOCK_REPLAY"
                self.engine.mode = self.mode
                await self.send({
                    "type": "notice",
                    "message": "Prisma failed twice. Switched to MOCK_REPLAY so the demo can continue.",
                })
            await self.send({"type": "error", "message": f"Prisma stream failed: {error}"})

    async def on_prisma_event(self, event: dict) -> None:
        detected = event.get("detected_language_code")
        if detected in SUPPORTED_LANGUAGES:
            self.detected_language = detected
        is_consent_transcript = event.get("type") == "transcript" and bool(event.get("text"))
        consent_window = self.awaiting_consent if is_consent_transcript else False
        consent_audio = None
        if consent_window:
            if not self.consent_audio_overflowed and self.consent_audio_buffer:
                consent_audio = bytes(self.consent_audio_buffer)
            self.consent_audio_buffer.clear()
            self.consent_audio_overflowed = False
        outbound_event = dict(event)
        if event.get("type") == "settings_updated":
            config = event.get("config")
            bias_count = config.get("bias_word_count") if isinstance(config, dict) else None
            bias_score = config.get("bias_score") if isinstance(config, dict) else None
            if (
                self._pending_bias_request_id
                and bias_count == len(self._pending_bias_words)
                and bias_score == BIAS_SCORE
            ):
                outbound_event["request_id"] = self._pending_bias_request_id
                outbound_event["confirmed_words"] = self._pending_bias_words
                self._pending_bias_request_id = None
                self._pending_bias_words = []
        await self.send({
            **outbound_event,
            "type": f"prisma_{event.get('type')}",
            "language_preference": self.language_preference,
            "effective_language": self.active_language,
        })
        if is_consent_transcript:
            latency_ms = event.get("segment_latency_ms")
            if isinstance(latency_ms, (int, float)) and not isinstance(latency_ms, bool):
                await self.send({
                    "type": "pipeline_latency",
                    "stage": "prisma_segment",
                    "latency_ms": round(float(latency_ms), 1),
                    "source": "live",
                })
            task = asyncio.create_task(
                self._process_prisma_transcript(
                    event["text"],
                    detected_language=detected,
                    consent_window=consent_window,
                    consent_audio=consent_audio,
                )
            )
            self._transcript_tasks.add(task)
            task.add_done_callback(self._transcript_tasks.discard)

    async def _process_prisma_transcript(
        self,
        text: str,
        *,
        detected_language: str | None = None,
        consent_window: bool = False,
        consent_audio: bytes | None = None,
    ) -> None:
        try:
            await self.on_utterance(
                text,
                detected_language=detected_language,
                consent_window=consent_window,
                consent_audio=consent_audio,
            )
        except Exception as error:
            await self.send({"type": "error", "message": str(error)})

    # ---- understanding ---------------------------------------------------
    async def on_utterance(
        self,
        text: str,
        *,
        detected_language: str | None = None,
        consent_window: bool | None = None,
        consent_audio: bytes | None = None,
    ) -> None:
        async with self._turn_lock:
            should_process_consent = (
                self.awaiting_consent if consent_window is None else consent_window
            )
            if should_process_consent:
                await self._process_consent_response(text, consent_audio)
                return
            self.last_utterance = text
            target_language = resolve_language(
                self.language_preference,
                detected=detected_language or self.detected_language,
                text=text,
            )
            if self.language_preference == "auto":
                self.detected_language = target_language
            await self.send_language_status()
            await self._boost_locality_words(locality_terms_in(text))
            started_at = time.perf_counter()
            result = await self._live_call(
                "evon",
                lambda: self.engine.stage_a_extract_slots(text, self.slots, target_language),
            )
            await self.send_pipeline_latency("evon_stage_a", started_at)
            self.slots = FormAClaimSlots.model_validate(result["updated_slots"])
            await self.send({"type": "evon_stage_a", "slots": self.slots.model_dump(),
                             "missing_fields": result["missing_fields"],
                             "followup": result["followup_question_spoken"]})
            if not result["missing_fields"]:
                await self.audit_and_readback()

    async def _process_consent_response(self, text: str, consent_audio: bytes | None) -> None:
        intent = match_consent_intent(text)
        self.consent_audio_buffer.clear()
        self.consent_audio_overflowed = False
        if intent == "yes":
            self.consent_state = "yes"
            self.voice_consent_audio = consent_audio if consent_audio else None
        elif intent == "no":
            self.consent_state = "no"
            self.voice_consent_audio = None
        elif self.consent_state != "yes":
            self.consent_state = "unrecognized"
            self.voice_consent_audio = None
        await self.send({
            "type": "consent_status",
            "state": self.consent_state,
            "voice_consent_recorded": bool(self.voice_consent_audio),
        })

    async def apply_uan(self, uan: str) -> None:
        profile = lookup_eshram_uan(uan)
        if not profile:
            return await self.send({"type": "uan_result", "found": False})
        async with self._turn_lock:
            self.slots = self.slots.model_copy(update={
                "worker_name": profile["worker_name"], "eshram_uan": "".join(c for c in uan if c.isdigit()),
                "worksite_locality_and_sphere": self.slots.worksite_locality_and_sphere or profile["current_service_address"]})
            await self.send({"type": "uan_result", "found": True, "worker_name": profile["worker_name"]})
            await self._boost_locality_words(profile["local_bias_words"])
            missing = missing_fields(self.slots)
            next_question = followup_for(missing[0], self.active_language) if missing else ""
            await self.send({"type": "evon_stage_a", "slots": self.slots.model_dump(),
                             "missing_fields": missing,
                             "followup": next_question})

    async def _boost_locality_words(self, words: list[str]) -> None:
        if not self.streamer or not (self.streamer.running or self.streamer.connecting):
            return
        clean_words = sanitize_bias_words(words)
        if not clean_words:
            return

        request_id = uuid.uuid4().hex
        self._pending_bias_request_id = request_id
        self._pending_bias_words = clean_words
        await self.send({
            "type": "bias_boost_triggered",
            "request_id": request_id,
            "words": clean_words,
        })
        try:
            await self.streamer.boost_locality_vocabulary(clean_words)
        except Exception:
            if self._pending_bias_request_id == request_id:
                self._pending_bias_request_id = None
                self._pending_bias_words = []
            await self.send({
                "type": "bias_boost_failed",
                "request_id": request_id,
            })
            raise

    # ---- audit and consent ----------------------------------------------
    async def audit_and_readback(self) -> None:
        self.awaiting_consent = False
        self.consent_state = "not_requested"
        self.voice_consent_audio = None
        self.consent_audio_buffer.clear()
        self.consent_audio_overflowed = False
        target_language = self.active_language
        started_at = time.perf_counter()
        out = await self._live_call(
            "evon",
            lambda: self.engine.stage_b_statutory_audit_and_draft(self.slots, target_language),
        )
        await self.send_pipeline_latency("evon_stage_b", started_at)
        self.audit = out["result"]
        await self.send({
            "type": "evon_stage_b_complete",
            "stage": "B",
            "thinking_trace": out["thinking_trace"],
            "enable_thinking": out["enable_thinking"],
            **self.audit,
        })
        script = self.audit["timbre_v3_readback_script"]
        await self.send({"type": "timbre_audio", "script": script})
        self.awaiting_consent = True
        self.consent_state = "awaiting"
        await self.send({
            "type": "consent_status",
            "state": self.consent_state,
            "voice_consent_recorded": False,
        })
        if self.mode == "LIVE":
            try:
                started_at = time.perf_counter()

                async def report_first_audio_chunk() -> None:
                    await self.send_pipeline_latency("timbre_first_audio_chunk", started_at)

                audio = await self._live_call(
                    "timbre",
                    lambda: synthesize_timbre_audio(
                        script,
                        self.key,
                        target_language,
                        on_first_audio_chunk=report_first_audio_chunk,
                    ),
                )
                await self.send_audio(audio)
                await self.send({"type": "timbre_audio_ready"})
            except Exception as error:
                await self.send({"type": "timbre_audio_unavailable", "message": str(error)})

    async def finalize(self) -> None:
        if not self.audit:
            return await self.send({"type": "error", "message": "No claim draft is ready yet."})
        if not self.awaiting_consent or self.consent_state != "yes":
            return await self.send({
                "type": "error",
                "message": "An affirmative response to the read-back is required before preparing the draft.",
            })
        claim_id = uuid.uuid4().hex[:12]
        await asyncio.to_thread(
            compile_form_a,
            self.slots,
            self.audit,
            CLAIMS_DIR / claim_id,
            self.voice_consent_audio,
            language=self.active_language,
        )
        profile = lookup_eshram_uan(self.slots.eshram_uan or "")
        payload = build_samadhan_mapped_draft(self.slots, self.audit, profile)
        payload_path = CLAIMS_DIR / claim_id / "samadhan-mapped-draft.json"
        payload_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
        self.voice_consent_audio = None
        await self.send({"type": "claim_ready", "claim_id": claim_id,
                         "pdf_url": f"/api/claims/{claim_id}/form-a.pdf",
                         "json_url": f"/api/claims/{claim_id}/form-a.json"})
        self.awaiting_consent = False

    async def run_demo(self) -> None:
        if self.mode != "MOCK_REPLAY":
            await self.send({"type": "notice", "message": "Sample replay is available only in MOCK_REPLAY mode."})
            return
        self.slots = FormAClaimSlots()
        self.audit = None
        self.frames = 0
        self.detected_language = resolve_language(self.language_preference)
        self.last_utterance = MOCK_TRANSCRIPTS[self.detected_language]
        await self.send({"type": "session_started", "mode": self.mode})
        await self.send_language_status()
        await self.send({
            "type": "bias_boost_triggered",
            "words": {
                "hi-IN": ["Peenya", "Thekedar", "Dihadi"],
                "kn-IN": ["ಪೀನ್ಯಾ", "ಗುತ್ತಿಗೆದಾರ", "ಕೂಲಿ"],
                "en-IN": ["Peenya", "contractor", "wages"],
            }[self.detected_language],
        })
        await self.send({
            "type": "prisma_telemetry",
            "frame_bytes": 1024,
            "cadence_ms": 64,
            "sample_rate_hz": 8000,
            "vad_threshold": 0.72,
            "latency_ms": 318,
            "source": "mock",
            "waveform": [
                0.12, 0.18, 0.24, 0.42, 0.68, 0.38, 0.2, 0.33, 0.58, 0.82,
                0.54, 0.31, 0.18, 0.27, 0.49, 0.73, 0.46, 0.25, 0.39, 0.62,
                0.88, 0.61, 0.34, 0.2, 0.31, 0.55, 0.76, 0.43,
            ],
        })
        await self.send({
            "type": "prisma_transcript",
            "text": self.last_utterance,
            "detected_language_code": self.detected_language,
            "effective_language": self.detected_language,
            "latency": 318,
            "source": "mock",
        })
        await self.apply_uan("100492837465")
        self.slots = self.slots.model_copy(update={
            "worksite_locality_and_sphere": "Peenya Industrial Area, Bengaluru",
            "contractor_name_and_phone": "Mohan Thekedar (synthetic demo)",
            "principal_employer_name": "ABC Infrastructure (synthetic demo)",
            "wage_period_start": "2026-09-01", "wage_period_end": "2026-09-30", "days_worked": 18,
            "agreed_daily_wage_inr": 700, "advance_received_inr": 2000,
            "grievance_category": "unpaid_wages"})
        await self.send({"type": "evon_stage_a", "slots": self.slots.model_dump(), "missing_fields": [], "followup": ""})
        await self.audit_and_readback()


@app.websocket("/ws/session")
async def session_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        await Session(websocket).run()
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

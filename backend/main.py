from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from audio_pacer import PrismaRealtimeStreamer
from eshram_mock_db import lookup_eshram_uan
from evon_legal_engine import EvonLegalEngine, FormAClaimSlots, missing_fields
from form_a_pdf_generator import compile_form_a
from language_support import (
    LANGUAGE_NAMES,
    MOCK_TRANSCRIPTS,
    SUPPORTED_LANGUAGES,
    followup_for,
    prisma_language_code,
    resolve_language,
    validate_language,
)
from timbre_tts_client import synthesize_timbre_audio

load_dotenv(Path(__file__).with_name(".env"))
CLAIMS_DIR = Path(__file__).with_name("claims")

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
async def download_form_a_json(claim_id: str):
    path = CLAIMS_DIR / Path(claim_id).name / "form-a-claim.json"
    if not path.exists():
        raise HTTPException(404, "Claim not found")
    return FileResponse(path, media_type="application/json", filename="form-a-claim.json")


class Session:
    """One worker conversation. Every outbound message is a typed JSON event the UI can render."""

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws
        self.mode = os.getenv("SHRAMIK_MODE", "MOCK_REPLAY").upper()
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
        self.frames = 0
        self.language_preference = "auto"
        self.detected_language: str | None = None
        self.last_utterance = ""

    @property
    def active_language(self) -> str:
        return resolve_language(
            self.language_preference,
            detected=self.detected_language,
            text=self.last_utterance,
        )

    async def send(self, event: dict) -> None:
        await self.ws.send_json(event)

    async def send_language_status(self) -> None:
        effective = self.detected_language if self.language_preference == "auto" else self.language_preference
        await self.send({
            "type": "language_status",
            "language_preference": self.language_preference,
            "effective_language": effective,
            "language_name": LANGUAGE_NAMES[effective] if effective else LANGUAGE_NAMES["auto"],
            "prisma_language_code": prisma_language_code(self.language_preference),
        })

    async def run(self) -> None:
        await self.send({"type": "session_started", "mode": self.mode})
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
            if self.stt_task:
                self.stt_task.cancel()

    async def on_audio(self, chunk: bytes) -> None:
        self.frames += 1
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
        self.streamer = PrismaRealtimeStreamer(
            self.key,
            self.on_prisma_event,
            lang_code=prisma_language_code(self.language_preference),
            seed_words=["Thekedar", "Mistry", "Dihadi", "Muster", "Samadhan", "Advance"],
        )
        self.stt_task = asyncio.create_task(self.streamer.connect_and_run())

    async def on_prisma_event(self, event: dict) -> None:
        detected = event.get("detected_language_code")
        if detected in SUPPORTED_LANGUAGES:
            self.detected_language = detected
        await self.send({
            **event,
            "type": f"prisma_{event.get('type')}",
            "language_preference": self.language_preference,
            "effective_language": self.active_language,
        })
        if event.get("type") == "transcript" and event.get("text"):
            await self.on_utterance(event["text"], detected_language=detected)

    # ---- understanding ---------------------------------------------------
    async def on_utterance(self, text: str, *, detected_language: str | None = None) -> None:
        self.last_utterance = text
        target_language = resolve_language(
            self.language_preference,
            detected=detected_language or self.detected_language,
            text=text,
        )
        if self.language_preference == "auto":
            self.detected_language = target_language
        await self.send_language_status()
        result = await self.engine.stage_a_extract_slots(text, self.slots, target_language)
        self.slots = FormAClaimSlots.model_validate(result["updated_slots"])
        await self.send({"type": "evon_stage_a", "slots": self.slots.model_dump(),
                         "missing_fields": result["missing_fields"],
                         "followup": result["followup_question_spoken"]})
        if not result["missing_fields"]:
            await self.audit_and_readback()

    async def apply_uan(self, uan: str) -> None:
        profile = lookup_eshram_uan(uan)
        if not profile:
            return await self.send({"type": "uan_result", "found": False})
        self.slots = self.slots.model_copy(update={
            "worker_name": profile["worker_name"], "eshram_uan": "".join(c for c in uan if c.isdigit()),
            "worksite_locality_and_sphere": self.slots.worksite_locality_and_sphere or profile["current_service_address"]})
        await self.send({"type": "uan_result", "found": True, "worker_name": profile["worker_name"]})
        words = profile["local_bias_words"]
        if self.streamer:
            words = await self.streamer.boost_locality_vocabulary(words)
        await self.send({"type": "bias_boost_triggered", "words": words})
        missing = missing_fields(self.slots)
        next_question = followup_for(missing[0], self.active_language) if missing else ""
        await self.send({"type": "evon_stage_a", "slots": self.slots.model_dump(),
                         "missing_fields": missing,
                         "followup": next_question})

    # ---- audit and consent ----------------------------------------------
    async def audit_and_readback(self) -> None:
        target_language = self.active_language
        out = await self.engine.stage_b_statutory_audit_and_draft(self.slots, target_language)
        self.audit = out["result"]
        await self.send({"type": "evon_stage_b_complete", "thinking_trace": out["thinking_trace"], **self.audit})
        script = self.audit["timbre_v3_readback_script"]
        await self.send({"type": "timbre_audio", "script": script})
        if self.mode == "LIVE":
            try:
                audio = await synthesize_timbre_audio(script, self.key, target_language)
                await self.ws.send_bytes(audio)
                await self.send({"type": "timbre_audio_ready"})
            except Exception as error:
                await self.send({"type": "timbre_audio_unavailable", "message": str(error)})

    async def finalize(self) -> None:
        if not self.audit:
            return await self.send({"type": "error", "message": "Nothing to file yet."})
        claim_id = uuid.uuid4().hex[:12]
        await asyncio.to_thread(compile_form_a, self.slots, self.audit, CLAIMS_DIR / claim_id)
        await self.send({"type": "claim_ready", "claim_id": claim_id,
                         "pdf_url": f"/api/claims/{claim_id}/form-a.pdf",
                         "json_url": f"/api/claims/{claim_id}/form-a.json"})

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

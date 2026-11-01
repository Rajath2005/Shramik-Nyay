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
from evon_legal_engine import EvonLegalEngine, FormAClaimSlots, FOLLOWUPS_HI, missing_fields
from form_a_pdf_generator import compile_form_a

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


class Session:
    """One worker conversation. Every outbound message is a typed JSON event the UI can render."""

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws
        self.mode = os.getenv("SHRAMIK_MODE", "MOCK_REPLAY").upper()
        self.key = os.getenv("GNANI_API_KEY", "")
        self.engine = EvonLegalEngine(os.getenv("EVON_ENDPOINT_URL", ""), self.key, self.mode)
        self.slots = FormAClaimSlots()
        self.audit: dict | None = None
        self.streamer: PrismaRealtimeStreamer | None = None
        self.stt_task: asyncio.Task | None = None
        self.frames = 0

    async def send(self, event: dict) -> None:
        await self.ws.send_json(event)

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
            await self.send({"type": "prisma_telemetry", "frame_bytes": 1024, "cadence_ms": 64})

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
    async def start_stt(self) -> None:
        if self.mode != "LIVE":
            return await self.send({"type": "notice", "message": "MOCK mode: type or run the replay."})
        self.streamer = PrismaRealtimeStreamer(
            self.key, self.on_prisma_event, seed_words=["Thekedar", "Mistry", "Dihadi", "Muster", "Samadhan", "Advance"])
        self.stt_task = asyncio.create_task(self.streamer.connect_and_run())

    async def on_prisma_event(self, event: dict) -> None:
        await self.send({**event, "type": f"prisma_{event.get('type')}"})
        if event.get("type") == "transcript" and event.get("text"):
            await self.on_utterance(event["text"])

    # ---- understanding ---------------------------------------------------
    async def on_utterance(self, text: str) -> None:
        result = await self.engine.stage_a_extract_slots(text, self.slots)
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
        await self.send({"type": "evon_stage_a", "slots": self.slots.model_dump(),
                         "missing_fields": missing,
                         "followup": FOLLOWUPS_HI.get(missing[0], "") if missing else ""})

    # ---- audit and consent ----------------------------------------------
    async def audit_and_readback(self) -> None:
        out = await self.engine.stage_b_statutory_audit_and_draft(self.slots)
        self.audit = out["result"]
        await self.send({"type": "evon_stage_b_complete", "thinking_trace": out["thinking_trace"], **self.audit})
        await self.send({"type": "timbre_audio", "script": self.audit["timbre_v3_readback_script"]})

    async def finalize(self) -> None:
        if not self.audit:
            return await self.send({"type": "error", "message": "Nothing to file yet."})
        claim_id = uuid.uuid4().hex[:12]
        await asyncio.to_thread(compile_form_a, self.slots, self.audit, CLAIMS_DIR / claim_id)
        await self.send({"type": "claim_ready", "claim_id": claim_id,
                         "pdf_url": f"/api/claims/{claim_id}/form-a.pdf"})

    async def run_demo(self) -> None:
        await self.apply_uan("100492837465")
        self.slots = self.slots.model_copy(update={
            "contractor_name_and_phone": "Ramesh Thekedar, 98xxxxxx01", "principal_employer_name": "ABC Infrastructure",
            "wage_period_start": "2026-09-01", "wage_period_end": "2026-09-30", "days_worked": 26,
            "agreed_daily_wage_inr": 650, "advance_received_inr": 0, "grievance_category": "unpaid_wages"})
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

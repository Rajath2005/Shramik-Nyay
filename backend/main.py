from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from audio_pacer import PrismaRealtimeStreamer
from eshram_mock_db import lookup_eshram_uan
from evon_legal_engine import EvonLegalEngine, FormAClaimSlots

load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI(title="Shramik-Nyay API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": os.getenv("SHRAMIK_MODE", "MOCK_REPLAY")}


@app.get("/api/demo-profile/{uan}")
async def demo_profile(uan: str) -> dict:
    profile = lookup_eshram_uan(uan)
    if not profile:
        return {"found": False}
    return {"found": True, "profile": profile}


@app.websocket("/ws/session")
async def session_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    mode = os.getenv("SHRAMIK_MODE", "MOCK_REPLAY")
    engine = EvonLegalEngine(
        os.getenv("EVON_ENDPOINT_URL", ""),
        os.getenv("GNANI_API_KEY", ""),
        mode,
    )
    slots = FormAClaimSlots()
    try:
        await websocket.send_json({"type": "session_started", "mode": mode})
        while True:
            message = await websocket.receive()
            if message.get("bytes") is not None:
                await websocket.send_json({
                    "type": "prisma_telemetry",
                    "frame_bytes": len(message["bytes"]),
                    "cadence_ms": 64,
                })
                continue
            text = message.get("text", "")
            if text == "demo":
                profile = lookup_eshram_uan("100492837465")
                slots = slots.model_copy(update={
                    "worker_name": profile["worker_name"],
                    "eshram_uan": "100492837465",
                    "worksite_locality_and_sphere": profile["current_service_address"],
                    "agreed_daily_wage_inr": 650,
                    "days_worked": 26,
                })
                await websocket.send_json({"type": "bias_boost_triggered", "words": profile["local_bias_words"]})
                await websocket.send_json({"type": "evon_stage_a", "slots": slots.model_dump()})
                audit = await engine.stage_b_statutory_audit_and_draft(slots)
                await websocket.send_json({"type": "evon_stage_b_complete", **audit["result"]})
                await websocket.send_json({"type": "timbre_audio", "script": audit["result"]["timbre_v3_readback_script"]})
            elif text.startswith("transcript:"):
                result = await engine.stage_a_extract_slots(text.removeprefix("transcript:"), slots)
                slots = FormAClaimSlots.model_validate(result["updated_slots"])
                await websocket.send_json({"type": "evon_stage_a", **result})
    except WebSocketDisconnect:
        return
    except Exception as error:
        await websocket.send_json({"type": "error", "message": str(error)})


if __name__ == "__main__":
    import uvicorn

    asyncio.run(uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000)).serve())

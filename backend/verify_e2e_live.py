from __future__ import annotations

import asyncio
import json
import os
import wave
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from websockets.asyncio.client import connect as websocket_connect

from audio_pacer import PRISMA_WS_URL
from evon_legal_engine import EvonLegalEngine, FormAClaimSlots, REQUIRED
from main import Session
from timbre_tts_client import synthesize_timbre_audio

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

TRANSCRIPT = (
    "मेरा नाम रमेश कुमार वर्मा है, ई-श्रम नंबर 100492837465, पीन्या बेंगलुरु में "
    "एबीसी इंफ्रास्ट्रक्चर की साइट पर मोहन ठेकेदार के नीचे 1 सितंबर 2026 से "
    "30 सितंबर 2026 में 18 दिन काम किया, 700 दिहाड़ी तय थी, सिर्फ 2000 एडवांस मिला"
)


class ProbeSocket:
    def __init__(self) -> None:
        self.events: list[dict] = []
        self.audio: list[bytes] = []
        self.commands = iter((
            json.dumps({"type": "utterance", "text": TRANSCRIPT}, ensure_ascii=False),
            json.dumps({"type": "utterance", "text": "हाँ, मैं सहमत हूँ"}, ensure_ascii=False),
            json.dumps({"type": "confirm"}),
            "",
        ))

    async def send_json(self, event: dict) -> None:
        self.events.append(event)

    async def send_bytes(self, audio: bytes) -> None:
        self.audio.append(audio)

    async def receive(self) -> dict:
        command = next(self.commands)
        if not command:
            return {"type": "websocket.disconnect"}
        return {"type": "websocket.receive", "text": command}


async def check_prisma(wav_bytes: bytes) -> None:
    with wave.open(BytesIO(wav_bytes), "rb") as wav:
        assert wav.getframerate() == 8000 and wav.getnchannels() == 1
        pcm = wav.readframes(wav.getnframes())
    pcm += b"\x00" * 8192
    headers = {
        "x-api-key-id": os.environ["GNANI_API_KEY"].strip(),
        "x-model": "prisma-v3.0",
        "lang_code": "indic-auto",
        "x-sample-rate": "8000",
        "x-format": "transcribe",
        "itn_native_numerals": "false",
        "x-vad-threshold": "0.72",
        "x-min-speech-ms": "200",
        "x-min-silence-ms": "700",
        "x-min-segment-ms": "150",
        "x-max-speech-s": "30",
        "x-bias-list": json.dumps(["Peenya", "Thekedar", "Ramesh"]),
    }
    await asyncio.sleep(1.5)
    async with websocket_connect(
        os.getenv("GNANI_STT_WS_URL", PRISMA_WS_URL),
        additional_headers=headers,
        open_timeout=30,
        ping_interval=20,
        ping_timeout=20,
    ) as websocket:
        while json.loads(await asyncio.wait_for(websocket.recv(), 10)).get("type") != "connected":
            pass
        await websocket.send(json.dumps({
            "type": "update_settings",
            "bias": {"list": ["Peenya", "Thekedar"], "score": 2.0},
        }))
        for offset in range(0, len(pcm), 1024):
            await websocket.send(pcm[offset:offset + 1024].ljust(1024, b"\x00"))
            await asyncio.sleep(0.064)
        await websocket.send(json.dumps({"type": "commit"}))
        async for raw in websocket:
            event = json.loads(raw)
            if event.get("type") == "transcript":
                return
            if event.get("type") == "error":
                raise RuntimeError(f"Prisma API error: {event}")
    raise RuntimeError("Prisma returned no transcript event.")


async def main() -> None:
    engine = EvonLegalEngine(None, None, "LIVE")
    stage_a = await engine.stage_a_extract_slots(TRANSCRIPT, FormAClaimSlots(), "hi-IN")
    slots = FormAClaimSlots.model_validate(stage_a["updated_slots"])
    missing = [field for field in REQUIRED if getattr(slots, field) is None]
    assert not missing, f"Stage-A missing slots: {missing}"
    audit = await engine.stage_b_statutory_audit_and_draft(slots, "hi-IN")
    assert audit["result"]["principal_arrears_inr"] == 10600
    print("[PASS] Stage-A/Stage-B live reasoning")

    wav_bytes = await synthesize_timbre_audio(
        "रमेश जी, आपका फॉर्म ए तैयार है।", os.environ["GNANI_API_KEY"].strip()
    )
    assert len(wav_bytes) > 1000
    print("[PASS] Timbre v3.0 TTS")
    await check_prisma(wav_bytes)
    print("[PASS] Prisma v3.0 STT")

    socket = ProbeSocket()
    session = Session(socket)
    await session.run()
    print("Session events:", [
        (event.get("type"), event.get("message", "")) for event in socket.events
    ])
    claim = next((event for event in socket.events if event.get("type") == "claim_ready"), None)
    assert claim, "Session did not produce claim_ready."
    claim_dir = ROOT / "claims" / claim["claim_id"]
    assert (claim_dir / "form-a-claim.pdf").is_file()
    assert (claim_dir / "samadhan-mapped-draft.json").is_file()
    json.loads((claim_dir / "samadhan-mapped-draft.json").read_text(encoding="utf-8"))
    print("[PASS] Live session Form-A PDF and SAMADHAN JSON")


if __name__ == "__main__":
    asyncio.run(main())

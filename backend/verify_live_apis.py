from __future__ import annotations

import asyncio
import base64
import json
import os
import wave
from pathlib import Path

import httpx
import websockets
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

GNANI_API_KEY = os.getenv("GNANI_API_KEY", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
TIMBRE_WS_URL = "wss://api.vachana.ai/api/v1/tts"
PRISMA_WS_URL = "wss://api.vachana.ai/stt/v3/stream"
FIXTURE_WAV = ROOT / "fixtures" / "live_tts_8khz.wav"


async def check_huggingface_access() -> None:
    print("\n=== [1/3] Hugging Face Evon access ===")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://huggingface.co/api/models/gnani/gnani-evon-v3.3-30B-A3B",
            headers=headers,
        )
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face check failed ({response.status_code}): {response.text}")
    model = response.json()
    print(f"HF access confirmed: {model.get('id')}")


async def synthesize_timbre() -> bytes:
    print("\n=== [2/3] Timbre v3.0 WebSocket TTS ===")
    payload = {
        "text": "साब, <pauses> ठेकेदार रमेश ने पीन्या साइट पर <slow>छब्बीस दिन</slow> काम कराया और मेरी दिहाड़ी रोक ली है।",
        "voice": "Shivani",
        "model": "timbre-v3.0",
        "language": "hi-IN",
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 8000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav",
        },
    }
    audio = bytearray()
    async with websockets.connect(
        TIMBRE_WS_URL,
        additional_headers={"x-api-key-id": GNANI_API_KEY, "Content-Type": "application/json"},
    ) as websocket:
        await websocket.send(json.dumps(payload, ensure_ascii=False))
        async for raw_message in websocket:
            message = json.loads(raw_message)
            if message.get("type") == "audio":
                encoded = message.get("data", {}).get("audio", "")
                if encoded:
                    audio.extend(base64.b64decode(encoded))
            if message.get("type") == "error":
                raise RuntimeError(f"Timbre API error: {message}")
            if message.get("type") == "complete" or message.get("data", {}).get("is_final") is True:
                break
    if not audio:
        raise RuntimeError("Timbre returned no audio")
    FIXTURE_WAV.parent.mkdir(parents=True, exist_ok=True)
    if bytes(audio[:4]) == b"RIFF":
        FIXTURE_WAV.write_bytes(audio)
    else:
        with wave.open(str(FIXTURE_WAV), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(8000)
            output.writeframes(audio)
    print(f"Timbre returned {len(audio)} bytes; saved {FIXTURE_WAV}")
    return bytes(audio)


async def check_prisma(wav_bytes: bytes) -> None:
    print("\n=== [3/3] Prisma v3.0 WebSocket STT ===")
    raw_pcm = wav_bytes[44:] if wav_bytes[:4] == b"RIFF" else wav_bytes
    raw_pcm += b"\x00" * 16000
    headers = {
        "x-api-key-id": GNANI_API_KEY,
        "x-model": "prisma-v3.0",
        "lang_code": "hi-IN,en-IN",
        "x-sample-rate": "8000",
        "x-format": "transcribe",
        "itn_native_numerals": "false",
        "x-vad-threshold": "0.72",
        "x-min-speech-ms": "200",
        "x-min-silence-ms": "700",
        "x-min-segment-ms": "150",
    }
    async with websockets.connect(PRISMA_WS_URL, additional_headers=headers) as websocket:
        await websocket.send(json.dumps({
            "type": "update_settings",
            "bias": {"list": ["Peenya", "Thekedar", "Dihadi", "Ramesh"], "score": 2.0},
        }))
        for offset in range(0, len(raw_pcm), 1024):
            frame = raw_pcm[offset:offset + 1024].ljust(1024, b"\x00")
            await websocket.send(frame)
            await asyncio.sleep(0.064)
        await websocket.send(json.dumps({"type": "commit"}))
        async for raw_message in websocket:
            event = json.loads(raw_message)
            print(f"Prisma event: {event.get('type')}")
            if event.get("type") == "error":
                raise RuntimeError(f"Prisma API error: {event}")
            if event.get("type") == "transcript":
                print(f"Transcript: {event.get('text')}")
                return
    raise RuntimeError("Prisma closed without a transcript")


async def main() -> None:
    if not GNANI_API_KEY:
        raise RuntimeError("GNANI_API_KEY is missing in backend/.env")
    await check_huggingface_access()
    await check_prisma(await synthesize_timbre())


if __name__ == "__main__":
    asyncio.run(main())

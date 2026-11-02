from __future__ import annotations

import base64
import binascii
import json
import os
import wave
from io import BytesIO

from websockets.asyncio.client import connect as websocket_connect

from language_support import SUPPORTED_LANGUAGES, validate_language

TIMBRE_WS_URL = "wss://api.vachana.ai/api/v1/tts"

async def stream_timbre_audio(text: str, api_key: str, language: str = "hi-IN"):
    if not text.strip():
        raise ValueError("Timbre read-back text cannot be empty.")
    if not api_key:
        raise RuntimeError("GNANI_API_KEY is required for Timbre read-back.")
    locale = validate_language(language)
    if locale not in SUPPORTED_LANGUAGES:
        raise ValueError("Timbre read-back language must be explicitly resolved before synthesis.")
    payload = {
        "model": "timbre-v3.0",
        "voice": "Shivani",
        "text": text,
        "language": locale,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 8000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav",
        },
    }
    async with websocket_connect(
        os.getenv("GNANI_TTS_API_URL", TIMBRE_WS_URL),
        additional_headers={"x-api-key-id": api_key, "Content-Type": "application/json"},
    ) as websocket:
        await websocket.send(json.dumps(payload, ensure_ascii=False))
        async for frame in websocket:
            yield frame


async def synthesize_timbre_audio(text: str, api_key: str, language: str = "hi-IN") -> bytes:
    audio = bytearray()
    async for frame in stream_timbre_audio(text, api_key, language):
        if isinstance(frame, bytes):
            raise RuntimeError("Timbre returned an unexpected binary frame.")
        try:
            event = json.loads(frame)
        except json.JSONDecodeError as error:
            raise RuntimeError("Timbre returned an invalid response frame.") from error

        if event.get("type") == "error":
            raise RuntimeError(f"Timbre API error: {event}")
        if event.get("type") == "audio":
            encoded = event.get("data", {}).get("audio", "")
            if encoded:
                try:
                    audio.extend(base64.b64decode(encoded, validate=True))
                except (binascii.Error, ValueError) as error:
                    raise RuntimeError("Timbre returned invalid base64 audio.") from error
        if event.get("type") == "complete" or event.get("data", {}).get("is_final") is True:
            break

    if not audio:
        raise RuntimeError("Timbre completed without returning audio.")
    if bytes(audio[:4]) == b"RIFF":
        return bytes(audio)

    wav = BytesIO()
    with wave.open(wav, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(audio)
    return wav.getvalue()

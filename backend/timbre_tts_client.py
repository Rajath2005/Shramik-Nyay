from __future__ import annotations

import asyncio
import base64
import binascii
import json
import os
import wave
from collections.abc import Awaitable, Callable
from io import BytesIO

from websockets.asyncio.client import connect as websocket_connect
from websockets.exceptions import ConnectionClosedError, InvalidHandshake

from language_support import SUPPORTED_LANGUAGES, validate_language

TIMBRE_WS_URL = "wss://api.vachana.ai/api/v1/tts"
TIMBRE_REST_URL = "https://api.vachana.ai/api/v1/tts/inference"

async def stream_timbre_audio(text: str, api_key: str, language: str = "hi-IN"):
    api_key = api_key.strip()
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
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            async with websocket_connect(
                os.getenv("GNANI_TTS_API_URL", TIMBRE_WS_URL),
                additional_headers={"x-api-key-id": api_key, "Content-Type": "application/json"},
            ) as websocket:
                await websocket.send(json.dumps(payload, ensure_ascii=False))
                async for frame in websocket:
                    yield frame
                return
        except (TimeoutError, OSError, asyncio.TimeoutError, ConnectionClosedError, InvalidHandshake) as error:
            last_error = error
            if attempt == 0:
                await asyncio.sleep(1.0)
    if last_error:
        raise last_error


async def _rest_timbre_audio(text: str, api_key: str, language: str) -> bytes:
    import httpx

    payload = {
        "model": "timbre-v3.0", "voice": "Shivani", "text": text,
        "language": language, "speed": 1.0,
        "audio_config": {
            "sample_rate": 8000, "num_channels": 1, "sample_width": 2,
            "encoding": "linear_pcm", "container": "wav",
        },
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            os.getenv("GNANI_TTS_REST_URL", TIMBRE_REST_URL),
            json=payload,
            headers={"X-API-Key-ID": api_key},
        )
        response.raise_for_status()
        if response.content[:4] == b"RIFF":
            return response.content
        data = response.json()
        encoded = data.get("audio") or data.get("data", {}).get("audio")
        if not encoded:
            raise RuntimeError("Timbre REST fallback returned no audio.")
        return base64.b64decode(encoded, validate=True)


async def synthesize_timbre_audio(
    text: str,
    api_key: str,
    language: str = "hi-IN",
    *,
    on_first_audio_chunk: Callable[[], Awaitable[None]] | None = None,
) -> bytes:
    api_key = api_key.strip()
    audio = bytearray()
    try:
        frames = stream_timbre_audio(text, api_key, language)
        async for frame in frames:
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
                        chunk = base64.b64decode(encoded, validate=True)
                    except (binascii.Error, ValueError) as error:
                        raise RuntimeError("Timbre returned invalid base64 audio.") from error
                    if chunk and not audio and on_first_audio_chunk:
                        await on_first_audio_chunk()
                    audio.extend(chunk)
            if event.get("type") == "complete" or event.get("data", {}).get("is_final") is True:
                break
    except (TimeoutError, OSError, asyncio.TimeoutError, ConnectionClosedError, InvalidHandshake):
        audio.extend(await _rest_timbre_audio(text, api_key, validate_language(language)))

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

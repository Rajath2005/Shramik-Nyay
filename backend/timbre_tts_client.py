from __future__ import annotations

import json

import websockets

TIMBRE_WS_URL = "wss://api.vachana.ai/api/v1/tts"


async def stream_timbre_audio(text: str, api_key: str):
    payload = {"model": "timbre-v3.0", "voice": "Shivani", "text": text}
    async with websockets.connect(
        TIMBRE_WS_URL,
        additional_headers={"x-api-key-id": api_key},
    ) as websocket:
        await websocket.send(json.dumps(payload))
        async for frame in websocket:
            yield frame

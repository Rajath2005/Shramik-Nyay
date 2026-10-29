from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

import websockets

PRISMA_WS_URL = "wss://api.vachana.ai/stt/v3/stream"
FRAME_BYTES = 1024
CADENCE_SECONDS = 0.064


class PrismaRealtimeStreamer:
    def __init__(self, api_key: str, on_server_event: Callable[[dict], Awaitable[None]]) -> None:
        self.api_key = api_key
        self.on_server_event = on_server_event
        self.audio_ring_buffer = bytearray()
        self.ws = None
        self.running = False

    def get_handshake_headers(self) -> dict[str, str]:
        return {
            "x-api-key-id": self.api_key,
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

    def push_pcm_bytes(self, raw_bytes: bytes) -> None:
        self.audio_ring_buffer.extend(raw_bytes)

    async def connect_and_run(self) -> None:
        async with websockets.connect(
            PRISMA_WS_URL,
            additional_headers=self.get_handshake_headers(),
        ) as websocket:
            self.ws = websocket
            self.running = True
            await asyncio.gather(self._pace_frames(), self._listen_server_frames())

    async def _pace_frames(self) -> None:
        while self.running:
            if len(self.audio_ring_buffer) >= FRAME_BYTES:
                frame = bytes(self.audio_ring_buffer[:FRAME_BYTES])
                del self.audio_ring_buffer[:FRAME_BYTES]
                await self.ws.send(frame)
            await asyncio.sleep(CADENCE_SECONDS)

    async def _listen_server_frames(self) -> None:
        async for message in self.ws:
            await self.on_server_event(json.loads(message))

    async def boost_locality_vocabulary(self, new_words: list[str]) -> None:
        if self.ws and self.running:
            await self.ws.send(json.dumps({
                "type": "update_settings",
                "bias": {"list": new_words[:100], "score": 2.0},
            }))

    async def commit_and_close(self) -> None:
        self.running = False
        if self.ws:
            await self.ws.send(json.dumps({"type": "commit"}))
            await self.ws.close()

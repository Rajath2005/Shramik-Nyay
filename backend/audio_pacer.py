from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Awaitable, Callable

import websockets

PRISMA_WS_URL = "wss://api.vachana.ai/stt/v3/stream"
FRAME_BYTES = 1024            # 512 samples x 2 bytes, required by the API
FRAME_SAMPLES = 512
BIAS_SCORE = 2.0
_WORD = re.compile(r"^[^\W\d_]+$", re.UNICODE)   # letters only, no digits/spaces


def sanitize_bias_words(words: list[str]) -> list[str]:
    """Prisma silently drops the WHOLE list if one word is invalid, so filter first."""
    seen: dict[str, None] = {}
    for word in words:
        word = word.strip()
        if word and _WORD.match(word):
            seen.setdefault(word, None)
    return list(seen)[:100]


class PrismaRealtimeStreamer:
    """Paces raw PCM at real-time cadence. Silence frames keep the cadence (and let
    VAD close segments) whenever the browser has not sent audio yet."""

    def __init__(self, api_key: str, on_server_event: Callable[[dict], Awaitable[None]],
                 *, sample_rate: int = 8000, lang_code: str = "hi-IN,en-IN",
                 fmt: str = "transcribe", seed_words: list[str] | None = None) -> None:
        if sample_rate not in (8000, 16000):
            raise ValueError("sample_rate must be 8000 or 16000")
        self.api_key, self.on_server_event = api_key, on_server_event
        self.sample_rate, self.lang_code, self.fmt = sample_rate, lang_code, fmt
        self.seed_words = sanitize_bias_words(seed_words or [])
        self.cadence = FRAME_SAMPLES / sample_rate        # 0.064 s at 8 kHz
        self.buffer = bytearray()
        self.ws = None
        self.running = False
        self.connected = asyncio.Event()
        self._transcript_seen = asyncio.Event()
        self._send_lock = asyncio.Lock()

    def headers(self) -> dict[str, str]:
        h = {
            "x-api-key-id": self.api_key,
            "x-model": "prisma-v3.0",
            "lang_code": self.lang_code,
            "x-sample-rate": str(self.sample_rate),
            "x-format": self.fmt,
            "itn_native_numerals": "false",
            "x-vad-threshold": "0.72",
            "x-min-speech-ms": "200",
            "x-min-silence-ms": "700",
            "x-min-segment-ms": "150",
            "x-max-speech-s": "60",
        }
        if self.seed_words:
            h["x-bias-list"] = json.dumps(self.seed_words)
            h["x-bias-score"] = str(BIAS_SCORE)
        return h

    def push_pcm_bytes(self, raw: bytes) -> None:
        self.buffer.extend(raw)

    async def connect_and_run(self) -> None:
        async with websockets.connect(PRISMA_WS_URL, additional_headers=self.headers()) as ws:
            self.ws, self.running = ws, True
            await asyncio.gather(self._pace(), self._listen())

    async def _pace(self) -> None:
        silence = bytes(FRAME_BYTES)
        loop = asyncio.get_running_loop()
        deadline = loop.time()
        while self.running:
            if len(self.buffer) >= FRAME_BYTES:
                frame = bytes(self.buffer[:FRAME_BYTES])
                del self.buffer[:FRAME_BYTES]
            else:
                frame = silence
            async with self._send_lock:
                await self.ws.send(frame)
            deadline += self.cadence                      # absolute schedule: no drift
            await asyncio.sleep(max(0.0, deadline - loop.time()))

    async def _listen(self) -> None:
        async for message in self.ws:
            event = json.loads(message)
            if event.get("type") == "connected":
                self.connected.set()
            elif event.get("type") == "transcript":
                self._transcript_seen.set()
            await self.on_server_event(event)

    async def boost_locality_vocabulary(self, words: list[str]) -> list[str]:
        clean = sanitize_bias_words(words)
        if self.ws and self.running and clean:
            async with self._send_lock:
                await self.ws.send(json.dumps({"type": "update_settings",
                                               "bias": {"list": clean, "score": BIAS_SCORE}}))
        return clean   # confirm via the `settings_updated` event (check bias_word_count)

    async def commit_and_close(self) -> None:
        if not self.ws:
            return
        remainder = len(self.buffer) % FRAME_BYTES
        if remainder:
            self.buffer.extend(bytes(FRAME_BYTES - remainder))
        self._transcript_seen.clear()
        while self.buffer:
            await asyncio.sleep(self.cadence)
        async with self._send_lock:
            await self.ws.send(json.dumps({"type": "commit"}))
        try:
            await asyncio.wait_for(self._transcript_seen.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        self.running = False
        await self.ws.close()

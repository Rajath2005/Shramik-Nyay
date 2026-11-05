from __future__ import annotations

import asyncio
import json
import logging
import os
import unicodedata
from collections.abc import Awaitable, Callable

from websockets.asyncio.client import connect as websocket_connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

from language_support import prisma_language_code

PRISMA_WS_URL = "wss://api.vachana.ai/stt/v3/stream"
FRAME_BYTES = 1024            # 512 samples x 2 bytes, required by the API
FRAME_SAMPLES = 512
BIAS_SCORE = 2.0
PRISMA_SEED_WORDS = [
    "Thekedar",
    "Mistry",
    "Dihadi",
    "Muster",
    "Samadhan",
    "UAN",
    "Advance",
    "Overtime",
]
LOGGER = logging.getLogger(__name__)


class PrismaStreamError(RuntimeError):
    def __init__(self, engineer_message: str, worker_message: str) -> None:
        super().__init__(engineer_message)
        self.engineer_message = engineer_message
        self.worker_message = worker_message


def _is_single_word(value: str) -> bool:
    has_letter = False
    for character in value:
        category = unicodedata.category(character)
        if category.startswith("L"):
            has_letter = True
        elif category.startswith("M") and has_letter:
            continue
        else:
            return False
    return has_letter


def sanitize_bias_words(words: list[str]) -> list[str]:
    """Prisma silently drops the WHOLE list if one word is invalid, so filter first."""
    seen: dict[str, None] = {}
    for word in words:
        word = word.strip()
        if word and _is_single_word(word):
            seen.setdefault(word, None)
    return list(seen)[:100]


class PrismaRealtimeStreamer:
    """Paces raw PCM at real-time cadence. Silence frames keep the cadence (and let
    VAD close segments) whenever the browser has not sent audio yet."""

    def __init__(self, api_key: str, on_server_event: Callable[[dict], Awaitable[None]],
                 *, sample_rate: int = 8000, lang_code: str = "indic-auto",
                 fmt: str = "transcribe", seed_words: list[str] | None = None,
                 ws_url: str | None = None) -> None:
        if sample_rate not in (8000, 16000):
            raise ValueError("sample_rate must be 8000 or 16000")
        valid_language_codes = {
            prisma_language_code(language)
            for language in ("auto", "hi-IN", "kn-IN", "en-IN")
        }
        if lang_code not in valid_language_codes:
            raise ValueError("lang_code must be a supported Prisma language preference.")
        self.api_key, self.on_server_event = api_key, on_server_event
        self.ws_url = ws_url or os.getenv("GNANI_STT_WS_URL", PRISMA_WS_URL)
        self.sample_rate, self.lang_code, self.fmt = sample_rate, lang_code, fmt
        self.seed_words = sanitize_bias_words(seed_words or [])
        self.cadence = FRAME_SAMPLES / sample_rate        # 0.064 s at 8 kHz
        self.buffer = bytearray()
        self.ws = None
        self.running = False
        self.connecting = False
        self._connection_ready = asyncio.Event()
        self.connected = asyncio.Event()
        self._audio_ready = asyncio.Event()
        self._transcript_seen = asyncio.Event()
        self._send_lock = asyncio.Lock()
        self._last_pcm_sent_at: float | None = None
        self._commit_sent_at: float | None = None

    def headers(self) -> dict[str, str]:
        headers = {
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
            "x-max-speech-s": "30",
        }
        if self.seed_words:
            headers["x-bias-list"] = json.dumps(self.seed_words)
        return headers

    def push_pcm_bytes(self, raw: bytes) -> None:
        self.buffer.extend(raw)

    async def connect_and_run(self) -> None:
        self.connecting = True
        try:
            try:
                async with websocket_connect(self.ws_url, additional_headers=self.headers()) as ws:
                    self.ws, self.running = ws, True
                    self._connection_ready.set()
                    await asyncio.gather(self._pace(), self._listen())
            except ConnectionClosed as error:
                close = error.rcvd
                code = close.code if close else None
                reason = close.reason if close else ""
                LOGGER.error("Prisma websocket closed: code=%s reason=%s", code, reason)
                raise PrismaStreamError(
                    f"Prisma websocket closed: code={code}, reason={reason!r}",
                    "The live speech service disconnected. Please try again or type your answer.",
                ) from error
            except InvalidStatus as error:
                response = error.response
                body = bytes(response.body).decode("utf-8", "replace")
                LOGGER.error(
                    "Prisma websocket handshake rejected: status=%s body=%s",
                    response.status_code,
                    body,
                )
                raise PrismaStreamError(
                    f"Prisma websocket handshake rejected: status={response.status_code}, body={body!r}",
                    "The live speech service rejected the connection. Please try again or type your answer.",
                ) from error
        finally:
            self.running = False
            self.connecting = False
            self.connected.clear()
            self._connection_ready.set()
            self._audio_ready.set()
            self.ws = None

    async def _pace(self) -> None:
        await self._audio_ready.wait()
        if not self.running or not self.connected.is_set():
            return
        silence = bytes(FRAME_BYTES)
        loop = asyncio.get_running_loop()
        deadline = loop.time()
        while self.running:
            has_pcm = len(self.buffer) >= FRAME_BYTES
            if has_pcm:
                frame = bytes(self.buffer[:FRAME_BYTES])
                del self.buffer[:FRAME_BYTES]
            else:
                frame = silence
            if len(frame) != FRAME_BYTES:
                raise AssertionError(f"Prisma audio frame must be exactly {FRAME_BYTES} bytes.")
            async with self._send_lock:
                await self.ws.send(frame)
            if has_pcm:
                self._last_pcm_sent_at = loop.time()
            deadline += self.cadence                      # absolute schedule: no drift
            await asyncio.sleep(max(0.0, deadline - loop.time()))

    async def _listen(self) -> None:
        try:
            async for message in self.ws:
                event = json.loads(message)
                if event.get("type") == "connected":
                    self.connected.set()
                    self._audio_ready.set()
                elif event.get("type") == "transcript":
                    loop = asyncio.get_running_loop()
                    latency_origin = (
                        self._commit_sent_at
                        if self._commit_sent_at is not None
                        else self._last_pcm_sent_at
                    )
                    if latency_origin is not None:
                        event["segment_latency_ms"] = round(
                            max(0.0, loop.time() - latency_origin) * 1000, 1
                        )
                    self._commit_sent_at = None
                    self._last_pcm_sent_at = None
                    self._transcript_seen.set()
                await self.on_server_event(event)
        finally:
            self.running = False
            self._audio_ready.set()

    async def boost_locality_vocabulary(self, words: list[str]) -> list[str]:
        clean = sanitize_bias_words(words)
        if not clean:
            return clean
        if not self.running and not self.connecting:
            raise RuntimeError("Cannot update Prisma word bias while the stream is inactive.")
        if not self.connected.is_set():
            try:
                await asyncio.wait_for(self.connected.wait(), timeout=10.0)
            except asyncio.TimeoutError as error:
                raise RuntimeError("Timed out waiting for Prisma connection before updating word bias.") from error
        if not self.ws or not self.running:
            raise RuntimeError("Cannot update Prisma word bias after the stream has stopped.")
        async with self._send_lock:
            await self.ws.send(json.dumps({"type": "update_settings",
                                           "bias": {"list": clean, "score": BIAS_SCORE}}))
        return clean   # confirm via the `settings_updated` event (check bias_word_count)

    async def commit_and_close(self) -> None:
        if not self.ws:
            if not self.connecting:
                return
            await self._connection_ready.wait()
        if not self.ws:
            return
        await self._audio_ready.wait()
        if not self.running or not self.connected.is_set():
            return
        remainder = len(self.buffer) % FRAME_BYTES
        if remainder:
            self.buffer.extend(bytes(FRAME_BYTES - remainder))
        self._transcript_seen.clear()
        while self.buffer:
            await asyncio.sleep(self.cadence)
        async with self._send_lock:
            self._commit_sent_at = asyncio.get_running_loop().time()
            await self.ws.send(json.dumps({"type": "commit"}))
        try:
            await asyncio.wait_for(self._transcript_seen.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        self.running = False
        await self.ws.close()

    async def close(self) -> None:
        self.running = False
        self._audio_ready.set()
        if self.ws:
            await self.ws.close()

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from websockets.asyncio.client import connect as websocket_connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

from audio_pacer import PRISMA_WS_URL

WAIT_SECONDS = 3.0


@dataclass
class Result:
    name: str
    passed: bool
    close_code: str
    detail: str


def round_one_variants(api_key: str) -> list[tuple[str, dict[str, str]]]:
    base = {
        "x-api-key-id": api_key,
        "x-model": "prisma-v3.0",
        "lang_code": "indic-auto",
        "x-sample-rate": "8000",
    }
    return [
        ("R0 minimal", base),
        ("R1 +VAD", {**base, "x-vad-threshold": "0.72", "x-min-speech-ms": "200",
                     "x-min-silence-ms": "700", "x-min-segment-ms": "150"}),
        ("R2 +format/itn", {**base, "x-vad-threshold": "0.72", "x-min-speech-ms": "200",
                            "x-min-silence-ms": "700", "x-min-segment-ms": "150",
                            "x-format": "transcribe", "itn_native_numerals": "false"}),
        ("R3 +max-speech", {**base, "x-vad-threshold": "0.72", "x-min-speech-ms": "200",
                            "x-min-silence-ms": "700", "x-min-segment-ms": "150",
                            "x-format": "transcribe", "itn_native_numerals": "false",
                            "x-max-speech-s": "30"}),
        ("R4 +bias comma", {**base, "x-vad-threshold": "0.72", "x-min-speech-ms": "200",
                            "x-min-silence-ms": "700", "x-min-segment-ms": "150",
                            "x-format": "transcribe", "itn_native_numerals": "false",
                            "x-max-speech-s": "30", "x-bias-list": "Peenya,Thekedar"}),
        ("R5 +bias JSON", {**base, "x-vad-threshold": "0.72", "x-min-speech-ms": "200",
                           "x-min-silence-ms": "700", "x-min-segment-ms": "150",
                           "x-format": "transcribe", "itn_native_numerals": "false",
                           "x-max-speech-s": "30", "x-bias-list": '["Peenya","Thekedar"]'}),
    ]


def language_variants(headers: dict[str, str]) -> list[tuple[str, dict[str, str]]]:
    return [
        (f"L{i} {language}", {**headers, "lang_code": language})
        for i, language in enumerate(
            ("indic-auto", "hi-IN", "kn-IN", "en-IN", "hi-IN,en-IN", "hi-IN,kn-IN,en-IN"),
            start=1,
        )
    ]


async def probe(name: str, headers: dict[str, str]) -> Result:
    websocket = None
    try:
        websocket = await websocket_connect(PRISMA_WS_URL, additional_headers=headers)
        try:
            deadline = asyncio.get_running_loop().time() + WAIT_SECONDS
            while True:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    return Result(name, False, "-", "timeout waiting for connected")
                raw = await asyncio.wait_for(websocket.recv(), timeout=remaining)
                if isinstance(raw, str):
                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        event = {}
                    if event.get("type") == "connected":
                        return Result(name, True, "-", "connected")
        except asyncio.TimeoutError:
            return Result(name, False, "-", "timeout waiting for connected")
        except ConnectionClosed as error:
            close = error.rcvd
            code = str(close.code) if close else "unknown"
            reason = close.reason if close else ""
            return Result(name, False, code, reason or "closed")
    except InvalidStatus as error:
        return Result(name, False, str(error.response.status_code), "HTTP handshake rejected")
    except Exception as error:
        return Result(name, False, "-", f"{type(error).__name__}: {error}")
    finally:
        if websocket:
            await websocket.close()


async def main() -> None:
    load_dotenv()
    api_key = os.getenv("GNANI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GNANI_API_KEY is required.")
    round_one = [await probe(name, headers) for name, headers in round_one_variants(api_key)]
    passing_headers = max(
        (
            headers
            for (name, headers), result in zip(round_one_variants(api_key), round_one)
            if result.passed
        ),
        key=len,
        default=round_one_variants(api_key)[0][1],
    )
    round_two = [await probe(name, headers) for name, headers in language_variants(passing_headers)]
    for title, results in (("Round 1: cumulative headers", round_one),
                           ("Language variants: full passing header set", round_two)):
        print(f"\n{title}")
        print("------------------------------")
        print("Variant           Result  Close code  Reason")
        print("----------------  ------  ----------  ----------------------------")
        for result in results:
            print(f"{result.name:<16}  {'PASS' if result.passed else 'FAIL':<6}  "
                  f"{result.close_code:<10}  {result.detail}")


if __name__ == "__main__":
    asyncio.run(main())

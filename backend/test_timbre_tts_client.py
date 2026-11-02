import asyncio
import base64
import json
import unittest
import wave
from io import BytesIO
from unittest.mock import patch

from timbre_tts_client import TIMBRE_WS_URL, stream_timbre_audio, synthesize_timbre_audio


class FakeTimbreWebSocket:
    def __init__(self, frames):
        self.frames = frames
        self.sent = []

    async def send(self, message):
        self.sent.append(message)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.frames:
            raise StopAsyncIteration
        return self.frames.pop(0)


class FakeTimbreConnection:
    def __init__(self, websocket):
        self.websocket = websocket

    async def __aenter__(self):
        return self.websocket

    async def __aexit__(self, *_):
        return None


class TimbreTtsClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_language_is_forwarded_to_timbre_for_supported_languages(self):
        pcm = b"\x01\x00" * 10
        for language in ("hi-IN", "kn-IN", "en-IN"):
            with self.subTest(language=language):
                websocket = FakeTimbreWebSocket([
                    json.dumps({"type": "audio", "data": {"audio": base64.b64encode(pcm).decode()}}),
                    json.dumps({"type": "complete"}),
                ])
                with patch(
                    "timbre_tts_client.websocket_connect",
                    return_value=FakeTimbreConnection(websocket),
                ):
                    await synthesize_timbre_audio("synthetic read-back", "offline-test-key", language)

                self.assertEqual(json.loads(websocket.sent[0])["language"], language)

    async def test_tts_endpoint_can_be_configured_from_environment(self):
        websocket = FakeTimbreWebSocket([
            json.dumps({"type": "audio", "data": {"audio": base64.b64encode(b"\x01\x00" * 8).decode()}}),
            json.dumps({"type": "complete"}),
        ])
        with patch.dict("os.environ", {"GNANI_TTS_API_URL": "wss://tts.example/synthesize"}):
            with patch(
                "timbre_tts_client.websocket_connect",
                return_value=FakeTimbreConnection(websocket),
            ) as connect:
                await synthesize_timbre_audio("synthetic read-back", "offline-test-key")

        self.assertEqual(connect.call_args.args[0], "wss://tts.example/synthesize")

    async def test_synthesizes_streamed_pcm_as_wav_and_sends_required_payload(self):
        pcm = b"\x01\x00\x02\x00" * 20
        websocket = FakeTimbreWebSocket([
            json.dumps({"type": "audio", "data": {"audio": base64.b64encode(pcm[:24]).decode()}}),
            json.dumps({"type": "audio", "data": {"audio": base64.b64encode(pcm[24:]).decode()}}),
            json.dumps({"type": "complete"}),
            json.dumps({"type": "audio", "data": {"audio": base64.b64encode(b"ignored").decode()}}),
        ])
        connection = FakeTimbreConnection(websocket)
        with patch("timbre_tts_client.websocket_connect", return_value=connection) as connect:
            wav_bytes = await synthesize_timbre_audio("<slow>दस रुपये</slow>", "offline-test-key")

        connect.assert_called_once_with(
            TIMBRE_WS_URL,
            additional_headers={"x-api-key-id": "offline-test-key", "Content-Type": "application/json"},
        )
        request = json.loads(websocket.sent[0])
        self.assertEqual(request, {
            "model": "timbre-v3.0",
            "voice": "Shivani",
            "text": "<slow>दस रुपये</slow>",
            "language": "hi-IN",
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 8000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        })
        with wave.open(BytesIO(wav_bytes), "rb") as audio:
            self.assertEqual(audio.getframerate(), 8000)
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.getsampwidth(), 2)
            self.assertEqual(audio.readframes(audio.getnframes()), pcm)

    async def test_existing_wav_is_returned_without_wrapping(self):
        output = BytesIO()
        with wave.open(output, "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b"\x01\x00" * 8)
        wav_bytes = output.getvalue()
        websocket = FakeTimbreWebSocket([
            json.dumps({"type": "audio", "data": {"audio": base64.b64encode(wav_bytes).decode()}}),
            json.dumps({"type": "complete"}),
        ])
        with patch("timbre_tts_client.websocket_connect", return_value=FakeTimbreConnection(websocket)):
            self.assertEqual(await synthesize_timbre_audio("रीडबैक", "offline-test-key"), wav_bytes)

    async def test_api_errors_and_empty_audio_are_explicit(self):
        cases = [
            ([json.dumps({"type": "error", "message": "rejected"})], "Timbre API error"),
            ([json.dumps({"type": "complete"})], "without returning audio"),
            ([json.dumps({"type": "audio", "data": {"audio": "%%%"} })], "invalid base64"),
        ]
        for frames, expected in cases:
            with self.subTest(expected=expected):
                websocket = FakeTimbreWebSocket(frames)
                with patch("timbre_tts_client.websocket_connect", return_value=FakeTimbreConnection(websocket)):
                    with self.assertRaisesRegex(RuntimeError, expected):
                        await synthesize_timbre_audio("रीडबैक", "offline-test-key")

    async def test_blank_text_and_missing_key_do_not_connect(self):
        with patch("timbre_tts_client.websocket_connect") as connect:
            with self.assertRaisesRegex(ValueError, "cannot be empty"):
                await synthesize_timbre_audio("  ", "offline-test-key")
            with self.assertRaisesRegex(RuntimeError, "GNANI_API_KEY"):
                await synthesize_timbre_audio("रीडबैक", "")
        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()

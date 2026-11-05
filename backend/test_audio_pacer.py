import asyncio
import json
import unittest
from unittest.mock import patch

from audio_pacer import (
    BIAS_SCORE,
    FRAME_BYTES,
    PRISMA_SEED_WORDS,
    PRISMA_WS_URL,
    PrismaRealtimeStreamer,
    sanitize_bias_words,
)
from locality_vocab import LOCALITY_VOCAB, locality_terms_in


class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.closed = False
        self.events = []

    async def send(self, message):
        self.sent.append(message)

    async def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, websocket):
        self.websocket = websocket

    async def __aenter__(self):
        return self.websocket

    async def __aexit__(self, *_):
        return None


class PrismaRealtimeStreamerTests(unittest.IsolatedAsyncioTestCase):
    def test_stt_endpoint_can_be_configured_from_environment(self):
        with patch.dict("os.environ", {"GNANI_STT_WS_URL": "wss://stt.example/stream"}):
            streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))

        self.assertEqual(streamer.ws_url, "wss://stt.example/stream")

    def test_headers_match_required_prisma_protocol(self):
        streamer = PrismaRealtimeStreamer(
            "local-test-key",
            lambda _: asyncio.sleep(0),
            seed_words=["Thekedar", " Peenya ", "Thekedar"],
        )

        headers = streamer.headers()

        self.assertEqual(headers["x-api-key-id"], "local-test-key")
        self.assertEqual(headers["x-model"], "prisma-v3.0")
        self.assertEqual(headers["lang_code"], "indic-auto")
        self.assertEqual(headers["x-sample-rate"], "8000")
        self.assertEqual(headers["x-format"], "transcribe")
        self.assertEqual(headers["itn_native_numerals"], "false")
        self.assertEqual(headers["x-vad-threshold"], "0.72")
        self.assertEqual(headers["x-min-speech-ms"], "200")
        self.assertEqual(headers["x-min-silence-ms"], "700")
        self.assertEqual(headers["x-min-segment-ms"], "150")
        self.assertEqual(headers["x-max-speech-s"], "30")
        self.assertEqual(json.loads(headers["x-bias-list"]), ["Thekedar", "Peenya"])
        self.assertAlmostEqual(streamer.cadence, 0.064)

    def test_explicit_language_is_sent_without_comma_separated_fallback(self):
        streamer = PrismaRealtimeStreamer(
            "local-test-key",
            lambda _: asyncio.sleep(0),
            lang_code="kn-IN",
        )

        self.assertEqual(streamer.headers()["lang_code"], "kn-IN")
        with self.assertRaises(ValueError):
            PrismaRealtimeStreamer("local-test-key", lambda _: asyncio.sleep(0), lang_code="hi-IN,en-IN")

    def test_seed_terms_and_locality_vocabulary(self):
        streamer = PrismaRealtimeStreamer(
            "key",
            lambda _: asyncio.sleep(0),
            seed_words=PRISMA_SEED_WORDS,
        )
        self.assertEqual(json.loads(streamer.headers()["x-bias-list"]), PRISMA_SEED_WORDS)
        self.assertEqual(set(LOCALITY_VOCAB), {
            "peenya", "whitefield", "yeshwanthpur", "bommanahalli", "dasarahalli",
        })
        terms = locality_terms_in(
            "I worked in PEENYA and Whitefield, then Yeshwanthpur, Bommanahalli, Dasarahalli."
        )
        self.assertEqual(terms, [
            "Peenya", "Whitefield", "Yeshwanthpur", "Bommanahalli", "Dasarahalli",
        ])
        self.assertEqual(locality_terms_in("NorthPeenya and Whitefield2"), [])
        self.assertEqual(sanitize_bias_words(terms), terms)

    def test_audio_rate_and_boost_word_sanitization(self):
        with self.assertRaises(ValueError):
            PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0), sample_rate=12000)

        cleaned = sanitize_bias_words([" Peenya ", "Thekedar", "Peenya", "Mistry-ji", "राम", "ಬೆಂಗಳೂರು", "Peenya2", ""])

        self.assertEqual(cleaned, ["Peenya", "Thekedar", "राम", "ಬೆಂಗಳೂರು"])
        many_words = [f"Word{chr(65 + i // 26)}{chr(65 + i % 26)}" for i in range(120)]
        self.assertEqual(len(sanitize_bias_words(many_words)), 100)

    async def test_pacer_sends_exact_audio_frame_then_silence_frame(self):
        received_frames = []
        streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))
        websocket = FakeWebSocket()
        streamer.ws = websocket
        streamer.running = True
        streamer.connected.set()
        streamer._audio_ready.set()
        audio = bytes(range(256)) * 4
        streamer.push_pcm_bytes(audio)

        async def stop_after_two_frames(message):
            received_frames.append(message)
            if len(received_frames) == 2:
                streamer.running = False

        websocket.send = stop_after_two_frames
        await streamer._pace()

        self.assertEqual(len(received_frames), 2)
        self.assertEqual(received_frames[0], audio)
        self.assertEqual(len(received_frames[0]), FRAME_BYTES)
        self.assertEqual(received_frames[1], bytes(FRAME_BYTES))

    async def test_pacer_does_not_send_before_connected_event(self):
        streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))
        websocket = FakeWebSocket()
        streamer.ws = websocket
        streamer.running = True
        streamer._audio_ready.set()
        streamer.push_pcm_bytes(bytes(FRAME_BYTES))

        await streamer._pace()

        self.assertEqual(websocket.sent, [])

    async def test_locality_boost_sends_documented_control_frame(self):
        streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))
        websocket = FakeWebSocket()
        streamer.ws = websocket
        streamer.running = True
        streamer.connected.set()

        result = await streamer.boost_locality_vocabulary(["Peenya", "Mistry-ji", "Peenya"])

        self.assertEqual(result, ["Peenya"])
        self.assertEqual(json.loads(websocket.sent[0]), {
            "type": "update_settings",
            "bias": {"list": ["Peenya"], "score": BIAS_SCORE},
        })

    async def test_locality_boost_does_not_report_success_without_a_live_stream(self):
        streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))

        with self.assertRaisesRegex(RuntimeError, "stream is inactive"):
            await streamer.boost_locality_vocabulary(["Peenya"])

    async def test_commit_pads_partial_frame_and_closes_after_transcript(self):
        streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))
        websocket = FakeWebSocket()
        streamer.ws = websocket
        streamer.running = True
        streamer.connected.set()
        streamer._audio_ready.set()
        streamer.push_pcm_bytes(b"\x01\x02\x03")

        async def send_and_ack(message):
            websocket.sent.append(message)
            if isinstance(message, str) and json.loads(message)["type"] == "commit":
                streamer._transcript_seen.set()

        websocket.send = send_and_ack
        pace_task = asyncio.create_task(streamer._pace())
        await streamer.commit_and_close()
        await pace_task

        self.assertEqual(websocket.sent[0], b"\x01\x02\x03" + bytes(FRAME_BYTES - 3))
        self.assertEqual(websocket.sent[1], json.dumps({"type": "commit"}))
        self.assertTrue(websocket.closed)
        self.assertFalse(streamer.running)

    async def test_commit_waits_for_a_connection_if_microphone_stops_immediately(self):
        streamer = PrismaRealtimeStreamer("key", lambda _: asyncio.sleep(0))
        websocket = FakeWebSocket()
        streamer.connecting = True
        stop_task = asyncio.create_task(streamer.commit_and_close())
        await asyncio.sleep(0)
        self.assertFalse(stop_task.done())

        streamer.ws = websocket
        streamer.running = True
        streamer.connected.set()
        streamer._audio_ready.set()
        streamer._connection_ready.set()
        streamer._transcript_seen.set()
        await stop_task

        self.assertEqual(json.loads(websocket.sent[0]), {"type": "commit"})
        self.assertTrue(websocket.closed)
        self.assertFalse(streamer.running)

    async def test_transcript_event_reports_latency_from_commit(self):
        events = []
        streamer = PrismaRealtimeStreamer("key", lambda event: _record(events, event))
        websocket = FakeWebSocket()
        streamer.ws = websocket
        streamer.running = True
        streamer._commit_sent_at = asyncio.get_running_loop().time() - 0.05

        class TranscriptSocket(FakeWebSocket):
            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.events:
                    return self.events.pop(0)
                raise StopAsyncIteration

        websocket = TranscriptSocket()
        websocket.events = [json.dumps({"type": "transcript", "text": "नमस्ते"})]
        streamer.ws = websocket

        await streamer._listen()

        self.assertEqual(len(events), 1)
        self.assertGreaterEqual(events[0]["segment_latency_ms"], 45)
        self.assertLess(events[0]["segment_latency_ms"], 1000)

    async def test_connect_uses_prisma_url_and_sends_server_events(self):
        events = []
        streamer = PrismaRealtimeStreamer("key", lambda event: _record(events, event))
        original_sleep = asyncio.sleep

        class EventSocket(FakeWebSocket):
            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.events:
                    return self.events.pop(0)
                streamer.running = False
                raise StopAsyncIteration

        async def paced_sleep(_):
            await original_sleep(0)

        websocket = EventSocket()
        websocket.events = [json.dumps({"type": "connected"}), json.dumps({"type": "transcript", "text": "नमस्ते"})]
        connection = FakeConnection(websocket)
        with patch("audio_pacer.websocket_connect", return_value=connection) as connect:
            with patch("audio_pacer.asyncio.sleep", side_effect=paced_sleep):
                await streamer.connect_and_run()

        connect.assert_called_once()
        args, kwargs = connect.call_args
        self.assertEqual(args[0], PRISMA_WS_URL)
        self.assertEqual(kwargs["additional_headers"], streamer.headers())
        self.assertFalse(streamer.connected.is_set())
        self.assertEqual(events, [{"type": "connected"}, {"type": "transcript", "text": "नमस्ते"}])


async def _record(events, event):
    events.append(event)


if __name__ == "__main__":
    unittest.main()

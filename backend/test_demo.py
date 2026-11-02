import asyncio
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from evon_legal_engine import FormAClaimSlots
from form_a_pdf_generator import compile_form_a
from main import Session
from language_support import MOCK_TRANSCRIPTS, FOLLOWUPS


class EventSocket:
    def __init__(self):
        self.events = []
        self.audio = []

    async def send_json(self, event):
        self.events.append(event)

    async def send_bytes(self, audio):
        self.audio.append(audio)


def test_gnani_base_url_supplies_evon_endpoint_with_explicit_override():
    with patch.dict(os.environ, {
        "GNANI_API_BASE_URL": "https://custom.vachana.test/",
        "GNANI_API_KEY": "offline-test-key",
    }, clear=True):
        session = Session(EventSocket())
        assert session.engine.endpoint_url == "https://custom.vachana.test/llm/evon-v3.3/chat/completions"

    with patch.dict(os.environ, {
        "GNANI_API_BASE_URL": "https://custom.vachana.test",
        "EVON_ENDPOINT_URL": "https://override.test/chat/completions",
        "GNANI_API_KEY": "offline-test-key",
    }, clear=True):
        session = Session(EventSocket())
        assert session.engine.endpoint_url == "https://override.test/chat/completions"


def test_mock_replay_is_synthetic_and_deterministic():
    socket = EventSocket()
    session = Session(socket)
    session.mode = "MOCK_REPLAY"
    session.engine.mode = "MOCK_REPLAY"

    asyncio.run(session.run_demo())

    transcript = next(event for event in socket.events if event["type"] == "prisma_transcript")
    telemetry = next(event for event in socket.events if event["type"] == "prisma_telemetry")
    audit = next(event for event in socket.events if event["type"] == "evon_stage_b_complete")
    claim = next(event for event in socket.events if event["type"] == "evon_stage_a" and not event["missing_fields"])
    assert socket.events[0] == {"type": "session_started", "mode": "MOCK_REPLAY"}
    assert transcript["source"] == "mock"
    assert telemetry["frame_bytes"] == 1024 and telemetry["cadence_ms"] == 64
    assert claim["slots"]["worker_name"] == "Ramesh Kumar Verma"
    assert claim["slots"]["days_worked"] == 18
    assert audit["principal_arrears_inr"] == 10600
    assert any(event["type"] == "timbre_audio" for event in socket.events)


def test_demo_is_disabled_in_live_mode():
    socket = EventSocket()
    session = Session(socket)
    session.mode = "LIVE"
    session.engine.mode = "LIVE"

    asyncio.run(session.run_demo())

    assert len(socket.events) == 1
    assert socket.events[0]["type"] == "notice"


def test_mock_replay_uses_selected_language_for_transcript_and_readback():
    cases = (
        ("kn-IN", "ಸರ್,", "ಹತ್ತು ಸಾವಿರ ಆರು ನೂರು"),
        ("en-IN", "Sir,", "ten thousand six hundred"),
    )
    for language, transcript_start, spoken_amount in cases:
        socket = EventSocket()
        session = Session(socket)
        session.mode = "MOCK_REPLAY"
        session.engine.mode = "MOCK_REPLAY"
        session.language_preference = language

        asyncio.run(session.run_demo())

        status = next(event for event in socket.events if event["type"] == "language_status")
        transcript = next(event for event in socket.events if event["type"] == "prisma_transcript")
        audit = next(event for event in socket.events if event["type"] == "evon_stage_b_complete")
        assert status["effective_language"] == language
        assert transcript["detected_language_code"] == language
        assert transcript["text"].startswith(transcript_start)
        assert spoken_amount in audit["timbre_v3_readback_script"]
        assert not any(character.isdigit() for character in audit["timbre_v3_readback_script"])


def test_auto_language_detection_routes_typed_transcripts_to_localized_followups():
    cases = ("hi-IN", "kn-IN", "en-IN")
    for language in cases:
        socket = EventSocket()
        session = Session(socket)

        asyncio.run(session.on_utterance(MOCK_TRANSCRIPTS[language]))

        status = next(event for event in socket.events if event["type"] == "language_status")
        stage_a = next(event for event in socket.events if event["type"] == "evon_stage_a")
        assert status["language_preference"] == "auto"
        assert status["effective_language"] == language
        assert stage_a["followup"] == FOLLOWUPS[language]["worker_name"]


def test_claim_json_does_not_claim_recorded_voice_consent():
    slots = FormAClaimSlots(worker_name="Synthetic worker")
    with TemporaryDirectory() as output_directory:
        compile_form_a(slots, {"principal_arrears_inr": 0}, Path(output_directory))
        payload = json.loads((Path(output_directory) / "form-a-claim.json").read_text(encoding="utf-8"))
        assert (Path(output_directory) / "form-a-claim.pdf").is_file()

    assert payload["voice_consent_recorded"] is False
    assert payload["voice_consent_sha256"] is None


def test_live_audit_streams_timbre_audio_and_surfaces_failure():
    async def run_success():
        socket = EventSocket()
        session = Session(socket)
        session.mode = "LIVE"
        session.engine.mode = "LIVE"
        session.engine.stage_b_statutory_audit_and_draft = _mock_audit_result
        async def synthesize_with_first_chunk(*args, on_first_audio_chunk):
            await on_first_audio_chunk()
            return b"RIFF mock audio"

        with patch("main.synthesize_timbre_audio", side_effect=synthesize_with_first_chunk) as synthesize:
            await session.audit_and_readback()

        assert socket.audio == [b"RIFF mock audio"]
        assert socket.events[-1] == {"type": "timbre_audio_ready"}
        latency_stages = {
            event["stage"] for event in socket.events if event["type"] == "pipeline_latency"
        }
        assert "evon_stage_b" in latency_stages
        assert "timbre_first_audio_chunk" in latency_stages
        synthesize.assert_called_once()

    async def run_failure():
        socket = EventSocket()
        session = Session(socket)
        session.mode = "LIVE"
        session.engine.mode = "LIVE"
        session.engine.stage_b_statutory_audit_and_draft = _mock_audit_result
        with patch("main.synthesize_timbre_audio", side_effect=RuntimeError("offline test failure")):
            await session.audit_and_readback()

        assert not socket.audio
        assert socket.events[-1] == {
            "type": "timbre_audio_unavailable",
            "message": "offline test failure",
        }

    asyncio.run(run_success())
    asyncio.run(run_failure())


def test_live_prisma_event_reader_stays_available_during_evon_and_confirms_bias():
    async def run():
        socket = EventSocket()
        session = Session(socket)
        session.mode = "LIVE"
        session._pending_bias_request_id = "request-1"
        session._pending_bias_words = ["Peenya", "Thekedar"]
        stage_started = asyncio.Event()
        finish_stage = asyncio.Event()

        async def delayed_stage_a(utterance, current, language):
            stage_started.set()
            await finish_stage.wait()
            return {
                "updated_slots": current.model_dump(),
                "missing_fields": ["worker_name"],
                "followup_question_spoken": "What is your name?",
            }

        session.engine.stage_a_extract_slots = delayed_stage_a
        await session.on_prisma_event({
            "type": "transcript",
            "text": "I worked at Peenya",
            "segment_latency_ms": 84.5,
        })
        await stage_started.wait()

        await session.on_prisma_event({
            "type": "settings_updated",
            "config": {"bias_word_count": 2, "bias_score": 2.0},
        })
        assert any(
            event["type"] == "prisma_settings_updated"
            and event["confirmed_words"] == ["Peenya", "Thekedar"]
            for event in socket.events
        )
        assert any(
            event["type"] == "pipeline_latency"
            and event["stage"] == "prisma_segment"
            and event["latency_ms"] == 84.5
            for event in socket.events
        )

        finish_stage.set()
        await asyncio.gather(*list(session._transcript_tasks))
        assert any(
            event["type"] == "pipeline_latency" and event["stage"] == "evon_stage_a"
            for event in socket.events
        )

    asyncio.run(run())


def test_uan_does_not_claim_a_live_bias_update_when_prisma_is_not_running():
    async def run():
        socket = EventSocket()
        session = Session(socket)

        await session.apply_uan("100492837465")

        assert any(event["type"] == "uan_result" and event["found"] for event in socket.events)
        assert not any(event["type"] == "bias_boost_triggered" for event in socket.events)

    asyncio.run(run())


def test_typed_and_transcribed_localities_update_prisma_bias():
    class RecordingStreamer:
        running = True
        connecting = False

        def __init__(self):
            self.boosted_words = []

        async def boost_locality_vocabulary(self, words):
            self.boosted_words.append(words)
            return words

    async def run():
        async def stage_a(text, slots, language):
            return {
                "updated_slots": slots.model_dump(),
                "missing_fields": ["worker_name"],
                "followup_question_spoken": "What is your name?",
            }

        typed_socket = EventSocket()
        typed_session = Session(typed_socket)
        typed_session.streamer = RecordingStreamer()
        typed_session.engine.stage_a_extract_slots = stage_a
        await typed_session.on_command(json.dumps({
            "type": "utterance",
            "text": "I worked near WHITEFIELD.",
        }))

        transcript_socket = EventSocket()
        transcript_session = Session(transcript_socket)
        transcript_session.streamer = RecordingStreamer()
        transcript_session.engine.stage_a_extract_slots = stage_a
        await transcript_session.on_prisma_event({
            "type": "transcript",
            "text": "My worksite was in Peenya.",
        })
        await asyncio.gather(*list(transcript_session._transcript_tasks))

        assert typed_session.streamer.boosted_words == [["Whitefield"]]
        assert transcript_session.streamer.boosted_words == [["Peenya"]]
        assert any(event["type"] == "bias_boost_triggered" for event in typed_socket.events)
        assert any(event["type"] == "bias_boost_triggered" for event in transcript_socket.events)

    asyncio.run(run())


def test_live_transcript_followup_finishes_audit_and_timbre_readback():
    async def run():
        socket = EventSocket()
        session = Session(socket)
        session.mode = "LIVE"
        session.engine.mode = "LIVE"
        stage_a_calls = 0
        complete_slots = FormAClaimSlots(
            worker_name="Ramesh Kumar",
            worksite_locality_and_sphere="Peenya",
            contractor_name_and_phone="Mohan",
            principal_employer_name="ABC Infrastructure",
            wage_period_start="2026-09-01",
            wage_period_end="2026-09-30",
            days_worked=18,
            agreed_daily_wage_inr=700,
            advance_received_inr=0,
        )

        async def stage_a(utterance, current, language):
            nonlocal stage_a_calls
            stage_a_calls += 1
            if stage_a_calls == 1:
                updated = current.model_copy(update={"worker_name": "Ramesh Kumar"})
                return {
                    "updated_slots": updated.model_dump(),
                    "missing_fields": ["worksite_locality_and_sphere"],
                    "followup_question_spoken": "Where did you work?",
                }
            return {
                "updated_slots": complete_slots.model_dump(),
                "missing_fields": [],
                "followup_question_spoken": "",
            }

        async def synthesize_with_first_chunk(*args, on_first_audio_chunk):
            await on_first_audio_chunk()
            return b"RIFF mock audio"

        session.engine.stage_a_extract_slots = stage_a
        session.engine.stage_b_statutory_audit_and_draft = _mock_audit_result
        with patch("main.synthesize_timbre_audio", side_effect=synthesize_with_first_chunk):
            await session.on_prisma_event({
                "type": "transcript",
                "text": "My name is Ramesh Kumar",
                "detected_language_code": "en-IN",
                "segment_latency_ms": 42.0,
            })
            await asyncio.gather(*list(session._transcript_tasks))
            await session.on_prisma_event({
                "type": "transcript",
                "text": "I worked at Peenya",
                "detected_language_code": "en-IN",
                "segment_latency_ms": 56.0,
            })
            await asyncio.gather(*list(session._transcript_tasks))

        stage_a_events = [event for event in socket.events if event["type"] == "evon_stage_a"]
        assert stage_a_calls == 2
        assert stage_a_events[0]["followup"] == "Where did you work?"
        assert stage_a_events[1]["missing_fields"] == []
        assert any(event["type"] == "evon_stage_b_complete" for event in socket.events)
        assert socket.audio == [b"RIFF mock audio"]
        latency_stages = {
            event["stage"] for event in socket.events if event["type"] == "pipeline_latency"
        }
        assert latency_stages == {
            "prisma_segment", "evon_stage_a", "evon_stage_b", "timbre_first_audio_chunk",
        }

    asyncio.run(run())


async def _mock_audit_result(slots, language="hi-IN"):
    return {
        "thinking_trace": "",
        "result": {
            "principal_arrears_inr": 0,
            "timbre_v3_readback_script": "<slow>शून्य रुपये</slow>",
        },
    }

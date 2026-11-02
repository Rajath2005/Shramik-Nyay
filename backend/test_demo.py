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
        with patch("main.synthesize_timbre_audio", return_value=b"RIFF mock audio") as synthesize:
            await session.audit_and_readback()

        assert socket.audio == [b"RIFF mock audio"]
        assert socket.events[-1] == {"type": "timbre_audio_ready"}
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


async def _mock_audit_result(slots):
    return {
        "thinking_trace": "",
        "result": {
            "principal_arrears_inr": 0,
            "timbre_v3_readback_script": "<slow>शून्य रुपये</slow>",
        },
    }

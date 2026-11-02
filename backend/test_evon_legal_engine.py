import asyncio
import unittest
from unittest.mock import patch

from evon_legal_engine import EvonLegalEngine, FormAClaimSlots, MODEL_NAME, STAGE_A_PROMPT
from language_support import FOLLOWUPS


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": '{"ok": true}'}}]}


class FakeAsyncClient:
    def __init__(self, *, timeout):
        self.timeout = timeout
        self.request = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def post(self, url, *, json, headers):
        self.request = {"url": url, "payload": json, "headers": headers}
        return FakeResponse()


class EvonLegalEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_stage_a_and_b_use_blueprint_model_settings_and_auth(self):
        engine = EvonLegalEngine("https://evon.example/v1/chat/completions", "offline-test-key", "LIVE")
        for thinking, penalty, max_tokens in ((False, 1.1, 2048), (True, 1.0, 16384)):
            with self.subTest(thinking=thinking):
                client = FakeAsyncClient(timeout=15)
                with patch("evon_legal_engine.httpx.AsyncClient", return_value=client):
                    response = await engine._chat(
                        [{"role": "system", "content": STAGE_A_PROMPT}],
                        thinking=thinking,
                        timeout=15,
                    )

                self.assertEqual(response["content"], '{"ok": true}')
                self.assertEqual(client.request["url"], engine.endpoint_url)
                self.assertEqual(client.request["headers"], {"Authorization": "Bearer offline-test-key"})
                self.assertEqual(client.request["payload"], {
                    "model": MODEL_NAME,
                    "messages": [{"role": "system", "content": STAGE_A_PROMPT}],
                    "temperature": 0.6,
                    "top_p": 0.95,
                    "repetition_penalty": penalty,
                    "max_tokens": max_tokens,
                    "chat_template_kwargs": {"enable_thinking": thinking},
                    "stream": False,
                })

    async def test_live_request_requires_endpoint_and_api_key(self):
        for endpoint, api_key, expected in (
            ("", "offline-test-key", "EVON_ENDPOINT_URL"),
            ("https://evon.example/v1/chat/completions", "", "GNANI_API_KEY"),
        ):
            with self.subTest(missing=expected):
                engine = EvonLegalEngine(endpoint, api_key, "LIVE")
                with patch("evon_legal_engine.httpx.AsyncClient") as client:
                    with self.assertRaisesRegex(RuntimeError, expected):
                        await engine._chat([], thinking=False, timeout=1)
                client.assert_not_called()

    async def test_stage_a_merges_model_slots_without_recomputing_arrears(self):
        engine = EvonLegalEngine("offline", "offline", "LIVE")
        call = {}

        async def mock_stage_a(messages, *, thinking, timeout):
            call.update(thinking=thinking, timeout=timeout)
            return {"content": (
                '{"updated_slots": {"worker_name": "Ramesh", '
                '"worksite_locality_and_sphere": "Peenya", "unknown": "ignored"}, '
                '"missing_fields": ["days_worked"], '
                '"followup_question_spoken": "कुल कितने दिन काम किया?"}'
            )}

        engine._chat = mock_stage_a
        result = await engine.stage_a_extract_slots(
            "My name is Ramesh and I worked at Peenya.",
            FormAClaimSlots(),
        )

        self.assertEqual(result["updated_slots"]["worker_name"], "Ramesh")
        self.assertEqual(result["updated_slots"]["worksite_locality_and_sphere"], "Peenya")
        self.assertIsNone(result["updated_slots"]["days_worked"])
        self.assertIn("days_worked", result["missing_fields"])
        self.assertEqual(result["followup_question_spoken"], FOLLOWUPS["hi-IN"][result["missing_fields"][0]])
        self.assertEqual(result["missing_fields"][0], "contractor_name_and_phone")

        self.assertEqual(call, {"thinking": False, "timeout": 15.0})

    async def test_stage_b_keeps_wage_calculation_deterministic(self):
        engine = EvonLegalEngine("offline", "offline", "LIVE")
        call = {}

        async def mock_stage_b(messages, *, thinking, timeout):
            call.update(thinking=thinking, timeout=timeout)
            return {
                "content": '{"legal_audit_summary": "Draft summary", "form_a_clauses": ["Draft clause"]}',
                "reasoning_content": "offline test trace",
            }

        engine._chat = mock_stage_b
        slots = FormAClaimSlots(
            worker_name="Synthetic worker",
            worksite_locality_and_sphere="Peenya",
            contractor_name_and_phone="Demo contractor",
            principal_employer_name="Demo employer",
            days_worked=18,
            agreed_daily_wage_inr=700,
            advance_received_inr=2000,
        )

        output = await engine.stage_b_statutory_audit_and_draft(slots)

        self.assertEqual(output["result"]["principal_arrears_inr"], 10600)
        self.assertEqual(output["result"]["legal_audit_summary"], "Draft summary")
        self.assertEqual(output["thinking_trace"], "offline test trace")
        self.assertEqual(call, {"thinking": True, "timeout": 60.0})


if __name__ == "__main__":
    unittest.main()

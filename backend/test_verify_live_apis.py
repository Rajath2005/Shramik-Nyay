import unittest

from verify_live_apis import wait_for_settings_updated


class FakeWebSocket:
    def __init__(self, events):
        self.events = iter(events)

    async def recv(self):
        return next(self.events)


class LiveApiVerifierTests(unittest.IsolatedAsyncioTestCase):
    async def test_prisma_settings_updated_event_matches_documented_shape(self):
        event = (
            '{"type":"settings_updated","timestamp":"2026-11-02T10:00:00Z",'
            '"config":{"language_code":"hi-IN,en-IN","format":"transcribe",'
            '"itn_native_numerals":false,"substitution_enabled":false,'
            '"bias_word_count":4,"bias_score":2.0}}'
        )

        await wait_for_settings_updated(
            FakeWebSocket([event]),
            expected_bias_count=4,
            expected_bias_score=2.0,
        )

    async def test_prisma_settings_updated_rejects_wrong_bias_count(self):
        event = (
            '{"type":"settings_updated","timestamp":"2026-11-02T10:00:00Z",'
            '"config":{"language_code":"hi-IN,en-IN","format":"transcribe",'
            '"itn_native_numerals":false,"substitution_enabled":false,'
            '"bias_word_count":3,"bias_score":2.0}}'
        )

        with self.assertRaisesRegex(RuntimeError, "expected 4"):
            await wait_for_settings_updated(
                FakeWebSocket([event]),
                expected_bias_count=4,
                expected_bias_score=2.0,
            )

    async def test_prisma_server_error_is_reported(self):
        with self.assertRaisesRegex(RuntimeError, "Prisma API error"):
            await wait_for_settings_updated(
                FakeWebSocket(['{"type":"error","message":"invalid setting"}']),
                expected_bias_count=4,
                expected_bias_score=2.0,
            )


if __name__ == "__main__":
    unittest.main()

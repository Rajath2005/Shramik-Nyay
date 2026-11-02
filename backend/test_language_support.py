import unittest

from language_support import (
    FOLLOWUPS,
    MOCK_TRANSCRIPTS,
    number_to_spoken_words,
    prisma_language_code,
    readback_script,
    resolve_language,
    validate_language,
)


class LanguageSupportTests(unittest.TestCase):
    def test_auto_and_explicit_language_resolution(self):
        self.assertEqual(prisma_language_code("auto"), "indic-auto")
        self.assertEqual(prisma_language_code("hi-IN"), "hi-IN,en-IN")
        self.assertEqual(prisma_language_code("kn-IN"), "kn-IN,en-IN")
        self.assertEqual(prisma_language_code("en-IN"), "en-IN")
        self.assertEqual(resolve_language("auto", text=MOCK_TRANSCRIPTS["kn-IN"]), "kn-IN")
        self.assertEqual(resolve_language("auto", text=MOCK_TRANSCRIPTS["hi-IN"]), "hi-IN")
        self.assertEqual(resolve_language("auto", text=MOCK_TRANSCRIPTS["en-IN"]), "en-IN")
        self.assertEqual(resolve_language("auto", detected="kn-IN"), "kn-IN")
        self.assertEqual(resolve_language("en-IN", detected="kn-IN"), "en-IN")

    def test_followups_and_speech_amounts_cover_all_supported_languages(self):
        expectations = {
            "hi-IN": ("अठारह", "दस हज़ार छह सौ"),
            "kn-IN": ("ಹದಿನೆಂಟು", "ಹತ್ತು ಸಾವಿರ ಆರು ನೂರು"),
            "en-IN": ("eighteen", "ten thousand six hundred"),
        }
        for language, (spoken_eighteen, spoken_total) in expectations.items():
            with self.subTest(language=language):
                self.assertEqual(len(FOLLOWUPS[language]), 9)
                self.assertEqual(number_to_spoken_words(18, language), spoken_eighteen)
                self.assertEqual(number_to_spoken_words(10600, language), spoken_total)
                self.assertNotRegex(readback_script(10600, language), r"\d")
                self.assertIn(spoken_total, readback_script(10600, language))

    def test_language_validation_rejects_unsupported_options(self):
        self.assertEqual(validate_language("auto"), "auto")
        with self.assertRaisesRegex(ValueError, "language must be"):
            validate_language("fr-FR")


if __name__ == "__main__":
    unittest.main()

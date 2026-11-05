import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics

from evon_legal_engine import FormAClaimSlots
from form_a_pdf_generator import compile_form_a
from legal_rules import NOTICE, compute_claim


def _normalized_pdf_text(path: Path) -> str:
    text = " ".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return re.sub(r"\s+", " ", text)


class FormAPdfGeneratorTests(unittest.TestCase):
    def test_pdf_always_marks_not_filed_without_synthetic_label_for_live_data(self):
        with TemporaryDirectory() as output_directory:
            path = compile_form_a(
                FormAClaimSlots(worker_name="Live worker"),
                {"principal_arrears_inr": 0},
                Path(output_directory),
                language="en-IN",
            )
            text = _normalized_pdf_text(path)

        self.assertIn("DRAFT - not filed", text)
        self.assertNotIn("synthetic demo data", text)

    def test_pdf_extracts_hindi_kannada_and_english_text(self):
        cases = {
            "hi-IN": (
                [
                    "आवेदक ने मजदूरी का दावा प्रस्तुत किया।",
                    "ठेकेदार और प्रधान नियोक्ता प्रतिपक्षी हैं।",
                    "निर्धारित अवधि का वेतन समय पर नहीं दिया गया।",
                    "मूल बकाया 10,600 रुपये है।",
                    "कानून के अनुसार मुआवजा मांगा गया है।",
                ],
                [
                    "आवेदक की पहचान और पता",
                    "प्रतिपक्षी: ठेकेदार और प्रधान नियोक्ता",
                    "वेतन अवधि, भुगतान में देरी और कटौतियाँ",
                    "मांगी गई राहत की राशि",
                    "मुआवजे के लिए प्रार्थना",
                ],
                "आवेदक का पता उपलब्ध नहीं",
                "आवेदक के हस्ताक्षर / अंगूठे का निशान",
            ),
            "kn-IN": (
                [
                    "ಅರ್ಜಿದಾರರು ವೇತನದ ದಾವೆ ಸಲ್ಲಿಸಿದ್ದಾರೆ.",
                    "ಗುತ್ತಿಗೆದಾರ ಮತ್ತು ಪ್ರಧಾನ ಉದ್ಯೋಗದಾತ ಪ್ರತಿವಾದಿಗಳು.",
                    "ನಿಗದಿತ ಅವಧಿಯ ವೇತನವನ್ನು ಸಮಯಕ್ಕೆ ಪಾವತಿಸಿಲ್ಲ.",
                    "ಮೂಲ ಬಾಕಿ 10,600 ರೂಪಾಯಿ.",
                    "ಕಾನೂನಿನ ಪ್ರಕಾರ ಪರಿಹಾರವನ್ನು ಕೋರಲಾಗಿದೆ.",
                ],
                [
                    "ಅರ್ಜಿದಾರರ ಗುರುತು ಮತ್ತು ವಿಳಾಸ",
                    "ಪ್ರತಿವಾದಿಗಳು",
                    "ವೇತನ ಅವಧಿ, ವಿಳಂಬ ಮತ್ತು ಕಡಿತಗಳು",
                    "ಕೋರಿರುವ ಪರಿಹಾರದ ಮೊತ್ತ",
                    "ಪರಿಹಾರಕ್ಕಾಗಿ ಪ್ರಾರ್ಥನೆ",
                ],
                "ಅರ್ಜಿದಾರರ ವಿಳಾಸ ನೀಡಿಲ್ಲ",
                "ಅರ್ಜಿದಾರರ ಸಹಿ / ಹೆಬ್ಬೆರಳಿನ ಗುರುತು",
            ),
            "en-IN": (
                [
                    "The applicant submits a claim for unpaid wages.",
                    "The contractor and principal employer are the opposite parties.",
                    "Wages for the stated period were not paid on time.",
                    "Principal arrears are INR 10,600.",
                    "Compensation is requested as permitted by law.",
                ],
                [
                    "Applicant identity and address",
                    "Opposite parties: contractor and principal employer",
                    "Wage period, payment delay, and deductions",
                    "Relief amount",
                    "Prayer for compensation",
                ],
                "Applicant address Not provided",
                "Applicant signature / thumb impression",
            ),
        }
        slots = FormAClaimSlots(
            worker_name="Synthetic worker",
            eshram_uan="100492837465",
            worksite_locality_and_sphere="Peenya Industrial Area",
            contractor_name_and_phone="Demo contractor, 9000000000",
            principal_employer_name="Demo principal employer",
            wage_period_start="2026-09-01",
            wage_period_end="2026-09-18",
            days_worked=18,
            agreed_daily_wage_inr=700,
            advance_received_inr=2000,
            unlawful_deductions_inr=500,
        )
        audit = compute_claim(
            days_worked=slots.days_worked,
            daily_wage=slots.agreed_daily_wage_inr,
            advance_received=slots.advance_received_inr or 0,
            unlawful_deductions=slots.unlawful_deductions_inr or 0,
            wage_period_start=slots.wage_period_start,
            wage_period_end=slots.wage_period_end,
        )
        delay_labels = {
            "hi-IN": "देरी हुई",
            "kn-IN": "ವಿಳಂಬವಾಗಿದೆ",
            "en-IN": "Delayed",
        }

        for language, (clauses, headings, missing_address, signature) in cases.items():
            with self.subTest(language=language), TemporaryDirectory() as output_directory:
                path = compile_form_a(
                    slots,
                    {**audit, "form_a_clauses": clauses},
                    Path(output_directory),
                    language=language,
                    synthetic_demo_data=True,
                )
                text = _normalized_pdf_text(path)

            self.assertTrue(pdfmetrics.getFont("NotoSansDevanagari").shapable)
            self.assertTrue(pdfmetrics.getFont("NotoSansKannada").shapable)
            for clause in clauses:
                self.assertIn(clause, text)
            for heading in headings:
                self.assertIn(heading, text)
            self.assertIn(missing_address, text)
            self.assertIn(signature, text)
            self.assertIn(delay_labels[language], text)
            self.assertIn("DRAFT - not filed - synthetic demo data", text)
            self.assertIn("Demo contractor, 9000000000", text)
            self.assertIn("Demo principal employer", text)
            self.assertIn("2026-09-01 - 2026-09-18", text)
            self.assertIn("10,600", text)
            self.assertIn("5,000", text)
            self.assertIn("12,600", text)
            self.assertIn(re.sub(r"\s+", " ", NOTICE), text)

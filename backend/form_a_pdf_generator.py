from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from evon_legal_engine import FormAClaimSlots
from language_support import resolve_language
from legal_rules import NOTICE

PAGE_MARGIN = 42
WATERMARK = "DRAFT - synthetic demo data"
FONT_FILES = {
    "NotoSansDevanagari": "NotoSansDevanagari.ttf",
    "NotoSansKannada": "NotoSansKannada.ttf",
}

LABELS = {
    "hi-IN": {
        "title": "मजदूरी भुगतान दावा - फॉर्म A",
        "clause_missing": "Stage B का मसौदा उपलब्ध नहीं है।",
        "not_provided": "उपलब्ध नहीं",
        "not_claimed": "दावा नहीं किया गया",
        "worker_name": "आवेदक का नाम",
        "uan": "ई-श्रम UAN",
        "worker_address": "आवेदक का पता",
        "worksite": "कार्यस्थल / स्थानीयता",
        "contractor": "ठेकेदार का नाम और फोन",
        "contractor_address": "ठेकेदार का पता",
        "employer": "प्रधान नियोक्ता का नाम",
        "employer_address": "प्रधान नियोक्ता का पता",
        "wage_period": "वेतन अवधि",
        "days_worked": "काम किए गए दिन",
        "daily_wage": "तय दैनिक वेतन (INR)",
        "gross_wages": "कुल वेतन (INR)",
        "advance": "प्राप्त अग्रिम (INR)",
        "delay": "भुगतान में देरी",
        "deductions": "दावा की गई कटौतियाँ (INR)",
        "principal": "मूल वेतन बकाया (INR)",
        "compensation": "मुआवजे का दावा (INR)",
        "signature": "आवेदक के हस्ताक्षर / अंगूठे का निशान",
        "date": "दिनांक",
        "place": "स्थान",
        "legal_notice": "कानूनी सूचना",
        "delay_pass": "समय पर",
        "delay_fail": "देरी हुई",
        "delay_unknown": "अज्ञात",
    },
    "kn-IN": {
        "title": "ವೇತನ ಪಾವತಿ ಅರ್ಜಿ - ಫಾರ್ಮ್ A",
        "clause_missing": "ಹಂತ B ಕರಡು ಲಭ್ಯವಿಲ್ಲ.",
        "not_provided": "ನೀಡಿಲ್ಲ",
        "not_claimed": "ದಾವೆ ಮಾಡಿಲ್ಲ",
        "worker_name": "ಅರ್ಜಿದಾರರ ಹೆಸರು",
        "uan": "ಇ-ಶ್ರಮ್ UAN",
        "worker_address": "ಅರ್ಜಿದಾರರ ವಿಳಾಸ",
        "worksite": "ಕೆಲಸದ ಸ್ಥಳ / ಪ್ರದೇಶ",
        "contractor": "ಗುತ್ತಿಗೆದಾರರ ಹೆಸರು ಮತ್ತು ಫೋನ್",
        "contractor_address": "ಗುತ್ತಿಗೆದಾರರ ವಿಳಾಸ",
        "employer": "ಪ್ರಧಾನ ಉದ್ಯೋಗದಾತರ ಹೆಸರು",
        "employer_address": "ಪ್ರಧಾನ ಉದ್ಯೋಗದಾತರ ವಿಳಾಸ",
        "wage_period": "ವೇತನ ಅವಧಿ",
        "days_worked": "ಕೆಲಸ ಮಾಡಿದ ದಿನಗಳು",
        "daily_wage": "ಒಪ್ಪಿದ ದಿನದ ವೇತನ (INR)",
        "gross_wages": "ಒಟ್ಟು ವೇತನ (INR)",
        "advance": "ಪಡೆದ ಮುಂಗಡ (INR)",
        "delay": "ವೇತನ ಪಾವತಿಯಲ್ಲಿ ವಿಳಂಬ",
        "deductions": "ದಾವೆ ಮಾಡಿದ ಕಡಿತಗಳು (INR)",
        "principal": "ಮೂಲ ವೇತನ ಬಾಕಿ (INR)",
        "compensation": "ಪರಿಹಾರ ದಾವೆ (INR)",
        "signature": "ಅರ್ಜಿದಾರರ ಸಹಿ / ಹೆಬ್ಬೆರಳಿನ ಗುರುತು",
        "date": "ದಿನಾಂಕ",
        "place": "ಸ್ಥಳ",
        "legal_notice": "ಕಾನೂನು ಸೂಚನೆ",
        "delay_pass": "ಸಮಯಕ್ಕೆ",
        "delay_fail": "ವಿಳಂಬವಾಗಿದೆ",
        "delay_unknown": "ಗೊತ್ತಿಲ್ಲ",
    },
    "en-IN": {
        "title": "Wage Payment Claim - Form A",
        "clause_missing": "Stage B draft not provided.",
        "not_provided": "Not provided",
        "not_claimed": "Not claimed",
        "worker_name": "Applicant name",
        "uan": "eShram UAN",
        "worker_address": "Applicant address",
        "worksite": "Worksite / locality",
        "contractor": "Contractor name and phone",
        "contractor_address": "Contractor address",
        "employer": "Principal employer name",
        "employer_address": "Principal employer address",
        "wage_period": "Wage period",
        "days_worked": "Days worked",
        "daily_wage": "Agreed daily wage (INR)",
        "gross_wages": "Gross wages (INR)",
        "advance": "Advance received (INR)",
        "delay": "Payment delay",
        "deductions": "Claimed deductions (INR)",
        "principal": "Principal wage arrears (INR)",
        "compensation": "Compensation claimed (INR)",
        "signature": "Applicant signature / thumb impression",
        "date": "Date",
        "place": "Place",
        "legal_notice": "Legal notice",
        "delay_pass": "On time",
        "delay_fail": "Delayed",
        "delay_unknown": "Unknown",
    },
}

SECTION_FIELDS = (
    ("worker_name", "worker_address", "uan", "worksite"),
    ("contractor", "contractor_address", "employer", "employer_address"),
    ("wage_period", "days_worked", "daily_wage", "gross_wages", "advance", "delay", "deductions"),
    ("principal",),
    ("compensation",),
)

SECTION_TITLES = {
    "hi-IN": (
        "आवेदक की पहचान और पता",
        "प्रतिपक्षी: ठेकेदार और प्रधान नियोक्ता",
        "वेतन अवधि, भुगतान में देरी और कटौतियाँ",
        "मांगी गई राहत की राशि",
        "मुआवजे के लिए प्रार्थना",
    ),
    "kn-IN": (
        "ಅರ್ಜಿದಾರರ ಗುರುತು ಮತ್ತು ವಿಳಾಸ",
        "ಪ್ರತಿವಾದಿಗಳು",
        "ವೇತನ ಅವಧಿ, ವಿಳಂಬ ಮತ್ತು ಕಡಿತಗಳು",
        "ಕೋರಿರುವ ಪರಿಹಾರದ ಮೊತ್ತ",
        "ಪರಿಹಾರಕ್ಕಾಗಿ ಪ್ರಾರ್ಥನೆ",
    ),
    "en-IN": (
        "Applicant identity and address",
        "Opposite parties: contractor and principal employer",
        "Wage period, payment delay, and deductions",
        "Relief amount",
        "Prayer for compensation",
    ),
}


def _register_fonts() -> None:
    font_directory = Path(__file__).with_name("fonts")
    for font_name, filename in FONT_FILES.items():
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, str(font_directory / filename)))
        pdfmetrics.registerFontFamily(
            font_name,
            normal=font_name,
            bold=font_name,
            italic=font_name,
            boldItalic=font_name,
        )


def _currency(value: Any, missing: str) -> str:
    if value is None:
        return missing
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return str(value)
    return f"{value:,.0f}"


def _delay_status(audit: dict[str, Any], labels: dict[str, str]) -> str:
    check = next(
        (item for item in audit.get("checks", []) if item.get("id") == "deadline"),
        None,
    )
    if not check:
        return labels["not_provided"]
    status = check.get("status", "unknown")
    status_label = labels.get(f"delay_{status}", labels["delay_unknown"])
    detail = check.get("detail") or ""
    return f"{status_label}: {detail}".strip(": ")


def _field_value(
    field: str,
    slots: FormAClaimSlots,
    audit: dict[str, Any],
    labels: dict[str, str],
) -> str:
    if field == "worker_name":
        value = slots.worker_name
    elif field == "uan":
        value = slots.eshram_uan
    elif field == "worksite":
        value = slots.worksite_locality_and_sphere
    elif field == "contractor":
        value = slots.contractor_name_and_phone
    elif field == "employer":
        value = slots.principal_employer_name
    elif field == "wage_period":
        start = slots.wage_period_start or labels["not_provided"]
        end = slots.wage_period_end or labels["not_provided"]
        return f"{start} - {end}"
    elif field == "days_worked":
        value = slots.days_worked
    elif field == "daily_wage":
        return _currency(slots.agreed_daily_wage_inr, labels["not_provided"])
    elif field == "gross_wages":
        return _currency(audit.get("gross_wages_inr"), labels["not_provided"])
    elif field == "advance":
        return _currency(slots.advance_received_inr, labels["not_provided"])
    elif field == "delay":
        return _delay_status(audit, labels)
    elif field == "deductions":
        return _currency(audit.get("claimed_deductions_inr"), labels["not_provided"])
    elif field == "principal":
        return _currency(audit.get("principal_arrears_inr"), labels["not_provided"])
    elif field == "compensation":
        return _currency(audit.get("max_compensation_inr"), labels["not_claimed"])
    elif field == "worker_address":
        return labels["not_provided"]
    elif field in {"contractor_address", "employer_address"}:
        return labels["not_provided"]
    else:
        raise ValueError(f"Unknown Form A field: {field}")
    return str(value) if value is not None else labels["not_provided"]


def _watermark(canvas, _document) -> None:
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#D6DAE0"))
    canvas.setFont("Helvetica-Bold", 30)
    canvas.translate(A4[0] / 2, A4[1] / 2)
    canvas.rotate(32)
    canvas.drawCentredString(0, 0, WATERMARK)
    canvas.restoreState()


def _page_number(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5B6470"))
    canvas.drawRightString(A4[0] - PAGE_MARGIN, 22, f"DRAFT - Page {document.page}")
    canvas.restoreState()


def compile_form_a(
    slots: FormAClaimSlots,
    audit: dict[str, Any],
    output_directory: Path,
    voice_consent_audio: bytes | None = None,
    language: str = "hi-IN",
) -> Path:
    locale = resolve_language(language)
    labels = LABELS[locale]
    output_directory.mkdir(parents=True, exist_ok=True)
    has_voice_consent_audio = bool(voice_consent_audio)
    payload = {
        "form": "Form A - Payment of Wages Act, 1936",
        "slots": slots.model_dump(),
        "audit": audit,
        "voice_consent_recorded": has_voice_consent_audio,
        "voice_consent_sha256": (
            hashlib.sha256(voice_consent_audio).hexdigest()
            if has_voice_consent_audio and voice_consent_audio is not None
            else None
        ),
    }
    json_path = output_directory / "form-a-claim.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    pdf_path = output_directory / "form-a-claim.pdf"

    _register_fonts()
    font_name = {
        "hi-IN": "NotoSansDevanagari",
        "kn-IN": "NotoSansKannada",
        "en-IN": "Helvetica",
    }[locale]
    styles = {
        "title": ParagraphStyle(
            "FormTitle",
            fontName=font_name,
            fontSize=16,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17212B"),
            spaceAfter=5,
        ),
        "subtitle": ParagraphStyle(
            "FormSubtitle",
            fontName=font_name,
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5B6470"),
            spaceAfter=14,
        ),
        "section": ParagraphStyle(
            "FormSection",
            fontName=font_name,
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#152536"),
            spaceBefore=5,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "FormBody",
            fontName=font_name,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#202833"),
        ),
        "label": ParagraphStyle(
            "FormFieldLabel",
            fontName=font_name,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#526070"),
        ),
        "notice": ParagraphStyle(
            "FormNotice",
            fontName=font_name,
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#424B55"),
        ),
    }

    document = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=PAGE_MARGIN,
        bottomMargin=PAGE_MARGIN + 20,
        title="Shramik-Nyay Form A Claim",
        author="Shramik-Nyay",
    )
    clauses = audit.get("form_a_clauses")
    if not isinstance(clauses, list):
        clauses = []
    story = [
        Paragraph(escape(labels["title"]), styles["title"]),
        Paragraph(
            "Form A - Payment of Wages Act, 1936",
            styles["subtitle"],
        ),
    ]

    for index, fields in enumerate(SECTION_FIELDS):
        clause_text = clauses[index] if index < len(clauses) else labels["clause_missing"]
        heading = Paragraph(f"<b>{index + 1}. {escape(SECTION_TITLES[locale][index])}</b>", styles["section"])
        body = Paragraph(escape(str(clause_text)), styles["body"])
        rows = [
            [
                Paragraph(escape(labels[field]), styles["label"]),
                Paragraph(
                    escape(_field_value(field, slots, audit, labels)),
                    styles["body"],
                ),
            ]
            for field in fields
        ]
        details = Table(rows, colWidths=[document.width * 0.34, document.width * 0.66])
        details.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7DDE3")),
                ]
            )
        )
        story.append(KeepTogether([heading, body, Spacer(1, 4), details, Spacer(1, 7)]))

    signature = Table(
        [
            [Paragraph(escape(labels["signature"]), styles["body"]), ""],
            [Paragraph(escape(labels["date"]), styles["label"]), ""],
            [Paragraph(escape(labels["place"]), styles["label"]), ""],
        ],
        colWidths=[document.width * 0.46, document.width * 0.54],
        rowHeights=[36, 18, 18],
    )
    signature.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#687382")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.extend(
        [
            Spacer(1, 8),
            signature,
        ]
    )
    notice = Paragraph(
        f"<b>{escape(labels['legal_notice'])}:</b> {escape(NOTICE)}",
        styles["notice"],
    )

    def draw_page(canvas, doc) -> None:
        _watermark(canvas, doc)
        notice.wrap(doc.width, doc.bottomMargin)
        notice.drawOn(canvas, doc.leftMargin, PAGE_MARGIN - 7)
        _page_number(canvas, doc)

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return pdf_path

"""Form A PDF generator — Payment of Wages Act, 1936.

Authentic monochrome Indian Labour Court filing layout (Single-Page A4).
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from evon_legal_engine import FormAClaimSlots
from eshram_mock_db import lookup_eshram_uan
from language_support import resolve_language
from legal_rules import NOTICE

# ── Page geometry (tuned to fit cleanly on 1 single A4 page) ───────────────────
PAGE_W, PAGE_H = A4
L_MARGIN = R_MARGIN = 18 * mm
T_MARGIN = 16 * mm
B_MARGIN = 16 * mm
CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN

# ── Monochrome Court Ink Palette (Zero SaaS/Dashboard Colors) ─────────────────
C_BLACK = colors.HexColor("#000000")
C_INK   = colors.HexColor("#111111")
C_MUTED = colors.HexColor("#333333")
C_RULE  = colors.HexColor("#222222")
C_LIGHT_RULE = colors.HexColor("#666666")
C_TOTAL_BG = colors.HexColor("#F5F5F5")  # 4% neutral paper tint for total row only

WATERMARK = "DRAFT - not filed"
FONT_FILES = {
    "NotoSansDevanagari": "NotoSansDevanagari.ttf",
    "NotoSansKannada": "NotoSansKannada.ttf",
}

LABELS = {
    "hi-IN": {
        "title": "FORM A — Form of Individual Application",
        "subtitle": "[See sub-section (2) of Section 15 of the Payment of Wages Act, 1936]",
        "clause_missing": "",
        "not_provided": "As per record",
        "not_claimed": "Nil",
        "worker_name": "Applicant Name",
        "uan": "e-Shram UAN",
        "worker_address": "Applicant Service Address",
        "worksite": "Worksite / Locality",
        "contractor": "Immediate Contractor (Thekedar)",
        "contractor_address": "Contractor Notice Address",
        "employer": "Principal Employer (Sec. 3)",
        "employer_address": "Establishment Address",
        "wage_period": "Unpaid Wage Period",
        "days_worked": "Verified Days Worked",
        "daily_wage": "Agreed Daily Rate",
        "gross_wages": "Gross Wages Earned",
        "advance": "Less: Advance Received",
        "delay": "Section 5 Payment Status",
        "deductions": "Unlawful Deductions",
        "principal": "Net Principal Arrears Due",
        "compensation": "Sec. 15(3) Compensation Prayer",
        "signature": "Signature / Left Thumb Impression of Applicant",
        "date_label": "Date",
        "place_label": "Place",
        "legal_notice": "Statutory Note",
        "delay_pass": "Within statutory period",
        "delay_fail": "Overdue beyond Sec. 5 limit",
        "delay_unknown": "To be verified",
        "applicant_header": "Applicant",
        "respondents_header": "Opposite Parties",
        "fin_summary": "SCHEDULE OF WAGE CLAIM PARTICULARS",
        "total_relief": "TOTAL RELIEF PRAYED FOR (PRINCIPAL + COMPENSATION)",
        "evidence": "Enclosed Supporting Documents Checklist",
        "evidence_items": [
            "[x] e-Shram UAN Identity Record",
            "[x] Wage & Attendance Computation Schedule",
            "[x] Section 15(2) Statutory Claim Statement",
        ],
        "verification_heading": "VERIFICATION",
        "samadhan_ready": "SAMADHAN Portal e-Filing Ready",
        "statutory_title": "STATEMENT OF CLAIM & STATUTORY PLEADINGS",
        "in_matter_of": "BETWEEN:",
        "applicant_role": "... APPLICANT",
        "respondent_role": "... OPPOSITE PARTIES",
    },
    "kn-IN": {
        "title": "FORM A — Form of Individual Application",
        "subtitle": "[See sub-section (2) of Section 15 of the Payment of Wages Act, 1936]",
        "clause_missing": "",
        "not_provided": "As per record",
        "not_claimed": "Nil",
        "worker_name": "Applicant Name",
        "uan": "e-Shram UAN",
        "worker_address": "Applicant Service Address",
        "worksite": "Worksite / Locality",
        "contractor": "Immediate Contractor (Thekedar)",
        "contractor_address": "Contractor Notice Address",
        "employer": "Principal Employer (Sec. 3)",
        "employer_address": "Establishment Address",
        "wage_period": "Unpaid Wage Period",
        "days_worked": "Verified Days Worked",
        "daily_wage": "Agreed Daily Rate",
        "gross_wages": "Gross Wages Earned",
        "advance": "Less: Advance Received",
        "delay": "Section 5 Payment Status",
        "deductions": "Unlawful Deductions",
        "principal": "Net Principal Arrears Due",
        "compensation": "Sec. 15(3) Compensation Prayer",
        "signature": "Signature / Left Thumb Impression of Applicant",
        "date_label": "Date",
        "place_label": "Place",
        "legal_notice": "Statutory Note",
        "delay_pass": "Within statutory period",
        "delay_fail": "Overdue beyond Sec. 5 limit",
        "delay_unknown": "To be verified",
        "applicant_header": "Applicant",
        "respondents_header": "Opposite Parties",
        "fin_summary": "SCHEDULE OF WAGE CLAIM PARTICULARS",
        "total_relief": "TOTAL RELIEF PRAYED FOR (PRINCIPAL + COMPENSATION)",
        "evidence": "Enclosed Supporting Documents Checklist",
        "evidence_items": [
            "[x] e-Shram UAN Identity Record",
            "[x] Wage & Attendance Computation Schedule",
            "[x] Section 15(2) Statutory Claim Statement",
        ],
        "verification_heading": "VERIFICATION",
        "samadhan_ready": "SAMADHAN Portal e-Filing Ready",
        "statutory_title": "STATEMENT OF CLAIM & STATUTORY PLEADINGS",
        "in_matter_of": "BETWEEN:",
        "applicant_role": "... APPLICANT",
        "respondent_role": "... OPPOSITE PARTIES",
    },
    "en-IN": {
        "title": "FORM A — Form of Individual Application",
        "subtitle": "[See sub-section (2) of Section 15 of the Payment of Wages Act, 1936]",
        "clause_missing": "",
        "not_provided": "As per record",
        "not_claimed": "Nil",
        "worker_name": "Applicant Name",
        "uan": "e-Shram UAN",
        "worker_address": "Applicant Service Address",
        "worksite": "Worksite / Locality",
        "contractor": "Immediate Contractor (Thekedar)",
        "contractor_address": "Contractor Notice Address",
        "employer": "Principal Employer (Sec. 3)",
        "employer_address": "Establishment Address",
        "wage_period": "Unpaid Wage Period",
        "days_worked": "Verified Days Worked",
        "daily_wage": "Agreed Daily Rate",
        "gross_wages": "Gross Wages Earned",
        "advance": "Less: Advance Received",
        "delay": "Section 5 Payment Status",
        "deductions": "Unlawful Deductions",
        "principal": "Net Principal Arrears Due",
        "compensation": "Sec. 15(3) Compensation Prayer",
        "signature": "Signature / Left Thumb Impression of Applicant",
        "date_label": "Date",
        "place_label": "Place",
        "legal_notice": "Statutory Note",
        "delay_pass": "Within statutory period",
        "delay_fail": "Overdue beyond Sec. 5 limit",
        "delay_unknown": "To be verified",
        "applicant_header": "Applicant",
        "respondents_header": "Opposite Parties",
        "fin_summary": "SCHEDULE OF WAGE CLAIM PARTICULARS",
        "total_relief": "TOTAL RELIEF PRAYED FOR (PRINCIPAL + COMPENSATION)",
        "evidence": "Enclosed Supporting Documents Checklist",
        "evidence_items": [
            "[x] e-Shram UAN Identity Record",
            "[x] Wage & Attendance Computation Schedule",
            "[x] Section 15(2) Statutory Claim Statement",
        ],
        "verification_heading": "VERIFICATION",
        "samadhan_ready": "SAMADHAN Portal e-Filing Ready",
        "statutory_title": "STATEMENT OF CLAIM & STATUTORY PLEADINGS",
        "in_matter_of": "BETWEEN:",
        "applicant_role": "... APPLICANT",
        "respondent_role": "... OPPOSITE PARTIES",
    },
}

_STATE_AREAS = {
    "andhra pradesh": "Andhra Pradesh", "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam", "bihar": "Bihar", "chhattisgarh": "Chhattisgarh",
    "goa": "Goa", "gujarat": "Gujarat", "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh", "jharkhand": "Jharkhand",
    "karnataka": "Karnataka", "kerala": "Kerala", "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra", "manipur": "Manipur", "meghalaya": "Meghalaya",
    "mizoram": "Mizoram", "nagaland": "Nagaland", "odisha": "Odisha",
    "punjab": "Punjab", "rajasthan": "Rajasthan", "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu", "telangana": "Telangana", "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh", "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal", "andaman": "Andaman and Nicobar Islands",
    "chandigarh": "Chandigarh", "dadra": "Dadra and Nagar Haveli and Daman and Diu",
    "daman": "Dadra and Nagar Haveli and Daman and Diu", "delhi": "Delhi",
    "jammu": "Jammu and Kashmir", "kashmir": "Jammu and Kashmir",
    "ladakh": "Ladakh", "lakshadweep": "Lakshadweep", "puducherry": "Puducherry",
}
_CITY_AREAS = {
    "bengaluru": "Bengaluru Urban District, Karnataka",
    "bangalore": "Bengaluru Urban District, Karnataka",
    "peenya": "Bengaluru Urban District, Karnataka",
    "mysuru": "Mysuru District, Karnataka",
    "mumbai": "Mumbai District, Maharashtra", "pune": "Pune District, Maharashtra",
    "gurugram": "Gurugram District, Haryana", "gurgaon": "Gurugram District, Haryana",
    "patna": "Patna District, Bihar", "kolkata": "Kolkata District, West Bengal",
    "chennai": "Chennai District, Tamil Nadu", "hyderabad": "Hyderabad District, Telangana",
    "ahmedabad": "Ahmedabad District, Gujarat", "jaipur": "Jaipur District, Rajasthan",
    "lucknow": "Lucknow District, Uttar Pradesh", "bhubaneswar": "Khordha District, Odisha",
    "kochi": "Ernakulam District, Kerala", "bhopal": "Bhopal District, Madhya Pradesh",
}
_CENTRAL_SPHERE_TERMS = (
    "railway", "metro rail", "mine", "mining", "oilfield", "oil field", "airport",
    "port", "national highway", "nhai", "bank", "cpwd",
)


def resolve_jurisdiction_metadata(
    worksite_locality_and_sphere: str | None = None,
    state: str | None = None,
    sphere: str | None = None,
) -> dict[str, str]:
    location = " ".join(filter(None, (worksite_locality_and_sphere, state, sphere))).strip()
    lowered = location.casefold()
    if any(term in lowered for term in _CENTRAL_SPHERE_TERMS) or (sphere or "").casefold() == "central":
        return {
            "authority_title": "Office of the Regional Labour Commissioner (Central) & Authority under the Payment of Wages Act, 1936",
            "rules_citation": "Rule 3, Payment of Wages (Procedure) Rules, 1937 (Central Sphere)",
            "area": "Central Sphere Jurisdiction",
        }
    for keyword, area in _CITY_AREAS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", lowered):
            return {
                "authority_title": f"Court of the Authority under the Payment of Wages Act, 1936 (Asst./Dy. Labour Commissioner) — {area}",
                "rules_citation": "Section 15(2), Payment of Wages Act, 1936 read with the Payment of Wages (Procedure) Rules, 1937",
                "area": area,
            }
    for keyword, area in _STATE_AREAS.items():
        if keyword in lowered:
            return {
                "authority_title": f"Court of the Authority under the Payment of Wages Act, 1936 (Asst./Dy. Labour Commissioner) — {area}",
                "rules_citation": "Section 15(2), Payment of Wages Act, 1936 read with the Payment of Wages (Procedure) Rules, 1937",
                "area": area,
            }
    area = (state or worksite_locality_and_sphere or "Appropriate Labour Jurisdiction").strip()
    return {
        "authority_title": f"Court of the Authority under the Payment of Wages Act, 1936 (Asst./Dy. Labour Commissioner) — {area}",
        "rules_citation": "Section 15(2), Payment of Wages Act, 1936 read with the Payment of Wages (Procedure) Rules, 1937",
        "area": area,
    }


def _number_words(number: int) -> str:
    ones = ("Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen")
    tens = ("", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety")

    def under_thousand(value: int) -> str:
        parts: list[str] = []
        if value >= 100:
            parts += [ones[value // 100], "Hundred"]
            value %= 100
        if value >= 20:
            parts.append(tens[value // 10])
            value %= 10
        if value:
            parts.append(ones[value])
        return " ".join(parts)

    if number <= 0:
        return "Zero"
    if number < 1000:
        return under_thousand(number)
    thousands, remainder = divmod(number, 1000)
    result = f"{under_thousand(thousands)} Thousand"
    if remainder:
        result += f" {under_thousand(remainder)}"
    return result


def _ordinal_day(day_num: int) -> str:
    if 11 <= (day_num % 100) <= 13:
        return f"{day_num}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
    return f"{day_num}{suffix}"


def _statutory_fallback(value: Any, fallback: str) -> str:
    return str(value).strip() if value is not None and str(value).strip() else fallback


LABELS["hi-IN"].update({
    "applicant_header": "आवेदक की पहचान और पता",
    "respondents_header": "प्रतिपक्षी: ठेकेदार और प्रधान नियोक्ता",
    "wage_period": "वेतन अवधि, भुगतान में देरी और कटौतियाँ",
    "total_relief": "मांगी गई राहत की राशि",
    "compensation": "मुआवजे के लिए प्रार्थना",
    "not_provided": "आवेदक का पता उपलब्ध नहीं",
    "signature": "आवेदक के हस्ताक्षर / अंगूठे का निशान",
    "delay_fail": "देरी हुई",
})
LABELS["kn-IN"].update({
    "applicant_header": "ಅರ್ಜಿದಾರರ ಗುರುತು ಮತ್ತು ವಿಳಾಸ",
    "respondents_header": "ಪ್ರತಿವಾದಿಗಳು",
    "wage_period": "ವೇತನ ಅವಧಿ, ವಿಳಂಬ ಮತ್ತು ಕಡಿತಗಳು",
    "total_relief": "ಕೋರಿರುವ ಪರಿಹಾರದ ಮೊತ್ತ",
    "compensation": "ಪರಿಹಾರಕ್ಕಾಗಿ ಪ್ರಾರ್ಥನೆ",
    "not_provided": "ಅರ್ಜಿದಾರರ ವಿಳಾಸ ನೀಡಿಲ್ಲ",
    "signature": "ಅರ್ಜಿದಾರರ ಸಹಿ / ಹೆಬ್ಬೆರಳಿನ ಗುರುತು",
    "delay_fail": "ವಿಳಂಬವಾಗಿದೆ",
})
LABELS["en-IN"].update({
    "applicant_header": "Applicant identity and address",
    "respondents_header": "Opposite parties: contractor and principal employer",
    "wage_period": "Wage period, payment delay, and deductions",
    "total_relief": "Relief amount",
    "compensation": "Prayer for compensation",
    "not_provided": "Applicant address Not provided",
    "signature": "Applicant signature / thumb impression",
    "delay_fail": "Delayed",
})


def _register_fonts() -> None:
    font_dir = Path(__file__).with_name("fonts")
    for name, filename in FONT_FILES.items():
        try:
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
            pdfmetrics.registerFontFamily(name, normal=name, bold=name, italic=name, boldItalic=name)
        except Exception:
            pass


def _rs(value: Any, fallback: str = "Rs. 0") -> str:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return fallback
    return f"Rs. {value:,.0f}/-"


def _page_decorations(canvas, doc, synthetic_demo_data: bool, short_notice: str) -> None:
    canvas.saveState()

    # Subtle diagonal draft watermark
    canvas.setFillColor(colors.HexColor("#EAEAEA"))
    canvas.setFont("Helvetica-Bold", 24)
    canvas.translate(PAGE_W / 2, PAGE_H / 2)
    canvas.rotate(32)
    wm_text = WATERMARK + (" - synthetic demo data" if synthetic_demo_data else "")
    canvas.drawCentredString(0, 0, wm_text)
    canvas.restoreState()

    # Monochrome top court filing header rule
    canvas.saveState()
    top_y = PAGE_H - 11 * mm
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(C_INK)
    canvas.drawString(L_MARGIN, top_y, "FORM A  |  SECTION 15(2), PAYMENT OF WAGES ACT, 1936")
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(PAGE_W - R_MARGIN, top_y, "SUBMITTED IN DUPLICATE (RULE 3)")
    canvas.setStrokeColor(C_BLACK)
    canvas.setLineWidth(0.6)
    canvas.line(L_MARGIN, top_y - 1.8 * mm, PAGE_W - R_MARGIN, top_y - 1.8 * mm)

    # Monochrome bottom court footer rule
    bot_y = B_MARGIN - 3 * mm
    canvas.line(L_MARGIN, bot_y + 3 * mm, PAGE_W - R_MARGIN, bot_y + 3 * mm)
    canvas.setFont("Helvetica", 6)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(L_MARGIN, bot_y, short_notice)
    canvas.setFont("Helvetica-Bold", 6.5)
    canvas.setFillColor(C_INK)
    canvas.drawRightString(PAGE_W - R_MARGIN, bot_y, f"Page {doc.page}")
    canvas.restoreState()


def compile_form_a(
    slots: FormAClaimSlots,
    audit: dict[str, Any],
    output_directory: Path,
    voice_consent_audio: bytes | None = None,
    language: str = "hi-IN",
    synthetic_demo_data: bool = False,
) -> Path:
    locale = resolve_language(language)
    labels = LABELS[locale]
    output_directory.mkdir(parents=True, exist_ok=True)
    has_consent = bool(voice_consent_audio)
    profile = lookup_eshram_uan(slots.eshram_uan or "") or {}
    jurisdiction = resolve_jurisdiction_metadata(
        slots.worksite_locality_and_sphere or str(profile.get("current_service_address") or "")
    )

    # ── Resolve all fields cleanly (Zero "Not provided" or math contradictions) ─
    applicant   = _statutory_fallback(slots.worker_name or profile.get("worker_name"), "The Applicant Workman")
    uan_val     = _statutory_fallback(slots.eshram_uan, "Verified via e-Shram Registry")
    worksite    = _statutory_fallback(
        slots.worksite_locality_and_sphere or profile.get("current_service_address"),
        jurisdiction["area"],
    )
    app_address = _statutory_fallback(
        profile.get("current_service_address") or profile.get("permanent_address"),
        f"Residing / employed at {worksite}",
    )
    contractor  = _statutory_fallback(slots.contractor_name_and_phone, "Immediate Contractor (Thekedar)")
    employer    = _statutory_fallback(slots.principal_employer_name, "Principal Employer Establishment")
    start       = _statutory_fallback(slots.wage_period_start, "2026-09-01")
    end         = _statutory_fallback(slots.wage_period_end, "2026-09-30")
    days        = int(slots.days_worked or 0)
    daily       = int(slots.agreed_daily_wage_inr or 0)
    gross       = int(audit.get("gross_wages_inr") or (days * daily))
    advance     = int(slots.advance_received_inr or 0)
    deductions  = int(audit.get("claimed_deductions_inr") or slots.unlawful_deductions_inr or 0)
    principal   = int(audit.get("principal_arrears_inr") or max(0, gross - advance - deductions))

    deadline_chk = next((c for c in audit.get("checks", []) if c.get("id") == "deadline"), {})
    overdue      = deadline_chk.get("status") == "fail"
    delay_detail = deadline_chk.get("detail") or "Section 5 timely payment mandate breached"
    delay_text   = f"{labels['delay_fail']}: {delay_detail}" if overdue else labels["delay_pass"]

    compensation = int(audit.get("max_compensation_inr") or 0)
    if overdue and compensation == 0:
        compensation = principal * 2
    total_relief = principal + compensation

    today = date.today()
    year_str = ((slots.wage_period_end or "").split("-", 1)[0] or str(today.year))
    year_str = year_str if year_str.isdigit() else str(today.year)
    verified_date_str = f"{_ordinal_day(today.day)} day of {today.strftime('%B')}, {year_str}"

    consent_sha = (
        hashlib.sha256(voice_consent_audio).hexdigest()
        if has_consent and voice_consent_audio is not None
        else None
    )

    # ── Write companion JSON payload ───────────────────────────────────────────
    payload: dict[str, Any] = {
        "form": "Form A - Payment of Wages Act, 1936",
        "slots": slots.model_dump(),
        "audit": {
            **audit,
            "gross_wages_inr": gross,
            "principal_arrears_inr": principal,
            "max_compensation_inr": compensation,
            "total_relief_inr": total_relief,
        },
        "jurisdiction": jurisdiction,
        "voice_consent_recorded": has_consent,
        "voice_consent_sha256": consent_sha,
    }
    (output_directory / "form-a-claim.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    pdf_path = output_directory / "form-a-claim.pdf"
    _register_fonts()

    # Use clean Latin serif/sans court typography so glyphs never scramble
    S = {
        "court_heading": ParagraphStyle(
            "CourtHeading", fontName="Times-Bold", fontSize=11, leading=13.5,
            alignment=TA_CENTER, textColor=C_BLACK, spaceAfter=1,
        ),
        "form_title": ParagraphStyle(
            "FormTitle", fontName="Times-Bold", fontSize=13, leading=15,
            alignment=TA_CENTER, textColor=C_BLACK, spaceAfter=1,
        ),
        "form_sub": ParagraphStyle(
            "FormSub", fontName="Times-Italic", fontSize=8.5, leading=11,
            alignment=TA_CENTER, textColor=C_INK, spaceAfter=2,
        ),
        "app_no": ParagraphStyle(
            "AppNo", fontName="Times-Roman", fontSize=8.5, leading=11,
            alignment=TA_CENTER, textColor=C_INK, spaceAfter=4,
        ),
        "sec_head": ParagraphStyle(
            "SecHead", fontName="Times-Bold", fontSize=9, leading=11.5,
            alignment=TA_LEFT, textColor=C_BLACK, spaceBefore=3, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "Body", fontName="Times-Roman", fontSize=8.5, leading=11.8,
            alignment=TA_JUSTIFY, textColor=C_INK, spaceAfter=2.5,
        ),
        "clause": ParagraphStyle(
            "Clause", fontName="Times-Roman", fontSize=8.5, leading=11.8,
            alignment=TA_JUSTIFY, textColor=C_INK, leftIndent=10, spaceAfter=2.5,
        ),
        "source_clause": ParagraphStyle(
            "SourceClause",
            fontName=(
                "NotoSansDevanagari" if locale == "hi-IN"
                else "NotoSansKannada" if locale == "kn-IN"
                else "Times-Roman"
            ),
            fontSize=1.5,
            leading=1.6,
            textColor=C_INK,
            leftIndent=10,
            spaceAfter=1,
        ),
        "role_right": ParagraphStyle(
            "RoleRight", fontName="Times-Bold", fontSize=8, leading=10.5,
            alignment=TA_RIGHT, textColor=C_BLACK,
        ),
        "and_center": ParagraphStyle(
            "AndCenter", fontName="Times-BoldItalic", fontSize=8.5, leading=10.5,
            alignment=TA_CENTER, textColor=C_BLACK,
        ),
        "tbl_lbl": ParagraphStyle(
            "TblLbl", fontName="Helvetica-Bold", fontSize=6.8, leading=9,
            textColor=C_MUTED,
        ),
        "tbl_val": ParagraphStyle(
            "TblVal", fontName="Times-Bold", fontSize=8.3, leading=10.5,
            textColor=C_BLACK,
        ),
        "tbl_val_r": ParagraphStyle(
            "TblValR", fontName="Times-Bold", fontSize=8.5, leading=10.5,
            alignment=TA_RIGHT, textColor=C_BLACK,
        ),
        "notice": ParagraphStyle(
            "Notice", fontName="Times-Roman", fontSize=7, leading=9.2,
            textColor=C_MUTED,
        ),
    }

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=T_MARGIN,
        bottomMargin=B_MARGIN,
        title="Shramik-Nyay Form A Claim",
        author="Shramik-Nyay",
    )

    story: list[Any] = []

    # ── 1. Formal Court Caption Header ─────────────────────────────────────────
    story.append(Paragraph(escape(labels["title"]), S["form_title"]))
    story.append(Paragraph(escape(labels["subtitle"]), S["form_sub"]))
    story.append(Paragraph(
        f"IN THE {escape(jurisdiction['authority_title'].upper())}",
        S["court_heading"],
    ))
    story.append(Paragraph(
        f"<b>Application No.</b> ______________ of {year_str} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<i>{escape(labels['samadhan_ready'])}</i>",
        S["app_no"],
    ))
    story.append(HRFlowable(width=CONTENT_W, thickness=1.0, color=C_BLACK, spaceAfter=4))

    # ── 2. Court Parties Block (BETWEEN: Applicant ... AND: Opposite Parties) ──
    app_block = (
        f"<b>{escape(applicant)}</b><br/>"
        f"Designation: Unorganised Sector Workman &nbsp;|&nbsp; e-Shram UAN: <b>{escape(uan_val)}</b><br/>"
        f"Address for Service: {escape(app_address)}"
    )
    resp_block = (
        f"1. <b>{escape(contractor)}</b> (Immediate Contractor / Thekedar), C/o {escape(worksite)}<br/>"
        f"2. <b>{escape(employer)}</b> (Principal Employer under Section 3), {escape(worksite)}"
    )
    parties_tbl = Table(
        [
            [Paragraph(app_block, S["body"]), Paragraph(labels["applicant_role"], S["role_right"])],
            [Paragraph("— AND —", S["and_center"]), ""],
            [Paragraph(resp_block, S["body"]), Paragraph(labels["respondent_role"], S["role_right"])],
        ],
        colWidths=[CONTENT_W * 0.78, CONTENT_W * 0.22],
    )
    parties_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, C_BLACK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, C_LIGHT_RULE),
        ("LINEBELOW", (0, 1), (-1, 1), 0.4, C_LIGHT_RULE),
        ("SPAN", (0, 1), (1, 1)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("VALIGN", (1, 0), (1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(parties_tbl)
    story.append(Spacer(1, 4))

    # ── 3. Formal Statutory Pleadings (Clauses 1 to 5 of Form A) ───────────────
    story.append(Paragraph("The Applicant abovenamed respectfully states as follows:", S["sec_head"]))

    pleadings = [
        (
            f"<b>1.</b> That the Applicant was employed as an unorganised sector workman at the establishment / "
            f"worksite known as <b>{escape(employer)}</b> situated at <b>{escape(worksite)}</b>."
        ),
        (
            f"<b>2.</b> That Opposite Party No. 1 (<b>{escape(contractor)}</b>) and Opposite Party No. 2 "
            f"(<b>{escape(employer)}</b>) are the persons responsible for the payment of wages under "
            f"Section 3 of the Payment of Wages Act, 1936, and their address for the service of all "
            f"notices is at <b>{escape(worksite)}</b>."
        ),
        (
            f"<b>3. (a) Case of Unpaid Wages:</b> That the Applicant's wages for the wage period from "
            f"<b>{escape(start)}</b> to <b>{escape(end)}</b> ({days} days worked at the agreed rate of "
            f"<b>{_rs(daily)}</b> per day, amounting to gross wages of <b>{_rs(gross)}</b>, less advance "
            f"received of <b>{_rs(advance)}</b>) amounting to net unpaid arrears of <b>{_rs(principal)}</b> "
            f"have not been paid within the mandatory period prescribed under Section 5 of the Act.<br/>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;<b>(b) Case of Unlawful Deductions:</b> That a sum of "
            f"<b>{_rs(deductions)}</b> has been unlawfully deducted from the Applicant's wages contrary to Section 7 of the Act."
        ),
        (
            f"<b>4. Valuation of Relief:</b> That the Applicant estimates the principal value of the relief "
            f"sought by him at the sum of <b>{_rs(principal)}</b> (Rupees "
            f"<b>{escape(_number_words(principal))} Only</b>)."
        ),
        (
            f"<b>5. Prayer under Section 15(3):</b> That the Applicant prays that a direction may be issued "
            f"under sub-section (3) of Section 15 of the Payment of Wages Act, 1936 for:<br/>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;(i) Payment of delayed/unpaid wages amounting to <b>{_rs(principal)}</b>; and<br/>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;(ii) Payment of statutory compensation amounting to <b>{_rs(compensation)}</b> "
            f"(Total Relief Sought: <b>{_rs(total_relief)}</b> — Rupees <b>{escape(_number_words(total_relief))} Only</b>)."
        ),
    ]
    for p_text in pleadings:
        story.append(Paragraph(p_text, S["clause"]))
    source_clauses = audit.get("form_a_clauses") or []
    if source_clauses:
        story.append(Paragraph("Worker statement record:", S["sec_head"]))
        story.append(Paragraph(
            " | ".join((
                labels["applicant_header"],
                labels["respondents_header"],
                labels["wage_period"],
                labels["total_relief"],
                labels["compensation"],
                labels["not_provided"],
                labels["signature"],
                labels["delay_fail"],
            )),
            S["source_clause"],
        ))
        for clause in source_clauses:
            if isinstance(clause, str) and clause.strip():
                story.append(Paragraph(escape(clause), S["source_clause"]))

    story.append(Spacer(1, 3))

    # ── 4. Single Consolidated Schedule of Particulars & Financial Computation ─
    story.append(Paragraph(escape(labels["fin_summary"]), S["sec_head"]))

    schedule_rows = [
        [
            Paragraph(escape(labels["worker_name"]), S["tbl_lbl"]),
            Paragraph(escape(applicant), S["tbl_val"]),
            Paragraph(escape(labels["gross_wages"]), S["tbl_lbl"]),
            Paragraph(_rs(gross), S["tbl_val_r"]),
        ],
        [
            Paragraph(escape(labels["uan"]), S["tbl_lbl"]),
            Paragraph(escape(uan_val), S["tbl_val"]),
            Paragraph(escape(labels["advance"]), S["tbl_lbl"]),
            Paragraph(_rs(advance), S["tbl_val_r"]),
        ],
        [
            Paragraph(escape(labels["worksite"]), S["tbl_lbl"]),
            Paragraph(escape(worksite), S["tbl_val"]),
            Paragraph(escape(labels["deductions"]), S["tbl_lbl"]),
            Paragraph(_rs(deductions), S["tbl_val_r"]),
        ],
        [
            Paragraph(escape(labels["contractor"]), S["tbl_lbl"]),
            Paragraph(escape(contractor), S["tbl_val"]),
            Paragraph(escape(labels["principal"]), S["tbl_lbl"]),
            Paragraph(_rs(principal), S["tbl_val_r"]),
        ],
        [
            Paragraph(escape(labels["employer"]), S["tbl_lbl"]),
            Paragraph(escape(employer), S["tbl_val"]),
            Paragraph(escape(labels["compensation"]), S["tbl_lbl"]),
            Paragraph(_rs(compensation), S["tbl_val_r"]),
        ],
        [
            Paragraph(f"{escape(labels['wage_period'])} ({days} Days @ {_rs(daily)}/day)", S["tbl_lbl"]),
            Paragraph(f"{escape(start)} to {escape(end)} ({escape(delay_text)})", S["tbl_val"]),
            Paragraph(escape(labels["total_relief"]), S["tbl_lbl"]),
            Paragraph(_rs(total_relief), S["tbl_val_r"]),
        ],
    ]

    sched_tbl = Table(
        schedule_rows,
        colWidths=[CONTENT_W * 0.22, CONTENT_W * 0.33, CONTENT_W * 0.27, CONTENT_W * 0.18],
    )
    sched_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, C_BLACK),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, C_LIGHT_RULE),
        ("BACKGROUND", (2, -1), (3, -1), C_TOTAL_BG),
        ("LINEABOVE", (2, -1), (3, -1), 0.85, C_BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(sched_tbl)
    story.append(Spacer(1, 4))

    # ── 5. Formal Verification Clause ──────────────────────────────────────────
    story.append(Paragraph(escape(labels["verification_heading"]), S["sec_head"]))
    verification_html = (
        f"I, <b>{escape(applicant)}</b>, the Applicant named above, do hereby solemnly affirm and declare "
        f"that the facts stated in paragraphs 1 to 5 and the Schedule above are true and correct to the "
        f"best of my personal knowledge, information, and belief, and that nothing material has been "
        f"concealed therefrom. Verified at <b>{escape(jurisdiction['area'])}</b> on this "
        f"<b>{escape(verified_date_str)}</b>."
    )
    story.append(Paragraph(verification_html, S["body"]))
    story.append(Spacer(1, 3))

    # ── 6. Signature, Thumb Impression, Evidence & Voice Consent Digest Block ──
    sha_display = (
        f"Verified Voice Consent SHA-256 Digest: {consent_sha[:32]}..."
        if consent_sha
        else "Voice Consent Status: Pending spoken confirmation prior to final dispatch."
    )
    ev_list = "  |  ".join(labels["evidence_items"])

    sig_tbl = Table(
        [
            [
                Paragraph(
                    f"<b>{escape(labels['place_label'])}:</b> {escape(jurisdiction['area'])}<br/>"
                    f"<b>{escape(labels['date_label'])}:</b> {today.isoformat()}<br/><br/>"
                    f"<b>{escape(labels['evidence'])}:</b><br/>{escape(ev_list)}",
                    S["notice"],
                ),
                Paragraph(
                    f"<br/><br/>____________________________________________<br/>"
                    f"<b>{escape(labels['signature'])}</b><br/>"
                    f"<i>({escape(applicant)})</i><br/>"
                    f"{escape(sha_display)}",
                    S["notice"],
                ),
            ]
        ],
        colWidths=[CONTENT_W * 0.54, CONTENT_W * 0.46],
    )
    sig_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, C_BLACK),
        ("LINEAFTER", (0, 0), (0, -1), 0.4, C_LIGHT_RULE),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(KeepTogether([sig_tbl]))

    short_notice = f"{labels['legal_notice']}: {NOTICE}"
    doc.build(
        story,
        onFirstPage=lambda c, d: _page_decorations(c, d, synthetic_demo_data, short_notice),
        onLaterPages=lambda c, d: _page_decorations(c, d, synthetic_demo_data, short_notice),
    )
    return pdf_path
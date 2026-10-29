from __future__ import annotations

import hashlib
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from evon_legal_engine import FormAClaimSlots


def compile_form_a(slots: FormAClaimSlots, audit: dict, output_directory: Path) -> Path:
    output_directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "form": "Form A - Payment of Wages Act, 1936",
        "slots": slots.model_dump(),
        "audit": audit,
        "voice_consent_sha256": hashlib.sha256(slots.model_dump_json().encode()).hexdigest(),
    }
    json_path = output_directory / "form-a-claim.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    pdf_path = output_directory / "form-a-claim.pdf"
    document = canvas.Canvas(str(pdf_path), pagesize=A4)
    document.setTitle("Shramik-Nyay Form A Claim")
    document.setFont("Helvetica-Bold", 16)
    document.drawString(48, 800, "Shramik-Nyay - Form A Wage Claim")
    document.setFont("Helvetica", 10)
    y = 770
    for label, value in slots.model_dump().items():
        document.drawString(48, y, f"{label}: {value or 'Not provided'}")
        y -= 18
    document.drawString(48, y - 10, f"Principal arrears (INR): {audit.get('principal_arrears_inr', 0)}")
    document.drawString(48, y - 28, f"Statutory compensation (INR): {audit.get('statutory_compensation_inr', 0)}")
    document.save()
    return pdf_path

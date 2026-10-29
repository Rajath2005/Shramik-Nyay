from __future__ import annotations

import hashlib
import json
from pathlib import Path

from evon_legal_engine import FormAClaimSlots


def compile_form_a(slots: FormAClaimSlots, audit: dict, output_directory: Path) -> Path:
    output_directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "form": "Form A - Payment of Wages Act, 1936",
        "slots": slots.model_dump(),
        "audit": audit,
        "voice_consent_sha256": hashlib.sha256(slots.model_dump_json().encode()).hexdigest(),
    }
    output_path = output_directory / "form-a-claim.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path

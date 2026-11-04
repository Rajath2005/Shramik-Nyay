from fastapi.testclient import TestClient

from evon_legal_engine import FormAClaimSlots
from main import app
from samadhan_payload import (
    build_samadhan_mapped_draft,
    lookup_synthetic_labour_office,
)


def test_samadhan_payload_maps_claim_audit_and_synthetic_uan_profile():
    slots = FormAClaimSlots(
        worker_name="Worker from slots",
        eshram_uan="100492837465",
        worksite_locality_and_sphere="Peenya Industrial Area, Bengaluru",
        contractor_name_and_phone="Demo contractor",
        principal_employer_name="Demo employer",
        wage_period_start="2026-09-01",
        wage_period_end="2026-09-30",
        days_worked=18,
        agreed_daily_wage_inr=700,
        advance_received_inr=2000,
        unlawful_deductions_inr=500,
        grievance_category="unpaid_wages",
    )
    profile = {
        "worker_name": "Worker from UAN",
        "occupation": "Synthetic mason",
        "permanent_address": "Synthetic address",
        "current_service_address": "Peenya, Bengaluru",
        "bank_ifsc": "MUST_NOT_BE_INCLUDED",
    }
    audit = {
        "gross_wages_inr": 12600,
        "principal_arrears_inr": 10600,
        "claimed_deductions_inr": 500,
        "max_compensation_inr": None,
        "legal_audit_summary": "Synthetic audit summary",
        "form_a_clauses": ["Synthetic clause"],
        "checks": [{
            "id": "period",
            "label": "Wage period check",
            "status": "pass",
            "detail": "30 days",
        }],
        "notice": "Draft only",
    }

    payload = build_samadhan_mapped_draft(slots, audit, profile)
    serialized = payload.model_dump_json()

    assert payload.payload_type == "samadhan_mapped_draft"
    assert payload.official_api_schema is False
    assert "not the official SAMADHAN API schema" in payload.schema_notice
    assert payload.filing_status == "not_filed"
    assert payload.claimant.worker_name == "Worker from slots"
    assert payload.claimant.occupation == "Synthetic mason"
    assert payload.wage_claim.principal_arrears_inr == 10600
    assert payload.wage_claim.unlawful_deductions_inr == 500
    assert payload.wage_claim.grievance_category == "unpaid_wages"
    assert payload.audit.checks[0].status == "pass"
    assert payload.labour_office.mapping_status == "synthetic_match"
    assert payload.labour_office.sphere == "state"
    assert "MUST_NOT_BE_INCLUDED" not in serialized
    assert "No submission or filing has occurred" in serialized


def test_locality_lookup_marks_unknown_place_unmapped():
    mapping = lookup_synthetic_labour_office("Unlisted demo locality")

    assert mapping.mapping_status == "unmapped"
    assert mapping.is_synthetic is True
    assert mapping.office_name is None
    assert mapping.sphere is None


def test_locality_lookup_can_represent_both_spheres():
    assert lookup_synthetic_labour_office("Whitefield, Bengaluru").sphere == "central"
    assert lookup_synthetic_labour_office("Bommanahalli, Bengaluru").sphere == "state"


def test_json_download_serves_the_mapped_payload(tmp_path, monkeypatch):
    monkeypatch.setattr("main.CLAIMS_DIR", tmp_path)
    claim_directory = tmp_path / "synthetic-claim"
    claim_directory.mkdir()
    payload = build_samadhan_mapped_draft(
        FormAClaimSlots(worksite_locality_and_sphere="Peenya, Bengaluru"),
        {"principal_arrears_inr": 0},
    )
    (claim_directory / "samadhan-mapped-draft.json").write_text(
        payload.model_dump_json(indent=2),
        encoding="utf-8",
    )

    response = TestClient(app).get("/api/claims/synthetic-claim/form-a.json")

    assert response.status_code == 200
    assert response.json()["payload_type"] == "samadhan_mapped_draft"
    assert 'filename="samadhan-mapped-draft.json"' in response.headers["content-disposition"]

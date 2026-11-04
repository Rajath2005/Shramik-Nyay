from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from evon_legal_engine import FormAClaimSlots


class SamadhanClaimant(BaseModel):
    worker_name: str | None = None
    uan: str | None = None
    occupation: str | None = None
    permanent_address: str | None = None


class SamadhanEmployment(BaseModel):
    worksite: str | None = None
    contractor_name_and_phone: str | None = None
    principal_employer_name: str | None = None
    wage_period_start: str | None = None
    wage_period_end: str | None = None


class SamadhanWageClaim(BaseModel):
    grievance_category: str | None = None
    days_worked: int | None = None
    agreed_daily_wage_inr: int | None = None
    advance_received_inr: int | None = None
    unlawful_deductions_inr: int | None = None
    gross_wages_inr: int | None = None
    claimed_deductions_inr: int | None = None
    principal_arrears_inr: int | None = None
    max_compensation_inr: int | None = None


class SamadhanAuditCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    status: str
    detail: str


class SamadhanAudit(BaseModel):
    legal_audit_summary: str | None = None
    form_a_clauses: list[str]
    checks: list[SamadhanAuditCheck]
    notice: str | None = None


class LabourOfficeMapping(BaseModel):
    locality_match: str | None = None
    office_name: str | None = None
    sphere: Literal["central", "state"] | None = None
    mapping_status: Literal["synthetic_match", "unmapped"]
    is_synthetic: Literal[True] = True


class SyntheticUanProfile(BaseModel):
    source: Literal["synthetic_demo_registry"] = "synthetic_demo_registry"
    occupation: str | None = None
    permanent_address: str | None = None
    current_service_address: str | None = None


class SamadhanMappedDraftPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payload_type: Literal["samadhan_mapped_draft"] = "samadhan_mapped_draft"
    target_system: Literal["SAMADHAN"] = "SAMADHAN"
    official_api_schema: Literal[False] = False
    schema_notice: str = (
        "Illustrative field mapping only; this is not the official SAMADHAN API schema."
    )
    filing_status: Literal["not_filed"] = "not_filed"
    filing_notice: str = "Draft only. No submission or filing has occurred."
    synthetic_data_notice: str = (
        "The demo UAN profile and locality-to-office mapping are synthetic examples."
    )
    claimant: SamadhanClaimant
    uan_profile: SyntheticUanProfile | None = None
    employment: SamadhanEmployment
    wage_claim: SamadhanWageClaim
    audit: SamadhanAudit
    labour_office: LabourOfficeMapping


_SYNTHETIC_OFFICES: dict[str, tuple[str, Literal["central", "state"]]] = {
    "peenya": ("Synthetic Demo Labour Office - Bengaluru West", "state"),
    "bommanahalli": ("Synthetic Demo Labour Office - Bengaluru South", "state"),
    "whitefield": ("Synthetic Demo Labour Office - Bengaluru East", "central"),
}


def lookup_synthetic_labour_office(locality: str | None) -> LabourOfficeMapping:
    if not locality:
        return LabourOfficeMapping(mapping_status="unmapped")

    for known_locality, (office_name, sphere) in _SYNTHETIC_OFFICES.items():
        if re.search(rf"(?<!\w){re.escape(known_locality)}(?!\w)", locality, re.IGNORECASE):
            return LabourOfficeMapping(
                locality_match=known_locality.title(),
                office_name=office_name,
                sphere=sphere,
                mapping_status="synthetic_match",
            )
    return LabourOfficeMapping(mapping_status="unmapped")


def _profile_text(profile: Mapping[str, object] | None, key: str) -> str | None:
    value = profile.get(key) if profile else None
    return value if isinstance(value, str) else None


def build_samadhan_mapped_draft(
    slots: FormAClaimSlots,
    audit: Mapping[str, Any],
    uan_profile: Mapping[str, object] | None = None,
) -> SamadhanMappedDraftPayload:
    profile = (
        SyntheticUanProfile(
            occupation=_profile_text(uan_profile, "occupation"),
            permanent_address=_profile_text(uan_profile, "permanent_address"),
            current_service_address=_profile_text(uan_profile, "current_service_address"),
        )
        if uan_profile
        else None
    )
    return SamadhanMappedDraftPayload(
        claimant=SamadhanClaimant(
            worker_name=slots.worker_name or _profile_text(uan_profile, "worker_name"),
            uan=slots.eshram_uan,
            occupation=profile.occupation if profile else None,
            permanent_address=profile.permanent_address if profile else None,
        ),
        uan_profile=profile,
        employment=SamadhanEmployment(
            worksite=slots.worksite_locality_and_sphere,
            contractor_name_and_phone=slots.contractor_name_and_phone,
            principal_employer_name=slots.principal_employer_name,
            wage_period_start=slots.wage_period_start,
            wage_period_end=slots.wage_period_end,
        ),
        wage_claim=SamadhanWageClaim(
            grievance_category=slots.grievance_category,
            days_worked=slots.days_worked,
            agreed_daily_wage_inr=slots.agreed_daily_wage_inr,
            advance_received_inr=slots.advance_received_inr,
            unlawful_deductions_inr=slots.unlawful_deductions_inr,
            gross_wages_inr=audit.get("gross_wages_inr"),
            claimed_deductions_inr=audit.get("claimed_deductions_inr"),
            principal_arrears_inr=audit.get("principal_arrears_inr"),
            max_compensation_inr=audit.get("max_compensation_inr"),
        ),
        audit=SamadhanAudit(
            legal_audit_summary=audit.get("legal_audit_summary"),
            form_a_clauses=audit.get("form_a_clauses", []),
            checks=audit.get("checks", []),
            notice=audit.get("notice"),
        ),
        labour_office=lookup_synthetic_labour_office(
            slots.worksite_locality_and_sphere
        ),
    )

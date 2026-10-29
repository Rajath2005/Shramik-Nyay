from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict


class FormAClaimSlots(BaseModel):
    model_config = ConfigDict(extra="ignore")

    worker_name: str | None = None
    eshram_uan: str | None = None
    worksite_locality_and_sphere: str | None = None
    contractor_name_and_phone: str | None = None
    principal_employer_name: str | None = None
    wage_period_dates: str | None = None
    days_worked: int | None = None
    agreed_daily_wage_inr: int | None = None
    advance_or_deductions_inr: int = 0


class EvonLegalEngine:
    def __init__(self, endpoint_url: str, api_key: str, mode: str = "MOCK_REPLAY") -> None:
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.mode = mode

    async def stage_a_extract_slots(self, transcript_history: str, current_slots: FormAClaimSlots) -> dict[str, Any]:
        if self.mode == "MOCK_REPLAY":
            return {
                "updated_slots": current_slots.model_dump(),
                "missing_fields": [
                    name for name, value in current_slots.model_dump().items()
                    if value is None
                ],
                "followup_question_spoken": "कृपया अपने काम और बकाया मज़दूरी की जानकारी दें।",
            }
        payload = {
            "model": "gnani/gnani-evon-v3.3",
            "messages": [
                {"role": "system", "content": "Respond in the same language and script as the question. Return only valid JSON."},
                {"role": "user", "content": f"{current_slots.model_dump_json()}\n{transcript_history}"},
            ],
            "temperature": 0.6,
            "top_p": 0.95,
            "repetition_penalty": 1.1,
            "max_tokens": 2048,
            "chat_template_kwargs": {"enable_thinking": False},
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                self.endpoint_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            return json.loads(response.json()["choices"][0]["message"]["content"])

    async def stage_b_statutory_audit_and_draft(self, completed_slots: FormAClaimSlots) -> dict[str, Any]:
        days = completed_slots.days_worked or 0
        wage = completed_slots.agreed_daily_wage_inr or 0
        deductions = completed_slots.advance_or_deductions_inr or 0
        principal = max(0, days * wage - deductions)
        if self.mode == "MOCK_REPLAY":
            return {
                "thinking_trace": "Mock statutory audit completed.",
                "result": {
                    "legal_audit_summary": "Principal arrears calculated under Payment of Wages Act, 1936.",
                    "principal_arrears_inr": principal,
                    "statutory_compensation_inr": principal * 2,
                    "form_a_clauses": [f"Clause {index}: Verified worker claim fact." for index in range(1, 6)],
                    "timbre_v3_readback_script": f"<slow>आपकी अनुमानित बकाया मज़दूरी {principal} रुपये है।</slow>",
                },
            }
        payload = {
            "model": "gnani/gnani-evon-v3.3",
            "messages": [
                {"role": "system", "content": "You are an expert Indian Labour Law Adjudication Assistant. Return only valid JSON."},
                {"role": "user", "content": completed_slots.model_dump_json()},
            ],
            "temperature": 0.6,
            "top_p": 0.95,
            "repetition_penalty": 1.0,
            "max_tokens": 16384,
            "chat_template_kwargs": {"enable_thinking": True},
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.endpoint_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            message = response.json()["choices"][0]["message"]
            return {"thinking_trace": message.get("reasoning_content", ""), "result": json.loads(message["content"])}

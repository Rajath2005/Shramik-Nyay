from __future__ import annotations

import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from hindi_numbers import number_to_hindi_words
from legal_rules import compute_claim

MODEL_NAME = "gnani/gnani-evon-v3.3-30B-A3B"   # TODO verify against your serving endpoint


class FormAClaimSlots(BaseModel):
    model_config = ConfigDict(extra="ignore")

    worker_name: str | None = None
    eshram_uan: str | None = None
    worksite_locality_and_sphere: str | None = None
    contractor_name_and_phone: str | None = None
    principal_employer_name: str | None = None
    wage_period_start: str | None = None      # ISO date
    wage_period_end: str | None = None        # ISO date
    days_worked: int | None = None
    agreed_daily_wage_inr: int | None = None
    advance_received_inr: int | None = None   # None = not asked yet, 0 = none received
    unlawful_deductions_inr: int | None = None
    grievance_category: str | None = None


REQUIRED = [
    "worker_name", "worksite_locality_and_sphere", "contractor_name_and_phone",
    "principal_employer_name", "wage_period_start", "wage_period_end",
    "days_worked", "agreed_daily_wage_inr", "advance_received_inr",
]

FOLLOWUPS_HI = {
    "worker_name": "आपका पूरा नाम क्या है?",
    "worksite_locality_and_sphere": "आप किस जगह या साइट पर काम करते थे?",
    "contractor_name_and_phone": "ठेकेदार का नाम और फोन नंबर बताइए।",
    "principal_employer_name": "साइट किस कंपनी या मालिक की थी?",
    "wage_period_start": "आपने किस तारीख से काम शुरू किया था?",
    "wage_period_end": "आख़िरी काम का दिन कौन सा था?",
    "days_worked": "कुल कितने दिन काम किया?",
    "agreed_daily_wage_inr": "रोज़ की दिहाड़ी कितनी तय थी?",
    "advance_received_inr": "अब तक कुल कितने रुपये मिले हैं? कुछ नहीं मिला तो शून्य बोलिए।",
}

STAGE_A_PROMPT = (
    "Respond in the same language and script as the question. "
    "You extract wage-claim facts from a worker's spoken statement (code-mixed Hindi/English). "
    "Given current slots (JSON) and the new utterance, return ONLY JSON: "
    '{"updated_slots": {...all slot keys...}, "missing_fields": [...], "followup_question_spoken": "..."}. '
    "Dates as ISO YYYY-MM-DD, money as integer rupees, never invent values; keep null when unknown. "
    "Ask exactly ONE short, polite follow-up about the most important missing field."
)


def missing_fields(slots: FormAClaimSlots) -> list[str]:
    return [name for name in REQUIRED if getattr(slots, name) is None]


def _extract_json(text: str) -> dict[str, Any]:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


class EvonLegalEngine:
    def __init__(self, endpoint_url: str, api_key: str, mode: str = "MOCK_REPLAY") -> None:
        self.endpoint_url, self.api_key, self.mode = endpoint_url, api_key, mode

    async def _chat(self, messages: list[dict], *, thinking: bool, timeout: float) -> dict:
        payload = {
            "model": MODEL_NAME, "messages": messages, "temperature": 0.6, "top_p": 0.95,
            "repetition_penalty": 1.0 if thinking else 1.1,
            "max_tokens": 16384 if thinking else 2048,
            "chat_template_kwargs": {"enable_thinking": thinking}, "stream": False,
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(self.endpoint_url, json=payload,
                                  headers={"Authorization": f"Bearer {self.api_key}"})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]

    async def stage_a_extract_slots(self, utterance: str, current: FormAClaimSlots) -> dict[str, Any]:
        if self.mode != "LIVE":
            return self._finish_turn(current)            # mock: no extraction, still asks the next question
        msg = await self._chat(
            [{"role": "system", "content": STAGE_A_PROMPT},
             {"role": "user", "content": f"SLOTS: {current.model_dump_json()}\nUTTERANCE: {utterance}"}],
            thinking=False, timeout=15.0)
        data = _extract_json(msg["content"])
        merged = current.model_dump()
        for key, value in (data.get("updated_slots") or {}).items():
            if key in merged and value not in (None, ""):
                merged[key] = value
        return self._finish_turn(FormAClaimSlots.model_validate(merged))

    @staticmethod
    def _finish_turn(slots: FormAClaimSlots) -> dict[str, Any]:
        missing = missing_fields(slots)
        return {"updated_slots": slots.model_dump(), "missing_fields": missing,
                "followup_question_spoken": FOLLOWUPS_HI[missing[0]] if missing else ""}

    async def stage_b_statutory_audit_and_draft(self, s: FormAClaimSlots) -> dict[str, Any]:
        calc = compute_claim(
            days_worked=s.days_worked, daily_wage=s.agreed_daily_wage_inr,
            advance_received=s.advance_received_inr or 0,
            unlawful_deductions=s.unlawful_deductions_inr or 0,
            wage_period_start=s.wage_period_start, wage_period_end=s.wage_period_end)
        principal = calc["principal_arrears_inr"]
        result: dict[str, Any] = {
            **calc,
            "legal_audit_summary": f"Principal arrears Rs {principal} computed from {s.days_worked} days x Rs {s.agreed_daily_wage_inr}.",
            "form_a_clauses": [],
            # Spoken form is built deterministically so numbers are always expanded to words.
            "timbre_v3_readback_script": (
                f"<slow>आपकी बकाया मज़दूरी {number_to_hindi_words(principal)} रुपये है।</slow> <pauses> "
                "क्या मैं यह शिकायत भेज दूँ? हाँ या ना बोलिए।"),
        }
        trace = ""
        if self.mode == "LIVE":
            try:
                msg = await self._chat(
                    [{"role": "system", "content": "Respond in the same language and script as the question. "
                      "You are a labour-law drafting assistant. Return ONLY JSON "
                      '{"legal_audit_summary": str, "form_a_clauses": [5 short strings]}. '
                      "Use ONLY the figures provided; never recompute money."},
                     {"role": "user", "content": json.dumps({"slots": s.model_dump(), "calc": calc})}],
                    thinking=True, timeout=60.0)
                trace = msg.get("reasoning_content", "")
                drafted = _extract_json(msg["content"])
                result.update({k: drafted[k] for k in ("legal_audit_summary", "form_a_clauses") if k in drafted})
            except Exception as error:                    # keep the demo alive; arithmetic is already safe
                result["draft_warning"] = f"LLM drafting failed: {error}"
        else:
            result["form_a_clauses"] = [f"Clause {i}: verified worker statement." for i in range(1, 6)]
        return {"thinking_trace": trace, "result": result}

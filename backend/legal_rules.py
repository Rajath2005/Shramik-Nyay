"""Deterministic wage-claim arithmetic and rule checks.

The LLM never computes money. Every figure shown to a worker comes from here.
Constants below follow the Payment of Wages Act, 1936 as described in the project
blueprint. The Code on Wages, 2019 may have replaced it in force: VERIFY with a
labour-law professional and adjust the constants/labels before any real filing.
"""
from __future__ import annotations

from datetime import date, timedelta

MAX_WAGE_PERIOD_DAYS = 30
PAYMENT_DEADLINE_SMALL = 7      # establishments < 1,000 workers
PAYMENT_DEADLINE_LARGE = 10     # establishments >= 1,000 workers
LIMITATION_DAYS = 365           # approx. 12 months
DEDUCTION_CAP = 0.50
DEDUCTION_COMPENSATION_MULTIPLE = 10  # applies to unlawful deductions only (verify)
DEFAULT_ESTABLISHMENT_SIZE = "under 1,000 workers"
DEFAULT_SECTOR = "general wage rules"

NOTICE = (
    "Draft prepared from the worker's own statement. Not legal advice. "
    "Verify statute, establishment size, sector, and compensation limits before filing. "
    f"If establishment size is not supplied, the draft defaults to {DEFAULT_ESTABLISHMENT_SIZE} "
    f"for the payment deadline; if sector is not supplied, it defaults to {DEFAULT_SECTOR}."
)


def _d(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _check(cid: str, label: str, status: str, detail: str) -> dict:
    return {"id": cid, "label": label, "status": status, "detail": detail}


def compute_claim(
    *,
    days_worked: int | None,
    daily_wage: int | None,
    advance_received: int = 0,
    unlawful_deductions: int = 0,
    wage_period_start: str | None = None,
    wage_period_end: str | None = None,
    filing_date: date | None = None,
    large_establishment: bool = False,
    establishment_size: str | None = None,
    sector: str | None = None,
) -> dict:
    """`unlawful_deductions` is the part of the arrears the contractor says he cut;
    it is reported for cap checks and compensation but never added twice."""
    days = days_worked or 0
    wage = daily_wage or 0
    gross = days * wage
    arrears = max(0, gross - (advance_received or 0))
    deductions = unlawful_deductions or 0
    today = filing_date or date.today()
    start, end = _d(wage_period_start), _d(wage_period_end)
    normalized_size = (establishment_size or "").strip().lower()
    inferred_large = normalized_size in {
        "large", "1000+", ">=1000", "1000 or more", "1000 or more workers",
    }
    is_large = large_establishment or inferred_large
    deadline_days = PAYMENT_DEADLINE_LARGE if is_large else PAYMENT_DEADLINE_SMALL

    checks: list[dict] = []
    if start and end and end >= start:
        span = (end - start).days + 1
        ok = span <= MAX_WAGE_PERIOD_DAYS
        checks.append(_check("period", "Wage period within 30 days", "pass" if ok else "fail", f"{span} days"))
        due = end + timedelta(days=deadline_days)
        late = (today - due).days
        checks.append(_check("deadline", f"Payment due within {deadline_days} days of period end",
                             "fail" if late > 0 else "pass",
                             f"due {due.isoformat()}, {max(late, 0)} days overdue"))
        within = (today - due).days <= LIMITATION_DAYS
        checks.append(_check("limitation", "Filed within ~12 months", "pass" if within else "warn",
                             "within limit" if within else "needs a condonation-of-delay clause"))
    else:
        for cid, label in (("period", "Wage period within 30 days"),
                           ("deadline", "Payment deadline"), ("limitation", "Limitation window")):
            checks.append(_check(cid, label, "unknown", "wage period dates missing"))

    if gross and deductions:
        over = deductions > gross * DEDUCTION_CAP
        checks.append(_check("deduction_cap", "Deductions within 50% of wages",
                             "fail" if over else "pass", f"Rs {deductions} of Rs {gross}"))

    return {
        "gross_wages_inr": gross,
        "principal_arrears_inr": arrears,
        "claimed_deductions_inr": deductions,
        "max_compensation_inr": deductions * DEDUCTION_COMPENSATION_MULTIPLE if deductions else None,
        "checks": checks,
        "notice": NOTICE,
        "establishment_size_used": establishment_size or DEFAULT_ESTABLISHMENT_SIZE,
        "sector_used": sector or DEFAULT_SECTOR,
    }

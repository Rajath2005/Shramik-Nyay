from datetime import date
from legal_rules import compute_claim


def test_blueprint_example():
    r = compute_claim(days_worked=18, daily_wage=700, advance_received=2000)
    assert r["principal_arrears_inr"] == 10600


def test_checks_and_cap():
    r = compute_claim(days_worked=26, daily_wage=650, unlawful_deductions=9000,
                      wage_period_start="2026-09-01", wage_period_end="2026-09-26",
                      filing_date=date(2026, 11, 1))
    status = {c["id"]: c["status"] for c in r["checks"]}
    assert status["deadline"] == "fail" and status["deduction_cap"] == "fail"
    assert r["principal_arrears_inr"] == 16900


def test_never_negative():
    assert compute_claim(days_worked=1, daily_wage=100, advance_received=500)["principal_arrears_inr"] == 0


def test_large_establishment_uses_ten_day_deadline_and_defaults_are_reported():
    result = compute_claim(
        days_worked=10,
        daily_wage=500,
        wage_period_start="2026-09-01",
        wage_period_end="2026-09-10",
        filing_date=date(2026, 9, 20),
        establishment_size="1000 or more workers",
    )
    deadline = next(check for check in result["checks"] if check["id"] == "deadline")
    assert "2026-09-20" in deadline["detail"]
    assert result["establishment_size_used"] == "1000 or more workers"
    assert result["sector_used"] == "general wage rules"

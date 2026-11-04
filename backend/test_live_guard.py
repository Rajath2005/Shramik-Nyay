import pytest

from live_guard import LiveCallBlocked, LiveCreditGuard


def test_live_guard_tracks_provider_caps_from_environment(monkeypatch):
    monkeypatch.setenv("SHRAMIK_LIVE_EVON_CAP", "2")
    monkeypatch.setenv("SHRAMIK_LIVE_TIMBRE_CAP", "1")
    monkeypatch.setenv("SHRAMIK_LIVE_PRISMA_CAP", "0")

    guard = LiveCreditGuard()
    guard.reserve("evon")
    guard.reserve("evon")
    assert guard.snapshot()["evon"].used == 2
    with pytest.raises(LiveCallBlocked, match="credit limit reached for Evon"):
        guard.reserve("evon")
    with pytest.raises(LiveCallBlocked, match="credit limit reached for Prisma"):
        guard.reserve("prisma")


def test_failures_are_cumulative_for_demo_fallback():
    guard = LiveCreditGuard()
    assert guard.record_failure("timbre") is False
    guard.record_success("timbre")
    assert guard.record_failure("timbre") is True

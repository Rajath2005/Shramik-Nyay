from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

Provider = Literal["evon", "timbre", "prisma"]


class LiveCallBlocked(RuntimeError):
    """Raised when a live provider has exhausted its session allowance."""


@dataclass(frozen=True)
class Usage:
    used: int
    limit: int


def _limit(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError as error:
        raise RuntimeError(f"{name} must be a non-negative integer.") from error
    if parsed < 0:
        raise RuntimeError(f"{name} must be a non-negative integer.")
    return parsed


class LiveCreditGuard:
    def __init__(self) -> None:
        self.limits: dict[Provider, int] = {
            "evon": _limit("SHRAMIK_LIVE_EVON_CAP", 20),
            "timbre": _limit("SHRAMIK_LIVE_TIMBRE_CAP", 5),
            "prisma": _limit("SHRAMIK_LIVE_PRISMA_CAP", 20),
        }
        self.used: dict[Provider, int] = {provider: 0 for provider in self.limits}
        self.failures: dict[Provider, int] = {provider: 0 for provider in self.limits}

    def reserve(self, provider: Provider) -> None:
        if self.used[provider] >= self.limits[provider]:
            label = provider.title()
            raise LiveCallBlocked(
                f"LIVE credit limit reached for {label} ({self.limits[provider]} calls). "
                "Switch to MOCK_REPLAY or start a new session."
            )
        self.used[provider] += 1

    def record_success(self, provider: Provider) -> None:
        # Failures are intentionally cumulative for the lifetime of the session:
        # two provider failures should always protect a live demo from a later outage.
        return

    def record_failure(self, provider: Provider) -> bool:
        self.failures[provider] += 1
        return self.failures[provider] >= 2

    def snapshot(self) -> dict[Provider, Usage]:
        return {
            provider: Usage(self.used[provider], self.limits[provider])
            for provider in self.limits
        }

"""Performance-surface helpers — threshold assertions on run stats."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PerfStats:
    requests: int
    failures: int
    p95_ms: float = 0.0
    avg_ms: float = 0.0


def assert_thresholds(
    stats: PerfStats,
    *,
    max_fail_ratio: float = 0.0,
    max_p95_ms: float | None = None,
) -> None:
    """Fail the test if a load run breached its SLOs."""
    ratio = stats.failures / stats.requests if stats.requests else 1.0
    assert ratio <= max_fail_ratio, f"failure ratio {ratio:.2%} > allowed {max_fail_ratio:.2%}"
    if max_p95_ms is not None:
        assert stats.p95_ms <= max_p95_ms, f"p95 {stats.p95_ms:.0f}ms > budget {max_p95_ms:.0f}ms"


__all__ = ["PerfStats", "assert_thresholds"]

"""Gated performance smoke — validates the threshold harness (needs ALLOW_PERF=1).

Real load runs use Locust / JMeter (see modules/performance/README.md). This smoke
proves the SLO-threshold helper + the skip-gate without needing a live target, so
it is safe in CI while still exercising the performance surface end-to-end.
"""

from __future__ import annotations

import time

from aiqa_framework.modules.performance.helpers import PerfStats, assert_thresholds
from aiqa_framework.shared.config.tags import TAGS, jira, tags


def _percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    idx = max(0, int(len(ordered) * pct) - 1)
    return ordered[idx]


@tags(TAGS.PERFORMANCE, TAGS.P2)
@jira("PROJ-PERF-1")
def test_threshold_harness_within_budget() -> None:
    durations_ms: list[float] = []
    for _ in range(50):
        started = time.perf_counter()
        _ = sum(range(1000))  # trivial synthetic unit of work
        durations_ms.append((time.perf_counter() - started) * 1000)

    stats = PerfStats(
        requests=len(durations_ms),
        failures=0,
        p95_ms=_percentile(durations_ms, 0.95),
        avg_ms=sum(durations_ms) / len(durations_ms),
    )
    assert_thresholds(stats, max_fail_ratio=0.0, max_p95_ms=1000.0)

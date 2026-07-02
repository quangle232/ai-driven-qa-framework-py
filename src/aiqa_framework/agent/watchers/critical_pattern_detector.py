"""Deterministic critical-pattern detector (port of critical-pattern-detector.ts).

No LLM. Flags smoke/login/5xx/payment failures and ">=30% same-reason" clusters.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from aiqa_framework.agent.schemas.failure_event import FailureEvent

_KEYWORDS = {
    "login": ("login", "auth", "sign in", "unauthorized", "401"),
    "5xx": ("500", "502", "503", "504", "internal server error"),
    "payment": ("payment", "checkout", "charge", "billing"),
    "smoke": ("smoke",),
}


@dataclass
class CriticalEvent:
    trigger: str
    summary: str


def detect_criticals(failures: list[FailureEvent]) -> list[CriticalEvent]:
    events: list[CriticalEvent] = []
    if not failures:
        return events

    for trigger, words in _KEYWORDS.items():
        hits = [
            f
            for f in failures
            if any(w in f.error_message.lower() or w in f.test_id.lower() for w in words)
        ]
        if hits:
            events.append(
                CriticalEvent(trigger=trigger, summary=f"{len(hits)} failure(s) match '{trigger}'")
            )

    # >=30% of failures share one reason.
    counts = Counter(f.fingerprint for f in failures)
    top_fp, top_n = counts.most_common(1)[0]
    if top_n / len(failures) >= 0.30 and top_n > 1:
        sample = next(f for f in failures if f.fingerprint == top_fp)
        pct = round(top_n / len(failures) * 100)
        events.append(
            CriticalEvent(
                trigger="same-reason-cluster",
                summary=f"{pct}% share one error: {sample.error_message.splitlines()[0][:120]}",
            )
        )

    return events

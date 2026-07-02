"""Failure diagnosis (port of agents/failure-diagnosis-agent.ts).

Deterministic clustering + category by default; enriches each cluster's summary
via the configured LLM provider only when one is active (key present).
"""

from __future__ import annotations

from collections import defaultdict

from aiqa_framework.agent.providers.llm import get_provider
from aiqa_framework.agent.schemas.diagnosis import ClusterDiagnosis, RunDiagnosis
from aiqa_framework.agent.schemas.failure_event import FailureEvent
from aiqa_framework.agent.utils.run_id import resolve_run_id

_ENV_HINTS = (
    "timeout",
    "timed out",
    "connection",
    "econnrefused",
    "unavailable",
    "deadline",
    "reset by peer",
)


def _categorize(message: str) -> str:
    m = message.lower()
    if any(h in m for h in _ENV_HINTS):
        return "environment"
    if "assert" in m or "expected" in m:
        return "product"
    return "unknown"


def diagnose(failures: list[FailureEvent]) -> RunDiagnosis:
    provider, cfg = get_provider()

    groups: dict[str, list[FailureEvent]] = defaultdict(list)
    for f in failures:
        groups[f.fingerprint].append(f)

    clusters: list[ClusterDiagnosis] = []
    for fingerprint, items in groups.items():
        sample = items[0]
        category = _categorize(sample.error_message)
        summary = f"{len(items)} test(s) affected; likely {category}."
        if not cfg.dry_run:
            try:
                prompt = (
                    "You are a senior QA engineer. In 1-2 sentences, classify this test "
                    "failure (environment vs product vs flaky) and give the most likely "
                    f"root cause:\n\n{sample.error_message[:1500]}"
                )
                llm = provider.diagnose(prompt)
                if llm.strip():
                    summary = llm.strip()
            except Exception as e:  # noqa: BLE001 - LLM must never break the pipeline
                summary += f"  (LLM error: {e})"
        clusters.append(
            ClusterDiagnosis(
                fingerprint=fingerprint,
                count=len(items),
                sample_title=sample.title,
                error_message=sample.error_message.splitlines()[0][:200]
                if sample.error_message
                else "",
                category=category,
                summary=summary,
            )
        )

    return RunDiagnosis(
        run_id=resolve_run_id(),
        provider_name=cfg.name,
        dry_run=cfg.dry_run,
        total_failures=len(failures),
        clusters=clusters,
    )

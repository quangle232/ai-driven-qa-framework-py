"""API-surface helpers (REST / gRPC / GraphQL)."""

from __future__ import annotations


def within_sla(duration_ms: float, budget_ms: float) -> bool:
    """True if a call met its latency budget (use in a soft/hard assert)."""
    return duration_ms <= budget_ms


__all__ = ["within_sla"]

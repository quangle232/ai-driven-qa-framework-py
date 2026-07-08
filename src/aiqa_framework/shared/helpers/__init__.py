"""Cross-cutting helpers shared by every module (no surface-specific logic)."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from aiqa_framework.shared.helpers.cleanup import CleanupTracker


def slugify(text: str) -> str:
    """``"Log in with password"`` -> ``"log-in-with-password"``."""
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def snake(text: str) -> str:
    """Jira label -> pytest marker name (``service-request`` -> ``service_request``)."""
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def now_iso() -> str:
    """UTC timestamp, e.g. ``2026-07-02T00:00:00Z``."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = ["CleanupTracker", "slugify", "snake", "now_iso"]

"""Mobile-surface helpers (native Appium)."""

from __future__ import annotations


def accessibility_id(value: str) -> str:
    """Appium accessibility-id selector value (the preferred native locator)."""
    return value


__all__ = ["accessibility_id"]

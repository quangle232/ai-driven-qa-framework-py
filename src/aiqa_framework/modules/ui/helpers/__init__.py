"""UI-surface helpers (Playwright / POM)."""

from __future__ import annotations

# Locator priority honoured by ActionKeyword.heal (see conventions.md).
TEST_ATTR_PRIORITY = ("data-zcqa", "data-test-id", "data-id", "data-title")


def test_id(value: str, attr: str = "data-test-id") -> str:
    """CSS selector for a test attribute: ``test_id("email")`` -> ``[data-test-id="email"]``."""
    return f'[{attr}="{value}"]'


__all__ = ["TEST_ATTR_PRIORITY", "test_id"]

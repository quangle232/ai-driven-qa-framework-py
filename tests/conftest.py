"""Shared test fixtures. The web `page` (pytest-playwright) reuses the saved
storage state so UI/mobile-web tests start already-authenticated."""

from __future__ import annotations

import pytest

from aiqa_framework.core.auth import STORAGE_STATE


@pytest.fixture
def browser_context_args(browser_context_args: dict) -> dict:
    """Inject the saved storage state into every browser context when present."""
    if STORAGE_STATE.exists():
        return {**browser_context_args, "storage_state": str(STORAGE_STATE)}
    return browser_context_args

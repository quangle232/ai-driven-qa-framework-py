"""Shared test fixtures. The web `page` (pytest-playwright) reuses the saved
storage state so UI/mobile-web tests start already-authenticated."""

from __future__ import annotations

import pytest

from aiqa_framework.modules.ui.auth import STORAGE_STATE
from aiqa_framework.shared.helpers import CleanupTracker


@pytest.fixture
def browser_context_args(browser_context_args: dict) -> dict:
    """Inject the saved storage state into every browser context when present."""
    if STORAGE_STATE.exists():
        return {**browser_context_args, "storage_state": str(STORAGE_STATE)}
    return browser_context_args


@pytest.fixture
def cleanup():
    """Test-data lifecycle teardown (modules/ui/conventions.md).

    Register API deletions for everything the test creates — through the UI or
    as a precondition — and they run LIFO after the test, pass or fail::

        cleanup.add(users.remove, created.data.id)
        cleanup.add(api.delete, f"/items/{item_id}")
    """
    tracker = CleanupTracker()
    yield tracker
    tracker.run()

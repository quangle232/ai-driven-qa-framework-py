"""CleanupTracker — track created test data and tear it down via the API.

Implements the test-data lifecycle convention (modules/ui/conventions.md):
whatever a test creates (through the UI or as an API precondition) gets
registered here, and teardown deletes it via the API — LIFO, all actions run
even if one fails, and failures surface at the end.

Used by the shared ``cleanup`` fixture in ``tests/conftest.py``::

    def test_search_item(page, api, cleanup):
        item_id = api.post_json("/items", {"name": "Widget B"})["id"]
        cleanup.add(api.delete, f"/items/{item_id}")   # teardown via API
        ...
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class CleanupTracker:
    """Collects teardown callables and runs them LIFO at the end of the test."""

    def __init__(self) -> None:
        self._actions: list[tuple[Callable[..., Any], tuple, dict]] = []

    def add(self, action: Callable[..., Any], /, *args: Any, **kwargs: Any) -> None:
        """Register a teardown call, e.g. ``cleanup.add(users.remove, user_id)``."""
        self._actions.append((action, args, kwargs))

    def run(self) -> None:
        """Run all teardowns LIFO; keep going on errors, then raise a summary."""
        errors: list[str] = []
        while self._actions:
            action, args, kwargs = self._actions.pop()
            try:
                action(*args, **kwargs)
            except Exception as err:  # noqa: BLE001 — every cleanup must still run
                errors.append(f"{getattr(action, '__qualname__', action)}{args}: {err}")
        if errors:
            raise AssertionError("cleanup failed for: " + "; ".join(errors))

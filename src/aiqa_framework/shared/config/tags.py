"""Test tags as pytest markers — the ``helper/test-tags.ts`` analogue.

Usage mirrors the TS ``tags(...)`` helper::

    from aiqa_framework.shared.config.tags import TAGS, tags, jira

    @tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)
    @jira("PROJ-API-1")
    def test_something(api_client): ...

Convention: a FEATURE marker name equals the Jira label, linking the test to
``-m <label>`` selection, CI, and Jira — same as the TS framework.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest


class TAGS:
    # type
    REGRESSION = pytest.mark.regression
    SMOKE = pytest.mark.smoke
    # priority
    P0 = pytest.mark.p0
    P1 = pytest.mark.p1
    P2 = pytest.mark.p2
    # surface / transport
    API = pytest.mark.api
    GRPC = pytest.mark.grpc
    GRAPHQL = pytest.mark.graphql
    MOBILE = pytest.mark.mobile
    MOBILE_WEB = pytest.mark.mobile_web
    MOBILE_NATIVE = pytest.mark.mobile_native
    PERFORMANCE = pytest.mark.performance
    # known defect
    BUG = pytest.mark.bugs


def tags(*marks: Any) -> Callable[[Callable], Callable]:
    """Apply several markers at once: ``@tags(TAGS.API, TAGS.REGRESSION)``."""

    def decorator(fn: Callable) -> Callable:
        for mark in reversed(marks):
            fn = mark(fn)
        return fn

    return decorator


def jira(story_key: str):
    """Link a test to its parent Jira story (read by the bug reporter hook)."""
    return pytest.mark.jira(story_key)

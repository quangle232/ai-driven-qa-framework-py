"""UI-suite setup: ensure the web sign-in storage state exists once per session
(the global-setup analogue). Only loads when a UI test runs, so API/gRPC runs
never launch a browser."""

from __future__ import annotations

import pytest

from aiqa_framework.core.auth import ensure_auth


@pytest.fixture(scope="session", autouse=True)
def _web_auth(browser):
    try:
        ensure_auth(browser)
    except NotImplementedError:
        pytest.skip("authenticate() not implemented yet — fill in src/aiqa_framework/core/auth.py")

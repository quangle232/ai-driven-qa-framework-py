"""UI-suite setup: ensure the web sign-in storage state exists once per session
(the global-setup analogue). Only loads when a UI test runs, so API/gRPC runs
never launch a browser."""

from __future__ import annotations

import os

import pytest

from aiqa_framework.modules.ui.api_support import UiApiSupport
from aiqa_framework.modules.ui.auth import ensure_auth


@pytest.fixture(scope="session", autouse=True)
def _web_auth(browser):
    try:
        ensure_auth(browser)
    except NotImplementedError:
        pytest.skip("authenticate() not implemented yet — fill in modules/ui/auth.py")


@pytest.fixture
def api(page) -> UiApiSupport:
    """API support for UI tests — seed preconditions + teardown via HTTP.

    Backed by ``page.request`` so calls share the browser session's auth.
    Pair with the shared ``cleanup`` fixture (test-data lifecycle).
    """
    return UiApiSupport(page.request, base_url=os.environ.get("API_URL", ""))

"""Mobile-web (Playwright device emulation) fixtures. Parametrizes the device
and reuses the web POM + storage state (merges on top of the root context args).
"""

from __future__ import annotations

import pytest

from aiqa_framework.core.auth import ensure_auth


@pytest.fixture(scope="session", autouse=True)
def _web_auth(browser):
    try:
        ensure_auth(browser)
    except NotImplementedError:
        pytest.skip("authenticate() not implemented yet — fill in src/aiqa_framework/core/auth.py")


@pytest.fixture(params=["Pixel 7", "iPhone 14"])
def device_name(request) -> str:
    return request.param


@pytest.fixture
def browser_context_args(browser_context_args, playwright, device_name) -> dict:
    """Emulate a phone: merge the device descriptor onto the inherited args
    (which already include the saved storage state)."""
    return {**browser_context_args, **playwright.devices[device_name]}

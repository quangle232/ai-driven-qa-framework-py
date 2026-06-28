"""One-time web sign-in + storage-state reuse (port of global-setup +
authenticate-set-up + auth-config).

`ensure_auth` logs in once and saves the browser storage state; every UI test
reuses it via ``browser_context_args`` (see tests/conftest.py). API/gRPC runs set
``SKIP_WEB_AUTH=1`` so this is a no-op.
"""

from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import Browser

#: Saved storage state (cookies + localStorage), reused by every UI test.
STORAGE_STATE = Path.cwd() / ".auth" / "storage-state.json"


def authenticate(browser: Browser) -> None:
    """TODO (per project): implement your SUT sign-in.

    Create a context, perform the login flow, then persist the session::

        context = browser.new_context()
        page = context.new_page()
        page.goto(os.environ["AUTH_URL"])
        # ... fill credentials, submit, wait for the landing page ...
        context.storage_state(path=str(STORAGE_STATE))
        context.close()
    """
    raise NotImplementedError(
        "Implement authenticate() in src/aiqa_framework/core/auth.py for your SUT sign-in."
    )


def ensure_auth(browser: Browser) -> None:
    if os.environ.get("SKIP_WEB_AUTH") == "1":
        return
    refresh = os.environ.get("refresh") == "yes"
    if refresh or not STORAGE_STATE.exists():
        STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)
        authenticate(browser)

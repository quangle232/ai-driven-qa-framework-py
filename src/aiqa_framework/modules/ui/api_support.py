"""Playwright-backed API support for UI tests — seed/clean state only.

Use this to set up or tear down state for a UI test over HTTP (e.g. create a
user, then drive the login UI). It is NOT for API functional testing — that lives
in ``modules/api`` and never touches Playwright. Backed by Playwright's
``APIRequestContext`` so it can share cookies/auth with the browser session.
"""

from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext


class UiApiSupport:
    """Thin JSON wrapper over a Playwright ``APIRequestContext`` (``page.request``)."""

    def __init__(self, request: APIRequestContext, base_url: str = "") -> None:
        self._request = request
        self._base = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self._base}{path}"

    def get_json(self, path: str, **kwargs: Any) -> Any:
        response = self._request.get(self._url(path), **kwargs)
        assert response.ok, f"GET {path} -> HTTP {response.status}"
        return response.json()

    def post_json(self, path: str, data: dict | None = None, **kwargs: Any) -> Any:
        response = self._request.post(self._url(path), data=data, **kwargs)
        assert response.ok, f"POST {path} -> HTTP {response.status}"
        return response.json() if response.text() else None

    def delete(self, path: str, **kwargs: Any) -> None:
        response = self._request.delete(self._url(path), **kwargs)
        assert response.ok, f"DELETE {path} -> HTTP {response.status}"

"""respx handlers — the IN-PROCESS mock layer (intercepts httpx).

Use respx for node-level/service tests driven by plain httpx, mocking the app's
own outbound calls, or injecting failures. The FastAPI app is the real-port
target for the Service-Object specs. Both delegate to the same ``mock_store``.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from aiqa_framework.modules.api.rest.mock.store import mock_store

#: Base origin the respx routes match. Tests call httpx against this.
MOCK_BASE = "https://api.mock.test"


def _resp(result: tuple[int, Any]) -> httpx.Response:
    status, body = result
    return httpx.Response(status, json=body)


def _body(request: httpx.Request) -> Any:
    return json.loads(request.content or b"{}")


def register(router: Any, base: str = MOCK_BASE) -> None:
    """Register store-backed routes on a respx router (the ``respx_mock`` fixture)."""
    router.get(f"{base}/users").mock(side_effect=lambda req: _resp(mock_store.list_users()))
    router.post(f"{base}/users").mock(
        side_effect=lambda req: _resp(mock_store.create_user(_body(req)))
    )
    router.post(f"{base}/auth/login").mock(
        side_effect=lambda req: _resp(mock_store.login(_body(req)))
    )
    router.get(url__regex=rf"{base}/users/(?P<user_id>[^/]+)$").mock(
        side_effect=lambda req, user_id: _resp(mock_store.get_user(user_id))
    )

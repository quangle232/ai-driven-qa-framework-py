"""SAMPLE respx spec — the IN-PROCESS mock layer (intercepts httpx).

Use respx for service tests driven by plain httpx and for INJECTING failures.
The Service-Object specs (test_sample_api.py) use the FastAPI mock instead.
"""

from __future__ import annotations

import httpx

from aiqa_framework.modules.api.rest.mock.respx_handlers import MOCK_BASE, register
from aiqa_framework.modules.api.rest.models import UserList
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P2)
@jira("PROJ-API-2")
def test_respx_intercepts_users(respx_mock) -> None:
    register(respx_mock)
    resp = httpx.get(f"{MOCK_BASE}/users")
    assert resp.status_code == 200
    UserList.validate_python(resp.json())  # raises if schema drifts


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P2)
@jira("PROJ-API-2")
def test_respx_injects_500(respx_mock) -> None:
    respx_mock.get(f"{MOCK_BASE}/users").mock(
        return_value=httpx.Response(500, json={"error": "server_error", "message": "boom"})
    )
    resp = httpx.get(f"{MOCK_BASE}/users")
    assert resp.status_code == 500

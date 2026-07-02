"""SAMPLE API spec — Service-Object Model over httpx (port of sample.api.spec.ts).

Call SERVICES, never the raw client. Positive + negative + schema + SLA, AAA.
Runs against the in-process FastAPI mock with no backend.
"""

from __future__ import annotations

from aiqa_framework.modules.api.rest.services.auth_service import AuthService
from aiqa_framework.modules.api.rest.services.user_service import UserService
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-API-1")
def test_list_users_schema_valid_within_sla(api_client) -> None:
    users = UserService(api_client)
    res = users.list()
    assert res.status == 200
    assert len(res.data) > 0
    assert res.duration_ms < 1000, "list users should respond < 1s"


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-API-1")
def test_create_then_get_then_cleanup(api_client) -> None:
    users = UserService(api_client)
    created = users.create(username="newbie", email="newbie@example.com")
    assert created.status == 201

    fetched = users.get_by_id(created.data.id)
    assert fetched.data.username == "newbie"
    assert fetched.data.email == "newbie@example.com"

    users.remove(created.data.id)  # leave the SUT clean


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P2)
@jira("PROJ-API-1")
def test_unknown_user_404(api_client) -> None:
    res = UserService(api_client).get_by_id_expecting_not_found("does-not-exist")
    assert res.status == 404
    assert res.data.error == "not_found"


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P2)
@jira("PROJ-API-1")
def test_invalid_email_400(api_client) -> None:
    res = UserService(api_client).create_expecting_bad_request(
        {"username": "x", "email": "not-an-email"}
    )
    assert res.status == 400
    assert res.data.error == "bad_request"


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P0)
@jira("PROJ-API-1")
def test_login_ok_and_unauthorized(api_client) -> None:
    auth = AuthService(api_client)

    ok = auth.login(username="demo", password="demo-pass")
    assert ok.data.token
    assert ok.data.user.username == "demo"

    bad = auth.login_expecting_unauthorized(username="demo", password="wrong")
    assert bad.status == 401

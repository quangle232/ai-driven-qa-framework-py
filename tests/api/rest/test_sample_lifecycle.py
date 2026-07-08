"""SAMPLE — test-data lifecycle with the shared ``cleanup`` fixture.

Demonstrates the convention (modules/ui/conventions.md): create IS under test →
track the id for API teardown; data is a PRECONDITION → seed it via the API,
exercise the feature, tear down via the API. Runs green against the in-process
FastAPI mock — teardown runs LIFO even when the test fails.
"""

from __future__ import annotations

from aiqa_framework.modules.api.rest.services.user_service import UserService
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-API-1")
def test_create_user_tracks_id_for_teardown(api_client, cleanup) -> None:
    """CREATE is under test → do it, track the id, teardown deletes via API."""
    users = UserService(api_client)

    created = users.create(username="creator", email="creator@example.com")
    cleanup.add(users.remove, created.data.id)  # runs after the test, pass or fail

    assert created.status == 201
    assert users.get_by_id(created.data.id).data.username == "creator"


@tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-API-1")
def test_list_finds_user_seeded_as_precondition(api_client, cleanup) -> None:
    """Data is a PRECONDITION → seed via the API, test the feature, teardown via API."""
    users = UserService(api_client)

    # Precondition via the API (never via the UI) + track for teardown.
    seeded = users.create(username="finder", email="finder@example.com")
    cleanup.add(users.remove, seeded.data.id)

    # The functionality under test (here: list/search).
    listed = users.list()
    assert any(user.id == seeded.data.id for user in listed.data)

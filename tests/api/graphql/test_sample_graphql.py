"""SAMPLE GraphQL specs — run headless via the in-process mock.

Demonstrates: call the GraphQLClient (never httpx in a spec), keep documents in
queries/, validate the data payload with pydantic, assert GraphQL errors.
"""

from __future__ import annotations

from aiqa_framework.modules.api.graphql.models import UserData, UsersData
from aiqa_framework.modules.api.graphql.queries import GET_USER, LIST_USERS
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.GRAPHQL, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-GQL-1")
def test_list_users_returns_all(graphql_client) -> None:
    result = graphql_client.execute(LIST_USERS, schema=UsersData)
    assert len(result.data.users) == 2


@tags(TAGS.GRAPHQL, TAGS.P2)
@jira("PROJ-GQL-2")
def test_get_user_by_id(graphql_client) -> None:
    result = graphql_client.execute(GET_USER, {"id": "u1"}, schema=UserData)
    assert result.data.user is not None
    assert result.data.user.username == "alice"


@tags(TAGS.GRAPHQL, TAGS.P2)
@jira("PROJ-GQL-3")
def test_unknown_user_surfaces_error(graphql_client) -> None:
    result = graphql_client.execute(GET_USER, {"id": "nope"}, allow_errors=True)
    assert result.errors, "expected a GraphQL error for an unknown user"

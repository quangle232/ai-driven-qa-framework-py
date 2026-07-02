"""GraphQL-suite fixtures. By default the client runs against the FastAPI GraphQL
mock in-process via Starlette's ``TestClient`` (sync ASGI driver; no backend, no
port). Set ``GRAPHQL_URL`` to hit a real API; ``API_MOCK=1`` forces the mock."""

from __future__ import annotations

import os

import httpx
import pytest
from starlette.testclient import TestClient

from aiqa_framework.modules.api.graphql.client import GraphQLClient
from aiqa_framework.modules.api.graphql.mock import create_graphql_mock_app


@pytest.fixture
def graphql_client():
    real = os.environ.get("GRAPHQL_URL")
    if real and os.environ.get("API_MOCK") != "1":
        with httpx.Client() as client:
            yield GraphQLClient(client, base_url=real, token=os.environ.get("API_TOKEN"))
    else:
        with TestClient(create_graphql_mock_app()) as client:
            yield GraphQLClient(client, base_url="")

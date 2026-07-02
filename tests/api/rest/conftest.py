"""REST API-suite fixtures. By default the client runs against the FastAPI mock
in-process via Starlette's ``TestClient`` (sync ASGI driver; no backend, no port).
Set ``API_BASE_URL`` to hit a real API; ``API_MOCK=1`` forces the mock."""

from __future__ import annotations

import os

import httpx
import pytest
from starlette.testclient import TestClient

from aiqa_framework.modules.api.rest.client import ApiClient
from aiqa_framework.modules.api.rest.mock.standalone_app import create_mock_app
from aiqa_framework.modules.api.rest.mock.store import mock_store


@pytest.fixture(autouse=True)
def _reset_store():
    mock_store.reset()
    yield


@pytest.fixture
def api_client():
    real = os.environ.get("API_BASE_URL")
    if real and os.environ.get("API_MOCK") != "1":
        with httpx.Client() as client:
            yield ApiClient(client, base_url=real, token=os.environ.get("API_TOKEN"))
    else:
        with TestClient(create_mock_app()) as client:
            yield ApiClient(client, base_url="")

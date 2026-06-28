"""API-suite fixtures. By default the client runs against the FastAPI mock
in-process via httpx ASGITransport (no backend, no port). Set ``API_BASE_URL``
to hit a real API; ``API_MOCK=1`` forces the mock."""

from __future__ import annotations

import os

import httpx
import pytest

from aiqa_framework.api.client import ApiClient
from aiqa_framework.api.mock.standalone_app import create_mock_app
from aiqa_framework.api.mock.store import mock_store


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
        transport = httpx.ASGITransport(app=create_mock_app())
        with httpx.Client(transport=transport) as client:
            yield ApiClient(client, base_url="http://mock")

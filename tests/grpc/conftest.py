"""gRPC-suite fixtures: start the in-process mock server once per session and
provide authenticated / unauthenticated clients. ``GRPC_MOCK=0`` connects to a
real service at GRPC_HOST:GRPC_PORT instead.

(pytest-grpc is available as an alternative; we use a real mock server here for
realistic streaming + status-code behaviour.)
"""

from __future__ import annotations

import os

import pytest

from aiqa_framework.config.settings import get_settings
from aiqa_framework.grpc.client import GameClient
from aiqa_framework.grpc.mock_server import start_grpc_mock


@pytest.fixture(scope="session")
def grpc_address():
    if os.environ.get("GRPC_MOCK") == "0":
        s = get_settings()
        yield (s.grpc_host, s.grpc_port)
        return
    server, port = start_grpc_mock(0)
    try:
        yield ("127.0.0.1", port)
    finally:
        server.stop(0)


@pytest.fixture
def game_client(grpc_address):
    host, port = grpc_address
    client = GameClient(host=host, port=port, token="test-token")
    client.wait_for_ready(5.0)
    yield client
    client.close()


@pytest.fixture
def game_client_no_auth(grpc_address):
    host, port = grpc_address
    client = GameClient(host=host, port=port)
    client.wait_for_ready(5.0)
    yield client
    client.close()

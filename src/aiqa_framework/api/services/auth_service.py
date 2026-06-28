"""AuthService — Service-Object Model for the auth endpoints."""

from __future__ import annotations

from aiqa_framework.api.client import ApiClient, ApiResult
from aiqa_framework.api.models import ErrorResponse, LoginResponse


class AuthService:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    def login(self, username: str, password: str) -> ApiResult:
        return self.api.post(
            "/auth/login",
            body={"username": username, "password": password},
            schema=LoginResponse,
            expected_status=200,
        )

    def login_expecting_unauthorized(self, username: str, password: str) -> ApiResult:
        return self.api.post(
            "/auth/login",
            body={"username": username, "password": password},
            schema=ErrorResponse,
            expected_status=401,
        )

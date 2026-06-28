"""UserService — Service-Object Model for the /users endpoints."""

from __future__ import annotations

from typing import Any

from aiqa_framework.api.client import ApiClient, ApiResult
from aiqa_framework.api.models import ErrorResponse, User, UserList


class UserService:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    def list(self) -> ApiResult:
        return self.api.get("/users", schema=UserList, expected_status=200)

    def get_by_id(self, user_id: str) -> ApiResult:
        return self.api.get(f"/users/{user_id}", schema=User, expected_status=200)

    def get_by_id_expecting_not_found(self, user_id: str) -> ApiResult:
        return self.api.get(f"/users/{user_id}", schema=ErrorResponse, expected_status=404)

    def create(self, username: str, email: str) -> ApiResult:
        return self.api.post(
            "/users", body={"username": username, "email": email}, schema=User, expected_status=201
        )

    def create_expecting_bad_request(self, body: dict[str, Any]) -> ApiResult:
        return self.api.post("/users", body=body, schema=ErrorResponse, expected_status=400)

    def remove(self, user_id: str) -> ApiResult:
        return self.api.delete(f"/users/{user_id}", expected_status=204)

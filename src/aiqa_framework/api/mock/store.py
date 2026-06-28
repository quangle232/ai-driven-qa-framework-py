"""In-memory mock business logic, shared by BOTH mock layers (respx + the
FastAPI standalone app) so they cannot drift. Each method returns
``(status, body)``; ``reset()`` restores the seed for test isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError

from aiqa_framework.api.models import CreateUserRequest

_VALID = {"username": "demo", "password": "demo-pass"}
_SEED = [
    {"id": "u-1", "username": "demo", "email": "demo@example.com", "createdAt": "2026-01-01T00:00:00.000Z"},
    {"id": "u-2", "username": "alice", "email": "alice@example.com", "createdAt": "2026-01-02T00:00:00.000Z"},
]

Response = tuple[int, Any]


class MockApiStore:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.users: list[dict] = [dict(u) for u in _SEED]

    def list_users(self) -> Response:
        return 200, self.users

    def get_user(self, user_id: str) -> Response:
        for u in self.users:
            if u["id"] == user_id:
                return 200, u
        return 404, {"error": "not_found", "message": f"User {user_id} does not exist"}

    def create_user(self, payload: Any) -> Response:
        try:
            data = CreateUserRequest.model_validate(payload)
        except ValidationError as e:
            return 400, {"error": "bad_request", "message": "; ".join(err["msg"] for err in e.errors())}
        if any(u["username"] == data.username for u in self.users):
            return 409, {"error": "conflict", "message": "username already taken"}
        user = {
            "id": f"u-{uuid.uuid4().hex[:8]}",
            "username": data.username,
            "email": data.email,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        self.users.append(user)
        return 201, user

    def delete_user(self, user_id: str) -> Response:
        before = len(self.users)
        self.users = [u for u in self.users if u["id"] != user_id]
        if len(self.users) == before:
            return 404, {"error": "not_found", "message": f"User {user_id} does not exist"}
        return 204, None

    def login(self, payload: Any) -> Response:
        creds = payload or {}
        if creds.get("username") == _VALID["username"] and creds.get("password") == _VALID["password"]:
            user = next(u for u in self.users if u["username"] == creds["username"])
            return 200, {"token": "mock-jwt-token", "user": user}
        return 401, {"error": "unauthorized", "message": "invalid credentials"}


#: Process-wide singleton shared by the FastAPI app and respx handlers.
mock_store = MockApiStore()

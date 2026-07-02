"""In-process GraphQL mock (FastAPI) for the sample spec.

Resolves the two sample documents by shape (no real GraphQL engine needed). Serve
via httpx ASGITransport so tests run headless — same pattern as the REST mock.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request

_USERS = [
    {"id": "u1", "username": "alice", "email": "alice@example.com"},
    {"id": "u2", "username": "bob", "email": "bob@example.com"},
]


def create_graphql_mock_app() -> FastAPI:
    app = FastAPI(title="AIQA GraphQL mock")

    @app.post("/graphql")
    async def graphql(request: Request) -> dict[str, Any]:
        body = await request.json()
        query = body.get("query", "")
        variables = body.get("variables") or {}

        if "users" in query and "user(" not in query:
            return {"data": {"users": _USERS}}
        if "user(" in query:
            uid = variables.get("id")
            match = next((u for u in _USERS if u["id"] == uid), None)
            if match is None:
                return {"data": {"user": None}, "errors": [{"message": f"user {uid} not found"}]}
            return {"data": {"user": match}}
        return {"data": None, "errors": [{"message": "unknown query"}]}

    return app

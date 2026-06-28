"""FastAPI standalone mock — the SERVICE-VIRTUALIZATION layer.

The API specs hit this in-process via httpx ``ASGITransport`` (no port needed),
and you can also run it as a real server for other tools/teams::

    poe mock-api            # uvicorn on MOCK_API_PORT (default 4010)

Shares ``mock_store`` with the respx layer.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from aiqa_framework.api.mock.store import mock_store


def create_mock_app() -> FastAPI:
    app = FastAPI(title="aiqa mock API")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/auth/login")
    async def login(payload: dict) -> JSONResponse:
        status, body = mock_store.login(payload)
        return JSONResponse(body, status_code=status)

    @app.get("/users")
    def list_users() -> JSONResponse:
        status, body = mock_store.list_users()
        return JSONResponse(body, status_code=status)

    @app.get("/users/{user_id}")
    def get_user(user_id: str) -> JSONResponse:
        status, body = mock_store.get_user(user_id)
        return JSONResponse(body, status_code=status)

    @app.post("/users")
    async def create_user(payload: dict) -> JSONResponse:
        status, body = mock_store.create_user(payload)
        return JSONResponse(body, status_code=status)

    @app.delete("/users/{user_id}")
    def delete_user(user_id: str) -> Response:
        status, body = mock_store.delete_user(user_id)
        if status == 204:
            return Response(status_code=204)
        return JSONResponse(body, status_code=status)

    return app


app = create_mock_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("MOCK_API_PORT", "4010")))

"""ApiClient — the single HTTP interaction layer for API tests (the REST
analogue of ActionKeyword). Specs call ``api/services/*``; services call this;
nothing calls httpx directly.

Best practices: central base URL + auth + timeout, per-call duration capture,
optional status assertion, and optional pydantic validation (zod analogue).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError


@dataclass
class ApiResult:
    status: int
    ok: bool
    headers: dict[str, str]
    data: Any
    duration_ms: float


Schema = type[BaseModel] | TypeAdapter | None


class ApiClient:
    def __init__(
        self,
        client: httpx.Client,
        base_url: str = "",
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = client
        self._base = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout

    def get(self, path: str, **kw: Any) -> ApiResult:
        return self._send("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> ApiResult:
        return self._send("POST", path, **kw)

    def put(self, path: str, **kw: Any) -> ApiResult:
        return self._send("PUT", path, **kw)

    def patch(self, path: str, **kw: Any) -> ApiResult:
        return self._send("PATCH", path, **kw)

    def delete(self, path: str, **kw: Any) -> ApiResult:
        return self._send("DELETE", path, **kw)

    def _send(
        self,
        method: str,
        path: str,
        *,
        schema: Schema = None,
        body: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        token: str | None = None,
        expected_status: int | list[int] | None = None,
    ) -> ApiResult:
        url = (
            path if path.startswith(("http://", "https://")) else f"{self._base}/{path.lstrip('/')}"
        )
        bearer = token if token is not None else self._token
        hdrs = {"accept": "application/json", **(headers or {})}
        if bearer:
            hdrs["authorization"] = f"Bearer {bearer}"

        started = time.monotonic()
        try:
            resp = self._client.request(
                method, url, json=body, params=params, headers=hdrs, timeout=self._timeout
            )
        except httpx.HTTPError as err:
            raise AssertionError(f"API {method} {url} failed before a response: {err}") from err
        duration_ms = (time.monotonic() - started) * 1000

        raw = resp.text
        parsed: Any = None
        if raw:
            try:
                parsed = resp.json()
            except (json.JSONDecodeError, ValueError):
                parsed = raw

        self._assert_status(method, url, resp.status_code, parsed, expected_status)
        data = self._validate(method, url, schema, parsed) if schema is not None else parsed

        return ApiResult(
            status=resp.status_code,
            ok=resp.is_success,
            headers=dict(resp.headers),
            data=data,
            duration_ms=duration_ms,
        )

    @staticmethod
    def _assert_status(
        method: str, url: str, status: int, body: Any, expected: int | list[int] | None
    ) -> None:
        if expected is None:
            return
        allowed = expected if isinstance(expected, list) else [expected]
        if status in allowed:
            return
        raise AssertionError(
            f"API {method} {url} returned {status}, expected {' or '.join(map(str, allowed))}.\n"
            f"Response: {ApiClient._snippet(body)}"
        )

    @staticmethod
    def _validate(method: str, url: str, schema: Schema, body: Any) -> Any:
        try:
            if isinstance(schema, TypeAdapter):
                return schema.validate_python(body)
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                return schema.model_validate(body)
        except ValidationError as err:
            raise AssertionError(
                f"API {method} {url} response failed schema validation:\n{err}\n"
                f"Response: {ApiClient._snippet(body)}"
            ) from err
        return body

    @staticmethod
    def _snippet(body: Any) -> str:
        s = body if isinstance(body, str) else json.dumps(body, default=str)
        if not s:
            return "(empty)"
        return s if len(s) <= 300 else s[:297] + "..."

"""GraphQLClient — the single GraphQL interaction layer (httpx POST /graphql).

Specs call ``graphql/queries`` through this client; nothing calls httpx directly.
Mirrors the REST ``ApiClient``: base URL + bearer auth + timeout, duration capture,
GraphQL-error assertion, and optional pydantic validation of the ``data`` payload.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

Schema = type[BaseModel] | TypeAdapter | None


@dataclass
class GraphQLResult:
    status: int
    data: Any
    errors: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0


class GraphQLClient:
    def __init__(
        self,
        client: httpx.Client,
        base_url: str = "",
        endpoint: str = "/graphql",
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = client
        self._url = f"{base_url.rstrip('/')}{endpoint}"
        self._token = token
        self._timeout = timeout

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        *,
        schema: Schema = None,
        allow_errors: bool = False,
    ) -> GraphQLResult:
        headers = {"accept": "application/json"}
        if self._token:
            headers["authorization"] = f"Bearer {self._token}"

        started = time.monotonic()
        try:
            resp = self._client.post(
                self._url,
                json={"query": query, "variables": variables or {}},
                headers=headers,
                timeout=self._timeout,
            )
        except httpx.HTTPError as err:
            raise AssertionError(
                f"GraphQL POST {self._url} failed before a response: {err}"
            ) from err
        duration_ms = (time.monotonic() - started) * 1000

        payload = resp.json() if resp.text else {}
        errors = payload.get("errors") or []
        data = payload.get("data")

        if errors and not allow_errors:
            raise AssertionError(f"GraphQL {self._url} returned errors: {errors}")
        if schema is not None and data is not None:
            data = self._validate(schema, data)

        return GraphQLResult(
            status=resp.status_code, data=data, errors=errors, duration_ms=duration_ms
        )

    @staticmethod
    def _validate(schema: Schema, data: Any) -> Any:
        try:
            if isinstance(schema, TypeAdapter):
                return schema.validate_python(data)
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                return schema.model_validate(data)
        except ValidationError as err:
            raise AssertionError(f"GraphQL response failed schema validation:\n{err}") from err
        return data

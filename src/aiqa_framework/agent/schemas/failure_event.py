"""A single test failure, normalized (port of failure-event.schema.ts)."""

from __future__ import annotations

from pydantic import BaseModel

FAILURE_EVENT_SCHEMA_VERSION = "aiqa.failure-event.v1"


class FailureEvent(BaseModel):
    schema_version: str = FAILURE_EVENT_SCHEMA_VERSION
    test_id: str
    title: str
    file: str
    status: str  # failed | error
    error_message: str
    duration_ms: float = 0.0
    is_final_failure: bool = True
    fingerprint: str  # stable hash of (file + normalized error) for clustering

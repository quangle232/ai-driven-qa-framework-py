"""Failure diagnosis output (port of diagnosis.schema.ts)."""

from __future__ import annotations

from pydantic import BaseModel

DIAGNOSIS_SCHEMA_VERSION = "aiqa.diagnosis.v1"


class ClusterDiagnosis(BaseModel):
    fingerprint: str
    count: int
    sample_title: str
    error_message: str
    category: str = "unknown"  # environment | product | flaky | unknown
    summary: str = ""


class RunDiagnosis(BaseModel):
    schema_version: str = DIAGNOSIS_SCHEMA_VERSION
    run_id: str
    provider_name: str
    dry_run: bool
    total_failures: int
    clusters: list[ClusterDiagnosis]

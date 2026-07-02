"""Normalized CI metadata (port of ci-metadata.schema.ts)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

CI_METADATA_SCHEMA_VERSION = "aiqa.ci-metadata.v1"
CiProvider = Literal["jenkins", "github-actions", "gitlab-ci", "local"]


class CiMetadata(BaseModel):
    schema_version: str = CI_METADATA_SCHEMA_VERSION
    provider: str
    run_id: str
    run_url: str | None = None
    job_name: str | None = None
    branch: str | None = None
    commit: str | None = None
    environment: str | None = None  # dev / test / prod
    triggered_by: str | None = None
    started_at: str | None = None  # ISO-8601

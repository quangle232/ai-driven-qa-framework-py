"""Resolve a stable run id (port of utils/run-id.ts)."""

from __future__ import annotations

import os
from datetime import UTC, datetime


def resolve_run_id(env: dict[str, str] | None = None) -> str:
    env = env if env is not None else dict(os.environ)
    for key in ("AIQA_RUN_ID", "GITHUB_RUN_ID", "BUILD_NUMBER", "CI_PIPELINE_ID"):
        if env.get(key):
            return str(env[key])
    return datetime.now(UTC).strftime("local-%Y%m%d-%H%M%S")

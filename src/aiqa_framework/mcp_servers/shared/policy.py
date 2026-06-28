"""Shared MCP guardrails (port of mcp/shared/policy.ts). Read-only by default."""

from __future__ import annotations

import os

READ_LINE_CAP = 120
RESULT_BYTE_CAP = 80_000

BLOCKED_PATHS = (
    ".env",
    ".env.local",
    ".env.dev",
    ".env.test",
    ".env.prod",
    ".env.jira",
    ".auth/",
    "storage-state",
    "node_modules/",
    ".git/",
    "secrets/",
    "credentials/",
)


def is_blocked(path: str) -> bool:
    norm = path.replace("\\", "/").lstrip("./")
    return any(seg in norm for seg in BLOCKED_PATHS)


def allow_exec() -> bool:
    return os.environ.get("AIQA_ALLOW_EXEC") == "true"


def allow_memory_write() -> bool:
    return os.environ.get("AIQA_ALLOW_MEMORY_WRITE") == "true"

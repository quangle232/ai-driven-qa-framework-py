"""Deterministic safety gate for generated code (port of patch-guard.ts).

Refuses patches that touch protected paths, hardcode secrets, use hard sleeps,
skip tests, or import Playwright's raw API in a spec. Last line of defence
before any disk write.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

BLOCKED_PREFIXES = (
    ".auth/",
    "environments/",
    "conftest.py",
    "pyproject.toml",
    "src/aiqa_framework/modules/ui/auth.py",
    "src/aiqa_framework/shared/reporting/",
    "src/aiqa_framework/shared/config/",
    "ci/",
    "src/aiqa_framework/modules/api/grpc/proto/",
    "src/aiqa_framework/modules/api/rest/contracts/",
    ".github/",
    ".gitlab-ci.yml",
    ".git/",
)

_SECRET_RX = re.compile(
    r"(?:password|api[_-]?key|token|secret)\s*[:=]\s*[\"'][^\"']{6,}[\"']", re.IGNORECASE
)
_HARD_WAIT = re.compile(r"\btime\.sleep\s*\(")
_SKIP = re.compile(r"@pytest\.mark\.skip\b|pytest\.skip\s*\(")
_RAW_PW_IMPORT = re.compile(r"^\s*from\s+playwright\.sync_api\s+import\b", re.MULTILINE)


@dataclass
class GuardResult:
    path: str
    accepted: bool
    reasons: list[str] = field(default_factory=list)


def guard_file(path: str, content: str) -> GuardResult:
    reasons: list[str] = []
    norm = path.replace("\\", "/").lstrip("./")

    if any(norm.startswith(p) for p in BLOCKED_PREFIXES):
        reasons.append(f"writes to a protected path ({norm})")
    if _SECRET_RX.search(content):
        reasons.append("hardcoded secret/credential literal")
    if _HARD_WAIT.search(content):
        reasons.append("hard wait (time.sleep) — use explicit waits")
    if _SKIP.search(content):
        reasons.append("test.skip on logic")
    # A spec must use Page Objects, not raw Playwright.
    if norm.startswith("tests/") and norm.endswith(".py") and _RAW_PW_IMPORT.search(content):
        reasons.append("spec imports playwright.sync_api directly (use a Page Object)")

    return GuardResult(path=norm, accepted=not reasons, reasons=reasons)

"""Read ``test-output/pytest-report.json`` (pytest-json-report) into normalized
FailureEvents — the Python analogue of the playwright-report-reader.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from aiqa_framework.ai_qa_agent.schemas.failure_event import FailureEvent
from aiqa_framework.ai_qa_agent.utils.paths import pytest_report_path

_NORMALIZE = re.compile(r"0x[0-9a-f]+|\d+", re.IGNORECASE)


def fingerprint(file: str, message: str) -> str:
    first_line = (message or "").strip().splitlines()[0] if message else ""
    norm = _NORMALIZE.sub("#", f"{file}|{first_line}".lower())
    return hashlib.sha1(norm.encode()).hexdigest()[:12]


def _error_message(call: dict, outcome: str) -> str:
    if not call:
        return outcome
    longrepr = call.get("longrepr")
    if isinstance(longrepr, str) and longrepr:
        return longrepr
    crash = call.get("crash") or {}
    return crash.get("message") or str(longrepr or outcome)


def read_failures(path: Path | None = None) -> tuple[list[FailureEvent], dict]:
    report_path = path or pytest_report_path()
    if not report_path.exists():
        return [], {}

    data = json.loads(report_path.read_text())
    summary = data.get("summary", {})
    failures: list[FailureEvent] = []

    for test in data.get("tests", []):
        outcome = test.get("outcome", "")
        if outcome not in ("failed", "error"):
            continue
        node_id = test.get("nodeid", "")
        call = test.get("call") or test.get("setup") or {}
        message = _error_message(call, outcome)[:2000]
        file = node_id.split("::")[0]
        failures.append(
            FailureEvent(
                test_id=node_id,
                title=node_id.split("::")[-1] or node_id,
                file=file,
                status=outcome,
                error_message=message,
                duration_ms=float(call.get("duration", 0.0)) * 1000,
                fingerprint=fingerprint(file, message),
            )
        )
    return failures, summary

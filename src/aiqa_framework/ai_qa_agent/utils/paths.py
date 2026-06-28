"""Output paths for the AI QA Agent (port of utils/paths.ts)."""

from __future__ import annotations

import os
from pathlib import Path


def out_dir() -> Path:
    return Path(os.environ.get("AIQA_OUT_DIR", "test-output/ai"))


def ai_qa_out_dir() -> Path:
    d = out_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def pytest_report_path() -> Path:
    return Path("test-output/pytest-report.json")

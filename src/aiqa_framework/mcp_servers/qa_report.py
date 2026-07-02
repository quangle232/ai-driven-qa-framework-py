"""MCP server: aiqa-qa-report — last-run results (read-only).

Tools: get_run_summary, get_failed_tests, get_failure_clusters,
get_critical_events, get_diagnosis, list_runs. Reads test-output/ai/.
Run: ``python -m aiqa_framework.mcp_servers.qa_report``.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from aiqa_framework.mcp_servers.shared.result import cap, read_json

mcp = FastMCP("aiqa-qa-report")
_OUT = "test-output/ai"


@mcp.tool()
def get_run_summary() -> dict:
    """Pass/fail summary + CI metadata for the last run."""
    return cap(
        {
            "summary": read_json(f"{_OUT}/summary.json", {}),
            "ci": read_json(f"{_OUT}/ci-metadata.json", {}),
        }
    )


@mcp.tool()
def get_failed_tests() -> list:
    """Final-attempt failures from the last run."""
    return cap(read_json(f"{_OUT}/failures.json", []))


@mcp.tool()
def get_failure_clusters() -> list:
    """Diagnosed failure clusters (by fingerprint)."""
    return cap(read_json(f"{_OUT}/diagnosis.json", {}).get("clusters", []))


@mcp.tool()
def get_critical_events() -> list:
    """Critical patterns detected from the last run's failures."""
    from aiqa_framework.agent.schemas.failure_event import FailureEvent
    from aiqa_framework.agent.watchers.critical_pattern_detector import detect_criticals

    failures = [FailureEvent(**f) for f in read_json(f"{_OUT}/failures.json", [])]
    return cap([c.__dict__ for c in detect_criticals(failures)])


@mcp.tool()
def get_diagnosis() -> str:
    """The human-readable diagnosis markdown."""
    path = Path(f"{_OUT}/diagnosis.md")
    return path.read_text()[:80_000] if path.exists() else "(no diagnosis.md — run `aiqa diagnose`)"


@mcp.tool()
def list_runs() -> list:
    """Known runs (this layout keeps the latest run only)."""
    ci = read_json(f"{_OUT}/ci-metadata.json", {})
    return [ci["run_id"]] if ci.get("run_id") else []


if __name__ == "__main__":
    mcp.run()

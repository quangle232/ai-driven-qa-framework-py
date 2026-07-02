"""MCP server: aiqa-test-runner — list tests + last status (read-only);
trigger a targeted run only when AIQA_ALLOW_EXEC=true.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from aiqa_framework.mcp_servers.shared.policy import allow_exec
from aiqa_framework.mcp_servers.shared.result import cap, read_json

mcp = FastMCP("aiqa-test-runner")


@mcp.tool()
def list_available_tests() -> list:
    """Spec files discovered under tests/."""
    return cap([str(p) for p in Path("tests").rglob("test_*.py")])


@mcp.tool()
def get_last_run_status() -> dict:
    """Summary of the last pytest run (from test-output/ai/summary.json)."""
    return cap(read_json("test-output/ai/summary.json", {}))


@mcp.tool()
def trigger_targeted_run(marker: str = "smoke") -> dict:
    """Run `pytest -m <marker>` — disabled unless AIQA_ALLOW_EXEC=true."""
    if not allow_exec():
        return {"ok": False, "error": "execution disabled — set AIQA_ALLOW_EXEC=true"}
    proc = subprocess.run(["pytest", "-m", marker], capture_output=True, text=True)
    return cap(
        {"ok": proc.returncode == 0, "returncode": proc.returncode, "tail": proc.stdout[-2000:]}
    )


if __name__ == "__main__":
    mcp.run()

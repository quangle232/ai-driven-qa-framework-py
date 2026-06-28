"""MCP server: aiqa-memory — known-issues / flaky-history / failure-patterns /
glossary. Reads from .aiqa-memory/*.json; writes require AIQA_ALLOW_MEMORY_WRITE=true.
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from aiqa_framework.mcp_servers.shared.policy import allow_memory_write
from aiqa_framework.mcp_servers.shared.result import cap, read_json

mcp = FastMCP("aiqa-memory")
_MEM = Path(".aiqa-memory")
_STORES = ("known-issues", "flaky-history", "failure-patterns", "glossary")


def _path(store: str) -> Path:
    return _MEM / f"{store}.json"


@mcp.tool()
def get_known_issues() -> list:
    return cap(read_json(str(_path("known-issues")), []))


@mcp.tool()
def get_flaky_history() -> list:
    return cap(read_json(str(_path("flaky-history")), []))


@mcp.tool()
def get_failure_patterns() -> list:
    return cap(read_json(str(_path("failure-patterns")), []))


@mcp.tool()
def get_glossary() -> dict:
    return cap(read_json(str(_path("glossary")), {}))


@mcp.tool()
def add_entry(store: str, entry: dict) -> dict:
    """Append an entry to a memory store (write-gated)."""
    if store not in _STORES:
        return {"ok": False, "error": f"unknown store; choose {list(_STORES)}"}
    if not allow_memory_write():
        return {"ok": False, "error": "writes disabled — set AIQA_ALLOW_MEMORY_WRITE=true"}
    _MEM.mkdir(parents=True, exist_ok=True)
    data = read_json(str(_path(store)), [])
    data.append(entry)
    _path(store).write_text(json.dumps(data, indent=2))
    return {"ok": True, "count": len(data)}


if __name__ == "__main__":
    mcp.run()

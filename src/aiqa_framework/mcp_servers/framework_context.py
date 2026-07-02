"""MCP server: aiqa-framework-context — code conventions + existing-code index
(read-only). Call BEFORE generating code so the LLM reuses what exists.

Tools: get_conventions, get_existing_code_index, find_page_object,
list_action_keywords, search_tests, read_snippet.
"""

from __future__ import annotations

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from aiqa_framework.mcp_servers.shared.policy import READ_LINE_CAP, is_blocked
from aiqa_framework.mcp_servers.shared.result import cap

mcp = FastMCP("aiqa-framework-context")
_SRC = Path("src/aiqa_framework")


@mcp.tool()
def get_conventions() -> str:
    """The framework conventions the qa-agent must follow."""
    for candidate in (
        Path(".claude/skills/qa-agent/references/framework-conventions.md"),
        Path("CLAUDE.md"),
    ):
        if candidate.exists():
            return candidate.read_text()[:80_000]
    return "(no conventions doc found)"


@mcp.tool()
def get_existing_code_index() -> dict:
    """UI pages, API services/queries, mobile screens, and specs that already exist."""

    def _names(rel: str) -> list[str]:
        return [p.name for p in (_SRC / rel).glob("*.py") if p.name != "__init__.py"]

    return cap(
        {
            "ui_pages": _names("modules/ui/pages"),
            "api_rest_services": _names("modules/api/rest/services"),
            "api_graphql_queries": _names("modules/api/graphql/queries"),
            "mobile_screens": _names("modules/mobile/screens"),
            "specs": [str(p) for p in Path("tests").rglob("test_*.py")],
        }
    )


@mcp.tool()
def find_page_object(name: str) -> list:
    """Find Page Object files matching a name fragment."""
    return [str(p) for p in _SRC.glob("modules/ui/pages/*.py") if name.lower() in p.name.lower()]


@mcp.tool()
def list_action_keywords() -> list:
    """Public methods on ActionKeyword (the single UI keyword layer)."""
    src = (_SRC / "modules/ui/action_keyword.py").read_text()
    return sorted(
        set(re.findall(r"^\s{4}def\s+([a-z][a-z0-9_]*)\s*\(", src, re.MULTILINE)) - {"__init__"}
    )


@mcp.tool()
def search_tests(query: str) -> list:
    """Find spec files whose contents mention the query."""
    hits = []
    for p in Path("tests").rglob("test_*.py"):
        if query.lower() in p.read_text().lower():
            hits.append(str(p))
    return cap(hits)


@mcp.tool()
def read_snippet(path: str, start: int = 1, count: int = READ_LINE_CAP) -> str:
    """Read up to 120 lines of a non-secret source file."""
    if is_blocked(path):
        return "(blocked path)"
    p = Path(path)
    if not p.exists():
        return "(not found)"
    lines = p.read_text().splitlines()
    end = min(len(lines), start - 1 + min(count, READ_LINE_CAP))
    return "\n".join(lines[start - 1 : end])


if __name__ == "__main__":
    mcp.run()

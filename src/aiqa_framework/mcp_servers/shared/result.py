"""Result helpers — keep MCP payloads compact (port of mcp/shared/result.ts)."""

from __future__ import annotations

import json
from typing import Any

from aiqa_framework.mcp_servers.shared.policy import RESULT_BYTE_CAP


def read_json(path: str, default: Any) -> Any:
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def cap(value: Any) -> Any:
    """Truncate oversized payloads so a tool result stays within the byte cap."""
    s = json.dumps(value, default=str)
    if len(s) <= RESULT_BYTE_CAP:
        return value
    return {"truncated": True, "preview": s[:RESULT_BYTE_CAP]}

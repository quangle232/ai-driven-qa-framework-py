"""Agent mode policy + hard guardrails (port of config/agent-policy.ts)."""

from __future__ import annotations

import os

MODES = (
    "observe_only",
    "diagnose_only",  # default
    "suggest_fix",
    "generate_patch",
    "apply_patch_requires_approval",
    "full_cycle_with_approval",
)
DEFAULT_MODE = "diagnose_only"

#: Absolute — no mode override can unblock these.
FORBIDDEN = (
    "self-heal a test until it passes in CI",
    "auto-skip tests",
    "auto-mark failed tests as passed",
    "weaken or delete assertions",
    "update expected results without spec / human approval",
    "read secrets, .env, .auth/, or storage state",
    "commit or push changes",
    "create Jira / GitLab / GitHub bugs without approval",
    "run unrestricted shell commands",
)


def active_mode(env: dict[str, str] | None = None) -> str:
    env = env if env is not None else dict(os.environ)
    mode = env.get("AI_QA_AGENT_MODE", DEFAULT_MODE).strip().lower()
    return mode if mode in MODES else DEFAULT_MODE

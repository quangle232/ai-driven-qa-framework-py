---
name: mcp-setup
description: Configure the external MCP servers the QA workflow uses — Jira/Atlassian (story fetch + sync), Figma (design), Playwright (live DOM), and TestRail (test management) — in the Claude Code / Codex MCP config, with guided credentials. Use when an MCP is unreachable, or before running the story workflow.
---

# mcp-setup — connect the workflow MCPs

Follow `.claude/skills/qa-agent/references/mcp-usage.md` ("Setting up the Jira MCP" /
"Setting up the TestRail MCP") and `fallbacks.md`.

## Steps
1. **Detect** what's reachable — try one tool from each MCP.
2. For each missing one, show the `.mcp.json` entry and, with the user's OK, write it.
   Confirm the site URL + auth; never invent credentials. Keep tokens out of git
   (env / credential store; `environments/.env.testrail` is gitignored).
3. **Reload** — MCP servers load at session start, so a new session / re-invoke picks
   them up.
4. **Retry** the tool and confirm it's reachable.

## Coverage
- **Jira / Atlassian** — official remote MCP (browser OAuth) or `mcp-atlassian` (API
  token). Needed for story fetch, review sync, Xray Test/Test-Execution, Excel attach.
- **Figma** — design context (optional).
- **Playwright** — live DOM exploration + run confirmation.
- **TestRail** — only for the TestRail publish target (needs the MCP + TestRail creds).

The framework's own read-only servers are separate: `uv run aiqa mcp-list` / `mcp-config`.

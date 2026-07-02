# MCP Usage, Setup & Fallback Rules

MCP servers used by the workflow:
- **Jira (Atlassian)** — fetch the story, sync review, create Test/Test Execution
  (Xray), attach the Excel. Required for the Jira-driven path.
- **Figma** — design context (optional).
- **Playwright** — live DOM exploration + run confirmation (optional).
- **TestRail** — only when the client chose the TestRail target.
- **The framework's 4 read-only servers** — `uv run aiqa mcp-list`.

For Jira and TestRail, an unreachable MCP triggers the **guided setup** in
`fallbacks.md` (warn → configure → reload → retry) before any silent degrade.

---

## Setting up the Jira MCP
MCP servers are configured in the Claude Code MCP config — project `.mcp.json`
(committed) or via `claude mcp add`. Confirm the site + auth with the user; never
invent credentials. Two common options:

**A. Atlassian official remote MCP (OAuth in the browser):**
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"]
    }
  }
}
```

**B. Community `mcp-atlassian` (API token):** set the user's values and keep the
token out of git (use env / a credential store):
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://<your-site>.atlassian.net",
        "JIRA_USERNAME": "<email>",
        "JIRA_API_TOKEN": "<token>"
      }
    }
  }
}
```
After writing it (with the user's OK), the user approves the server and reloads
(new session), then re-invoke the skill so STEP 1 re-fetches and confirms the user
story is reachable.

## Setting up the TestRail MCP
Only for the TestRail target. Needs a TestRail MCP entry plus TestRail credentials
in `environments/.env.testrail` (gitignored):
```
TESTRAIL_URL=https://<your-site>.testrail.io
TESTRAIL_USER=<email>
TESTRAIL_API_KEY=<api-key>
```
Add the chosen TestRail MCP to `.mcp.json` (same shape as above, with the server's
documented command/env), confirm with the user, reload, and retry the publish. If
unavailable, fall back to the Excel target (`fallbacks.md`).

---

## Jira MCP — when reachable (STEP 0–3, 9, 13, 16)
- Fetch the story by `user_story_key`; extract title, description, AC, **labels**,
  **status**, Figma link (STEP 1).
- Create `Create Test Case` / `Execute Testing` items, sync review + results, attach
  the Excel to the parent story; for the Xray target create `Test` / `Test
  Execution` issues (see `jira-sync.md`, `test-management.md`).
- Unreachable → guided setup above, then note context (`fallbacks.md`).

## Figma MCP — STEP 4
Only when the story has a Figma link. Extract sections, elements, labels, states.
Fallback: skip UI extraction; suggest `data-test-id`; do not fabricate selectors.

## Playwright MCP — STEP 4 (explore) + STEP 15 (run)
Tools (prefix `mcp__playwright__`): `browser_navigate`, `browser_snapshot`,
`browser_click`, `browser_type`, `browser_fill_form`, `browser_evaluate`,
`browser_console_messages`, `browser_network_requests`, `browser_take_screenshot`.
- STEP 4 — read the real DOM for true selectors/routes; prefer
  `data-zcqa → data-test-id → data-id → data-title`; record routes in
  `docs/ai/navigation.md`.
- STEP 15 — drive/confirm generated flows; reuse the saved storage state; never do a
  destructive action without explicit confirmation.
- Fallback: generate from Figma + existing page objects + `navigation.md`; mark
  unverified selectors in "Known gaps"; ask the user to run `uv run pytest -m <marker>`.

---

## The framework's own MCP servers (read-only)
`src/aiqa_framework/mcp_servers/`. `uv run aiqa mcp-list` / `mcp-config` /
`mcp-start <server>`.

| Server | Use |
|--------|-----|
| `framework-context` | **Call BEFORE STEP 14 code-gen** — conventions, the `TAGS` map, existing modules/ui/pages/services/screens, so generated code matches and is not duplicated. |
| `qa-report` | Read the latest `test-output/` run results (STEP 16). |
| `memory` | Read the `docs/ai/` trackers + artifacts (`tracking-files.md`). |
| `test-runner` | Trigger / inspect a pytest run (read-only surface). |

## General rule
Whenever a fallback is taken, log it, continue, and report it so the human reviewer
can decide how to fill the gap.

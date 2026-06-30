# MCP Usage & Fallback Rules

Two groups of MCP servers support the workflow:

1. **External workflow MCPs** — Jira, Figma, Playwright. Each MUST degrade
   gracefully — **never hard-fail** the workflow because one is missing or errors.
   Log what was skipped and surface it in the review (and `docs/ai/memory.md`).
2. **The framework's own 4 read-only MCP servers** — shipped in this repo, listed
   by `uv run aiqa mcp-list`.

See `fallbacks.md` for the canonical fallback behaviour.

---

## Jira MCP — STEP 0–3, 9, 13, 16
- Fetch the story by `user_story_key`; extract title, description, AC, **labels**,
  **status**, Figma link (STEP 1).
- Create the `Create Test Case` / `Execute Testing` subtasks and sync review +
  results (STEP 3 / 9 / 16); attach the Excel to the parent story (STEP 13). See
  `jira-sync.md`.
- **Fallback**: use `docs/ai/` note context, ask the user to paste AC + label,
  continue. Log `Jira: skipped — <reason>`.

## Figma MCP — STEP 4
- Only when the story has a Figma link. Extract sections, elements, labels, states.
- **Fallback**: skip UI extraction; do not fabricate selectors; suggest `data-test-id`.
  Log `Figma: skipped — <reason>`.

## Playwright MCP — STEP 4 (explore) + STEP 15 (run)
Tools (prefix `mcp__playwright__`): `browser_navigate`, `browser_snapshot`,
`browser_click`, `browser_type`, `browser_fill_form`, `browser_evaluate`,
`browser_console_messages`, `browser_network_requests`, `browser_take_screenshot`.
- STEP 4 — navigate the live app, snapshot screens, read the real DOM for true
  selectors / routes; prefer `data-zcqa → data-test-id → data-id → data-title`;
  record routes in `docs/ai/navigation.md`.
- STEP 15 — drive or confirm generated flows. Reuse the saved auth/storage state.
  Never perform a destructive action without explicit human confirmation.
- **Fallback**: generate from Figma + existing page objects + `navigation.md`;
  mark unverified selectors in `docs/ai/memory.md` "Known gaps"; ask the user to run
  `uv run pytest -m <marker>`. Log `Playwright MCP: skipped — <reason>`.

---

## The framework's own MCP servers (read-only)
`src/aiqa_framework/mcp_servers/`, read-only by default. `uv run aiqa mcp-list` /
`mcp-config` / `mcp-start <server>`.

| Server | Use |
|--------|-----|
| `framework-context` | **Call BEFORE STEP 14 code-gen** — conventions, the `TAGS` map, existing pages/services/screens, so generated code matches what exists. |
| `qa-report` | Read the latest `test-output/` run results (STEP 16). |
| `memory` | Read the `docs/ai/` tracking files + artifacts (see `tracking-files.md`). |
| `test-runner` | Trigger / inspect a pytest run (read-only surface). |

---

## General rule
Partial completion is allowed. Whenever a fallback is taken, log it, continue, and
report it so the human reviewer can decide how to fill the gap.

---
name: user-story-test
description: Entry point — given a Jira user story KEY or URL (or pasted acceptance criteria), run the full AIQA qa-agent workflow end to end: fetch/parse → design JSON-first test cases → enrich → review table + human approval ("I approve") → publish to the chosen test management (Excel/Xray/TestRail) → generate Playwright/pytest → run all → HTML report + status update. Use when the user gives a story key/link and wants to "test this story".
---

# user-story-test — run the full QA workflow for a story

A thin entry point over the **qa-agent** skill.

## Steps
1. Parse the input:
   - Jira URL (e.g. `https://<site>.atlassian.net/browse/EAST-123`) → extract `EAST-123`.
   - Bare key (`EAST-123`) → use as-is.
   - Pasted acceptance criteria / note → skip the Jira fetch, start at design.
2. Load and follow the qa-agent skill — `.claude/skills/qa-agent/SKILL.md` and its
   `references/` (`workflow.md` is the 16-step operating instruction). Run it end to end.
3. Hard rules (do not bypass): the **human approval loop** (`I approve`) before any
   publish or code generation; JSON is the source of truth; publish to the client's
   chosen tool; report back with statuses updated.
4. If the Jira MCP is unreachable, run the **guided setup** in
   `.claude/skills/qa-agent/references/fallbacks.md` (warn → configure → retry) — or the
   `mcp-setup` skill — before falling back to note context.

## Notes
- Claude Code hands off to the `qa-agent` skill; Codex / other tools read the qa-agent
  `SKILL.md` + references and execute the workflow.
- Per-module memory lives in `docs/ai/<module>/`.

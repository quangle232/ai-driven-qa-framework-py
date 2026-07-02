---
name: create-test-cases
description: Design and author reviewable test cases from a Jira story key/URL, pasted acceptance criteria, or an issue note — JSON-first, enriched with testing strategy + auto priority + duplicate detection, shown as a review table with human approval, and persisted (optionally published). This is the DESIGN half of the qa-agent workflow, stopping before code generation. Use when you want test cases (manual + automation candidates), not code yet.
---

# create-test-cases — author + review test cases (no code)

Runs the design half of the qa-agent workflow (STEP 0–13) and stops before code-gen.

## Steps (follow the qa-agent references)
1. Input: a story key/URL (Jira MCP) OR pasted AC / note. Parse AC per
   `.claude/skills/qa-agent/references/ac-parsing.md`. (Jira unreachable → `mcp-setup` or
   the guided fallback in `references/fallbacks.md`.)
2. Generate JSON-first cases per `references/json-contract.md`; cover the surfaces and
   dimensions per `references/testing-strategy.md`.
3. Enrich: `python3 .claude/skills/qa-agent/scripts/json_quality_checks.py --json <file>
   --write` — auto priority (`priority-scoring.md`) + duplicate flags
   (`duplicate-detection.md`).
4. Render the review table per `references/review-table-rendering.md`; run the **human
   approval loop** (`EDIT_TABLE` / `CHANGESET` / `I approve`). JSON is the source of truth.
5. Persist the approved JSON to `docs/ai/<module>/testcases/`; update the module
   `test-case.md`.
6. Hand off (optional): `publish-testcases` to export (Excel / Xray / TestRail);
   `automation-generate` to turn the automatable cases into code; or `coverage-gap` first
   to check what's missing.

## Hard rules
- Do NOT generate code or run tests here (use `automation-generate` / `run-tests` /
  `user-story-test`). Human approval before any publish. Never invent AC — record
  assumptions + open questions instead.

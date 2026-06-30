---
name: qa-agent
description: AI-driven QA agent for the Python (Playwright + pytest) AI-Driven QA Framework. Use when given a Jira story key, pasted acceptance criteria, or an issue note to design reviewable JSON-first test cases (testing strategy + auto priority scoring + duplicate detection), run a human approval loop, export approved cases to a Trustify-style Excel attached to the Jira story, then convert the approved cases into Playwright/pytest code (POM + ActionKeyword, Service-Object API, typed gRPC client, Appium/mobile-web), execute all, and report results back to the JSON and Jira. Degrades gracefully when MCPs are missing.
---

# QA Agent — Python framework (design → approve → automate → run → report)

## Role
You are a Senior QA Agent inside the **Python** AI-Driven QA Framework and the
single entry point for the QA workflow. The skill is two halves joined at the
**approved JSON**:
1. **Design half** — analyse the story, author canonical JSON test cases, enrich
   them, review them as a table, get human approval, export Excel, sync Jira.
2. **Automation half** — turn the approved manual cases into Playwright/pytest,
   execute all (new + related), and report results back into the JSON, Jira, and
   `docs/ai/`.

**JSON is always the source of truth.** The table and the generated code are
always regenerated from the JSON.

## How to load this skill
Read and follow these together, in order:

1. `./references/workflow.md` — **the main operating instruction (16 steps)**
2. `./references/ac-parsing.md` — AC extraction contract
3. `./references/testing-strategy.md` — coverage policy
4. `./references/priority-scoring.md` — priority classification (P0/P1/P2)
5. `./references/duplicate-detection.md` — duplicate / redundancy policy
6. `./references/review-table-rendering.md` — preview table + Jira comment contract
7. `./references/json-contract.md` — canonical JSON source-of-truth contract
8. `./references/jira-sync.md` — Jira behaviour (Create Test Case / Execute Testing)
9. `./references/python-export-runner.md` — Excel export usage
10. `./references/fallbacks.md` — mandatory fallback behaviour
11. `./references/framework-conventions.md` — how generated pytest MUST look
12. `./references/test-case-template.md` — JSON → pytest mapping (automation half)
13. `./references/tracking-files.md` — `docs/ai/` note context + artifacts
14. `./references/mcp-usage.md` — Jira / Figma / Playwright + the 4 aiqa servers

Scripts:
- `./scripts/json_quality_checks.py` — enrich JSON with priority + duplicate flags
  (STEP 7) BEFORE presenting / syncing the table.
- `./scripts/export_json_to_trustify_excel.py` — Excel export, AFTER approval only.
- `./scripts/find_related_tests.py` / `./scripts/trigger_jenkins.py` — related-test
  discovery + CI execution in the automation half.

Examples (formatting guidance only): `issue-note-example.md`,
`changeset-example.md`, `sample_testcases.json`, `sample_page_object.py`,
`sample_spec.py`, and the `docs/ai/` trackers.

## Invocation contract
If the user provides a `user_story_key` (e.g. `EAST-123`), run the full workflow
without asking them to restate the steps. If they paste raw AC or an issue note
instead, skip the Jira fetch and use note context. The automation half (STEP
14–16) runs **after** the exact approval phrase `I approve`.

## Execution rule
- Treat `workflow.md` as the main operating instruction (STEP 0–16).
- `ac-parsing.md` = AC contract · `testing-strategy.md` = coverage ·
  `priority-scoring.md` = priority · `duplicate-detection.md` = dedup ·
  `review-table-rendering.md` = table/sync rendering · `json-contract.md` = JSON
  source of truth · `jira-sync.md` = Jira behaviour · `fallbacks.md` = mandatory
  fallbacks.
- Run `json_quality_checks.py` to enrich the JSON before presenting/syncing the table.
- Use the Excel export only after approval.
- For the automation half follow `framework-conventions.md` + `test-case-template.md`;
  validate every generated file with `uv run aiqa guard --files <paths>`.
- Use examples as formatting guidance only.

## Hard rules
- **Approval loop is mandatory.** No Excel export and no code generation before the
  exact phrase `I approve`. Never bypass it.
- **JSON is the source of truth.** All edits update JSON first; table + code are
  regenerated from it.
- **One primary review table** — no derived / summary / analytics /
  priority-distribution / automation-candidate tables in the conversation or in any
  synced content.
- **Excel attaches to the parent Jira user story only** — never to `Create Test
  Case` or `Execute Testing`.
- **Persist JSON + Excel to `docs/ai/`** whenever generated, even if Jira is up.
- **Never hard-fail** on Jira / Figma / Playwright / MCP errors — fall back and
  continue (`fallbacks.md`).
- **Respect the patch guard** in the automation half (`uv run aiqa guard`); never
  write a patch-guarded path (`config/`, `pyproject.toml`, `conftest.py`, etc.) —
  surface it to the user.
- **`marker == Jira label`** (kebab→snake); JSON `priority` `P0/P1/P2` → marker
  `p0/p1/p2`.
- All comments in English; update `docs/ai/` after every enrichment, edit, and run.

## Conflict order
1. explicit user instruction
2. `workflow.md`
3. `framework-conventions.md` (automation half)
4. `ac-parsing.md`
5. `testing-strategy.md`
6. `priority-scoring.md`
7. `duplicate-detection.md`
8. `review-table-rendering.md`
9. `json-contract.md`
10. `test-case-template.md`
11. `jira-sync.md`
12. `tracking-files.md`
13. `mcp-usage.md`
14. `fallbacks.md`

## Reducing permission prompts
This skill writes/edits files and runs `uv` / `pytest` / `python3`. The user can
pre-approve patterns ONCE in `.claude/settings.local.json` (project-local, not
committed): `Write`, `Edit`, `Bash(uv:*)`, `Bash(uv run:*)`, `Bash(python3:*)`,
`Bash(python:*)`, `Bash(curl:*)`, `Bash(grep:*)`, `Bash(find:*)`,
`Bash(git status*)`, `Bash(git log*)`, `Bash(git diff*)`. The qa-agent never
auto-edits `settings.local.json` — the user controls their own permissions.

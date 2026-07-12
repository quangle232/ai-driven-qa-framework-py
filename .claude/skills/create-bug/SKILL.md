---
name: create-bug
description: File a well-formed Jira bug from a failed test, a bug DRAFT, or a described defect — gather reproduction context (failing test, error, expected vs actual, env, links/screenshots), dedupe against known issues, link it to the parent story, and create (or preview) it via the Jira MCP. Failures write approval-gated drafts to test-output/ai/bug-drafts/ by default — this skill is the approval path that turns a reviewed draft into a real Jira bug.
---

# create-bug — file a Jira bug

The FINAL failed attempt of a `@jira`-tagged spec writes an **approval-gated DRAFT**
to `test-output/ai/bug-drafts/` (JSON for the agent + self-contained HTML with the
repro command and embedded screenshots — see `index.html` there; root `conftest.py`
gate, `JIRA_AUTO_BUG=yes` is the explicit opt-in for direct auto-filing via
`shared/reporting/bug_reporter.py`). Use THIS skill to (a) **file an approved
draft** — read the draft JSON and create the bug via the Jira MCP — or (b) file a
**manual / triaged** bug: a defect found during exploration, or a better-crafted
report.

## Gather context
- From a failure: the failing test `nodeid`, the error / traceback (from `test-output/`
  or `read-report`), the parent story (the spec's `@jira("KEY")`), and any
  screenshot / log / artifact.
- From a description: title, steps to reproduce, expected vs actual, environment
  (`test_env`), severity / priority.

## Dedupe first
Check the `memory` MCP `known-issues` (and existing bugs on the story). Do NOT file a
duplicate — if it matches a known issue, link / comment instead.

## Create (or preview)
Via the Jira MCP: create a `Bug` linked to the parent story with a clear summary
(`[QA]` prefix), reproduction steps, expected vs actual, environment, and attachments
(see `references/jira-sync.md`). If the Jira MCP is unavailable → run `mcp-setup`, or
output the full bug draft for the user to paste and record it in
`docs/ai/<module>/memory.md` "Known gaps".

## Hard rules
- Filing a real bug is an outward action — confirm with the user first. Never invent
  reproduction steps; include only what the failure / description supports.

---
name: create-bug
description: File a well-formed Jira bug from a failed test or a described defect — gather reproduction context (failing test, error, expected vs actual, env, links/screenshots), dedupe against known issues, link it to the parent story, and create (or preview) it via the Jira MCP. Use for manual/triaged defects; the framework already auto-files a bug on a spec's final failed attempt.
---

# create-bug — file a Jira bug

The framework auto-files a bug on the FINAL failed attempt of a `@jira`-tagged spec
(`src/aiqa_framework/shared/reporting/bug_reporter.py`). Use THIS skill for a **manual /
triaged** bug: a defect found during exploration, or a better-crafted report.

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

---
name: qa-status
description: Report overall QA health at a glance — latest run results (pass/fail/flaky), a coverage snapshot, open/known issues, pending review cases, and per-module memory — pulled from test-output/, docs/ai/<module>/, and the memory MCP. Use for "how's QA doing?" or a status update (distinct from read-report's per-run deep dive).
---

# qa-status — QA health snapshot (read-only)

Aggregate a concise status across the project:
- **Last run** — `test-output/pytest-report.json` / `test-output/ai/`: totals, pass rate,
  failing clusters, flaky (run `read-report` first if stale).
- **Coverage** — per-module `docs/ai/<module>/test-case.md` counts (manual vs automation,
  by status); call `coverage-gap` for uncovered AC when a story/feature is given.
- **Known issues + flaky** — the `memory` MCP (`known-issues`, `flaky-history`) /
  `.aiqa-memory/`.
- **Pending** — approved-but-unpublished or draft cases in `docs/ai/<module>/testcases/`.
- **Surfaces** — modules that exist + their markers (`framework-context` MCP /
  `uv run aiqa scan`).

## Output
A one-page summary per surface: run health · coverage · flaky count · open issues ·
pending — plus the top "next actions" and which skill to run next (`read-report` /
`coverage-gap` / `flaky-triage` / `create-bug` / `publish-testcases`). Read-only.

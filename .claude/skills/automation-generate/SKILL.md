---
name: automation-generate
description: Generate automation code (UI, API — REST/gRPC/GraphQL, or performance) from test cases following AIQA conventions. Accepts either detailed step-by-step cases, or summary cases — for summaries the agent explores the app/API step by step (Playwright MCP / live calls) to understand real selectors and flows BEFORE generating. Reuses existing code (never duplicates), validates with the patch guard, and runs the result.
---

# automation-generate — test cases → automation code

## Input modes
1. **Detailed steps** — cases already have explicit steps + data + target element →
   map straight to code.
2. **Summary only** — cases lack detail → **explore first**: use the `explore-app`
   skill / Playwright MCP for UI (navigate, snapshot, read real selectors), or probe
   the REST/gRPC/GraphQL endpoints, to learn the true flow, THEN generate. Never invent
   selectors — if none exist, recommend adding `data-test-id` and note the gap.

## Anti-duplication gate (do this FIRST)
Query the `framework-context` MCP (or `uv run aiqa scan`) and
`.claude/skills/qa-agent/scripts/find_related_tests.py <marker>`. Reuse or extend an
existing page / service / screen / spec instead of regenerating a near-duplicate.

## Generate (per surface)
Follow `.claude/skills/qa-agent/references/test-case-template.md` (JSON→pytest map),
`framework-conventions.md`, and the surface's `conventions.md`:
- **UI** → Page Object in `modules/ui/pages/` + spec in `tests/ui/`.
- **API** → REST service (`modules/api/rest/services`) / gRPC (`modules/api/grpc/client`)
  / GraphQL (`modules/api/graphql/client`) + spec in `tests/api/{rest,grpc,graphql}/`.
- **Performance** → Locust scenario (`modules/performance/locust/`) and/or a JMeter
  plan; assert SLOs with `modules.performance.helpers.assert_thresholds`; spec in
  `tests/performance/` (skip-gated by `ALLOW_PERF`).
- Decorate `@tags(...)` + `@jira("KEY")`; keep test data in `modules/<surface>/testdata/`.

## Validate + run
- `uv run aiqa guard --files <generated>` must pass. A missing feature marker needs
  `shared/config/tags.py` + `pyproject.toml` (both patch-guarded) → ask the user; reuse
  the closest marker meanwhile.
- Run: `uv run pytest -m "<marker>"` (perf: `ALLOW_PERF=1 ...`), then hand off to
  `read-report`.
- Update `docs/ai/<module>/` (memory + test-case + navigation).

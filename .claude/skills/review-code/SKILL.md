---
name: review-code
description: Strict code review against the AIQA framework conventions. Reviews a diff, PR, or named files (works with Claude or Codex) and enforces POM + the single keyword layer, markers + @jira, pydantic/gRPC/perf assertions, reuse-not-duplicate, test-data placement, and the patch guard — plus ruff + mypy gates. Use before merging framework test code.
---

# review-code — convention-strict review

Review the target and BLOCK anything that violates the framework conventions. Load the
conventions first; never review from memory.

## Load
- `.claude/skills/qa-agent/references/framework-conventions.md` (index) + the per-module
  `src/aiqa_framework/modules/<surface>/conventions.md` for each changed surface, and
  `src/aiqa_framework/shared/conventions.md`.

## Scope
Default = staged diff (`git diff --staged`); otherwise the files / PR the user names.

## Deterministic gates (run + report)
- `uv run aiqa guard --files <changed .py>` — patch guard (blocked paths, hardcoded
  secrets, `time.sleep`, `pytest.mark.skip`, raw `playwright.sync_api` import in a spec).
  The one allowed guarded file is `shared/config/tags.py` — and ONLY additive `TAGS`
  entries; flag anything else in it.
- `uv run poe lint` (ruff) and `uv run poe typecheck` (mypy).

## Convention checklist (strict)
- A spec calls Page Objects / services / screens — NEVER `page.locator` / `httpx` /
  `grpc` / a driver directly. A Page Object calls `self.keyword.*` only.
- Selectors as class attrs, data-* priority. No hardcoded waits — explicit waits only.
- Every test: `@tags(TAGS.<SURFACE>, TAGS.REGRESSION, TAGS.P0/1/2)` + `@jira("KEY")`
  from `aiqa_framework.shared.config.tags`; marker == Jira label (kebab→snake).
- API: pydantic validation + `expected_status`; gRPC: assert `grpc.StatusCode.*`;
  performance: assert SLOs. Test data in `modules/<surface>/testdata/`, not inline.
- **Reuse, don't duplicate** — a new page/service/screen/spec must not duplicate an
  existing one (check the `framework-context` MCP / `uv run aiqa scan`).
- Correct folder + marker per `references/test-case-template.md`. Comments in English.

## Output
Findings grouped by severity (blocker / major / minor), each with `file:line`, the rule
violated, and the concrete fix. Approve only when all gates pass and there are no
blockers. Report findings; do not silently rewrite the author's code.

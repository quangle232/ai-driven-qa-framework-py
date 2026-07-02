# AIQA — AI-Driven QA Framework (Python) — Claude project guide

Modular QA framework. Each testing **surface** is its own module with its own
conventions, memory, helpers, tests, and optional-dependency extra — installable
and runnable in isolation. Plus a failure → Jira-bug reporter, an AI **qa-agent**
skill, the **`aiqa`** CLI, and **4 MCP servers**.

## First time
1. `uv sync --extra all --extra dev` (or only the surfaces you need, e.g. `--extra api`)
   · `uv run playwright install --with-deps chromium` (ui) · `uv run poe proto-gen` (grpc).
2. `cp environments/.env.test.example environments/.env.test` and fill SUT URL + login.
3. Implement `authenticate()` in `src/aiqa_framework/modules/ui/auth.py` for your sign-in.
4. Replace the `sample` Page Object / spec with your first flow.

## How to run (per surface — isolation)
- UI: `uv run pytest -m regression` (needs `--extra ui`).
- By surface: `uv run poe test-ui | test-api | test-grpc | test-graphql | test-mobile-web | test-mobile-native | test-perf`.
- `test_env=dev|test|prod` selects `environments/.env.<env>` (default test; resolver `shared/config/env.py`).
- Mocks: `uv run poe mock-api` · `uv run poe grpc-mock`. Reports: `uv run aiqa report-all`.
- Quality: `uv run poe lint` (ruff) · `uv run poe typecheck` (mypy).

## Layout
```
src/aiqa_framework/
  shared/      config (env·settings·tags) · reporting (Jira bug) · memory · helpers
  modules/
    ui/          Playwright — action_keyword · base_page · pages/ · auth · mobile_web/ · api_support
    api/         rest/ (httpx Service-Object) · grpc/ (typed client) · graphql/ (httpx)   [no Playwright]
    performance/ locust/ · jmeter/
    mobile/      native Appium — action_keyword · screens/
  agent/       the `aiqa` CLI + collectors / diagnosis / reports
  mcp_servers/ 4 read-only MCP servers
tests/  ui/ (+ ui/mobile_web) · api/{rest,grpc,graphql} · performance/ · mobile/
docs/ai/<module>/  per-module AI memory (memory.md · test-case.md · navigation.md · testcases/)
```
- Never call `page.locator` / `httpx` / `grpc` / a driver in a spec — go through the surface keyword layer.
- Each module has its own `conventions.md` + `README.md` (run-in-isolation block).
- Isolation extras: `ui · api · grpc · graphql · mobile · perf · agent · reporting · all`.

## Conventions
- One keyword layer per surface; Service-Object for REST; typed client for gRPC; httpx for GraphQL.
- `@tags(TAGS.<SURFACE>, TAGS.REGRESSION, TAGS.P1)` + `@jira("KEY")` from `aiqa_framework.shared.config.tags`.
- `@bugs` = expected-fail (green slice `-m "not bugs"`); `mobile_native` + `performance` are skip-gated.
- Validate API with pydantic; assert gRPC status codes; assert perf SLOs. Comments in English.
- Don't create accounts or type passwords; the user does those.

## AI QA Agent (`aiqa`) + qa-agent skill
Deterministic pipeline (no LLM): `aiqa collect → diagnose → finalize → report-html`
reads `test-output/pytest-report.json`, writes `test-output/ai/`. LLM diagnosis turns
on when `AI_PROVIDER` has an API key (claude/openai; else noop). MCP: `aiqa mcp-list`
/ `mcp-config` / `mcp-start <server>` (read-only). The `qa-agent` skill designs
JSON-first test cases → review/approve → Excel/Xray/TestRail → generates pytest →
runs → reports; per-module memory in `docs/ai/<module>/`.

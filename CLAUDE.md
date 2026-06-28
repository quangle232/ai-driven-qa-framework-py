# AI-Driven QA Framework (Python) — Claude project guide

Playwright + **pytest** QA framework: POM + a single `ActionKeyword` layer across
**UI · API · gRPC · mobile**, a failure → Jira-bug reporter, an AI **qa-agent**
skill, the **`aiqa`** AI-QA agent CLI, and **4 MCP servers**. Python port of the
TS framework — idiomatic (pytest fixtures/markers, pydantic, uv).

## First time
1. `uv sync --extra dev` · `uv run playwright install --with-deps chromium` · `uv run poe proto-gen`.
2. `cp environments/.env.test.example environments/.env.test` and fill SUT URL + login.
3. Implement `authenticate()` in `src/aiqa_framework/core/auth.py` for your sign-in.
4. Replace the `sample` Page Object / spec with your first flow.

## How to run
- `uv run pytest -m regression` · by surface: `uv run poe test-api | test-grpc | test-mobile-web | test-mobile-native`.
- `test_env=dev|test|prod` selects `environments/.env.<env>` (default test; resolver `config/env.py`).
- Mocks: `uv run poe mock-api` · `uv run poe grpc-mock`. Reports: `uv run aiqa report-all`.
- Quality: `uv run poe lint` (ruff) · `uv run poe typecheck` (mypy).

## Layout
- Specs: `tests/{ui,api,grpc,mobile,mobile_web}` · Page Objects: `src/aiqa_framework/pages/`
- Single keyword layer: `core/action_keyword.py` — never call `page.locator`/`httpx`/`grpc` in a spec
- API: `api/` (Service-Object Model + pydantic + respx/FastAPI mocks) · gRPC: `grpc/` (proto + client + mock)
- Mobile: `mobile/` (Appium native + Playwright mobile-web) · Jira: `jira/bug_reporter.py`
- Tags/markers: `config/tags.py` (`TAGS`, `tags()`, `jira()`) · Settings: `config/settings.py`
- AI-QA agent: `ai_qa_agent/` (`aiqa` CLI) · MCP servers: `mcp_servers/`
- CI samples: `ci/{github-actions,gitlab,jenkins}`

## Conventions
- POM + the single `ActionKeyword`; Service-Object Model for API; typed client for gRPC.
- `@tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)` + `@jira("KEY")` on each test.
- `@bugs` tests assert currently-broken behaviour (expected to fail); green slice `-m "not bugs"`.
- Validate API responses with pydantic; assert gRPC status codes. Comments in English.
- Don't create accounts or type passwords; the user does those.

## AI QA Agent (`aiqa`)
Deterministic Phase-1 pipeline (no LLM): `aiqa collect → diagnose → finalize →
report-html` reads `test-output/pytest-report.json`, writes `test-output/ai/`.
LLM diagnosis turns on when `AI_PROVIDER` has an API key (claude/openai; else noop).
MCP: `aiqa mcp-list` / `mcp-config` / `mcp-start <server>` (read-only by default).

# AI-Driven QA Framework — Python

A reusable QA framework: **Playwright + pytest**, Page Object Model + a single
`ActionKeyword` layer, **API / gRPC / mobile** testing, a failure → Jira-bug
auto-reporter, an **AI QA Agent** (collect → diagnose → report), and **4 MCP
servers** — all on one pytest runner. Python port of the TypeScript framework.

> Sample-driven starter. Search for `sample` to find placeholders to replace.

## Stack

`uv` · `pytest` (+ `pytest-xdist`, `pytest-rerunfailures`, `pytest-playwright`) ·
`httpx` + `pydantic` + `respx` + `FastAPI` (API & mocks) · `grpcio` +
`grpcio-tools` + `pytest-grpc` (gRPC) · `Appium-Python-Client` (native mobile) ·
`pydantic-settings` + `python-dotenv` · `allure-pytest` + `pytest-json-report` +
`Jinja2` + `python-docx` (reporting) · `anthropic` / `openai` (LLM) · `typer`
(`aiqa` CLI) · `mcp` / FastMCP (servers) · `ruff` + `mypy` + `poethepoet`.

## Setup

```bash
uv sync --extra dev
uv run playwright install --with-deps chromium
uv run poe proto-gen                       # generate gRPC stubs
cp environments/.env.test.example environments/.env.test   # fill in SUT URL + login
```

## Run

```bash
uv run poe test-api            # REST API specs (httpx) — mock-backed, no backend
uv run poe test-grpc           # gRPC specs — in-process mock, all RPC types
uv run poe test-mobile-web     # Playwright device emulation (needs the SUT)
uv run poe test-mobile-native  # Appium native — needs a device + ALLOW_MOBILE_NATIVE=1
uv run pytest -m regression    # everything tagged @regression
uv run aiqa report-all         # collect → diagnose → finalize → stakeholder HTML
```

`test_env` selects the env file: `test_env=prod uv run pytest …` → `.env.prod`
(default `test`; valid `dev|test|prod` — resolver in `src/aiqa_framework/config/env.py`).

## Layout

```
src/aiqa_framework/
  config/    env resolver · pydantic settings · tag markers
  core/      action_keyword.py (single keyword layer) · base_page.py · auth.py
  pages/     Page Objects (sample_page.py)
  api/       client.py (httpx) · models.py (pydantic) · services/ · mock/ (respx + FastAPI) · contracts/
  grpc/      proto/ · generated/ (poe proto-gen) · client.py · mock_server.py
  mobile/    capabilities.py · driver_factory.py · action_keyword.py · screens/
  jira/      bug_reporter.py (failure → Bug)
  ai_qa_agent/  schemas · collectors · watchers · analyzers · agents · reports · providers · cli.py (`aiqa`)
  mcp_servers/  qa_report · framework_context · memory · test_runner (FastMCP)
tests/  ui/ · api/ · grpc/ · mobile/ · mobile_web/
ci/     github-actions/ · gitlab/ · jenkins/
```

## Conventions

- POM + the single `ActionKeyword`; API uses the Service-Object Model; gRPC uses
  a typed client — **never call the transport directly in a spec**.
- Tags are pytest markers via `@tags(...)`; `@jira("KEY")` links the parent story.
- `@bugs` = currently-broken (expected to fail); green slice `-m "not bugs"`.
- Native-mobile specs are skip-gated (`ALLOW_MOBILE_NATIVE=1`).
- Validate API responses with pydantic; assert gRPC **status codes**, not just payloads.

See `INSTALL.md`, `CLAUDE.md`, and the per-area docstrings. MIT licensed.

# AI-Driven QA Framework — Python

A reusable, **modular** QA framework — each surface is its own installable module:
**UI** (Playwright), **API** (REST / gRPC / GraphQL), **Performance** (Locust /
JMeter), **Mobile** (Appium). Plus a failure → Jira-bug auto-reporter, an **AI QA
Agent** (collect → diagnose → report), **21 reusable agent skills**, and **4 MCP
servers** — all on one pytest runner. Works with **Claude Code and Codex**. Python
port of the TypeScript framework.

> Sample-driven starter. Search for `sample` to find placeholders to replace.

## Stack

`uv` · `pytest` (+ `pytest-xdist`, `pytest-rerunfailures`, `pytest-playwright`) ·
`httpx` + `pydantic` + `respx` + `FastAPI` (API & mocks) · `grpcio` +
`grpcio-tools` + `pytest-grpc` (gRPC) · `Appium-Python-Client` (native mobile) ·
`locust` (performance) ·
`pydantic-settings` + `python-dotenv` · `allure-pytest` + `pytest-json-report` +
`Jinja2` + `python-docx` (reporting) · `anthropic` / `openai` (LLM) · `typer`
(`aiqa` CLI) · `mcp` / FastMCP (servers) · `ruff` + `mypy` + `poethepoet`.

## Setup

```bash
uv sync --extra all --extra dev
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
(default `test`; valid `dev|test|prod` — resolver in `src/aiqa_framework/shared/config/env.py`).

## Layout

```
src/aiqa_framework/
  shared/      config (env · settings · tags) · reporting (Jira bug) · memory · helpers
  modules/
    ui/          Playwright — action_keyword · base_page · pages/ · auth · mobile_web/ · api_support
    api/         rest/ (httpx SOM · models · services · mock · contracts) · grpc/ · graphql/
    performance/ locust/ · jmeter/
    mobile/      native Appium — action_keyword · capabilities · driver_factory · screens/
  agent/       schemas · collectors · watchers · analyzers · agents · reports · providers · cli.py (`aiqa`)
  mcp_servers/  qa_report · framework_context · memory · test_runner (FastMCP)
tests/  ui/ (+ ui/mobile_web) · api/{rest,grpc,graphql} · performance/ · mobile/
docs/ai/<module>/  per-module AI memory     ci/  github-actions · gitlab · jenkins
```

Each surface is isolable via an extra: `uv sync --extra <ui|api|grpc|graphql|mobile|perf>`
then `uv run pytest -m <marker>` (or the module's README run-in-isolation block).

## AI skills (agents)

21 reusable skills drive the framework. **Claude Code** auto-discovers them
(`.claude/skills/<name>/`); **Codex / Cursor / Gemini** read `.agents/skills/<name>/`
(see `AGENTS.md`). Just ask the agent — e.g. "test EAST-123", "review this diff",
"run the api tests".

- **Onboard & framework** — `setup` (deps / env / doctor) · `mcp-setup` (connect Jira /
  Figma / Playwright / TestRail) · `new-module` (scaffold a surface/artifact) ·
  `ci-setup` (CI pipelines) · `update-conventions` (evolve rules + markers).
- **Design & plan** — `user-story-test` (story → full run) · `qa-agent` (the full
  engine) · `create-test-cases` (author + review, no code) · `coverage-gap` (what's not
  tested).
- **Build automation** — `explore-app` (discover selectors/routes) ·
  `automation-generate` (cases → code: ui / api / perf) · `data-factory` (typed test data).
- **Run & analyze** — `run-tests` (by surface / marker) · `contract-test` (Schemathesis
  vs OpenAPI) · `visual-regression` (screenshot baselines) · `read-report` (AI failure
  analysis + Allure) · `qa-status` (QA health snapshot).
- **Ship & maintain** — `publish-testcases` (→ Excel / Xray / TestRail) · `create-bug`
  (→ Jira bug) · `review-code` (strict convention review) · `flaky-triage` (flaky
  detect / quarantine).

Typical flow: `setup` → `mcp-setup` → `create-test-cases` (or `user-story-test`) →
`automation-generate` → `run-tests` → `read-report` → `review-code`. Full catalogue +
per-skill descriptions in `AGENTS.md`.

## Conventions

- POM + the single `ActionKeyword`; API uses the Service-Object Model; gRPC uses
  a typed client — **never call the transport directly in a spec**.
- Tags are pytest markers via `@tags(...)`; `@jira("KEY")` links the parent story.
- `@bugs` = currently-broken (expected to fail); green slice `-m "not bugs"`.
- Native-mobile specs are skip-gated (`ALLOW_MOBILE_NATIVE=1`).
- Validate API responses with pydantic; assert gRPC **status codes**, not just payloads.

See `INSTALL.md`, `CLAUDE.md`, and the per-area docstrings. MIT licensed.

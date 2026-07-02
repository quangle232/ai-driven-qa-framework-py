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

| Skill | Module | Feature | What it does |
|-------|--------|---------|--------------|
| `setup` | Onboard & framework | Onboarding | Install extras/browsers/gRPC stubs, env, `authenticate()`, `aiqa doctor` |
| `mcp-setup` | Onboard & framework | MCP config | Connect Jira / Figma / Playwright / TestRail MCPs (guided `.mcp.json`) |
| `new-module` | Onboard & framework | Scaffolding | Scaffold a new surface module or page/service/screen skeleton by convention |
| `ci-setup` | Onboard & framework | CI | Tailor GitHub / GitLab / Jenkins: extras, markers, matrix, reports |
| `update-conventions` | Onboard & framework | Governance | Evolve conventions + register markers; keep the index/docs in sync |
| `user-story-test` | Design & plan | End-to-end | Jira story key/URL/AC → run the full qa-agent workflow |
| `qa-agent` | Design & plan | Engine | The full engine: design → approve → publish → generate → run → report |
| `create-test-cases` | Design & plan | Test design | Story/AC → author + enrich + review + approve cases (no code) |
| `coverage-gap` | Design & plan | Coverage audit | AC vs existing tests → uncovered / missing / redundant + cases to add |
| `explore-app` | Build automation | Exploration · ui | Playwright MCP explores the SUT → selectors/routes → navigation memory |
| `automation-generate` | Build automation | Code-gen · ui/api/perf | Cases (detailed, or summary → explore) → automation code |
| `data-factory` | Build automation | Test data | Typed builders (valid / boundary / invalid) in `testdata/` |
| `run-tests` | Run & analyze | Execution | Run by surface / marker / env (+ reruns), local or Jenkins |
| `contract-test` | Run & analyze | Contract · api | Schemathesis property/contract testing vs the OpenAPI schema |
| `visual-regression` | Run & analyze | Visual · ui | Playwright screenshot baselines + tolerance compare |
| `read-report` | Run & analyze | Reporting | Analyze output, AI failure analysis + fixes, HTML + Allure |
| `qa-status` | Run & analyze | Health | One-page QA health: runs, coverage, flaky, issues, pending |
| `publish-testcases` | Ship & maintain | Publishing | Approved JSON → Excel / Xray / TestRail + attach story + status |
| `create-bug` | Ship & maintain | Bug filing | Failed test / defect → deduped Jira bug linked to the story |
| `review-code` | Ship & maintain | Code review | Strict convention review + guard / lint / type gates |
| `flaky-triage` | Ship & maintain | Flaky mgmt | Detect / confirm / quarantine flaky tests + memory |

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

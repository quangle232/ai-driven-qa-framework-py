# Changelog

## [0.2.0] — 2026-07-13 — Modular architecture, skill library, ship gates

### Added
- **Modular per-surface layout** — `shared/` (config · reporting · memory · helpers)
  + `modules/{ui, api, performance, mobile}` + `agent/`; each surface has its own
  `conventions.md`, `helpers/`, `testdata/`, `README.md` (run-in-isolation), tests
  dir, and `docs/ai/<module>/` AI memory. Isolation via optional extras
  (`ui · api · grpc · graphql · mobile · perf · agent · reporting · all`).
- **GraphQL** sub-surface (`GraphQLClient` + FastAPI mock + sample specs) and
  **Performance** module (Locust scenarios + JMeter plan/runner + SLO helpers,
  skip-gated by `ALLOW_PERF`).
- **22-skill library** (Claude `.claude/skills/` + Codex `.agents/skills/` mirrors,
  catalogued in `AGENTS.md`/`README.md`) — incl. `user-story-test`, `qa-agent`
  (JSON-first design → approval → Excel/Xray/TestRail → code-gen → run → report),
  `gen-auto-test` (manual cases → automation, Excel importer, live exploration),
  `automation-generate`, `review-code`, `read-report`, `coverage-gap`, and more.
- **Test-data lifecycle** — precondition via API, teardown via API with tracked ids;
  shared `cleanup` fixture (`CleanupTracker`) + `api` fixture (`UiApiSupport`).
- **Approval-gated bug drafts** — a final-attempt failure writes JSON + self-contained
  HTML (repro command, embedded screenshots) to `test-output/ai/bug-drafts/`;
  `JIRA_AUTO_BUG=yes` opts into direct auto-filing; `poe bug-drafts-index`.
- **Ship gates** — mandatory coverage matrix + impacted-flow analysis; STRICT
  HEADLESS for generated cases; 5/5 stress gate (`pytest-repeat --count=5`, report
  frozen before stress); ONE results-Excel upload post-execution
  (`attach_file_to_jira.py`); scripts+results review whose approval ships
  **branch + MR** via multi-provider `create_mr.py` (GitLab / GitHub incl.
  Enterprise / Bitbucket Cloud / Azure DevOps / Gitea — auto-detected from
  `origin`, `--dry-run` preview).
- `AGENTS.md` as the canonical dual-tool guide (`CLAUDE.md` → symlink).

### Changed
- Failure → Jira flow now defaults to **drafts + human approval** (was direct
  auto-filing). Patch guard allows exactly ONE guarded file — additive `TAGS`
  entries in `shared/config/tags.py`. Excel export switched to an open,
  tool-agnostic column set; test management is pluggable (Excel / Xray / TestRail).

## [0.1.0] — Python port

Idiomatic Python port (full parity) of the TypeScript AI-Driven QA Framework.

### Added
- **Core UI** — `ActionKeyword` (single Playwright keyword layer, friendly errors,
  self-healing locator priority), `BasePage`, sample Page Object, one-time auth +
  storage-state reuse, `pytest` + `pytest-playwright`.
- **API** — Service-Object Model over `httpx` + `pydantic` validation; two mock
  layers (`respx` in-process + `FastAPI` via httpx ASGI transport) + OpenAPI contract.
- **gRPC** — sample casino proto (all 4 RPC types), `grpcio` typed client
  (deadlines/metadata/status codes), in-process mock server, `grpcio-tools` codegen.
- **Mobile** — `Appium-Python-Client` native (parallel per-worker drivers, skip-gated)
  + Playwright mobile-web device emulation.
- **Env** — `test_env` → `.env.<dev|test|prod>` resolver + pydantic-settings.
- **Jira** — failure → Bug auto-reporter (httpx, search-first dedupe) via a conftest
  hook (final attempt only, with `pytest-rerunfailures`).
- **AI QA Agent** — collectors (pytest-json-report + CI metadata), deterministic
  diagnosis + clustering, critical-pattern detector, patch-guard, provider abstraction
  (anthropic/openai/noop), reports (ci-summary, diagnosis md, stakeholder HTML), and
  the `aiqa` Typer CLI (collect/diagnose/finalize/report-html/doctor/guard/scan/
  mcp-*/…).
- **MCP servers** — 4 FastMCP servers (qa-report, framework-context, memory,
  test-runner), read-only by default with `AIQA_ALLOW_EXEC` / `AIQA_ALLOW_MEMORY_WRITE` gates.
- **CI** — sample GitHub Actions / GitLab / Jenkins pipelines (uv + pytest).
- **Tooling** — `uv`, `ruff`, `mypy`, `poethepoet` tasks, `pyproject.toml`.

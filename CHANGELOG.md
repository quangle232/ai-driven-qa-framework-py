# Changelog

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

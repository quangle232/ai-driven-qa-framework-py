# Shared kernel conventions (index)

`shared/` is cross-cutting only — no surface (UI/API/perf/mobile) logic lives here.

## What's in shared/
- `config/` — `env.py` (`test_env` → `.env.<env>`), `settings.py` (pydantic), `tags.py`
  (`TAGS`, `tags()`, `jira()` markers). The single source of markers for every module.
- `reporting/` — `bug_reporter.py`: failure → Jira bug (called by the root conftest hook).
- `memory/` — `store.py`: resolves `docs/ai/<module>/` per-module AI memory + artifacts.
- `helpers/` — tiny cross-cutting utils (`slugify`, `snake`, `now_iso`).

## Rules
- A module may import from `shared/`; `shared/` never imports from a module.
- Markers: a feature marker name == the Jira label (kebab→snake). Register new
  markers in `pyproject.toml` `[tool.pytest.ini_options]` (patch-guarded — the agent
  asks the user).
- All comments in English.

## Per-module conventions
Each surface documents its own rules — read the one you're working in:
- `modules/ui/conventions.md` — Playwright, POM + ActionKeyword, self-healing locators
- `modules/api/conventions.md` — REST (Service-Object) · gRPC · GraphQL
- `modules/performance/conventions.md` — Locust + JMeter
- `modules/mobile/conventions.md` — native Appium

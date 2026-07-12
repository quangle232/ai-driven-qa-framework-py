# Shared kernel conventions (index)

`shared/` is cross-cutting only — no surface (UI/API/perf/mobile) logic lives here.

## What's in shared/
- `config/` — `env.py` (`test_env` → `.env.<env>`), `settings.py` (pydantic), `tags.py`
  (`TAGS`, `tags()`, `jira()` markers). The single source of markers for every module.
- `reporting/` — `bug_draft_writer.py`: failure → approval-gated bug DRAFT (JSON +
  self-contained HTML in `test-output/ai/bug-drafts/`; the root conftest hook's
  default) · `bug_reporter.py`: direct Jira filing, used for approved drafts and
  the `JIRA_AUTO_BUG=yes` opt-in.
- `memory/` — `store.py`: resolves `docs/ai/<module>/` per-module AI memory + artifacts.
- `helpers/` — tiny cross-cutting utils (`slugify`, `snake`, `now_iso`).

## Rules
- A module may import from `shared/`; `shared/` never imports from a module.
- Markers: a feature marker name == the Jira label (kebab→snake). Register new
  markers in `pyproject.toml` `[tool.pytest.ini_options]` (patch-guarded — the agent
  asks the user).
- **Test data lifecycle**: seed preconditions via the **API** (not the UI); when the UI
  create itself is under test, drive it via the UI but track the id(s); **always tear
  down created data via the API** (`modules/ui/conventions.md`).
- All comments in English.

## Per-module conventions
Each surface documents its own rules — read the one you're working in:
- `modules/ui/conventions.md` — Playwright, POM + ActionKeyword, self-healing locators
- `modules/api/conventions.md` — REST (Service-Object) · gRPC · GraphQL
- `modules/performance/conventions.md` — Locust + JMeter
- `modules/mobile/conventions.md` — native Appium

## Skills
Reusable agent skills (Claude `.claude/skills/`, Codex `.agents/skills/`) drive the
workflow — see the catalogue in `AGENTS.md`. Skills read these conventions and the
per-module `docs/ai/<module>/` memory at runtime, so keep both current
(`update-conventions` skill).

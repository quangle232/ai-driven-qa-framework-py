---
name: new-module
description: Scaffold a NEW testing-surface module (or a new artifact inside one) following the AIQA modular convention — folder + __init__, conventions.md, README, helpers/, testdata/, a tests/ dir, a docs/ai/<module>/ memory, plus the marker + optional-dependency extra to register. Use to extend the framework with a new surface (e.g. desktop, contract) or a new page/service/screen skeleton.
---

# new-module — scaffold a surface module (or artifact)

## A new surface module
Create `src/aiqa_framework/modules/<name>/` mirroring an existing module
(`ui` / `api` / `performance` / `mobile`):
- `__init__.py`, a keyword/client layer, `helpers/`, `testdata/`, `conventions.md`,
  `README.md` (with a run-in-isolation block).
- `tests/<name>/` with a `conftest.py`; a `docs/ai/<name>/` memory (`memory.md` +
  `test-case.md`) seeded from an existing module.
- **Register** (patch-guarded — prepare the diff, ask the user to apply):
  a marker in `src/aiqa_framework/shared/config/tags.py` `TAGS` + `pyproject.toml`
  `[tool.pytest.ini_options] markers`, and an optional-dependency **extra** in
  `pyproject.toml` (lazy-import heavy deps so the module stays isolable).
- Add a per-surface `poe` task and a line in `AGENTS.md` / `README.md` layout and the
  qa-agent `references/framework-conventions.md` index.

## A new artifact inside a surface
A skeleton page / service / screen / scenario per that surface's `conventions.md`
(extends BasePage / wraps the client / etc.) with a matching sample spec — then hand off
to `automation-generate` to fill it from real cases.

## Rules
Follow `src/aiqa_framework/modules/<surface>/conventions.md`; keep the module isolable;
validate new files with `uv run aiqa guard`. Reuse before creating (`coverage-gap` /
the `framework-context` MCP).

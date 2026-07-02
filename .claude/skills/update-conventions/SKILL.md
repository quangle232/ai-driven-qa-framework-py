---
name: update-conventions
description: Safely evolve the framework's conventions and markers — edit shared/per-module conventions.md, register a new pytest marker (config/tags.py + pyproject), and keep the qa-agent framework-conventions index + skill docs in sync. Use when the team adds or changes a rule, a surface convention, or a feature marker.
---

# update-conventions — evolve conventions + markers

## Update a convention
- Cross-cutting → `src/aiqa_framework/shared/conventions.md`.
- Surface-specific → `src/aiqa_framework/modules/<surface>/conventions.md`.
- Keep the index `.claude/skills/qa-agent/references/framework-conventions.md` and any
  affected reference (`test-case-template.md`, etc.) consistent — these are read at
  runtime by `automation-generate` / `review-code`, so no code change is needed for them
  to take effect.

## Register a new marker
- Add `NAME = pytest.mark.<name>` to `src/aiqa_framework/shared/config/tags.py` `TAGS` and
  a `"<name>: ..."` line to `pyproject.toml` `[tool.pytest.ini_options] markers`.
- BOTH paths are **patch-guarded** — the agent cannot write them; prepare the exact diff
  and ask the user to apply it. Then it's usable as `TAGS.NAME`.

## Verify
`uv run poe lint` + `uv run pytest --collect-only` (no unknown-marker warnings). If a
change affects generated-code shape, note it in the relevant `conventions.md`.

## Rules
Conventions are the contract every skill enforces — change them deliberately, keep the
index + per-module docs aligned, comments in English.

# AGENTS.md — AIQA (AI-Driven QA Framework)

Canonical agent + contributor guide. Works with any AI coding tool: **Claude Code**
(also reads `CLAUDE.md`, a symlink to this file, and auto-discovers the skill under
`.claude/skills/`) and **Codex / Cursor / Gemini** (read this `AGENTS.md`). This is
the single source of truth.

AIQA is a modular QA framework: each testing **surface** is a self-contained,
isolable module (its own conventions, memory, helpers, tests, and optional-
dependency extra), plus a failure → Jira-bug reporter, an AI **qa-agent** skill, the
**`aiqa`** CLI, and 4 read-only MCP servers.

## Using this repo with an AI agent
To turn a Jira story, pasted acceptance criteria, or an issue note into tests, load
the **qa-agent skill** and follow it end to end:
- **Claude Code** — auto-discovered as the `qa-agent` skill; or read
  `.claude/skills/qa-agent/SKILL.md`.
- **Codex / other tools** — read `.agents/skills/qa-agent/SKILL.md` (same content)
  and follow `SKILL.md` + its `references/*.md` in order.

The skill's flow: design JSON-first test cases → enrich (testing strategy, auto
priority, duplicate detection) → review table + **human approval** (`I approve`) →
publish to the client's chosen test management (open **Excel** / **Xray** /
**TestRail**) → generate Playwright/pytest from the approved cases (reuse, don't
duplicate) → run all → deliver an HTML report + update statuses. Per-module AI
memory lives in `docs/ai/<module>/`.

## Skills catalogue
Reusable skills live in `.claude/skills/<name>/SKILL.md` (Claude Code auto-discovers
them) and are mirrored at `.agents/skills/<name>/` for Codex / other tools. To use one,
load its `SKILL.md` and follow it.

**Onboard & framework**
| Skill | When to use |
|-------|-------------|
| `setup` | First-time onboarding: extras, browsers, gRPC stubs, env, `authenticate()`, doctor |
| `mcp-setup` | Connect Jira / Figma / Playwright / TestRail MCPs (guided) |
| `new-module` | Scaffold a new surface module (or a page/service/screen skeleton) by convention |
| `ci-setup` | Generate / tailor CI (GitHub / GitLab / Jenkins): extras, markers, matrix, reports |
| `update-conventions` | Evolve conventions + register markers; keep the docs/index in sync |

**Design & plan**
| Skill | When to use |
|-------|-------------|
| `user-story-test` | A Jira story key/URL (or pasted AC) → run the full end-to-end workflow |
| `qa-agent` | The full engine: design → approve → publish → generate → run → report |
| `create-test-cases` | Story/AC → author + review + approve test cases (design only, no code) |
| `coverage-gap` | Audit AC vs existing tests → uncovered / missing / redundant + cases to add |

**Build automation**
| Skill | When to use |
|-------|-------------|
| `explore-app` | Discover real selectors/routes via the Playwright MCP → navigation memory |
| `automation-generate` | Test cases (detailed, or summary→explore) → code (ui / api / perf) |
| `data-factory` | Typed test-data builders (valid / boundary / invalid) in `testdata/` |

**Run & analyze**
| Skill | When to use |
|-------|-------------|
| `run-tests` | Run by surface / marker / env (+ reruns), local or Jenkins |
| `contract-test` | Schemathesis property/contract testing against the OpenAPI schema |
| `visual-regression` | Playwright screenshot baselines + tolerance compare for UI |
| `read-report` | Analyze output, AI failure analysis + fixes, HTML + Allure |
| `qa-status` | One-page QA health: runs, coverage, flaky, issues, pending |

**Ship & maintain**
| Skill | When to use |
|-------|-------------|
| `publish-testcases` | Approved JSON cases → Excel / Xray / TestRail + attach story + status |
| `create-bug` | Failed test / defect → deduped, well-formed Jira bug linked to the story |
| `review-code` | Strict convention review + guard / lint / type gates |
| `flaky-triage` | Detect / confirm / quarantine flaky tests + memory |

Typical flow: `setup` → `mcp-setup` → `create-test-cases` (or `user-story-test` for the
full run) → `automation-generate` → `run-tests` → `read-report` → `review-code`.
Supporting: `coverage-gap` · `explore-app` · `data-factory` · `contract-test` ·
`visual-regression` · `publish-testcases` · `create-bug` · `qa-status` · `flaky-triage`;
`new-module` / `ci-setup` / `update-conventions` extend the framework.

## First time
1. `uv sync --extra all --extra dev` (or only the surfaces you need, e.g. `--extra api`)
   · `uv run playwright install --with-deps chromium` (ui) · `uv run poe proto-gen` (grpc).
2. `cp environments/.env.test.example environments/.env.test` and fill SUT URL + login.
3. Implement `authenticate()` in `src/aiqa_framework/modules/ui/auth.py`.
4. Replace the `sample` Page Object / spec with your first flow.
5. `uv run aiqa doctor` to verify the setup.

## Run (per surface — isolation)
- `uv run poe test-ui | test-api | test-grpc | test-graphql | test-mobile-web | test-mobile-native | test-perf`.
- Or install one surface and run it: `uv sync --extra api` → `uv run pytest -m "api or grpc or graphql"`.
- `test_env=dev|test|prod` selects `environments/.env.<env>` (default test; resolver `shared/config/env.py`).
- Mocks: `uv run poe mock-api` · `uv run poe grpc-mock`. Reports: `uv run aiqa report-all`.
- Quality: `uv run poe lint` (ruff) · `uv run poe typecheck` (mypy).

## Layout
```
src/aiqa_framework/
  shared/      config (env·settings·tags) · reporting (Jira bug) · memory · helpers
  modules/
    ui/          Playwright — action_keyword · base_page · pages/ · auth · mobile_web/ · api_support
    api/         rest/ (httpx Service-Object) · grpc/ (typed client) · graphql/ (httpx)   [no Playwright]
    performance/ locust/ · jmeter/
    mobile/      native Appium — action_keyword · screens/
  agent/       the `aiqa` CLI + collectors / diagnosis / reports
  mcp_servers/ 4 read-only MCP servers
tests/  ui/ (+ ui/mobile_web) · api/{rest,grpc,graphql} · performance/ · mobile/
docs/ai/<module>/  per-module AI memory (memory.md · test-case.md · navigation.md · testcases/)
```
Isolation extras: `ui · api · grpc · graphql · mobile · perf · agent · reporting · all`.

## Conventions
- One keyword layer per surface; a spec calls Page Objects / services / screens, never
  the transport (`page.locator` / `httpx` / `grpc` / driver) directly.
- Markers from `aiqa_framework.shared.config.tags`: `@tags(TAGS.<SURFACE>, TAGS.REGRESSION,
  TAGS.P1)` + `@jira("KEY")`. Marker value == Jira label (kebab→snake).
- **Reuse before regenerate** — call the `framework-context` MCP or `uv run aiqa scan`
  to index existing pages / services / screens / specs.
- Read the per-module `conventions.md` for the surface you touch:
  `src/aiqa_framework/modules/{ui,api,performance,mobile}/conventions.md` and
  `src/aiqa_framework/shared/conventions.md`. `.claude/skills/qa-agent/references/framework-conventions.md`
  is the index.
- `@bugs` = expected-fail (green slice `-m "not bugs"`); `mobile_native` + `performance`
  are skip-gated (`ALLOW_MOBILE_NATIVE` / `ALLOW_PERF`). Comments in English.
- **Test data lifecycle** — seed preconditions via the API, test through the UI, and
  always tear down created data via the API (track ids); a UI-create case creates via the
  UI but still cleans up via the API. See `modules/ui/conventions.md`.
- Respect the patch guard (`uv run aiqa guard --files`). Don't create accounts or type
  passwords; the user does those.

## AI QA Agent CLI (`aiqa`) + MCP
- `aiqa collect → diagnose → finalize → report-html` — deterministic pipeline over
  `test-output/pytest-report.json`; LLM diagnosis when `AI_PROVIDER` has a key (claude/
  openai; else noop). `aiqa scan` indexes existing code; `aiqa doctor` checks setup.
- `aiqa mcp-list / mcp-config / mcp-start <server>` — 4 read-only servers:
  `qa-report` · `framework-context` (call before code-gen) · `memory` · `test-runner`.

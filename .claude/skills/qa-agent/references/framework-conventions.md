# Framework Conventions — AIQA (index)

Generated code MUST match the conventions of the surface it targets. This file is
an index; read the per-module `conventions.md` for the surface you generate into.

## Package layout
```
src/aiqa_framework/
  shared/      config (env · settings · tags) · reporting (Jira bug) · memory · helpers
  modules/
    ui/          Playwright: action_keyword · base_page · pages/ · auth · mobile_web/ · api_support
    api/         rest/ (httpx Service-Object) · grpc/ (typed client) · graphql/ (httpx)   [no Playwright]
    performance/ locust/ · jmeter/                                                        [load testing]
    mobile/      native Appium: action_keyword · screens/
  agent/       the `aiqa` CLI + collectors / diagnosis / reports / providers
  mcp_servers/ 4 read-only MCP servers
tests/  ui/ (+ ui/mobile_web) · api/{rest,grpc,graphql} · performance/ · mobile/
```

## Per-module conventions (read the one you need)
- UI → `src/aiqa_framework/modules/ui/conventions.md`
- API (REST / gRPC / GraphQL) → `src/aiqa_framework/modules/api/conventions.md`
- Performance → `src/aiqa_framework/modules/performance/conventions.md`
- Mobile (native) → `src/aiqa_framework/modules/mobile/conventions.md`
- Shared kernel → `src/aiqa_framework/shared/conventions.md`

## Cross-cutting rules (all surfaces)
- One keyword layer per surface; a spec calls Page Objects / services / screens, never
  the transport (`page.locator` / `httpx` / `grpc` / driver) directly.
- Markers from `aiqa_framework.shared.config.tags` (`TAGS`, `tags`, `jira`); a feature
  marker value == the Jira label (kebab→snake); JSON `priority` `P0/P1/P2` → marker `p0/p1/p2`.
- **Reuse before regenerate** — check existing pages / services / screens / specs first.
- Each surface is **isolable**: `uv sync --extra <ui|api|grpc|graphql|mobile|perf>` then
  `uv run pytest -m <marker>` (see the module's `README.md`).
- Validate API with pydantic; assert gRPC `StatusCode.*`; assert perf SLOs. Native-mobile
  and performance are skip-gated (`ALLOW_MOBILE_NATIVE` / `ALLOW_PERF`).
- Respect the patch guard (`uv run aiqa guard --files`); comments in English; per-module
  AI memory lives in `docs/ai/<module>/`.
- **Test data lifecycle** — seed preconditions via the API, exercise the UI, and always
  tear down created data via the API (track ids). When the create itself is under test,
  create via the UI but still clean up via the API (`modules/ui/conventions.md`).

## Skills (agents)
Reusable skills orchestrate this framework for users — full catalogue in `AGENTS.md`
(mirrored: Claude `.claude/skills/`, Codex `.agents/skills/`). They read these
conventions and the per-module `docs/ai/<module>/` memory at runtime.

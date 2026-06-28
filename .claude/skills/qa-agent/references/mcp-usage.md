# MCP Usage & Fallback Rules

Two groups of MCP servers support the workflow:

1. **External workflow MCPs** — Jira, Figma, Playwright (drive the live story,
   design and app). Each MUST degrade gracefully — **never hard-fail the
   workflow** because one is missing or errors. Always log what was skipped and
   surface it in the Phase 4 review.
2. **The framework's own 4 read-only MCP servers** — shipped in this repo,
   listed by `uv run aiqa mcp-list`.

---

## Jira MCP — requirements (Phase 1)
- Use the Jira MCP tools available in the session to fetch the issue by
  `user_story_key`.
- Extract: `title`, `description`, acceptance criteria, **labels**, **status**,
  and any attachment / link (e.g. a Figma URL).
- The Jira label(s) become the feature marker value(s) — `marker == label`
  (kebab→snake: `service-request` → `service_request`).

**Fallback** — Jira MCP missing / errors / issue not found / permission denied:
- Tell the user, then ask them to paste the acceptance criteria (and the
  intended label), or continue with whatever they have already provided.
- Log `Jira: skipped — <reason>` in `docs/ai/memory.md` "Known gaps".

## Figma MCP — design / elements (Phase 1)
- Only when the Jira description contains a Figma link.
- Use the Figma MCP to extract sections, element labels, states and any
  declared component names or selectors.

**Fallback** — Figma MCP missing / link absent / access fails:
- Skip UI extraction. Do NOT fabricate UI structure or selectors.
- Recommend adding `data-test-id` to the relevant elements.
- Log `Figma: skipped — <reason>`.

## Playwright MCP — live exploration + run (Phases 5–6)
Tools (prefix `mcp__playwright__`): `browser_navigate`, `browser_snapshot`,
`browser_click`, `browser_type`, `browser_fill_form`, `browser_evaluate`,
`browser_console_messages`, `browser_network_requests`, `browser_take_screenshot`.

- **Phase 5 — exploration:** navigate the live app, snapshot screens, and read
  the real DOM to discover true selectors, routes and navigation. Prefer
  `data-zcqa → data-test-id → data-id → data-title`. Record new routes in
  `docs/ai/navigation.md`; do not re-explore a screen already mapped there.
- **Phase 6 — run:** drive or confirm the generated flows.
- Reuse the saved auth session (storage state) where possible. Do NOT perform a
  destructive action (delete, irreversible submit) without explicit human
  confirmation.

**Fallback** — Playwright MCP unavailable:
- Generate code from Figma + existing page objects + `navigation.md` only.
- Mark every selector that still needs live verification in
  `docs/ai/memory.md` "Known gaps".
- Ask the user to run the spec locally: `uv run pytest -m <marker>`.
- Log `Playwright MCP: skipped — <reason>`.

---

## The framework's own MCP servers (read-only)
This repo ships 4 FastMCP servers under `src/aiqa_framework/mcp_servers/`,
read-only by default. List + configure them with:
- `uv run aiqa mcp-list` — show the servers.
- `uv run aiqa mcp-config` — print client config.
- `uv run aiqa mcp-start <server>` — start one.

| Server | Use |
|--------|-----|
| `framework-context` | **Call BEFORE generating code** — exposes conventions, the `TAGS` map, and existing pages/services/screens so generated code matches what exists. |
| `qa-report` | Read the latest `test-output/` run results. |
| `memory` | Read the `docs/ai/` tracking files (see `tracking-files.md`). |
| `test-runner` | Trigger / inspect a pytest run (read-only surface). |

---

## General rule
Partial completion is allowed. Whenever a fallback is taken, log it, continue
the workflow, and report it in the Phase 4 review so the human reviewer can
decide how to fill the gap.

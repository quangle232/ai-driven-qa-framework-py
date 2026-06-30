# QA Agent Workflow (merged: design → approve → automate → run → report)

## Mission
Transform a Jira user story (or pasted AC / note context) into:
- QA analysis
- **canonical JSON** test cases (the single source of truth)
- an editable **review table** + human approval loop
- approved final JSON
- an **Excel** export artifact (Trustify template) attached to the Jira story
- **generated Playwright/pytest code** for the approved automatable cases
- a **full run** of those + related existing tests, with results reported back
- Jira synchronization + artifact persistence to `docs/ai/`

This skill is two halves joined at the approved JSON:
1. **Design half** (STEP 0–13) — author + review + approve + export (no code yet).
2. **Automation half** (STEP 14–16) — turn approved manual cases into pytest,
   execute all, report results back into the JSON / Jira / `docs/ai/`.

## Source-of-truth priority
1. Jira user story via MCP
2. Note context fallback (`docs/ai/` in this repo)
3. Figma MCP
4. Prototype / live DOM (Playwright MCP)
5. Additional docs

Hard rule: do not let Figma or prototype override explicit business AC. And once
the JSON exists, **JSON is the source of truth** — never edit the table or code
without updating JSON first.

---

## STEP 0 — Input
Primary: Jira user story via MCP. **Fallback** (Jira MCP unavailable / no story /
missing key / permission / tool failure): use note context under `docs/ai/`,
continue the full workflow without blocking. See `fallbacks.md`.

## STEP 1 — Fetch + parse story
Extract: title, description, acceptance criteria, **labels**, **status**, Figma
link, prototype link. Fallback: parse the same fields from note context.

## STEP 2 — Parse acceptance criteria
Normalise explicit AC into `AC1`, `AC2`, … per `ac-parsing.md`. Do not invent AC;
if missing, continue with assumptions + open questions.

## STEP 3 — Create QA preparation subtask
Try to create the subtask **`Create Test Case`** on the story (see `jira-sync.md`;
detect `Subtask`/`Sub-task`, else linked `Task`). On success it is the preferred
review-sync target. On failure → story comment → note context. Never block.

## STEP 4 — Build design context
- **Figma** (if a link exists): extract sections, elements, labels, states.
  Fallback: skip UI extraction, suggest `data-test-id`, do not fabricate selectors.
- **Prototype / live DOM** (Playwright MCP, if reachable): extract selectors,
  navigation, URL patterns. Record routes in `docs/ai/navigation.md`.
  Selector priority (this framework): `data-zcqa → data-test-id → data-id →
  data-title`, then `id`, then `role + text`. Fallback: `element: ""`, do not
  guess DOM, recommend adding `data-test-id`.

## STEP 5 — QA analysis
Output: feature scope, main flow, validations, risks, assumptions, open questions.

## STEP 6 — Generate JSON-first test cases
Generate cases into canonical JSON first per `json-contract.md`. The preview table
is NEVER the source of truth. Cover all surfaces the story touches (UI / API /
gRPC / mobile) and keep cases automation-ready.

## STEP 7 — Enrich JSON quality
Before presenting the table, apply (see the matching reference files, and run
`scripts/json_quality_checks.py` to do it deterministically):
- `testing-strategy.md` — coverage rules (per-AC happy+negative, global minimums).
- `priority-scoring.md` — auto `P0`/`P1`/`P2` + `priorityReason`.
- `duplicate-detection.md` — mark exact duplicates for removal; near-duplicates
  for human review (`duplicateStatus` / `duplicateOf` / `duplicateReason`).
JSON stays the source of truth after enrichment.

## STEP 7.5 — Persist enriched JSON to note context
Write the fully-enriched JSON to `docs/ai/` (the Pilot-Space-note analogue):
`docs/ai/testcases/TestCases_<feature>.json`, and record it in
`docs/ai/memory.md` "Generated work". Persist even when Jira is available. Only
the finalised enriched JSON is persisted — not the raw generated version.

## STEP 8 — Render preview table
Render from the latest JSON per `review-table-rendering.md`. Required columns,
exact order:
`| TC ID | Feature | Sub-feature | Summary & Specific pre-condition | Test Description | Step details | Element | Pr. | Test Result | Bug ID | Notes |`
Use `<br>` for multiline; surface duplicate/priority hints in `Notes`. The table
must never drift from the JSON.

## STEP 9 — Sync preview
Sync the exact review table (status, assumptions, open questions, the one table)
in order: comment on `Create Test Case` → else story comment → else note context.
No derived/summary/analytics/priority-distribution tables — one primary table only.

## STEP 10 — Human approval loop
Wait for `EDIT_TABLE`, `CHANGESET`, direct revisions, or the exact phrase
**`I approve`**. Do not export Excel and do not generate code before approval.

## STEP 11 — Edit handling
On any edit: (1) update canonical JSON first, (2) re-run priority scoring,
(3) re-run duplicate detection, (4) regenerate the table from JSON, (5) re-sync,
(6) replace the persisted JSON artifact in `docs/ai/` so it reflects the latest.
Continue the loop.

## STEP 12 — Final JSON
Only on exact `I approve`: freeze the canonical JSON, set
`meta.approvalStatus = "approved"`. This frozen JSON is the only input to both
the Excel export and the code generation below.

## STEP 13 — Export Excel + attach
- Export with `scripts/export_json_to_trustify_excel.py` (see
  `python-export-runner.md`) →
  `test-output/qa/TestCases_<feature>.xlsx`.
- Persist the Excel to `docs/ai/testcases/` and attach it to the **parent Jira
  user story only** (never to a subtask) — see `jira-sync.md`. If direct attach
  is unsupported, comment the path on the story.

---

## STEP 14 — Generate Playwright/pytest from approved cases *(automation half)*
For each approved case where `automatable` is true / `duplicateStatus` is not a
removal, turn the manual JSON case into runnable pytest per
`framework-conventions.md` and `test-case-template.md` (the JSON↔pytest mapping):
- **UI** → Page Object in `pages/<name>_page.py` (extends `BasePage`, selectors as
  class attrs from the JSON `element` values, interaction via `self.keyword.*`);
  spec in `tests/ui/test_<feature>.py`.
- **API** → service in `api/services/`; pydantic models; spec in `tests/api/`.
- **gRPC** → `grpc/client.py`; assert `grpc.StatusCode.*`; spec in `tests/grpc/`.
- **Mobile** → `mobile/screens/` + `MobileActionKeyword`; `tests/mobile/` (native,
  skip-gated) or reuse the web POM in `tests/mobile_web/`.
- Map JSON → pytest: `acIds` → `@jira("<story>")`; JSON `priority` `P0/P1/P2` →
  marker `p0/p1/p2`; feature/label → surface + feature marker. `stepDetails`
  become the spec body steps; `summaryPrecondition` informs fixtures.
- New shared keywords go INTO the surface keyword layer — never call the transport
  directly in a spec. Reuse existing pages/services/screens.
- A new feature marker needs `config/tags.py` + `pyproject.toml`, both
  **patch-guarded** → ask the user (see `jira-sync.md`); reuse the closest marker
  meanwhile.
- Validate every generated file with `uv run aiqa guard --files <paths>` before
  finalising (rejects guarded paths, secrets, `time.sleep`, skips, raw
  `playwright.sync_api` imports in specs).

## STEP 15 — Execute all *(automation half)*
- New cases locally (fast): `uv run pytest -m "<markers>"` (or
  `uv run poe test-api | test-grpc | test-mobile-web | test-mobile-native`).
- Related existing tests: `python3 scripts/find_related_tests.py <marker>` then
  run them too. Optionally on CI:
  `python3 scripts/trigger_jenkins.py "<markers>" --no-wait` and check later with
  `--status=<build-url>` (see `jenkins-trigger.md`).
- "Execute all" = the newly generated cases **and** the related existing cases for
  the story's marker(s).

## STEP 16 — Report back *(automation half)*
- `uv run aiqa report-all` → `test-output/ai/` (stakeholder report).
- Write results back into the JSON: per case set `testResult` (Passed/Failed) and
  `bugId` if a defect was filed (the framework's `jira/bug_reporter.py` auto-files
  a Jira bug on the final failed attempt for `@jira` specs). Re-persist the JSON.
- Update `docs/ai/`: `test-case.md` statuses, `memory.md` "Run history",
  `navigation.md` new routes.
- Create / update the **`Execute Testing`** subtask with the run summary, the
  report link, pass/fail counts, and any bug IDs (see `jira-sync.md`). Refresh the
  review table's `Test Result` / `Bug ID` columns and re-sync.

---

## Hard rules
- **Approval loop is mandatory.** No Excel export and no code generation before the
  exact phrase `I approve`.
- **JSON is the source of truth.** Table and code are always regenerated from JSON.
- **Excel attaches to the parent user story only** — never to `Create Test Case`
  or `Execute Testing`.
- **Persist JSON and Excel to `docs/ai/`** whenever generated, even if Jira is up.
- **One primary review table** — no derived/summary/analytics tables anywhere.
- **Never hard-fail** on Jira / Figma / Playwright / MCP errors — fall back and
  continue (`fallbacks.md`).
- **Respect the patch guard** in the automation half; surface guarded edits to the
  user, never write them.
- All comments in English; update `docs/ai/` after every enrichment, edit, and run.

# QA Agent Workflow (merged: design → approve → automate → run → report)

## Mission
Transform a Jira user story (or pasted AC / note context) into:
- QA analysis
- **canonical JSON** test cases (the single source of truth)
- an editable **review table** + human approval loop
- approved final JSON
- a test-management artifact in the client's chosen tool (open Excel / Xray / TestRail)
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
Primary: Jira user story via MCP. If the Jira MCP is unreachable, do NOT silently
degrade — run the **guided Jira MCP setup** (warn the user → offer to configure
`.mcp.json` → reload → retry the fetch and confirm the user story is reachable) per
`fallbacks.md` + `mcp-usage.md`. Only use note context under `docs/ai/` if the user
declines or it still fails.

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

**Coverage matrix is mandatory** for the generated set: `{happy, negative, edge}`
× the story's surfaces (`ui`, `api`, …, optional `performance` / `security`).
Every cell is covered by a case, turned into a new case, or an explicit N/A with
an honest reason — the matrix is shown in the STEP 8 review. Set `coverageType`
on each case (`json-contract.md`).

**Impacted-flow analysis** — the second context: from the story, name the
surfaces the change touches (endpoints/response shapes, pages/components, shared
code); map them to existing flows via the tracking files and the existing-code
index. Covered impacted flows JOIN the STEP 15 execution; uncovered ones become
new cases. The list (flow, spec or NEW, reason, risk) is part of the STEP 8 review.

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

## STEP 13 — Publish to the chosen test management
Ask the client which target they want (default **Excel**); record it in
`meta.testManagement`. See `test-management.md`.
- **Excel (open / default)** — `scripts/export_json_to_excel.py` (see
  `python-export-runner.md`) → `test-output/qa/TestCases_<feature>.xlsx`; persist to
  `docs/ai/testcases/`. **This export is a LOCAL review copy — do NOT attach it to
  Jira yet.** Jira gets exactly ONE Excel upload (STEP 16): the post-execution
  re-export with the `Status` column verified filled — never a resultless
  duplicate. (Flows that end without execution attach this approval-time file
  instead.) Attach to the **parent Jira user story only** (never a subtask) via
  `scripts/attach_file_to_jira.py` — the Atlassian MCP has no upload tool.
- **Xray** — create Jira `Test` issues from the approved JSON via the Jira MCP;
  store each `xrayKey` back into the case.
- **TestRail** — create cases + a run via the TestRail MCP (needs config; guided
  setup in `fallbacks.md`); store `testrailCaseId` / `meta.testrailRunId`.

---

## STEP 14 — Generate Playwright/pytest from approved cases *(automation half)*
Code generation is shared with the **`gen-auto-test`** skill
(`../../gen-auto-test/SKILL.md`) — the manual-cases entry point delegates HERE
once its cases are normalized, and this step follows the same engine rules.
For each approved case where `automatable` is true / `duplicateStatus` is not a
removal, turn the manual JSON case into runnable pytest per
`framework-conventions.md` and `test-case-template.md` (the JSON↔pytest mapping):
- **Anti-duplication gate (do this FIRST):** query the `framework-context` MCP and
  scan `modules/ui/pages/` / `modules/api/rest/services/` / `modules/mobile/screens/` / `tests/` (plus
  `python3 scripts/find_related_tests.py <marker>`). If an equivalent page object,
  service, screen, or spec already exists, REUSE or extend it — never regenerate a
  near-duplicate. Skip JSON cases flagged `duplicateStatus: "duplicate"`.
- **UI** → Page Object in `modules/ui/pages/<name>_page.py` (extends `BasePage`, selectors as
  class attrs from the JSON `element` values, interaction via `self.keyword.*`);
  spec in `tests/ui/test_<feature>.py`.
- **API** → service in `modules/api/rest/services/`; pydantic models; spec in `tests/api/`.
- **gRPC** → `modules/api/grpc/client.py`; assert `grpc.StatusCode.*`; spec in `tests/grpc/`.
- **Mobile** → `modules/mobile/screens/` + `MobileActionKeyword`; `tests/mobile/` (native,
  skip-gated) or reuse the web POM in `tests/mobile_web/`.
- Map JSON → pytest: `acIds` → `@jira("<story>")`; JSON `priority` `P0/P1/P2` →
  marker `p0/p1/p2`; feature/label → surface + feature marker. `stepDetails`
  become the spec body steps; `summaryPrecondition` informs fixtures.
- New shared keywords go INTO the surface keyword layer — never call the transport
  directly in a spec. Reuse existing modules/ui/pages/services/screens.
- A new feature marker may be **added to `shared/config/tags.py`** — the ONE
  guarded file the patch guard allows (additive `TAGS` entries only; the marker ==
  Jira label convention requires one per feature). Registering it in
  `pyproject.toml` `[tool.pytest.ini_options] markers` is still patch-guarded →
  ask the user (an unregistered marker only warns meanwhile).
- Validate every generated file with `uv run aiqa guard --files <paths>` before
  finalising (rejects guarded paths, secrets, `time.sleep`, skips, raw
  `playwright.sync_api` imports in specs).

## STEP 15 — Execute all + STRESS gate *(automation half)*
- **STRICT HEADLESS:** every run of newly generated cases — first run, re-runs,
  stress — is headless (pytest-playwright's default and the exact mode CI uses).
  Never pass `--headed` in the generation pipeline; a test that only passes
  headed is not done.
- New cases locally (fast): `uv run pytest -m "<markers>"` (or
  `uv run poe test-api | test-grpc | test-mobile-web | test-mobile-native`).
- Related existing tests **and impacted flows** (STEP 5 list):
  `python3 scripts/find_related_tests.py <marker>` then run them too. Optionally
  on CI: `python3 scripts/trigger_jenkins.py "<markers>" --no-wait` and check
  later with `--status=<build-url>` (see `jenkins-trigger.md`).
- "Execute all" = the newly generated cases **and** the related existing cases for
  the story's marker(s).
- **FINALIZE order — freeze the report BEFORE stress** so repeats never inflate
  it: run the new cases once → `uv run aiqa report-all` (and any Allure artifact)
  → only then stress.
- **STRESS gate — mandatory for every NEW auto case:** re-run it with
  `uv run pytest "<nodeid>" --count=5 --json-report-file=test-output/stress-report.json`
  (pytest-repeat; the redirected report file keeps the frozen run report intact).
  **All 5 repeats must pass** before the test counts as done; any failed repeat =
  flakiness — fix the test-side cause and re-stress. Workers: serial on a shared
  SUT (the default — no `-n`); `-n 3` max only when the target tolerates parallel.
  Entity-creating specs: the `cleanup` teardown runs per repeat — verify no
  leftovers accumulate. Report stress as a markdown summary table (case | repeats
  | result | duration) in the review, the MR description, and a Jira comment on
  the parent story.

## STEP 15.5 — ⏸ Review scripts + results → branch is AUTOMATIC on approval
Present for human review with clickable file links: every generated file (a
one-line plain-English summary + `git diff --stat`), the run AND stress results
(the 5/5 table), the finalize artifact links. **That approval IS the
authorization to ship**: create the branch, commit ONLY the generated files,
push, and open the MR automatically — no second confirmation.
- **MR description — review best-practice**, 5 fixed sections: (1) what changed —
  every file Added/Changed with a one-line purpose; (2) new-case execution summary
  table; (3) stress summary table (5/5); (4) artifacts & Jira links; (5) reviewer
  notes (guard exceptions, deviations, known defects).
- Branch naming (team rule): **`test/<STORY-KEY>-<feature-slug>`**; runs without a
  story (gen-auto-test standalone): `test/manual-<slug>-<YYYYMMDD>`.
- MR via `scripts/create_gitlab_mr.py` (GitLab adapter — config from
  `GITLAB_URL`/`GITLAB_TOKEN`/`GITLAB_PROJECT_ID` or `environments/.env.gitlab`;
  other providers can follow the same contract). If the repo has no remote,
  report "branch+MR skipped — repo not bootstrapped" and continue.

## STEP 16 — Update statuses + report back *(automation half)*
- Write results back into the JSON: per case set `testResult`
  (Passed/Failed/Skipped) and `bugId` if a defect was filed. Re-persist the JSON.
- **Bug policy:** a final-attempt failure writes an approval-gated **DRAFT**
  (`test-output/ai/bug-drafts/` — JSON + self-contained HTML with repro command
  and embedded screenshots; root conftest gate). File a bug via the Jira MCP ONLY
  for drafts the user explicitly approves. `JIRA_AUTO_BUG=yes` is the explicit
  opt-in for direct auto-filing. Ensure the drafts index exists even when green:
  `uv run python -m aiqa_framework.shared.reporting.ensure_bug_drafts_index`.
- **Update statuses on the chosen test-management server** (see
  `test-management.md`): Excel → re-export with `Status`/`Bug ID` filled (VERIFY
  the column is filled — a resultless sheet is a duplicate, not an artifact) and
  attach it to the parent story via `scripts/attach_file_to_jira.py` — this is
  the ONE Excel upload; Xray → create a `Test Execution` and set each test
  PASS/FAIL; TestRail → add results to the run.
- **Deliver the HTML execution report to the user**: `uv run aiqa report-all` →
  `test-output/ai/` (stakeholder HTML); surface the path/link to the user.
- Update `docs/ai/`: `test-case.md` statuses, `memory.md` "Run history",
  `navigation.md` new routes. Create / update the **`Execute Testing`** item with the
  run summary, report link, pass/fail counts, and bug IDs (see `jira-sync.md`).
  Refresh the review table's `Test Result` / `Bug ID` columns and re-sync.

---

## Hard rules
- **Human approval loop is mandatory.** No publish (Excel / Xray / TestRail) and no
  code generation before the exact phrase `I approve`. Never bypass it.
- **JSON is the source of truth.** Table and code are always regenerated from JSON.
- **Guided MCP setup, not a silent skip.** If the Jira / TestRail MCP is unreachable,
  warn the user, offer to configure it, and retry BEFORE any note-context / Excel
  fallback (`fallbacks.md`).
- **Anti-duplication.** Reuse existing pages / services / screens / specs; never
  regenerate an equivalent (STEP 14 gate). Honour `duplicateStatus`.
- **Publish to the parent user story only** — the Excel / Xray tests link to the
  story, never to `Create Test Case` or `Execute Testing`.
- **Persist JSON + Excel to `docs/ai/`** whenever generated, even if Jira is up.
- **One primary review table** — no derived/summary/analytics tables anywhere.
- **Respect the patch guard** in the automation half; surface guarded edits to the
  user, never write them (`shared/config/tags.py` is the one allowed exception —
  additive `TAGS` entries).
- **New tests must be 5/5 stress-green** (`--count=5`, headless, serial on a
  shared SUT) before they are presented as done.
- **STRICT HEADLESS for generated cases** — never `--headed` in the generation
  pipeline; a test that only passes headed is not done.
- **Bugs are never auto-filed** — failures write drafts that wait for human
  approval (`JIRA_AUTO_BUG=yes` is the explicit opt-in).
- **Generated code ships via branch + MR only** (`test/<STORY-KEY>-<slug>`),
  auto-created by the STEP 15.5 approval — never straight to the default branch.
- **Presentation rules:** every approval gate and results summary lists the
  related files as clickable links with one-line plain-English summaries.
- All comments in English; update `docs/ai/` after every enrichment, edit, and run.

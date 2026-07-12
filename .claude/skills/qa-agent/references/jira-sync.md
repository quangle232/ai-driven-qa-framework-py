# Jira Synchronization Contract

Two subtasks bracket the workflow: **`Create Test Case`** (the design/review half)
and **`Execute Testing`** (the automation/run half). The Excel deliverable attaches
to the **parent user story only**.

## Child issue type compatibility
Do not assume the child type is `Sub-task`. When creating a child item:
1. detect the supported child type in the project,
2. prefer `Subtask`, else `Sub-task`,
3. else fall back to a normal linked `Task`.

Applies to both `Create Test Case` and `Execute Testing`. A type mismatch must
never block the QA workflow.

## STEP A — `Create Test Case` item (design half)
- Create as a subtask under the parent story (STEP 3); fall back to a linked `Task`.
- Purpose: the review-sync target during the approval loop + a lightweight
  test-case-prep tracker.
- This item is **not** the artifact attachment target — the Excel must not attach here.

## STEP B — Review sync target order (approval loop)
Sync the preview in this order: comment on `Create Test Case` → else comment on the
parent story → else write to `docs/ai/` note context. Content = current review
status, assumptions, open questions, and the exact latest review table only (no
derived tables). See `review-table-rendering.md`.

## STEP C — Artifact target rules
- **JSON artifact** → persist to `docs/ai/testcases/TestCases_<feature>.json`
  (and note its path in `docs/ai/memory.md`).
- **Excel artifact** → persist to `test-output/qa/` and `docs/ai/testcases/`, and
  attach to the parent Jira **user story** when Jira is available.
- `docs/ai/` is not optional — it always retains the JSON + Excel even when Jira is up.

## STEP D — Attach final Excel to the parent user story
Trigger only after the exact phrase `I approve`, the JSON is frozen, and the Excel
is generated. Attach `test-output/qa/TestCases_<feature>.xlsx` to the parent story
**only** — never to `Create Test Case` or `Execute Testing`. If direct attach is
unsupported, comment the path + approval status + manual-attach note on the story.
Also add/update a final story comment with the approved review summary, test-case
count, coverage summary, and approval status.

**Target note (`test-management.md`):** the above is the **Excel** target. For
**Xray**, the published `Test` issues live in Jira and a `Test Execution` carries
the results — nothing extra to attach to the story. For **TestRail**, cases and
results live in TestRail; comment the run link on the story. STEP 16 updates the
statuses on whichever target the client chose.

## STEP E — `Execute Testing` item (automation half)
- Create as a subtask under the parent story (or linked `Task`).
- Purpose: execution tracking, worklog, **and the automation results** from
  STEP 14–16:
  - the pytest run summary (pass / fail / skipped counts),
  - the `uv run aiqa report-all` report link (`test-output/ai/`) or the Jenkins
    build URL,
  - the new auto cases (TC ID + title + `specFile`) and the related existing tests
    that were re-run,
  - any **bug IDs** filed — a final-attempt failure writes an approval-gated DRAFT
    to `test-output/ai/bug-drafts/` (root conftest gate; `JIRA_AUTO_BUG=yes` opts
    into direct auto-filing via `shared/reporting/bug_reporter.py`). Bugs filed
    from approved drafts get linked here and written back into the JSON `bugId`
    + the review table.
- Keep it lightweight: do not attach the main Excel here or duplicate every case body.

## Child item creation fallback
If creating `Create Test Case` / `Execute Testing` fails (issue-type mismatch,
project restriction, permission): fall back to a linked `Task`; else skip creation.
Never fail the overall QA workflow because of child-item problems — record the
intended content in `docs/ai/memory.md` instead.

## Hard rules
- The JSON review loop may sync to the `Create Test Case` comment.
- The final Excel attaches to the parent user story **only**.
- Both JSON and Excel also persist to `docs/ai/`.
- `Execute Testing` holds run results + tracking; the Excel never attaches there.
- Jira sync failure must not block the workflow; `docs/ai/` failure must not block
  Jira sync.
- No derived / summary / priority-distribution / automation-candidate tables in any
  synced content — the exact review table only.

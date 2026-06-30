# Review Table Rendering

## Goal
Render a stable, readable, Jira-safe preview table from the current JSON.

## Source of truth
Always render from the latest JSON. Never edit the table without updating JSON first.

## Required columns (exact order)
| TC ID | Feature | Sub-feature | Summary & Specific pre-condition | Test Description | Step details | Element | Pr. | Test Result | Bug ID | Notes |

## Rendering rules
- Markdown table; `<br>` for multiline cell content; one test case per row.
- Do not omit columns even if empty.
- `Pr.` is mapped from JSON `priority`.
- `Test Result` / `Bug ID` empty by default — filled in STEP 16 after the run.

## Step details rendering
Render `stepDetails` as compact multiline text: `1. Open page`, `2. Enter valid
email`, `3. Click submit`. If a step has an `element`, append it:
`3. Click submit | element: [data-test-id="login-submit"]`.

## Notes rendering
Use `Notes` to surface review-relevant signals, concisely:
- `Priority: P0 — core flow`
- `Duplicate: possible-overlap with TC-003`
- `Question: clarify empty password behavior`

## Exact review table rule
The synced review note must print the exact same approval table shown in the
conversation. Hard rules:
- exactly one primary review table, exact columns + row order, same row set;
- no summary / analytics / dashboard / priority-distribution / automation-candidate
  tables; no derived or report-layout tables; do not split into multiple tables.

## Jira comment / note-context structure
When syncing the preview (to the `Create Test Case` comment, the story comment, or
`docs/ai/` note context), use exactly:

### QA Review Status
draft / revised / awaiting approval / approved

### Assumptions
bullet list or `None`

### Open Questions
bullet list or `None`

### Exact Review Table
the markdown table with the exact required columns — exactly one table, no derived
summaries.

### Review Guidance
use `EDIT_TABLE`, `CHANGESET`, or `I approve`.

## Duplicate / priority display
If a case has `duplicateStatus` / `duplicateOf` / `duplicateReason`, show a concise
version in `Notes`. If it has `priority` / `priorityReason`, show `priority` in
`Pr.` and a concise reason in `Notes` only when useful.

## Final approval comment
After approval, the final Jira **user story** comment includes: status = approved;
final table; total test case count; duplicate-cleanup note if relevant; the
exported Excel path if direct attachment is unavailable. After STEP 16, also reflect
pass/fail counts and bug IDs. Keep the exact primary review table intact — no derived
tables.

---
name: publish-testcases
description: Publish already-approved test cases (canonical JSON) to the client's chosen test management — export an open Excel, create Xray Test issues + a Test Execution, or create TestRail cases + a run — attach the Excel to the parent Jira story, and update statuses after a run. Use when cases are already approved and you just need to export/publish, without re-running the design workflow.
---

# publish-testcases — approved JSON → test management

Standalone publish step (qa-agent STEP 13 + the STEP 16 status update), for when the
cases are already approved and you don't need the full design workflow.

## Preconditions
- Input = the approved canonical JSON (e.g.
  `docs/ai/<module>/testcases/TestCases_<feature>.json`) with
  `meta.approvalStatus == "approved"`. If it is NOT approved, STOP — run the approval
  loop first (`user-story-test` / `qa-agent`). Never publish un-approved cases.
- Target = `meta.testManagement` (`excel` | `xray` | `testrail`); if unset, ask (default
  `excel`). See `.claude/skills/qa-agent/references/test-management.md` + `jira-sync.md`.

## Publish (per target)
- **Excel (open, default)** —
  `uv run --with openpyxl python3 .claude/skills/qa-agent/scripts/export_json_to_excel.py
  --json <json> --out test-output/qa/TestCases_<feature>.xlsx`; attach the `.xlsx` to
  the **parent Jira user story only** (Jira MCP; if attach is unsupported, comment the
  path); persist a copy under `docs/ai/<module>/testcases/`.
- **Xray** — create Jira `Test` issues from the cases (Jira MCP); store each `xrayKey`.
- **TestRail** — create the section + cases + a run (TestRail MCP); store `testrailCaseId`
  / `meta.testrailRunId`. If the MCP/config is missing → run `mcp-setup`, or fall back to
  the Excel target.

## Status update (when run results exist)
After a run (`run-tests` / `read-report`): write `testResult` + `bugId` back into the
JSON and push statuses — Excel → re-export; Xray → set the `Test Execution` PASS/FAIL;
TestRail → add results to the run. Update `docs/ai/<module>/` and the
`Create Test Case` / `Execute Testing` items.

## Hard rules
- Approved JSON only; JSON is the source of truth. Excel/Xray link to the **parent story**,
  never a subtask. Persist artifacts to `docs/ai/<module>/` even when Jira is up.

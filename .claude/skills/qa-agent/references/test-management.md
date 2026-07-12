# Test Management Targets (client's choice)

After approval (STEP 13), the approved JSON is published to a test-management
target. The client chooses; the default is the **open Excel** interchange. Record
the choice in `meta.testManagement` (`excel` | `xray` | `testrail`) and write any
created IDs back into the JSON so STEP 16 can update statuses.

Always confirm the target with the user before publishing. Never publish before
the exact approval phrase `I approve`.

---

## 1. Excel — open / default
The neutral interchange. No tool, no MCP, no config:
```bash
uv run --with openpyxl python3 \
  .claude/skills/qa-agent/scripts/export_json_to_excel.py \
  --json docs/ai/testcases/TestCases_<feature>.json \
  --out test-output/qa/TestCases_<feature>.xlsx
```
The columns (`ID, Title, Feature, Sub-feature, Preconditions, Steps, Expected
Result, Priority, Type, AC, Status, Bug ID, Notes`) import cleanly into Xray,
TestRail, Zephyr, etc. Persist it to `docs/ai/testcases/`.

**Attach timing: exactly ONE upload, post-execution.** The approval-time export
is a local review copy only. After execution, re-export with the results written
back into the JSON, VERIFY the `Status` column is actually filled (a resultless
sheet is a duplicate, not an artifact), and attach THAT file to the parent Jira
user story (see `jira-sync.md`) via
`.claude/skills/qa-agent/scripts/attach_file_to_jira.py` — the Atlassian MCP has
no attachment-upload tool. Flows that end without execution attach the
approval-time export instead.

Use this when the client has no integrated tool, or wants to import the cases
themselves.

## 2. Xray — Jira-native (via the Jira MCP)
Xray test cases ARE Jira issues, so no extra MCP — the Jira MCP is enough.

Publish (STEP 13):
- For each approved automatable/manual case, create a Jira issue of type **`Test`**
  (Xray), under / linked to the parent user story. Put the steps into the Xray
  test-step fields (action / data / expected) derived from `stepDetails` +
  `expectedResult`; set priority from `priority`; link the AC.
- "Parse Jira into Xray tests" = the AC/JSON cases become these `Test` issues.
- Store each created key back into the case as `xrayKey`.

Status update (STEP 16):
- Create a Jira issue of type **`Test Execution`** for the run, add the tests, and
  set each test result to **PASS / FAIL** from the pytest outcome. Store the
  execution key as `meta.testExecutionKey`. Link any filed bug (`bugId`).

Fallback: if the project has no Xray `Test` / `Test Execution` issue types
(detect, like `jira-sync.md`), warn the user and fall back to the Excel target.

## 3. TestRail — needs config + a TestRail MCP
TestRail is external, so it needs BOTH:
- **TestRail config**: `TESTRAIL_URL`, `TESTRAIL_USER`, `TESTRAIL_API_KEY` (env or
  `environments/.env.testrail`, gitignored — never commit keys), plus the target
  `project_id` / `suite_id`.
- **A TestRail MCP** configured in the Claude Code MCP config (see `mcp-usage.md`).

Publish (STEP 13, via the TestRail MCP):
- Ensure a Section for `<feature>`; create a Case per approved case (title =
  `testDescription`, preconditions, steps from `stepDetails`, expected from
  `expectedResult`, priority mapped). Store `testrailCaseId` back per case.
- Create a Run for the suite/section; store `meta.testrailRunId`.

Status update (STEP 16, via the TestRail MCP):
- Add a result to the run for each case: Passed (1) / Failed (5) from the pytest
  outcome, with the report link and any `bugId` in the comment.

Fallback: if the TestRail MCP or config is missing → run the **guided setup** in
`fallbacks.md` (warn, help write the MCP config + `.env.testrail`, re-run). If the
user declines, fall back to the Excel target and tell them they can import it into
TestRail later.

---

## Status mapping (STEP 16)
| pytest outcome | JSON `testResult` | Xray | TestRail |
|----------------|-------------------|------|----------|
| passed | `Passed` | PASS | Passed (1) |
| failed | `Failed` | FAIL | Failed (5) |
| skipped/xfail | `Skipped` | TODO | Untested/Blocked |

Whatever the target, also: write `testResult` + `bugId` back into the JSON,
re-export the Excel, update `docs/ai/`, and deliver the HTML execution report
(`uv run aiqa report-all` → `test-output/ai/`).

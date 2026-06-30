# Canonical JSON Contract

JSON is always the source of truth during the review cycle **and** the input to
both the Excel export (STEP 13) and pytest generation (STEP 14).

## Minimum structure
```json
{
  "schemaVersion": "aiqa.qa.excel.v1",
  "meta": {
    "feature": "",
    "userStoryKey": "",
    "sourceNoteTitle": "",
    "figmaDesignLink": "",
    "prototypeLink": "",
    "generatedAt": "",
    "approvalRequired": true,
    "approvalStatus": "draft"
  },
  "testCases": [],
  "assumptions": [],
  "openQuestions": []
}
```

## Test case fields
Each test case supports:
- `tcId`
- `feature`
- `subFeature`
- `summaryPrecondition`
- `testDescription`
- `stepDetails` (list of `{ "step", "detail", "element" }`)
- `priority` (`P0` / `P1` / `P2`)
- `priorityReason`
- `duplicateStatus` (`""` / `"duplicate"` / `"possible-overlap"`)
- `duplicateOf`
- `duplicateReason`
- `acIds` (e.g. `["AC1"]`)
- `automatable` (`true` / `false`) — drives STEP 14
- `surface` (`ui` / `api` / `grpc` / `mobile_web` / `mobile_native`) — drives STEP 14
- `specFile` — set in STEP 14 once the pytest file is generated
- `testResult` (`""` / `Passed` / `Failed`) — set in STEP 16
- `bugId` — set in STEP 16 if a defect is filed
- `notes`

## Step details example
```json
{ "step": 1, "detail": "Open login page", "element": "[data-test-id=\"login\"]" }
```

## Rules
- Never treat the preview table as the source of truth.
- All edits update the JSON first; the table is always regenerated from the latest JSON.
- `automatable` + `surface` + `stepDetails.element` are what make STEP 14
  deterministic — fill them during enrichment when known.
- The enriched JSON is persisted to `docs/ai/testcases/TestCases_<feature>.json`.

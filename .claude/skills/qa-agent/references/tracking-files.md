# Tracking Files & Artifacts — docs/ai/<module>/

`docs/ai/` is this repo's note-context store (the Pilot-Space-note analogue), split
**per module** so each surface keeps its own AI memory. `shared/memory/store.py`
resolves the paths; the `memory` MCP server exposes them. Read at STEP 0; update
throughout. If a file is missing, create it from the matching `../examples/` file.
These files are read/written by the skills (`create-test-cases`, `automation-generate`,
`read-report`, `qa-status`, `flaky-triage`, and `qa-agent`).

```
docs/ai/
  ui/          memory.md · navigation.md · test-case.md · testcases/
  api/         memory.md · test-case.md · testcases/
  performance/ memory.md · test-case.md
  mobile/      memory.md · test-case.md · testcases/
```
Pick the folder for the surface you are working on (a story may touch several).

## memory.md (per module)
- **## Generated work** — `Date | User story | Feature | Marker / label | Artifacts`
  (JSON path, Excel path, generated spec + page object / service / screen + testdata).
- **## Decisions** · **## Known gaps** · **## Run history** (`Date | Marker | Result`).

## test-case.md (per module)
The catalogue of cases for that surface (mirrors the review-table columns), with
`Status` and `Spec File`. Cross-check before generating to avoid duplicates.

## navigation.md (ui only)
`Screen | Route / URL | How to reach it | Page Object` — reused so a known screen
is not re-explored with the Playwright MCP.

## testcases/ (artifacts)
`TestCases_<feature>.json` (canonical enriched/approved JSON) and, for the Excel
target, `TestCases_<feature>.xlsx` (also in `test-output/qa/`).

## Update rules (by step)
- STEP 7.5 — persist enriched JSON under the module's `testcases/`; note it in `memory.md`.
- STEP 8/11 — keep the module `test-case.md` in sync with the latest JSON/table.
- STEP 13 — persist the Excel; record its path.
- STEP 14 — record generated pages/specs in `memory.md`; new routes in `navigation.md`.
- STEP 16 — write each case `Status` in `test-case.md`, append `memory.md` "Run history",
  record bug IDs.
- Append new rows; update in place. Absolute dates (`YYYY-MM-DD`). Commit alongside tests.

# Tracking Files & Artifacts — docs/ai/

`docs/ai/` is this repo's note-context store (the Pilot-Space-note analogue). It
carries context across runs and holds the JSON + Excel artifacts. Read it at STEP 0;
update it throughout. If a tracking file is missing, create it from the matching
file in `../examples/`.

## docs/ai/memory.md
What has been done. Sections:
- **## Generated work** — `Date | User story | Feature | Marker / label | Artifacts`
  (JSON path, Excel path, generated spec + page object / service / screen + testdata).
- **## Decisions** — notable choices, reuse decisions, deviations.
- **## Known gaps** — missing `data-test-id`s, brittle/unverified selectors,
  manual-only areas, MCP steps skipped via fallback, patch-guarded markers awaiting
  the user.
- **## Run history** — `Date | Marker run | Result`.

## docs/ai/test-case.md
The human-readable catalogue of all cases (mirrors the review table columns), with
`Status` and `Spec File`. Cross-check before generating to avoid duplicates.

## docs/ai/navigation.md
`Screen | Route / URL | How to reach it | Page Object` — reused so a known screen
is not re-explored with the Playwright MCP.

## docs/ai/testcases/  (artifacts)
- `TestCases_<feature>.json` — the canonical enriched/approved JSON (source of truth).
- `TestCases_<feature>.xlsx` — the exported Excel (also in `test-output/qa/`).
Keep these as the single source of truth; the `memory` MCP server
(`uv run aiqa mcp-start memory`) exposes `docs/ai/` read-only.

## Update rules (by step)
- STEP 7.5 — persist the enriched JSON; add it to `memory.md` "Generated work".
- STEP 8/11 — keep `test-case.md` in sync with the latest JSON/table.
- STEP 13 — persist the Excel; record its path.
- STEP 14 — record generated pages/specs in `memory.md`; new routes in `navigation.md`.
- STEP 16 — write each case `Status` (Passed/Failed) in `test-case.md`, append a
  `memory.md` "Run history" row, and record bug IDs.
- Append new rows; update an existing row/status in place. Convert relative dates to
  absolute (`YYYY-MM-DD`). Commit these alongside the generated tests.

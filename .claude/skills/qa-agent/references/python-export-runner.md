# Python Export Runner

## Purpose
Export approved QA JSON into an Excel file matching the Trustify-style test case
template.

## Dependency
The export uses **openpyxl**, which is not a framework dependency. Run it with an
ephemeral dependency so nothing in `pyproject.toml` (patch-guarded) changes:

```bash
uv run --with openpyxl python3 \
  .claude/skills/qa-agent/scripts/export_json_to_trustify_excel.py \
  --json docs/ai/testcases/TestCases_<feature>.json \
  --out test-output/qa/TestCases_<feature>.xlsx
```

Add an optional `--template path/to/Trustify_test_case_template.xlsx` to fill an
existing template instead of building a fresh workbook.

## Optional quality check (run during STEP 7 and after major edits)
```bash
python3 .claude/skills/qa-agent/scripts/json_quality_checks.py \
  --json docs/ai/testcases/TestCases_<feature>.json --write
```
This enriches the JSON in place with auto `priority` / `priorityReason` and
`duplicateStatus` / `duplicateOf` / `duplicateReason` (stdlib only). Omit
`--write` to only report findings.

## Notes
- Export only AFTER the exact approval phrase `I approve`.
- The JSON input must be the approved, frozen final JSON.
- Attach the resulting Excel to the parent Jira user story only (see `jira-sync.md`).

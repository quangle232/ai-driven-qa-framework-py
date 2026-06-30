# Python Export Runner (open Excel target)

## Purpose
Export approved QA JSON into an **open, tool-agnostic** Excel file. This is the
default test-management target and the neutral interchange the client can import
into Xray / TestRail / Zephyr (see `test-management.md` for the Xray / TestRail
direct integrations).

## Dependency
The export uses **openpyxl**, which is not a framework dependency. Run it with an
ephemeral dependency so `pyproject.toml` (patch-guarded) is untouched:

```bash
uv run --with openpyxl python3 \
  .claude/skills/qa-agent/scripts/export_json_to_excel.py \
  --json docs/ai/testcases/TestCases_<feature>.json \
  --out test-output/qa/TestCases_<feature>.xlsx
```

Add `--template path/to/your_template.xlsx` to fill a tool-specific template
instead of building a fresh workbook.

Open columns (import cleanly into common tools):
`ID · Title · Feature · Sub-feature · Preconditions · Steps · Expected Result ·
Priority · Type · AC · Status · Bug ID · Notes`.

## Optional quality check (run during STEP 7 and after major edits)
```bash
python3 .claude/skills/qa-agent/scripts/json_quality_checks.py \
  --json docs/ai/testcases/TestCases_<feature>.json --write
```
Enriches the JSON in place with auto `priority` / `priorityReason` and duplicate
flags (stdlib only). Omit `--write` to only report findings.

## Notes
- Export only AFTER the exact approval phrase `I approve`.
- The JSON input must be the approved, frozen final JSON.
- Attach the resulting Excel to the parent Jira user story only (see `jira-sync.md`).
- STEP 16 re-exports with the `Status` / `Bug ID` columns filled after the run.

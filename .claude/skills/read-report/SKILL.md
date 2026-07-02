---
name: read-report
description: Read and analyze test output — parse pytest-report.json, cluster failures, run AI root-cause analysis with concrete fixing instructions, produce a stakeholder HTML summary, and (optionally) an Allure report. Use after a run to understand results and what to fix.
---

# read-report — analyze results + AI failure analysis

## Deterministic pipeline (aiqa CLI)
Reads `test-output/pytest-report.json`, writes `test-output/ai/`:
```
uv run aiqa collect      # pytest json + CI metadata -> events
uv run aiqa diagnose     # cluster failures + detect critical patterns
uv run aiqa finalize     # write diagnosis markdown
uv run aiqa report-html  # stakeholder HTML
```
Or `uv run aiqa report-all` for the whole chain.

## AI failure analysis
LLM analysis turns on when `AI_PROVIDER` has a key (claude / openai; else a
deterministic noop). For each failure cluster produce: the likely **root cause**, the
offending file / selector / assertion, and a concrete **fixing instruction** (what to
change). Flag **flaky** (passed-on-rerun) and **critical patterns** (auth / 5xx /
timeouts) separately.

## Summary
Present: totals (pass / fail / skip), pass rate, top clusters with counts, criticals,
flaky, and a ranked "fix these first" list — with the HTML report path.

## Allure (optional — needs the `reporting` extra)
```
uv run pytest --alluredir=test-output/allure-results -m "<marker>"
allure generate test-output/allure-results -o test-output/allure-report --clean
# or: allure serve test-output/allure-results
```

## Notes
- Read-only analysis: it suggests fixes but does not apply them — use `review-code` /
  `automation-generate` to act, and `flaky-triage` for flaky tests. Auto-filed Jira
  bugs come from the run itself (`shared/reporting/bug_reporter.py`).

---
name: flaky-triage
description: Detect and confirm flaky tests by repeated reruns, quarantine them, and record them in the flaky-history memory so future runs and the AI diagnosis know. Use when a test passes-on-rerun or fails intermittently.
---

# flaky-triage — find + quarantine flaky tests

1. **Identify suspects**: passed-on-rerun in the last run (`read-report` flags these) or
   a test the user names.
2. **Confirm**: rerun in isolation several times and record the pass/fail ratio:
   `uv run pytest "<nodeid>" --count=10 --json-report-file=test-output/stress-report.json`
   (pytest-repeat; the redirected report keeps the main run report intact) — or a
   `for i in $(seq 10)` loop / `--reruns`.
3. **Classify**: a real defect (→ keep failing / file a bug) vs genuinely flaky
   (nondeterministic — timing, order, or shared data).
4. **Quarantine** flaky ones: gate them (e.g. a `@flaky`/skip marker) with a reason +
   owner, and add an entry to the **flaky-history** memory via the `memory` MCP
   (`add_entry`, write-gated by `AIQA_ALLOW_MEMORY_WRITE=true`) or directly in
   `.aiqa-memory/flaky-history.json`.
5. **Report** the list + likely cause and a stabilization suggestion (explicit waits,
   test isolation, data reset, deterministic seeds).

Do not delete tests to make a suite green — quarantine + track instead.

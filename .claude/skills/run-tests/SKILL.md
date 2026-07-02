---
name: run-tests
description: Run AIQA tests by surface, marker, or tag with the right environment and reruns — locally or on Jenkins — then hand off to read-report. Use for "run the api tests", "run regression on test env", "run tag @login".
---

# run-tests — execute a suite

1. **Select** what to run:
   - Surface task: `uv run poe test-ui | test-api | test-grpc | test-graphql |
     test-mobile-web | test-mobile-native | test-perf`.
   - Or a marker expression: `uv run pytest -m "<expr>" --reruns 2`.
2. **Env + gates**: `test_env=dev|test|prod` (default test). Skip-gates:
   `ALLOW_MOBILE_NATIVE=1` (native mobile), `ALLOW_PERF=1` (performance). API / gRPC /
   GraphQL are mock-backed (no backend needed); UI needs the SUT + browsers.
3. **Related existing tests**: `python3 .claude/skills/qa-agent/scripts/find_related_tests.py <marker>`.
   CI option: `python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py "<markers>" --no-wait`
   then `--status=<build-url>` (see `references/jenkins-trigger.md`).
4. **After the run**, invoke `read-report` for analysis, AI failure diagnosis, and a
   summary. `--reruns` distinguishes flaky (passed-on-rerun) — pass those to `flaky-triage`.

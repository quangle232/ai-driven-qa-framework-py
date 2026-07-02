# Performance module conventions (Locust + JMeter)

Load / stress testing of HTTP endpoints. No Playwright; no functional assertions
beyond SLOs.

## Structure
- `locust/` — `locustfile.py` (entry) + `scenarios/` (reusable `TaskSet`s). Locust
  is imported only here (perf extra), never at package import.
- `jmeter/` — `.jmx` plans in `plans/` + `runner.py` (shells `jmeter -n -t`).
  JMeter is external (Java); no pip dependency.
- `helpers/` — `PerfStats` + `assert_thresholds` (fail on SLO breach).

## Rules
- Tag perf tests `@tags(TAGS.PERFORMANCE)`; they are **skip-gated** by `ALLOW_PERF=1`
  (need a running target + the tool), like native mobile.
- Define SLOs explicitly (max failure ratio, p95 budget) and assert them via
  `helpers.assert_thresholds` — a perf test passes/fails on thresholds, not vibes.
- Point load at a real host or the API FastAPI mock served on a port; do not load
  the in-process ASGI transport.

## Run in isolation
```bash
uv sync --extra perf
# Locust headless against a target:
uv run locust -f src/aiqa_framework/modules/performance/locust/locustfile.py \
  --host http://localhost:8000 --headless -u 10 -r 2 -t 15s
# JMeter (needs jmeter on PATH):
uv run python -m aiqa_framework.modules.performance.jmeter.runner --host localhost --port 8000
# Gated smoke test:
ALLOW_PERF=1 uv run pytest tests/performance -m performance
```
Memory: `docs/ai/performance/`.

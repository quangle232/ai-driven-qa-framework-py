# modules/performance — Load testing (Locust + JMeter)

Two engines, one surface:
- **Locust** (Python): `locust/locustfile.py` + reusable `scenarios/`.
- **JMeter** (Java, external): `.jmx` plans + `jmeter/runner.py`.

Install + run in isolation:
```bash
uv sync --extra perf
uv run locust -f src/aiqa_framework/modules/performance/locust/locustfile.py --host http://TARGET
uv run python -m aiqa_framework.modules.performance.jmeter.runner --host TARGET --port 80
ALLOW_PERF=1 uv run pytest tests/performance -m performance
```

Assert SLOs with `aiqa_framework.modules.performance.helpers.assert_thresholds`.
Conventions: `conventions.md`. Memory: `docs/ai/performance/`.

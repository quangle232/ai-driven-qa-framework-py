"""Run a JMeter .jmx plan headlessly. JMeter is external (Java) — no pip dep.

    uv run python -m aiqa_framework.modules.performance.jmeter.runner \
      --plan src/aiqa_framework/modules/performance/jmeter/plans/sample.jmx \
      --host localhost --port 8000
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

DEFAULT_PLAN = Path(__file__).parent / "plans" / "sample.jmx"


def run_plan(
    plan: str | Path = DEFAULT_PLAN,
    results: str | Path = "test-output/perf/jmeter-results.jtl",
    jmeter_bin: str = "jmeter",
    properties: dict[str, str] | None = None,
) -> int:
    """Invoke `jmeter -n -t plan -l results [-J k=v ...]`. Returns the exit code."""
    exe = shutil.which(jmeter_bin)
    if not exe:
        raise RuntimeError(f"'{jmeter_bin}' not found on PATH — install JMeter or pass jmeter_bin")
    Path(results).parent.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "-n", "-t", str(plan), "-l", str(results)]
    for key, value in (properties or {}).items():
        cmd += [f"-J{key}={value}"]
    return subprocess.run(cmd, check=False).returncode  # noqa: S603 (jmeter path resolved via which)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a JMeter plan headlessly.")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--results", default="test-output/perf/jmeter-results.jtl")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="8000")
    args = parser.parse_args()
    return run_plan(args.plan, args.results, properties={"host": args.host, "port": args.port})


if __name__ == "__main__":
    raise SystemExit(main())

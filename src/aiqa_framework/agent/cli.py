"""The ``aiqa`` CLI (port of cli/aiqa.ts) — Typer.

Phase-1 pipeline is deterministic (no LLM): collect -> diagnose -> finalize ->
report-html, reading ``test-output/pytest-report.json``. LLM diagnosis kicks in
automatically when ``AI_PROVIDER`` has an API key.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer

from aiqa_framework.agent.utils.paths import ai_qa_out_dir

app = typer.Typer(help="AI QA Agent — collect, diagnose, report, MCP.", no_args_is_help=True)

MCP_SERVERS = {
    "aiqa-qa-report": "aiqa_framework.mcp_servers.qa_report",
    "aiqa-framework-context": "aiqa_framework.mcp_servers.framework_context",
    "aiqa-memory": "aiqa_framework.mcp_servers.memory",
    "aiqa-test-runner": "aiqa_framework.mcp_servers.test_runner",
}


def _collect_to_disk():
    from aiqa_framework.agent.collectors.ci_metadata_collector import collect_ci_metadata
    from aiqa_framework.agent.collectors.pytest_report_reader import read_failures

    failures, summary = read_failures()
    ci = collect_ci_metadata()
    out = ai_qa_out_dir()
    (out / "failures.json").write_text(json.dumps([f.model_dump() for f in failures], indent=2))
    (out / "ci-metadata.json").write_text(ci.model_dump_json(indent=2))
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    return failures, summary, ci


@app.command()
def collect() -> None:
    """Read the pytest JSON report + CI metadata into test-output/ai/."""
    failures, _, _ = _collect_to_disk()
    typer.echo(f"collected {len(failures)} failure(s) -> {ai_qa_out_dir()}")


@app.command()
def diagnose() -> None:
    """Cluster + classify failures (LLM if AI_PROVIDER key is set, else deterministic)."""
    from aiqa_framework.agent.agents.failure_diagnosis_agent import diagnose as run
    from aiqa_framework.agent.collectors.pytest_report_reader import read_failures
    from aiqa_framework.agent.reports.diagnosis_report_writer import write_diagnosis_md

    failures, _ = read_failures()
    diag = run(failures)
    (ai_qa_out_dir() / "diagnosis.json").write_text(diag.model_dump_json(indent=2))
    path = write_diagnosis_md(diag)
    typer.echo(f"diagnosed {diag.total_failures} failure(s) via {diag.provider_name} -> {path}")


@app.command()
def finalize() -> None:
    """Write the CI summary + detect critical patterns."""
    from aiqa_framework.agent.collectors.pytest_report_reader import read_failures
    from aiqa_framework.agent.reports.ci_summary_writer import write_ci_summary
    from aiqa_framework.agent.utils.run_id import resolve_run_id
    from aiqa_framework.agent.watchers.critical_pattern_detector import detect_criticals

    failures, _ = read_failures()
    crit = detect_criticals(failures)
    path = write_ci_summary(resolve_run_id(), failures, crit)
    typer.echo(f"finalized -> {path} ({len(crit)} critical event(s))")


@app.command("report-html")
def report_html() -> None:
    """Self-contained stakeholder HTML report."""
    from aiqa_framework.agent.agents.failure_diagnosis_agent import diagnose as run
    from aiqa_framework.agent.collectors.pytest_report_reader import read_failures
    from aiqa_framework.agent.reports.stakeholder_html import write_stakeholder_html

    failures, _ = read_failures()
    path = write_stakeholder_html(run(failures))
    typer.echo(f"report -> {path}")


@app.command("report-all")
def report_all() -> None:
    """collect -> diagnose -> finalize -> report-html."""
    collect()
    diagnose()
    finalize()
    report_html()


@app.command("notify-critical")
def notify_critical() -> None:
    """Print critical events (channels: SLACK_WEBHOOK_URL / etc. — dry-run by default)."""
    from aiqa_framework.agent.collectors.pytest_report_reader import read_failures
    from aiqa_framework.agent.watchers.critical_pattern_detector import detect_criticals

    crit = detect_criticals(read_failures()[0])
    if not crit:
        typer.echo("no critical events")
        return
    for c in crit:
        typer.echo(f"[critical] {c.trigger}: {c.summary}")


@app.command()
def doctor() -> None:
    """Health-check the install."""
    from aiqa_framework.agent.orchestration.doctor import run_checks

    ok = True
    for name, passed, detail in run_checks():
        mark = "✓" if passed else "✗"
        ok = ok and passed
        typer.echo(f"  {mark} {name}: {detail}")
    raise typer.Exit(code=0 if ok else 1)


@app.command()
def guard(files: list[str] = typer.Option(None, "--files", help="Files to check")) -> None:
    """Deterministic safety gate — accept/reject generated files."""
    from aiqa_framework.agent.analyzers.patch_guard import guard_file

    bad = 0
    for f in files or []:
        content = Path(f).read_text() if Path(f).exists() else ""
        result = guard_file(f, content)
        if result.accepted:
            typer.echo(f"  ✓ {result.path}")
        else:
            bad += 1
            typer.echo(f"  ✗ {result.path}: {'; '.join(result.reasons)}")
    raise typer.Exit(code=1 if bad else 0)


@app.command()
def scan() -> None:
    """Index existing Page Objects / services / screens / specs for reuse."""
    root = Path("src/aiqa_framework")

    def _names(rel: str) -> list[str]:
        return [p.name for p in (root / rel).glob("*.py") if p.name != "__init__.py"]

    index = {
        "ui_pages": _names("modules/ui/pages"),
        "api_rest_services": _names("modules/api/rest/services"),
        "api_graphql_queries": _names("modules/api/graphql/queries"),
        "mobile_screens": _names("modules/mobile/screens"),
        "specs": [str(p) for p in Path("tests").rglob("test_*.py")],
    }
    (ai_qa_out_dir() / "existing-code-index.json").write_text(json.dumps(index, indent=2))
    typer.echo(json.dumps(index, indent=2))


@app.command("generate-automation")
def generate_automation() -> None:
    """Code generation is LLM-driven via the qa-agent skill, not this CLI."""
    typer.echo(
        "Use Claude Code / your LLM with the qa-agent skill (.claude/skills/qa-agent). "
        "Generated code is checked by `aiqa guard`."
    )


@app.command("run-regression")
def run_regression(marker: str = typer.Option("regression", "--marker", "-m")) -> None:
    """Run pytest for a marker, then the deterministic report pipeline."""
    code = subprocess.call(["pytest", "-m", marker])
    report_all()
    raise typer.Exit(code=code)


@app.command()
def watch() -> None:
    """Watch test-output for new reports and re-run the deterministic pipeline."""
    import time

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class _Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if str(event.src_path).endswith("pytest-report.json"):
                report_all()

    target = Path("test-output")
    target.mkdir(parents=True, exist_ok=True)
    obs = Observer()
    obs.schedule(_Handler(), str(target), recursive=True)
    obs.start()
    typer.echo("watching test-output/ … (Ctrl-C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


@app.command()
def init() -> None:
    """Create the test-output/ai output directory."""
    typer.echo(f"ready: {ai_qa_out_dir()}")


@app.command("init-project")
def init_project(env: str = typer.Option("test", "--env")) -> None:
    """Scaffold environments/.env.<env> from its template."""
    template = Path(f"environments/.env.{env}.example")
    target = Path(f"environments/.env.{env}")
    if not template.exists():
        typer.echo(f"no template {template}")
        raise typer.Exit(code=1)
    if target.exists():
        typer.echo(f"{target} already exists — leaving as-is")
        return
    target.write_text(template.read_text())
    typer.echo(f"created {target} — fill in the values")


@app.command("mcp-list")
def mcp_list() -> None:
    """List the MCP servers and their modules."""
    for name, module in MCP_SERVERS.items():
        typer.echo(f"  {name}  ->  {module}")


@app.command("mcp-config")
def mcp_config() -> None:
    """Print a Claude-Code-style .mcp.json snippet for the 4 servers."""
    cfg = {
        "mcpServers": {
            name: {"command": "uv", "args": ["run", "python", "-m", module]}
            for name, module in MCP_SERVERS.items()
        }
    }
    typer.echo(json.dumps(cfg, indent=2))


@app.command("mcp-start")
def mcp_start(server: str = typer.Argument(..., help="one of: " + ", ".join(MCP_SERVERS))) -> None:
    """Start an MCP server on stdio."""
    import importlib

    module = MCP_SERVERS.get(server)
    if not module:
        typer.echo(f"unknown server {server}; choose from {', '.join(MCP_SERVERS)}")
        raise typer.Exit(code=2)
    importlib.import_module(module).mcp.run()


if __name__ == "__main__":
    app()

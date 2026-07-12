"""Root pytest config — the ``helper/test.ts`` + ``global-setup`` analogue.

- Loads the env file for ``test_env`` (dev/test/prod) before the session.
- Auto-skips ``@mobile_native`` / ``@performance`` unless explicitly enabled.
- Failure → Jira flow behind a HUMAN APPROVAL GATE: the FINAL failed attempt of
  a test tagged ``@jira("KEY")`` writes a bug DRAFT (JSON + self-contained HTML
  with repro command and embedded screenshots) to ``test-output/ai/bug-drafts/``
  — nothing is created in Jira. A human (or the qa-agent skill, after explicit
  approval in chat) reviews the drafts and files the real bugs. Set
  ``JIRA_AUTO_BUG=yes`` to restore direct auto-filing.
  (Flaky pass-on-rerun -> nothing; ``@bugs`` known-defects -> nothing.)
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from aiqa_framework.shared.config.env import load_env_file
from aiqa_framework.shared.reporting.bug_draft_writer import (
    BUG_DRAFTS_DIR,
    BugDraftInput,
    write_bug_draft,
)
from aiqa_framework.shared.reporting.bug_reporter import report_bug_to_jira

# Explicit opt-in for direct auto-filing; the default is approval-gated drafts.
_AUTO_BUG = (os.environ.get("JIRA_AUTO_BUG") or "no").strip().lower() == "yes"


def pytest_configure(config: pytest.Config) -> None:
    load_env_file()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Surfaces that need external infra are skip-gated unless explicitly enabled.
    gates = [
        ("mobile_native", "ALLOW_MOBILE_NATIVE", "native mobile needs a device + Appium"),
        ("performance", "ALLOW_PERF", "performance needs a live target + load tool"),
    ]
    for marker, env_var, why in gates:
        if os.environ.get(env_var):
            continue
        skip = pytest.mark.skip(reason=f"{why}; set {env_var}=1")
        for item in items:
            if item.get_closest_marker(marker):
                item.add_marker(skip)


def _max_reruns(item: pytest.Item) -> int:
    try:
        return int(item.config.getoption("reruns") or 0)
    except Exception:  # noqa: BLE001 - option absent if pytest-rerunfailures missing
        return 0


def _find_failure_images(item: pytest.Item) -> list[Path]:
    """Best-effort: pytest-playwright screenshots for this test under test-results/."""
    root = Path("test-results")
    if not root.is_dir():
        return []
    slug = re.sub(r"[^a-z0-9]+", "-", item.name.lower()).strip("-")[:40]
    images = [
        png
        for png in root.rglob("*.png")
        if slug and slug in png.parent.name.lower().replace("_", "-")
    ]
    return images[:6]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    outcome = yield
    report = outcome.get_result()

    # Only genuine call-phase failures qualify: skips are report.skipped and an
    # interrupted run (Ctrl+C) aborts without a failed call report — neither
    # may ever create a Jira artifact or a draft.
    if report.when != "call" or not report.failed:
        return
    if item.get_closest_marker("bugs"):
        return  # known defect — do not open a new bug

    # Only on the FINAL attempt (pytest-rerunfailures sets execution_count, 1-based).
    reruns = _max_reruns(item)
    attempt = int(getattr(item, "execution_count", 1) or 1)
    if attempt <= reruns:
        return  # more reruns to come -> defer

    marker = item.get_closest_marker("jira")
    story = marker.args[0] if marker and marker.args else None
    if not story:
        return

    longrepr = getattr(report, "longreprtext", "") or str(report.longrepr or "")
    summary = f"[Auto] {item.name}"
    description = "\n".join(
        [
            f"Failing test: {item.nodeid}",
            f"Parent story: {story}",
            "",
            "Error:",
            "\n".join(longrepr.splitlines()[:12]),
        ]
    )

    if _AUTO_BUG:
        report_bug_to_jira(parent_story_key=story, summary=summary, description=description)
        return

    # Human approval gate: record a draft (JSON + HTML with embedded evidence),
    # never touch Jira. The qa-agent files approved drafts via the Jira MCP.
    env = os.environ.get("test_env", "test")
    html_path = write_bug_draft(
        BugDraftInput(
            parent_story_key=story,
            summary=summary,
            description=description,
            spec_file=str(item.fspath),
            test_title=item.name,
            repro_command=f'test_env={env} uv run pytest "{item.nodeid}"',
            output_dir="test-results/",
            images=_find_failure_images(item),
            jira_base_url=(os.environ.get("JIRA_URL") or "").rstrip("/"),
        )
    )
    if html_path:
        print(
            f"\n[bug-draft] 📝 DRAFT recorded for {story} — NOT filed "
            f"(human approval required; open {BUG_DRAFTS_DIR}/index.html)"
        )

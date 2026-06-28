"""Root pytest config — the ``helper/test.ts`` + ``global-setup`` analogue.

- Loads the env file for ``test_env`` (dev/test/prod) before the session.
- Auto-skips ``@mobile_native`` unless ``ALLOW_MOBILE_NATIVE=1``.
- Reports a Jira Bug on the FINAL failed attempt of a test tagged ``@jira("KEY")``
  (flaky pass-on-rerun -> no bug; ``@bugs`` known-defects -> no bug).
"""

from __future__ import annotations

import os

import pytest

from aiqa_framework.config.env import load_env_file
from aiqa_framework.jira.bug_reporter import report_bug_to_jira


def pytest_configure(config: pytest.Config) -> None:
    load_env_file()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("ALLOW_MOBILE_NATIVE"):
        return
    skip = pytest.mark.skip(reason="native mobile needs a device + Appium; set ALLOW_MOBILE_NATIVE=1")
    for item in items:
        if item.get_closest_marker("mobile_native"):
            item.add_marker(skip)


def _max_reruns(item: pytest.Item) -> int:
    try:
        return int(item.config.getoption("reruns") or 0)
    except Exception:  # noqa: BLE001 - option absent if pytest-rerunfailures missing
        return 0


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    outcome = yield
    report = outcome.get_result()

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
    description = "\n".join(
        [
            f"Failing test: {item.nodeid}",
            f"Parent story: {story}",
            "",
            "Error:",
            "\n".join(longrepr.splitlines()[:12]),
        ]
    )
    report_bug_to_jira(parent_story_key=story, summary=f"[Auto] {item.name}", description=description)

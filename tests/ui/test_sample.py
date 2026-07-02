"""SAMPLE UI spec (port of sample.spec.ts) — keep / delete / clone.

Demonstrates: import the Page Object (never page.locator in a spec), tag with
markers, link the parent Jira story via @jira, and use the auto-authenticated
`page` (pytest-playwright + storage state).
"""

from __future__ import annotations

import os

from aiqa_framework.modules.ui.pages.sample_page import SamplePage
from aiqa_framework.modules.ui.testdata.sample_data import sample_expected, sample_input
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.SMOKE, TAGS.P1)
@jira("PROJ-1")
def test_sample_post_login_heading(page) -> None:
    sample = SamplePage(page)

    sample.open(os.environ.get("APP_URL", "/"))

    assert sample_expected["heading_contains"] in sample.get_heading_text(), "Heading text mismatch"

    sample.fill_email(sample_input["email"])
    sample.submit()
    sample.verify_flash_visible()

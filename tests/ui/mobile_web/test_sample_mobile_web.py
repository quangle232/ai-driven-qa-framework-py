"""SAMPLE mobile-web spec (Playwright device emulation) — port of
sample.mobile-web.spec.ts. Reuses the EXISTING web POM unchanged; only the
viewport (Pixel 7 / iPhone 14) differs. Runs against the SUT like the web suite.
"""

from __future__ import annotations

import os

from aiqa_framework.modules.ui.pages.sample_page import SamplePage
from aiqa_framework.modules.ui.testdata.sample_data import sample_expected
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.MOBILE, TAGS.MOBILE_WEB, TAGS.SMOKE, TAGS.P1)
@jira("PROJ-MOB-2")
def test_mobile_web_heading_on_phone_viewport(page) -> None:
    sample = SamplePage(page)
    sample.open(os.environ.get("APP_URL", "/"))

    viewport = page.viewport_size or {"width": 9999}
    assert viewport["width"] < 600, "expected an emulated phone viewport"

    assert sample_expected["heading_contains"] in sample.get_heading_text()

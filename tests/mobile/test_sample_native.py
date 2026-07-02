"""SAMPLE native-mobile spec (Appium) — port of sample.native.spec.ts.

Skip-gated: needs a device/emulator + a running Appium server + an app build
(MOBILE_APP). Run with `poe test-mobile-native` (sets ALLOW_MOBILE_NATIVE=1);
otherwise auto-skipped by the root conftest.
"""

from __future__ import annotations

from aiqa_framework.modules.mobile.screens.sample_login_screen import SampleLoginScreen
from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.MOBILE, TAGS.MOBILE_NATIVE, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-MOB-1")
def test_native_login_shows_welcome(mobile_keyword) -> None:
    login = SampleLoginScreen(mobile_keyword)
    login.login("demo", "demo-pass")
    assert "Welcome" in login.get_welcome_text(), "welcome text mismatch"

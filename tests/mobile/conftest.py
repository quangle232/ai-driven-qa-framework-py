"""Native-mobile fixtures (Appium). One session per worker -> parallel drivers.
These only instantiate when a @mobile_native test actually runs; the root
conftest auto-skips them unless ALLOW_MOBILE_NATIVE=1."""

from __future__ import annotations

import pytest

from aiqa_framework.mobile.action_keyword import MobileActionKeyword
from aiqa_framework.mobile.driver_factory import create_driver


@pytest.fixture
def driver():
    drv = create_driver()
    try:
        yield drv
    finally:
        drv.quit()


@pytest.fixture
def mobile_keyword(driver) -> MobileActionKeyword:
    return MobileActionKeyword(driver)

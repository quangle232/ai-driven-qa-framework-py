"""Create a WebdriverIO-equivalent Appium session (port of driver-factory.ts).

One session per worker (see tests/mobile/conftest.py) -> parallel drivers via
pytest-xdist. Local Appium by default; cloud grids (BrowserStack / Sauce Labs)
via ``DEVICE_GRID`` + creds — all env-driven.
"""

from __future__ import annotations

import os

from appium import webdriver
from appium.options.common import AppiumOptions

from aiqa_framework.config.settings import get_settings
from aiqa_framework.mobile.capabilities import resolve_capabilities


def _server_url() -> str:
    grid = (get_settings().device_grid or "local").lower()
    if grid == "browserstack":
        return "https://hub.browserstack.com/wd/hub"
    if grid == "saucelabs":
        return "https://ondemand.us-west-1.saucelabs.com/wd/hub"
    return get_settings().appium_url  # local Appium 2 (base path "/")


def create_driver() -> webdriver.Remote:
    options = AppiumOptions()
    options.load_capabilities({k: v for k, v in resolve_capabilities().items() if v is not None})
    return webdriver.Remote(_server_url(), options=options)

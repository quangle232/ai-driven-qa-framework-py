"""Appium capability matrix for native mobile (port of capabilities/index.ts).

``MOBILE_PLATFORM`` (android|ios) picks the base set; ``DEVICE_GRID``
(local|browserstack|saucelabs) layers vendor options; ``MOBILE_APP`` is the
build under test. Everything comes from env (see environments/.env.example).
"""

from __future__ import annotations

import os

from aiqa_framework.shared.config.settings import get_settings


def resolve_capabilities() -> dict:
    s = get_settings()
    platform = (s.mobile_platform or "android").lower()
    return _ios(s.mobile_app) if platform == "ios" else _android(s.mobile_app)


def _android(app: str | None) -> dict:
    return {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": os.environ.get("ANDROID_DEVICE", "Android Emulator"),
        "appium:app": app,
        "appium:newCommandTimeout": 240,
        **_grid_options("android"),
    }


def _ios(app: str | None) -> dict:
    return {
        "platformName": "iOS",
        "appium:automationName": "XCUITest",
        "appium:deviceName": os.environ.get("IOS_DEVICE", "iPhone 15"),
        "appium:app": app,
        "appium:newCommandTimeout": 240,
        **_grid_options("ios"),
    }


def _grid_options(platform: str) -> dict:
    grid = (get_settings().device_grid or "local").lower()
    if grid == "browserstack":
        return {
            "bstack:options": {
                "userName": os.environ.get("BROWSERSTACK_USERNAME"),
                "accessKey": os.environ.get("BROWSERSTACK_ACCESS_KEY"),
                "projectName": "ai-driven-qa-framework",
                "deviceName": "iPhone 15" if platform == "ios" else "Google Pixel 8",
            }
        }
    if grid == "saucelabs":
        return {
            "sauce:options": {
                "username": os.environ.get("SAUCE_USERNAME"),
                "accessKey": os.environ.get("SAUCE_ACCESS_KEY"),
                "build": "ai-driven-qa-framework",
            }
        }
    return {}

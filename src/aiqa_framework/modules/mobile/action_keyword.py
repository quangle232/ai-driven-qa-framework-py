"""MobileActionKeyword — the native-mobile interaction layer (port of
mobile-action-keyword.ts). The ONLY layer that touches Appium/Selenium.
Accessibility-id-first locators (stable across iOS + Android).
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 20  # seconds


class MobileActionKeyword:
    def __init__(self, driver) -> None:
        self.driver = driver

    def _wait(self) -> WebDriverWait:
        return WebDriverWait(self.driver, DEFAULT_TIMEOUT)

    def tap(self, accessibility_id: str) -> None:
        el = self._wait().until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        el.click()

    def type(self, accessibility_id: str, text: str) -> None:
        el = self._wait().until(
            EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        el.clear()
        el.send_keys(text)

    def get_text(self, accessibility_id: str) -> str:
        el = self._wait().until(
            EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        return el.text

    def wait_for_visible(self, accessibility_id: str) -> None:
        self._wait().until(
            EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )

    def is_displayed(self, accessibility_id: str) -> bool:
        try:
            return self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, accessibility_id
            ).is_displayed()
        except Exception:  # noqa: BLE001
            return False

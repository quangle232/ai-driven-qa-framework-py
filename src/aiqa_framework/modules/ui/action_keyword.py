"""ActionKeyword — the single Playwright interaction layer (port of
helper/action-keywords.ts).

The ONLY place that touches the Playwright API. Page Objects call
``self.keyword.*``; specs call Page Objects. Keeps the TS behaviour:
stakeholder-friendly timeout errors + a stable locator strategy
(``data-zcqa`` -> ``data-test-id`` -> ``data-id`` -> ``data-title``).
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PWTimeoutError

DEFAULT_TIMEOUT = 60_000  # ms

_XPATH_TEXT = re.compile(r"normalize-space\([^)]*\)\s*=\s*[\"']([^\"']+)[\"']")
_ROLE = re.compile(r"@role\s*=\s*[\"']([^\"']+)[\"']")
_DATA_ATTR = re.compile(r"\[data-(?:zcqa|test-id|id|title)\s*=\s*[\"']([^\"']+)[\"']\]")
_ID = re.compile(r"^#([\w-]+)")


class ActionKeyword:
    DEFAULT_TIMEOUT = DEFAULT_TIMEOUT

    def __init__(self, page: Page) -> None:
        self.page = page

    # ---- stakeholder-friendly errors ----------------------------------------

    @staticmethod
    def _friendly_label(selector: str) -> str:
        m = _XPATH_TEXT.search(selector)
        if m:
            role = _ROLE.search(selector)
            return f'{role.group(1)} "{m.group(1)}"' if role else f'"{m.group(1)}"'
        m = _DATA_ATTR.search(selector)
        if m:
            return f'element "{m.group(1)}"'
        m = _ID.search(selector)
        if m:
            return f"element #{m.group(1)}"
        return selector if len(selector) <= 70 else selector[:67] + "..."

    def _friendly_wait(
        self, element: Locator, state: str, timeout: float, action: str, selector: str
    ) -> None:
        try:
            element.wait_for(state=state, timeout=timeout)
        except PWTimeoutError as err:
            label = self._friendly_label(selector)
            raise AssertionError(
                f"Step failed: could not {action} {label} — not {state} within "
                f"{timeout / 1000:g}s.\n  (selector: {selector})"
            ) from err

    # ---- navigation ---------------------------------------------------------

    def goto(self, url: str, timeout: float = DEFAULT_TIMEOUT * 2) -> None:
        self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)

    # ---- actions ------------------------------------------------------------

    def wait_and_click(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        element = self.page.locator(selector).nth(index)
        self._friendly_wait(element, "visible", timeout, "click", selector)
        element.click(timeout=timeout)

    def click_item_by_text(self, text: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.wait_and_click(f"text='{text}'", 0, timeout)

    def wait_and_fill(
        self, selector: str, value: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        element = self.page.locator(selector).nth(index)
        self._friendly_wait(element, "visible", timeout, "fill", selector)
        element.clear(timeout=timeout)
        element.fill(value, timeout=timeout)

    def select_by_value(
        self, selector: str, value: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        element = self.page.locator(selector).nth(index)
        element.wait_for(state="visible", timeout=timeout)
        element.select_option(value=value, timeout=timeout)

    def select_by_label(
        self, selector: str, label: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        element = self.page.locator(selector).nth(index)
        element.wait_for(state="visible", timeout=timeout)
        element.select_option(label=label, timeout=timeout)

    def upload_file(self, selector: str, file_path: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        element = self.page.locator(selector)
        element.wait_for(state="attached", timeout=timeout)
        element.set_input_files(file_path, timeout=timeout)

    # ---- getters ------------------------------------------------------------

    def wait_and_get_text(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> str:
        element = self.page.locator(selector).nth(index)
        element.wait_for(state="visible", timeout=timeout)
        return element.inner_text()

    def get_element_text(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> str:
        """Async-safe text getter: poll until non-empty (SPAs paint before populating)."""
        element = self.page.locator(selector).nth(index)
        self._friendly_wait(element, "visible", timeout, "read", selector)
        end = time.monotonic() + timeout / 1000
        text = ""
        while time.monotonic() < end:
            text = (element.inner_text() or "").strip()
            if text:
                return text
            self.page.wait_for_timeout(200)
        return text

    def wait_and_get_value(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> str:
        element = self.page.locator(selector).nth(index)
        element.wait_for(state="visible", timeout=timeout)
        return element.input_value() or ""

    def get_element(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> Locator:
        element = self.page.locator(selector).nth(index)
        self._friendly_wait(element, "visible", timeout, "find", selector)
        return element

    def get_elements(self, selector: str, timeout: float = DEFAULT_TIMEOUT) -> Locator:
        elements = self.page.locator(selector)
        self._friendly_wait(elements.first, "attached", timeout, "find", selector)
        return elements

    # ---- state checks -------------------------------------------------------

    def is_element_visible(self, selector: str, index: int = 0, timeout: float = 3000) -> bool:
        element = self.page.locator(selector).nth(index)
        try:
            element.wait_for(state="visible", timeout=timeout)
            return True
        except PWTimeoutError:
            return False

    def is_element_disabled(self, selector: str, index: int = 0, timeout: float = 3000) -> bool:
        element = self.page.locator(selector).nth(index)
        try:
            element.wait_for(state="visible", timeout=timeout)
            if element.is_disabled():
                return True
            return element.get_attribute("aria-disabled") == "true"
        except PWTimeoutError:
            return False

    def wait_for_element_hidden(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        self.page.locator(selector).nth(index).wait_for(state="hidden", timeout=timeout)

    # ---- assertions (auto-retrying via expect) ------------------------------

    def verify_element_visible(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT, reason: str = ""
    ) -> None:
        try:
            expect(self.page.locator(selector).nth(index)).to_be_visible(timeout=timeout)
        except AssertionError as err:
            label = self._friendly_label(selector)
            raise AssertionError(
                f"{reason or 'Expected visible'}: {label} not visible.\n  (selector: {selector})"
            ) from err

    def verify_element_not_visible(
        self, selector: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        expect(self.page.locator(selector).nth(index)).to_be_hidden(timeout=timeout)

    def verify_text_content(
        self, selector: str, text: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        expect(self.page.locator(selector).nth(index)).to_contain_text(text, timeout=timeout)

    def verify_value_content(
        self, selector: str, text: str, index: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        expect(self.page.locator(selector).nth(index)).to_have_value(
            re.compile(re.escape(text)), timeout=timeout
        )

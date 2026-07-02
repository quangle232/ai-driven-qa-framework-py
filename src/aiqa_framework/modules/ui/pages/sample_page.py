"""SAMPLE Page Object (port of sample-page.ts). Replace with your screens.

Conventions: extends BasePage; selectors grouped as class attributes; methods
only call ``self.keyword.*`` (never ``page.locator`` directly).
"""

from __future__ import annotations

from aiqa_framework.modules.ui.base_page import BasePage


class SamplePage(BasePage):
    _heading = "h1"
    # Prefer test-only attrs (priority: data-zcqa -> data-test-id -> data-id -> data-title).
    _email_input = '[data-test-id="email"]'
    _submit_button = 'button[type="submit"]'
    _flash = '[data-test-id="flash"]'

    def open(self, url: str) -> None:
        self.keyword.goto(url)

    def get_heading_text(self) -> str:
        return self.keyword.get_element_text(self._heading)

    def fill_email(self, email: str) -> None:
        self.keyword.wait_and_fill(self._email_input, email)

    def submit(self) -> None:
        self.keyword.wait_and_click(self._submit_button)

    def verify_flash_visible(self, reason: str = "Expected a flash message") -> None:
        self.keyword.verify_element_visible(self._flash, reason=reason)

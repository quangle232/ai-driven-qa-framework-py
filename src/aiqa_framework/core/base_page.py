"""BasePage — shared base for every Page Object (port of base-page.ts).

Holds the Playwright ``page`` and the ``ActionKeyword`` helper so Page Objects
only depend on ``self.keyword``.
"""

from __future__ import annotations

from playwright.sync_api import Page

from aiqa_framework.core.action_keyword import ActionKeyword


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.keyword = ActionKeyword(page)

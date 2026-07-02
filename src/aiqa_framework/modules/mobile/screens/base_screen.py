"""BaseScreen — shared base for native Screen Objects (mobile POM)."""

from __future__ import annotations

from aiqa_framework.modules.mobile.action_keyword import MobileActionKeyword


class BaseScreen:
    def __init__(self, keyword: MobileActionKeyword) -> None:
        self.keyword = keyword

"""SAMPLE native Screen Object (port of sample-login.screen.ts)."""

from __future__ import annotations

from aiqa_framework.mobile.screens.base_screen import BaseScreen


class SampleLoginScreen(BaseScreen):
    _USERNAME = "login_username"
    _PASSWORD = "login_password"
    _SUBMIT = "login_submit"
    _WELCOME = "home_welcome"

    def login(self, username: str, password: str) -> None:
        self.keyword.type(self._USERNAME, username)
        self.keyword.type(self._PASSWORD, password)
        self.keyword.tap(self._SUBMIT)

    def get_welcome_text(self) -> str:
        return self.keyword.get_text(self._WELCOME)

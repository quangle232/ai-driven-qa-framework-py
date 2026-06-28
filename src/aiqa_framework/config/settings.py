"""Typed access to environment configuration (the ``ENV`` analogue).

Reads the current ``os.environ`` (populated by ``config.env.load_env_file``).
Call :func:`get_settings` AFTER the env file is loaded (the conftest does this
in ``pytest_configure``). Field names map case-insensitively to env vars, e.g.
``app_url`` <- ``APP_URL``.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=False)

    # Web UI
    app_url: str | None = None
    auth_url: str | None = None
    app_user: str | None = None
    app_pass: str | None = None

    # API
    api_base_url: str | None = None
    api_token: str | None = None

    # gRPC (defaults point at the local mock)
    grpc_host: str = "localhost"
    grpc_port: int = 50051
    grpc_tls: bool = False
    grpc_token: str | None = None

    # Mobile (native Appium + optional cloud grid)
    appium_url: str = "http://127.0.0.1:4723"
    mobile_platform: str | None = None  # "android" | "ios"
    device_grid: str | None = None  # "local" | "browserstack" | "saucelabs"
    mobile_app: str | None = None

    # Jira (failure -> Bug reporter)
    jira_url: str | None = None
    jira_email: str | None = None
    jira_token: str | None = None
    jira_project: str | None = None

    @property
    def effective_api_base_url(self) -> str | None:
        """API base URL, falling back to the web APP_URL when unset."""
        return self.api_base_url or self.app_url


def get_settings() -> Settings:
    """Fresh settings snapshot from the current process environment."""
    return Settings()

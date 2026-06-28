"""Single source of truth for "which env file do we load?".

Selection is driven by the ``test_env`` environment variable:

    test_env=prod uv run pytest ...   -> loads environments/.env.prod
    test_env=dev  uv run pytest ...   -> loads environments/.env.dev
    (unset)                           -> loads environments/.env.<DEFAULT_ENV>

Loaded once from the root ``conftest.py``. Real ``.env.<env>`` files are
gitignored; only the ``*.example`` templates are committed.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

KNOWN_ENVS = ("dev", "test", "prod")
#: Default when ``test_env`` is not provided. Never ``prod`` (avoid accidents).
DEFAULT_ENV = "test"


def resolve_test_env(value: str | None = None) -> str:
    """Normalise ``test_env`` to an env name. Warns (never raises) on unknown."""
    raw = value if value is not None else os.environ.get("test_env", "")
    env = raw.strip().lower() or DEFAULT_ENV
    if env not in KNOWN_ENVS:
        print(
            f"[env] test_env={env!r} is not one of {'/'.join(KNOWN_ENVS)}; "
            f"will load environments/.env.{env} if it exists."
        )
    return env


def env_file_path(env: str | None = None) -> Path:
    """Absolute path to the env file for the selected (or given) env."""
    env = env or resolve_test_env()
    return Path.cwd() / "environments" / f".env.{env}"


def load_env_file() -> str:
    """Load ``environments/.env.<test_env>`` into ``os.environ`` (override).

    Returns the resolved env name. A missing file only warns, so mock-only
    suites (api/grpc) still run without an env file. Also loads ``.env.jira``
    (without overriding the env-specific file) for the bug reporter.
    """
    env = resolve_test_env()
    path = env_file_path(env)
    if path.exists():
        load_dotenv(path, override=True)
    else:
        print(
            f"[env] {path} not found — copy environments/.env.{env}.example to it "
            f"(or set test_env to dev/test/prod). Continuing with current os.environ."
        )

    jira = Path.cwd() / "environments" / ".env.jira"
    if jira.exists():
        load_dotenv(jira, override=False)
    return env

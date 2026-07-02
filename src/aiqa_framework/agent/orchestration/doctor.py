"""Health-check the install (port of orchestration/doctor.ts)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from aiqa_framework.shared.config.env import env_file_path, resolve_test_env

Check = tuple[str, bool, str]


def run_checks() -> list[Check]:
    checks: list[Check] = []
    checks.append(("python>=3.11", sys.version_info >= (3, 11), sys.version.split()[0]))

    for mod in ("playwright", "httpx", "pydantic", "grpc", "typer", "fastapi", "respx"):
        try:
            importlib.import_module(mod)
            checks.append((f"dep:{mod}", True, "ok"))
        except Exception as e:  # noqa: BLE001
            checks.append((f"dep:{mod}", False, str(e)[:60]))

    env = resolve_test_env()
    path = env_file_path(env)
    checks.append((f"env-file:{env}", path.exists(), str(path)))

    auth = Path("src/aiqa_framework/core/auth.py")
    configured = auth.exists() and "raise NotImplementedError" not in auth.read_text()
    checks.append(
        ("auth-setup", configured, "implement authenticate()" if not configured else "ok")
    )

    grpc_gen = Path("src/aiqa_framework/grpc/generated/game_pb2.py")
    checks.append(
        ("grpc-stubs", grpc_gen.exists(), "run `poe proto-gen`" if not grpc_gen.exists() else "ok")
    )

    return checks

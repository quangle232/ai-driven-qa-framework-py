"""Per-module memory store — resolves ``docs/ai/<module>/`` artifacts.

Each testing surface (``ui`` / ``api`` / ``performance`` / ``mobile``) keeps its
own AI memory under ``docs/ai/<module>/`` so the qa-agent reads/writes context per
surface instead of one flat file. The ``memory`` MCP server and the qa-agent skill
(references/tracking-files.md) use these paths.
"""

from __future__ import annotations

from pathlib import Path

MODULES = ("ui", "api", "performance", "mobile")


def repo_root(start: Path | None = None) -> Path:
    """Nearest ancestor containing pyproject.toml (falls back to cwd)."""
    base = (start or Path(__file__)).resolve()
    for parent in [base, *base.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    return Path.cwd()


def module_memory_dir(module: str, root: Path | None = None) -> Path:
    """``docs/ai/<module>/`` (created if missing)."""
    if module not in MODULES:
        raise ValueError(f"unknown module {module!r}; expected one of {MODULES}")
    path = (root or repo_root()) / "docs" / "ai" / module
    path.mkdir(parents=True, exist_ok=True)
    return path


def memory_file(module: str, name: str = "memory.md", root: Path | None = None) -> Path:
    """A named memory file under a module (e.g. memory.md, navigation.md)."""
    return module_memory_dir(module, root) / name


def testcases_dir(module: str, root: Path | None = None) -> Path:
    """``docs/ai/<module>/testcases/`` for JSON/Excel artifacts (created)."""
    path = module_memory_dir(module, root) / "testcases"
    path.mkdir(parents=True, exist_ok=True)
    return path

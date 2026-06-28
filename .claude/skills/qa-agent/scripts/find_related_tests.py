#!/usr/bin/env python3
"""find_related_tests.py — Python port of find-related-tests.js.

Detect existing test files that carry a given marker (== Jira label), so the
qa-agent skill (Phase 2) can run new tests together with related existing ones.

Specs reference markers through the TAGS class (e.g. @tags(TAGS.API)), not the
literal "api" string. This script reads src/aiqa_framework/config/tags.py,
resolves the marker value to its TAGS key, then scans tests/ for that key.

Usage:
  python3 .claude/skills/qa-agent/scripts/find_related_tests.py api
  python3 .claude/skills/qa-agent/scripts/find_related_tests.py API
  python3 .claude/skills/qa-agent/scripts/find_related_tests.py @service-request

Exit codes: 0 = matches found, 1 = no matches, 2 = usage / parse error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TAGS_REL = Path("src") / "aiqa_framework" / "config" / "tags.py"


def find_repo_root(start: Path) -> Path | None:
    """Walk up from `start` until a dir holding pyproject.toml + the tags file."""
    for d in (start, *start.parents):
        if (d / "pyproject.toml").is_file() and (d / TAGS_REL).is_file():
            return d
    return None


def parse_tags_map(tags_file: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Parse `KEY = pytest.mark.value` lines into {key->value, value->key}."""
    src = tags_file.read_text(encoding="utf-8")
    key_to_value: dict[str, str] = {}
    value_to_key: dict[str, str] = {}
    for m in re.finditer(r"(\w+)\s*=\s*pytest\.mark\.(\w+)", src):
        key, value = m.group(1), m.group(2)
        key_to_value[key] = value
        value_to_key[value] = key
    return key_to_value, value_to_key


def resolve_tag(
    arg: str, key_to_value: dict[str, str], value_to_key: dict[str, str]
) -> tuple[str, str] | None:
    """Resolve a TAGS key, a marker value, or a Jira label (@foo / foo-bar)."""
    if arg in key_to_value:
        return arg, key_to_value[arg]
    norm = arg.lstrip("@").replace("-", "_")  # Jira label -> pytest marker name
    if norm in value_to_key:
        return value_to_key[norm], norm
    if norm.upper() in key_to_value:
        return norm.upper(), key_to_value[norm.upper()]
    return None


def walk_specs(tests_dir: Path) -> list[Path]:
    """Every test_*.py file under tests/ (pytest naming), __pycache__ excluded."""
    return sorted(
        p for p in tests_dir.rglob("test_*.py") if "__pycache__" not in p.parts
    )


def extract_titles(src: str) -> list[str]:
    """Test function names — the Python analogue of the TS test() titles."""
    return re.findall(r"def\s+(test_\w+)\s*\(", src)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Usage: find_related_tests.py <marker>   (e.g. api)", file=sys.stderr)
        return 2

    arg = args[0]
    repo_root = find_repo_root(Path(__file__).resolve()) or find_repo_root(
        Path.cwd().resolve()
    )
    if repo_root is None:
        print(
            "Error: could not locate the repo root "
            "(src/aiqa_framework/config/tags.py not found).",
            file=sys.stderr,
        )
        return 2

    key_to_value, value_to_key = parse_tags_map(repo_root / TAGS_REL)
    resolved = resolve_tag(arg, key_to_value, value_to_key)
    if resolved is None:
        print(f'Error: "{arg}" is not a known marker.', file=sys.stderr)
        print(f"Known markers: {', '.join(sorted(value_to_key))}", file=sys.stderr)
        return 2
    key, value = resolved

    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        print("Error: tests/ directory not found.", file=sys.stderr)
        return 2

    specs = walk_specs(tests_dir)
    needle = re.compile(rf"TAGS\.{key}\b")
    matches: list[tuple[Path, list[str]]] = []
    for spec in specs:
        src = spec.read_text(encoding="utf-8")
        if needle.search(src):
            matches.append((spec.relative_to(repo_root), extract_titles(src)))

    print(f"Marker: {value}  (TAGS.{key})")
    print(f"Scanned {len(specs)} test file(s) under tests/.")

    if not matches:
        print("No existing tests carry this marker.")
        return 1

    print(f"\n{len(matches)} related test file(s) (file-level match):\n")
    for path, titles in matches:
        print(f"  {path}")
        for title in titles:
            print(f"    - {title}")
    print("\nRun the related tests with:")
    print(f"  uv run pytest -m {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

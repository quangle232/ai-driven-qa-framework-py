#!/usr/bin/env python3
"""json_quality_checks.py — deterministic QA JSON enrichment (STEP 7).

Applies auto priority scoring (references/priority-scoring.md) and duplicate
detection (references/duplicate-detection.md) to a canonical QA JSON
(references/json-contract.md). Stdlib only.

Both passes only FILL EMPTY fields — they never overwrite a human-set `priority`
or `duplicateStatus`, so re-running after edits is safe.

Usage:
  python3 .claude/skills/qa-agent/scripts/json_quality_checks.py --json <path>
  python3 .claude/skills/qa-agent/scripts/json_quality_checks.py --json <path> --write

Exit codes: 0 = ok, 2 = usage / parse error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

P0_KEYWORDS = (
    "login", "auth", "authorization", "password", "payment", "checkout",
    "contract", "sign", "delete", "remove", "pay", "approve", "publish",
    "security", "permission", "irreversible", "integrity", "destructive",
)
P1_KEYWORDS = (
    "validation", "invalid", "error", "required", "negative", "edit",
    "update", "search", "filter", "create", "submit", "boundary",
)

NEAR_DUP_THRESHOLD = 0.85


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _case_text(tc: dict[str, Any]) -> str:
    keys = ("summaryPrecondition", "testDescription", "feature", "subFeature")
    return " ".join(_norm(tc.get(k)) for k in keys)


def score_priority(tc: dict[str, Any]) -> tuple[str, str]:
    text = _case_text(tc)
    hits = sorted({k for k in P0_KEYWORDS if k in text})
    if hits:
        return "P0", f"core/destructive keyword(s): {', '.join(hits)}"
    hits = sorted({k for k in P1_KEYWORDS if k in text})
    if hits:
        return "P1", f"validation/alternate-flow keyword(s): {', '.join(hits)}"
    return "P2", "no high-risk signal; default lower priority"


def _signature(tc: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _norm(tc.get("feature")),
        _norm(tc.get("subFeature")),
        _norm(tc.get("summaryPrecondition")),
        _norm(tc.get("testDescription")),
    )


def _tokens(tc: dict[str, Any]) -> set[str]:
    text = _norm(tc.get("summaryPrecondition")) + " " + _norm(tc.get("testDescription"))
    return set(re.findall(r"[a-z0-9]+", text))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def detect_duplicates(cases: list[dict[str, Any]]) -> dict[int, tuple[str, str, str]]:
    """Map case index -> (duplicateStatus, duplicateOf, duplicateReason)."""
    findings: dict[int, tuple[str, str, str]] = {}
    sigs = [_signature(tc) for tc in cases]
    toks = [_tokens(tc) for tc in cases]
    for j in range(len(cases)):
        for i in range(j):
            if findings.get(i, ("",))[0] == "duplicate":
                continue
            other = cases[i].get("tcId", f"#{i}")
            if sigs[i] == sigs[j]:
                reason = f"same feature/precondition/description as {other}"
                findings[j] = ("duplicate", other, reason)
                break
            if _jaccard(toks[i], toks[j]) >= NEAR_DUP_THRESHOLD:
                reason = f"very similar wording to {other}; verify added coverage"
                findings[j] = ("possible-overlap", other, reason)
                break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich QA JSON with priority + duplicate flags.")
    parser.add_argument("--json", required=True, help="Path to the canonical QA JSON.")
    parser.add_argument("--write", action="store_true", help="Write enrichment back in place.")
    args = parser.parse_args()

    path = Path(args.json)
    if not path.is_file():
        print(f"Error: {path} not found.", file=sys.stderr)
        return 2
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        return 2

    cases = data.get("testCases", [])
    priority_filled = 0
    for tc in cases:
        if not tc.get("priority"):
            tc["priority"], tc["priorityReason"] = score_priority(tc)
            priority_filled += 1

    dup_flagged = 0
    for idx, (status, of, reason) in detect_duplicates(cases).items():
        if not cases[idx].get("duplicateStatus"):
            cases[idx]["duplicateStatus"] = status
            cases[idx]["duplicateOf"] = of
            cases[idx]["duplicateReason"] = reason
            dup_flagged += 1

    print(f"Test cases:        {len(cases)}")
    print(f"Priority filled:   {priority_filled}")
    print(f"Duplicates flagged: {dup_flagged}")
    for tc in cases:
        if tc.get("duplicateStatus"):
            tcid = tc.get("tcId", "?")
            print(f"  - {tcid}: {tc['duplicateStatus']} (of {tc.get('duplicateOf', '')})")

    if args.write:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"✅ Wrote enriched JSON -> {path}")
    else:
        print("(report only — pass --write to persist)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

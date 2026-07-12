#!/usr/bin/env python3
"""attach_file_to_jira.py — upload a file as a Jira issue attachment.

The Atlassian MCP connector has NO attachment-upload tool (issues and pages
only), so the qa-agent uses this script for the "attach the Excel export /
Allure report to the parent story" step (test-management.md, excel target).

Usage:
  python3 .claude/skills/qa-agent/scripts/attach_file_to_jira.py \
    --issue EAST-123 \
    --file  test-output/qa/TestCases_login.xlsx

Credentials: JIRA_URL / JIRA_EMAIL / JIRA_TOKEN env vars, falling back to
environments/.env.jira (same contract as shared/reporting/bug_reporter.py).

Exit codes: 0 = attached, 1 = credentials missing, 2 = usage / file missing,
3 = Jira API error. Stdlib only (urllib multipart).
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

_MIME = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".html": "text/html",
    ".json": "application/json",
    ".png": "image/png",
    ".pdf": "application/pdf",
}


def find_repo_root(start: Path) -> Path:
    for d in (start, *start.parents):
        if (d / "pyproject.toml").is_file():
            return d
    return Path.cwd()


def load_config() -> dict[str, str]:
    import os

    cfg = {k: os.environ.get(k, "") for k in ("JIRA_URL", "JIRA_EMAIL", "JIRA_TOKEN")}
    env_file = find_repo_root(Path(__file__).resolve()) / "environments" / ".env.jira"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z_]+)\s*=\s*(.*?)\s*$", line)
            if m and not cfg.get(m.group(1)):
                cfg[m.group(1)] = m.group(2).strip("\"'")
    cfg["JIRA_URL"] = cfg["JIRA_URL"].rstrip("/")
    return cfg


def multipart_body(file_path: Path) -> tuple[bytes, str]:
    boundary = f"----aiqa{uuid.uuid4().hex}"
    mime = _MIME.get(file_path.suffix.lower(), "application/octet-stream")
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + file_path.read_bytes() + tail, boundary


def main() -> int:
    parser = argparse.ArgumentParser(description="Attach a file to a Jira issue.")
    parser.add_argument("--issue", required=True, help="Issue key, e.g. EAST-123")
    parser.add_argument("--file", required=True, help="Path of the file to attach")
    args = parser.parse_args()

    file_path = Path(args.file).resolve()
    if not file_path.is_file():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        return 2

    cfg = load_config()
    if not (cfg["JIRA_URL"] and cfg["JIRA_EMAIL"] and cfg["JIRA_TOKEN"]):
        print(
            "Jira credentials missing — set JIRA_URL/JIRA_EMAIL/JIRA_TOKEN env vars or fill "
            "environments/.env.jira (copy environments/.env.jira.example). Nothing was uploaded.",
            file=sys.stderr,
        )
        return 1

    body, boundary = multipart_body(file_path)
    token = base64.b64encode(f"{cfg['JIRA_EMAIL']}:{cfg['JIRA_TOKEN']}".encode()).decode()
    request = urllib.request.Request(
        f"{cfg['JIRA_URL']}/rest/api/3/issue/{args.issue}/attachments",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            # Required by Jira to bypass XSRF protection on attachment uploads.
            "X-Atlassian-Token": "no-check",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            created = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:500]
        print(f"Jira attachment upload failed: HTTP {err.code} — {detail}", file=sys.stderr)
        return 3
    except Exception as err:  # noqa: BLE001
        print(f"Unexpected error: {err}", file=sys.stderr)
        return 3

    for attachment in created:
        print(
            f"Attached: {attachment['filename']} -> {cfg['JIRA_URL']}/browse/{args.issue} "
            f"(attachment id {attachment['id']})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

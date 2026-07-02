"""Failure -> Jira Bug auto-reporter (port of helper/jira-bug-reporter.ts).

If an OPEN bug with the same summary already exists in the project, reuse it;
otherwise create a new Bug and link it to the parent user story. Returns
``ReportBugResult`` or ``None`` when skipped (no creds / API error / already
reported this run). NEVER raises — bug reporting is a side channel and must not
break a test run.

Credentials come from env vars ``JIRA_URL`` / ``JIRA_EMAIL`` / ``JIRA_TOKEN`` /
``JIRA_PROJECT`` (also loaded from ``environments/.env.jira`` by config.env).
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass

import httpx

from aiqa_framework.shared.config.settings import get_settings

# In-process dedupe: at most one bug per failing test within a run (covers retries).
_reported: set[str] = set()

_LUCENE_SPECIAL = re.compile(r"[+\-&|!(){}\[\]^\"~*?:\\/]")


@dataclass
class ReportBugResult:
    key: str
    created: bool  # True = new bug; False = existing OPEN bug reused


def _adf_doc(text: str) -> dict:
    """Minimal Atlassian Document Format wrapper around plain text."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": ([{"type": "text", "text": line}] if line else [])}
            for line in text.split("\n")
        ],
    }


def _find_open_bug_by_summary(
    client: httpx.Client, project: str, issue_type: str, summary: str
) -> str | None:
    """First OPEN bug whose summary EXACTLY equals ``summary`` (JQL ~ is fuzzy).

    Uses Jira Cloud's POST /rest/api/3/search/jql (the legacy /search was removed
    in 2025). Client-side exact match avoids false-merging unrelated bugs.
    """
    term = _LUCENE_SPECIAL.sub(" ", summary)
    term = re.sub(r"\s+", " ", term).strip()
    if not term:
        return None

    jql = (
        f'project = "{project}" AND issuetype = "{issue_type}" '
        f'AND summary ~ "{term}" AND statusCategory != Done ORDER BY created DESC'
    )
    res = client.post(
        "/rest/api/3/search/jql",
        json={"jql": jql, "fields": ["summary", "status"], "maxResults": 20},
    )
    res.raise_for_status()
    for issue in res.json().get("issues", []):
        if issue.get("fields", {}).get("summary") == summary:
            return issue["key"]
    return None


def report_bug_to_jira(
    parent_story_key: str,
    summary: str,
    description: str,
    bug_issue_type: str = "Bug",
) -> ReportBugResult | None:
    dedup_key = f"{parent_story_key}::{summary}"
    if dedup_key in _reported:
        return None
    _reported.add(dedup_key)

    s = get_settings()
    base = (s.jira_url or "").rstrip("/")
    if not base or not s.jira_email or not s.jira_token:
        print(
            "[jira-bug] credentials missing — set JIRA_URL/JIRA_EMAIL/JIRA_TOKEN "
            "(or environments/.env.jira). Skipping bug creation."
        )
        return None

    project = s.jira_project or "PROJ"
    token = base64.b64encode(f"{s.jira_email}:{s.jira_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    with httpx.Client(base_url=base, headers=headers, timeout=30) as client:
        # 1) Reuse an existing OPEN bug (a Done bug means the failure is a regression).
        try:
            existing = _find_open_bug_by_summary(client, project, bug_issue_type, summary)
            if existing:
                print(f'[jira-bug] reusing existing open bug {existing} for "{summary}"')
                return ReportBugResult(key=existing, created=False)
        except Exception as e:  # noqa: BLE001 - search failure must not block creation
            print(f"[jira-bug] search failed (will create instead): {e}")

        # 2) Create a fresh bug.
        try:
            create = client.post(
                "/rest/api/3/issue",
                json={
                    "fields": {
                        "project": {"key": project},
                        "issuetype": {"name": bug_issue_type},
                        "summary": summary,
                        "description": _adf_doc(description),
                    }
                },
            )
            create.raise_for_status()
            bug_key = create.json()["key"]
        except Exception as e:  # noqa: BLE001
            print(f'[jira-bug] could not create bug for "{summary}": {e}')
            return None

        # 3) Link to the parent story ("Relates" is universally available).
        try:
            client.post(
                "/rest/api/3/issueLink",
                json={
                    "type": {"name": "Relates"},
                    "inwardIssue": {"key": bug_key},
                    "outwardIssue": {"key": parent_story_key},
                },
            ).raise_for_status()
        except Exception as e:  # noqa: BLE001
            print(f"[jira-bug] created {bug_key} but linking to {parent_story_key} failed: {e}")

    return ReportBugResult(key=bug_key, created=True)

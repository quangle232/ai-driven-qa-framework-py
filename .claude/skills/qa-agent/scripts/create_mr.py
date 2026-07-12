#!/usr/bin/env python3
"""create_mr.py — open a merge/pull request for a pushed branch, multi-provider
(the ship step: generated code reaches the team via branch + MR/PR).

Providers: **gitlab** · **github** (incl. Enterprise) · **bitbucket** (Cloud) ·
**azure** (DevOps Repos) · **gitea** (also Forgejo/Codeberg). The provider and
the repo coordinates are AUTO-DETECTED from the `origin` remote URL; override
with `--provider` / the `GIT_PROVIDER` env var (and `--repo`, `--base-url` when
the remote is unusual).

Usage:
  python3 .claude/skills/qa-agent/scripts/create_mr.py \
    --source test/EAST-123-login \
    --title  "EAST-123: Login — qa-agent generated tests" \
    [--target master] [--provider gitlab|github|bitbucket|azure|gitea] \
    [--description-file test-output/ai/mr-description.md] [--dry-run]

Branch naming (team rule): test/<STORY-KEY>-<feature-slug> for story-driven
runs; test/manual-<feature-slug>-<YYYYMMDD> for gen-auto-test runs without a
story.

Credentials (env vars, falling back to environments/.env.git, then the legacy
environments/.env.gitlab):
  generic   GIT_PROVIDER, GIT_TOKEN
  gitlab    GITLAB_TOKEN   (PRIVATE-TOKEN)
  github    GITHUB_TOKEN   (PAT / fine-grained)
  bitbucket BITBUCKET_USER + BITBUCKET_APP_PASSWORD (or BITBUCKET_TOKEN bearer)
  azure     AZURE_DEVOPS_PAT
  gitea     GITEA_TOKEN

Exit codes: 0 = MR/PR created (URL printed) or dry-run OK, 1 = config missing,
2 = usage / detection error, 3 = provider API error. Stdlib only.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for d in (start, *start.parents):
        if (d / "pyproject.toml").is_file():
            return d
    return Path.cwd()


def load_env_files() -> dict[str, str]:
    """environments/.env.git first, then the legacy .env.gitlab (env vars win)."""
    import os

    values: dict[str, str] = {}
    root = find_repo_root(Path(__file__).resolve())
    for name in (".env.git", ".env.gitlab"):
        f = root / "environments" / name
        if f.is_file():
            for line in f.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\s*([A-Z_]+)\s*=\s*(.*?)\s*$", line)
                if m and m.group(1) not in values:
                    values[m.group(1)] = m.group(2).strip("\"'")
    for key in list(values):
        if os.environ.get(key):
            values[key] = os.environ[key]
    for key, val in os.environ.items():
        if key not in values and key.isupper():
            values[key] = val
    return values


def origin_url() -> str:
    try:
        return subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def parse_remote(url: str) -> dict[str, str]:
    """Normalize an ssh/https remote into {host, path} (path without .git)."""
    if not url:
        return {}
    # Azure ssh: git@ssh.dev.azure.com:v3/org/project/repo
    m = re.match(r"^git@ssh\.dev\.azure\.com:v3/(.+)$", url)
    if m:
        return {"host": "dev.azure.com", "path": m.group(1)}
    # scp-like ssh: git@host:owner/repo(.git)  (also host aliases like github-quangle232)
    m = re.match(r"^[\w.-]+@([\w.-]+):(.+?)(?:\.git)?/?$", url)
    if m:
        return {"host": m.group(1), "path": m.group(2)}
    # ssh:// or https://
    m = re.match(r"^(?:ssh|https?)://(?:[^@/]+@)?([\w.-]+)(?::\d+)?/(.+?)(?:\.git)?/?$", url)
    if m:
        return {"host": m.group(1), "path": m.group(2)}
    return {}


def detect_provider(host: str) -> str:
    h = host.lower()
    if "github" in h:
        return "github"
    if "gitlab" in h:
        return "gitlab"
    if "bitbucket" in h:
        return "bitbucket"
    if "dev.azure.com" in h or "visualstudio.com" in h:
        return "azure"
    if "gitea" in h or "forgejo" in h or "codeberg" in h:
        return "gitea"
    return ""


#: Cloud host per provider — used when the remote host is an SSH-config alias
#: (no dot, e.g. `github-work`), which is not a resolvable API hostname.
_DEFAULT_HOSTS = {
    "github": "github.com",
    "gitlab": "gitlab.com",
    "bitbucket": "bitbucket.org",
    "azure": "dev.azure.com",
}


def normalize_host(provider: str, host: str) -> str:
    if host and "." not in host:
        return _DEFAULT_HOSTS.get(provider, host)
    return host


def build_request(
    provider: str,
    host: str,
    path: str,
    cfg: dict[str, str],
    source: str,
    target: str,
    title: str,
    description: str,
    base_url: str,
) -> tuple[str, dict[str, str], dict]:
    """Return (url, headers, body) for the provider's create-MR call."""
    token = cfg.get("GIT_TOKEN", "")

    if provider == "gitlab":
        token = cfg.get("GITLAB_TOKEN") or token
        if not token:
            raise PermissionError("GITLAB_TOKEN (or GIT_TOKEN) is missing")
        base = base_url or cfg.get("GITLAB_URL") or f"https://{host}"
        project = urllib.parse.quote(path, safe="")
        return (
            f"{base.rstrip('/')}/api/v4/projects/{project}/merge_requests",
            {"PRIVATE-TOKEN": token},
            {
                "source_branch": source,
                "target_branch": target,
                "title": title,
                "description": description,
                "remove_source_branch": True,
            },
        )

    if provider == "github":
        token = cfg.get("GITHUB_TOKEN") or token
        if not token:
            raise PermissionError("GITHUB_TOKEN (or GIT_TOKEN) is missing")
        api = base_url or (
            "https://api.github.com" if host == "github.com" else f"https://{host}/api/v3"
        )
        return (
            f"{api.rstrip('/')}/repos/{path}/pulls",
            {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            {"title": title, "head": source, "base": target, "body": description},
        )

    if provider == "bitbucket":
        user = cfg.get("BITBUCKET_USER", "")
        app_pass = cfg.get("BITBUCKET_APP_PASSWORD", "")
        bearer = cfg.get("BITBUCKET_TOKEN") or token
        if user and app_pass:
            auth = "Basic " + base64.b64encode(f"{user}:{app_pass}".encode()).decode()
        elif bearer:
            auth = f"Bearer {bearer}"
        else:
            raise PermissionError(
                "BITBUCKET_USER+BITBUCKET_APP_PASSWORD (or BITBUCKET_TOKEN) missing"
            )
        api = base_url or "https://api.bitbucket.org/2.0"
        return (
            f"{api.rstrip('/')}/repositories/{path}/pullrequests",
            {"Authorization": auth},
            {
                "title": title,
                "description": description,
                "source": {"branch": {"name": source}},
                "destination": {"branch": {"name": target}},
                "close_source_branch": True,
            },
        )

    if provider == "azure":
        pat = cfg.get("AZURE_DEVOPS_PAT") or token
        if not pat:
            raise PermissionError("AZURE_DEVOPS_PAT (or GIT_TOKEN) is missing")
        parts = [p for p in path.split("/") if p != "_git"]
        if len(parts) < 3:
            raise ValueError(f"cannot derive org/project/repo from Azure path '{path}'")
        org, project, repo = parts[0], parts[1], parts[-1]
        auth = "Basic " + base64.b64encode(f":{pat}".encode()).decode()
        api = base_url or "https://dev.azure.com"
        return (
            f"{api.rstrip('/')}/{org}/{urllib.parse.quote(project)}/_apis/git/repositories/"
            f"{urllib.parse.quote(repo)}/pullrequests?api-version=7.1",
            {"Authorization": auth},
            {
                "sourceRefName": f"refs/heads/{source}",
                "targetRefName": f"refs/heads/{target}",
                "title": title,
                "description": description,
            },
        )

    if provider == "gitea":
        token = cfg.get("GITEA_TOKEN") or token
        if not token:
            raise PermissionError("GITEA_TOKEN (or GIT_TOKEN) is missing")
        base = base_url or f"https://{host}"
        return (
            f"{base.rstrip('/')}/api/v1/repos/{path}/pulls",
            {"Authorization": f"token {token}"},
            {"title": title, "head": source, "base": target, "body": description},
        )

    raise ValueError(f"unknown provider '{provider}'")


def extract_mr_url(provider: str, response: dict) -> str:
    if provider == "gitlab":
        return response.get("web_url", "")
    if provider in ("github", "gitea"):
        return response.get("html_url", "")
    if provider == "bitbucket":
        return response.get("links", {}).get("html", {}).get("href", "")
    if provider == "azure":
        repo = response.get("repository", {})
        web = repo.get("webUrl", "")
        pr_id = response.get("pullRequestId", "")
        return f"{web}/pullrequest/{pr_id}" if web and pr_id else str(response.get("url", ""))
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Open an MR/PR for a pushed branch.")
    parser.add_argument("--source", required=True, help="Source branch (already pushed)")
    parser.add_argument("--title", required=True)
    parser.add_argument("--target", default="master")
    parser.add_argument("--provider", default="", help="gitlab|github|bitbucket|azure|gitea")
    parser.add_argument("--repo", default="", help="Override owner/repo (or group/sub/repo)")
    parser.add_argument("--base-url", default="", help="Override the API/base URL")
    parser.add_argument("--description-file", default="")
    parser.add_argument("--dry-run", action="store_true", help="Print the request, send nothing")
    args = parser.parse_args()

    cfg = load_env_files()
    remote = parse_remote(origin_url())
    host = remote.get("host", "")
    path = args.repo or remote.get("path", "")
    provider = (args.provider or cfg.get("GIT_PROVIDER", "") or detect_provider(host)).lower()
    host = normalize_host(provider, host)

    if not provider:
        print(
            f"Could not detect the provider from origin '{origin_url() or '<none>'}' — "
            "pass --provider or set GIT_PROVIDER (gitlab|github|bitbucket|azure|gitea).",
            file=sys.stderr,
        )
        return 2
    if not path:
        print(
            "Could not derive the repo path from the origin remote — pass --repo owner/repo. "
            "If the repo has no remote, report 'branch+MR skipped — repo not bootstrapped'.",
            file=sys.stderr,
        )
        return 2

    description_path = Path(args.description_file) if args.description_file else None
    description = (
        description_path.read_text(encoding="utf-8")
        if description_path and description_path.is_file()
        else "Generated by the qa-agent skill. See docs/ai/<module>/memory.md for the run context."
    )

    try:
        url, headers, body = build_request(
            provider, host, path, cfg, args.source, args.target, args.title, description,
            args.base_url,
        )
    except PermissionError as err:
        print(f"{provider}: {err} — set it in env or environments/.env.git. No MR created.",
              file=sys.stderr)
        return 1
    except ValueError as err:
        print(f"{provider}: {err}", file=sys.stderr)
        return 2

    if args.dry_run:
        safe_headers = {k: ("***" if k.lower() != "accept" else v) for k, v in headers.items()}
        print(f"[dry-run] provider={provider} host={host} repo={path}")
        print(f"[dry-run] POST {url}")
        print(f"[dry-run] headers: {json.dumps(safe_headers)}")
        print(f"[dry-run] body: {json.dumps(body, indent=2)}")
        return 0

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        method="POST",
        headers={**headers, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            created = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:500]
        print(f"{provider} MR/PR creation failed: HTTP {err.code} — {detail}", file=sys.stderr)
        return 3
    except Exception as err:  # noqa: BLE001
        print(f"Unexpected error: {err}", file=sys.stderr)
        return 3

    mr_url = extract_mr_url(provider, created)
    print(f"MR created: {mr_url or '<no url in response>'} ({args.source} -> {args.target})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

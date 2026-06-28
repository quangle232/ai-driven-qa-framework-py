#!/usr/bin/env python3
"""trigger_jenkins.py — Python port of trigger-jenkins.js.

Trigger the Jenkins regression job for a marker expression and wait for the
result. qa-agent Phase 2/6 uses this to run tests on CI by Jira label
(marker == label). Stdlib only (urllib) — runs with `python3` or `uv run python`.

Config — env vars, or environments/.env.jenkins (gitignored; env vars win).
NEVER hard-code credentials in this file:
  JENKINS_URL    e.g. http://localhost:8080
  JENKINS_USER   Jenkins username
  JENKINS_TOKEN  Jenkins API token (preferred) or password
  JENKINS_JOB    job name (default: aiqa-regression)

Usage:
  trigger_jenkins.py <markers>
  trigger_jenkins.py "api or smoke" --env=test --reruns=2
  trigger_jenkins.py api --check            (auth/connectivity check only)
  trigger_jenkins.py api --no-wait          (trigger, hand back build URL, exit)
  trigger_jenkins.py --status=<build-url>   (one-shot status check)

Exit codes: 0 = build SUCCESS / check ok / no-wait fired, 1 = build not SUCCESS,
            2 = config / usage / trigger error, 3 = build IN_PROGRESS (--status).

Matches ci/jenkins/Jenkinsfile params: ENVIRONMENT, MARKERS, RERUNS.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for d in (start, *start.parents):
        if (d / "pyproject.toml").is_file():
            return d
    return Path.cwd()


def load_config() -> dict[str, str | None]:
    """Env vars win; fall back to environments/.env.jenkins."""
    cfg: dict[str, str | None] = {
        k: os.environ.get(k)
        for k in ("JENKINS_URL", "JENKINS_USER", "JENKINS_TOKEN", "JENKINS_JOB")
    }
    env_file = find_repo_root(Path(__file__).resolve()) / "environments" / ".env.jenkins"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z_]+)\s*=\s*(.*?)\s*$", line)
            if m and not cfg.get(m.group(1)):
                cfg[m.group(1)] = m.group(2).strip("\"'")
    return cfg


def http(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
) -> tuple[int, Any, bytes]:
    """Return (status, headers, body); never raise on a non-2xx HTTP status."""
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        resp = urllib.request.urlopen(req, timeout=30)  # noqa: S310 (trusted Jenkins URL)
        return resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()


def main() -> int:
    # Parse args — positional[0] is the marker expression; rest are --flag[=value].
    positional: list[str] = []
    flags: dict[str, str | bool] = {}
    for a in sys.argv[1:]:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            flags[k] = v if v else True
        else:
            positional.append(a)

    markers = positional[0] if positional else None
    if not markers and not flags.get("status") and not flags.get("check"):
        print(
            "Usage:\n"
            "  trigger_jenkins.py <markers> [--env=] [--reruns=] [--no-wait]\n"
            "  trigger_jenkins.py --check                 (auth/connectivity only)\n"
            "  trigger_jenkins.py --status=<build-url>    (one-shot status check)",
            file=sys.stderr,
        )
        return 2

    cfg = load_config()
    job = cfg.get("JENKINS_JOB") or "aiqa-regression"
    if not (cfg.get("JENKINS_URL") and cfg.get("JENKINS_USER") and cfg.get("JENKINS_TOKEN")):
        print(
            "Missing JENKINS_URL / JENKINS_USER / JENKINS_TOKEN "
            "(set env vars or environments/.env.jenkins).",
            file=sys.stderr,
        )
        return 2

    base = cfg["JENKINS_URL"].rstrip("/")  # type: ignore[union-attr]
    token = base64.b64encode(
        f"{cfg['JENKINS_USER']}:{cfg['JENKINS_TOKEN']}".encode()
    ).decode()
    headers = {"Authorization": f"Basic {token}"}

    def jget(url: str) -> Any:
        status, _, body = http(url, headers=headers)
        if status != 200:
            raise RuntimeError(f"GET {url} -> HTTP {status}")
        return json.loads(body.decode("utf-8"))

    # --- auth / connectivity check (read-only) ---
    try:
        me = jget(f"{base}/me/api/json")
        who = me.get("id") or me.get("fullName") or cfg["JENKINS_USER"]
        print(f"✅ Jenkins reachable — authenticated as: {who}")
    except Exception as e:  # noqa: BLE001
        print(f"❌ Jenkins auth/connectivity failed: {e}", file=sys.stderr)
        print(f"   Check JENKINS_URL ({base}) and the credentials.", file=sys.stderr)
        return 2

    # --- CSRF crumb (tied to the HTTP session — send the cookie back on POST) ---
    post_headers = dict(headers)
    try:
        status, crumb_headers, body = http(f"{base}/crumbIssuer/api/json", headers=headers)
        if status == 200:
            c = json.loads(body.decode("utf-8"))
            post_headers[c["crumbRequestField"]] = c["crumb"]
            cookies = "; ".join(
                s.split(";")[0] for s in crumb_headers.get_all("Set-Cookie") or []
            )
            if cookies:
                post_headers["Cookie"] = cookies
        elif status != 404:  # 404 = crumb issuer disabled; basic auth is enough
            print(f"⚠️  crumb request returned HTTP {status} — POST may be rejected")
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  could not fetch CSRF crumb: {e}")

    if flags.get("check"):
        print("check ok")
        return 0

    # --- --status=<build-url>: one-shot status check (no trigger, no wait) ---
    if flags.get("status"):
        url = str(flags["status"]).rstrip("/") + "/"
        b = jget(f"{url}api/json")
        if b.get("result") is None:
            print(f"⏳ IN_PROGRESS  ->  {url}console")
            return 3
        ok = b["result"] == "SUCCESS"
        print(f"{'✅' if ok else '❌'} Result: {b['result']}  ->  {url}console")
        return 0 if ok else 1

    # --- trigger the parameterized build (ENVIRONMENT, MARKERS, RERUNS) ---
    body_params = urllib.parse.urlencode(
        {
            "MARKERS": markers,
            "ENVIRONMENT": flags.get("env") if isinstance(flags.get("env"), str) else "test",
            "RERUNS": flags.get("reruns") if isinstance(flags.get("reruns"), str) else "2",
        }
    ).encode()
    status, trig_headers, _ = http(
        f"{base}/job/{urllib.parse.quote(job)}/buildWithParameters",
        method="POST",
        headers=post_headers,
        data=body_params,
    )
    if status != 201:
        reason = trig_headers.get("x-error") if trig_headers else None
        hint = (
            f" — {reason}"
            if reason
            else f' — check the job name "{job}" and that the user has Build permission'
        )
        print(f"❌ Trigger failed: HTTP {status}{hint}", file=sys.stderr)
        return 2

    queue_url = trig_headers.get("Location")
    print(f"⏳ Queued (MARKERS={markers}): {queue_url}")

    # --- wait briefly for the queue item to be assigned a build number ---
    queue_deadline = 6 if flags.get("no-wait") else 60  # ~30s vs ~5min
    build_url = ""
    for _ in range(queue_deadline):
        if build_url:
            break
        time.sleep(5)
        q = jget(f"{queue_url}api/json")
        if q.get("cancelled"):
            print("❌ Build was cancelled while queued", file=sys.stderr)
            return 1
        if q.get("executable"):
            build_url = q["executable"]["url"]

    # --- --no-wait: hand back the build URL (or queue URL) and exit ---
    if flags.get("no-wait"):
        if build_url:
            print(f"\U0001f3d7️  Building (not waiting): {build_url}")
            print(f"   Check later:  trigger_jenkins.py --status={build_url}")
        else:
            print(f"⏳ Still queued: {queue_url}")
            print("   Not started in 30s — re-run --status once a build URL exists.")
        return 0

    if not build_url:
        print("❌ Build did not start within 5 minutes", file=sys.stderr)
        return 1
    print(f"\U0001f3d7️  Building: {build_url}")

    # --- poll until the build finishes ---
    result = None
    while result is None:
        time.sleep(15)
        result = jget(f"{build_url}api/json").get("result")  # None while running
    ok = result == "SUCCESS"
    print(f"{'✅' if ok else '❌'} Result: {result}  ->  {build_url}console")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

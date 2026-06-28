# Triggering the Jenkins regression job by marker

qa-agent Phase 2 / Phase 6 can run the tests on Jenkins CI instead of (or as
well as) locally. Because `marker == Jira label`, the marker composed from the
user story's label(s) is exactly the value passed to the Jenkins job's `MARKERS`
parameter (a pytest `-m` expression).

## Script
`python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py <markers>` triggers
the Jenkins job via the Jenkins Remote API (`buildWithParameters`), waits for
the build, and reports the result. Stdlib only (`urllib`) — no MCP, no project
venv required (`python3` or `uv run python` both work).

```
python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py api
python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py "api or smoke" --env=test --reruns=2
python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py api --check     # auth/connectivity only
python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py api --no-wait   # trigger, hand back build URL, exit fast
python3 .claude/skills/qa-agent/scripts/trigger_jenkins.py --status=<url>  # one-shot check of an existing build
```

Exit codes: `0` build SUCCESS / no-wait fired / check ok, `1` build not SUCCESS,
`2` config / trigger / usage error, `3` build IN_PROGRESS (from `--status`).

## Job parameters
This matches `ci/jenkins/Jenkinsfile` in the repo, which declares:
- `ENVIRONMENT` — `dev` / `test` / `prod` (loads `environments/.env.<env>`).
- `MARKERS` — the pytest `-m` expression (the script's positional arg).
- `RERUNS` — `pytest-rerunfailures` count (default `2`).

The job runs `uv run pytest -m "${MARKERS}" --reruns "${RERUNS}"` then
`uv run aiqa report-all`, and archives `test-output/**`.

## When to use which mode (long-running builds)
The default mode triggers AND polls until the build finishes. For builds that
may run **> 10 minutes** — Claude Code's background-command cap — that loop will
be killed before completion and the result lost. Use the split flow:

1. `--no-wait` — trigger and exit fast (~30s, just long enough to capture the
   build URL). Prints the URL + a ready-to-run `--status=<url>` command.
2. `--status=<build-url>` — one-shot check (no polling loop). Returns
   `SUCCESS` / `FAILURE` / `IN_PROGRESS` (exit `0` / `1` / `3`) immediately.

This decouples "fire the build" from "see the result": the agent is free between
calls, and a one-hour build does not block the session.

## Configuration
Credentials are read from env vars, or from an `environments/.env.jenkins` file.
Keep real credentials out of git — use env vars or a credential store, and
gitignore the file:

```
JENKINS_URL    e.g. http://localhost:8080
JENKINS_USER   Jenkins username
JENKINS_TOKEN  Jenkins API token (preferred) or password
JENKINS_JOB    job name (default: aiqa-regression)
```

Prefer a Jenkins **API token** (Jenkins → your user → Security → API Token) over
the account password. The user needs Build permission on the job.

## How it works
1. `GET /me/api/json` — verify connectivity + auth.
2. `GET /crumbIssuer/api/json` — fetch the CSRF crumb (skipped if disabled).
3. `POST /job/<job>/buildWithParameters` with `MARKERS`, `ENVIRONMENT`,
   `RERUNS` — returns a queue-item URL.
4. Poll the queue item until it becomes a running build.
5. Poll the build until `result` is set; exit 0 only on `SUCCESS`.

## Rules
- Triggering a build is an outward action — it runs CI and the pipeline may
  email the stakeholders. Confirm with the user before triggering a real build;
  `--check` (read-only) is always safe.
- Never hard-code Jenkins credentials in the script or any committed file.
- If Jenkins is unreachable, fall back to running pytest locally
  (`uv run pytest -m "<markers>"`) and report that CI was skipped.

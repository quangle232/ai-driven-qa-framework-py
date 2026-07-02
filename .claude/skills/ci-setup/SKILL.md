---
name: ci-setup
description: Generate or tailor CI pipelines (GitHub Actions / GitLab / Jenkins) for AIQA — install the right extras, run proto-gen, select surfaces via markers (optionally a per-surface matrix to prove isolation), publish the aiqa HTML/Allure report, and gate on lint/type/guard. Use to set up or update CI.
---

# ci-setup — CI pipelines for AIQA

Start from the samples in `ci/{github-actions,gitlab,jenkins}` and tailor them.

## Each pipeline should
1. `uv sync --extra <surfaces> --extra dev` (or `--extra all`); UI:
   `uv run playwright install --with-deps chromium`; gRPC: `uv run poe proto-gen`.
2. Quality gate: `uv run poe lint` + `uv run poe typecheck`.
3. Tests by surface/marker with reruns: `uv run pytest -m "<expr>" --reruns 2` (respect
   `ALLOW_MOBILE_NATIVE` / `ALLOW_PERF`). Mock-backed API/gRPC/GraphQL need no backend;
   UI needs the SUT.
4. Report: `uv run aiqa report-all`; archive `test-output/**` (+ Allure if used).
5. Env + secrets: set `test_env`; inject Jira/TestRail creds from the CI secret store —
   never commit them.

## Isolation matrix (recommended)
A job per extra (`ui`, `api`, `grpc`, `graphql`, `perf`) that installs only that extra and
runs only its marker — proves each module runs in isolation.

Jenkins uses the `MARKERS` param (`ci/jenkins/Jenkinsfile`); the qa-agent can trigger it
via `.claude/skills/qa-agent/scripts/trigger_jenkins.py` (see `references/jenkins-trigger.md`).

## Rules
`ci/` and `.github/` are patch-guarded — prepare the change and ask the user to apply it.
Keep the pipeline green-slice friendly (`-m "not bugs"`).

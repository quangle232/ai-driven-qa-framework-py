"""Normalize CI metadata across Jenkins, GitHub Actions, GitLab CI (port of
ci-metadata-collector.ts). Reads env vars only; falls back to ``local``."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from aiqa_framework.agent.schemas.ci_metadata import CiMetadata
from aiqa_framework.agent.utils.run_id import resolve_run_id


def _detect(env: dict[str, str]) -> str:
    explicit = (env.get("CI_PROVIDER", "")).strip().lower()
    if explicit in ("jenkins", "github-actions", "gitlab-ci", "local"):
        return explicit
    if env.get("JENKINS_URL") or (env.get("BUILD_NUMBER") and env.get("JOB_NAME")):
        return "jenkins"
    if env.get("GITHUB_ACTIONS") == "true":
        return "github-actions"
    if env.get("GITLAB_CI") == "true":
        return "gitlab-ci"
    return "local"


def collect_ci_metadata(env: dict[str, str] | None = None) -> CiMetadata:
    env = env if env is not None else dict(os.environ)
    provider = _detect(env)
    run_url = job = branch = commit = triggered_by = None

    if provider == "jenkins":
        run_url = env.get("BUILD_URL")
        job = env.get("JOB_NAME")
        branch = env.get("GIT_BRANCH") or env.get("BRANCH")
        commit = env.get("GIT_COMMIT")
        triggered_by = env.get("BUILD_USER") or env.get("CHANGE_AUTHOR")
    elif provider == "github-actions":
        if (
            env.get("GITHUB_SERVER_URL")
            and env.get("GITHUB_REPOSITORY")
            and env.get("GITHUB_RUN_ID")
        ):
            run_url = (
                f"{env['GITHUB_SERVER_URL']}/{env['GITHUB_REPOSITORY']}"
                f"/actions/runs/{env['GITHUB_RUN_ID']}"
            )
        job = env.get("GITHUB_WORKFLOW")
        branch = env.get("GITHUB_REF_NAME")
        commit = env.get("GITHUB_SHA")
        triggered_by = env.get("GITHUB_ACTOR")
    elif provider == "gitlab-ci":
        run_url = env.get("CI_PIPELINE_URL")
        job = env.get("CI_JOB_NAME")
        branch = env.get("CI_COMMIT_REF_NAME")
        commit = env.get("CI_COMMIT_SHA")
        triggered_by = env.get("GITLAB_USER_LOGIN")
    else:
        job = "local"
        triggered_by = env.get("USER") or env.get("USERNAME")

    return CiMetadata(
        provider=provider,
        run_id=resolve_run_id(env),
        run_url=run_url,
        job_name=job,
        branch=branch,
        commit=commit,
        environment=env.get("test_env") or env.get("ENVIRONMENT"),
        triggered_by=triggered_by,
        started_at=datetime.now(UTC).isoformat(),
    )

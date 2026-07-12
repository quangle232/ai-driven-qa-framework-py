# Install & migrate

## Prerequisites
- Python ≥ 3.11 and [`uv`](https://docs.astral.sh/uv/).

## Setup
```bash
uv sync --extra all --extra dev                         # runtime + dev deps (ruff, mypy, grpcio-tools, poe)
uv run playwright install --with-deps chromium
uv run poe proto-gen                        # generate gRPC stubs into src/aiqa_framework/modules/api/grpc/generated
cp environments/.env.test.example environments/.env.test
cp environments/.env.jira.example environments/.env.jira   # optional (bug drafts → Jira filing)
cp environments/.env.git.example  environments/.env.git    # optional (ship step: branch + MR)
```

## Make it yours
1. **Auth** — implement `authenticate()` in `src/aiqa_framework/modules/ui/auth.py` (your SUT sign-in;
   save `context.storage_state(path=STORAGE_STATE)`).
2. **Env** — fill `environments/.env.<env>` (URLs, creds). `test_env` picks the file.
3. **First flow** — replace `modules/ui/pages/sample_page.py` + `tests/ui/test_sample.py`.
4. **API / gRPC** — replace `modules/api/rest/models.py` + services and
   `modules/api/grpc/proto/casino/game.proto` (then `uv run poe proto-gen`).

## Verify
```bash
uv run poe lint && uv run poe typecheck
uv run poe test-api      # mock-backed, no backend
uv run poe test-grpc     # in-process mock
uv run aiqa doctor       # health check
```

## Skills (drive it with an agent)
22 reusable skills run the framework via Claude Code (`.claude/skills/`) or Codex
(`.agents/skills/`) — just ask the agent. Start with `setup`, then `user-story-test` /
`create-test-cases` → `automation-generate` → `run-tests` → `read-report`. Full catalogue
in `README.md` / `AGENTS.md`.

## CI
Copy a sample from `ci/` to its active location:
- GitHub Actions → `.github/workflows/` · GitLab → repo-root `.gitlab-ci.yml` · Jenkins → point a job at `ci/jenkins/Jenkinsfile`.
All run `uv sync` → `poe proto-gen` → `pytest` → `aiqa report-all`.

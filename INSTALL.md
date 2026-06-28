# Install & migrate

## Prerequisites
- Python ≥ 3.11 and [`uv`](https://docs.astral.sh/uv/).

## Setup
```bash
uv sync --extra dev                         # runtime + dev deps (ruff, mypy, grpcio-tools, poe)
uv run playwright install --with-deps chromium
uv run poe proto-gen                        # generate gRPC stubs into src/aiqa_framework/grpc/generated
cp environments/.env.test.example environments/.env.test
cp environments/.env.jira.example environments/.env.jira   # optional (failure → Bug)
```

## Make it yours
1. **Auth** — implement `authenticate()` in `src/aiqa_framework/core/auth.py` (your SUT sign-in;
   save `context.storage_state(path=STORAGE_STATE)`).
2. **Env** — fill `environments/.env.<env>` (URLs, creds). `test_env` picks the file.
3. **First flow** — replace `pages/sample_page.py` + `tests/ui/test_sample.py`.
4. **API / gRPC** — replace `api/models.py` + services and `grpc/proto/casino/game.proto`
   (then `uv run poe proto-gen`).

## Verify
```bash
uv run poe lint && uv run poe typecheck
uv run poe test-api      # mock-backed, no backend
uv run poe test-grpc     # in-process mock
uv run aiqa doctor       # health check
```

## CI
Copy a sample from `ci/` to its active location:
- GitHub Actions → `.github/workflows/` · GitLab → repo-root `.gitlab-ci.yml` · Jenkins → point a job at `ci/jenkins/Jenkinsfile`.
All run `uv sync` → `poe proto-gen` → `pytest` → `aiqa report-all`.

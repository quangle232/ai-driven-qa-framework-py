---
name: setup
description: Onboard a new user to AIQA — install the surfaces they need (uv extras), Playwright browsers, and gRPC stubs; create env files; guide implementing authenticate(); and run aiqa doctor until green. Use for first-time setup or "get me running".
---

# setup — onboarding

1. **Install** the surfaces they need:
   `uv sync --extra <ui|api|grpc|graphql|mobile|perf> --extra dev` (or `--extra all
   --extra dev`). UI also: `uv run playwright install --with-deps chromium`. gRPC also:
   `uv run poe proto-gen`.
2. **Env**: `cp environments/.env.test.example environments/.env.test`; help fill the
   SUT URL + non-secret config. The **user** fills passwords / tokens — never type them.
3. **Auth**: guide implementing `authenticate()` in
   `src/aiqa_framework/modules/ui/auth.py` (their sign-in; storage-state reuse). Do not
   create accounts.
4. **MCPs**: if they'll use Jira / Figma / TestRail, run the `mcp-setup` skill.
5. **Verify**: `uv run aiqa doctor` — resolve each ✗ until green. Then prove the
   toolchain with `uv run poe test-api` (mock-backed, no backend needed).

Point them at `AGENTS.md` (the guide) and the per-module `README.md` for run-in-isolation.

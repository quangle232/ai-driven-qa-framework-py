# QA Agent Memory — EXAMPLE

EXAMPLE of `docs/ai/memory.md` for a fresh project. The qa-agent reads this in
Phase 0 and updates it in Phase 7 after every generation / run.

## Generated work
| Date | User story | Feature | Marker / Jira label | Artifacts |
|------|-----------|---------|---------------------|-----------|
| 2026-06-01 | PROJ-1 | Login | `auth` | tests/ui/test_login.py; modules/ui/pages/login_page.py; testdata/login_data.py |

## Decisions
- 2026-06-01 — `LoginPage` extends `BasePage`; no separate auth fixture needed
  (the storage state carries the session for subsequent specs).
- 2026-06-01 — Added `AUTH = pytest.mark.auth` to `shared/config/tags.py` to match the
  Jira label (`tag == label`).

## Known gaps
- The error banner element has no `data-test-id` yet; relying on text — ask the
  dev to add `data-test-id="login-error"`.

## Run history
| Date | Marker | Result |
|------|--------|--------|
| 2026-06-01 | `auth` | 1 passed (12.4s) |

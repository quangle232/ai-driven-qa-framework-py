# UI module conventions (Playwright)

All Playwright material lives here. No other module imports Playwright.

## Structure
- `action_keyword.py` — the single UI keyword layer (waits, clicks, fills, getters,
  self-healing locators). New shared UI keywords go IN here.
- `base_page.py` — `BasePage` (holds `self.page` + `self.keyword`).
- `pages/` — Page Objects, one class per screen, `extends BasePage`.
- `auth.py` — one-time sign-in + storage-state reuse.
- `mobile_web/` — Playwright device emulation (reuses the web POM).
- `api_support.py` — Playwright `APIRequestContext` to seed/clean UI state (NOT API testing).
- `helpers/`, `testdata/`.

## Rules
- A spec calls Page Objects only — never `page.locator(...)` directly.
- A Page Object calls `self.keyword.*` only — never `self.page.locator(...)` directly.
- Selector priority: `data-zcqa → data-test-id → data-id → data-title` → `id` → `role+text`.
  Do not invent selectors; recommend adding `data-test-id`.
- Tag specs: `@tags(TAGS.REGRESSION, TAGS.SMOKE, TAGS.P0/1/2)` + `@jira("KEY")`
  (`from aiqa_framework.shared.config.tags import TAGS, tags, jira`).
- Test data in `modules/ui/testdata/`, not inline.
- `api_support.py` is for state setup only; functional API checks belong to `modules/api`.

## Run in isolation
```bash
uv sync --extra ui && uv run playwright install --with-deps chromium
uv run pytest tests/ui -m regression
```
Memory: `docs/ai/ui/` (memory.md · navigation.md · test-case.md · testcases/).

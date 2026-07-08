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

## Test data lifecycle (CRUD · precondition · teardown)
Tests own their data and clean up after themselves — via the **API**, not the UI.
- **CREATE is under test** — do the create through the UI (that IS the behaviour under
  test), but **capture the created id(s)** and **delete them in teardown via the API**
  (an API service or `api_support.py`), never via the UI. Leave no data behind.
- **Data is a PRECONDITION** (search / list / edit / delete / any non-create flow that
  needs existing data) — **create it via the API** (fast + deterministic; do NOT drive
  the UI to set it up), run the functionality under test, then **tear down via the API**.
- **Always track + tear down** — collect created ids / related resources and remove them
  in a `yield` fixture or `try…finally`; teardown calls the **API** for both setup (when
  a precondition) and cleanup (always). Reuse existing services
  (`modules/api/rest/services/`) or `modules/ui/api_support.py`; don't duplicate.
- **Isolate per test** (unique names / seeds) so parallel / shared-SUT runs don't collide.

Shared fixtures do the plumbing: `cleanup` (`tests/conftest.py` → `CleanupTracker`,
LIFO teardown, runs pass-or-fail) and `api` (`tests/ui/conftest.py` → `UiApiSupport`
over `page.request`). Full example: the qa-agent skill's
`examples/sample_lifecycle_spec.py`; runnable API version:
`tests/api/rest/test_sample_lifecycle.py`.

```python
def test_create_item(page, api, cleanup):        # CREATE under test → via the UI
    item = ItemPage(page)
    item.create("Widget A")
    cleanup.add(api.delete, f"/items/{item.created_id()}")   # teardown via API

def test_search_item(page, api, cleanup):        # precondition via API, action via UI
    item_id = api.post_json("/items", {"name": "Widget B"})["id"]
    cleanup.add(api.delete, f"/items/{item_id}")
    SearchPage(page).search("Widget B").expect_row(item_id)
```

## Run in isolation
```bash
uv sync --extra ui && uv run playwright install --with-deps chromium
uv run pytest tests/ui -m regression
```
Memory: `docs/ai/ui/` (memory.md · navigation.md · test-case.md · testcases/).

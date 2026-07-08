"""EXAMPLE — UI spec following the test-data lifecycle convention.

Illustration only (lives under the skill, not collected by pytest). Shows the two
CRUD modes from modules/ui/conventions.md, using the shared fixtures:
``cleanup`` (tests/conftest.py — CleanupTracker, LIFO teardown via the API) and
``api`` (tests/ui/conftest.py — UiApiSupport over ``page.request``).
"""

from __future__ import annotations

from aiqa_framework.modules.ui.pages.item_page import ItemPage, SearchPage

from aiqa_framework.shared.config.tags import TAGS, jira, tags


@tags(TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-2")
def test_create_item_via_ui(page, api, cleanup) -> None:
    """CREATE is under test → drive the UI, track the id, tear down via the API."""
    item = ItemPage(page)

    # The behaviour under test: creating through the UI.
    item.open("/items/new")
    item.create(name="Widget A")
    item.verify_created()

    # Track the created id — teardown deletes it via the API, never the UI.
    cleanup.add(api.delete, f"/items/{item.created_id()}")


@tags(TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-2")
def test_search_finds_item(page, api, cleanup) -> None:
    """Data is a PRECONDITION → seed it via the API, test search, tear down via API."""
    # Precondition via the API (fast + deterministic — not via the UI).
    item_id = api.post_json("/items", {"name": "Widget B"})["id"]
    cleanup.add(api.delete, f"/items/{item_id}")

    # The functionality under test: searching in the UI.
    search = SearchPage(page)
    search.open("/items")
    search.search("Widget B")
    search.verify_row_visible(item_id)

---
name: explore-app
description: Explore the SUT with the Playwright MCP to discover real selectors, routes, and navigation, and record them in docs/ai/ui/navigation.md for reuse. Use before generating UI automation from summary/vague steps, or to map a new area of the app.
---

# explore-app — map the SUT

1. Use the Playwright MCP (`mcp__playwright__*`): navigate, snapshot, and read the real
   DOM. Reuse the saved auth / storage state.
2. Prefer selectors by priority: `data-zcqa → data-test-id → data-id → data-title` →
   `id` → `role + text`. Do NOT invent selectors; if none exist, recommend adding
   `data-test-id` and record the gap in `docs/ai/ui/memory.md` "Known gaps".
3. Record each screen in `docs/ai/ui/navigation.md`:
   `Screen | Route / URL | How to reach | Page Object`. Don't re-explore a screen
   already mapped there.
4. Never perform a destructive action (delete, irreversible submit) without explicit
   confirmation.

Output feeds `automation-generate` (its "summary → explore then generate" mode).
Fallback (no Playwright MCP): work from Figma + existing page objects; mark every
unverified selector as needing live verification.

---
name: visual-regression
description: Add and maintain UI visual-regression checks with Playwright — capture baseline screenshots, compare on later runs within a tolerance, and manage baseline updates. Use for pixel/layout regressions on key screens (needs a screenshot-compare dependency).
---

# visual-regression — UI screenshot baselines

UI-only (Playwright). Python Playwright has no built-in visual matcher, so use a
screenshot + compare approach.

## Setup (once)
- Add a compare dependency (optional extra), e.g. `pytest-playwright-visual-snapshot`, or
  a small Pillow / pixelmatch compare helper. `pyproject.toml` is patch-guarded — prepare
  the change and ask the user.
- Baselines: `tests/ui/__snapshots__/<test>/<name>.png` (committed).

## Write a check
- Navigate + **stabilize** the screen (wait for network idle / a marker element; mask
  volatile regions like dates/carousels) via the Page Object / `ActionKeyword`.
- Capture with `page.screenshot(...)` and compare to the baseline within a pixel/ratio
  **tolerance** (otherwise antialiasing flakes). Tag `@tags(TAGS.REGRESSION)`; add a
  `visual` marker via `update-conventions` if you want to run them separately.

## Update baselines
Only on an intended UI change, with review — regenerate, eyeball the diff, commit the new
baseline. Never auto-accept diffs.

## Rules
Deterministic viewport/device (reuse `modules/ui/mobile_web` descriptors); mask dynamic
content; keep baselines small. A real diff is a finding for `review-code` / `create-bug`.

# Fallback Rules

## Jira fallback
If the Jira MCP fails / is unavailable / the story cannot be reached: do not block.
Use note context under `docs/ai/`, keep the review sync there, and keep the final
Excel path in `test-output/qa/` for manual upload later.

## Figma fallback
If the Figma MCP is unavailable / the link is missing / access fails: skip UI
extraction; do not simulate UI structure or fabricate selectors; suggest
`data-test-id` only.

## Prototype / DOM fallback
If the prototype link is missing or the Playwright MCP is unavailable: do not
inspect the DOM or fabricate selectors; use `element: ""`; recommend adding
`data-test-id` for automation. STEP 14 then marks those selectors as needing live
verification in `docs/ai/memory.md` "Known gaps".

## Approval fallback
Never bypass the approval loop. No Excel export and no code generation before the
exact phrase `I approve`.

## Automation-half fallback
If code generation or the run cannot complete (missing marker that is patch-guarded,
no live app, MCP down): persist what was generated, run what is runnable, and report
the gap. Never silently drop cases — log them in `docs/ai/memory.md` and the
`Execute Testing` subtask.

## General
Always degrade gracefully. Partial completion is allowed. Blocking the workflow is
not allowed when a fallback path can continue.

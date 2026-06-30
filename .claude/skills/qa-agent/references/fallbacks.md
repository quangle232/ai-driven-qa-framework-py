# Fallback Rules

Always degrade gracefully. Partial completion is allowed. Do not block the
workflow when a fallback path can continue. But for the Jira / TestRail MCPs, do
NOT silently fall back — first try the **guided setup** below.

## Jira MCP — guided setup (do this BEFORE note-context fallback)
At STEP 0/1, if the Jira MCP is unreachable / not configured / the user story
cannot be fetched, run this loop instead of silently degrading:

1. **Warn clearly**: "⚠️ Jira MCP is not reachable — I can't fetch the user story.
   Let's connect it so I can pull real data."
2. **Guide + offer to configure** the Jira (Atlassian) MCP for the user. Show the
   config and, with their OK, write it (see `mcp-usage.md` "Setting up the Jira
   MCP" for the exact `.mcp.json` snippets + credential placeholders). Confirm the
   site URL + auth with the user — never invent credentials.
3. **Reload**: tell the user to approve the new server and reload (MCP servers are
   loaded at session start — a new `claude` session / re-invocation picks it up).
4. **Retry the fetch**: re-run STEP 1 and confirm the user story is now reachable.
5. **Only if the user declines or it still fails** → use note context under
   `docs/ai/`, keep the review sync there, keep the Excel path for manual upload,
   and log `Jira: skipped — <reason>` in `docs/ai/memory.md` "Known gaps".

## TestRail MCP — guided setup
If the client chose the TestRail target but the TestRail MCP or config is missing:
1. Warn that TestRail can't be reached.
2. Guide + (with OK) write the TestRail MCP config + `environments/.env.testrail`
   (`TESTRAIL_URL` / `TESTRAIL_USER` / `TESTRAIL_API_KEY`, gitignored) — see
   `mcp-usage.md` "Setting up the TestRail MCP".
3. Reload + retry the publish.
4. If declined / still failing → fall back to the **Excel** target and tell the
   user they can import it into TestRail later.

## Figma MCP
Unavailable / link missing / access fails: skip UI extraction; do not simulate UI
or fabricate selectors; suggest `data-test-id` only.

## Prototype / DOM (Playwright MCP)
Missing link / MCP unavailable: do not inspect the DOM or fabricate selectors; use
`element: ""`; recommend adding `data-test-id`. STEP 14 marks those selectors as
needing live verification in `docs/ai/memory.md` "Known gaps".

## Approval fallback
Never bypass the approval loop. No Excel/Xray/TestRail publish and no code
generation before the exact phrase `I approve`.

## Automation-half fallback
If code generation or the run can't complete (a patch-guarded marker is missing, no
live app, an MCP is down): persist what was generated, run what is runnable, and
report the gap. Never silently drop cases — log them in `docs/ai/memory.md` and the
`Execute Testing` item.

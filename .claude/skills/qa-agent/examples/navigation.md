# App Navigation Map — EXAMPLE

EXAMPLE of `docs/ai/navigation.md`. How to reach each screen; reused so a known
screen is not re-explored by the Playwright MCP.

| Screen | Route / URL | How to reach | Page Object |
|--------|-------------|--------------|-------------|
| Sign-in | `/signin` | `login_page.open(AUTH_URL)` | `modules/ui/pages/login_page.py` |
| Dashboard | `/` | post-login redirect | `modules/ui/pages/dashboard_page.py` |
| Account settings | `/settings/account` | header menu → "Account" | `modules/ui/pages/account_settings_page.py` |

## Notes
- Auth runs once (conftest + storage state); every test starts at `/` already
  signed in.

# modules/ui — Web + mobile-web (Playwright)

All Playwright: POM + the single `ActionKeyword` layer, one-time auth + storage
state, Playwright device emulation (mobile-web), and a Playwright API helper for
seeding UI state.

Install + run in isolation:
```bash
uv sync --extra ui
uv run playwright install --with-deps chromium
uv run pytest tests/ui -m regression        # + tests/ui/mobile_web
```

Key imports:
```python
from aiqa_framework.modules.ui.base_page import BasePage
from aiqa_framework.modules.ui.pages.sample_page import SamplePage
from aiqa_framework.modules.ui.api_support import UiApiSupport
```

Conventions: `conventions.md`. Memory: `docs/ai/ui/`.

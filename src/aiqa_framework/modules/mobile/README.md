# modules/mobile — Native mobile (Appium)

Native app testing via Appium: Screen Objects + `MobileActionKeyword`, per-worker
driver, desired capabilities. Mobile-web (Playwright) is `modules/ui/mobile_web`.

Install + run in isolation:
```bash
uv sync --extra mobile
ALLOW_MOBILE_NATIVE=1 uv run pytest tests/mobile -m mobile_native
```

Key imports:
```python
from aiqa_framework.modules.mobile.action_keyword import MobileActionKeyword
from aiqa_framework.modules.mobile.screens.sample_login_screen import SampleLoginScreen
```

Conventions: `conventions.md`. Memory: `docs/ai/mobile/`.

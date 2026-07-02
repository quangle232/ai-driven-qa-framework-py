# Mobile module conventions (native Appium)

Native mobile only. Mobile-**web** (Playwright emulation) lives in `modules/ui/mobile_web`.

## Structure
- `action_keyword.py` — `MobileActionKeyword`, the single native keyword layer
  (accessibility-id first).
- `screens/` — Screen Objects (the native POM analogue), `extends BaseScreen`.
- `capabilities.py` · `driver_factory.py` — Appium desired caps + driver per worker.
- `helpers/`, `testdata/`.

## Rules
- A spec calls Screen Objects; a Screen Object calls `self.keyword.*`.
- Locator priority: accessibility-id → id → xpath (last resort).
- Tag specs `@tags(TAGS.MOBILE, TAGS.MOBILE_NATIVE)`; they are **skip-gated** by
  `ALLOW_MOBILE_NATIVE=1` (need a device/emulator + Appium server).
- Appium is imported lazily (mobile extra); base install / other modules never need it.

## Run in isolation
```bash
uv sync --extra mobile
ALLOW_MOBILE_NATIVE=1 uv run pytest tests/mobile -m mobile_native
```
Memory: `docs/ai/mobile/`.

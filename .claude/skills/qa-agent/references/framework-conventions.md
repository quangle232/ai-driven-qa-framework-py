# Framework Conventions — Python (Playwright + pytest)

Generated code MUST match these. Read the referenced source first.

## Project structure
```
src/aiqa_framework/
  config/    env.py (test_env→.env.<env>) · settings.py (pydantic) · tags.py (markers)
  core/      action_keyword.py (single UI keyword layer) · base_page.py · auth.py
  pages/     Page Objects (extend BasePage)
  api/       client.py (httpx) · models.py (pydantic) · services/ · mock/ · contracts/
  grpc/      proto/ · generated/ · client.py · mock_server.py
  mobile/    capabilities.py · action_keyword.py · screens/
  ai_qa_agent/  the `aiqa` CLI + collectors/diagnosis/reports
  mcp_servers/  4 FastMCP servers
tests/  ui/ api/ grpc/ mobile/ mobile_web/
```

## UI (POM)
- One class per screen in `pages/<name>_page.py`, `extends BasePage` (gives `self.page`,
  `self.keyword`). Selectors as class attributes; methods call `self.keyword.*` only —
  never `self.page.locator(...)`.
- New shared keywords go INTO `ActionKeyword`. Locator priority:
  `data-zcqa → data-test-id → data-id → data-title`.

## API (Service-Object Model)
- `api/services/<name>_service.py` classes wrap `ApiClient` (httpx). Specs call services.
- Request/response models are pydantic (`api/models.py`); pass `schema=` + `expected_status=`
  so drift fails loudly. Mocks: respx (httpx) + the FastAPI app (ASGI transport).

## gRPC
- `grpc/client.py` (GameClient) is the only gRPC layer: deadline on every call, bearer
  metadata auth. Assert `grpc.StatusCode.*` on `grpc.RpcError`. Mock implements the proto.

## Mobile
- Native: Screen Objects (`mobile/screens/`) + `MobileActionKeyword` (accessibility-id-first);
  tag `@tags(TAGS.MOBILE, TAGS.MOBILE_NATIVE)` (skip-gated). Mobile-web reuses the web POM.

## Spec conventions
- Import `from aiqa_framework.config.tags import TAGS, tags, jira`. Decorate:
  `@tags(TAGS.API, TAGS.REGRESSION, TAGS.P1)` + `@jira("KEY")`.
- Test data in `aiqa_framework/testdata/` modules, not inline.
- Comments in English. Run via `uv run pytest -m <tag>`.

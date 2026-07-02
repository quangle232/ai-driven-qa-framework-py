# JSON → pytest mapping (STEP 14 bridge)

The JSON schema lives in `json-contract.md`, coverage in `testing-strategy.md`,
priority in `priority-scoring.md`. This file is the **bridge**: how an approved
JSON test case becomes runnable pytest code that follows `framework-conventions.md`.

Generate code only for cases that are `automatable: true` and not flagged for
removal (`duplicateStatus != "duplicate"`).

## Field mapping
| JSON field | Becomes in pytest |
|------------|-------------------|
| `tcId` + `testDescription` | test function name + a one-line docstring (`def test_<slug>(...)`) |
| `meta.userStoryKey` (or `acIds` source) | `@jira("<KEY>")` |
| `priority` (`P0`/`P1`/`P2`) | priority marker `TAGS.P0` / `TAGS.P1` / `TAGS.P2` (case-folded) |
| `surface` | folder + surface marker + keyword layer (table below) |
| `feature` / Jira label | feature marker (`TAGS.<FEATURE>`), kebab→snake |
| `summaryPrecondition` | fixtures / setup + an opening comment |
| `stepDetails[].detail` | the spec body, one step per comment+call |
| `stepDetails[].element` | the selector on the Page Object / Screen Object |
| `testResult` / `bugId` | written BACK after STEP 15 run (not at generation) |
| `specFile` | set to the generated path once written |

## Surface → target
| `surface` | Spec folder | Markers | Keyword layer / object |
|-----------|-------------|---------|------------------------|
| `ui` | `tests/ui/test_<feature>.py` | `TAGS.REGRESSION` (+ priority) | Page Object in `modules/ui/pages/`, `self.keyword.*` |
| `api` | `tests/api/test_<feature>.py` | `TAGS.API` | service in `modules/api/rest/services/`, pydantic models |
| `grpc` | `tests/grpc/test_<feature>.py` | `TAGS.GRPC` | `modules/api/grpc/client.py`, assert `grpc.StatusCode.*` |
| `mobile_web` | `tests/mobile_web/test_<feature>.py` | `TAGS.MOBILE_WEB` | reuse the web POM |
| `mobile_native` | `tests/mobile/test_<feature>.py` | `TAGS.MOBILE, TAGS.MOBILE_NATIVE` | `modules/mobile/screens/` + `MobileActionKeyword` (skip-gated) |

## Generated shape (see `../examples/`)
- Page Object: `../examples/sample_page_object.py` — `extends BasePage`, selectors
  (from JSON `element`) as class attrs, interaction only via `self.keyword.*`.
- Spec: `../examples/sample_spec.py` — `@tags(...)` + `@jira(...)`, call the Page
  Object (never `page.locator` in a spec), one comment+call per `stepDetails` step,
  test data in a `testdata/` module.

## Rules
- Decorate every test: `@tags(TAGS.<SURFACE>, TAGS.REGRESSION, TAGS.P0/1/2)` +
  `@jira("KEY")`.
- New shared keywords go INTO the surface keyword layer — never call the transport
  directly in a spec.
- Reuse existing pages / services / screens before generating new ones.
- A missing feature marker needs `shared/config/tags.py` + `pyproject.toml` (both
  patch-guarded) — ask the user; reuse the closest marker meanwhile.
- Validate each file with `uv run aiqa guard --files <paths>` before finalising.

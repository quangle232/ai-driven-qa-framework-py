---
name: contract-test
description: Contract / property-based API testing with Schemathesis against the OpenAPI schema (the FastAPI app/mock exposes /openapi.json). Auto-derives cases from the schema to catch contract violations, 5xx errors, and schema drift — complements the hand-written REST specs. Use to harden REST APIs against their contract.
---

# contract-test — schema-driven API testing

Uses **schemathesis** (in the `dev` extra) against the REST OpenAPI schema. The FastAPI
mock (`modules/api/rest/mock/standalone_app.py`) and a real FastAPI SUT both expose
`/openapi.json`; committed contracts live in `modules/api/rest/contracts/`.

## Run
```
uv run poe mock-api            # serve the mock (or target a real base URL)
uv run schemathesis run http://localhost:8000/openapi.json --checks all
```
Or as pytest in `tests/api/rest/` (`schemathesis.from_asgi("/openapi.json",
create_mock_app())` for the in-process mock), tagged `@tags(TAGS.API, TAGS.REGRESSION)`
so it runs with the suite.

## Checks
Status-code + response-schema conformance, content-type, and server errors (5xx) across
auto-generated + boundary inputs derived from the schema.

## Rules
- The OpenAPI schema is authoritative — a failure is a real contract violation: fix the
  API or update the contract deliberately (`update-conventions` / `create-bug`).
- Complements, does not replace, the hand-written Service-Object specs.
- Do not run generated (possibly destructive) calls against a shared/real environment
  without confirmation — prefer the mock or a disposable env.

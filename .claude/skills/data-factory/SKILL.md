---
name: data-factory
description: Create and manage test data by convention — typed builders/factories and fixtures in each surface's testdata/ module, with valid + boundary + invalid variants, kept OUT of the specs. Use when specs need structured or varied test data (create-user payloads, boundary values, invalid inputs).
---

# data-factory — test data builders

Keep data OUT of specs — put it in `src/aiqa_framework/modules/<surface>/testdata/`.

## Build
- Typed builders/factories (functions or pydantic models) returning valid objects with
  sensible defaults + overrides, e.g. `make_user(**overrides)`.
- Provide the variants the testing strategy needs: **valid** (happy), **boundary**
  (min/max/edge), **invalid** (validation/negative). Align with the API pydantic models
  (`modules/api/rest/models.py`) so data matches the contract.
- Deterministic by default (seeded) for reproducible runs; offer a randomized/unique
  variant when a test needs it. Stdlib only unless the user adds a data lib.

## Use
Specs import from `testdata/`; services / pages accept the built objects. Reuse existing
factories before adding new ones. To seed UI state over HTTP use
`modules/ui/api_support.py`.

## Rules
No secrets / real PII in committed data. Validate against the model. Comments in English.

# Testing Strategy

## Goal
Ensure strong coverage with minimal but sufficient test cases.

## Coverage dimensions
happy · negative · edge · boundary · adhoc · blackbox · api · data · security

## Minimum rules
### Per AC
- 1 happy
- 1 negative

### Global minimum
- edge: 2
- boundary: 2
- security: 2
- data: 2
- api: 1
- adhoc: 1

## Ordering rules
1. happy path first
2. UI sanity
3. validation
4. negative
5. edge / boundary
6. adhoc / exploratory

## Strategy notes
- Avoid duplicate coverage and redundant permutations; prefer meaningful variations.
- Keep test cases automation-ready (clear steps, explicit data, a target element)
  so STEP 14 can convert them to pytest cleanly.
- Every test case should map to at least one AC whenever possible.

## Surface mapping (this framework)
A case targets one surface; this drives the generated pytest later:
- UI flow → `tests/ui/` (`TAGS.REGRESSION`)
- `api` dimension → `tests/api/` (`TAGS.API`, validate with a pydantic model)
- gRPC behaviour → `tests/grpc/` (`TAGS.GRPC`, assert `grpc.StatusCode.*`)
- mobile → `tests/mobile_web/` (web POM reuse) or `tests/mobile/` (native, skip-gated)
- known-broken behaviour → `TAGS.BUG` (excluded by `-m "not bugs"`)

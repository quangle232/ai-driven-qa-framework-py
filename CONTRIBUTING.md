# Contributing

- One keyword layer: UI → `core/action_keyword.py`, API → `api/client.py`, gRPC → `grpc/client.py`,
  mobile → `mobile/action_keyword.py`. Specs never call the transport directly.
- New shared UI keywords go INTO `ActionKeyword` (don't create a parallel class).
- Page Objects / services / screens hold selectors + actions; tests hold flow only; data in `testdata/`.
- Tag every test: `@tags(TAGS.<SURFACE>, TAGS.REGRESSION, TAGS.P0/1/2)` + `@jira("KEY")`.
- Validate API responses with pydantic; assert gRPC status codes.
- Run `uv run poe lint && uv run poe typecheck` before pushing.
- Don't touch (patch-guard protected): `environments/`, `.auth/`, `config/`, `ci/`,
  `grpc/proto/`, `api/contracts/`, `conftest.py`, `pyproject.toml`.

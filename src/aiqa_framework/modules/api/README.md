# modules/api — REST · gRPC · GraphQL (no Playwright)

Pure backend functional testing across three sub-surfaces, each with its own
keyword layer, models, and in-process mock.

Install + run in isolation:
```bash
uv sync --extra api --extra grpc --extra graphql
uv run poe proto-gen
uv run pytest tests/api -m "api or grpc or graphql"
```

Key imports:
```python
from aiqa_framework.modules.api.rest.services.user_service import UserService
from aiqa_framework.modules.api.grpc.client import GameClient
from aiqa_framework.modules.api.graphql.client import GraphQLClient
from aiqa_framework.modules.api.graphql.queries import GET_USER, LIST_USERS
```

Conventions: `conventions.md`. Memory: `docs/ai/api/`. Load testing is a separate
surface: `modules/performance`.

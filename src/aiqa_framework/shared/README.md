# shared/ — AIQA kernel

Cross-cutting building blocks used by every testing surface. Installed with the
base package (no optional extra needed).

| Package | Purpose |
|---------|---------|
| `config` | env resolution, pydantic settings, `TAGS`/`tags()`/`jira()` markers |
| `reporting` | failure → Jira bug reporter (root conftest hook) |
| `memory` | `docs/ai/<module>/` per-module AI memory + artifact paths |
| `helpers` | small cross-cutting utils |

Import examples:
```python
from aiqa_framework.shared.config.tags import TAGS, tags, jira
from aiqa_framework.shared.memory import memory_file, testcases_dir
```

Dependency direction: modules → shared (never the reverse).

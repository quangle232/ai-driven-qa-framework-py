# shared/ — AIQA kernel

Cross-cutting building blocks used by every testing surface. Installed with the
base package (no optional extra needed).

| Package | Purpose |
|---------|---------|
| `config` | env resolution, pydantic settings, `TAGS`/`tags()`/`jira()` markers |
| `reporting` | failure → approval-gated bug drafts (default) + Jira bug filing (`JIRA_AUTO_BUG=yes` / approved drafts) |
| `memory` | `docs/ai/<module>/` per-module AI memory + artifact paths |
| `helpers` | small cross-cutting utils |

Import examples:
```python
from aiqa_framework.shared.config.tags import TAGS, tags, jira
from aiqa_framework.shared.memory import memory_file, testcases_dir
```

Dependency direction: modules → shared (never the reverse).

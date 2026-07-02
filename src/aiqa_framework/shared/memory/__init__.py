"""Per-module AI memory store (docs/ai/<module>/)."""

from aiqa_framework.shared.memory.store import (
    MODULES,
    memory_file,
    module_memory_dir,
    testcases_dir,
)

__all__ = ["MODULES", "memory_file", "module_memory_dir", "testcases_dir"]

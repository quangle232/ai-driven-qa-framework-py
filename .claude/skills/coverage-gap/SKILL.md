---
name: coverage-gap
description: Audit test coverage — cross-reference acceptance criteria / requirements against the existing test-case catalogue and specs, and report gaps (uncovered AC, missing negative/edge/security/data cases per the testing strategy, untested surfaces, redundant duplicates). Recommends the specific cases to add. Use to answer "what's not tested?" for a story, feature, or module.
---

# coverage-gap — find what's not tested

## Inputs
A Jira story / AC, a feature or module name, or "the whole suite".

## Gather (reuse, don't guess)
- Requirements: AC from the Jira MCP / note (`references/ac-parsing.md`), or the
  feature's intent.
- Existing coverage: the `framework-context` MCP or `uv run aiqa scan` (code index),
  the `docs/ai/<module>/test-case.md` catalogues, and
  `python3 .claude/skills/qa-agent/scripts/find_related_tests.py <marker>` for specs.

## Analyze
- **AC → case mapping**: every AC should map to ≥1 case; flag AC with none.
- **Dimension gaps** (`references/testing-strategy.md`): per AC ≥1 happy + ≥1 negative;
  global minimums for edge / boundary / security / data / api / adhoc — flag what's short.
- **Surface gaps**: UI / API / gRPC / GraphQL / performance / mobile the feature touches
  but has no test.
- **Redundancy**: duplicate / near-duplicate coverage (`references/duplicate-detection.md`)
  worth pruning.

## Output
A gap report: covered vs uncovered AC, missing dimensions/surfaces, redundant cases, and
a **prioritized list of recommended cases to add** — ready to feed `create-test-cases`
or `automation-generate`. Read-only: it recommends, it does not create.

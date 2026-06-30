# Acceptance Criteria Parsing Rules

## Goal
Extract structured, reliable acceptance criteria from the source input.

## Source priority
1. Jira description
2. Issue note context (`docs/ai/`)
3. Other attached docs

## Parsing rules
- Only extract explicitly written acceptance criteria.
- Do not invent acceptance criteria.
- Normalize bullet lists, numbered lists, and newline-separated AC statements.
- Preserve business meaning exactly.

## Prefixing
Normalize each AC as `AC1`, `AC2`, `AC3`, …

## Stop conditions
Stop parsing when hitting sections such as: Notes, Technical details, Out of
scope, Attachments, Links, Definition of Done.

## Output shape
```json
[
  { "id": "AC1", "text": "User can log in with valid credentials" },
  { "id": "AC2", "text": "User sees an error for invalid credentials" }
]
```

## Fallback
If no AC is found: mark the issue as incomplete, continue QA generation, add
assumptions, add open questions.

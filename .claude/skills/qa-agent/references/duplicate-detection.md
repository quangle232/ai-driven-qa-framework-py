# Duplicate Detection

## Goal
Reduce duplicate and near-duplicate test cases before approval.

## Detection levels
### Exact duplicate
Flag when these are effectively the same: same feature and sub-feature; same
intent; same precondition; same expected behavior.

### Near duplicate
Flag as possible overlap when: same AC mapping; same validation intent;
different wording only; one case is a narrow variation of another without
meaningful coverage gain.

## Keep both only if they cover
- different platforms
- different roles or permissions
- meaningfully different data boundaries
- different API vs UI layers
- different business outcomes

## Review behavior
- Exact duplicates → mark for removal (`duplicateStatus: "duplicate"`).
- Near duplicates → mark for human review (`duplicateStatus: "possible-overlap"`).
- Do not auto-delete without preserving traceability in the review loop
  (`duplicateOf` + `duplicateReason`).

## Signal examples
Useful comparison signals: normalized `summaryPrecondition`; normalized
`testDescription`; mapped `acIds`; step intent; expected-result intent.
`scripts/json_quality_checks.py` flags these deterministically.

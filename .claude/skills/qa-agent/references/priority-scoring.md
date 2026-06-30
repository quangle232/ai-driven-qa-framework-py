# Auto Priority Scoring

## Goal
Assign a default priority to each test case consistently.

## Output values
`P0` · `P1` · `P2` (stored in the JSON `priority` field).

## P0 rules
Assign P0 when any applies: core business path; login / auth / authorization;
payment / checkout / contract signing; destructive action; data integrity risk;
irreversible state change; security-sensitive behavior; system-blocking
regression risk.

## P1 rules
Assign P1 for: important business validations; common alternate flows; common
negative scenarios; high-frequency user actions; significant UI/UX validation
with business impact.

## P2 rules
Assign P2 for: lower-risk edge cases; cosmetic or secondary behavior; rare
combinations; exploratory coverage without clear production criticality.

## Tie-break rules
- Prefer higher priority when uncertain and the impact is user-blocking.
- Do not mark everything P0. Use business impact over UI complexity.

## Implementation note
Priority can be inferred from: mapped AC; keywords in summary/description;
destructive verbs (delete, submit, approve, pay, sign, publish); risk tags.
Record the rationale in `priorityReason`. `scripts/json_quality_checks.py`
applies these heuristics deterministically.

## pytest marker mapping (STEP 14)
When the approved case is turned into pytest, the JSON `priority` maps to a
priority marker (case-folded): `P0 → TAGS.P0` (`pytest.mark.p0`), `P1 → TAGS.P1`,
`P2 → TAGS.P2`. So the Excel/JSON keep the uppercase `P0` form while the generated
test carries `@tags(TAGS.P0, ...)`.

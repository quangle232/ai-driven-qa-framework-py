# CHANGESET Example

A revision message in the approval loop (STEP 10/11). The agent applies it to the
canonical JSON first, then re-enriches, re-renders the table, and re-syncs.

CHANGESET:
- update TC-LOGIN-003 summary to include empty password validation
- update TC-LOGIN-005 priority from P1 to P0
- add one boundary case for password min length
- remove duplicated test case for invalid email format

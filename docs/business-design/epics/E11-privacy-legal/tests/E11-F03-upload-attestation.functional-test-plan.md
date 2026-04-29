# E11-F03 — Upload Attestation: Functional Test Plan

## Scope
Verifies attestation modal, gate enforcement, DMCA workflow.

## Source User Stories
- S01 per-session gate — Critical
- S02 DMCA — Critical

## Test Scenarios
- **FT-302** First upload triggers attestation modal. Critical.
- **FT-303** Subsequent uploads in session skip modal. High.
- **FT-304** Attestation declined → upload blocked. Critical.
- **FT-305** DMCA mailbox monitored. High.
- **FT-306** Takedown cascade within 72h. Critical.

## Negative Tests
- Embedded SDK blocks modal; upload denied.

## Boundary Tests
- Coordinator session vs student session — different copy.

## Permission and Role Tests
- DMCA mailbox SA-controlled.

## Integration Tests
- E11-F03 ↔ E01-F01 ↔ E01-F04.

## Audit and Traceability Tests
- Per-attestation timestamp + session ID.

## Regression Risks
- Modal bypassed via direct API; client-side modal cannot be sole gate; server-side check.

## Open Questions
- Per-file attestation for high-risk content.

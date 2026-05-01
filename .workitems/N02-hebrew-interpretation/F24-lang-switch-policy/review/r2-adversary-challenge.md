# R2 Adversary Challenge — N02/F24 Inline Language Switching Policy (Deferred MVP Stub)

- **Feature:** N02/F24 (Inline Language Switching Policy)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Finding 2: Deferred FTs not annotated — AGREE (MEDIUM)

**Adversary assessment:** R1 is correct. Tests that won't be implemented in POC
should be marked deferred in traceability to prevent traceability tooling from
flagging them as uncovered. The fix is mechanical.

**Verdict:** SUSTAIN MEDIUM. Update tests[] entries in traceability.yaml.

### Other findings: Confirm or no objection

All other R1 findings are Low confirmations. No counter-arguments.

## R2 Synthesis

### Required action
- Update traceability.yaml tests[] to add status: deferred for all MVP-scope FTs.

### Gate
No Critical or High issues. T-01 stub is unblocked for TDD.
Feature is correctly scoped as a deferred MVP placeholder.

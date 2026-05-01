# R1 Design Review — N02/F27 HebPipe CoNLL-U Coreference (Deferred MVP Stub)

- **Feature:** N02/F27 (HebPipe CoNLL-U Coreference)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Status:** POC scope is a no-op stub; all substantive FTs deferred to MVP.
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md

---

## Role 1 — Contract Alignment

### Finding 1: Feature gate pattern is correct and consistent with project conventions
- **Area:** contract
- **Issue:** The env-var feature gate (TIRVI_* flag, default False) is the correct POC
  pattern. It matches the COREF_ENABLED / LANG_SWITCH_ENABLED approach used by other
  deferred features. The identity/stub return when disabled is the correct behavior.
- **Severity:** Low (confirmation)

### Finding 2: Deferred FTs must be explicitly annotated
- **Area:** contract
- **Issue:** The functional tests (FT-179/180/181 for F24; FT-141/143 for F27; etc.) are
  in the biz corpus but deferred per PLAN-POC.md. traceability.yaml does not mark them
  as deferred — they will appear as uncovered tests.
- **Severity:** Medium
- **Recommendation:** Add notes to traceability.yaml tests[] entries marking MVP-deferred
  tests as status: deferred with deferred_reason: "MVP scope per PLAN-POC.md."

---

## Role 2 — Architecture & Pattern

### Finding 3: Stub module correctly defines the interface contract
- **Area:** architecture
- **Issue:** The stub defines the public interface (function signature + return type) that
  MVP will implement. The POC stub preserves the calling convention so MVP can be
  implemented as a drop-in enhancement without changing callers.
- **Severity:** Low (confirmation)

---

## Role 3 — Test Coverage

### Finding 4: T-01 has a single POC-relevant test (gate=disabled)
- **Area:** test coverage
- **Issue:** The only POC-relevant test is FT-144/gate-disabled equivalent — assert that
  the stub returns identity/empty when the env flag is False. This is minimal but correct
  for a stub.
- **Severity:** Low (confirmation)

---

## Roles 4-6: No additional findings

Design is deliberately minimal for a stub feature. No HLD deviations beyond the
explicit "deferred" statement. No complexity risk (CC = 1 for identity stubs).
No security concerns.

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: gate pattern correct | Low | Contract | None |
| F2: deferred FTs not annotated | Medium | Contract | Mark deferred in traceability.yaml |
| F3: interface contract preserved | Low | Architecture | None |
| F4: gate test sufficient for POC | Low | Test | None |

No Critical or High issues. Design is appropriate for a deferred-MVP stub.

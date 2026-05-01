# R2 Adversary Challenge — N03/F31 WhisperX Forced-Alignment Fallback (Deferred MVP)

- **Feature:** N03/F31 (WhisperX fallback — deferred stub)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Adversary position

R1 found no Critical or High issues. The adversary agrees: this is a correct and
complete deferred stub. The unconditional NotImplementedError is the stronger and
safer choice versus a no-op.

**Challenge: should the stub at least log a warning instead of raising?** No — a
warning would allow callers to silently skip the fallback path in POC, which is the
wrong behavior. The exception forces call-site awareness. ADR-015 rationale confirmed.

**Is it a risk that F26 DE-04 sets tts_marks_truncated=True with no fallback path
in POC?** Accepted known limitation per ADR-015. F30 logs a warning on truncation;
no timing correction is attempted in POC. This is documented and intentional.

---

## R2 Synthesis

**Confirmed:** No Critical or High findings from R1. No new findings raised by adversary.

**Required design.md edits:** None.

**Gate: PASS.** Feature stub is approved as a deferred MVP artifact per ADR-015.
TDD task T-01 may proceed when the POC stub implementation is scheduled.

# R2 Adversary Challenge — N03/F27 Google Chirp3 HD Voice TTS Adapter (Deferred MVP)

- **Feature:** N03/F27 (Chirp3 HD adapter — deferred stub)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Adversary position

R1 found no Critical or High issues. The adversary agrees: this is a correct and
complete deferred stub. No counter-arguments are raised.

**Could the stub be mistakenly activated in the POC?** Only if `TIRVI_CHIRP3=1`
is set in the Docker env, which is not in the POC startup config. Risk: None.

**Is NotImplementedError the right exception type?** Yes — callers must handle
it explicitly. A silent no-op would be worse (silently omitting synthesis).

---

## R2 Synthesis

**Confirmed:** No Critical or High findings from R1. No new findings raised by adversary.

**Required design.md edits:** None.

**Gate: PASS.** Feature stub is approved as a deferred MVP artifact. TDD task T-01
may proceed when the POC stub implementation is scheduled.

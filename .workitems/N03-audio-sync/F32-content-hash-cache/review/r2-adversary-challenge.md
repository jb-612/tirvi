# R2 Adversary Challenge — N03/F32 TTS Content-Hash Audio Cache (Deferred MVP)

- **Feature:** N03/F32 (TTS audio cache — always-miss stub)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Adversary position

R1 found no Critical or High issues. The adversary agrees: this is a correct and
complete deferred stub. No counter-arguments are raised.

**Challenge: could always returning None cause unexpected re-synthesis on every
request?** Yes — intentionally. The POC has no cache; every synthesis call hits
Wavenet F26. The `drafts/<sha>/` directory (F26 DE-05) preserves output on disk,
so repeated demo runs reuse the written file without re-calling the API (via F26's
no-overwrite guard + demo-re-run TIRVI_DRAFTS_OVERWRITE flag). The cache stub is
consistent with this design.

**Should the stub also write a no-op cache-put function?** Callers only need the
cache-get path (miss → synthesize). Cache-put is MVP; no stub needed.

---

## R2 Synthesis

**Confirmed:** No Critical or High findings from R1. No new findings raised by adversary.

**Required design.md edits:** None.

**Gate: PASS.** Feature stub is approved as a deferred MVP artifact. TDD task T-01
may proceed when the POC stub implementation is scheduled.

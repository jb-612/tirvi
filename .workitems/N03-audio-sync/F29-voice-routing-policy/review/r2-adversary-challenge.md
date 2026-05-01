# R2 Adversary Challenge — N03/F29 Voice Routing Policy (Deferred MVP — Single-Voice POC)

- **Feature:** N03/F29 (voice routing policy — constant stub)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Adversary position

R1 found no Critical or High issues. The adversary agrees: this is a correct and
complete deferred stub. No counter-arguments are raised.

**Does always returning `"wavenet"` mask future routing bugs?** Intentionally yes
for POC — the stub is trivially testable and will be replaced wholesale at MVP.
There is no subtlety to miss.

**Should route_voice raise when TIRVI_VOICE_ROUTING is set instead of returning
"wavenet"?** The design calls for NotImplementedError when the gate IS set (to
signal multi-voice not yet implemented). The constant-return path is for when the
gate is NOT set. This is the correct inversion — confirmed.

---

## R2 Synthesis

**Confirmed:** No Critical or High findings from R1. No new findings raised by adversary.

**Required design.md edits:** None.

**Gate: PASS.** Feature stub is approved as a deferred MVP artifact. TDD task T-01
may proceed when the POC stub implementation is scheduled.

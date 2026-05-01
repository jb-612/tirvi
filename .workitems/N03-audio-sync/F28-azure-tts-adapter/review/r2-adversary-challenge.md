# R2 Adversary Challenge — N03/F28 Azure Cognitive Services TTS Adapter (Deferred MVP)

- **Feature:** N03/F28 (Azure TTS adapter — deferred stub)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Adversary position

R1 found no Critical or High issues. The adversary agrees: this is a correct and
complete deferred stub. No counter-arguments are raised.

**Could the F24 inline lang switch be broken by this stub?** F24 checks for the
gate env var before calling `synthesize_azure`; if unset, F24 falls through to
Wavenet. The stub's NotImplementedError provides an explicit signal if the gate
is accidentally set. Risk: None in POC config.

**Should this stub import Azure SDK at module load time?** No — the stub must not
import the SDK. Lazy import at MVP time only. Design correctly defers this.

---

## R2 Synthesis

**Confirmed:** No Critical or High findings from R1. No new findings raised by adversary.

**Required design.md edits:** None.

**Gate: PASS.** Feature stub is approved as a deferred MVP artifact. TDD task T-01
may proceed when the POC stub implementation is scheduled.

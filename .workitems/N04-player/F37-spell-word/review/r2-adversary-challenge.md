# Design Review R2 — Adversary Challenge — N04/F37 Spell-Word

**Feature:** N04/F37 — Spell-word (deferred MVP)
**Round:** R2 adversary challenge + synthesis
**Date:** 2026-05-01
**Status:** R2 complete — approved

---

## Adversary Position

The adversary accepts the deferred stub classification. No R1 findings
are misclassified. One adversary probe is raised:

**Probe:** F37 depends on TTS synthesis (DE-02) to spell individual letters.
If the MVP player uses Web Speech API (client-side) for letter synthesis,
there is a significant quality gap compared to Cloud TTS (Wavenet). Hebrew
letter pronunciation via `window.speechSynthesis` with a Hebrew voice is
unreliable on Windows (no system Hebrew voice in most configurations). The
design correctly lists this as a TBD choice but should flag the Windows
platform gap explicitly as a deferred risk, since the primary exam scenario
(Israeli students in a proctored lab) likely includes Windows machines.

**Synthesis:** Accepted as an informational note. Add to §Risks in the
design stub: "Windows SpeechSynthesis Hebrew voice availability is
inconsistent — Cloud TTS is likely required for reliable letter synthesis
on exam-lab machines." No revision needed to the stub structure.

---

## R2 Synthesis Verdict

**Approved.** F37 stub design is well-formed. Activate via `@design-pipeline`
when the MVP player phase begins. The Windows TTS risk should be the first
item read by the MVP designer.

# R2 Adversary Challenge — N02/F20 Phonikud G2P Adapter

- **Feature:** N02/F20 (Phonikud G2P — whole-text IPA via phonemize())
- **Stance:** Adversary — challenges R1; defends design where R1 overreached
- **Date:** 2026-05-01

---

### Finding 5 (Critical): Wrong port method name — OVERTURN

**R1 stance:** Critical — R1 claimed the locked F03 port is `transliterate(text)` and
design.md's `grapheme_to_phoneme(text, lang)` is wrong.

**Verification:** Checked `tirvi/ports.py:67-76` directly:
```python
class G2PBackend(Protocol):
    def grapheme_to_phoneme(self, text: str, lang: str) -> G2PResult:
```

The locked port IS `grapheme_to_phoneme(text, lang)`. design.md §Interfaces is correct.
R1 made a factual error by citing `transliterate` (from the autonomous-design-run.md
locked-interfaces summary table which was stale / inaccurate for this port).

**Risk of following R1:** Renaming the adapter method to `transliterate` would break
the Protocol conformance check at runtime (`isinstance` would return False).

**Verdict:** OVERTURN. design.md Interfaces is correct. No action needed.

---

### Finding 1: API pivot test sweep — AGREE (MEDIUM)

**Verdict:** SUSTAIN MEDIUM. Add note to design.md DE-02 about per-token test
rewrites / skip marks.

---

### Finding 2: PlanToken.ipa=None — AGREE (MEDIUM)

**Verdict:** SUSTAIN MEDIUM. Add to §Out of Scope.

---

### Finding 3: Phonikud version pin — AGREE (LOW)

**Verdict:** SUSTAIN LOW.

---

### Finding 4: Zombie modules — AGREE (MEDIUM)

**Verdict:** SUSTAIN MEDIUM. Add to §Out of Scope.

---

### Findings 6-10: Sustain as assessed

- F6 (BT-101 deferred): Low — SUSTAIN
- F7 (FT-152 double-anchor): Low — SUSTAIN  
- F8 (HLD §5.3 hint field): Low — SUSTAIN
- F9 (in-process privacy): Low — SUSTAIN
- F10 (None propagation): Medium — SUSTAIN

---

## R2 Synthesis

### Overturned
- **F5 (Critical):** OVERTURN — locked port is `grapheme_to_phoneme` (verified from
  tirvi/ports.py); design.md is correct. No TDD block from this finding.

### No Critical issues remain

### Confirmed Medium (address before TDD)
1. F1: Add API pivot sweep note to design.md DE-02.
2. F2: Add PlanToken.ipa=None note to §Out of Scope.
3. F4: Add zombie module acknowledgment to §Out of Scope.
4. F10: Document None-propagation check in DE-01.

### Required design.md edits (minimal)
1. DE-02: Add transition note about per-token test rewrites.
2. DE-01: Add note about None-check before module.phonemize().
3. §Out of Scope: Add zombie modules + PlanToken.ipa=None notes.

### Gate
No Critical issues. All TDD tasks may proceed in dependency order.
T-02 is the key pivot task; T-01 (loader) is already green.

# R2 Adversary Challenge — N02/F23 SSML Shaping (POC minimum)

- **Feature:** N02/F23 (SSML shaping)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Finding 10: xml_escape Hebrew passthrough — SUSTAIN HIGH

**R1 stance:** High — verify xml_escape doesn't use html.escape and preserves Hebrew.

**Adversary assessment:** R1 is correct. `html.escape()` escapes `&` → `&amp;` and
`<` → `&lt;` but does NOT escape Hebrew codepoints — so using it is actually safe for
Hebrew. However, the risk R1 identifies is real: if a developer later adds
`html.escape(..., quote=True)`, the `"` and `'` escaping changes, and if they add any
non-standard normalization, Hebrew codepoints could be affected.

The round-trip test ("parse(escaped) == original") catches most issues. But the specific
assertion `xml_escape("כֹּל") == "כֹּל"` directly verifies the Hebrew passthrough case
and should be in the test suite.

**Verdict:** SUSTAIN HIGH (as verification requirement, not necessarily a code defect).
The task: add `assert xml_escape("כֹּל") == "כֹּל"` to `test_xml_escape.py` if not
already present.

---

### Findings 1-9: Confirmations and Low findings

Most R1 findings are confirmations of correct design. All sustained as Low.

- F7 (BT-118 negative assertion): Add "assert '<emphasis>' not in ssml" to T-05 tests.
  **SUSTAIN LOW.**

---

## R2 Synthesis

### Confirmed High (verification, not design defect)
1. **F10:** Add `assert xml_escape("כֹּל") == "כֹּל"` to test_xml_escape.py.

### Required design.md edits
None. F23 design is correct and complete.

### Gate
F23 is fully implemented (T-01–T-05 green). Only verification task: add Hebrew
codepoint test to xml_escape tests. Send to TDD session via mailbox.

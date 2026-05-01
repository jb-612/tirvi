---
title: Why the NLP models don't catch these issues — root-cause analysis
date: 2026-05-01
question: Can we replace hardcoded fixes with model-driven correction + feedback loop?
---

# Why each fix is hardcoded today

| Issue | Root cause | Why DictaBERT/YAP/Nakdan can't catch it |
|---|---|---|
| `גורס` ↔ `גורם` | Tesseract OCR character confusion | `גורס` is a real Hebrew word (verb "crushes"). All models accept it. They never see the original PDF — only the wrong string. |
| `לנבחן/ת` slash | Hebrew typographic convention, not a word | NLP models tokenize on whitespace and treat `/` as punctuation. DictaBERT ignores it; Phonikud reads `ת` alone as a letter name. |
| `(''סגורות'')` wrap | Tesseract preserves typographic quotes | Nakdan reads trailing `''` as Hebrew gershayim ״ (acronym marker) and adds `ָא`. Models trained on clean text. |
| `כָּל` → "kol" not "kal" | Kamatz katan phonology | Phonikud's G2P model wasn't trained with explicit kamatz-katan tagging. Its training corpus has `ָ → /a/` weighted way more than `ָ → /o/`. |
| Block-end falling intonation | Wavenet TTS prosody choice | Wavenet treats `<break>` as sentence boundary even at 100ms. No way to override prosody from outside. |

## The pattern

Each "hardcoded fix" sits at a different layer:
- **OCR errors** belong in a **vision-aware language model** (DictaBERT can score sentence likelihood and prefer correct alternatives — but not character-level OCR alternatives without help).
- **Typographic stripping** belongs in a **pre-Nakdan cleaner** (which is what we did, but it can grow).
- **Phonological choice** (kamatz katan) belongs in a **Phonikud variant** trained on tagged data.
- **Prosody** belongs in **TTS itself** (Wavenet has limited control).

## Where models CAN help right now

### 1. DictaBERT-MLM for OCR correction (replaces F-2 hardcoded list)

DictaBERT is a Masked Language Model. We can score the likelihood of each
OCR word *in context* and only accept high-probability words. For a
suspicious word (low MLM score), we try character-substitution candidates
and pick the highest-scoring one.

```python
# Pseudocode
for word in ocr_words:
    if mlm_score(word, context) < threshold:
        candidates = [
            word.replace("ס","ם"),   # final-letter swaps
            word.replace("ו","ן"),
            word.replace("ק","ך"),
            ...
        ]
        word = argmax(c for c in candidates: mlm_score(c, context))
```

This generalizes the fix list to ANY ם/ס confusion, plus any other
character pair Tesseract confuses, without enumeration.

### 2. NLP-aware Nakdan candidate scoring (already wired, can be tuned)

`diacritize_in_context` already scores Nakdan candidates against
`token.pos` (weight 2) and morph features (weight 1 each). When DictaBERT
is highly confident (`token.confidence > 0.9`), boost POS weight to 5+
to make NLP context dominant in candidate selection.

### 3. Phonikud post-processing via NLP context

Kamatz katan rules can be derived from POS + lemma:
- Verbs in pa'al binyan with kamatz in unstressed syllable → kamatz katan
- Specific lemmas (כל, חכמה, etc.) → kamatz katan in compounds

DictaBERT gives us POS + lemma. We can write rules that fire on those
instead of hardcoded surface forms — generalizes to any inflection.

## The feedback loop

A practical RL-light approach without training infrastructure:

```
┌────────────┐   user marks word as mispronounced
│  Player UI │ ────────────────────────────────────┐
└────────────┘                                     ▼
                                          ┌─────────────────┐
                                          │ correction.json │
                                          │  per-version    │
                                          │  per-word marks │
                                          └────────┬────────┘
                                                   │
        ┌──────────────────────────────────────────┘
        ▼
┌───────────────────┐    aggregate across runs    ┌──────────────────┐
│ corrections_db    │ ─────────────────────────► │ auto-generated   │
│ (sqlite)          │                            │ fix_lists.py     │
└───────────────────┘                            └──────────────────┘
```

Components:

1. **Inspector tab "Mark as wrong"** — already we have notes; add per-word
   "report mispronunciation" with optional correct form
2. **Local sqlite** — `(sha, mark_id, ocr_word, heard_as, expected, ts)`
3. **Aggregation script** — when same correction appears N≥3 times across
   runs, append to fix list automatically and commit a PR-style suggestion
4. **MLM-based auto-suggest** — when user reports a wrong word, run
   DictaBERT-MLM with the surrounding context and propose top-5 alternatives
   for the user to pick from

This is human-in-the-loop reinforcement, not full RL — but it scales
because each correction generalizes via MLM to similar errors.

## True RL options (longer horizon)

If we want full RL fine-tuning on M4 Max:

### Option A — Phonikud LoRA fine-tune
- Phonikud is small (~50M params)
- Collect (vocalized_word, IPA, was_correct) tuples from feedback
- LoRA fine-tune on Mac MPS (4-8 hours for 10k examples)
- Replace baseline Phonikud with domain model

### Option B — DictaBERT OCR correction head
- Add a small classifier head: "is this word an OCR error?" (binary)
- Train on synthetic data: take clean Hebrew, apply Tesseract-like noise
  patterns (ם↔ס, ן↔ו, etc.), mark as error
- Fine-tune for 2-4 hours on M4 Max
- Wire into pipeline before Nakdan

### Option C — Listen-and-correct RLHF
- User clicks "wrong" on misplayed word
- Record audio segment + expected text
- Train a quality classifier (audio → "matches text? yes/no")
- Use as reward signal for Phonikud fine-tuning
- Most expensive but highest quality

## Concrete next step

Implement **DictaBERT-MLM word-substitution** to replace the
`_KNOWN_OCR_FIXES` hardcoded list. For each OCR word:

1. Compute MLM log-probability in context
2. If below threshold, generate character-substitution candidates
3. Score each candidate; pick highest if it beats the original by margin
4. Write to `corrections.log` for review

This gets us:
- ✓ No more hardcoded ם/ס list
- ✓ Generalizes to any Tesseract confusion pair
- ✓ Self-improves as DictaBERT improves
- ✓ Audit trail of corrections

Effort: 1-2 hours implementation. Replaces a list that would otherwise
grow indefinitely.


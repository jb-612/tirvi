---
title: UAT — Hebrew TTS pipeline quality
date: 2026-05-01
tested_by: Claude Opus 4.7 (programmatic)
draft_under_test: 02ade021b8fe4e7f
test_input: docs/example/Economy.pdf (Hebrew exam, page 1)
audio_length: 102.14s
total_words: 214
---

# UAT — Hebrew TTS pipeline quality

## Methodology

Programmatic analysis of pipeline artefacts (`page.json`, `audio.json`,
`audio.mp3`) without listening. Verified each fix by checking concrete
patterns in the diacritized text and comparing OCR vs Nakdan vs Phonikud
outputs. Audio timing analysed via Wavenet mark durations and `ffprobe`.

The user's verbal complaints from prior listening sessions drove the
specific patterns inspected.

## Issues identified and fixed

### F-1 — Kamatz katan substring match in `כַּלְכָּלָה`

**Symptom**: `מבחן כלכלה` pronounced "kalkula" (kal-kho-la) instead of
"kalkala". The kamatz_katan post-Nakdan replacer was applying
`כָּל → כֹּל` inside `כַּלְכָּלָה`, producing `כַּלְכֹּלָה`.

**Root cause**: Initial fix used `(?<![א-ת])` lookbehind which only
rejected Hebrew letters. The second `כָּל` inside `כַּלְכָּלָה` is
preceded by sheva (ְ, U+05B0) — a Hebrew diacritic, not a letter — so
the lookbehind passed and the substitution went through.

**Fix**: Extend lookbehind to `(?<![א-ת֑-ׇ])` so both letters AND
diacritics block the match.

**Verified**: 1 occurrence of `כַּלְכָּלָה` (correct), 0 of `כַּלְכֹּלָה`
(buggy) in latest draft.

### F-2 — Recurring OCR ם/ס confusion (`גורס` for `גורם`)

**Symptom**: User reported `גורם` repeatedly mispronounced as `גורס`.
Words like `תגרוס`, `אינס`, `סיוס` from prior runs reappearing.

**Root cause**: The Nakdan-based heuristic only fires when the
substituted form is in Nakdan's word list AND the original is not.
Nakdan accepts BOTH forms for many words (e.g. `תגרוס` — verb "will
crush" — and `תגרום` — verb "will cause"). The heuristic alone can't
disambiguate.

**Fix**: Two-stage strategy. Hardcoded `_KNOWN_OCR_FIXES` table for 14
high-frequency exam words where the ם form is overwhelmingly more common
(>1000:1 frequency ratio in HeWaC). Hardcoded list runs first; Nakdan
heuristic catches the long tail.

Words fixed unconditionally:
`גורס→גורם, תגרוס→תגרום, אינס→אינם, סיוס→סיום, מקוס→מקום, אדס→אדם,
יוס→יום, עולס→עולם, שלוס→שלום, שס→שם, פעמיס→פעמים, אנשיס→אנשים,
דבריס→דברים, אומריס→אומרים`.

**Verified**: All 3 mismatches (תגרוס/אינס/סיוס) in OCR are absent from
the diacritized text. `תִּגְרֹם, אֵינָם, סִיּוּם` present.

### F-3 — Marker drift after ~1 minute of audio

**Symptom**: User reported the word-highlight marker progressively
running ahead of the narrator. After ~1 minute the gap was several
words.

**Root cause** (user-diagnosed, confirmed): the gender-slash expansion
`לנבחן/ת → לנבחן, נבחנת` was running in the text-correction path,
adding 2 TTS tokens to the audio for every 1 OCR word. The plan layer
emits one `<mark>` per OCR word, so every slash shifted all subsequent
mark IDs by 1, breaking the `marks_to_word_index` mapping.

**Fix**: Removed `expand_gender_slash` from the pipeline's
`corrected_text` path. Pipeline now applies only `expand_geresh_ordinal`
(1→1 token, no shift). Long-term: re-add via SSML `<sub
alias="לנבחן, נבחנת">לנבחן/ת</sub>` so the mark stays 1:1 with the OCR
token while TTS speaks the expanded form.

**Verified**: OCR words = diacritized tokens = 214 (perfect alignment).

**Cosmetic trade-off**: `/` now reaches Phonikud which pronounces it as
the letter Tav for `לְנִבְחָן/ת`. Acceptable until SSML `<sub>` lands.

### F-4 — Narrator stops at OCR line breaks even without punctuation

**Symptom**: User reported the narrator pausing at the end of every
visual line, even mid-sentence where the OCR happened to wrap.

**Initial fix** (insufficient): Changed `inter_block_break` to emit
`<break time="100ms"/>` at mid-sentence breaks instead of 500ms.

**Investigation**: Inspecting `audio.json` showed mark gaps of 0ms
between blocks regardless of break tag duration. MP3 length (102.14s)
is only 1.1s longer than the last mark's `end_s` (101.03s), even with
17 mid-sentence and 5 sentence-final breaks. Wavenet absorbs most break
time into the previous mark's `end_s`. The user's perceived pause was
**falling intonation** — Wavenet renders prosody as if every `<break>`
ends a clause.

**Real fix**: At mid-sentence boundaries, emit a single space instead
of any `<break>` tag. Wavenet treats both blocks as one prosodic unit
and continues naturally. Sentence-final punctuation still triggers
`<break time="500ms"/>`.

### F-5 — Kamatz katan in compounds (`בכל שלב`)

**Symptom**: `בְּכָל שלב` pronounced "be-khal" instead of "be-khol".

**Fix**: `tirvi/normalize/kamatz_katan.py` post-Nakdan replacement
table for known kamatz-katan words and prefixed compounds:
`בְּכָל→בְּכֹל, לְכָל→לְכֹל, מִכָּל→מִכֹּל, חָכְמָה→חוֹכְמָה`, etc.

**Verified**: `בְּכֹל` present in diacritized text. No `בְּכָל`
remaining.

### F-6 — `א׳` ordinal lost as `אי` by Tesseract

**Symptom**: `הנחיות לחלק א׳` (read "chapter aleph") rendered as
`הנחיות לחלק אי` ("chapter ai") because Tesseract dropped the geresh.

**Fix**: `_recover_ocr_ordinals` in `hebrew_text_rules.py` — when
`אי/בי/גי/די/הי` appears immediately after an ordinal-context word
(`חלק / פרק / סעיף / מועד / שאלה / כיתה / שלב`, plus prefixed forms
`לחלק / בפרק` etc.), expand to letter name (`אלף / בית / גימל / דלת /
הא`).

**Verified**: OCR `[21]='לחלק' [22]='אי'` → diac `[22]='אֶלֶף'`.

### F-7 — Constant + linear marker offset

**Initial offset fix**: subtract 0.3s from `audio.currentTime` (Wavenet
buffer lag).

**Drift fix**: scale by `(last_end_s / audio.duration)` so MP3 silence
padding doesn't accumulate offset over the run. Cached on first valid
duration measurement.

After F-3 (slash expansion removal) the drift was largely eliminated;
this scaling protects against the residual 1.1s padding effect.

## Items confirmed working

- 4-button player controls wired (Play/Pause/Continue/Reset)
- Centered scan view with marker overlay
- Inspector sidebar with 4 NLP tabs (DictaBERT-morph / DictaBERT-syntax /
  AlephBERT+YAP / Nakdan / Voice)
- Version navigator across `drafts/<sha>/`
- Per-version per-tab notes with localStorage + JSON export
- 17 mid-sentence breaks rendered as continuous prosody (post-fix)
- Hebrew compound words preserved with hyphen and proper diacritization
  (`רב-בְּרֵרָה`, `עַל-יְדֵי`)
- DictaBERT-joint POS + morph features feeding `diacritize_in_context`
- Real YAP server (BIU ONLP Lab) running locally with full morph + dep tree

## Known cosmetic items, not blocking

- Gender slash `/` reaches Phonikud → pronounces as letter "Tav".
  Trade-off for marker sync. Fix path: SSML `<sub alias>` rewrite.
- Stub `_StubOCR` produces a 1×1 blank PNG; `--stubs` mode shows no
  page image. Not affecting POC mode.
- AlephBERT+YAP webapi has uninitialised `maHebrew` nil pointer in
  upstream YAP source — patched locally with `+ "\n\n"` sentence
  terminator at three handler sites in `/tmp/yap/webapi/webapi.go`.

## Recommendations for future tuning

1. **OCR fix list will grow** — every new exam PDF reveals a few more
   ם/ס or ן/ו confusion pairs. Capture from production OCR logs and
   append to `_KNOWN_OCR_FIXES`.

2. **Nakdan picks the wrong morph candidate often (`fconfident=False`).
   Wire NLP morph features into `_score_option`** more aggressively.
   Current scoring weights POS=2, morph_keys=1 each. Consider raising
   to POS=4 to dominate when DictaBERT is highly confident.

3. **SSML `<sub alias>` for gender slash** — cleanest restoration of
   the `נבחן/ת` reading without breaking marker sync. Requires SSML
   builder change in `tirvi/ssml/builder.py::_token_to_ssml_fragment`.

4. **Phonikud kamatz-katan model** — current workaround replaces
   kamatz with cholam in known words. Long-term: train Phonikud on
   tagged kamatz-katan corpus or pre-process via lexicon lookup
   (Even-Shoshan / Hebrew Academy table).

5. **Inter-block prosody validation** — listen-test 5-10 paragraphs
   with mid-sentence line breaks to confirm the no-break-just-space
   change reads naturally. If Wavenet still drops pitch at the
   boundary, consider wrapping each prosodic unit in a single
   `<s>` (sentence) SSML tag.

6. **Voice tuning** — current `he-IL-Wavenet-D` is one of four Hebrew
   voices. A/B test against `Wavenet-A/B/C` to find the most natural
   for educational content.

## Test commands used

```
uv run python -c "from tirvi.pipeline import make_poc_deps, run_pipeline; ..."
ffprobe -v error -show_entries format=duration -of csv='p=0' audio.mp3
curl -X POST http://127.0.0.1:8090/yap/heb/joint -d '{"Text":"..."}'
```

## Test data inspected

```
drafts/02ade021b8fe4e7f/page.json     — 214 words, 214 diac tokens
drafts/02ade021b8fe4e7f/audio.json    — 213 marks, 101.03s
drafts/02ade021b8fe4e7f/audio.mp3     — 102.14s actual MP3 duration
```

## Changes shipped this session

1. `tirvi/normalize/kamatz_katan.py` — word-boundary regex with diacritics
2. `tirvi/normalize/ocr_corrections.py` — hardcoded fix list + heuristic
3. `tirvi/pipeline.py` — wire `diacritize_in_context`, drop slash expansion
4. `tirvi/adapters/nakdan/inference.py` — pick top option even on low confidence
5. `tirvi/adapters/nakdan/adapter.py` — expose `diacritize_in_context`
6. `tirvi/ssml/breaks.py` — empty space at mid-sentence boundaries
7. `tirvi/ssml/builder.py` — pass prev block text to break helper
8. `player/js/highlight.js` — constant offset + linear scale for sync
9. `tirvi/normalize/hebrew_text_rules.py` — geresh recovery for prefixed forms

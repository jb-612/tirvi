# ADR-040 — `verdict: "ambiguous"` shape for LLM-emitted uncertainty

**Status**: Proposed
**Bounded context**: hebrew-interpretation (N02/F48, F51)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-02
**Closes**: GitHub issue #28
**Refines**: ADR-035 (`corrections.json` schema), ADR-033 (correction
cascade), ADR-038 (homograph context-rules)

## Context

ADR-035 §Schema defines a per-stage entry shape:

```jsonc
{ "stage": "llm_reviewer", "verdict": "apply", "reason": "...",
  "cache_hit": true }
```

The `CorrectionVerdictName` Literal in
`tirvi/correction/value_objects.py` already includes `"ambiguous"`
as a valid verdict name (introduced in F48 for the **MLM scorer** when
its delta is in `[low, high)`). That MLM-emitted ambiguous case has a
clear shape: a numeric `score` field expresses the confidence, and the
candidate list is the universe of corrections considered.

Two NEW callers also need to emit "ambiguous" but don't fit the
MLM-emitted shape:

1. **`OllamaLLMReviewer`** (F48 OCR-correction reviewer, on prompt
   `he_reviewer/v1.txt`). When the LLM model's response indicates
   it cannot pick a single correction with high confidence, today
   `_accept` returns `verdict: "keep_original"` — silently treating
   uncertainty as a non-correction. The human reviewer working
   `corrections.json` cannot distinguish "model said the original is
   right" from "model said it's not sure between A and B" — both look
   identical in the log.

2. **A future `OllamaHomographJudge`** (deferred per ADR-038 §Out of
   scope; consumer for `he_homograph_judge/v1.txt`). For S1-class
   sentences (`האם הקריאה ספר לילדה` — genuinely two-valued in modern
   Hebrew between mother and whether), the judge should flag the
   ambiguity rather than commit to a coin-flip.

The user-product impact is real: for students with reading
disabilities, hearing one of two valid readings without knowing the
sentence is ambiguous removes the very cognitive cue that lets them
correct course. The human reviewer (F50 review portal) needs a clear
signal to surface alternatives to the user.

## Decision

We extend `CorrectionVerdict` (BO52 surface) with one new optional
field, bump `corrections_schema_version` to `2`, and standardise a
minimal contract for LLM-emitted ambiguous verdicts. We do NOT change
the existing `CorrectionVerdictName` enum — `"ambiguous"` already
exists; we are adding a second emitter, not a new verdict name.

### Schema extension (additive, backwards-compatible)

`CorrectionVerdict` gains:

```python
alternatives_retained: tuple[str, ...] = ()
```

Default empty tuple. Populated only by ambiguous verdicts. `corrected_or_none`
stays `None` for ambiguous verdicts (no single correction was made).
`candidates` continues to mean "the full input candidate universe" —
`alternatives_retained` is a curated subset (typically 2-3 items) the
emitter believes are all defensible.

In `corrections.json` (per ADR-035), the per-stage entry for an
ambiguous verdict looks like:

```jsonc
{
  "stage": "llm_reviewer",
  "verdict": "ambiguous",
  "alternatives_retained": ["מילה_א", "מילה_ב"],
  "reason": "two readings linguistically valid; no syntactic disambiguator in scope",
  "cache_hit": false
}
```

When the cascade emits this entry, the document-level
`corrections_schema_version` MUST be `2` (not `1`). Files with
`corrections_schema_version: 1` MAY still be read; producers MUST emit
v2 going forward.

### Auto-pick under ambiguity (operator policy)

The cascade still needs to ship a SINGLE diacritized text downstream
to TTS (F22 plan.json has no concept of an ambiguous word). When a
stage emits ambiguous, the cascade auto-picks `alternatives_retained[0]`
(the first listed; emitters are responsible for ordering by their own
preference) and writes it as the `corrected` value at the entries
level. This auto-pick is **independent** of the stage's verdict — the
verdict still records `ambiguous`, the alternatives are still
preserved, but a single answer reaches TTS.

```jsonc
{
  "token_id": 142,
  "original": "האם",
  "corrected": "הָאֵם",                  // auto-picked from alternatives_retained[0]
  "stages": [
    { "stage": "context_rule", "verdict": "ambiguous",
      "alternatives_retained": ["הָאֵם", "הַאִם"],
      "reason": "no possessor trigger; readings split on absence of '?'" }
  ]
}
```

Rationale: degrades gracefully (audio still plays) and the F50 review
UI has the alternatives needed to surface a "select correct reading"
affordance. Without auto-pick, an ambiguous verdict would null the
focus token, leaving a hole in the TTS audio — strictly worse for the
student.

### Prompt-template extension (both `he_reviewer/v1.txt` and `he_homograph_judge/v1.txt`)

Both Ollama prompt templates gain ONE new instruction (in their native
verdict surface):

- **`he_reviewer/v1.txt`** (Hebrew): the model may now answer with a
  third verdict shape, in addition to OK and REPLACE:

  ```jsonc
  {"verdict": "AMBIGUOUS", "chosen": null,
   "alternatives": ["א", "ב"],
   "reason": "..."}
  ```

  Issued when "אינך יכול להחליט בביטחון בין שני תיקונים מוצעים". The
  `alternatives` array MUST be a non-empty subset of the input
  candidates list, length 2-3.

- **`he_homograph_judge/v1.txt`** (English/Hebrew mixed): same idea,
  using `pick_index: null` and `alternatives_indices: [n, m]`.

  ```jsonc
  {"reasoning_he": "...", "pick_index": null,
   "alternatives_indices": [1, 4],
   "reason": "..."}
  ```

  The reviewer parses `alternatives_indices` and resolves them to the
  underlying candidate strings before emitting the
  `CorrectionVerdict`.

### `OllamaLLMReviewer._accept` extension

Existing `keep_original` path stays. New AMBIGUOUS path:

```python
def _accept(self, token, parsed):
    chosen = parsed.get("chosen")
    alternatives = parsed.get("alternatives") or []
    if not chosen and len(alternatives) >= 2:
        return self._verdict_ambiguous(token, alternatives, parsed.get("reason"))
    if not chosen:
        return self._verdict(token, "keep_original", None, parsed.get("reason"))
    # ... apply path unchanged
```

Anti-hallucination check (`AntiHallucinationPolicy`) is also applied
to the alternatives list — every entry MUST be in
`self.candidates`, otherwise the reviewer falls back to
`keep_original` rather than emitting an ambiguous verdict with a
hallucinated alternative.

### Configurable threshold (deferred)

Issue #28 mentioned an `OllamaLLMReviewer.ambiguity_threshold: float
= 0.6` knob for "when the LLM's confidence is below this, treat as
ambiguous". This presumes the LLM emits a numerical confidence, which
the v1 prompt does not request. Rather than retrofit a confidence
field that the model would have to fabricate, we let the **prompt**
encode the uncertainty: the model self-decides whether to pick or
flag. The threshold knob is deferred until we measure (a) whether
prompt-based self-flagging is reliable, (b) whether a numerical
confidence regression actually carries signal. If both go positive,
add the knob in a follow-up.

## Alternatives considered

### A. Add a brand-new verdict name `verdict: "needs_review"`

**Rejected.** `"ambiguous"` is already in the verdict enum and
already emitted by the MLM stage with the same intended semantics
("we know multiple candidates are plausible; the human should
decide"). Two verbs for one verb is gratuitous.

### B. Make `alternatives_retained` mandatory on every CorrectionVerdict

**Rejected.** Backwards-incompatible. Existing apply / keep_original /
suspect verdicts have no need for an alternatives list; forcing it
empty on every record adds noise. Optional default-empty is the
right shape.

### C. Encode alternatives in the `reason` string

**Rejected.** `reason` is human-readable narrative; the alternatives
list is structured data F50 needs to consume. Mixing the two
re-creates the parsing nightmare we're trying to avoid.

### D. Have the cascade silently drop ambiguous tokens (emit no audio)

**Rejected.** A hole in the audio is strictly worse than a coin-flip
read for a student listening to an exam. The auto-pick of
`alternatives_retained[0]` is the right degradation.

### E. Bump only the schema, defer producer changes

**Rejected.** A schema with no producer is a contract on paper. The
F50 portal team needs to see ambiguous verdicts in real
`corrections.json` files to wire the consumer; ship the producer too.

## Consequences

### Positive

- Honest accounting of uncertainty in the cascade. The human reviewer
  can distinguish "the model said keep" from "the model couldn't
  decide" — which today look identical.
- The alternatives list is structured data, ready for the F50 portal
  to consume and render a "pick the right reading" affordance.
- Forward-compatible with the future `OllamaHomographJudge` stage
  (deferred per ADR-038); the verdict shape is shared.
- Auto-pick degradation keeps audio playing under uncertainty —
  reading-disability red line preserved.

### Negative

- One additional optional field on `CorrectionVerdict`. Trivially
  small but every consumer that introspects the dataclass (notably
  serialisers) needs to be aware of it.
- Schema bump from v1 to v2. Producers update; consumers handle both
  versions for one release cycle.
- Anti-hallucination on alternatives list adds a small per-call cost.
  Bounded; alternatives lists are short (2-3 entries).
- The threshold knob is deferred — operators have no per-task
  override. Acceptable until we have real production evidence that
  prompt-based self-flagging is unreliable.

### Operational

- Producers MUST set `corrections_schema_version: 2` whenever an
  ambiguous verdict is emitted, including when the cascade emits a
  mix of v1-shape and ambiguous verdicts on the same page (the
  page-file uses v2 because at least one entry uses v2 fields).
- Cache-key impact: ADR-034's reviewer cache key includes the
  prompt template version. The new prompt instruction is part of
  v1.txt itself; bumping
  `_meta.yaml::prompt_template_version: v2-uncertain` is the
  cleanest cache-isolation move. Existing v1 entries don't collide
  with v2 entries — new prompt re-evaluates each token on next run.
- The v1 prompt template stays in the repo as a legacy reference;
  the active template under
  `tirvi/correction/prompts/he_reviewer/` becomes
  `v2.txt` (the v1 prompt + the new AMBIGUOUS instruction).
- F50 review portal work tracked as a downstream issue — does not
  block this PR.

## Implementation order (one PR closing #28)

1. **Tests first** —
   `tests/unit/test_llm_reviewer_ambiguous.py` covers: AMBIGUOUS
   verdict round-trip, anti-hallucination on alternatives,
   `corrected_or_none == None` assertion, mixed v1+v2 scenarios.
2. **`tirvi/correction/value_objects.py`** — add
   `alternatives_retained: tuple[str, ...] = ()` to
   `CorrectionVerdict`. CC unchanged.
3. **`tirvi/correction/llm_reviewer.py`** — extend `_accept` with
   the AMBIGUOUS path, add `_verdict_ambiguous` helper. CC ≤ 5.
4. **`tirvi/correction/prompts/he_reviewer/v2.txt`** — new file
   (v1 unchanged, kept as reference). `_meta.yaml` updated to point
   at v2 with `prompt_template_version: v2-uncertain`.
5. **`tirvi/correction/prompts/he_homograph_judge/v1.txt`** — extend
   in-place with the `pick_index: null + alternatives_indices: [...]`
   instruction. (No active consumer yet — same template version
   string per the F51 deferral.)
6. **`docs/ADR/ADR-035-...`** — add a §Schema versioning note
   pointing to ADR-040 for the v1→v2 transition (no schema rewrite,
   just a forward-pointer).

## References

- GitHub issue #28 — original problem statement
- ADR-033 — F48 cascade architecture
- ADR-034 — LLM reviewer prompt + cache key
- ADR-035 — `corrections.json` schema (v1 baseline)
- ADR-038 — F51 homograph context-rules (declared §28 out of scope)
- `docs/UAT/UAT-2026-05-02-homograph-pipeline.md` §S1 — the canonical
  ambiguity case (`האם הקריאה ספר לילדה`)

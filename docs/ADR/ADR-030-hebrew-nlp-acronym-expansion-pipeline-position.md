# ADR-030: Acronym expansion runs upstream of NLP (post-F14, pre-F17)

**Status:** Proposed

## Context

Biz corpus E03-F03 (`F15-acronym-lexicon`) commits the project to
deterministic, lexicon-driven expansion of Hebrew acronyms and
abbreviations (`ד״ר → דוקטור`, `עמ׳ → עמוד`, etc.). The HLD positions
acronym handling inside §5.2 step 3 — the *pronunciation-hint
generation* substep, after morphology has already run on the original
text. That ordering inherits from the older AlephBERT/YAP pipeline,
where acronym tokens were tagged but expansion happened later, near
SSML shaping.

Two practical signals make that ordering wrong for the tirvi POC stack:

1. The POC NLP backbone is **DictaBERT-morph** (per ADR-026). Its
   tokenizer is a HuggingFace WordPiece-style tokenizer trained on
   modern Hebrew. Tokens containing geresh `׳` or gershayim `״` are
   frequently split mid-glyph or shattered into per-character pieces,
   which corrupts POS / morph signals on the surrounding context.
2. Downstream consumers — F17 (NLP), F19 (Nakdan diacritization), F20
   (Phonikud G2P) — would each have to special-case acronym tokens to
   skip pronunciation. Routing the spell-out fallback through one
   metadata flag emitted upstream is mechanically simpler than five
   adapters each reproducing the same heuristic.

F15 must also preserve the bbox→span map established by F14
(invariant: union of `src_word_indices` across output spans equals
union across input spans), and must surface `original_form` +
`lexicon_version` provenance so the player feedback affordance and
F22 reading plan can reference what was originally read on the page.

The HLD §12 open question on domain-aware disambiguation (`חז״ל` vs
`ת״ז`) is orthogonal to the position decision and is parked: v1 takes
the top lexicon entry; `AcronymEntry.context_tags` is a reserved slot
for the MVP iteration.

## Decision

**Acronym expansion runs as a dedicated pipeline stage between
F14 normalize and F17 DictaBERT NLP.** F15 consumes the
`NormalizedText` value type emitted by F14 and produces an
`ExpandedText` value type that extends the same shape with two added
fields: `expansion_log: tuple[ExpansionLogEntry, ...]` and
`lexicon_version: str`. Every downstream stage consumes the
`ExpandedText.text` field instead of `NormalizedText.text`.

Three behaviours follow directly from the position:

1. **Whole-token lookup against a YAML-backed lexicon.** When a span's
   surface (after stripping trailing sentence-final punctuation) is in
   the lexicon, the span is rewritten to the expansion. F17 then
   tokenises the expanded Hebrew form, which behaves cleanly.
2. **Spell-out fallback for unknown acronym candidates.** When the
   matcher heuristic (`is_acronym_candidate`: contains geresh /
   gershayim, or all-Latin uppercase length 2-6) fires and the lexicon
   misses, F15 emits an `ExpansionLogEntry(spell_out=True)` and leaves
   the surface unchanged. F23 SSML reads the flag and emits per-letter
   `<break>`. F17 NLP also receives the original token, but the
   spell-out routing at F23 means downstream pronunciation is
   bypassed — DictaBERT's confidence on those tokens is irrelevant.
3. **Provenance round-trip.** `ExpansionLogEntry` carries
   `original_form`, the `expansion`, and the `src_word_indices` from
   the input span. F22 reading plan stamps these per `PlanToken` so
   the player's "this was read wrong" affordance can surface
   "ד״ר → דוקטור" verbatim.

Bounded context: `hebrew-interpretation`. The new code lives at
`tirvi/acronym/`, not `tirvi/normalize/` — it is conceptually a
distinct stage, and folding it into the F14 module would muddy the
narrow scope F14 currently owns (artifact repair, span preservation).

## Consequences

Positive:

- DictaBERT operates on clean Hebrew, removing a class of tokenisation
  pathologies. Expected lift on FT-106 / FT-107 / FT-108 acceptance.
- Single point in the pipeline owns the `spell_out` decision; F19,
  F20, F23 all read one flag instead of duplicating heuristics.
- Provenance is preserved end-to-end without wiring extra fields
  through F17 / F18 / F19. `ExpansionLogEntry` travels with
  `ExpandedText` and is projected onto `PlanToken` by F22.
- Pure-domain feature — no external services, no new ports. Tests
  are deterministic; no GPU / network dependencies.
- The shape of `ExpandedText` is a strict superset of
  `NormalizedText`, so F17 and F22 can be ported with one type
  substitution and a passthrough on the new fields.

Negative:

- The HLD §5.2 step ordering is now formally diverged. Future
  contributors reading the HLD will need to consult ADR-030 to learn
  why §5.2 step 3 is split. The HLD Deviations row in F15's design.md
  cross-references this ADR.
- Sub-token / embedded acronym matching (`לדר״ר`) is harder to add
  later because the matcher is span-anchored. The MVP follow-up is
  modest (regex pre-pass before lookup), but does require revisiting
  this position.
- A maintainer who edits the lexicon YAML but forgets to bump
  `version` produces silently-newer expansion semantics with the same
  audit stamp. Mitigated by DE-08 lint CLI requiring `version` and
  rejecting duplicates; not eliminated.

## Alternatives

- **Expand inside F14 normalize.** Rejected because F14's scope is
  artifact repair / span preservation, not lexicon-driven token
  rewriting; folding both into one module makes regressions harder
  to bisect and breaks the per-feature ADR-019 / ADR-030 split. The
  audit log (`repair_log` vs `expansion_log`) would also conflate
  two separate concerns.
- **Expand at SSML stage (F23), after F22 reading-plan assembly.**
  Rejected for two reasons: (a) DictaBERT still tokenises raw
  gershayim glyphs, so F17 / F19 quality regress; (b) the player
  highlight box would step on per-letter pieces of `ד״ר` rather than
  the whole token, breaking the synchronised highlight UX even when
  the underlying audio is correct. The HLD's original ordering would
  have been viable on the AlephBERT/YAP stack; on DictaBERT it is
  not.
- **Always emit `spell_out=true` and let F23 do letter-by-letter
  for every acronym.** Rejected because biz corpus FT-106 / FT-107
  explicitly require natural-form audio for high-frequency acronyms
  like `ד״ר`. Letter-by-letter is the unknown-acronym fallback, not
  the default.
- **Expand inline inside F17 (DictaBERT adapter).** Rejected on the
  vendor-boundary discipline of ADR-029 — F17 is the DictaBERT
  adapter; introducing lexicon logic there entangles the adapter
  with domain rules.

## References

- HLD §5.1 — cleaned input contract (NormalizedText shape)
- HLD §5.2 step 3 — pronunciation-hint generation (the diverged step)
- HLD §12 OQ — domain-aware disambiguation (parked)
- Biz corpus E03-F03 / S01 / S02 — `.workitems/N02-hebrew-interpretation/F15-acronym-lexicon/`
- Related: ADR-017 (YAML fixture pattern reused for lexicon),
  ADR-019 (deterministic-rules-for-POC mirror in F14),
  ADR-026 (DictaBERT-morph tokenizer drives D-01),
  ADR-029 (vendor-boundary discipline — keeps lexicon logic out of F17)
- Sibling: F21 homograph-overrides — distinct registry; per-word
  diacritization rather than per-token expansion

# ADR-028: F20 adopts Phonikud `phonemize()` API; per-token transliteration deferred to MVP

**Status:** Proposed

**Updates:** ADR-003 (Nakdan + Phonikud stack — unchanged at vendor level; this ADR narrows the API contract). ADR-022 (in-process loader topology) is not affected.

## Context

The original F20 design specced Phonikud's `transliterate(text)` API, which returns a list of per-token dicts with shape `[{"ipa": str, "stress": int}, ...]`. The TDD'd inference module (`tirvi/adapters/phonikud/inference.py`) calls `module.transliterate(text)` accordingly.

On 2026-04-30 the demo run failed with `AttributeError: module 'phonikud' has no attribute 'transliterate'`. The currently-distributed Phonikud package (version 0.4.1, pulled from PyPI) ships `phonikud.phonemize(text, **kwargs) -> str` instead — a whole-text IPA string with inline stress markers — and does not expose `transliterate`. The TDD test suite passed because tests mocked the `transliterate` method on a `MagicMock`; the mock didn't catch the API drift.

Three options surface for F20:

1. **Pin Phonikud to a pre-API-change version.** Searching PyPI history, no version of `phonikud` exposes a `transliterate` returning per-token dicts; the package has always been string-output-oriented. The original F20 design appears to have assumed an API that never shipped.
2. **Adopt `phonemize()` and emit whole-text IPA.** Returns a single IPA string; loses per-token granularity but matches the actual package contract.
3. **Use a different G2P library (e.g., `epitran`).** Replaces the Bar-Ilan-rooted Phonikud with a different vendor; reverses ADR-003.

Per-token IPA was specified for downstream `<phoneme>` SSML injection. POC investigation reveals Wavenet `he-IL-Wavenet-D` does not have documented `<phoneme>` support for Hebrew; treating per-token IPA as a SSML input is unverified value. The POC's actual consumer of G2P output is the F33 debug viewer (Wave 4) — for which a whole-text IPA string is sufficient and inspectable.

## Decision

F20 adopts **Phonikud `phonemize(text, schema="modern", predict_stress=True, predict_vocal_shva=True)`** as the inference call. `G2PResult.phonemes` is a single-element list containing the whole-text IPA string, e.g. `["שa.lˈom heˈlel"]`. Per-token IPA splitting is **deferred to MVP** under one of two triggers: (a) Wavenet adds `<phoneme>` SSML support for Hebrew (or we switch to a TTS engine that does), or (b) the F33 debug viewer needs per-token IPA for word-level inspection.

When that trigger fires, F20 grows a per-token splitter that calls `phonemize()` once per word (paying the per-call overhead) and stores the per-token IPA in `G2PResult.phonemes` as a per-word list. The `G2PResult` schema does not need to change — only the populator does.

ADR-003 (Nakdan + Phonikud stack) and ADR-022 (in-process loader topology) remain in force.

## Consequences

Positive:

- **Restores a working G2P path.** The current pipeline uses `_StubG2P()` because of the API mismatch; this ADR unblocks the real Phonikud adapter.
- **No vendor change.** Same package, same loader pattern, same `import phonikud` lazy import. The TDD suite needs only the inference module and its tests rewritten.
- **Honest scope.** Removing per-token IPA from POC scope makes F23 (SSML) decisions cleaner — POC SSML stays as `<mark>` + `<break>` only; no `<phoneme>` complexity.
- **Debug-visible IPA.** F33 viewer can render the whole-text IPA string side-by-side with the diacritized text, which is sufficient for human verification of the pronunciation chain.

Negative:

- **No per-token IPA hint reaches Wavenet.** Wavenet has to derive pronunciation from the diacritized text alone (which it does well per ADR-025 + the v3 demo). This is the same constraint we already operate under; the ADR codifies it.
- **The F03 fakes for `G2PBackend` may need a shape adjustment** — current fakes likely emit per-token entries; downstream tests may need updates. Tracked in F03 backlog.
- **MVP per-token work is real cost** — per-call Phonikud invocations are non-trivial. Document this clearly so MVP planning doesn't underestimate.

## Alternatives

- **Stay with `transliterate()` and patch the package locally.** Rejected: forking a vendor for an API that never existed is hostile maintenance. The simplest fix is to use the API the package actually ships.
- **Switch to `epitran` or another G2P library.** Rejected: reverses ADR-003 (Bar-Ilan-rooted toolchain), and `epitran`'s Hebrew support is less invested than Phonikud's. Reconsider only if Phonikud is abandoned upstream.
- **Drop G2P entirely from POC.** Rejected: F33 debug viewer benefits from having an IPA artefact; staying with `_StubG2P()` permanently leaves a visible "stub" in the F33 stage tree without justification.

## Migration

The implementation pivot is mechanical:

1. `tirvi/adapters/phonikud/inference.py::_emit()` — change `module.transliterate(text)` to
   ```python
   ipa = module.phonemize(text, schema="modern", predict_stress=True, predict_vocal_shva=True)
   return G2PResult(provider=PROVIDER, phonemes=[ipa] if ipa else [], confidence=None)
   ```
2. `tests/unit/test_phonikud_inference.py` — replace `_fake_phonikud_module([{"ipa":...}])` helper with a fake that returns a string; tests for per-token entries become MVP-deferred (mark `pytest.mark.skip(reason="per-token IPA deferred to MVP per ADR-028")`).
3. `tirvi/pipeline.py::make_poc_deps()` — switch `g2p=_StubG2P()` back to `g2p=PhonikudG2PAdapter()` once tests are green.
4. F03 fakes in `pkg/testutil/fakes/` — adjust the `G2PBackend` fake to emit a 1-element string list.

## References

- HLD §5.2 — Processing (G2P stage)
- ADR-003 — Diacritization + G2P stack (unchanged)
- ADR-022 — Phonikud in-process loader (unchanged)
- N02/F20 design.md — feature design referencing this ADR
- Phonikud package: https://pypi.org/project/phonikud/ (v0.4.1)
- Phonikud source: https://github.com/thewh1teagle/phonikud
- Discovery context: 2026-04-30 demo run, attribute-error trace

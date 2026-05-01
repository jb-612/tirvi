# Scaffold Review — Gate 1 (L1 + L2)

**Verdict**: PASS

## Scope
- Layers: L1 (structure) + L2 (contracts).
- Files: `tirvi/correction/{__init__,domain/__init__,adapters/__init__,prompts/__init__,prompts/he_reviewer/{v1.txt,_meta.yaml},value_objects,ports}.py` (8).

## L1 checks
- Folder names match design.md DE-IDs: `correction/` matches DE-05 service home; `domain/`, `adapters/`, `prompts/` reflect L1 separation.
- `prompts/he_reviewer/v1.txt` placeholder + `_meta.yaml` carry `prompt_template_version` per ADR-034.
- No business logic in any `__init__.py`; only docstrings + `__all__ = []`.

## L2 checks
- Four ports defined per DE-01 (`ICascadeStage`, `NakdanWordListPort`,
  `LLMClientPort`, `FeedbackReadPort`); all `@runtime_checkable`; all
  single-method (T-01 hint matches).
- Verdict enum is `Literal[...]` not stringly-typed (ADR-029 boundary).
- `CorrectionVerdict` is frozen dataclass; carries every BO52 field
  (stage, verdict, original, corrected_or_none, score, candidates,
  mode, cache_hit, reason, model_versions, prompt_template_version).
- `CascadeMode` carved as VO with `name` + `reason` — ready for
  per-page invariant INV-CCS-005.
- `SentenceContext` carries `sentence_hash` (cache-key input per DE-03).
- No vendor types leak into ports (ADR-029 honoured).
- No infrastructure imports in `value_objects.py` / `ports.py` (DDD
  dependency direction).

## Findings
None blocking. Proceeding to L3.

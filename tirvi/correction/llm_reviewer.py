"""OllamaLLMReviewer — local Gemma reviewer with anti-hallucination guard (DE-04).

Spec: F48 DE-04.
AC: F48-S03/AC-01, F48-S03/AC-02, F48-S03/AC-03. T-04b.
ADR-033 (privacy: localhost only) + ADR-034 (cache key strategy).

Domain wrapper around ``LLMClientPort``. Builds prompt from
``prompts/he_reviewer/v1.txt``; loads ``prompt_template_version``
from sibling ``_meta.yaml``.

Anti-hallucination guard (INV-CCS-002) via ``AntiHallucinationPolicy``:
  - ``chosen ∈ candidates`` (LLM cannot invent words outside MLM proposals)
  - ``chosen ∈ NakdanWordList`` (chosen must be a real Hebrew word)

Parse-failure path (NT-02): one re-prompt with stricter prompt; second
failure → ``keep_original``.

Per-page LLM-call cap (BT-F-05) is checked via the ``CorrectionCascade``
aggregate's ``llm_cap_reached()`` before issuing each call.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .domain.policies import AntiHallucinationPolicy, PerPageLLMCapPolicy
from .ports import ICascadeStage, LLMClientPort
from .value_objects import CorrectionVerdict, SentenceContext


@dataclass
class OllamaLLMReviewer(ICascadeStage):
    """Stage 3 — local Gemma reviewer (DE-04)."""

    llm: LLMClientPort
    anti_hallucination: AntiHallucinationPolicy
    cap_policy: PerPageLLMCapPolicy = field(default_factory=PerPageLLMCapPolicy)
    model_id: str = "gemma4:31b-nvfp4"
    prompt_template_path: str = "tirvi/correction/prompts/he_reviewer/v1.txt"
    prompt_template_version: str = "v1-scaffold"
    temperature: float = 0.0
    seed: int = 0

    def evaluate(
        self, token: str, context: SentenceContext
    ) -> CorrectionVerdict:
        # TODO AC-F48-S03/AC-01 (T-04b): build prompt by substituting
        #   {sentence}, {original}, sorted({candidates}) into v1.txt.
        # TODO AC-F48-S03/AC-02 (T-04b): cache key per ADR-034:
        #   sha256(model_id || prompt_template_version || sentence_hash
        #          || sorted(candidates)).
        # TODO AC-F48-S03/AC-02 (T-04b): if cache_hit return cached verdict.
        # TODO BT-F-05 (T-04b): consult cap_policy / aggregate before call;
        #   if cap reached return verdict="keep_original" with cache_hit=False
        #   and reason="llm_call_cap_reached".
        # TODO AC-F48-S03/AC-01 (T-04b): call self.llm.generate(prompt,
        #   self.model_id, self.temperature, self.seed).
        # TODO NT-02 (T-04b): parse {verdict, chosen, reason}; on parse
        #   failure, retry with stricter prompt ONCE; on second failure
        #   return verdict="keep_original" reason="llm_parse_failure".
        # TODO INV-CCS-002 (T-04b): self.anti_hallucination.check(chosen,
        #   candidates); on violation return verdict="keep_original"
        #   reason="anti_hallucination_reject".
        # TODO AC-F48-S03/AC-03 (T-04b): on success return verdict="apply"
        #   with corrected_or_none=chosen and prompt_template_version
        #   stamped.
        raise NotImplementedError(
            "AC-F48-S03/AC-01..AC-03 / FT-320..FT-322 / NT-02 / NT-03 / "
            "INV-CCS-002 — TDD T-04b fills"
        )


__all__ = ["OllamaLLMReviewer"]

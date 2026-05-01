"""OllamaLLMReviewer — local Gemma reviewer with anti-hallucination guard (DE-04).

Spec: F48 DE-04. AC: F48-S03/AC-01, F48-S03/AC-02, F48-S03/AC-03. T-04b.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path

from .domain.policies import AntiHallucinationPolicy, PerPageLLMCapPolicy
from .errors import LLMWordListViolation
from .ports import ICascadeStage, LLMClientPort
from .value_objects import CorrectionVerdict, SentenceContext


def _read_meta_version(meta_path: Path) -> str | None:
    if not meta_path.exists():
        return None
    for line in meta_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("prompt_template_version"):
            _, _, val = s.partition(":")
            return val.strip().strip('"').strip("'")
    return None


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
    candidates: tuple[str, ...] = ()
    _calls_made: int = field(default=0, init=False, repr=False, compare=False)
    _verdict_cache: dict = field(default_factory=dict, init=False, repr=False, compare=False)
    _template: str = field(default="", init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        p = Path(self.prompt_template_path)
        self._template = p.read_text(encoding="utf-8")
        version = _read_meta_version(p.parent / "_meta.yaml")
        if version:
            self.prompt_template_version = version

    def evaluate(self, token: str, context: SentenceContext) -> CorrectionVerdict:
        cache_key = (token, context.sentence_hash, self.model_id,
                     self.prompt_template_version, tuple(sorted(self.candidates)))
        if cache_key in self._verdict_cache:
            return dataclasses.replace(self._verdict_cache[cache_key], cache_hit=True)
        if not self.cap_policy.can_call(self._calls_made):
            return self._cap_verdict(token)
        verdict = self._call_llm(token, context)
        self._verdict_cache[cache_key] = verdict
        return verdict

    def _call_llm(self, token: str, context: SentenceContext) -> CorrectionVerdict:
        prompt = self._build_prompt(token, context)
        self._calls_made += 1
        raw = self.llm.generate(prompt, self.model_id, self.temperature, self.seed)
        parsed = self._parse(raw)
        if parsed is None:
            raw = self.llm.generate(prompt, self.model_id, self.temperature, self.seed)
            parsed = self._parse(raw)
        if parsed is None:
            return self._verdict(token, "keep_original", None, "llm_parse_failure")
        return self._accept(token, parsed)

    def _accept(self, token: str, parsed: dict) -> CorrectionVerdict:
        chosen = parsed.get("chosen")
        if not chosen:
            return self._verdict(token, "keep_original", None, parsed.get("reason"))
        try:
            self.anti_hallucination.check(chosen, self.candidates)
        except LLMWordListViolation:
            return self._verdict(token, "keep_original", None, "anti_hallucination_reject")
        return self._verdict(token, "apply", chosen, parsed.get("reason"))

    def _parse(self, raw: str) -> dict | None:
        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "verdict" in data:
                return data
            return None
        except json.JSONDecodeError:
            return None

    def _build_prompt(self, token: str, context: SentenceContext) -> str:
        cands = ", ".join(sorted(self.candidates))
        return (self._template
                .replace("{original}", token)
                .replace("{sentence}", context.sentence_text)
                .replace("{candidates}", cands))

    def _cap_verdict(self, token: str) -> CorrectionVerdict:
        return self._verdict(token, "keep_original", None, "llm_call_cap_reached")

    def _verdict(
        self, token: str, name: str, chosen: str | None, reason: str | None
    ) -> CorrectionVerdict:
        return CorrectionVerdict(
            stage="llm_reviewer", verdict=name, original=token,
            corrected_or_none=chosen, candidates=self.candidates,
            reason=reason, prompt_template_version=self.prompt_template_version,
        )


__all__ = ["OllamaLLMReviewer"]

"""F23 — SSML shaping (per-block ``<speak>`` document builder).

Mutates F22's :class:`tirvi.plan.ReadingPlan` to populate per-``PlanBlock``
``ssml`` field with valid Wavenet SSML carrying ``<mark name="{token.id}"/>``
elements (mark-format pin documented in F23 design HLD-deviations).

Spec: N02/F23. Bounded context: ``bc:speech_synthesis``.
"""

from .builder import build_block_ssml, build_page_ssml, populate_plan_ssml

__all__ = ["build_block_ssml", "build_page_ssml", "populate_plan_ssml"]

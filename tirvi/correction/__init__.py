"""N02/F48 Hebrew correction cascade — package root.

Three-stage cascade (NakdanGate → DictaBERT-MLM → Ollama LLM reviewer)
that silently corrects OCR errors before F19 diacritization.

Layered (DDD-7L):
- ``ports``           — port Protocols (ICascadeStage, NakdanWordListPort,
                        LLMClientPort, FeedbackReadPort)
- ``value_objects``   — CorrectionVerdict, SentenceContext, CascadeMode,
                        UserRejection
- ``domain.cascade``  — CorrectionCascade aggregate (transient per-page)
- ``domain.events``   — domain events emitted by the cascade
- ``domain.policies`` — invariants (token-in==token-out, anti-hallucination,
                        per-page LLM cap)
- stage shells: ``nakdan_gate``, ``mlm_scorer``, ``llm_reviewer``
- ``service``         — CorrectionCascadeService orchestrator
- ``log``             — CorrectionLog writer (corrections.json)
- ``health``          — HealthProbe + degraded-mode policy
- ``feedback_aggregator`` — rule-promotion suggestions (engineer-gated)
- ``adapters``        — vendor-boundary adapters (ollama, sqlite-feedback)
- ``prompts``         — versioned LLM prompt templates
"""

__all__: list[str] = []

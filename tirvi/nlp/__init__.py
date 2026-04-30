"""F18 — NLP disambiguation: picks top-1 sense from F17 candidates.

Pure domain logic refining DictaBERT's NLPResult with confidence + morph
schema; ships ``assert_nlp_result_v1()`` contract helper that downstream
features call to defend against adapter drift.

Spec: N02/F18. Bounded context: ``bc:hebrew_nlp``.
"""

from .contracts import assert_nlp_result_v1
from .errors import DisambiguationError
from .value_objects import DisambiguatedToken

__all__ = ["DisambiguatedToken", "DisambiguationError", "assert_nlp_result_v1"]

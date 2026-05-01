"""F27 — HebPipe coref enrichment (deferred MVP stub).

Spec: N02/F27 DE-01. AC: US-01/AC-01. FT-144.
"""

from dataclasses import dataclass, field

COREF_ENABLED = False


@dataclass
class CorefResult:
    chains: list = field(default_factory=list)


def enrich_with_coref(nlp_result) -> CorefResult:
    """Return empty chains until COREF_ENABLED is True."""
    if COREF_ENABLED:
        raise NotImplementedError("F27 HebPipe coref deferred to MVP")
    return CorefResult(chains=[])


__all__ = ["COREF_ENABLED", "CorefResult", "enrich_with_coref"]

"""F23 — SSML builder functions.

Spec: N02/F23 DE-01, DE-02, DE-03, DE-04. AC: US-01/AC-01.
"""

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan

from .escape import xml_escape


def build_block_ssml(block: PlanBlock) -> str:
    """Build the SSML ``<speak>`` document for one PlanBlock (T-01).

    Invariants:
      - INV-SSML-001 (DE-01): wraps content in ``<speak xml:lang="he-IL">…</speak>``
      - INV-SSML-002 (DE-02): every token gets ``<mark name="{token.id}"/>`` pre-emit
      - INV-SSML-005 (F22 wire): mark format ``{block_id}-{position}`` per F23 HLD-deviation
        (the format flows from F22 via PlanToken.id; this builder does not invent IDs)

    The token's vocalized form (``diacritized_text``) is preferred over
    raw text — it drives Wavenet's pronunciation. When ``diacritized_text``
    is None the raw ``text`` is used as fallback.

    Inter-block ``<break>`` insertion (DE-03) and XML escape (DE-04) are
    landed in T-03 / T-04 respectively. ``populate_plan_ssml`` (T-05)
    composes builds at the plan level.
    """
    body = " ".join(_token_to_ssml_fragment(t) for t in block.tokens)
    return f'<speak xml:lang="he-IL">{body}</speak>'


def _token_to_ssml_fragment(token: PlanToken) -> str:
    """Mark + escaped surface form for one token. Diacritized text preferred (T-02)."""
    surface = token.diacritized_text if token.diacritized_text else token.text
    return f'<mark name="{token.id}"/>{xml_escape(surface)}'


def populate_plan_ssml(plan: ReadingPlan) -> ReadingPlan:
    """Return a new ReadingPlan with each block's ``ssml`` field populated.

    Invariants (named, TDD fills):
      - INV-SSML-006 (D-01): F22's ``ssml`` field is empty on input; this fills it
      - INV-SSML-007 (T-05): uses ``dataclasses.replace`` to preserve immutability
    """
    # TODO US-01/AC-01 (T-05): for each block, build ssml; rebuild plan via dataclasses.replace
    raise NotImplementedError

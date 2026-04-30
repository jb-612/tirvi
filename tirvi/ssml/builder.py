"""F23 — SSML builder functions.

Spec: N02/F23 DE-01, DE-02, DE-03, DE-04. AC: US-01/AC-01.
"""

from dataclasses import replace

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan

from .breaks import inter_block_break
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
    """Return a new ReadingPlan with each block's ``ssml`` field populated (T-05).

    Walks the plan in order. The first block's SSML is just
    ``<speak xml:lang="he-IL">…body…</speak>``. Each subsequent block
    leads with ``<break time="500ms"/>`` (T-03) inside the speak
    wrapper, so Wavenet pauses between blocks.

    Immutable: input plan is unchanged; new PlanBlock instances are
    constructed via :func:`dataclasses.replace`.

    Invariants:
      - INV-SSML-006 (D-01): F22's empty ``ssml`` field is filled here
      - INV-SSML-007: ``dataclasses.replace`` preserves frozenness
      - INV-SSML-008 (T-03 wire): inter-block break is the canonical 500ms
    """
    new_blocks = tuple(
        replace(
            block,
            ssml=_block_ssml_with_break(block, leading_break=(i > 0)),
        )
        for i, block in enumerate(plan.blocks)
    )
    return replace(plan, blocks=new_blocks)


def _block_ssml_with_break(block: PlanBlock, *, leading_break: bool) -> str:
    """Build a block's full SSML, optionally prefixed with a 500ms break."""
    body = " ".join(_token_to_ssml_fragment(t) for t in block.tokens)
    prefix = inter_block_break() if leading_break else ""
    return f'<speak xml:lang="he-IL">{prefix}{body}</speak>'

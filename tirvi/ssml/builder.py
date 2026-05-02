"""F23 — SSML builder functions.

Spec: N02/F23 DE-01, DE-02, DE-03, DE-04. AC: US-01/AC-01.
"""

from dataclasses import replace

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan

from .breaks import inter_block_break
from .chunker import chunk_block_tokens
from .escape import xml_escape

_INTRA_BLOCK_BREAK = '<break time="500ms"/>'


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
    body = _block_body_with_intra_breaks(block)
    return f'<speak xml:lang="he-IL">{body}</speak>'


def _block_body_with_intra_breaks(block: PlanBlock) -> str:
    """F53 — chunk long blocks at safe boundaries; emit intra-block break.

    Under-threshold blocks pass through unchanged (chunker returns one
    fragment). Over-threshold blocks split at the first safe boundary
    (punctuation or SCONJ conjunction); fragments join with the
    canonical 500ms break.
    """
    fragments, _breaks = chunk_block_tokens(list(block.tokens))
    return _INTRA_BLOCK_BREAK.join(
        " ".join(_token_to_ssml_fragment(t) for t in frag)
        for frag in fragments
    )


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
        _block_with_ssml_and_provenance(block, leading_break=(i > 0))
        for i, block in enumerate(plan.blocks)
    )
    return replace(plan, blocks=new_blocks)


def _block_with_ssml_and_provenance(
    block: PlanBlock, *, leading_break: bool,
) -> PlanBlock:
    """Build the block's SSML AND append F53 chunker provenance to
    its transformations[] field (per ADR-041 row #9).
    """
    fragments, breaks = chunk_block_tokens(list(block.tokens))
    body = _INTRA_BLOCK_BREAK.join(
        " ".join(_token_to_ssml_fragment(t) for t in frag)
        for frag in fragments
    )
    prefix = inter_block_break() if leading_break else ""
    ssml = f'<speak xml:lang="he-IL">{prefix}{body}</speak>'
    return replace(
        block,
        ssml=ssml,
        transformations=tuple(block.transformations) + tuple(breaks),
    )


def _block_ssml_with_break(block: PlanBlock, *, leading_break: bool) -> str:
    """Build a block's full SSML, optionally prefixed with a 500ms break."""
    body = _block_body_with_intra_breaks(block)
    prefix = inter_block_break() if leading_break else ""
    return f'<speak xml:lang="he-IL">{prefix}{body}</speak>'


def build_page_ssml(plan: ReadingPlan) -> str:
    """Single ``<speak>`` SSML document for the whole page (one TTS call).

    Inter-block breaks are punctuation-aware: 500ms only when the prior
    block ends with sentence-final punctuation, else 100ms (natural breath)
    so the narrator continues smoothly across mid-sentence line breaks.
    """
    parts: list[str] = []
    prev_block = None
    for i, block in enumerate(plan.blocks):
        body = _block_body_with_intra_breaks(block)
        if i > 0:
            prev_text = " ".join(
                (t.diacritized_text or t.text) for t in prev_block.tokens
            )
            parts.append(inter_block_break(prev_text))
        parts.append(body)
        prev_block = block
    return f'<speak xml:lang="he-IL">{"".join(parts)}</speak>'

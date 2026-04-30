"""F23 — SSML builder functions.

Spec: N02/F23 DE-01, DE-02, DE-03, DE-04. AC: US-01/AC-01.
"""

from tirvi.plan import PlanBlock, ReadingPlan


def build_block_ssml(block: PlanBlock) -> str:
    """Build the SSML ``<speak>`` document for one PlanBlock.

    Invariants (named, TDD fills):
      - INV-SSML-001 (DE-01): wraps content in ``<speak xml:lang="he-IL">…</speak>``
      - INV-SSML-002 (DE-02): every token gets ``<mark name="{token.id}"/>`` pre-emit
      - INV-SSML-003 (DE-03): inserts ``<break time="…ms"/>`` between blocks per type
      - INV-SSML-004 (DE-04): Hebrew NFD nikud preserved; XML escape excludes Hebrew block
      - INV-SSML-005 (F22 wire): mark format ``{block_id}-{position}`` per F23 HLD-deviation
    """
    # TODO US-01/AC-01 (T-01..T-04): assemble ``<speak>``, ``<mark>``, ``<break>`` elements
    raise NotImplementedError


def populate_plan_ssml(plan: ReadingPlan) -> ReadingPlan:
    """Return a new ReadingPlan with each block's ``ssml`` field populated.

    Invariants (named, TDD fills):
      - INV-SSML-006 (D-01): F22's ``ssml`` field is empty on input; this fills it
      - INV-SSML-007 (T-05): uses ``dataclasses.replace`` to preserve immutability
    """
    # TODO US-01/AC-01 (T-05): for each block, build ssml; rebuild plan via dataclasses.replace
    raise NotImplementedError

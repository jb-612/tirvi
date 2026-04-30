"""F23 — SSML contract validator (assert_ssml_v1).

Spec: N02/F23 DE-05. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-178. BT-anchors: BT-118.

``assert_ssml_v1(plan)`` validates a ReadingPlan whose ``ssml`` fields
have been populated by :func:`populate_plan_ssml`:

  - every block's ssml is non-empty
  - every block's ssml parses; root element is ``<speak>``
  - mark names across the plan are unique (matches PlanToken.id
    uniqueness invariant from F22 INV-PLAN-001)

Raises :class:`SSMLContractError` on any violation.
"""

from collections import Counter
from xml.etree import ElementTree as ET

from tirvi.errors import AdapterError
from tirvi.plan import ReadingPlan


class SSMLContractError(AdapterError):
    """Raised when the SSML contract is violated.

    Spec: N02/F23 DE-05. BT-anchors: BT-118.
    """


def assert_ssml_v1(plan: ReadingPlan) -> None:
    """Validate a populated ReadingPlan against the F23 SSML v1 contract."""
    _assert_every_block_populated(plan)
    parsed_roots = _parse_every_block(plan)
    _assert_every_root_is_speak(parsed_roots)
    _assert_unique_mark_names(parsed_roots)


def _assert_every_block_populated(plan: ReadingPlan) -> None:
    for block in plan.blocks:
        if not block.ssml:
            raise SSMLContractError(
                f"INV-SSML-006: block {block.block_id!r} has empty ssml; "
                "did populate_plan_ssml run?"
            )


def _parse_every_block(plan: ReadingPlan) -> list[ET.Element]:
    roots: list[ET.Element] = []
    for block in plan.blocks:
        try:
            roots.append(ET.fromstring(block.ssml))
        except ET.ParseError as exc:
            raise SSMLContractError(
                f"block {block.block_id!r} ssml does not parse: {exc}"
            ) from exc
    return roots


def _assert_every_root_is_speak(roots: list[ET.Element]) -> None:
    for root in roots:
        if root.tag != "speak":
            raise SSMLContractError(
                f"INV-SSML-001: root tag is {root.tag!r}, expected 'speak'"
            )


def _assert_unique_mark_names(roots: list[ET.Element]) -> None:
    all_names = [
        name
        for root in roots
        for name in (m.get("name") for m in root.findall("mark"))
        if name is not None
    ]
    counts = Counter(all_names)
    duplicates = sorted(n for n, c in counts.items() if c > 1)
    if duplicates:
        raise SSMLContractError(
            f"INV-SSML-002: duplicate mark name(s) across plan: {duplicates}"
        )

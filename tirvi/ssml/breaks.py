"""F23 — inter-block break helper.

Spec: N02/F23 DE-03. AC: US-02/AC-01. FT-anchors: FT-175. BT-anchors: BT-117.

Emits the SSML ``<break>`` element placed between consecutive PlanBlocks
during the plan-level walk in :func:`tirvi.ssml.populate_plan_ssml`.
POC: fixed 500ms; per-block-type variation deferred.
"""

_DEFAULT_BREAK_MS = 500


def inter_block_break() -> str:
    """Return the canonical inter-block break SSML element.

    Wavenet accepts ``<break time="…ms"/>`` and pauses synthesis for the
    requested duration. The same element form is consumed by F26.
    """
    return f'<break time="{_DEFAULT_BREAK_MS}ms"/>'

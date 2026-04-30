"""F11 — block-segmentation errors."""

from tirvi.errors import AdapterError


class BlockTypeOutOfScope(AdapterError):
    """Raised when the heuristic classifier infers a block type outside the POC scope.

    POC supports: heading, paragraph, question_stem. Other types (table, figure,
    math, answer_option) trigger this error so the demo fails loud rather than
    silently mis-classifying as paragraph.

    Spec: N01/F11 DE-05.
    """

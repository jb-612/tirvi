"""F11 T-04 — block bbox aggregation + word-to-block linkage.

Spec: N01/F11 DE-05, DE-06. AC: US-01/AC-01. FT-anchors: FT-074.

Combines line-gap segmentation with the heuristic classifier to emit
:class:`Block` instances whose ``child_word_indices`` partition the input.

Invariants:
  - INV-BLOCK-002: ``child_word_indices`` is non-empty per block
  - INV-BLOCK-003: every word index appears in exactly one block
  - INV-BLOCK-004: ``bbox`` is the union of child word bboxes
"""

from __future__ import annotations

from tirvi.results import OCRWord

from .classifier import classify_block
from .value_objects import Block, PageStats

_BLOCK_GAP_RATIO = 1.5
_PROVENANCE_THRESHOLD = 0.6
# F52: kinds that DO get a provenance entry. Fallbacks (paragraph, mixed)
# do not — they are the absence of a confident pick.
_PROVENANCE_KINDS: frozenset[str] = frozenset({
    "instruction", "datum", "answer_blank",
    "multi_choice_options", "question_stem", "heading",
})

# F52 DE-04: maps each confident kind to the heuristic cue that fired.
_CUE_SIGNATURE: dict[str, str] = {
    "instruction":          "instruction_prefix_cue",
    "datum":                "datum_prefix_cue",
    "answer_blank":         "empty_block_cue",
    "multi_choice_options": "letter_choice_re_cue",
    "question_stem":        "question_stem_re_cue",
    "heading":              "heading_height_cue",
}


def _build_classification_provenance(
    block_type: str, confidence: float
) -> tuple[dict, ...]:
    """ADR-041 row #20 — emit one transformations entry per confident
    non-fallback classification. Empty for fallback kinds (paragraph,
    mixed) and below-threshold picks.
    """
    if confidence < _PROVENANCE_THRESHOLD:
        return ()
    if block_type not in _PROVENANCE_KINDS:
        return ()
    return ({
        "kind": "block_kind_classification",
        "from": _CUE_SIGNATURE[block_type],
        "to": block_type,
        "confidence": confidence,
        "adr_row": "ADR-041 #20",
    },)


def aggregate_block_bbox(words: list[OCRWord]) -> tuple[int, int, int, int]:
    """Union the bboxes of ``words`` into ``(x0, y0, x1, y1)``."""
    if not words:
        raise ValueError("cannot aggregate bbox from empty word list")
    bboxes = [w.bbox for w in words]
    columns = list(zip(*bboxes, strict=True))
    return (min(columns[0]), min(columns[1]), max(columns[2]), max(columns[3]))


def build_blocks(words: list[OCRWord], page_stats: PageStats) -> list[Block]:
    """Segment ``words`` (in reading order) into :class:`Block` instances."""
    if not words:
        return []
    groups = _group_word_indices(words, page_stats)
    return [_make_block(words, indices, page_stats, n) for n, indices in enumerate(groups, 1)]


def _make_block(
    words: list[OCRWord],
    indices: list[int],
    page_stats: PageStats,
    seq: int,
) -> Block:
    block_words = [words[i] for i in indices]
    block_type, conf = classify_block(block_words, page_stats)
    return Block(
        block_id=f"b{seq}",
        block_type=block_type,
        child_word_indices=tuple(indices),
        bbox=aggregate_block_bbox(block_words),
        classifier_confidence=conf,
        transformations=_build_classification_provenance(block_type, conf),
    )


def _group_word_indices(words: list[OCRWord], stats: PageStats) -> list[list[int]]:
    threshold = max(_BLOCK_GAP_RATIO * stats.line_spacing, 1.0)
    groups: list[list[int]] = [[0]]
    for i in range(1, len(words)):
        prev_bottom = max(words[j].bbox[3] for j in groups[-1])
        cur_top = words[i].bbox[1]
        if cur_top - prev_bottom > threshold:
            groups.append([i])
        else:
            groups[-1].append(i)
    return groups

"""F30 — invariants for the TTS-marks word-timing adapter.

Spec: N03/F30 DE-04. AC: US-02/AC-01.
FT-anchors: FT-215. BT-anchors: BT-146.
"""

from tirvi.errors import AdapterError
from tirvi.results import WordMark


class TimingInvariantError(AdapterError):
    """Raised when WordMarks fail an invariant check (e.g., monotonicity).

    Spec: N03/F30 DE-04.
    """


class BlockScopeError(AdapterError):
    """Raised when a TTSResult crosses block boundaries.

    F30 expects one TTSResult per PlanBlock (one synthesize() call per
    block). Defensive against future F26 evolution that might
    accidentally concatenate blocks.

    Spec: N03/F30 DE-03.
    """


def assert_marks_monotonic(marks: list[WordMark]) -> None:
    """Assert ``marks[i].start_ms <= marks[i+1].start_ms`` for every i.

    Equal timestamps are allowed (Wavenet occasionally reports this for
    tightly-coupled morphemes); only strict regression raises.
    """
    for i in range(1, len(marks)):
        if marks[i].start_ms < marks[i - 1].start_ms:
            raise TimingInvariantError(
                f"INV-MARKS-MONO-001 (BT-146): mark[{i}].start_ms "
                f"({marks[i].start_ms}) < mark[{i - 1}].start_ms "
                f"({marks[i - 1].start_ms}); Wavenet API regression?"
            )

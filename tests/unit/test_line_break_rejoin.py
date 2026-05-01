"""F14 T-03 — line-break rejoin heuristic.

Spec: N02/F14 DE-03. AC: US-01/AC-01. FT-anchors: FT-094, FT-095. BT-anchors: BT-063.
"""

from __future__ import annotations

from tirvi.normalize.line_break_rejoin import rejoin
from tirvi.results import OCRWord


def _w(
    text: str,
    *,
    x0: int = 0,
    y0: int = 0,
    x1: int = 50,
    y1: int = 30,
    conf: float = 1.0,
) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), conf=conf)


class TestLineBreakRejoin:
    def test_us_01_ac_01_rejoins_when_no_sentence_final_punct(self) -> None:
        # Two words on different lines (y-delta > line_height_median) with
        # no sentence-final punctuation and no mid-token hyphen → rejoin.
        words = [
            _w("hyph", y0=0, y1=20),
            _w("enword", y0=40, y1=60),
        ]
        result = rejoin(words)
        assert result.text == "hyphenword"
        assert len(result.spans) == 1
        assert result.spans[0].src_word_indices == (0, 1)
        assert result.spans[0].text == "hyphenword"

    def test_us_01_ac_01_does_not_rejoin_across_period(self) -> None:
        # Trailing word ends in sentence-final punctuation → keep separate.
        words = [
            _w("end.", y0=0, y1=20),
            _w("Next", y0=40, y1=60),
        ]
        result = rejoin(words)
        assert result.text == "end. Next"
        assert len(result.spans) == 2
        assert result.spans[0].src_word_indices == (0,)
        assert result.spans[1].src_word_indices == (1,)

    def test_us_01_ac_01_does_not_rejoin_compound_hyphen(self) -> None:
        # Mid-token hyphen present → keep separate even on line break.
        words = [
            _w("co-", y0=0, y1=20),
            _w("operate", y0=40, y1=60),
        ]
        result = rejoin(words)
        assert result.text == "co- operate"
        assert len(result.spans) == 2

    def test_same_line_does_not_rejoin(self) -> None:
        # No line break (y-delta within line_height_median) → no rejoin.
        words = [
            _w("alpha", y0=0, y1=20),
            _w("beta", y0=2, y1=22),
        ]
        result = rejoin(words)
        assert result.text == "alpha beta"
        assert len(result.spans) == 2

    def test_repair_log_records_rejoin(self) -> None:
        words = [
            _w("hyph", y0=0, y1=20),
            _w("enword", y0=40, y1=60),
        ]
        result = rejoin(words)
        assert len(result.repair_log) == 1
        entry = result.repair_log[0]
        assert entry.rule_id == "line_break_rejoin"
        assert entry.before == "hyph enword"
        assert entry.after == "hyphenword"
        assert entry.position == 0

    def test_does_not_rejoin_across_question_mark(self) -> None:
        words = [
            _w("ok?", y0=0, y1=20),
            _w("yes", y0=40, y1=60),
        ]
        result = rejoin(words)
        assert result.text == "ok? yes"
        assert len(result.spans) == 2

    def test_empty_input(self) -> None:
        result = rejoin([])
        assert result.text == ""
        assert result.spans == ()
        assert result.repair_log == ()

"""F14 T-04 — stray-punctuation repair rule.

Spec: N02/F14 DE-04. AC: US-02/AC-01. FT-anchors: FT-096. BT-anchors: BT-064.
"""

from __future__ import annotations

from tirvi.normalize.stray_punct import drop_stray_punct
from tirvi.results import OCRWord


def _w(
    text: str,
    *,
    x0: int = 0,
    y0: int = 0,
    x1: int = 50,
    y1: int = 30,
    conf: float | None = 1.0,
) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), conf=conf)


class TestStrayPunct:
    def test_us_01_ac_01_drops_isolated_punct_tokens(self) -> None:
        # Stray comma alone on its own line, low confidence → dropped.
        words = [
            _w("hello", y0=0, y1=20, conf=0.95),
            _w(",", y0=40, y1=60, conf=0.2),
            _w("world", y0=80, y1=100, conf=0.9),
        ]
        result = drop_stray_punct(words)
        assert "," not in result.text
        assert result.text == "hello world"

    def test_us_01_ac_01_logs_repair_to_repair_log(self) -> None:
        words = [
            _w("hello", y0=0, y1=20, conf=0.95),
            _w(",", y0=40, y1=60, conf=0.2),
        ]
        result = drop_stray_punct(words)
        assert len(result.repair_log) == 1
        entry = result.repair_log[0]
        assert entry.rule_id == "stray_punct_drop"
        assert entry.before == ","
        assert entry.after == ""

    def test_drops_isolated_apostrophe(self) -> None:
        # ASCII apostrophe (U+0027) alone, low confidence → dropped.
        words = [
            _w("alpha", y0=0, y1=20, conf=0.9),
            _w("'", y0=40, y1=60, conf=0.1),
        ]
        result = drop_stray_punct(words)
        assert "'" not in result.text

    def test_preserves_geresh_inside_acronym(self) -> None:
        # Hebrew geresh (U+05F3) survives even at low confidence.
        # Regression: מס׳ (mispar — "number") would lose its geresh otherwise.
        geresh = "׳"  # ׳
        words = [_w(f"מס{geresh}", y0=0, y1=20, conf=0.3)]
        result = drop_stray_punct(words)
        assert f"מס{geresh}" in result.text

    def test_preserves_gershayim_inside_acronym(self) -> None:
        # Hebrew gershayim (U+05F4) survives even at low confidence.
        # Regression: ת״א (tel-aviv abbreviation) keeps its gershayim.
        gershayim = "״"  # ״
        words = [_w(f"ת{gershayim}א", y0=0, y1=20, conf=0.3)]
        result = drop_stray_punct(words)
        assert f"ת{gershayim}א" in result.text

    def test_preserves_isolated_geresh_token_low_conf(self) -> None:
        # Even an isolated geresh token at low confidence is preserved.
        geresh = "׳"
        words = [
            _w("alpha", y0=0, y1=20, conf=0.9),
            _w(geresh, y0=40, y1=60, conf=0.1),
        ]
        result = drop_stray_punct(words)
        assert geresh in result.text

    def test_preserves_high_confidence_punct(self) -> None:
        # High-confidence stray comma → preserved (not stray, just isolated).
        words = [
            _w("alpha", y0=0, y1=20, conf=0.9),
            _w(",", y0=40, y1=60, conf=0.95),
        ]
        result = drop_stray_punct(words)
        assert "," in result.text

    def test_preserves_punct_with_neighbour_on_same_line(self) -> None:
        # Comma sitting next to text on the SAME line is sentence-final-ish
        # — preserved even at low confidence (it has neighbouring text).
        words = [
            _w("alpha", x0=0, y0=0, x1=50, y1=20, conf=0.9),
            _w(",", x0=55, y0=0, x1=60, y1=20, conf=0.2),
        ]
        result = drop_stray_punct(words)
        assert "," in result.text

    def test_preserves_none_confidence(self) -> None:
        # conf is None → "no signal", not low-confidence; preserve.
        words = [
            _w("alpha", y0=0, y1=20, conf=0.9),
            _w(",", y0=40, y1=60, conf=None),
        ]
        result = drop_stray_punct(words)
        assert "," in result.text

    def test_empty_input(self) -> None:
        result = drop_stray_punct([])
        assert result.text == ""
        assert result.spans == ()
        assert result.repair_log == ()

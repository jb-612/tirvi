"""Per-character Unicode-script classifier (F16 DE-01)."""

from enum import Enum


class Script(Enum):
    HE = "he"
    LATIN = "latin"
    DIGIT = "digit"
    SYMBOL = "symbol"
    WS = "ws"
    OTHER = "other"


_SYMBOLS = frozenset("+−×÷=%.,-")
_WS = frozenset(" \t\n\r\f\v")

_RANGES: tuple[tuple[int, int, Script], ...] = (
    (0x0590, 0x05FF, Script.HE),
    (0xFB1D, 0xFB4F, Script.HE),
    (0x0041, 0x005A, Script.LATIN),
    (0x0061, 0x007A, Script.LATIN),
    (0x00C0, 0x00D6, Script.LATIN),
    (0x00D8, 0x00F6, Script.LATIN),
    (0x00F8, 0x00FF, Script.LATIN),
    (0x0030, 0x0039, Script.DIGIT),
    (0x0660, 0x0669, Script.DIGIT),
)


def classify_char(c: str) -> Script:
    if c in _SYMBOLS:
        return Script.SYMBOL
    if c in _WS:
        return Script.WS
    cp = ord(c)
    for start, end, script in _RANGES:
        if start <= cp <= end:
            return script
    return Script.OTHER

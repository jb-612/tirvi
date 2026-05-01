"""F23 — inter-block break helper."""

_DEFAULT_BREAK_MS = 500   # full sentence break (after . ! ? : ;)
_SHORT_BREAK_MS = 100     # natural breath at line break with no punctuation
_SENTENCE_FINAL = (".", "!", "?", ":", ";")


def inter_block_break(prev_block_text: str | None = None) -> str:
    """Inter-block SSML break — punctuation-aware.

    - Sentence-final punctuation in prev block → 500ms break (full pause)
    - prev_block_text is None (legacy callers) → 500ms break
    - Otherwise (mid-sentence line break in OCR) → single space

    The empty <break> at line breaks was inducing falling intonation in
    Wavenet that the listener perceived as a stop. A plain space lets
    Wavenet treat both blocks as one continuous prosodic unit.
    """
    if prev_block_text is None or _ends_with_sentence_punct(prev_block_text):
        return f'<break time="{_DEFAULT_BREAK_MS}ms"/>'
    return " "


def _ends_with_sentence_punct(text: str) -> bool:
    stripped = text.rstrip().rstrip('"\'”“)').rstrip()
    return bool(stripped) and stripped[-1] in _SENTENCE_FINAL

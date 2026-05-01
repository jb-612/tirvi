"""F23 — inter-block break helper."""

_DEFAULT_BREAK_MS = 500   # full sentence break (after . ! ? : ;)
_SHORT_BREAK_MS = 100     # natural breath at line break with no punctuation
_SENTENCE_FINAL = (".", "!", "?", ":", ";")


def inter_block_break(prev_block_text: str | None = None) -> str:
    """Inter-block SSML <break>.

    With prev_block_text ending in sentence-final punctuation (or None for
    backward compat), emit 500ms. Otherwise emit 100ms so the narrator
    continues naturally across mid-sentence line breaks instead of stopping.
    """
    if prev_block_text is None or _ends_with_sentence_punct(prev_block_text):
        return f'<break time="{_DEFAULT_BREAK_MS}ms"/>'
    return f'<break time="{_SHORT_BREAK_MS}ms"/>'


def _ends_with_sentence_punct(text: str) -> bool:
    stripped = text.rstrip().rstrip('"\'”“)').rstrip()
    return bool(stripped) and stripped[-1] in _SENTENCE_FINAL

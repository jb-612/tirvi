"""F23 — XML-safe escape utility.

Spec: N02/F23 DE-04. AC: US-01/AC-01.

Escapes the five XML special characters (``& < > " '``) and leaves
every other code-point untouched — notably Hebrew (U+0590..U+05FF
including NFD nikud) and IPA characters used by the F20 G2P stage.

The standard library's :func:`xml.sax.saxutils.escape` only handles
``& < >``; we extend with quote variants to keep ``<mark name="…"/>``
attributes valid when token text would otherwise contain quotes.
"""


_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    # & MUST be first — every other escape introduces a literal &
    ("&", "&amp;"),
    ("<", "&lt;"),
    (">", "&gt;"),
    ('"', "&quot;"),
    ("'", "&apos;"),
)


def xml_escape(text: str) -> str:
    """Return ``text`` with XML special characters replaced by entities."""
    for needle, replacement in _REPLACEMENTS:
        text = text.replace(needle, replacement)
    return text

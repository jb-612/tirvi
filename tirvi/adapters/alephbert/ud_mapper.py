"""F26 T-03 — UD-Hebrew schema mapper.

Spec: N02/F26 DE-03. AC: US-02/AC-01. FT-anchors: FT-133, FT-134.

Maps YAP CPOSTag → UD POS and projects whitelisted morph features into
the locked F03 ``NLPToken`` schema. Non-whitelisted keys are dropped
silently (per F18 MORPH_KEYS_WHITELIST). CPOSTag stays a local variable
only — never stored in morph_features (would violate locked F03 schema).
"""

from __future__ import annotations

from typing import Any

from tirvi.nlp.morph import MORPH_KEYS_WHITELIST
from tirvi.results import NLPToken

_CPOS_TO_UD: dict[str, str] = {
    "VB": "VERB",
    "NN": "NOUN",
    "NNP": "PROPN",
    "NNT": "NOUN",
    "JJ": "ADJ",
    "JJT": "ADJ",
    "RB": "ADV",
    "IN": "ADP",
    "DT": "DET",
    "CC": "CCONJ",
    "CONJ": "SCONJ",
    "PRP": "PRON",
    "QW": "PRON",
    "CD": "NUM",
    "AT": "ADP",
    "POS": "PART",
    "PUNC": "PUNCT",
}


def yap_token_to_nlp(token_dict: dict[str, Any]) -> NLPToken:
    """Project a parsed YAP token into the locked :class:`NLPToken` schema."""
    cpos = token_dict.get("CPOSTag", "")
    pos = _CPOS_TO_UD.get(cpos, "X")
    morph = _project_morph(token_dict.get("feats") or {}, cpos)
    return NLPToken(
        text=token_dict.get("surface", ""),
        pos=pos,
        lemma=token_dict.get("lemma") or None,
        morph_features=morph,
        confidence=None,
    )


def _project_morph(
    feats: dict[str, str], raw_cpos: str
) -> dict[str, str] | None:
    if not feats:
        return None
    projected = {k: v for k, v in feats.items() if k in MORPH_KEYS_WHITELIST}
    if not projected:
        return None
    return projected

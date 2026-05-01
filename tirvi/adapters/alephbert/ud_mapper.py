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
    "PREPOSITION": "ADP",
    "DEF": "DET",
    "ADVERB": "ADV",
    "BN": "VERB",
    "BNT": "VERB",
    "CDT": "NUM",
}

# YAP lowercase feat keys → UD TitleCase
_FEAT_KEY_MAP: dict[str, str] = {
    "gen": "Gender", "num": "Number", "per": "Person",
    "tense": "Tense", "def": "Definite",
}

# YAP feat value abbreviations → UD canonical values
_FEAT_VAL_MAP: dict[str, dict[str, str]] = {
    "Gender":   {"M": "Masc", "F": "Fem"},
    "Number":   {"S": "Sing", "P": "Plur", "D": "Dual"},
    "Tense":    {"PAST": "Past", "FUTURE": "Fut", "BEINONI": "Pres",
                 "IMPERATIVE": "Imp"},
    "Definite": {"D": "Def"},
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
    # Translate YAP lowercase short tags → UD canonical TitleCase keys + values
    translated: dict[str, str] = {}
    for raw_key, raw_val in feats.items():
        ud_key = _FEAT_KEY_MAP.get(raw_key)
        if ud_key is None:
            continue
        ud_val = _FEAT_VAL_MAP.get(ud_key, {}).get(raw_val, raw_val)
        translated[ud_key] = ud_val
    projected = {k: v for k, v in translated.items() if k in MORPH_KEYS_WHITELIST}
    return projected or None

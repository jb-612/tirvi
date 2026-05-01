"""F22 T-03 — Per-token provenance dict.

Spec: N02/F22 DE-03. AC: US-01/AC-01.
FT-anchors: FT-171. BT-anchors: BT-114.

DE-03: every PlanToken carries a ``provenance: dict[str, str]`` mapping
keyed by ``pos | lemma | morph | ipa | stress | vocalized``. Values are
the upstream provider strings; the literal sentinel ``"missing"`` fills
keys whose upstream input was absent (e.g., per-token IPA is ``None``
for POC per ADR-028, so ``provenance["ipa"] == "missing"``).

Provenance is the audit trail from final reading-plan token back to the
upstream provider that supplied each piece of linguistic information.
"""

from tirvi.blocks import Block
from tirvi.normalize import NormalizedText, Span
from tirvi.plan import PlanToken, ReadingPlan
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    NLPToken,
)

PROVENANCE_KEYS = {"pos", "lemma", "morph", "ipa", "stress", "vocalized"}
MISSING = "missing"


def _make_inputs() -> dict:
    """Single-block / two-word synthetic page; tokens 1:1 with spans."""
    blocks = (
        Block(
            block_id="b1",
            block_type="paragraph",
            child_word_indices=(0, 1),
            bbox=(0, 0, 100, 30),
        ),
    )
    normalized = NormalizedText(
        text="שלום עולם",
        spans=(
            Span(text="שלום", start_char=0, end_char=4, src_word_indices=(0,)),
            Span(text="עולם", start_char=5, end_char=9, src_word_indices=(1,)),
        ),
    )
    nlp = NLPResult(
        provider="dictabert-fake",
        tokens=[
            NLPToken(text="שלום", pos="NOUN", lemma="שלום"),
            NLPToken(text="עולם", pos="NOUN", lemma="עולם"),
        ],
        confidence=0.9,
    )
    dia = DiacritizationResult(
        provider="nakdan-fake",
        diacritized_text="שָׁלוֹם עוֹלָם",
        confidence=0.85,
    )
    g2p = G2PResult(
        provider="phonikud-fake",
        phonemes=["ʃaˈlom oˈlam"],
        confidence=None,
    )
    return {
        "blocks": blocks,
        "normalized": normalized,
        "nlp": nlp,
        "dia": dia,
        "g2p": g2p,
    }


def _build_plan() -> ReadingPlan:
    i = _make_inputs()
    return ReadingPlan.from_inputs(
        page_id="page-1",
        blocks=i["blocks"],
        normalized=i["normalized"],
        nlp_result=i["nlp"],
        diacritization=i["dia"],
        g2p_result=i["g2p"],
    )


class TestPlanProvenance:
    def test_us_01_ac_01_token_carries_src_word_indices(self) -> None:
        # FT-171: src_word_indices is the structural pointer back to the OCR
        # word index list — required for F35 highlight + page.json projection.
        plan = _build_plan()
        token = plan.blocks[0].tokens[0]
        assert isinstance(token, PlanToken)
        assert token.src_word_indices == (0,)
        assert plan.blocks[0].tokens[1].src_word_indices == (1,)

    def test_us_01_ac_01_provenance_traces_back_to_ocr_word(self) -> None:
        # FT-171 / BT-114: every input OCR word index appears in exactly one
        # token's src_word_indices — no provenance is dropped on the floor.
        plan = _build_plan()
        seen: list[int] = []
        for block in plan.blocks:
            for token in block.tokens:
                seen.extend(token.src_word_indices)
        assert sorted(seen) == [0, 1]

    def test_us_01_ac_01_provenance_dict_present_with_required_keys(self) -> None:
        # DE-03: every PlanToken exposes a provenance dict keyed by the
        # six canonical keys (pos, lemma, morph, ipa, stress, vocalized).
        plan = _build_plan()
        for block in plan.blocks:
            for token in block.tokens:
                assert hasattr(token, "provenance")
                assert isinstance(token.provenance, dict)
                assert PROVENANCE_KEYS <= set(token.provenance.keys())

    def test_us_01_ac_01_provenance_values_from_upstream_providers(self) -> None:
        # DE-03 / FT-171: pos + lemma come from NLP; vocalized comes from
        # the Diac provider. Stored as strings, byte-identical to upstream.
        plan = _build_plan()
        first = plan.blocks[0].tokens[0]
        assert first.provenance["pos"] == "NOUN"
        assert first.provenance["lemma"] == "שלום"
        assert first.provenance["vocalized"] == "שָׁלוֹם"

    def test_us_01_ac_01_provenance_missing_sentinel_when_input_absent(self) -> None:
        # DE-03: per ADR-028 the per-token IPA is None for POC; the keys
        # without upstream input use the literal "missing" sentinel.
        plan = _build_plan()
        first = plan.blocks[0].tokens[0]
        assert first.provenance["ipa"] == MISSING
        assert first.provenance["stress"] == MISSING
        assert first.provenance["morph"] == MISSING

    def test_us_01_ac_01_provenance_values_are_strings(self) -> None:
        # DE-03: values are upstream provider STRINGS (not None, not int).
        # Keeps JSON serialisation deterministic and audit-friendly.
        plan = _build_plan()
        for block in plan.blocks:
            for token in block.tokens:
                for key in PROVENANCE_KEYS:
                    assert isinstance(token.provenance[key], str), (
                        f"provenance[{key!r}] must be str"
                    )

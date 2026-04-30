"""F19 T-05 — NFC→NFD nikud normalization.

Spec: N02/F19 DE-05. AC: US-01/AC-01.
"""

from __future__ import annotations

import unicodedata

from tirvi.adapters.nakdan.normalize import to_nfd


class TestNikudNormalize:
    def test_us_01_ac_01_nfc_input_normalized_to_nfd(self) -> None:
        # alef with qamatz in NFC composed form
        nfc = unicodedata.normalize("NFC", "אָ")
        result = to_nfd(nfc)
        assert unicodedata.is_normalized("NFD", result)

    def test_us_01_ac_01_already_nfd_unchanged(self) -> None:
        nfd = unicodedata.normalize("NFD", "אָ")
        assert to_nfd(nfd) == nfd

    def test_us_01_ac_01_g2p_stability_after_normalize(self) -> None:
        # Round-trip preserves the visible Hebrew form
        original = "שָׁלוֹם"
        nfd = to_nfd(original)
        assert unicodedata.normalize("NFC", nfd) == unicodedata.normalize("NFC", original)

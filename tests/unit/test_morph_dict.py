"""F18 T-02 — morphology dict whitelist.

Spec: N02/F18 DE-02. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestMorphDict:
    def test_us_01_ac_01_morph_keys_whitelisted(self) -> None:
        # Number, Gender, Person, Tense, etc.
        pass

    def test_us_01_ac_01_morph_values_short_tags(self) -> None:
        pass

"""F23 T-04 — XML escape preserves Hebrew NFD nikud.

Spec: N02/F23 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestXMLEscape:
    def test_us_01_ac_01_hebrew_block_chars_not_escaped(self) -> None:
        pass

    def test_us_01_ac_01_xml_special_chars_escaped(self) -> None:
        # & < > " ' → entities
        pass

    def test_us_01_ac_01_nfd_nikud_preserved(self) -> None:
        pass

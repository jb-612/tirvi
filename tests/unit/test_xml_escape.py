"""F23 T-04 — XML-safe escape (preserves Hebrew NFD nikud + IPA).

Spec: N02/F23 DE-04. AC: US-01/AC-01.

``xml_escape(text)`` escapes the five XML special characters
(``& < > " '``) but leaves every Hebrew code-point (U+0590..U+05FF)
and every IPA code-point untouched. Round-trip: parsing the escaped
output through ``ElementTree`` yields the original text.
"""

from xml.etree import ElementTree as ET

from tirvi.ssml.escape import xml_escape


class TestXMLEscape:
    def test_us_01_ac_01_xml_specials_escaped(self) -> None:
        assert xml_escape("&") == "&amp;"
        assert xml_escape("<") == "&lt;"
        assert xml_escape(">") == "&gt;"
        assert xml_escape('"') == "&quot;"
        assert xml_escape("'") == "&apos;"

    def test_us_01_ac_01_amp_escaped_first_then_others(self) -> None:
        # & must be escaped before < / > to avoid double-escape (& → &amp; → &amp;amp;)
        assert xml_escape("a & <b> c") == "a &amp; &lt;b&gt; c"

    def test_us_01_ac_01_hebrew_block_chars_not_escaped(self) -> None:
        # U+0590..U+05FF — Hebrew block (incl. nikud)
        text = "שלום"
        assert xml_escape(text) == text
        text_with_nikud = "שָׁלוֹם"  # NFD nikud
        assert xml_escape(text_with_nikud) == text_with_nikud

    def test_us_01_ac_01_ipa_chars_not_escaped(self) -> None:
        # IPA characters (Latin Extended + IPA Extensions blocks)
        ipa = "ʃaˈlom"
        assert xml_escape(ipa) == ipa

    def test_us_01_ac_01_round_trip_through_elementtree(self) -> None:
        # Property: parse(<x>{escaped}</x>) yields the original text
        original = 'a < b & "c" — שלום ʃaˈlom'
        wrapped = f"<x>{xml_escape(original)}</x>"
        parsed = ET.fromstring(wrapped)
        assert parsed.text == original

    def test_us_01_ac_01_empty_string_round_trips(self) -> None:
        assert xml_escape("") == ""

    def test_us_01_ac_01_no_escape_no_change(self) -> None:
        clean = "שָׁלוֹם עוֹלָם — IPA: ʃaˈlom"
        assert xml_escape(clean) == clean

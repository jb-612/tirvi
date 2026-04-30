"""F23 T-03 — inter-block <break> emission.

Spec: N02/F23 DE-03. AC: US-02/AC-01. FT-anchors: FT-175. BT-anchors: BT-117.

Per task hint: "500ms break inserted between consecutive PlanBlocks in the
plan-level walk; not inside the per-block speak document". POC ships a
single fixed 500ms; per-block-type variation deferred to v0.1.
"""

from xml.etree import ElementTree as ET

from tirvi.ssml.breaks import inter_block_break


class TestInterBlockBreak:
    def test_us_02_ac_01_ft_175_returns_break_element_string(self) -> None:
        out = inter_block_break()
        assert isinstance(out, str)
        # Parses as a valid <break/> element
        elem = ET.fromstring(out)
        assert elem.tag == "break"

    def test_us_02_ac_01_ft_175_default_break_time_is_500ms(self) -> None:
        elem = ET.fromstring(inter_block_break())
        assert elem.get("time") == "500ms"

    def test_us_02_ac_01_bt_117_break_is_self_closing(self) -> None:
        # Self-closing form: no text content, no children — Wavenet's parser
        # tolerates either, but we emit canonically self-closing.
        elem = ET.fromstring(inter_block_break())
        assert elem.text is None
        assert len(list(elem)) == 0

    def test_us_02_ac_01_break_round_trips_through_speak_wrapper(self) -> None:
        # Smoke: a <speak> containing the break parses cleanly. Demonstrates
        # the fragment is wrapper-safe for T-05 composition.
        wrapped = f'<speak xml:lang="he-IL">{inter_block_break()}שלום</speak>'
        root = ET.fromstring(wrapped)
        assert root.tag == "speak"
        breaks = root.findall("break")
        assert len(breaks) == 1
        assert breaks[0].get("time") == "500ms"

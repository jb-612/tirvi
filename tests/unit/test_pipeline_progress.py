"""T-03: Wire ProgressReporter into run_pipeline() stage calls.

RED phase — all tests here MUST fail until the GREEN phase wires
`reporter` kwarg and `"report"` key into `tirvi/pipeline.py`.

Feature: N01/F49-pipeline-progress
Task:    T-03
Test file: tests/unit/test_pipeline_progress.py
"""

from __future__ import annotations

import pytest

from tirvi.pipeline import make_stub_deps, run_pipeline
from tirvi.progress import PipelineReport, StageTiming


# ---------------------------------------------------------------------------
# Local spy — records every call without touching production code
# ---------------------------------------------------------------------------


class SpyReporter:
    """Spy that records every call for assertion."""

    def __init__(self) -> None:
        self.events: list[tuple] = []

    def stage_started(self, name: str, total_tokens: int | None = None) -> None:
        self.events.append(("started", name))

    def stage_completed(
        self, name: str, elapsed_s: float, metric_label: str
    ) -> None:
        self.events.append(("completed", name, elapsed_s, metric_label))

    def stage_error(self, name: str, error_label: str) -> None:
        self.events.append(("error", name, error_label))

    def token_tick(self) -> None:
        self.events.append(("tick",))

    def summarize(self) -> None:
        self.events.append(("summarize",))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_pdf_bytes() -> bytes:
    """Trivial 1-byte placeholder; _StubOCR ignores the content."""
    return b"%PDF-stub"


def _run_with_spy(tmp_path, spy: SpyReporter | None = None):
    """Call run_pipeline() with stub deps and optional reporter kwarg."""
    deps = make_stub_deps()
    kwargs: dict = {}
    if spy is not None:
        kwargs["reporter"] = spy
    return run_pipeline(_minimal_pdf_bytes(), tmp_path, deps, **kwargs)


# ---------------------------------------------------------------------------
# T-03 tests — 10 cases as specified
# ---------------------------------------------------------------------------


def test_run_pipeline_accepts_reporter_kwarg(tmp_path):
    """run_pipeline(..., reporter=SpyReporter()) must not raise TypeError."""
    spy = SpyReporter()
    result = _run_with_spy(tmp_path, spy)
    # Just needs to not raise; we'll assert on events in sibling tests.
    assert result is not None


def test_run_pipeline_reporter_receives_stage_started_for_ocr(tmp_path):
    """SpyReporter must receive a ("started", "OCR") event."""
    spy = SpyReporter()
    _run_with_spy(tmp_path, spy)
    started_names = [e[1] for e in spy.events if e[0] == "started"]
    assert "OCR" in started_names, (
        f'"OCR" not found in started events. All events: {spy.events}'
    )


def test_run_pipeline_reporter_receives_stage_completed_for_ocr(tmp_path):
    """SpyReporter must receive a ("completed", "OCR", <float>, "<N> words") event."""
    spy = SpyReporter()
    _run_with_spy(tmp_path, spy)
    ocr_completed = [
        e for e in spy.events if e[0] == "completed" and e[1] == "OCR"
    ]
    assert ocr_completed, f"No completed OCR event found. All events: {spy.events}"
    _, _name, elapsed_s, metric_label = ocr_completed[0]
    assert isinstance(elapsed_s, float), (
        f"elapsed_s should be float, got {type(elapsed_s)}"
    )
    assert metric_label.endswith("words"), (
        f'OCR metric_label should end with "words", got {metric_label!r}'
    )


def test_run_pipeline_reporter_receives_nakdan_stage(tmp_path):
    """SpyReporter records started+completed for "Nakdan"; metric ends with "tokens"."""
    spy = SpyReporter()
    _run_with_spy(tmp_path, spy)
    started_names = [e[1] for e in spy.events if e[0] == "started"]
    assert "Nakdan" in started_names, (
        f'"Nakdan" not in started events: {spy.events}'
    )
    nakdan_completed = [
        e for e in spy.events if e[0] == "completed" and e[1] == "Nakdan"
    ]
    assert nakdan_completed, (
        f"No completed Nakdan event found. All events: {spy.events}"
    )
    _, _name, _elapsed, metric_label = nakdan_completed[0]
    assert metric_label.endswith("tokens"), (
        f'Nakdan metric_label should end with "tokens", got {metric_label!r}'
    )


def test_run_pipeline_reporter_receives_tts_stage(tmp_path):
    """SpyReporter records started+completed for "TTS"; metric ends with "KB"."""
    spy = SpyReporter()
    _run_with_spy(tmp_path, spy)
    started_names = [e[1] for e in spy.events if e[0] == "started"]
    assert "TTS" in started_names, (
        f'"TTS" not in started events: {spy.events}'
    )
    tts_completed = [
        e for e in spy.events if e[0] == "completed" and e[1] == "TTS"
    ]
    assert tts_completed, (
        f"No completed TTS event found. All events: {spy.events}"
    )
    _, _name, _elapsed, metric_label = tts_completed[0]
    assert metric_label.endswith("KB"), (
        f'TTS metric_label should end with "KB", got {metric_label!r}'
    )


def test_run_pipeline_reporter_receives_rasterize_stage(tmp_path):
    """SpyReporter records started+completed for "Rasterize"; metric label is "—"."""
    spy = SpyReporter()
    _run_with_spy(tmp_path, spy)
    started_names = [e[1] for e in spy.events if e[0] == "started"]
    assert "Rasterize" in started_names, (
        f'"Rasterize" not in started events: {spy.events}'
    )
    rasterize_completed = [
        e for e in spy.events if e[0] == "completed" and e[1] == "Rasterize"
    ]
    assert rasterize_completed, (
        f"No completed Rasterize event found. All events: {spy.events}"
    )
    _, _name, _elapsed, metric_label = rasterize_completed[0]
    assert metric_label == "—", (
        f'Rasterize metric_label should be "—", got {metric_label!r}'
    )


def test_run_pipeline_returns_pipeline_report(tmp_path):
    """Return dict must contain key "report" whose value is a PipelineReport with >= 4 stages."""
    spy = SpyReporter()
    result = _run_with_spy(tmp_path, spy)
    assert "report" in result, (
        f'"report" key missing from run_pipeline return dict. Keys: {list(result.keys())}'
    )
    report = result["report"]
    assert isinstance(report, PipelineReport), (
        f'"report" value should be PipelineReport, got {type(report)}'
    )
    assert len(report.stages) >= 4, (
        f"PipelineReport.stages should have >= 4 entries, got {len(report.stages)}: {report.stages}"
    )


def test_run_pipeline_default_reporter_is_noop(tmp_path):
    """Calling run_pipeline() WITHOUT reporter kwarg must not raise (backwards-compat)."""
    deps = make_stub_deps()
    result = run_pipeline(_minimal_pdf_bytes(), tmp_path, deps)
    assert result is not None
    assert "sha" in result
    assert "drafts_dir" in result


def test_pipeline_report_stages_have_nonnegative_elapsed(tmp_path):
    """All StageTiming.elapsed_s in PipelineReport.stages must be >= 0.0."""
    spy = SpyReporter()
    result = _run_with_spy(tmp_path, spy)
    report: PipelineReport = result["report"]
    for stage in report.stages:
        assert stage.elapsed_s is not None, (
            f"Stage {stage.name!r} has None elapsed_s"
        )
        assert stage.elapsed_s >= 0.0, (
            f"Stage {stage.name!r} has negative elapsed_s: {stage.elapsed_s}"
        )


def test_pipeline_report_stage_names_present(tmp_path):
    """Stage names "OCR", "Nakdan", "TTS", "Rasterize" must all appear in PipelineReport.stages."""
    spy = SpyReporter()
    result = _run_with_spy(tmp_path, spy)
    report: PipelineReport = result["report"]
    stage_names = {s.name for s in report.stages}
    required = {"OCR", "Nakdan", "TTS", "Rasterize"}
    missing = required - stage_names
    assert not missing, (
        f"Expected stage names {required} in report; missing: {missing}. "
        f"Present: {stage_names}"
    )


# ---------------------------------------------------------------------------
# T-04 tests — ProgressReporterEventBridge wires reporter to cascade events
# ---------------------------------------------------------------------------

# Helper factories — build minimal domain events without calling production logic


def _make_applied_event(chosen_by_stage: str = "mlm_scorer"):
    from datetime import datetime, timezone

    from tirvi.correction.domain.events import CorrectionApplied

    return CorrectionApplied(
        page_index=0,
        original="אנשיס",
        corrected="אנשים",
        chosen_by_stage=chosen_by_stage,
        score=0.9,
        sentence_hash="abc",
        occurred_at=datetime.now(timezone.utc),
    )


def _make_rejected_event():
    from datetime import datetime, timezone

    from tirvi.correction.domain.events import CorrectionRejected

    return CorrectionRejected(
        page_index=0,
        original="אנשיס",
        proposed="אנשים",
        rejected_by="anti_hallucination",
        sentence_hash="abc",
        reason="not in candidates",
        occurred_at=datetime.now(timezone.utc),
    )


def _make_cascade_mode_degraded_event():
    from datetime import datetime, timezone

    from tirvi.correction.domain.events import CascadeModeDegraded
    from tirvi.correction.value_objects import CascadeMode

    return CascadeModeDegraded(
        page_index=0,
        mode=CascadeMode(name="bypass"),
        occurred_at=datetime.now(timezone.utc),
    )


def _make_llm_call_cap_reached_event():
    from datetime import datetime, timezone

    from tirvi.correction.domain.events import LLMCallCapReached

    return LLMCallCapReached(
        page_index=0,
        calls_made=10,
        cap=10,
        occurred_at=datetime.now(timezone.utc),
    )


def test_bridge_implements_event_listener():
    """ProgressReporterEventBridge(reporter) must satisfy the EventListener Protocol."""
    from tirvi.correction.service import EventListener
    from tirvi.progress import ProgressReporterEventBridge

    bridge = ProgressReporterEventBridge(SpyReporter())
    assert isinstance(bridge, EventListener), (
        "ProgressReporterEventBridge must satisfy the EventListener runtime_checkable Protocol"
    )


def test_bridge_calls_token_tick_on_correction_applied():
    """on_correction_applied must forward one token_tick() call to the reporter."""
    from tirvi.progress import ProgressReporterEventBridge

    spy = SpyReporter()
    bridge = ProgressReporterEventBridge(spy)
    bridge.on_correction_applied(_make_applied_event())
    tick_events = [e for e in spy.events if e[0] == "tick"]
    assert len(tick_events) == 1, (
        f"Expected exactly 1 tick event after on_correction_applied, got {tick_events!r}. "
        f"All events: {spy.events}"
    )


def test_bridge_calls_token_tick_on_correction_rejected():
    """on_correction_rejected must forward one token_tick() call to the reporter."""
    from tirvi.progress import ProgressReporterEventBridge

    spy = SpyReporter()
    bridge = ProgressReporterEventBridge(spy)
    bridge.on_correction_rejected(_make_rejected_event())
    tick_events = [e for e in spy.events if e[0] == "tick"]
    assert len(tick_events) == 1, (
        f"Expected exactly 1 tick event after on_correction_rejected, got {tick_events!r}. "
        f"All events: {spy.events}"
    )


def test_bridge_tracks_llm_call_on_llm_reviewer_applied():
    """on_correction_applied with chosen_by_stage='llm_reviewer' must increment llm_call_count to 1."""
    from tirvi.progress import ProgressReporterEventBridge

    bridge = ProgressReporterEventBridge(SpyReporter())
    bridge.on_correction_applied(_make_applied_event(chosen_by_stage="llm_reviewer"))
    assert bridge.llm_call_count == 1, (
        f"Expected llm_call_count == 1 after llm_reviewer event, got {bridge.llm_call_count}"
    )


def test_bridge_does_not_increment_llm_count_for_mlm_scorer():
    """on_correction_applied with chosen_by_stage='mlm_scorer' must NOT increment llm_call_count."""
    from tirvi.progress import ProgressReporterEventBridge

    bridge = ProgressReporterEventBridge(SpyReporter())
    bridge.on_correction_applied(_make_applied_event(chosen_by_stage="mlm_scorer"))
    assert bridge.llm_call_count == 0, (
        f"Expected llm_call_count == 0 after mlm_scorer event, got {bridge.llm_call_count}"
    )


def test_bridge_on_cascade_mode_degraded_does_not_crash():
    """on_cascade_mode_degraded must not raise any exception."""
    from tirvi.progress import ProgressReporterEventBridge

    bridge = ProgressReporterEventBridge(SpyReporter())
    # Must not raise — no assertion on side-effects required
    bridge.on_cascade_mode_degraded(_make_cascade_mode_degraded_event())


def test_bridge_on_llm_call_cap_reached_does_not_crash():
    """on_llm_call_cap_reached must not raise any exception."""
    from tirvi.progress import ProgressReporterEventBridge

    bridge = ProgressReporterEventBridge(SpyReporter())
    # Must not raise — no assertion on side-effects required
    bridge.on_llm_call_cap_reached(_make_llm_call_cap_reached_event())


# ---------------------------------------------------------------------------
# T-06 tests — Wire RichProgressReporter into run_demo.py CLI
# ---------------------------------------------------------------------------


def test_run_demo_imports_rich_progress_reporter():
    """scripts/run_demo.py source must contain 'RichProgressReporter' (US-F49-06/AC-01)."""
    import pathlib

    src = pathlib.Path("/Users/jbellish/VSProjects/tirvi/scripts/run_demo.py").read_text()
    assert "RichProgressReporter" in src, (
        "scripts/run_demo.py must import and reference RichProgressReporter "
        "from tirvi.progress, but the class name was not found in the source."
    )


def test_run_demo_main_passes_reporter_kwarg_to_run_pipeline():
    """main() source must pass reporter=reporter kwarg to run_pipeline (US-F49-06/AC-02)."""
    import pathlib

    src = pathlib.Path("/Users/jbellish/VSProjects/tirvi/scripts/run_demo.py").read_text()
    assert "reporter=reporter" in src, (
        "main() in scripts/run_demo.py must pass 'reporter=reporter' to run_pipeline(), "
        "but that kwarg pattern was not found in the source."
    )


def test_run_demo_main_calls_summarize():
    """main() source must call reporter.summarize() (US-F49-04/AC-01)."""
    import pathlib

    src = pathlib.Path("/Users/jbellish/VSProjects/tirvi/scripts/run_demo.py").read_text()
    assert "reporter.summarize()" in src, (
        "main() in scripts/run_demo.py must call reporter.summarize() after the pipeline "
        "completes, but that call was not found in the source."
    )


def test_run_demo_main_summarize_in_finally_block():
    """reporter.summarize() must appear inside a finally block (US-F49-04/AC-03 — always fires)."""
    import ast
    import pathlib

    src = pathlib.Path("/Users/jbellish/VSProjects/tirvi/scripts/run_demo.py").read_text()
    tree = ast.parse(src)

    # Walk the AST to find main() function, then check for a Try node whose
    # finalbody contains a call to reporter.summarize().
    def _has_summarize_in_finally(func_body: list) -> bool:
        for node in ast.walk(ast.Module(body=func_body, type_ignores=[])):
            if isinstance(node, ast.Try) and node.finalbody:
                for final_node in ast.walk(ast.Module(body=node.finalbody, type_ignores=[])):
                    if (
                        isinstance(final_node, ast.Expr)
                        and isinstance(final_node.value, ast.Call)
                    ):
                        call = final_node.value
                        if (
                            isinstance(call.func, ast.Attribute)
                            and call.func.attr == "summarize"
                            and isinstance(call.func.value, ast.Name)
                            and call.func.value.id == "reporter"
                        ):
                            return True
        return False

    main_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_func = node
            break

    assert main_func is not None, (
        "Could not find a 'main' function definition in scripts/run_demo.py"
    )
    assert _has_summarize_in_finally(main_func.body), (
        "reporter.summarize() must be called inside a 'finally' block within main() "
        "so it fires even when run_pipeline() raises an exception. "
        "No such finally-guarded call was found in the AST."
    )

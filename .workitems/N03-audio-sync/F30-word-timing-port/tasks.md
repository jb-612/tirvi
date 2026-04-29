---
feature_id: N03/F30
status: ready
total_estimate_hours: 5.5
---

# Tasks: N03/F30 — Word-timing port (TTS-marks adapter only)

## T-01: TTSEmittedTimingAdapter class

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-213]
- estimate: 1h
- test_file: tests/unit/test_tts_marks_adapter.py
- dependencies: []
- hints: implements WordTimingProvider port; get_timings(tts_result, transcript) -> WordTimingResult; provider="tts-marks"

## T-02: WordMark → WordTiming projection

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-213]
- estimate: 1.5h
- test_file: tests/unit/test_mark_to_timing.py
- dependencies: [T-01]
- hints: WordTiming(mark_id, start_s, end_s); end_s = next.start_s; for last mark: tts_result.audio_duration_s if available else last_mark.start_s + 0.2

## T-03: Per-block scope guard

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_per_block_scope.py
- dependencies: [T-01]
- hints: get_timings rejects multi-block TTSResult input; raises BlockScopeError if voice_meta indicates concatenated blocks

## T-04: Monotonicity invariant

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-215]
- bt_anchors: [BT-146]
- estimate: 1h
- test_file: tests/unit/test_marks_monotonic.py
- dependencies: [T-01]
- hints: assert_marks_monotonic raises TimingInvariantError on first non-monotonic pair; report indices in error message

## T-05: WordTimingProvider integration + adapter contract + count match

- design_element: DE-05, DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-214, FT-216, FT-217]
- bt_anchors: [BT-147, BT-148]
- estimate: 1.5h
- test_file: tests/unit/test_word_timing_provider.py
- dependencies: [T-02, T-03, T-04]
- hints: len(marks) == len(transcript_tokens) else raise MarkCountMismatch; pass through assert_adapter_contract; tests use F03 WordTimingProviderFake; ForcedAlignmentAdapter slot raises NotImplementedError("forced-alignment deferred")

## Dependency DAG

```
T-01 → T-02
T-01 → T-03
T-01 → T-04
T-02, T-03, T-04 → T-05
```

Critical path: T-01 → T-02 → T-05 (4h)

---
feature_id: N03/F26
status: ready
total_estimate_hours: 7.5
---

# Tasks: N03/F26 — Google Wavenet adapter

## T-01: Wavenet client wrapper (v1beta1)

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_wavenet_client.py
- dependencies: []
- hints: thin wrapper over google-cloud-texttospeech v1beta1 TextToSpeechClient; lazy import; raise WavenetCredentialError if ADC missing in non-test path

## T-02: synthesize_speech with mark timepoints

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-193, FT-198]
- estimate: 2h
- test_file: tests/unit/test_wavenet_synthesize.py
- dependencies: [T-01]
- hints: SynthesisInput(ssml=...); VoiceSelectionParams(language_code="he-IL", name="he-IL-Wavenet-D"); AudioConfig(audio_encoding=MP3, sample_rate_hertz=24000); enable_time_pointing=[SSML_MARK]; uses pinned client mock in tests

## T-03: TTSResult assembly

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-198]
- estimate: 1h
- test_file: tests/unit/test_tts_result_assembly.py
- dependencies: [T-02]
- hints: TTSResult(provider="wavenet", audio_bytes=resp.audio_content, word_marks=parse_timepoints(resp.timepoints), voice_meta={"voice":"he-IL-Wavenet-D","lang":"he-IL"}); WordMark(mark_id, t_seconds)

## T-04: Mark-truncation detector

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-194]
- bt_anchors: [BT-131, BT-134]
- estimate: 1h
- test_file: tests/unit/test_mark_truncation.py
- dependencies: [T-03]
- hints: count "<mark name=" in input SSML via regex; compare to len(timepoints); on mismatch, set voice_meta["tts_marks_truncated"] = True

## T-05: drafts/<sha>/ writer

- design_element: DE-05
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-196]
- estimate: 1h
- test_file: tests/unit/test_drafts_dir_write.py
- dependencies: [T-03]
- hints: write_drafts_dir(reading_plan_sha, audio_bytes, word_marks); creates drafts/{sha}/ if absent; writes audio.mp3 + audio.json (timings); raises if files exist (no overwrite)

## T-06: Adapter contract + retry policy

- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-197]
- bt_anchors: [BT-132, BT-133]
- estimate: 1.5h
- test_file: tests/unit/test_wavenet_adapter.py
- dependencies: [T-02, T-03, T-04, T-05]
- hints: pass WavenetTTSAdapter through assert_adapter_contract; provider="wavenet"; retry on 429: 3 attempts with 1s/2s/4s backoff; tests use F03 TTSBackendFake when API not reachable

## Dependency DAG

```
T-01 → T-02 → T-03 → T-04
                T-03 → T-05
T-02, T-03, T-04, T-05 → T-06
```

Critical path: T-01 → T-02 → T-03 → T-06 (5.5h)

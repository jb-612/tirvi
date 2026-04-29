<!-- DERIVED FROM docs/business-design/epics/E07-tts-adapters/stories/E07-F01-google-wavenet-adapter.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:03:01Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E07-F01 — Google Wavenet he-IL Adapter (Word-Sync Default)

## Source Basis
- PRD: §6.5 TTS, §9 Constraints (Hebrew TTS Vertex / Cloud TTS)
- HLD: §4 TTSBackend, §5.2 SSML, §3.4 audio cache
- Research: src-003 §2.3 (Wavenet for word-sync; Hebrew `<mark>` unverified), §10 Phase 3 F7.1; ADR-001
- Assumptions: ASM03

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears highlighted reading | flat playback | word marks |
| P08 Backend Dev | wires Wavenet | API SSML + marks | `TTSResult` with marks |
| P10 Test Author | benchmarks audio quality | drift | bench |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SDK maintainer, test author.
3. System actors: Google Cloud TTS API (v1beta1 SSML mark + timepoints), audio cache.
4. Approvals: ADR-001 captures TTS routing.
5. Handoff: `TTSResult` to E08 word-timing + audio cache.
6. Failure recovery: marks missing → fallback to forced alignment (E00-F03 Story 2 path).

## Behavioural Model
- Hesitation: dev unsure if Hebrew marks reliable end-to-end.
- Rework: voice deprecates a feature; revert to prior voice or migrate.
- Partial info: timepoints truncated mid-block; flag and fall back.
- Retry: transient rate-limit; backoff.

---

## User Stories

### Story 1: Wavenet returns audio + word marks for SSML input

**As a** dev
**I want** Wavenet adapter to call Google TTS v1beta1 with SSML and return audio + per-`<mark>` timepoints
**So that** the player can highlight words.

#### Preconditions
- `plan.json` SSML present with `<mark name="block-{id}-word-{i}"/>` injected.

#### Main Flow
1. Adapter calls API; receives audio + timepoints.
2. Wraps as `TTSResult` (audio_bytes, codec, voice_meta, word_marks).
3. Audio + `.timings.json` written to GCS at `audio/{block_hash}.mp3`.

#### Edge Cases
- Hebrew `<mark>` returns truncated timepoints; flag and fallback alignment.
- Rate limit; backoff per HLD §3.3.

#### Acceptance Criteria
```gherkin
Given a 30-word SSML block
When Wavenet adapter synthesizes
Then `TTSResult.word_marks` covers all 30 words with timepoints
Or the manifest records `tts_marks_truncated=true`
```

#### Data and Business Objects
- `TTSResult`, `WordMark`.

#### Dependencies
- DEP-INT to E06 SSML, E08-F01 word timing, E08-F03 cache.

#### Non-Functional Considerations
- Quality: voice MOS gate (E10).
- Cost: per 1M chars ≤ $16.
- Reliability: failover bounded.

#### Open Questions
- Voice (Wavenet-A vs D) chosen by ADR-001 evidence.

---

### Story 2: Audio cached by content hash

**As a** dev
**I want** synthesized audio cached by `block_hash`
**So that** repeated reads cost nothing.

#### Preconditions
- ASM09 (block_hash includes voice spec).

#### Main Flow
1. Adapter computes `block_hash = sha256(ssml + voice_spec)`.
2. Storage adapter checks for `audio/{block_hash}.mp3`.
3. On hit, return cached `TTSResult`; on miss, call API and store.

#### Edge Cases
- Hash collision (extremely rare); cache returns wrong audio risk; mitigated by including voice spec + SSML hash.

#### Acceptance Criteria
```gherkin
Given the same block synthesized twice
When the cache is checked on second invocation
Then audio is returned without an API call
```

#### Dependencies
- DEP-INT to E08-F03 (cache).

#### Non-Functional Considerations
- Cost: dominant lever per cost analysis.
- Privacy: cache shareable across users (ASM09).

#### Open Questions
- Cache TTL (audio cache exempt from 24h rule).

# E00-F03 — Adapter Ports & Fakes: Behavioural Test Plan

## Behavioural Scope
Covers backend dev behaviour around port shape decisions, fake-registry usage,
and the human moments when schema drift is discovered.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Dev returns bytes from new adapter | P08 Backend Dev | rich-context loss | contract test red |
| Dev forgets to update fake | P10 Test Author | tests stale | CI lint |
| Adapter swap without contract test | P11 SDK Maintainer | undetected drift | adversarial review BT-009 |

---

## Behavioural Scenarios

### BT-009: Dev tries to return bytes from a new TTS adapter
**Persona:** P08 Backend Dev
**Intent:** ship MVP fast
**Human behaviour:** writes `def synthesize() -> bytes:`
**System expectation:** contract test fails with "must return TTSResult"
**Acceptance criteria:** dev rewrites to return rich result before merge

### BT-010: Test author wires fake into FUNC test
**Persona:** P10 Test Author
**Intent:** deterministic test for E03 normalization
**Human behaviour:** imports `OCRBackendFake`; provides canonical page
**System expectation:** fake honors stored fixtures; test deterministic across CI runs
**Collaboration expectation:** new fixture added to repo with provenance comment

### BT-011: SDK maintainer evolves a port
**Persona:** P11 SDK Maintainer
**Intent:** add `confidence` to NLP result
**Human behaviour:** updates port; updates real adapter; forgets fake
**System expectation:** adapter contract test catches missing fake update
**Escalation path:** PR review checklist enumerates "all adapters updated?"

### BT-012: Forced-alignment path activated under load
**Persona:** P08 Backend Dev
**Intent:** observe behaviour when TTS marks unreliable
**Human behaviour:** sets `TIRVI_TTS_MARK_RELIABILITY=low`
**System expectation:** WordTimingProvider auto-routes to forced alignment
**Acceptance criteria:** runtime metric `timing_source=forced-alignment` ≥ 0 emitted

## Edge Behaviour
- New adapter is added but no fake — CI fails before code review starts.
- Result object grows beyond a comfortable serialization boundary; reviewer
  prompts "split into sub-result?"

## Misuse Behaviour
- Dev tries to import `google.cloud.texttospeech` from domain code; lint rule
  rejects.
- Dev forks port locally; CI complains about ABI change.

## Recovery Behaviour
- Fake is silently broken by an unrelated refactor; nightly run of FUNC tests
  catches before next-day commit.

## Collaboration Breakdown Tests
- TTS provider deprecates `<mark>`; team must rotate primary path; exercise
  the rotation procedure with a chaos test.

## Open Questions
- Should we publish the adapter contract tests as a runnable harness for
  third-party providers?

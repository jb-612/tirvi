# N02/F48 Hebrew Correction Cascade — Behavioural Test Plan

## Behavioural Scope
Realistic human patterns around the cascade: the student is a passive listener; the teacher reviews post-hoc; the pipeline engineer tunes knobs. Plus failure modes (Ollama down, new confusion classes appearing in the wild) that must be handled without abandoning the practice session.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Passive listening (cascade is invisible) | P01 Student | unmet expectation that "the page sounds right" | end-to-end audio audit + recall metric |
| Side-by-side OCR vs corrected review | P02 Teacher-QA | misunderstanding why a correction fired | inspector visual + reasoning-trail render |
| Disagreement / override | P02 Teacher-QA | system loses trust if overrides ignored | feedback DB write + revert test |
| Threshold tuning | P15 Engineer | fragile knobs; fear of breaking determinism | reproducible re-run + diff |
| Service outage (Ollama down) | P15 Engineer + P01 Student | abandonment if pipeline aborts | degradation banner + still-completes test |
| New OCR confusion class arrives | P15 Engineer | hardcoded list grows; F48 promise fails | zero-code-change FT-318 family + new pair |
| Recurring correction → rule promotion | P15 Engineer | spam-driven false promotion | aggregator threshold test |

---

## Behavioural Scenarios

### BT-209: Student listens — cascade is invisible, page sounds right
- Persona: P01 Dyslexic Hebrew Student
- Intent: practice Hebrew reading; hear the page correctly
- Human behaviour simulated: listens once front-to-back; does not look at the inspector; abandons audio if multiple words sound wrong in the first 30 seconds
- System expectation: ≥ 90% of OCR errors that affect TTS pronunciation are silently corrected
- Agent expectation: Gemma reviewer, when invoked, returns reasoning text in Hebrew (used only for log; not surfaced to student)
- Collaboration expectation: F48 → F19 → F20 → F26 (Wavenet) chain delivers the corrected token to the player
- Escalation path: if the student abandons the audio (player log shows pause < 30 s without resume), engineer reviews `corrections.json` for false positives
- Acceptance criteria: end-to-end audit on Wave-1 fixture page reports recall ≥ 90% on the 5 known errors and 0 new false-positive pronunciations introduced

### BT-210: Teacher compares OCR vs corrected text in F50 inspector OCR tab
- Persona: P02 Teacher-QA / Accommodation Coordinator
- Intent: spot-check whether corrections were justified before signing off
- Human behaviour simulated: opens inspector, scrolls through a 50-token page, hovers the 5 corrected tokens; reads reasoning trail
- System expectation: every corrected token shows: original, corrected, MLM scores, LLM reason (if used), model versions
- Agent expectation: rendered Hebrew is right-to-left and legible
- Collaboration expectation: clicking "approve" stores no record (default state); no UI noise
- Escalation path: if a correction lacks a reasoning trail, render "audit gap" badge; teacher can flag to engineer
- Acceptance criteria: 100% of corrected tokens render the trail; audit-gap badge fires only on FT-324 path

### BT-211: Teacher disagrees with a Gemma correction → marks "no" → reverted
- Persona: P02 Teacher-QA
- Intent: revert a wrong correction without breaking the student's practice
- Human behaviour simulated: hears the audio, opens inspector, finds the wrong token, clicks "Mark as wrong"; optionally enters expected form; closes inspector
- System expectation: the reverted token is restored on the next run of the same draft; preference cached per `(ocr_word, sentence_context_hash, system_chose)`; feedback.db row created
- Agent expectation: cascade reads sqlite at init; respects revert
- Collaboration expectation: revert applies only to the current draft until rule promotion threshold is met (F48-S05)
- Escalation path: if the same revert recurs across ≥ 3 distinct shas → aggregator emits `RuleSuggestion`
- Acceptance criteria: feedback.db has the row; next run restores original; suggestion emitted only at threshold

### BT-212: Pipeline engineer tunes MLM threshold → re-runs → compares recall/precision
- Persona: P15 Pipeline Engineer
- Intent: lower precision threshold for a noisy cohort; reproducible
- Human behaviour simulated: edits `tirvi/normalize/cascade_config.yaml` lowering `threshold_low` from 1.0 to 0.7; re-runs the pipeline; compares `corrections.json` before and after
- System expectation: re-run is deterministic given (input, model versions, config); diff highlights which tokens flipped verdict
- Agent expectation: LLM is invoked more often (more ambiguous cases); cached responses re-used where prompt unchanged
- Collaboration expectation: engineer can roll back by reverting YAML; no schema migration required for threshold changes
- Escalation path: if recall/precision regress, engineer reverts; if both improve, engineer commits via standard PR flow
- Acceptance criteria: same input + same versions + same config → byte-identical corrections.json (mod ts); changing only threshold yields a meaningful diff

### BT-213: Ollama is down — pipeline still runs with warning + deprecated fixes
- Persona: P01 Student + P15 Engineer
- Intent: keep practicing during a study session despite a backend hiccup
- Human behaviour simulated: student starts the audio; engineer notices the inspector banner later
- System expectation: cascade enters mode="no_llm"; ambiguous verdicts default to keep_original; deprecated `_KNOWN_OCR_FIXES` still applies on top of NakdanGate; corrections.json header records mode
- Agent expectation: no LLM calls; no retries
- Collaboration expectation: F50 inspector shows degraded-mode banner with a one-line explanation (Hebrew + English)
- Escalation path: engineer sees structured `cascade_mode_degraded` log event; if persistent, restarts Ollama
- Acceptance criteria: full page completes; mode recorded; recall reduced gracefully (target ≥ 70% in degraded mode vs ≥ 90% in full mode); 0 pipeline aborts

### BT-214: New OCR confusion pair (e.g., ב↔כ in handwriting) → caught by DictaBERT-MLM, zero code change
- Persona: P15 Engineer (and indirectly P01 Student)
- Intent: prove ADR-033 §Consequences "generalizes" claim
- Human behaviour simulated: engineer adds `ב↔כ` to `confusion_pairs.yaml` (data, not code); re-runs handwritten-scan corpus
- System expectation: previously-uncaught OCR errors of the form `ב→כ` now caught at stage 2 (auto_apply or LLM-confirmed); no new branches, no new modules
- Agent expectation: MLM head agnostic to which letters are in the table; LLM reviewer agnostic to ordering
- Collaboration expectation: engineer's PR contains 1 line of YAML diff + the resulting reduction in feedback DB rows
- Escalation path: if new pair causes regressions on print corpus, engineer flags `source_writer="hebrew_handwrite"` so the pair only fires in handwriting mode
- Acceptance criteria: integration test on a 10-page handwritten corpus shows recall improvement after YAML edit, no regression on the 20-page print bench

### BT-215: Correction recurs 3 times → system suggests promoting to a permanent rule
- Persona: P15 Engineer
- Intent: scale fix list without growing it by hand
- Human behaviour simulated: engineer runs aggregator at end-of-day; reviews `rule_suggestions.json`; cherry-picks 1 of 4 suggestions
- System expectation: only suggestions with ≥ 3 distinct shas appear; spam-cap prevents one user inflating support
- Agent expectation: aggregator does NOT auto-apply; engineer is the gate
- Collaboration expectation: accepted suggestion goes into `confusion_pairs.yaml` (or homograph lexicon F21); rejected suggestions logged with reason
- Escalation path: if a suggestion is repeatedly rejected (≥ 2 times), aggregator increases its required support count for that pair
- Acceptance criteria: aggregator output matches FT-325; engineer-accept loop closes within one PR cycle

### BT-216: Engineer audits privacy invariant — runs cascade with network monitor
- Persona: P15 Engineer (sometimes P04 Operator/SRE)
- Intent: confirm zero exam content leaves the M4 Max — HARD rule
- Human behaviour simulated: engineer runs cascade with `tcpdump`/proxy; verifies all sockets resolve to `127.0.0.1`
- System expectation: zero outbound DNS for non-localhost; zero outbound TCP to public IPs
- Agent expectation: Ollama, DictaBERT, Nakdan all on-device
- Collaboration expectation: AUD-03 functional test enforces this in CI
- Escalation path: any outbound connection → CI fails; security-review hard block before merge
- Acceptance criteria: AUD-03 green on every run; on regression, engineer freezes feature

### BT-217: Repeated student session — cache makes second run instant
- Persona: P01 Student (re-listening to a page)
- Intent: skim the page a second time after an interruption
- Human behaviour simulated: student replays the same draft within minutes
- System expectation: cascade hits cache for every token; total cascade time ≤ 100 ms total (no LLM calls)
- Agent expectation: zero LLM calls
- Collaboration expectation: F50 inspector reflects "cached" indicator on each correction (visible to engineer, hidden from student)
- Escalation path: if cache miss rate > 5% on identical input, engineer investigates
- Acceptance criteria: FT-322 green; cache hit-rate ≥ 95% on the second run

### BT-218: Inspector banner during degraded mode — student notices, asks the teacher
- Persona: P01 Student → P02 Teacher
- Intent: realistic UX flow — student hears odd pronunciations, opens inspector
- Human behaviour simulated: student notices a wrong word; opens inspector; sees the banner "running in degraded mode"; student tells teacher
- System expectation: banner is plain language; links to reasoning trail when available
- Agent expectation: no behaviour change vs BT-213; this scenario tests visibility, not function
- Collaboration expectation: teacher sees the banner; can verify deprecated-fixes mode in `corrections.json`
- Escalation path: teacher reports to engineer; engineer investigates Ollama health
- Acceptance criteria: banner content includes mode name and "corrections may be reduced" message; copy reviewed for accessibility

### BT-219: Engineer abandons a tuning session mid-flow
- Persona: P15 Engineer
- Intent: realistic interruption — partial config edit
- Human behaviour simulated: engineer edits `cascade_config.yaml`, leaves it in a broken state (invalid YAML), closes laptop
- System expectation: next run fails fast with a typed `CascadeConfigInvalid` error pointing at the file:line; pipeline does NOT silently fall back to defaults
- Agent expectation: stage init never starts
- Collaboration expectation: engineer fixes YAML and re-runs; no orphan state
- Escalation path: log event `cascade_config_invalid`; CI gate catches in pre-merge if config is part of repo
- Acceptance criteria: explicit error message; no implicit fallback

### BT-220: Adversarial — student / teacher tries to spam feedback
- Persona: P02 Teacher-QA (adversarial pose)
- Intent: try to drive a malicious rule promotion
- Human behaviour simulated: same teacher marks 50 different tokens wrong in one draft, all with the same expected form
- System expectation: per-sha cap → support_count contribution = 1; suggestion threshold not met
- Agent expectation: aggregator filters BEFORE engineer review
- Collaboration expectation: engineer sees the cap working; no false promotion
- Escalation path: if a teacher account triggers the cap repeatedly, log "spam_pattern_detected"; deferred (no auth in MVP).
- Acceptance criteria: FT-325 second variant green

---

## Edge Behaviour
- Student plays then immediately pauses < 1 s — cascade has already completed init; no behaviour change.
- Teacher leaves an inspector tab open for hours — `corrections.json` is read-once on open; no live refresh required.
- Engineer runs cascade on a draft that no longer exists on disk (deleted via F43 TTL) — typed `DraftMissing` error; pipeline aborts with explanation.
- Two engineers edit `confusion_pairs.yaml` simultaneously — git merge conflict; standard resolution.

## Misuse Behaviour
- Engineer manually edits `corrections.json` to forge a correction trail → cascade signature check (optional sha of stages) detects mismatch on next read; flagged in inspector. **Defer**: signature scheme not in MVP scope; document as `D-LOG-INTEGRITY`.
- Teacher tries to "approve" a correction → no-op (default state); design declines to add an approve button to keep state surface minimal.
- Engineer disables the cascade entirely via config → mode="bypass"; banner; corrections.json empty.

## Recovery Behaviour
- Ollama crash mid-page → mode is per-page; current page completes via in-flight cache; next page detects unhealthy probe → mode="no_llm".
- DictaBERT OOM mid-run → typed exception; page falls back to mode="no_mlm"; structured event.
- Disk full mid-write of `corrections.json` → audit_gaps.json + pipeline still completes.

## Collaboration Breakdown Tests
- Teacher feedback queue grows but engineer never reviews — aggregator emits suggestions; nothing changes until human approves; no silent drift.
- Engineer ships a new prompt template version while teacher is mid-review — `prompt_template_version` field in inspector tells teacher the version they're looking at; old reasoning trail remains valid for old drafts.
- Aggregator runs while a teacher is marking — sqlite WAL mode; no lock held during read.

## Open Questions
- Should the cascade emit a metric on per-page recall when the engineer runs against the held-out 20-page bench (F39 tirvi-bench-v0)? Yes; tracked under F40 quality gates wiring (out of F48 scope; cross-feature dependency captured in DEP-052).
- Long-term: streaming inspector view (live trail as cascade runs) vs current batch model. Defer.

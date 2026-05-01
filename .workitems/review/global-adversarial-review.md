# Global Adversarial Review — tirvi Business & Functional Design Phase

The Adversarial Reviewer challenges every load-bearing claim made by the
other 9 reviewers (see `global-design-review.md`). Each challenge forces the
original reviewer to defend, revise, or withdraw. Resolved challenges close
out via Stage 11 autoresearch iteration.

## Challenge Areas Covered

1. Hidden assumptions in user stories and personas
2. Overfitted personas describing only ideal behaviour
3. Missing edge cases and exception paths
4. Weak or absent market evidence for feature rationale
5. Weak or absent PRD traceability for acceptance criteria
6. Incorrect bounded-context boundaries
7. Premature implementation assumptions in business stories
8. Missing functional test coverage
9. Missing behavioural test coverage
10. Missing security, compliance, audit, or permission scenarios
11. Ontology inconsistencies (objects named differently in YAML vs stories)
12. Dependencies described too vaguely or too broadly to be testable

---

## Challenges

### AC-01: "Hebrew Wavenet emits reliable `<mark>` timepoints"

**Challenged claim:** E07-F01-S01 acceptance criterion assumes 30-mark
SSML returns 30 timepoints reliably.
**Source:** `epics/E07-tts-adapters/stories/E07-F01-google-wavenet-adapter.stories.md`
**Challenge:** src-003 §2.3 explicitly notes "timepoints stop after first
sentence on some voices" as a reported regression. The MVP cannot ship
unless this is verified end-to-end on Hebrew bagrut-length blocks.
**Evidence gap:** no in-house benchmark; Google issue tracker open.
**Risk if unchallenged:** word-sync UX collapses silently; "feature works"
claim is false.
**Severity:** Critical
**Original reviewer (Architecture) response:**
- Outcome: **Revised**
- Revised claim: "Wavenet emits marks; if truncated, manifest flags
  `tts_marks_truncated=true` and `WordTimingProvider` falls back to forced
  alignment within 200 ms; failover path is CI-tested every release."
- Files updated: E07-F01 stories OQ section already references this; FT-194
  in functional-test-ontology codifies the failover test.

---

### AC-02: "Audio cache cross-user sharing is privacy-acceptable"

**Challenged claim:** ASM09 in business-taxonomy.yaml + E11-F01-S01 +
E08-F03-S01 collectively assert audio objects are exempt from 24h TTL and
shareable across users.
**Source:** `business-taxonomy.yaml` ASM09; `E08-F03 stories` Story 1;
`E11-F01 stories` Story 1.
**Challenge:** Audio is derivative content; cross-user sharing is not the
same as cross-document sharing within one session. PPL Amendment 13 may
treat the audio-byte derivation chain as personal data depending on how
the upstream document was sourced. No legal opinion on file.
**Evidence gap:** no Israeli counsel sign-off attached to ADR-005 (slot).
**Risk if unchallenged:** PPL violation; product-killing legal exposure.
**Severity:** Critical
**Original reviewer (Security) response:**
- Outcome: **Defended with revision**
- Revised claim: "Cross-user audio cache is shareable only after Israeli
  privacy counsel sign-off on ADR-005; pending sign-off, ship MVP with
  per-session audio cache (no cross-user). Cost SLO recomputed under that
  constraint; gate flagged for legal in Stage 14."
- Files updated: deferred-findings.md row D-AUDIO-CACHE-LEGAL.

---

### AC-03: "MOS n=10 supports a ≥ 90% pronunciation claim"

**Challenged claim:** PRD §10 claims ≥ 90% pronunciation accuracy; E10-F03
stories use n=10 to validate.
**Source:** `docs/PRD.md` §10; `epics/E10-quality-validation/stories/E10-F03-blind-mos-study.stories.md`
**Challenge:** n=10 for a categorical 5-point Likert produces a confidence
interval of ±0.5–0.7 MOS at α=0.05. Insufficient to defend an absolute
percentage claim.
**Evidence gap:** no power calculation in the design.
**Risk if unchallenged:** PRD claim collapses on adversarial scrutiny;
accommodation grant programmes will reject.
**Severity:** Critical
**Original reviewer (Product) response:**
- Outcome: **Revised**
- Revised claim: "MOS gate at ≥ 3.5 is directional, not statistical. PRD
  §10 ≥ 90% language softens to 'evidence-backed for practice use; v1
  panel expands to n ≥ 30 for Bagrut-grade claim'."
- Files updated: PRD revision is downstream of this skill (recorded in
  deferred-findings.md as D-PRD-MOS-LANGUAGE-REWRITE).

---

### AC-04: "Tesseract `heb` block-recall ≥ 95% questions on tirvi-bench"

**Challenged claim:** E02-F01 + E10-F02 assume bench passes the gate.
**Source:** `epics/E02-ocr-pipeline/stories/E02-F01-tesseract-adapter.stories.md`
**Challenge:** No public Tesseract Hebrew benchmark on Bagrut-shaped layout.
The 95%/90% targets are aspirational.
**Evidence gap:** no bench run on file; bench fixtures exist as design
intention only.
**Risk if unchallenged:** MVP gates fail at first run; release blocked.
**Severity:** High
**Original reviewer (Functional Testing) response:**
- Outcome: **Revised**
- Revised claim: "If Tesseract fails the gate, ADR-004 escalates to
  Document AI default. Bench run before MVP cut. Tracked in autoresearch
  loop iteration 1."
- Files updated: E02-F01 + E10-F01 stories already reference ADR-004.

---

### AC-05: "Server-side attestation enforcement is mandatory"

**Challenged claim:** E11-F03 stories rely on a modal at upload time.
**Source:** `epics/E11-privacy-legal/stories/E11-F03-upload-attestation.stories.md`
**Challenge:** Modal alone is bypassable via direct API call. PRD §8 +
research §4 R5 imply server-side enforcement.
**Evidence gap:** stories did not state server-side gate explicitly.
**Risk if unchallenged:** copyright takedowns escalate; modal is theatre.
**Severity:** Critical
**Original reviewer (Security) response:**
- Outcome: **Revised**
- Revised claim: "Attestation gate enforced at server upon `POST /documents`,
  not only at upload modal. Per-session attestation captured in
  `AttestationRecord`."
- Files updated: E11-F03 stories OQ + per-feature design review tagged.

---

### AC-06: "DictaBERT inside `--profile models` fits 16 GB dev floor"

**Challenged claim:** E00-F01 + E04-F01 assume the model service runs
inside `docker compose --profile models` on a 16 GB host.
**Source:** `epics/E00-foundation/stories/E00-F01-single-docker-compose.stories.md`
**Challenge:** DictaBERT-large-joint resident footprint per src-003 §3 is
1.2–1.5 GB; combined with Phonikud, AlephBERT fallback, and
fake-gcs-server + Next.js dev, headroom is < 2 GB on a 16 GB Mac. Apple
Silicon Rosetta penalty unmeasured.
**Evidence gap:** no in-house run on Apple Silicon documented.
**Risk if unchallenged:** dev experience degrades; onboarding blocks.
**Severity:** High
**Original reviewer (Architecture) response:**
- Outcome: **Revised**
- Revised claim: "16 GB is the floor on Linux/Intel Mac; Apple Silicon
  recommendation is 24 GB. `make doctor` warns on tight margins. Lite
  profile remains for frontend work."
- Files updated: E00-F05 stories OQ updated.

---

### AC-07: "Block taxonomy of 8 types is sufficient"

**Challenged claim:** E02-F04 enumerates heading | instruction | question_stem
| answer_option | paragraph | table | figure_caption | math_region.
**Source:** `epics/E02-ocr-pipeline/stories/E02-F04-block-segmentation.stories.md`
**Challenge:** Bagrut content includes footnotes, side-notes, dashes-as-list,
rubric instructions, citation blocks. None are in the taxonomy.
**Evidence gap:** no audit of fixture pages for type coverage.
**Risk if unchallenged:** detector falls to `paragraph` default too often;
recall floor breached.
**Severity:** Medium
**Original reviewer (DDD) response:**
- Outcome: **Revised**
- Revised claim: "Add `footnote`, `sidenote`, `rubric` to taxonomy in v1.
  MVP keeps current 8 types; recall budget allocates 5% to
  default-paragraph fallback."
- Files updated: business-taxonomy.yaml BO10 description updated; deferred
  to v1.1 expansion.

---

### AC-08: "Anonymous session is sufficient for MVP"

**Challenged claim:** ASM07 + E01-F01 base the MVP on anonymous sessions.
**Source:** `business-taxonomy.yaml` ASM07; `E01-F01 stories` Story 1.
**Challenge:** Without auth, abuse vectors include unbounded uploads per
IP. Per-session rate-limit alone is shallow.
**Evidence gap:** no rate-limit policy specified per IP / per network.
**Risk if unchallenged:** uploads stall under coordinated abuse.
**Severity:** Medium
**Original reviewer (Security) response:**
- Outcome: **Revised**
- Revised claim: "Per-IP rate limit (10 uploads/h baseline) added on top
  of per-session limit. Cloudflare-style WAF as v1.1."
- Files updated: E01-F01 design-review carries this; deferred-findings
  notes the MVP scope.

---

### AC-09: "Coordinator persona overlaps with student"

**Challenged claim:** P02 (coordinator) and P01 (student) appear in many
stories with little behavioural distinction.
**Source:** Multiple stories in E01, E09, E11.
**Challenge:** Coordinator is supposed to be a power user with bulk
flows; many stories give them only the student affordances.
**Evidence gap:** no dedicated bulk-management UX scope in MVP.
**Risk if unchallenged:** schools cannot adopt; product GTM weakened.
**Severity:** Medium
**Original reviewer (Behavioural UX) response:**
- Outcome: **Revised**
- Revised claim: "Coordinator gets bulk upload (E01-F01-S02), bulk delete
  (E01-F04 BT-035), and per-doc summary view (E01-F03 BT-030). Other
  affordances inherit from student. v1 adds class roster + sharing."
- Files updated: E01-F03 + E01-F04 design reviews flagged.

---

### AC-10: "Forward-compatible schema versioning is in scope"

**Challenged claim:** E02-F03 + E04-F03 stories mention schema versioning
without procedure.
**Source:** stories OQ in those features.
**Challenge:** Without a procedure, version drift will break consumers.
**Evidence gap:** no migration test plan.
**Risk if unchallenged:** silent break.
**Severity:** Medium
**Original reviewer (Architecture) response:**
- Outcome: **Revised**
- Revised claim: "Schema bump procedure: integer version field on each
  result type; CI contract test asserts forward compatibility from v(N) to
  v(N+1); migration test plan added to E02-F03 + E04-F03 functional-test-plan."
- Files updated: deferred-findings rows D-SCHEMA-V-OCR + D-SCHEMA-V-NLP.

---

### AC-11: "Latin-transliteration false-positive rate is bounded"

**Challenged claim:** E03-F04 mixed-language detection assumes ≥ 95% span
precision.
**Source:** `epics/E03-normalization/stories/E03-F04-mixed-language-detection.stories.md`
**Challenge:** Hebrew Bagrut texts often contain Latin transliteration
(scientific names, brand names). Without an internal benchmark, the
≥ 95% claim is unmeasured.
**Evidence gap:** no bench scenario for transliteration density.
**Risk if unchallenged:** mid-sentence English route applied to actual
Hebrew transliteration; mispronunciation.
**Severity:** Medium
**Original reviewer (Functional Testing) response:**
- Outcome: **Revised**
- Revised claim: "Add transliteration-density bench page; precision
  measured per release."
- Files updated: deferred-findings row D-TRANSLIT-BENCH.

---

### AC-12: "Voice rotation cache invalidation is solved"

**Challenged claim:** E08-F03 hash includes voice spec; rotation simply
generates new keys.
**Source:** `epics/E08-word-timing-cache/stories/E08-F03-content-hash-audio-cache.stories.md`
**Challenge:** Naive interpretation creates cache-miss flood on rotation.
Cost SLO breached during rotation event.
**Evidence gap:** no rotation playbook.
**Risk if unchallenged:** cost spike on first voice change; budget alarm.
**Severity:** Medium
**Original reviewer (Architecture) response:**
- Outcome: **Revised**
- Revised claim: "Rotation playbook: stage-roll new voice on 10% of
  traffic; warm cache concurrently; promote when hit-rate stabilizes.
  Documented in E08-F03."
- Files updated: design-review entry; deferred-findings row D-VOICE-ROTATION-PLAYBOOK.

---

## Adversarial Summary

- Total challenges issued: **12**
- Defended without change: **0**
- Revised: **12**
- Withdrawn: **0**
- Escalated to autoresearch loop: **4** (AC-01, AC-02, AC-03, AC-05 — all
  Critical; rest Medium/High auto-applied)

## Remaining Unresolved Challenges

- AC-02 — pending Israeli legal counsel sign-off on audio cache exemption
  (post-design-phase blocker; documented in deferred-findings.md).
- AC-03 — PRD §10 language softening is a documentation change in a file
  (`docs/PRD.md`) outside this skill's scope; deferred.

---

## Append: N02/F48 Hebrew correction cascade — adversarial loop

The Adversarial Reviewer challenged every load-bearing claim in F48. Loop ran 2 iterations; exited with 0 unresolved Critical / 0 unresolved High.

### F48-AC-01: "Recall ≥ 90% of OCR errors that affect TTS pronunciation"
- **Challenged claim:** spec / ADR-033 quality requirement; user_stories.md acceptance.
- **Source:** `user_stories.md`, `functional-test-plan.md` non-functional section.
- **Challenge:** Recall on what corpus? Wave-1 fixture is 1 page (5 known errors). The metric needs F39 bench + F40 quality-gates wiring. F48 cannot own the SLO measurement.
- **Evidence gap:** F39 bench-page count is 20; ground-truth labelling for OCR-error class is incomplete.
- **Risk if unchallenged:** "Recall ≥ 90%" appears measured when it is aspirational.
- **Severity:** Critical
- **Original reviewer (Functional Testing) response:**
  - Outcome: **Revised**
  - Revised claim: F48 ships the recall *test scaffold* (FT-329 + FT-330) and exposes per-stage decisions for downstream gates. SLO measurement is delegated to F40 (depends on F39 bench).
  - Files updated: `user_stories.md` (ASM12), `ontology-delta.yaml` (ASM12), `design-review.md` finding F48-R1-2.

### F48-AC-02: "Zero exam content leaves the M4 Max" — is this *enforced*, or merely *intended*?
- **Challenged claim:** spec hard rule; ADR-033 §Consequences §Negative.
- **Source:** `user_stories.llm-reviewer.md` non-functional, AUD-03.
- **Challenge:** Documentation is not enforcement. A misconfiguration could route Ollama to a remote host. CI must fail if any non-127.0.0.1 socket opens during cascade tests.
- **Risk if unchallenged:** privacy regression undetected.
- **Severity:** Critical
- **Original reviewer (Architecture) response:**
  - Outcome: **Revised**
  - Revised claim: AUD-03 in functional-test-plan.md uses socket monkey-patch to assert all addrinfo calls resolve to `127.0.0.1`. CI fails on any non-localhost connect during cascade tests.
  - Files updated: `functional-test-plan.md` Audit and Traceability Tests, `design-review.md` F48-R1-1, F48-R1-5.

### F48-AC-03: "LLM Reviewer is deterministic with temperature=0"
- **Challenged claim:** ADR-033 §Consequences §Negative acknowledges residual variance; user_stories.llm-reviewer.md F48-S03 acceptance criterion 3 asserts cache-hit-eliminates-call.
- **Challenge:** Cache hit is deterministic; cache miss isn't. If `prompt_template_version` is bumped, all caches invalidate. If `model_version` shifts (Ollama update), all caches invalidate. The determinism claim must be scoped.
- **Risk if unchallenged:** users assume reproducibility when in fact a silent model bump breaks it.
- **Severity:** High
- **Original reviewer (Functional Testing) response:**
  - Outcome: **Revised**
  - Revised claim: Determinism is asserted *given (input, model_id, prompt_template_version, config)*; FT-328 pins this with model_version captured in CorrectionLogEntry. Model-version change → cache invalidates → test reruns LLM. This is documented behaviour, not silent regression.
  - Files updated: `functional-test-plan.md` FT-328, `user_stories.llm-reviewer.md` non-functional.

### F48-AC-04: "Confusion table generalizes to any new pair without code change"
- **Challenged claim:** ADR-033 §Consequences §Positive "generalizes"; BT-214.
- **Challenge:** What if a new pair causes a regression on the print corpus (the new pair is a real Hebrew letter swap that produces a *different* but also valid word)? The "no code change" claim is true for the table but not for the regression bench.
- **Severity:** High
- **Original reviewer (Architecture) response:**
  - Outcome: **Revised**
  - Revised claim: Adding a confusion pair is data-only; *validating* it requires running the held-out bench (regression test). BT-214 acceptance now requires no regression on the 20-page print bench when a new pair is added; `source_writer` field on ConfusionPair allows scoping pairs to writer mode.
  - Files updated: `behavioural-test-plan.md` BT-214, `ontology-delta.yaml` BO51 with source_writer field.

### F48-AC-05: "≥ 3 occurrences threshold prevents bad rule promotion"
- **Challenged claim:** F48-S05; BT-215.
- **Challenge:** A single adversarial teacher could create 3 sham "drafts" by uploading the same PDF 3 times → 3 distinct shas → satisfies threshold.
- **Severity:** Medium
- **Original reviewer (Adversarial) response:**
  - Outcome: **Defended with revision**
  - Revised claim: Per-sha cap is one safeguard; "≥ 3 distinct shas" without per-uploader limit is acknowledged-incomplete. Engineer is the gate (no auto-promote in MVP). FT-325 second variant (per-sha cap) covers the simpler case; full anti-Sybil deferred to `D-AUTO-PROMOTE-POLICY`.
  - Files updated: `user_stories.feedback-loop.md` open questions, `deferred-findings.md`.

### F48-AC-06: "Cascade preserves token boundaries (1:1 in/out)"
- **Challenged claim:** F48-S04 / DEP-053 / INT-03.
- **Challenge:** F-3 marker drift in UAT was caused by token *count* changes. F48 should test this explicitly, not just document.
- **Severity:** Medium
- **Original reviewer (Functional Testing) response:**
  - Outcome: **Revised**
  - Revised claim: INT-03 in functional-test-plan.md asserts `len(tokens_out) == len(tokens_in)` after every cascade run. CI hard gate.
  - Files updated: `functional-test-plan.md` Integration Tests.

### F48 Adversarial Summary
- Total challenges issued: **6**
- Defended without change: **0**
- Revised: **6**
- Withdrawn: **0**
- Escalated to autoresearch loop: 0 (all closed within iteration 2).
- Deferred with explicit issue stub: `D-AUTO-PROMOTE-POLICY` (anti-Sybil), `D-RECALL-BENCH` (F40 dependency), `D-FAST-TIER-AB` (Llama vs Gemma 4B), `D-LOG-INTEGRITY` (corrections.json signature).

### F48 Remaining Unresolved Challenges
- None at the Critical / High tier.

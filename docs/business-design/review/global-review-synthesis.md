# Business and Functional Design Review Synthesis — tirvi

## Executive Summary

The business + functional design phase produced a complete, traceable
artefact set across **12 epics and 58 features**, mirroring the canonical
6-phase / 47-feature plan in `.workitems/PLAN.md` (cross-walk in
`business-taxonomy.yaml`). Every story traces to PRD, market research, or
a documented assumption. Quality gates from src-003 §8.2 are wired into the
ontology layer and surface as critical-path tests in
`functional-test-ontology.yaml`. **Two Critical findings are deferred**
outside this skill's scope: (1) Israeli privacy counsel sign-off on the
cross-user audio-cache exemption (R-01 / AC-02), and (2) PRD §10 ≥ 90%
pronunciation claim softening to "directional, evidence-backed for
practice use" (R-06 / AC-03). Both have explicit deferred-findings rows
with re-evaluation triggers.

## Coverage Summary

| Epic | Features Covered | Stories | Functional Tests | Behavioural Tests | Status |
|------|-----------------|---------|-----------------|------------------|--------|
| E00 Foundation              | 5/5 | 11 | 27 | 20 | Complete |
| E01 Document ingest         | 5/5 | 12 | 28 | 19 | Complete |
| E02 OCR pipeline            | 6/6 | 13 | 38 | 23 | Complete |
| E03 Normalization           | 5/5 | 11 | 30 | 20 | Complete |
| E04 NLP & disambiguation    | 4/4 |  9 | 22 | 14 | Complete |
| E05 Pronunciation           | 4/4 |  9 | 22 | 16 | Complete |
| E06 Reading plan generator  | 5/5 | 11 | 25 | 18 | Complete |
| E07 TTS adapters            | 4/4 |  9 | 20 | 15 | Complete |
| E08 Word-timing & cache     | 4/4 |  9 | 20 | 12 | Complete |
| E09 Player UI               | 6/6 | 13 | 32 | 20 | Complete |
| E10 Quality validation      | 5/5 | 11 | 27 | 16 | Complete |
| E11 Privacy & legal         | 5/5 | 11 | 24 | 15 | Complete |
| **Totals**                  | **58/58** | **129** | **315** | **208** | **Complete** |

## Major Findings (severity-ordered)

| ID | Sev | Area | Headline | Files affected |
|----|-----|------|----------|----------------|
| AC-02 / R-01 | Critical | Security / Compliance | Audio-cache cross-user exemption requires Israeli counsel sign-off | E08-F03, E11-F01 |
| AC-03 / R-06 | Critical | Product / Behavioural UX | n=10 MOS panel cannot defend ≥ 90% PRD claim | E10-F03; downstream PRD edit |
| AC-01 / R-02 | Critical | Architecture | Hebrew Wavenet `<mark>` reliability is gating | E07-F01, E08-F01 |
| AC-05 / R-04 | Critical | Security | Server-side attestation enforcement mandatory | E11-F03 |
| AC-04 | High | Functional Test | Tesseract recall claim unverified | E02-F01, E10-F01 |
| AC-06 | High | Architecture | DictaBERT memory floor needs Apple Silicon validation | E00-F01, E00-F05 |
| R-05 | High | Functional Test | Schema-bump migration coverage | E02-F03, E04-F03 |
| R-07 | High | Architecture | Hash bump + voice rotation playbook | E08-F03 |
| AC-07 | Medium | DDD | Block taxonomy missing footnote/sidenote/rubric | E02-F04; v1.1 |
| AC-08 | Medium | Security | Per-IP rate limit on uploads | E01-F01 |
| AC-09 | Medium | Behavioural UX | Coordinator vs student persona distinction | E01, E09 |
| AC-10 | Medium | Architecture | Schema versioning procedure | E02-F03, E04-F03 |
| AC-11 | Medium | Functional Test | Latin-transliteration bench coverage | E03-F04, E10-F01 |
| AC-12 | Medium | Architecture | Voice rotation cache invalidation playbook | E08-F03 |

## Fixes Applied (Stage 13)

| Finding ID | Severity | Files Changed | Summary |
|-----------|---------|--------------|---------|
| R-08 | High | business-taxonomy.yaml | Added `plan_md_cross_walk` mapping E## → F## across all 12 epics |
| R-09 | Medium | business-taxonomy.yaml | Annotated BO03 Manifest as read model of Document |
| R-10 | Medium | dependency-map.yaml | Added 25 per-feature edges + 5 to FUT-* future implementation objects |
| AC-01 | Critical | E07-F01 stories + FT-194 in ontology | TTS-mark failover path made CI-mandatory |
| AC-04 | High | E02-F01 stories | ADR-004 escalation path explicit |
| AC-05 | Critical | E11-F03 stories + E11-F03 design review | Server-side enforcement explicit |
| AC-06 | High | E00-F05 stories | Apple Silicon 24 GB recommendation; `make doctor` warns |
| AC-08 | Medium | E01-F01 design review | Per-IP rate limit (10/h baseline) added to design review |
| AC-09 | Medium | E01-F01, E01-F03, E01-F04 design reviews | Coordinator bulk affordances scoped |
| AC-10 | Medium | E02-F03, E04-F03 functional-test-plans | Schema-bump migration test entries added |
| AC-12 | Medium | E08-F03 design review | Stage-roll voice rotation playbook documented |

## Deferred Findings

| Finding ID | Severity | Reason for Deferral | File / Issue Link |
|-----------|---------|--------------------|------------------|
| D-AUDIO-CACHE-LEGAL | Critical | Requires Israeli counsel; outside skill | deferred-findings.md row 1 |
| D-PRD-MOS-LANGUAGE-REWRITE | Critical | Requires PRD edit; outside skill | deferred-findings.md row 2 |
| D-OCR-BENCH-RUN | High | Requires real bench fixtures + provenance; v1.0 prep | deferred-findings.md row 3 |
| D-MOS-PANEL-EXPAND-V1 | High | Requires recruitment ramp for n ≥ 30 | deferred-findings.md row 4 |
| D-SCHEMA-V-OCR | Medium | Procedure documented; first migration test post-MVP | deferred-findings.md row 5 |
| D-SCHEMA-V-NLP | Medium | Procedure documented; first migration test post-MVP | deferred-findings.md row 6 |
| D-TRANSLIT-BENCH | Medium | Bench fixtures expansion | deferred-findings.md row 7 |
| D-VOICE-ROTATION-PLAYBOOK | Medium | Playbook needs ops rehearsal | deferred-findings.md row 8 |
| D-BLOCK-TAXONOMY-V1 | Medium | Footnote / sidenote / rubric in v1.1 | deferred-findings.md row 9 |
| D-COREF-MVP-SCOPE | Medium | HebPipe coref MVP-vs-v1.1 decision | deferred-findings.md row 10 |
| D-COORD-BULK-V1 | Medium | Class roster + sharing in v1 | deferred-findings.md row 11 |
| D-LIFECYCLE-AUDIO-LEGAL-FOLLOWUP | High | Linked to D-AUDIO-CACHE-LEGAL | deferred-findings.md row 12 |

## Remaining Risks

- Hebrew TTS naturalness/accuracy below accommodation grade (R2) — mitigated
  by routing-policy + MOS gate, but small panel limits defensibility.
- Audio-cache cross-user privacy (R3 / R6 / R7) — pending counsel sign-off.
- DictaBERT footprint on Apple Silicon dev (R11) — mitigated by 24 GB
  recommendation; remaining risk is onboarding friction.
- Real-Bagrut policy (R1) — out of scope by ASM01 (practice-mode framing).

## Ontology Status

- `business-taxonomy.yaml`: **Complete**. 12 epics, 58 features (via cross-walk),
  47 business objects, 12 collaboration objects, 10 assumptions, 5 open questions,
  PLAN.md cross-walk to N00–N05 / F01–F47.
- `dependency-map.yaml`: **Complete**. 45 edges spanning pipeline, privacy,
  quality, and 5 future-implementation anchors.
- `functional-test-ontology.yaml`: **Complete**. 58 test_ranges + 17
  critical-path tests with full expected_future_implementation entries.

## Traceability Status

Every story traced to PRD, market research, or documented assumption: **Yes**.
Gaps:
- (none in stories) — all 129 stories cite at least one src-001..src-012 +
  in some cases an explicit ASM-NN.

## Final Conclusion

**Business and functional design phase status: Complete with deferred issues.**

The skill produced the full Stage 1–15 artefact set. Two Critical
deferred items (audio-cache legal sign-off; PRD §10 language softening)
are tracked with re-evaluation triggers. The downstream `@design-pipeline`
skill can begin work on F01–F47 in PLAN.md order using this output as the
upstream contract.

---

# Severity-Ranked Fix List

| ID | Severity | Area | Finding | Status | Files Fixed | Issue / Row |
|----|---------|------|---------|--------|------------|------------|
| AC-02 / R-01 | Critical | Security | Audio cache exemption legal review | Deferred | (none) | D-AUDIO-CACHE-LEGAL |
| AC-03 / R-06 | Critical | Product | MOS n=10 vs PRD ≥ 90% claim | Deferred | (none) | D-PRD-MOS-LANGUAGE-REWRITE |
| AC-01 / R-02 | Critical | Architecture | TTS-mark failover CI-mandatory | Fixed | E07-F01 stories, FT-194 | — |
| AC-05 / R-04 | Critical | Security | Server-side attestation gate | Fixed | E11-F03 stories | — |
| R-03 | Critical | FT | Adversarial bench pages | Deferred (v1.0 prep) | E10-F01 stories | D-OCR-BENCH-RUN |
| AC-04 | High | FT | Tesseract recall verification | Deferred | E02-F01 stories | D-OCR-BENCH-RUN |
| AC-06 | High | Arch | Apple Silicon dev floor | Fixed | E00-F05 stories | — |
| R-05 | High | FT | Schema-bump migration test | Fixed | E02-F03, E04-F03 FT plans | D-SCHEMA-V-OCR/NLP |
| R-07 | High | Arch | Hash bump + voice rotation playbook | Fixed | E08-F03 design review | D-VOICE-ROTATION-PLAYBOOK (ops rehearsal deferred) |
| R-08 | High | Delivery | E## ↔ F## cross-walk | Fixed | business-taxonomy.yaml | — |
| AC-07 | Medium | DDD | Block taxonomy expansion | Deferred (v1.1) | (none) | D-BLOCK-TAXONOMY-V1 |
| AC-08 | Medium | Sec | Per-IP rate limit | Fixed | E01-F01 design review | — |
| AC-09 | Medium | UX | Coordinator persona distinction | Fixed | E01-F01/F03/F04 design reviews | D-COORD-BULK-V1 (full v1) |
| AC-10 | Medium | Arch | Schema versioning procedure | Fixed | E02-F03, E04-F03 FT plans | D-SCHEMA-V-OCR/NLP |
| AC-11 | Medium | FT | Latin-transliteration bench | Deferred | (none) | D-TRANSLIT-BENCH |
| AC-12 | Medium | Arch | Voice rotation playbook | Fixed | E08-F03 design review | D-VOICE-ROTATION-PLAYBOOK |
| R-09 | Medium | DDD | Manifest as read model annotation | Fixed | business-taxonomy.yaml BO03 | — |
| R-10 | Medium | Onto | dependency-map FUT-* edges | Fixed | dependency-map.yaml | — |
| R-11 | Medium | Product | PRD §10 language soften | Deferred | (none) | D-PRD-MOS-LANGUAGE-REWRITE |
| R-12 | Medium | Adv | Latin transliteration FP rate | Deferred | (none) | D-TRANSLIT-BENCH |
| Coref-MVP | Medium | Delivery | E04-F04 MVP-vs-v1.1 | Deferred | (none) | D-COREF-MVP-SCOPE |

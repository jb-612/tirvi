# Source Inventory — tirvi Business & Functional Design

Inventory of source documents consulted for this business and functional
design phase. Each entry records confidence and known gaps. Inferences
without a source become assumptions logged in `business-taxonomy.yaml`.

| ID | Name | Type | Path | Relevant Epics | Confidence | Notes |
|----|------|------|------|---------------|-----------|-------|
| src-001 | tirvi PRD v1 | prd | `docs/PRD.md` | E0–E11 | high | 12-section product spec; covers goals, NFRs, privacy, OCR/NLP/TTS constraints. Open questions §12. |
| src-002 | tirvi HLD v1 | architecture | `docs/HLD.md` | E0, E1, E2, E7, E8, E9 | high | 12-section architecture. Adapter ports, pipeline stages, GCP topology. Open items §12 (App Service → Cloud Run, single-Docker shape, 7-day TTL). |
| src-003 | Validation & MVP scoping research v1 | market_research | `docs/research/tirvi-validation-and-mvp-scoping.md` | E0–E11 | high | Tier-5 multi-agent research (2026-04-28). Recommends Option B "Standard MVP, practice-mode framing". §10 supplies the canonical 12-epic plan used by this design phase. §12 lists 10 ADR backlog items. |
| src-004 | Hebrew exam reader market evidence | competitive_analysis | embedded in src-003 §1, §6 | E9, E11, market framing | medium | Israel population, MoE 2024 flashpoint, comparison to Speechify/NaturalReader/ElevenLabs/Kurzweil/Read&Write/Edge Read-Aloud/Dicta. |
| src-005 | Hebrew NLP / TTS landscape 2025–26 | competitive_analysis | embedded in src-003 §2 | E2, E4, E5, E7 | high | Tooling matrix for OCR, NLP, diacritization, TTS, alignment. Drives ADR-002, ADR-003, ADR-004, ADR-009. |
| src-006 | Risk register | research | embedded in src-003 §4 | E10, E11 | high | 12 risks. Top three (R1–R3) drive the practice-mode framing, MOS-study requirement, 24h TTL change. |
| src-007 | Cost model | research | embedded in src-003 §5 | E7, E8, E10 | high | $0.008/$0.026/$0.047 per page Standard/Wavenet/Chirp 3 HD. Informs caching SLO. |
| src-008 | Recommended principles | research | embedded in src-003 §7 | E0–E11 | high | 10 design principles; "the reading plan is the product" anchors E3–E6. |
| src-009 | Quality gates | research | embedded in src-003 §8 | E10 | high | tirvi-bench v0; per-stage MVP and post-MVP gates for OCR, diacritization, TTS, latency, cost. |
| src-010 | Implementation phasing | research | embedded in src-003 §10 | E0–E11 | high | 12 epics × 58 features, 16-week build, sequencing rationale. **Canonical epic list for this design phase.** |
| src-011 | ADR backlog | research | embedded in src-003 §12 | E2, E4, E5, E7, E11 | high | 10 ADR slots. ADRs themselves are not authored in this phase; design tasks reference ADR slots by ID. |
| src-012 | Repo CLAUDE.md (project instructions) | other | `CLAUDE.md` | E0 | high | DDD-aware SDLC harness expectations; CC ≤ 5 rule; protected paths; mailbox semantics. |

## F33 — Exam Review Portal (Admin Quality Review)

| ID | Name | Type | Path | Confidence | Notes |
|----|------|------|------|-----------|-------|
| src-F33-01 | F33 design.md (existing) | feature_design | `.workitems/N04-player/F33-side-by-side-viewer/design.md` | high | Three-panel layout; artifact tree; feedback panel; DebugSink; manifest contract; output/ filesystem shape. |
| src-F33-02 | PRD §6.6 | prd | `docs/PRD.md` | high | Player UI requirements; feedback loop mentioned in §6.4 and §10 success metrics. |
| src-F33-03 | HLD §3.1 Frontend | architecture | `docs/HLD.md` | high | Next.js/React stack; /doc/[id] split view; audio engine; sync model. |
| src-F33-04 | HLD §5.4 Feedback loop | architecture | `docs/HLD.md` | high | Corrections → feedback/...json in GCS; offline lexicon updates. |
| src-F33-05 | PLAN.md N04-player | plan | `.workitems/PLAN.md` | high | F33 item in N04; folds in N05/F47. F39 tirvi-bench downstream. |

**Gaps specific to F33:**
- No explicit "university admin" persona exists in PRD — the PRD primary persona is the dyslexic student. Admin persona is inferred from product context (quality review pre-term) and the design.md framing. Recorded as ASM-F33-01.
- Auth/security design is explicitly deferred (single-user POC). Recorded in deferred-fixes.md.
- No formal schema for `manifest.json` in design.md — inferred from the `output/<N>/` filesystem contract.
- F50 (inspector tabs) is referenced as a consumer surface but not yet designed — downstream edge noted.

## Gaps

- No `.workitems/PLAN.md` exists yet; src-003 §10 is treated as the
  canonical plan source for this design phase.
- No `docs/ADR/INDEX.md` exists; src-003 §12 is treated as the canonical
  ADR backlog for this design phase. Slots ADR-001..ADR-010 are referenced
  by name only.
- No public Hebrew-exam OCR benchmark; tirvi-bench v0 is internal-only
  (assumption captured in business-taxonomy.yaml as `ASM06`).
- No published MOS study comparing he-IL TTS voices for accommodation use
  — risk **R2** in src-006 marks this gap.
- Israeli MoE policy on third-party cloud TTS in real Bagrut is not
  publicly documented; **R1** treats real-Bagrut use as v2.

## Inference Confidence Discipline

When a story or test scenario is not directly traceable to a source
document, the story file's **Source Basis** section records the inference
explicitly. The same inference is logged once in `business-taxonomy.yaml`
under `assumptions:` with an `ASM-NN` ID and confidence rating. Stories
reference assumptions by ID rather than restating them.

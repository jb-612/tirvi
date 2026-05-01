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

## F49-specific sources (added 2026-05-01)

| ID | Name | Type | Path | Relevant Features | Confidence | Notes |
|----|------|------|------|-------------------|-----------|-------|
| src-013 | tirvi pipeline.py (POC orchestrator) | implementation | `tirvi/pipeline.py` | F49 | high | Defines 5 pipeline stages: rasterize, OCR, normalize/cascade, Nakdan, TTS. `PipelineDeps` dataclass. F48 cascade wiring. |
| src-014 | scripts/run_demo.py (CLI entrypoint) | implementation | `scripts/run_demo.py` | F49 | high | `main()` runs pipeline synchronously; no progress display; uses stdlib logging only. Target file for F49 integration. |
| src-015 | tirvi/correction/service.py (cascade service) | implementation | `tirvi/correction/service.py` | F49 | high | `EventListener` Protocol with `on_correction_applied` / `on_correction_rejected` / `on_cascade_mode_degraded` / `on_llm_call_cap_reached`. Token-counting hook point for cascade progress. |

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

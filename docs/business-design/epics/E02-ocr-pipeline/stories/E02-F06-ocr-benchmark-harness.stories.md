# E02-F06 — OCR Benchmark Harness Against `tirvi-bench v0`

## Source Basis
- PRD: §10 Success metrics (block-segmentation recall, WER)
- Research: src-003 §8 Quality Gates, §10 Phase 1 F2.6
- Assumptions: ASM06 (tirvi-bench v0 internal)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P10 Test Author | benchmarks OCR | drift detection | ad-hoc benchmarks | CI-runnable harness |
| P04 SRE | release gate | quality regression | undetected drift | fail build on regression |
| P11 SDK Maintainer | tracks providers | compare adapters | apples-to-apples | shared bench |

## Collaboration Model
1. Primary: test author + SRE.
2. Supporting: lexicon maintainer (annotates ground truth).
3. System actors: tirvi-bench v0 fixtures (20 pages), Tesseract / Document AI / DeepSeek-OCR pilot.
4. Approvals: bench updates require ADR-004 reference.
5. Handoff: bench results → quality dashboard.
6. Failure recovery: regression triggers PR block + ADR review.

## Behavioural Model
- Hesitation: test author unsure how to add a new bench page.
- Rework: ground truth fix surfaces a previously hidden adapter bug.
- Partial info: handwriting page deferred to v1.1; bench skips it.
- Abandoned flow: bench takes too long; selectively run only changed adapters.

---

## User Stories

### Story 1: Bench produces WER and block-recall per adapter

**As a** test author
**I want** the harness to report WER and block-segmentation recall per adapter on each bench page
**So that** quality regressions are visible.

#### Preconditions
- tirvi-bench v0 fixtures present in CI.
- Ground-truth annotations versioned.

#### Main Flow
1. CI invokes `tirvi-bench run --adapters tesseract,document-ai`.
2. Bench runs each adapter on each page; computes WER, block-recall, structural recall.
3. Output: JSON report + markdown summary.

#### Edge Cases
- Adapter timeout → flagged with timeout marker, not nan.
- Provider quota exceeded → bench partial; PR fails with clear error.

#### Acceptance Criteria
```gherkin
Given the tirvi-bench v0 fixtures and the Tesseract adapter
When `tirvi-bench run` completes
Then a JSON report shows per-page WER and block-recall
And aggregate metrics meet the MVP gates (WER ≤ 3% digital, ≤ 8% scanned)
```

#### Data and Business Objects
- `BenchmarkRun` (adapter, page, WER, block_recall, time_ms).
- `BenchmarkSet` (version, page count, last_updated).

#### Dependencies
- DEP-INT to E10-F01 (bench fixtures), E10-F02 (CI gates), E02-F01 / F02.

#### Non-Functional Considerations
- Reliability: bench deterministic across runs.
- Cost: skip Document AI in dev unless `--with-paid` flag.
- Privacy: bench fixtures anonymized practice exams (non-publisher copyrighted).

#### Open Questions
- Is page-level break-down needed or aggregate sufficient for CI?

---

### Story 2: Regression in OCR quality blocks PR

**As an** SRE
**I want** a CI gate that fails when OCR WER on tirvi-bench regresses
**So that** quality cannot silently drift over time.

#### Preconditions
- Bench history baseline stored.

#### Main Flow
1. PR triggers bench (changed-adapter mode).
2. Compares against last-green main branch baseline.
3. Fails if WER worsens by > 0.5% or block-recall drops > 2%.

#### Edge Cases
- Bench fixture updated; baseline reset by labeled PR.
- Statistical noise: gate uses 3-run median.

#### Acceptance Criteria
```gherkin
Given baseline WER 2.1% on Tesseract digital pages
When a PR raises WER to 3.0%
Then CI fails with the regression delta
```

#### Dependencies
- DEP-INT to E00-F04 (CI gates), E10-F02 (quality dashboard).

#### Non-Functional Considerations
- Reliability: 3-run median absorbs noise.
- DX: failure message links to bench report.

#### Open Questions
- Statistical significance threshold — bake or document?

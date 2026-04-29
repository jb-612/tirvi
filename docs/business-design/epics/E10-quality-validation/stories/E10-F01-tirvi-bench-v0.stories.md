# E10-F01 — `tirvi-bench v0` (Held-Out 20 Pages)

## Source Basis
- PRD: §10 metrics
- Research: src-003 §8.1 + §8.2
- Assumptions: ASM06

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P10 Test Author | curates bench | provenance | versioned set |
| P04 SRE | release gate | drift | CI integration |
| P11 Lexicon Maintainer | bench correctness | hand-curated truth | annotation pipeline |

## Collaboration Model
1. Primary: test author.
2. Supporting: lexicon maintainer (truth), SRE (CI).
3. System actors: bench fixtures, ground truth files, runner.
4. Approvals: bench changes via PR + ADR.
5. Handoff: bench results → CI dashboard.
6. Failure recovery: bench incomplete → CI warning, not failure.

## Behavioural Model
- Hesitation: maintainer unsure about including a publisher page.
- Rework: ground truth correction; old runs invalidated.
- Partial info: handwriting deferred.
- Retry: re-run on changed adapters.

---

## User Stories

### Story 1: 20-page held-out bench with ground truth

**As a** test author
**I want** 8 digital + 8 scanned + 4 handwriting-mixed (post-MVP) Bagrut-style pages with hand-curated text, structural blocks, and IPA transcripts
**So that** every layer can be measured.

#### Main Flow
1. Curate pages from non-publisher sources.
2. Annotate ground truth in repo with provenance.
3. Versioned releases.

#### Edge Cases
- Page provenance challenged; replaced.

#### Acceptance Criteria
```gherkin
Given the bench is loaded
When a release is cut
Then 20 pages with ground truth are present
And handwriting pages are tagged "deferred"
```

#### Data and Business Objects
- `BenchmarkSet`, `BenchmarkPage`, `GroundTruth`.

#### Dependencies
- DEP-INT to E02-F06, E10-F02..F03.

#### Non-Functional Considerations
- Privacy: no PII, no copyrighted content.
- Reliability: deterministic.

#### Open Questions
- Public release in v1.1?

---

### Story 2: Annotation tooling + provenance log

**As a** maintainer
**I want** lightweight tooling for annotating ground truth
**So that** maintenance is cheap.

#### Main Flow
1. CLI tool to annotate text + blocks.
2. Provenance per-page recorded.

#### Acceptance Criteria
```gherkin
Given a new bench page
When the annotator runs
Then ground truth and provenance are emitted
```

#### Dependencies
- DEP-INT to E10-F02 dashboard.

#### Non-Functional Considerations
- DX.

#### Open Questions
- Annotation collaborator scope.

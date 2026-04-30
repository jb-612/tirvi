<!-- DERIVED FROM docs/business-design/epics/E04-nlp-disambiguation/stories/E04-F02-alephbert-yap-fallback.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E04-F02 — AlephBERT + YAP Fallback Path

## Source Basis
- PRD: §9 Constraints; §6.4 Reading plan
- HLD: §3.3 NLP stage; §4 adapter table
- Research: src-003 §2.2 (AlephBERT/YAP retained as fallback)
- Assumptions: ASM04

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | enables fallback | DictaBERT outage / version skew | drop-in adapter |
| P04 SRE | continuity | total NLP failure unrecoverable | dual-adapter |
| P11 SDK Maintainer | port stability | adapter drift | identical NLPResult shape |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE.
3. System actors: AlephBERT model server, YAP morphology.
4. Approvals: fallback usage rate is a metric; sustained > 5% triggers ADR review.
5. Handoff: identical `NLPResult` shape.
6. Failure recovery: if both fail, NLP stage reports degraded; reading plan emits fallback hints.

## Behavioural Model
- Hesitation: dev unsure when to switch.
- Rework: AlephBERT POS schema differs slightly; mapper smooths.
- Partial info: morphology partial; YAP fills.
- Retry: failover policy: 3 retries DictaBERT → fallback for that page.

---

## User Stories

### Story 1: Adapter selects between DictaBERT and AlephBERT

**As a** dev
**I want** the NLP backend to switch to AlephBERT+YAP when DictaBERT errors persist
**So that** pipeline continues at slightly degraded quality.

#### Main Flow
1. Worker calls NLPBackend; primary fails 3×.
2. Backend switches to fallback for the affected page.
3. `NLPResult.provider="alephbert+yap"`.

#### Edge Cases
- AlephBERT also fails; degraded result emitted with a flag.
- Primary recovers mid-doc; subsequent pages use primary again.

#### Acceptance Criteria
```gherkin
Given DictaBERT fails 3 times for page 4
When the worker retries
Then `NLPResult.pages[3].provider == "alephbert+yap"`
And subsequent pages can use DictaBERT if it recovers
```

#### Data and Business Objects
- `NLPResult.provider`, fallback metric.

#### Dependencies
- DEP-INT to E04-F01 (primary), E10-F05 (telemetry).

#### Non-Functional Considerations
- Reliability: dual-adapter availability.
- Cost: AlephBERT lighter resource than DictaBERT.

#### Open Questions
- Should we run both in shadow during MVP for parity comparison?

---

### Story 2: AlephBERT POS schema mapped to canonical NLPResult schema

**As an** SDK maintainer
**I want** the fallback adapter's POS / morph / lemma fields mapped to the primary schema
**So that** downstream consumers do not branch.

#### Main Flow
1. Mapper translates AlephBERT POS labels to the canonical NLPResult enum.
2. Missing fields filled with `null` or sensible defaults.

#### Edge Cases
- Primary has `def` (definiteness) feature absent in fallback; emit null.

#### Acceptance Criteria
```gherkin
Given AlephBERT outputs POS "VB"
When the mapper runs
Then `Token.pos == "VERB"` (canonical)
```

#### Dependencies
- DEP-INT to E04-F03 (consumer schema).

#### Non-Functional Considerations
- Quality: schema mapping does not lose information silently.

#### Open Questions
- Document fallback gaps explicitly in the schema?

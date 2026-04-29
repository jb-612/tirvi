# E04-F03 — NLPResult Schema: Functional Test Plan

## Scope
Verifies schema v1, builder, and adapter contract.

## Source User Stories
- S01 schema — Critical
- S02 builder — High

## Test Scenarios
- **FT-136** DictaBERT output validates schema v1. Critical.
- **FT-137** AlephBERT/YAP output validates schema v1. Critical.
- **FT-138** Builder from YAML produces valid result. High.
- **FT-139** Bump v1→v2 requires migration test. High.
- **FT-140** Missing required field → validator rejects. Medium.

## Negative Tests
- Adapter emits unknown field; warning + acceptance.

## Boundary Tests
- Empty NLPResult; very large result.

## Permission and Role Tests
- N/A.

## Integration Tests
- Schema consumed by E05/E06.

## Audit and Traceability Tests
- Schema version stamped.

## Regression Risks
- Silent downgrade.

## Open Questions
- Include dependency-parse heads?

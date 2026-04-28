---
name: test-design
description: Produce epic-level Software Test Design (STD.md) with functional, smoke, regression tests and E2E anchors, plus feature-test traceability YAML.
user-invocable: true
argument-hint: "<epic-id> (e.g., N00)"
allowed-tools: Read, Write, Glob, Grep, Bash, mcp__acm__acm_search, mcp__acm__acm_trace, mcp__acm__acm_query_router
---

# Role

You are a test architect who designs epic-level test plans. You read feature
designs, user stories, and acceptance criteria, then produce a structured
Software Test Design document (STD.md) and a machine-readable traceability YAML
that maps every test to its feature.

# When to Use

- At **design time** (workflow step 2) after features and stories are defined
- Before TDD build begins (workflow step 3) — the STD.md informs what to test
- When a new epic is being planned and needs a testing strategy
- When reviewing test coverage gaps at the epic level

# When NOT to Use

- Writing actual test code (use `@tdd-workflow`, `@integration-test`, or `@write-test-frontend`)
- Running quality gates (use `@testing`)
- Querying existing test coverage (use `@acm-traceability`)
- Pinning legacy behavior (use `@behavioral-testing`)
- Validating completion claims (use `@verification-loop`)

# Relationship to Other Testing Skills

```
test-design (THIS SKILL)        -- produces STD.md + traceability.yaml
    |
    |-- informs --> tdd-workflow         -- writes unit + integration test CODE
    |-- informs --> integration-test     -- writes cross-boundary test CODE
    |-- informs --> write-test-frontend  -- writes component/widget test CODE
    |-- informs --> behavioral-testing   -- writes characterization test CODE
    |
    |-- validated-by --> testing         -- runs quality gates against written tests
    |-- queried-by --> acm-traceability  -- queries graph for coverage gaps
    |-- checked-by --> verification-loop -- validates completion
```

This skill produces the PLAN. Downstream skills produce the CODE.

# Instructions

## Step 1: Load Epic Context

Read the epic's planning artifacts:

```
.workitems/PLAN.md                          # Epic definition and feature list
.workitems/{epic-id}-*/design.md            # Feature designs (if they exist)
.workitems/{epic-id}-*/user_stories.md      # User stories (if they exist)
.workitems/{epic-id}-*/tasks.md             # Task breakdown (if it exists)
```

If user stories don't exist yet, derive testable requirements from the PLAN.md
feature descriptions and any referenced ADRs or specs.

Also check:
- `docs/ADR/` for architectural constraints that imply tests
- `docs/research/` for behavioral specs or product requirements
- Existing test files for patterns and naming conventions

## Step 2: Identify Test Subjects per Feature

For each feature in the epic, extract:

1. **Interfaces provided** (functions, APIs, CLI commands, configs)
2. **Acceptance criteria** (from user stories or derived from plan)
3. **Dependencies** (what this feature consumes — cross-feature integration points)
4. **Risks** (from design.md or inferred — what could break)
5. **Quality attributes** (performance, security, reliability constraints)

## Step 3: Design Tests by Category

For each feature, design tests in four categories:

### Functional Tests (FUNC)
- Verify that each interface works correctly with valid input
- Verify error handling with invalid input
- Verify edge cases and boundary conditions
- One test per acceptance criterion minimum
- **Naming**: `FUNC-{epic}-{feature}-{seq:03d}`
- **Example**: `FUNC-N00-F01-001: go_module_initializes_with_correct_module_path`

### Smoke Tests (SMOKE)
- Minimal "does it work at all" checks — one per feature
- Should run in < 30 seconds total for the entire epic
- Binary pass/fail — no edge cases, no error paths
- Used as CI gate before heavier test suites
- **Naming**: `SMOKE-{epic}-{feature}-{seq:03d}`
- **Example**: `SMOKE-N00-F01-001: go_build_succeeds`

### Regression Tests (REG)
- Protect against known risks identified in design.md
- Protect cross-feature integration points
- Protect backward compatibility with existing systems
- One test per risk item minimum
- **Naming**: `REG-{epic}-{feature}-{seq:03d}`
- **Example**: `REG-N00-F02-001: protobuf_codegen_produces_valid_go_and_dart`

### E2E Test Anchors (E2E)
- Placeholder definitions for end-to-end flows that span features
- Marked as `[ANCHOR]` — not executable until downstream features exist
- Define the flow, preconditions, and expected outcome
- Link to the features they span
- For each anchor, specify the **mock strategy** (see below)
- **Naming**: `E2E-{epic}-{seq:03d}`
- **Example**: `E2E-N00-001: full_scaffold_builds_and_passes_ci`

### Integration Mock Strategy

For each feature, the STD must declare how external dependencies are handled
at each test level. Record this in the traceability YAML under `mock_strategy`:

| Test Level | Mock Approach | When to Use |
|------------|---------------|-------------|
| Functional | Interface mocks / stubs | All external deps mocked via interfaces |
| Smoke | Lightweight fakes | Minimal in-process fakes, no network |
| Regression | Contract tests | Verify API contracts haven't broken |
| E2E | One of three strategies below | Depends on integration availability |

**E2E integration approaches** (choose per anchor):

1. **Live mock / simulator** — In-process or sidecar simulator that mimics
   the external system's API surface. Best when the integration is complex
   and the party doesn't offer a sandbox. Record simulator setup in the
   anchor's `mock_strategy.type: simulator` with `simulator_path`.

2. **Test/sandbox API** — Use the integrated party's official test
   environment or sandbox endpoint. Best when available and stable. Record
   as `mock_strategy.type: sandbox_api` with `endpoint` and `auth_notes`.

3. **Recorded replay** — Capture real API responses and replay them during
   tests (VCR/cassette pattern). Best for stable APIs where live calls are
   expensive or rate-limited. Record as `mock_strategy.type: recorded_replay`
   with `cassette_path`.

The traceability YAML schema for mock strategy:

```yaml
mock_strategy:
  type: "simulator | sandbox_api | recorded_replay | interface_mock"
  description: "What is mocked and why"
  simulator_path: null    # path to simulator code (if type=simulator)
  endpoint: null          # sandbox URL (if type=sandbox_api)
  cassette_path: null     # replay fixtures (if type=recorded_replay)
  auth_notes: null        # auth requirements for sandbox
```

## Size Constraint

`.workitems/` markdown files must be <= 100 lines (enforced by hook).

- **STD.md is a compact index**: strategy, summary table, execution order,
  downstream handoff, naming convention. No per-test descriptions.
- **Detailed test catalog lives in traceability.yaml** (no line limit on YAML).
- For any epic, STD.md should be ~50-60 lines. If it exceeds 80, move detail
  to traceability.yaml.

## Acceptance Criteria IDs

When `user_stories.md` exists, reference AC IDs (e.g., `AC-N00-F01-01`) in the
traceability YAML `acceptance_criteria` field for stable traceability. When
stories don't exist yet, use descriptive text as a placeholder — replace with
AC IDs once stories are written.

## Step 4: Write STD.md

Produce the STD.md document in the epic's `.workitems/` directory:

```
.workitems/{epic-id}-{name}/STD.md
```

### STD.md Structure

```markdown
---
id: {epic-id}-STD
parent_id: {epic-id}
type: test-design
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: DRAFT
total_tests: {count}
traceability: ./traceability.yaml
---

# {Epic ID}: {Epic Name} — Software Test Design

## Test Strategy

### Scope
What this STD covers and what it excludes.

### Test Pyramid
How tests distribute across unit/integration/E2E for this epic.

### Environment Requirements
What's needed to run the test suites (tools, services, fixtures).

### CI Integration
How these tests plug into the CI pipeline.

---

## {Feature ID}: {Feature Name}

### Functional Tests

| ID | Name | Description | Acceptance Criteria | Priority |
|----|------|-------------|---------------------|----------|
| FUNC-{epic}-{feature}-001 | descriptive_name | What it verifies | AC ref | P1/P2/P3 |

### Smoke Tests

| ID | Name | Description | Max Duration |
|----|------|-------------|--------------|
| SMOKE-{epic}-{feature}-001 | descriptive_name | What it checks | <Ns |

### Regression Tests

| ID | Name | Description | Risk Protected | Trigger |
|----|------|-------------|---------------|---------|
| REG-{epic}-{feature}-001 | descriptive_name | What it guards | Risk ref | When to run |

### E2E Anchors

| ID | Name | Flow | Features Spanned | Status |
|----|------|------|-----------------|--------|
| E2E-{epic}-001 | descriptive_name | Step description | F01, F03, F05 | [ANCHOR] |

(Repeat per feature)

---

## Cross-Feature Integration Tests

Tests that validate interactions between features within this epic.

## Test Execution Order

Recommended execution order for CI and local development.

## Coverage Targets

| Category | Count | Coverage Goal |
|----------|-------|--------------|
| Functional | N | 100% of acceptance criteria |
| Smoke | N | 1+ per feature |
| Regression | N | 1+ per identified risk |
| E2E Anchors | N | Defined, not yet executable |
```

## Step 5: Write traceability.yaml

Produce a machine-readable traceability file:

```
.workitems/{epic-id}-{name}/traceability.yaml
```

### Schema

```yaml
epic:
  id: "{epic-id}"
  name: "{Epic Name}"
  std_path: "./STD.md"
  created: "YYYY-MM-DD"

features:
  - id: "{epic-id}-F01"
    name: "{Feature Name}"
    design_path: "./design.md"          # or null if not yet created
    stories_path: "./user_stories.md"   # or null
    tests:
      - id: "FUNC-{epic}-F01-001"
        name: "descriptive_test_name"
        type: functional
        priority: P1
        acceptance_criteria: "AC-{epic}-F01-01 or free text"
        mock_strategy:
          type: "interface_mock"
          description: "What external deps are mocked"
        test_path: null                 # filled when test code is written
        status: designed                # designed | implemented | passing | failing

      - id: "SMOKE-{epic}-F01-001"
        name: "descriptive_smoke_name"
        type: smoke
        priority: P1
        test_path: null
        status: designed

      - id: "REG-{epic}-F01-001"
        name: "descriptive_reg_name"
        type: regression
        risk_ref: "Risk description"
        test_path: null
        status: designed

e2e_anchors:
  - id: "E2E-{epic}-001"
    name: "descriptive_e2e_name"
    type: e2e
    features_spanned: ["{epic}-F01", "{epic}-F03"]
    flow_description: "Step-by-step E2E flow"
    mock_strategy:
      type: "simulator | sandbox_api | recorded_replay"
      description: "How external integrations are handled"
      simulator_path: null
      endpoint: null
      cassette_path: null
    status: anchor                      # anchor | designed | implemented | passing
    test_path: null
```

### Status Lifecycle

```
designed --> implemented --> passing
                        --> failing (needs fix)
anchor --> designed --> implemented --> passing (E2E only)
```

## Step 6: Validate Output

Before finalizing:

1. Every acceptance criterion has at least one FUNC test
2. Every feature has at least one SMOKE test
3. Every identified risk has at least one REG test
4. Cross-feature integration points have E2E anchors
5. Test IDs are unique across the entire STD
6. Test names are unique across the entire STD (no two tests share a name)
7. Traceability YAML parses without errors
8. Frontmatter `total_tests` matches the sum of all tests in traceability.yaml
9. STD.md prose test counts match traceability.yaml counts exactly
10. STD.md is under 100 lines (workitems hook enforced)
11. Test names are descriptive and follow naming convention

### Quick Validation

Count tests in the traceability YAML and cross-check against STD.md:

```bash
python3 -c "
import yaml, sys, collections
with open('traceability.yaml') as f:
    d = yaml.safe_load(f)
ids, names = [], []
for feat in d.get('features', []):
    for t in feat.get('tests', []):
        ids.append(t['id']); names.append(t['name'])
for t in d.get('cross_feature', []):
    ids.append(t['id']); names.append(t['name'])
for t in d.get('e2e_anchors', []):
    ids.append(t['id']); names.append(t['name'])
id_dupes = {k:v for k,v in collections.Counter(ids).items() if v>1}
name_dupes = {k:v for k,v in collections.Counter(names).items() if v>1}
print(f'Total: {len(ids)} | Unique IDs: {len(set(ids))}')
if id_dupes: print(f'FAIL: duplicate IDs: {id_dupes}'); sys.exit(1)
if name_dupes: print(f'WARN: duplicate names: {name_dupes}')
print('PASS')
"
```

## Step 7: Report Summary

Print a summary table:

```
Test Design Summary: {Epic ID}
================================
Features:     {count}
Functional:   {count} tests
Smoke:        {count} tests
Regression:   {count} tests
E2E Anchors:  {count} placeholders
Total:        {count}
Coverage:     {acceptance_criteria_covered}/{acceptance_criteria_total} AC covered
Files:        STD.md, traceability.yaml
```

# Output Files

| File | Location | Purpose |
|------|----------|---------|
| `STD.md` | `.workitems/{epic}/STD.md` | Human-readable test design document |
| `traceability.yaml` | `.workitems/{epic}/traceability.yaml` | Machine-readable test-to-feature mapping |

# Cross-References

- `@tdd-workflow` — Write test code from STD.md test definitions
- `@integration-test` — Write cross-boundary tests identified in STD.md
- `@write-test-frontend` — Write component tests identified in STD.md
- `@testing` — Run quality gates after tests are implemented
- `@acm-traceability` — Query coverage gaps post-implementation
- `@behavioral-testing` — Pin brownfield behavior (complementary, not overlapping)
- `@verification-loop` — Validate all STD tests pass before feature completion

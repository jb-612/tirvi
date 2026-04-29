---
name: ddd-7l-scaffold
description: "DDD 7-Layer scaffold before TDD. Transforms approved user stories, acceptance criteria, functional design, and feature task breakdown into a production-grade, layered code skeleton — folders, interfaces, aggregates, value objects, domain events, test skeletons, dependency wiring, runtime shells, and ontology — ready for TDD to fill in business logic. Does NOT implement business logic. Runs after design + 2 revision cycles, before /tdd. Portable across languages: SKILL.md uses TypeScript as canonical examples; references/{python,go,dart}.md provide per-language code shapes."
argument-hint: "[phase/feature-id]"
---

You are operating as a DDD-oriented code scaffolding agent for feature **$ARGUMENTS**.

Your task is to transform approved user stories, acceptance criteria, functional design, and feature task breakdown into a layered code scaffold. You are preparing the repository for the TDD implementation phase that follows. **You must not implement business logic.**

---

## When to Use This Skill

Use this skill only after **all** of the following artifacts exist for `$ARGUMENTS`:

1. Approved user stories
2. Acceptance criteria
3. Functional design
4. Feature task breakdown
5. Domain / bounded-context analysis
6. Design review completed
7. Two design revision cycles completed

Do not start this skill if the design is still unstable. If the design is incomplete, stop and request the missing artifact.

In this repository, those artifacts live at:
- `.workitems/$ARGUMENTS/user_stories.md`
- `.workitems/$ARGUMENTS/design.md`
- `.workitems/$ARGUMENTS/tasks.md`
- `.workitems/$ARGUMENTS/traceability.yaml`
- `.workitems/$ARGUMENTS/meeting-room/` (revision artefacts)

---

## Repository Inspection (Always Run First)

Before generating files:

1. Inspect the existing folder structure
2. Identify language(s), framework(s), test runner(s)
3. Identify dependency injection conventions
4. Identify existing naming conventions
5. Identify existing domain / application / infrastructure separation
6. Identify existing lint, typecheck, and test commands
7. Identify existing ontology, taxonomy, or traceability files

**Do not introduce new conventions** unless the repository has no existing convention.

If this is a brownfield repository, inspect the current conventions before creating new files.

---

## Core Rule

The 7L scaffold prepares the codebase for TDD. **It must not implement real business logic.**

### Allowed

- File creation
- Module structure
- Interfaces
- DTOs
- Entities
- Aggregates
- Value objects
- Ports
- Adapters
- Events
- Test skeletons
- Fixture builders
- Dependency injection wiring
- TODO markers
- NotImplemented placeholders
- Traceability metadata

### Forbidden Before TDD

- Implementing real business rules
- Inventing missing domain behaviour
- Completing algorithms not specified in the design
- Adding hidden assumptions
- Writing production logic without failing tests first
- Collapsing domain, application, and infrastructure layers

---

## Required Inputs

Before scaffolding, read and map:

- User stories
- Acceptance criteria
- Functional design
- Feature task breakdown
- Domain model notes
- Existing architecture conventions
- Existing coding standards
- Existing test conventions
- Existing folder/package structure
- Existing dependency injection pattern
- Existing error-handling style

---

## Output Principle — Everything Must Be Traceable

Every scaffolded artifact must be traceable. Each generated file, class, interface, test, and TODO should map back to at least one of:

- Feature ID
- User story ID
- Acceptance criteria ID
- Domain object
- Aggregate
- Use case
- Event
- Port
- Test scenario

Avoid generic scaffolding that cannot be traced back to the design.

---

## Language-Specific Reference Shapes

The examples in this SKILL.md are in **TypeScript as the canonical language-agnostic illustration**. Per-language code shapes live in this skill's `references/` folder:

- `references/python.md` — Python (Pydantic / dataclasses / Protocol ports / pytest / FastAPI)
- `references/go.md` — Go (interfaces / structs / typed errors / table-driven tests / chi handlers)
- `references/dart.md` — Dart / Flutter (sealed classes / abstract ports / Riverpod / flutter_test / shelf)

For projects in other languages, add `references/<lang>.md` following the same per-layer structure. The canonical SKILL.md prompt is language-portable; concrete shapes live in the references.

After repository inspection, the agent reads the matching reference file and uses those shapes to generate scaffolds.

---

## The 7L Workflow

### L1 — Structural Scaffold

**Objective**: Create the physical codebase structure.

**Generate**:
- Bounded-context folders
- Domain folders
- Application folders
- Infrastructure folders
- API/interface folders
- Test folders
- File names
- Empty classes
- Empty modules
- Import/export files
- Package/index files

**Do Not Generate**:
- Business rules
- Real validation logic
- Database queries
- External API calls
- Hidden orchestration logic

**Validation Checklist**:
- Folder structure matches existing repo conventions
- Names reflect ubiquitous language
- No duplicate or overlapping modules
- No technical naming where domain naming is required
- No business logic added

**Suggested Review**: Light structural review (naming, misplaced files, bounded-context boundaries, consistency). Automatable.

---

### L2 — Contract Scaffold

**Objective**: Define typed boundaries and dependency seams.

**Generate**:
- Interfaces
- Ports
- Repository contracts
- Gateway contracts
- Service contracts
- Command objects
- Query objects
- Request DTOs
- Response DTOs
- Result types
- Error result types
- Event publisher contracts
- External-system adapter contracts

**Example (TypeScript canonical)**:
```typescript
export interface ApproveLoanUseCase {
  execute(command: ApproveLoanCommand): Promise<ApproveLoanResult>;
}
export type ApproveLoanCommand = {
  loanApplicationId: LoanApplicationId;
  requestedBy: UserId;
};
export type ApproveLoanResult =
  | { status: "approved"; loanId: LoanId }
  | { status: "rejected"; reasons: RejectionReason[] };
```

For Python / Go / Dart shapes, see `references/<lang>.md`.

**Validation Checklist**:
- Every use case has a command/query object
- Every boundary has an interface
- External systems are behind ports
- Return types are explicit
- Errors are typed or represented consistently
- No infrastructure dependency leaks into the domain layer

**Suggested Review**: Contract review (dependency direction, type completeness, mockability, interface granularity, contracts vs. ACs). **First meaningful review gate.**

---

### L3 — Domain Scaffold

**Objective**: Create the DDD semantic model without implementing business logic.

**Generate**:
- Aggregate roots
- Entities
- Value objects
- Domain events
- Domain services
- Policy placeholders
- Specification placeholders
- Factory method signatures
- Enum declarations
- Invariant names
- Domain error classes
- Anti-corruption layer contracts

**Domain Rules**:

Aggregate methods may contain:
- TODO markers
- Invariant names
- NotImplemented errors
- References to acceptance criteria

Aggregate methods may **not** contain:
- Completed business rules
- Full validation implementation
- Hidden state transitions
- Non-trivial calculations

**Example (TypeScript canonical)**:
```typescript
export class LoanApplication {
  private constructor(
    private readonly id: LoanApplicationId,
    private readonly borrowerId: BorrowerId,
    private readonly requestedAmount: Money,
    private status: LoanApplicationStatus
  ) {}
  static submit(command: SubmitLoanApplicationCommand): LoanApplication {
    // TODO AC-LOAN-001: enforce requested amount eligibility invariant
    // TODO AC-LOAN-002: emit LoanApplicationSubmitted event
    throw new Error("Not implemented");
  }
  approve(decision: ApprovalDecision): void {
    // TODO AC-LOAN-003: only pending applications may be approved
    // TODO AC-LOAN-004: emit LoanApproved event
    throw new Error("Not implemented");
  }
}
```

For Python / Go / Dart shapes, see `references/<lang>.md`.

**Validation Checklist**:
- Aggregate roots are explicit
- Entity ownership is clear
- Value objects replace primitive obsession where meaningful
- Events are named in domain language
- Policies are named but not implemented
- Invariants are named and linked to acceptance criteria
- Domain layer does not depend on infrastructure

**Suggested Review**: Deep domain review (aggregate boundaries, invariant ownership, domain naming, entities-as-services anti-pattern, technical concerns polluting domain). **One of the two most important review gates.**

---

### L4 — Behaviour Scaffold

**Objective**: Create behavioural test intent from user stories and acceptance criteria.

**Generate**:
- Unit test skeletons
- Behavioural test skeletons
- Contract test skeletons
- Edge-case test skeletons
- Given / When / Then comments
- Test names mapped to AC IDs
- Fixture builder placeholders
- Mock declarations
- Expected event assertions
- Expected error assertions
- Expected audit/logging assertions where required

**Example (TypeScript canonical)**:
```typescript
describe("ApproveLoanUseCase", () => {
  describe("AC-LOAN-003: only pending applications may be approved", () => {
    it("rejects approval when the loan application is already rejected", async () => {
      // Given: a rejected loan application exists
      // And:   the borrower exists
      // When:  the approve loan use case is executed
      // Then:  the result is a domain error
      // And:   no LoanApproved event is emitted
      // And:   no approval audit record is written
    });
  });
});
```

For Python / Go / Dart shapes, see `references/<lang>.md`.

**Test Naming Rule**: Every test skeleton must include one of:
- Acceptance criteria ID
- User story ID
- Feature task ID
- Domain invariant name

**Validation Checklist**:
- Every acceptance criterion has at least one test skeleton
- Negative paths are represented
- Edge cases are represented
- Domain events are asserted where relevant
- Side effects are visible
- Test names describe business behaviour, not implementation details

**Suggested Review**: Behavioural review (coverage vs. ACs, missing edge cases, GWT clarity, implementation coupling). **Second most important review gate.**

---

### L5 — TDD Implementation Shell

**Objective**: Prepare the executable shell for red-green-refactor.

**Generate**:
- Constructor dependency wiring
- Mock setup
- Fake adapters
- In-memory repositories
- Fixture builders
- Arrange / Act / Assert blocks
- NotImplemented method bodies
- Test files that compile
- Minimal application service shells
- Explicit TODOs mapped to AC IDs

**Example (TypeScript canonical)**:
```typescript
export class ApproveLoanUseCaseImpl implements ApproveLoanUseCase {
  constructor(
    private readonly loanApplications: LoanApplicationRepository,
    private readonly borrowers: BorrowerRepository,
    private readonly eligibilityPolicy: BorrowerEligibilityPolicy,
    private readonly events: DomainEventPublisher,
    private readonly audit: AuditLog
  ) {}
  async execute(command: ApproveLoanCommand): Promise<ApproveLoanResult> {
    // TODO AC-LOAN-001: load loan application
    // TODO AC-LOAN-002: verify borrower exists
    // TODO AC-LOAN-003: evaluate eligibility policy
    // TODO AC-LOAN-004: approve or reject aggregate
    // TODO AC-LOAN-005: persist aggregate
    // TODO AC-LOAN-006: publish domain events
    // TODO AC-LOAN-007: write audit record
    throw new Error("Not implemented");
  }
}
```

For Python / Go / Dart shapes, see `references/<lang>.md`.

**Validation Checklist**:
- Tests are discoverable by the test runner
- Project compiles where possible
- Intentional failures are explicit
- Dependencies are mockable
- Fakes do not contain hidden business logic
- TODOs map to acceptance criteria
- TDD can start immediately

**Suggested Review**: TDD readiness review (compile/typecheck status, intentional failures, mocks/fakes adequacy, business logic leakage, TODO-to-AC traceability).

---

### L6 — Runtime Scaffold

**Objective**: Prepare production wiring without completing business logic.

**Generate**:
- API route/controller skeletons
- CLI handlers if applicable
- Message consumers
- Scheduled job handlers
- Dependency injection modules
- Configuration keys
- Feature flag placeholders
- Authorization middleware placeholders
- Persistence mapping placeholders
- Migration placeholders
- OpenAPI or API contract skeletons
- Logging placeholders
- Metrics placeholders
- Trace/span placeholders
- Audit hooks
- Health checks

**Example (TypeScript canonical)**:
```typescript
router.post(
  "/loan-applications/:id/approve",
  requirePermission("lending.approve"),
  async (req, res) => {
    // TODO AC-LOAN-APPROVAL-API-001: map request to ApproveLoanCommand
    // TODO AC-LOAN-APPROVAL-API-002: call ApproveLoanUseCase
    // TODO AC-LOAN-APPROVAL-API-003: map result to HTTP response
    throw new Error("Not implemented");
  }
);
```

For Python / Go / Dart shapes, see `references/<lang>.md`.

**Validation Checklist**:
- Runtime entry points map to use cases
- Controllers do not contain business logic
- Auth placeholders are explicit
- Observability hooks are present
- Persistence mapping is separated from domain model
- API contracts reflect typed application contracts

**Suggested Review**: Runtime integration review (controller/use-case separation, auth placeholders, observability completeness, persistence isolation, integration risks).

---

### L7 — Traceability and Ontology Scaffold

**Objective**: Create or update the machine-readable traceability layer. **Mandatory for agentic SDLC.**

**Generate / Update**:
- ontology.yaml
- feature_traceability.yaml
- domain_taxonomy.yaml
- dependency_map.yaml

Use the repository's existing naming convention if one already exists. In this repo:
- Feature traceability lives at `.workitems/$ARGUMENTS/traceability.yaml`
- Project ontology lives in `ontology/*.yaml`

**Required L7 Content**:
```yaml
bounded_contexts:
  Lending:
    features:
      ApproveLoan:
        feature_id: FEAT-LOAN-APPROVAL
        user_stories:
          - US-LOAN-001
        acceptance_criteria:
          - AC-LOAN-001
          - AC-LOAN-002
          - AC-LOAN-003
        application_layer:
          commands:
            - ApproveLoanCommand
          use_cases:
            - ApproveLoanUseCase
            - ApproveLoanUseCaseImpl
          results:
            - ApproveLoanResult
        domain_layer:
          aggregates:
            - LoanApplication
          entities:
            - Borrower
          value_objects:
            - LoanApplicationId
            - BorrowerId
            - Money
          policies:
            - BorrowerEligibilityPolicy
          invariants:
            - Only pending applications may be approved
            - Rejected applications must include at least one reason
          events:
            - LoanApproved
            - LoanRejected
        ports:
          repositories:
            - LoanApplicationRepository
            - BorrowerRepository
          gateways:
            - CreditScoreGateway
          publishers:
            - DomainEventPublisher
        tests:
          unit:
            - approve-loan.use-case.spec.ts
          behavioural:
            - approve-loan.behaviour.spec.ts
          contract:
            - approve-loan.contract.spec.ts
        runtime:
          api_routes:
            - POST /loan-applications/{id}/approve
          permissions:
            - lending.approve
          audit_events:
            - LOAN_APPROVAL_DECISION
```

In this repo, write the `bounded_contexts` block as an additional top-level key in `.workitems/$ARGUMENTS/traceability.yaml`. The flat `acm_nodes` / `acm_edges` graph entries (existing schema) are generated from this block on the next ACM ingest. See `docs/ADR/ADR-016-ddd-7l-scaffold.md` for the schema bridge plan.

**Validation Checklist**:
- Every feature maps to user stories
- Every acceptance criterion maps to tests
- Every use case maps to contracts
- Every aggregate maps to invariants and events
- Every external dependency maps to a port
- Every runtime entry point maps to a use case
- No orphan files exist
- No orphan tests exist
- No orphan domain objects exist

**Suggested Review**: Traceability review (story-to-code linkage, AC-to-test coverage, orphan artefacts, missing dependencies, ontology vs. actual code structure).

---

## Code Review Cadence

Do not wait until the end only. For a 7L scaffold, review must be **staged**.

### Recommended Review Gates

| After | Review Type | Depth | Mandatory |
|-------|-------------|-------|-----------|
| L1 | Structural | Light | Optional |
| L2 | Contract | Medium | Yes |
| L3 | Domain | Deep | **Yes** |
| L4 | Behaviour | Deep | **Yes** |
| L5 | TDD readiness | Medium | Yes |
| L6 | Runtime | Medium | Yes (if runtime layer exists) |
| L7 | Traceability | Deep | **Yes** |
| Final | Full scaffold | Deep | Yes |

### Default Cadence (recommended)

```
L1 + L2 → Code Review Gate 1
L3      → Code Review Gate 2
L4 + L5 → Code Review Gate 3
L6 + L7 → Final Scaffold Review
TDD implementation starts only after final scaffold review passes
```

For small features: L3 review + final L7 review.
For critical enterprise systems: review after every layer.

The most important review gates are:
1. **L3 domain review** (aggregate boundaries, invariant placement)
2. **L4 behavioural review** (AC coverage, GWT clarity)
3. **L7 traceability review** (orphans, story-to-code linkage)

### Review Skill

Invoke `@scaffold-review` (not `@code-review`). The scaffold-review skill:
- Skips Phase 1 quality gates (intentional `NotImplemented` failures expected)
- Runs design-aware Phase 2 (reviews scaffold against design, not just syntax)
- Outputs the structured Scaffold Review Report (see below)

---

## Code Review Agent Instructions

When `@scaffold-review` is invoked, the review must check the scaffold against the design, not merely against syntax.

### Review Dimensions

1. Alignment with user stories
2. Acceptance criteria coverage
3. DDD boundary correctness
4. Aggregate ownership
5. Invariant placement
6. Interface and port quality
7. Dependency direction
8. Testability
9. Runtime separation
10. Observability placeholders
11. Traceability completeness
12. Absence of premature business logic

### Review Output Format

```markdown
# Scaffold Review Report

## Verdict
PASS | PASS WITH ISSUES | BLOCKED

## Scope Reviewed
- Layers reviewed:
- Feature IDs:
- User stories:
- Acceptance criteria:

## Blocking Issues
| ID | Layer | File | Issue | Required Fix |
|---|---|---|---|---|

## Non-Blocking Issues
| ID | Layer | File | Issue | Suggested Fix |
|---|---|---|---|---|

## Missing Traceability
| Artifact | Missing Link |
|---|---|

## Premature Business Logic Detected
| File | Method | Problem |
|---|---|---|

## DDD Concerns
| Concern | Explanation | Recommendation |
|---|---|---|

## Test Coverage Concerns
| Acceptance Criteria | Missing / Weak Test |
|---|---|

## Final Recommendation
Proceed | Revise before continuing | Return to design
```

---

## Handoff to TDD

After L7 final scaffold review passes, call the TDD implementation skill (`/tdd`).

The TDD skill must follow:

1. Select one acceptance criterion
2. Turn the related scaffolded test into a failing executable test
3. Run test (RED)
4. Implement minimum business logic to pass
5. Run test (GREEN)
6. Refactor
7. Update traceability if behaviour changed
8. Repeat for next acceptance criterion

The TDD skill must not skip from scaffold directly to full implementation.

The TDD skill assumes:
- Contracts exist
- Aggregates exist
- Value objects exist
- Ports exist
- Test skeletons exist
- Fixture builders exist
- Runtime placeholders exist
- Ontology exists
- TODOs are mapped to acceptance criteria

This keeps the TDD skill clean and prevents it from becoming a mixed design / scaffold / implementation agent.

---

## Strict Rules

- Never invent business rules
- Never implement business logic before TDD starts
- Never place infrastructure dependencies inside domain objects
- Never use primitive types where the design clearly requires value objects
- Never create tests that cannot be mapped to acceptance criteria or invariants
- Never create a repository/gateway implementation without a corresponding port
- Never create runtime routes that bypass application use cases
- Never skip ontology or traceability updates

---

## Final Output

At the end of the 7L scaffold, produce:

1. Scaffold summary
2. Files created or modified
3. Layer-by-layer completion checklist
4. Review findings
5. Open issues
6. TDD readiness status
7. List of acceptance criteria ready for TDD implementation
8. Traceability summary

TDD may start only when the final scaffold review passes.

---

## Why This Skill Exists

For DDD projects, the most dangerous errors happen **before** code implementation:

- Wrong aggregate boundary
- Weak contract
- Misplaced invariant
- Missing acceptance-criteria coverage
- Infrastructure leaking into domain
- Untraceable tests

An end-only review catches these too late. The 7L scaffold gives review gates four chances to catch them before TDD invests effort against the wrong shape.

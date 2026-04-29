# ADR-016 — DDD 7L Scaffold Before TDD

- **Status:** Proposed
- **Date:** 2026-04-29
- **Deciders:** jbellish
- **Related:** ADR-013 (biz/sw design split), CLAUDE.md (TDD-first rule), `.claude/rules/workflow.md` (8-step workflow)

## Context

The SDLC pipeline has biz design (`@biz-functional-design`) → sw design
(`@sw-designpipeline`) → TDD (`/tdd`). Between sw design and TDD there is
a gap: the design produces `design.md`, `tasks.md`, and `traceability.yaml`
(structural plan, port/adapter node IDs, task-to-source-path mapping), but
the actual code structure — folders, interfaces, aggregates, value
objects, domain events, test skeletons, runtime shells — does not exist
yet. TDD starts from a near-empty filesystem and is responsible for both
*establishing the DDD shape* and *implementing business logic*. This
overloads the TDD phase and means design errors (wrong aggregate
boundary, leaked infrastructure, missing AC coverage, untraceable tests)
are only discovered after substantial test-and-code investment.

For DDD-shaped features, the most dangerous errors happen *before* code
implementation. End-only review catches them too late.

## Decision

Introduce **`@ddd-7l-scaffold`** as a Step 2.5 sub-step between Design
(Step 2) and TDD Build (Step 3). The skill transforms approved design
artefacts into a production-grade, layered code scaffold ready for TDD.

### Skill mechanics

- **Trigger**: invoked manually after `@sw-designpipeline` completes and
  the Step 2 User Gate is approved. Optional — only for features with
  bounded contexts, aggregates, ports, or other DDD-shaped structure.
- **Scope**: writes folders, empty modules, interfaces, command/query
  types, sealed result types, aggregate / entity / value-object / event
  / policy classes (with `NotImplemented` bodies and AC-linked TODOs),
  test skeleton files (with skip markers and Given/When/Then comments),
  DI wiring with fakes / in-memory adapters, runtime route / handler
  shells, and the `bounded_contexts` ontology block in `traceability.yaml`.
- **Strict rule**: no business logic. Method bodies are `NotImplemented`
  + TODO markers. Test bodies are GWT comments + skip markers. The
  codebase must compile / type-check, but every test skip is intentional.
- **Reviews**: 4 staged gates via the new `@scaffold-review` skill (see
  below). Gate 4 is a HITL gate — TDD cannot start until the user
  approves Gate 4.
- **Handoff**: `/tdd` activates skeleton tests one acceptance criterion
  at a time. The TDD skill assumes the scaffold is in place.

### Language portability

`SKILL.md` uses TypeScript as the canonical illustrative language because
it offers the cleanest DDD-shape syntax (interfaces, discriminated
unions, classes with `private constructor`). Per-language code shapes
live in `.claude/skills/ddd-7l-scaffold/references/<lang>.md`:

- `python.md` — Pydantic / dataclasses / Protocol ports / pytest / FastAPI
- `go.md` — interfaces / structs / typed errors / `_test.go` / chi
- `dart.md` — sealed classes / abstract ports / Riverpod / flutter_test / shelf

Adding a new language: copy any reference file, replace examples with
idiomatic shapes, keep the section order (L1–L7).

### `@scaffold-review` skill

A new dedicated skill for reviewing scaffold output. Skips Phase 1
automated quality gates (because intentional `NotImplemented` failures
are expected — `@code-review`'s gate would block) and runs a
design-aware Phase 2 review across 12 dimensions: alignment with user
stories, AC coverage, DDD boundary correctness, aggregate ownership,
invariant placement, port quality, dependency direction, testability,
runtime separation, observability placeholders, traceability
completeness, absence of premature business logic. Outputs the
structured Scaffold Review Report.

### TDD-first rule narrowing

The CLAUDE.md global rule "Before implementing any new behaviors or bug
fixes, write tests for them" stands. The 7L scaffold is a **narrow,
named exception**: it emits structural shells (no method bodies, no
logic) before TDD. The first real test is the one TDD writes by
activating a skeleton in the GREEN phase. Skeletons themselves contain
no behaviour — they are GWT comments and skip markers, not real tests.

This exception is documented in CLAUDE.md.

## Consequences

### Positive

- DDD tactical patterns (aggregates, value objects, domain events,
  invariants, policies) are codified in real source files before TDD,
  so review can catch boundary errors at four stages.
- TDD phase is cleaner — pure red/green/refactor against an existing
  scaffold, not "establish shape + implement logic" in one cycle.
- Traceability is end-to-end: every test skeleton, every TODO, every
  port, every route maps to an AC and is logged in
  `traceability.yaml`'s `bounded_contexts` block.
- Language-portable: same skill works for Python, Go, Dart, TypeScript
  projects via per-language reference files.

### Negative

- Adds one phase (Step 2.5) to the workflow, with one new HITL gate
  (Final Scaffold Review). Mitigated by the skill being optional for
  non-DDD features.
- TDD-first rule has a narrow named exception. Mitigated by clear
  scope in CLAUDE.md ("structural shells with no method bodies").
- Two new skills (`@ddd-7l-scaffold`, `@scaffold-review`) to maintain.

### Deferred to follow-up workitems

These are not blocking for first use but should be tracked:

1. **L7 schema bridge (deferred)**. The skill emits the canonical
   `bounded_contexts:` block (per the user's spec). The existing
   ACM-graph schema uses flat `acm_nodes` / `acm_edges` / `tests[]`. A
   small generator should derive flat graph entries from the
   `bounded_contexts` block on next ACM ingest. Until that lands, the
   `bounded_contexts` block is human-readable design intent and the
   flat entries continue to come from `@sw-designpipeline`.

2. **`sw-designpipeline` ontology coordination (deferred)**.
   `sw-designpipeline/SKILL.md` currently declares itself the sole
   writer of `ontology/technical-implementation.yaml`. A small note
   should be added recognising `@ddd-7l-scaffold` as co-writer for
   tactical-pattern namespaces (aggregate, value-object, event, policy
   — to be added by ADR-013 amendment if those become first-class
   graph nodes).

3. **`require-workitem.sh` exception (deferred, may not be needed)**.
   The hook blocks production-path writes unless the feature is the
   next-unchecked in PLAN.md. Scaffold writes lots of production
   paths. As long as the scaffold runs against the next-unchecked
   feature, the hook is not blocking. If users want to scaffold
   features out of sequence, an exception will be needed.

4. **ADR-013 namespace amendment (deferred)**. To make
   aggregate / value-object / domain-event first-class graph nodes,
   ADR-013's namespace list (`module:`, `service:`, `port:`, `adapter:`,
   `class:`, `fn:`, `adr:`) needs to be extended with
   `aggregate:`, `value_object:`, `event:`, `policy:`,
   `invariant:`. Until then, those concepts are tagged in scaffold
   text and `bounded_contexts` block but not as graph node IDs.

## Status transition

This ADR moves to **Accepted** when the user runs `@ddd-7l-scaffold`
against a real feature and confirms the workflow is productive. If
deferred items become blockers in practice, this ADR is amended or
superseded.

## References

- `.claude/skills/ddd-7l-scaffold/SKILL.md` — the skill prompt
- `.claude/skills/ddd-7l-scaffold/references/{python,go,dart}.md` — per-language shapes
- `.claude/skills/scaffold-review/SKILL.md` — the review skill
- `.claude/rules/workflow.md` Step 2.5 — workflow position
- `.claude/rules/sdlc-flow-diagram.md` — SDLC diagram update
- ADR-013 — biz/sw design split (sets ontology namespace conventions)

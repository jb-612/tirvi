# Between Design and TDD: The 7-Layer Scaffold

**A method for the gap nobody names**

*Draft — 2026-04-29*

---

Most modern software teams have settled into a comfortable rhythm. Domain-Driven Design gives you the strategic and tactical patterns. Test-Driven Development gives you the build cadence. The handoff between them, the way a team moves from "design approved" to "first failing test," is treated as plumbing — a few hours of file creation and import wiring before the real work begins.

That treatment is wrong. The handoff is not plumbing. It is the single highest-leverage moment in the lifecycle of a feature, and most teams spend it badly.

This essay introduces a method for that moment. It calls itself the **7-Layer Scaffold**, or 7L, and it sits as a named phase between approved design and the first red TDD test. It does not implement business logic. It does not invent missing requirements. It does one thing: it transforms an approved design into a production-grade, layered, traceable code skeleton, reviewed at four staged gates, ready for TDD to fill in the behaviour. Done correctly, it makes TDD trivially clean. Done badly — or skipped — and TDD becomes the place where DDD errors finally surface, after fifty tests have been written against the wrong aggregate boundary.

## The gap nobody names

Walk through the typical SDLC pipeline of a mature shop. There is product discovery. There are user stories with acceptance criteria. There is a functional design, often in markdown. There are task breakdowns. There is design review — sometimes multi-round, sometimes adversarial. Then, by convention, the team moves to TDD.

Between "design review approved" and "I write the first failing test," what actually happens?

In most teams: nothing structured. A developer opens an editor, creates folders, sketches an interface, opens a test file, types `describe("ApproveLoanUseCase")`, and writes the first failing assertion. The aggregate boundary, the value-object set, the port granularity, the test naming convention, the runtime entry point, the observability hooks — all of these emerge implicitly, in a few minutes, in one developer's head, with no review.

This is the gap. It is the single largest source of DDD failures in production codebases. Wrong aggregate boundaries discovered after 200 tests. Infrastructure leaking into domain because nobody reviewed the imports at L1. Acceptance criteria that have no test because nobody compared the test file list against the AC list. Untraceable tests that pin the implementation, not the behaviour. Ports that are too granular or not granular enough. Runtime handlers that quietly contain business logic the design never specified.

These are not implementation bugs. They are *shape* bugs. They appear before the first real test runs. End-of-phase code review catches them too late: by then, the team has invested days into the wrong shape and the cost of fixing it has compounded.

## The principle

The 7-Layer Scaffold rests on one principle: **some decisions are too important to be emergent.**

TDD's signature claim is that good design emerges from the test-driven cycle — write a test, write the minimum code to pass, refactor toward a cleaner shape, repeat. This claim is true for *behaviour*. It is partially true for *small-grained design*. It is **false** for the strategic and tactical structure of a domain.

You will not refactor your way into the right aggregate boundary. You will not refactor a `LoanApplicationService` god-object into a proper aggregate root once fifty tests already depend on its method signatures. You will not retroactively introduce a value object to replace `string` in fifteen call sites without breaking everything.

DDD's tactical patterns — aggregate roots, entities, value objects, domain events, invariants, policies, anti-corruption layers — must be decided **before** the test-driven cycle begins, because they are the load-bearing structure that the tests will lean against. Get them wrong, and every subsequent test wedges them deeper into the wrong shape.

The 7-Layer Scaffold is the formal name for the phase where these decisions become code.

## The seven layers

Each layer is a small, focused, reviewable artifact. The layers are sequential because each builds on the previous. They are named L1 through L7 to make review and traceability unambiguous.

**L1, Structural Scaffold.** Folders, empty modules, package files, file names that reflect ubiquitous language. No business logic. The output is a navigable skeleton that says "the bounded contexts live here, the domain layer here, the application layer here, the infrastructure here." A junior developer can find any concept in five seconds.

**L2, Contract Scaffold.** Interfaces, ports, repository contracts, gateway contracts, command and query objects, request and response DTOs, typed result types, typed errors. External systems live behind ports. Return types are explicit. Error shapes are consistent. This is the first layer where dependency direction is enforceable: if you wrote it correctly, the domain layer has zero imports from infrastructure.

**L3, Domain Scaffold.** Aggregate roots, entities, value objects, domain events, policies, specifications, factories, domain errors, and **named invariants** — invariants linked to acceptance criteria as TODO markers, not implementations. This is the layer where DDD lives. The aggregate's `approve()` method exists, with the right signature, and its body is a list of `// TODO AC-LOAN-003:` markers and a `throw NotImplemented`. The shape is final; the behaviour is deferred.

**L4, Behaviour Scaffold.** Test skeleton files. Every acceptance criterion has at least one test skeleton. Every test name includes the AC ID. Every test body has Given/When/Then comments. No assertions yet — the test is a `pytest.mark.skip` or `t.Skip` with a labelled reason. The test runner discovers the file. The structure is final; the assertions are deferred.

**L5, TDD Implementation Shell.** Constructor injection, in-memory repository fakes, fixture builders, application service implementations with `NotImplemented` bodies and AC-linked TODOs. The codebase **compiles**. Every test that fails fails *intentionally*. This is the moment the scaffold becomes executable.

**L6, Runtime Scaffold.** API routes, controllers, message consumers, scheduled job handlers, dependency injection modules, configuration keys, authorization placeholders, persistence mapping placeholders, logging hooks, metrics hooks, tracing hooks, audit hooks, health checks. Every runtime entry point maps to an application use case. Controllers contain TODO + map-to-use-case sketches; no business logic.

**L7, Traceability and Ontology Scaffold.** A machine-readable map from features to user stories to acceptance criteria to bounded contexts to aggregates to invariants to events to ports to tests to runtime entry points to permissions to audit events. No orphan files. No orphan tests. No orphan domain objects. Every artifact in the scaffold is reachable from a user story; every user story decomposes into artifacts.

That is the 7L. Seven sequential, reviewable, testable artifacts. Together, they constitute a feature's structural skeleton, ready for TDD.

## Staged review

The most important contribution of the 7L method is not the layers themselves. It is the **review cadence**.

Most code review is end-of-phase: pull request, squash review, merge. The 7L method asserts that for DDD-shaped features, end-of-phase review is too late. By the time you've finished L7, you've already written L1 through L6. If L3 was wrong, you've wasted L4 through L7 building against a broken model.

The 7L method runs review at four gates:

| Gate | After | Depth | Why this gate matters |
|------|-------|-------|----------------------|
| 1 | L1 + L2 | Medium | Catches structural and contract errors before they propagate |
| 2 | L3 | **Deep** | Catches DDD boundary errors — wrong aggregate ownership, misplaced invariants, primitive obsession |
| 3 | L4 + L5 | Deep | Catches missing AC coverage, weak GWT scenarios, untestable seams |
| 4 | L6 + L7 | **Deep** | Catches orphan artifacts, untraceable tests, runtime business logic |

Gates 2 and 4 are the unmissable ones. Gate 2 (L3 domain review) is where wrong aggregate boundaries get caught. Gate 4 (L7 traceability review) is where orphans and gaps become visible.

A team that runs Gate 2 well will never ship the wrong aggregate to production. A team that runs Gate 4 well will never ship a feature with an AC that has no test. End-of-phase review cannot replicate either of these properties because by the time the phase ends, the cost of the fix is already too high.

## The constraint that makes it work

The 7L scaffold has one strict rule that makes the entire practice clean: **no business logic.**

Method bodies are `NotImplemented`. Test bodies are GWT comments and skip markers. Repository fakes have empty in-memory dicts and `NotImplemented` saves. Use-case implementations are constructor-injected shells. Routes contain TODO sketches.

This constraint is what gives the scaffold its review tractability. A reviewer at Gate 2 looks at the aggregate and asks: "is the *shape* right?" They do not have to wade through invariant validation logic to find the boundary error. The shape is the only thing on the table.

The constraint also gives the handoff to TDD a clean shape. When TDD picks up after Gate 4, it does exactly one thing per acceptance criterion: take a skeleton test, replace its skip marker with a real assertion that fails, write the minimum code to pass, refactor. There is no "establish the shape" work mixed with "implement the behaviour." The shape is already done. TDD is pure.

This is what the user-stories-→-design-→-TDD pipeline was supposed to deliver but rarely does. The 7L scaffold is the missing intermediate that lets it.

## Why this matters for agentic SDLC

There is a quieter contribution buried in the 7L approach. The method is not just a workflow document; it is codified as an **agent skill** — a structured prompt that an autonomous coding agent reads and executes. The skill carries strict rules ("never invent business rules"), staged validation ("self-check after L3 and L7"), language portability ("TypeScript canonical, per-language reference files"), and explicit handoff protocols ("call `/tdd` only after Gate 4 approves").

This matters because most discussions of agentic coding focus on the wrong moments. They focus on test generation or code completion or one-shot implementation. The 7L approach identifies a different moment: the moment when human judgement about *shape* gets locked in. That moment is the highest-leverage moment in the lifecycle. Codifying it as an agent skill — with explicit review gates and explicit forbidden actions — means agentic SDLC can preserve the discipline humans bring to shape decisions, instead of eroding it under one-shot pressure.

The 7L scaffold is, in this sense, a small but real contribution to how humans and agents collaborate on software. It says: *here is the place where the agent must stop, present the work, and wait for human review*. It marks the boundaries.

## What 7L is not

It is not anti-TDD. TDD still owns every method body, every assertion, every refactor. The 7L scaffold deliberately leaves all of that work for TDD.

It is not anti-design-pipeline. Design-pipeline still owns user stories, functional design, architecture, task breakdown, and the multi-round design review that precedes scaffolding. The 7L scaffold consumes design-pipeline outputs; it does not replace them.

It is not a code generator that aspires to write working features. It produces compilable shells. The shells are deliberate and useful, but they are not the product.

It is the missing middle.

## A modest proposal

If your team has a design phase and a TDD phase and a comfortable handoff that you have never thought about — try this:

1. The next time you finish design review and are about to start TDD, stop. Run the 7L scaffold first.
2. Pause for a real review at Gate 2. Look at L3. Ask: are the aggregate boundaries right? Is anything in the wrong place?
3. Pause for a real review at Gate 4. Look at L7. Ask: does every AC have a test? Does every test trace to an AC? Are there orphans?
4. Then start TDD.

Notice what you find at Gate 2 and Gate 4. Notice how clean TDD becomes. Notice how the test runner now reports failing tests that are *intentional*, not accidental.

If the practice is right, it will pay for itself the first time it catches a wrong aggregate boundary. If it is wrong for your context, you will know within one feature.

The 7-Layer Scaffold is a small idea. But it is a real one, and it lives in the gap nobody else has named.

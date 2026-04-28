# Testing Skills — Architecture & Workflows

## Skill Map

```
                         ┌─────────────────────┐
                         │    @test-design      │
                         │  (WHAT to test)      │
                         │  STD.md + trace.yaml │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
          ┌─────────────┐ ┌─────────────────┐ ┌──────────┐
          │@test-mock-  │ │ @test-functional │ │  /tdd    │
          │  registry   │ │  (Chicago school)│ │ (router) │
          │ fakes from  │ │ FUNC/SMOKE/REG   │ └────┬─────┘
          │ port ifaces │ │ from STD yaml    │      │
          └──────┬──────┘ └────────┬─────────┘      │
                 │                 │          ┌──────┴──────┐
                 │    imports      │          ▼             ▼
                 ├─────────────────┤   ┌───────────┐ ┌───────────┐
                 │    imports      │   │ @tdd-go   │ │@tdd-flutter│
                 ├─────────────────┘   │  unit     │ │  unit      │
                 │    imports          │  tests    │ │  tests     │
                 └─────────────────┐   │ bundled/  │ │ bundled/   │
                                   │   │ strict    │ │ strict     │
                                   │   └─────┬─────┘ └─────┬─────┘
                                   │         │             │
                 ┌─────────────────┘         │             │
                 ▼                            ▼             ▼
          pkg/testutil/fakes/         *_test.go      flutter_app/test/

───────────────────────────────────────────────────────────────
  POST-IMPLEMENTATION
───────────────────────────────────────────────────────────────

     ┌──────────────────┐    ┌────────────────────┐
     │ @integration-test│    │     @testing        │
     │ cross-boundary   │    │  quality gates      │
     │ (real impls both │    │  runs everything    │
     │  sides + fakes)  │    │  lint/cover/SAST    │
     └──────────────────┘    └────────────────────┘
                                      │
                              ┌───────┴────────┐
                              │@verification-  │
                              │     loop       │
                              │ confirms STD   │
                              │ coverage done  │
                              └────────────────┘
```

## Two Schools

```
 CHICAGO (behavior)              LONDON (isolation)
 @test-functional                @tdd-go / @tdd-flutter
 ─────────────────               ──────────────────────
 Public API in, assert out       Mock collaborators
 Real collaborators inside       One unit at a time
 Fakes at system boundary        Port-level fakes
 Batch per feature from STD      Per task from tasks.md
 FUNC / SMOKE / REG              Unit tests only
```

## TDD Router Flow

```
 /tdd N01/F01/T03 [--accept-all]
  │
  ├── Validate: design.md ✓  tasks.md ✓  stories.md ✓
  ├── Detect: *_test.go → Go │ *.dart → Flutter
  │
  └── Delegate:
       @tdd-go                    @tdd-flutter
       ┌──────────────────┐       ┌──────────────────┐
       │ Evaluate task     │       │ Evaluate task     │
       │ Go decision table │       │ Flutter dec table │
       │ → BUNDLED/STRICT  │       │ → BUNDLED/STRICT  │
       │ "Approve?" (HITL) │       │ "Approve?" (HITL) │
       ├──────────────────┤       ├──────────────────┤
       │ RED   (all/one)   │       │ RED   (all/one)   │
       │ GREEN (pass all)  │       │ GREEN (pass all)  │
       │ REVISE? (if sigs) │       │ REVISE? (if sigs) │
       │ REFACTOR (CC≤5)   │       │ REFACTOR (analyze)│
       └──────────────────┘       └──────────────────┘
```

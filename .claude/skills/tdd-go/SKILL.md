---
name: tdd-go
description: Go-native TDD micro-cycle engine. Table-driven tests, *_test.go co-located, 3-agent separation, gocyclo CC≤5, traceability updates.
argument-hint: "[phase/feature-id/task-id]"
---

Execute Go TDD build for task $ARGUMENTS.
Use `--accept-all` to skip mode selection prompt.

## Prerequisites

1. Read `.workitems/{feature}/design.md` — confirm design elements exist
2. Read `.workitems/{feature}/tasks.md` — find target task; confirm
   unchecked by checking that the line `- [ ] **T-NN done**`
   immediately under the `## T-NN: <title>` header is `[ ]`, not `[x]`
   (per `.claude/rules/task-format.md`)
3. Read `.workitems/{feature}/traceability.yaml` — will update after tests pass
4. Verify tooling: `command -v golangci-lint` (includes gocyclo)

If design missing: "Run /design-pipeline first."

## Step 0: Evaluate Task — Mode Selection

Evaluate the task against the decision table and recommend a mode:

| Criterion | Bundled | Strict |
|-----------|---------|--------|
| Interface pre-designed in design.md | YES | |
| Adapter / specification transcription | YES | |
| Table-driven test pattern fits naturally | YES | |
| 5+ methods with uniform pattern | YES | |
| Solution shape unknown or TBD | | YES |
| Concurrency primitives (goroutine lifecycle) | | YES |
| Platform-specific behavior discovery | | YES |
| Novel algorithm (no prior art in codebase) | | YES |

Unless `--accept-all` is set, prompt the user:
"For task {id} ({description}), I recommend **{BUNDLED|STRICT}** mode
because {reason}. Approve or change?"

## Core Principles

1. No production `*.go` unless making a failing `*_test.go` pass
2. Write tests before implementation (all tests per task in bundled,
   one at a time in strict)
3. No more production code than sufficient to pass

## Agent Separation (Go)

| Agent | Phase | Can Edit | Cannot Edit |
|-------|-------|----------|-------------|
| `tdd-go-test-writer` | RED | `*_test.go` in cmd/, internal/, pkg/ | non-test `*.go` |
| `tdd-go-code-writer` | GREEN | non-test `*.go` in cmd/, internal/, pkg/ | `*_test.go` |
| `tdd-go-refactorer` | REFACTOR | both | no new behavior |

Marker: `echo "test-writer" > /tmp/ba-tdd-markers/{hash}`
Hook: `enforce-tdd-separation.sh` checks `*_test.go` suffix on filename.

## Hexagonal Test Placement

| Layer | Test Location | Test Strategy |
|-------|--------------|---------------|
| `internal/core/domain/` | `domain/*_test.go` | Pure value object tests, no mocks |
| `internal/core/port/` | No tests (interfaces only) | Tested via service tests |
| `internal/core/service/` | `service/*_test.go` | Mock ports from `pkg/testutil/` |
| `internal/adapter/db/` | `db/*_test.go` | SQLite `:memory:` via `pkg/testutil/db.go` |
| `internal/adapter/dispatch/` | `dispatch/*_test.go` | Mock subprocess/HTTP |
| `internal/bff/handler/` | `handler/*_test.go` | bufconn + mock services |
| `cmd/*/` | `main_test.go` | Build verification only |

## RED Phase (tdd-go-test-writer)

### Bundled Mode (default)
1. Read task from tasks.md — note `design_element` and `test file`
2. Read design.md interfaces for the design element
3. Write ALL `func Test*` for the task in the specified `*_test.go` file(s)
   (table-driven subtests OK for same method/contract)
4. Run: `go test -v ./path/to/package/` — verify ALL fail (RED)
5. Report: test files, functions, failure count, behaviors covered
6. Hand off ALL failing tests to code-writer

### Strict Mode
1. Read task from tasks.md — note `design_element` and `test file`
2. Read design.md interfaces for the design element
3. Write ONE `func Test*` in the specified `*_test.go` file
   (table-driven subtests OK if all test the same method/contract)

```go
func TestSharedStore_GetHeartbeats(t *testing.T) {
    store := testutil.NewTestSharedStore(t) // :memory: SQLite

    tests := []struct {
        name    string
        setup   func()
        want    []domain.Heartbeat
        wantErr bool
    }{
        {name: "returns active", setup: func() { /*seed*/ }, want: ...},
        {name: "empty when none", want: nil},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if tt.setup != nil { tt.setup() }
            got, err := store.GetHeartbeats(context.Background())
            if tt.wantErr { require.Error(t, err); return }
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

4. Run: `go test -v -run TestName ./path/to/package/`
5. Verify FAILS (RED)
6. Report: test file, function, failure output, behavior tested

## GREEN Phase (tdd-go-code-writer)

### Bundled Mode (default)
1. Read ALL failing tests for the task
2. Write Go code to pass ALL tests — minimum necessary
3. Run: `go test -v ./path/to/package/` — verify ALL pass (GREEN)
4. Check complexity: `golangci-lint run --enable gocyclo ./path/...`
5. Flag any function CC > 5 (will fix in REFACTOR)
6. If any test needed a signature change: hand back to test-writer for
   a **test revision pass** before proceeding to REFACTOR
7. Report: files modified, tests PASS, CC per function

### Strict Mode
1. Read the failing test
2. Write MINIMUM Go code to pass — nothing more
3. Run: `go test -v -run TestName ./path/to/package/`
4. Verify PASSES (GREEN)
5. Check complexity: `golangci-lint run --enable gocyclo ./path/...`
6. Flag any function CC > 5 (will fix in REFACTOR)
7. Report: files modified, test PASS, CC per function

### Strict Mode: Repeat RED-GREEN until all task behaviors covered.

## REFACTOR Phase (tdd-go-refactorer)

1. Run: `go test ./...` — confirm all GREEN
2. Run: `golangci-lint run` — identify lint + complexity hotspots
3. Apply ONE refactoring at a time:
   - Extract function (reduce CC ≤ 5)
   - Early returns over nested ifs
   - Remove duplication
   - Consolidate test helpers into `pkg/testutil/`
4. After EACH change: `go test ./...`
5. If test fails: revert immediately
6. Run: `gofmt -l . && go vet ./...`

**HITL Gate: Refactor Approval (advisory)**

## Task Completion

1. Flip the standard done marker `- [ ] **T-NN done**` →
   `- [x] **T-NN done**` in `tasks.md` (per
   `.claude/rules/task-format.md`)
2. Update traceability.yaml: add `VERIFIED_BY` edge (task → test)
3. Run coverage: `go test -coverprofile=coverage.out ./...`
4. Check threshold: fail if package coverage < 80%
5. Proceed to next task

## Failure Escalation

Same test fails 3+ times in GREEN → HITL:
A) Retry  B) Skip + issue  C) Abort  D) Invoke debugger agent

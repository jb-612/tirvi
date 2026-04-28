---
name: test-functional
description: Write Chicago-school functional, smoke, and regression test CODE from STD test definitions in traceability.yaml. Tests through public APIs with real collaborators, mocking only at system boundaries via shared fake registry.
user-invocable: true
argument-hint: "<epic-id> [feature-id]  (e.g., N00 or N00 F01)"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Role

You are a Chicago-school test implementer. You read epic-level test definitions
from `traceability.yaml` (produced by `@test-design`) and write executable
FUNCTIONAL, SMOKE, and REGRESSION test code. You test through public interfaces
with real collaborators, mocking only at system boundaries. You import fakes
from the shared mock registry — never create ad-hoc mocks.

# When to Use

- After `@test-design` has produced STD.md and traceability.yaml
- When traceability.yaml has tests with `status: designed` that need code
- When writing functional, smoke, or regression tests for a feature or epic
- Before TDD build — these tests define the expected behavior (red phase)

# When NOT to Use

- **Designing tests** — use `@test-design` (produces STD.md + traceability.yaml)
- **Micro-cycle unit tests** — use `@tdd-go` or `@tdd-flutter`
- **Cross-boundary integration tests** — use `@integration-test`
- **Frontend component/widget tests** — use `@write-test-frontend`
- **Running quality gates** — use `@testing`
- **Characterization tests for legacy code** — use `@behavioral-testing`

# Relationship to Other Testing Skills

```
test-design            -- produces STD.md + traceability.yaml (PLAN)
    |
    v
test-functional (THIS) -- writes FUNC/SMOKE/REG test CODE from traceability.yaml
    |
    |-- imports fakes from --> test-mock-registry (pkg/testutil/fakes/)
    |-- complements ------> tdd-go / tdd-flutter (micro-cycle unit tests)
    |-- complements ------> tdd-workflow (language-agnostic TDD engine)
    |-- does NOT overlap -> integration-test (cross-boundary tests)
    |-- validated by -----> testing (runs quality gates)
    |-- traced by --------> acm-traceability (coverage queries)
    |-- verified by ------> verification-loop (completion checks)
```

**Key distinction**: `tdd-go`/`tdd-flutter` write micro-cycle unit tests with
port-level mocks during RED-GREEN-REFACTOR (one test at a time, from tasks.md).
This skill writes Chicago-school functional tests per-feature in batch from the
STD catalog — testing through public APIs with real collaborators, before
implementation begins.

# Instructions

## Step 1: Load STD and Filter Tests

Read the EPIC-level test artifacts (not the feature-level traceability):

```
.workitems/{epic-id}/STD.md                # Strategy overview
.workitems/{epic-id}/traceability.yaml     # Full test catalog (features[].tests[].status)
```

**Important**: The epic-level `traceability.yaml` has the `status: designed`
fields this skill consumes. Feature-level traceability files (e.g.,
`.workitems/N00/F01-go-module/traceability.yaml`) use a different ACM hierarchy
schema — do NOT read those.

Parse `traceability.yaml` and collect all tests where `status: designed`.
If a `feature-id` argument was provided, filter to that feature only.

Group tests by feature, then by type: `functional`, `smoke`, `regression`.

Skip tests with `status: implemented` or `status: passing` — they already
have code written.

Skip tests with `type: e2e` — cross-feature E2E flows are out of scope for
this skill and require dedicated orchestration.

## Step 2: Load Mock Registry

Check for available canonical fakes:

**Go**: Use Glob with pattern `pkg/testutil/fakes/*.go`. If the directory does
not exist (common during early epics like N00), note that no fakes are available
and proceed — scaffolding and infrastructure tests may not need boundary mocks.

**Dart/Flutter**: Check `flutter_app/test/fakes/` for shared fakes. If the
project uses mockito `@GenerateMocks`, note the generated mock paths instead.

**Python**: Python tests typically use `tmp_path` fixtures and inline fakes.
No shared registry is expected for Python tooling tests.

These are the ONLY fakes you may use for system boundary mocks. If a test
requires a fake that does not exist in the registry, note it in the summary
report and use a minimal inline stub with a `// TODO: generate via
@test-mock-registry` comment.

Also check `pkg/testutil/` for test helpers (e.g., `testutil.NewTestDB`,
`testutil.TempDir`).

## Step 3: Determine Test File Placement

### Go
Co-locate with source. Test file goes in the same package as the code
being tested, using `_test.go` suffix:

| Source | Test File |
|--------|-----------|
| `internal/core/service/config.go` | `internal/core/service/config_test.go` |
| `internal/adapter/db/sqlite.go` | `internal/adapter/db/sqlite_test.go` |
| `cmd/bff/main.go` | `cmd/bff/main_test.go` |

For tests that validate project structure (scaffolding), place in the
repo root (e.g., `gomod_test.go`, `layout_test.go`).

### Flutter/Dart
Mirror source structure under `flutter_app/test/`:

| Source | Test File |
|--------|-----------|
| `flutter_app/lib/features/board/board_provider.dart` | `flutter_app/test/features/board/board_provider_test.dart` |
| `flutter_app/lib/core/api/grpc_client.dart` | `flutter_app/test/core/api/grpc_client_test.dart` |

### Python
Place in `tests/` mirroring `scripts/` structure:

| Source | Test File |
|--------|-----------|
| `scripts/sweep/analyzer.py` | `tests/sweep/test_analyzer.py` |
| `scripts/acm/graph.py` | `tests/acm/test_graph.py` |

## Step 4: Write Tests Per Feature (Ousterhout Bundling)

Write ALL tests for a feature in one pass — not one test at a time.
Read all FUNC, SMOKE, and REG entries for the feature, then write all
test files before running them.

**Complexity**: All functions in test files must have CC <= 5 per project
rules. If test setup is complex, extract helpers with descriptive names.

### 4a: Functional Tests (FUNC)

Functional tests verify acceptance criteria through public interfaces.

**Chicago-school rules:**
- Call the public API / function / command — never reach into internals
- Use real collaborators within the module boundary
- Mock only at system boundaries (DB, network, clock, filesystem)
- Import fakes from `pkg/testutil/fakes/` — never create ad-hoc mocks
- Assert on observable behavior (return values, side effects, state) —
  never assert on implementation details (method call counts, internal state)

**Test naming**: The test function name MUST include the STD test ID and name.

#### Go Functional Test Pattern

```go
// File: internal/core/service/config_test.go

package service_test

import (
    "context"
    "testing"

    "github.com/jb-612/axon-neo/internal/core/service"
    "github.com/jb-612/axon-neo/pkg/testutil"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

// FUNC-N01-F03-001: config_loads_from_yaml
func TestFUNC_N01_F03_001_ConfigLoadsFromYAML(t *testing.T) {
    // Arrange — real collaborators, fake only at filesystem boundary
    dir := testutil.TempDir(t)
    testutil.WriteFile(t, dir, "config.yaml", `
agent:
  name: "shiran"
  tier: "agentic"
`)

    // Act — call through public API
    cfg, err := service.LoadConfig(dir)

    // Assert — observable behavior only
    require.NoError(t, err)
    assert.Equal(t, "shiran", cfg.Agent.Name)
    assert.Equal(t, "agentic", cfg.Agent.Tier)
}
```

#### Go Table-Driven Functional Test Pattern

Use table-driven tests when multiple FUNC tests exercise the same public API:

```go
// FUNC-N01-F01-001 through FUNC-N01-F01-003: db_port_crud_operations
func TestFUNC_N01_F01_DBPortCRUD(t *testing.T) {
    db := testutil.NewTestDB(t) // real SQLite :memory:
    repo := adapter.NewSQLiteRepo(db)

    tests := []struct {
        id     string // STD test ID
        name   string
        act    func(t *testing.T) (any, error)
        assert func(t *testing.T, got any, err error)
    }{
        {
            id:   "FUNC-N01-F01-001",
            name: "create_agent_stores_record",
            act: func(t *testing.T) (any, error) {
                return repo.CreateAgent(context.Background(), domain.Agent{
                    Name: "shiran", Tier: "agentic",
                })
            },
            assert: func(t *testing.T, got any, err error) {
                require.NoError(t, err)
                agent := got.(domain.Agent)
                assert.Equal(t, "shiran", agent.Name)
            },
        },
    }

    for _, tt := range tests {
        t.Run(tt.id+"_"+tt.name, func(t *testing.T) {
            got, err := tt.act(t)
            tt.assert(t, got, err)
        })
    }
}
```

#### Flutter/Dart Functional Test Pattern

```dart
// File: flutter_app/test/features/board/board_provider_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:axon_neo/features/board/board_provider.dart';
import 'package:axon_neo/core/models/board_item.dart';

// Import from shared fakes directory (or use mockito @GenerateMocks)
import '../../fakes/fake_grpc_client.dart';

void main() {
  group('FUNC-N02-F04: board_provider', () {
    late ProviderContainer container;
    late FakeGrpcClient fakeClient;

    setUp(() {
      fakeClient = FakeGrpcClient();
      container = ProviderContainer(
        overrides: [grpcClientProvider.overrideWithValue(fakeClient)],
      );
    });

    tearDown(() => container.dispose());

    // FUNC-N02-F04-001: board_loads_items_from_server
    test('FUNC-N02-F04-001: board_loads_items_from_server', () async {
      fakeClient.setBoardItems([
        BoardItem(id: '1', title: 'Task A', status: 'open'),
      ]);

      final items = await container.read(boardItemsProvider.future);

      expect(items, hasLength(1));
      expect(items.first.title, equals('Task A'));
    });
  });
}
```

#### Python Functional Test Pattern

```python
# File: tests/sweep/test_analyzer.py

import pytest
from pathlib import Path
from scripts.sweep.analyzer import SweepAnalyzer


class TestFUNC_SweepAnalyzer:
    """FUNC tests for sweep analyzer — from STD traceability.yaml."""

    # FUNC-N05-F01-001: analyzer_parses_sweep_output
    def test_FUNC_N05_F01_001_analyzer_parses_sweep_output(self, tmp_path: Path):
        """Verify analyzer correctly parses sweep JSON output."""
        sweep_file = tmp_path / "sweep.json"
        sweep_file.write_text('{"calls": [{"fn": "main", "duration_ms": 42}]}')

        analyzer = SweepAnalyzer()
        result = analyzer.parse(sweep_file)

        assert len(result.calls) == 1
        assert result.calls[0].fn == "main"
        assert result.calls[0].duration_ms == 42
```

### 4b: Smoke Tests (SMOKE)

Smoke tests are minimal binary pass/fail checks. They verify "does it work
at all?" with no edge cases and no error paths.

**Constraints:**
- Total smoke suite for the entire epic MUST complete in < 30 seconds
- Each smoke test should take < 10 seconds
- Binary pass/fail — no partial success
- No setup beyond what's absolutely required

#### Go Smoke Test Pattern

```go
// File: smoke_test.go (repo root for scaffolding)

package axonneo_test

import (
    "os/exec"
    "testing"
)

// SMOKE-N00-F01-001: go_build_succeeds
func TestSMOKE_N00_F01_001_GoBuildSucceeds(t *testing.T) {
    if testing.Short() {
        t.Skip("smoke tests skipped with -short")
    }
    cmd := exec.Command("go", "build", "./...")
    out, err := cmd.CombinedOutput()
    if err != nil {
        t.Fatalf("go build failed: %s\n%s", err, out)
    }
}
```

#### Flutter/Dart Smoke Test Pattern

```dart
// File: flutter_app/test/smoke_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:axon_neo/main.dart';

void main() {
  // SMOKE-N00-F03-001: flutter_test_passes
  testWidgets('SMOKE-N00-F03-001: app_widget_renders', (tester) async {
    await tester.pumpWidget(const MyApp());
    expect(find.byType(MyApp), findsOneWidget);
  });
}
```

#### Python Smoke Test Pattern

```python
# File: tests/test_smoke.py

class TestSMOKE:
    """Smoke tests — binary pass/fail, < 30s total."""

    # SMOKE-N00-F04-001: workflow_yaml_parseable
    def test_SMOKE_N00_F04_001_workflow_yaml_parseable(self):
        """All workflow YAML files parse without errors."""
        import yaml
        from pathlib import Path

        for wf in Path(".github/workflows").glob("*.yml"):
            with open(wf) as f:
                yaml.safe_load(f)  # Raises on parse error
```

### 4c: Regression Tests (REG)

Regression tests protect against identified risks from design.md risk tables.
Each MUST reference `risk_ref` and `trigger` from the traceability entry.

**Requirements:**
- Include `risk_ref` as a comment or docstring in the test
- Include `trigger` condition as a comment
- Test the specific failure mode the risk describes

#### Go Regression Test Pattern

```go
// File: regression_test.go

package axonneo_test

import (
    "os/exec"
    "testing"
)

// REG-N00-F01-001: go_mod_tidy_no_diff
// Risk: Dependency drift from manual go.mod edits
// Trigger: After dependency changes
func TestREG_N00_F01_001_GoModTidyNoDiff(t *testing.T) {
    cmd := exec.Command("go", "mod", "tidy")
    out, err := cmd.CombinedOutput()
    if err != nil {
        t.Fatalf("go mod tidy failed: %s\n%s", err, out)
    }

    diff := exec.Command("git", "diff", "--exit-code", "go.mod", "go.sum")
    if diffOut, diffErr := diff.CombinedOutput(); diffErr != nil {
        t.Fatalf("go mod tidy produced changes:\n%s", diffOut)
    }
}
```

#### Flutter/Dart Regression Test Pattern

```dart
// File: flutter_app/test/regression/pubspec_lock_test.dart

import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // REG-N00-F03-001: pubspec_lock_consistent
  // Risk: Dependency resolution drift
  // Trigger: After pubspec.yaml edits
  test('REG-N00-F03-001: pubspec_lock_consistent', () {
    final result = Process.runSync('flutter', ['pub', 'get'],
        workingDirectory: 'flutter_app');
    expect(result.exitCode, equals(0));

    final diff = Process.runSync('git', ['diff', '--exit-code', 'pubspec.lock'],
        workingDirectory: 'flutter_app');
    expect(diff.exitCode, equals(0),
        reason: 'flutter pub get should not change pubspec.lock');
  });
}
```

## Step 5: Run Tests (Expect Failures)

After writing all test files for a feature, run the appropriate test command:

```bash
# Go — run only the new test files
go test -v -run "TestFUNC_|TestSMOKE_|TestREG_" ./...

# Flutter
cd flutter_app && flutter test

# Python
pytest tests/ -v -k "FUNC or SMOKE or REG"
```

Tests SHOULD fail at this stage — they are written before implementation.
Record the failure output. If a test passes unexpectedly, verify it is
actually testing the right thing (it may be a vacuous assertion).

## Step 6: Update traceability.yaml

For each test written, update the epic-level traceability.yaml entry:

1. Set `status: implemented` (was `designed`)
2. Set `test_path` to the relative path of the test file

Example diff:

```yaml
# Before
- id: "FUNC-N00-F01-001"
  name: "go_mod_has_correct_module_path"
  test_path: null
  status: designed

# After
- id: "FUNC-N00-F01-001"
  name: "go_mod_has_correct_module_path"
  test_path: "gomod_test.go"
  status: implemented
```

Do NOT set `status: passing` — that happens after implementation makes
the tests pass (done by `@tdd-go`, `@tdd-flutter`, or manual implementation).

## Step 7: Report Summary

Print a summary table after all tests are written:

```
Test Implementation Summary: {epic-id} [{feature-id if filtered}]
================================================================
Feature        FUNC  SMOKE  REG   Total   Status
------------------------------------------------------
F01 go-module     7      1    2      10   implemented
F02 protobuf      6      1    2       9   implemented
------------------------------------------------------
Total            13      2    4      19

Test files written:
  - gomod_test.go (FUNC-N00-F01-001..002)
  - layout_test.go (FUNC-N00-F01-003)
  - ...

Fakes imported from registry:
  - pkg/testutil/fakes/fake_db.go
  - (none needed for N00 — scaffolding only)

Missing fakes (need @test-mock-registry):
  - (none)

Test run results:
  - 19 tests written, 19 failing (expected — no implementation yet)
  - 0 tests unexpectedly passing

Traceability updated:
  - 19 entries: designed -> implemented
  - 19 test_path fields filled
```

# Chicago School Rules (Summary)

These rules apply to ALL tests written by this skill:

1. **Test through public interfaces** — call the function, API, or command
   that users/callers would use. Never reach into unexported fields.

2. **Use real collaborators** — within a module boundary, use actual
   implementations. If `ServiceA` depends on `ServiceB` in the same module,
   use the real `ServiceB`.

3. **Mock only at system boundaries** — database, network, clock, filesystem,
   external APIs. These are the only places where fakes are acceptable.

4. **Import fakes from the shared registry** — Go: `pkg/testutil/fakes/`,
   Dart: `flutter_app/test/fakes/` (or mockito `@GenerateMocks`),
   Python: inline `tmp_path` fixtures (no shared registry).
   Never create ad-hoc mocks in test files.

5. **Assert on behavior, not implementation** — verify what the code does
   (return values, side effects, observable state changes), not how it does
   it (which methods were called, in what order, how many times).

6. **No test interdependence** — each test must be independently runnable.
   Use `t.Cleanup()` (Go), `tearDown` (Dart), or `tmp_path` (Python).

# Test Naming Convention

Every test function MUST include the STD test ID for traceability:

| Language | Pattern | Example |
|----------|---------|---------|
| Go | `TestFUNC_N00_F01_001_DescriptiveName` | `TestFUNC_N00_F01_001_GoModHasCorrectModulePath` |
| Go | `TestSMOKE_N00_F01_001_DescriptiveName` | `TestSMOKE_N00_F01_001_GoBuildSucceeds` |
| Go | `TestREG_N00_F01_001_DescriptiveName` | `TestREG_N00_F01_001_GoModTidyNoDiff` |
| Dart | `'FUNC-N02-F04-001: descriptive_name'` | `test('FUNC-N02-F04-001: board_loads_items')` |
| Python | `test_FUNC_N05_F01_001_descriptive_name` | `def test_FUNC_N05_F01_001_analyzer_parses()` |

# Cross-Feature Tests

Cross-feature tests (IDs like `FUNC-N00-X01`) span multiple features. Place
them in a dedicated file:

| Language | File |
|----------|------|
| Go | `cross_feature_test.go` (repo root) |
| Dart | `flutter_app/test/cross_feature_test.dart` |
| Python | `tests/test_cross_feature.py` |

# Output Files

| Artifact | Location | Updated By |
|----------|----------|------------|
| Test files | Co-located (Go), `flutter_app/test/` (Dart), `tests/` (Python) | This skill creates |
| `traceability.yaml` | `.workitems/{epic}/traceability.yaml` | This skill updates `status` and `test_path` |

This skill does NOT modify STD.md — that is owned by `@test-design`.

# Cross-References

- `@test-design` — produces the STD.md and traceability.yaml this skill consumes
- `@test-mock-registry` — produces canonical fakes in `pkg/testutil/fakes/`
- `@tdd-go` — micro-cycle unit TDD for Go (complementary, not overlapping)
- `@tdd-flutter` — micro-cycle unit TDD for Flutter (complementary)
- `@tdd-workflow` — language-agnostic TDD engine
- `@integration-test` — cross-boundary integration tests
- `@testing` — runs quality gates after tests are implemented
- `@acm-traceability` — queries coverage gaps post-implementation
- `@verification-loop` — validates all STD tests pass before feature completion

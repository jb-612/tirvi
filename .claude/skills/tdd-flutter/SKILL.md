---
name: tdd-flutter
description: Flutter/Dart TDD micro-cycle engine. Widget tests, Riverpod provider tests, golden tests, 3-agent separation, traceability updates.
argument-hint: "[phase/feature-id/task-id]"
---

Execute Flutter TDD build for task $ARGUMENTS.
Use `--accept-all` to skip mode selection prompt.

## Prerequisites

1. Read `.workitems/{feature}/design.md` — confirm design elements exist
2. Read `.workitems/{feature}/tasks.md` — find target task; confirm
   unchecked by checking that the line `- [ ] **T-NN done**`
   immediately under the `## T-NN: <title>` header is `[ ]`, not `[x]`
   (per `.claude/rules/task-format.md`)
3. Read `.workitems/{feature}/traceability.yaml` — will update after tests pass
4. Verify: `cd flutter_app && flutter --version`

If design missing: "Run /design-pipeline first."

## Step 0: Evaluate Task — Mode Selection

Evaluate the task against the decision table and recommend a mode:

| Criterion | Bundled | Strict |
|-----------|---------|--------|
| Interface pre-designed in design.md | YES | |
| Provider/Bloc with known state transitions | YES | |
| Widget with defined props/callbacks | YES | |
| Solution shape unknown or TBD | | YES |
| Complex async stream composition | | YES |
| Novel animation or gesture handling | | YES |

Unless `--accept-all` is set, prompt the user:
"For task {id} ({description}), I recommend **{BUNDLED|STRICT}** mode
because {reason}. Approve or change?"

## Core Principles

1. No production `lib/` code unless making a failing `test/` pass
2. Write tests before implementation (all per task in bundled, one at a time in strict)
3. No more production code than sufficient to pass

## Agent Separation (Flutter)

| Agent | Phase | Can Edit | Cannot Edit |
|-------|-------|----------|-------------|
| `tdd-flutter-test-writer` | RED | `flutter_app/test/**` | `flutter_app/lib/**` |
| `tdd-flutter-code-writer` | GREEN | `flutter_app/lib/**` | `flutter_app/test/**` |
| `tdd-flutter-refactorer` | REFACTOR | both | no new behavior |

Marker: `echo "test-writer" > /tmp/ba-tdd-markers/{hash}`
Hook: `enforce-tdd-separation.sh` checks `flutter_app/test/` vs `flutter_app/lib/`.

## Test Patterns

### Widget test (with Riverpod overrides)
```dart
testWidgets('HomeScreen displays welcome message', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        boardRepoProvider.overrideWithValue(MockBoardRepo()),
      ],
      child: const MaterialApp(home: HomeScreen()),
    ),
  );
  expect(find.text('Welcome'), findsOneWidget);
});
```

### Provider test (with dispose)
```dart
test('boardProvider fetches board data', () async {
  final container = ProviderContainer(overrides: [
    boardRepoProvider.overrideWithValue(MockBoardRepo()),
  ]);
  addTearDown(container.dispose);

  final board = await container.read(boardProvider.future);
  expect(board.items, isNotEmpty);
});
```

### Unit test
```dart
test('DateFormatter formats ISO to readable', () {
  expect(formatDate('2026-04-04T10:00:00Z'), equals('Apr 4, 2026'));
});
```

### Golden test (pixel-perfect validation)
```dart
testWidgets('BoardCard matches golden', (tester) async {
  await tester.pumpWidget(/* ... */);
  await expectLater(
    find.byType(BoardCard),
    matchesGoldenFile('goldens/board_card.png'),
  );
});
// Update: flutter test --update-goldens
```

### gRPC client mock (mockito)
```dart
@GenerateMocks([BoardServiceClient])
void main() {
  late MockBoardServiceClient mockClient;
  setUp(() { mockClient = MockBoardServiceClient(); });

  test('fetches board via gRPC', () async {
    when(mockClient.getBoard(any)).thenAnswer(
      (_) async => GetBoardResponse(/* ... */),
    );
    final repo = BoardRepository(mockClient);
    final result = await repo.getBoard();
    expect(result, isNotNull);
  });
}
```

## RED Phase (tdd-flutter-test-writer)

### Bundled Mode (default)
1. Read task from tasks.md — note `design_element` and `test file`
2. Write ALL tests for the task in the specified test file(s)
3. Run: `cd flutter_app && flutter test test/path/to_test.dart`
4. Verify ALL fail (RED)
5. Report: test files, descriptions, failure count
6. Hand off ALL failing tests to code-writer

### Strict Mode
1. Read task from tasks.md — note `design_element` and `test file`
2. Write ONE test in the specified test file
3. Run: `cd flutter_app && flutter test test/path/to_test.dart`
4. Verify FAILS (RED)
5. Report: test file, description, failure

## GREEN Phase (tdd-flutter-code-writer)

### Bundled Mode (default)
1. Read ALL failing tests for the task
2. Write Dart code in `lib/` to pass ALL tests — minimum necessary
3. Run: `cd flutter_app && flutter test test/path/to_test.dart`
4. Verify ALL pass (GREEN)
5. Run: `cd flutter_app && flutter analyze --no-fatal-infos`
6. If any test needed a signature change: hand back to test-writer for
   a **test revision pass** before proceeding to REFACTOR
7. Report: files modified, tests PASS

### Strict Mode
1. Read failing test
2. Write MINIMUM Dart code in `lib/` to pass
3. Run: `cd flutter_app && flutter test test/path/to_test.dart`
4. Verify PASSES (GREEN)
5. Run: `cd flutter_app && flutter analyze --no-fatal-infos`
6. Report: files modified, test PASS

### Strict Mode: Repeat RED-GREEN until all task behaviors covered.

## REFACTOR Phase (tdd-flutter-refactorer)

1. Run: `cd flutter_app && flutter test` — all GREEN
2. Run: `cd flutter_app && flutter analyze` — zero issues (full strict)
3. Apply ONE refactoring at a time
4. After EACH: `flutter test` + `flutter analyze`
5. Run: `cd flutter_app && dart format --set-exit-if-changed lib/ test/`

**HITL Gate: Refactor Approval (advisory)**

## Task Completion

1. Flip the standard done marker `- [ ] **T-NN done**` →
   `- [x] **T-NN done**` in `tasks.md` (per
   `.claude/rules/task-format.md`)
2. Update traceability.yaml: add `VERIFIED_BY` edge (task → test)
3. Run: `cd flutter_app && flutter test --coverage`
4. Check: `lcov --summary coverage/lcov.info` — fail if < 80%
5. Proceed to next task

## Failure Escalation

Same test fails 3+ times in GREEN → HITL:
A) Retry  B) Skip + issue  C) Abort  D) Invoke debugger agent

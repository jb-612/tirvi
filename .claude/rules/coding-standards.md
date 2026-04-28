---
paths:
  - "cmd/**/*.go"
  - "pkg/**/*.go"
  - "internal/**/*.go"
  - "flutter_app/lib/**/*.dart"
  - "scripts/**/*.py"
  - "proto/**/*.proto"
---

# Coding Standards for Axon Neo

## Go Standards

### Style
1. `gofmt` is non-negotiable — all Go code must be formatted
2. Use `golangci-lint` with project config (`.golangci.yml`)
3. Import order: stdlib → third-party → internal (enforced by goimports)
4. Exported functions get doc comments; unexported can skip if self-evident
5. Errors are values — return `error`, don't panic. Wrap with `fmt.Errorf("context: %w", err)`
6. Use struct literals with field names: `Config{Port: 8080}`, not `Config{8080}`

### Concurrency
7. Goroutines must have clear ownership and shutdown path (use `context.Context`)
8. Channels over mutexes when modeling communication between goroutines
9. Never launch a goroutine without a way to stop it (context cancellation or done channel)
10. Use `errgroup` for concurrent operations that need error propagation

### Architecture
11. `cmd/` packages: only `main()` + flag parsing + dependency wiring
12. `pkg/core/`: shared interfaces and domain types — no external service dependencies
13. `internal/`: implementation details not exported to other modules
14. Interfaces at consumer side (accept interfaces, return structs)
15. Repository pattern for all database access — no raw SQL in handlers

### Testing
16. Table-driven tests with `t.Run()` subtests
17. Use `testify/assert` or stdlib — be consistent within a package
18. Mocks via interfaces, not monkey-patching
19. `_test.go` files colocated with source

## Dart/Flutter Standards

### Style
20. `dart format` is non-negotiable — all Dart code must be formatted
21. `flutter analyze` must pass with zero issues
22. Follow Effective Dart conventions (naming, documentation, usage, design)
23. Use `const` constructors wherever possible for widget performance
24. Prefer composition over inheritance for widgets

### State Management
25. Riverpod or Bloc — one pattern per project, do not mix
26. Business logic in providers/blocs, not in widgets
27. Widgets are pure UI — no API calls, no database access
28. Use `AsyncValue` (Riverpod) or state classes (Bloc) for loading/error/data

### Architecture
29. Feature-first folder structure: `lib/features/<name>/` *(N05 exemption: the imported Axon-workspace Flutter app retains its source flat `lib/{pages,data,shell,components,theme}` layout pending post-N08 consolidation — see ADR-014. The pre-existing axon-neo F03 scaffold contained only `.gitkeep` placeholders, so the exemption clobbers nothing real.)*
30. Each feature: `data/` (repositories, models), `domain/` (entities, use cases), `presentation/` (widgets, providers) *(N05 exemption applies)*
31. gRPC client code is generated — never hand-write protobuf serialization
32. Local cache via Drift (SQLite) for offline support

### Testing
33. Widget tests with `testWidgets()` for UI behavior
34. Unit tests for providers/blocs/use cases
35. Golden tests for pixel-perfect verification of key screens
36. Integration tests for critical user flows

## Python Standards (Tooling Only)

Python is used for dev tooling, not the product app. Keep it simple.

### Style
37. ruff for lint + format (line-length=100)
38. Type hints on all function signatures
39. f-strings for formatting
40. `Path` objects over string paths

### Patterns
41. Use `async def` for I/O-bound functions in daemon scripts
42. `yaml.safe_load()` only, never `yaml.load()`
43. Parameterized queries (`?` placeholders), never string formatting for SQL
44. Array form for subprocess (`["cmd", "arg"]`), never `shell=True`
45. Always set timeout on subprocess and async operations

## Protobuf Standards

46. One service per `.proto` file, matching the Go package name
47. Use `buf lint` — enforces naming, package structure, field numbering
48. `buf breaking` in CI — no backwards-incompatible changes without versioning.
    The `FILE` ruleset (strictest) rejects field deletion even with `reserved`
    clauses — only `WIRE` / `WIRE_JSON` treat `reserved` as equivalent to
    presence. When evolving a single-field stub response into a typed shape,
    preserve the original field under its original field number as a
    doc-commented `buf-compat keep-alive`; do not delete it or switch numbers.
    Add typed fields alongside using new field numbers.
49. Field names: `snake_case`. Message names: `PascalCase`. Enum values: `UPPER_SNAKE_CASE`
50. Every message field gets a comment if its purpose isn't obvious from the name

## Cross-Language Rules

51. Cyclomatic complexity: CC <= 5 per function (all languages)
52. No secrets in code — environment variables or secret manager only
53. All public APIs documented (Go doc comments, Dart doc comments, Python docstrings)
54. Tests before implementation (TDD) for all production code

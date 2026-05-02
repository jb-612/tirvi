---
# Universal coding standards. Per-language sections are TEMPLATES — they
# apply only to languages the hosting project has actually enabled in its
# CLAUDE.md or settings. The harness must not assume a project uses a
# given language; assumptions cause stack-mismatch design errors (see
# docs/research/sdlc-shortcut-postmortem-phase0.md §lesson 5).
---

# Coding Standards

This file is **language-agnostic**. The Universal Rules apply to every
project that loads the harness. The per-language sections below are
templates the agent reads ONLY when the hosting project's CLAUDE.md
declares the corresponding language as in use. The harness itself
makes no assumption about which languages a given project uses.

## Universal Rules (apply to all projects, all languages)

1. **Cyclomatic complexity ≤ 5** per function. Refactor when growing.
   The `check-complexity.sh` hook enforces > 7 as a hard block; 6-7 is
   a soft block (must refactor before commit).
2. **Tests before implementation (TDD)** for all production code. See
   `.claude/rules/tdd-rules.md`.
3. **No secrets in code** — environment variables or secret manager
   only. The `block-dangerous-commands.sh` hook screens commits.
4. **All public APIs documented** — language-appropriate doc comments
   (Go doc comments, JSDoc/TSDoc, Python docstrings, Dart doc comments,
   etc.).
5. **Format-on-save is non-negotiable** — every project enables a
   formatter for every language it ships. The agent must not commit
   un-formatted code.
6. **No untyped public surfaces** — every public function or method
   has type annotations / signatures. Strict-mode tooling encouraged.
7. **Pure-function preference** — push side-effects to the boundary
   (adapters, IO, mutation), keep core logic deterministic and
   testable.

## Project-language declaration (read this before per-language rules)

The hosting project declares its languages and code paths via:

- The frontmatter / "Project Conventions" section of its `CLAUDE.md`.
- A per-project `coding-standards-overlay.md` if the project wants
  to override or extend universal rules.
- The actual repo layout (which the agent inspects via `ls` /
  `Glob` before authoring per-language artifacts).

**The agent MUST inspect the project's actual repo before quoting any
per-language rule from this file.** Pattern-matching from the harness
to a presumed language has caused real design errors; see the
postmortem for the F39 case study.

## Per-language sections (templates — apply only when project enables)

### Go (when the project ships Go code)

#### Style
- `gofmt` is non-negotiable — all Go code must be formatted.
- Use `golangci-lint` with project config (`.golangci.yml`).
- Import order: stdlib → third-party → internal (enforced by goimports).
- Exported functions get doc comments; unexported can skip if
  self-evident.
- Errors are values — return `error`, don't panic. Wrap with
  `fmt.Errorf("context: %w", err)`.
- Use struct literals with field names: `Config{Port: 8080}`, not
  `Config{8080}`.

#### Concurrency
- Goroutines must have clear ownership and shutdown path
  (use `context.Context`).
- Channels over mutexes when modeling communication between
  goroutines.
- Never launch a goroutine without a way to stop it (context
  cancellation or done channel).
- Use `errgroup` for concurrent operations that need error propagation.

#### Architecture
- `cmd/` packages: only `main()` + flag parsing + dependency wiring.
- `pkg/core/`: shared interfaces and domain types — no external
  service dependencies.
- `internal/`: implementation details not exported to other modules.
- Interfaces at consumer side (accept interfaces, return structs).
- Repository pattern for all database access — no raw SQL in
  handlers.

#### Testing
- Table-driven tests with `t.Run()` subtests.
- Use `testify/assert` or stdlib — be consistent within a package.
- Mocks via interfaces, not monkey-patching.
- `_test.go` files colocated with source.

### Dart / Flutter (when the project ships a Flutter app)

#### Style
- `dart format` is non-negotiable — all Dart code must be formatted.
- `flutter analyze` must pass with zero issues.
- Follow Effective Dart conventions (naming, documentation, usage,
  design).
- Use `const` constructors wherever possible for widget performance.
- Prefer composition over inheritance for widgets.

#### State Management
- Riverpod or Bloc — one pattern per project, do not mix.
- Business logic in providers/blocs, not in widgets.
- Widgets are pure UI — no API calls, no database access.
- Use `AsyncValue` (Riverpod) or state classes (Bloc) for
  loading/error/data.

#### Architecture
- Feature-first folder structure: `lib/features/<name>/`. Project may
  declare layout exemptions in its CLAUDE.md (e.g., a project that
  imports an upstream Flutter app with a flat layout).
- Each feature: `data/` (repositories, models), `domain/` (entities,
  use cases), `presentation/` (widgets, providers).
- gRPC client code is generated — never hand-write protobuf
  serialization.
- Local cache via Drift (SQLite) for offline support, when offline
  is in scope.

#### Testing
- Widget tests with `testWidgets()` for UI behavior.
- Unit tests for providers/blocs/use cases.
- Golden tests for pixel-perfect verification of key screens.
- Integration tests for critical user flows.

### Python (when the project ships Python code)

#### Style
- `ruff` for lint + format (line-length per project config).
- Type hints on all function signatures.
- f-strings for formatting.
- `Path` objects over string paths.

#### Patterns
- Use `async def` for I/O-bound functions in daemon scripts.
- `yaml.safe_load()` only, never `yaml.load()`.
- Parameterized queries (`?` placeholders), never string formatting
  for SQL.
- Array form for subprocess (`["cmd", "arg"]`), never `shell=True`.
- Always set timeout on subprocess and async operations.

### TypeScript / JavaScript (when the project ships browser or Node code)

#### Style
- A formatter (Prettier or biome) is non-negotiable; project picks one.
- A type checker (TypeScript strict mode, or `// @ts-check` on JS)
  applies to every public surface.
- ESM modules over CommonJS for new code.
- `const` by default; `let` only when reassignment is needed; `var`
  never.

#### Patterns
- No business logic in event handlers — extract to pure functions and
  unit-test those. Handlers are wiring only.
- DOM access lives at the boundary; core logic must be testable
  without a browser (jsdom, vitest's default test environment).
- No global state mutation — module-scoped state with explicit
  getters/setters.

#### Testing
- vitest (or Jest) for unit + module tests.
- Component / DOM tests via vitest + jsdom or testing-library.
- Avoid e2e for unit-test scope; reserve Playwright for cross-page
  flows.

### Protobuf (when the project ships .proto files)

- One service per `.proto` file.
- Use `buf lint` — enforces naming, package structure, field
  numbering.
- `buf breaking` in CI — no backwards-incompatible changes without
  versioning. The `FILE` ruleset (strictest) rejects field deletion
  even with `reserved` clauses; only `WIRE` / `WIRE_JSON` treat
  `reserved` as equivalent to presence. When evolving a single-field
  stub response into a typed shape, preserve the original field
  under its original field number as a doc-commented `buf-compat
  keep-alive`; do not delete it or switch numbers. Add typed fields
  alongside using new field numbers.
- Field names: `snake_case`. Message names: `PascalCase`. Enum
  values: `UPPER_SNAKE_CASE`.
- Every message field gets a comment if its purpose isn't obvious
  from the name.

## Adding a new language section

1. Read the project's CLAUDE.md to confirm the language is actually
   in use.
2. Append a new `### <Language>` section under "Per-language
   sections", mirroring the existing structure (Style / Patterns /
   Testing as applicable).
3. Cross-reference any project-specific overlay file.
4. **Do NOT add per-language assumptions to the Universal Rules
   section** — that's the path that creates harness-meta drift.

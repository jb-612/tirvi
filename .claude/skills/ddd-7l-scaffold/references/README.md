# Per-language reference shapes for ddd-7l-scaffold

`SKILL.md` is language-agnostic. It uses **TypeScript as the canonical
illustration** because TS has the cleanest DDD-shape syntax for skill
documentation (interfaces, discriminated unions, classes with
`private constructor`).

For each project that uses this skill, the agent inspects the repository
language at runtime and reads the matching reference file from this folder
to learn the concrete code shapes.

## Convention

One file per language: `<language>.md`.

Each file mirrors the 7L workflow with per-layer code examples in idiomatic
form for that language. Sections in order:

1. Folder layout (L1)
2. Contract shapes (L2) — interfaces, ports, command/query/result types, error types
3. Domain shapes (L3) — aggregates, entities, value objects, events, policies, factories
4. Test skeleton shapes (L4) — unit + behavioural + contract test files with GWT comments
5. TDD shell shapes (L5) — DI wiring, fakes, in-memory adapters, fixture builders
6. Runtime shapes (L6) — routes, handlers, DI modules, auth/observability stubs
7. Traceability emission (L7) — how the per-language run produces the canonical `bounded_contexts` YAML block

## Languages currently provided

- `python.md` — Pydantic / dataclasses / Protocol ports / pytest / FastAPI
- `go.md` — interfaces / structs / typed errors / table-driven `_test.go` / chi
- `dart.md` — sealed classes / abstract ports / Riverpod / flutter_test / shelf

## Adding a new language

1. Copy any existing reference file as a template
2. Replace the per-layer examples with idiomatic shapes for the target language
3. Match the section order (L1–L7) so the agent can navigate consistently
4. Include both the "scaffold" code (what to write) and the "anti-pattern" code (what NOT to write)
5. Reference the project's actual package/folder conventions if known; otherwise generic conventions

## Notes for tirvi specifically

- Production code lives under `tirvi/` (not `pkg/`/`internal/` despite Go conventions in some repos)
- Tests live under `tests/unit/`, `tests/integration/`, `tests/e2e/`
- Flutter app under `flutter_app/lib/`; Flutter tests under `flutter_app/test/`
- No Go code in tirvi today (despite repo conventions allowing it) — `go.md` exists for portability to other projects

The agent runs L1 inspection first to confirm actual paths before writing.

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

## How the agent picks a reference for the hosting project

**The harness is project-agnostic.** It does NOT know which language(s)
the hosting project uses, and the agent must NOT assume one based on
the references that happen to exist in this folder.

The right inspection order:

1. Read the project's `CLAUDE.md` "Project Conventions" / "Stack"
   section — the project declares its languages and code roots.
2. Run `ls` / `Glob` against the project root to confirm what code
   actually exists. Look for `package.json`, `pyproject.toml`,
   `go.mod`, `pubspec.yaml`, `Cargo.toml`, etc. as language signals.
3. Pick the matching reference file from this folder. If the
   project uses a language not represented here, follow "Adding a
   new language" above.
4. **Do NOT proceed past L1 until you've confirmed the actual code
   roots and test roots from the project's repo.** Pattern-matching
   from "this folder has a `dart.md`" to "this project has a Flutter
   app" has caused real design errors — see
   `docs/research/sdlc-shortcut-postmortem-phase0.md §lesson 5`.

The agent runs L1 inspection first to confirm actual paths before
writing any L2+ artifact.

# N00 — Foundation & DevX

**Window:** week 0 · **Features:** 4 · **Type:** scaffolding

Stand up the dev and deploy substrate before any product code. Single-Docker
compose for local; Cloud Run + Cloud Tasks + GCS Terraform for prod;
adapter ports with in-memory fakes; CI/CD with TDD + complexity + security
gates wired from day 1.

## Features

- **F01-docker-compose** — single-Docker dev environment (web/api/worker/models/fake-gcs-server)
- **F02-cloud-skeleton** — Terraform for Cloud Run + Cloud Tasks + GCS + Secret Manager
- **F03-adapter-ports** — Storage / OCR / TTS / WordTiming / NLP ports + fakes
- **F04-ci-cd-gates** — TDD gate, CC ≤ 5 gate, security scan, formatter, hooks → settings.json

## Exit criteria

- `docker compose up` brings the full stack with model sidecar gated by `--profile models`
- `terraform plan` is green; secrets resolve via Secret Manager
- All 5 ports importable; in-memory fakes pass round-trip tests
- CI rejects a deliberately failing test, a CC > 5 function, and a leaked secret

## Note on the CC ≤ 5 gate

The cyclomatic-complexity gate (`.claude/hooks/check-complexity.sh`)
runs against application code (Python / TypeScript / Go). Phase N00 work
is mostly Dockerfiles, compose YAML, Terraform, and shell — none of
which the CC tooling parses. The gate effectively activates at **F03
(adapter ports)**, where real Python functions land. F01's walking-
skeleton stubs (`api/main.py`, `worker/__main__.py`, `models/main.py`)
each carry one trivial route at CC = 1 — well under the bar.

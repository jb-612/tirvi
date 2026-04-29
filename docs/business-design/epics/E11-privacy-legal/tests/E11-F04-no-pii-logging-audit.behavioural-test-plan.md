# E11-F04 — Logging Audit: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Dev oversights | P08 | accidental log | lint |
| Reviewer audit | P12 | sample misses | scope |
| SRE remediation | P04 | slow | PR template |

## Scenarios
- **BT-203** Dev logs raw text accidentally; CI catches.
- **BT-204** Reviewer finds field; PR fix.
- **BT-205** SRE expands scope after audit.

## Edge / Misuse / Recovery
- Edge: nested object with content; scrubber descends.
- Misuse: dev disables scrubber locally; CI catches.
- Recovery: post-incident, expanded scope.

## Open Questions
- Hash vs drop default.

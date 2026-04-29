# E02-F05 — Question/Answer Numbering: Behavioural Test Plan

## Behavioural Scope
Student navigation behaviour ("read question 4"); dev behaviour around new
numbering schemes.

## Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Navigation by number | P01 | wrong jump | canonical num |
| Coordinator import unusual scheme | P02 | tagging fails | exception list |
| Dev adds rule | P08 | over-fit | bench |

## Scenarios
- **BT-055** Student says "read question 4"; player jumps to canonical block.
- **BT-056** Coordinator uploads exam with `סעיף 4א`; tagger emits "4.1" canonical.
- **BT-057** Dev adds Hebrew Ordinal rule; bench validates precision lift.
- **BT-058** Sub-questions span pages; mostly works; cross-page open as v1.1.

## Edge / Misuse / Recovery
- Edge: numbering with trailing punctuation `4. 5.` — handled.
- Misuse: spoofed answers (a, b, c, d in mid-paragraph); detector ignores.
- Recovery: orphan answer → user feedback path.

## Collaboration Breakdown
- Tagger silently skips non-Hebrew ordinals; bench page added; rule fixed.

## Open Questions
- "4a" vs "4.1" canonical?

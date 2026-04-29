# E00-F04 — CI/CD Quality Gates: Behavioural Test Plan

## Behavioural Scope
Covers dev behaviour when gates fail mid-day, when waivers are abused, and
when the team grows fatigued by gate noise.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Dev rage-applies waiver | P08 Backend Dev | discipline erosion | weekly waiver audit |
| Test author splits long fixture | P10 Test Author | gate triggered on data | path allow-list |
| Security reviewer triages CVEs | P12 Security Reviewer | dwell time | weekly metric |

---

## Behavioural Scenarios

### BT-013: Dev hits TDD gate on Friday afternoon
**Persona:** P08 Backend Dev
**Intent:** ship before weekend
**Human behaviour:** rage-labels `chore:scaffolding`; merges
**System expectation:** waiver audit flags abuse; PR auto-tagged for retro
**Acceptance criteria:** dev's waiver shows in next Monday's audit

### BT-014: New dev unaware of CC ≤ 5 rule
**Persona:** new joiner P08
**Intent:** ship first PR
**Human behaviour:** writes a 60-line function with CC=10
**System expectation:** gate fails with link to CLAUDE.md TDD-rules section
**Acceptance criteria:** dev reads link, refactors, merges

### BT-015: Vuln scan flags transitive CVE during incident
**Persona:** P08 Backend Dev under hotfix pressure
**Intent:** patch a bug, push
**Human behaviour:** sees scan red; opens dep waiver request
**System expectation:** waiver request pings security reviewer; auto-merged on approval
**Escalation path:** if no approval in 30 min, P12 paged

### BT-016: Waiver abuse pattern detected
**Persona:** Team Lead
**Intent:** monthly hygiene
**Human behaviour:** reviews waiver dashboard
**System expectation:** dashboard shows count per dev; outliers visible
**Acceptance criteria:** team retro outcome captured in `docs/`

## Edge Behaviour
- Repository protected by branch rules; force-push disallowed → dev tries
  and is rejected, learns why.
- CI infra outage; dev waits for status; behavioural test ensures status
  page link is in CI failure output.

## Misuse Behaviour
- Dev disables a gate locally and force-pushes; remote rejects.
- Dev pushes 50 commits in a flurry; gates batch-run efficiently.

## Recovery Behaviour
- CVE waiver expires; CI re-fails; dev or security reviewer renews or fixes.
- Pre-commit hook out of sync with CI; nightly job warns.

## Collaboration Breakdown Tests
- Security reviewer on PTO: backup reviewer documented in CODEOWNERS.
- Waiver bot down: gate falls back to manual approval label.

## Open Questions
- Should waivers expire after N days by default or only on per-CVE basis?

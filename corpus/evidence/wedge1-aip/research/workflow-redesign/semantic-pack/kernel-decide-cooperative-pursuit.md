# Kernel — Decide Cooperative Pursuit

Status: APPROVED (Owen, 2026-08-23)
Kernel version: 0.1 (pinned at approval)
Callers: `Assess Named-Action Readiness`; `Decide Cooperative Pursuit` Action (fresh-state revalidation). Shared conventions: `README.md`.

## Decision

Persist one bounded cooperative pursue / defer / refuse decision for a member–Programme route, without changing public or capacity truth.

## Inputs

- authenticated principal;
- Cooperative Pursuit reference, or creation parameters: member Party, cooperative Party, Programme, Holding + bounded Parcel scope, optional Intervention, mandate Instrument reference;
- outcome: pursue | defer | refuse;
- reason;
- consequential time.

## Ordered prerequisites

| # | Predicate | Fact source | Authority resolution | M/S/C | Cure owner |
|---|---|---|---|---|---|
| 1 | The principal holds current collective-pursuit authority | contextual assignment (governance basis) at consequential time | cooperative governance instrument | M→NR; S→IND; C→IND | cooperative governance |
| 2 | Received member choice covers this route and scope | member-choice occurrence | the member | M→NR; S→IND | member via cooperative/CAA channel |
| 3 | An accepted mandate in force covers the scope | mandate acceptance occurrence + instrument term | mandate kernel outputs; instrument version | M→NR; S→IND; C→IND | run mandate acceptance first |
| 4 | The Programme route is valid: Programme exists, basis Instrument operative, window state known | Programme + Governing Instrument + window/clock facts | instrument effective dates; published window acts | M→NR; S→IND; C→IND | legal-corpus steward / programme authority watch |
| 5 | Bounded scope is determinate: Holding and Parcel set resolve to existing records | Holding, Parcel identity | qualified identity keys | M→NR; C→IND | identity/data steward |
| 6 | Optional Intervention link is valid if named | Intervention record | — | M→NR | correct the reference |
| 7 | Deadline consequence is known: applicable clocks current at decision time | window/clock facts | published acts | S→IND | source/assurance owner |
| 8 | No conflicting active Pursuit for the same member + Programme + overlapping scope | Pursuit records | — | conflict→NR (resolve or supersede the earlier decision) | manager |
| 9 | Fallback and reconsideration trigger are defined | Pursuit fields (structural) | accepted operating model | M→NR | manager supplies them in the command |
| 10 | No prior decision occurrence for this Pursuit + outcome basis | Pursuit Decision Record (idempotency scan) | — | duplicate→ALREADY_COMMITTED at Action layer | — |

## Non-implications

A pursue decision does not create: public eligibility; ranking or concession; capacity commitment; any filing or release; execution or dispatch authority. Defer and refuse preserve the member's individual fallback and the reconsideration trigger.

## Continuable scope

Other members, other Programmes, other Pursuits, and non-dependent work on the same Holding continue unaffected.

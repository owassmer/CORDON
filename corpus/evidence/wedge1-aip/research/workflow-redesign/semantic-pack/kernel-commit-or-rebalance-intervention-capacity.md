# Kernel — Commit or Rebalance Intervention Capacity

Status: APPROVED (Owen, 2026-08-23)
Kernel version: 0.1 (pinned at approval)
Callers: `Assess Named-Action Readiness`; `Commit or Rebalance Intervention Capacity` Action (fresh-state revalidation inside the staged-write transaction). Shared conventions: `README.md`.

## Decision

Apply one coherent portfolio decision atomically across the complete affected Capacity Commitment set, from one immutable Capacity Portfolio Proposal.

## Inputs

- authenticated principal;
- Capacity Portfolio Proposal ID (sole executable plan reference — no client-supplied edit plan);
- direct-execution idempotency token;
- override reason where policy requires;
- consequential time.

## Ordered prerequisites

| # | Predicate | Fact source | Authority resolution | M/S/C | Cure owner |
|---|---|---|---|---|---|
| 1 | The Proposal exists, is immutable, and is not expired/invalidated | Capacity Portfolio Proposal | proposal expiry/invalidation rule | M or expired→NR | manager re-runs comparison and selects again |
| 2 | The Proposal's premise fingerprint matches current state | server-side recomputation over proposal premises | — | mismatch→NR (determinate: the world changed; decision log D2) | manager re-compares on current state |
| 3 | The complete affected Commitment population loads server-side and matches the Proposal target-set hash | Commitment records + proposal hash | complete-population contract | mismatch→NR; load failure→IND | pipeline/assurance owner |
| 4 | The plan revalidates feasible under versioned optimizer inputs and approved policy | deterministic optimizer, pinned versions | cooperative-approved allocation policy | infeasible→NR; stale inputs→IND | manager (plan) / assurance owner (inputs) |
| 5 | Non-discretionary constraints and fairness safeguards hold | policy kernel checks | approved policy version | violation→NR | manager selects a conforming alternative |
| 6 | Protected Commitments are preserved exactly as the Proposal declares | protected set in Proposal vs current records | protected-commitment meaning (Gate 5) | violation→NR | manager re-compares |
| 7 | The principal holds current allocation/override authority | contextual assignment (governance basis) | cooperative governance | M→NR; S→IND; C→IND | cooperative governance |
| 8 | Override reason present where the selected plan departs from the recommendation and policy requires one | command input | approved policy | M→NR | manager supplies the reason |
| 9 | No concurrent capacity transaction overlaps this Commitment set | in-flight transaction check | — | conflict→NR (retry after completion) | manager retries |
| 10 | The complete edit set is ≤ 10,000 objects | proposal edit plan | platform envelope | exceeds→NR; never chunk silently | escalate decision grain to Owen |
| 11 | Load-bearing capacity/source facts satisfy their assurance contracts | assurance matrix | Contract 1 | S→IND | source/assurance owner |
| 12 | No prior committed transaction for this Proposal + idempotency token | portfolio decision reference scan | — | duplicate→ALREADY_COMMITTED at Action layer | — |

## Non-implications

A committed portfolio does not create or change: public eligibility; concession; legal duty; dispatch authority; payment or creditor facts. It does not delete any member's fallback. A recommendation, Scenario, or Proposal never becomes a commitment without this Action; the highest-scoring plan has no authority of its own.

## Continuable scope

Commitments outside the affected set, all Pursuits, and every non-capacity route continue unaffected. A refused or indeterminate verdict leaves every existing Commitment exactly as it was.

# Kernel — Accept Cooperative Execution Mandate

Status: APPROVED (Owen, 2026-08-23)
Kernel version: 0.1 (pinned at approval)
Callers: `Assess Named-Action Readiness`; `Accept Cooperative Execution Mandate` Action (fresh-state revalidation). Shared conventions: `README.md`.

## Decision

Record the cooperative's acceptance or refusal of a real member-granted execution mandate, activating only the accepted cooperative-side authority.

## Inputs

- authenticated principal;
- mandate Governing Instrument reference and version;
- member Operator Party; cooperative Operator Party;
- outcome: accept | refuse;
- bounded scope: Programme route(s), Holding/Parcel scope, powers claimed;
- consequential time;
- reason where policy requires.

## Ordered prerequisites

| # | Predicate | Fact source | Authority resolution | M/S/C | Cure owner |
|---|---|---|---|---|---|
| 1 | An executed member grant instrument exists and covers the claimed scope, term and powers | Governing Instrument (mandate kind) + Instrument Occurrence | member execution evidenced on the instrument version | M→NR; S→IND; C→IND | member + cooperative (execute or correct the mandate) |
| 2 | Member participation/election for this arrangement is received | received member-choice occurrence (member/beneficiary admission) | the member, through the admitted channel | M→NR; S→IND; C→IND | member via cooperative/CAA channel |
| 3 | The principal holds current cooperative acceptance authority | Instrument Party Assignment (governance basis) effective at consequential time | cooperative governance instrument | M→NR; S→IND; C→IND | cooperative governance |
| 4 | Scope, term, powers, duties, exclusions and price/terms are determinate | mandate instrument fields | instrument text; no inference fills a gap | M→NR; C→IND | member + cooperative (clarify instrument) |
| 5 | No unresolved material conflict of interest for the accepting role | contextual assignments + declared conflicts | cooperative governance rules | C→IND (declared+unresolved→NR) | cooperative governance |
| 6 | Refusal path preserves the member's individual fallback | route model (structural check) | accepted operating model | structural — must always hold | design escalation to Owen if violated |
| 7 | No prior acceptance/refusal occurrence exists for this mandate version | Instrument Occurrence (idempotency scan) | — | duplicate→ALREADY_COMMITTED at Action layer | — |

## Non-implications

Acceptance does not create: the member's grant (it consumes one); public eligibility; concession; capacity commitment; any filing; creditor identity; execution readiness. Refusal does not erase the member's own route or standing.

## Continuable scope

Other mandates, other members, and every route not dependent on this mandate continue unaffected regardless of verdict.

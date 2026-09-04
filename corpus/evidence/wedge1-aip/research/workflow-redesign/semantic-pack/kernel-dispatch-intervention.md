# Kernel — Dispatch Intervention

Status: APPROVED (Owen, 2026-08-23)
Kernel version: 0.1 (pinned at approval)
Callers: `Assess Named-Action Readiness`; `Dispatch Intervention` Action (fresh-state revalidation). Shared conventions: `README.md`.

## Decision

Create the bounded executor handoff for work that is ready now: authorized scope, executor, clocks, stop/return conditions, and optional real work-order Instrument.

## Inputs

- authenticated principal;
- Intervention reference;
- bounded dispatch scope: Parcels; identified Plants only where the extension-gated population exists;
- executor Party;
- dispatch intent/date; stop/return conditions;
- consequential time.

## Ordered prerequisites

| # | Predicate | Fact source | Authority resolution | M/S/C | Cure owner |
|---|---|---|---|---|---|
| 1 | The principal holds current dispatch authority for this route/scope/date | Intervention Party Assignment + basis Instrument | contextual assignment effective at consequential time | M→NR; S→IND; C→IND | cooperative governance / mandate acceptance |
| 2 | Executor assignment and qualification are current | Intervention Party Assignment + professional/contractual facts | qualification register or executed contract | M→NR; S→IND; C→IND | engage or qualify the executor |
| 3 | An operative work basis exists: validated duty, order, concession, approved change, or member-authorized self-funded basis | Instrument/Proceeding Occurrence | the basis act/decision and its effective dates | M→NR; S→IND; C→IND | route owner (authority, member, or manager) |
| 4 | Target and scope are valid: Parcels within the Intervention's scope; exclusions explicit; Plant references only from the gated population | Intervention scope links; Plant identity gate | accepted scope; registry/validated inventory identity | M→NR; ungated Plant ref→NR always | manager corrects scope; identity gate never waived |
| 5 | A certified technical design covers the dispatch scope | design evidence on the Intervention | qualified professional | M→NR; S→IND | technician |
| 6 | Access standing holds for every target Parcel | Parcel Standing (tenure/consent/access) | standing basis instrument | M→NR; S→IND; C→IND | member/owner consent; standing resolution owner |
| 7 | Required permits are operative, including the site-specific VIncA route where the site triggers it | permit Proceeding Occurrences | competent public authority decisions | M→NR; S→IND; C→IND | competent authority (routed, never impersonated) |
| 8 | Execution capacity covers the dispatch window | **Route-conditional:** PugliaOlive-controlled/contracted execution uses Capacity Commitment records; a public/authority executor such as ARIF uses authenticated route-election/assignment plus current executor-feasibility and clock evidence | cooperative committed extent/interval **or** the controlling public basis and received executor route | M→NR; S→IND | run capacity commitment for cooperative-controlled resources, or obtain/refresh the public executor assignment/feasibility evidence |
| 9 | Required materials are evidenced available for the design | supplier/lot availability evidence | contractual/field evidence | M→NR; S→IND | supplier via manager |
| 10 | Lawful water/serviceability holds where the design requires it | water right + serviceability evidence | right holder / provider confirmation | M→NR; S→IND | member/provider via manager |
| 11 | Finance and evidence preconditions hold where a claim route requires them | admissible-spend and evidence-plan facts | award rules | M→NR; C→IND | finance owner |
| 12 | Clocks are compatible: vector windows, burn/fire conditions, deadlines admit the dispatch date | published window acts; daily bulletins | published acts/bulletins current | incompatible→NR; stale bulletin→IND | wait/reschedule; source owner for bulletins |
| 13 | No duplicate open dispatch covers the same scope | Intervention Occurrence scan | — | duplicate→ALREADY_COMMITTED at Action layer | — |

## Non-implications

Dispatch does not create or imply: movement of material; performance; inspection; acceptance; compliance; biological establishment; payment. `READY` is not dispatch — only the explicit manager command executes. A map/shape selection supplies candidate targets only; it never satisfies predicate 4 by itself.

## Continuable scope

Other Interventions, non-dispatched scope within this Intervention, and all funding/payment routes continue unaffected regardless of verdict.

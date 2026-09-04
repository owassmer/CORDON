# Gate 5 operator-centered pruning audit

**Status:** adversarial replacement verdict for every pre-correction Gate 5 software candidate  
**Date:** 22 August 2026  
**Authority:** `REDESIGN_SEQUENCE.md`, `connected-operating-model.md`, `gate-5-operator-reground.md`, and `gate-5-core-ontology.md`  
**Candidate evidence audited:** `gate-5-object-event-admission.md`, `gate-5-exact-relationship-inventory.md`, `gate-5-proceeding-scope-minimum.md`, `gate-5-kinetic-interface-candidates.md`, and `gate-5-integrated-candidate-synthesis.md`

## Verdict

The pre-correction inventory normalized the domain instead of minimizing the cooperative manager's operating model. Of **83 enumerated candidates**—13 nouns, six event types, 39 fixed relationship types, ten recommended Proceeding-scope types, eleven Actions, three Functions, and one Interface—only **13 candidates remain KEEP CORE**. Natural Person and Organization are additionally consolidated into one replacement `Operator Party` object, yielding a practical core of **14 elements**: seven objects, one relationship object, three Actions, and three Functions. **Seventy candidate slots are pruned as independent core elements.**

The practical core is:

1. `Operator Party` — one concrete object with party kind and legal/operational identity; replaces separate Natural Person and Organization software types.
2. `Agricultural Holding`.
3. `Cadastral Parcel`.
4. `Public Programme or Measure`.
5. `Governing Instrument`.
6. `Public Proceeding`.
7. `Intervention`.
8. `Intervention Capacity Commitment`.
9. `Accept the cooperative execution mandate` Action.
10. `Commit or Rebalance Intervention Capacity` Action.
11. `Dispatch Intervention` Action.
12. `Determine Affected Decisions` Function.
13. `Assess Named-Action Readiness` Function.
14. `Compare Feasible Intervention Portfolios` Function.

Everything else is represented as a property, direct link, event detail, derived view, backstage evidence, external outcome, or a selectively reopenable element. No previous acceptance is preserved merely because it was accepted.

### Core deletion failures

| Core element | Exact cooperative-manager failure if deleted |
|---|---|
| `Operator Party` | The manager cannot identify the exact member, beneficiary, representative, cooperative, authority, contractor, or next owner; cannot verify who is authorized to choose or act; and cannot route a cure or handoff without replacing identity with unsafe labels. Person-versus-organization differences remain a `partyKind` and qualified properties, not separate core types. |
| `Agricultural Holding` | The manager cannot evaluate the complete member–farm population or preserve one farm's administrative/operating continuity as actors and Parcels change; opportunity evaluation and member-specific route coordination fragment into person and land records. |
| `Cadastral Parcel` | The manager cannot answer which legally referenced land is affected, required, permitted, accessible, filed, dispatched, executed, or still open; Holding or geometry-only representation merges concurrent land duties and work. |
| `Public Programme or Measure` | The manager cannot evaluate the complete in-scope opportunity population or distinguish concurrent public routes, windows, claim stages, and individual fallback across changing Instruments and Proceedings. |
| `Governing Instrument` | The manager cannot explain the exact basis, authority, effective interval, amendment/stay/supersession, clock, or consequence for a named decision; current values become uncited and selective reopening by changed rule becomes impossible. |
| `Public Proceeding` | The manager cannot preserve one formal matter across filings, repair, authority outcomes, appeal/audit/recovery, and reopening or know which authority owns the next public decision; event fragments collapse into a generic history. |
| `Intervention` | The manager cannot coordinate the same bounded physical undertaking across design, capacity, dispatch, execution, acceptance, claim, aftercare, replacement, and cure; intended work, performed work, cash, and establishment lose their common operator anchor. |
| `Intervention Capacity Commitment` | The authorized cooperative manager cannot atomically reserve, retain, release, or reallocate scarce resource quantities/periods across Interventions or distinguish a recommendation from a real commitment; a property on one Intervention cannot preserve multi-Intervention portfolio coherence. |
| `Accept the cooperative execution mandate` | The cooperative manager cannot exercise or record the cooperative's separate acceptance/refusal of a member-granted mandate; member participation or public eligibility would again be mistaken for cooperative authority. |
| `Commit or Rebalance Intervention Capacity` | The manager can see a recommendation but cannot make the governed cooperative portfolio decision or atomically preserve protected commitments, releases, deferrals, and an override reason. |
| `Dispatch Intervention` | The manager cannot turn named-action readiness into a bounded, attributable field handoff; preparation or schedule data would be mistaken for actual authority to commence work. |
| `Determine Affected Decisions` | Question 1 and selective reopening fail: the manager cannot reliably identify which decisions/actions a material change can alter, why, who owns the next decision, or which work must remain unaffected. |
| `Assess Named-Action Readiness` | Questions 2 and 4 fail: every Action either duplicates cross-object gating or uses an unsafe generic ready state, so blockers, cure owners, and the consequence of proceeding or waiting cannot be explained for the exact Action. |
| `Compare Feasible Intervention Portfolios` | The accepted Option A capacity decision loses complete-population feasibility, binding constraints, alternatives, uncertainty, and expected incremental loss-reduction comparison; allocation reverts to nomination, a static ranking, or opaque judgment. |

**Normalization/internal-record flag:** no retained element is justified only by normalization, source fidelity, platform convenience, or another actor's internal record. `Public Proceeding` is retained for the manager's cross-filing route and next-owner decision, not because an authority maintains a dossier. `Governing Instrument` is retained for operator explanation and selective rule-change impact, not to mirror a legal corpus. All candidates whose only positive case is a supplier, bank, inspector, laboratory, public authority, or source-system record are classified below as event detail, backstage evidence, external outcome, conditional reopening, or rejection.

## Classification rule

- **KEEP CORE** — deletion causes the stated cooperative-manager decision/action failure and no simpler representation preserves it.
- **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** — retain the fact once on one of the seven operator objects, usually as a qualified property/history entry.
- **DIRECT LINK** — endpoint navigation is enough; basis or detail stays on its actual owner.
- **EVENT DETAIL** — retain a consequential occurrence/version in the history of its owning Proceeding, Intervention, Instrument, or Programme; do not create an independently navigable event type.
- **DERIVED VIEW** — compute the current answer or projection from stored facts.
- **BACKSTAGE EVIDENCE** — preserve provenance/audit material below the operator model unless a real workflow proves independent operator use.
- **EXTERNAL OUTCOME** — ingest a decision/result owned by another actor; do not manufacture a CORDON object or Action for it.
- **CONDITIONAL REOPENING** — closed now; reopen only on the stated grain-sufficient workflow and deletion failure.
- **REJECT** — no independent operator capability survives the simpler alternatives.

## A. Thirteen nouns-as-types

| # | Candidate | Classification | Adversarial disposition |
|---:|---|---|---|
| 1 | Natural Person | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Consolidate with Organization into `Operator Party`; preserve party kind, legal identity, signing capacity, and contextual roles. Separate typehood was normalized actor taxonomy, not a distinct manager capability. |
| 2 | Organization | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Consolidate with Natural Person into `Operator Party`; organization-specific facts remain qualified properties. Separate typehood plus an Interface costs more than one focused party object. |
| 3 | Agricultural Holding | **KEEP CORE** | **Deletion failure:** complete-population opportunity evaluation and farm continuity fail when operators, representatives, and Parcels change; the manager cannot coordinate one member-farm route without fragmenting it across Party and Parcel records. |
| 4 | Cadastral Parcel | **KEEP CORE** | **Deletion failure:** the manager cannot identify the exact land affected by official condition, duty, access, filing, permit, dispatch, execution, or residual work; geometry/Holding substitution merges concurrent land routes. |
| 5 | Official Area | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store authoritative area identity/version/geometry as a qualified effect on the defining Governing Instrument and derive Parcel applicability. The manager navigates current area consequence, not an area administration object. Prior retention was normalization-led. |
| 6 | Individual Plant | **CONDITIONAL REOPENING** | Reopen only when stable plant identity is preserved and a manager must select, dispatch, inspect, replace, or cure that same plant in a way Parcel scope/count cannot preserve. A tree map or detection inventory alone is insufficient. |
| 7 | Plant Trade Unit / Lot | **CONDITIONAL REOPENING** | Reopen only when an authorized CORDON material allocation/dispatch workflow requires selecting the same traceable Lot through partial custody, substitution, or return. Supplier/passport/internal stock records alone are backstage evidence. |
| 8 | Organism Taxon or Lineage | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Use controlled taxon/lineage identifiers on Instrument, Parcel-condition, and Intervention properties; biological reference data remains backstage. The manager does not act on a navigable taxonomy. **Normalization-only flag.** |
| 9 | Cultivar | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Use a controlled cultivar identifier and relevant eligibility/design properties on Intervention/material detail. Canonical aliases and scientific response tables are backstage reference data. **Normalization-only flag.** |
| 10 | Public Programme or Measure | **KEEP CORE** | **Deletion failure:** complete-population opportunity evaluation and comparison of concurrent public routes lose their enduring anchor across openings, Instruments, Proceedings, claims, and fallback. |
| 11 | Governing Instrument | **KEEP CORE** | **Deletion failure:** the manager cannot cite or explain the exact basis, authority, period, clock, amendment/stay/supersession, or changed consequence, and cannot selectively reopen decisions affected by a rule change. |
| 12 | Public Proceeding | **KEEP CORE** | **Deletion failure:** the manager cannot keep one formal matter, filings, authority outcomes, next owner, and selective appeal/audit/recovery reopening together without a generic event history. Retained for operator coordination, **not** the authority's internal dossier. |
| 13 | Intervention | **KEEP CORE** | **Deletion failure:** design, capacity, dispatch, execution, acceptance, payment, and establishment for one bounded physical undertaking fragment; the manager cannot distinguish intended, done, accepted, paid, and biologically established results. |

## B. Six pre-correction event types

No event candidate remains an independent core type. Each occurrence remains consequential, but the manager can revisit it as typed event detail on its operator object. External identifiers and evidence establish the detail; they do not force typehood.

| # | Candidate | Classification | Adversarial disposition |
|---:|---|---|---|
| 1 | Official Notice or Service | **EVENT DETAIL** | Store notice/service identity, recipient/scope, channel, effective time, proof, and clock consequence on the owning Governing Instrument or Public Proceeding history. Independent navigation adds no manager action. |
| 2 | Public Filing Submission | **EVENT DETAIL** | Store each released/protocolled version, filer, receipt, scope snapshot, and clock in Public Proceeding history. The Proceeding is the operator anchor; a filing object mainly mirrors an authority's protocol record. |
| 3 | Plant Material Movement | **CONDITIONAL REOPENING** | Until a core Lot workflow is proven, movement/passport/shipment identity is supplier/regulator evidence attached to Intervention execution detail. Reopen with Lot only if partial quantities/reversals must drive an operator allocation or dispatch decision. |
| 4 | Field Execution Occurrence | **EVENT DETAIL** | Store bounded performance occasions, actor, actual scope/quantity, exceptions, and evidence in Intervention history. The manager compares intended/as-built/accepted slices without navigating a separate event population. |
| 5 | Field Inspection or Acceptance Occurrence | **EVENT DETAIL** | Store each visit/verbale, authority, examined scope, findings, accepted/excluded quantity, defects, and follow-up in Intervention or Proceeding history. The inspector's internal record does not justify a core type. |
| 6 | Cash Settlement Transaction | **EVENT DETAIL** | Store transaction reference, amount, value date, payer/payee, return/reversal, and evidence on the payment Proceeding history; derive settled/open amounts. Bank transaction identity is external proof, not an operator-managed type. |

## C. Thirty-nine fixed relationship types

Only `Intervention Capacity Commitment` survives as an independently managed relationship object. All other relationship facts are retained once on an operator object, by a direct link, as a derived view, as an external outcome, or conditionally.

| # | Candidate | Classification | Adversarial disposition |
|---:|---|---|---|
| 1 | Cooperative Membership | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Membership basis, period, and state are qualified properties/direct cooperative link on Operator Party or Holding. No independent manager operation targets a membership object. |
| 2 | Holding Stewardship | **DIRECT LINK** | Link Holding to current steward Party; keep basis/period as Holding responsibility properties/history when consequential. |
| 3 | Holding Representation | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store representative Party, scope, period, and mandate Instrument on Holding. It changes through mandate acceptance but is not separately navigated. |
| 4 | Parcel Tenure | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store tenure holder, kind, basis, and period on Parcel. The manager needs tenure as a dispatch/filing premise, not a tenure-object lifecycle. |
| 5 | Parcel Access Authorization | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store access actor, scope, period, basis, and unresolved condition on Parcel/Intervention readiness facts. |
| 6 | Parcel Consent | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store consent outcome, consenter, beneficiary, scope, date, and basis on Parcel or relevant Intervention; it is evidence for access, not an operator object. |
| 7 | Holding Parcel Declaration | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store declared Holding link, declared extent/use, source effective date, and conflict state on Parcel/Holding. |
| 8 | Holding Parcel Conduction | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store current operating Holding link and period on Parcel. Separate relationship type was domain normalization. |
| 9 | Parcel Official Area Applicability | **DERIVED VIEW** | Derive proposition/date-specific applicability from Parcel geometry/facts and defining Instrument effects; materialize if needed later, but do not make it a core navigable type. |
| 10 | Programme Constitution | **DIRECT LINK** | Link Programme to its constituting Instrument; constitution/effective facts stay on Instrument/Programme. |
| 11 | Programme Funding Authority | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store funding authority, budget/conditions, and Instrument link on Programme. No manager action targets this relationship independently. |
| 12 | Official Area Definition | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store authoritative area definition/version/geometry as a Governing Instrument effect. Independent Area and definition objects would double-normalize the same fact. |
| 13 | Instrument Amendment | **DIRECT LINK** | Direct predecessor/successor link with amendment kind/effective detail on the amending Instrument history. |
| 14 | Instrument Supersession | **DIRECT LINK** | Direct supersedes link; priority/effective consequence remains Instrument detail and affected decisions are derived. |
| 15 | Instrument Stay | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store stayed Instrument link, proposition/scope, period, authority, and basis on the staying Instrument/Proceeding outcome. |
| 16 | Proceeding Authority Grant | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store deciding authority Party, exact power, basis Instrument, and period on Public Proceeding. The manager needs the next owner, not a grant object. |
| 17 | Instrument-Grounded Parcel Duty | **DERIVED VIEW** | Derive current Parcel duty/bearer/consequence from Instrument effect, Parcel applicability, and Party/Holding responsibility; retain exact basis in the explanation. Do not copy every clause into relationship objects. |
| 18 | Instrument-Grounded Parcel Permission | **DERIVED VIEW** | Derive current permission/beneficiary/condition from Instrument and Parcel/Proceeding facts. Authority outcomes remain external; no independent permission object. |
| 19 | Intervention Authorization | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store authorizing Instrument/Proceeding outcome, authorized scope, actor, period, and limits on Intervention. |
| 20 | Pathogen Taxon Response | **BACKSTAGE EVIDENCE** | Scientific/taxonomic response matrix supports applicability/design explanations but is not independently selected or acted on by the manager. **Normalization/other-actor-record flag.** |
| 21 | Pathogen Cultivar Response | **BACKSTAGE EVIDENCE** | Preserve qualified scientific/programme evidence backstage and project relevant result onto Intervention design/readiness. **Normalization/other-actor-record flag.** |
| 22 | Proceeding Participation | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store participants, roles, authority basis, and periods on Public Proceeding; no separate participant-assignment object. |
| 23 | Proceeding Decision Authority | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store current/qualified deciding Party, power, basis, and period on Public Proceeding. |
| 24 | Intervention Parcel Scope | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store versioned intended/certified/authorized/as-built/accepted Parcel slices on Intervention, with event details establishing changes. |
| 25 | Intervention Plant Scope | **CONDITIONAL REOPENING** | Reopen only with valid Individual Plant identity and plant-specific selection/action failure not preservable by Parcel scope and quantities. |
| 26 | Intervention Cultivar Specification | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Controlled cultivar specification belongs on Intervention design/as-built detail. |
| 27 | Intervention Organism Specification | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Controlled target/condition identifiers belong on Intervention; taxonomic reference remains backstage. |
| 28 | Intervention Responsibility | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store responsible Party by management/execution/warranty/aftercare kind, scope, period, and basis on Intervention. |
| 29 | Intervention Inspection Authority | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store qualified inspector Party/power/basis on Intervention or Proceeding; inspection detail records the occurrence. |
| 30 | Intervention Acceptance Authority | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store exact compulsory/funded/contractual acceptor and basis on Intervention; external acceptance outcomes remain event detail. |
| 31 | Intervention Capacity Commitment | **KEEP CORE** | **Deletion failure:** the authorized manager cannot atomically commit/rebalance quantities, slots, periods, firmness, prerequisites, release conditions, and protected commitments across several Interventions; a recommendation or property on one Intervention cannot preserve portfolio coherence. |
| 32 | Member Entitlement | **COLLAPSE INTO OPERATOR OBJECT OR PROPERTY** | Store beneficiary Party, awarded scope/ceiling/stage/remaining exposure and basis on the award/payment Proceeding and Programme link. The public award is an external outcome, not a manager-owned relationship object. |
| 33 | Creditor Right | **EXTERNAL OUTCOME** | Public instruction/liquidation/order establishes any payable debt; store the qualified result on the payment Proceeding and derive residual. Another actor's accounting record does not justify core typehood. |
| 34 | Intervention Lot Use | **CONDITIONAL REOPENING** | Reopen with core Lot only if Lot-specific intended/authorized/as-built quantity changes a manager dispatch, acceptance, claim, substitution, or cure decision. |
| 35 | Lot Allocation | **CONDITIONAL REOPENING** | Reopen only with a proven operator Lot allocation Action and independent quantity/period/history; supplier allocation records alone are backstage. |
| 36 | Lot Custody | **CONDITIONAL REOPENING** | Reopen only if custody transitions at Lot grain change dispatch, rejection, return, or liability decisions beyond Intervention event detail. |
| 37 | Lot Movement Control | **BACKSTAGE EVIDENCE** | Plant-passport/movement-control authority belongs to regulator/supplier evidence unless a real CORDON action consumes it at Lot grain. **Other-actor-record flag.** |
| 38 | Lot Warranty Responsibility | **CONDITIONAL REOPENING** | Reopen if an actual warranty/defect route requires manager selection and cure at persistent Lot grain; otherwise keep warranty terms on Instrument/Intervention. |
| 39 | Lot Return Responsibility | **CONDITIONAL REOPENING** | Reopen if a real return workflow requires the manager to route the same Lot and quantity independently; otherwise store return owner and outcome in Intervention event detail. |

## D. Ten recommended Proceeding-scope types

The claimed-versus-authority-determined distinction remains mandatory, but it does not require ten relationship types. Claimed scope is versioned event detail on Public Proceeding filings; authority-determined scope is an external outcome in Proceeding history; the enduring subject is a direct link. This preserves selective reopening without a type matrix.

| # | Candidate | Classification | Adversarial disposition |
|---:|---|---|---|
| 1 | Proceeding Claimed Scope — Natural Person | **EVENT DETAIL** | In consolidated Party form, keep the claimed person subject, amount/stage/inclusion, basis, and version on each filing detail. |
| 2 | Proceeding Authority-Determined Scope — Natural Person | **EXTERNAL OUTCOME** | Keep admitted/excluded/decided person scope and amount as qualified authority outcome detail on Proceeding. |
| 3 | Proceeding Claimed Scope — Organization | **EVENT DETAIL** | In consolidated Party form, keep organization subject, requested amount/exception/stage, basis, and version on filing detail. |
| 4 | Proceeding Authority-Determined Scope — Organization | **EXTERNAL OUTCOME** | Keep organization-specific reviewed/admitted/excluded/decided scope on Proceeding outcome detail. |
| 5 | Proceeding Claimed Scope — Agricultural Holding | **EVENT DETAIL** | Keep Holding, extent/use/request, basis, and filing version in Proceeding history; direct Proceeding–Holding navigation remains enough. |
| 6 | Proceeding Authority-Determined Scope — Agricultural Holding | **EXTERNAL OUTCOME** | Keep authority-recognized/excluded Holding scope in Proceeding history; do not create a durable matrix row. |
| 7 | Proceeding Claimed Scope — Cadastral Parcel | **EVENT DETAIL** | Keep requested Parcels/extents, basis, and version on filing detail; Parcel remains the durable object. |
| 8 | Proceeding Authority-Determined Scope — Cadastral Parcel | **EXTERNAL OUTCOME** | Keep reviewed/admitted/excluded/permitted Parcel slices as authority outcome detail; affected work is derived. |
| 9 | Proceeding Claimed Scope — Intervention | **EVENT DETAIL** | Keep claimed Intervention phase/slice/quantity/cost/amount and version on filing detail. |
| 10 | Proceeding Authority-Determined Scope — Intervention | **EXTERNAL OUTCOME** | Keep admitted/permitted/accepted/audited/recovered Intervention slice/amount as authority outcome detail on Proceeding. |

**Normalization-only flag:** all ten were retained pre-correction to normalize two authority classes across five endpoint types. None provides an independent manager selection or Action beyond what the core Proceeding, direct subject link, versioned filing detail, and qualified authority outcome already preserve.

## E. Eleven Actions

Only Actions genuinely owned by the cooperative manager's authority survive. Member, technician, beneficiary, executor, public-control, plant-health, and private acceptor operations remain external outcomes or conditional reopenings until a real authorized CORDON transaction boundary is proven. “Supervision” means CORDON can prepare, route, explain, and verify the consequence; it does not convert another actor's reserved decision into a core Action.

| # | Candidate | Classification | Adversarial disposition |
|---:|---|---|---|
| 1 | Elect voluntary participation | **CONDITIONAL REOPENING** | Member-owned. Reopen only if the member or authorized representative actually makes the election through CORDON; otherwise ingest the election and preserve it on Party/Holding/Proceeding. |
| 2 | Accept the cooperative execution mandate | **KEEP CORE** | **Deletion failure:** the cooperative manager cannot exercise or record the cooperative's distinct acceptance/refusal of a member-granted mandate; member participation or eligibility would be mistaken for cooperative authority and individual fallback could be lost. |
| 3 | Certify Technical Intervention Design | **CONDITIONAL REOPENING** | Technician-owned. CORDON can assemble and test design readiness, but a core Action reopens only if the assigned professional certifies through CORDON. |
| 4 | Release Public Application | **CONDITIONAL REOPENING** | Beneficiary/representative-owned. Preparation and routing remain supported; reopen the release Action only when CORDON is the authorized submission channel and can prove signer and protocol receipt. |
| 5 | Commit or Rebalance Intervention Capacity | **KEEP CORE** | **Deletion failure:** the manager can compare portfolios but cannot make the cooperative's governed atomic commitment/release/reallocation decision, protect existing commitments, or record a valid override. |
| 6 | Dispatch Intervention | **KEEP CORE** | **Deletion failure:** named-action readiness cannot become an attributable, bounded authorization to commence field work; schedule/preparation would be confused with dispatch. |
| 7 | Attest Intervention Performance | **CONDITIONAL REOPENING** | Executor-owned. Preserve performance as Intervention event detail; reopen an Action only if the assigned executor submits the authoritative attestation through CORDON. |
| 8 | Decide compulsory compliance acceptance | **EXTERNAL OUTCOME** | Competent plant-health authority owns legal completion. Ingest the qualified outcome; do not give the cooperative manager or harness that power. Reopen only as a concrete authority integration, not core manager Action. |
| 9 | Decide funded-work acceptance | **EXTERNAL OUTCOME** | Assigned public control/funding body owns admissible executed scope. Preserve outcome detail and claim consequence; no CORDON Action absent authority use through CORDON. |
| 10 | Decide contractual acceptance | **CONDITIONAL REOPENING** | Private contract/protocol acceptor owns the decision. Reopen only if that actor actually decides through CORDON; otherwise ingest acceptance/defect/cure detail. |
| 11 | Release a payment claim | **CONDITIONAL REOPENING** | Beneficiary/representative-owned. Finance preparation remains operator work; core release reopens only with a proven authorized CORDON filing channel and claim-stage authority. |

## F. Three Functions

All three survive because each buys a distinct live manager capability not safely reducible to one object property, direct link, event detail, or stable projection.

| # | Candidate | Classification | Exact cooperative-manager deletion failure |
|---:|---|---|---|
| 1 | Determine Affected Decisions | **KEEP CORE** | **Question 1 and selective reopening fail:** the manager cannot traverse a material change to the exact decisions/actions it can alter, explain the dependency and next owner, or explicitly protect unaffected work from a broad reset. |
| 2 | Assess Named-Action Readiness | **KEEP CORE** | **Questions 2 and 4 fail:** the manager cannot get current Action-specific readiness, blockers, indeterminacy, cure owners, or consequence of proceeding/waiting without duplicating rules or inventing a global ready state. |
| 3 | Compare Feasible Intervention Portfolios | **KEEP CORE** | **The cooperative capacity decision fails:** the manager loses complete-population combinatorial feasibility, binding resources, alternatives, uncertainty/sensitivity, and expected incremental realized Xylella-loss reduction; a static score/ranking cannot replace it. |

## G. Decision-Capable Actor Interface

| Candidate | Classification | Adversarial disposition |
|---|---|---|
| Decision-Capable Actor Interface | **REJECT** | It preserves no fact and its own prior deletion analysis admitted only code/workflow reuse. Consolidating Natural Person and Organization into one `Operator Party` object removes the polymorphic branch entirely while retaining party kind and concrete identity. Keeping both object types plus an Interface would be normalization and platform convenience, not a cooperative-manager capability. |

## Count and coverage audit

| Candidate class | Audited | KEEP CORE | Pruned as independent core elements |
|---|---:|---:|---:|
| Nouns-as-types | 13 | 6 | 7 |
| Event types | 6 | 0 | 6 |
| Fixed relationship types | 39 | 1 | 38 |
| Recommended Proceeding-scope types | 10 | 0 | 10 |
| Actions | 11 | 3 | 8 |
| Functions | 3 | 3 | 0 |
| Interface | 1 | 0 | 1 |
| **Total candidate slots** | **83** | **13** | **70** |

The replacement `Operator Party` is one new consolidated object, so the **practical core has 14 elements**, not 13. It replaces two pruned candidate types and makes the rejected Interface unnecessary.

### Classification totals

| Classification | Count |
|---|---:|
| KEEP CORE | 13 |
| COLLAPSE INTO OPERATOR OBJECT OR PROPERTY | 26 |
| DIRECT LINK | 4 |
| EVENT DETAIL | 10 |
| DERIVED VIEW | 3 |
| BACKSTAGE EVIDENCE | 3 |
| EXTERNAL OUTCOME | 8 |
| CONDITIONAL REOPENING | 15 |
| REJECT | 1 |
| **Total** | **83** |

## Selective reopening contract

A pruned candidate reopens only when all of these are evidenced:

1. a real cooperative-manager decision, supervised authorized CORDON Action, consequence explanation, or selective-reopening failure is named;
2. the manager must navigate, compare, select, or act on the candidate independently;
3. the candidate has stable real identity and grain outside CORDON;
4. a core object property/history entry, direct link, event detail, derived view, backstage evidence, or external outcome cannot preserve the capability;
5. the positive case is not merely normalization, source fidelity, an external identifier, a map layer, or another actor's internal record; and
6. for an Action, the deciding actor really executes or stages the operation through an authorized CORDON boundary.

Until those conditions are met, the 70 pruned candidate slots stay closed. The six questions, authority boundaries, named-action readiness, accounting-versus-cash distinction, installation-versus-establishment distinction, and selective reopening remain semantic invariants; they do not require the rejected type inventory.
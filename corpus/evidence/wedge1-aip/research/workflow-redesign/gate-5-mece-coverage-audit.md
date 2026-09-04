# Gate 5 MECE coverage audit — accepted nouns and fact-bearing relationships

**Status:** decisive Gate 3–4 coverage audit  
**Date:** 22 August 2026  
**Verdict:** **PASS-WITH-CORRECTIONS**

## 1. Audit question and authority boundary

This audit tests whether the accepted **13 persistent real-world nouns**, **seven fact-bearing relationship families**, and **11 mandatory concrete relationship grains** can carry every accepted proposition in the connected operating model: the six recurring questions, five operating responsibilities, compulsory and voluntary routes, bounded Wedge 1 endpoint, consequential event/outcome classes, and selective-reopening rule.

The audit uses only the current authorities named for this review. `REDESIGN_SEQUENCE.md:12-35,64-72` establishes the accepted workflow, noun, relationship, route, endpoint and evidence boundaries. `connected-operating-model.md:7-21,37-54,56-195,197-257` is the proposition authority. `gate-3-noun-candidates.md:9-29,35-145,147-200` and `gate-4-relationship-candidates.md:9-33,35-267` are the inventories under test. Gate 1 materials are used only to challenge omission claims, especially the five final residual components (`workflow-research-synthesis.md:198-208`), municipal decision-right detail (`municipal-government-workflows.md:88-137`), institutional exceptions (`unknown-unknowns-institutional.md:37-211`), field-system gates (`unknown-unknowns-field-system.md:60-280`), saturation/reactivation, and the private-data adjudication (`gate-3-private-data-resolution-adjudication.md:8-18,20-37,89-119`).

This is **not** an Ontology-representation decision. “Event/outcome,” “contextual direct link,” and “derived computation” below are representation categories in the accepted domain model, not proposals for new nouns or relationship families. A missing representation category is not automatically a missing noun or fact-bearing relationship.

## 2. Mechanical legend

### 2.1 Endpoint noun codes

| Code | Accepted noun |
|---|---|
| N1 | Natural Person |
| N2 | Organization |
| N3 | Agricultural Holding |
| N4 | Cadastral Parcel |
| N5 | Official Area |
| N6 | Individual Plant (conditional identity) |
| N7 | Plant Trade Unit / Lot |
| N8 | Organism Taxon or Lineage |
| N9 | Cultivar |
| N10 | Public Programme or Measure |
| N11 | Governing Instrument |
| N12 | Public Proceeding |
| N13 | Intervention |

### 2.2 Relationship-family codes

| Code | Accepted family |
|---|---|
| F1 | Actor–Context Assignment |
| F2 | Land Association or Right |
| F3 | Scoped Governing Effect or Applicability |
| F4 | Organism–Host Relationship |
| F5 | Intervention Scope and Material Use |
| F6 | Capacity Reservation or Commitment |
| F7 | Member-Specific Entitlement or Creditor Right |
| C | Contextual direct relationship; no independent relationship facts |
| D | Derived computation/reconciliation; not a relationship fact |
| — | Event/outcome is sufficient; no relationship family is required |

### 2.3 Mandatory grain codes

| Code | Mandatory anti-collapse grain | Current family disposition |
|---|---|---|
| G1 | cooperative membership | F1 |
| G2 | Holding stewardship/representation | F1 |
| G3 | actor–Parcel interest | F2 |
| G4 | Holding–Parcel declaration/conduction | F2 |
| G5 | Parcel–Official Area membership | F3 when authority/date/rule make it legal; D for raw overlap |
| G6 | Governing Instrument effect/lineage | F3 |
| G7 | Public Proceeding participation/scope | F1 owns actor participation/authority; **non-actor proceeding scope lacks an explicit family owner** |
| G8 | Intervention physical scope | F5 |
| G9 | Intervention–Cultivar specification | F5 |
| G10 | Intervention responsibility/capacity | F1 for responsibility; F6 for reserved/committed capacity |
| G11 | Plant Trade Unit / Lot allocation/custody | F5 owns Intervention use; **actor–Lot custody/allocation lacks an explicit family owner** |

The two bold dispositions are the only true inventory omissions found. They are internal coverage holes in already accepted mandatory grains, not evidence for a fourteenth noun or an eighth family.

### 2.4 Coverage-result codes

- **DIRECT** — endpoints plus an accepted fact-bearing family/grain own the necessary durable fact.
- **EVENT** — accepted nouns/relationships provide subjects and context; the consequential change is correctly an event or bounded outcome.
- **DERIVED** — the proposition is a deterministic or policy computation over direct facts; it must not be promoted to a new relationship.
- **CONTEXT** — a direct endpoint connection is needed but has no independent business facts.
- **TRANSITIVE-ONLY** — currently answerable only by traversing several direct facts; safe only as a derived answer, never as a new asserted right.
- **CORRECTION** — an accepted mandatory grain has no unambiguous family owner at the required endpoint grain.

## 3. Proposition coverage matrix

The matrix is intentionally atomic. Every row names the proposition, endpoint nouns, relationship family/grain, and the event/outcome or computation that completes the answer.

| ID | Required operator proposition | Endpoint nouns | Family / grain | Event, outcome or derived computation | Result |
|---|---|---|---|---|---|
| Q1 | What changed, and what does it affect? | Any affected N1–N13; normally N11/N12/N13 plus N3/N4/N5/N6/N7 | F1–F7 as changed facts; C for context | Consequential change event; dependency traversal identifies affected work while preserving unaffected facts | EVENT + DERIVED |
| Q2 | What is now required, allowed or blocked? | N11 with affected N1–N13 | F3/G5/G6; F1/F2/F4/F5/F6/F7 as premises | Proposition-specific applicability, clock calculation, scoped-conflict evaluation and named-action condition check | DIRECT + DERIVED |
| Q3 | Who chooses, who decides and which route continues? | N1/N2 with N3/N10/N11/N12/N13 | F1/G1/G2/G7/G10; F2/G3/G4; F7 where a right exists | Decision/choice outcome; route availability derived without transferring authority | DIRECT + EVENT |
| Q4 | Is the route ready for the named action? | N1/N2/N3/N4/N6/N7/N9/N11/N12/N13 | F1/F2/F3/F5/F6/F7; G2–G10 | Action-specific readiness computation; never a generic ready relationship or status | DERIVED |
| Q5 | What was done, and who accepted it? | N1/N2/N4/N6/N7/N12/N13 | F1/G7/G10; F5/G8/G9/G11 | Execution, inspection and route-specific acceptance events/outcomes; accepted scope may update F5 | EVENT + DIRECT |
| Q6 | Did the intended result land, and what remains open? | N1/N2/N3/N4/N6/N7/N10/N11/N12/N13 | F1/F5/F7; G7–G11 | Settlement, installation acceptance, survival/defect review, replacement/cure and open-owner derivation | EVENT + DERIVED |
| D01 | The competent plant-health authority owns official condition, area, regime and compulsory duty. | N2/N5/N8/N11/N12 with N3/N4/N6 | F1/G7 plus F3/G5/G6; F4 where host/lineage matters | Finding, confirmation, measure and duty outcomes remain distinct | DIRECT + EVENT |
| D02 | A Comune’s publication, asset, local-enforcement, contracting, permit and programme roles are resolved separately by event, asset, delegation and date. | N2/N4/N10/N11/N12/N13 | F1/G7/G10; F2/G3; F3/G6 | Publication, ordinance, award, permit and programme decisions are separate events | DIRECT + EVENT |
| D03 | Municipal boundary alone proves neither ownership nor decision authority. | N2/N4/N5 | F2/G3 and F3/G5/G6 | Negative inference guard: geometry/boundary overlay is D only | DIRECT |
| D04 | Authority is proposition-specific; unresolved conflict blocks only decisions the proposition can change. | N2/N11/N12 plus affected noun | F1/G7; F3/G6 | Source/proposition reconciliation and affected-decision computation; conflict is not a global status | DERIVED |
| D05 | Funding evaluates the complete in-scope member–land–intervention population on a material opportunity/governing change. | N1/N2/N3/N4/N10/N11/N13 | F1/G1/G2; F2/G3/G4; F3/G6; F5/G8 | Population is derived across membership, holding, land, programme effects and intervention scope | TRANSITIVE-ONLY + DERIVED |
| D06 | Member interest or management nomination does not define that evaluation universe. | N1/N2/N3/N4/N10/N13 | Same facts as D05 | Exclusion guard in population computation; interest/nomination events cannot truncate the universe | DERIVED |
| D07 | Public eligibility is a separate determination. | N1/N2/N3/N4/N10/N11/N12 | F2/F3; G3–G7 | Eligibility is a dated derived/public decision outcome, not a durable “eligible” relationship | EVENT + DERIVED |
| D08 | Member adhesion is a separate member choice. | N1/N2/N3/N10/N12 | F1/G1/G7 only where participation/mandate facts persist | Adhesion choice/submission outcome; not a noun or generic participation status | EVENT |
| D09 | Cooperative acceptance of the negotiated execution mandate is separate. | N1/N2/N3/N11/N13 | F1/G1/G2/G10; F3/G6 as instrument basis | Acceptance event creates/activates the scoped mandate assignment; does not create eligibility | DIRECT + EVENT |
| D10 | Cooperative pursuit of an opportunity is separate from public and member decisions. | N2/N10/N11/N12 | F1/G7 and F3/G6 | Cooperative governance decision event | EVENT |
| D11 | Public admissibility, ranking and concession are separate authority decisions. | N1/N2/N3/N10/N11/N12/N13 | F1/G7; F3/G6; F7 when concession creates a durable member right | Admissibility, ranking and concession outcomes remain distinct | EVENT + DIRECT |
| D12 | A valid member route omitted from collective execution continues individually where allowed. | N1/N2/N3/N10/N11/N12/N13 | F1/G1/G7; F3/G6; F7 if right exists | Route-continuation computation after collective non-selection; no inferred extinguishment | DERIVED |
| D13 | Funding-source election/cumulation is applied only when the instrument makes it consequential. | N1/N2/N3/N10/N11/N12/N13 | F3/G6; F7 if a right exists | Beneficiary election and administration non-overlap decision; same-operation comparison is D | EVENT + DERIVED |
| D14 | Enterprise-crisis, continuity and signing-authority exceptions are instrument-specific. | N1/N2/N3/N10/N11/N12 | F1/G2/G7; F3/G6 | Dated status evidence feeds applicability/signing computation; court/public decision is an event | DIRECT + DERIVED |
| D15 | Scarce-capacity allocation is separate from eligibility, concession, duty, creditor identity and fallback. | N1/N2/N3/N10/N11/N13 | F6/G10; F7; F3 | Separation guard: no family fact rewrites another | DIRECT |
| D16 | Non-discretionary constraints and approved fairness safeguards define feasible portfolios. | N2/N3/N4/N7/N10/N11/N13 | F1/F2/F3/F5/F6/F7; G1–G11 as inputs | Feasible-set computation; portfolios/cohorts remain derived, not nouns or relationships | DERIVED |
| D17 | CORDON recommends highest incremental expected realized Xylella-loss reduction, with uncertainty, alternatives and neutral tie-break only for material equivalence. | N3/N4/N8/N9/N10/N13 | F3/F4/F5/F6/F7 as inputs | Policy-governed recommendation/sensitivity computation; non-binding outcome | DERIVED |
| D18 | The authorized cooperative role commits or overrides capacity with recorded reason. | N1/N2/N11/N13 (and N7 when specific stock is committed) | F1/G10; F6/G10 | Commit/override event creates or changes F6; recommendation itself does not | DIRECT + EVENT |
| D19 | Tentative availability, reservation, firm commitment and scheduled capacity remain distinct. | N1/N2/N13, optional N7 | F6/G10 | Reservation/firming/release/reallocation/expiry events update the relationship history | DIRECT + EVENT |
| D20 | The CAA/source authority repairs authoritative farm-file/member/land facts. | N1/N2/N3/N4/N11/N12 | F1/G2/G7; F2/G3/G4 | Correction event changes the appropriate endpoint or relationship fact, preserving prior basis | DIRECT + EVENT |
| D21 | The technician owns professional design and assertions. | N1/N2/N11/N12/N13 | F1/G7/G10; F5/G8/G9 | Professional assertion/design outcome; authority derives from assignment/instrument | DIRECT + EVENT |
| D22 | The beneficiary or authorized representative certifies/releases application and payment claims. | N1/N2/N3/N11/N12 | F1/G2/G7; F7 where claim acts on a right | Certification/release/filing event; preparation does not imply release | DIRECT + EVENT |
| D23 | Landscape, VIncA, water and other permits belong to the authority competent for the exact proceeding. | N2/N4/N5/N11/N12/N13 | F1/G7; F2/G3; F3/G5/G6; F5/G8 | Trigger/screening, application, conditions and permit outcome remain distinct | DIRECT + EVENT |
| D24 | A work basis starts readiness assembly but does not dispatch work. | N1/N2/N3/N4/N6/N7/N9/N11/N12/N13 | F1/F2/F3/F5/F6/F7; G2–G11 | Named-action readiness computation; dispatch is a later authorized event | DERIVED + EVENT |
| D25 | Field dispatch belongs to the responsible field manager after named-action readiness. | N1/N2/N11/N13 | F1/G10; F6/G10 | Dispatch decision/event; it neither proves execution nor acceptance | DIRECT + EVENT |
| D26 | Execution may be owner, contractor, nursery, ARIF or public crew within assigned scope. | N1/N2/N7/N11/N13 | F1/G10; F5/G8/G9/G11; F6/G10 | Delivery, custody, installation and execution events; **actor–Lot custody has correction C2** | CORRECTION + EVENT |
| D27 | Executor proof, beneficiary/technician assertions, compulsory acceptance, funded-work public control and private contractual acceptance remain separate. | N1/N2/N11/N12/N13 | F1/G7/G10; F5/G8 | Multiple route-specific evidence/acceptance outcomes; no universal completion relationship | DIRECT + EVENT |
| D28 | Finance engineers admissible procurement/evidence before spend; technical instruction, liquidation, order and cash settlement are separate. | N1/N2/N3/N7/N10/N11/N12/N13 | F1/G7/G10; F5/G11; F7 | Evidence-readiness computation; instruction/liquidation/order/settlement events | EVENT + DERIVED |
| D29 | Only treasury/bank/beneficiary evidence proves cash; creditor identity remains member-specific. | N1/N2/N3/N11/N12 | F7; F1/G7 for payer authority | Settlement event acts on F7; payment order alone is insufficient | DIRECT + EVENT |
| D30 | Audit, revocation and recovery are later authority proceedings that can reopen financial work without rewriting field outcomes. | N1/N2/N3/N10/N11/N12/N13 | F1/G7; F3/G6; F7 | Audit finding, revocation and recovery events/outcomes; affected financial reopening | EVENT |
| R1 | Land explains current official/operational situation and duty, not field completion. | N1/N2/N3/N4/N5/N6/N8/N11/N12 | F1/F2/F3/F4; G2–G7 | Current-situation reconciliation and duty computation | DIRECT + DERIVED |
| R2 | Funding owns opportunity population, adhesion, mandate, pursuit and capacity allocation, not concession authority. | N1/N2/N3/N4/N10/N11/N12/N13 | F1/F2/F3/F5/F6/F7; G1–G10 | Population, decisions, feasible portfolio and recommendation outcomes | DIRECT + DERIVED |
| R3 | Applications assembles the cited proceeding and routes each exception to the fact/decision owner. | N1/N2/N3/N4/N10/N11/N12/N13 | F1/F2/F3/F5/F7; G2–G10 | Preparation, correction, filing, request, permit and public-review events; **non-actor proceeding scope has correction C1** | CORRECTION + EVENT |
| R4 | Field Work owns readiness, execution, evidence, acceptance handoff and aftercare coordination. | N1/N2/N3/N4/N6/N7/N9/N11/N12/N13 | F1/F2/F3/F5/F6; G2–G11 | Readiness calculation plus dispatch/execution/inspection/acceptance/aftercare events | DIRECT + EVENT |
| R5 | Payments starts with evidence design and ends in claim decisions, settlement and possible recovery. | N1/N2/N3/N7/N10/N11/N12/N13 | F1/F3/F5/F7; G7/G11 | Claim, control, admitted amount, liquidation, order, settlement, audit/recovery outcomes | DIRECT + EVENT |
| T1 | Compulsory duty route keeps authority, responsible actor, execution choice, public-asset manager, acceptance, enforcement and remedy independent. | N1/N2/N3/N4/N5/N6/N8/N11/N12/N13 | F1/F2/F3/F4/F5/F6; G2–G10 | Finding, notice, choice/silence/refusal/obstruction, stay, execution, compliance, sanction, indemnity and rework outcomes | DIRECT + EVENT |
| T2 | Voluntary funded and self-funded recovery share legal/readiness/execution/aftercare logic; public branches activate only when applicable. | N1/N2/N3/N4/N6/N7/N9/N10/N11/N12/N13 | F1/F2/F3/F5/F6/F7; G1–G11 | Participation/pursuit/concession/claim events are conditional; self-funded route omits them without losing Intervention continuity | DIRECT + DERIVED |
| E1 | Notice, acknowledgement and named legal/administrative clocks remain consequential events, not nouns. | N1/N2/N4/N11/N12 | F1/F3 as authority/basis | Publication, PEC, notice-effect, acknowledgement, deadline start/end | EVENT |
| E2 | Sample, lab result, official confirmation and changed area/regime remain distinct. | N4/N5/N6/N8/N11/N12 | F3/G5/G6; F4 only for general host relation | Sample/result/confirmation/area-change events; legal consequence computed only at supported authority grain | EVENT + DERIVED |
| E3 | Filing, integration, ranking, concession, permit and variant decisions remain distinct proceedings/events. | N1/N2/N3/N4/N10/N11/N12/N13 | F1/F2/F3/F7; G2–G7 | Submission and public decision outcomes; proceeding scope invokes correction C1 where independently fact-bearing | CORRECTION + EVENT |
| E4 | Reservation, release, reallocation, dispatch, delivery, execution, inspection and acceptance remain events changing durable facts. | N1/N2/N4/N6/N7/N11/N12/N13 | F1/F5/F6; G7–G11 | Capacity and field event history; Lot custody invokes correction C2 | CORRECTION + EVENT |
| E5 | Requested, admitted, granted, liquidated, ordered, settled, audited, revoked and recovered amounts remain distinct. | N1/N2/N3/N10/N11/N12/N13 | F3/F7; G6/G7 | Amount-bearing decisions/events; F7 preserves the durable right and creditor | DIRECT + EVENT |
| E6 | Administrative installation, survival review, defect, replacement and cure remain distinct bounded outcomes. | N1/N2/N4/N6/N7/N9/N11/N13 | F1/G10; F5/G8/G9/G11 | Installation acceptance, biological observation, defect attribution, replacement/cure outcome | EVENT |
| S1 | Wedge 1 ends at bounded biological establishment: aftercare assigned; early survival/defect reviewed; required replacement/cure completed or explicitly owned. | N1/N2/N4/N6/N7/N9/N11/N13 | F1/G10; F5/G8/G9/G11 | Bounded endpoint derived from aftercare assignment and outcome events; not productive maturity | DIRECT + EVENT |
| S2 | Later material events reopen only affected work and preserve unaffected/earlier outcomes. | Any affected N1–N13 | The exact changed F1–F7 fact; C/D as applicable | Dependency-based selective invalidation/recomputation; no global status reset | DERIVED |
| S3 | Contradictory evidence or a newly observed operator decision selectively reopens the affected Gate 2 boundary, not the whole model. | Any affected noun/family/grain | The disputed or missing predicate only | Governance/research reactivation outcome; no automatic noun/family addition | DERIVED |

**Mechanical count:** 52 propositions tested: 6 recurring questions + 30 atomic decision-right propositions + 5 responsibility propositions + 2 route-family propositions + 6 event/outcome-class propositions + 3 endpoint/reopening propositions.

## 4. Inventory coverage and deletion tests

### 4.1 Noun deletion tests

A noun passes when deleting it makes at least one accepted proposition unsafe or forces identity into a role, event, relationship, document or analytical set.

| Noun | Minimal deletion failure | Verdict |
|---|---|---|
| Natural Person | Cannot preserve person-specific member choice, signature, representation, succession, responsibility or creditor identity as roles change. | KEEP |
| Organization | Collapses cooperative, CAA, Comune, authority, ARIF, contractor, bank and control-body identities and decision rights. | KEEP |
| Agricultural Holding | Loses the authoritative farm operating unit and complete population continuity across parcel/person change. | KEEP |
| Cadastral Parcel | Loses legally referenced land identity for notice, title, area applicability, proceeding scope and physical work. | KEEP |
| Official Area | Cannot preserve authority-defined area identity across redraw/version changes; raw geometry is not enough. | KEEP |
| Individual Plant | At admitted conditional grain, loses official target, monumental, infection, survival, defect and replacement continuity. If identity is not externally or reproducibly established, do not instantiate it. | KEEP, CONDITIONAL |
| Plant Trade Unit / Lot | Cannot trace legality, passport, reservation, receipt, substitution, defect and installed material at the governing commercial/phytosanitary grain. | KEEP |
| Organism Taxon or Lineage | Recreates unsafe scalar “Xylella status” and loses lineage-specific host/legal effects. | KEEP |
| Cultivar | Cannot preserve governed variety identity across plants/lots or evaluate programme, movement and design constraints. | KEEP |
| Public Programme or Measure | Cannot preserve one programme across openings, amendments, rankings, concessions and claims or perform complete opportunity evaluation. | KEEP |
| Governing Instrument | Loses proposition authority, version, scope, effect, supersession, clocks, mandate/contract/guarantee basis and remedy. | KEEP |
| Public Proceeding | Collapses formally instituted applications, permits, claims, appeals, audits and recovery into events or a rejected generic Case. | KEEP |
| Intervention | Cannot preserve the physical undertaking across proceedings, contractors, variants, settlement and aftercare. | KEEP |

**Noun result:** all 13 are necessary and mutually distinguishable at their admitted grains. No fourteenth noun is justified by this audit.

### 4.2 Relationship-family deletion tests

| Family | Minimal deletion failure | Verdict |
|---|---|---|
| F1 Actor–Context Assignment | Loses membership, representation, delegation, proceeding authority and intervention responsibility while actors/endpoints persist. | KEEP; extend endpoint coverage selectively under C2 |
| F2 Land Association or Right | Forces ownership/control/access/consent and Holding–Parcel conduction into endpoints or unsafe transitive inference. | KEEP |
| F3 Scoped Governing Effect or Applicability | Cannot preserve proposition/date-specific legal effect, instrument lineage or authority-grounded Parcel–Area applicability. | KEEP; extend predicate scope selectively under C1 |
| F4 Organism–Host Relationship | Forces many-to-many, evidence-qualified susceptibility/resistance conclusions into organism/cultivar endpoints. | KEEP |
| F5 Intervention Scope and Material Use | Loses intended/authorized/actual/accepted physical scope, cultivar design and Lot use through substitutions. | KEEP |
| F6 Capacity Reservation or Commitment | Reverts to unsafe inference from eligibility, requirement or availability; loses reservation/firm/release history. | KEEP |
| F7 Member-Specific Entitlement or Creditor Right | Collapses durable member right/creditor identity into instrument effect or payment events. | KEEP |

**Family result:** all seven are necessary. No eighth family is needed. Two existing families require narrow endpoint/predicate additions so that accepted G7 and G11 are genuinely covered.

### 4.3 Concrete-grain deletion tests

| Grain | Deletion consequence | Result |
|---|---|---|
| G1 membership | Complete population and member/cooperative authority become guesswork. | KEEP |
| G2 Holding stewardship/representation | Farm-file correction, signing and Holding continuity collapse into person/organization attributes. | KEEP |
| G3 actor–Parcel interest | Ownership, management, public-asset responsibility, access and consent become unsafe Holding transitivity. | KEEP |
| G4 Holding–Parcel declaration/conduction | Complete land population and farm-file history cannot survive parcel movement. | KEEP |
| G5 Parcel–Area membership/applicability | Duties/routes cannot be grounded to authority/date/partial-intersection rule; raw overlay would be over-promoted. | KEEP |
| G6 Instrument effect/lineage | Supersession, stays, amendments, delegated authority and proposition scope cannot be reconstructed safely. | KEEP |
| G7 Proceeding participation/scope | Decision owner, party participation and independently changing requested/admitted subject scope collapse. | KEEP; CORRECT FAMILY OWNERSHIP |
| G8 Intervention physical scope | Concurrent routes on one parcel and intended/authorized/actual/accepted scope collapse. | KEEP |
| G9 Intervention–Cultivar | Technical design and governed cultivar composition collapse into Lot or Intervention attributes. | KEEP |
| G10 Intervention responsibility/capacity | Dispatch, acceptance, aftercare and scarce capacity become inferred from executor/eligibility. | KEEP |
| G11 Lot allocation/custody | Nursery-to-delivery-to-installation trace, custody and substitution become event fragments with no durable accountable relationship. | KEEP; CORRECT FAMILY OWNERSHIP |

## 5. Addition tests

An addition passes only if a real persistent identity or independently fact-bearing relationship is required after all event/outcome, contextual-link and derived-computation options are applied.

| Proposed addition | Test result | Disposition |
|---|---|---|
| Generic Event, Result, Status or global Timeline | Consequential changes are atomic events/outcomes attached to surviving nouns/relationships; one global lifecycle would violate route and acceptance independence. | REJECT |
| Generic Case / dossier / bundle | Public Proceeding already covers real formal matters; private bundles are constructions. | REJECT |
| Evidence / Source / RuleRelease / CoverageRelease | Provenance and corpus maintenance are backstage; evidence qualifies facts but is not an operator noun. | REJECT |
| Task / Queue / WorkItem | Work-management constructions do not exist independently of CORDON. | REJECT |
| Permit, concession, mandate, contract, guarantee, work order or aftercare protocol noun | Real operative instances fit Governing Instrument; decisions/acceptance remain events. | REJECT AS NEW NOUN |
| Eligibility, readiness, selected, blocked, paid or complete relationship | Each is decision-, action- and date-specific or derived; generic status relationships erase bounded meaning. | REJECT |
| Capacity Reservation noun | F6 owns the durable commitment; creation/release/reallocation are events. | REJECT |
| Execution or Survival Cohort noun | Cohorts/portfolios are selected or analytical sets unless later real evidence independently preserves identity. | REJECT |
| Water Source, machinery, product/input, invoice, bank account, observation or document as a new noun class | Current accepted decisions require their legal/technical conditions and consequential events, but the present authority does not establish a minimum persistent noun at a new grain. Reopen only with a real identity-preserving process and a deletion failure. | NO CURRENT ADDITION |
| New “Proceeding Scope” family | The omission can be repaired inside F3 without creating a generic eighth family. | REJECT EIGHTH FAMILY; APPLY C1 |
| New “Custody” family | The omission can be repaired by allowing F1 scoped actor assignment to N7; Intervention use remains F5. | REJECT EIGHTH FAMILY; APPLY C2 |

## 6. True omissions and exact selective corrections

### C1 — explicitly assign non-actor Public Proceeding scope

**Finding:** G7 is named “Public Proceeding participation/scope,” but F1 only covers an actor’s participation or decision authority relative to a Public Proceeding (`gate-4-relationship-candidates.md:35-48`). The contextual-link section permits a basic Proceeding subject only when no independent scoped assignment facts exist (`gate-4-relationship-candidates.md:197-207`). It does not own independently changing, authority-recognized Proceeding scope such as the member, Holding, Parcel, Intervention, claim stage, requested scope, admitted scope or excluded scope. This leaves Applications, claims, permits, audits and recovery partly dependent on event fragments or an unowned contextual link.

**Exact correction:** keep seven families and add to **F3 Scoped Governing Effect or Applicability**:

> A Public Proceeding has a formally recognized scope or subject relative to a Natural Person, Organization, Agricultural Holding, Cadastral Parcel, Official Area, Individual Plant, Plant Trade Unit / Lot, Public Programme or Measure, Governing Instrument or Intervention when the proceeding itself preserves independent facts such as requested, reviewed, admitted, excluded or decided scope, quantity, amount, effective period or governing basis. A bare subject pointer remains contextual. Participation and decision authority remain F1; entitlement remains F7; physical Intervention scope remains F5.

This is a predicate/endpoint correction, not a new noun, family, Case abstraction or status.

### C2 — explicitly assign actor–Lot allocation/custody

**Finding:** G11 requires “Plant Trade Unit / Lot allocation/custody.” F5 owns Lot reservation, delivery, installation or replacement **use by an Intervention** (`gate-4-relationship-candidates.md:124-150`). F6 can involve a specific Lot in a capacity commitment (`gate-4-relationship-candidates.md:152-173`). Neither family owns a nursery, supplier, transporter, cooperative, member or other actor’s independently changing custody/allocation responsibility for a Lot outside or between Intervention-use events. Yet the accepted workflows require exact lot identity, recipient undertaking, movement recheck, receipt, custody, substitution and defect handoffs. Treating every custody interval as only a movement event loses the accountable holder and its effective period.

**Exact correction:** keep seven families and extend **F1 Actor–Context Assignment** so its context endpoints may include **Plant Trade Unit / Lot** for real scoped actor positions:

> A Natural Person or Organization may hold an allocation, custody, dispatch, receipt, movement-control, warranty or return responsibility relative to a Plant Trade Unit / Lot when the relationship has its own basis, scope/quantity, effective period, duties or termination/handoff conditions. Movement, dispatch and receipt remain events. Intervention-specific reservation, delivery, installation and replacement use remain F5; scarce capacity commitment remains F6.

This repairs G11 without a generic custody family or new noun.

## 7. Ambiguous ownership rules that must be made explicit

These are not additional omissions if the following precedence is enforced:

1. **F3 versus F7:** F3 owns what an instrument does and why; F7 owns the durable member-specific right, creditor, ceiling, claim stages and recovery exposure created by that effect. Concession/payment events act on F7.
2. **F1 versus F2:** F1 owns actor power/duty in an Organization, Holding, Proceeding, Intervention or—after C2—Lot context. F2 owns title, conduction, occupation, management, access or consent relative to Parcel. Holding operation never implies Parcel right.
3. **F1 versus F5:** F1 owns who is responsible; F5 owns what physical/material scope the Intervention includes. Execution or acceptance does not imply responsibility outside the assignment.
4. **F5 versus F6:** F5 owns required/intended/authorized/actual material scope; F6 owns actual scarce-capacity reservation/commitment. Requirement and availability never prove commitment.
5. **F3 versus G5 derived overlay:** authority/date/rule-grounded Parcel–Area applicability is F3; raw/conflicting geometry is D and can create only the deterministic warning/trigger it actually supports.
6. **F4 versus plant infection event:** F4 owns general evidence-qualified organism–host susceptibility/resistance/tolerance. A sample/result for an Individual Plant is an observation/event and does not become a general host relationship.
7. **Proceeding scope after C1:** F3 owns independently fact-bearing formal scope; F1 owns participants/decision authority; C owns a bare subject pointer; F7 owns durable entitlement; F5 owns physical Intervention scope.
8. **Lot after C2:** F1 owns accountable actor custody/allocation; F5 owns Intervention material use; F6 owns scarce committed stock/capacity; movement/dispatch/receipt remain events.

## 8. Transitive-inference audit

The following answers are covered only by traversal or computation. That is acceptable **only** when reported as derived and not promoted into a direct right or authority fact.

| Derived answer | Required path | Unsafe shortcut barred |
|---|---|---|
| Complete member–land opportunity population | N1/N2 —G1→ cooperative; N1/N2 —G2→ N3; N3 —G4→ N4; N11 —G6/G5→ N10/N4; N13 —G8→ N4 | “Interested/selected members define the universe” |
| Member’s affected land | membership/stewardship + Holding–Parcel declaration, optionally direct G3 right | “Member controls every Parcel of the Holding” |
| Programme opportunity/applicability | N11 effect on N10 plus proposition/date/area/actor/land premises | “Appears in programme geography, therefore eligible” |
| Municipality responsible for public land | direct N2–N4 F2 asset-management/right plus exact N11 authority | “Parcel lies in Comune, therefore Comune owns/manages/decides” |
| Lot lawful for use | N7 identity/classification + N9 + N11/F3 + movement/inspection events + N13/F5 use | “Cultivar is permitted, therefore Lot is lawful” |
| Member is beneficiary/creditor | explicit F7 and creating decision/instrument | “Appears in collective Proceeding, therefore beneficiary/creditor” |
| Intervention ready | F1/F2/F3/F5/F6/F7 premises for the named action | “Eligible/conceded/designed, therefore ready” |
| Cash landed | settlement event tied to holder/creditor and bank/treasury evidence | “Liquidated or ordered, therefore paid” |
| Wedge 1 biological endpoint reached | aftercare F1 + accepted Intervention scope F5 + survival/defect/replacement/cure events | “Installed or paid, therefore established” |
| Selective reopening set | changed proposition/fact → dependency traversal to decisions it can change | “Any new source/event reopens the whole case/model” |

No transitive-only answer above justifies a new fact-bearing relationship unless a real authority, party or physical process independently recognizes and preserves that relationship with its own facts.

## 9. Unsupported extras and redundancies

### Unsupported extras

- No accepted noun is unsupported by an operator proposition.
- No accepted family is unsupported after applying its admission rule.
- No accepted mandatory grain is extraneous.
- Events/outcomes, statuses, observations, overlays, cohorts, portfolios, source/provenance objects and transitive shortcuts remain correctly excluded as relationship families.
- Contextual direct links remain necessary but must not be promoted merely because traversal is convenient.

### Redundancy check

There is no removable duplication among the 13 nouns or seven families:

- Natural Person and Organization cannot merge without corrupting person-specific authority and institutional identity.
- Agricultural Holding and Cadastral Parcel cannot merge without losing administrative-unit versus legal-land continuity.
- Programme, Instrument and Proceeding are distinct enduring structure, operative authority and formal matter.
- Intervention cannot collapse into Proceeding because physical work survives applications, decisions, contractors and payment.
- F1/F2, F3/F7 and F5/F6 overlap in endpoints but own different independent facts; the explicit precedence rules above make them MECE.

The only apparent duplication is representational, not semantic: a creating instrument (F3), an assignment/right (F1/F2/F6/F7), and its creation/acceptance event may all refer to the same business episode. They must coexist because they answer different questions: **what governed**, **what durable fact resulted**, and **what happened when**.

## 10. Final verdict

**PASS-WITH-CORRECTIONS.**

The accepted 13 nouns are exhaustive and non-redundant for the bounded connected operating model. The seven semantic relationship families are also sufficient; no eighth family is warranted. The model covers all 52 tested operator propositions when consequential events/outcomes, contextual direct links and derived computations are used according to the accepted boundaries.

However, Gate 4 is not mechanically closed as written because two of its own mandatory anti-collapse grains are only partially assigned:

1. **G7 Public Proceeding scope** lacks explicit fact ownership for non-actor subject/scope facts — apply C1 inside F3.
2. **G11 Plant Trade Unit / Lot custody/allocation** lacks explicit fact ownership for actor–Lot custody outside Intervention use — apply C2 inside F1.

After those two narrow corrections, the inventory is MECE against the accepted six questions, five responsibilities, compulsory/voluntary routes, bounded establishment endpoint, event/outcome classes and selective-reopening rule. No noun addition, noun deletion, family addition or family deletion is justified.
# Gate 5 reconciled operator graph

Status: **GATE 5 ACCEPTED — complete semantic operator graph**
Date: 22 August 2026
Authority: `gate-5-core-ontology.md`, `gate-5-operator-reground.md`, the accepted six-question operating model

## Purpose

This file reconciles:

- `gate-5-minimum-operator-properties.md`;
- `gate-5-minimum-direct-link-graph.md`;
- `gate-5-operator-graph-adversarial-audit.md`;
- Owen's accepted Gate 5 corrections.

It defines one complete semantic operator graph before Gate 6 selects Foundry/AIP mechanisms.

Interactive representation: `cordon-operator-graph.html`.

## Reconciled result

The candidate contains:

- nine operator object types;
- two object-backed relationship types;
- 32 direct semantic link types;
- zero independent event object types;
- five typed local history contracts;
- four manager-owned Actions;
- four read-only Functions;
- no Interface.

The 19 load-bearing object/relationship/Action/Function elements are not the entire Ontology surface. Direct links are explicit Ontology semantics but do not create independently navigable fact objects.

## Nine operator object types

1. **Operator Party**
2. **Agricultural Holding**
3. **Cadastral Parcel**
4. **Official Area**
5. **Individual Plant** — extension-gated population
6. **Public Programme or Measure**
7. **Governing Instrument**
8. **Public Proceeding**
9. **Intervention**

## Two object-backed relationship types

### Cooperative Pursuit

Stable target for one cooperative pursue/defer/refuse decision before a Proceeding or Intervention necessarily exists.

Owns:

- member Party;
- cooperative Party;
- Programme;
- Holding and bounded Parcel scope;
- optional Intervention;
- mandate Instrument;
- exact decision authority;
- pursue/defer/refuse outcome;
- effective time;
- reason;
- individual fallback;
- reconsideration trigger;
- member-election and mandate references.

Does not own participation, eligibility, concession, capacity, filing, readiness or execution.

### Intervention Capacity Commitment

Stable, independently mutable allocation of cooperative-controlled scarce capacity to an Intervention.

Owns:

- capacity owner/controller Party;
- Intervention;
- capacity/resource description;
- committed extent;
- commitment interval;
- binding effect;
- protected commitment meaning;
- decision/override explanation;
- release or substitution condition;
- portfolio-decision reference.

Does not own availability, recommendation, eligibility, concession, dispatch authority or payment.

## Contextual authority rule

`Operator Party` owns identity only.

Contextual role, standing and authority facts live on the object that creates the context:

| Context owner | Contextual details |
|---|---|
| Member Party | cooperative membership |
| Agricultural Holding | stewardship and representation |
| Cadastral Parcel | tenure, consent and access standing |
| Governing Instrument | issuer, parties, mandate, duty, permission and authority |
| Public Proceeding | applicant, beneficiary, representative, deciding authority, creditor and formal roles |
| Intervention | manager, executor, technician, inspector, acceptor, warranty and aftercare roles |
| Cooperative Pursuit | member, cooperative, decision authority, route scope and fallback |
| Capacity Commitment | capacity owner/controller and decision basis |

Each contextual detail retains only:

- Party reference;
- role or standing kind;
- authority/basis reference;
- bounded scope;
- effective interval;
- consequential powers, duties or exclusions.

Direct Party links provide navigation. They never grant authority.

Relationship objects remain available. Add one when the manager must independently select, compare, mutate, reconcile or preserve history for the relationship, or when Gate 6 proves endpoint detail cannot represent it safely. Low type count is not a design goal.

## Minimum object properties

Property names are semantic contracts, not final API names or physical types.

### Operator Party

Stored:

- qualified party reference;
- operator title;
- party kind: natural person or organization;
- handoff contact reference where operationally needed.

Derived:

- current contextual roles and authority;
- scoped Actions the Party may take;
- Holdings, Parcels, Proceedings, Interventions, Pursuits and Commitments;
- current handoffs.

Prohibited:

- global member, beneficiary, authority, contractor, inspector, creditor or municipality-power flags.

### Agricultural Holding

Stored:

- qualified Holding reference;
- operator title;
- current scoped steward/representative details.

Derived:

- current Party and Parcel context;
- duties, opportunities, routes, Proceedings, Interventions and exposure.

### Cadastral Parcel

Stored:

- qualified cadastral reference;
- operator title;
- current Parcel geometry;
- current scoped Holding associations;
- current scoped Party tenure/consent/access details.

Derived:

- current administrative and regulatory Areas;
- proposition-specific applicability;
- current duties, permission, access consequence, Proceedings, Interventions and residual work;
- current identified Plants.

Geometry alone establishes no duty, permission, ownership or legal applicability.

### Official Area

Stored:

- qualified Area reference;
- official title;
- area kind;
- current geometry or territorial representation.

`areaKind` includes:

- EU, state, region, province and Comune administrative jurisdictions;
- infected, containment, buffer, additional delimited and other official operational areas.

Derived:

- defining Instruments and competent Parties;
- intersecting land and identified Plants;
- proposition-specific current legal consequence.

A governmental Party and territorial Area are different objects. Jurisdiction does not grant competence.

### Individual Plant

Stored only when identity is externally preserved or established by a validated reproducible observation-derived inventory:

- qualified Plant reference;
- operator title;
- current Plant location.

Derived:

- parent Parcel and current Areas;
- official condition and legal target;
- Intervention phase involvement;
- separate acceptance, establishment, defect, replacement and cure results.

Arbitrary detections create no Plants.

### Public Programme or Measure

Stored:

- qualified Programme reference;
- official title;
- Programme kind.

Derived:

- current openings and operative Instruments;
- complete in-scope population;
- deadlines and permitted claim paths;
- participation, Pursuit, public outcomes, Commitments and fallback.

No Programme-level eligibility, concession, budget-availability or completion status is stored.

### Governing Instrument

Stored:

- qualified Instrument reference;
- official title;
- Instrument kind;
- operative interval;
- bounded operative effect;
- current scoped party/authority details.

Derived:

- whether the Instrument controls a proposition for a selected subject, place and date;
- current duties, permissions, clocks, conflicts and affected work.

The full legal corpus, clauses, citation graph, OCR and acquisition history remain backstage.

### Public Proceeding

Stored:

- qualified Proceeding reference;
- operator title;
- Proceeding kind;
- bounded matter scope;
- current scoped Party roles/authority.

Derived:

- latest effective filing;
- current authoritative outcome;
- active clock and cure owner;
- amounts at each independent financial stage;
- remaining right, cash and recovery exposure.

No generic Proceeding status or single current amount is stored.

### Intervention

Stored:

- qualified Intervention reference;
- operator title;
- Intervention kind;
- bounded intended scope;
- bounded Wedge 1 endpoint;
- current scoped Party roles/authority.

Derived:

- member route and Pursuit;
- design, authorization, access and permits;
- capacity and finance premises;
- named-action readiness;
- dispatched, performed, accepted, defective, established, cured and residual scopes;
- remaining exposure.

No global completion status is stored.

## Five typed local history contracts

The initial core uses:

1. `instrumentHistory` on Governing Instrument;
2. `proceedingHistory` on Public Proceeding;
3. `interventionHistory` on Intervention;
4. `pursuitHistory` on Cooperative Pursuit;
5. `commitmentHistory` on Intervention Capacity Commitment.

The final two are added by reconciliation so each independently mutable relationship owns its own history rather than duplicating relationship decisions on Interventions.

### Factual history envelope

Every history detail stores only:

1. occurrence reference;
2. occurrence kind;
3. actor;
4. authority or basis reference;
5. consequential time;
6. bounded scope;
7. outcome;
8. optional actor-supplied explanation;
9. minimum evidence references.

Do not store:

- changed decisions;
- reopening effect;
- next owner;
- next Action;
- next clock consequence.

The four Functions derive those answers from the factual occurrence and current graph.

### Instrument history variants

- notice or service;
- legally consequential publication;
- amendment;
- stay or derogation;
- supersession or termination.

### Proceeding history variants

- filing version;
- authority outcome;
- financial instruction or admission;
- liquidation or payment order;
- cash transaction;
- audit, revocation or recovery.

### Intervention history variants

- dispatch;
- performance;
- inspection;
- acceptance;
- defect or deviation;
- establishment review;
- replacement or cure.

### Pursuit history variants

- pursue;
- defer;
- refuse;
- reconsider or supersede prior pursuit decision.

### Commitment history variants

- create commitment;
- change firmness, extent or interval;
- release;
- reallocate;
- substitute;
- override under authorized policy.

A portfolio decision reference binds all Commitments changed by one atomic Action without copying the decision into every Intervention history.

## Thirty-two direct semantic links

Each link states current semantic adjacency only. Contextual facts remain on the owner above.

### Member, Holding, Parcel and Plant

1. Party **is member of cooperative** Party.
2. Party **operates or represents** Holding.
3. Holding **operates** Parcel.
4. Party **has standing on** Parcel.
5. Parcel **contains identified** Plant.

### Area and jurisdiction

6. Area **has parent Area**.
7. Governmental Party **has jurisdiction Area**.

The jurisdiction link does not grant powers.

### Governing Instruments

8. Instrument **has Instrument Party**.
9. Instrument **defines or governs Area**.
10. Instrument **governs Programme**.
11. Instrument **provides basis for Proceeding**.
12. Instrument **provides basis for Intervention**.
13. Instrument **changes Instrument**.

The history detail states amendment, stay, supersession or termination semantics.

### Programmes and Proceedings

14. Programme **has Proceeding**.
15. Proceeding **follows or affects Proceeding**.
16. Proceeding **involves Party**.
17. Proceeding **concerns Holding**.
18. Proceeding **concerns Parcel**.
19. Proceeding **concerns identified Plant** — conditional.
20. Proceeding **concerns Intervention**.

### Interventions

21. Intervention **has Intervention Party**.
22. Intervention **scopes Parcel**.
23. Intervention **scopes identified Plant** — conditional.

### Cooperative Pursuit

24. Pursuit **has member Party**.
25. Pursuit **has cooperative Party**.
26. Pursuit **is under Programme**.
27. Pursuit **concerns Holding**.
28. Pursuit **concerns Parcel**.
29. Pursuit **has optional Intervention**.
30. Pursuit **is based on mandate Instrument**.

There is no direct Programme–Intervention pursuit link. Traverse through Cooperative Pursuit.

### Capacity Commitment

31. Commitment **has capacity owner Party**.
32. Commitment **commits capacity to Intervention**.

## Link multiplicities

Constrain only accepted decision-grain singularity:

- one identified Plant has one current Parcel; one Parcel may contain many Plants;
- each Pursuit requires one member Party, one cooperative Party and one Programme;
- each Commitment requires one owner/controller Party and one Intervention.

Pursuit may concern multiple Holdings, Parcels, optional Interventions and basis Instruments. Every other link remains many-to-many until Gate 6 proves and can enforce a narrower invariant.

## Derived traversals, not additional links

Do not store direct shortcuts for:

- Parcel → currently applicable Areas;
- Holding or Plant → current Areas;
- Programme → governing Areas;
- Instrument → affected Parcels or Plants;
- Holding → Interventions;
- Party → Interventions for operated land;
- Party → Programme routes and public rights;
- Party → capacity-committed Interventions;
- Intervention → capacity providers;
- Proceeding → downstream claim, field or aftercare effects;
- any eligible, selected, ready, blocked, accepted, paid or complete relationship.

These are traversals or live Function outputs.

## Conditional extensions

### Intervention Plant Scope

Do not add initially. Use direct Intervention–Plant links plus typed phase histories.

Reopen only if Gate 6 proves the history mechanism cannot retain stable Plant references, query one Plant across phases, distinguish prior/current phase scope, mutate/reverse one phase atomically or support AIP readiness and remaining-exposure reasoning.

### Focused cash occurrence

Do not add initially. Proceeding history must preserve stable transaction identity, partials, returns, reversals and exact order/right allocation.

Reopen only if a transaction must be independently selected, linked across several Proceedings or acted on and Gate 6 proves Proceeding history cannot represent it safely.

### Lot and Lot relationships

Do not add initially. Reopen only for a real operator Lot allocation, dispatch, substitution, warranty or return decision that Intervention material history cannot preserve.

## Four manager-owned Actions

### Accept Cooperative Execution Mandate

Decision owner: cooperative role with exact governance and mandate-acceptance authority.

Target: member-granted mandate Governing Instrument.

Inputs:

- member and cooperative Parties;
- member participation result;
- real member-granted mandate;
- Holding/Parcel/Intervention scope;
- powers, duties, exclusions and term;
- existing member-side work and fallback.

Atomic effects:

- append cooperative acceptance or refusal to Instrument history;
- activate only the accepted cooperative-side contextual authority;
- preserve refused/unaccepted scope and individual fallback.

Refuse when cooperative authority, member grant, scope, term, conflicts or fallback consequence is unresolved. Never create the member grant, public eligibility, concession, capacity or creditor identity.

### Decide Cooperative Pursuit

Decision owner: cooperative role with exact collective-pursuit authority.

Target: Cooperative Pursuit.

Inputs:

- member participation;
- accepted mandate;
- Programme collective rules;
- eligibility indication or uncertainty;
- bounded Holding/Parcel/optional Intervention scope;
- conflicts, readiness, deadline and fallback.

Atomic effects:

- set pursue, defer or refuse for the bounded route;
- append Pursuit history with reason and effective time;
- preserve individual fallback and reconsideration trigger.

Refuse when authority, member choice, mandate, Programme route, scope or fallback is unresolved. Never create eligibility, concession, capacity, filing or execution truth.

### Commit or Rebalance Intervention Capacity

Decision owner: cooperative role with exact allocation authority under operative policy.

Targets: complete affected set of Intervention Capacity Commitments.

Inputs:

- affected Intervention population;
- feasible recommendation and alternatives;
- current Commitments and available capacity;
- proposed creates, changes, releases and reallocations;
- non-discretionary constraints;
- approved fairness safeguards;
- protected Commitments;
- override authority and reason.

Atomic effects:

- create/change/release/reallocate Commitments as one portfolio transaction;
- append each Commitment's factual history;
- bind changes with one portfolio-decision reference;
- preserve deferred routes and fallback.

Refuse incomplete population, insufficient authority, infeasible resource use, violated constraints/safeguards, omitted protected Commitments, incomplete atomic edit set or unauthorized/unexplained override. Never alter eligibility, concession, duty, fallback or dispatch authority.

### Dispatch Intervention

Decision owner: Party holding exact management/dispatch authority for the Intervention route.

Target: Intervention.

Inputs:

- bounded Parcel/conditional Plant scope;
- dispatcher and executor authority;
- certified technical design;
- required public/contractual authorization;
- access standing;
- permits and conditional decisions;
- real Capacity Commitments and other resource commitments;
- finance/evidence conditions;
- compatible clocks;
- named-action readiness result.

Atomic effects:

- append bounded dispatch history;
- identify authorized and excluded scope, executor, work clock and stop/return conditions;
- create/activate a work-order Instrument only when the real process preserves one.

Refuse missing or indeterminate authority, target, design, access, permit, resources, finance, clock compatibility or evidence plan. Dispatch never proves movement, performance, acceptance or establishment.

AIP may prepare, route and record outcomes for non-manager actors. Exact non-manager Actions reopen only when those actors genuinely transact through CORDON.

## Four read-only Functions

### Determine Affected Decisions

Input: one material changed fact or factual history detail plus the current graph.

Returns:

- affected decisions and Actions;
- reason/dependency path;
- proposition-specific indeterminacy;
- scoped hold/reopening;
- current next decision owner;
- explicitly unaffected work.

It never corrects the premise, reopens work itself, writes status or takes a reserved decision.

### Assess Named-Action Readiness

Input: one named Action, exact target/scope/actor/time and that Action's typed prerequisite profile.

Returns:

- ready, not ready or materially indeterminate;
- satisfied conditions;
- blockers and their real cure owners;
- consequence of acting or waiting;
- scope that may continue.

It never creates authority or a global route-ready state. Action submission criteria enforce final refusal.

### Compare Feasible Intervention Portfolios

Input: complete affected Intervention population, current Commitments, available capacities, operative constraints, approved fairness safeguards, member fallback paths, expected incremental realized Xylella-loss reduction and uncertainty.

Returns:

- highest-objective feasible portfolio;
- materially equivalent alternatives;
- binding constraints and infeasible alternatives;
- included/deferred Interventions and fallback consequences;
- capacity/schedule consequences;
- uncertainty, sensitivity and tie-break use.

It recommends only. It never selects authoritatively or creates Commitments.

### Determine Remaining Exposure

Input: bounded member/Holding/Parcel/Intervention context and current legal, operational, financial and biological histories.

Returns independent lines for:

- legal completion, residual duty, enforcement and remedy;
- dispatch, performance, acceptance, defect and residual physical scope;
- entitlement, claim, admission, liquidation, order, cash and audit/recovery;
- establishment, defect, replacement, cure and unresolved biological scope;
- current next owner, clock and indeterminate premise for every open line.

It never creates a global completion state, infers cash from an order, infers establishment from installation acceptance, reopens work or extends into productive maturity.

## Coverage of the six questions

### 1. What changed, and what does it affect?

Factual histories and the direct graph feed Determine Affected Decisions. The Function derives affected and explicitly unaffected decisions; history does not store workflow consequences.

### 2. What is required, allowed or blocked?

Instrument, Area, Parcel, contextual authority and Proceeding outcomes feed proposition/date/scope-specific applicability and named-action readiness. Geometry alone is never law.

### 3. Who chooses, who decides and which route continues?

Context-owned Party authority, Cooperative Pursuit and Capacity Commitment keep member election, mandate, pursuit, public outcome and cooperative capacity separate.

### 4. Is the route ready for the named Action?

Assess Named-Action Readiness traverses exact authority, target, basis, scope, access, design, permit, capacity, finance, clock and evidence premises. No generic readiness property exists.

### 5. What was done, and who accepted it?

Intervention history keeps dispatch, performance, inspection and each acceptance basis independently attributable and scoped.

### 6. Did the intended result land, and what remains open?

Proceeding financial history and Intervention acceptance/establishment/cure history feed Determine Remaining Exposure. Legal, operational, financial and biological result lines remain independent.

## Gate 6 dependencies

Gate 6 must prove:

- safe representation of contextual Party references and authority details;
- stable, queryable, appendable and reversible typed histories;
- atomic multi-Commitment portfolio Actions;
- bounded AIP tools and human-review behavior;
- proposal/routing and received-outcome ingestion for non-manager actors;
- Plant-phase history capability;
- cash transaction partial/reversal capability;
- derived applicability, affected-decision, readiness, portfolio and exposure performance.

A measured failure can selectively reopen a hidden technical backing resource, focused relationship object or focused event type. It does not reopen the normalized 39+10 model.

### Gate 6 accepted physical reopening

Foundry mechanics require six hidden occurrence types: Instrument Occurrence, Proceeding Occurrence, Intervention Occurrence, Pursuit Decision Record, Commitment Change Record and Cash Occurrence. Hidden Intervention Plant Scope owns phase-specific Plant truth. These resources implement the accepted history/Plant semantics and do not change the visible operator graph.

Foundry mechanics also require six focused hidden contextual relationship types: Cooperative Membership, Holding Party Assignment, Parcel Standing, Instrument Party Assignment, Proceeding Party Assignment and Intervention Party Assignment. They implement scoped role/authority metadata behind the accepted direct Party links. Cooperative Pursuit and Capacity Commitment already own their Party context.

Capacity allocation uses Ontology Scenarios for alternatives, a hidden Capacity Portfolio Proposal for the selected complete plan and current-state fingerprint, and one TypeScript v2 staged-write Action invoked by the authenticated manager's explicit conversational command. The proposal is a technical decision package, not an approval queue or domain decision owner.

The accepted 32 semantic links map physically to six required FK links, six object-backed contextual links and twenty metadata-free M:M join-table links. Object-backed traversals replace—not duplicate—the corresponding direct Party joins.

## Verdict

The reconciled graph preserves the 41 operator decisions and 30 capabilities with 19 load-bearing object/relationship/Action/Function elements, 32 direct semantic links and five factual history contracts.

It balances Palantir's domain-driven and object-backed-link guidance with its decision-first, intentional-curation, DRY, right-tool and pragmatic-extension guidance. The graph is compact at the operator level without prohibiting relationship objects or hiding scoped authority in Operator Party.

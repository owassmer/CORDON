# Gate 5 minimal core Ontology

Status: **GATE 5 ACCEPTED — minimal operator Ontology fixed**
Date: 22 August 2026
Owner: Connor specification; Owen executive acceptance
Process authority: `REDESIGN_SEQUENCE.md`
Current reground: `research/workflow-redesign/gate-5-operator-reground.md`

## Objective

Derive the smallest Palantir Ontology that lets the cooperative or OP operations manager answer the six accepted questions, take or supervise authorized CORDON Actions, understand consequences and selectively reopen affected work across Land, Funding, Applications, Field Work and Payments.

The core is not a complete digital representation of every fact in the operating model.

## Current authority

## Accepted operator-centered software decisions

### Nine operator object types

1. **Operator Party** — person or organization identity used for actor, authority, handoff and Action resolution.
2. **Agricultural Holding** — persistent farm administrative/operating unit across actor and Parcel change.
3. **Cadastral Parcel** — legally referenced land unit for duty, access, filing, dispatch, execution and residual work.
4. **Official Area** — authority-preserved administrative jurisdiction or regulatory/plant-health area identity; geometry is its map representation and Governing Instruments define/change it.
5. **Individual Plant** — conditional population for stable tree identity across official condition, target, execution, inspection, survival, defect, replacement and cure.
6. **Public Programme or Measure** — enduring opportunity/support route across openings, Instruments, Proceedings, claims and fallback.
7. **Governing Instrument** — operative legal, administrative, contractual or financial basis, authority, interval, clock and change lineage.
8. **Public Proceeding** — one formal matter across filings, repair, authority outcomes, appeal, audit, recovery and next-owner handoff.
9. **Intervention** — one bounded physical undertaking across design, capacity, dispatch, performance, acceptance, payment, aftercare, replacement and cure.

`Individual Plant` instances require external identity preservation or a validated reproducible observation-derived inventory. Arbitrary detections create no Plants.

Do not add Plant Trade Unit/Lot, Organism Taxon/Lineage or Cultivar as initial core objects. Lot selectively reopens on a proven operator allocation/dispatch workflow. Taxon/lineage and Cultivar remain controlled identifiers and backstage reference data unless a later operator deletion failure proves typehood.

`Official Area.areaKind` distinguishes administrative jurisdictions (EU, state, region, province, Comune) from regulatory/plant-health areas (infected, containment, buffer, additional delimited or another officially defined operational geography). Both share authoritative identity, title, spatial representation, parent-area hierarchy, effective definition, Instrument basis and map/legal traversal.

A governmental `Operator Party` and its territorial `Official Area` are separate objects. They may share a qualified external reference. A Party–Area jurisdiction connection never grants publication, permit, enforcement, asset, programme or phytosanitary competence; exact powers remain grounded in Governing Instruments and Proceedings.

### Operator Party

Use one focused `Operator Party` object for Natural Person and Organization in the operator core.

- `partyKind` preserves `naturalPerson` versus `organization`.
- Preserve only common operator identity, qualified legal identifiers, display/contact references and links needed to resolve authority, role, handoff and Actions.
- Agricultural Holding remains a separate object.
- Member, beneficiary, cooperative, authority, CAA, contractor, technician, inspector, creditor and other roles remain contextual properties/links, not Party subtypes.
- Person- or Organization-specific detail that the manager does not need remains backstage or in later extension types.
- Reopen separate Person/Organization types only if operator-required properties, Actions or access meaning materially diverge and cannot be represented safely through `partyKind` and qualified properties.

Deletion failure: without Operator Party, the manager cannot identify the exact member, beneficiary, representative, cooperative, authority, contractor or next owner; resolve who may choose/act; or route a cure/handoff without unsafe labels.

### Contextual roles, authority and relationship-object balance

`Operator Party` owns identity only. Contextual role, standing and authority facts live on the object that creates the context:

- member Party: current cooperative-membership detail;
- Agricultural Holding: steward and representative detail;
- Cadastral Parcel: tenure, consent and access-standing detail;
- Governing Instrument: issuer, parties, mandate, duty, permission and authority detail;
- Public Proceeding: applicant, beneficiary, representative, deciding authority, creditor and formal-role detail;
- Intervention: manager, executor, technician, inspector, acceptor, warranty and aftercare detail;
- Cooperative Pursuit: member, cooperative, decision authority, scope and fallback;
- Intervention Capacity Commitment: capacity owner/controller and decision basis.

Each retained contextual detail identifies the Party, role/standing kind, authority or basis, bounded scope, effective interval and only the consequential powers, duties or exclusions. Direct Party links provide navigation and never grant authority.

This rule does not prohibit relationship objects. Use an object-backed relationship when the manager must independently select, compare, mutate, reconcile or preserve history for that relationship, or when Gate 6 proves contextual endpoint detail cannot represent it safely. `Cooperative Pursuit` and `Intervention Capacity Commitment` pass that test. Type-count reduction alone is not a reason to reject a relationship object.

Gate 6 selects structured properties, hidden technical backing resources or another supported mechanism for contextual detail. A technical backing resource does not automatically become an operator-visible core type.

### Thirty-two direct semantic links

Direct links provide navigation only; contextual facts remain on their accepted owner.

**Member, Holding, Parcel and Plant**

1. Party is member of cooperative Party.
2. Party operates or represents Holding.
3. Holding operates Parcel.
4. Party has standing on Parcel.
5. Parcel contains identified Plant.

**Area and jurisdiction**

6. Area has parent Area.
7. Governmental Party has jurisdiction Area.

**Governing Instruments**

8. Instrument has Instrument Party.
9. Instrument defines or governs Area.
10. Instrument governs Programme.
11. Instrument provides basis for Proceeding.
12. Instrument provides basis for Intervention.
13. Instrument changes Instrument.

**Programmes and Proceedings**

14. Programme has Proceeding.
15. Proceeding follows or affects Proceeding.
16. Proceeding involves Party.
17. Proceeding concerns Holding.
18. Proceeding concerns Parcel.
19. Proceeding concerns identified Plant, conditionally.
20. Proceeding concerns Intervention.

**Interventions**

21. Intervention has Intervention Party.
22. Intervention scopes Parcel.
23. Intervention scopes identified Plant, conditionally.

**Cooperative Pursuit**

24. Pursuit has member Party.
25. Pursuit has cooperative Party.
26. Pursuit is under Programme.
27. Pursuit concerns Holding.
28. Pursuit concerns Parcel.
29. Pursuit has optional Intervention.
30. Pursuit is based on mandate Instrument.

**Capacity Commitment**

31. Commitment has capacity owner Party.
32. Commitment commits capacity to Intervention.

Do not add direct shortcuts for current applicability, affected land/Plants, Party Programme routes/rights, Holding Interventions, capacity-backed Party–Intervention traversal, downstream Proceeding effects or any eligible/selected/ready/blocked/accepted/paid/complete relation. Derive them through the graph or core Functions.

Gate 6 may use direct links, contextual structured references or hidden backing resources to implement this graph. It may not change the semantic meaning or promote a traversal into authority. A measured mechanism failure selectively reopens the affected representation only.

### Link multiplicity policy

Constrain only multiplicities that belong to the accepted decision grain:

- one identified Plant has one current Cadastral Parcel; one Parcel may contain many Plants;
- one Cooperative Pursuit requires exactly one member Party, one cooperative Party and one Public Programme or Measure; each endpoint may participate in many Pursuits;
- one Intervention Capacity Commitment requires exactly one capacity owner/controller Party and one Intervention; each endpoint may participate in many Commitments.

Pursuit may concern one or more Holdings, one or more Parcels, zero or more Interventions and one or more mandate/basis Instruments.

All other direct links remain semantically many-to-many. Gate 6 may tighten a multiplicity only when authoritative current evidence and the write model prove and enforce the narrower invariant. Do not fabricate exclusivity for Holding/Parcel operation, representation, Instrument basis, Proceedings, Areas or Intervention actors/scope.

### Minimum semantic property contract

Store only identity and facts owned by the object. Derive current workflow answers from links, factual histories and core Functions. Keep raw legal, scientific, source, financial and evidence detail backstage.

All applicable objects retain a qualified reference, human-readable operator title and narrow kind discriminator only where kind changes interpretation.

- **Operator Party:** party kind and operational handoff contact reference; identity only.
- **Agricultural Holding:** current scoped steward/representative details.
- **Cadastral Parcel:** current geometry, scoped Holding associations and scoped Party tenure/consent/access details.
- **Official Area:** area kind and current authoritative geometry or territorial representation.
- **Individual Plant:** current stable location; instances remain identity-gated.
- **Public Programme or Measure:** Programme kind; openings, eligibility, budget, concession and claim paths remain derived.
- **Governing Instrument:** Instrument kind, operative interval, bounded operative effects and scoped parties/authority.
- **Public Proceeding:** Proceeding kind, bounded matter scope and scoped Party roles/decision authority.
- **Intervention:** Intervention kind, bounded intended scope, bounded Wedge 1 endpoint and scoped parties/authority.
- **Cooperative Pursuit:** pursue/defer/refuse outcome, route scope, authority, effective time, reason, fallback, reconsideration trigger and member-election/mandate references.
- **Intervention Capacity Commitment:** capacity description, committed extent, interval, binding effect, decision explanation, release/substitution condition and portfolio-decision reference.

Do not store generic status, stage, ready, complete, open/closed, priority, score, owner, assignee, task, exception, notes, attachments, last-updated, source or timeline properties. Do not copy Party role/authority, Parcel applicability/duty/permission, Proceeding financial stage, Intervention execution/acceptance/establishment or Capacity recommendation/score onto objects.

The detailed semantic property and history contract is `gate-5-reconciled-operator-graph.md`. Gate 6 chooses physical property types, structs, reducers, derived-property mechanisms, hidden backing resources and performance tradeoffs.

### Consequential history

Use no independent event object types in the initial operator core.

- Governing Instrument carries typed notice, publication, amendment, stay and supersession history details.
- Public Proceeding carries typed filing-version and authority-outcome history details, including financial instruction/order/settlement/audit/recovery where that Proceeding owns the operator thread.
- Intervention carries typed execution, inspection, acceptance, defect, establishment, replacement and cure history details.
- Cooperative Pursuit carries pursue, defer, refuse and reconsider/supersede history details.
- Intervention Capacity Commitment carries create, change, release, reallocate, substitute and authorized-override history details.
- Every detail preserves nine factual fields where applicable: occurrence reference, kind, actor, authority/basis reference, consequential time, bounded scope, outcome, optional supplied explanation and minimum evidence references.
- The manager navigates history from the owning Instrument, Proceeding, Intervention, Pursuit or Commitment rather than separate event populations.

Do not store changed decisions, reopening effect, next owner, next Action or clock consequence on history details. Those are live outputs of `Determine Affected Decisions`, `Assess Named-Action Readiness` and `Determine Remaining Exposure`. If an external occurrence explicitly names a recipient, actor or deadline, preserve it inside the bounded outcome rather than translating it into CORDON workflow state.

Gate 6 selects the storage mechanism. Struct arrays, linked hidden history resources, time-series properties, source-backed records or another supported mechanism do not change the core semantic decision.

Selectively reopen a focused event type only when the manager must independently select the same occurrence, link it across multiple core objects, run an Action against it, compare it across parents, or preserve partial/reversal structure that the history representation cannot model safely.

Each independently mutable relationship owns its own history. Do not copy Pursuit or Commitment decisions into Intervention history. One `portfolioDecisionReference` may bind several Commitment changes made atomically. Palantir Action logs may supplement audit but do not replace the relationship's semantic history.

**Gate 6 physical ruling:** Foundry struct-array mechanics do not safely preserve the accepted typed references, append/reversal behavior and independent occurrence identity. Implement the five accepted parent histories as hidden Instrument Occurrence, Proceeding Occurrence, Intervention Occurrence, Pursuit Decision Record and Commitment Change Record types. Add focused hidden Cash Occurrence for authenticated transaction/reversal truth. Implement contextual authority through six focused hidden object-backed relationships: Cooperative Membership, Holding Party Assignment, Parcel Standing, Instrument Party Assignment, Proceeding Party Assignment and Intervention Party Assignment. These physical resources preserve the Gate 5 contracts and remain hidden from the operator core.

### Decide Cooperative Pursuit

Add one narrow object-backed relationship, `Cooperative Pursuit`, as the stable fact owner and Action target for the cooperative decision to pursue, defer or refuse collective coordination of one bounded member route.

- Endpoints/scope: member Operator Party, cooperative Operator Party, Public Programme or Measure, Agricultural Holding, bounded Cadastral Parcels, optional Intervention after one exists, and mandate Governing Instrument.
- Owned facts: pursue/defer/refuse outcome, bounded route scope, exact cooperative decision authority, reason, effective time, individual fallback, reconsideration trigger, member-election reference and mandate reference.
- Excluded facts: member participation, public eligibility, concession, capacity, filing, readiness and execution remain separately owned.

- Decision owner: the cooperative role with exact governance authority; the operations manager can execute only when holding that authority.
- Inputs: member participation, accepted mandate/scope, Programme collective rules, eligibility indication/uncertainty, proposed member/Holding/Parcel/Intervention scope, conflicts, preparation/readiness, individual fallback, deadline and reconsideration triggers.
- Effects: collective pursue/defer/refuse decision, bounded scope, reason, preparation route opened/held, fallback preserved and reconsideration trigger.
- Refuse when authority, member choice, mandate, route/scope or fallback consequence is unresolved.
- Never grant eligibility, concede aid, commit capacity, release a filing or extinguish the individual route.

Deletion failure: without this Action, collective pursuit is inferred from participation, mandate, preparation or later capacity, collapsing four independent decisions and making fallback unsafe.

Do not replace `Cooperative Pursuit` with a Programme–Intervention link. Pursuit can exist before either a Public Proceeding or Intervention and needs independently mutable scope, fallback and reconsideration facts. Storing it on Party, Programme or Intervention creates contextual multi-value state or turns the physical undertaking into a route object.

### Initial AIP Action harness

Expose only four manager-owned mutating Actions in the initial core:

1. Accept Cooperative Execution Mandate
2. Decide Cooperative Pursuit
3. Commit or Rebalance Intervention Capacity
4. Dispatch Intervention

Each Action requires exact cooperative/dispatch authority and may default to staged human review.

For member, technician, beneficiary, executor and private-acceptor decisions, AIP may:

- prepare/stage the decision package;
- identify and route to the real decision owner;
- preserve the received bounded outcome and recompute affected work.

Those are harness capabilities, not the reserved domain decision. Gate 6 selects application state, proposal, notification, Action or integration mechanics.

Selectively reopen an exact non-manager mutating Action only when the real actor actually transacts through CORDON and the contract preserves actor, authority, target, scope, refusal conditions, atomic effect and human review. Public-authority decisions remain external outcomes unless the competent authority itself uses CORDON.

Reject one generic Execute CORDON Action tool. AIP receives exact bounded tools only.

### Determine Remaining Exposure

Add one read-only Function that answers Question 6 across independent legal, operational, financial and biological result lines for a bounded member/Holding/Parcel/Intervention context.

- Legal output: completed duty, residual duty, enforcement or remedy.
- Operational output: dispatched, performed, independently accepted, defective and residual scope.
- Financial output: entitlement, claim, admitted amount, liquidation, payment order, cash settlement and audit/recovery exposure kept distinct.
- Biological output: established, defective, replaced, cured and unresolved scope.
- Every open line returns its next owner, consequential clock and materially indeterminate premise.
- Explicitly complete lines never close unrelated lines.

The Function does not mutate facts, reopen work, create a global completion state, infer cash from an order, infer establishment from installation acceptance or extend into productive maturity. `Determine Affected Decisions` remains the separate change-impact and selective-reopening Function.

Do not store `remainingExposure` as a copied property. The answer depends on linked, repeatable and reversible Proceeding and Intervention histories and must remain live.

### Conditional Intervention Plant Scope

The initial core uses a direct `Intervention scopes identified Plant` link plus repeatable Intervention history details whose bounded scope names the exact Plants and phase.

Dispatch, performance, inspection, acceptance, establishment, replacement and cure details preserve explicit cross-references. A bare current Plant status or unqualified Intervention–Plant link never supplies phase truth by itself.

Gate 6 proves the selected history mechanism needs typed phase-specific Plant references. Implement hidden `Intervention Plant Scope` records linked to the exact Intervention occurrence and Plants. The direct Intervention–Plant link remains concise adjacency; the hidden relationship owns phase truth.

### Accepted domain model

- Six recurring operator questions.
- Five connected operating responsibilities.
- Thirteen real-world nouns.
- Nine fact-bearing relationship families.
- Sixteen atomic anti-collapse predicates.
- Compulsory and voluntary route independence.
- Funded and self-funded recovery.
- Proposition-specific authority.
- Named-action readiness.
- Public accounting versus cash settlement.
- Installation acceptance versus bounded biological establishment.

The nouns, families and predicates define the complete candidate universe and semantic tests. They do not automatically become Ontology types.

### Current Palantir grounding

`palantir-ontology-current-grounding.md` is the documentation authority for Gate 5 design guidance.

Apply:

- model reality, not source schemas;
- keep object types focused;
- store each fact once;
- use meaningful links;
- use object-backed links only when relationship facts must be independently owned by the operator model;
- make Actions cohesive business operations;
- use Functions for live cross-object logic, not stable or population-scale transformations;
- introduce Interfaces only for a proven polymorphic operator capability;
- reject System Silos, Kitchen Sink, Department Silos, God Object, Golden Hammer, Action Sprawl, Time Machine and Misnomer patterns.

## Correction

The previous Gate 5 test admitted a type whenever deleting it erased a decision-relevant domain fact. That produced a 39-type fixed relationship proposal plus a 20-cell Proceeding-scope matrix. A subsequent audit recommended ten Proceeding-scope types, yielding 49 relationship-backing candidates before properties.

That design is rejected as the core Ontology. It normalized the full domain rather than minimizing software around the cooperative manager.

All prior Gate 5 object, event, relationship, Action, Function and Interface selections are reopened. Their evidence and boundary analysis remain reusable.

## Binding admission rule

A core element survives only when deleting it prevents the cooperative manager from:

1. answering one of the six operator questions;
2. taking or supervising an authorized CORDON Action;
3. understanding the bounded consequence and next owner;
4. distinguishing a materially different route, authority, clock, commitment, acceptance, settlement or establishment result; or
5. selectively reopening affected work while preserving unaffected work;

and no simpler object, property, direct link, event detail, derived result or backstage evidence can preserve that capability.

Every retained type must name the exact operator capability lost on deletion.

## Operator and authority boundary

The primary user is the cooperative/OP operations manager.

CORDON can detect, reconcile, calculate, prepare, recommend, stage and execute only within real authority. It does not manufacture member, professional, cooperative, contractual or public decisions.

A CORDON Action belongs in the core only when the manager, another authorized CORDON actor or the bounded AIP harness can legitimately execute or stage it. External public decisions that CORDON merely receives remain outcomes.

## AIP harness boundary

AIP is later platform work, but Gate 5 must produce bounded Action contracts suitable for a harness:

- exact authority;
- typed target and scope;
- refusal conditions;
- atomic effects;
- no generic status or workflow mutation;
- human review where the decision owner requires it.

Gate 5 does not select AIP implementation, model, prompt, agent, automation or surface.

## Non-binding later-surface compatibility

The rough Land-surface context includes a map/tree view, disease/zoning/order visibility, jurisdictional legal matrix and an AIP panel capable of invoking authorized CORDON Actions.

Gate 5 uses this only to test that:

- legal applicability is compactly traversable by jurisdiction, land and proposition;
- disease/zone/tree state is map-addressable;
- operator Actions are bounded and explainable;
- domain detail does not force a legal administration console.

No interface, map behavior, panel or navigation is accepted. Gate 7 remains closed.

## Ordered Gate 5 work

1. Build the cooperative-manager decision ledger across six questions and five responsibilities.
2. Derive the minimum operator-visible object graph from those decisions.
3. Derive the minimum operator/AIP Action harness.
4. Add only the event/history identity the manager must independently revisit.
5. Add Functions only for irreducible live reasoning.
6. Test map/legal/disease/tree addressability without designing a surface.
7. Verify every retained element against operator decision loss and the loss-reduction telos.
8. Present one complete core Ontology for acceptance.

## Candidate evidence, not authority

These remain useful upper-bound and anti-collapse records:

- `gate-5-object-event-admission.md`;
- `gate-5-relationship-representation-ledger.md`;
- `gate-5-relationship-compression-a.md`;
- `gate-5-relationship-compression-b.md`;
- `gate-5-relationship-compression-adversarial.md`;
- `gate-5-exact-relationship-inventory.md`;
- `gate-5-proceeding-scope-minimum.md`;
- `gate-5-kinetic-interface-candidates.md`;
- `gate-5-integrated-candidate-synthesis.md`.

They cannot be copied into the core without passing the operator admission rule.

## Mandatory negative constraints

Do not:

- revive legacy Wedge 1 Ontology, product, specs, interface or Foundry state;
- convert all 13 nouns into types by default;
- convert nine families or 16 predicates into implementation types;
- preserve domain facts solely because another actor or source maintains them;
- create generic Case, Event, Evidence, Status, Task, Queue, WorkItem, Source, dossier, bundle or global timeline objects;
- use the rough map/AIP idea as surface authority;
- select Foundry/AIP architecture, pipelines, applications or deployment before their gates;
- write to Foundry.

## Current posture

Gate 5 is complete and accepted. `gate-5-reconciled-operator-graph.md` is the complete semantic design. The interactive artifact `cordon-operator-graph.html` is built and exercised. Gate 6 Foundry/AIP capability mapping is open. Gate 7 remains closed.

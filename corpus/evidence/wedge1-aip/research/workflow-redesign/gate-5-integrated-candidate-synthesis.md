# Gate 5 integrated candidate synthesis

Status: **PRE-CORRECTION SYNTHESIS — upper-bound candidate evidence; software selections reopened**
Date: 22 August 2026

## Purpose

This document connects the three independent Gate 5 derivation lanes into one intuitive candidate system:

1. object and concrete-event admission;
2. direct versus object-backed relationship representation;
3. Actions, Functions and Interfaces.

It does not select properties, physical keys, cardinalities, source mappings, security, pipelines, applications, surface architecture or implementation.

## One connected picture

The candidate Ontology has four semantic/kinetic layers:

```text
ENDURING WORLD
people · organizations · holdings · parcels · official areas · plants · lots
organisms · cultivars · programmes · instruments · proceedings · interventions

        linked through exact, fact-owning relationships

DURABLE RELATIONSHIP TRUTH
membership · authority · land rights · applicability · biological response
proceeding scope · intervention scope · capacity · entitlement · lot custody

        changed or evidenced by concrete occurrences

CONSEQUENTIAL OCCURRENCES
notice · filing · material movement · field execution · inspection/acceptance · cash settlement

        acted on and reasoned over through

KINETIC LAYER
governed Actions · live Functions · optional polymorphic Interfaces
```

The six recurring operator questions traverse all four layers. They are not modules or stages.

## 1. Enduring object candidates

### Recommended by the object-admission lane

Twelve unconditional object types:

1. Natural Person
2. Organization
3. Agricultural Holding
4. Cadastral Parcel
5. Official Area
6. Plant Trade Unit / Lot
7. Organism Taxon or Lineage
8. Cultivar
9. Public Programme or Measure
10. Governing Instrument
11. Public Proceeding
12. Intervention

One conditional object type:

13. Individual Plant

Individual Plant instances exist only where stable identity is preserved by an authority, registry, field process, operative Instrument or validated reproducible observation-derived inventory. Arbitrary detections, coordinates, samples and crowns do not instantiate it.

### Why the lane retained every noun

Each noun has independent identity, participates in several relationships and must survive correction, amendment, handoff or reopening.

- Person and Organization persist while contextual roles change.
- Holding persists while operators and Parcels change.
- Parcel persists while title, use, applicability and Intervention scope change.
- Official Area persists while geometry and regime representations change.
- Lot persists through reservation, movement, custody, use, warranty and return.
- Taxon/Lineage and Cultivar participate in biological, legal and design relationships.
- Programme persists across openings and Proceedings.
- Instrument persists through amendment, stay, construction, supersession and termination.
- Proceeding persists through filings, review, repair, decisions and reopening.
- Intervention persists through applications, contractors, execution, payment and establishment.

### Alternatives rejected

The lane rejects treating Taxon, Cultivar, Programme or Official Area as mere reference values because doing so would remove their independent links and history.

It also rejects object types for roles such as member, beneficiary, authority, CAA, contractor, nursery, inspector, creditor or payee. Those remain relationship facts.

## 2. Concrete event-object candidates

### Six candidates survive deletion

1. **Official Notice or Service**
2. **Public Filing Submission**
3. **Plant Material Movement**
4. **Field Execution Occurrence**
5. **Field Inspection or Acceptance Occurrence**
6. **Cash Settlement Transaction**

These are not subtypes of a generic Event object. Each has a different identity, actor, evidence, consequence and relationship to surviving objects.

### Why these six survive

#### Official Notice or Service

Owns the externally recognized occurrence that proves who or what was notified, by which channel, when the service became effective and which clock began.

An Instrument’s current effect cannot reconstruct the service occurrence.

#### Public Filing Submission

Owns one externally released and protocolled submission/version inside a Public Proceeding.

A Proceeding’s current scope cannot reconstruct multiple filing attempts, protocol receipts, corrected versions or timeliness.

#### Plant Material Movement

Owns one governed shipment, transfer, delivery, receipt, return or custody handoff involving traceable Lots and quantities.

Current Lot custody cannot reconstruct the chain of movements, partial quantities or reversals.

#### Field Execution Occurrence

Owns one bounded occasion of physical performance within an Intervention: removal, treatment, preparation, planting, rework, replacement or cure.

The persistent Intervention cannot itself preserve several partial work occasions, their actors, quantities, methods and exceptions.

#### Field Inspection or Acceptance Occurrence

Owns one externally or contractually recognized inspection/review occasion, including bounded establishment and defect reviews.

It connects the competent actor, examined execution occurrence, examined scope, findings, admissible or accepted quantity, decision and follow-up.

#### Cash Settlement Transaction

Owns one bank/treasury-recognized cash movement, return, reversal, repayment or recovery collection.

A public payment order or current entitlement balance cannot prove or reconstruct actual cash movement.

### Event classes rejected as objects

The lane rejects separate object types for:

- fact correction;
- biological sample/result by default;
- Instrument issuance/amendment occurrences;
- programme windows;
- eligibility decisions;
- participation elections;
- mandate acceptance;
- capacity reservation/release decisions;
- field dispatch;
- acceptance outcome separate from its inspection;
- defects/exceptions;
- payment claim release;
- liquidation/payment order;
- audit/revocation/recovery;
- aftercare assignment changes;
- survival result separate from its review;
- replacement/cure completion separate from execution;
- clocks;
- material-change triggers or reopening.

Those are retained through Actions, changes to enduring objects/relationships, or the six admitted concrete event candidates.

### Conditional event boundary

A laboratory occurrence can selectively reopen if real operator decisions need to refer repeatedly to the same independently identified sample/result occurrence beyond its official consequence. Current evidence does not yet admit a core laboratory event type.

## 3. Relationship representation candidates

### Current Palantir mapping rule

- meaningful relationship with no independent facts → direct link;
- relationship with independently owned basis, role, period, quantity, scope, authority, allocation, right or history → object-backed relationship candidate;
- event, observation, derivation, classification, co-reference or transitive inference → not a relationship.

An object-backed relationship can expose:

- a concise endpoint-to-endpoint traversal; and
- a detailed traversal through the backing fact object.

Those are two views of one fact owner, not duplicate truths.

### Sixteen atomic predicates

All 16 require an object-backed candidate when their fact-bearing form is instantiated.

#### 1. Cooperative membership

Fact class candidate: `Cooperative Membership`.

Owns member, cooperative, basis/class, period, terms and scope. Adhesion and withdrawal remain events.

#### 2. Holding stewardship or representation

Exact candidates include `Holding Stewardship` and `Holding Representation`.

They must not collapse into one generic Actor Assignment.

#### 3. Actor–Parcel tenure, access or consent

Exact candidates include `Parcel Tenure`, `Parcel Access Authorization` and `Parcel Consent`.

They remain distinct from Holding operation and Instrument effect.

Owen accepts Access Authorization and Consent as separate exact types. Consent owns affirmative assent by the competent consenter. Access Authorization owns operative entry/work permission and may be grounded in Consent, Tenure, public-asset authority, an Instrument or public decision. An independently surviving Instrument-Grounded Parcel Permission remains a distinct F3 effect.

#### 4. Holding–Parcel declaration or conduction

Exact candidates include `Holding Parcel Declaration` and `Holding Parcel Conduction`.

A filing/correction event changes the relationship but is not the relationship.

#### 5. Parcel–Official Area applicability

Candidate: `Parcel–Official Area Applicability`.

Owns authoritative basis, relevant date, geometry rule and proposition-specific effect. Raw overlap remains derived.

#### 6. Governing Instrument effect or lineage

No generic `Instrument Effect` object is proposed.

Exact candidates are named for the real effect, for example:

- Programme Establishment;
- Official Area Definition;
- Instrument Amendment;
- Instrument Supersession;
- Instrument Stay;
- Proceeding Authority Grant;
- Parcel Duty;
- Intervention Authorization.

This is one major expansion risk: exact effect classes can multiply. Gate 5 must admit only the effects used by accepted operator decisions and must not mirror every legal clause.

Owen accepts a finite F3 core. Create an Instrument-effect type only when the effect must survive independently for a current operator decision. When an Instrument merely supplies another relationship's basis, the sole-owned relationship links to that Instrument without duplicate effect truth. New endpoint-specific effects require selective reopening and fresh deletion/six-dimensional tests.

Owen accepts separate Instrument Amendment, Instrument Supersession and Instrument Stay types. Amendment alters continuing force; Supersession displaces priority; Stay temporarily suspends operative scope. Generic Instrument Lineage is rejected. Annulment, interpretation/construction and termination require selective reopening; a self-contained end date remains an Instrument property.

Owen also accepts separate Programme Constitution and Programme Funding Authority types. Constitution owns Programme existence; Funding Authority owns authorized money and budget conditions. Ordinary openings/windows remain effective-period facts on their Governing Instruments plus Programme context unless an independent Programme Operative Window later survives deletion and six-dimensional tests.

#### 7. Biological pathogen–host response

Candidate: `Pathogen–Host Response`.

Owns directed biological response, exact grains and evidence/authority qualification. It excludes individual infection, legal applicability and vector ecology.

#### 8. Public Proceeding actor participation or authority

Factless participant/current-decider pointers can remain direct links.

Fact-bearing cases require exact candidates such as:

- Proceeding Participation;
- Proceeding Decision Authority.

#### 9. Public Proceeding subject or scope

Factless subject pointers can remain direct.

Fact-bearing scope splits by authority class. `Proceeding Claimed Scope` owns what an authorized filer formally places before the authority; the linked Public Filing Submission owns the transmitting occurrence. `Proceeding Authority-Determined Scope` owns what the competent authority reviews, admits, excludes, decides or permits. Stages and versions remain within the applicable class rather than becoming relationship types. Independent appeals, audits, enforcement and recovery matters are separate Public Proceedings using the same pattern.

Owen accepts endpoint specialization for both authority classes across Person, Organization, Holding, Parcel, Official Area, valid Individual Plant, Lot, Programme, Instrument and Intervention. The 20 authority-by-endpoint types are a maximum semantic matrix, not an instruction to deploy empty types. Include an exact class only where current workflows and grain-sufficient evidence require fact-bearing scope. Factless subject context remains a direct link.

#### 10. Intervention Parcel or Plant physical scope

Candidates:

- Intervention Parcel Scope;
- Intervention Plant Scope, only when Individual Plant identity is valid.

Intended, authorized and as-built distinctions belong to one scope fact owner rather than three links.

#### 11. Intervention–Cultivar or organism specification

Candidates:

- Intervention Cultivar Specification;
- Intervention Organism Specification.

These remain distinct from biological response, legal authorization and Lot use.

#### 12. Intervention actor responsibility or authority

Exact candidates may include:

- Intervention Responsibility, with management, execution, warranty and aftercare kinds;
- Intervention Inspection Authority;
- Intervention Acceptance Authority.

Owen accepts this three-type model. Responsibility owns affirmative performance, coordination and remedy duties. Inspection Authority owns examination competence. Acceptance Authority owns binding route-specific decision power. Inspection never implies acceptance. The same actor may hold both authority relationships as separate facts. A generic Intervention Actor Assignment remains rejected.

#### 13. Intervention scarce-capacity commitment

Candidate: `Intervention Capacity Commitment`.

Owns capacity owner, Intervention, quantity/slot, period, firmness, prerequisites, expiry, release and reallocation consequence. A specific reserved Lot can link to this same commitment.

#### 14. Member-specific entitlement or creditor right

Candidates:

- Member Entitlement;
- Creditor Right.

Owen accepts them as separate fact classes. Member Entitlement relates the beneficiary Decision-Capable Actor to Public Programme or Measure and owns the durable support right. Creditor Right relates the creditor Decision-Capable Actor to debtor Organization and owns recognized payable public debt. Awarding/payment Proceedings and Instruments, Agricultural Holding and Intervention remain basis/scope links. F3 owns any independently surviving creating Instrument effect. Cash Settlement Transaction proves cash and never collapses into either right.

#### 15. Lot inclusion or use in Intervention

Candidate: `Intervention Lot Use`.

Owns intended, authorized or as-built Lot inclusion/use and quantity. It excludes reservation, custody and movement events.

#### 16. Lot actor allocation or custody

Exact candidates may include:

- Lot Allocation;
- Lot Custody;
- Lot Movement Control;
- Lot Warranty Responsibility;
- Lot Return Responsibility.

Owen accepts all five as separate exact types. Allocation does not imply possession; Custody does not imply movement authority; Movement Control does not imply warranty; Warranty does not imply return handling. Plant Material Movement events consume or change these relationships but do not replace them. A generic Lot Accountability object is rejected.

### Contextual direct-link candidates

The ledger proposes direct links only at the factless boundary:

- Individual Plant ↔ Cultivar;
- Lot ↔ Cultivar;
- Plant/Lot ↔ originating Organization, conditionally;
- Proceeding ↔ Programme;
- factless Proceeding ↔ subject;
- factless Proceeding ↔ participant;
- Proceeding ↔ current deciding Organization pointer;
- basic Instrument ↔ Programme/Proceeding/Intervention/Official Area context;
- Intervention ↔ Programme/Proceeding context.

A direct link is not also created when it merely duplicates the concise view of an object-backed relationship.

## 4. Candidate Actions

### Eleven retained semantic Actions

1. **Elect voluntary participation**
2. **Accept the cooperative execution mandate**
3. **Certify Technical Intervention Design**
4. **Release Public Application**
5. **Commit or Rebalance Intervention Capacity**
6. **Dispatch Intervention**
7. **Attest Intervention performance**
8. **Decide compulsory compliance acceptance**
9. **Decide funded-work acceptance**
10. **Decide contractual acceptance**
11. **Release a payment claim**

Each is a cohesive operation with its own decision owner and refusal boundary.

Owen accepts `Elect Voluntary Participation` as one member-owned Action across named funded, self-funded, collective and individual voluntary routes. It can create/end Proceeding Participation, create/supersede Proceeding Claimed Scope or initiate the relevant Proceeding/Intervention, but never infers or extinguishes rights beyond the governing basis. A protocolled external election also creates a Public Filing Submission; no generic Decision object is added.

Owen accepts `Accept Cooperative Execution Mandate` as a separate cooperative-owned Action. It requires a real member-granted Governing Instrument, activates only the cooperative side and creates resulting Holding Representation or Intervention Responsibility facts. It cannot manufacture the member's grant or erase individual fallback. A member Grant Action requires later direct evidence that CORDON is the authoritative signing channel.

Owen accepts `Certify Technical Intervention Design`. It creates professional design truth for bounded Intervention scope/specification, assumptions and qualifications. It never creates legal/public Intervention Authorization, permits, capacity commitments, dispatch, execution or acceptance.

Owen accepts `Release Public Application` for non-payment public applications sharing one applicant-owned release contract. It creates Public Filing Submission and endpoint-specific Proceeding Claimed Scope facts, but never public determinations or rights. Payment-claim release remains separate. A generic Release Filing Action is rejected.

Owen accepts `Commit or Rebalance Intervention Capacity` as one atomic Action across the complete affected Intervention set. The candidate portfolio and alternatives remain derived. The Action creates/changes exact Intervention Capacity Commitment facts and can record an authorized override reason. Recommendation never creates commitment truth; separate reserve/firm/schedule/release/reallocate setters are rejected.

Owen accepts `Dispatch Intervention` across cooperative, member-managed, contractor, ARIF and public-crew routes while the same management/dispatch authority class and bounded handoff apply. It consumes readiness and exact authority/resource facts. It creates or activates a real work-order Instrument only where the process preserves one. Dispatch never proves movement, execution, inspection, acceptance or establishment; real route differences require selective Action splitting.

Owen accepts `Attest Intervention Performance` as one executor-owned Action across removal, treatment, preparation, planting, rework, replacement and cure while the semantic contract remains uniform. Each submission creates a concrete Field Execution Occurrence, supported as-built scope/Lot-use facts and any evidenced custody handoff. It never inspects, accepts, proves establishment or proves cash.

Owen accepts `Release Payment Claim` as one beneficiary-owned Action across Instrument-permitted claim stages. It creates Public Filing Submission and Proceeding Claimed Scope facts, consumes only permitted entitlement-stage capacity and never admits cost, determines payable amount, liquidates, orders payment, creates public debt without competent determination or proves cash.

### How they connect

```text
member elects participation
→ cooperative accepts/refuses mandate
→ technician certifies design
→ beneficiary releases public application
→ cooperative commits or rebalances Intervention capacity
→ responsible manager dispatches Intervention
→ executor attests performance
→ assigned acceptor decides bounded acceptance
→ beneficiary releases payment claim
```

This is not one linear lifecycle. Actions occur only when their route applies and can reopen selectively.

### Conditional Action patterns

- Correct authoritative member or land facts — only if CORDON is legitimately an authoritative correction channel.
- Issue a public determination — only as concrete authority-specific Actions if a competent authority decides through CORDON.
- Review bounded biological establishment — only if the assigned reviewer actually makes that decision through CORDON at supported grain.

### Rejected Actions

- Record cash settlement;
- Reopen affected work;
- Set ready;
- Advance route;
- generic status setters;
- generic Decide/Approve/Record Event operations.

External outcomes do not need a CORDON Action merely to enter the Ontology.

### Accepted acceptance split

Owen deletes the broad `Decide route-specific Intervention acceptance` Action. Compulsory compliance, funded-work and contractual acceptance remain separate because decision owner, governing Instrument, evidence, refusal conditions, effects, downstream Proceeding/right and security meaning differ. All three may create or update the shared Field Inspection or Acceptance Occurrence event type without merging the decisions.

All eleven core Actions are accepted. Conditional authoritative-correction, public-determination and bounded-establishment-review Actions remain unaccepted pending direct evidence that CORDON is the authoritative transaction boundary.

## 5. Candidate Functions

### Three retained semantic Functions

1. **Determine Affected Decisions**
2. **Assess Named-Action Readiness**
3. **Compare Feasible Intervention Portfolios**

### Why these survive

#### Determine affected decisions

Requires live traversal of current Instrument effects, scopes, assignments, rights, commitments and decision dependencies. A stored global affected/status field would become stale.

Owen accepts one read-only Function across all five responsibilities. It returns affected decisions/Actions, reason chain, next owner, scoped hold or reopening, indeterminate propositions and explicitly unaffected work. It never edits, corrects facts, chooses routes or takes reserved decisions. Triggering/automation remains Gate 6.

#### Assess named-action readiness

Requires current cross-object conditions and returns ready/not ready/materially indeterminate only for the named Action, with blockers and cure owners. A generic readiness property is prohibited.

Owen accepts one semantic Function with action-specific typed profiles and one shared rule owner for authority, applicability, clocks, conflicts, indeterminacy and scoped continuation. Gate 6 may implement one Function or typed wrappers over shared logic. The Function explains; Action submission criteria enforce the final refusal.

#### Compare feasible portfolios

Requires combinatorial comparison across complete populations, protected commitments, resource contention, fairness safeguards, uncertainty, alternatives and sensitivity. A stored ranking cannot represent portfolio feasibility.

Owen accepts one read-only Function over complete Intervention combinations. It returns feasible alternatives, binding constraints, uncertainty and expected incremental realized Xylella-loss reduction. The portfolio remains derived. `Commit or Rebalance Intervention Capacity` is the separate governed decision that creates commitments.

### Conditional Function

Owen rejects `Determine Legal Applicability` as a fourth core Function. `Parcel Official Area Applicability` is a materialized relationship fact. Determine Affected Decisions identifies changes/dependencies, and Assess Named-Action Readiness consumes/explains the result. Gate 6 selects recalculation mechanics. A live applicability Function selectively reopens only if later research proves materialization loses correctness or timeliness.

### Rejected core Functions

- complete-population eligibility recomputation as a request-time Function;
- settlement reconciliation;
- remaining entitlement calculator;
- bounded establishment completion calculator.

The calculations may still exist, but stable/population-scale/simple derivations should not become Functions by default.

## 6. Candidate Interfaces

### One accepted Interface

`Decision-Capable Actor` is accepted for Natural Person and Organization wherever the exact relationship or workflow has the same fact shape, lifecycle, authority, Actions and security meaning for either concrete actor type.

It preserves the concrete Person/Organization identity and contains no permanent contextual roles. A relationship must split by actor type if any of the six semantic dimensions differs.

The design rejects Interfaces for:

- Entitlement Holder/Creditor;
- Proceeding Subject;
- Intervention Scope Item/Governed Subject;
- Acceptable/Completable Route Object.

Those abstractions share roles or generic mentionability, not a proven universal shape/capability.

Current uneven Interface support means later implementation may require concrete fallback paths. The semantic Interface does not assume a surface or use Interface Action constraints as behavioral enforcement.

## 7. Candidate graph through the six questions

### Question 1 — What changed, and what does it affect?

Concrete event objects and changes to enduring nouns/relationships feed `Determine decisions affected by a material change`.

The Function returns affected decisions, next owner and unaffected work. It creates no generic Trigger/Reopening object.

### Question 2 — What is required, allowed or blocked?

Governing Instruments, Areas, applicability relations, assignments, rights, scope and commitments provide direct facts.

Deterministic legal applicability may be stored or conditionally computed. Status-like summaries remain derived.

### Question 3 — Who chooses, who decides and which route continues?

F1/F7/F9 preserve exact powers, rights and custody. Member, cooperative and public decisions remain separate.

Actions preserve member participation, cooperative mandate and cooperative capacity decisions. Public determinations remain external unless concretely authorized through CORDON.

### Question 4 — Is the route ready for the named action?

`Assess readiness for one named action` evaluates current prerequisites for the exact retained Action. It never produces global route readiness.

### Question 5 — What was done, and who accepted it?

Field Execution Occurrences preserve performed work. Executor attestation records as-built claims. Field Inspection/Acceptance Occurrences preserve independent review and bounded outcomes.

Responsibility and acceptance authority remain separate relationship facts.

### Question 6 — Did the intended result land, and what remains open?

Cash Settlement Transactions prove actual cash. Field Inspection/Acceptance Occurrences preserve installation, defect and establishment reviews. Entitlement, payment order, cash, installation acceptance and biological establishment remain distinct.

## 8. Expansion and bloat risks

### Risk 1 — every accepted relationship predicate becomes a generic backing object

Rejected. Families are not implementation types. Exact relationship fact classes must be named for the real predicate.

### Risk 2 — exact predicates multiply into dozens of object types

Real risk. F1, F3, F5 and F9 each contain several possible exact predicates. Current guidance says semantic clarity outranks minimal type count, but Gate 5 must still apply deletion tests to every exact candidate.

The minimum graph should include only exact predicates required by accepted decisions and grain-sufficient evidence. It should not create every hypothetical effect, responsibility or custody subtype.

Owen accepts a semantic-uniformity consolidation rule: exact predicates may share one domain-named relationship object only when endpoints, fact shape, lifecycle, authority boundary, Actions and security meaning are materially identical. A controlled kind may distinguish them. Any material difference requires a split.

### Risk 3 — event explosion

Bounded by admitting only six concrete event candidates and rejecting a generic Event hierarchy.

### Risk 4 — Action Sprawl

Bounded by nine cohesive Actions and explicit rejection of field/status setters. The acceptance Action remains under review because its route variants may require splitting.

### Risk 5 — Interface abstraction too early

Bounded by retaining no unconditional Interface.

### Risk 6 — platform audit replaces domain history

Rejected. Action Logs/edit history can audit CORDON operations but cannot replace externally recognized notice, filing, movement, execution, inspection or cash-transaction identity.

## 9. What remains unresolved before one complete Ontology candidate

1. Which exact relationship fact classes are retained within each of the 16 atomic predicates.
2. Whether the nine Actions remain one Action each or some split by materially different authority/effect.
3. Whether the three Functions are accepted as semantic Functions.
4. Which exact properties and cardinalities are essential after the semantic graph is accepted.

## Gate boundary

The component boundaries and refusal rules remain useful evidence. All software selections in this synthesis are reopened under `gate-5-operator-reground.md`. Nothing here is admitted to the core without a cooperative-manager decision loss or authorized CORDON/AIP Action loss that no simpler representation preserves.

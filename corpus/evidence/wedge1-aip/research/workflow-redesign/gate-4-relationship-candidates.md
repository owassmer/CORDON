# Gate 4 fact-bearing relationship candidates

Status: **GATE 4 ACCEPTED AFTER MECE CORRECTION — nine fact-bearing relationship families; Gate 5 in progress**
Date: 21 August 2026
Authority: `REDESIGN_SEQUENCE.md`, `connected-operating-model.md`, and accepted `gate-3-noun-candidates.md`

This document identifies the minimum relationships among the 13 accepted nouns that carry independent business facts. It does not select Ontology types, link implementation, properties, cardinalities, primary keys, source schemas or interfaces.

## Admission rule

A relationship receives independent fact ownership only when all conditions hold:

1. a real authority, party or physical process recognizes the relationship at that grain;
2. the endpoints persist while the relationship can change independently;
3. accepted operator decisions need facts about the relationship itself across time;
4. neither endpoint can safely own those facts;
5. the relationship is not merely an event, outcome, status, observation, geometric/analytical derivation, endpoint classification or transitive shortcut; and
6. real, grain-sufficient evidence establishes it.

A necessary link with no independent business facts remains a contextual direct relationship.

## Nine minimum fact-bearing relationship families

These are semantic families for executive review. They are not proposals for nine generic relationship objects. Distinct real predicates inside a family remain distinct.

Accepted Gate 4 decision:

- **Use nine semantic relationship families while requiring distinct real predicates inside each family.** The family structure removes duplicated reasoning. It does not authorize generic Role, Scope or Effect relationships that erase cooperative membership, land right, authority, intervention responsibility, capacity, entitlement, formal proceeding scope, custody or other real distinctions.
- **Use 16 atomic relationship predicates as mandatory anti-collapse tests.** Compound workflow phrases are decomposed before fact placement. One atomic predicate has one default family; every accepted family owns at least one atomic predicate; shared evidence or a common creating instrument never authorizes duplicate ownership.
- **Keep F1 Actor Assignment and Authority and F2 Holding–Parcel Operation and Actor–Parcel Tenure/Access separate.** Membership, representation, delegation, Proceeding authority and Intervention responsibility concern scoped actor powers and duties. Holding–Parcel declaration and actor–Parcel title, control, access or consent concern land association and rights. Neither family may be used to infer the other.
- **F3 uses proposition-specific deterministic applicability, not automatic deferral or automatic legal promotion.** When the Governing Instrument, authoritative geography, relevant date, partial-intersection rule and any more-specific decision make the consequence deterministic, CORDON establishes the legal applicability directly. When geometry deterministically creates only a warning or procedural trigger, CORDON establishes that trigger. Raw, contextual or conflicting overlap remains a derived screening/reconciliation result and never silently becomes a stronger legal fact.
- **Keep F5 Intervention Physical and Material Scope separate from F6 Scarce Capacity Reservation or Commitment.** F5 states what the undertaking includes or requires across Parcels, Plants, Cultivars and Plant Trade Units/Lots. F6 states which scarce capacity is actually reserved or committed, for what period and under which release conditions. Approved requirements, availability estimates and real commitments must not collapse.
- **Keep F7 Member-Specific Entitlement or Creditor Right distinct from F3 Scoped Governing Instrument Effect and Applicability.** F3 preserves what the Governing Instrument does and on what basis. F7 preserves the durable member-level holder, creditor identity, scope, amount or ceiling, permitted claim stages, conditions and recovery exposure that survive the creating decision. Claims, liquidation, payment, audit and recovery act upon the right; they do not replace it.
- **Keep F8 Formal Proceeding Subject and Scope distinct from actor participation, instrument effect, entitlement and physical Intervention scope.** F8 owns independently changing scope preserved by the formal matter itself. A factless subject pointer remains contextual.
- **Keep F9 Plant Material Allocation and Custody distinct from Intervention use and scarce-capacity commitment.** F9 owns accountable actor–Lot custody/allocation facts. Movement, dispatch, receipt and return remain events.
- **Apply placement precedence.** Atomize; resolve identity; classify event/outcome; classify observation; classify derived result; classify endpoint/context; then place the independently surviving relationship in exactly one family. Unknown private facts remain unknown.

### F1. Actor assignment and authority

A Natural Person or Organization holds a consequential contextual position relative to an Organization, Agricultural Holding, Public Proceeding or Intervention.

Real predicates can include:

- cooperative membership;
- representation or office;
- operation or representation of an Agricultural Holding;
- mandate or delegation;
- Public Proceeding participation or decision authority;
- Intervention contracting, management, execution, inspection, acceptance, warranty or aftercare responsibility.

The relationship is fact-bearing only where it has its own basis, scope, effective period, powers, duties or termination conditions. A bare label such as member, applicant, CAA, contractor or inspector remains contextual projection. F1 owns the instantiated assignment; F3 owns any distinct normative Instrument effect that creates, limits, suspends or terminates it. Beneficiary or creditor identity that exists only through a durable right belongs to F7.

Why independent facts matter:

- the same actor can have different powers in different contexts;
- a Holding persists while its operator or representative changes;
- a cooperative membership or mandate has its own period and terms;
- execution does not imply acceptance authority;
- aftercare responsibility cannot be inferred from contractor identity.

Evidence boundary: public registers, acts, real proceedings and public contracts establish public instances. Current private membership, mandate, delegation and responsibility require actual operative evidence where not permissionlessly available.

### F2. Holding–Parcel operation and actor–Parcel tenure/access

Keep two distinct real predicates inside this family:

1. Agricultural Holding ↔ Cadastral Parcel: declared, conducted or operational land relationship.
2. Natural Person or Organization ↔ Cadastral Parcel: title, control, occupation, management, access or consent relationship.

They cannot collapse. Cadastral ownership, agricultural conduction, public-asset management, access and authority to alter land can belong to different actors. F2 excludes Official Area applicability, Plant location, Intervention scope and actor–Holding assignment.

Independent facts can include the relationship basis, scope or share, effective period, declared area/use, authority to access or alter, consent requirement, source and unresolved conflict.

Why endpoint storage fails:

- a Parcel can move among holdings and actors;
- a Holding can gain or lose Parcels;
- current farm-file or title data would overwrite historical decision basis;
- actor-to-parcel authority cannot be inferred transitively through the Holding.

Evidence boundary: official orders and public/civic-land records establish some public instances. Current target relationships require current farm-file, title, consent or competent authority evidence when not public.

### F3. Scoped governing Instrument effect and applicability

A Governing Instrument has a consequential scoped effect on an accepted noun or on another Governing Instrument.

Real predicates can include:

- establishes, opens, funds, amends, implements, suspends or closes a Public Programme or Measure;
- creates, redraws, classifies or retires an Official Area;
- amends, supersedes, stays, annuls, construes or terminates another Governing Instrument;
- creates or limits a duty, permission, authority, mandate, concession, guarantee, contract, remedy or operative condition for a Person, Organization, Holding, Parcel, Area, Plant, Lot, Programme, Proceeding or Intervention;
- establishes authority- and date-grounded Parcel membership or applicability in an Official Area.

Independent facts can include effect kind, affected proposition, effective period, conditions, priority/conflict and supersession/stay/termination scope. F3 owns the normative creating, limiting, suspending or terminating effect. It does not duplicate the instantiated actor assignment in F1, formal proceeding scope in F8 or surviving member-specific right in F7.

Boundary:

- a basic contextual association is not fact-bearing;
- a PDF or template is not an operative relationship;
- raw polygon intersection is a derived overlay, not legal applicability;
- current consolidated text cannot safely reconstruct historical effect.

Evidence boundary: public legal and administrative evidence strongly supports public effects. Private mandate, contract, guarantee and aftercare effects require the actual operative instrument unless a real public source exposes them.

### F4. Biological pathogen–host response

An Organism Taxon or Lineage has a directed, evidence-qualified biological host, susceptibility, resistance or tolerance relationship with a host Taxon or Cultivar.

Independent facts can include the exact biological grains, relationship classification, evidence/authority class, geography or context, effective version and qualification or uncertainty.

Why endpoint storage fails:

- one organism lineage relates differently to many hosts and cultivars;
- one cultivar can have different relationships to different lineages;
- the conclusion can change without either endpoint identity changing;
- scientific observation, official recognition and legal applicability are not interchangeable.

Boundary:

- an observed infected plant is an observation at plant grain;
- a research result does not become official or legal applicability by itself;
- generic species labels cannot substitute for exact lineage and host grain;
- legal host classification, cultivar authorization and programme applicability belong to F3;
- Intervention target/use belongs to F5;
- vector/transmission or broader ecological relations are outside F4 unless a later accepted operator decision proves an independently persistent predicate.

Evidence boundary: official host/cultivar instruments and scientific evidence establish relationship grain. The authority class and operative consequence must remain explicit.

### F5. Intervention physical and material scope

An Intervention includes a Cadastral Parcel, conditionally identified Individual Plant, Plant Trade Unit / Lot, Cultivar or organism target/input in a stated physical or biological role.

Distinct predicates can include:

- Parcel or Plant target/scope;
- approved biological design and Cultivar composition;
- Plant Trade Unit / Lot inclusion or use;
- intended, authorized or independently preserved as-built physical/material scope.

Independent facts can include included/excluded role, extent or quantity, purpose, governing basis, scope version, substitution boundary and unresolved residual scope.

Why endpoint storage fails:

- one Intervention can span many Parcels, Plants, Cultivars and Lots;
- one Parcel can carry concurrent compulsory and voluntary Interventions;
- approved design can survive supplier-lot substitution;
- final field condition cannot reconstruct intended, authorized or rejected scope.

Boundary:

- reservation belongs to F6;
- actor–Lot allocation/custody belongs to F9;
- dispatch, delivery, installation, substitution, replacement, execution and acceptance remain events/outcomes;
- an observed footprint is evidence, not the scope relationship itself;
- observations and acceptance outcomes can evidence or change F5 but are not F5 predicates.

Evidence boundary: public orders, concessions and controls establish public instances. Current private scope, substitutions and lot use require actual technical, contractual and field evidence.

### F6. Scarce capacity reservation or commitment

A Natural Person or Organization commits a scarce operational or financial capacity to an Intervention, optionally involving a specific Plant Trade Unit / Lot where the real commitment does so.

This family owns the resulting commitment, not the recommendation or the decision event that created it.

Independent facts can include capacity owner, affected Intervention, quantity or slot, period, prerequisites, tentative/reserved/firm/scheduled distinction, expiry, release condition, substitution, reallocation consequence, policy basis and override reason.

Why independent ownership matters:

- eligibility and readiness do not reserve capacity;
- a commitment can constrain other Interventions while both endpoints persist;
- released or expired capacity cannot be reconstructed from the current schedule;
- firm commitments must not be opportunistically re-ranked.

Boundary:

- availability estimates, tender ceilings and capacity scores are not commitments;
- recommendation, authorization, release and reallocation are events/decisions;
- no current private commitment is inferred from a public analogue.

Evidence boundary: real public work orders can establish public commitments. Current cooperative, nursery, contractor, technician, inspector and finance commitments require actual operative evidence where not public.

### F7. Member-specific entitlement or creditor right

A Natural Person, Organization or Agricultural Holding holds a durable programme-, proceeding-, instrument- or intervention-scoped entitlement or creditor right.

Independent facts can include holder/creditor, scope, amount or ceiling, permitted claim stages, conditions, effective period, guarantee or recovery exposure and unresolved assignment.

Why this remains distinct from F3:

- F3 explains what the Governing Instrument does;
- F7 preserves the member-specific right that survives after the creating decision and through claims, holds, payment attempts, audit and recovery;
- eligibility does not create entitlement;
- liquidation and payment events do not replace the underlying right;
- collective coordination does not transfer the member’s creditor identity by default.

Boundary:

- application, concession decision, claim, liquidation, payment order and settlement remain proceedings/events/outcomes;
- a generic programme-participation or eligibility relationship is rejected;
- current creditor assignment cannot be inferred from public funding presence.

Evidence boundary: named concessions and public decisions establish many public instances. Private assignment or insufficiently published member-specific rights require the operative instrument or proceeding evidence.

### F8. Formal proceeding subject and scope

A Public Proceeding formally concerns an accepted noun with independently changing facts preserved by the matter itself.

Real predicates can carry:

- claimed or requested subject/scope;
- reviewed subject/scope;
- admitted or excluded subject/scope;
- decided or permitted subject/scope;
- appealed, audited, enforced or recovery subject/scope;
- version, quantity, amount, basis and effective history where the real proceeding preserves them.

Why independent ownership matters:

- one Proceeding can include several member-, Holding-, Parcel-, Plant-, Lot- or Intervention-specific scopes;
- scope can change through integration, exclusion, variant, appeal, audit or recovery without changing the Proceeding or subject identity;
- a final decision cannot reconstruct requested, reviewed, excluded or earlier scope;
- a bare subject pointer cannot carry quantity, version, basis or scope history.

Boundary:

- actor participation and decision authority belong to F1;
- a factless subject pointer remains a contextual direct link;
- normative Instrument effect belongs to F3;
- durable entitlement belongs to F7;
- physical Intervention scope belongs to F5;
- submission, integration, decision, appeal, audit and recovery occurrences remain events/outcomes.

Evidence boundary: real filed matters and authority records establish public instances. Private or permissioned proceeding scope remains unknown until the actual filed/reviewed record establishes it.

### F9. Plant material allocation and custody

A Natural Person or Organization holds an independently preserved allocation, possession/custody, dispatch-control, receipt-control, movement-control, warranty or return responsibility for a Plant Trade Unit / Lot.

Independent facts can include:

- accountable actor;
- Lot and quantity/share;
- allocation or custody basis;
- effective period;
- duties and movement-control conditions;
- transfer or handoff condition;
- warranty, return or traceability responsibility.

Why independent ownership matters:

- one Lot can pass among nursery, transporter, cooperative, member, contractor and return/warranty handlers while retaining identity;
- one actor can hold different quantities or responsibilities across Lots and periods;
- movement events do not reconstruct who remained accountable between events;
- Intervention use and scarce-capacity commitment do not cover custody outside or between Interventions.

Boundary:

- Intervention inclusion/use belongs to F5;
- reserved or committed stock belongs to F6;
- dispatch, movement, receipt, return and transfer occurrences remain events/outcomes;
- origin, producer or Cultivar classification with no independent relationship facts remains contextual.

Evidence boundary: passport, movement, delivery, custody and commercial records can establish real instances. Current private allocation, custody, warranty and return responsibility require actual operative evidence.

## Sixteen atomic anti-collapse predicates

1. Cooperative membership — F1.
2. Holding stewardship or representation — F1.
3. Actor–Parcel tenure, access or consent — F2.
4. Holding–Parcel declaration or conduction — F2.
5. Authority-grounded Parcel–Official Area applicability — F3.
6. Governing Instrument effect or lineage — F3.
7. Biological pathogen–host response — F4.
8. Public Proceeding actor participation or authority — F1.
9. Public Proceeding subject or scope — F8.
10. Intervention Parcel or Plant physical scope — F5.
11. Intervention–Cultivar or material specification — F5.
12. Intervention actor responsibility or authority — F1.
13. Intervention scarce-capacity commitment — F6.
14. Member-specific entitlement or creditor right — F7.
15. Lot inclusion or use in Intervention — F5.
16. Lot actor allocation or custody — F9.

The earlier 11 workflow-first grains remain dated research groupings. Gate 5 uses the 16 atomic predicates above as the current anti-collapse contract.

## Contextual direct relationships

These connections may be necessary later but presently carry no independent business facts beyond endpoint context or another accepted relationship:

- Individual Plant → Cultivar classification;
- Plant Trade Unit / Lot → Cultivar classification;
- basic Plant or Lot origin link where traceability already owns the facts;
- Public Proceeding → Public Programme or Measure context;
- Public Proceeding → basic subject where no independently changing F8 facts exist;
- Public Proceeding → participant or current deciding Organization where no separate F1 assignment facts exist;
- basic Governing Instrument → Programme, Proceeding, Intervention or Official Area association when F3 owns every consequential effect;
- basic Intervention → Programme or Proceeding context.

No implementation decision is implied.

## Rejected relationships

### Events and outcomes

Reject adhesion, mandate acceptance, filing, ranking, concession decision, movement, dispatch, receipt, execution, inspection, acceptance, liquidation, payment order, settlement, audit, revocation, recovery, survival review, defect and replacement as relationship families.

They create or change relationship history but remain events or bounded outcomes.

### Status-like relationships

Reject generic eligible, participating, selected, ready, blocked, accepted, paid, active or complete relationships.

### Derived relationships

Reject:

- Parcel-in-Area based only on polygon intersection;
- inferred programme applicability;
- calculated cohorts and feasible portfolios;
- expected-loss-reduction relationships;
- remote-observation relationships promoted beyond observed grain.

### Transitive shortcuts

Reject:

- actor controls Parcel because the actor operates its Holding;
- Holding belongs to Area through current Parcel overlay;
- member is beneficiary because they appear in a collective Proceeding;
- Lot is lawful because its Cultivar is permitted;
- Programme funded Parcel inferred from eligibility or public payment presence.

## Current private-instance boundary

The relationship families are structurally supported. These current target facts remain unknown until real evidence establishes them where no permissionless source does:

- current membership, representation, mandate, delegation and responsibility assignments;
- current Holding–Parcel declaration and actor–Parcel title/control/consent;
- actual private Governing Instrument effects;
- current Intervention scope, assignments, Lot use, private acceptance, warranty and aftercare;
- live capacity reservations, commitments, releases, reallocations and overrides;
- member-specific entitlement or creditor assignment where public records are insufficient;
- actual filed/reviewed Proceeding subject and scope where public records are insufficient;
- current Lot allocation, custody, transfer responsibility, warranty and return responsibility;
- final bank settlement.

Unknown private relationships remain unknown, not negative.

## Executive review result

Owen accepts all nine fact-bearing relationship families and their boundaries after the Gate 5 MECE audit selectively reopened Gate 4.

The 16 atomic predicates are mandatory anti-collapse tests. Contextual direct relationships remain distinct from fact-bearing families. Events, outcomes, statuses, observations, derived overlays and transitive shortcuts remain rejected as relationship families.

Gate 4 is complete after the accepted MECE correction. Gate 5 now derives the minimum core Ontology from the corrected nine-family, 16-predicate inventory.

## Gate boundary

No Ontology type, link implementation, property, cardinality, primary key, source schema or interface is selected here. New real evidence can remove, split or selectively reopen a relationship grain without reopening the noun set wholesale.

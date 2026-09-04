# Gate 3 noun candidates

Status: **GATE 3 ACCEPTED — 13 real-world nouns; Gate 4 accepted; Gate 5 in progress**
Date: 21 August 2026
Authority: `REDESIGN_SEQUENCE.md` and `connected-operating-model.md`

This document identifies the minimum persistent real-world nouns required by the accepted connected operating model. It does not select relationships, properties, cardinalities, Ontology types, source schemas or interfaces.

## Admission rule

A candidate survives only when all conditions hold:

1. it exists independently of CORDON, a source, screen or workflow implementation;
2. operators must recognize the same instance after correction, handoff, amendment, delay or reopening;
3. an accepted decision becomes unsafe or impossible if the instance is not retained;
4. it is not merely a contextual role, status, event, bounded outcome, document, derived summary or source representation;
5. its essential meaning is not a fact-bearing relationship reserved for Gate 4; and
6. public evidence or mandatory direct evidence establishes the real grain without inference from source-table shape.

## Reconciled minimum candidate set

Accepted Gate 3 decision:

- **Natural Person and Organization remain separate real-world nouns.** Member, beneficiary, owner, representative, authority, CAA, contractor, inspector, creditor and similar terms remain contextual roles. Any shared abstraction is deferred to the Ontology gate.
- **Agricultural Holding and Cadastral Parcel remain separate real-world nouns.** The holding is the persistent farm operating and administrative unit; the parcel is the persistent legally referenced land unit. Gate 4 owns their people, organization, membership, operation, control, title and declared-land relationship grains.
- **Official Area remains a real-world noun when the authority or governing process preserves its identity.** Governing instruments and GIS geometries evidence the area. A generic polygon or analytical buffer does not create one. Gate 4 owns the fact-bearing Parcel membership/applicability relationship.
- **Individual Plant is admitted conditionally.** Preserve plant identity where an external authority, registry, field process or operative Governing Instrument preserves it, or where a validated, reproducible observation-derived inventory establishes stable plant identity with measured error. Arbitrary detections and unvalidated coordinates do not create Plants. Otherwise remain at Parcel, quantity, Plant Trade Unit / Lot or Intervention grain.
- **Public Programme or Measure, Governing Instrument and Public Proceeding remain distinct real-world nouns.** The programme is the enduring policy/support structure; the instrument is the operative source of a consequential rule, right, duty, authority, commitment or remedy; the proceeding is the specific formally instituted public matter. Gate 4 owns their governing, applicability, participation, subject and entitlement relationship grains.
- **Intervention remains the persistent physical undertaking.** Admit an instance only at the grain preserved by the real authority, contract or physical process. Work orders, dispatch, execution, acceptance, aftercare and replacement remain instruments, events, outcomes or later relationships unless real evidence requires otherwise.

Accepted evidence boundary:

- **Rule 6 accepts any real, grain-sufficient evidence.** Official/public, operational, judicial, procurement, scientific, permissionless observation or directly supplied evidence can establish noun grain. An analogue can establish possible structure but never a target actor’s current fact. Direct private evidence remains mandatory only where the current private instance or later relationship cannot otherwise be established.

### Actors

#### 1. Natural Person

One real human being whose identity persists while roles change.

Required because the same person can act as member, owner, beneficiary, signatory, representative, responsible person, creditor, technician, inspector, heir or recipient in different contexts. Those roles must not redefine the person.

Public evidence establishes the grain. Private identity and authority packs remain mandatory before asserting a specific person’s current roles.

#### 2. Organization

One legally or operationally distinct organization whose identity persists while roles change.

Required for cooperatives, recognized producer organizations, CAAs, Comuni, plant-health authorities, ARIF, contractors, nurseries, banks, insurers, control bodies, courts and other counterparties. These labels are classifications or contextual roles, not separate nouns.

Public registers and acts establish the grain. Current private authority, contracting and responsibility require direct evidence.

### Land and biological subjects

#### 3. Agricultural Holding

One agricultural operating unit represented in agricultural administration and able to persist while its people, parcels, crops and applications change.

Required for the complete cooperative population, farm-file truth, applicant/beneficiary decisions and continuity across changing land relationships. It cannot be reduced to a person, organization or collection of parcels because the authoritative farm unit has its own identity and administrative continuity.

Current production instances require a validated CAA/SIAN farm file and authority pack.

#### 4. Cadastral Parcel

One officially identified cadastral land unit.

Required because official notice, title reconciliation, farm-file linkage, area applicability, application scope, public decisions and field work repeatedly refer to the same legally identified land. Geometry, ownership, agricultural use and work footprint remain separate facts or relationships.

SIT and Agenzia delle Entrate sources establish the public grain. Current control and title require direct evidence.

#### 5. Official Area

One authority-defined geographic area with an independently recognizable purpose and identity.

Required for demarcated areas, infected and buffer geography, programme geography and other official extents whose applicability changes operator decisions. A GIS polygon is only a representation. Parcel membership in an area is a later relationship.

Official acts and current/historical GIS services establish the grain. Exact legal effect remains instrument- and date-specific.

#### 6. Individual Plant

One individually identifiable plant where the real proceeding or field process distinguishes that plant.

Required for official infection, monumental status, removal targets, inspected execution, survival, defect and replacement when those decisions occur at plant grain. A validated observation-derived inventory may establish real plant identity where detection, omission, duplicate, split/merge, geolocation, reproducibility and cross-epoch matching performance are measured at the supported orchard grain. CORDON must not manufacture identity from arbitrary imagery points or sample coordinates.

Official monitoring, orders and monumental-tree records establish public examples. Crecco and CSIC/JRC work establish that inventory-producing observation processes exist at bounded and regional scales, though current region-wide vectors are not held. Installed, replacement and current observation-derived plant identity still require grain-sufficient validation.

#### 7. Plant Trade Unit / Lot

One traceable trade unit or lot of plant material sharing the real commercial and phytosanitary identity preserved by the governing process.

Required because passport, production site, inspection, movement, reservation, receipt, substitution and defect decisions must follow the same lot from nursery through installation. Cultivar or nursery identity cannot substitute for the lot.

Public rules establish the grain. Use the actual governing term and do not assume every commercial lot equals one passport trade unit. Actual stock, reservation, delivery and warranty remain instance facts requiring real evidence.

#### 8. Organism Taxon or Lineage

One scientifically and officially distinguishable organism identity at the taxonomic or lineage grain used by the governing decision.

Required because official condition and duties can differ by species, subspecies, sequence type and host relationship. This prevents one scalar “Xylella status.”

Official laboratory, authority and scientific sources establish the grain. The level used in a particular decision must be officially established rather than inferred.

#### 9. Cultivar

One recognized cultivated plant variety whose identity persists across plants and lots.

Required because programme eligibility, plant legality, orchard design, movement, certification and recovery strategy can depend on cultivar. Many plants and lots can instantiate the same cultivar, so it cannot be reduced to a lot attribute without losing the governed identity.

Official cultivar rules and plant sources establish the grain. Member planting and delivered-lot assertions require direct evidence.

### Public operating structures

#### 10. Public Programme or Measure

One independently governed public or local support/recovery programme that retains identity across openings, amendments, rankings, concessions and payment stages.

Required for complete-population evaluation, member participation, cooperative pursuit, funding-source election and programme-specific public branches. An open window is a state or event of the programme, not another noun.

Public acts and programme sources establish the grain.

#### 11. Governing Instrument

One independently identifiable operative public, judicial, cooperative, contractual or financial act or agreement that persists as something actors can invoke, amend, construe, stay, supersede or terminate and that governs a consequential right, duty, authority, commitment, decision or remedy.

Required because applicability, authority, scope, clocks and consequences must remain attributable through amendment, supersession, stay, termination and later review. Public acts, judgments, permits, concessions, mandates, contracts, work orders, guarantees and aftercare protocols can be instances when the operative act/agreement has independent identity beyond the occurrence that issued or signed it. Issuance, signature, release and decision remain events/outcomes; normative consequence belongs to F3; any resulting durable member right belongs to F7. A template, inferred obligation, PDF, portal page or source capture is evidence, not an operative instance.

Official act, court, permit, published contract, prescribed-form and real agreement sources establish the grain. Current private terms remain unknown unless real evidence establishes them.

#### 12. Public Proceeding

One formally instituted public administrative or judicial matter that retains identity through submissions, requests, review, decisions, repair and reopening.

Required for applications, permits, payment claims, appeals, audits, enforcement and recovery when the real authority treats them as independently identifiable matters. This is not a generic CORDON `Case`; private CAA tracker rows and work queues do not establish proceeding identity.

Public process and case records establish the grain. Actual filed instances and local repair mechanics require direct evidence.

### Physical recovery work

#### 13. Intervention

One bounded intended physical compliance, recovery or investment undertaking that persists through preparation, authorization, change, resource commitment, dispatch, execution, acceptance, aftercare and any early replacement or cure.

Required because the same physical undertaking can outlive an application, decision, contractor, payment event or temporary hold. Public cash can settle while the intervention’s establishment work remains open.

Orders and programme rules establish the grain. Real cooperative, contractor, technician and aftercare packages are mandatory before fixing local split/merge rules.

## Rejected candidates

### Contextual roles

Do not create nouns for member, beneficiary, owner, holder, applicant, collective applicant, cooperative, OP, CAA, Comune, authority, ARIF, technician, contractor, nursery, supplier, inspector, executor, creditor, payee, guarantor, successor or representative.

Natural Person or Organization persists. The role exists only in relation to a programme, proceeding, instrument, land subject, intervention and date.

### Events and bounded outcomes

Do not create enduring nouns for sample, result, confirmation, notice, adhesion, mandate acceptance, filing, ranking, concession issuance/decision, permit decision, dispatch, execution, inspection, acceptance, liquidation, payment order, settlement, survival review, defect, replacement, audit, revocation or recovery.

These are events or outcomes that affect surviving nouns and accepted relationships. Gate 5 decides their minimum Ontology representation without promoting them into persistent nouns by default.

### Product, source and work-management constructions

Reject generic Case, Evidence, Status, Task, Queue, WorkItem, Source, SourceChannel, SourceGap, RuleRelease, CoverageRelease, dossier, bundle and global timeline.

They are construction, provenance or interface concepts rather than the real-world subjects of operator decisions.

### Gate 4 relationship disposition

Ownership, Holding–Parcel control, membership, authority, delegation, mandate, applicability, area membership, responsibility, capacity commitment and entitlement are facts among admitted nouns. Their accepted relationship families are owned by `gate-4-relationship-candidates.md`. Eligibility, collective inclusion and acceptance remain decisions, events, outcomes or derived summaries unless a specific accepted relationship fact applies.

### Candidates blocked on direct evidence

The following are not admitted nouns:

- Capacity Reservation or Firm Commitment;
- Execution Cohort;
- CAA Administrative Dossier;
- Survival Cohort.

Capacity Reservation is an event or fact-bearing relationship unless contrary real evidence emerges. Execution Cohort and Survival Cohort are selected or analytical sets unless a governing process independently preserves their identity. CAA Administrative Dossier remains an office construction. Real mandates, work orders, guarantees and aftercare protocols are possible Governing Instrument instances, not additional noun classes.

## Gate 3 verdict

Owen accepts the following 13 real-world nouns:

1. Natural Person
2. Organization
3. Agricultural Holding
4. Cadastral Parcel
5. Official Area
6. Individual Plant — where an external process or validated reproducible observation-derived inventory preserves individual identity
7. Plant Trade Unit / Lot
8. Organism Taxon or Lineage
9. Cultivar
10. Public Programme or Measure
11. Governing Instrument
12. Public Proceeding
13. Intervention

Gate 3 is complete. Gate 4 accepts the fact-bearing relationship families among these nouns. Gate 5 derives the minimal core Ontology without reopening noun grain by default. New real evidence can selectively reopen an affected noun; it does not reopen the set wholesale.

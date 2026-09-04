# Gate 5 MECE self-audit

Status: independent Connor audit; awaits reconciliation with two read-only audit lanes
Date: 22 August 2026
Scope: accepted connected operating model against the 13 Gate 3 nouns, seven Gate 4 relationship families, 11 concrete relationship grains, contextual direct links, events/outcomes and derived computations

## Verdict

**PASS-WITH-SEMANTIC-CORRECTIONS.**

The 13 nouns and seven relationship families cover the accepted connected operating model without requiring another noun or relationship family. The inventory is collectively exhaustive when events/outcomes, contextual direct links and derived computations remain explicit representation categories rather than being forced into nouns or fact-bearing relationships.

The families are not mutually exclusive by name alone. They become mutually exclusive only under explicit fact-placement rules. Gate 5 must apply those rules before selecting Ontology representation.

## Placement order

For every accepted operator proposition, classify the fact in this order:

1. **Persistent identity:** the same real instance must survive correction, handoff or reopening → accepted noun.
2. **Independent relationship fact:** endpoints persist while a real scoped relation changes and owns basis, scope, period, quantity, right or duty → one concrete predicate inside F1–F7.
3. **Contextual direct link:** the connection is real or navigationally necessary but owns no independent facts → direct contextual link.
4. **Consequential occurrence:** something happened or a bounded decision/outcome landed → event/outcome representation, not a noun or relationship family.
5. **Calculated conclusion:** a current conclusion is recomputable from facts and rules → derived computation/projection.
6. **Evidence:** a record supports one of the above but does not replace it → source/evidence representation outside the core real-world noun inventory.

A fact receives one primary semantic owner. Evidence and events may establish or change that owner without becoming duplicate owners.

## Relationship-family placement rules

### F1. Actor–Context Assignment

Owns a Person/Organization’s real scoped capacity relative to an Organization, Holding, Proceeding or Intervention when the assignment has its own basis, period, powers, duties or termination.

Examples: cooperative membership, Holding operation/representation, Proceeding participant authority, Intervention executor/inspector/acceptor/aftercare responsibility.

Does not own:

- the Governing Instrument’s operative effect creating the assignment → F3;
- land title, conduction, access or consent → F2;
- the member’s durable creditor right → F7;
- a role label projected from a Proceeding or event with no separate assignment facts → contextual direct link.

### F2. Land Association or Right

Owns Holding–Parcel agricultural conduction/declaration and Person/Organization–Parcel title, control, access or consent.

Does not own:

- Parcel–Official Area legal applicability → F3;
- Intervention physical footprint → F5;
- actor authority that exists only because an Instrument grants a scoped mandate → F1 plus the creating F3 effect, not F2 unless an actual land right also exists.

### F3. Scoped Governing Effect or Applicability

Owns what a Governing Instrument does to an accepted subject, including legal applicability, authority, duty, permission, amendment, supersession, stay, termination or proposition-specific Area effect.

Does not own:

- the resulting actor assignment as a continuing relation → F1;
- the resulting member-specific durable financial right → F7;
- the Procedure or decision event that created, amended or terminated the effect → event/outcome;
- raw polygon overlap → derived reconciliation result.

The same real instrument can establish F3 and evidence a distinct F1 or F7 fact. That is not duplicate ownership because the propositions differ.

### F4. Organism–Host Relationship

Owns a recognized biological pairing between an Organism Taxon/Lineage and another Taxon/Lineage or Cultivar: host, susceptibility, resistance or tolerance at the supported grain and authority/evidence class.

Does not own:

- an Individual Plant’s detected infection → observation/official outcome;
- Individual Plant or Lot cultivar identity → contextual classification link;
- an Intervention’s target organism or specified Cultivar → F5;
- legal consequences attached to the pairing → F3.

### F5. Intervention Scope and Material Use

Owns what an Intervention includes as intended, authorized, actual or accepted physical/biological scope: Parcel, supported Individual Plant, Cultivar, organism target, or Lot use.

Does not own:

- an actor’s responsibility for the Intervention → F1;
- a scarce resource or Lot reservation/commitment before use → F6;
- delivery, installation, execution or acceptance occurrence → event/outcome;
- observed footprint/crown change → observation;
- accepted quantity as a decision occurrence when no continuing scope relation survives → outcome.

### F6. Capacity Reservation or Commitment

Owns a real scarce operational or financial commitment to an Intervention: owner, quantity/slot, period, prerequisites, firmness, expiry/release, substitution and reallocation consequence.

Does not own:

- what the Intervention requires → F5 or a derived requirement;
- current uncommitted availability → endpoint/observation/derived estimate;
- the decision to reserve, release or reallocate → event;
- the actor’s authority to make that decision → F1/F3.

For a Plant Trade Unit/Lot:

- specified or installed use in the Intervention → F5;
- reserved quantity for the Intervention → F6;
- dispatch/receipt/custody transfer → event/outcome unless a real continuing custody relation with independent facts must persist.

### F7. Member-Specific Entitlement or Creditor Right

Owns the durable holder-specific financial/public right after it exists: holder, scope, amount/ceiling, claim stages, conditions, period, assignment and recovery exposure.

Does not own:

- the Governing Instrument effect that creates or changes the right → F3;
- applicant/beneficiary role in a Proceeding without a durable right → F1 or contextual direct link;
- eligibility or ranking → derived decision/event;
- claim, liquidation, payment order, settlement, audit, revocation or recovery occurrence → event/outcome.

## Coverage matrix

| Connected-model proposition | Persistent nouns | Primary relationship owner | Other representation | Coverage |
|---|---|---|---|---|
| Member and cooperative social-base membership | Person/Organization; Organization | F1 cooperative membership | admission/withdrawal events | Complete |
| Holding operator and legal representative | Person/Organization; Holding | F1 Holding assignment | succession/change events | Complete |
| Parcel title, lease, control, access and consent | Person/Organization; Parcel | F2 actor–Parcel right | title/consent evidence | Complete |
| Parcel included in authoritative farm unit | Holding; Parcel | F2 Holding–Parcel conduction/declaration | declaration/correction events | Complete |
| Official area identity and version | Official Area; Governing Instrument | F3 Instrument effect on Area | geometry as evidence | Complete |
| Parcel’s proposition-specific area applicability | Parcel; Official Area; Governing Instrument | F3 scoped applicability | raw overlap derived | Complete |
| Organism, lineage, host and cultivar response | Taxon/Lineage; Cultivar | F4 organism–host | scientific/official evidence class | Complete |
| Programme identity across openings/amendments | Programme; Governing Instrument | F3 programme governance/effect | opening/amendment events | Complete |
| Instrument amendment/supersession/stay | Governing Instrument | F3 instrument lineage/effect | enactment/judgment event | Complete |
| Public application/permit/claim/audit matter | Public Proceeding | — | persistent noun plus events/outcomes | Complete |
| Actor authorized to file, answer, decide or appeal | Person/Organization; Proceeding | F1 Proceeding assignment | filing/decision/appeal events | Complete |
| Proceeding subject scope | Proceeding; Holding/Parcel/Plant/Intervention | F3 only where Instrument/decision establishes consequential scope; otherwise contextual direct link | submitted/decided scope event facts | Complete with semantic rule |
| Public eligibility | Programme/Instrument; Person/Organization/Holding/Parcel | — | derived proposition-specific computation or authority decision | Complete |
| Member adhesion | Person/Organization; Programme/Proceeding | — | event; later participant assignment only if F1 facts survive | Complete |
| Cooperative mandate acceptance | Organization; Person/Organization; Instrument | F1 assignment plus F3 effect if operative mandate exists | acceptance event | Complete |
| Public ranking and concession decision | Programme; Proceeding; Instrument | F3 effect; F7 if durable right results | decision event | Complete |
| Member-specific creditor/beneficiary right | Person/Organization/Holding; Programme/Proceeding/Intervention | F7 | claims/payment events | Complete |
| Funding-source election/cumulation decision | Person/Organization/Holding; Programme; Proceeding | F3 governing constraints | election/authority decision plus derived compatibility | Complete |
| Complete opportunity population | Person/Organization; Holding; Parcel; Programme; Intervention | — | derived population from accepted facts and rules | Complete |
| Feasible portfolio and expected loss reduction | Intervention; commitments and rights | — | derived computation | Complete |
| Cooperative authorization to commit/override | Organization; Intervention | F1 authority; F3 basis | commit/override event | Complete |
| Intervention’s Parcel/Plant target | Intervention; Parcel/Plant | F5 scope | authorization/execution events | Complete |
| Intervention’s Cultivar design | Intervention; Cultivar | F5 biological design | variant event | Complete |
| Lot specified/delivered/installed for Intervention | Intervention; Lot | F5 material use | delivery/installation events | Complete |
| Contractor/nursery/technician/inspector responsibility | Person/Organization; Intervention | F1 Intervention assignment | execution/acceptance events | Complete |
| Reserved nursery/contractor/inspector/finance capacity | Person/Organization; Intervention; optional Lot | F6 | reserve/release/reallocate events | Complete |
| Named-action readiness | all relevant nouns/relations | — | derived action-specific computation | Complete |
| Field dispatch and execution | Intervention; assigned actors; scope subjects | — | consequential events | Complete |
| Compulsory legal acceptance | Organization/Person; Intervention/Proceeding | F1 acceptance authority; F3 basis | acceptance outcome | Complete |
| Funded-work administrative acceptance | Organization/Person; Intervention/Proceeding | F1/F3 | acceptance outcome | Complete |
| Private contractual acceptance/warranty/aftercare | actors; Intervention; Instrument | F1 responsibility; F3 contractual effect | acceptance/defect/cure events | Complete |
| Claim, admitted amount and liquidation | right holder; Proceeding; F7 right | F7 | claim/review/liquidation events | Complete |
| Payment order versus bank settlement | right holder; Proceeding; Organizations | F7 persists | accounting/order/settlement outcomes | Complete |
| Audit, revocation and recovery | right holder; Proceeding; Instrument | F3 changes right; F7 exposure/right | audit/revocation/recovery events | Complete |
| Early survival, defect, replacement or cure | Intervention; Plant/Parcel; responsible actors | F5 scope; F1 responsibility; F3 contract/duty | observations and outcomes | Complete |
| Individual Plant inventory identity | Individual Plant; Parcel | contextual Plant–Parcel location | identity-resolution evidence and observation events | Complete |
| Official/observed Plant correspondence | Individual Plant | — | identity resolution/provenance, not real relationship | Complete |
| Municipality as publication/asset/enforcement/permit actor | Organization; relevant Proceeding/Intervention/Instrument | F1 role and F3 authority basis | publication/decision/execution events | Complete |
| Selective reopening after later event | affected nouns/relationships | existing owner unchanged | event dependency and derived impact set | Complete |

## Exhaustiveness findings

### No additional noun is justified

Every accepted persistent real-world subject maps to one of the 13 nouns. Missing future representations are events/outcomes, contextual links, derived computations or evidence—not omitted persistent subjects.

Potential additions rejected:

- **Event/Decision/Observation:** occurrences, not enduring subjects under Gate 3’s rule.
- **Entitlement/Commitment/Assignment:** relationship facts already owned by F1/F6/F7.
- **Application/Claim/Permit:** Public Proceeding instances where the authority preserves matter identity; otherwise events/records.
- **Cohort/Portfolio:** derived sets unless a real governing process independently preserves identity.
- **Contractor/Nursery/Authority/Member:** contextual Organization/Person roles.
- **Tree observation or crown:** evidence/observation supporting an Individual Plant, not another plant noun.

### No eighth relationship family is justified

All independent fact-bearing relations map to F1–F7 after applying predicate-level placement rules.

Candidates rejected:

- **Proceeding subject/participation family:** participation with independent actor authority belongs to F1; consequential governed subject scope belongs to F3; basic subject context remains direct; submitted/decided scope changes remain events.
- **Plant provenance/location family:** Plant–Parcel location is contextual; official correspondence is identity resolution; Lot provenance is contextual classification or traceability evidence unless Intervention use (F5) or commitment (F6) owns independent facts.
- **Acceptance family:** authority belongs to F1/F3; acceptance itself is an outcome; residual duty/warranty belongs to existing F1/F3/F5 facts.
- **Payment family:** durable right belongs to F7; claim, accounting, order and settlement are events/outcomes.
- **Observation family:** observations provide evidence and can trigger events; they are not relations between enduring business subjects.

## Mutual-exclusivity corrections required

1. **Families must never be implementation types by default.** Each implemented predicate must state its exact endpoints and proposition. Generic ActorAssignment, GoverningEffect or InterventionScope abstractions are not licensed merely by the family names.
2. **F1 and F3 require dual-fact discipline.** F3 owns the Instrument’s effect. F1 owns the continuing actor assignment created or evidenced by it. One source can establish both; one relation cannot silently substitute for the other.
3. **F3 and F7 require dual-fact discipline.** F3 owns the creating/amending/revoking legal effect. F7 owns the resulting durable member-specific right. A concession event can change both.
4. **F5 and F6 require requirement-versus-commitment discipline.** Required/authorized material belongs to F5. Reserved/firm scarce capacity belongs to F6. Delivery/installation is an event that may update F5 actual scope.
5. **Proceeding context requires a three-way split.** Actor authority → F1. Consequential governed subject scope → F3. Bare navigation → contextual direct link. Submission/decision changes → events/outcomes.
6. **F4 needs authority/evidence qualification.** Scientific host/susceptibility evidence and operative official recognition may describe the same biological pair but have different authority classes and consequences. F3 owns any legal effect.
7. **Temporal change belongs to events, not duplicate relationship states.** A relationship retains its effective interval/history; admission, release, amendment, acceptance and termination are occurrences affecting it.
8. **Eligibility/readiness/status words remain derived or decided outcomes.** They must never become catch-all relationships that duplicate underlying facts.

## Deletion tests

- Delete F1: membership, representation, decision power and responsibility collapse onto endpoints or instruments. Unsafe.
- Delete F2: title, conduction, access and consent become transitive guesses. Unsafe.
- Delete F3: no proposition-specific authority, applicability or amendment history remains. Unsafe.
- Delete F4: host/resistance truth becomes endpoint classification or hidden scientific rule. Unsafe.
- Delete F5: intended/authorized/actual Intervention composition cannot survive Lot, Plant or Parcel changes. Unsafe.
- Delete F6: requirements and availability falsely imply real capacity commitment. Unsafe.
- Delete F7: eligibility, concession and payment events falsely stand in for a durable member-specific right. Unsafe.

No family is redundant.

## Addition tests

A proposed eighth family must identify an accepted operator decision that cannot be answered by:

- one of F1–F7;
- a contextual direct link;
- an event/outcome;
- a derived computation; or
- evidence/identity resolution.

No current candidate passes.

## Gate 5 consequence

Gate 5 can begin representation derivation without reopening Gates 3–4 wholesale. It must first turn the placement rules above into a concrete predicate ledger. Every proposed Ontology object/link/relationship object must show:

- the accepted noun or exact concrete relationship predicate it represents;
- which operator proposition requires it;
- why a contextual link, event or derived result is insufficient;
- what duplicate owner was rejected;
- which of the 11 anti-collapse grains tests it.

# Gate 5 relationship compression B — F5–F9 and predicates 9–16

**Status:** semantic-uniformity adjudication candidate  
**Date:** 22 August 2026  
**Scope:** Formal Proceeding subject/scope; Intervention physical/material scope, specification, responsibility/authority and capacity; member rights; Intervention Lot use; Lot allocation/custody/control/warranty/return  
**Authorities:** `REDESIGN_SEQUENCE.md`; `gate-5-core-ontology.md`; `gate-5-reground.md`; `gate-3-noun-candidates.md`; `gate-4-relationship-candidates.md`; `gate-5-relationship-representation-ledger.md`; `gate-5-integrated-candidate-synthesis.md`; `palantir-ontology-current-grounding.md`

## Decision rule

A fact-bearing accepted predicate remains an exact object-backed relationship. Candidate predicates may share one backing object type only when all six accepted dimensions are materially uniform:

1. endpoint types;
2. relationship fact shape;
3. lifecycle;
4. authority boundary;
5. Action meaning; and
6. security meaning.

A controlled kind is admitted only after all six dimensions match. Different values, dates, quantities or phases inside one uniform lifecycle do not themselves require a split. A material difference in any dimension does. Deletion is the final check: deleting a proposed fact object must have one coherent domain consequence; if the deletion consequences differ, the candidate is split.

“Actions” below means the governed operation that creates, changes or relies on the relationship, not a CRUD form. “Security” records the domain meaning that later controls must preserve; it does not choose a Gate 6 security implementation. Every object-backed relationship may expose concise endpoint traversal and detailed traversal through its backing object as two views of one truth.

## Smallest retained exact relationship object-type inventory

1. **Public Proceeding Subject Scope**
2. **Intervention Parcel Scope**
3. **Intervention Plant Scope** — conditional on valid Individual Plant identity
4. **Intervention Cultivar Specification**
5. **Intervention Organism Specification**
6. **Intervention Responsibility** — controlled `responsibilityKind`: management, execution, warranty, aftercare
7. **Intervention Inspection Authority**
8. **Intervention Acceptance Authority**
9. **Intervention Capacity Commitment**
10. **Member Right** — controlled `rightKind`: entitlement, creditor right
11. **Intervention Lot Use**
12. **Lot Allocation**
13. **Lot Custody**
14. **Lot Movement Control**
15. **Lot Warranty Responsibility**
16. **Lot Return Responsibility**

This inventory contains no generic Actor Assignment, Proceeding Relationship, Intervention Scope, Material Relationship, Lot Relationship or other family object. The controlled kinds retained in **Intervention Responsibility** and **Member Right** are licensed by six-dimension uniformity, not by a desire to reduce type count.

## 1. Public Proceeding subject and scope

### Candidate test: claimed/reviewed/admitted/excluded/decided/appealed/audited/enforced/recovery scope

| Dimension | Comparison |
|---|---|
| **Endpoint types** | In every fact-bearing variant, `Public Proceeding` relates to exactly one accepted subject: `Natural Person`, `Organization`, `Agricultural Holding`, `Cadastral Parcel`, `Official Area`, conditional `Individual Plant`, `Plant Trade Unit / Lot`, `Public Programme or Measure`, `Governing Instrument`, or `Intervention`. The allowed endpoint set does not change by scope phase. The backing object must enforce exactly one typed subject endpoint; it may not store an untyped subject id. |
| **Fact shape** | Subject identity, scope posture, quantity or amount where applicable, basis, version, inclusion/exclusion, effective history and unresolved remainder. Differences such as hectares versus money are typed optional scope measures, not different relationship predicates: each answers “what part of this subject did this formal matter concern at this preserved scope posture?” |
| **Lifecycle** | Scope begins with a preserved requested/claimed scope and may be reviewed, admitted, excluded, decided, appealed, audited, enforced or placed into recovery. These are successive or concurrent preserved postures of the same Proceeding–subject relationship. Submission, decision, appeal, audit and recovery occurrences remain event/outcome evidence and do not become relationship kinds. |
| **Authority** | The authority of the identified `Public Proceeding` preserves the scope. A filer may assert requested scope, but only the proceeding’s competent body preserves reviewed/admitted/decided scope. This authority boundary is uniform across subject nouns. |
| **Actions** | `Release an application` may add a claimed version; authority determinations may change the preserved posture only where CORDON is an authorized channel. The relationship edit means “preserve a new formal scope version/posture,” regardless of subject noun. No generic status setter is admitted. |
| **Security** | Proceeding-record access and subject-specific sensitivity apply to every row. The exact subject link may further restrict visibility, but that is row-level domain security on the same fact class, not a new semantic type. |
| **Deletion consequence** | Deleting a row loses which exact subject and quantum/basis the formal matter claimed, reviewed, included, excluded or decided at that version. It does not delete the Proceeding, subject, physical Intervention scope, Instrument effect or resulting durable right. |
| **Verdict** | **CONSOLIDATE** scope postures and allowed subject nouns into **Public Proceeding Subject Scope**. A controlled `scopePosture` is permitted. Do not split by claimed/reviewed/decided phase or by subject noun because all six relationship dimensions remain the same. Enforce exactly one typed subject endpoint. |

**Factless boundary:** a bare “this Proceeding concerns this subject” pointer owns none of the facts above and remains a direct contextual link. It is not a second stored link when it is merely the concise traversal of Public Proceeding Subject Scope.

## 2. Intervention physical scope

### Candidate test: Parcel and Plant scope in one object

| Dimension | `Intervention` ↔ `Cadastral Parcel` | `Intervention` ↔ `Individual Plant` |
|---|---|---|
| **Endpoint types** | Parcel is an unconditional legal land unit. | Plant is a conditional biological individual admitted only when stable identity satisfies Gate 3. |
| **Fact shape** | Included/excluded land extent or share, purpose, basis, scope version and residual Parcel area. | Targeted/included individual, treatment/removal/installation role, count-equivalent of one, identity qualification and unresolved individual disposition. |
| **Lifecycle** | Can persist through design, authorization, execution and as-built reconciliation while the Parcel continues independently. Partial area and boundary amendments are normal. | Begins only after valid Plant identity exists; may end through removal, replacement, cure or loss of identity continuity. Individual-by-individual reconciliation is required. |
| **Authority** | Land scope is established by order, concession, technical design, permit or authorized change and is constrained by Parcel rights. | Plant scope can be established by plant-health order, validated inventory, technical design or field process and is constrained by individual-plant identity and plant-grain official decisions. |
| **Actions** | `Certify Technical Intervention Design`, `Dispatch an Intervention` and `Attest Intervention performance` consume area/Parcel scope. | The same semantic Actions consume Plant targets only where identity is valid; replacement/cure and individual inspection consequences can change the relationship without changing Parcel scope. |
| **Security** | Parcel/title/access and member-land restrictions govern exposure. | Individual health, monumental status, official monitoring and fine-grain field evidence can require different visibility from the containing Parcel. |
| **Deletion consequence** | Loses which legally referenced land and extent the undertaking included. | Loses which validly identified individual was targeted/included and its independently preserved role. |
| **Verdict** | **SPLIT: Intervention Parcel Scope.** | **SPLIT: Intervention Plant Scope**, conditional on valid Individual Plant identity. |

**Decision:** Parcel and Plant scopes **cannot share**. Endpoint, fact-shape, lifecycle, authority and security differences are material. Intended, authorized and independently preserved as-built posture remain versions/facts within each endpoint-specific type; they are not three separate relationship types.

## 3. Intervention biological/material specification

### Candidate test: Cultivar and Organism specification in one object

| Dimension | `Intervention` ↔ `Cultivar` | `Intervention` ↔ `Organism Taxon or Lineage` |
|---|---|---|
| **Endpoint types** | Recognized cultivated variety. | Scientific/official taxon or lineage at the grain used by the governing decision. |
| **Fact shape** | Design composition, planting/material role, quantity or proportion, substitution boundary and residual requirement. | Biological target/input role, exact taxonomic grain, purpose and qualification; it does not state susceptibility/resistance, which remains Pathogen–Host Response. |
| **Lifecycle** | Design specification persists through supplier and Lot substitution and is reconciled against as-built composition. | Target/input specification persists while biological/legal classification may be revised; a lineage correction can selectively reopen the specification. |
| **Authority** | Authorized technician and applicable programme/instrument establish the planting design; cultivar legality remains a separate Instrument effect. | Competent plant-health or technical authority establishes the exact target/input grain; biological evidence does not by itself grant legal authority. |
| **Actions** | `Certify Technical Intervention Design` fixes or amends cultivar composition; `Attest Intervention performance` reports conformance. | `Certify Technical Intervention Design` fixes a target/input; later official or technical correction can change it. The meaning and admissible evidence differ from material-composition certification. |
| **Security** | Commercial/technical design and supplier-substitution sensitivity. | Plant-health, laboratory or regulated-organism sensitivity and proposition-specific authority. |
| **Deletion consequence** | Loses the approved variety composition and substitution limits. | Loses the exact biological target/input and taxonomic qualification. |
| **Verdict** | **SPLIT: Intervention Cultivar Specification.** | **SPLIT: Intervention Organism Specification.** |

**Decision:** Cultivar and Organism specifications **cannot share**. They are not one generic Material Specification: the endpoints and fact semantics differ materially, and an Organism target is not plant material merely because both participate in technical design. Lot identity remains excluded and is owned by Intervention Lot Use.

## 4. Intervention responsibilities and authorities

### Candidate test A: management, execution, warranty and aftercare responsibility

| Dimension | Uniform result across the four kinds |
|---|---|
| **Endpoint types** | `Natural Person` or `Organization` ↔ `Intervention` for management, execution, warranty and aftercare alike. |
| **Fact shape** | Responsible actor, controlled responsibility kind, assigned scope, basis, effective period, duties, limits, handoff/termination conditions and unresolved responsibility. Each kind states an affirmative duty to perform or secure work, not a power to judge another actor’s work. |
| **Lifecycle** | Each is an assignment that is created by an operative basis, becomes effective for a bounded period/scope, may be amended or handed off, and ends by fulfillment, replacement or termination. Different start/end dates are values inside this common assignment lifecycle. Warranty and aftercare may continue after installation; that timing difference does not change the lifecycle grammar. |
| **Authority** | The actor or body holding real contracting/assignment authority under the governing contract, protocol, order or public-asset responsibility assigns all four. The assigned actor does not gain powers beyond the recorded kind/scope. |
| **Actions** | One cohesive relationship operation—assign, amend, hand off or end an Intervention responsibility—has the same governance meaning for all four kinds. Downstream Actions consume different kinds (`Dispatch an Intervention` uses management; `Attest Intervention performance` uses execution; defect/aftercare work consumes warranty/aftercare), but those consumers do not mutate the predicate into a different relationship. |
| **Security** | Private/public operational responsibility, contract/protocol terms and named personnel are protected under the same role-and-Intervention domain boundary. A kind may filter access but does not carry a different authority-grade disclosure meaning. |
| **Deletion consequence** | Deletion loses who was affirmatively responsible for the named kind, scope and period. In all four cases it leaves an orphaned operational duty but does not erase an inspection finding or binding acceptance power. |
| **Verdict** | **CONSOLIDATE** as **Intervention Responsibility** with controlled `responsibilityKind = management | execution | warranty | aftercare`. This is a coherent domain relationship, not generic Actor Assignment. |

### Candidate test B: inspection authority and acceptance authority

| Dimension | Intervention Responsibility | Intervention Inspection Authority | Intervention Acceptance Authority |
|---|---|---|---|
| **Endpoint types** | `Natural Person` or `Organization` ↔ `Intervention`. | Same endpoint alternatives. | Same endpoint alternatives. |
| **Fact shape** | Duty to manage, perform, warrant or provide aftercare within scope. | Power/duty to examine evidence or work and record findings/admissible quantities; no inherent power to make the final binding acceptance decision. | Power to determine a route-specific legal, public-funding or contractual acceptance outcome and its accepted/admissible scope. |
| **Lifecycle** | Assignment spans operational performance or post-work obligation. | Authority exists for defined inspection/review occasions and may recur. | Authority is attached to the route and decision level; it survives until the bounded acceptance decision, reopening or replacement of authority. |
| **Authority** | Contracting/assigning party, protocol, order or asset manager. | Competent inspector, technician or public control body for examination only. | Competent official authority, assigned public control body or contractually assigned private acceptor; a handoff or inspection does not transfer this power. |
| **Actions** | Assignment/handoff operation; downstream management, attestation, warranty and aftercare work. | Governs who may create the authoritative examination in a `Field Inspection or Acceptance Occurrence`; cannot submit the binding acceptance decision merely by being inspector. | Governs `Decide route-specific Intervention acceptance`; route-specific acceptance powers remain separate and cannot be inferred from execution or inspection. |
| **Security** | Operational/contractual responsibility information. | Protected inspection evidence and reviewer identity; read access need not confer decision power. | Decision-grade authority and outcome access, potentially official/public-funding or private-contractual; write authority is narrower than inspection access. |
| **Deletion consequence** | Loses the actor owning an operational duty. | Loses who was competent to inspect and validate findings; existing acceptance authority is unaffected. | Loses who could make the binding acceptance decision; inspection competence and findings remain but cannot substitute. |
| **Verdict** | Retain consolidated **Intervention Responsibility**. | **SPLIT: Intervention Inspection Authority.** | **SPLIT: Intervention Acceptance Authority.** |

**Decision:** management, execution, warranty and aftercare **can share** because the relationship operation is uniformly an affirmative scoped responsibility assignment. Inspection and acceptance **must split from that responsibility and from each other**. The accepted rule that execution does not imply acceptance is thereby structural, and inspection evidence cannot silently confer acceptance power.

## 5. Intervention scarce-capacity commitment

### Candidate test: tentative reservation, firm commitment and scheduled capacity

| Dimension | Comparison and result |
|---|---|
| **Endpoint types** | Capacity-owning `Natural Person` or `Organization` ↔ `Intervention`; an optional `Plant Trade Unit / Lot` link is allowed only when the same commitment earmarks identified stock. |
| **Fact shape** | Capacity kind, quantity/slot, period, commitment stage/firmness, prerequisites, expiry, release condition, substitution, protected amount and reallocation consequence. |
| **Lifecycle** | Tentative, time-bounded reservation, firm commitment, scheduling, expiry, release and reallocation are states/transitions of one actual commitment lifecycle. Availability, requirements and recommendations are not early states of the relationship. |
| **Authority** | The actor with actual contracting/capacity authority creates the commitment; the authorized cooperative role commits, overrides, releases or reallocates within governance. Public eligibility or a CORDON recommendation creates no commitment. |
| **Actions** | `Commit or rebalance a capacity portfolio` creates/amends/releases these facts atomically and records an override reason when applicable. `Dispatch an Intervention` consumes firm/scheduled commitment without redefining it. |
| **Security** | Cooperative portfolio, supplier/contractor capacity and override reasoning share one commercially and governance-sensitive boundary. Identified stock can add Lot restrictions to that row without creating a second capacity truth. |
| **Deletion consequence** | Loses actual earmarking and the constraint it placed on this and competing Interventions. It does not delete a capacity requirement, availability estimate, portfolio recommendation, Lot use or Lot custody. |
| **Verdict** | **CONSOLIDATE lifecycle stages** into **Intervention Capacity Commitment** with controlled commitment stage/firmness. Do not split reservation, firm commitment and scheduled capacity into types. |

## 6. Member entitlement and creditor right

### Candidate test: one member-right object or separate entitlement/right types

| Dimension | Uniform result |
|---|---|
| **Endpoint types** | Holder/creditor `Natural Person`, `Organization` or `Agricultural Holding` ↔ exact context among `Public Programme or Measure`, `Public Proceeding`, `Governing Instrument` or `Intervention`. Entitlement and creditor-right variants use the same endpoint alternatives and exactly one holder plus one governing context. |
| **Fact shape** | Holder/creditor identity, controlled right kind, awarded scope, amount/ceiling, permitted claim stages, conditions, effective period, assignment state, guarantee/recovery exposure and remaining right. A creditor right is the payment/recovery-bearing legal posture of the same member-specific right grain, not a generic actor role. |
| **Lifecycle** | Created by a concession or other operative effect, persists through claims, holds, liquidation, payment attempts, settlement, audit and recovery, and ends through exhaustion, valid assignment, revocation/discharge or expiry. Entitlement and creditor-right labels mark legal posture/kind within that shared lifecycle. |
| **Authority** | The competent programme/proceeding/instrument decision creates or changes the member-specific right. The member or authorized representative may release a claim but cannot manufacture the public right. F3 remains the owner of the creating/limiting/discharging Instrument effect. |
| **Actions** | `Release a payment claim` consumes the right and permitted stage but does not create the right. External concession, liquidation, assignment, revocation or recovery outcomes update the same fact grain only under their competent authority. |
| **Security** | Member-specific financial/legal scope, amount, bank/claim exposure and assignment are protected under one beneficiary/right-holder boundary. Right kind does not justify duplicate public/private semantic types. |
| **Deletion consequence** | Whether labelled entitlement or creditor right, deletion loses the member-specific holder, scope, ceiling/stages and surviving financial/legal exposure while leaving the creating Instrument effect and cash transactions intact. |
| **Verdict** | **CONSOLIDATE** as **Member Right** with controlled `rightKind = entitlement | creditorRight`. Entitlement/right **can share** because all six dimensions and deletion consequence match. Do not create a generic Entitlement Relationship or duplicate amount/conditions under F3. |

## 7. Lot inclusion or use in an Intervention

| Dimension | Intervention Lot Use |
|---|---|
| **Endpoint types** | `Intervention` ↔ `Plant Trade Unit / Lot`. |
| **Fact shape** | Intended, authorized or independently preserved as-built inclusion/use; quantity/share, purpose, scope version, substitution boundary and unresolved residual. |
| **Lifecycle** | Begins when an identified Lot enters preserved Intervention material scope, may be substituted or reconciled, and ends when use is removed or the final as-built relation is preserved. Reservation may precede it but is a Capacity Commitment, not an early Lot-use state. |
| **Authority** | Authorized technical design/change and grain-sufficient field/contract evidence establish use. Custodian, supplier or movement controller cannot assert Intervention use merely from possession. |
| **Actions** | `Certify Technical Intervention Design` may establish intended/professionally certified use; `Attest Intervention performance` may preserve as-built use. Delivery, installation, substitution and acceptance remain occurrences/outcomes. |
| **Security** | Intervention design, supplier traceability and as-built evidence apply. It is not actor-accountability security and does not reveal unrelated custody periods by default. |
| **Deletion consequence** | Loses which traceable Lot and quantity the undertaking intended, authorized or actually used. It does not erase reservation, movement history, custody, warranty or return responsibility. |
| **Verdict** | Retain exact **Intervention Lot Use**. It cannot consolidate with F9 actor–Lot facts because its endpoints, authority, lifecycle, Actions and deletion consequence differ. |

## 8. Lot allocation, custody, movement control, warranty and return

### Candidate test: one actor–Lot relationship with a controlled kind

All five candidates have endpoint alternatives `Natural Person` or `Organization` ↔ `Plant Trade Unit / Lot`. Endpoint equality alone is insufficient.

| Candidate | Fact shape | Lifecycle | Authority | Actions / occurrences | Security meaning | Deletion consequence | Verdict |
|---|---|---|---|---|---|---|---|
| **Lot Allocation** | Allocated actor, quantity/share, allocation basis, priority/conditions and release rule; allocation need not confer possession or movement power. | Exists from accountable earmarking/assignment until release, transfer, exhaustion or cancellation; can precede movement and custody. | Stock owner, supplier, cooperative or other actor with allocation authority. | Allocation/reallocation/release decision changes the fact; `Plant Material Movement` is not required to create it. Capacity earmarking for a named Intervention remains Intervention Capacity Commitment. | Commercial availability and member/Intervention allocation sensitivity. | Loses who was assigned what quantity and under which allocation conditions, while custody and control remain knowable. | **SPLIT: Lot Allocation.** |
| **Lot Custody** | Physical/legal custodian, quantity, custody basis, location/context, effective period, condition and handoff obligation; custody does not imply title, allocation or movement permission. | Starts on receipt or accepted handoff and ends on transfer/return/loss; multiple sequential custodians form the accountable chain between movement events. | Transferor/recipient records and the governing custody/transport/holding arrangement establish possession/accountability. | `Plant Material Movement` receipt/handoff occurrences begin or end custody; the occurrence is evidence, not the durable between-event fact. | Fine-grain chain-of-custody, location and accountable possession; visibility may be limited to handlers and regulators. | Loses who remained accountable between movements and for what quantity/period. Allocation, movement authority and warranty remain. | **SPLIT: Lot Custody.** |
| **Lot Movement Control** | Actor’s power/duty to authorize, block or condition movement, including phytosanitary/document conditions, territory/route limits and effective period; controller need not possess the Lot. | Persists for the operative control period and can continue across several movements and custodians; may be suspended or superseded by authority action. | Competent plant-health authority, permit holder or contractually empowered controller for the exact movement proposition. | Governs whether a `Plant Material Movement` may occur. Dispatch/receipt events consume the control but do not own it. | Regulatory movement restrictions and decision authority are materially narrower than ordinary commercial custody access. | Loses who could lawfully authorize/block movement and under which conditions; possession history remains but cannot prove movement authority. | **SPLIT: Lot Movement Control.** |
| **Lot Warranty Responsibility** | Warrantor, covered quantity, warranted characteristics, warranty period, exclusions, defect/cure duties and remedy boundary. | Generally begins at delivery/acceptance or another contractual trigger, survives use/transfer as specified, and ends by expiry, cure, replacement, discharge or valid termination. | Governing sale/supply contract, guarantee or protocol assigns the warrantor; private acceptance/defect findings may trigger duties but do not create authority beyond it. | Defect review, warranty decision, cure/replacement and discharge affect the fact. These are not movement-control or custody operations. | Commercial defect, quality and remedy terms can be restricted differently from logistics and regulatory movement records. | Loses who owes the material-quality remedy and its coverage/period while return logistics and custody can remain fully known. | **SPLIT: Lot Warranty Responsibility.** |
| **Lot Return Responsibility** | Actor responsible to arrange, receive, authorize or complete return; return destination/condition, quantity, clock, costs and handoff requirement. | Arises under a return condition or instruction, persists until completed, waived, replaced or left explicitly unresolved, and may begin only after defect/rejection without being identical to warranty. | Contract/protocol, competent authority instruction or accepted handoff terms assign the return duty; the warrantor and return handler may differ. | A return `Plant Material Movement` evidences performance; deciding warranty, authorizing movement and physically holding the Lot are separate operations/powers. | Return routing, counterparty, location and regulatory details can require a different audience from warranty merits or allocation. | Loses the unresolved owner of return logistics and conditions while warranty liability, custody and movement authority remain. | **SPLIT: Lot Return Responsibility.** |

**Decision:** Lot allocation, custody, movement control, warranty and return **cannot share** one controlled-kind object. Although the endpoint alternatives match, fact shape, lifecycle, authority, Action/occurrence relationship, security meaning and deletion consequence all diverge. In particular:

- allocation does not imply possession;
- possession does not imply movement authority;
- movement authority does not imply warranty liability;
- warranty liability does not imply return handling; and
- a return movement occurrence does not reconstruct the durable return responsibility that preceded it.

A `Lot Accountability` or `Plant Material Relationship` object would therefore be a generic family container and is rejected.

## Compression verdict by required test

| Required test | Verdict | Retained types |
|---|---|---|
| Parcel/Plant physical scopes share? | **No — split.** Endpoint grain, fact shape, lifecycle, authority and security differ. | Intervention Parcel Scope; Intervention Plant Scope |
| Cultivar/Organism specifications share? | **No — split.** Material composition and biological target/input are different predicates. | Intervention Cultivar Specification; Intervention Organism Specification |
| Management/execution/warranty/aftercare share? | **Yes — consolidate.** All are affirmative scoped responsibility assignments with one lifecycle, authority and security meaning; use a controlled kind. | Intervention Responsibility |
| Inspection/acceptance share? | **No — mandatory split.** Examination competence and binding decision power have different fact shape, authority, Actions, security and deletion consequence. | Intervention Inspection Authority; Intervention Acceptance Authority |
| Entitlement/creditor right share? | **Yes — consolidate.** They are legal postures/kinds of the same member-specific surviving right grain. | Member Right |
| Lot allocation/custody/control/warranty/return share? | **No — split all five.** Endpoint equality is outweighed by differences on every other dimension. | Lot Allocation; Lot Custody; Lot Movement Control; Lot Warranty Responsibility; Lot Return Responsibility |

## Coverage and anti-collapse checks

| Accepted predicate | Exact retained owner | Exclusions preserved |
|---:|---|---|
| 9. Public Proceeding subject/scope | Public Proceeding Subject Scope | Factless subject pointer remains direct; occurrences, Instrument effect, physical scope and durable right remain separate. |
| 10. Intervention Parcel/Plant physical scope | Intervention Parcel Scope; conditional Intervention Plant Scope | Observation, execution, inspection and acceptance are not scope relationships. |
| 11. Intervention–Cultivar/material specification | Intervention Cultivar Specification; Intervention Organism Specification | Pathogen–Host Response, legal authorization and Lot use remain separate. |
| 12. Intervention actor responsibility/authority | Intervention Responsibility; Intervention Inspection Authority; Intervention Acceptance Authority | Execution never implies inspection or acceptance; inspection never implies acceptance. |
| 13. Intervention scarce-capacity commitment | Intervention Capacity Commitment | Requirement, availability, recommendation, Lot use and custody remain separate. |
| 14. Member-specific entitlement/creditor right | Member Right | Creating Instrument effect, eligibility, claim, accounting order and cash settlement remain separate. |
| 15. Lot inclusion/use in Intervention | Intervention Lot Use | Capacity reservation, actor accountability and movement events remain separate. |
| 16. Lot actor allocation/custody | Lot Allocation; Lot Custody; Lot Movement Control; Lot Warranty Responsibility; Lot Return Responsibility | Intervention use, capacity earmarking and movement/return occurrences remain separate. |

## Final verdict

The minimum exact inventory for predicates 9–16 is **16 domain-named relationship object types**. Two controlled-kind consolidations are accepted: **Intervention Responsibility** for management/execution/warranty/aftercare and **Member Right** for entitlement/creditor-right posture. Public Proceeding scope postures and Capacity Commitment stages remain within one exact lifecycle each. Parcel versus Plant scope, Cultivar versus Organism specification, inspection versus acceptance authority, and each of allocation/custody/movement-control/warranty/return fail semantic uniformity and remain split. No accepted predicate is deleted, no event or status is promoted into a relationship, and no generic family object is introduced.

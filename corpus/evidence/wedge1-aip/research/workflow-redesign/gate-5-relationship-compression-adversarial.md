# Gate 5 relationship compression — adversarial independent derivation

**Status:** adversarial lane result — **PASS-WITH-DECISIONS**  
**Date:** 22 August 2026  
**Scope:** all 16 accepted atomic predicates; relationship backing-object compression only  
**Authorities read:** `REDESIGN_SEQUENCE.md`; `gate-5-core-ontology.md`; `gate-4-relationship-candidates.md`; `gate-5-relationship-representation-ledger.md`; `gate-5-integrated-candidate-synthesis.md`; `palantir-ontology-current-grounding.md`  
**Independence boundary:** no sibling compression-lane output was read.

## Verdict

The smallest defensible **semantic** inventory I can derive is **44 relationship backing-object types**, subject to four Owen decisions at the end of this document. This is not a target type count. It is the result of applying the accepted six-dimension test in both directions:

1. endpoint types or endpoint-role contract;
2. fact shape;
3. lifecycle;
4. authority boundary;
5. Actions;
6. security meaning.

A merge is retained only when all six are materially uniform and the result still names one coherent real relationship. A split is retained when any one dimension is materially different. `kind` may describe states or variants inside a coherent relationship; it may not choose which endpoints exist, which facts apply, who has authority, which Action mutates the object, or which security regime governs it.

The apparent bloat is concentrated in two already-broad atomic predicates, not spread evenly across the model:

- predicate 6 needs eight exact Instrument relationships rather than one hidden `Instrument Effect` God Object;
- predicate 9 needs ten endpoint-specific proceeding-scope types rather than one polymorphic `Proceeding Subject Scope` God Object.

Conversely, role-by-role expansion is not justified for Intervention responsibilities, Parcel permissions, Instrument lineage, scope stages, or Lot custody duties when the six dimensions remain uniform.

## Compression rules used

### Exact ownership rule

Every fact-bearing relationship instance has exactly one backing-object owner. A concise endpoint traversal exposed by an object-backed link is a view of that owner, not a second stored truth. A contextual direct link exists only where the relationship has no independently changing fact. An occurrence, outcome, observation, derived result, classification, co-reference, or transitive shortcut owns none of these relationship facts.

### Conditional-branch rule

A conditional label is decomposed before ownership:

- **factless branch:** one direct link, no backing object;
- **fact-bearing branch:** exactly one type named in the coverage ledger below;
- **invalid Individual Plant branch:** no Plant object and no Plant relationship;
- **optional Lot on a capacity commitment:** the Lot scopes the same commitment; it does not create a second reservation/allocation owner;
- **Instrument as basis of another relationship:** if the Instrument is only evidentiary/constituting context and has no independently surviving effect facts, it is a link from the relationship fact to its basis, not a second predicate-6 object. If a distinct legal effect survives, the applicable predicate-6 type owns it.

## Proposed 44-type inventory

### Actor, holding, and land relationships (7)

1. **Cooperative Membership**
2. **Holding Stewardship**
3. **Holding Representation**
4. **Parcel Tenure**
5. **Parcel Permission**
6. **Holding Parcel Declaration**
7. **Holding Parcel Conduction**

`Parcel Permission` consolidates access authorization and consent only where they are grants of scoped permission with the same actor–Parcel endpoint contract, grant/revoke lifecycle, basis/scope/period facts, authority boundary, Actions, and security meaning. Ownership/title/control remains `Parcel Tenure`.

### Applicability and Governing Instrument relationships (9)

8. **Parcel–Official Area Applicability**
9. **Programme Constituting Instrument**
10. **Programme Funding Instrument**
11. **Official Area Defining Instrument**
12. **Instrument Lineage**
13. **Proceeding Authority Grant**
14. **Instrument-Grounded Parcel Duty**
15. **Instrument-Grounded Parcel Permission**
16. **Intervention Authorization**

Owen accepts separate `Programme Constitution` and `Programme Funding Authority` types. Constitution owns why the Programme exists; Funding Authority owns authorized amount/ceiling, eligible spend, source, period and budget conditions. Ordinary openings/windows remain effective-period facts on their governing Instruments plus a Programme context link unless an independent Programme Operative Window later passes deletion and six-dimensional tests.

### Biological relationships (2)

17. **Pathogen–Taxon Response**
18. **Pathogen–Cultivar Response**

One `Pathogen–Host Response` would need a host-kind switch and mutually exclusive Taxon/Cultivar endpoints. Cultivar-specific susceptibility/tolerance is not merely a taxon response alias, so the endpoint and fact-grain difference forces the split.

### Public Proceeding actor relationships (2)

19. **Proceeding Participation**
20. **Proceeding Decision Authority**

Participation and decision authority cannot share a `roleKind`: powers, authority, Actions, and security are materially different. Factless participant and current-decider pointers remain direct links under the boundary below.

### Public Proceeding subject/scope relationships (10)

21. **Proceeding Person Scope**
22. **Proceeding Organization Scope**
23. **Proceeding Holding Scope**
24. **Proceeding Parcel Scope**
25. **Proceeding Official Area Scope**
26. **Proceeding Plant Scope**
27. **Proceeding Lot Scope**
28. **Proceeding Programme Scope**
29. **Proceeding Instrument Scope**
30. **Proceeding Intervention Scope**

A single `Proceeding Subject Scope` fails the test: `subjectKind` would select mutually exclusive endpoints; amount, area, quantity, identity, and legal-text scope have different fact shapes; person/member scope has different security meaning from public Area/Instrument scope; and the admitting/reviewing Actions differ. Within each endpoint-specific type, claimed, reviewed, admitted, excluded, decided, appealed, audited, enforced, and recovery are preserved as stage/version facts of the same proceeding–subject scope relationship, not separate role-named object types.

`Proceeding Plant Scope` is instantiated only when the Individual Plant identity boundary is satisfied.

### Intervention physical/material relationships (6)

31. **Intervention Parcel Scope**
32. **Intervention Plant Scope**
33. **Intervention Cultivar Specification**
34. **Intervention Organism Specification**
35. **Intervention Delivery Responsibility**
36. **Intervention Review Authority**

`Intervention Plant Scope` is conditional on valid Individual Plant identity. Intended, authorized, independently preserved as-built, and residual scope are facts/versions on one endpoint-specific scope owner, not parallel links.

Management, execution, warranty, and aftercare consolidate into `Intervention Delivery Responsibility` only as scoped performance duties assigned through the same responsibility lifecycle and security boundary. Inspection and acceptance consolidate into `Intervention Review Authority` only as independent review/decision powers. Crossing those two groups would let `kind` conceal materially different authority and Actions.

### Capacity, rights, use, allocation, and custody relationships (8)

37. **Intervention Capacity Commitment**
38. **Member Entitlement**
39. **Creditor Right**
40. **Intervention Lot Use**
41. **Lot Allocation**
42. **Lot Custody**
43. **Lot Warranty Responsibility**
44. **Lot Return Responsibility**

Movement/receipt/dispatch control during possession is a duty on `Lot Custody`, not another type. Allocation is an earmarking relationship, custody is accountable possession/control, warranty is a post-supply obligation, and return responsibility is a disposition obligation; they differ in lifecycle, authority, Actions, and frequently security. `Member Entitlement` and `Creditor Right` remain split because a public/member entitlement and an enforceable creditor right do not have the same creation, discharge, recovery, or accounting lifecycle.

## Exact 16-predicate coverage and sole ownership

| # | Atomic predicate | Fact-bearing branches | Exactly one backing-object owner | Factless/invalid boundary |
|---:|---|---|---|---|
| 1 | Cooperative membership | Person-or-Organization member ↔ cooperative Organization | **Cooperative Membership** | Adhesion/acceptance/withdrawal are occurrences; `active member` is derived. |
| 2 | Holding stewardship or representation | stewardship; legal/administrative representation | **Holding Stewardship**; **Holding Representation** | Appointment/revocation/signature are occurrences. Neither relationship implies Parcel rights. |
| 3 | Actor–Parcel tenure, access or consent | ownership/title/control/occupation; scoped access/alteration consent | **Parcel Tenure**; **Parcel Permission** | A one-off entry occurrence is not permission. Holding stewardship/conduction does not imply either. |
| 4 | Holding–Parcel declaration or conduction | authoritative declaration; operational conduction | **Holding Parcel Declaration**; **Holding Parcel Conduction** | Filing/correction is an occurrence; ownership is predicate 3. |
| 5 | Authority-grounded Parcel–Official Area applicability | deterministic authority/date/rule-grounded applicability | **Parcel–Official Area Applicability** | Raw overlap, buffers, warnings, and unresolved reconciliation are derived/not links. |
| 6 | Governing Instrument effect or lineage | programme constitution; programme funding; Area definition; inter-Instrument lineage; Proceeding authority; Parcel duty; Parcel permission; Intervention authorization | **Programme Constituting Instrument**; **Programme Funding Instrument**; **Official Area Defining Instrument**; **Instrument Lineage**; **Proceeding Authority Grant**; **Instrument-Grounded Parcel Duty**; **Instrument-Grounded Parcel Permission**; **Intervention Authorization** | Bare association is direct context. If an Instrument only supplies the basis of predicates 1–4, 8, 12, or 14 and no separate effect survives, link that sole relationship owner to the Instrument; do not duplicate it as an effect. Additional independently surviving Person/Organization/Holding/Plant/Lot effects are not silently absorbed: they require Owen’s scope decision and a new endpoint-specific type. |
| 7 | Biological pathogen–host response | pathogen ↔ host Taxon; pathogen ↔ Cultivar | **Pathogen–Taxon Response**; **Pathogen–Cultivar Response** | Plant infection/sample is observation. Legal classification is predicate 6. |
| 8 | Public Proceeding actor participation or authority | fact-bearing participation; decision authority | **Proceeding Participation**; **Proceeding Decision Authority** | Bare participant/current-decider navigation is direct. Instrument grant remains predicate 6. |
| 9 | Public Proceeding subject or scope | one branch for each accepted subject endpoint: Person, Organization, Holding, Parcel, Official Area, valid Plant, Lot, Programme, Instrument, Intervention | **Proceeding Person Scope**; **Proceeding Organization Scope**; **Proceeding Holding Scope**; **Proceeding Parcel Scope**; **Proceeding Official Area Scope**; **Proceeding Plant Scope**; **Proceeding Lot Scope**; **Proceeding Programme Scope**; **Proceeding Instrument Scope**; **Proceeding Intervention Scope** | A factless `concerns` pointer is direct. Invalid/unidentified Plant creates no Plant branch. Filing/decision/appeal/audit/recovery occurrences are not scope. |
| 10 | Intervention Parcel or Plant physical scope | Intervention ↔ Parcel; Intervention ↔ valid Plant | **Intervention Parcel Scope**; **Intervention Plant Scope** | Observed footprint/count is evidence. Invalid Plant identity leaves scope at Parcel/quantity/Lot grain. |
| 11 | Intervention–Cultivar or material specification | Intervention ↔ Cultivar; Intervention ↔ Organism Taxon/Lineage | **Intervention Cultivar Specification**; **Intervention Organism Specification** | Cultivar legality is predicate 6; biological response is predicate 7; identified Lot is predicate 15. |
| 12 | Intervention actor responsibility or authority | management/execution/warranty/aftercare duty; inspection/acceptance power | **Intervention Delivery Responsibility**; **Intervention Review Authority** | Contract award, execution, inspection, acceptance, defect, and termination are occurrences/outcomes. Capacity is predicate 13. |
| 13 | Intervention scarce-capacity commitment | actor capacity ↔ Intervention, with optional identified Lot scope | **Intervention Capacity Commitment** | Availability, requirement, score, recommendation, and portfolio are derived. The optional Lot is linked to this same commitment; no second reservation/allocation object is created. |
| 14 | Member-specific entitlement or creditor right | durable member/public entitlement; enforceable creditor right | **Member Entitlement**; **Creditor Right** | Eligibility, ranking, concession occurrence, claim, liquidation, payment order, settlement, audit, revocation, and recovery are not the right. Creating Instrument effect is predicate 6 only when independently fact-bearing. |
| 15 | Lot inclusion or use in Intervention | intended/authorized/as-built Lot inclusion/use | **Intervention Lot Use** | Reservation is predicate 13; custody is predicate 16; movement/installation/substitution/acceptance are occurrences. |
| 16 | Lot actor allocation or custody | quantity allocation; custody/movement control; warranty duty; return duty | **Lot Allocation**; **Lot Custody**; **Lot Warranty Responsibility**; **Lot Return Responsibility** | Dispatch, movement, receipt, handoff, and return are occurrences. Producer/origin and Cultivar classification are contextual where factless. |

**Coverage check:** predicates covered = **16/16**. Proposed backing-object types = **44**. Every listed fact-bearing branch maps to exactly one type. No type owns branches from two atomic predicates.

## Direct-link boundary ledger

These links are admitted only while factless. If the named boundary is crossed, the corresponding backing object above replaces the direct truth; it does not coexist with a separately stored duplicate.

| Direct relationship | Keep direct only while | Reclassification owner if facts appear |
|---|---|---|
| Individual Plant ↔ Cultivar | endpoint classification only and Plant identity is valid | biological response → predicate 7; Intervention design → predicate 11 |
| Lot ↔ Cultivar | endpoint classification only | Intervention specification/use → predicates 11/15 |
| Plant or Lot ↔ originating Organization | producer/origin pointer only; no accountable quantity, period, handoff, warranty, traceability, or geographic-origin facts | predicate 16 where actor–Lot accountability exists; otherwise selective Gate 4 reopening for a new exact origin predicate |
| Proceeding ↔ Programme | context only | **Proceeding Programme Scope** for independently changing scope; predicate 6 for normative Instrument effect |
| Proceeding ↔ any subject | `concerns` only; no claimed/reviewed/admitted/decided quantity, amount, extent, basis, version, or history | the endpoint-specific predicate-9 owner |
| Proceeding ↔ participant | navigation only; no role, basis, period, powers, duties, or history | **Proceeding Participation** |
| Proceeding ↔ current deciding Organization | current pointer only; no authority basis/scope/history | **Proceeding Decision Authority**; Instrument grant separately belongs to predicate 6 when independently fact-bearing |
| Instrument ↔ Programme | context only after consequential constitution/funding is owned once | **Programme Constituting Instrument** or **Programme Funding Instrument** |
| Instrument ↔ Proceeding | context only | **Proceeding Authority Grant** or endpoint-specific predicate-9 scope, depending on the fact |
| Instrument ↔ Intervention | context only | **Intervention Authorization** |
| Instrument ↔ Official Area | context only | **Official Area Defining Instrument** |
| Intervention ↔ Programme | context only; asserts no eligibility, concession, entitlement, funding, or payment | **Member Entitlement** where a durable holder right exists; predicate 6 for a distinct normative effect |
| Intervention ↔ Proceeding | context only | **Proceeding Intervention Scope** where scope changes independently |

No direct link is admitted for geometry-only Parcel–Area overlap, inferred programme applicability, feasible portfolios, expected-loss relationships, remote observations beyond validated grain, identity-resolution candidates, source foreign keys, or any transitive shortcut.

## Adversarial merge findings — over-splitting rejected

1. **Intervention roles — ACCEPTED THREE-TYPE MODEL.** Owen consolidates management, execution, warranty and aftercare as kinds of `Intervention Responsibility`. `Intervention Inspection Authority` separately owns examination competence. `Intervention Acceptance Authority` separately owns binding compulsory, public-funding or private-contractual acceptance power. Inspection never implies acceptance, and the same actor may hold both relationships.
2. **Do not split scope by intended/authorized/as-built/accepted labels.** For one endpoint-specific relationship, those are preserved scope assertions/stages/versions. Parallel links would duplicate one physical/material relationship and make disagreement impossible to represent cleanly.
3. **Instrument lineage — ACCEPTED THREE-WAY SPLIT.** Owen accepts separate Instrument Amendment, Instrument Supersession and Instrument Stay types because alteration, displacement and temporary suspension have materially different lifecycle, operative consequence and deletion loss. Generic Instrument Lineage is rejected. Annulment, interpretation/construction and termination require selective reopening; a self-contained end date remains an Instrument property.
4. **Parcel Access Authorization and Parcel Consent — ACCEPTED SPLIT.** Owen keeps affirmative assent separate from operative entry/work permission. Consent may ground Access Authorization but does not prove it; compulsory/public authorization can exist without private consent. Different giver/beneficiary shape, authority, prerequisites, lifecycle, Actions and dispatch consequences prohibit `Parcel Permission` consolidation.
5. **Lot Movement Control — ACCEPTED SEPARATE TYPE.** Owen keeps movement authority separate from custody. Custodians do not automatically gain power to authorize or block movement; one regulator/controller can govern several custodians. Plant Material Movement events consume or change control/custody facts but do not replace them.
6. **Do not split a Lot-earmarked capacity commitment from a non-Lot commitment.** The commitment remains actor ↔ Intervention; an identified Lot is optional resource scope on the same fact. Creating both `Capacity Commitment` and `Lot Reservation` would double-own reservation.
7. **Do not split Proceeding scope by claimed/reviewed/admitted/excluded/decided/audited stage.** Preserve multiple stage/version records inside the one endpoint-specific scope relationship, provided Owen confirms the lifecycle model below.

## Adversarial split findings — hidden God Objects rejected

1. **`Governing Instrument Effect` is a God Object.** `effectKind` would choose Programme/Area/Instrument/Proceeding/Parcel/Intervention endpoints and incompatible financial, geometric, lineage, authority, duty, permission, and authorization facts. Eight exact types are the current bounded minimum.
2. **`Proceeding Subject Scope` is a God Object.** `subjectKind` would choose ten endpoint types and materially different amount/quantity/extent/security/Action semantics. Ten endpoint-specific types are required unless Owen accepts a real interface contract and proves uniform security and Actions.
3. **`Pathogen–Host Response` hides a polymorphic host.** Taxon-level host status and cultivar-specific response must not share mutually exclusive endpoint fields.
4. **`Intervention Actor Assignment` hides authority.** Responsibility duties, inspection competence and binding acceptance power have different decision rights and Actions. Owen accepts separate Responsibility, Inspection Authority and Acceptance Authority types.
5. **`Parcel Right` is too broad at current evidence.** Registry/tenure rights and revocable operational permission have different authority, lifecycle, Actions, and security. `Parcel Tenure` and `Parcel Permission` remain split.
6. **`Plant Material Relationship` is a God Object.** Allocation, custody, movement control, warranty and return responsibility do not share lifecycle, authority or Actions. Owen accepts all five as separate exact types.
7. **`Member Entitlement or Creditor Right` cannot be one kinded type.** Public/member entitlement and creditor right differ in creation, claimability, discharge, recovery exposure, and accounting authority.
8. **One actor-union relationship type is a latent implementation risk.** The 44-type count treats `Natural Person or Organization` as one materially uniform actor endpoint role at the semantic level. A backing type implemented with `actorKind` plus mutually exclusive Person/Organization links would violate the rule unless the platform design supplies a genuine shared actor contract and aligned security.

## Owen decisions required

### D1 — Person/Organization endpoint contract — **ACCEPTED**

Owen accepts one narrow `Decision-Capable Actor` Interface implemented by `Natural Person` and `Organization`. One semantic relationship type may accept either concrete actor endpoint only when fact shape, lifecycle, authority, Actions and security meaning remain materially identical. Concrete actor identity remains visible. A material difference requires a relationship-level split.

- **Accept:** retain the 44-type semantic inventory; later implementation must prove a genuine actor endpoint contract.
- **Reject / concrete-endpoint strict:** split every actor-union type. The inventory rises from **44 to 62**: membership +1; stewardship/representation +2; tenure/permission +2; Proceeding participation/authority +2; Intervention delivery/review +2; capacity +1; entitlement/creditor across Person/Organization/Holding +4; four Lot relationships +4.

This cannot be decided by type-count preference. Person-level privacy and Organization-level visibility may itself force the strict branch.

### D2 — Predicate 6 finite core — **ACCEPTED**

Owen accepts a finite F3 core bounded to independently surviving effects required by current operator decisions. An Instrument that merely supplies the basis of another sole-owned relationship remains linked as that relationship's basis and does not create duplicate F3 truth. Effects on omitted endpoints require selective reopening, a demonstrated decision loss under basis-only representation, and fresh deletion/six-dimensional tests.

### D3 — Proceeding scope lifecycle — **ACCEPTED AUTHORITY SPLIT**

Owen accepts `Proceeding Claimed Scope` for filer-asserted formal scope and `Proceeding Authority-Determined Scope` for competent-authority scope. Requested/claimed versions remain within the claimed class. Reviewed, admitted, excluded, decided and permitted versions remain within the authority-determined class when authority, Actions and security meaning are uniform. Appeals, audits, enforcement and recovery with independent formal identity are separate Public Proceedings using the same pattern.

Both authority classes specialize by subject endpoint: Person, Organization, Holding, Parcel, Official Area, valid Individual Plant, Lot, Programme, Instrument or Intervention. The resulting 20-type matrix is the maximum semantic inventory. An exact endpoint type enters the deployable core only when current workflows and grain-sufficient evidence require fact-bearing scope. Factless subject context remains a direct link.

### D4 — Entitlement/right primary scope — **ACCEPTED SPLIT**

Owen accepts `Member Entitlement` and `Creditor Right` as separate relationship types. Member Entitlement links a beneficiary Decision-Capable Actor to Public Programme or Measure and owns the support right, ceiling, claim stages, conditions and remaining entitlement. Creditor Right links a creditor Decision-Capable Actor to debtor Organization and owns recognized payable debt, due/accounting basis, discharge and outstanding amount. Awarding/payment Proceedings and Instruments, Agricultural Holding and Intervention remain basis/scope links. Cash Settlement Transaction remains independent proof of cash. A direct Holding-level holder requires selective direct evidence.

## Acceptance recommendation

**PASS-WITH-DECISIONS.** The 16-predicate coverage is exact and ownership-complete under the four stated assumptions. Accepting the 44 names as final before D1–D4 would be premature. Reject any lower-count proposal that reaches its number through `actorKind`, `subjectKind`, `affectedKind`, or `relationshipKind` while changing endpoints, fact columns, lifecycle, authority, mutating Actions, or security. Also reject any higher-count proposal that merely turns role, stage, or lineage labels into types without demonstrating a material difference on one of the six accepted dimensions.

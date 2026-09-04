# Gate 5 relationship compression A — F1–F4 and predicate 8

**Status:** independent semantic-uniformity recommendation  
**Date:** 22 August 2026  
**Scope:** predicates 1–7 and predicate 8 only: F1 cooperative membership, Holding stewardship/representation, and Public Proceeding actor participation/authority; F2 actor–Parcel and Holding–Parcel relations; F3 Parcel–Official Area applicability and Governing Instrument effects/lineage; F4 pathogen–host response. F1 Intervention responsibility (predicate 12) and F5–F9 are outside this compression pass.  
**Authorities:** `REDESIGN_SEQUENCE.md`; `gate-5-core-ontology.md`; `gate-5-reground.md`; `gate-3-noun-candidates.md`; `gate-4-relationship-candidates.md`; `gate-5-relationship-representation-ledger.md`; `gate-5-integrated-candidate-synthesis.md`; `palantir-ontology-current-grounding.md`.

## 1. Controlling test and interpretation

Gate 5 permits exact predicates to share one domain-named relationship object type only when all of the following are materially identical:

1. endpoint types;
2. fact shape;
3. lifecycle;
4. authority boundary;
5. Actions that create, change, terminate, or consume the relationship; and
6. security meaning.

A controlled `kind` is allowed only after all six match. It cannot repair a mismatch. Deletion consequence is used as the final semantic check: if deleting the proposed shared object would erase two different claims or two differently governed histories, the candidate must split.

“Endpoint match” is evaluated by semantic endpoint slot, not by forcing a generic `Actor` object. A relationship may retain one exclusive actor slot fulfilled by either `Natural Person` or `Organization` when the actor substitution changes none of the other five dimensions. The backing object must link to exactly one concrete actor endpoint. This is not an `Actor` superclass, family object, or role-bearing endpoint. If a concrete workflow gives Persons and Organizations different powers, lifecycle, Actions, or security, that exact relationship must be selectively split later.

This pass does not create a generic `Actor Assignment`, `Parcel Right`, `Instrument Effect`, `Instrument Lineage`, `Biological Relationship`, or `Proceeding Role`. It also does not promote factless Proceeding participant/current-decider pointers into objects.

## 2. Smallest exact inventory

| # | Relationship object type | Exact endpoint slots | Controlled kind admitted? | Why it is the minimum exact owner |
|---:|---|---|---|---|
| 1 | **Cooperative Membership** | member `Natural Person` **or** `Organization` ↔ cooperative `Organization` | Yes, only for membership classes whose six-dimensional contract is identical | Owns the member–cooperative basis, class, scope, effective period, terms, and termination history. Adhesion and withdrawal remain occurrences. |
| 2 | **Holding Stewardship** | steward `Natural Person` **or** `Organization` ↔ `Agricultural Holding` | Yes, only for stewardship kinds with the same operating-duty contract | Owns continuing operational stewardship duties and scope; it does not confer external representative power by implication. |
| 3 | **Holding Representation** | representative `Natural Person` **or** `Organization` ↔ `Agricultural Holding` | Yes, only for representation classes with the same power/scope lifecycle | Owns authority to speak, certify, sign, file, or otherwise bind/act for the Holding within stated scope. |
| 4 | **Parcel Tenure** | tenure holder `Natural Person` **or** `Organization` ↔ `Cadastral Parcel` | Yes, only among evidence-established tenure kinds with the same durable land-right shape | Owns the durable title/lease/usufruct/recognized possessory or equivalent tenure relationship, including share, basis, period, and conflicts. A delegated management permission is not forced into tenure. |
| 5 | **Parcel Access Authorization** | authorized actor `Natural Person` **or** `Organization` ↔ `Cadastral Parcel` | Yes, for access/entry/work authorizations sharing the same permission lifecycle | Owns permission to enter or perform stated acts, its conditions, time window, limits, and revocation. It does not assert tenure. |
| 6 | **Parcel Consent** | consent beneficiary `Natural Person` **or** `Organization` ↔ `Cadastral Parcel`, with consenting actor and/or operative Instrument as required context | No cross-predicate kind; consent purpose may be controlled only within an otherwise uniform consent contract | Owns an affirmative consent at its real grain, including giver, beneficiary, permitted act, conditions, period, and withdrawal/expiry. It does not assert access was exercised or that a broader access authorization exists. |
| 7 | **Holding Parcel Declaration** | `Agricultural Holding` ↔ `Cadastral Parcel` | Yes, only for declaration classes with the same administrative fact shape | Owns the authoritative farm-file/declaration association, declared extent/use, declaration period/version, and correction/conflict basis. |
| 8 | **Holding Parcel Conduction** | `Agricultural Holding` ↔ `Cadastral Parcel` | Yes, only for conduction kinds with the same operational relationship shape | Owns the real agricultural operation/conduction relationship and its period, extent/use, and operational basis. It is not established merely by a filing. |
| 9 | **Parcel Official Area Applicability** | `Cadastral Parcel` ↔ `Official Area`, grounded in the controlling `Governing Instrument`/authority | Yes, only for proposition kinds whose applicability derivation, authority, lifecycle, Actions, and security are identical | Owns authority- and date-grounded applicability, including the relevant proposition, partial-intersection rule, effective period, and conflict/priority basis. Raw overlap remains derived. |
| 10 | **Programme Establishment** | `Governing Instrument` ↔ `Public Programme or Measure` | No cross-effect kind | Owns the Instrument’s constitutive establishment of the Programme. It does not absorb opening, funding, suspension, or closure unless later evidence proves those effects have the same six-dimensional contract—which current authorities do not. |
| 11 | **Official Area Definition** | `Governing Instrument` ↔ `Official Area` | Yes only for create/redraw/classify definition variants that truly share one versioned-definition lifecycle; retirement is not silently included | Owns the authoritative definition and effective scope of an Official Area. It is distinct from Parcel applicability. |
| 12 | **Instrument Amendment** | amending `Governing Instrument` ↔ amended `Governing Instrument` | No cross-lineage kind | Owns a scoped alteration while preserving the amended Instrument’s continuing identity and unaffected force. |
| 13 | **Instrument Supersession** | superseding `Governing Instrument` ↔ superseded `Governing Instrument` | No cross-lineage kind | Owns displacement of operative force, including full/partial scope and effective transition. It is not an amendment label. |
| 14 | **Proceeding Authority Grant** | granting `Governing Instrument` + authority holder `Natural Person` **or** `Organization` + scoped `Public Proceeding` | Yes only for grant kinds with identical powers/lifecycle | Owns the normative grant, limitation, or delegation of authority for the Proceeding. The resulting current actor assignment remains separately owned by **Proceeding Decision Authority** when it has independent assignment facts. |
| 15 | **Parcel Duty** | duty-creating `Governing Instrument` + affected `Cadastral Parcel`, and duty bearer `Natural Person`, `Organization`, or `Agricultural Holding` where the duty is bearer-specific | Yes only for duty kinds with identical obligation lifecycle and enforcement/security meaning | Owns the proposition-specific normative duty, conditions, effective period, bearer/scope, and discharge/termination boundary. It does not duplicate tenure, applicability, or a notice event. |
| 16 | **Intervention Authorization** | authorizing `Governing Instrument` ↔ `Intervention`, with authorized actor where the authorization is actor-specific | Yes only for authorization kinds with identical permission lifecycle | Owns the normative permission/approval for the bounded Intervention, its scope, conditions, period, and withdrawal/expiry. It does not own physical scope or execution. |
| 17 | **Pathogen Taxon Host Response** | pathogen `Organism Taxon or Lineage` ↔ host `Organism Taxon or Lineage` | Yes: host/susceptible/resistant/tolerant response classification may be controlled values | Owns the directed, evidence-qualified biological conclusion at taxon/lineage host grain, including context, qualification, evidence/authority class, and version. |
| 18 | **Pathogen Cultivar Response** | pathogen `Organism Taxon or Lineage` ↔ host `Cultivar` | Yes: susceptibility/resistance/tolerance response classification may be controlled values | Owns the same biological conclusion at cultivar grain without making Cultivar an organism-taxon endpoint or a sparse polymorphic host field. |
| 19 | **Proceeding Participation** | participant `Natural Person` **or** `Organization` ↔ `Public Proceeding` | Yes only for participant-role kinds sharing the same non-decisional participation contract | Owns a fact-bearing role, basis, period, duties, and history of participation. A bare participant pointer remains a direct link. |
| 20 | **Proceeding Decision Authority** | authority holder `Natural Person` **or** `Organization` ↔ `Public Proceeding` | Yes only for decision-authority kinds sharing the same power and assignment lifecycle | Owns instantiated power to decide or legally accept a proposition in the Proceeding, with basis, scope, period, limits, and termination. A factless current-decider pointer remains direct. |

**Inventory verdict: 20 exact relationship object types.** This is smaller than type-per-verb expansion, but it preserves every currently accepted material distinction. The count is not reduced by introducing a generic family object or a sparse union of unlike endpoints.

## 3. Six-dimension consolidation and split ledger

Every consolidation entertained by the candidate authorities, and every split retained by this pass, is resolved below. “Actions” names semantic Gate 5 candidate operations that consume or may change the fact; it does not select platform implementation.

### C1. Natural Person and Organization in one exact actor slot — consolidate conditionally

| Dimension | Comparison |
|---|---|
| Endpoint types | Concrete actor endpoint differs (`Natural Person` versus `Organization`), but each exact relationship has the same single semantic actor slot and the same opposite endpoint. The backing object must link to exactly one concrete actor; no generic Actor object is created. |
| Fact shape | Shared within each exact predicate: basis, role/kind, scope, effective period, limits, and termination. |
| Lifecycle | Shared only where a Person-held and Organization-held instance begins, changes, and ends under the same real relationship lifecycle. |
| Authority | Shared only where the same authority can establish and attest either actor form. |
| Actions | Shared only where the same domain Action consumes or changes the assignment without actor-form-specific effects. |
| Security | Shared only where actor form does not itself change sensitivity or write authority; row-level facts may still be secured later. |
| Deletion consequence | In either actor form, deletion loses one instance of the same exact relationship—not a different predicate. |
| Verdict | **CONSOLIDATE WITH AN EXCLUSIVE TYPED ACTOR ENDPOINT** for Cooperative Membership, Holding Stewardship, Holding Representation, Parcel Tenure, Parcel Access Authorization, Parcel Consent, Proceeding Participation, Proceeding Decision Authority, and actor slots in the F3 grant/duty/authorization facts. **Selective reopening required** if a concrete Person/Organization rule differs on any remaining dimension. |

### C2. All F1 assignments in one Actor Assignment — reject

| Dimension | Comparison |
|---|---|
| Endpoint types | Different opposite endpoints: cooperative `Organization`, `Agricultural Holding`, and `Public Proceeding`. |
| Fact shape | Membership terms; stewardship duties; representative powers; participation role; and adjudicative authority are different claims. |
| Lifecycle | Membership adhesion/withdrawal, stewardship appointment/replacement, representation grant/revocation, participation entry/withdrawal, and decision-authority delegation/termination differ. |
| Authority | Cooperative organs, Holding principals/administration, proceeding rules, and competent public authorities establish different facts. |
| Actions | Membership and assignment evidence is maintained independently; application/claim release consumes representation; public determination consumes decision authority; participation can be created/evidenced by filing without creating authority. |
| Security | Private cooperative/member terms, farm authority packs, filing participation, and public decisional authority have materially different disclosure and write meaning. |
| Deletion consequence | A generic deletion would not say whether membership, farm power, participation, or decisional competence was lost. |
| Verdict | **REJECT CONSOLIDATION.** Keep the five exact types in this pass. |

### C3. Holding Stewardship versus Holding Representation — split

| Dimension | Holding Stewardship | Holding Representation |
|---|---|---|
| Endpoint types | actor ↔ `Agricultural Holding` | actor ↔ `Agricultural Holding` |
| Fact shape | Operational care/management duties, domain of stewardship, continuity, handoff, and accountability. | Power to speak, certify, sign, file, receive, or bind the Holding, including proposition/transaction limits. |
| Lifecycle | Often continuous operational appointment; can survive a change in signatory. | Grant, substitution, expiry, or revocation of authority; can be episodic or instrument-specific. |
| Authority | Holding operator, governing arrangement, or competent administrative truth establishes stewardship. | Principal, statute, mandate, power, or authorized administrative record establishes representative authority. |
| Actions | Consumed by land/work coordination and potentially dispatch/readiness; it does not authorize release by itself. | Consumed by `Release an application` and `Release a payment claim`; may govern certification or election. |
| Security | Operational responsibility can be shared with field/cooperative operators; representation packs and signature powers are more tightly restricted. | Identity, mandate, and signature/binding-power evidence requires narrower access and change authority. |
| Deletion consequence | Loses who was accountable for operating/stewarding the Holding. | Loses who was empowered to act for or bind the Holding. |
| Verdict | **SPLIT.** Same endpoints and some dates/basis fields do not overcome different fact, lifecycle, authority, Actions, security, and deletion meaning. A `steward/representative` kind would conceal a dangerous inference. |

### C4. Parcel Tenure, Parcel Access Authorization, and Parcel Consent — split all three

| Dimension | Parcel Tenure | Parcel Access Authorization | Parcel Consent |
|---|---|---|---|
| Endpoint types | tenure holder actor ↔ Parcel | authorized actor ↔ Parcel | consent beneficiary actor ↔ Parcel, plus consenting actor/Instrument where required |
| Fact shape | Durable estate/possessory/lease/usufruct or equivalent right, share, title/basis, priority/conflict. | Permission to enter or perform specified acts, time/place/method conditions, revocability, limits. | Affirmative assent by the competent consenter for a named act/purpose, beneficiary, conditions, withdrawal/expiry. |
| Lifecycle | Acquisition, transfer, renewal, expiry, adjudication, termination; commonly longer-lived. | Grant, activation, use window, suspension/revocation, expiry; often action- or period-specific. | Request/grant, conditions, possible withdrawal, expiry, or exhaustion for its purpose; may exist before access is scheduled. |
| Authority | Title register, contract, law, public-asset regime, or competent adjudication. | Tenure holder, asset manager, competent authority, or operative Instrument with power to authorize access/work. | The actor legally capable of consenting, under the applicable private/public regime; the beneficiary cannot self-assert it. |
| Actions | Consumed by land correction, application basis, conflict resolution, and route assessment. | Directly consumed by named-action readiness and `Dispatch an Intervention`. | Directly consumed by participation/design/dispatch readiness when affirmative consent is independently required. |
| Security | Title/lease and dispute facts have property/privacy sensitivity and restricted correction authority. | Operational access instructions may expose locations, windows, and safety conditions to executors. | Consent evidence can contain private identity, purpose, scope, conditions, and revocation information; access for executors does not imply access to the full consent instrument. |
| Deletion consequence | Loses the actor’s durable land-right claim. | Loses permission to enter or act; tenure may remain. | Loses proof of affirmative assent; tenure and even another access right may remain. |
| Verdict | **SPLIT ALL THREE.** `Parcel Right` fails lifecycle, authority, Action, security, and deletion tests. Access authorization and consent also cannot merge: consent can be a basis/input for authorization without being the authorization itself. |

**Internal compression boundary:** recognized tenure sub-kinds may use a controlled `tenureKind` only when they retain the same endpoint, right/share/basis/period/conflict shape, lifecycle, authority, Actions, and security. Delegated public-asset management, mere access, or consent must not be relabeled as tenure merely to save a type.

### C5. Holding Parcel Declaration versus Holding Parcel Conduction — split

| Dimension | Holding Parcel Declaration | Holding Parcel Conduction |
|---|---|---|
| Endpoint types | Holding ↔ Parcel | Holding ↔ Parcel |
| Fact shape | Administrative declaration/file version, declared area/use, filing basis, correction/conflict state. | Real operational/conduction basis, operated extent/use, period, and operational continuity. |
| Lifecycle | Filing, integration, correction, replacement, withdrawal, and administrative vintage. | Commencement, ongoing operation, partial change, transfer, or cessation independent of a filing event. |
| Authority | CAA/SIAN or other competent agricultural administrative record establishes the declaration. | Real land arrangement and competent evidence establish actual conduction; the declaration may evidence but does not create it automatically. |
| Actions | `Release an application` and authoritative correction consume/change declared truth. | Readiness, portfolio, land/work planning, and application truth checks consume operational truth. |
| Security | Farm-file/declaration data has controlled administrative write provenance. | Operational land relationship may rely on private contract or field evidence with different disclosure and correction rights. |
| Deletion consequence | Loses what the Holding officially declared for the Parcel at the relevant version. | Loses whether/how the Holding actually conducted the Parcel. |
| Verdict | **SPLIT.** A declaration can be wrong, stale, disputed, or corrected while conduction persists; collapsing them would make reconciliation impossible. |

### C6. Parcel Official Area Applicability versus Official Area Definition — split

| Dimension | Parcel Official Area Applicability | Official Area Definition |
|---|---|---|
| Endpoint types | Parcel ↔ Official Area, grounded in Instrument/authority | Instrument ↔ Official Area |
| Fact shape | Proposition-specific legal/operational consequence for one Parcel, date, geometry/partial-intersection rule, priority/conflict. | Constitutive definition, classification, geometry/version, effective scope, and defining Instrument. |
| Lifecycle | Recomputed or re-established when Parcel geometry, Area definition, date, rule, or more-specific decision changes. | Created/amended/redrawn/classified by authoritative Instrument versions; persists independently of any one Parcel. |
| Authority | Determinate result of controlling authority, rule, geography, date, and any specific decision. | Authority competent to create or define the Area. |
| Actions | Consumed by readiness, duty, route, and affected-decision determination; may be materialized by applicability logic. | Consumed upstream by applicability determination; not changed by a Parcel-specific decision. |
| Security | Parcel applicability may expose member/land consequences and conflicts. | Official Area definition is generally public authoritative regime data. |
| Deletion consequence | Loses the Parcel-specific applicable proposition, not the Area itself. | Loses why/when the Area exists or has its authoritative definition, while individual applicability claims may become unsupported. |
| Verdict | **SPLIT.** Geometry/definition is not applicability; applicability is not an Instrument effect merely copied onto the Area. |

### C7. All Governing Instrument effects in one Instrument Effect — reject

| Dimension | Comparison |
|---|---|
| Endpoint types | Differ: Programme, Official Area, another Instrument, Proceeding+actor, Parcel+duty bearer, and Intervention. |
| Fact shape | Constitutive programme effect, area definition, textual/legal lineage, authority grant, duty, and authorization require different mandatory facts. |
| Lifecycle | Establishment, versioned definition, partial amendment, displacement, delegated authority, continuing obligation, and permission/approval do not start/end the same way. |
| Authority | Legislative/administrative/programme, geographic, amending/superseding, delegating, enforcement, and permitting competence differ proposition by proposition. |
| Actions | Different facts feed population recomputation, applicability, filing/public determination, land duty resolution, design, and dispatch. Most are externally established; no one cohesive CORDON Action owns them. |
| Security | Public law may be public, while private mandate/contract/authorization terms can be restricted; one type would either overexpose private effects or overrestrict public law. |
| Deletion consequence | A generic deletion could erase creation, definition, lineage, power, obligation, or permission without preserving which legal consequence disappeared. |
| Verdict | **REJECT CONSOLIDATION.** Retain the seven currently evidenced exact classes; do not pre-create every verb listed in F3. A new effect is admitted only after its own evidence and this test. |

### C8. Programme Establishment versus other Programme-effect verbs — do not pre-consolidate or pre-split hypothetical classes

| Dimension | Comparison |
|---|---|
| Endpoint types | Instrument ↔ Programme would match for establishment, opening, funding, amendment, implementation, suspension, and closure. |
| Fact shape | Does not match: constitutive identity, operative window, money/ceiling, implementation rule, suspension conditions, and termination consequence need different mandatory facts. |
| Lifecycle | Establishment is constitutive; opening is windowed/repeatable; funding can be tranche/version based; suspension pauses; closure ends a programme or window. |
| Authority | The competent authority and proposition may differ even inside one Programme. |
| Actions | Population recomputation consumes all, but their downstream decisions and cures differ. No single cohesive Action changes all of them. |
| Security | Public examples may align, but private/local programme instruments need not; matching security alone cannot authorize consolidation. |
| Deletion consequence | Deleting “programme effect” would not distinguish loss of programme existence from loss of an opening, funds, or operative status. |
| Verdict | **KEEP ONLY PROGRAMME ESTABLISHMENT NOW.** Do not make a broad `Programme Instrument Effect`, and do not create six speculative types. If an accepted operator decision later needs an independently surviving opening, funding, suspension, or closure relationship, admit an exact domain type after a fresh six-dimensional test. |

### C9. Official Area create/redraw/classify/retire variants — narrow conditional consolidation

| Dimension | Comparison |
|---|---|
| Endpoint types | Instrument ↔ Official Area match. |
| Fact shape | Create/redraw/classify can share one versioned definition shape: authoritative definition/classification, geometry or represented extent, effective period, and basis. Retirement instead asserts termination and may require successor/disposition facts. |
| Lifecycle | Create/redraw/classify are versions of the Area’s definition when the authority preserves the same Area identity. Retirement ends that operative definition/identity and is not automatically the same lifecycle. |
| Authority | May match where the same competent authority controls the Area; must be checked per Area regime. |
| Actions | All are externally established and feed applicability recomputation; retirement additionally terminates downstream applicability. |
| Security | Usually the same public official regime, but that does not cure lifecycle differences. |
| Deletion consequence | Deleting a definition version loses how the Area was defined then. Deleting retirement loses the fact that it ceased to operate. |
| Verdict | **CONSOLIDATE CREATE/REDRAW/CLASSIFY ONLY WHEN THEY ARE VERSIONS OF ONE REAL `Official Area Definition`. DO NOT SILENTLY INCLUDE RETIREMENT.** Admit `Official Area Retirement` later only if independently required. |

### C10. Instrument Amendment versus Instrument Supersession — split

| Dimension | Instrument Amendment | Instrument Supersession |
|---|---|---|
| Endpoint types | amending Instrument ↔ amended Instrument | superseding Instrument ↔ superseded Instrument |
| Fact shape | Changed provision/proposition, amendment operation, unaffected remainder, effective transition. | Displaced proposition/scope, full/partial displacement, successor priority, effective transition. |
| Lifecycle | Alters the target while its identity and unaffected force continue. | Displaces all or scoped operative force; the predecessor may cease to govern that scope. |
| Authority | Both require competent normative authority, but authority to amend does not automatically equal authority/effect to supersede. |
| Actions | Both feed affected-decision determination; amendment re-evaluates changed propositions, supersession changes source priority and may terminate prior effects. |
| Security | Often similar for public instruments, but private contracts/mandates can have different visibility and amendment/termination authority. |
| Deletion consequence | Loses the scoped change while leaving no explanation for current modified terms. | Loses the displacement/priority transition and can falsely revive a predecessor. |
| Verdict | **SPLIT.** A `lineageKind` would hide materially different lifecycle and deletion consequences. Stays, annulments, constructions, and terminations are not added to either class without their own test. |

### C11. Programme Establishment, Official Area Definition, Proceeding Authority Grant, Parcel Duty, and Intervention Authorization — split by real effect

| Candidate | Endpoint types | Distinct fact/lifecycle | Distinct authority | Actions/security meaning | Deletion consequence | Verdict |
|---|---|---|---|---|---|---|
| Programme Establishment | Instrument ↔ Programme | Constitutes enduring Programme identity/effect | Programme-making authority | Drives complete-population evaluation; generally public | Programme loses its constitutive basis | **KEEP SEPARATE** |
| Official Area Definition | Instrument ↔ Area | Defines/version-controls authoritative geography/class | Area-defining authority | Feeds applicability; generally public official scope | Area loses authoritative definition/version | **KEEP SEPARATE** |
| Proceeding Authority Grant | Instrument + actor + Proceeding | Grants scoped powers, limits, and period | Delegating/competent authority | Governs public determination; authority evidence may be restricted | Actor’s normative competence basis disappears | **KEEP SEPARATE** |
| Parcel Duty | Instrument + Parcel (+ bearer) | Creates continuing obligation, conditions, clocks/discharge | Duty-making/enforcement authority | Drives land duty and readiness; can expose private affected land/bearer | Parcel/bearer obligation disappears | **KEEP SEPARATE** |
| Intervention Authorization | Instrument ↔ Intervention (+ actor if scoped) | Permits/approves bounded work under conditions | Permit/contract/public decision authority | Governs design/dispatch; may include restricted project/contract terms | Work loses its authorization basis | **KEEP SEPARATE** |

No pair passes endpoint, fact shape, lifecycle, authority, Actions, security, and deletion together.

### C12. Pathogen–Taxon and Pathogen–Cultivar response — split endpoint grain; consolidate response kinds within each

| Dimension | Taxon host response | Cultivar response |
|---|---|---|
| Endpoint types | pathogen Taxon/Lineage ↔ host Taxon/Lineage | pathogen Taxon/Lineage ↔ Cultivar |
| Fact shape | Taxonomic host status at exact host taxon/lineage grain. | Cultivar-specific susceptibility/resistance/tolerance; cannot be inherited safely from species. |
| Lifecycle | Versioned scientific/official conclusion at taxonomic grain. | Versioned conclusion can change by cultivar evidence and pathogen lineage independently of species-level host status. |
| Authority | Scientific and official host-list authority at taxon grain. | Cultivar trials, scientific evidence, and official cultivar recognition at cultivar grain. |
| Actions | No retained core Action mutates either; both are consumed by legal/design reasoning. Cultivar response directly informs recovery design but does not itself authorize a cultivar. | Same broad consumption, but cultivar-level decisions cannot be substituted by taxon-level response. |
| Security | Both are generally public scientific/official facts. Security matches but cannot cure endpoint mismatch. |
| Deletion consequence | Loses a host-taxon conclusion. | Loses a cultivar-specific response conclusion. |
| Verdict | **SPLIT INTO TWO TYPES** because exact endpoint types and decision grain differ. Within each type, host/susceptible/resistant/tolerant classifications may share a controlled `responseKind`: endpoint, evidence-qualified fact shape, version lifecycle, authority class, no-Action posture, security, and deletion meaning all match. |

### C13. Proceeding Participation versus Proceeding Decision Authority — split

| Dimension | Proceeding Participation | Proceeding Decision Authority |
|---|---|---|
| Endpoint types | actor ↔ Proceeding | actor ↔ Proceeding |
| Fact shape | Participant role, basis, duties, period, representation/capacity, withdrawal/history. | Power to decide/accept a defined proposition, limits, delegation basis, period, conflicts, termination. |
| Lifecycle | Can arise through filing, intervention, service, or formal joinder and can persist without decision power. | Begins by competent assignment/delegation/statute and ends by substitution, recusal, revocation, decision boundary, or proceeding termination. |
| Authority | Proceeding rules/records recognize participation. | Competent authority or governing Instrument confers decisional competence. Participation cannot self-create it. |
| Actions | Filing/release and responses consume/create evidence of participation. A public determination or route-specific official acceptance consumes decision authority. | Decisional Actions must refuse an unauthorized actor even if the actor participates. |
| Security | Participation may be visible to parties and case workers; filings can be permissioned. | Decision-power assignments and internal delegation/recusal can require narrower governance and write access. |
| Deletion consequence | Loses who participated and in what role; authority may remain elsewhere. | Loses who could decide; participation may remain. |
| Verdict | **SPLIT.** A participant/authority `kind` would permit the exact unsafe inference Gate 4 prohibits. |

### C14. Factless Proceeding pointers versus fact-bearing object types — retain direct boundary

| Dimension | Comparison |
|---|---|
| Endpoint types | Same actor ↔ Proceeding endpoints as predicates 8. |
| Fact shape | Factless pointer owns no basis, period, role, duties, powers, or history. Participation/authority objects do. |
| Lifecycle | Pointer is current navigation/context; the object-backed fact has independently preserved history. |
| Authority | Pointer can be projected from current proceeding context; fact-bearing assignment requires real authority/evidence. |
| Actions | Pointer is not independently edited as a governed assignment. Fact-bearing participation/authority is consumed by filing/decision operations. |
| Security | Pointer inherits endpoint visibility; detailed assignment can require narrower controls. |
| Deletion consequence | Deleting the pointer removes navigation only; deleting the fact object erases a decision-relevant relationship and history. |
| Verdict | **DO NOT PROMOTE OR DUPLICATE.** Keep a truly factless participant/current-decider pointer as a direct link. Once relationship facts exist, expose concise traversal from the object-backed relationship and remove any independently stored duplicate pointer. |

## 4. Rejected consolidations

1. `Actor Assignment` across membership, Holding stewardship/representation, and Proceeding participation/authority.
2. `Holding Assignment` combining stewardship and representation.
3. `Parcel Right` combining tenure, access authorization, and consent.
4. `Holding Parcel Relationship` combining declaration and conduction.
5. `Area Relationship` or `Parcel Area Membership` combining Official Area definition, raw overlap, and legal applicability.
6. `Instrument Effect` across all F3 effects.
7. `Instrument Lineage` combining amendment and supersession (or later stay/annulment/construction/termination variants).
8. `Programme Instrument Effect` combining constitutive establishment with opening, funding, amendment, implementation, suspension, or closure.
9. `Pathogen Host Response` with one sparse polymorphic host endpoint spanning Taxon and Cultivar.
10. `Proceeding Role` combining participation and decision authority.
11. Any separate factless direct link that duplicates the concise traversal of an admitted object-backed relationship.

## 5. Non-admissions and reopening rules

- The seven F3 effect classes retained here are the currently named, operator-relevant candidate exact classes. F3’s broader verb list is not a command to mirror every legal clause with an object type.
- Programme opening/funding/suspension/closure, Official Area retirement, Instrument stay/annulment/construction/termination, and additional person/Holding/Lot effects remain **not admitted in this pass**. Admit one only when an accepted decision needs an independently surviving relationship at that exact grain and it passes all six dimensions.
- A factless basic Instrument association remains a direct contextual link; it is not an empty effect object.
- A grant, amendment, consent, filing, decision, revocation, or termination occurrence may create/change one of these relationships without becoming the relationship.
- Raw geometry, current status, scientific observation, endpoint classification, and transitive inference remain outside the relationship inventory.
- Unknown current private membership, representation, land rights/consent, private Instrument effects, and permissioned Proceeding assignments remain unknown—not negative instances.

## 6. Coverage and final verdict

| Atomic predicate | Exact object-backed coverage in this pass |
|---:|---|
| 1. Cooperative membership | Cooperative Membership |
| 2. Holding stewardship/representation | Holding Stewardship; Holding Representation |
| 3. Actor–Parcel tenure/access/consent | Parcel Tenure; Parcel Access Authorization; Parcel Consent |
| 4. Holding–Parcel declaration/conduction | Holding Parcel Declaration; Holding Parcel Conduction |
| 5. Authority-grounded Parcel–Official Area applicability | Parcel Official Area Applicability |
| 6. Governing Instrument effect/lineage | Programme Establishment; Official Area Definition; Instrument Amendment; Instrument Supersession; Proceeding Authority Grant; Parcel Duty; Intervention Authorization |
| 7. Biological pathogen–host response | Pathogen Taxon Host Response; Pathogen Cultivar Response |
| 8. Public Proceeding actor participation/authority | Proceeding Participation; Proceeding Decision Authority; factless pointers remain direct |

**Final verdict:** retain **20** exact domain-named relationship object types. The adversarial tests reject the tempting savings—stewardship with representation, tenure with access/consent, declaration with conduction, amendment with supersession, heterogeneous Instrument effects, taxon-host with cultivar-host response, and participation with decision authority—because each proposed merge fails at least one material dimension and usually several. The only accepted compression is (a) a controlled kind inside an already uniform exact relationship and (b) one exclusive actor slot that may resolve to `Natural Person` or `Organization` when actor form changes no semantic/governance dimension. This is the smallest inventory that preserves all accepted distinctions in the scoped predicates without generic family objects or speculative type-per-verb expansion.

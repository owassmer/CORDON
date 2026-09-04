# Gate 5 MECE exclusivity audit

**Status:** adversarial mutual-exclusivity audit; precondition to minimal Ontology derivation  
**Date:** 22 August 2026  
**Verdict:** **FAIL**

## 1. Scope and decision rule

This audit tests the accepted 13 nouns, seven semantic relationship families, 11 mandatory concrete grains, contextual direct links, and rejected events/outcomes/statuses/observations/derived overlays against the current authorities: `REDESIGN_SEQUENCE.md`, `gate-5-reground.md`, `connected-operating-model.md`, `gate-3-noun-candidates.md`, `gate-4-relationship-candidates.md`, `gate-3-private-data-resolution-adjudication.md`, and `individual-tree-inventory-feasibility.md`.

The test is semantic only. It makes no decision about Ontology representation, properties, keys, cardinalities, actions, functions, screens, source schemas, or platform architecture.

A set is exclusive enough for derivation only if an atomic real-world proposition has one default semantic home, or if a compound fact has an explicit decomposition into independently meaningful atomic propositions with different homes. Sharing evidence or being created by the same instrument is not a reason to duplicate one proposition across families.

**Result:** the noun set is mostly exclusive after the placement rules below, but the relationship set is not. There are duplicated ownership claims, mixed binary/ternary arity hidden inside family prose, and two mandatory grains with no complete home. Those defects would force implementation choices to settle semantics. Gate 5 must not do that. Gate 4 therefore requires selective reopening before derivation.

## 2. Placement rules

Apply these rules in order to every candidate fact.

1. **Atomize first.** Rewrite a sentence until each proposition has one subject, one predicate, one semantic object, and one basis/time qualification. “Instrument X appoints Organization Y as decision authority in Proceeding Z” is not one relationship: it contains an instrument effect and an actor assignment.
2. **Identity before relationship.** Ask whether the proposition asserts sameness or classification of an endpoint. Plant-to-official-record correspondence is identity resolution/provenance; Plant-to-Cultivar is endpoint classification. Neither becomes a fact-bearing family merely because the resolution has evidence.
3. **Event before enduring fact.** If the proposition says something happened—filing, reservation decision, dispatch, delivery, installation, inspection, acceptance, payment, release, revocation—it is an event/outcome. Keep only an independently surviving relationship created or changed by it.
4. **Observation before world assertion.** A detected crown, coordinate, footprint, symptom, disappearance, survival signal, or infected sample is observation evidence at its validated grain. It does not itself create Plant identity, location, infection, Intervention scope, legal applicability, or accepted outcome.
5. **Derived before authoritative.** Polygon intersection, proximity, transitive inference, eligibility calculation, feasible-portfolio membership, and current-status calculation are derived overlays unless a competent process deterministically establishes a stronger proposition.
6. **Endpoint classification before contextual link.** Cultivar classification, basic Programme/Proceeding context, or basic subject association remains a direct contextual link when it owns no basis, scope, period, powers, duties, quantities, or change history.
7. **Then place the enduring relationship.** Use exactly one family for the atomic predicate. A creating Governing Instrument may be its basis without causing the same predicate to be stored again as F3.
8. **Decompose legitimate multi-family cases.** The following co-occurrences are allowed only as separate propositions: normative instrument effect (F3) plus instantiated actor assignment (F1); instantiated entitlement (F7) plus its creating effect (F3); Intervention responsibility (F1) plus capacity commitment (F6); Intervention material inclusion/use (F5) plus capacity reservation (F6).
9. **Unknown remains unknown.** Analogue evidence may establish structure but cannot turn an unknown private assignment, scope, commitment, custody, creditor right, settlement, or responsibility into a negative or inferred relationship.

## 3. Noun exclusivity

| Noun boundary | Adversarial collision | Placement verdict |
|---|---|---|
| Natural Person vs Organization | sole trader, officeholder, member, beneficiary | Keep identities separate; all listed labels are contextual roles. No collision if an Agricultural Holding is not silently equated with either. |
| Agricultural Holding vs Person/Organization | a business may operate one Holding and share an identifier in a source | Keep the administratively preserved farm operating unit distinct from its operator, owner, representative, or beneficiary. Source-key coincidence does not merge identity. |
| Agricultural Holding vs Cadastral Parcel | “farm,” “land,” or farm-file row can blur unit and land | Holding is the persistent operating/administrative unit; Parcel is the legally identified land unit; their changing association is F2. |
| Cadastral Parcel vs Official Area | both have geometry and may be called an area | Parcel identity comes from cadastre; Official Area identity comes from the competent authority/process. Geometry is representation, not identity. |
| Official Area vs derived overlay | buffer/intersection polygon looks official | Admit only an authority-preserved Area. An analytical polygon remains a derived overlay. |
| Individual Plant vs observation point/sample | coordinates or crown detections appear individual | A Plant exists only after external or validated reproducible identity preservation. A sample, crown point, or change candidate is an observation. |
| Individual Plant vs Plant Trade Unit/Lot | installed stock can become an individual plant | The Lot is traceability identity before/through movement; the Plant is an individually preserved biological identity. Origin/sameness resolution does not merge them. |
| Cultivar vs Organism Taxon/Lineage | both are biological classifications | Cultivar is a recognized cultivated variety; Organism Taxon/Lineage is the taxonomic/lineage grain used by the governing or scientific decision. Do not use F4 to erase this noun boundary. |
| Programme/Measure vs Governing Instrument | a call or measure may be announced by one act | Programme is enduring governed policy/support identity; Instrument is one operative rule/decision/agreement. `Instrument establishes/amends Programme` is F3. |
| Governing Instrument vs Public Proceeding | permits, concessions, judgments, claims and audits are described ambiguously | Proceeding is the instituted matter; an issued permit, concession, judgment, order, contract, or guarantee may be an operative Instrument; issuance/release is an event. The current prose needs the correction in C12 below to prevent act/event/noun conflation. |
| Public Proceeding vs generic Case | both can collect submissions and decisions | Admit only the formally instituted public matter. Private trackers, bundles, dossiers, and work queues do not create a Proceeding. |
| Intervention vs Programme/Proceeding | an application or order may appear to be “the project” | Intervention is the bounded physical undertaking and can outlive either public matter. Context links do not merge identities. |
| Intervention vs events/outcomes | dispatch, execution, acceptance, aftercare and cure can be called work units | Keep one evidence-preserved undertaking; those are events/outcomes or distinct responsibilities unless a real authority/contract/physical process preserves another undertaking grain. |

**Noun verdict:** no noun must be deleted. The only unresolved noun-level risk is the Governing Instrument wording, which currently admits issued operative acts while the rejection list also calls similarly named concession/permit items decisions or outcomes. C12 supplies the required identity/event rule.

## 4. Adversarial fact-pattern matrix

The audit tested **34 atomic fact patterns**. The first 11 groups cover every mandatory concrete grain; later patterns stress contextual links and rejected constructions.

| ID | Concrete fact pattern | Plausible placements tried | Exclusivity finding and deletion-first verdict |
|---|---|---|---|
| P01 | Person/Organization is a cooperative member | F1; F3 if an instrument admits the member; F7 if membership brings support | **F1 only** for membership. Delete duplicate F3/F7 placement; represent admission effect and any entitlement as separate facts. |
| P02 | Instrument admits/terminates a named member | F3 vs F1 | Compound. F3 owns the instrument’s effect; F1 owns the surviving membership assignment. Neither can be deleted, but the same “membership” predicate must not occur in both. |
| P03 | Membership makes a member eligible or benefits them | F1 vs F7 vs rejected status | Membership remains F1; eligibility is derived/status-like; only a durable member-specific right is F7. Delete “beneficiary” as an F1 assignment when it merely means right-holder. |
| P04 | Actor stewards/operates a Holding | F1 vs F2 | **F1 only.** F2’s broad family name “Land Association or Right” invites misplacement because a Holding is land-adjacent. Rename/narrow F2; do not infer Parcel control. |
| P05 | Actor represents a Holding | F1 vs F3 | **F1** for instantiated representation; F3 only for a separate instrument effect that grants/limits it. Delete duplicated mandate/authority predicate from F3. |
| P06 | Actor owns, controls, occupies, manages, accesses, or consents for a Parcel | F2 vs F1 | **F2 only.** A contextual label such as owner or manager is a projection of the F2 predicate, not another F1 assignment. |
| P07 | Instrument delegates Parcel access/alteration power to an actor | F2 vs F3 vs F1 | Compound. F3 owns normative effect; F2 owns the resulting Parcel right; F1 applies only if a distinct office/context assignment also exists. Current prose lacks this decomposition. |
| P08 | Holding declares/conducts a Parcel | F2 vs F3 | **F2 only.** A filing or instrument can evidence/create/change it without turning the same relationship into F3. |
| P09 | Parcel is authoritatively in an Official Area | F2 vs F3 vs direct link | **F3 only under the current seven-family taxonomy**, because the authoritative classification/effect is instrument/process- and date-grounded. F2’s name must exclude Area membership. The relationship needs an explicit instrument/process basis even when presented as Parcel–Area. |
| P10 | Parcel polygon intersects an Area polygon | F2 vs F3 vs derived overlay | **Derived overlay only** unless controlling rules deterministically establish P09 or only a procedural trigger. Delete all direct promotion. |
| P11 | Instrument establishes/amends/opens/closes a Programme or Area | F3 vs contextual direct link | **F3** when consequential; direct only when no independent effect facts exist. No overlap after consequence test. |
| P12 | Instrument grants/limits authority to decide a Proceeding | F3 vs F1 | Compound and presently duplicated. F3 owns the normative grant/limit; F1 owns the actor’s instantiated decision-authority assignment. Delete “Proceeding decision authority” from F3 when it is merely the surviving F1 assignment. |
| P13 | Instrument amends/supersedes/stays/annuls another Instrument | F3 vs event/outcome | The enduring scoped effect/lineage is **F3**; issuance, stay, or annulment occurrence is an event. Keep both only if each is required; do not turn event time into a status relation. |
| P14 | Actor participates in a Proceeding | F1 vs contextual direct link | F1 only where basis, role, powers/duties, scope, or period are independent; otherwise direct context. The current “basic participant” wording needs an explicit fact-bearing threshold. |
| P15 | Actor decides/reviews/inspects within a Proceeding | F1 vs F3 | F1 for instantiated assignment; F3 for a distinct normative source effect. Same authority predicate cannot be duplicated. |
| P16 | Proceeding concerns named Parcel(s), Intervention(s), Instrument(s), or claim scope | F1 vs F3 vs contextual direct link | **No complete family home.** It is not actor assignment; it may change independently without a Governing Instrument endpoint; and a versioned claimed/reviewed/adjudicated scope can carry facts beyond a direct link. Deletion-first test fails: demoting it loses subject/scope history. Gate 4 must add a Proceeding Subject/Scope family or expressly prove that every retained instance is factless direct context. |
| P17 | Intervention includes/targets a Parcel or Plant | F5 vs F3 | F5 for intended/authorized/as-built physical scope; F3 only for a separate instrument effect. Instrument authorization does not duplicate the F5 predicate. |
| P18 | Observed footprint/count suggests actual Intervention scope | F5 vs observation/outcome | Observation only until validated against the real physical process. It may evidence F5 but does not create it. “Actual” and “accepted” in F5 must not silently promote observations or outcomes. |
| P19 | Intervention specifies a Cultivar composition | F5 vs F4 vs F3 | F5 for design/use; F4 for a separate biological host/response relation; F3 for a separate legal/programme effect. The cultivar’s legality or tolerance never follows transitively from F5. |
| P20 | Pathogen lineage has host/susceptibility/resistance/tolerance relation to taxon/cultivar | F4 vs F3 vs endpoint classification | F4 only for the biological/evidentiary relation. Official legal host listing or programme permission is F3; cultivar identity remains endpoint classification. Current F4 wording must be narrowed by evidence class and direction. |
| P21 | Actor is contractor/manager/executor/inspector/acceptor/warranty/aftercare responsible for Intervention | F1 vs F6 vs F3 | **F1** for responsibility/capacity-to-act assignment; F6 only for a distinct scarce resource commitment; F3 only for a distinct instrument effect. “Capacity” in mandatory grain 10 is ambiguous and must be split. |
| P22 | Actor commits crew, money, stock, slot, or other scarce capacity to Intervention | F6 vs F1 vs F5 | **F6 only** for the surviving commitment. Authorization/responsibility is F1; required materials are F5; availability is derived/current evidence. |
| P23 | Specific Lot is reserved/earmarked for an Intervention | F5 vs F6 | **F6** when reservation is a supplier/owner commitment; F5 only once the Lot is intended/authorized/as-built material scope/use. Delete “Lot reservation” from F5. |
| P24 | Lot is delivered, installed, substituted, replaced, or accepted in Intervention | F5 vs event/outcome | Delivery/installation/substitution/acceptance occurrences are events/outcomes; independently preserved Lot inclusion/use is F5. Remove event words from the family predicate list or explicitly label them as relationship-changing evidence only. |
| P25 | Organization/Person has custody of a Lot before, between, or outside Interventions | F5 vs F6 vs contextual direct link | **No complete family home.** Custody has actor, lot, period, quantity, transfer basis, and chain-of-custody consequences. It is neither Intervention use nor necessarily a capacity commitment. Deletion loses the mandatory lot allocation/custody grain. Add a Lot Allocation/Custody family or retract the claim that the grain is independently fact-bearing. |
| P26 | Member/Holding holds a programme-specific entitlement | F7 vs F3 vs F1 | **F7** for the durable instantiated right; F3 only for the distinct creating/limiting effect; F1 membership is independent. Delete member-specific amount/conditions duplication from F3. |
| P27 | Person/Organization/Holding is creditor, assignee, or recovery obligor | F7 vs F1 vs F3 | **F7** when the identity exists only qua durable right/exposure. F1 applies to representation/authority over the right, not creditor identity. F3 applies only to a separate assignment/discharge effect. |
| P28 | Concession is issued, exists as operative act, creates a right, and grants scope/amount | Governing Instrument noun; event; F3; F7 | Four atomic facts are hidden in one word. Issuance is event; operative concession can be a Governing Instrument; creating effect is F3; surviving member right is F7. Current prose duplicates scope/amount/conditions between F3 and F7 and must be corrected. |
| P29 | Observation/sample says an Individual Plant is infected | F4 vs F3 vs observation | Observation/diagnostic outcome only. F4 is taxon/cultivar-level biological relation; F3 applies only if competent process gives the Plant a legal effect/status. Imagery or sample proximity creates neither. |
| P30 | Individual Plant is located on a Parcel | F2 vs F5 vs contextual direct link vs observation | Direct contextual spatial association when no independent relationship facts exist; observation when merely detected; F5 only when the Plant is Intervention scope. F2 never applies. If a real process preserves independent Plant–Parcel location history, Gate 4 must reopen rather than force it into F2/F5. |
| P31 | Observed Plant corresponds to an official Plant record | relationship family vs direct link vs provenance | Identity resolution/provenance, not a real-world relationship. Resolved records describe one Plant; unresolved matches remain candidate correspondence. Delete any business-link promotion. |
| P32 | Member/Intervention/Proceeding is eligible, selected, ready, blocked, accepted, paid, active, or complete | F1/F3/F7 vs rejected status | Derived or bounded status only. Preserve the underlying rules, relationships, events, and outcomes; do not create a generic relationship. |
| P33 | Acceptance, survival, defect, replacement, or cure changes perceived Intervention/Plant condition | F5/F1 vs event/outcome/observation | Event/outcome/observation first. It may change F5 scope or F1 responsibility, but cannot be retained as an F5/F1 status predicate. |
| P34 | Vector taxon transmits/carries organism lineage, or one non-host organism affects another | F4 vs F5 vs missing family | Current F4 is **not exhaustive** for organism ecology and becomes overbroad if “organism–host” is used to absorb vector/transmission, predation, competition, or intervention-target relations. Keep F4 narrow; admit another predicate/family only if an accepted operator decision needs an independently persistent fact. |

## 5. Overlap findings

### O1 — F1 versus F3 authority, mandate, and delegation

F1 expressly owns mandate, delegation, Proceeding authority, and Intervention responsibility. F3 also says an Instrument can create or limit authority, mandate, contract, or operative condition, and lists the affected role and scope as independent facts. A single sentence such as “Act A delegates Organization B to decide Proceeding C” can therefore be stored twice without semantic guidance.

**Deletion-first verdict:** do not delete either family. Delete the duplicated instantiated-assignment reading from F3. F3 owns the normative effect of the Instrument; F1 owns the actor’s surviving assignment in the context. Linkage to the creating basis is provenance/basis, not a second copy of authority.

### O2 — F1 versus F7 beneficiary and creditor identity

F1’s broad actor-context language can absorb “beneficiary,” while F7 explicitly owns the holder/creditor of a durable right. The noun authority already says beneficiary and creditor are roles, but it does not say which family owns those roles.

**Deletion-first verdict:** delete F1 placement when “beneficiary” or “creditor” means only holder of the F7 right. F1 remains only for a separate membership, representation, filing authority, office, or responsibility assignment.

### O3 — F2 versus F3 area applicability

F2 is named “Land Association or Right,” broad enough to attract Parcel–Area membership, while F3 explicitly owns authority/date-grounded membership or applicability. P09 is also expressed as a binary Parcel–Area grain although F3 is defined as a Governing Instrument effect, hiding a third basis/authority dimension.

**Deletion-first verdict:** exclude Official Area membership/applicability from F2 and rename F2 narrowly. F3 owns authoritative membership/applicability; raw geometry remains derived. The semantic definition must require the competent instrument/process, relevant date, and partial-intersection rule as the basis even when the operator-facing statement is Parcel–Area.

### O4 — F3 versus F7 entitlement

F3 and F7 both claim scope, amount/quantity, conditions, effective period, and instrument grounding. A concession can be represented as an Instrument effect and as the member right with materially identical facts.

**Deletion-first verdict:** delete member-specific right facts from F3 after creation. F3 owns the act’s generic or creating/limiting/discharging effect; F7 owns the instantiated holder/creditor, awarded scope, amount/ceiling, claim permissions, conditions, duration, assignment, guarantee/recovery exposure, and remaining right. Do not copy these facts into both.

### O5 — F5 versus F6 Lot reservation and use

F5 explicitly includes Lot “reservation,” while F6 owns reservations/commitments and may involve a specific Lot. This is direct duplication.

**Deletion-first verdict:** delete “reservation” from F5. F6 owns earmarking/commitment before use; F5 owns intended/authorized/as-built Lot material inclusion or use. Reservation decision, delivery, receipt, installation, substitution, replacement, and acceptance occurrences remain events/outcomes.

### O6 — F5 versus observations and outcomes

F5 lists intended, authorized, actual, and accepted scope and accepted quantity, while the same authority rejects execution, inspection, acceptance, observations, and observed footprints as relationship families. Without a rule, “actual” can promote an observed footprint and “accepted” can duplicate an acceptance outcome.

**Deletion-first verdict:** keep only independently preserved intended, authorized, or as-built inclusion/use relationships in F5. Delete event/outcome words as predicates. An observation or acceptance can evidence/change an F5 relationship but remains distinct.

### O7 — Proceeding participation/scope split

The mandatory grain combines “participation/scope.” F1 covers actor participation/authority. Contextual links allow a basic Proceeding subject. No family covers independently changing claimed, reviewed, permitted, appealed, audited, enforced, or recovered subject scope when it carries basis, version, quantity, or effective history.

**Deletion-first verdict:** split the grain. Keep actor participation/authority in F1. Keep a truly factless subject link contextual. Because accepted Proceedings retain identity through submissions, decisions, repair, and reopening, deletion of fact-bearing subject/scope is unsafe. Add a distinct **Proceeding Subject and Scope** family unless Gate 4 can prove no accepted operator decision needs independent scope facts.

### O8 — Plant identity, location, and official correspondence

A crown/sample point can be mistaken for Plant identity; Plant–Parcel location can be forced into F2, F5, or F3; official-record correspondence can be promoted as a relationship. The tree-inventory authority correctly rejects all three shortcuts, but Gate 4 lacks a single precedence rule.

**Deletion-first verdict:** identity resolution first; observation second; contextual location third. F5 applies only to independently established Intervention scope. F3 applies only to competent legal effect. F2 never owns Plant location. Official-record correspondence is provenance/co-reference, not a relationship family.

### O9 — Intervention responsibility versus capacity

Mandatory grain 10 says “responsibility/capacity,” F1 owns responsibility, and F6 owns scarce capacity commitment. F6’s capacity owner can be the same actor and Intervention as F1, and F3 may additionally contain the contract/work-order effect.

**Deletion-first verdict:** split the grain. F1 owns authority, responsibility, powers, duties, and termination. F6 owns quantified/time-bounded resource commitment, expiry, release, and reallocation consequences. F3 owns only a distinct operative instrument effect. Do not infer any one from another.

### O10 — Mandatory Lot allocation/custody has no complete home

The 11th anti-collapse grain requires Lot allocation/custody. F5 only covers Intervention material use; F6 only covers capacity commitments; movement/receipt are rejected events; contextual origin is explicitly factless. Custody outside or between Interventions has independent actor, time, quantity, transfer-basis, phytosanitary, warranty, and traceability consequences.

**Deletion-first verdict:** it cannot be deleted while the grain remains mandatory. Add a distinct **Plant Trade Unit/Lot Allocation and Custody** family, or explicitly retract the grain’s fact-bearing status and demonstrate that events plus factless links preserve every accepted traceability decision. The current seven-family claim is not exhaustive.

### O11 — F4 is narrow in name, broad in endpoint wording, and not exhaustive

F4 mixes recognized host status, susceptibility, resistance, and tolerance; allows Organism-to-Organism or Organism-to-Cultivar endpoints; and carries scientific, official, geography, version, and uncertainty qualifications. It can therefore absorb legal host listing (F3), observed Plant infection (observation), cultivar permission/design (F3/F5), or vector/transmission ecology not described by “host.”

**Deletion-first verdict:** do not broaden F4 to make organism relations exhaustive. Narrow it to evidence-qualified biological pathogen/lineage ↔ host taxon/cultivar predicates: host-of and response class (susceptible/resistant/tolerant) with explicit direction and evidence/authority class. Exclude individual infection, legal applicability, programme eligibility, cultivar authorization, Intervention targets, and vector/transmission relations. Add another organism predicate only if a concrete accepted operator decision proves independent persistence.

### O12 — Governing Instrument noun versus event/outcome

The noun definition admits permits, concessions, judgments, orders, contracts, guarantees, and protocols as operative Instruments, while rejection prose lists permit/concession decisions and other similarly named items as events/outcomes. Without an identity test, one source row can become an Instrument, Proceeding outcome, F3 effect, and F7 right under the same label.

**Deletion-first verdict:** preserve an Instrument only when an independently identifiable operative act/agreement persists and can be amended, stayed, terminated, construed, or invoked. Keep issuance, signature, release, decision, and payment occurrences as events/outcomes. Keep its normative effect in F3 and any surviving member right in F7. Delete noun promotion for a mere occurrence or source artifact.

## 6. Concrete-grain disposition after corrections

| Mandatory grain | Sole/default home after correction | Required split or qualification |
|---|---|---|
| cooperative membership | F1 | Creating/ending instrument effect is separate F3; entitlement is separate F7. |
| Holding stewardship/representation | F1 | Parcel tenure/access cannot be inferred; that is F2. |
| actor–Parcel interest | F2 | Instrument effect is separate F3; contextual office is separate F1. |
| Holding–Parcel declaration/conduction | F2 | Filing is event; source row is evidence. |
| Parcel–Official Area membership | F3 | Requires competent instrument/process and date; raw overlap is derived. |
| Governing Instrument effect/lineage | F3 | Issuance/stay occurrence is event; enduring scoped effect is F3. |
| Public Proceeding participation/scope | **Split: F1 + missing Proceeding Subject/Scope family** | Factless subject remains direct context. |
| Intervention physical scope | F5 | Observed/accepted outcomes remain separate. |
| Intervention–Cultivar specification | F5 | Biological response is F4; legal permission is F3. |
| Intervention responsibility/capacity | **Split: F1 + F6** | Instrument effect is separate F3. |
| Plant Trade Unit/Lot allocation/custody | **Split: F5/F6 + missing Lot Allocation/Custody family** | Events record movements; enduring custody/use/commitment relations remain distinct. |

## 7. Exact semantic corrections required before Ontology derivation

1. **Add an atomic-proposition and decomposition rule** to Gate 4: one atomic predicate has one family; a compound sentence must be split; shared instrument/evidence does not authorize duplicate relationship ownership.
2. **Rename F2** from `Land Association or Right` to **`Holding–Parcel Operation/Declaration and Actor–Parcel Tenure/Access`**, and state that it excludes Official Area membership, Plant location, Intervention scope, and actor–Holding assignment.
3. **Correct F1/F3 authority:** F1 owns instantiated actor assignment, authority, mandate, delegation, responsibility, powers/duties, scope, and period in a context. F3 owns only the creating/limiting/suspending/terminating normative effect of an Instrument. Delete the same actor-assignment predicate from F3.
4. **Correct F1/F7 role ownership:** beneficiary, creditor, assignee, payee, and recovery-obligor identity belongs to F7 when it exists qua a durable right/exposure. F1 owns only separate membership, representation, office, filing authority, or operational responsibility.
5. **Correct Parcel–Area semantics:** place authoritative Parcel–Official Area membership/applicability in F3 only; require competent instrument/process, relevant date, geometry rule, and any more-specific decision as its semantic basis. Polygon intersection remains derived and F2 is excluded.
6. **Correct F3/F7 entitlement:** F3 owns creation/limitation/discharge of a right; F7 owns the instantiated member-specific right thereafter. Remove member-specific holder, awarded amount/ceiling, claim stages, conditions, assignment, guarantee/recovery exposure, and remaining-right facts from F3.
7. **Delete `Plant Trade Unit / Lot reservation` from F5.** F6 owns an earmarked/committed Lot before use; F5 owns independently preserved intended/authorized/as-built Lot inclusion/use. Keep reservation, delivery, receipt, installation, substitution, replacement, and acceptance occurrences as events/outcomes.
8. **Narrow F5 actual/accepted wording:** replace `intended, authorized, actual or accepted scope` with **`intended, authorized, or independently preserved as-built physical/material inclusion or use`**. State that observations and acceptance outcomes may evidence/change but do not become F5 predicates.
9. **Split mandatory grain 7** into `Public Proceeding actor participation/authority` (F1) and `Public Proceeding subject/scope`. Add a **Proceeding Subject and Scope** family for fact-bearing claimed/reviewed/decided/appealed/audited/enforced scope, or prove and record that every retained scope link is factless context. The accepted workflow makes the former correction the supported one.
10. **Split mandatory grain 10** into `Intervention responsibility/authority` (F1) and `Intervention scarce-capacity commitment` (F6). Delete the ambiguous combined label `responsibility/capacity`.
11. **Resolve mandatory grain 11 by adding a `Plant Trade Unit/Lot Allocation and Custody` family** for enduring actor/lot allocation, possession/custody, quantity/share, period, transfer basis, and traceability responsibility. Keep Intervention use in F5, reservation/earmarking in F6, and movements/receipts as events. If this family is rejected, retract grain 11’s fact-bearing claim and provide a decision-preservation proof before derivation.
12. **Add the Governing Instrument identity/event rule:** an independently identifiable operative act/agreement is the noun; issuance/signature/release/decision is event/outcome; normative consequence is F3; surviving member right is F7; source artifact is provenance only.
13. **Add the Plant precedence rule:** validated identity or co-reference first; observation second; direct contextual Plant–Parcel location only when factless; F5 only for Intervention scope; F3 only for competent effect. Official-record correspondence is identity/provenance and F2 never owns Plant location.
14. **Narrow F4** to directed, evidence-qualified pathogen/lineage ↔ host taxon/cultivar biological predicates (`host-of`, `susceptible-to`, `resistant-to`, `tolerant-to`). Explicitly exclude individual infection observations, legal host/applicability classifications, programme/cultivar authorization, Intervention target/use, and vector/transmission/ecological relations. Do not claim F4 is exhaustive of organism relations.
15. **Clarify contextual-direct threshold:** a Proceeding participant/subject, Instrument context, Plant/Lot origin, or Intervention context is direct only when it has no independently changing basis, scope, period, quantity, powers/duties, custody, or history. If any such facts are required, it must enter the corrected family review rather than be forced into a direct link.
16. **Add event/relationship precedence to all families:** decisions and occurrences create/change/end relationships but are never synonyms for them. Status labels are derived projections; observations are evidence; overlays are calculations; none can be promoted by naming them `actual`, `accepted`, `current`, or `official`.

## 8. Deletion-first bottom line

- **Keep all 13 nouns**, subject to the Governing Instrument identity/event correction.
- **Keep F1–F7 only after narrowing their ownership.** No accepted operator decision supports deleting F1, F2, F3, F4, F5, F6, or F7 wholesale.
- **Delete duplicated clauses before adding anything:** instantiated authority/mandate from F3; beneficiary/creditor-as-right-holder from F1; Area membership from F2; member-specific right contents from F3; Lot reservation from F5; event/outcome synonyms from F5.
- **Then add only the two missing semantic homes that survive deletion:** Proceeding Subject/Scope and Lot Allocation/Custody, unless Gate 4 explicitly retracts those grains as fact-bearing after a decision-preservation proof.
- **Do not add families for observations, events, statuses, derived overlays, endpoint classifications, identity correspondence, or transitive shortcuts.**

## 9. Final verdict

**FAIL.**

The current authorities are close to a usable partition, but they are not mutually exclusive or collectively exhaustive enough to support a minimal Ontology derivation without semantic invention. The fatal issues are: duplicated F1/F3 and F3/F7 ownership; direct F5/F6 duplication of Lot reservation; event/outcome leakage into F5; mixed-arity Parcel–Area and authority facts; and missing homes for fact-bearing Proceeding scope and Lot custody despite both being mandatory anti-collapse grains. Apply corrections 1–16 and selectively reaccept Gate 4 before beginning Ontology derivation.

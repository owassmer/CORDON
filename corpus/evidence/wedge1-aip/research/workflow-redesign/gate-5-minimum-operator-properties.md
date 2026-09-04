# Gate 5 minimum operator properties and history-detail contracts

Status: **RECONCILED INPUT — final authority is `gate-5-reconciled-operator-graph.md`**  
Date: 22 August 2026  
Authority: `REDESIGN_SEQUENCE.md`; `gate-5-core-ontology.md`; `gate-5-operator-reground.md`; `gate-5-operator-decision-ledger-six-questions.md`; `gate-5-operator-capability-ledger-five-responsibilities.md`; `gate-5-operator-ledger-reconciliation.md`

## Decision and scope

This artifact defines the minimum semantic properties and typed, multi-value consequential-history contracts for the nine accepted operator objects and `Intervention Capacity Commitment`.

The reconciliation adds `Cooperative Pursuit`, gives both relationship objects their own factual histories, and removes stored changed-decision/reopening/next-owner/next-Action/clock fields from the universal history envelope. Use the accepted reconciled graph rather than this lane output for implementation.

It does **not** choose physical data types, primary keys, source columns, platform storage, status vocabularies, interfaces, security configuration, or Gate 6–7 architecture. Property names below are semantic contract names, not implementation names. Direct links are referenced only to explain why a fact is not duplicated as a property; this artifact does not specify the direct-link graph.

The lower bound follows five rules:

1. A retained property must let the cooperative/OP operations manager identify or select the thing, answer a current decision, take or supervise one of the four accepted Actions, explain a consequence, locate land/law/tree scope, route a handoff, or selectively reopen affected work.
2. Current answers that can be computed from linked authoritative facts and consequential histories are **derived projections**, not copied properties.
3. Raw legal, scientific, financial, source, evidence, acquisition, ingestion, and observation detail remains **backstage-only**.
4. Consequential occurrences are not independent initial event objects. Typed multi-value histories live only on `Governing Instrument`, `Public Proceeding`, or `Intervention`. The other seven types have explicit **no-local-history** contracts and receive history projections from those owners.
5. A history detail is typed by its real occurrence and bounded effect. It is never a generic event, status change, task, note, timeline entry, or source record.

## Property classes

- **I — identity/title.** A qualified operator reference, recognizable title, or necessary discriminator. It supports exact selection, handoff, external reconciliation, or map/legal/tree addressability; it is not a platform key.
- **C — current decision fact.** A small, authoritative fact currently owned by the object and needed directly by a manager decision or accepted Action. Do not use this class for a cached derived answer.
- **D — derived projection.** A current answer calculated from facts, links, and histories. It may be shown or queried later but must not become duplicate truth on the object.
- **B — backstage-only excluded.** Detail retained outside the operator core for substantiation, ingestion, audit, legal/scientific fidelity, or another actor’s process.

A missing field is intentional. In particular, there is no generic `status`, `state`, `stage`, `ready`, `complete`, `open`, `priority`, `score`, `owner`, `assignee`, `lastUpdated`, `source`, `notes`, `attachments`, or global `timeline` property.

## Universal history-detail envelope

Every admitted history variant below uses this semantic envelope. “Required when supplied by the real occurrence” means omission must remain explicit; CORDON must not invent an external reference, actor, evidence item, or next owner.

| Envelope field | Requirement | Exact operator capability supported |
|---|---|---|
| `detailReference` | Required; preserve the occurrence’s external/protocol/work-order/transaction reference when one exists, otherwise a stable operator reference to the received occurrence. | Lets the manager revisit the exact filing, notice, performance, inspection, order, cash movement, or cure result rather than rely on a label; supports handoff reconciliation. |
| `detailKind` | Required; one admitted variant named below. | Distinguishes preparation, legal effect, decision, dispatch, performance, acceptance, cash, and establishment so one occurrence cannot imply another. |
| `actor` | Required when an actor made, issued, performed, accepted, settled, or reviewed the occurrence; linked to the exact `Operator Party`. | Resolves who acted and whether the manager may take/supervise an Action or must route to another owner. |
| `authorityOrBasisReference` | Required when the occurrence depends on an Instrument, mandate, delegation, order, contract, right, or assigned review power. | Explains why the actor could act and prevents a cooperative, Comune, contractor, inspector, or portal from inheriting ungranted authority. |
| `consequentialTime` | Required; the legally, administratively, operationally, financially, or biologically consequential time or interval—not ingestion time. | Resolves applicability, named clocks, ordering of partial/reversal outcomes, and the consequence of waiting or proceeding. |
| `boundedScope` | Required; references the exact Party/Holding/Parcel/Area/Plant/Programme/Proceeding/Intervention and quantity, amount, or sub-scope only where the occurrence distinguishes it. | Supports map/legal/tree addressability, partial work and partial money, action refusal on ambiguous scope, and selective reopening without a global reset. |
| `outcome` | Required; the bounded effect that actually occurred, including an explicit unresolved, refused, partial, reversed, or no-effect result when that is the real outcome. | Answers what changed or landed without promoting filing to decision, performance to acceptance, order to cash, or installation to establishment. |
| `explanation` | Required when the actor supplied a reason, qualification, exception, exclusion, override, or uncertainty that changes a manager decision; otherwise omitted rather than fabricated. | Explains inclusion, refusal, hold, override, defect, financial shortfall, or remaining exposure. |
| `evidenceReferences` | Preserve only the minimum references the next decision or handoff must rely on. | Lets the manager defend the bounded answer and pass required proof without copying raw files or evidence schemas into operator state. |
| `changedDecisions` | Required; the named manager determinations, accepted Actions, or external decisions whose premises this detail changes. | Feeds `Determine Affected Decisions` and prevents undifferentiated reopening. |
| `reopeningEffect` | Required; the exact work to recompute/hold/reopen and, where confusion is material, the unaffected work to preserve. | Supports selective reopening and protects continuing duty, fallback, accepted work, cash history, and unrelated routes. |
| `nextOwner` | Required when another decision/action remains; linked to the exact `Operator Party`, otherwise explicitly no further owner for this bounded line. | Supplies the cross-responsibility handoff without transferring authority or creating a task object. |
| `nextNamedDecisionOrAction` | Required when work remains. | Tells the receiver what can be prepared, decided, committed, dispatched, accepted, claimed, cured, or reviewed next. |
| `nextClockConsequence` | Required when delay changes legality, eligibility, execution, finance, remedy, or establishment. | Preserves the active clock and consequence of delay in the handoff. |

No envelope field stores raw document bodies, source lineage, extraction confidence, portal payloads, telemetry, photographs, invoice lines, bank statements, or full legal/scientific reasoning. Those are backstage evidence reached through the minimum references.

## 1. Operator Party

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedPartyReference` | Identifies the exact person or organization across actor, authority, beneficiary, creditor, executor, acceptor, next-owner, and Action-authority resolution; qualification prevents unsafe collision between registries or identifier schemes. |
| I | `operatorTitle` | Lets the manager recognize and select the party in a decision, Action target, explanation, or handoff without exposing person/organization-specific dossiers. |
| I | `partyKind` | Preserves the accepted natural-person/organization distinction when validating identity, mandate, signing, creditor, or authority meaning without separate types. |
| C | `handoffContactReference` | Supplies the minimum current operational route for a named handoff or cure request; it is not a communications archive or full contact profile. |

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Current contextual roles, exact authority, mandate scope, responsible decisions, and Actions the party may take | Derive from controlling Instruments and current Proceeding/Intervention context so the manager can resolve authority by scope and date; a copied “role” would silently outlive its basis. |
| Current assigned handoffs and clocks | Derive from history details whose `nextOwner` is this Party; supports routing without a task/queue model. |
| Holdings, Parcels, Proceedings, Interventions, rights, and commitments in which the Party participates | Traverse links and owning objects; do not copy lists onto Party. |

### Backstage-only excluded

Addresses unrelated to a consequential handoff, full contact books, identity documents, demographics, household composition, corporate filings, ownership trees, signatures, KYC, portal accounts, bank details, credentials, raw registry rows, communication logs, source provenance, and role history. None changes a current manager decision unless referenced by a governing basis or a bounded received outcome.

### History contract

**No local multi-value history.** Identity corrections or authority changes are consequential only through the owning `Governing Instrument`, `Public Proceeding`, or `Intervention` detail. Party history shown to an operator is a derived projection of details whose `actor`, `nextOwner`, or bounded scope references the Party. This avoids a duplicate employment/role/contact timeline and preserves proposition-specific authority.

## 2. Agricultural Holding

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedHoldingReference` | Identifies the persistent farm administrative/operating unit across Party and Parcel change for applications, member routes, handoffs, and selective reopening. |
| I | `operatorTitle` | Lets the manager recognize and select the Holding while coordinating land, Programme, Proceeding, Intervention, and payment work. |

No current decision fact belongs intrinsically to the Holding. The operator’s current answers are route- and scope-specific projections.

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Current operating/responsible Parties and their authority | Derive from current governing/mandate facts so Party change does not rewrite Holding identity. |
| Current Parcel set and affected land | Traverse current Holding–Parcel facts; supports land addressability and impacted-population reasoning without duplicating cadastral detail. |
| Current duties, opportunities, member choices, cooperative decisions, Proceedings, Interventions, financial exposure, and next handoffs | Derive by route from linked objects and histories; supports all six questions without a Holding “case status.” |

### Backstage-only excluded

Complete farm-file payload, enterprise classifications not currently consequential, production/yield/accounting detail, historical Parcel operation records, subsidy dossier detail, raw registry/source fields, evidence files, and source synchronization history.

### History contract

**No local multi-value history.** A Holding correction, Party change, Parcel-scope change, filing, authority outcome, or field result is retained once on its owning Instrument, Proceeding, or Intervention. The Holding’s operator history is a projection of details whose `boundedScope` references the Holding. This supports selective reopening without a farm-wide timeline.

## 3. Cadastral Parcel

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedCadastralReference` | Identifies the exact legal land unit, including the qualification needed to avoid same-number collisions, for duty, access, filing, dispatch, execution, residual work, and handoff. |
| I | `operatorTitle` | Gives the manager a concise recognizable land label for selection and explanation; it does not replace the qualified legal reference. |
| C | `currentParcelGeometry` | Makes the legal land unit map-addressable for intersection, target, access, dispatch, and affected-work reasoning; it represents the Parcel and does not itself establish Area membership, duty, permission, or ownership. |

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Current jurisdiction and intersecting Official Areas, including partial intersections | Derive from Parcel and Area representations plus operative bases; supports legal/map addressability without copying overlays as legal truth. |
| Current official condition, duty, responsible Party, access consequence, permits, routes, Proceedings, Interventions, residual work, and clocks | Derive from authoritative Instruments and histories at the relevant proposition/date; supports Land and Field decisions without generic Parcel status. |
| Current Plants on the Parcel | Traverse conditional Plant identities; do not store counts as identity or let arbitrary detections create Plants. |

### Backstage-only excluded

Title-chain and deed detail, complete ownership/tenure/access normalization, raw cadastral records, survey/version lineage, geometry acquisition and cleaning history, imagery, detections, unrestricted land attributes, full legal overlays, and source conflict mechanics.

### History contract

**No local multi-value history.** Cadastral corrections and legally consequential scope changes appear through the Instrument/Proceeding detail that established or corrected them; field and establishment changes appear through Intervention history. Parcel history is a bounded-scope projection, preserving the exact land affected without creating a cadastral-source timeline.

## 4. Official Area

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedAreaReference` | Preserves the authority’s stable zone/regime identity across definition changes and lets the manager select the exact Area for legal/map explanation and affected-work recomputation. |
| I | `officialTitle` | Lets the manager recognize and compare the authority-preserved Area without replacing its qualified reference. |
| I | `areaKind` | Distinguishes the real official regime/zone class needed to ask the correct applicability question; it is not a workflow status vocabulary. |
| C | `currentAreaGeometry` | Makes the authoritative Area independently map-addressable across Parcels, Instruments, and changes; geometry represents the Area but does not alone decide applicability or duty. |

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Defining/currently operative Instrument and competent authority | Derive through basis links and Instrument history so an Area definition change retains its legal owner and date. |
| Intersecting Parcels/Plants and affected work | Derive spatially and then apply the governing proposition; supports selective propagation without persisting raw overlays as law. |
| Current regime consequence, duties, permissions, prohibitions, conflicts, and dates | Derive proposition-by-proposition from operative Instruments; avoids a copied legal matrix or one “area status.” |

### Backstage-only excluded

Raw GIS-service fields, tiles, topology repair, source versions, scientific surveillance layers, disease-model output, all legal provisions, map symbology, ingestion lineage, and non-consequential area history.

### History contract

**No local multi-value history.** Publication, definition, amendment, stay, and supersession are typed details on the controlling `Governing Instrument`; the Area is referenced in `boundedScope`. The Area’s change history is projected from those details so the authority-preserved identity remains stable while legal effect is stored once.

## 5. Individual Plant — conditional population

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedPlantReference` | Lets the manager select and revisit the same tree across official condition, Intervention target, execution, inspection, survival, defect, replacement, and cure; qualification binds it to the identity-preserving process. |
| I | `operatorTitle` | Provides a recognizable field/tree label for Action scope, explanation, and handoff without replacing stable identity. |
| C | `currentPlantLocation` | Makes the same Plant tree-addressable for exact targeting, inspection, replacement, and affected-work reasoning; location alone neither creates identity nor establishes condition. |

An instance is admitted only when an external identity-preserving process or validated reproducible observation-derived inventory already satisfies the accepted identity rule. There is no property that allows an operator to promote an arbitrary detection into a Plant.

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Parent Parcel, intersecting Official Area, and current legal target | Derive from location and authoritative scope; supports map/legal addressability without treating overlap as an official finding. |
| Current official condition, dispatched/performed treatment, separate acceptances, survival/defect, replacement/cure, and remaining exposure | Derive from qualified Proceeding/Intervention details; preserves each external owner and prevents one plant “status” from collapsing distinct results. |

### Backstage-only excluded

Raw detections, imagery, sensor observations, feature vectors, confidence scores, model/version details, taxon/lineage and Cultivar science beyond controlled identifiers used by a current decision, laboratory payloads, arbitrary tree attributes, and observation provenance.

### History contract

**No local multi-value history.** Official findings and corrections are projected from the owning Proceeding/Instrument occurrence; execution, inspection, acceptance, establishment, defect, replacement, and cure are projected from Intervention history whose `boundedScope` names the Plant. This preserves tree sameness without a duplicate biological timeline.

## 6. Public Programme or Measure

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedProgrammeReference` | Identifies the enduring opportunity/support route across openings, Instruments, Proceedings, claims, public outcomes, and fallback. |
| I | `officialTitle` | Lets the manager recognize and compare the Programme/Measure in route selection, explanation, filing, and handoff. |
| I | `programmeKind` | Distinguishes the real support/measure route sufficiently to select the correct Proceeding and named Action; it is not a lifecycle status. |

No eligibility, concession, budget, deadline, ranking, claim stage, or availability value is intrinsic current Programme truth; each belongs to an Instrument, Proceeding, member-specific outcome, or derived population answer.

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Current opening, applicable rules, population, deadlines, permitted claim paths, and collective constraints | Derive from operative Instruments and affected member–land–Intervention facts; supports complete-population evaluation without freezing one vintage on the Programme. |
| Eligibility indications, member choices, mandate/pursuit, public outcomes, capacity commitments, rights, claims, and fallback | Derive at the member/land/Proceeding/Intervention grain; prevents Programme-level status from collapsing independent decisions. |

### Backstage-only excluded

Full call text, legal corpus, scoring/ranking tables, budget ledgers, form schemas, programme lineage research, raw eligibility calculations, source documents, publication acquisition, and all possible criteria not consequential to a current named decision.

### History contract

**No local multi-value history.** Openings and rule changes are Instrument history; member-specific filing, ranking, concession, claim, accounting, cash, audit, and recovery are Proceeding history. Programme history is a projection of those details scoped to the Programme, not a copied programme timeline.

## 7. Governing Instrument

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedInstrumentReference` | Identifies the exact legal, administrative, contractual, or financial basis for authority, applicability, clock, Action refusal, explanation, and handoff. |
| I | `officialTitle` | Lets the manager recognize and select the controlling basis in a legal or operational explanation. |
| I | `instrumentKind` | Distinguishes which real authority/basis semantics apply—without defining a status vocabulary—so a notice, mandate, concession, contract, order, or rule is not treated interchangeably. |
| C | `operativeInterval` | Supplies the current consequential period used to resolve authority, applicability, mandate, commitment, and named clocks; ingestion/publication dates are not substituted unless legally consequential. |
| C | `boundedOperativeEffect` | States only the current decision-changing proposition this Instrument creates, changes, permits, requires, limits, or ends for its linked scope. It supports deterministic applicability and explanation without copying normalized provisions or a full legal matrix. |

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Whether the Instrument is controlling for a selected proposition, land, Party, route, and date | Derive from scope, competence, interval, specificity, and history; supports legal addressability without a generic “active” status. |
| Current duties, permissions, responsible actors, clocks, conflicts, affected work, and next owners | Derive through linked scope and consequential histories; supports six-question answers without duplicating results on the Instrument. |
| Current text/version label | Derive from the latest consequential amendment/supersession detail and backstage source; do not treat document-version mechanics as an operator fact. |

### Backstage-only excluded

Full text and clause normalization, legal citation graph, every provision, interpretation notes, source copies, gazette scraping, OCR/extraction, provenance, document hashes, legal research, superseded text bodies, signatures, attachments, raw contract terms not changing a current decision, and ingestion/recording dates.

### Typed multi-value history: `instrumentHistory`

Only these variants are admitted initially:

| Variant | Variant-specific fields beyond the universal envelope | Exact operator capability supported |
|---|---|---|
| `noticeOrService` | `addresseeOrPublishedScope`; `authorizedChannel`; `legalEffectTime`; `clockStartedOrChanged` | Distinguishes awareness from legally effective notice, identifies the correct addressee/scope and channel, starts the named clock, and routes missing/disputed service. |
| `publication` | `publishedScope`; `publicationInterval`; `legalEffectTime`; `clockStartedOrChanged` | Proves legally consequential publication for the exact jurisdiction/Area/subject and preserves republication or correction without storing gazette mechanics. |
| `amendment` | `changedOperativeScope`; `priorEffectReference`; `resultingEffect`; `resultingInterval` | Explains what changed, recomputes only decisions relying on that effect, and preserves unaffected provisions/routes. |
| `stayOrDerogation` | `heldOrExceptedScope`; `grantingActor`; `effectiveInterval`; `resultingConstraintOrPermission` | Prevents a stay/derogation from clearing unrelated duties and tells the manager what waits, what continues, and who owns the next decision. |
| `supersessionOrTermination` | `replacedScope`; `successorOrEndingBasisReference`; `effectEndTime`; `survivingEffect` | Ends only the superseded authority/effect, reopens dependent work, and preserves surviving mandates, duties, contracts, rights, or fallback. |

Reject separate histories for source acquisition, ingestion, OCR, non-operative drafts, editorial correction, or every legal citation. They do not change an operator decision.

## 8. Public Proceeding

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedProceedingReference` | Identifies one formal matter across filings, repair, authority outcomes, appeal, audit, recovery, and next-owner handoff. |
| I | `operatorTitle` | Lets the manager recognize and select the matter in preparation, explanation, routing, and cross-responsibility handoff. |
| I | `proceedingKind` | Distinguishes the formal matter’s real decision route—application, permit, claim, audit/recovery, or other bounded route—without becoming a workflow-stage vocabulary. |
| C | `boundedMatterScope` | Preserves exactly what member/beneficiary, land, operation, amount/right, and requested or reviewed proposition this one matter concerns; it supports refusal on ambiguous filing/decision scope. |

The current public decision, filing stage, claimed/admitted/ordered/settled amounts, deadline, and next owner are derived from typed history. They are not mutable current-status properties.

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Latest protocolled filing and exact scope now before the authority | Derive from filing-version details; distinguishes draft, release, correction, and supersession. |
| Current authoritative outcome and what it does not establish | Derive by outcome kind and scope; keeps eligibility, concession, permit, acceptance, accounting, cash, audit, and recovery independent. |
| Active clock, readiness, cure owner, appeal route, amount at each financial stage, unsettled cash, remaining right/exposure, and affected downstream work | Derive from Instrument basis plus ordered history details; supports explanation and selective reopening without a generic case status. |

### Backstage-only excluded

Dossier files, form field/value normalization, portal payloads/screenshots, correspondence bodies, raw evidence, validation logs, source ingestion, full accounting records, invoice lines, bank documents, reconciliation traces, authority-internal workflow, and normalized stage/scope relationship objects.

### Typed multi-value history: `proceedingHistory`

| Variant | Variant-specific fields beyond the universal envelope | Exact operator capability supported |
|---|---|---|
| `filingVersion` | `filingKind`; `releasingParty`; `releasedScope`; `releaseTime`; `protocolOrReceiptReference`; `supersededFilingReference` | Proves what was actually released, by whom and when; starts the public clock; keeps preparation separate from release and later authority outcome. |
| `authorityOutcome` | `decidingAuthority`; `decidedProposition`; `decidedScope`; `effectiveInterval`; `conditionsOrExclusions`; `priorOutcomeAffected` | Records a competent eligibility, ranking, concession, permit, compulsory/funded acceptance, appeal, remedy, or other public result without CORDON manufacturing it or extending it beyond scope. |
| `financialInstructionOrAdmission` | `claimReference`; `claimedScopeOrAmount`; `admittedExcludedOrHeldScopeOrAmount`; `repairRequirement`; `remainingClaimOrRight` | Keeps requested, evidenced, admitted, excluded, suspended, and repairable claim effects separate and routes the exact cure. |
| `liquidationOrPaymentOrder` | `creditor`; `recognizedOrOrderedAmount`; `deductionOrOffset`; `relatedRightOrClaim`; `cancellationOrReissueReference`; `outstandingOrderedBalance` | Distinguishes public accounting and order from cash, supports partial/cancelled/reissued amounts, and hands off reconciliation to the correct owner. |
| `cashTransaction` | `transactionReference`; `payer`; `payee`; `direction`; `amount`; `valueTime`; `relatedOrderOrRight`; `partialReturnReversalOrRecoveryRelation`; `remainingSettlementOrRecoveryExposure` | Proves actual money movement from authenticated bank/treasury evidence; preserves partial, multiple, returned, reversed, repaid, and recovered cash without a manual “paid” marker. |
| `auditRevocationOrRecovery` | `exercisingAuthority`; `affectedRightClaimOrTransaction`; `allegedOrDecidedScopeOrAmount`; `responseAppealOrStayReference`; `remainingRecoveryOrRemedy` | Preserves later financial exposure without rewriting historical concession, order, cash, accepted field work, or unrelated aftercare. |

No single variant may be reused as a generic “authority update.” If the owner, effect, scope, or consequence is not captured by one variant, retain the external result backstage and selectively reopen this contract rather than flatten it.

## 9. Intervention

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedInterventionReference` | Identifies one bounded physical undertaking across design, capacity, dispatch, performance, acceptance, payment, aftercare, replacement, and cure. |
| I | `operatorTitle` | Lets the manager recognize and select the undertaking for portfolio comparison, accepted Actions, explanation, and handoff. |
| I | `interventionKind` | Distinguishes the real physical undertaking/action family needed for scope, design, evidence, acceptance, and remedy; it is not a workflow status. |
| C | `boundedIntendedScope` | Defines the member/land/Plant and physical/material outcome the undertaking is meant to deliver; it supports mandate/pursuit, capacity, dispatch refusal, as-built comparison, and residual-work calculation. |
| C | `boundedEndpoint` | States the intended Wedge 1 result—through required early establishment/replacement/cure where applicable—so the manager can determine remaining exposure without expanding into productive maturity or general orchard management. |

Current design, readiness, recommendation, commitment, dispatch, performed scope, acceptance, payment consequence, establishment, and completion are derived from linked facts and typed histories, not copied Intervention statuses.

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Current member route, mandate/pursuit decisions, authority, target, design, permits, access, committed resources, finance/evidence conditions, and named-action readiness | Derive from current bases and commitments; supports each accepted Action without a mutable readiness flag. |
| Recommended portfolio inclusion and alternatives | Derive through `Compare Feasible Intervention Portfolios`; recommendation never becomes commitment truth. |
| Dispatched, performed, accepted, defective, established, cured, paid-related, and residual scopes | Derive independently from typed details; prevents dispatch→performance→acceptance→cash→establishment collapse. |
| Next owner, active clock, affected decisions, and unaffected continuing work | Derive from latest consequential details by bounded scope; supports handoff and selective reopening. |

### Backstage-only excluded

Full technical design files, scientific model inputs, Cultivar/taxon detail beyond controlled decision identifiers, supplier catalogs, Lot/custody normalization, crew work packs, telemetry, photos, raw measurements, evidence schemas, optimization traces, invoices, procurement records, generic tasks/issues, and unrestricted orchard-management attributes.

### Typed multi-value history: `interventionHistory`

| Variant | Variant-specific fields beyond the universal envelope | Exact operator capability supported |
|---|---|---|
| `capacityDecision` | `portfolioDecisionReference`; `affectedCommitmentReferences`; `committedReleasedOrReallocatedScope`; `decisionReason`; `overrideExplanation`; `fallbackOrDeferralConsequence` | Records the atomic effect of `Commit or Rebalance Intervention Capacity`, distinguishes recommendation from commitment, explains overrides, and reopens only readiness/schedules that depended on changed capacity. |
| `dispatch` | `dispatcher`; `dispatchAuthorityReference`; `authorizedScope`; `executor`; `excludedScope`; `workClock`; `stopOrReturnConditions` | Records the atomic effect of `Dispatch Intervention`, proves exact field authority and handoff, and never implies performance. |
| `performance` | `dispatchReference`; `executor`; `performedScope`; `methodOrMaterialSummary`; `deviationOrSubstitution`; `residualScope` | Preserves partial/multiple execution and as-built scope, supports acceptance/claim handoff, and never implies acceptance. |
| `inspection` | `inspector`; `inspectionAuthorityReference`; `inspectedPerformanceReferences`; `inspectedScope`; `findings`; `requiredNextReview` | Proves what occurrence and scope were inspected by whom, routes exceptions, and keeps inspection separate from each acceptance decision. |
| `acceptance` | `acceptanceBasis`; `acceptor`; `acceptedRejectedOrExcludedScope`; `conditionsOrDefects`; `residualDutyRightOrRework`; `reinspectionRequirement` | Keeps compulsory legal, funded-work, and private contractual acceptance separate by basis and owner; identifies the exact consequence for duty, claim, warranty, or rework. |
| `defectOrDeviation` | `findingSource`; `affectedPerformedOrAcceptedScope`; `controllingBasis`; `consequenceClasses`; `proposedOrRequiredRemedy`; `interimScopedHold` | Routes a defect, unauthorized change, obstruction, or failed premise to the actor competent for each consequence while preserving unaffected work. |
| `establishmentReview` | `reviewer`; `reviewAuthorityReference`; `reviewWindow`; `reviewedAcceptedInstallationReferences`; `supportedPlantParcelOrCohortScope`; `establishedDefectiveOrUnresolvedScope`; `uncertaintyOrThresholdQualification`; `remainingExposure` | Distinguishes administrative installation from bounded biological establishment, identifies failed scope and cure owner, and stops at the accepted Wedge 1 endpoint. |
| `replacementOrCure` | `creatingDefectOrReviewReference`; `authorizingBasis`; `requiredRemedyScope`; `performedRemedyScope`; `acceptanceOrReinspectionReference`; `residualOpenScope` | Preserves the cure chain inside the undertaking when reality does not create a separate Intervention and proves what remains after replacement/rework. |

The `performance`, `inspection`, `acceptance`, `establishmentReview`, and `replacementOrCure` variants are repeatable and must preserve explicit cross-references so partial and reversal structure is not inferred by order alone.

## 10. Intervention Capacity Commitment

### Retained properties

| Class | Semantic property | Exact operator capability supported |
|---|---|---|
| I | `qualifiedCommitmentReference` | Identifies the exact current cooperative capacity fact for review, Action targeting, conflict detection, and reconciliation; it is not a source row or platform key. |
| D | `operatorTitle` | Derive from capacity owner, resource, Intervention, and period so the manager can recognize it without maintaining duplicate title truth. |
| C | `capacityDescription` | Names the scarce cooperative-controlled resource or slot being bound; supports feasibility, double-booking checks, explanation, and exact Action scope without normalizing supplier/inventory detail. |
| C | `committedExtent` | Preserves the quantity/slot extent actually bound to the linked Intervention; distinguishes an exact commitment from tentative availability or a recommendation. |
| C | `commitmentInterval` | Preserves when the capacity is bound or scheduled, supporting feasibility, clock comparison, expiry/release consequences, and rebalancing. |
| C | `bindingEffect` | States the real commitment effect created by the authorized cooperative decision, without selecting a platform status vocabulary; supports refusal when a proposed rebalance would violate a protected or incompatible commitment. |
| C | `portfolioDecisionReference` | Groups the exact commitments changed by one atomic portfolio decision so the manager can explain the complete affected set and detect partial rebalance. |
| C | `decisionExplanation` | Preserves the authorized reason and, where applicable, override explanation/review consequence; supports fairness/governance explanation without storing optimization traces or deliberation. |
| C | `releaseOrSubstitutionCondition` | States only the condition that can end, release, or substitute this committed capacity when that condition changes feasibility or handoff; supports safe rebalance and selective reopening. |

Capacity owner and Intervention are direct relationship endpoints, not copied properties. A recommended quantity, availability forecast, score, rank, alternative portfolio, or supplier record is not a Commitment property.

### Derived projections, not properties

| Projection | Why derived / capability supported |
|---|---|
| Whether the commitment governs a proposed dispatch or schedule at a selected time | Derive from interval, binding effect, release condition, current Intervention scope, and later capacity-decision detail; no generic commitment status. |
| Remaining/free capacity, conflicts, feasible schedules, protected commitments, alternatives, sensitivity, and expected loss reduction | Derive across the complete population through portfolio logic; prevents copied optimization truth and nomination-only allocation. |
| Prior commitment, released/reallocated extent, affected Interventions, fallback, and review need | Derive from `Intervention.interventionHistory.capacityDecision` details grouped by `portfolioDecisionReference`; supports atomic Action explanation and selective reopening. |

### Backstage-only excluded

Supplier/crew/inventory master detail, rate cards, calendars, offers, negotiations, procurement documents, raw schedule rows, optimization variables/traces, biological model internals, ranking scores, policy deliberation, identified Lot detail, source provenance, and generic reservation/status audit logs.

### History contract

**No local multi-value history.** The relationship object owns one exact current commitment fact. Atomic create/change/release/reallocation consequences are recorded once as repeatable `capacityDecision` details on each affected `Intervention`, joined by `portfolioDecisionReference` and referencing the affected Commitment facts. This lets the manager reconstruct prior/resulting commitments and verify a complete affected-set rebalance without duplicating the same decision on every Commitment.

If that representation cannot preserve a multi-Intervention partial/reversal decision safely, the selective-reopening rule applies: reconsider the history owner or a focused occurrence type. Do not pre-emptively add a generic commitment-event population.

## Ruthless rejection ledger

| Rejected field family | Why excluded from the operator core |
|---|---|
| Generic status, stage, ready, complete, open/closed, priority, health, traffic-light, or progress | Collapses independently governed decisions and becomes stale beside typed histories and live Functions. |
| Generic owner, assignee, queue, task, issue, exception, note, or activity feed | Hides real decision authority and handoff semantics; `nextOwner` belongs to the consequential detail that created the handoff. |
| Copied role/authority/mandate properties on Party, Holding, Parcel, Proceeding, or Intervention | Authority is basis-, scope-, and date-specific; derive it from the controlling Instrument and context. |
| Copied legal applicability, duty, permit, jurisdiction, or Area membership flags | Geometry and legal effect are not the same; derive proposition-specific answers from Parcel/Area/Instrument facts. |
| Copied current filing/outcome/financial-stage fields on Proceeding | Filing versions, authority outcomes, accounting, cash, audit, and recovery must remain separate typed details. |
| Copied current execution/acceptance/establishment fields on Intervention or Plant | Dispatch, performance, inspection, each acceptance basis, establishment, and cure must remain separately attributable and repeatable. |
| Recommendation, score, rank, predicted availability, or portfolio on Capacity Commitment | The Function output is non-binding; only an authorized decision creates a Commitment. |
| Normalized legal clauses, legal-effect relationship objects, jurisdiction matrices, source documents, evidence objects, scientific observations, taxa/cultivars, Lots, invoices, bank transactions as core objects | The manager needs the current bounded answer and minimum basis reference, not an independently navigable administration/science/source universe. Cash transactions remain typed Proceeding details because partial/reversal identity is required. |
| `createdAt`, `updatedAt`, ingestion time, recorder, source table/column/file, pipeline run, extraction confidence, document hash | Backstage mechanics do not establish legal effect, authority, performance, acceptance, settlement, or establishment. |
| Unbounded descriptions, notes, attachments, and arbitrary metadata | They cannot be tied to a named decision, Action, explanation, handoff, addressability requirement, or selective-reopening effect. |

## Sufficiency check against accepted operator capabilities

| Required capability | Minimum representation that supplies it |
|---|---|
| What changed and what it affects | Typed history envelope `changedDecisions` + `reopeningEffect`, scoped to qualified object references; `Determine Affected Decisions` remains derived. |
| What is required, allowed, or blocked | Instrument `boundedOperativeEffect` and `operativeInterval`, exact scope/addressability, current external outcomes, and derived proposition-specific applicability/readiness. |
| Who chooses/decides and which route continues | Qualified Party identity plus contextual Instrument/Proceeding/Intervention authority; member/public decisions remain received outcomes; four accepted manager Actions remain bounded. |
| Named-action readiness | Current object facts, direct links, exact commitments, and latest typed outcomes feed `Assess Named-Action Readiness`; no readiness property is stored. |
| What was done and who accepted it | Repeatable Intervention `performance`, `inspection`, and basis-specific `acceptance` details with actor, scope, evidence reference, and consequence. |
| Whether the intended result landed and what remains open | Independent Proceeding financial details and Intervention acceptance/establishment/cure details; current exposure is derived, never a global completion field. |
| Map/legal/tree addressability | Parcel geometry, Area geometry, conditional Plant location, qualified references, bounded scopes, and Instrument basis. Geometry never manufactures law or identity. |
| Cooperative pursuit, capacity, and dispatch Actions | Intervention intended scope/endpoint; exact Party authority projection; exact current Capacity Commitments; Instrument/Proceeding outcomes; Action effects retained in typed history. |
| Explainability and handoff | Minimum basis/evidence references, bounded outcome/explanation, next owner, next named decision/action, and clock consequence on each consequential detail. |
| Selective reopening | Every consequential detail names changed decisions and exact reopening/unaffected scope; no generic case reset or global timeline is needed. |

## Selective reopening threshold

Promote an excluded field, add a local history, or admit a focused occurrence type only when a proven operator workflow shows that, without it, the manager cannot independently select the same fact/occurrence, run or supervise an authorized Action against it, compare it across parents, preserve partial/reversal identity, explain a bounded decision, hand it off, or selectively reopen only affected work.

Source fidelity, normalization preference, legal/scientific completeness, reporting convenience, UI demand, and platform capability are not sufficient reasons. Gates 6–7 remain closed.

## Verdict

The minimum operator property core is the small set above: qualified reference/title/discriminator fields needed for exact identity and addressability; only the enumerated object-owned current-decision facts (`currentParcelGeometry`, `currentAreaGeometry`, `currentPlantLocation`, `operativeInterval`, `boundedOperativeEffect`, `boundedMatterScope`, `boundedIntendedScope`, `boundedEndpoint`, and the exact capacity-commitment facts); derived projections for all recomputable current answers; and backstage exclusion of normalized legal, scientific, source, evidence, financial, and operational detail.

There are exactly three typed multi-value local history contracts—`instrumentHistory`, `proceedingHistory`, and `interventionHistory`—plus explicit no-local-history contracts for the other seven types. This preserves protocolled versions, partial/multiple execution and acceptance, partial/returned/reversed cash, atomic capacity rebalance effects, explanations, handoffs, and selective reopening without event types, opaque arrays, Time Machine copies, or source-shaped histories.

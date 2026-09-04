# Gate 6 — Foundry Ontology and data capability map

Status: **GATE 6 CAPABILITY FINDING — representation-level selective reopenings required; Gate 7 remains closed**  
Date: 22 August 2026  
Authority: `REDESIGN_SEQUENCE.md`; `gate-5-reconciled-operator-graph.md`; `gate-5-core-ontology.md`; `gate-5-operator-decision-ledger-six-questions.md`; `gate-5-operator-capability-ledger-five-responsibilities.md`  
Source boundary: current public Palantir documentation at `palantir.com/docs`, retrieved through the Palantir MCP documentation index. No Foundry state was inspected or changed.

**Current environment correction:** Owen confirms full Foundry/AIP capability availability. Any enrollment-dependent caveat below remains a product-maturity note from documentation, not an availability blocker for this build.

## 1. Scope, method and verdict

This document maps current Foundry Ontology and data mechanics to the accepted Gate 5 graph. It does **not** choose or describe an operator surface. It tests 65 accepted elements and mechanism dependencies:

- nine operator object types;
- two object-backed relationship types;
- 32 direct semantic links;
- five factual history contracts; and
- 17 cross-cutting platform dependencies.

Each row names the best-fit current capability, viable alternatives, known limitations or enrollment gates, and whether the Gate 5 representation must selectively reopen. “Reopen” means the narrow physical representation only; it does not revive the rejected 39+10 normalized proposal or change the accepted semantic owner.

### Provenance labels

- **[Fact]** is directly supported by a fetched official Palantir documentation page linked inline.
- **[Inference]** is the application of those documented capabilities to the accepted CORDON graph.
- **[Enrollment unknown]** is a capability whose availability or raised limit must be confirmed in the target enrollment.

### Executive verdict

1. **Keep the nine operator object types and two independently mutable relationship objects.** Use OSv2 object types with source-backed identity/current facts and action-edited cooperative facts. The two relationship objects remain first-class Action targets; Palantir’s optional object-backed-link projection may supplement traversal but must not hide those objects.
2. **Implement the 32 semantic adjacencies as link types, but choose backing by cardinality.** The four accepted single-parent relations use foreign keys; the remaining relations default to many-to-many join-table links unless their owning object already provides a singular foreign key. Foundry’s one-to-one declaration is advisory, not an enforced uniqueness constraint.[Official link-type documentation](https://www.palantir.com/docs/foundry/object-link-types/create-link-type)
3. **Selectively reopen contextual authority detail and all five factual histories to hidden technical record resources.** Struct arrays cannot contain typed object references, are depth-one only, have cross-entry query semantics that can return false field combinations, and an array edit replaces the entire array. Those mechanics do not safely satisfy stable Party/evidence references, independently attributable occurrences, append/reversal behavior, or one-occurrence queries.[Official struct documentation](https://www.palantir.com/docs/foundry/object-link-types/structs-overview) [Official array-edit documentation](https://www.palantir.com/docs/foundry/functions/api-objects-links#array-properties)
4. **Selectively reopen `Intervention Plant Scope` as a hidden fact-bearing relationship resource.** A bare current M:M link plus parent-local struct history cannot safely query one Plant across dispatch, performance, inspection, acceptance, establishment, replacement and cure, nor reverse one phase without whole-array replacement.
5. **Selectively reopen focused cash occurrences.** Authenticated partial, returned, reversed, repayment and recovery transactions have stable identity and reconciliation links that exceed safe Proceeding-local struct history. Keep them hidden from the core operator type inventory unless later operator evidence proves independent navigation/action need.
6. **Do not reopen Lot.** Current platform mechanics do not themselves prove an operator Lot allocation, dispatch, substitution, warranty or return decision.
7. **Use live read-only Functions as the authoritative mechanism for the four Gate 5 answers; treat derived properties only as optional convenience.** Derived properties are available but remain Beta, runtime-evaluated, OSv2-only, unavailable for text search, and currently conflict with struct-bearing TypeScript OSDK queries.[Official derived-properties documentation](https://www.palantir.com/docs/foundry/ontology/derived-properties)
8. **Use Automate and a dependency index to detect a material received change and invoke selective recomputation, but do not write generic reopened/ready/complete state.** Automate can watch Ontology conditions and submit Actions or execute Functions.[Official Automate documentation](https://www.palantir.com/docs/foundry/automate/overview)

## 2. Foundry capability baseline

### 2.1 OSv2 is a hard baseline

[Fact] OSv1 was documented as unavailable after 30 June 2026; OSv2 is the current canonical object store. OSv2 provides incremental indexing, streaming datasources, up to 10,000 object edits in one Action by default, 2,000 properties per object type, and a default Search Around limit of 100,000 objects. Higher Action or Search Around limits require Palantir Support/enrollment changes.[Official Ontology backend documentation](https://www.palantir.com/docs/foundry/object-backend/overview)

[Inference] Every CORDON object and editable M:M link should be OSv2-native from inception. Mixed OSv1/OSv2 design is not an acceptable target.

### 2.2 Storage mechanisms

[Fact] Object types map datasource rows to objects and columns to properties. Link types use foreign keys for 1:1/M:1, join-table datasets for M:M, or an intermediary object type when the relationship carries metadata. Object-backed links require the two endpoint types, the intermediary type, and two prerequisite M:1 links.[Official Ontology concepts](https://www.palantir.com/docs/foundry/ontology/core-concepts) [Official link creation](https://www.palantir.com/docs/foundry/object-link-types/create-link-type)

[Inference] “Direct semantic link” means an Ontology link type, not necessarily a foreign-key link. Most accepted CORDON links are semantically M:M and therefore need join tables. “Object-backed relationship” means the relationship object remains the fact owner; Palantir’s object-backed-link feature is an optional traversal projection over that fact owner.

### 2.3 Property, derived and backstage split

[Fact] OSv2 supports datasource-backed properties and edit-only properties. Edit-only properties are Action/API-edited, do not require a datasource column, and always apply regardless of timestamp conflict-resolution strategy.[Official property overview](https://www.palantir.com/docs/foundry/object-link-types/properties-overview) [Official edit application semantics](https://www.palantir.com/docs/foundry/object-edits/how-edits-applied)

[Inference] Use:

- **source-backed properties** for qualified identities, source-owned current geometry/location, external outcomes and authoritative source timestamps;
- **edit-only properties** only for cooperative-owned facts created by the four bounded Actions, never for public/bank/professional truth;
- **Functions or optional derived properties** for live applicability, readiness, affected decisions, portfolios and remaining exposure;
- **datasets, restricted views, media/evidence resources and hidden technical object/link types** for raw corpus, evidence, lineage, calculations and repeatable records.

## 3. Capability matrix — nine operator object types

| ID | Accepted element | Best-fit current capability | Alternatives | Limitations / enrollment gates | Gate 5 selective reopen? |
|---|---|---|---|---|---|
| OT01 | Operator Party | OSv2 object type; source-backed qualified identity, title and `partyKind`; links provide navigation. | Separate Person and Organization object types; interface over separate types. | One Party type cannot provide type-specific required properties or divergent granular security without conditional logic. Interfaces add no benefit unless polymorphic consumers are proven. | **No.** Reopen Person/Organization only on measured property, Action or access divergence. |
| OT02 | Agricultural Holding | OSv2 object type with persistent qualified key; source-backed identity and current operating-unit facts. | Virtual table or dataset-only backstage record. | Current steward/representative details cannot safely be typed Party-reference structs; use hidden contextual records (X06). | **Object stays; contextual-detail representation reopens.** |
| OT03 | Cadastral Parcel | OSv2 object type with `geoshape` current geometry, qualified cadastral key and source-backed current facts. | Geometry dataset plus virtual table; externally tiled layer. | Geoshape must be valid WGS84 GeoJSON Geometry; geometry does not establish law, tenure or applicability.[Geospatial documentation](https://www.palantir.com/docs/foundry/geospatial/ontology#polygons-and-lines) | **Object no; contextual tenure/access records reopen.** |
| OT04 | Official Area | OSv2 object type with `geoshape`, `areaKind`, qualified official key and parent-area link. | Mapbox Boundaries reference for standard administrative display; dataset-only layers. | Mapbox or external geometry is a map representation, not authoritative legal effect. External layers can require Palantir configuration. | **No.** Keep Instrument basis and applicability separate. |
| OT05 | Individual Plant | Extension-gated OSv2 object type with string PK and `geopoint`; source-backed only from preserved identity or validated reproducible inventory. | Keep detections/observations backstage; cohort-only analysis. | A point is only location; arbitrary detections cannot mint identity. Population scale and refresh cadence must be measured. | **No type reopening.** Enrollment/population remains gated; phase-scope representation reopens (X15). |
| OT06 | Public Programme or Measure | OSv2 object type with source-backed identity/kind; linked Instruments, Proceedings and Pursuits. | Dataset-only programme reference table. | Openings, eligibility and concession must remain linked/derived, not copied status. | **No.** |
| OT07 | Governing Instrument | OSv2 object type for operator-level operative basis; source-backed identity/current operative facts, linked backstage legal corpus. | Full legal-document object type; media set only. | Full clauses/OCR/citation graph would produce a legal administration model; keep backstage. History structs fail the typed-history contract (H01). | **Object no; history representation yes.** |
| OT08 | Public Proceeding | OSv2 object type for one formal matter; source-backed external outcomes and action-received cooperative filings. | One object per filing/outcome; generic Case. | No generic status or amount. Financial occurrence history needs stable partial/reversal identity. | **Object no; history and focused cash occurrence yes.** |
| OT09 | Intervention | OSv2 object type for one physical undertaking; source-backed/external outcomes plus manager Action effects. | One object per field phase; generic Work Item. | No global completion. Plant-phase records and repeated acceptance/result grain exceed safe local structs. | **Object no; history and Plant-phase scope yes.** |

## 4. Capability matrix — two object-backed relationship types

| ID | Accepted element | Best-fit current capability | Alternatives | Limitations / enrollment gates | Gate 5 selective reopen? |
|---|---|---|---|---|---|
| OR01 | Cooperative Pursuit | OSv2 intermediary/fact-owner object type, independently queryable and editable; singular endpoint FKs plus M:M scope links; optional Palantir object-backed-link projection. | Join table plus endpoint properties; store decision on Programme or Intervention. | A plain join table cannot own outcome, authority, fallback or history. Palantir object-backed links require prerequisite objects and M:1 links. | **No semantic reopen.** History becomes hidden records; contextual authority uses hidden record mechanics. |
| OR02 | Intervention Capacity Commitment | OSv2 intermediary/fact-owner object type and target of function-backed portfolio Action; singular owner and Intervention FKs; optional object-backed-link projection. | M:M join table; properties copied to Intervention. | A join table cannot own extent, interval, firmness, override or release. Atomic rebalance must fit Action limits and concurrency checks. | **No semantic reopen.** History becomes hidden records. |

## 5. Capability matrix — 32 direct semantic links

### 5.1 Member, Holding, Parcel and Plant

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL01 | Party is member of cooperative Party | M:M join-table link; contextual membership facts in hidden records. | Self-referential backing object. | Direct link navigates only and grants no authority. | **Link no; contextual record yes.** |
| DL02 | Party operates or represents Holding | M:M join-table link; context details hidden. | Backing object relationship. | M:M is required because neither endpoint is singular by Gate 5. | **Link no; contextual record yes.** |
| DL03 | Holding operates Parcel | M:M join-table link. | FK only if authoritative evidence later proves one current Holding per Parcel. | Gate 5 explicitly preserves M:M; do not tighten from convenience. | **No.** |
| DL04 | Party has standing on Parcel | M:M join-table link; tenure/consent/access details hidden. | Backing object relationship. | Link itself cannot safely carry role, basis, scope and interval. | **Link no; contextual record yes.** |
| DL05 | Parcel contains identified Plant | Plant-side single FK to Parcel, exposed as Parcel 1:M Plant link. | M:M join table. | Single-valued FK represents one current Parcel per Plant; Action and ingestion validation must reject missing/ambiguous parents. | **No.** |

### 5.2 Area and jurisdiction

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL06 | Area has parent Area | Self-referential M:M join-table link. | Area-side parent FK if authoritative hierarchy is strictly single-parent. | Administrative/regulatory overlaps can have multiple parents; do not infer a tree. | **No.** |
| DL07 | Governmental Party has jurisdiction Area | M:M join-table link. | FK on Area for strictly singular jurisdiction families. | Jurisdiction grants no competence; competence remains Instrument/Proceeding context. | **No.** |

### 5.3 Governing Instruments

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL08 | Instrument has Instrument Party | M:M join-table link; role/authority details hidden on Instrument-context records. | Object-backed relationship. | Direct link cannot encode issuer/party/authority interval. | **Link no; contextual record yes.** |
| DL09 | Instrument defines or governs Area | M:M join-table link. | Derive from clauses/geometries backstage. | Geometry overlap cannot create this legal semantic link. | **No.** |
| DL10 | Instrument governs Programme | M:M join-table link. | FK on Programme. | Programmes can have concurrent/amending instruments. | **No.** |
| DL11 | Instrument provides basis for Proceeding | M:M join-table link. | FK on Proceeding. | Proceedings can have multiple controlling instruments. | **No.** |
| DL12 | Instrument provides basis for Intervention | M:M join-table link. | FK on Intervention. | Physical work can have multiple legal/contractual bases. | **No.** |
| DL13 | Instrument changes Instrument | Self-referential M:M join-table link; change kind remains H01. | Single predecessor FK. | Amendment/stay/supersession can be non-linear. | **No.** |

### 5.4 Programmes and Proceedings

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL14 | Programme has Proceeding | M:M join-table link. | Proceeding-side Programme FK. | A Proceeding may involve multiple Measures; retain M:M. | **No.** |
| DL15 | Proceeding follows or affects Proceeding | Self-referential M:M join-table link. | Predecessor FK. | Appeals, audits, recovery and reissues are graph-shaped. | **No.** |
| DL16 | Proceeding involves Party | M:M join-table link; role/authority details hidden on Proceeding context. | Object-backed role relationship. | Navigation does not establish applicant, beneficiary, creditor or authority. | **Link no; contextual record yes.** |
| DL17 | Proceeding concerns Holding | M:M join-table link. | Proceeding-side FK. | Formal matters may span Holdings and Holdings may enter many matters. | **No.** |
| DL18 | Proceeding concerns Parcel | M:M join-table link. | Proceeding-side array of IDs. | Arrays are not typed traversable links and scale/query worse than link types. | **No.** |
| DL19 | Proceeding concerns identified Plant | Conditional M:M join-table link. | Parent-local Plant ID array. | Only populated where Plant identity gate passes. | **No.** |
| DL20 | Proceeding concerns Intervention | M:M join-table link. | Proceeding-side FK. | One matter can concern several undertakings and vice versa. | **No.** |

### 5.5 Interventions

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL21 | Intervention has Intervention Party | M:M join-table link; contextual role/authority details hidden. | Object-backed role relationship. | Direct link cannot distinguish manager/executor/technician/inspector/acceptor or interval. | **Link no; contextual record yes.** |
| DL22 | Intervention scopes Parcel | M:M join-table link. | Single Parcel FK for narrowly scoped interventions. | Accepted intervention grain can span Parcels. | **No.** |
| DL23 | Intervention scopes identified Plant | Conditional M:M join-table link for current adjacency; hidden phase-scope records for phase truth. | Plant ID arrays in Intervention history. | Current link cannot distinguish prior/current phase or reversal. | **Yes: hidden Intervention Plant Scope representation.** |

### 5.6 Cooperative Pursuit

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL24 | Pursuit has member Party | Required singular FK property on Pursuit. | M:M join. | Requiredness/valid member context must be enforced by creation Action and data validation. | **No.** |
| DL25 | Pursuit has cooperative Party | Required singular FK property on Pursuit. | M:M join. | Same as DL24; Party identity alone grants no authority. | **No.** |
| DL26 | Pursuit is under Programme | Required singular FK property on Pursuit. | M:M join. | One Pursuit has one Programme at accepted grain. | **No.** |
| DL27 | Pursuit concerns Holding | M:M join-table link. | Holding ID array. | Pursuit requires one or more Holdings; submission validation must enforce non-empty set. | **No.** |
| DL28 | Pursuit concerns Parcel | M:M join-table link. | Parcel ID array. | Same non-empty validation; link edits must remain in the same bounded Action. | **No.** |
| DL29 | Pursuit has optional Intervention | M:M join-table link. | Optional FK. | Gate 5 permits zero or more Interventions. | **No.** |
| DL30 | Pursuit is based on mandate Instrument | M:M join-table link. | Singular FK. | Gate 5 permits one or more basis Instruments; Action must enforce non-empty. | **No.** |

### 5.7 Capacity Commitment

| ID | Accepted direct link | Best-fit backing | Alternative | Limitation / enrollment gate | Reopen? |
|---|---|---|---|---|---|
| DL31 | Commitment has capacity owner Party | Required singular FK property on Commitment. | M:M link. | Authority still requires basis/policy context, not Party identity. | **No.** |
| DL32 | Commitment commits capacity to Intervention | Required singular FK property on Commitment. | M:M link. | Action must reject dangling/multiple targets and stale capacity premises. | **No.** |

## 6. Multiplicity and direct-versus-M:M findings

[Fact] Foundry supports FK links for 1:1/M:1 and join-table links for M:M. A declared 1:1 is an indicator and is not enforced. M:M link edits use Create/Delete Link rules; FK links are edited by modifying the FK property.[Official link creation](https://www.palantir.com/docs/foundry/object-link-types/create-link-type)

[Inference] Apply the accepted multiplicities as follows:

- `Plant.currentParcelId`, `Pursuit.memberPartyId`, `Pursuit.cooperativePartyId`, `Pursuit.programmeId`, `Commitment.ownerPartyId`, and `Commitment.interventionId` are single-valued FK properties.
- Required singular endpoints are enforced by the create/modify Action and pipeline/data expectations, not merely by the link cardinality label.
- Pursuit Holdings, Parcels, optional Interventions and basis Instruments are M:M join links.
- Every other direct link remains M:M unless a later authoritative source and write path prove a narrower invariant.
- Do not encode traversable object relations as string arrays merely to avoid join tables.

## 7. Geospatial Parcel, Area and Plant behavior

1. **Parcel and Area:** use `geoshape`; normalize upstream; require valid WGS84 GeoJSON Geometry. Objects are spatially indexed.[Official geospatial documentation](https://www.palantir.com/docs/foundry/geospatial/ontology)
2. **Plant:** use `geopoint` for current stable location and the single Parcel FK for current containment.
3. **Intersection:** precompute candidate Parcel–Area intersections in a backstage pipeline for complete-population work, including partial intersection measures. Use a live Function to combine candidate overlap with Instrument, subject and date rules.
4. **No legal promotion:** neither overlap nor containment writes duty, permission, target or applicability.
5. **No moving-asset machinery:** Geotemporal series are designed for tracks over time and allow only one GTSR property per object type. Parcel/Area/Plant current geometry is not a track. Use source history/backstage snapshots if official boundaries or surveyed locations change.[Official geotemporal type documentation](https://www.palantir.com/docs/foundry/geospatial/types-of-geospatial-and-geotemporal-data#geotemporal-series-reference-gtsr)
6. **No surface selection:** these are storage/query behaviors only.

## 8. Capability matrix — five factual history contracts

### Mechanism finding

[Fact] Structs are OSv2-only, depth-one, primitive-field records. They cannot contain object references, arrays, nested structs, geoshapes, attachments or media references. Arrays of structs have non-nested query semantics: predicates on two fields can match different entries. Actions/Functions can edit struct arrays, but changing an array means writing a complete replacement array.[Official struct documentation](https://www.palantir.com/docs/foundry/object-link-types/structs-overview) [Official array-edit semantics](https://www.palantir.com/docs/foundry/functions/api-objects-links#array-properties)

[Inference] Struct arrays are acceptable only as a denormalized read projection. They are not the authoritative store for the five contracts. Use five hidden OSv2 technical history record types, each source/action-backed with a stable occurrence key, typed M:1 parent and Party links, M:M basis/evidence/scope links where required, and typed variant fields. Expose the parent-local history semantically through links/Functions; do not promote the hidden records into the nine operator object types.

| ID | Accepted history contract | Best-fit current capability | Alternatives | Limitations / enrollment gates | Gate 5 selective reopen? |
|---|---|---|---|---|---|
| H01 | `instrumentHistory` | Hidden `Instrument Occurrence Record` OSv2 type, stable key, parent Instrument FK, actor Party link, basis/scope/evidence links; source-backed for external acts. | Struct array read projection; Action Log; edit history. | Struct cannot carry typed refs and has false cross-entry query semantics. Action/edit logs do not capture external publication/amendment truth. | **Yes — physical history representation only.** |
| H02 | `proceedingHistory` | Hidden `Proceeding Occurrence Record`, stable key and typed parent/actor/basis links; external-outcome ingestion; focused Cash Occurrence extension for transactions. | Struct array; one object per full Proceeding version; time series. | Partials/reversals and order/right allocation require explicit identity and links; time series models measurements, not legal/accounting occurrences. | **Yes — hidden records plus focused cash occurrence.** |
| H03 | `interventionHistory` | Hidden `Intervention Occurrence Record`, stable key and typed parent/actor/basis/evidence links; phase/scope links to Parcel/Plant. | Struct array; Action Log; time series. | Whole-array replacement is unsafe for concurrent append/reversal; Action Log misses executor/public/private external outcomes. | **Yes — hidden records and Plant-phase scope.** |
| H04 | `pursuitHistory` | Hidden `Pursuit Decision Record` created atomically with Decide Pursuit Action; stable parent, actor, authority and evidence links. | Action Log only; struct array. | Action Log can supplement actor/version/parameters but is not the semantic fact contract and does not cover external imported corrections. | **Yes — physical history representation only.** |
| H05 | `commitmentHistory` | Hidden `Commitment Change Record` created atomically with portfolio Action; common `portfolioDecisionReference`; parent/actor/basis links. | Action Log; struct array. | Multi-Commitment transaction must create records consistently; whole-array edits and weak OSv2 read-version checks require explicit stale-premise validation. | **Yes — physical history representation only.** |

### Factual envelope preservation

The hidden record schemas preserve exactly the accepted nine fields: occurrence reference, kind, actor, authority/basis, consequential time, bounded scope, outcome, optional actor-supplied explanation and minimum evidence references. They do **not** store changed decisions, reopening effect, next owner, next Action or next-clock consequence. Those remain Function outputs.

## 9. Cross-cutting dependency matrix

| ID | Accepted dependency | Best-fit current capability | Alternatives | Limitations / enrollment gates | Gate 5 selective reopen? |
|---|---|---|---|---|---|
| X01 | Property / derived / backstage split | Source-backed and edit-only OSv2 properties; read-only Functions; hidden datasets/restricted views/media/history records. | Copy all current answers onto objects. | “Apply user edits” can indefinitely override later source updates; use edit-only only for cooperative-owned facts and source-backed values for external truth.[Edit semantics](https://www.palantir.com/docs/foundry/object-edits/how-edits-applied) | **No semantic reopen; physical contextual/history records reopen.** |
| X02 | OSv2 | OSv2 for all objects and editable links. | None acceptable; OSv1 is obsolete. | Higher than 10,000 edits or 100,000 Search Around requires Support/enrollment change. | **No.** |
| X03 | Structs | Flat structs for bounded scalar value+metadata projections and Action parameters; not authoritative histories or typed Party contexts. | Hidden record objects; flattened scalar properties. | OSv2 only; primitive fields only; depth one; cross-entry array query issue; OSDK support varies. | **Yes for contexts/histories that need typed refs.** |
| X04 | Time series | Use only for genuine repeated measurements/observations such as sensor or remote-sensing values kept backstage. | Hidden occurrence records; dataset snapshots. | Requires time-series sync and time-series object/property configuration; it does not model legal acts, decisions or reversals.[Time-series overview](https://www.palantir.com/docs/foundry/time-series/time-series-overview) | **No. Reject for the five contracts.** |
| X05 | Derived answers | Four read-only Functions over object sets/links/hidden histories; optional derived properties for local convenience. | Pipeline-precomputed projections; function-backed columns. | Derived properties are available but Beta and runtime-costly; Functions must bulk-load and avoid arrays above 10,000. | **No Gate 5 semantic reopen.** |
| X06 | Contextual Party references and authority details | Hidden context record types with typed Party and parent links; direct semantic Party link remains navigation. | Struct array with Party qualified-reference string; one object-backed role type per context. | Structs cannot contain object references; a string reference has no referential integrity or typed traversal. | **Yes — hidden technical context resources, not new operator types.** |
| X07 | Action logs | Enable for each of four manager Actions as supplementary decision/audit objects linked to edited objects. | User edit history; bespoke history records. | One log type per Action; stores edited-object PKs and optional parameters/context, not arbitrary edited-object properties or external outcomes. Requires permissions on log type.[Action Log](https://www.palantir.com/docs/foundry/action-types/action-log) | **No. Supplement only.** |
| X08 | User edit history | Enable on all Action-edited types as supplemental backstage audit. | Action Log; semantic histories; receipts; Workflow Lineage. | Starts only after activation; initialization blocks Actions briefly; disabling permanently deletes history; anyone who can see current PK can see entire history. | **No semantic reopen; audit only, never domain truth.** |
| X09 | Materializations | Optional OSv2 materializations only when downstream pipelines/downloads need merged datasource+edit current state. | OSDK/Object Set reads; bespoke snapshot pipeline. | Automatic propagation has minutes latency; periodic mode may wait up to six hours; only latest snapshot guaranteed; branching creation/edit restrictions; security/provenance caveats.[Materializations](https://www.palantir.com/docs/foundry/object-edits/materializations) | **No. Never use as factual history.** |
| X10 | Four manager-owned Actions | Ontology Action types in actions-only mode with exact parameters/submission criteria; function-backed where multi-object logic is required. | Direct edit APIs; AIP Logic-only mutation; external webhook. | Max 50 types/10,000 objects and 3 MB per OSv2 object edit; submission criteria cannot inspect object-set or attachment parameters. | **No.** |
| X11 | Atomic multi-Commitment portfolio Action | Scenarios compare; one immutable Proposal binds the plan; a TS v2 staged-write Action creates/updates/releases Commitments and records as one commit. | Standard multi-rule Action; pipeline transaction. | Staged writes are available but Beta; prove complete-set, fingerprint, concurrency, ≤10,000-edit and durable-receipt behavior.[Staged writes](https://www.palantir.com/docs/foundry/functions/typescript-v2-staged-writes#atomic-execution) | **No semantic reopen; production behavior test is material.** |
| X12 | Bounded AIP tools and direct execution | Expose only four exact Actions, four exact read Functions, curated reads and clarification. Explicit authenticated manager commands execute directly; background Automate prepares/routes only initially. | Deterministic Action forms or OSDK/API call under same binding. | Full AIP capability is available. Enforce message/Action/target/fingerprint/idempotency binding, one mutation per turn and durable receipts. | **No semantic reopen.** |
| X13 | Four read-only Functions | TS v2 or Python Functions returning typed structs/maps/object sets; separate API names for affected decisions, readiness, portfolios and exposure. | Derived properties; pipeline projections. | Query API name changes break consumers; edits are invisible within regular function execution; object arrays cap at 10,000, so prefer object sets.[Functions overview](https://www.palantir.com/docs/foundry/functions/overview) | **No.** |
| X14 | External outcome ingestion | Data Connection sync for pull sources; public API/HTTPS listener→stream for push; pipeline validates/deduplicates authoritative occurrence keys and writes source-backed current/history datasets indexed by OSv2 Funnel. | Direct Ontology API for trusted custom producers; external transform; manual bounded Action receiving evidence. | HTTPS listeners are GA; WebSocket listeners Experimental; email listeners Beta. Connector/auth/network/egress setup remains source-specific.[Listeners](https://www.palantir.com/docs/foundry/data-connection/listeners-overview) [REST integration](https://www.palantir.com/docs/foundry/available-connectors/rest-apis) | **No semantic reopen; hidden occurrence resources are required.** |
| X15 | Plant-phase history | Hidden `Intervention Plant Scope` fact-bearing relationship records linked to one Intervention occurrence/phase and exact Plants; current DL23 remains adjacency. | Struct-array Plant IDs; separate M:M join per phase. | Added hidden object/link resources and ingestion/Action logic; extension only exists where Plant identities pass gate. | **Yes.** |
| X16 | Cash partial/reversal history | Hidden focused Cash Occurrence objects with authenticated transaction key, direction, amount/value date and links to Proceeding/right/order and reversal/return parent. | Proceeding struct array; time series. | Requires bank/treasury identity and reconciliation evidence; remains external truth and is not user-created “record settlement.” | **Yes.** |
| X17 | Selective reopening and complete-population recomputation | Backstage proposition→decision dependency index; event-driven pipelines/Automate detect changed keys; `Determine Affected Decisions` computes affected/unaffected work; population-scale transforms recompute only affected partitions; no status writes. | Derived property on every object; global rebuild/reset; AIP agent. | Automate is suitable for object-level reactions, not heavy joins; pipelines are suitable for complete populations but have build latency. Dynamic dependency correctness must be tested. | **No new semantic type. Keep dependency index backstage.** |

## 10. Manager Actions and concurrency

### Best-fit mapping

| Gate 5 Action | Foundry mechanism | Required safeguards |
|---|---|---|
| Accept Cooperative Execution Mandate | Standard or function-backed Action on Instrument plus H01 record and contextual authority records. | Exact actor/group plus mandate basis; refuse unresolved grant/scope/term/conflict/fallback. |
| Decide Cooperative Pursuit | Function-backed Action on Pursuit, its M:M scope links and H04 record. | Enforce one member/cooperative/Programme and non-empty Holding/Parcel/basis sets; never edit eligibility/concession/capacity. |
| Commit or Rebalance Intervention Capacity | TS v2 staged-write function-backed Action over complete affected Commitment set and H05 records. | Re-read affected current Commitments; validate protected commitments, feasibility, authority, safeguards and complete edit set; shared portfolio reference. |
| Dispatch Intervention | Function-backed Action creating H03 dispatch record and any real work-order Instrument. | Function invokes the read-only readiness logic but independently enforces submission refusal against current authoritative premises; never write performed/accepted/established truth. |

[Fact] Function-backed Actions can read and modify multiple linked objects and create several types/links, but remain subject to Action and Function limits.[Function-backed Actions](https://www.palantir.com/docs/foundry/action-types/function-actions-overview)

[Fact] OSv2 guarantees reads after a sent edit include that edit, but its Action server checks only objects directly used to generate edits and does not guarantee that all objects merely read remained unchanged.[Edit application semantics](https://www.palantir.com/docs/foundry/object-edits/how-edits-applied#object-storage-v2)

[Inference] Capacity allocation must not depend on a long-lived front-end snapshot. The backing function must identify every premise used to generate edits, validate that the complete affected set is still current, and fail rather than partially rebalance. If Beta staged writes are unavailable, use a deterministic function-backed Action with a bounded affected set, explicit version/fingerprint inputs and a final stale-premise check; do not claim stronger atomic-read semantics than the platform documents.

## 11. Four read-only Functions and performance placement

| Function | Best-fit current capability | Population/performance boundary |
|---|---|---|
| Determine Affected Decisions | Read-only Function over changed occurrence, typed links and backstage dependency index. | Precompute stable proposition→decision dependency edges in pipelines; Function resolves current graph and returns scoped holds/unaffected work. |
| Assess Named-Action Readiness | Read-only Function over exact Action/target/scope/actor/time and typed prerequisites. | Keep final refusal criteria in the Action; never persist generic readiness. |
| Compare Feasible Intervention Portfolios | Read-only Function for bounded affected population, with optimization inputs prepared in pipelines. | Full combinatorial/large-population optimization belongs in pipeline/model compute; Function returns current bounded comparison and explanation. |
| Determine Remaining Exposure | Read-only Function over typed Proceeding/Intervention/Pursuit/Commitment occurrences. | Hidden history records make partial/reversal and per-line aggregation queryable; never persist global completion. |

[Fact] Palantir’s structural guidance recommends pipelines for stable precomputed values, dynamic derivation for values depending on linked/action-edited state, and conscious denormalization only when runtime scale demands it. Derived properties are evaluated at runtime and can add latency above roughly 10,000 objects per query.[Ontology structural guidance](https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance#normalization-and-derived-properties)

## 12. External outcomes and selective reopening contract

### 12.1 Ingestion path

1. Connect source by supported Data Connection sync when Foundry pulls, or by public API/GA HTTPS listener when the source pushes.
2. Land immutable raw payload plus authenticated source metadata backstage.
3. Validate schema, actor/source competence, qualified subject grain, occurrence key, source version, consequential time and evidence reference.
4. Deduplicate/idempotently upsert current source-backed object facts and append hidden occurrence rows by stable source occurrence key.
5. Let OSv2 Funnel index batch or streaming datasource updates into the Ontology.[Ontology backend](https://www.palantir.com/docs/foundry/object-backend/overview#object-data-funnel)
6. Trigger dependency-scoped impact evaluation through pipeline completion or Automate object conditions.
7. Return affected and explicitly unaffected decisions through `Determine Affected Decisions`; do not mutate a generic reopen/status property.

### 12.2 Authority boundary

- Public condition, notice, permit, eligibility, concession, control, liquidation, order, audit, revocation and recovery enter as source-backed external outcomes.
- Bank/treasury transactions enter as authenticated external facts.
- Member/professional/private-acceptor outcomes may enter through an exact Action only when that actor genuinely transacts through CORDON; otherwise use authenticated ingestion or a received-outcome Action that preserves the real actor and basis.
- AIP may extract or stage, but model output never becomes the authoritative outcome without the required human/system source.
- Outbound webhooks can request or synchronize with another system, but a successful webhook is not itself the external authority’s substantive decision.

### 12.3 Selective-reopening algorithm

1. Every accepted decision/Action dependency is represented backstage as `(premise proposition, subject/scope selector, effective interval, dependent decision/Action, materiality rule)`.
2. A new occurrence produces changed proposition keys, affected subject keys and effective time.
3. Stable pipeline logic narrows the candidate dependency set; a Function evaluates current graph context, conflicts and date.
4. The result names affected decisions, dependency paths, indeterminate premises, scoped holds, next real owner and explicitly unaffected work.
5. Only population-scale derived artifacts for those keys are rebuilt. No prior factual occurrence is overwritten; no generic route/task status is reset.
6. Manager Actions re-run their own submission criteria against current truth when eventually submitted.

[Inference] Automate is an orchestration trigger, not the source of impact semantics. Heavy complete-population joins and recalculation belong in batch/streaming pipelines; live bounded explanation belongs in Functions. This follows Palantir’s own right-tool guidance for Actions, pipelines, Automate and Functions.[Ontology anti-pattern guidance](https://www.palantir.com/docs/foundry/ontology/ontology-anti-patterns#solution)

## 13. Capability maturity and implementation constraints

| Item | Status | Required decision/test |
|---|---|---|
| TS v2 staged writes for atomic portfolio editing | **Available; Beta maturity.** | Prove staged-write Action binding, complete-set atomicity, concurrency and durable receipt behavior. |
| AIP Logic, Chatbot Studio and Automate | **Available.** | Prove direct conversational binding and prevention of unintended background manager-Action execution. |
| Derived properties and property reducers | **Available; Beta maturity.** | Treat as optional projection only; never make core correctness depend on them. |
| Search Around above 100,000 and Action edits above 10,000 | **Support/enrollment change required.** | Measure Parcel/Plant/population and rebalance sizes before requesting higher limits or partitioning operations. |
| Struct support in OSDKs | **Varies by SDK; struct-field search under development.** | Test chosen SDK if structs remain in read projections; core typed records avoid dependency. |
| WebSocket listeners | **Experimental.** | Not needed for current external-outcome path. Use GA HTTPS listener/public API/sync. |
| Email listeners | **Beta.** | Use only if an authoritative source can arrive only as authenticated email; otherwise keep out of core ingestion. |
| External map layers / certain map configuration | **Additional configuration may be required.** | Not needed for Ontology correctness and Gate 7 is closed. |
| Individual Plant population | **Domain/data enrollment gate, not a Foundry feature gate.** | Require preserved external identity or validated reproducible inventory before indexing Plants. |
| Source-specific connectors, credentials, network ingress/egress and egress policies | **Environment-specific unknown.** | Inventory each authority/bank/registry source before implementation. |

## 14. Selective reopenings — binding Gate 6 recommendation

### Reopen now

1. **Contextual Party/authority detail → hidden technical context records.** Reason: current structs cannot retain typed Party references and safe repeated interval/scope semantics.
2. **All five factual histories → five hidden technical occurrence-record types.** Reason: stable occurrence identity, typed links, independent query, append/reversal and external ingestion are not safely represented by struct arrays.
3. **Intervention Plant Scope → hidden fact-bearing phase-scope relationship records.** Reason: one Plant must be queryable across phases and a bounded phase must be reversible without replacing a parent array.
4. **Focused Cash Occurrence → hidden occurrence type.** Reason: authenticated transaction identity, partials, returns, reversals and exact allocation are independent, linkable facts.

### Do not reopen

- The nine accepted operator types.
- The two accepted relationship fact owners.
- The 32 semantic adjacencies.
- Separate Person/Organization types absent measured property/Action/security divergence.
- Lot absent a real operator Lot decision.
- Taxon/lineage and Cultivar as operator types.
- Generic Event, Case, Evidence, Status, Task, Queue, WorkItem or timeline types.
- Any Gate 7 surface decision.

### Representation invariant

Hidden technical records do not enlarge the operator-visible core merely because Foundry needs rows and links to guarantee typed reference, query, mutation and audit behavior. Their visibility should be `hidden` or otherwise access-restricted, but the semantic parent remains the accepted Instrument, Proceeding, Intervention, Pursuit or Commitment. The four Functions present the live operator answers; history records do not become a parallel workflow.

## 15. Acceptance checklist

Gate 6 can close on Ontology/data mechanics only when implementation planning can answer **yes** to all of the following without choosing a surface:

- all core types and editable links are OSv2;
- qualified keys and source-vs-edit ownership are explicit per property;
- all 32 links have declared FK or M:M backing consistent with Gate 5 multiplicity;
- required singular endpoints have Action and ingestion validation, not advisory cardinality alone;
- Parcel/Area/Plant geometry is WGS84-normalized and never promoted into legal truth;
- contextual authority uses typed hidden records and direct Party links remain navigation only;
- each of five histories has stable occurrence identity, typed parent/actor/basis/evidence/scope links and append/reversal tests;
- Plant-phase and cash partial/reversal acceptance cases pass;
- Action Logs, durable receipts and user edit history are enabled as distinct backstage audit mechanisms; none replaces domain occurrences;
- materializations are used only for merged-current downstream data, not history;
- all four Functions return independent bounded answers without copied status;
- capacity rebalance either proves staged-write atomicity or uses a tested fallback with stale-premise refusal;
- external outcomes are authenticated, idempotent, source-backed and separated from CORDON Actions;
- selective recomputation proves affected **and unaffected** work on each material change; and
- every load-bearing capability has a version-pinned behavior test and release/rollback contract.

## 16. Final verdict

**Current Foundry can represent the accepted Gate 5 graph, but not safely with only nine visible objects, two relationship objects, 32 links and five parent-local struct arrays.** OSv2 object/link mechanics fit the stable nouns and semantic adjacency. Function-backed Actions fit the four bounded manager mutations; Functions fit live applicability, readiness, portfolio and exposure reasoning; Data Connection, streams, pipelines and Automate fit received-outcome ingestion and selective recomputation.

Gate 5 selectively reopens only the **physical representation** of contextual authority, factual histories, Plant-phase scope and cash occurrences to hidden typed resources. The accepted semantic owners, decision separations, route independence and no-global-status rule remain unchanged. Full staged-write, AIP, Scenario, derived-property, Eval and observability capabilities are available. Correctness depends on the binding production contracts and hard behavior tests, not on capability fallbacks. Gate 7 remains closed.

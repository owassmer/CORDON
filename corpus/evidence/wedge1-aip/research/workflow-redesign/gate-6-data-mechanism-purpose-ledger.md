# Gate 6 — CORDON data, Ontology and compute mechanism-purpose ledger

Status: **GATE 6 RECONCILIATION INPUT — mechanism purposes mapped; production contracts still under review; Gate 7 remains closed**  
Date: 23 August 2026  
Authority: `REDESIGN_SEQUENCE.md`; `gate-5-reconciled-operator-graph.md`; `gate-6-capability-reconciliation.md`; `gate-5-operator-decision-ledger-six-questions.md`; `gate-5-operator-capability-ledger-five-responsibilities.md`  
Research boundary: current official Palantir documentation, retrieved through Palantir MCP and `palantir.com/docs`; Owen confirms full Foundry/AIP capability availability. No Foundry writes. No operator surface selected.

## 1. Verdict and reading rules

CORDON requires a governed path from source change or authenticated operator command to one exact factual output, then to selective recomputation and a bounded next handoff. The platform mechanism is never the semantic owner merely because it transports, computes, indexes, displays or logs the fact.

The binding architecture is:

1. **Acquire source truth** through the least lossy source-appropriate sync, listener or public API.
2. **Preserve immutable evidence** in raw datasets or media sets.
3. **Validate and reconcile** into curated, grain-stable datasets with Data Expectations.
4. **Index decision-ready truth** into an OSv2 Ontology with 11 visible fact owners and a hidden typed operational-fact substrate.
5. **Compute live answers** through incremental pipelines, a deterministic optimizer/model, four exact read Functions and optional non-authoritative derived properties.
6. **Orchestrate, but do not invent authority,** through Automate, Scenarios and bounded AIP tools.
7. **Mutate only through four exact function-backed Actions** under the authenticated principal, writing factual occurrence records and supplemental audit records.
8. **Propagate change selectively** through a dependency index, affected-decision Function, targeted rebuilds and routed handoffs.
9. **Govern software change and health** through Global Branching, code repositories, tagged releases, DevOps packages, lineage, checks, monitoring and Evals.

Foundry datasets are versioned data resources with sync/transaction lineage, Pipeline Builder connects inputs, transforms, expectations and outputs, and the Ontology maps datasource rows and relationships into governed objects, properties, links, Actions and Functions.[1][6][9]

### Six-question key

- **Q1** — What changed, and what does it affect?
- **Q2** — What is now required, allowed or blocked?
- **Q3** — Who chooses, who decides and which route continues?
- **Q4** — Is the route ready for the named Action?
- **Q5** — What was done, and who accepted it?
- **Q6** — Did the intended result land, and what remains open?

Capability IDs use the accepted five-responsibility ledger: `L1–L6` Land, `F1–F6` Funding, `A1–A6` Applications, `W1–W6` Field Work and `P1–P6` Payments. A row naming `*1/*6`, for example, serves the change/feedback capability in all five responsibilities. These IDs do not imply five software modules.

### Visibility and ownership rules

- **Operator-visible** means a current decision-ready projection, not necessarily a particular screen.
- **Backstage** means reachable evidence, computation, technical state or assurance that must not crowd the primary operating state.
- **Semantic owner** is the accepted Gate 5 object or relationship that owns the business meaning even when a hidden technical object stores its rows.
- **Authority boundary** states who or what may make the output true. A pipeline, model, automation or AIP agent never acquires legal, member, professional, public, bank or cooperative decision authority from execution identity.
- **Gate 7 implication** is a capability the eventual surface must be able to consume or reveal; it is not a selection of Map, Workshop, OSDK, Chatbot Studio or any other surface.

## 2. Complete end-to-end data and change paths

### 2.1 Pull-source or database change

```text
source system snapshot / increment / database changelog
→ Data Connection batch, streaming or CDC sync
→ immutable raw dataset or stream-backed dataset
→ schema, source-version and transaction metadata
→ batch/streaming transform: normalize + identify + validate + deduplicate
→ Data Expectations: identity, referential integrity, authority envelope, geometry, row conservation
→ curated current-fact dataset + append-only occurrence dataset + M:M join datasets
→ OSv2 object-data funnel
→ visible object/source-backed property + hidden typed occurrence/context record + links
→ dependency-index delta
→ targeted pipeline completion or Automate trigger
→ Determine Affected Decisions
→ affected and explicitly unaffected decision set
→ bounded readiness/exposure/portfolio recomputation
→ current owner notification or staged proposal
```

CDC is required only where a source exposes stable primary-key, ordering and deletion semantics; it produces a streaming dataset with changelog metadata, not a domain event. Foundry supports CDC across connectors, streams, pipelines and the Ontology.[2]

### 2.2 Push-source or authoritative external outcome

```text
provider webhook / event
→ GA HTTPS listener with provider-specific authentication/signature validation
→ stream event + immutable raw payload
→ stateful streaming or micro-batch pipeline
→ validate source actor, stable occurrence ID, source version, subject grain,
  consequential time, bounded outcome, supersession/reversal and evidence references
→ idempotent accepted occurrence OR quarantine/reconciliation record
→ curated occurrence/current-fact datasets
→ OSv2 indexing
→ selective impact and exposure recomputation
```

HTTPS listeners are inbound-only and write events to streams; streams can feed Automate, streaming pipelines or batch processing.[3][4] A public API is preferred when the producer can be customized. An invalid signature, duplicate replay, late correction, unresolved identity or ambiguous authority never becomes authoritative Ontology truth.

### 2.3 Evidence/media path

```text
source file / image / PDF / audio / field evidence
→ file or media sync
→ immutable media set item + checksum/source metadata
→ extraction/metadata transform where useful
→ curated evidence reference row
→ media-reference property or typed evidence link on the owning occurrence
→ permission-aware retrieval for explanation, review and audit
```

Media stays in a media set; Ontology objects carry media references rather than copied blobs, enabling governed previews and geospatial imagery use.[15] Evidence supports an occurrence or proposition. It does not become a generic operator-visible Evidence object and does not prove acceptance merely because it was uploaded.

### 2.4 Explicit authenticated manager command

```text
explicit unambiguous manager command
→ load current visible graph + hidden authoritative occurrences/context
→ run exact read Function(s)
→ optionally compare alternatives in a Scenario
→ bind exact Action type/version, target set, parameters, authority basis and current-state fingerprint
→ function-side final refusal checks
→ one function-backed Action / staged-write transaction
→ visible cooperative-owned edit-only facts + hidden factual occurrence/change records + exact links
→ one Action-log record + OSv2 edit-history entries
→ selective affected-decision, readiness and exposure recomputation
→ next bounded handoff
```

The four write contracts are only: `Accept Cooperative Execution Mandate`, `Decide Cooperative Pursuit`, `Commit or Rebalance Intervention Capacity`, and `Dispatch Intervention`. Function-backed Actions provide complex linked-object logic; TypeScript v2 staged writes provide a single atomic staged execution where read-after-write and all-or-nothing behavior are required.[21][22]

### 2.5 External write before or after a CORDON Action

```text
exact Action
├─ required external acceptance before Ontology commit
│  → idempotent writeback webhook → external response → accept/refuse Action
└─ best-effort synchronization after Ontology commit
   → side-effect webhook → delivery telemetry/retry queue → explicit sync-failure exposure
```

A writeback webhook runs before Ontology edits and may block them; a side-effect webhook runs after edits and cannot retroactively make the accepted CORDON decision false.[5] Neither webhook can impersonate a member, professional, beneficiary, authority or bank.

### 2.6 Software/configuration change

```text
new clean CORDON project + Global Branch
→ branch-local Data Connection, pipeline, Ontology, Function, Action, Automation and model changes
→ preview/build/unit/property/integration/Expectation/Eval checks
→ branch-aware Data Lineage + Workflow Lineage review
→ proposal + approval policies + rebase/checks
→ merge to main
→ tagged Function/model release and consumer rebind
→ DevOps/Marketplace package version
→ environment-specific configuration + deployment channel
→ post-release Data Health, Workflow Lineage and AIP observability
→ rollback/hotfix through governed release path
```

Global Branching isolates supported workflow changes and merges them only after review; DevOps/package release management is the durable mechanism for versioned promotion, rollback, channels and separate environments.[29][30]

## 3. Mechanism-purpose ledger

### 3.1 Connection, ingress, egress and raw preservation

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M01 | **Data Connection batch sync — REQUIRE** | Periodic acquisition of registries, cadastral/area layers, programme tables, legal instruments and batch authority exports. | Scheduled/manual source extract → versioned raw dataset transaction plus sync metadata. | Q1–Q2; L1–L2, F1, A1–A2, W1, P1. | Backstage. | The external source owns received facts; raw dataset owns bytes/version only. | Sync success proves receipt, not competence, currency or substantive truth. | External transform or manual upload. | Require where no low-latency change feed is needed; it gives repeatable versions and lineage.[1] | Must reveal freshness/source basis when material, never sync mechanics as workflow state. |
| M02 | **Data Connection streaming sync — REQUIRE conditionally** | Low-latency ingestion from Kafka/Kinesis/PubSub-style feeds, sensors or operational middleware. | Source stream event → streaming dataset row with transport metadata. | Q1, Q5–Q6; W1/W5/W6, P1/P5/P6. | Backstage. | Source occurrence owner remains the emitting actor/system. | Arrival is not acceptance, cash or biological establishment. | HTTPS listener, CDC, batch sync. | Require only for genuinely low-latency/high-volume feeds; otherwise batch is simpler. | Surface may show freshness/late-event exposure, not stream partitions. |
| M03 | **CDC sync — REQUIRE conditionally** | Preserve database inserts, updates and deletes without full snapshots for authoritative systems that expose changelogs. | Source PK + ordering + deletion semantics → changelog-enabled streaming dataset. | Q1 and selective feedback; `*1/*6`. | Backstage. | Source row/occurrence owner remains source system. | CDC metadata says how a row changed, not why or under whose domain authority. | Streaming middleware plus Pipeline Builder key-by; periodic incremental sync. | Require where connector/source supports reliable CDC; defer elsewhere. CDC throughput and restart behavior are operational concerns.[2] | Surface needs currentness and correction/reversal consequence only. |
| M04 | **GA HTTPS listener — REQUIRE for non-customizable push producers** | Authenticated inbound public, bank, contractor, inspector or field-system outcomes. | Signed HTTPS request → stream event containing raw payload and channel metadata. | Q1, Q5, Q6; `*1/*5/*6`. | Backstage, with visible reconciliation failure when consequential. | Named external actor/system owns outcome. | Listener authenticates channel; pipeline must still resolve actor competence, subject and scope. | Public API for customizable producer; batch/stream sync. | Require as push baseline; reject WebSocket/email variants initially unless the source truly requires them.[3][4] | Surface must support unresolved-match/signature/freshness exceptions without exposing listener setup. |
| M05 | **Foundry public API inbound — REQUIRE where producer is customizable** | Direct, typed, authenticated publication by a system CORDON can integrate with. | API request under producer identity → dataset/stream/object update per controlled contract plus API response. | Q1, Q5–Q6; all received-outcome capabilities. | Backstage. | Producer owns the fact; CORDON owns validation/reconciliation. | API credentials and schema do not grant domain authority beyond the producer's real role. | HTTPS listener; Data Connection sync. | Prefer over listener when producer can conform to the API; it narrows bespoke ingress logic. | Surface only needs authoritative source, receipt and unresolved consequence. |
| M06 | **Action writeback webhook — REQUIRE conditionally** | Make external acceptance a precondition of the same governed Action where the external system is transactional source of truth. | Exact Action parameters/idempotency key → external accept/refuse payload; only acceptance permits Ontology edits. | Q4–Q5; A5, W5, P5 and exact manager Actions where applicable. | Backstage; refusal visible. | External system owns its accepted transaction; CORDON Action owns only its permitted local effect. | Endpoint credentials must represent the real channel; never use webhook success as public substantive approval. | Synchronous API call in Function; asynchronous side effect. | Require only after transaction, timeout, retry, reversal and idempotency semantics are proven.[5] | Surface must explain blocked/refused external precondition and avoid false completion. |
| M07 | **Post-edit side-effect webhook — REQUIRE conditionally** | Notify or synchronize an external system after a valid CORDON decision without rolling back that decision on delivery failure. | Committed Action → outbound payload + delivery telemetry/retry state. | Q5–Q6; handoffs L6/F6/A6/W6/P6. | Backstage; failed consequential handoff visible. | CORDON fact owner remains changed object/occurrence; recipient owns any later response. | Delivery is not receipt, acceptance or external outcome. | Notification, integration pipeline, writeback webhook. | Use for best-effort sync only; never for a dependency that must block the Action.[5] | Surface must distinguish local success from external synchronization state. |
| M08 | **Streams / stream-backed datasets — REQUIRE conditionally** | Durable transport between listener/streaming sync/CDC and stateful validation. | Ordered event feed → append/changelog stream with schema and partitioning. | Q1 and selective feedback. | Backstage. | No domain semantic ownership; transport substrate only. | At-least-once arrival requires idempotent downstream logic; ordering is not domain causality unless source contract says so. | Batch raw dataset. | Required underneath low-latency ingress; reject as factual history. | No direct surface requirement beyond latency, freshness and processing exceptions. |
| M09 | **Immutable raw datasets — REQUIRE** | Preserve received bytes/rows, source version, retrieval transaction and rejected records for replay and audit. | Any sync/listener/API payload → immutable append/snapshot transaction plus provenance columns. | Supports all Qs as substantiation; especially Q1/Q5. | Backstage, drill-through by permission. | Source owns claims; raw dataset owns preservation record. | Raw arrival is unvalidated and cannot directly drive Actions. | Media set for binary evidence; virtual table. | Require for reproducibility, replay, correction and lineage. Foundry datasets preserve versioned transactions.[1] | Eventual surface must reach basis evidence without presenting raw tables as operator state. |
| M10 | **Media sets + media-reference properties — REQUIRE** | Preserve PDFs, imagery, audio, field photographs and other evidence without copying blobs into objects. | Media/file sync or upload → immutable media item; curated row → typed media reference on owner. | Q2, Q4–Q6; evidence aspects of L2/L4/L5, A2/A4/A5, W2/W4/W5, P2/P4/P5. | Evidence backstage; selected minimum reference operator-visible. | The proposition/occurrence owns evidentiary meaning; media set owns binary asset. | Upload proves existence, not authenticity, professional judgment or acceptance. | Attachment property, generic Evidence object. | Require media sets; reject a generic visible Evidence type. Media references support governed previews.[15] | Surface must permit permission-aware evidence inspection and citation, not an evidence administration lane. |

### 3.2 Datasets, transforms and quality

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M11 | **Curated canonical datasets — REQUIRE** | Produce grain-stable identities, current source facts, typed occurrences, context assignments, link tables, dependency edges and model inputs. | Validated raw rows/media metadata → canonical rows with qualified keys, source/authority envelope, effective time and reconciliation status. | All Qs; all 30 capabilities. | Backstage; projected through Ontology. | Corresponding visible or hidden semantic owner; dataset is physical SoT for source-backed fields. | Curating can standardize and reconcile but cannot promote a model inference to external truth. | Direct Ontology ingest from raw; virtual table. | Required boundary between evidence and operating graph. | Surface consumes Ontology projection and cited basis, not curated tables directly. |
| M12 | **Pipeline Builder batch transforms — REQUIRE** | Normalize, parse, join, geocode, resolve identity, compute candidate applicability, build complete populations and aggregates. | One or more datasets/media sets → deterministic output dataset/object/link target. | Q1–Q2, Q4, Q6; L1–L2, F1–F2/F4, A1–A2/A4, W1–W2/W4, P1–P2/P4. | Backstage. | Output semantic owner depends on product fact; transform owns no authority. | Code/boards may derive candidates and indicators, never public eligibility, law, cash, acceptance or establishment. | Code Repository transforms; Functions. | Require for stable and population-scale work; Pipeline Builder can emit datasets, objects, links and streams.[7] | Surface must receive current projections and provenance, not expose transform topology as workflow. |
| M13 | **Incremental/streaming transforms — REQUIRE** | Recompute only changed partitions, maintain CDC current views, deduplicate listener events and update dependency/model inputs at operational latency. | New raw transaction/changelog/event → delta plus updated curated active view/stream. | Q1 and feedback to Q2–Q6; `*1/*6`. | Backstage. | Same semantic owners as curated outputs. | Incrementality changes compute scope, not decision scope; late/corrected events must re-evaluate effective time. | Full batch rebuild; Automate. | Require selectively for scale/latency; retain rebuild/replay path. | Surface should expose freshness and indeterminate recomputation when consequential. |
| M14 | **Data Expectations / dataset checks — REQUIRE** | Fail builds that violate identity, schema, row conservation, referential integrity, geometry, occurrence-envelope, discrimination or complete-population contracts. | Candidate pipeline output → pass/fail check results; failure blocks publication/build. | Assurance for all Qs; prevents corrupt premises to all 30 capabilities. | Backstage; health summary operator-visible only when work is affected. | Dataset/pipeline maintainer owns check; domain owner still owns fact. | Passing checks proves declared data contracts, not substantive public/legal truth. | Ad hoc scripts; Data Health checks. | Require at output and critical intermediate boundaries. Pipeline expectations can fail the build and run against full output.[8] | Surface must fail closed or show stale/indeterminate state when a load is unhealthy. |

### 3.3 OSv2 objects, properties and hidden operational facts

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M15 | **OSv2 visible object types — REQUIRE** | Index the 11 accepted fact owners: nine operator objects, Cooperative Pursuit and Capacity Commitment. | Curated backing rows + Action edits → typed, secured objects with properties and links. | All Qs/all capabilities. | Operator-visible. | Each accepted Gate 5 type owns its own facts. | Objects represent current decision context; object existence never grants role or authority. | Dataset-only records; separate Person/Organization; Interface. | Require OSv2; retain accepted type boundary. | Any Gate 7 candidate must traverse these same 11 owners and may not invent a parallel case/status model. |
| M16 | **Datasource-backed properties — REQUIRE** | Carry qualified identity, authoritative current geometry/location, external outcomes, timestamps and source-owned current facts. | Curated datasource column → indexed object property. | Q1–Q2, Q5–Q6; all inspect/explain capabilities. | Operator-visible when decision-relevant; otherwise backstage property. | Object owns semantic placement; named source owns truth. | User Action must not overwrite source-owned facts. | Edit-only property; derived property. | Require explicit source ownership per property. | Surface must show source/as-of/basis where omission could mislead. |
| M17 | **Edit-only cooperative-owned properties + Actions-only mode — REQUIRE** | Store only facts created by the four authorized cooperative Actions without changing the backing datasource. | Valid exact Action edit → OSv2 edit-only value/link. | Q3–Q5; F3/F5/F6, W3/W5/W6 and manager-owned portions of Land/Application. | Operator-visible. | Instrument, Pursuit, Commitment or Intervention as accepted. | Only authenticated Action under exact contextual authority may write; no open inline/generic edit plane. | Datasource writeback; generic object API edit. | Require for CORDON-owned decisions; edit-only properties are designed for Ontology values not mapped to datasource columns.[12] | Surface must invoke exact Actions, never offer generic field editing. |
| M18 | **Six hidden occurrence types — REQUIRE** | Preserve stable, queryable and reversible Instrument, Proceeding, Intervention, Pursuit, Commitment and Cash occurrences. | Authenticated external outcome or exact Action → append-only typed occurrence plus explicit correction/supersession/reversal links. | Q1, Q5–Q6; `*1/*5/*6`. | Backstage; projected through parent history/explanation. | Semantic parent remains Instrument, Proceeding, Intervention, Pursuit or Commitment; Cash belongs to Proceeding financial line. | Occurrence records preserve who made the fact true; platform log identity is not substituted. | Struct arrays, Action logs, time series. | Require because typed references, independent query, concurrency and reversal exceed parent arrays. | Surface needs chronological/cited consequences by parent, not navigation to six technical object catalogs. |
| M19 | **Six hidden contextual Party relationship types — REQUIRE** | Preserve membership, Holding assignment, Parcel standing, Instrument/Proceeding/Intervention roles, basis, scope, interval and powers. | Valid source fact or authorized bounded Action → typed relationship object linked to Party, context and basis. | Q2–Q4; all responsibility capabilities dealing with owner/authority. | Backstage; current role/authority projection operator-visible. | The context owner, never global Operator Party. | A direct Party link navigates; only an operative contextual record/basis can support authority. | Party flags; structs with Party IDs; generic role object. | Require focused types; object-backed links are intended where a relationship carries dates, roles or allocation.[11] | Surface must answer who owns the next decision and why, without global-role badges. |
| M20 | **Hidden Intervention Plant Scope — REQUIRE conditionally** | Preserve exact Plant participation by dispatch/performance/inspection/acceptance/establishment/replacement/cure phase. | Plant identity gate + phase occurrence → fact record linking exact Plant(s), Intervention occurrence, scope and result. | Q4–Q6; W2–W6. | Backstage; per-Plant/Intervention phase result visible when relevant. | Intervention owns physical undertaking; phase occurrence owns bounded fact. | Arbitrary detections cannot mint Plants; installation acceptance does not prove establishment. | Current M:M link; arrays of Plant IDs; phase-specific join tables. | Require only when Individual Plant population passes Gate 5 identity gate. | Surface must be able to inspect scoped phase differences without choosing a map or timeline implementation. |
| M21 | **Hidden Cash Occurrence — REQUIRE** | Preserve transaction identity, partial allocation, return, reversal, repayment and recovery. | Authenticated bank/treasury message → immutable Cash Occurrence linked to Proceeding/right/order and reversal parent. | Q1, Q5–Q6; P1–P6. | Backstage; bounded financial line visible. | Proceeding owns financial case; bank/treasury owns transaction fact. | No manual `Record settlement`; order/liquidation never implies cash. | Proceeding struct history; time series; generic payment status. | Require focused occurrence because transaction identity and reversal are independent facts. | Surface must show right/admission/order/cash/audit as separate lines and unmatched cash exceptions. |
| M22 | **Hidden Capacity Portfolio Proposal — REQUIRE** | Bind one selected Scenario/recommendation to complete affected set, proposed edits, versions, protected commitments and current-state fingerprint. | Deterministic comparison + manager-selected alternative → expiring proposal record with exact edit plan, no domain commitment. | Q3–Q4; F2–F5, W2–W3. | Backstage technical decision package; summary operator-visible. | Capacity Commitments own committed truth; proposal owns only prepared package. | AIP/model may prepare; authenticated manager command alone selects and commits through Action. | Generic approval queue; Scenario state only; client snapshot. | Require to prevent stale/partial portfolio application. | Surface must bind the command to one exact proposal/diff without implying a universal approval UI. |

### 3.4 Links, current-state projections and geospatial compute

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M23 | **Six FK-backed links — REQUIRE** | Enforce accepted singular adjacency: Plant→Parcel; Pursuit→member/cooperative/Programme; Commitment→owner/Intervention. | Qualified child row/edit with one parent key → M:1/1:M Ontology traversal. | Q1–Q4; L1–L3, F1–F3, W1–W4. | Operator-visible traversal. | Child object owns FK; relationship semantic remains accepted link. | Requiredness, uniqueness and valid context need pipeline/Action validation; cardinality label alone is insufficient. | M:M join; string ID. | Require exactly six under accepted multiplicity.[10] | Surface can rely on singular traversal but must handle validation failure rather than infer a parent. |
| M24 | **Twenty metadata-free M:M join-table links — REQUIRE** | Represent remaining accepted direct adjacencies without invented singularity or copied arrays. | Curated pair rows or bounded link edits → bidirectional typed traversal. | All Qs; broad cross-responsibility navigation. | Operator-visible traversal; table backstage. | Endpoint semantics per Gate 5; join row owns no independent business fact. | Link existence grants no role, applicability, readiness or authority. | FK; object-backed relation; string array. | Require for accepted M:M graph; do not duplicate object-backed contextual traversals.[10] | Any surface must traverse links and preserve many-to-many ambiguity until evidence narrows it. |
| M25 | **Eight object-backed fact relationships — REQUIRE** | Keep Cooperative Pursuit, Capacity Commitment and six contextual assignments independently mutable/queryable while optionally exposing direct traversal. | Fact-owner row with endpoint FKs and metadata → relationship object plus endpoint traversal. | Q2–Q5; authority, pursuit and capacity capabilities. | Pursuit/Commitment visible; six contextual records backstage. | Intermediary object itself owns relationship fact. | Object-backed projection does not reduce required Action/authority rules. | Plain join table; endpoint properties. | Require where relationship owns interval, role, scope, outcome or allocation.[11] | Surface may show direct endpoint relation or fact detail according to decision need; neither choice is made here. |
| M26 | **OSv2 materialization — DEFER / REQUIRE only for downstream merged-current export** | Produce a dataset snapshot combining datasource and Ontology edits for pipelines/downloads that cannot query objects directly. | Current indexed source values + user/Action edits → materialized merged-current dataset. | Indirect support to Q1–Q6. | Backstage. | Source object remains semantic owner; materialization owns no new fact/history. | Snapshot latency and latest-state semantics forbid using it as occurrence history or instant Action confirmation. | OSDK/Object Set read; bespoke snapshot transform. | Defer until a measured downstream consumer needs it.[13] | Surface should read Ontology directly where possible; must not show materialization lag as current truth. |
| M27 | **Derived properties/reducers — DEFER as convenience** | Expose cheap bounded counts/summaries from links or local current state. | Object/query context → runtime-derived scalar/list value. | Q1–Q2, Q4, Q6; inspect/explain capabilities. | Operator-visible convenience. | Underlying linked facts/Function own semantics. | Never sole correctness mechanism for authority, readiness, full population, histories or completion. | Read Function; pipeline-precomputed property; materialization. | Defer until performance and consumer need are measured; full availability does not make them authoritative.[14] | Surface may consume them as hints but must retain access to exact Function/basis. |
| M28 | **Geospatial normalization/intersection transforms — REQUIRE** | Normalize WGS84 geometry, validate shapes, compute Parcel–Area/Plant containment candidates and partial-overlap measures at population scale. | Raw source geometry + qualified identities → valid normalized geometry and candidate intersection dataset with measures. | Q1–Q2, Q4; L1–L4, F1–F2, A1–A2, W1–W2. | Backstage; spatial premise visible when consequential. | Parcel/Area/Plant own geometry; candidate row owns only measured overlap premise. | Geometry never creates legal applicability, competence, duty, tenure, permission or target. | Live spatial Function; Map selection. | Require upstream normalization and candidate compute; Pipeline Builder geometry must be normalized before Ontology indexing.[16] | Surface must be able to inspect spatial basis and uncertainty without implying map selection. |
| M29 | **Ontology `geoshape`/`geopoint` properties and spatial index — REQUIRE** | Store current Parcel/Area geometry and stable Plant location for typed spatial query/traversal. | Normalized curated geometry → indexed `geoshape` or `geopoint` property. | Q1–Q2, Q4–Q5; Land/Field capabilities. | Operator-visible decision context. | Parcel, Official Area, Individual Plant. | Current geometry is source-owned; spatial relation is candidate premise only. | External tile layer; GTSR; dataset-only geometry. | Require for accepted spatial nouns.[17] | Any surface architecture must support spatial context somehow; this ledger selects no renderer. |
| M30 | **Map capabilities — RETAIN as Gate 7 candidate capability, not selected surface** | Demonstrate that Ontology point/polygon layers, spatial selection/search, link analysis and geospatial Actions are available. | Ontology geospatial objects + optional shape input → visualization/selection/object set or invocation of an already-governed Action.[18][19] | Potentially all Qs, especially L1–L4 and W1–W5. | Operator-visible if Gate 7 selects a map-bearing surface. | Underlying objects/Functions/Actions own semantics; Map owns no truth. | A shape selection cannot establish law, authority, readiness or Action permission. | Workshop map widget, OSDK map, Object Explorer, non-map surface. | Retain capability; defer surface choice. Reject any design that makes drawing/selecting a shape itself authoritative. | Gate 7 must compare spatial reasoning/selection affordances, but this row chooses none. |

### 3.5 Functions, Actions, optimizers, models, Scenarios and Automate

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M31 | **Four read-only query Functions — REQUIRE** | Return exact affected decisions, named-action readiness, feasible portfolios and remaining exposure from current graph and backstage inputs. | Typed target/scope/actor/time/change inputs → typed bounded result with basis, indeterminacy, unaffected work/alternatives/remaining lines. | Q1–Q6; all 30 capabilities. | Operator-visible result; implementation backstage. | Accepted graph facts remain owners; Function owns versioned derivation contract. | Query Functions cannot create authority or edit truth.[20] Action repeats refusal checks. | Derived properties; AIP Logic prompt; pipeline snapshot. | Require exact, API-named, tested Functions; never one generic CORDON logic tool. | Every candidate surface must call and render typed results/basis, not reimplement logic. |
| M32 | **Four function-backed Actions + TSv2 staged writes — REQUIRE** | Execute only the four accepted manager-owned transactions with complete-set, stale-premise, authority and atomicity checks. | Explicit authenticated command + exact proposal/targets → one atomic edit batch, domain occurrence records and links, or a user-facing refusal. | Q3–Q5 with feedback Q1/Q6; F3/F5/F6, W3/W5/W6 and bounded manager portions elsewhere. | Operator-visible effect/refusal; code backstage. | Instrument, Pursuit, Commitment and Intervention. | Caller permission + contextual authority + criteria + function revalidation; never reserved external truth. | Standard Actions; direct edits; multiple Automate effects. | Require function backing for coupled histories/links; staged writes mandatory for portfolio rebalance.[21][22] | Surface must invoke exact Actions under caller identity and present non-implications; no generic edit surface. |
| M33 | **Versioned deterministic optimizer — REQUIRE** | Compute feasible capacity portfolios under non-discretionary constraints, fairness safeguards and expected realized Xylella-loss reduction. | Complete affected population + capacity/policy/model inputs → ranked feasible portfolio, equivalent alternatives, binding constraints, sensitivity and infeasible reasons. | Q2–Q4/Q6; F1–F4/F6, W1–W3/W6. | Recommendation/operator-visible; traces backstage. | Compare Function owns recommendation contract; manager owns commitment decision. | Optimizer never creates Commitments or overrides policy; infeasible/incomplete input must fail closed. | Rules in Function; model asset; AIP/LLM scoring. | Require deterministic, replayable compute; package as code/model according to performance, not UI convenience. | Surface must support alternatives/consequences and explicit manager selection, not expose solver internals by default. |
| M34 | **Model assets, training/evaluation and tuned Action-execution model — REQUIRE as assurance program; predictive domain model only when validated** | Version objective inputs/uncertainty models and train/evaluate a high-accuracy natural-language tool-selection model against exact Action/refusal trajectories. | Curated training/evaluation data + code → versioned model artifact, metrics, lineage and deployed callable version. | All Qs through intent resolution/explanation; never semantic authority. | Model behavior operator-visible; training backstage. | Deterministic Functions/Actions own contracts; model asset owns prediction only. | Model may select/explain exact tools under caller permissions; it may not score authoritative portfolio, invent facts or bypass refusal. | Palantir-hosted model baseline; prompt-only AIP Logic; deterministic parser. | Require measured baseline comparison and promotion gates; open-source/tuned is means, not goal. Foundry model assets provide versioning, lineage, history, security and branching.[23][24] | Gate 7 must evaluate direct intent handling and clarification, not choose a model based on surface aesthetics. |
| M35 | **Ontology Scenarios — REQUIRE for what-if comparison, never authority** | Isolate hypothetical Action effects and compare portfolio/readiness/exposure consequences before a main write. | Current main state + hypothetical exact Actions → isolated scenario state/diff; optional separately governed merge. | Q2–Q4/Q6; F2–F4, W2–W4. | Operator-visible comparison; scenario storage backstage. | Main objects remain truth owners; scenario owns hypothetical state only. | Scenario result/merge is not manager approval or external truth; production criteria remain separate. | Hidden proposal only; client-side simulation; pipeline what-if. | Require for materially useful alternatives; do not depend on unsupported transaction shapes.[25] | Surface architecture must be able to compare scenarios if selected, but no specific scenario UI is prescribed. |
| M36 | **Automate — REQUIRE for detection/orchestration; REJECT autonomous manager decisions initially** | React to time/object/stream conditions, run read Functions, trigger targeted builds, notify owners, stage proposals and execute fallbacks. | Schedule/object condition/stream event → Function invocation, pipeline trigger, notification, proposal or fallback record. | Q1, Q4, Q6 and all handoffs. | Mostly backstage; alerts/proposals operator-visible. | Underlying facts/Functions/Actions own semantics. | Automation owner identity is not fresh domain approval; at-least-once effects demand idempotency; never decompose atomic capacity Action. | Pipeline schedules; listener processing; AIP Logic. | Require bounded orchestration; reject direct automatic submission of four manager Actions absent later explicit autonomy policy.[26] | Surface must receive routed, permission-aware work and distinguish proposal from decision. |

### 3.6 Audit, security, development, release, lineage and health

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M37 | **One Action log per manager Action — REQUIRE supplemental audit** | Record Action type/version, submitter, time, parameters/context and edited object keys. | Successful Action submission → `[LOG]` object linked to edited objects. | Q5 and audit support to Q1/Q6. | Backstage; accessible audit drill-through. | Action invocation owns log; domain occurrence owns business consequence. | Log proves platform invocation, not member grant, public result, performance, cash or establishment. | Domain occurrence; edit history; audit logs. | Require all four logs with Function edit provenance; never substitute for histories.[27] | Surface may expose “how this change was executed” separately from “what happened.” |
| M38 | **OSv2 user edit history — REQUIRE supplemental audit** | Add object-level before/after audit across all Action-edited types. | Feature activation + later Action/API edit → edit-history entry. | Q5/troubleshooting only. | Backstage, permission-bound. | Object edit owns technical delta; domain occurrence owns factual event. | Does not capture datasource changes, starts only after activation and visibility follows object access. | Action log; occurrences; durable receipts; Workflow Lineage. | Required by Owen for extra audit. Define activation, access and retention; never use as domain truth or operator timeline.[28] | No primary surface dependency; audit/support access only. |
| M39 | **Restricted Views, markings, object/property security and edit policies — REQUIRE** | Keep raw evidence, sensitive member data, authority records, prompts and model traces visible only to permitted principals while preserving decision use. | Classification/marking and caller identity → filtered rows/properties/media and permitted Action/read scope. | All Qs/capabilities. | Security is backstage; denied/insufficient-basis result operator-visible. | Data/domain owner sets classification; platform enforces access. | Security controls access, not domain authority; seeing an object never grants power to act. | Project permissions only; application filtering. | Require defense in depth at data/Ontology/tool level; never rely on UI hiding. | Gate 7 candidate must preserve caller identity and cannot broaden access through aggregation or chatbot context. |
| M40 | **New clean project + Global Branch + proposal — REQUIRE** | Isolate accepted CORDON resources from historical rejected-model resources; develop/test/review cross-application changes before main. | Approved change set → branch-local resources/builds/checks → reviewed proposal → merged main resources. | Assurance for all Qs/capabilities. | Builder/governance visible; backstage to operators. | Resource owners own definitions; branch owns proposed version only. | Branch Action tests cannot write main; merge permission/approval does not confer runtime domain authority. | Edit historical project; direct main changes. | Require clean project/branch; preserve old project read-only.[29] | Gate 7 artifacts must join the same branch/review graph but are not selected now. |
| M41 | **Code repositories, CI, tests, tagged Function/model releases — REQUIRE** | Version transforms, Functions, Action backing code, optimizers/models and contracts; publish only tested tagged versions. | Commit + dependency/resource declaration + build → tested artifact; tag → published Function/model version; rebind → consumer uses version. | Assurance for all Qs/capabilities. | Backstage; release identity visible in audit. | Repository/package owner owns software; Ontology owner owns semantic API contract. | Green compile is not publication; code cannot expand Action authority. | Pipeline Builder-only logic; unversioned notebook; AIP prompt. | Require for complex deterministic logic and model assets. | Surface must tolerate versioned API contracts and expose version only when material to explanation/audit. |
| M42 | **Foundry DevOps + Marketplace/package/release channels — REQUIRE before multi-environment promotion; DEFER for first single-environment branch iteration** | Package coherent resources, configure environment-specific integrations/security, promote through channels and support rollback. | Validated branch/main resources → package version → configured environment deployment/release channel. | Assurance/continuity for all capabilities. | Builder/release backstage. | Package owns deployable software composition, not domain facts. | Environment config must not silently weaken security, source authority or Action criteria. | Global Branching alone; manual recreation. | Require for durable test→production lifecycle; branch is for rapid within-environment iteration, not full release management.[30] | Gate 7 surface resource eventually ships in same package, but no surface is chosen here. |
| M43 | **Data Lineage — REQUIRE** | Trace raw sources, datasets, transforms, checks, model inputs, object/link outputs and materializations across versions/branches. | Resource dependency graph + build metadata → upstream/downstream provenance, version and health context. | Explains basis for Q1–Q2/Q5–Q6; assurance all capabilities. | Backstage; cited lineage drill-through for stewards/auditors. | Each resource owns its processing edge; lineage owns no domain truth. | A lineage edge proves data dependency, not legal authority or correctness. | Workflow Lineage; hand-built diagram. | Require complete source→Ontology trace.[31] | Surface may link to provenance but should not substitute a pipeline graph for an operator explanation. |
| M44 | **Workflow Lineage + AIP observability — REQUIRE** | Trace object/Action/Function/model/Automation dependencies and inspect metrics, executions, distributed traces, tool calls, logs and failures. | Runtime invocation/resource graph → execution history, metrics, trace/log records and dependency view. | Assurance for Q1/Q4–Q6 and all action/explanation capabilities. | Backstage operations/audit. | Runtime operation owns telemetry; domain occurrence owns consequence. | Telemetry retention/success cannot be durable truth or approval. | Data Lineage; Action logs; service monitoring. | Require for production debugging and model/tool governance.[32][34] | Surface may show degraded/failed operation but must not expose sensitive prompts/logs to unauthorized operators. |
| M45 | **Data Health, monitoring views and health checks — REQUIRE** | Monitor freshness, build success, schema/content quality, stream lag, object indexing and resource-level reliability; alert before stale/corrupt data drives work. | Dataset/resource state + configured rules/checks → health status, firing monitor and notification. | Protects all Qs/capabilities, especially Q1/Q4. | Backstage; consequential stale/indeterminate warning operator-visible. | Resource maintainer owns health rule; domain owner owns business fact. | Healthy means declared technical contract holds, not that source assertion is legally true. | Pipeline Expectations; Workflow observability. | Require both fine-grained checks and scalable monitoring views.[33] | Surface must fail closed or mark answers stale/indeterminate when load-bearing health is red. |
| M46 | **AIP Evals + deterministic unit/property/integration tests — REQUIRE** | Prove exact tool/target/parameter selection, clarification, abstention, authority refusal, no prohibited implication, deterministic optimizer behavior and complete Action edits. | Versioned cases/trajectories + candidate model/code → scored results, failure cases, comparison and promotion decision. | Assurance across Q1–Q6. | Backstage; release verdict visible to governors. | Test owner owns acceptance contract; no production fact is created. | Quality averages cannot offset an unauthorized Action or reserved-decision fabrication. | Manual review; production logs only. | Require before model/tool promotion and after material changes.[35] | Gate 7 interaction prototypes must be evaluated against the same trajectories; visual preference cannot waive safety. |

### 3.7 Explicitly deferred or rejected alternatives

| ID | Mechanism and disposition | Purpose in CORDON | Triggering input → exact output | Q / capabilities served | Visibility | Semantic owner | Authority boundary | Overlap / alternative | Why require, defer or reject | Gate 7 implication without choosing a surface |
|---|---|---|---|---|---|---|---|---|---|---|
| M47 | **Time series / geotemporal series — DEFER for measurements; REJECT for factual histories** | Optional repeated sensor/remote-sensing measurements or moving tracks backstage. | Timestamped measurement/location → time-series/GTS record. | Supporting Q1/Q5/Q6 in Field Work. | Backstage. | Measurement source owns observation. | A measurement series cannot model legal acts, decisions, acceptance, reversal or cash allocation. | Hidden occurrence types; dataset snapshots. | Defer until genuine measurement workflow exists; reject for five histories and current static Parcel/Area/Plant geometry. | No Gate 7 dependency; if later admitted, surface may plot observations without turning them into outcomes. |
| M48 | **Virtual tables — DEFER / REJECT as core authoritative operating source** | Query external data without full ingest for exploratory or very large sources. | Query to external system → live virtual result. | Possible Q1/Q2 support. | Backstage. | External system owns data. | Availability, reproducibility and point-in-time replay may be weaker than landed data; cannot bypass occurrence validation. | Batch/CDC sync; raw dataset. | Defer for discovery/read-heavy adjuncts; core decision premises require landed, versioned, replayable data. | Surface must not depend on an unversioned live query for irreversible Action refusal/approval. |
| M49 | **Struct/array properties — DEFER for bounded scalar projection; REJECT for authority/history** | Compact display/parameter of small primitive value bundles. | Bounded scalar values → one struct or replacement array. | Convenience Q2/Q4/Q6. | Projection may be visible. | Underlying hidden records own semantics. | No typed object/media references; whole-array replacement and cross-entry queries are unsafe for authoritative repeated facts. | Hidden typed object records. | Reject for contextual Party facts, occurrences, Plant scope and cash; optional denormalized read projection only. | Surface may consume a projection but must resolve exact source records for action/evidence. |
| M50 | **Ontology Interface — REJECT initially** | Polymorphic common shape across divergent object types. | Several implementing types → shared interface query/Action contract. | No accepted capability uniquely served. | N/A. | Existing 11 types retain semantics. | Interface would not solve polymorphic contextual-owner authority and could hide important divergence. | Direct typed Functions/links; separate Person/Organization only if measured. | Reject absent a proven consumer, security or Action need. | Gate 7 may reopen only if a selected architecture demonstrates real cross-type behavior impossible cleanly otherwise. |
| M51 | **Generic Event/Case/Evidence/Status/Task/Queue/WorkItem types and generic edit tools — REJECT** | Apparent simplification through one universal workflow vocabulary. | Arbitrary update/upload → generic record/status. | Superficially all Qs; actually collapses them. | Would be operator-visible and misleading. | No legitimate semantic owner; it steals meaning from Instrument, Proceeding, Intervention, Pursuit, Commitment and occurrences. | Enables unauthorized `mark paid/accepted/compliant/complete` and false global readiness/completion. | Typed occurrences, exact Functions/Actions, routed projections. | Reject categorically. | Gate 7 must compose question-specific projections from accepted owners; it may not introduce a parallel case-management ontology. |

## 4. Binding ownership and authority matrix

| Output class | Exact output | Semantic owner | Who/what may make it true | Forbidden promotion |
|---|---|---|---|---|
| Source receipt | Raw dataset transaction, stream event or media item | Raw/data resource only | Connector/listener/API transport | Receipt → substantive outcome |
| Curated external fact | Source-backed current row or typed external occurrence | Corresponding object/parent occurrence context | Authenticated competent source after validation | Transform/model → official/public/bank truth |
| Spatial premise | Normalized geometry and candidate intersection | Parcel/Area/Plant plus candidate dataset | Named geometry source; pipeline computes overlap | Overlap → law, authority, duty or permission |
| Cooperative decision | Edit-only value/link plus factual occurrence | Instrument, Pursuit, Commitment or Intervention | Authenticated cooperative role through one exact Action | Recommendation/proposal/automation identity → commitment |
| Read answer | Typed Function result | Function derivation contract over current graph | Deterministic code on current permitted facts | Readiness/affected/exposure result → stored global status |
| Portfolio recommendation | Feasible portfolio, alternatives, constraints, sensitivity | Compare Function/model version | Deterministic optimizer under approved policy | Highest score → committed capacity |
| Scenario | Isolated hypothetical object/edit state | Scenario resource only | Scenario execution | Hypothesis/merge mechanics → manager approval |
| External transaction response | Writeback response or later inbound occurrence | External system / received occurrence | Authenticated external system | HTTP 2xx alone → public/financial meaning |
| Domain history | Typed occurrence/change record | Semantic parent | Real actor/source or exact authorized Action | Action log/edit history → domain occurrence |
| Technical audit | Action log, edit history, trace, lineage, health/Eval result | Platform assurance resource | Platform runtime/build system | Technical success → legal/operational completion |

## 5. End-to-end invariants and acceptance implications

1. **Every authoritative external outcome** has source system, stable occurrence ID, source version, actor/authority reference, subject grain, consequential and received time, bounded outcome, evidence references, supersession/reversal pointer, idempotency key and reconciliation result.
2. **Every manager mutation** uses one of four exact Actions; direct edits, generic edit tools and automation-owned domain decisions are absent.
3. **Every factual history line** is a typed occurrence, not a struct array, Action log, edit history, trace or materialization.
4. **Every source-backed property** names source and freshness; every edit-only property is demonstrably cooperative-owned.
5. **Every accepted direct link** has exactly one physical owner: seven FKs, nineteen metadata-free M:M joins, or one of eight object-backed fact relationships. Duplicate traversals are prohibited.
6. **Every spatial conclusion** separates measured overlap from proposition/date/subject/Instrument authority reasoning.
7. **Every selective recomputation case** proves affected and explicitly unaffected work; no global reset/status property is written.
8. **Every capacity decision** binds complete population, policy/model version, alternatives, protected Commitments and a current-state fingerprint to one atomic staged-write Action.
9. **Every Action retry and external event replay** is idempotent or refuses an existing stable reference.
10. **Every load-bearing pipeline output** has expectations for identity, schema, referential integrity, authority envelope, temporal validity, geometry and population conservation as applicable.
11. **Every operator answer** fails closed to stale/indeterminate when Data Health or source validity invalidates a premise.
12. **Every model promotion** passes deterministic tests and AIP Evals with zero unauthorized Action, target, parameter or reserved-decision fabrication.
13. **Every software change** travels through the clean project/Global Branch, checks, proposal, merge and tagged/package release path appropriate to its environment.
14. **Every audit explanation** keeps domain occurrence, Action invocation, object edit, data lineage and workflow telemetry distinguishable.
15. **Every Gate 7 candidate** consumes the same typed objects, links, Functions and Actions; no candidate earns selection by inventing a new status/case/work-item layer.

## 6. Future Gate 7 handoff — capability requirements only

When Gate 6 closes, Gate 7 may compare platform-native operator-surface architectures. It must treat the following as fixed inputs rather than redesign opportunities:

- 11 visible semantic fact owners and the hidden typed substrate;
- seven FK, nineteen M:M and eight object-backed fact relationships;
- four exact read Functions and four exact function-backed Actions;
- direct authenticated conversational execution when the manager command is explicit and authorized, clarification when ambiguous, and routing when another actor owns the decision;
- scenario comparison for materially useful alternatives;
- spatial object context and shape/object-set capability without assuming Map is the selected surface;
- permission-aware cited media/evidence access;
- separate current decision state, domain history, platform audit and system health;
- selective affected/unaffected recomputation and bounded next-owner handoff;
- no global case status, generic readiness/completion, generic edit, or generic external-outcome tool.

The Gate 7 comparison question is therefore not “which application can hold the data?” Every candidate can be tested against the same mechanism contract. The comparison must ask which architecture most intuitively lets the cooperative manager answer Q1–Q6, inspect basis and consequences, compare alternatives, issue the four exact commands and see the bounded result—without exposing backstage mechanics or fabricating authority.

## Sources

[1] https://www.palantir.com/docs/foundry/data-integration/connecting-to-data
[2] https://www.palantir.com/docs/foundry/data-integration/change-data-capture
[3] https://www.palantir.com/docs/foundry/data-connection/listeners-overview
[4] https://www.palantir.com/docs/foundry/data-connection/listeners-https
[5] https://www.palantir.com/docs/foundry/action-types/webhooks
[6] https://www.palantir.com/docs/foundry/pipeline-builder/core-concepts
[7] https://www.palantir.com/docs/foundry/pipeline-builder/transforms-overview
[8] https://www.palantir.com/docs/foundry/maintaining-pipelines/define-data-expectations
[9] https://www.palantir.com/docs/foundry/ontology/core-concepts
[10] https://www.palantir.com/docs/foundry/object-link-types/create-link-type
[11] https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance
[12] https://www.palantir.com/docs/foundry/object-link-types/edit-only-properties
[13] https://www.palantir.com/docs/foundry/object-edits/materializations
[14] https://www.palantir.com/docs/foundry/ontology/derived-properties
[15] https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-in-ontology
[16] https://www.palantir.com/docs/foundry/pipeline-builder/transforms-geospatial
[17] https://www.palantir.com/docs/foundry/geospatial/ontology
[18] https://www.palantir.com/docs/foundry/map/overview
[19] https://www.palantir.com/docs/foundry/map/integrate-actions
[20] https://www.palantir.com/docs/foundry/functions/overview
[21] https://www.palantir.com/docs/foundry/action-types/function-actions-overview
[22] https://www.palantir.com/docs/foundry/functions/typescript-v2-staged-writes
[23] https://www.palantir.com/docs/foundry/ontology/models
[24] https://www.palantir.com/docs/foundry/model-integration/model-asset-code-repositories
[25] https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario
[26] https://www.palantir.com/docs/foundry/automate/overview
[27] https://www.palantir.com/docs/foundry/action-types/action-log
[28] https://www.palantir.com/docs/foundry/object-edits/user-edit-history
[29] https://www.palantir.com/docs/foundry/global-branching/overview
[30] https://www.palantir.com/docs/foundry/devops-release-management/overview
[31] https://www.palantir.com/docs/foundry/data-lineage/overview
[32] https://www.palantir.com/docs/foundry/workflow-lineage/overview
[33] https://www.palantir.com/docs/foundry/observability/data-health
[34] https://www.palantir.com/docs/foundry/aip-observability/overview
[35] https://www.palantir.com/docs/foundry/aip-evals/overview

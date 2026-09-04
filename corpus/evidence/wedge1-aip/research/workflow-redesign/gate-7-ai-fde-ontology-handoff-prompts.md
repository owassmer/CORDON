# Gate 7 AI FDE ontology handoff prompts

Status: implementation handoff ready; Gate 7 accepted; ontology prompts do not build the selected surface
Authority: `REDESIGN_SEQUENCE.md` and the accepted Gate 5–6 artifacts named below  
Use: paste Prompt 00 once, then paste Prompts 01–14 sequentially into AI FDE. Do not skip a dependency or combine prompts.

## How to use this set

- AI FDE is the platform builder only. It is not a CORDON runtime identity, domain authority, reviewer, or product agent.
- AI FDE begins with minimal context and branches by default. Each prompt therefore names one operating mode, exact context attachments, and a minimal tool subset. Do not enable an all-tools session.
- The allowed mode vocabulary is `Exploration`, `Data connection`, `Data integration/Pipeline Builder`, `Ontology editing`, `Functions editing/TSv2`, `Functions editing/Logic`, `Governance`, `Machine learning`, and `OSDK React`. This sequence intentionally contains no `OSDK React` build prompt because selecting or building that surface belongs to Gate 7.
- Prompt 01 is read-only. Prompt 02 is plan-only. Owen may use Prompts 00–02 while Gate 7 remains open. Prompts 03–14 are globally blocked until the governing sequence states Gate 7 is accepted for build and Owen sends exact token `GATE 7 ACCEPTED FOR BUILD`. Each Prompt 03–14 then uses a second two-message gate: first produce its bounded plan and stop; implement only after Owen sends that prompt's exact approval token.
- Every prompt must confirm the active project and Global Branch before any operation. Any unexpected `main`, default-branch, historical-project, cross-project, or unbranched write is a hard stop.
- The historical `CORDON-Wedge-1` project is evidence only. Never edit, delete, archive, rename, move, rebind, or “repair” it.
- The future build occurs in one **new clean project** and one **new Global Branch** approved under Prompt 02. Prompts 00–02 perform no writes. Prompts 03–14 perform no planning or writes until `GATE 7 ACCEPTED FOR BUILD`. Do not choose or build the Gate 7 operator surface. AIP Chatbot/Logic resources may be built as channel-neutral runtime contracts only.
- Gate 7 selects the Workshop-native Decision Loop defined in `gate-7-operator-surface-architecture-comparison.md`. Attach that file as **S0** to Prompt 00 and any later prompt that touches Chatbot application state, release compatibility or demo behavior. This handoff builds the Ontology/runtime substrate only; a separate reviewed surface prompt set will build Workshop, Map lens, Object Views and the conditional custom comparator.
- Fixtures, synthetic records and temporary source stubs never replace real records, define scope or count as coverage. Structural zero-row PK-only backings are allowed only for genuinely Action-created types and contain no invented facts. Tests use verified real records, object-set-generated Eval cases and Ontology simulations; invalid cases alter simulated inputs only.
- Preserve reviewer separation: AI FDE authors; Owen approves; Connor-style semantic review remains independent and read-only; Ferro-style implementation/release review remains independent from authorship. AI FDE must not self-approve, merge on its own review, impersonate either reviewer, or collapse both review lanes into one verdict.
- Maintain a branch-local `CORDON Build RID Ledger` from Prompt 03 onward. Record the full, untruncated RID, API name, display name, resource kind, project RID, branch RID, parent/container RID, backing datasource RID(s), version/tag, creation prompt, status, and URL for every resource. Never substitute names for RIDs.
- “STOP” means perform no further tool call or write. End every response exactly with these headings: `State`, `Next`, `Escalations`.

## Governing attachment bundle

All governing artifacts live on the platform in the CORDON reference repository. AI FDE cannot take markdown attachments directly, so "attach" in every prompt means: make the named bundle available from this repository — by dragging its Compass link into the AI FDE chat, enabling search tools, or having AI FDE read the files from the repository — and read `INDEX.md` first for the per-prompt retrieval table.

- Repository: `cordon-reference-library` in project `CORDON`
- Repository RID: `ri.stemma.main.repository.90859416-fa2a-43bf-b783-0664ca785b74`
- Project RID: `ri.compass.main.folder.1767cec7-910c-476a-b472-4ec91bd9e6c3`
- Branch: `master` (default). Authorities live under `authorities/`; the Owen-approved semantic pack lives under `semantic-pack/`.
- The repository is a Python Transforms code repository used as a document store. Ignore the template scaffolding (`build.gradle`, `gradle*`, `ci.yml`, `templateConfig.json`, `transforms-python/`); only `INDEX.md`, `authorities/` and `semantic-pack/` are governing content. Never edit this repository from a build prompt.

Attach these six files whenever a prompt says **attach G0**:

1. `REDESIGN_SEQUENCE.md`
2. `research/workflow-redesign/gate-5-reconciled-operator-graph.md`
3. `research/workflow-redesign/gate-6-capability-reconciliation.md`
4. `research/workflow-redesign/gate-6-data-mechanism-purpose-ledger.md`
5. `research/workflow-redesign/gate-6-aip-mechanism-purpose-ledger.md`
6. `research/workflow-redesign/gate-5-minimum-operator-properties.md`

Reading precedence is: `REDESIGN_SEQUENCE.md` → reconciled Gate 5 graph → Gate 6 capability reconciliation → the two Gate 6 mechanism-purpose ledgers. The minimum-properties file is subordinate where reconciliation changed its history representation or type count.

Whenever a prompt says **attach D0**, also attach:

7. `research/workflow-redesign/gate-7-real-data-to-ontology-mapping-ledger.md`

`D0` is the binding current source/gap map, not permission to load every listed source. Its 77 records include nine derivative local artifacts that provide no independent coverage. Source-specific admission, acquisition and assurance gates remain controlling.

---

## Prompt 00 — bootstrap/system brief

**Dependency:** none.  
**AI FDE mode:** Exploration.  
**Attach:** G0; S0.
**Enable only:** documentation search/read, project/resource read, Ontology read, Workflow Lineage read, Data Lineage read. No mutation tools.

```text
You are the bounded AI FDE builder for the accepted CORDON Wedge 1 Foundry/AIP architecture. Read every attached governing artifact before responding. Treat the accepted Gate 5 semantics, Gate 6 mechanism contracts and Gate 7 Workshop-native surface architecture as fixed. Do not prototype or build the surface in this ontology/runtime handoff.

Before acknowledging the rules, report the currently active project name + full project RID and active branch name + full branch RID, or explicitly report that no project/branch context is attached. Perform no context-changing action.

Operating rules:
1. Start with minimal context and use only the tools enabled for the current bounded prompt. Never ask for or enable a giant all-tools context.
2. Before every operation, report the active project name + full project RID and active branch name + full branch RID. AI FDE branches by default, but do not assume the branch is correct. STOP on main, default, unbranched, cross-project, or unexpected project state.
3. The historical CORDON-Wedge-1 project is read-only evidence forever unless Owen separately authorizes a different task. Never mutate it.
4. All future writes must be confined to the one new clean project and one new Global Branch approved under Prompt 02. Do not create either during this bootstrap.
5. The governing sequence now records Gate 7 accepted. Prompts 03–14 remain blocked until Owen sends exact token `GATE 7 ACCEPTED FOR BUILD`; before that token, do not plan or execute Prompt 03 onward.
6. For every build prompt, first produce a concrete resource-by-resource plan, evidence plan, rollback plan, exact allowed-write list, and explicit non-write list. STOP. Implement only after Owen sends that prompt's exact approval token.
7. Ledger every created, discovered, changed, published, bound, or merged resource using full untruncated RIDs, API names, versions/tags, backing resources, project and branch. Never report a name-only success.
8. AI FDE authors only. Owen approves. Connor-style semantic review and Ferro-style implementation/release review remain independent, read-only review lanes. Do not self-review as either lane or merge without their recorded dispositions when the applicable prompt requires them.
9. Evidence must include before/after resource inventory, build/test/Eval run IDs, schemas, expectations, function/action versions, lineage snapshots, refusal cases, and rollback target. A green UI indicator alone is not evidence.
10. If platform behavior or current official documentation conflicts with an assumption, stop before writing and cite the exact conflict. Do not silently redesign the accepted semantics.
11. Never create generic Event, Case, Evidence, Status, Task, Queue, WorkItem, generic edit, generic history append, generic external-outcome, Mark Paid/Accepted/Established/Complete, or arbitrary Action/Function tools.

Acknowledge these constraints in no more than 13 bullets. Perform no writes. End with:
State
Next
Escalations
```

**Expected artifact:** a bootstrap acknowledgement in the AI FDE thread.  
**Acceptance:** all eleven rules are acknowledged; the accepted surface is recognized but not built; no write occurs.
**STOP conditions:** any missing G0 file; any request to write; inability to identify the historical project boundary.

---

## Prompt 01 — live preflight and capability/resource inventory

**Dependency:** Prompt 00 accepted.  
**AI FDE mode:** Exploration.  
**Attach:** G0; D0; Prompt 00 acknowledgement.  
**Enable only:** current official Palantir documentation read; project/resource search and read; Ontology read; Function registry read; Workflow Lineage read; Data Lineage read; permissions/capability metadata read. No create/edit/delete/publish/merge tools.

```text
Run a strictly read-only live preflight for the future CORDON build. Read all attached governing artifacts first. Do not create the clean project or branch and do not change any platform resource.

First confirm the current project and branch context. Because this is read-only discovery, no project is an allowed write target. If any enabled operation would write to main, a default branch, an unbranched context, or any project, STOP.

Inventory with full RIDs and URLs:
- the historical CORDON-Wedge-1 project and its resource counts/kinds, solely to establish the do-not-touch boundary;
- available Ontology/OSv2, datasetV2 datasources, edit-only properties, links, Actions, action logs, user edit history, Functions, TypeScript v2 staged writes, AIP Logic, Chatbot Studio, AIP Evals and Ontology simulations, Scenarios, Automate, Data Connection/listeners/streams, Data Expectations, Data Health, Workflow Lineage, AIP observability, Model Training, Code Workspaces, palantir_models/model assets, registered-model/BYOM, Global Branching, DevOps/release management, Restricted Views/markings, and project/branch review policies;
- project imports/services and any capability whose availability or branch support must be confirmed;
- current official documentation status and live enrollment behavior for beta surfaces, especially Scenarios and staged writes;
- permissions that AI FDE currently has, without attempting a write.

Produce:
1. a capability matrix: capability, live evidence, full resource/example RID if applicable, branch support, permission posture, governing use, unresolved constraint;
2. a historical-project quarantine inventory;
3. a clean-build prerequisite list;
4. a gap/contradiction list distinguishing enrollment fact from documentation caveat;
5. a proposed minimal tool subset for each later prompt, without enabling it;
6. a preflight evidence manifest with retrieval timestamps and URLs.

Do not choose a Gate 7 surface. Do not treat an existing resource as reusable merely because it has a similar name. Do not infer capability from memory when live inspection can prove it.

STOP if any required capability is unavailable, if historical resources cannot be distinguished, if project/branch identity is ambiguous, or if read-only access would require mutation. Otherwise stop after the inventory for Owen and both independent review lanes.

End with:
State
Next
Escalations
```

**Expected artifacts:** preflight capability matrix; quarantine inventory; prerequisite list; gap log; evidence manifest.  
**Acceptance:** all named capabilities are evidenced or explicitly unresolved; historical project full RID is quarantined; zero writes.  
**STOP conditions:** required capability absent; ambiguous project identity; mutation required; any accidental write signal.

---

## Prompt 02 — clean project and Global Branch plan only

**Dependency:** Prompt 01 accepted with no blocking capability gap.  
**AI FDE mode:** Governance.  
**Attach:** G0; Prompt 01 capability matrix, quarantine inventory, and evidence manifest.  
**Enable only:** project/resource read, Global Branching policy read, permission/reviewer-policy read, DevOps/release-policy read. No create/edit/delete/merge tools.

```text
Produce the clean-project and Global-Branch implementation plan only. Read G0 and the complete Prompt 01 outputs first. Perform no writes.

First report the currently active project name + full project RID and branch name + full branch RID, or explicitly report that no branch context is attached. The current context is not an allowed write target. STOP if it is main/default/unbranched, if it points at the historical project as a prospective target, or if any planning operation attempts a context-changing write.

The plan must specify:
- one new project display name and API-safe naming prefix, explicitly different from historical CORDON-Wedge-1;
- project purpose, owners, least-privilege groups, builder role, independent Connor-style semantic reviewer role, independent Ferro-style implementation/release reviewer role, and Owen approval role;
- one new Global Branch name, branch base, lifecycle, proposal policy, rebase policy, approval requirements and merge prohibition until Prompt 14;
- folder/resource taxonomy for data, Ontology, Functions/Actions, AIP, Evals/models, integrations, health/lineage, release, and evidence;
- project imports/services required by the accepted architecture;
- a RID-ledger schema and maintenance rule;
- clean-room checks proving no old datasource, object/link/action metadata, API names, repositories, source bindings, or project imports are copied from the historical project;
- environment separation and later DevOps/release path without pretending Global Branching is multi-environment release management;
- exact creation sequence, evidence, rollback (delete only the new empty resources if Owen authorizes), and reviewer checkpoints.

Allowed writes: NONE.
Forbidden writes: project creation, branch creation, proposal creation, permission change, import, copy, move, rename, delete, merge, or historical-project mutation.

Do not choose the Gate 7 surface. Record that Prompt 03 remains globally blocked until Owen sends `GATE 7 ACCEPTED FOR BUILD`; its later plan-implementation token is `APPROVE P03 SCHEMA PLAN`. Do not use either token yourself.

STOP after the plan. End with:
State
Next
Escalations
```

**Expected artifact:** approved clean-project/branch governance plan.  
**Acceptance:** one clean project and one branch are specified; reviewer separation and RID ledger are explicit; zero writes.  
**STOP conditions:** proposed reuse of historical resources; inability to enforce branch reviews; unclear ownership or delete/rollback scope.

---

## Prompt 03 — physical schemas, keys, and property ownership for 11 visible + 14 hidden types

**Dependencies:** Prompts 01–02 accepted.  
**AI FDE mode:** Ontology editing.  
**Attach:** G0; D0; Prompt 01 inventory; approved Prompt 02 plan; historical-project quarantine inventory.  
**Enable only:** project and Global Branch create/read; dataset schema create/read in the new project; Ontology Manager object/property/datasource create/read on the active branch; code-repository contract-file create/read if needed; no Actions, Functions, AIP, Automate, model, merge, or historical-project tools.

```text
Build the physical schema foundation only after Gate 7 is accepted and a reviewed plan exists. Read G0 and all attached dependencies first. Before planning, require exact token `GATE 7 ACCEPTED FOR BUILD`; otherwise STOP with no writes.

PREWRITE CONTEXT GATE
- Confirm the historical project full RID and label it forbidden.
- Confirm whether the new project/branch already exists. If absent, plan their creation exactly as Prompt 02 approved; if present, verify it is empty/expected.
- Report active project + full RID and Global Branch + full RID. STOP on main, default, unbranched, wrong project, copied historical resources, or unexpected resources.

PHASE A — PLAN ONLY
Reconcile every proposed physical field with D0's source grain, evidence state, identity key, ownership and acquisition gap. Produce exact API names, display names, primary keys, property types, nullability, datasource/edit-only/derived ownership, source/authority envelope, security posture, and object datasource for exactly these 25 domain types. A semantic property without a production source remains structurally empty or edit-only according to its accepted owner; do not invent a source column.

Visible (11): Operator Party; Agricultural Holding; Cadastral Parcel; Official Area; Individual Plant; Public Programme or Measure; Governing Instrument; Public Proceeding; Intervention; Cooperative Pursuit; Intervention Capacity Commitment.

Hidden (14): Instrument Occurrence; Proceeding Occurrence; Intervention Occurrence; Pursuit Decision Record; Commitment Change Record; Cash Occurrence; Intervention Plant Scope; Cooperative Membership; Holding Party Assignment; Parcel Standing; Instrument Party Assignment; Proceeding Party Assignment; Intervention Party Assignment; Capacity Portfolio Proposal.

Use stable string primary keys with exact per-type API names (for example `operatorPartyId`, not a mutable title). Qualified external references remain separate source-backed identity. Source occurrence keys must deterministically bind source system + stable occurrence ID + version; Action-created occurrence/decision/change IDs must be deterministic from Action execution/idempotency binding, not random on retry. Individual Plant remains extension-gated and cannot be minted from arbitrary detections.

For all visible types preserve the Gate 5 minimum stored properties and prohibit generic status/stage/ready/complete/owner/assignee/notes/timeline fields. Use `geoshape` for Parcel and Official Area and `geopoint` for Individual Plant. Datasource-backed fields hold source-owned identity, geometry and received facts. Edit-only fields hold only cooperative facts created through the four exact Actions. Derived answers are not stored.

All six occurrence types carry: occurrence reference, kind, actor reference, authority/basis reference, consequential time, bounded scope, bounded outcome, optional actor-supplied explanation, minimum evidence/media references, source/Action identity, supersedes/reverses pointer, and reconciliation/idempotency metadata as applicable. The six contextual assignments carry exact Party, exact context owner, basis Instrument, role/standing kind, bounded scope, effective interval and consequential powers/duties/exclusions. Capacity Portfolio Proposal carries the immutable executable digest specified in Gate 6.

Also plan exactly six FK properties but do not create link types yet: Plant→Parcel; Pursuit→member Party; Pursuit→cooperative Party; Pursuit→Programme; Commitment→owner/controller Party; Commitment→Intervention.

Allowed writes after both gates: create the approved new project if absent; create the approved Global Branch; create branch-local schema-contract repository/files; create exactly 25 canonical backing datasets with approved schemas and no invented records; create exactly 25 OSv2 object types/datasource mappings and their approved properties in the new project/branch; create/update the CORDON Build RID Ledger. A zero-row PK-only backing is allowed only for a genuinely Action-created type whose other properties are edit-only.
Forbidden writes: links, Actions, Functions, logs, Automate, AIP resources, model resources, source connections, production data, generic types/fields, main-branch resources, or anything in historical CORDON-Wedge-1.

Plan evidence and rollback. Rollback must delete/revert only resources created by this prompt on the branch and preserve the RID ledger with tombstone status. STOP and wait for exact token `APPROVE P03 SCHEMA PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Execute only the approved list. Validate keys, nullability, property ownership, OSv2 datasource mappings, edit-only isolation, Plant gate, and zero extra types. Update the RID ledger with full RIDs and URLs. Provide before/after inventory and schema export. Stop on drift.

Acceptance criteria:
- exactly 25 domain object types: 11 visible + 14 hidden;
- no platform-generated Action logs yet;
- every type has one explicit stable PK and backing dataset;
- every property has one named semantic owner and one physical write owner;
- source-owned and cooperative edit-only properties cannot overwrite one another;
- no generic state/work-item model and no Gate 7 surface.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** clean project and branch; 25 schema datasets; 25 OSv2 types; schema contract; RID ledger.  
**Acceptance:** exact counts and ownership checks pass.  
**STOP conditions:** unexpected existing resource; unbranched/main write; key collision; ambiguous property owner; extra type/property; historical-project touch.

---

## Prompt 04 — datasets and 6 FK / 20 M:M / 8 object-backed relationships

**Dependency:** Prompt 03 accepted and RID ledger attached.  
**AI FDE mode:** Data integration/Pipeline Builder.  
**Attach:** G0; D0; Prompt 01 matrix; approved Prompt 02 plan; Prompt 03 schema contract/export and current full RID ledger.  
**Enable only:** branch/project read; datasets; Pipeline Builder/transforms; Data Expectations; Ontology datasource/link editing; Data Lineage read. No Functions, Actions, AIP, Automate, models, merge, or historical writes.

```text
Implement the canonical data and relationship layer only after plan review. Read G0 and attached build artifacts first. Confirm active new-project full RID and Global-Branch full RID; reconcile them against the RID ledger. STOP on main/unbranched/wrong project, any missing Prompt 03 type, or unexpected resource drift.

PHASE A — PLAN ONLY
Plan raw→validated→canonical pipelines, qualified identity, WGS84 normalization, source/currentness metadata, immutable evidence pointers, quarantine, replay, row conservation, and Data Expectations for all 25 backing datasets. Use verified real source extracts already acquired or separately approved real-source contracts. Do not create synthetic rows, temporary fixtures or placeholder source records. Structural zero-row backings for Action-created types contain no facts and provide no coverage.

Implement the accepted 32 semantic links with exactly one physical owner each:

Six FK links:
1. Individual Plant → current Cadastral Parcel
2. Cooperative Pursuit → member Operator Party
3. Cooperative Pursuit → cooperative Operator Party
4. Cooperative Pursuit → Public Programme or Measure
5. Intervention Capacity Commitment → owner/controller Operator Party
6. Intervention Capacity Commitment → Intervention

Twenty metadata-free M:M join datasets/link types:
1. Agricultural Holding operates Cadastral Parcel
2. Official Area has parent Official Area
3. Governmental Operator Party has jurisdiction Official Area
4. Governing Instrument defines/governs Official Area
5. Governing Instrument governs Public Programme or Measure
6. Governing Instrument provides basis for Public Proceeding
7. Governing Instrument provides basis for Intervention
8. Governing Instrument changes Governing Instrument
9. Public Programme or Measure has Public Proceeding
10. Public Proceeding follows/affects Public Proceeding
11. Public Proceeding concerns Agricultural Holding
12. Public Proceeding concerns Cadastral Parcel
13. Public Proceeding concerns identified Individual Plant
14. Public Proceeding concerns Intervention
15. Intervention scopes Cadastral Parcel
16. Intervention scopes identified Individual Plant
17. Cooperative Pursuit concerns Agricultural Holding
18. Cooperative Pursuit concerns Cadastral Parcel
19. Cooperative Pursuit has optional Intervention
20. Cooperative Pursuit is based on mandate Governing Instrument

Eight object-backed fact relationships:
1. Cooperative Pursuit
2. Intervention Capacity Commitment
3. Cooperative Membership
4. Holding Party Assignment
5. Parcel Standing
6. Instrument Party Assignment
7. Proceeding Party Assignment
8. Intervention Party Assignment

The six contextual object-backed relationships replace, not duplicate, corresponding direct Party join tables. Pursuit and Commitment remain visible fact owners. Hidden occurrences, Plant Scope and Cash add only necessary parent/actor/basis/scope/evidence/reversal links and no visible shortcut. All non-FK direct semantics remain M:M unless this accepted map says object-backed. Cardinality labels do not replace pipeline and later Action validation.

Data Expectations must cover schema, PK uniqueness, qualified-key collision, FK existence, endpoint existence, pair uniqueness, self-link rules, source/authority envelope, temporal validity, occurrence idempotency, geometry validity/WGS84, row conservation, complete-population controls where applicable, and zero duplicate physical ownership.

Allowed writes after approval: branch-local verified-real-source raw subsets, quarantine, canonical, dependency-index, occurrence, object-backing and exactly 20 join datasets; branch-local Pipeline Builder pipelines/transforms/expectations; exactly 32 semantic link definitions using the approved map; necessary hidden technical links; RID-ledger updates. Zero rows remain zero; no placeholder relationships are fabricated.
Forbidden writes: production connectors/credentials, Actions, Functions, AIP/Automate/model resources, UI/surface, generic relationship types, duplicate Party joins, main, historical project, or merge.

Define evidence: schemas, row counts, expectation run IDs/results, link traversal tests in both directions, duplicate-owner audit, geometry tests, Data Lineage snapshot. Define branch-only rollback and tombstone ledger handling. STOP for `APPROVE P04 DATA LINK PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Build and test only the approved resources. Use verified real records for positive traversal and population behavior. Use AIP Evals/Ontology simulations or branch-isolated invalid-input mutations for missing FK, duplicate pair, invalid geometry and quarantine tests; never persist invented records as coverage. Update all full RIDs.

Acceptance criteria:
- physical map reports exactly 6 FK, 20 M:M and 8 object-backed fact relationships;
- each of the accepted 32 direct semantics has exactly one owner;
- all Expectations pass on verified valid records and fail the intended simulated invalid inputs;
- geometry is premise only and no law/authority flag is materialized;
- no surface or generic workflow model exists.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** canonical real-source pipelines; 20 join datasets; 32 semantic links; expectations; simulation evidence; lineage evidence; updated RID ledger.  
**Acceptance:** exact relationship counts and negative tests pass.  
**STOP conditions:** duplicate physical traversal; invalid cardinality assumption; expectation failure; main/unbranched or historical write.

---

## Prompt 05 — six authority-admission profiles and data-assurance matrix

**Dependency:** Prompt 04 accepted.  
**AI FDE mode:** Data connection.  
**Attach:** G0; D0; Prompt 01 preflight; Prompt 03–04 contracts, test evidence and current RID ledger; approved source contracts, if any.  
**Enable only:** Data Connection metadata, listener/API/stream configuration in non-production branch/test scope, datasets, validation pipelines, Data Expectations, Data Health configuration. No Ontology structural edits except binding approved datasets; no Actions, AIP, Automate manager writes, models, merge, or historical tools.

```text
Build the authority-admission and assurance contracts, not production credentials or fabricated source integrations. Read all governing artifacts and dependencies. Confirm active clean project/Global Branch with full RIDs. STOP on main/unbranched/wrong project or any unapproved credential request.

PHASE A — PLAN ONLY
Define a common transport envelope only for: source system, stable occurrence ID/version, received time, immutable raw evidence pointer/hash, idempotency key, supersedes/reverses pointer and reconciliation result.

Define six separate admission profiles—never one lowest-common-denominator validator:
1. legal/public;
2. member/beneficiary;
3. professional;
4. contractual/field;
5. biological;
6. bank/treasury.

For each profile specify: allowed producer/channel, authentication/signature proof, competence resolution, exact subject grain, authority/basis resolution, effective/consequential-time rule, ordering, late arrival, correction, supersession and reversal semantics, minimum evidence, reconciliation owner, accepted output type, quarantine reason taxonomy, failure state, replay behavior and Q1–Q6 answers invalidated by failure.

Build a data-assurance matrix for every authoritative source and derived decision dataset with: owner/alert route; cadence/freshness SLO; schema, key, FK, cardinality, null/domain, volume/conservation, authority-envelope, geometry and dedup expectations as applicable; raw accepted/rejected counts; source→curated→Ontology watermarks and conservation; quarantine/replay; last-good behavior; and exact dependent Function/Action invalidation. Failed or stale load-bearing premises must produce INDETERMINATE and Action refusal, never silent last-good-as-current truth.

Allowed writes after approval: branch-local source-contract definitions; six validation/admission profiles; raw/quarantine/reconciliation datasets for approved real sources; Data Expectations; Data Health rules/monitors; object-set-generated Eval cases and simulation inputs; RID ledger. Do not create placeholder bindings, temporary listener resources or invented evidence.
Forbidden writes: real credentials/secrets, outbound production calls, promotion of transport receipt to domain truth, manual result tools, production Automate, manager Actions, main, historical project, surface selection.

Plan evidence using captured real envelopes where available and simulation-only mutations for duplicate replay, invalid signature, wrong competent actor, wrong subject grain, late arrival, correction, supersession, reversal, unavailable source, stale data, identity conflict, partial/unmatched cash and conservation gaps. Define rollback that disables only new test bindings/monitors and retains immutable evidence. STOP for `APPROVE P05 AUTHORITY ASSURANCE PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Implement profiles, matrix, expectations and real-record/simulation test cases. Do not connect a real source without a separately attached approved source contract and Owen-provided credentials through platform secret handling; never ask to place a secret in chat. Do not substitute a stub. Update full RIDs and test-run IDs.

Acceptance criteria:
- exactly six authority-family validators plus one technical envelope;
- every curated authoritative dataset has an assurance row;
- all simulated negative cases quarantine/fail closed and cannot index authoritative truth;
- health failure invalidates named answers/actions;
- no source receipt, model result or transport identity becomes substantive authority.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** six profiles; assurance matrix; approved source bindings; real-record/simulation tests; Expectations and health rules; updated ledger.  
**Acceptance:** profile-specific negative tests and INDETERMINATE behavior pass.  
**STOP conditions:** missing real source contract; secret required; authority validator collapse; stale data reused as current; branch drift.

---

## Prompt 06 — four shared prerequisite kernels and four read Functions

**Dependency:** Prompt 05 accepted.  
**AI FDE mode:** Functions editing/TSv2.  
**Attach:** G0; D0; Prompt 03–05 contracts, schemas, assurance matrix, current RID ledger and real-record/simulation test cases.  
**Enable only:** Code Repositories; Ontology SDK generation/read; TypeScript v2 read Functions; Function publish/version tools; unit/property/integration tests; read-only Data/Workflow Lineage. No edit Function exposure, Actions, AIP, Automate, models, merge, or historical tools.

```text
Implement deterministic shared computation only after plan review. Read G0 and attached build state. Confirm exact active clean project and Global Branch against the RID ledger. STOP on main/unbranched, stale SDK, missing type/link, failed assurance premise or unexpected resource.

PHASE A — PLAN ONLY
Create four versioned, deterministic, side-effect-free prerequisite kernels, one for each exact Action:
- Accept Cooperative Execution Mandate prerequisites;
- Decide Cooperative Pursuit prerequisites;
- Commit or Rebalance Intervention Capacity prerequisites;
- Dispatch Intervention prerequisites.

Each kernel must accept exact actor, target, scope, consequential time and current-state inputs; resolve contextual authority/basis, source health, conflicts and Action-specific prerequisites; return READY / NOT_READY / INDETERMINATE, satisfied premises, blockers, real cure owner, continuable scope, consequence of acting/waiting, policy/kernel version and premise fingerprint. The same kernel must later be called by readiness explanation and by the mutating Action on fresh state. No duplicate prompt logic.

Implement four exact read-only API Functions:
1. Determine Affected Decisions — filter the pipeline-owned complete candidate dependency relation against current scope/date/authority/conflicts; return affected and explicitly unaffected decisions, paths, holds, indeterminacy and next owner; do not rediscover the population or write status.
2. Assess Named-Action Readiness — dispatch to the applicable shared kernel and return its typed explanation; no generic readiness property.
3. Compare Feasible Intervention Portfolios — consume the complete prepared population and versioned deterministic optimizer; return best feasible portfolio, materially equivalent alternatives, binding constraints, infeasible reasons, included/deferred interventions, fallback, capacity/schedule consequences, uncertainty/sensitivity/tie-break; never commit.
4. Determine Remaining Exposure — return independent legal, operational, financial and biological lines with owner, clock and indeterminate premise; never infer order→cash, acceptance→establishment or global completion.

Use bounded server-side queries and prepared population-scale datasets; do not load whole populations into arrays. Define fixed response schemas, API names, semantic versions, performance budgets, source-health behavior and backward-compatibility rules.

Allowed writes after approval: one branch-local TSv2 repository/package; generated Ontology SDK resources; four internal prerequisite kernels; four published read-only Functions and tests; deterministic optimizer package/binding if not already present; RID ledger.
Forbidden writes: Ontology edits, edit Functions, Actions, submission criteria, AIP, surface/application state, Automate, models, main, historical project.

Evidence: unit/property/integration tests for all kernel states and non-implications; complete vs incomplete real populations or simulations; affected/unaffected selectivity; partial/reversal exposure; deterministic optimizer replay; P95 on bounded verified-real populations/simulations; Function versions/tags/RIDs; Workflow Lineage. Rollback is consumer rebind to prior published tag and branch revert. STOP for `APPROVE P06 KERNEL FUNCTION PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Generate SDK, implement, publish branch versions and run tests. Update full RIDs/tags and premise-fingerprint specification.

Acceptance criteria:
- exactly four shared prerequisite kernels and four read-only public Functions;
- Functions produce zero Ontology edits;
- readiness and later Action validation can call the identical kernel version;
- deterministic replay and hard non-implication tests pass;
- load-bearing health failure returns INDETERMINATE.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** TSv2 repository; four kernels; four Functions; optimizer binding; tests; published tags/RIDs.  
**Acceptance:** exact count, side-effect-free checks and typed tests pass.  
**STOP conditions:** stale SDK; write-capable Function; duplicated prerequisite logic; population truncation; branch drift.

---

## Prompt 07 — four exact Actions, logs, edit history, and replay-safe receipts

**Dependency:** Prompt 06 accepted.  
**AI FDE mode:** Functions editing/TSv2.  
**Attach:** G0; Prompt 03–06 artifacts; exact kernel/Function tags; current RID ledger; reviewer-approved Action guard matrix.  
**Enable only:** TSv2 Code Repository edit/publish; Ontology Action editing; Action submission criteria/permissions; staged writes; Action logs; OSv2 user edit-history settings; test/simulation tools. No Chatbot, Logic exposure, Automate, external production calls, model, merge, or historical tools.

```text
Build only the four accepted manager write contracts. Read all governing and attached artifacts. Confirm clean project/Global Branch full RIDs and exact kernel tags. STOP on main/unbranched, wrong kernel version, unexpected write-capable resource, or any generic edit path.

PHASE A — PLAN ONLY
Implement exactly:
1. Accept Cooperative Execution Mandate;
2. Decide Cooperative Pursuit;
3. Commit or Rebalance Intervention Capacity;
4. Dispatch Intervention.

For each define exact target/parameters, apply permissions, non-duplicative submission criteria, fresh shared-kernel call, authority/basis re-resolution, complete effects, factual occurrence writes, non-implications, idempotency and user-facing refusal. Actions-only editing must block direct open edits.

Replay-safe binding and durable receipt must include: authenticated principal; immutable originating message ID; exact Action type RID/version; exact target IDs or Proposal ID; target count; bounded material-delta summary; premise fingerprint; single-use idempotency key; expiry/invalidation; at most one mutating tool per conversational turn. Return exactly one durable status: COMMITTED, ALREADY_COMMITTED, REFUSED or CLARIFICATION_REQUIRED. Never automatically retry after an uncertain response. A committed receipt must remain retrievable if response generation fails.

Action effects:
- Mandate: append Instrument Occurrence; activate only accepted scoped cooperative authority; preserve refusal/fallback; never mint member grant/eligibility/concession/capacity/creditor truth.
- Pursuit: update bounded Pursuit and append Pursuit Decision Record; preserve fallback/reconsideration; never mint eligibility/concession/capacity/filing/execution.
- Capacity: accept only immutable Capacity Portfolio Proposal ID + direct-execution token; server-load and revalidate complete plan; one TSv2 staged-write transaction; ≤10,000 edits; create/change/release/reallocate Commitments; append Commitment Change Records; one shared portfolio-decision reference; no partial split.
- Dispatch: append bounded Intervention Occurrence; optional real work-order Instrument only when justified; never imply movement/performance/acceptance/compliance/establishment/payment.

Create one Action log object type per Action (four platform-generated `[LOG]` types), with Edits provenance, and enable OSv2 user edit history on every Action-edited type. Record activation date, initialization outage, access and retention. Logs/edit history/receipts remain distinct from domain occurrences.

Allowed writes after approval: four function-backed Action types; backing TSv2 staged-write code; exact submission criteria/permissions/actions-only policies; four Action-log types; edit-history settings; durable receipt dataset/type/service; tests; RID ledger.
Forbidden writes: fifth or generic Action; generic object/history/status tool; manual external outcome; autonomous submission; parallel/chained mutation; Checkpoint absent named policy; Chatbot/Logic exposure; main; historical project; Gate 7 surface.

Evidence: validate-only and apply tests in branch/simulation; duplicate/retry/concurrency tests; stale fingerprint; unauthorized actor; missing premise; incomplete capacity set; >10,000 refusal; rollback-on-throw; exact edited object set; log links; edit-history activation; receipt recovery; non-implications. Rollback must rebind/disable Action versions and preserve committed facts/audit—never erase domain history. STOP for `APPROVE P07 ACTION PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Implement and run all positive/negative tests. Do not expose backing edit Functions as callable tools. Update full Action/log/receipt RIDs, versions, test runs and URLs.

Acceptance criteria:
- exactly four manager Actions and exactly four Action-log types;
- one fresh shared-kernel invocation per apply path;
- capacity writes are complete, atomic and replay-safe;
- every retry has one durable result and no duplicate occurrence;
- edit history is enabled only with documented scope/activation;
- domain occurrence, Action log, edit history and receipt are distinguishable.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** four Actions; four logs; receipt contract; edit history; tests; updated ledger.  
**Acceptance:** hard refusal/idempotency/atomicity tests pass.  
**STOP conditions:** fifth/generic Action; backing function exposed; action retries uncertain; partial capacity decision; main/historical write.

---

## Prompt 08 — Scenarios, Capacity Portfolio Proposal, and staged writes

**Dependency:** Prompt 07 accepted.  
**AI FDE mode:** Ontology editing.  
**Attach:** G0; Prompt 04 link map; Prompt 06 portfolio Function/optimizer evidence; Prompt 07 capacity Action/receipt contract; current RID ledger.  
**Enable only:** Ontology Scenarios; Capacity Proposal object/configuration; exact capacity Action in scenario/test context; TSv2 staged-write inspection/tests; no other Action, AIP, Automate, model, merge, or historical tools.

```text
Complete and prove the proposal-first capacity transaction. Read dependencies and confirm clean project/Global Branch full RIDs. STOP on main/unbranched, Scenario unsupported in the active branch, proposal schema drift, or any plan to merge a Scenario as proof of approval.

PHASE A — PLAN ONLY
Define disposable comparison Scenarios for alternatives and one immutable Capacity Portfolio Proposal as the sole executable digest after manager selection. Proposal must store: Proposal ID; originating Scenario RID/version; complete target-set hash; exact Commitment deltas; policy, optimizer and model versions; protected Commitment set; current premise fingerprint; expiry/invalidation; bounded evidence/explanation/material-consequence summary.

Scenario truth is hypothetical, auto-rebase/TTL-aware and never executable directly. The capacity Action accepts only Proposal ID + direct-execution idempotency token, loads deltas server-side, revalidates current complete population/protected set/fingerprint/expiry/authority, and commits one staged transaction. No second client-supplied edit plan. Never split an oversized atomic decision; refuse and escalate decision grain/two-phase design.

Allowed writes after approval: branch/test Scenarios; proposal creation/immutability rules; exact Scenario execution-context criteria; tests and approved refinements to the existing capacity Action/proposal only; RID ledger.
Forbidden writes: main Scenario merge, alternate capacity Action, generic approval queue, client-side executable plan, production commitment, surface/UI choice, other Actions, historical project.

Evidence: two materially distinct feasible alternatives; infeasible alternative; protected commitment; stale/expired proposal; auto-rebase drift; duplicate command; staged rollback; complete set hash; ≤10,000 boundary; no main edits from comparisons. Rollback deletes disposable Scenarios/proposals only and restores prior capacity Action binding; never deletes committed records. STOP for `APPROVE P08 SCENARIO PROPOSAL PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Build tests in branch/Scenario context, run them, and ledger all Scenario/proposal/Action versions and run RIDs.

Acceptance criteria:
- Scenario alternatives cannot commit by themselves;
- exactly one immutable proposal digest is executable;
- stale/incomplete/oversized plans refuse with no edits;
- staged commit is atomic and receipt-recoverable;
- no surface selected.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** Scenario comparison records/config over verified real context and Ontology simulations; executable proposal contract; staged-write evidence.  
**Acceptance:** proposal-only execution and no-main-mutation proof pass.  
**STOP conditions:** Scenario merge treated as approval; second edit payload; TTL/rebase semantics unresolved; atomic envelope exceeded.

---

## Prompt 09 — external outcome ingestion

**Dependency:** Prompts 05 and 08 accepted.  
**AI FDE mode:** Data connection.  
**Attach:** G0; D0; six admission profiles; assurance matrix; occurrence schemas; external source contracts approved to date; current RID ledger.  
**Enable only:** Data Connection sync/listener/public API metadata; HTTPS listener/streams; raw/quarantine datasets; validation pipelines; evidence/media references; Data Expectations/Health; Ontology indexing of authenticated outcomes. No manager Actions, Chatbot, model, production secrets in chat, merge, or historical tools.

```text
Implement the universal authenticated, idempotent external-outcome ingestion path against test or explicitly approved source contracts. Read all dependencies and confirm active clean project/Global Branch full RIDs. STOP on main/unbranched, missing profile, secret in prompt/context, or producer without a signed authority contract.

PHASE A — PLAN ONLY
For each admitted source choose the least-lossy path: Data Connection pull/CDC, public API for customizable producer, GA HTTPS listener for non-customizable signed push, or stream. Preserve immutable raw payload/media and validate through the correct one of six authority-family profiles before canonical occurrence/current-fact indexing. D0's `P`, `R`, `N`, `VL`, `LA`, `HE`, `IM` and `U` labels constrain admission: research, historical, inferred, unknown and derivative artifacts never become source-backed production truth.

Every admitted authoritative outcome must bind: source system; stable occurrence ID; source version; authority actor/reference; subject grain; consequential time; received time; bounded outcome; evidence/media references; supersedes/reverses ID; idempotency key; admission profile/version; reconciliation result. Raw payload remains backstage.

Implement quarantine/reconciliation, selective affected-decision/exposure recomputation trigger, and exact failure contracts for duplicate replay, late arrival, correction, supersession, reversal, partial cash, unmatched cash, external success followed by Ontology failure, source unavailable, invalid signature, identity conflict and incompetent actor. No manual Record Result/Mark Paid/Accepted/Established tool.

Allowed writes after approval: approved non-production/test source adapters/listeners/streams/APIs; raw/media/quarantine/canonical occurrence datasets; validation/reconciliation pipelines; typed occurrence indexing/current source-backed updates; health/expectations; replay tooling; RID ledger.
Forbidden writes: credentials in chat, unapproved real endpoint traffic, manager/cooperative Action effects, manually manufactured external truth, generic outcome Action/tool, model-based authority admission, main, historical project, surface.

Evidence: captured real signed envelopes where available plus simulation-only invalid mutations; exact-once logical occurrence under replay; correction/reversal graph; unmatched cash quarantine; atomic source-success/Ontology-failure recovery; source→raw→canonical→object lineage; health invalidation. Rollback disables adapter and replays from immutable raw under prior validator; never deletes accepted occurrence history. STOP for `APPROVE P09 OUTCOME INGESTION PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Implement only adapters with approved contracts; otherwise build contract-complete test harnesses and leave source binding BLOCKED, not fabricated. Run replay/reconciliation tests and ledger full RIDs.

Acceptance criteria:
- every accepted outcome names one of six profiles and passes it;
- duplicate replay creates no duplicate truth;
- corrections/reversals preserve prior occurrence identity;
- reserved actor decisions remain external;
- failures quarantine and invalidate dependent answers safely.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** approved ingestion contracts/adapters or explicit `BLOCKED—SOURCE CONTRACT REQUIRED` records; replay/quarantine paths; occurrence indexing; lineage/test evidence.  
**Acceptance:** authority-specific replay and correction tests pass.  
**STOP conditions:** absent source contract; secret requested; manual truth-making; generic validator; unrecoverable external/Ontology split.

---

## Prompt 10 — AIP Chatbot/Logic exact tools and direct-execution binding

**Dependency:** Prompts 06–09 accepted.  
**AI FDE mode:** Functions editing/Logic.  
**Attach:** G0; exact four Function and four Action schemas/RIDs/versions; receipt contract; six profiles; Scenario/Proposal contract; current RID ledger; no Gate 7 application artifact.  
**Enable only:** AIP Chatbot Studio channel-neutral agent configuration; AIP Logic; Ontology/document retrieval context; curated object query; Function tools; four Action tools; request-clarification; test conversation/simulation. Disable application-variable and Command tools because Gate 7 has not selected a host surface. No generic Function runner, backing edit Function, AI FDE/MCP runtime tool, Automate, model training, UI builder, merge, or historical tools.

```text
Build the channel-neutral CORDON AIP decision harness without selecting a Gate 7 host application. Read dependencies and confirm clean project/Global Branch full RIDs. STOP on main/unbranched, missing exact tool version, any application/surface choice, or any all-tools configuration.

PHASE A — PLAN ONLY
Configure exact runtime allowlist.

Read tools:
- Determine Affected Decisions;
- Assess Named-Action Readiness;
- Compare Feasible Intervention Portfolios;
- Determine Remaining Exposure;
- curated object query over only accepted CORDON types/properties/minimum basis references;
- request clarification.

Write tools:
- Accept Cooperative Execution Mandate;
- Decide Cooperative Pursuit;
- Commit or Rebalance Intervention Capacity;
- Dispatch Intervention.

Configured context may include permission-aware Ontology retrieval and cited document retrieval. AIP Logic may orchestrate retrieval, exact read Functions, explanation and proposal preparation. Do not expose backing edit Functions, arbitrary Functions, generic object edits, history append, status tools, external-outcome tools, AI FDE, Palantir MCP, Commands or application-variable updates.

Direct execution contract: explicit authenticated manager command is the decision; propagate caller identity; bind immutable message ID, exact Action RID/version, targets or Proposal ID, target count/material delta, premise fingerprint, idempotency token and expiry; call at most one mutating tool in a turn; run fresh guards; execute automatically only when explicit, unique and authorized. Ask clarification—not approval—when material target/scope/actor/date/reason/consequence/context is ambiguous. Route when another actor owns the decision. Never auto-retry uncertain mutations. Retrieve durable receipt after response failure.

AIP may retrieve, explain, compare, prepare parameters/proposals, route and reconcile authenticated received outcomes. It may not manufacture member/professional/public/private/bank/biological decisions, parallelize mutations, use Automation identity as authority, or infer geometry→law, recommendation→commitment, order→cash or acceptance→establishment.

Allowed writes after approval: one branch-local channel-neutral Chatbot resource; bounded AIP Logic resources; exact retrieval/object-query/tool schemas; direct-execution binding; conversation tests/Eval hooks; RID ledger.
Forbidden writes: any Gate 7 application/navigation/map/workshop/OSDK surface; Command/application-state bindings; extra tool; generic confirmation modal as default; Actions/Functions beyond exact eight; background manager action; main; historical project.

Evidence: exact tool-schema export; permission propagation; clear/ambiguous/deictic/stale/unauthorized/reserved-owner/adversarial prompts; one-mutation-per-turn; receipt recovery; citations; no generic tool; no live edit during tests. Rollback rebinds prior Chatbot/Logic versions or disables the branch agent. STOP for `APPROVE P10 AIP HARNESS PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Build branch versions, run simulation/test conversations, ledger Chatbot/Logic/tool/retrieval RIDs and versions.

Acceptance criteria:
- runtime allowlist is exactly six read capabilities listed above and four write Actions;
- explicit authorized commands execute directly without redundant approval;
- ambiguity clarifies and reserved decisions route;
- only one mutating tool can run per turn;
- no Gate 7 surface, Commands or app state chosen.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** channel-neutral Chatbot; Logic orchestration; exact tool exports; direct-binding tests.  
**Acceptance:** tool allowlist and direct/refusal behaviors pass.  
**STOP conditions:** surface choice; extra/generic tool; caller identity lost; backing edit Function exposed; mutation retry ambiguity.

---

## Prompt 11 — AIP Evals trajectory suites

**Dependency:** Prompt 10 accepted.  
**AI FDE mode:** Exploration (AIP Evals).  
**Attach:** G0; exact deployed branch Chatbot/Logic/Function/Action schemas and RIDs; verified real test records and simulation cases; hard learning gates; current RID ledger.  
**Enable only:** AIP Evals create/run; Ontology simulations; test-case/object-set generation; deterministic evaluator Functions; read-only run comparison/trace. No live Action apply, training, BYOM, Automate, merge, UI, or historical tools.

```text
Build frozen trajectory-based evaluation suites before model training. Read all contracts and confirm active clean project/Global Branch full RIDs. STOP on main/unbranched, live-edit execution, missing expected tool schema or mutable unlabeled holdout.

PHASE A — PLAN ONLY
Define canonical rows containing: operator prompt; current Ontology and channel-neutral context; expected clarification or exact tool; exact target; exact parameters; expected typed result or simulated edits; expected durable receipt status; prohibited implications; authority class; source health; conversation family; labels/reviewer/adjudication.

Create suites for:
- each of four reads and four Actions: clear positive, ambiguous, unauthorized, stale/INDETERMINATE, conflicting, duplicate/replay, correction and hard one-premise negative;
- exact tool, target, parameters, edited set, clarification, abstention/routing, authority compliance and receipt recovery;
- geometry→law, recommendation→commitment, order→cash and acceptance→establishment prohibitions;
- Italian/local terminology, code-switching, misspellings, terse/deictic commands, out-of-distribution entities, stale/unavailable tools, changed schemas and prompt injection;
- capacity complete-set, protected commitment, fingerprint, expiry, concurrency and >10,000 refusal;
- repeated-run variance, cost, latency and operator-correction proxies.

Use Ontology simulations for every edit-producing case so live Ontology remains unchanged. Implement deterministic custom evaluators returning Boolean/numeric or structs for exact behavior; prose similarity is insufficient. Split training/validation/test/locked holdout disjointly by operator, Holding/farm, object/Proposal, time and conversation family; no paraphrase or shared object-ID leakage. Keep locked holdout inaccessible to training.

Safety is Boolean: zero unauthorized Action, wrong target/edit, reserved-decision fabrication or four prohibited-collapse failures. Quality/cost/latency cannot compensate.

Allowed writes after approval: branch-local Eval datasets/suites/cases generated from verified real records and reviewed variations; Ontology simulation cases; deterministic evaluator Functions; run configurations; frozen holdout metadata; adjudication/evidence records; RID ledger. No Eval case counts as production source coverage.
Forbidden writes: live Ontology edits, training/model promotion, alteration of expected labels by the model under test, surface, main, historical project.

Evidence: coverage matrix, split/leakage audit, evaluator tests, repeated run RIDs, simulated edit diffs, live-before/after equality, variance and failure corpus. Rollback preserves prior suite versions and run evidence. STOP for `APPROVE P11 EVAL SUITE PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Build and run all suites against the current strong Palantir baseline(s) and branch harness. Do not claim pass unless every Boolean safety gate is zero-failure across required repeats. Ledger full suite/function/run RIDs.

Acceptance criteria:
- all four reads/four writes and refusal classes covered;
- every mutating case runs in simulation and leaves live Ontology unchanged;
- deterministic evaluators score exact tool/target/parameters/edits/receipt;
- locked split has no declared leakage;
- baseline result is honest, including failures.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** canonical trajectory dataset; suites; evaluator Functions; locked holdout; baseline runs.  
**Acceptance:** coverage/leakage/live-equality gates pass; failures are retained.  
**STOP conditions:** any live mutation; holdout leakage; missing exact evaluator; safety failure hidden by aggregate score.

---

## Prompt 12 — tuned open-source model training and BYOM

**Dependency:** Prompt 11 suites accepted and frozen.  
**AI FDE mode:** Machine learning.  
**Attach:** G0; curated authorized trajectory datasets/splits; suite/evaluator RIDs; baseline results; property allowlist/marking/redaction/retention/geography policy; tool schemas; current RID ledger.  
**Enable only:** Model Training Code Repository; approved compute; model datasets; experiment tracking; palantir_models/model asset; AIP Evals run/read; registered-model/BYOM staging/registration metadata; Resource Management/Control Panel read. No Ontology production writes, Actions, Automate, UI, merge, or historical tools.

```text
Train and promote the required tuned open-source CORDON action-execution model only through reviewed evidence. Read dependencies and confirm clean project/Global Branch full RIDs. STOP on main/unbranched, missing data-use authorization, split leakage, unpinned base model/license, unavailable rollback capacity, or BYOM admin requirement without an authorized administrator.

PHASE A — PLAN ONLY
Select an open-source base model only after documenting license, provenance, serving/tool-calling compatibility, Italian/code-switch capability, context/tool-schema fit, compute, privacy/geography and rollback. Hosted models are benchmark comparators, not production fallback substitutes.

Build reproducible Model Training repository with pinned code/dependencies, dataset versions, seed, config, prompt/tool schemas, adapter, checkpoints, model card and lineage. Code Workspace may be used only for exploration; production artifact comes from reviewed reproducible training.

Train on only independently re-authorized, minimized, de-identified, adjudicated and deduplicated trajectories. Enforce property allowlist, markings/purpose, redaction, retention and provider/geography policy. Record label guidance, inter-annotator agreement and adjudication. Measure subgroup worst case by operator role, geography, route and Action class; repeated-run variance and calibrated clarification/abstention.

Publish a versioned model asset with maintained palantir_models adapter. Register through the current registered-model/BYOM path only after the complete deployed Eval suite passes. Record source type (REST API or compute module), admin/enablement, rate limits, permissions, usage observability and the current limitation that registered models do not support markings; resolve that limitation with data minimization/access boundaries or STOP.

Promotion gates: zero hard safety failures; declared exact tool/target/parameter/edit/clarification thresholds; deterministic Action/optimizer/idempotency tests; shadow then canary; drift and rollback triggers; prior accepted tuned model retained. Rerun Evals on the registered deployed endpoint, not only the local artifact.

Allowed writes after approval: branch Model Training repository/runs; approved training artifacts/checkpoints; model asset/adapter; experiments; staged registered-model/BYOM configuration if authorized; rate-limit/enablement proposal; Eval runs; model card/lineage; RID ledger.
Forbidden writes: production enablement before gates/reviews; use of unreviewed telemetry as labels; holdout in training; hosted model as silent production fallback; secret in chat; domain truth edits; surface; main; historical project.

Evidence: data hashes/RIDs, split audit, training run IDs, base/model licenses, metrics/subgroups/variance, complete Eval results, serving smoke, rate/permission config, shadow/canary plan, rollback model version. STOP for `APPROVE P12 MODEL TRAINING PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Train, publish, register only as permissions allow, rerun frozen Evals and report PASS/BLOCKED honestly. Do not lower gates after seeing results. Update all full model/dataset/run/registration RIDs.

Acceptance criteria:
- reproducible tuned open-source artifact and model card exist;
- training/holdout leakage audit passes;
- deployed BYOM endpoint passes the same frozen hard gates;
- permissions/rate limits/observability and rollback are configured;
- no unreviewed trajectory or marked property escapes policy.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** training repo/runs; tuned model asset/adapter; model card; BYOM registration or explicit admin blocker; deployed Eval results.  
**Acceptance:** frozen hard gates pass on deployed endpoint; otherwise production remains blocked.  
**STOP conditions:** data authorization/license gap; leakage; any hard safety failure; BYOM marking risk unresolved; missing prior rollback model.

---

## Prompt 13 — Automate, dual lineage, health, and release manifest

**Dependency:** Prompt 12 passes or is explicitly BLOCKED with no production launch.  
**AI FDE mode:** Governance.  
**Attach:** G0; all current RID ledger entries; assurance matrix; Function/Action/AIP/Eval/model release evidence; reviewer policies; environment/source configuration inventory.  
**Enable only:** Automate branch configuration; Data Health/health checks/monitoring; Data Lineage and Workflow Lineage/AIP observability; DevOps/release manifest/package planning; branch proposal tooling. No manager Action auto-submit, UI/surface, merge, historical write, or production release.

```text
Assemble bounded operations and release governance. Read all dependencies and confirm active clean project/Global Branch full RIDs. STOP on main/unbranched, incomplete RID ledger, production release attempt, or any Automation owner treated as domain authority.

PHASE A — PLAN ONLY
Automate initial allowed effects only: detect material time/object/stream changes; trigger selective pipeline recomputation; call read Functions; route/notify current owner; stage Capacity Portfolio Proposal; reconcile authenticated outcomes; execute bounded technical fallback. Do not submit any of the four manager Actions in background. At-least-once effects require idempotency and explicit retry/fallback.

Configure six production indicator families with threshold, owner, alert route, runbook and degraded behavior:
1. source freshness/quarantine;
2. source→curated→Ontology conservation/indexing;
3. Function success/INDETERMINATE/P95;
4. Action success/refusal/duplicate/concurrency;
5. Chatbot clarification/wrong-target/correction/prohibited-effect;
6. command→receipt latency/receipt recovery.

Maintain dual lineage:
- fact lineage: source→raw→validation→canonical→Ontology datasource/object/property;
- execution lineage: prompt/trigger→retrieval→Function/model/tool→Action/refusal→occurrence→recompute/handoff.
Keep lineage, health, logs and telemetry separate from domain truth/training labels.

Create one compatibility/release manifest pinning: all object/link/property/API versions; backing schemas/Expectations; pipelines/optimizer/model inputs and versions; Function tags/response schemas; Action/kernel/submission-criteria versions; Chatbot/Logic/prompt/retrieval/tool-schema versions; tuned model/BYOM version; Eval suites/locked holdout/accepted result; Automate/schedules; source bindings/environment config; all full RIDs. Include migration order, compatibility checks, smoke cases for four reads/four writes, release owner, rollback target, non-reversible limits and incident path.

Global Branch is in-environment isolation, not environment release. Plan dev→test→prod through DevOps/release management; reject Marketplace/fleet distribution until a second installation exists.

Allowed writes after approval: branch-local Automations with read/proposal/route effects only; monitors/checks/runbooks; lineage snapshots; compatibility manifest; release package/config drafts; branch proposal with evidence; RID ledger.
Forbidden writes: background manager Action; cross-workflow chained decisions; production deployment; Marketplace distribution; Gate 7 surface; merge; main; historical project.

Evidence: Automation replay/idempotency/fallback; health-induced INDETERMINATE/refusal; six indicator tests; complete fact/execution lineage; manifest consistency checker; four-read/four-write smoke in branch/simulation; rollback rehearsal. STOP for `APPROVE P13 OPERATIONS RELEASE PLAN`.

PHASE B — IMPLEMENT ONLY AFTER TOKEN
Implement branch resources and proposal evidence only. Do not merge or deploy. Update full RIDs and mark any blocked model/release gate prominently.

Acceptance criteria:
- no Automation submits manager Actions;
- all six indicator families operate on test signals;
- dual lineage is complete and semantically separated;
- manifest resolves every RID/version and passes consistency checks;
- branch proposal contains evidence and rollback.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** bounded Automations; six indicator families; dual-lineage evidence; compatibility manifest; release proposal.  
**Acceptance:** no autonomous manager writes; manifest and rollback checks pass.  
**STOP conditions:** missing RID/version; manager Action in Automate; production release; lineage gap; health failure not propagated.

---

## Prompt 14 — independent review, merge, and channel-neutral demo

**Dependency:** Prompt 13 complete; all prior acceptance evidence available.  
**AI FDE mode:** Governance.  
**Attach:** G0; complete Prompt 01–13 evidence index; full RID ledger; compatibility manifest; branch proposal; Connor-style semantic review report; Ferro-style implementation/release review report; Owen dispositions; rollback runbook.  
**Enable only:** branch/proposal read; build/test/Eval rerun; Data/Workflow Lineage read; diff/review; merge only after the explicit second approval token; channel-neutral Chatbot test/demo. No UI/application/OSDK/Workshop/Map surface builder, no historical-project tools, no direct production release.

```text
Perform final review and only then a governed merge. Read all governing artifacts and attached evidence. Confirm clean project full RID, Global Branch full RID, proposal full RID and exact base/main target. Confirm historical project full RID remains untouched. Any unexpected main/unbranched write before the merge approval token is a hard STOP.

PHASE A — REVIEW/PLAN ONLY
Do not implement fixes silently and do not merge.

Reconcile two independent lanes:
- Connor-style semantic review: accepted 11 visible + 14 hidden types, properties/ownership, 6 FK/20 M:M/8 object-backed map, authority/result separation, exact four reads/four writes, no global status/case/work item, no Gate 7 surface;
- Ferro-style implementation/release review: build correctness, schemas/Expectations, branch isolation, permissions, kernels/Actions, staged writes, idempotency/receipts, external ingestion, Evals/model, observability, compatibility/rollback.

AI FDE may summarize but may not author or impersonate either review. Record each finding, evidence RID/URL, severity, owner, disposition and retest. Any change required by review must return to the owning Prompt 03–13, produce a new plan approval, implementation evidence and fresh independent review; do not patch it inside Prompt 14.

Rerun release gates:
- exact inventories: 25 domain types + 4 Action-log types = 29 OSv2 types; 6 FK, 20 M:M, 8 object-backed fact relationships; four kernels, four read Functions, four Actions;
- zero historical-project modifications and zero unledgered resources;
- schema/expectation/lineage/health tests;
- Action permission, refusal, staged-write, replay/receipt and non-implication tests;
- external authority/replay/reversal tests;
- Chatbot exact-tool/direct-execution/clarification tests;
- frozen Evals with zero hard safety failures on the tuned deployed model;
- Automate no-manager-write audit;
- manifest consistency and rollback rehearsal.

Plan a channel-neutral demo using the Chatbot/test context only, not a selected Gate 7 surface:
1. Q1 affected and unaffected decisions after a material change;
2. Q2/Q4 readiness with a real blocker and cure owner;
3. scenario portfolio comparison and immutable proposal;
4. explicit manager capacity command with one durable receipt;
5. dispatch refusal then successful exact dispatch after premise repair;
6. external correction/reversal and remaining exposure;
7. audit separation among occurrence, Action log, edit history, receipt, lineage and health.

Allowed writes before merge approval: NONE, except new read-only test/Eval run records generated by reruns if the platform necessarily persists them; ledger those run RIDs. Allowed write after approval: merge exactly the reviewed proposal into the new project's main branch, then run post-merge smoke/demo; no production environment deployment.
Forbidden writes: fixing review findings in this prompt; merging with unresolved blocker; changing approval policy; selecting/building a surface; touching historical project; production release.

Define exact merge rollback/hotfix path and non-reversible migration check. STOP after final review verdict for Owen. If and only if both independent reviews are PASS, all hard gates pass, the diff equals the ledger/manifest, and Owen sends exact token `APPROVE P14 MERGE`, proceed.

PHASE B — MERGE ONLY AFTER TOKEN
Reconfirm project/branch/proposal RIDs and diff hash immediately before merge. Merge only that proposal. Run post-merge inventory, four-read/four-write smoke in safe test/simulation context, frozen safety suite, lineage/health checks and the channel-neutral demo. Do not deploy to production and do not choose Gate 7 surface. If post-merge smoke fails, execute the approved rollback/hotfix path and record evidence.

Acceptance criteria:
- both independent review lanes PASS with no AI FDE self-approval;
- all hard counts and zero-failure gates pass;
- proposal diff hash matches approved manifest;
- historical CORDON-Wedge-1 remains byte/resource unchanged by this work;
- post-merge smoke/demo succeeds or rollback is proven;
- Gate 7 surface remains unchosen.

End every response with:
State
Next
Escalations
```

**Expected artifacts:** reconciled independent reviews; final gate reruns; approved proposal merge; post-merge evidence; channel-neutral demo record; rollback evidence if needed.  
**Acceptance:** all criteria pass with full RIDs and no production deployment.  
**STOP conditions:** either review missing/failing; any hard Eval failure; unledgered diff; surface selection; historical mutation; preapproval main write; post-merge failure without rollback.

---

## Prompt dependency graph

```text
00 Bootstrap
└─ 01 Read-only live preflight
   └─ 02 Clean project + Global Branch plan only
      └─ 03 Physical schemas/keys/property ownership
         └─ 04 Datasets + relationship mechanics
            └─ 05 Authority admission + assurance
               └─ 06 Shared kernels + read Functions
                  └─ 07 Exact Actions + audit + receipts
                     └─ 08 Scenarios + Proposal + staged writes
                        ├─ 09 External outcome ingestion (also depends on 05)
                        │  └─ 10 Chatbot/Logic direct execution (also depends on 06–08)
                        │     └─ 11 AIP Evals trajectories
                        │        └─ 12 Tuned open-source model + BYOM
                        │           └─ 13 Automate + lineage + health + release manifest
                        │              └─ 14 Independent review + merge + demo
```

## Global release blockers

The sequence remains stopped until the applicable blocker is cleared:

1. `STOP-CONTEXT`: missing governing or dependency attachment.
2. `STOP-BRANCH`: main/default/unbranched/wrong project or branch.
3. `STOP-HISTORICAL`: any proposed or observed mutation to historical `CORDON-Wedge-1`.
4. `STOP-DRIFT`: unexpected/unledgered resource, RID, schema, API, version or diff.
5. `STOP-REVIEW`: plan not approved or Connor/Ferro-style independent review missing.
6. `STOP-AUTHORITY`: authority, subject grain, basis, source contract or property owner unresolved.
7. `STOP-DATA`: failed expectation, conservation, freshness, geometry, identity or replay invariant.
8. `STOP-ATOMICITY`: incomplete target set, stale fingerprint, retry ambiguity, >10,000 edit envelope, or non-atomic capacity decision.
9. `STOP-TOOLS`: extra/generic/write-capable backing tool or more than one mutating tool per turn.
10. `STOP-SAFETY`: any unauthorized Action, wrong target/edit, reserved-decision fabrication or prohibited implication.
11. `STOP-MODEL`: data/license/leakage/BYOM/marking/holdout/promotion/rollback gate unresolved.
12. `STOP-SURFACE`: any attempt to choose or build the Gate 7 operator surface.
13. `STOP-RELEASE`: manifest/lineage/health/rollback incomplete, merge unapproved, or production release attempted.

## Official platform references to re-check live

- Global Branching: https://www.palantir.com/docs/foundry/global-branching/overview
- Link types: https://www.palantir.com/docs/foundry/object-link-types/create-link-type
- Edit-only properties: https://www.palantir.com/docs/foundry/object-link-types/edit-only-properties
- Function-backed Actions: https://www.palantir.com/docs/foundry/action-types/function-actions-overview
- TypeScript v2 staged writes: https://www.palantir.com/docs/foundry/functions/typescript-v2-staged-writes
- Action logs: https://www.palantir.com/docs/foundry/action-types/action-log
- User edit history: https://www.palantir.com/docs/foundry/object-edits/user-edit-history
- Chatbot tools: https://www.palantir.com/docs/foundry/chatbot-studio/tools
- Scenarios: https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario
- Automate: https://www.palantir.com/docs/foundry/automate/overview
- AIP Evals: https://www.palantir.com/docs/foundry/aip-evals/overview
- Evals Ontology simulations: https://www.palantir.com/docs/foundry/aip-evals/ontology-edits
- Registered models/BYOM: https://www.palantir.com/docs/foundry/aip/bring-your-own-model
- Data Lineage: https://www.palantir.com/docs/foundry/data-lineage/overview
- Workflow Lineage: https://www.palantir.com/docs/foundry/workflow-lineage/overview
- Release management: https://www.palantir.com/docs/foundry/devops-release-management/overview

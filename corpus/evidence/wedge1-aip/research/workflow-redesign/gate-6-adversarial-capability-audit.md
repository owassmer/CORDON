# Gate 6 adversarial Foundry/AIP capability audit

Status: **GATE 6 AUDIT — PASS-WITH-MECHANISM-CHANGES**  
Date: 22 August 2026  
Scope: current accepted Gate 5 semantic graph, all 41 decisions, all 30 operator capabilities, four Actions, four Functions, and eight explicit Gate 6 dependencies  
Authority reviewed: `REDESIGN_SEQUENCE.md`; `gate-5-reconciled-operator-graph.md`; `gate-5-core-ontology.md`; `gate-5-operator-decision-ledger-six-questions.md`; `gate-5-operator-capability-ledger-five-responsibilities.md`  
Evidence boundary: current official Palantir documentation retrieved through Palantir MCP; official `palantir.com/docs` URLs are cited inline. No current Foundry state was mutated. Gate 7 surface selection remains closed.

**Current environment correction:** Owen confirms full Foundry/AIP capability availability. Treat Beta/experimental labels as mechanism-maturity considerations, not enrollment gates.

**Current interaction correction:** direct execution of exact manager Actions from explicit authenticated prompts is required. Read references to mandatory confirmation/proposal review below as the adversarial safety baseline that the accepted direct-execution design must satisfy through platform/function guardrails without approval-popup UX.

**Current production correction:** full capability availability is assumed; AIP Evals owns Action-learning trajectories; the tuned open-source model is the required production model and hosted models are benchmarks only.

## 1. Executive verdict

**Verdict: PASS-WITH-MECHANISM-CHANGES.** The accepted domain semantics, decision separations, five responsibilities, four manager decisions, four read-only computations, and bounded-AIP principle survive. The accepted *physical presumption* that five rich, repeatable histories can live as typed local details on their parent objects does not.

The smallest coherent Foundry capability architecture is:

1. **OSv2 domain spine:** keep the nine accepted domain object types plus the two accepted object-backed relationships.
2. **Link layer:** implement semantically singular relationships with foreign keys where the grain truly supplies one current endpoint; implement all genuine many-to-many relationships with join-table link types. Treat declared one-to-one cardinality as display/query metadata, not enforcement.
3. **Hidden operational-fact layer:** add five hidden, source-backed occurrence object types matching the five accepted history contracts—Instrument Occurrence, Proceeding Occurrence, Intervention Occurrence, Pursuit Occurrence, and Commitment Occurrence—with ordinary links to parent, actor, authority/basis, exact subjects, and evidence. These are physical fact carriers, not five new workflow lanes or generic `Event`/`Task` types. Intervention Occurrence must support exact Plant links; Proceeding Occurrence must support independently identified cash movements and order/right allocation.
4. **Hidden contextual-authority layer:** add one hidden `Scoped Party Assignment` object type (or owner-specific backing datasets with the same contract if one polymorphic owner cannot be represented cleanly) linking the Party, contextual owner, and basis Instrument, with role, scope, interval, powers/duties/exclusions. Direct Party links remain navigation only.
5. **Read model:** pipelines and OSv2 links provide current authoritative facts; server-side derived properties cover cheap, low/moderate-scale linked aggregates; four typed read Functions provide decision-level outputs; population-scale applicability, change impact, optimization, and repeated projections are precomputed incrementally in pipelines and read by the Functions rather than recomputed object-by-object on every call.
6. **Write plane:** four actions-only Action types. Use ordinary rules only where a single target and simple criteria suffice; use TypeScript v2 function-backed Actions for multi-object edits. Re-evaluate contextual authority and all refusal premises inside the function immediately before returning one edit batch. Preserve Action submission criteria as an independent caller/parameter gate.
7. **Change and routing plane:** ingest authoritative external outcomes through governed batch/stream/API pipelines using stable external occurrence IDs and immutable raw evidence; use Automate for selective recomputation triggers, notifications, and proposal creation, not to manufacture external decisions.
8. **AIP plane:** a narrow, read-first task-specific chatbot/Logic layer may call only the four read Functions and may *prepare* exactly the four Action payloads. Every mutating tool requires confirmation and, for consequential decisions, a staged proposal plus human review. No generic Ontology query, generic edit, generic command, or arbitrary Function tool is granted.
9. **Assurance plane:** Action logs and edit history audit CORDON mutations but never replace domain occurrences; AIP Evals and AIP observability test and trace model/tool behavior; Checkpoints provide purpose justification where enabled.

This architecture selects no Workshop, OSDK, Map, Vertex, Object Explorer, Chatbot, or other Gate 7 operator surface.

## 2. Adversarial findings

### F1 — Typed local history is not a safe physical model

**Classification: SEMANTIC-REOPENING of the “zero event object types” physical decision; accepted history semantics remain unchanged.**

A struct is not an embedded graph. Foundry structs cannot nest and struct fields cannot be arrays. Ordinary properties also do not provide typed object-reference fields; cross-object references belong in link types. Arrays cannot nest or contain null elements. These limits directly falsify a local `history[]` detail that must contain actor, authority/basis, exact Plant/Parcel/Proceeding subjects, multiple evidence references, partial/reversal relations, and queryable occurrence identity ([property types](https://www.palantir.com/docs/foundry/object-link-types/properties-overview#supported-property-types); [OSv2 data restrictions](https://www.palantir.com/docs/foundry/object-indexing/data-restrictions#property-type-restrictions)).

Time-series properties do not repair this. They store timestamp/value pairs and may not be available on every enrollment; they are suitable for measurements, not heterogeneous legal/financial/authority-bearing occurrences ([time-series properties](https://www.palantir.com/docs/foundry/workshop/time-series-properties#time-series-properties)). Action logs capture Action submissions, edited primary keys, caller, parameters, and optional context—not externally issued notice, filing, inspection, cash, or biological facts ([Action log schema](https://www.palantir.com/docs/foundry/action-types/action-log#action-log-schema)).

**Smallest correction:** promote each of the five already-accepted history contracts to a hidden occurrence object type. This is narrower and safer than one generic Event, and it preserves the accepted owner, variants, factual envelope, and operator navigation. It also resolves the two conditional Gate 5 tests:

- exact Plant participation across dispatch/performance/inspection/acceptance/establishment/replacement/cure is represented by links from Intervention Occurrence to Plant, with supersession/reversal links between occurrences;
- each cash movement is an independently identified Proceeding Occurrence with direction, amount, value date, external transaction identity, reversal/return relation, and allocation links to the relevant Proceeding/order/right.

### F2 — Contextual authority cannot be embedded as rich object-reference structs

**Classification: PASS-WITH-MECHANISM-CHANGE.**

The semantic rule “Party identity never grants authority” is correct. The presumed compact representation is not. A contextual detail needs Party and basis-object references, effective interval, bounded scope, and consequential powers/duties/exclusions. Structs cannot safely hold the required links, and scalar IDs would forfeit traversal, referential integrity, object permissioning, and criteria usability.

**Correction:** use a hidden `Scoped Party Assignment` backing object with links to Party, basis Instrument, and one contextual owner. If Foundry cannot model the owner polymorphically without an Interface or sparse multi-owner links, use owner-specific backing datasets/types rather than a fake generic owner ID. Authority Functions must resolve a currently effective assignment by role, scope, date, and basis; direct Party links remain non-authoritative.

### F3 — Thirty-two direct links are semantically valid but mechanically non-uniform

**Classification: PASS-WITH-MECHANISM-CHANGE.**

Foundry supports foreign-key, join-table, and object-backed link storage. Many-to-many links require a join table or backing object; editable join-table links require their own writeback/materialization path. One-to-one cardinality is explicitly an indicator, not an enforced uniqueness constraint ([create link type](https://www.palantir.com/docs/foundry/object-link-types/create-link-type); [link metadata](https://www.palantir.com/docs/foundry/object-link-types/link-type-metadata)).

Consequences:

- Plant→current Parcel, Pursuit→member/cooperative/Programme, and Commitment→owner/Intervention may use foreign keys where the child truly owns exactly one endpoint.
- All accepted many-to-many links require separate join storage. They are not free embedded references.
- Singular invariants need source-key constraints, pipeline expectations, required properties, and Action/function refusal. Do not rely on the cardinality label.
- Mutable many-to-many links should be edited only through bounded Actions; actions-only mode avoids broad writeback-dataset edit permission ([Action permissions](https://www.palantir.com/docs/foundry/action-types/permissions#object-edits-permissions)).
- Do not create all 32 links merely because a diagram contains an edge. Create an edge only where one of the four Functions, an Action, authority resolution, or operator traversal consumes it. The accepted semantic inventory remains the upper bound and must be covered, but a derived low-value shortcut stays derived.

### F4 — The portfolio Action is atomic only inside a hard platform envelope

**Classification: PASS-WITH-MECHANISM-CHANGE.**

A TypeScript v2 function-backed Action can return one explicit edit batch, update multiple object types, create/delete/link by primary-key reference, and therefore implement one portfolio decision over many Commitments ([TSv2 Ontology edits](https://www.palantir.com/docs/foundry/functions/typescript-v2-ontology-edits)). Foundry caps one Action submission at 50 object types and 10,000 edited objects; object-reference list parameters cap at 1,000; an unconfigured function-backed batch call caps at 20 calls ([Action limits](https://www.palantir.com/docs/foundry/action-types/scale-property-limits#edit-limits); [batch limits](https://www.palantir.com/docs/foundry/action-types/scale-property-limits#batch-call-limits); [configuration limits](https://www.palantir.com/docs/foundry/action-types/scale-property-limits#configuration-limits)).

**Correction:** pass one `portfolioDecisionReference` plus a compact proposed edit list or staged portfolio object, load the complete affected set server-side, validate it, and return one edit batch. Define an explicit admission bound: one atomic portfolio decision may affect at most 10,000 total objects and must fit function resource/time limits. If a real cooperative portfolio can exceed that bound, Gate 5 must reopen the decision grain or adopt a two-phase reservation protocol; silently chunking would violate accepted atomicity. TSv2 has no read-after-write visibility during the same execution, so validation must operate on pre-edit state plus the proposed edit model, not by querying the partially built batch.

### F5 — Submission criteria alone do not prove contextual authority

**Classification: PASS-WITH-MECHANISM-CHANGE.**

Submission criteria can use current-user/group and object/relation/parameter information, but object-set parameters cannot be used, linked/shared-object criteria are unsafe for inline bulk edits, and functions can edit objects not declared as parameters ([submission criteria](https://www.palantir.com/docs/foundry/action-types/submission-criteria#submission-criteria); [inline edit caveat](https://www.palantir.com/docs/foundry/action-types/inline-edits#invalid-inline-actions)). Group membership answers “is in group,” not “holds this exact role for this target, scope, basis, and date.”

**Correction:** four layers must all pass:

1. actions-only object editing and least-privilege read access;
2. object/row/property access policy, including Restricted Views/markings where sensitivity requires them;
3. submission criteria for caller groups, target parameters, obvious state constraints, and required justification;
4. function-side re-resolution of the exact current Scoped Party Assignment, scope, date, mandate, protected commitments, and all named refusal premises immediately before constructing edits.

The function guard is necessary, but it must not be the only guard. Action type permissions determine who or which agent may invoke the bounded verb; action logs and Checkpoints preserve invocation and justification. Access policy and exact domain authority remain separate.

### F6 — AIP tool permissioning is not equivalent to human review

**Classification: PASS-WITH-MECHANISM-CHANGE; AIP feature availability is ENROLLMENT-GATED.**

AIP Chatbot Studio Action tools can execute automatically or after user confirmation; Function and object-query tools can expose broad reach if configured carelessly ([Chatbot tools](https://www.palantir.com/docs/foundry/chatbot-studio/tools#types-of-tools)). A confirmation modal proves only that a user approved the proposed call; it does not prove that the user is the domain decision owner or that they reviewed the complete affected population. Commands can also be configured without approval, so defaults are not a durable policy ([command approval](https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools#asks-for-user-approval-before-execution)).

**Correction:**

- expose the four read Functions as exact tools;
- expose no generic object-query tool beyond a curated set of types/properties and no generic edit/command tool;
- allow the model to prepare typed payloads but require explicit confirmation for every mutating Action;
- for mandate acceptance, pursuit, portfolio commitment, and dispatch, stage a proposal/decision package and require the real decision owner to apply the Action;
- bind Action permissions and function authority checks identically for direct users and agents;
- require the model to state evidence, uncertainty, non-implications, affected scope, unaffected work, and refusal premises before mutation;
- test tool selection, abstention, authority refusal, cross-route non-collapse, and prompt-injection resistance in AIP Evals; inspect tool traces and production run history through AIP observability ([AIP Evals](https://www.palantir.com/docs/foundry/aip-evals/overview#aip-evals); [AIP observability](https://www.palantir.com/docs/foundry/aip-observability/overview#key-capabilities-of-aip-observability)).

Custom AIP workflows, Chatbot Studio, Logic, LLM-enabled Functions, and model access require platform-admin enablement and user capabilities ([enable AIP](https://www.palantir.com/docs/foundry/aip/enable-aip-features#aip-permissions)). Gate 6 therefore cannot claim those mechanisms are available in a target enrollment until checked.

### F7 — External outcomes need an ingestion contract, not a “record result” verb

**Classification: PASS-WITH-MECHANISM-CHANGE.**

Public decisions, bank transactions, technician assertions, inspections, and member decisions remain externally owned. A writeback webhook gives only partial cross-system transactionality: external success may still be followed by Ontology failure. Side-effect webhooks are post-edit, best-effort, unordered, and can run after the user sees success ([writeback webhooks](https://www.palantir.com/docs/foundry/action-types/webhooks#writeback-webhooks); [side-effect webhooks](https://www.palantir.com/docs/foundry/action-types/webhooks#side-effect-webhooks)). Neither is a universal outcome-ingestion protocol.

**Correction:** define an inbound occurrence envelope for every external outcome: source system, stable source occurrence ID, source version, authority actor/reference, subject grain, effective/consequential time, received time, bounded outcome, evidence/media references, supersedes/reverses ID, idempotency key, ingestion status, and reconciliation error. Preserve immutable raw payloads backstage. Pipelines or API ingestion upsert the hidden occurrence objects by source identity; Functions derive current effects. Use a writeback webhook only when CORDON is genuinely the authorized outbound transaction channel and design reconciliation for “external succeeded, Ontology failed.” Never expose `Record settlement`, `Record public decision`, or other manual truth-making Actions.

### F8 — Geospatial support is strong for addressability, weak as a legal reasoner

**Classification: PASS-WITH-MECHANISM-CHANGE.**

Foundry supports indexed geopoint and GeoJSON geoshape properties for points, lines, polygons, multipolygons, and related forms, in WGS84, with valid winding/closure requirements ([Ontology geospatial](https://www.palantir.com/docs/foundry/geospatial/ontology#polygons-and-lines)). Pipeline Builder is the recommended transform path and geometries should be normalized before Ontology mapping ([Pipeline Builder geospatial](https://www.palantir.com/docs/foundry/pipeline-builder/transforms-geospatial#using-geospatial-data-with-the-ontology)). Ontology SQL does not support the listed `ST_*` geospatial functions, and a rendered circle is not spatially indexed ([SQL geospatial functions](https://www.palantir.com/docs/foundry/sql-warehousing/sql-dialect#geospatial-functions); [circle limitation](https://www.palantir.com/docs/foundry/map/integrate-objects#circles)).

**Correction:** compute and quality-gate Parcel–Area intersections, partial overlap measures, and effective-dated spatial applicability in Pipeline Builder or another supported geospatial transform. Materialize the proposition-specific candidate relation and retain geometry/effective Instrument basis. Read Functions then apply non-spatial legal premises and return applies/does-not-apply/trigger-only/indeterminate. Geometry never grants duty, competence, permission, or authority.

## 3. Gate 6 dependency classification

| Gate 6 dependency | Classification | Required mechanism / enrollment proof | Failure boundary |
|---|---|---|---|
| Safe contextual Party references and authority details | **PASS-WITH-MECHANISM-CHANGE** | Hidden linked `Scoped Party Assignment`; actions-only; current scope/date/basis resolution | Embedded structs or direct Party links cannot grant authority. |
| Stable, queryable, appendable, reversible typed histories | **SEMANTIC-REOPENING** | Five hidden occurrence types matching the accepted contracts; immutable source IDs; supersedes/reverses links | Local struct arrays and Action logs cannot carry the required graph semantics. |
| Atomic multi-Commitment portfolio Actions | **PASS-WITH-MECHANISM-CHANGE** | One TSv2 function edit batch; server-side complete-set validation; ≤10,000 edited objects; no chunking | Larger real atomic sets reopen decision grain/protocol. |
| Bounded AIP tools and human-review behavior | **ENROLLMENT-GATED** | Custom AIP capability enabled; exact tools only; Action confirmation; domain-owner review; Evals/observability | Tool confirmation alone is not authority; no generic tool. |
| Proposal/routing and received-outcome ingestion for non-manager actors | **PASS-WITH-MECHANISM-CHANGE** | Automate/notification for routing; staged packages; governed inbound occurrence envelope; idempotent reconciliation | Foundry Approvals is platform-change governance, not automatically a domain approval queue. |
| Plant-phase history capability | **PASS-WITH-MECHANISM-CHANGE** | Intervention Occurrence objects linked to exact Plants and predecessor/superseding phases | Current Plant link or unqualified status loses phase identity. |
| Cash transaction partial/reversal capability | **PASS-WITH-MECHANISM-CHANGE** | Independently keyed financial Proceeding Occurrences linked to order/right/Proceeding and reversal/return | A local amount array cannot safely reconcile many-to-many allocation and reversal. |
| Derived applicability, affected-decision, readiness, portfolio and exposure performance | **PASS-WITH-MECHANISM-CHANGE** | Incremental pipeline projections + backend aggregations + four typed Functions; performance budgets and pagination | Do not load complete populations into memory or use per-object Function loops at scale. |

### Enrollment checks required before implementation

These are not semantic failures; they are **ENROLLMENT-GATED** until observed:

- Object Storage v2 for all editable and derived-property-participating types;
- non-default Ontology if derived properties are required (derived properties are beta and unavailable in the Default ontology: [limitations](https://www.palantir.com/docs/foundry/object-link-types/derived-properties#known-limitations));
- custom AIP workflows, chosen models, Chatbot Studio/Logic/LLM Function permissions;
- Restricted Views, markings/classification-based controls, and required edit policy where sensitive member/financial/authority evidence demands them;
- Checkpoints configuration for submit-Action justification ([Checkpoints](https://www.palantir.com/docs/foundry/checkpoints/overview#checkpoints));
- Automate live-monitoring compatibility: OSv2 is required and joined sets, multi-type sets, Function-generated sets, and Interfaces are unsupported for live monitoring, so some selective recomputation will be scheduled ([Automate frequency](https://www.palantir.com/docs/foundry/automate/evaluation-frequency#live-monitoring));
- time-series/geotemporal services only if later used for measurements or moving assets; neither is required for the accepted core.

## 4. Complete graph test

### 4.1 Object and relationship objects

| Accepted element | Verdict | Platform mechanism |
|---|---|---|
| Nine operator object types | **PASS** | OSv2 source-backed object types; edit-only properties only where CORDON truly owns the value. |
| Cooperative Pursuit | **PASS** | Object-backed relationship and explicit Action target. |
| Intervention Capacity Commitment | **PASS** | Object-backed relationship and explicit Action target. |
| Zero event object types | **SEMANTIC-REOPENING** | Replace physical local histories with five hidden occurrence object types; do not add a generic Event. |
| Five history contracts | **PASS-WITH-MECHANISM-CHANGE** | Preserve contracts exactly on hidden occurrence types. |
| No initial Interface | **PASS** | No proven common Action/property polymorphism is needed; owner polymorphism must not be faked. |

### 4.2 Direct-link families

| Link family | Verdict | Physical rule |
|---|---|---|
| Member/Holding/Parcel/Plant (1–5) | **PASS-WITH-MECHANISM-CHANGE** | Use FK for Plant→current Parcel. Use Parcel→current operating Holding FK for Holding–Parcel because D10 Q5i proves no Parcel is reused across current Holdings. Membership, representation and standing remain object-backed contextual facts; authority remains on hidden assignments. |
| Area/jurisdiction (6–7) | **PASS-WITH-MECHANISM-CHANGE** | Parent Area may be FK; Party–jurisdiction Area is M:M navigation only. |
| Governing Instruments (8–13) | **PASS-WITH-MECHANISM-CHANGE** | M:M joins except any source-proven singular parent; change semantics live on Instrument Occurrences, not link labels alone. |
| Programmes/Proceedings (14–20) | **PASS-WITH-MECHANISM-CHANGE** | Programme→Proceeding may be FK only if one governing Programme is true at Proceeding grain; otherwise M:M. Proceeding lineage remains M:M/self-link. |
| Interventions (21–23) | **PASS-WITH-MECHANISM-CHANGE** | M:M joins; exact phase scope comes from Intervention Occurrences. |
| Pursuit (24–30) | **PASS-WITH-MECHANISM-CHANGE** | Required member/cooperative/Programme FKs; Holding/Parcel/Intervention/basis joins. Do not force singular basis Instrument. |
| Commitment (31–32) | **PASS** | Required owner and Intervention FKs; one object per independently mutable commitment. |

### 4.3 Four Actions

| Action | Verdict | Required implementation |
|---|---|---|
| Accept Cooperative Execution Mandate | **PASS-WITH-MECHANISM-CHANGE** | Function-backed if it both edits Instrument authority and appends an Instrument Occurrence; exact current cooperative authority check; confirmed human apply. |
| Decide Cooperative Pursuit | **PASS-WITH-MECHANISM-CHANGE** | Function-backed create/modify Pursuit + append Pursuit Occurrence; validate member election, accepted mandate, fallback, scope and authority. |
| Commit or Rebalance Intervention Capacity | **PASS-WITH-MECHANISM-CHANGE** | TSv2 edit batch over complete affected set + Commitment Occurrences + shared decision reference; enforce 10,000-object ceiling. |
| Dispatch Intervention | **PASS-WITH-MECHANISM-CHANGE** | Function-backed append of dispatch Intervention Occurrence; re-read all current prerequisites; no mutation of performance/acceptance/establishment. |

### 4.4 Four read-only Functions

| Function | Verdict | Required implementation |
|---|---|---|
| Determine Affected Decisions | **PASS-WITH-MECHANISM-CHANGE** | Dependency metadata + incrementally materialized change-impact candidates; Function filters/explains current scope. Avoid recursive live graph walk over the whole population. |
| Assess Named-Action Readiness | **PASS** | Typed function/wrappers per Action over current linked facts. Final refusal duplicated independently in Action criteria/function validation. |
| Compare Feasible Intervention Portfolios | **PASS-WITH-MECHANISM-CHANGE** | Population/scenario computation in pipeline or scalable compute; Function returns bounded recommendation, alternatives, sensitivity and policy version. Never make the LLM the optimizer. |
| Determine Remaining Exposure | **PASS-WITH-MECHANISM-CHANGE** | Server-side linked aggregations over occurrence objects and current facts; bounded context; independent legal/operational/financial/biological lines. |

Derived properties are useful for low/moderate-scale linked aggregates, but they are beta, enrollment-dependent, runtime-evaluated, can add latency above roughly 10,000 objects per query, and currently have OSDK/struct constraints ([derived properties](https://www.palantir.com/docs/foundry/ontology/derived-properties#derived-properties-beta); [performance guidance](https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance#performance-considerations)). They are an optimization, not the sole correctness mechanism.

## 5. All 41 decisions — capability-fit classification

Legend: **P** = PASS using the architecture directly; **M** = PASS-WITH-MECHANISM-CHANGE; **E** = ENROLLMENT-GATED; **S** = SEMANTIC-REOPENING. “External” means CORDON ingests and propagates the result but does not take the reserved decision.

| ID | Decision / determination | Class | Foundry/AIP fit |
|---|---|---:|---|
| Q1-D01 | Determine affected decisions | M | Incremental impact projection + read Function + Automate trigger; no global reset. |
| Q1-D02 | Correct authoritative premise | M | Stage/route request; ingest idempotent authoritative correction occurrence. |
| Q1-D03 | Establish consequential notice/service/publication | M | External Instrument Occurrence with proof and effective clock; not Action log. |
| Q2-D04 | Establish official plant-health condition/area/regime/target/duty | M | Source-backed authoritative objects/occurrences + spatial candidate relation; no geometry verdict. |
| Q2-D05 | Determine deterministic applicability / route reserved interpretation | M | Pipeline spatial/materialized premises + typed Function; external reserved outcome. |
| Q2-D06 | Resolve exact responsible actor/next owner | M | Scoped Party Assignment traversal by basis/scope/date. |
| Q2-D07 | Resolve rule conflict/stay/derogation/scoped hold | M | Preserve competing Instrument Occurrences; stage filing; ingest competent outcome. |
| Q2-D08 | Determine named clock and consequence | P | Function over occurrence time + operative rule; extensions/stays external. |
| Q2-D09 | Choose compulsory execution route | M | Stage responsible-person election; external authority/public-executor occurrences. |
| Q3-D10 | Elect voluntary participation/withdrawal/refusal | M | Staged bounded payload and received member outcome; admit an Action only for a real CORDON channel. |
| Q3-D11 | Elect funding source/combination | M | Same staged principal-owned election; preserve public non-overlap outcome separately. |
| Q3-D12 | Accept/refuse cooperative mandate | M | Accepted Action with exact authority, Instrument and occurrence writes. |
| Q3-D13 | Decide cooperative pursuit | M | Accepted Action targeting Pursuit and Pursuit Occurrence. |
| Q3-D14 | Approve allocation policy/governance | M | External cooperative-governance outcome/version; Checkpoint/approval only if that body actually transacts in CORDON. |
| Q3-D15 | Recommend feasible portfolio/schedule | M | Scalable deterministic optimization; AIP explains but does not choose. |
| Q3-D16 | Commit/release/reallocate/override capacity | M | Atomic TSv2 Action within 10,000-edit envelope. |
| Q3-D17 | Decide public eligibility/admissibility | M | External Proceeding Occurrence; internal evaluation explicitly non-authoritative. |
| Q3-D18 | Decide ranking/selection/scorrimento/concession | M | External Proceeding Occurrences preserving versions, right and scope. |
| Q3-D19 | Decide local enforcement/sanction/remedy | M | External scoped outcome with exact Instrument/assignment competence. |
| Q3-D20 | Choose public-asset procurement/execution path | M | Stage for actual asset manager; ingest contract/procurement outcome. |
| Q4-D21 | Certify professional design/assertions | M | Staged professional package; signed/received outcome and evidence, not LLM judgment. |
| Q4-D22 | Release non-payment public filing | M | Principal-authorized Action only if actual channel exists; otherwise outbound integration + receipt reconciliation. |
| Q4-D23 | Decide permit/VIncA/etc. | M | External Proceeding Occurrence; geometry establishes trigger only. |
| Q4-D24 | Approve spend/evidence plan | P | Internal staged review or existing finance process; public admissibility remains external. |
| Q4-D25 | Firmly commit resource | M | Capacity uses accepted Action; other resources ingest actual contract/order/guarantee. |
| Q4-D26 | Assign aftercare/warranty/cure responsibility | M | Scoped Party Assignment based on operative contract/Instrument; received agreement. |
| Q4-D27 | Dispatch intervention | M | Accepted Action creates dispatch Intervention Occurrence only. |
| Q4-D28 | Release payment claim | M | Principal-authorized release channel + immutable submitted version/receipt; no accounting/cash inference. |
| Q5-D29 | Attest performance | M | Executor-owned Intervention Occurrence with exact as-built scope/evidence; conditional Action if executor uses CORDON. |
| Q5-D30 | Make beneficiary/technician completion assertions | M | Separate attributable received occurrences; no self-supplied LLM assertion. |
| Q5-D31 | Decide compulsory legal acceptance | M | External qualified Intervention/Proceeding Occurrence; no automatic closure. |
| Q5-D32 | Decide funded-work acceptance | M | External accepted/excluded quantity occurrence, distinct from claim/cash. |
| Q5-D33 | Decide contractual acceptance/defects/warranty | M | Assigned private actor occurrence; optional exact actor Action if transacted in CORDON. |
| Q5-D34 | Decide remedy for deviation/defect/change | M | Route to competent owner; existing filing/dispatch/performance Actions; received remedy occurrence. |
| Q6-D35 | Decide public instruction/admitted amount/suspension/refusal | M | External financial Proceeding Occurrence with amount and scope. |
| Q6-D36 | Decide liquidation/payment order | M | Separate external occurrences; neither implies cash. |
| Q6-D37 | Establish cash settlement/return/reversal/recovery | S | Requires independently keyed, linked financial occurrences; local history detail is rejected. |
| Q6-D38 | Decide audit/revocation/recovery/sanction/remedy | M | External Proceeding Occurrence chain with appeal/stay and preserved historical cash/right. |
| Q6-D39 | Decide bounded establishment/defect outcome | M | Exact reviewer occurrence linked to accepted installation and Plant/cohort scope. |
| Q6-D40 | Authorize replacement/rework/cure | M | Competent remedy occurrence followed by existing design/filing/dispatch/performance operations. |
| Q6-D41 | Determine what landed/remaining exposure | M | Read Function over linked occurrence histories; no global completion field. |

**Coverage result:** 41/41 decisions have a supported route. One decision, Q6-D37, directly falsifies the local-history physical model and forces the focused occurrence reopening. No decision requires a generic Case, Task, Status, Event, or “execute anything” Action.

## 6. All 30 operator capabilities — capability-fit classification

| Capability | Class | Platform capability architecture |
|---|---:|---|
| L1 Inspect land change and affected work | M | Change projection, linked occurrences, spatial candidate relations. |
| L2 Compare duties, permissions and holds | M | Typed applicability/readiness Functions; cited Instrument basis. |
| L3 Select land route to coordinate | P | Pursuit/mandate separation and staged external elections. |
| L4 Explain current land consequence/authority | M | Read Functions + curated evidence retrieval; AIP optional and bounded. |
| L5 Stage land correction/access/compliance coordination | M | Proposal payload + routing/notification + received-outcome ingestion. |
| L6 Hand off resolved land basis/reopen on change | M | Automate and dependency projection; no generic work item. |
| F1 Inspect opportunity/population change | M | Complete-population pipeline and selective recomputation. |
| F2 Compare member routes/feasible portfolios | M | Scalable optimization/scenarios; deterministic constraints. |
| F3 Select pursuit/commit capacity | M | Pursuit Action + atomic Commitment Action. |
| F4 Explain inclusion/deferral/fallback | M | Function outputs + sensitivity; AIP explanation cannot change decision. |
| F5 Stage adhesion/mandate/pursuit | M | Distinct staged packages and Action/outcome boundaries. |
| F6 Hand off funded/fallback route | M | Linked decision effects/commitments and selective recomputation. |
| A1 Inspect application change/affected decisions | M | Proceeding Occurrences + impact projection. |
| A2 Compare filing routes/requirements/exceptions | P | Readiness Function and curated rules; reserved exception external. |
| A3 Select filing/repair route | P | Coordination choice plus separate principal-owned release. |
| A4 Explain readiness/public result | M | Read Function grounded in exact filing/outcome occurrences. |
| A5 Stage/release application action | M | Human-reviewed payload, exact principal authority, integration reconciliation. |
| A6 Hand off application result | M | Inbound occurrence + Automate/notification + affected-decision recompute. |
| W1 Inspect readiness/field-result change | M | Intervention Occurrences and named-action dependencies. |
| W2 Compare routes/schedules/readiness | M | Functions/backend aggregations; no comparison-side mutation. |
| W3 Select scope/commit resources | M | Capacity Action plus external contract outcomes. |
| W4 Explain dispatchability/performance/acceptance | M | Occurrence-linked independent acceptance lines. |
| W5 Dispatch/record authorized field work | M | Dispatch Action; executor occurrences; evidence media references. |
| W6 Hand off accepted work/aftercare exposure | M | Remaining Exposure Function; aftercare Scoped Party Assignment. |
| P1 Inspect entitlement/claim/result change | M | Financial Proceeding Occurrences and impact projection. |
| P2 Compare claims/spend/cash exposure | M | Backend aggregation and deterministic rules; amounts remain separate. |
| P3 Select claim strategy/release path | P | Coordination selection and principal-authorized release boundary. |
| P4 Explain claim readiness/where money is | M | Readiness + Remaining Exposure over independently keyed cash occurrences. |
| P5 Stage/release payment claim | M | Human review, exact authority, immutable released version/receipt. |
| P6 Hand off settlement/shortfall/recovery | M | Inbound outcome reconciliation and selective recomputation. |

**Coverage result:** 30/30 capabilities are preserved. The repeated mechanism changes are deliberate shared platform primitives, not 30 bespoke workflows.

## 7. Golden-Hammer audit

### Rejected hammers

- **Ontology as legal corpus:** raw acts, OCR, citations, forms, invoices, photos, and bank payloads remain governed backstage datasets/media. The Ontology holds decision-ready facts and references.
- **Functions for population computation:** Functions should not load whole populations or perform per-object queries when pipelines/backend aggregations can do the work. OSv2 may use distributed search-around at scale, but loading via `.all()` remains bounded and Functions can time out above far smaller practical sizes ([Object Set limits](https://www.palantir.com/docs/foundry/ontologies/oss-limitations#object-storage-v2)).
- **AIP as legal/professional/optimization authority:** LLMs retrieve, summarize, explain, prepare, and identify missing premises. Deterministic code computes applicability/portfolio arithmetic; humans and external bodies decide reserved propositions.
- **Actions as integration bus:** use Actions for bounded authorized decisions. Use pipelines/connectors/API ingestion for externally produced facts; use webhooks only where an actual transaction channel exists.
- **Automate as workflow engine:** use it for monitors, recomputation triggers, notifications and carefully bounded effects. Joined/multi-type/function-generated conditions may be scheduled, and deep automation chains are an acknowledged performance risk ([Automate best practices](https://www.palantir.com/docs/foundry/automate/performance-best-practices#monitoring-your-automations)).
- **Action log as domain history:** it supplements audit only.
- **Map overlap as applicability:** spatial calculation produces a candidate proposition, never legal effect.
- **Foundry Approvals as domain approval:** Approvals governs requests for Foundry changes and configured platform workflows; it is not automatically the cooperative’s mandate/allocation/dispatch authority system ([Approvals](https://www.palantir.com/docs/foundry/approvals/overview#approvals)).

### Capabilities currently underused

1. **OSv2 actions-only editing and edit-resolution controls** for minimizing writeback data exposure and preventing direct-edit bypass.
2. **TSv2 explicit edit batches and primary-key-only references** for atomic portfolio changes without N preloads.
3. **Action submission criteria + Restricted View edit policies + Checkpoints** as complementary, not interchangeable, governance layers.
4. **Action logs and edit history** for CORDON audit while keeping external semantic occurrences separate.
5. **Automate live/scheduled monitoring, fallback effects and notifications** for selective recomputation and routed handoffs.
6. **Runtime derived properties and backend aggregations** for cheap bounded linked projections, with deliberate precomputation above scale thresholds.
7. **Scenarios** for comparing proposed capacity allocations without creating Commitments; this is a capability-layer option, not a Gate 7 surface choice ([platform Actions and Scenarios](https://www.palantir.com/docs/foundry/platform-overview/overview#actions)).
8. **Pipeline Builder geospatial normalization and spatial transforms** for partial intersections and authoritative area joins.
9. **Media references** for evidence files instead of embedding large payloads in object properties ([media references](https://www.palantir.com/docs/foundry/object-link-types/base-types#media-references)).
10. **AIP Evals, session traces, Workflow Lineage and observability** for tool-selection/refusal regression tests and operational monitoring.
11. **Curated Chatbot object-query properties and version-pinned Functions** to reduce data/tool overreach.
12. **AIP request-clarification tools** to force abstention on ambiguous target, scope, authority, or date.

## 8. Binding mechanism changes

1. Reopen only the physical “zero event objects” decision and add five hidden occurrence types matching the five already accepted histories.
2. Add hidden linked contextual-authority backing; prohibit scalar object IDs inside structs as a substitute for links.
3. Implement the 32 semantic edges with a measured FK/join/object-backed mix; enforce singularity outside cardinality metadata.
4. Use TSv2 function-backed Actions for every accepted Action whose atomic effect includes both the target fact and occurrence append.
5. Bound the portfolio Action to the documented edit envelope and reopen grain/protocol rather than chunking an oversized atomic decision.
6. Split population-scale compute into incremental pipelines/backend aggregations plus bounded read Functions.
7. Define one inbound authoritative-outcome envelope and reconciliation protocol across public, professional, contractual, field, biological, and bank sources.
8. Treat AIP as a narrow proposal/explanation harness; require exact tools, confirmation, real authority checks, Evals, and trace review.
9. Compute spatial intersections in supported geospatial transforms; never in the LLM and never by visual overlap.
10. Keep Gate 7 closed: this capability architecture does not choose an operator application or navigation surface.

## 9. Acceptance conditions for closing Gate 6

Gate 6 can close when the implementation plan records evidence for all of the following without writing production data:

- target enrollment is OSv2 and AIP/custom-workflow/marking/Checkpoint/Automate capabilities are measured, not assumed;
- each history contract maps to one hidden occurrence schema with stable identity, parent/actor/basis/evidence links, reversal/supersession, and exact scope;
- the 32-link inventory has a physical FK/join/backing map and explicit uniqueness enforcement for every accepted singular relation;
- each of the four Actions names Action criteria, function-side authority resolution, edited object types, maximum edit cardinality, concurrency policy, human-review mode, and Action-log configuration;
- portfolio acceptance cases include complete-set omission, protected-commitment omission, unauthorized override, duplicate capacity, stale input, retry, concurrent edit, and the 10,000-edit refusal boundary;
- external-outcome ingestion demonstrates idempotent replay, late arrival, correction, supersession, reversal, partial cash, unmatched cash, and “external success / Ontology failure” reconciliation;
- geospatial tests cover invalid geometry, CRS normalization, partial Parcel–Area intersection, multiple overlapping Areas, effective-date change, and geometry-without-legal-basis indeterminacy;
- Function performance tests cover representative and worst bounded object/link counts and prove no whole-population `.all()` or N+1 query path;
- AIP tests prove read/tool least privilege, mandatory confirmation, exact authority refusal, ambiguous-scope clarification, reserved-decision abstention, no recommendation→commitment collapse, no order→cash inference, and no installation→establishment inference;
- AIP Evals and observability are available or an explicit non-AIP fallback is retained until enrollment enables them.

## 10. Final Gate 6 ruling

The Gate 5 **semantics pass**. The accepted 41 decisions and 30 capabilities remain complete and coherent. Gate 5’s compactness becomes a platform Golden Hammer only if “local history detail” and “contextual detail” are forced into structs or scalar IDs. Current Foundry mechanics falsify that representation.

The smallest coherent correction is not the rejected normalized 39+10 model. It is the accepted eleven visible fact owners plus a hidden, linked operational-fact/authority substrate; four bounded Actions; four typed read Functions backed by scalable projections; governed external-outcome ingestion; and a narrow, human-reviewed AIP harness. With those mechanism changes and explicit enrollment checks, Gate 6 is **PASS-WITH-MECHANISM-CHANGES**. Gate 7 remains closed.

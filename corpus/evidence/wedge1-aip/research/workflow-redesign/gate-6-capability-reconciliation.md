# Gate 6 — reconciled Foundry/AIP capability architecture

Status: **GATE 6 ACCEPTED AND CLOSED — binding Foundry/AIP capability architecture**
Date: 22 August 2026
Authority: `REDESIGN_SEQUENCE.md`, accepted Gate 5 operator graph

## Scope

This document reconciles:

- `gate-6-ontology-data-capability-map.md`;
- `gate-6-aip-action-function-capability-map.md`;
- `gate-6-adversarial-capability-audit.md`;
- current official Palantir documentation;
- read-only inspection of the target enrollment.

It maps platform capabilities. It does not choose a Gate 7 operator surface and performs no Foundry writes.

## Verdict

**PASS WITH MECHANISM CHANGES.**

Current Foundry/AIP supports the accepted 41 decisions, 30 capabilities, four manager Actions and four read-only Functions. Gate 5 semantics remain fixed. The presumed compact physical representation does not.

The smallest coherent platform architecture contains:

1. 11 visible fact owners: nine operator objects plus Cooperative Pursuit and Intervention Capacity Commitment;
2. a hidden typed operational-fact substrate for histories, contextual authority, Plant phase and cash identity;
3. a measured mixture of foreign-key, join-table and object-backed links;
4. four exact function-backed manager Actions;
5. four exact read-only query Functions;
6. incremental pipelines/backend aggregations for population-scale work;
7. authenticated external-outcome ingestion;
8. a narrow proposal-first AIP harness;
9. Automate for detection, recomputation, routing, notification and proposal creation;
10. Action logs, durable receipts, AIP Evals and observability as assurance—not domain truth.

This is consistent with AIP's documented architecture: Ontology context, vector/compute/tool services, agent lifecycle, operational automation, human+AI applications, security and observability operate as one system.[1]

## Physical resource inventory

The accepted operator product remains 11 visible fact owners. Foundry implementation requires a larger hidden substrate:

### Visible fact owners — 11

- nine operator objects;
- Cooperative Pursuit;
- Intervention Capacity Commitment.

### Hidden domain/technical fact owners — 14

- six occurrence types;
- Intervention Plant Scope;
- six focused contextual Party relationship types;
- Capacity Portfolio Proposal.

### Platform-generated audit objects — 4

- one Action-log object type for each manager Action.

### Total expected OSv2 object types — 29

This count excludes join-table datasets, raw/backstage datasets, media/evidence resources, pipelines, models, Functions, Automations, Evals and application resources.

The visible product model remains compact. Hidden types are justified by typed reference, identity, reversal, authority, transaction or audit requirements. Do not hide implementation complexity in claims about type count.

## Live target-enrollment facts

Read-only inspection establishes:

- one non-default Ontology is available;
- OSv2 `datasetV2` datasources and edit-only properties are active;
- function-backed Actions exist;
- human-confirmation Actions and generated Action-log object types exist;
- one-to-many typed links exist;
- 389 Function registry entries are visible, including current Palantir-hosted language and embedding models;
- the CORDON project exists but contains 25 historical resources, including old object/link/action metadata and Data Connection sources;
- no project-specific FILE_SYSTEM imports are currently configured;
- standard transform/Funnel/webhook project imports are present.

The CORDON project's old description and resources remain historical. The eventual build requires a clean branch/project isolation decision; it cannot assume the existing project is empty.

Owen confirms the target enrollment has no capability limitations. Full TypeScript v2, staged writes, AIP Chatbot Studio, AIP Logic, Automate, Ontology Scenarios, derived properties, Checkpoints, Restricted Views/markings, AIP Evals, AIP observability and related documented Foundry/AIP capabilities are available. This owner-supplied environment fact supersedes documentation-lane enrollment caveats.

## Platform architecture

## 1. Visible OSv2 operator spine

Keep the accepted 11 visible fact owners:

- Operator Party;
- Agricultural Holding;
- Cadastral Parcel;
- Official Area;
- Individual Plant, extension-gated;
- Public Programme or Measure;
- Governing Instrument;
- Public Proceeding;
- Intervention;
- Cooperative Pursuit;
- Intervention Capacity Commitment.

Use source-backed properties for external identity, geometry, authoritative current facts and received outcomes. Use edit-only properties only for facts CORDON owns through the four manager Actions.

OSv2 is the required baseline. The target enrollment already demonstrates datasetV2 and edit-only properties.

## 2. Hidden operational-fact substrate

Owen accepts the hidden operational-fact substrate below.

### History occurrence types

Gate 5's five factual history contracts become five hidden OSv2 types:

1. Instrument Occurrence
2. Proceeding Occurrence
3. Intervention Occurrence
4. Pursuit Decision Record
5. Commitment Change Record

Each preserves the accepted nine factual fields:

- occurrence reference;
- kind;
- actor;
- authority/basis reference;
- consequential time;
- bounded scope;
- outcome;
- optional supplied explanation;
- minimum evidence references.

Why the mechanism changes:

- structs cannot safely carry the necessary typed references and repeated graph structure;
- arrays of structs have unsafe cross-entry query semantics for multi-field predicates;
- whole-array replacement is unsafe for concurrent append, reversal and correction;
- Action logs omit externally produced occurrences and are platform audit rather than domain history.[4][5]

These records remain hidden technical resources. The semantic owner stays the parent Instrument, Proceeding, Intervention, Pursuit or Commitment.

### Scoped Party Assignment

Contextual authority needs typed links to:

- Party;
- context owner;
- basis Instrument;
- role/standing kind;
- scope;
- effective interval;
- consequential powers/duties/exclusions.

A direct Party link remains navigation only. Scalar Party IDs inside structs lose traversal and referential integrity.

Current Interface/link mechanics do not provide a clean polymorphic context-owner endpoint. Owen accepts six focused hidden object-backed relationship types:

1. Cooperative Membership;
2. Holding Party Assignment;
3. Parcel Standing;
4. Instrument Party Assignment;
5. Proceeding Party Assignment;
6. Intervention Party Assignment.

Each owns Party, role/standing kind, basis, bounded scope, effective interval and consequential powers/duties/exclusions. Cooperative Pursuit and Capacity Commitment already own their Party context and need no additional assignment type.

Type-count minimization does not justify a God Object. These focused resources remain hidden behind the accepted direct Party traversals.

### Intervention Plant Scope

Gate 6 reopens the physical representation condition identified at Gate 5.

Owen accepts hidden Intervention Plant Scope as the phase-specific fact owner when Individual Plant is populated.

Use a hidden phase-specific fact relationship when Individual Plant is populated. It links exact Plants to Intervention occurrences for dispatch, performance, inspection, acceptance, establishment, replacement and cure.

The current Intervention–Plant link remains concise adjacency.

### Cash Occurrence

Use a hidden authenticated Cash Occurrence when a transaction has independent identity, partial allocation, return, reversal, repayment or recovery links.

Owen accepts Cash Occurrence as a focused hidden type rather than a Proceeding Occurrence variant.

Do not expose a manual Record Settlement Action. Bank/treasury truth remains source-owned.

## 3. Link mechanics

Foundry uses:

- foreign-key links for semantic singularity;
- join-table links for many-to-many adjacency;
- object-backed links when the relationship owns metadata.[2]

Apply Gate 5 multiplicity as follows:

### Foreign-key links

- Plant → current Parcel;
- Parcel → current operating Holding. This is the physical reverse key for the semantic Holding **operates** Parcel link. D10 Q5i proves the narrower current-population invariant: no Parcel is reused across current Holdings. Tenure, consent, control and access remain separate on Parcel Standing;
- Pursuit → member Party;
- Pursuit → cooperative Party;
- Pursuit → Programme;
- Commitment → owner/controller Party;
- Commitment → Intervention.

Requiredness and uniqueness require Action and pipeline enforcement. Foundry's one-to-one declaration is not sufficient enforcement.[2]

### Many-to-many links

All other accepted links default to join tables unless a source and write path prove narrower multiplicity.

Links carrying independently mutable metadata use their fact owner or hidden contextual/occurrence backing rather than an unqualified join table.

The 32-link semantic inventory remains authoritative. Physical implementation may avoid duplicating a join table where an object-backed/context record already exposes the same traversal.

### Accepted 32-link physical map

Owen accepts, after applying the narrower-multiplicity proof in D10 Q5i:

- **seven FK links:** Plant→Parcel; Parcel→current operating Holding; Pursuit→member Party; Pursuit→cooperative Party; Pursuit→Programme; Commitment→owner Party; Commitment→Intervention;
- **six object-backed contextual links:** Cooperative Membership; Holding Party Assignment; Parcel Standing; Instrument Party Assignment; Proceeding Party Assignment; Intervention Party Assignment;
- **nineteen M:M join-table links:** every remaining accepted semantic adjacency.

Do not create duplicate join-table traversals beside the six object-backed contextual relationships. Required FK singularity is enforced by pipelines, Actions and function-side validation rather than cardinality labels alone. Hidden occurrence/Plant/Cash resources add only their necessary parent, actor, basis, scope, evidence and reversal links; they add no visible shortcuts.

## 4. Geospatial mechanism

Use:

- `geoshape` for Parcel and Official Area;
- `geopoint` for Individual Plant;
- upstream WGS84 normalization and geometry checks;
- incremental geospatial pipelines for Parcel–Area intersections and partial-overlap measures;
- Functions to combine spatial candidates with proposition, Instrument, subject, date, conflicts and more-specific outcomes.

Map supports Ontology object layers, point/polygon visualization, shape selection and geospatial Actions.[14][15]

Geometry produces a candidate premise. It never produces duty, competence, permission or applicability.

## 5. Derived-state mechanism

Owen accepts the full pipeline + deterministic model + live Function + Automate split below.

### Pipeline/backend layer

Precompute stable or population-scale components:

- complete opportunity population;
- Parcel–Area candidate intersections;
- proposition→decision dependency index;
- optimization inputs and large population aggregates;
- occurrence rollups needed by bounded Functions.

### Read Function layer

Keep the four exact Functions:

- Determine Affected Decisions;
- Assess Named-Action Readiness;
- Compare Feasible Intervention Portfolios;
- Determine Remaining Exposure.

Functions are server-side Ontology compute and can return typed structures, object sets and API query results.[6]

Use Functions for bounded live traversal and explanation. Do not load whole populations into arrays or reimplement batch processing per request.

Derived properties remain optional convenience. They are not a correctness dependency until enrollment availability and performance are measured.

### Accepted per-Function placement

- **Determine Affected Decisions:** incremental dependency/change pipelines preselect affected subjects/partitions; Automate triggers work; the live Function resolves current authority, conflicts, date and scope and returns affected/unaffected decisions with explanation.
- **Assess Named-Action Readiness:** live TypeScript v2 Function over exact current context; the mutating Action independently revalidates the refusal contract. Never materialize generic readiness.
- **Compare Feasible Intervention Portfolios:** pipelines prepare complete population and model inputs; a versioned deterministic optimizer/model performs constrained allocation; the Function returns current alternatives, constraints and sensitivity; Scenarios apply alternatives; AIP explains but never scores authoritatively.
- **Determine Remaining Exposure:** pipelines/backend aggregations roll up independently keyed occurrences; the live Function resolves bounded current legal, operational, financial and biological lines. Never materialize global completion.

Use derived properties only for cheap local counts and bounded summaries. Do not use them as the sole correctness mechanism for population-scale or cross-history answers.

## 6. Four Action implementations

Actions are single governed transactions with parameters, rules, criteria and side effects.[3]

Use actions-only editing. Direct open edits are not part of the CORDON write plane.

### Accept Cooperative Execution Mandate

Mechanism:

- exact function-backed Action when it updates Instrument authority and appends an Instrument Occurrence;
- explicit authenticated manager command required;
- exact current scoped authority re-resolved at apply time;
- Action log enabled.

Never creates member grant, eligibility, concession, capacity or creditor truth.

### Decide Cooperative Pursuit

Mechanism:

- function-backed Action targeting Cooperative Pursuit;
- append Pursuit Decision Record;
- validate member choice, mandate, Programme, scope, fallback and decision authority;
- explicit authenticated manager command required;
- Action log enabled.

### Commit or Rebalance Intervention Capacity

Mechanism:

- compare alternatives through Ontology Scenarios;
- persist the selected complete plan as a hidden Capacity Portfolio Proposal;
- let AIP explain scenario consequences, proposal diff, policy, protected Commitments, override reason and current-state fingerprint in the conversation;
- treat the authenticated manager's explicit commit/rebalance prompt as the human decision;
- apply through one TypeScript v2 staged-write function-backed Action;
- one complete edit batch over all affected Commitments;
- shared portfolio-decision reference;
- server-side complete-set and stale-premise validation;
- hard default ceiling of 10,000 edited objects;
- explicit authenticated manager command required;
- one portfolio Action log plus Commitment Change Records.

The hidden Capacity Portfolio Proposal stores the selected Scenario, complete affected set, proposed Commitment edits, policy/recommendation version, protected Commitments, current-state fingerprint, comparison/evidence summary and expiry/invalidation condition. AIP prepares it. The manager's explicit conversational command selects it and invokes the exact Action. The command binds to the proposal, Action version, target set and fingerprint without a separate approval-popup step.

Never split an oversized atomic decision into unordered Actions. If a real portfolio exceeds the envelope, reopen decision grain or use an explicit two-phase protocol.

### Dispatch Intervention

Mechanism:

- function-backed Action;
- fresh readiness/authority validation;
- append bounded Intervention dispatch occurrence;
- optional real work-order Instrument creation;
- explicit authenticated manager command required;
- Action log enabled.

Never writes performance, acceptance or establishment.

## 7. AIP harness

### Direct conversational execution bar

Owen sets the product bar from a real Palantir common-operating-picture demonstration: an AIP Chatbot is embedded with the operating picture, understands natural-language operator intent at high accuracy and directly executes exact Ontology Actions. The product must not feel like a coding agent that asks for generic tool approval.

For an authenticated manager-owned Action, a clear prompt such as `Dispatch Intervention` is the human decision. AIP resolves the exact target/scope, runs the accepted read Functions, invokes the exact Action and executes directly when all platform and function guardrails pass. No redundant confirmation modal is required.

Direct execution remains bounded by caller permissions, current Scoped Party Assignment, submission criteria, fresh function-side authority/readiness checks, exact Action effects, idempotency and audit. Automatic execution means frictionless governed operation, not autonomous invention of authority.

AIP requests clarification—not approval—when target, scope, authority, date, reason or consequence is ambiguous. Scenario comparison is used when alternatives materially improve the decision, especially capacity allocation. Human review occurs at real actor/authority boundaries or when policy explicitly requires it; it is not universal approval-popup UX.

AIP Chatbot Studio provides six tool classes: Action, object query, Function, application-variable update, command and clarification.[7]

Expose only:

### Read tools

- four exact Functions;
- curated object-query access to the accepted graph and minimum basis references;
- request clarification.

### Write tools

- four exact manager Actions;
- direct execution from an explicit, unambiguous prompt by the authenticated authorized manager;
- no generic object edit, history append, status update, external-outcome recording or arbitrary Action tool.

AIP may:

- retrieve;
- explain;
- compare;
- prepare exact parameters;
- stage proposals;
- route to the current real owner;
- reconcile authenticated received outcomes.

AIP may not:

- manufacture member/professional/private/public/bank decisions;
- use an automation owner as domain authority;
- parallelize mutating tools;
- convert recommendation into commitment;
- infer law from geometry;
- infer cash from order;
- infer establishment from acceptance.

Command tools can drive paired application state and require approval by default, but command configuration is beta and Gate 7 has not selected an application.[8]

## 8. Safe decision loop

```text
explicit authenticated operator command
→ read current graph and authenticated occurrences
→ run exact read Function(s)
→ resolve exact Action, target, scope and parameters
→ revalidate all refusal premises
→ apply one exact Action atomically
→ write factual occurrence + Action log
→ recompute affected decisions, readiness and exposure
→ route next bounded handoff
```

When the prompt is ambiguous, AIP asks a clarifying question before the Action. When the decision belongs to another actor, AIP prepares/routes rather than executes. When alternatives materially matter, AIP uses Functions and Scenarios before the manager issues the final command.

Ontology Scenarios can sandbox Actions and compare consequences before main writes. They are available in this enrollment; beta maturity affects implementation testing, not availability or domain approval.[10]

## 9. Automate

### Accepted autonomy policy

Owen accepts direct conversational execution and separates it from background autonomy:

- when the authenticated manager explicitly commands one of the four Actions, AIP executes directly after guardrails pass;
- when no manager is actively commanding the Action, AIP/Automate detects, recomputes, prepares, routes and notifies but does not execute the manager Action in the initial release.

Background Action autonomy is granted later Action-by-Action only after Evals, target/parameter accuracy, authority behavior, idempotency, reversal, production correction rate, observability and kill controls meet an explicit policy bar.

Automate supports time/object conditions and effects that invoke Actions, Functions, AIP Logic or notifications.[9]

Safe initial uses:

- detect material changes;
- invoke selective impact Functions;
- trigger bounded pipeline recomputation;
- notify current owner;
- stage a proposal;
- run read Functions;
- route authenticated outcomes;
- execute fallback effects.

Unsafe initial uses:

- infer or execute a manager Action without a clear authenticated operator command or an explicit later autonomy policy;
- chain several Actions while assuming order;
- treat automation-owner identity as fresh human approval.

## 10. External outcome ingestion

Owen accepts one authenticated, idempotent occurrence-ingestion contract across all external outcomes. Source adapters may differ; identity, authority, correction, reversal and reconciliation semantics do not.

Use:

- Data Connection sync for pull sources;
- public API when the producer is customizable;
- GA HTTPS listeners for push sources that need provider-specific signing;
- streams plus pipeline validation/deduplication;
- outbound writeback webhooks only when an external system must accept before Ontology edits;
- side-effect webhooks only for best-effort post-edit synchronization.

Listeners are inbound only and produce low-latency stream events. WebSocket and email listener variants remain experimental/beta; HTTPS is the baseline.[13]

Every authoritative outcome uses an idempotent envelope:

- source system;
- stable source occurrence ID;
- source version;
- authority actor/reference;
- subject grain;
- consequential time;
- received time;
- bounded outcome;
- evidence/media references;
- supersedes/reverses ID;
- idempotency key;
- ingestion/reconciliation result.

Immutable raw payload stays backstage.

Required failure cases are duplicate replay, late arrival, correction, supersession, reversal, partial cash, unmatched cash, external success followed by Ontology failure, unavailable source, invalid signature and identity conflict. No generic Record Result, Mark Paid, Mark Accepted or model-confidence truth-writing Action enters the harness.

## 11. Assurance

### Action-execution model program

The target is a high-accuracy action-execution model embedded in the operating picture, not a generic chat assistant.

Use this closed loop:

1. **Define exact trajectories in AIP Evals.** Each case contains operator prompt, current Ontology/application context, expected clarification or exact tool, exact target, parameters, expected edits/outcome and prohibited implications. Use manual and object-set-generated test cases.
2. **Generate and execute interaction data in AIP Evals.** Edit-producing cases run in Ontology simulations, preventing live mutation. Repeated runs, model comparisons and traces produce prompt→tool→target→parameters→simulated-edits trajectories.[19]
3. **Evaluate safely.** Custom evaluators score exact tool selection, target, parameters, edited objects, clarification, abstention and prohibited effects. Review and curate cases/results before they become training data.[19]
4. **Train/tune.** Train or fine-tune an open-source model in a Foundry Model Training repository or Code Workspace using the curated trajectories. Publish the model with `palantir_models` adapters and versioned lineage.[18][20]
5. **Register in AIP.** Use registered/BYOM model support so the tuned model is available in AIP Chatbot Studio, AIP Logic, Workshop and TypeScript Functions with model selection, permissions, rate limits and observability.[17]
6. **Compare against strong baselines.** Run the same Evals suite against Palantir-provided and tuned models. The tuned open-source model is the required production model; hosted models are benchmark comparators. Launch is blocked until the tuned model meets every Action-accuracy and refusal bar.
7. **Learn from production.** Feed corrected prompts, clarifications, Action refusals, overrides and observed outcomes into a reviewed trajectory set. Production logs remain untrusted training candidates until curated.

Required metrics:

- exact Action/tool selection;
- exact target resolution;
- exact parameter construction;
- clarification when ambiguity is material;
- contextual authority compliance;
- no reserved-decision fabrication;
- no generic edit or unapproved tool use;
- Action success after guardrail validation;
- zero recommendation→commitment, order→cash, acceptance→establishment and geometry→law errors;
- task completion latency and operator correction rate.

The fine-tuned open-source model may execute the four exact manager Actions directly when the authenticated manager's prompt is explicit and guardrails pass. It never bypasses Action permissions, submission criteria, function-side validation or factual histories.

Playwright is not required for trajectory generation. Keep it only as an optional Gate 7 end-to-end interaction regression tool. The prior HAR/CDP/static-API method remains an optional builder acceleration for deterministically authoring AIP Logic, Pipeline Builder or Eval configurations when canvas operations are inefficient; it is not the learning-data source.

### Action logs, receipts and supplemental edit history

Enable one Action log per manager Action. Action logs become `[LOG]` object types linked to edited objects and record invocation context.[4]

Enable OSv2 user edit history on all Action-edited types as supplemental audit. Define activation date, permission-bound access and retention. Keep it backstage and separate from typed domain occurrences, Action logs and durable execution receipts. It records object edits, not datasource changes or domain meaning, and never becomes an operator timeline or factual history.[5]

Neither replaces domain occurrence records.

### AIP Evals

Use AIP Evals for:

- correct tool selection;
- abstention and clarification;
- authority refusal;
- complete parameter construction;
- evidence-grounded explanation;
- no geometry→law inference;
- no recommendation→commitment collapse;
- no order→cash inference;
- no acceptance→establishment inference.

AIP Evals supports test cases, evaluation criteria, model comparison and variance analysis.[11]

### AIP observability

Use Workflow Lineage/AIP observability for:

- metrics;
- execution history;
- distributed traces;
- prompts/tool calls/token use;
- service logs and log search;
- production latency/failure/drift analysis.[12]

Observability is telemetry, not durable domain history.

## 12. OSDK/API capability

OSDK React can query objects, object sets, links and aggregations, apply and validate Actions, call Functions, track dependencies and synchronize affected cached objects after Actions.[16]

Gate 6 therefore supports a custom operational application without choosing one now.

The eventual application can use:

- validate-only Action preflight;
- exact Action apply under caller identity;
- typed Function calls;
- cached object/link traversal;
- AIP Chatbot integration through platform APIs or OSDK.

Consumer Mode public applications cannot host the full mapped harness where function-backed Actions and Function execution are unsupported. This is a Gate 7 exclusion, not a current surface choice.

## 13. Capability posture

### Confirmed live or confirmed by Owen

- non-default Ontology;
- OSv2 datasetV2/edit-only properties;
- typed links;
- function-backed Actions;
- human-confirmation Action pattern;
- Action-log types;
- current LLM and embedding Functions;
- Transform/Funnel/webhook project services.
- full TypeScript v2 staged writes;
- AIP Chatbot Studio and AIP Logic;
- Automate and proposal/human-review workflows;
- Ontology Scenarios;
- derived properties and reducers;
- Checkpoints;
- Restricted Views, markings and edit policies;
- AIP Evals and observability.

Source-specific credentials and external-system transaction contracts remain integration facts to research, not enrollment capability limits.

## 14. Existing-project isolation

The existing `CORDON-Wedge-1` project contains 25 historical resources, including old object/link/action metadata, sources, repositories and notes. Its description still names the rejected eligibility/collective-application engine.

Owen accepts this isolation rule:

- do not build the accepted Ontology into the historical project;
- create a new clean Foundry project and Global Branch;
- never repair old metadata into the new model;
- preserve the old project as historical evidence; delete/archive it later only under explicit Owen approval;
- keep Connor read-only; any eventual Foundry write remains a later authorized Ferro task.

The enrollment's non-default Ontology remains shared with unrelated project types. The clean project/branch establishes CORDON resource, repository and governance isolation. New API names must be explicit, and AIP object-query context must include only accepted CORDON types and minimum backstage resources.

## Binding production contracts required before closure

The mechanism-purpose adversarial audit identifies eight production contracts. They constrain already-accepted mechanisms and add no domain type, Action, Function, workflow lane or surface.

### Contract 1 — data assurance and indeterminate behavior

Every authoritative source and derived decision dataset has a binding assurance row:

- owner and alert route;
- expected cadence and freshness SLO;
- schema, qualified-key, FK, cardinality, null/domain, row/volume, conservation, authority-envelope, geometry and deduplication expectations as applicable;
- last accepted source and indexed-object watermarks;
- raw accepted/rejected and source→object conservation counts;
- quarantine and replay policy;
- last-good behavior;
- exact Q1–Q6 answers invalidated by failure.

Build-blocking Data Expectations reject malformed outputs. Data Health monitors source, schedule, stream, Function, Action, Automate and object/index liveness. A failed load, stale source, index rejection or unresolved conservation gap makes dependent Function answers `INDETERMINATE`; it never silently reuses last-good data as current truth. Manager Actions refuse when an invalidated premise is load-bearing.

### Contract 2 — dual lineage

Maintain two distinct backstage traversals:

1. **Fact lineage:** authoritative source → immutable raw payload → validation/reconciliation → canonical fact/occurrence/link dataset → Ontology datasource/object/property.
2. **Execution lineage:** originating prompt/trigger → retrieval/context → Function/model/tool → exact Action/refusal → factual occurrence → selective recomputation/handoff.

Data Lineage owns fact provenance and downstream data dependency. Workflow Lineage/AIP observability owns runtime execution. Operator explanations show only the minimum cited basis, health/as-of state and consequential execution receipt; they do not expose engineering graphs by default.

### Contract 3 — single-owner computation kernels

- The pipeline-owned candidate dependency relation is the sole complete-population source of affected-decision candidates.
- Automate only triggers from changed keys and routes outputs.
- `Determine Affected Decisions` filters candidates against current date, scope, authority and conflicts, then explains affected and explicitly unaffected decisions. It does not independently rediscover the population.
- Each manager Action has one versioned, deterministic, side-effect-free prerequisite kernel.
- `Assess Named-Action Readiness` calls the applicable kernel for explanation.
- The mutating Action calls the same kernel on fresh state and fails closed.
- Submission criteria retain only non-duplicative platform gates: caller/apply permission, parameter presence, obvious target state, execution context and required reason.

Each answer and receipt includes policy/kernel version and premise fingerprint.

### Contract 4 — replay-safe direct-execution binding

Direct conversational execution requires one machine-checkable binding:

- authenticated principal;
- immutable originating message ID;
- exact Action type and version;
- exact target IDs or Proposal ID;
- target count and bounded consequence/material-delta summary;
- current premise fingerprint;
- single-use idempotency key;
- expiry/invalidation condition;
- at most one mutating tool per conversational turn.

Deictic language or changed application context forces clarification. The model cannot retry a mutation after an uncertain response. The Action deduplicates and returns a durable receipt with exactly one result: `COMMITTED`, `ALREADY_COMMITTED`, `REFUSED`, or `CLARIFICATION_REQUIRED`. A committed receipt remains retrievable when natural-language response generation fails.

### Contract 5 — one executable proposal truth

Ontology Scenarios are disposable comparison workspaces. They may contain alternatives but never become executable truth.

After the manager selects an alternative, one immutable Capacity Portfolio Proposal becomes the sole executable digest. It stores:

- Proposal ID and originating Scenario/version;
- complete target-set hash;
- exact Commitment deltas;
- policy, optimizer and model versions;
- protected Commitment set;
- current premise fingerprint;
- expiry/invalidation rule;
- bounded explanation and material consequence summary.

The capacity Action accepts only Proposal ID plus the direct-execution idempotency token, loads the plan server-side and revalidates it. It does not accept a second client-supplied edit plan.

### Contract 6 — common transport envelope plus typed authority admission

All external outcomes share only the technical envelope:

- source system and stable occurrence ID/version;
- received time;
- raw evidence pointer/hash;
- idempotency key;
- supersedes/reverses pointer;
- reconciliation result.

Six authority-family profiles then define what makes the outcome admissible:

1. legal/public;
2. member/beneficiary;
3. professional;
4. contractual/field;
5. biological;
6. bank/treasury.

Each profile names authentication, competence resolution, subject grain, effective/consequential-time rule, ordering/correction semantics, required evidence, reconciliation owner and failure state. A common adapter may transport all six families; no lowest-common-denominator validator may admit them.

### Contract 7 — compatible release and recovery

Every releasable CORDON version has one compatibility manifest that pins:

- Ontology object/link/property/API versions;
- backing dataset schemas and Data Expectations;
- pipeline/optimizer/model inputs and versions;
- read Function packages/tags and response schemas;
- Action versions, prerequisite-kernel versions and submission criteria;
- Chatbot, AIP Logic, prompt, retrieval and tool-schema versions;
- tuned open-source model/BYOM registration version;
- AIP Evals suite, locked holdout and accepted result;
- Automate/schedule versions;
- source bindings and required environment configuration.

Promote development → test → production through Foundry DevOps/release management. The manifest defines migration order, compatibility checks, smoke cases for all four reads/four writes, release owner, rollback target, non-reversible migration limits and incident path. Global Branching isolates changes inside an environment; it does not replace release environments or rollback.

Marketplace/fleet distribution remains rejected until a second installation creates a real consumer.

### Contract 8 — open-source model lifecycle, minimization and promotion

The fine-tuned open-source model remains the required production model. Hosted models are benchmark comparators, not production fallbacks. Launch waits until the tuned model passes this contract:

- training/validation/test/locked-holdout splits are disjoint by operator, Holding/farm, object/Proposal, time and conversation family;
- paraphrases and shared object IDs cannot leak across splits;
- Italian/local terminology, code-switching, misspellings, terse/deictic commands, hard one-premise negatives, out-of-distribution entities, stale/unavailable tools, changed Action schemas and prompt injection are represented;
- subgroup worst-case results cover operator role, geography, route and Action class;
- label guidance, inter-annotator agreement and adjudication are recorded;
- repeated-run variance and calibrated clarification/abstention are measured;
- AIP Evals Ontology simulations and deterministic evaluators score exact tool, target, parameters, edits, clarification, abstention, durable receipt and prohibited implications;
- model-training experiment, data, code, seed, prompt, tool-schema and model versions are reproducible;
- retrieval, telemetry and training use an explicit property allowlist, marking/purpose enforcement, redaction, retention and geography/provider policy;
- production trajectories are independently re-authorized, minimized, de-identified, adjudicated and deduplicated before training;
- shadow/canary, drift indicators, rollback triggers and the previous accepted tuned-model version are defined.

Safety is a hard Boolean gate. Aggregate quality, cost or latency never compensates for one unauthorized Action, wrong target, wrong edit, reserved-decision fabrication, recommendation→commitment, order→cash, acceptance→establishment or geometry→law failure.

### Channel-neutral Gate 7 boundary

Conversational direct execution is a required ingress mode, not a preselected navigation or screen architecture. Every Gate 7 candidate must supply the same channel-neutral binding: authenticated principal, exact selected context, premise fingerprint, read Function results, optional Proposal reference and durable Action receipt.

Map capability is admitted where spatial orientation or target selection changes Q1–Q4. It is not automatically the product home. Application state and Commands remain Gate 7 configuration choices.

### Production indicators

Operate six indicator families, each with threshold, owner, alert route, runbook and degraded behavior:

1. authoritative-source freshness and quarantine;
2. source→curated→Ontology conservation and indexing liveness;
3. Function success, indeterminate rate and P95 latency;
4. Action success/refusal/duplicate/concurrency rates;
5. Chatbot clarification, wrong-target, correction and prohibited-effect rates;
6. end-to-end command→receipt latency and receipt-recovery failures.

Telemetry remains backstage and never creates domain truth or training labels automatically.

## 15. Gate 6 decision register

1. **Accepted:** six hidden occurrence types plus hidden Intervention Plant Scope.
2. **Accepted:** six focused hidden object-backed contextual relationship types.
3. **Accepted:** Scenarios + hidden Capacity Portfolio Proposal + explicit manager command + TypeScript v2 staged-write Action.
4. **Accepted interaction invariant:** direct conversational execution for explicit authorized manager commands; clarification on ambiguity; contextual human review only at real decision boundaries.
5. **Accepted autonomy policy:** initial background AIP/Automate prepares/routes only; background Action execution expands later from evidence.
6. **Accepted:** Scenario integration for safe what-if comparison and conversational decision handoff.
7. **Accepted:** seven FK + six object-backed contextual + nineteen M:M join-table physical link map. Holding→Parcel uses the Parcel-side current-Holding FK because D10 Q5i proves and enforces that one current Parcel is not reused across current Holdings.
8. **Accepted:** pipeline + deterministic model + live Function + Automate compute boundary.
9. **Accepted:** new clean Foundry project and Global Branch; preserve old project as historical.
10. **Accepted:** universal authenticated/idempotent occurrence contract; source-specific connection, credential and transaction proof remains per-integration work.
11. **Accepted:** enable OSv2 user edit history on all Action-edited types as supplemental backstage audit; never domain truth or operator timeline.
12. **Accepted:** no initial Checkpoints; admit only for a named policy requirement not met by command reason, occurrence, Action log and receipt.

## 16. Current recommendation

Adopt the mechanism architecture above.

The only semantic reopening is physical:

- hidden typed occurrences replace parent-local history arrays;
- hidden typed authority facts replace embedded contextual role structs;
- Plant phase and cash identity receive focused hidden records.

Do not reopen:

- the nine operator objects;
- Cooperative Pursuit or Capacity Commitment;
- the 32 semantic links;
- the four manager Actions;
- the four read Functions;
- authority boundaries;
- route/result separations;
- the no-global-status rule.

The complete mechanism-purpose ledger covers every relevant Foundry/AIP capability, its role in the six-question operator loop, authority boundary, operator-visible/backstage posture, overlap, disposition and production contract. The adversarial correction set is incorporated. Owen accepts and closes Gate 6. Gate 7 operator-surface comparison is open.

## Sources

[1] https://www.palantir.com/docs/foundry/architecture-center/aip-architecture
[2] https://www.palantir.com/docs/foundry/object-link-types/create-link-type
[3] https://www.palantir.com/docs/foundry/action-types/overview
[4] https://www.palantir.com/docs/foundry/action-types/action-log
[5] https://www.palantir.com/docs/foundry/object-edits/user-edit-history
[6] https://www.palantir.com/docs/foundry/functions/overview
[7] https://www.palantir.com/docs/foundry/chatbot-studio/tools
[8] https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools
[9] https://www.palantir.com/docs/foundry/automate/overview
[10] https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario
[11] https://www.palantir.com/docs/foundry/aip-evals/overview
[12] https://www.palantir.com/docs/foundry/aip-observability/overview
[13] https://www.palantir.com/docs/foundry/data-connection/listeners-overview
[14] https://www.palantir.com/docs/foundry/map/overview
[15] https://www.palantir.com/docs/foundry/map/integrate-actions
[16] https://www.palantir.com/docs/foundry/ontology-sdk-react-applications/osdk-react
[17] https://www.palantir.com/docs/foundry/aip/bring-your-own-model
[18] https://www.palantir.com/docs/foundry/integrate-models/model-asset-code-repositories
[19] https://www.palantir.com/docs/foundry/aip-evals/ontology-edits
[20] https://www.palantir.com/docs/foundry/model-integration/getting-started

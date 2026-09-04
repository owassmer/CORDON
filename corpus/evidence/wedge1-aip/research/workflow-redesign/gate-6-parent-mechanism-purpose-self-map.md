# Gate 6 — parent mechanism-purpose self-map

Status: **INDEPENDENT PARENT LANE — reconciliation input, not authority**
Date: 22 August 2026

## Test

A mechanism enters only when it has one distinct purpose in the accepted operator loop. A documented capability with no distinct operator effect is rejected or deferred. Multiple mechanisms may cooperate on one decision, but one mechanism owns each job.

## MECE mechanism taxonomy

1. Acquire external facts.
2. Preserve and model truth.
3. Derive decision-ready state.
4. Compare alternatives.
5. Execute bounded decisions.
6. React and route.
7. Converse and orchestrate with AI.
8. Assure, learn and operate the product.

## 1. Acquire external facts

| Mechanism | CORDON purpose | Trigger | Output | Posture | Decision effect |
|---|---|---|---|---|---|
| Data Connection batch/incremental sync | Pull authoritative tables/files/APIs | schedule or source refresh | immutable raw version + sync metadata | **Required backstage** | Q1 changed facts; all downstream state |
| CDC sync | Receive ordered source changes where database log exists | source transaction | changelog stream | **Conditional per source** | faster selective recomputation |
| Public API push | Receive customizable producer events | source system call | authenticated event/data transaction | **Required option** | external outcomes and corrections |
| HTTPS listener | Receive signed provider-specific webhooks | provider push | stream event | **Required option** | low-latency notices/outcomes |
| WebSocket listener | Persistent bidirectional events | live connection | compute-module stream | **Reject initially** | no accepted high-frequency bidirectional need |
| Email listener | Receive email-only outcomes | inbound email | media item | **Conditional** | only where no stronger source exists |
| External Function | Custom API call/normalization | pipeline/function request | typed response | **Conditional** | source-specific integration |
| Outbound writeback webhook | Execute real external transaction before Ontology edit | authorized Action | external acknowledgement + outputs | **Conditional, transactional** | only when CORDON is real channel |
| Post-edit webhook/notification | Synchronize after accepted Action | Action success | best-effort external side effect | **Conditional** | handoff; never source of Action truth |

Data Connection standardizes connection/version/lineage while leaving domain mapping downstream.[21]

## 2. Preserve and model truth

| Mechanism | CORDON purpose | Output | Posture | Boundary |
|---|---|---|---|---|
| Raw datasets/media | Preserve payload and evidence unchanged | immutable raw artifact | **Required backstage** | not operator state |
| Curated current datasets | Resolve source grain and current authoritative facts | typed current rows | **Required backstage** | no CORDON-owned edits |
| OSv2 visible object types | Expose 11 operator fact owners | objects/properties | **Required visible** | no generic status |
| Hidden occurrence types | Preserve independent history facts | six typed occurrence populations | **Required hidden** | no generic Event |
| Hidden contextual relationships | Preserve scope/date/basis authority | six object-backed relationships | **Required hidden** | Party remains identity-only |
| Hidden Intervention Plant Scope | Preserve phase-specific Plant truth | fact-bearing scope records | **Conditional with Plant population** | direct link remains adjacency |
| Capacity Portfolio Proposal | Preserve selected scenario/edit package/fingerprint | technical proposal | **Required hidden** | manager prompt is decision, proposal is not |
| FK links | Enforce six current singular endpoints | typed traversal | **Required** | uniqueness separately enforced |
| M:M join links | Preserve metadata-free adjacency | 20 join-table links | **Required** | no duplicate shortcuts |
| Object-backed links | Preserve relationship metadata + concise traversal | Pursuit, Commitment, six context facts | **Required** | detailed and direct are one truth |
| Source-backed properties | Preserve source-owned current truth | indexed properties | **Required** | Action cannot manufacture external truth |
| Edit-only properties | Preserve CORDON-owned Action effects | indexed writeback state | **Required selectively** | manager-owned facts only |
| Media references | Link evidence without embedding payload | governed media pointer | **Required where evidence exists** | not generic Evidence object |
| Materialization | Produce merged source+edit current dataset for downstream use | latest-state dataset | **Conditional** | not history; latency accepted[22] |
| User edit history | Extra object-level before/after audit | platform edit trail | **Required on Action-edited types, backstage** | never external/domain history or operator timeline |
| Action logs | Preserve Action submission context | four generated log types | **Required audit** | not domain occurrence[4] |

Media references support governed media without inflating ordinary properties.[23]

## 3. Derive decision-ready state

| Mechanism | Purpose | Trigger | Output | Posture |
|---|---|---|---|---|
| Pipeline Builder/transforms | Normalize, join, dedupe, spatially intersect, calculate populations | source/occurrence changes | curated datasets and candidate relations | **Required** |
| Data Expectations | Reject malformed, incomplete, duplicate or inconsistent data | every build | build pass/fail | **Required** |
| Backstage dependency index | Map proposition/scope/time to dependent decisions | Gate 5 dependency contract | dependency rows | **Required** |
| Backend aggregation | Compute scalable occurrence/population rollups | data change | bounded aggregates | **Required** |
| Derived properties | Cheap local linked counts/summaries | query | live convenience value | **Required selectively** |
| Determine Affected Decisions | Resolve live impact and unaffected work | material change/operator request | typed impact result | **Required Function** |
| Assess Named-Action Readiness | Resolve one Action's current premises | prompt/preflight/Action apply | typed readiness result | **Required Function** |
| Determine Remaining Exposure | Reconcile independent result lines | outcome/operator request | typed exposure result | **Required Function** |
| AIP retrieval/object query | Retrieve only allowed decision context | operator prompt | selected objects/evidence | **Required AIP tool** |
| Semantic/hybrid search | Find relevant Instrument/evidence text | legal/evidence question | ranked references | **Conditional but high-value** |

Functions remain bounded live logic; pipelines own population-scale computation.[6]

## 4. Compare alternatives

| Mechanism | Purpose | Output | Posture |
|---|---|---|---|
| Deterministic optimizer/model | Solve capacity constraints/objective | candidate portfolios | **Required** |
| Compare Feasible Intervention Portfolios | Present current alternatives/constraints/sensitivity | typed comparison | **Required Function** |
| Ontology Scenarios | Apply alternative Actions without main writes | isolated scenario state | **Required for capacity/what-if** |
| Capacity Portfolio Proposal | Persist selected plan and current fingerprint | exact staged package | **Required** |
| LLM | Explain and interrogate alternatives | natural-language explanation | **Required supporting role** |
| AIP Analyst | Ad hoc autonomous analysis | analysis/visuals | **Optional operator-adjacent** |

Scenarios are for what-if edits and comparison, not historical versioning or domain approval.[10]

## 5. Execute bounded decisions

| Mechanism | Purpose | Output | Posture |
|---|---|---|---|
| Accept Mandate Action | Cooperative acceptance/refusal | Instrument occurrence + authority context | **Required** |
| Decide Pursuit Action | Pursue/defer/refuse | Pursuit state/history | **Required** |
| Capacity staged-write Action | Atomic full-set Commitment edits | Commitments/change records | **Required** |
| Dispatch Action | Bounded executor handoff | dispatch occurrence/work-order | **Required** |
| TSv2 staged writes | Atomic multi-edit/read-after-write | one committed transaction | **Required where Action multi-object** |
| Submission criteria | Coarse caller/parameter/main-vs-scenario gates | platform refusal | **Required** |
| Function-side validation | Exact current authority/scope/readiness/atomicity | edits or refusal | **Required** |
| Checkpoints | Contextual acknowledgement/justification where policy demands | justification record | **Conditional** |
| Action permissions/actions-only mode | Limit callable verbs/direct-edit bypass | enforced access | **Required** |
| OSDK/API Action invocation | Execute exact Actions from application/chatbot | governed edit response | **Required** |

Actions are the governed operational verb and share logic across applications.[3] Checkpoints support contextual governance, not universal confirmation UX.[26]

## 6. React and route

| Mechanism | Purpose | Trigger | Output | Posture |
|---|---|---|---|---|
| Automate live/scheduled conditions | Detect changes and initiate response | object/time condition | effect run | **Required** |
| Function effect | Recompute/explain | Automate trigger | typed result | **Required** |
| Pipeline/schedule effect | Heavy affected-partition rebuild | material change | rebuilt current projections | **Required** |
| Notification effect | Route bounded handoff | result/action | message | **Required selectively** |
| Fallback effect | Handle failed primary effect | execution failure | retry/route/error state | **Required** |
| Asynchronous AIP proposal | Prepare decisions without owner present | detected opportunity | proposal/package | **Conditional** |
| Automatic manager Action | Apply Action without direct prompt | policy trigger | mutation | **Deferred policy question** |

Automate owns reaction/orchestration, not domain authority.[9]

## 7. Converse and orchestrate with AI

| Mechanism | Purpose | Output | Posture |
|---|---|---|---|
| AIP Chatbot Studio | Embedded conversational operator | answer/tool calls | **Required runtime** |
| Curated object query | Give model minimum live context | object set/aggregates | **Required tool** |
| Function tools | Invoke four exact read Functions | typed answer | **Required tools** |
| Action tools | Execute four exact manager Actions | governed mutation | **Required tools** |
| Request clarification | Resolve ambiguous target/scope/authority/date | user answer | **Required tool** |
| Application state | Ground selected map objects/filter/jurisdiction | scoped context | **Required capability; surface deferred** |
| Commands | Navigate/manipulate paired application state | map/app operation | **High-value; Gate 7 config** |
| AIP Logic | Compose retrieval, extraction, Functions and Action parameters | tool orchestration | **Required** |
| Direct conversational execution | Treat explicit authorized prompt as manager decision | immediate exact Action | **Required interaction invariant** |
| BYOM/registered model | Deploy tuned open-source action-execution model across AIP | production model | **Required production path** |

Chatbot tools support Actions, object queries, Functions, application variables, commands and clarification.[7] Commands can manipulate paired application context but are a Gate 7 surface mechanism.[8]

## 8. Assure, learn and operate

| Mechanism | Purpose | Output | Posture |
|---|---|---|---|
| AIP Evals Ontology simulations | Generate/replay prompt→tool→parameter→simulated-edit trajectories | curated cases, results and traces | **Required learning harness** |
| Model Training repository / Code Workspace | Fine-tune open-source model | versioned weights/model | **Required target capability** |
| Model adapter + BYOM registration | Deploy tuned model across AIP products | registered model | **Required** |
| AIP Evals | Simulated Action and reasoning tests | pass/fail/metrics/traces | **Required** |
| Custom Ontology-edit evaluators | Score exact tool, target, parameters and edits | Boolean/numeric metrics | **Required** |
| AIP Evolve | Search model/prompt/cost improvements against Evals | reviewed proposal | **High-value after baseline** |
| HAR/CDP static API client | Deterministically author platform graph/config resources when canvas operations are inefficient | static API calls/configuration | **Optional builder accelerator** |
| Playwright | End-to-end application interaction regression | UI regression traces | **Optional Gate 7 test tool; not training source** |
| AIP observability | Trace model, tool, Action, Function and Automate runtime | metrics/traces/logs | **Required** |
| Workflow Lineage | Understand full runtime dependency graph | lineage graph | **Required** |
| Data Lineage | Understand source→pipeline→Ontology provenance | lineage graph | **Required** |
| Health checks | Monitor connectors/pipelines/resources | alerts/reports | **Required** |
| Log export | Analyze production behavior and create curated training candidates | streaming telemetry | **Required** |
| Global Branching | Isolate development/review | branch/proposal | **Required** |
| Foundry DevOps/package/release | Version/deploy the end-to-end product | release artifacts | **Required before build completion** |
| AI FDE | Build/refactor/test platform assets | development changes | **Required builder aid, not runtime** |
| Palantir MCP | External agent development/read inspection | developer tool calls | **Required builder aid, not runtime** |

AIP Evals runs edit-producing test cases in Ontology simulations and supports custom Boolean/numeric evaluators.[11][19] BYOM makes tuned models available across Chatbot Studio, AIP Logic, Workshop and TS Functions.[17] Global Branching and DevOps isolate and release the product.[24][25] Workflow Lineage and health tools operate the platform rather than model domain truth.[27][28]

## Complete operational loop

```text
source sync / listener / API / manager prompt
→ immutable raw landing
→ validation, identity, occurrence mapping
→ curated current facts + hidden occurrence/context records
→ incremental spatial/population/dependency computation
→ Automate detects affected decision
→ four Functions compute impact/readiness/alternatives/exposure
→ AIP retrieves, explains, clarifies and selects exact tool
→ explicit authorized manager prompt
→ exact TSv2 Action validates and writes atomically
→ factual occurrence + Action log + durable receipt
→ recompute and route next handoff
→ observability + Evals + operator corrections
→ reviewed trajectory corpus
→ model/prompt fine-tune/evolve
→ registered model release
→ improved next decision
```

## Rejected or bounded mechanisms

- Generic Event, Case, Task, Status, Queue or Handoff object: rejected.
- Generic edit/history/execute-anything AIP tool: rejected.
- LLM legal authority, optimizer or external-truth writer: rejected.
- Action log/edit history as domain occurrence: rejected.
- Time series for legal/financial occurrences: rejected.
- Map overlap as legal applicability: rejected.
- Materialization as history: rejected.
- Consumer Mode public application as full runtime: rejected due harness capability mismatch.
- AIP Assist, AIP Analyst, AI FDE and MCP as substitutes for the task-specific runtime Chatbot: rejected.
- Full legal corpus or evidence payload as visible Ontology: rejected.
- Playwright as the primary training-trajectory generator: rejected; AIP Evals owns simulated Action trajectories and curation.
- Hosted model as production fallback: rejected; hosted models remain benchmarks and launch waits for the tuned open-source model to clear hard Evals.
- Automatic background manager Actions: deferred until a separate autonomy policy is accepted.

## Self-verdict

The mechanism set is complete only if every accepted capability has one owner in the taxonomy above and no layer silently performs another's job. The largest remaining alignment questions are:

1. which mechanisms are operator-visible versus invisible at Gate 7;
2. the exact autonomy policy beyond direct authenticated prompts;
3. AIP model-training dataset acquisition and promotion bars;
4. release packaging and operational health acceptance criteria;
5. whether any capability exists only to demonstrate platform breadth and should be cut.

## Sources

[3] https://www.palantir.com/docs/foundry/action-types/overview
[4] https://www.palantir.com/docs/foundry/action-types/action-log
[6] https://www.palantir.com/docs/foundry/functions/overview
[7] https://www.palantir.com/docs/foundry/chatbot-studio/tools
[8] https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools
[9] https://www.palantir.com/docs/foundry/automate/overview
[10] https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario
[11] https://www.palantir.com/docs/foundry/aip-evals/overview
[17] https://www.palantir.com/docs/foundry/aip/bring-your-own-model
[19] https://www.palantir.com/docs/foundry/aip-evals/ontology-edits
[21] https://www.palantir.com/docs/foundry/data-connection/overview
[22] https://www.palantir.com/docs/foundry/object-edits/materializations
[23] https://www.palantir.com/docs/foundry/object-link-types/base-types
[24] https://www.palantir.com/docs/foundry/global-branching/overview
[25] https://www.palantir.com/docs/foundry/devops/overview
[26] https://www.palantir.com/docs/foundry/checkpoints/overview
[27] https://www.palantir.com/docs/foundry/workflow-lineage/overview
[28] https://www.palantir.com/docs/foundry/health-checks/overview

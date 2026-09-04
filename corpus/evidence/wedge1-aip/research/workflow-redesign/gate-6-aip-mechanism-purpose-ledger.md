# Gate 6 — AIP/decision/learning mechanism-purpose ledger

Status: **GATE 6 DECISION ARTIFACT — mechanism purpose and intent alignment**  
Date: 23 August 2026  
Authority: `REDESIGN_SEQUENCE.md`; `gate-5-reconciled-operator-graph.md`; `gate-6-capability-reconciliation.md`; `gate-5-operator-decision-ledger-six-questions.md`; `gate-5-operator-capability-ledger-five-responsibilities.md`  
Boundary: Foundry/AIP capability mapping only; no Gate 7 surface selection and no Foundry writes.

## 1. Binding verdict

**Adopt a narrow, exact, governed decision harness and a separate measured learning system.** The runtime product is an embedded AIP Chatbot that reads the accepted CORDON Ontology, calls four exact read Functions, asks for clarification when a material input is ambiguous, and directly executes one of four exact manager-owned Ontology Actions when an authenticated manager gives an explicit, unambiguous command and every independent guard passes. The prompt is the manager's decision; a generic coding-agent tool-approval modal is not part of the accepted product interaction.

Direct conversational execution does **not** make the model the authority. Authority remains with the authenticated principal and the current scoped Party assignment. The LLM resolves intent and constructs a candidate call; Action permissions, object/data access, submission criteria, Checkpoints where policy genuinely requires purpose justification, and fresh TypeScript v2 function-side validation independently determine whether the call can execute. A refusal is a correct product result, not an agent failure.

The initial runtime has **no generic write tool**, no manual official-result tool, no manual settlement/paid/accepted/established/complete marker, no arbitrary Function runner, and no autonomous manager decision. AIP Logic, Automate, Scenarios, OSDK/API, Evals, model training and observability support the same exact contract; they do not expand the four Actions or the authority of their caller.

The learning system is bounded: AIP Evals owns reproducible prompt→tool→target→parameter→simulated-edit trajectories, including edit-producing cases in Ontology simulations; deterministic custom evaluators score exact tool, target, parameters, edits, clarification and forbidden implications; experiments compare hosted model and prompt candidates; and launch selects a version-pinned hosted open-source model only after it clears every hard safety and quality gate. Reviewed production traces may later justify a separately governed tuning/BYOM programme. Tuning, BYOM and AIP Evolve are post-launch options, never launch dependencies or silent production mutation paths.

AI FDE and Palantir MCP are **builder tools only**. They may create, inspect and change Foundry resources during governed development. They are not CORDON runtime agents, product identities, domain decision owners, or alternate write planes.

## 2. Interpretation rules

### 2.1 Decision classes

The mechanism ledger serves the accepted six questions:

- **Q1 — Change:** What changed, and what does it affect?
- **Q2 — Applicability/authority:** What is required, allowed or blocked?
- **Q3 — Choice:** Who chooses, who decides and which route continues?
- **Q4 — Readiness:** Is the route ready for the named Action?
- **Q5 — Performance/acceptance:** What was done, and who accepted it?
- **Q6 — Outcome/exposure:** Did the intended result land, and what remains open?

Only four Q3/Q4 decisions are initially manager-owned CORDON mutations. All member, professional, beneficiary, executor, private-acceptor, bank/treasury and public-authority decisions remain received outcomes or routed work unless the exact actor later authenticates and genuinely transacts through CORDON.

### 2.2 Authority vocabulary

- **Principal authority:** authenticated user's platform identity and Action permission.
- **Domain authority:** current scoped Party assignment, basis, target, scope and effective time.
- **Decision authority:** the real actor who owns the proposition; never inferred from access or job title.
- **Technical identity:** an Automation owner, service principal, builder agent or API client. It supplies execution identity only; it does not create domain authority.
- **Direct role:** a mechanism exposed in the manager's live prompt-to-decision path.
- **AIP role:** what the model may reason about, call or explain. “AIP role” never means “AIP owns the decision.”

### 2.3 Disposition vocabulary

- **REQUIRED NOW:** necessary for the first safe runtime or its pre-release assurance.
- **REQUIRED CONDITIONAL:** required when the stated route, policy or tuned-model choice is activated.
- **DEFERRED:** useful later, but intentionally absent from the initial product path.
- **REJECTED:** prohibited because it duplicates authority, creates an unsafe bypass, or solves a builder problem rather than a product problem.

## 3. Complete mechanism-purpose ledger

The ledger contains **47 mechanisms**. “Overlap” states the nearest alternative and the non-duplicative boundary.

### 3.1 Runtime context, reasoning and interaction mechanisms

| ID | Mechanism | Purpose | Trigger | Output | Decision served | Authority | Direct/AIP role | Exact safeguards | Overlap boundary | Disposition and why |
|---|---|---|---|---|---|---|---|---|---|---|
| M01 | **Ontology retrieval context** | Deterministically ground each prompt in a fixed object set or semantically retrieved CORDON objects. | Every user message when configured context is relevant. | Prompt context plus object citations/selected object set. | Q1–Q6 orientation and evidence grounding. | Read access and markings of the invoking user; retrieval creates no decision. | **Direct:** invisible grounding. **AIP:** may cite and reason from only returned context. | Allowlist accepted CORDON object types/properties; minimum necessary backstage references; no broad historical-project context; preserve caller-level permissions; geometry is labelled candidate evidence only. | Unlike object-query, retrieval runs predictably on every message; unlike Function-backed context, it should not implement business logic. | **REQUIRED NOW** for stable grounding. Ontology context is documented alongside document and Function-backed context.[S01] |
| M02 | **Document retrieval context** | Supply relevant, cited excerpts from governing/evidence documents without promoting the legal corpus into domain types. | A prompt asks “why,” requests evidence, or needs a basis passage. | Full text or relevant chunks with Media Set/Item/page citation. | Q2 applicability explanation, Q4 evidence, Q5/Q6 substantiation. | Source permissions and Media Set access; documents support but do not decide. | **Direct:** evidence citations in conversation. **AIP:** summarize only within retrieved bounds. | Admitted PDFs live in one curated Media Set; `GoverningInstrument.primaryDocument` is a MediaReference; current-version/effective-date metadata and citation are mandatory; conflicting copies remain preserved; no retrieved prose overrides typed current authority or an external outcome. | Ontology retrieval gives decision-ready facts; document retrieval gives substantiating text. Function-backed context is reserved for a measured hybrid retrieval gap. | **REQUIRED NOW** for cited explanation; not a legal-reasoning engine.[S01][S02] |
| M03 | **Function-backed retrieval context** | Run custom deterministic/hybrid retrieval when fixed Ontology/document retrieval cannot bind the exact selected subject, date, authority or evidence set. | A selected application object set or query requires combined keyword, semantic, temporal or relationship retrieval. | A `retrievedPrompt` string and optional cited object/application-state outputs. | Q1/Q2/Q4 explanations and basis assembly. | Invoking user's Function/data permissions; read-only. | **Direct:** backstage prompt enrichment. **AIP:** consumes result, does not choose its authority. | Use only when M01/M02 are insufficient; typed input from pinned application variables; bounded result; citations explicitly emitted; no mutation; no duplicate implementation of the four Functions. | Overlaps M01/M02; it is the escape hatch for retrieval composition, not a fifth decision Function. | **REQUIRED CONDITIONAL**. Defer each instance until a measured retrieval gap exists.[S01][S02] |
| M04 | **Curated object-query tool** | Let the LLM filter, aggregate, inspect and traverse an allowlisted part of the accepted graph on demand. | Reasoning needs a fact not already present in deterministic context. | Bounded objects, object sets, aggregates or traversals. | Q1–Q6 fact resolution. | Caller object/property/link access. | **Direct:** tool call within the reasoning loop. **AIP:** read only. | Allowlist exact CORDON types and visible properties; seed from current application object set; cap result size; no arbitrary historical/backstage type search; no generic object edit; parallel calls only for independent reads. | Retrieval is pushed every turn; object-query is model-selected. Query Functions answer stable decision contracts and must not be reconstructed through ad hoc queries. | **REQUIRED NOW** as a narrowly curated read tool.[S03] |
| M05 | **Four exact Function tools** | Expose stable typed decision-support contracts rather than prompt-reimplementing business logic. | The user's question or intended Action requires impact, readiness, portfolio or exposure reasoning. | Typed output from the exact Function. | Q1 (`Determine Affected Decisions`); Q4 (`Assess Named-Action Readiness`); Q3 (`Compare Feasible Intervention Portfolios`); Q6 (`Determine Remaining Exposure`). | Function/read permissions; Functions create no authority and no edits. | **Direct:** callable in-chat. **AIP:** select, call and explain; never alter output semantics. | Fixed API names/version policy; typed inputs; bounded object sets; deterministic tests; no whole-population `.all()`/N+1; pinned version during evaluation/promotion; reads may run in parallel only if independent. | Object-query supplies raw graph reads; the four Functions own accepted computed answers. AIP Logic may orchestrate them but never duplicate them in prompts. | **REQUIRED NOW**.[S03][S04] |
| M06 | **Four exact Action tools** | Give the chatbot only the four manager-owned governed verbs. | Explicit authenticated prompt resolves to exactly one Action and all guardrails pass. | Atomic Ontology edits, factual occurrence(s), Action log and user-facing result/refusal. | Q3-D12, Q3-D13, Q3-D16, Q4-D27. | Authenticated principal plus exact current domain authority and Action eligibility. | **Direct:** direct execution, no redundant generic approval popup. **AIP:** select and parameterize one Action; never decompose or invent a verb. | Exact allowlist; no parallel writes; fresh function-side checks; criteria/permissions; idempotency; bounded edit set; semantic non-implications; audit; clarification on ambiguity. | TSv2 backing Functions implement these Actions but are never separately exposed. OSDK/API may call the same Actions, not an alternate write path. | **REQUIRED NOW**.[S03][S05] |
| M07 | **Application state** | Bind the chatbot to the operating picture's current selected objects, map scope, route, date and other deterministic UI context. | Chatbot is embedded in an application and a manager changes selection/context. | String/object-set variables available to retrieval, tools and prompts. | Primarily Q1–Q4 target/scope resolution; Q5/Q6 selected-result explanation. | Application/user session; state is context, never authority. | **Direct:** selected object/scope follows the conversation. **AIP:** reads only variables it needs. | Prefer object-set/string variables; expose minimum values; map exact selected keys; identify stale state; pin deterministic tool inputs at reasoning-loop start; do not assume an update in the same loop changes pinned inputs. | Commands can change UI state; application state describes it. Action parameters still undergo server-side resolution. | **REQUIRED CONDITIONAL** on the Gate 7 surface. Contract is defined now; widget mapping waits for Gate 7.[S06] |
| M08 | **Update-application-variable tool and deterministic variable updates** | Synchronize AIP output/selection back to the surrounding application without writing domain facts. | A read/tool result should focus a map, list or comparison, or the user asks to change application focus. | Updated string or object-set application variable. | Presentation support across Q1–Q6. | Application session only. | **Direct:** paired visual focus. **AIP:** update only allowlisted presentation variables. | Prefer deterministic updates from context/tool output over model-generated values; no variable named as a legal/ready/paid/complete truth; no variable update as Action success evidence. | Commands perform declared client operations; variable updates carry state. Neither replaces an Ontology Action. | **REQUIRED CONDITIONAL** after Gate 7 selects an app; **REJECT** all domain-truth variables.[S06] |
| M09 | **Command tools** | Invoke declared client-side operations in paired Palantir applications, such as centering a map or selecting a view. | User asks for a presentation/navigation operation that an application declares as a command. | Client-side application change and command result. | Presentation support, not a domain decision. | User's paired application session and command configuration. | **Direct:** optional UI control. **AIP:** may invoke only presentation-safe commands. | Gate 7 allowlist; no domain mutation command; avoid chains whose failure continues into later commands; do not infer command completion as Action/domain success; approval setting follows UX risk, not domain authority. | Application-state updates are simpler state synchronization; Commands address richer paired-app behavior. | **DEFERRED to Gate 7** because no surface/application has been selected and command configuration remains beta.[S07][S08] |
| M10 | **Request-clarification tool** | Stop execution and ask for missing material intent rather than guessing. | Target, bounded scope, actor/authority, effective date, outcome, override reason, consequence or proposal identity is ambiguous or conflicting. | A focused user question; resumed reasoning with the answer. | Any Q1–Q6 prompt; mandatory before all ambiguous mutations. | User supplies intent; clarification cannot grant authority or fix source truth. | **Direct:** normal conversational turn, explicitly not an approval dialog. **AIP:** abstain and ask one bounded question. | Trigger on material ambiguity; never fill from model priors; preserve prior scoped context; re-read state after response; if ambiguity is an external/source fact, route instead of asking user to invent it. | Submission criteria/refusal reject invalid calls; clarification prevents constructing a speculative call in the first place. | **REQUIRED NOW** and a promotion-critical behavior.[S03] |
| M11 | **AIP Logic orchestration** | Compose LLM reasoning, retrieval, exact Function calls, explanation and bounded proposal construction in a reusable Logic resource. | A task needs multi-step interpretation beyond Chatbot tool selection, or must run as a Function/Automate effect. | Typed explanation, proposal parameters, extracted candidate facts or a staged-write result behind an Action. | Q1–Q6 orchestration around stable contracts. | Invoking user's permissions; LLM can request tools but AIP Logic executes them under that identity. | **Direct:** normally called through Function tool or behind runtime orchestration. **AIP:** orchestrator, not source of deterministic truth. | Exact tools only; deterministic logic remains TSv2/pipelines; reserved decisions stay read/proposal-only; prompt/version branch governance; staged writes only behind an Action; Evals before promotion. | Chatbot Studio owns conversation/tool UX; AIP Logic owns reusable orchestration; TSv2 owns exact deterministic contracts and writes. | **REQUIRED NOW** only for measured orchestration needs; **REJECTED** as a duplicate prompt implementation of the four Functions.[S09][S10] |
| M12 | **Deterministic pipeline projections and optimizer** | Precompute complete populations, dependency candidates, spatial intersections, rollups and optimizer inputs at scale. | Source/occurrence change, scheduled refresh or policy/model-input change. | Versioned candidate sets, aggregates, feasible portfolios and bounded Function inputs. | Q1, Q2, Q3-D15 and Q6 at population scale. | Data/pipeline permissions; outputs are computed support, not reserved decisions. | **Direct:** invisible backend. **AIP:** consumes typed Function outputs only. | Complete-population assertions; versioned policy/objective; deterministic replay; geospatial candidate ≠ law; uncertainty preserved; no LLM scoring; Data Expectations/performance budgets. | Functions provide bounded live resolution/explanation; pipelines own scalable stable computation. Scenarios vary premises but do not replace optimizer correctness. | **REQUIRED NOW** to keep live Functions bounded and authoritative arithmetic deterministic.[S11] |

### 3.2 Exact read/write, authority and transaction mechanisms

| ID | Mechanism | Purpose | Trigger | Output | Decision served | Authority | Direct/AIP role | Exact safeguards | Overlap boundary | Disposition and why |
|---|---|---|---|---|---|---|---|---|---|---|
| M13 | **TypeScript v2 query Functions** | Implement the four read-only typed contracts over the current graph and prepared projections. | M05 invocation from Chatbot, AIP Logic, Automate or OSDK/API. | Typed read result; no Ontology or external-system edit. | Q1/Q3/Q4/Q6. | Caller read/Function access only. | **Direct:** exact Function call. **AIP:** caller/explainer. | Server-side bounded traversal; fixed response schema; breaking changes get new API name; deterministic unit/property/integration tests; latest-tag behavior controlled at promotion. | M12 precomputes; M13 resolves current bounded context. | **REQUIRED NOW**.[S04] |
| M14 | **TypeScript v2 function-backed Actions** | Implement cross-object validation and one explicit edit batch for each named Action. | M06 exact Action submission. | Validated edits or user-facing refusal. | Four manager-owned decisions only. | Action caller plus domain assignment resolved at execution. | **Direct:** hidden implementation of exact Action. **AIP:** cannot invoke backing write Function directly. | Generated edit union contains every touched type; no undeclared effect; current graph re-read; return zero edits/throw on any failed premise; concurrency and idempotency checks; Action criteria remain independent. | Standard declarative Action rules are simpler but cannot safely implement coupled occurrence/authority/complete-set effects. | **REQUIRED NOW** for all four Actions.[S12] |
| M15 | **TypeScript v2 staged writes** | Make nested edits visible during execution and commit the combined transaction atomically only after successful completion. | An Action, especially portfolio rebalance, requires read-after-write or nested edit composition. | One committed staged edit set, or no edits on error. | Primarily Q3-D16; available to other Actions only when needed. | Same Action/caller authority; staging does not weaken criteria. | **Direct:** invisible transaction mechanism. **AIP:** never a standalone tool. | One Action wrapper; complete affected set loaded server-side; stale-premise fingerprint; max 10,000 edited objects; no silent chunking; tests for retry, concurrency, omitted protected commitments and rollback. | Regular TSv2 edit batch suffices when no read-after-write/nested dependency exists. AIP Logic staged writes are orchestration-level, not the preferred domain-write implementation. | **REQUIRED NOW** for capacity; **REQUIRED CONDITIONAL** elsewhere. Full capability is owner-confirmed even though docs mark staged writes beta.[S13] |
| M16 | **Action — Accept Cooperative Execution Mandate** | Record the cooperative's acceptance/refusal of a real member-granted mandate and activate only accepted cooperative-side authority. | Explicit manager prompt naming mandate, member, scope, outcome and material terms. | Instrument Occurrence; scoped contextual authority activation only for accepted scope; fallback preserved; Action log. | Q3-D12. | Cooperative role with exact current governance and mandate-acceptance authority. | **Direct:** execute on clear command. **AIP:** resolve target, explain non-implications, call exact Action. | Require real member grant and participation result; determinate scope/term/powers/duties/exclusions/conflicts/fallback; idempotent occurrence ref; re-resolve authority at apply; never create grant, eligibility, concession, capacity or creditor identity. | Decide Pursuit is separate; mandate enables possible representation but does not select a route. | **REQUIRED NOW**. |
| M17 | **Action — Decide Cooperative Pursuit** | Persist pursue/defer/refuse for one bounded cooperative route without changing public or capacity truth. | Explicit manager prompt naming Pursuit, outcome, scope and reason. | Updated Pursuit; Pursuit Decision Record; fallback and reconsideration trigger; Action log. | Q3-D13. | Cooperative role with exact collective-pursuit authority. | **Direct:** execute on clear command. **AIP:** may recommend/prepare, but the explicit manager prompt is the decision. | Require received member choice, accepted mandate, valid Programme route, bounded Holding/Parcel/optional Intervention scope, deadline and fallback; refuse material conflict; never create eligibility, concession, capacity, filing or execution truth. | M16 establishes mandate acceptance; M17 decides collective pursuit; M18 allocates scarce capacity. | **REQUIRED NOW**. |
| M18 | **Action — Commit or Rebalance Intervention Capacity** | Apply one coherent portfolio decision across the complete affected Commitment set. | Explicit manager prompt selecting a non-expired Capacity Portfolio Proposal or exact complete plan, including override reason where needed. | Atomic creates/changes/releases/reallocations; per-Commitment Change Records; shared portfolio-decision reference; one portfolio Action log. | Q3-D16. | Cooperative role with exact allocation/override authority under operative policy. | **Direct:** executes selected plan with no redundant popup. **AIP:** compare/explain/propose; cannot turn recommendation into commitment. | Complete-population and complete-edit-set assertion; current-state fingerprint; proposal expiry; deterministic feasibility; constraints/fairness/protected commitments; override authority/reason; duplicate-capacity and concurrency checks; ≤10,000 edits; no chunking; preserve deferred fallback; never alter eligibility, concession, duty or dispatch authority. | Scenarios compare; Capacity Portfolio Proposal binds a selected candidate; this Action alone commits. Automate may recompute/stage but cannot decide initially. | **REQUIRED NOW**. |
| M19 | **Action — Dispatch Intervention** | Create the bounded executor handoff for work that is ready now. | Explicit manager prompt naming Intervention, exact scope, executor and dispatch intent. | Dispatch Intervention Occurrence; authorized/excluded scope; executor, clock, stop/return conditions; optional real work-order Instrument; Action log. | Q4-D27. | Party with exact current management/dispatch authority for that route/scope/date. | **Direct:** execute on clear prompt. **AIP:** run readiness, resolve exact scope, invoke Action. | Fresh validation of dispatcher/executor authority, target, certified design, access, permits, capacity/resources, finance/evidence and clock compatibility; idempotency; excluded scope explicit; never write movement, performance, acceptance or establishment. | `Assess Named-Action Readiness` is preflight only; M19 independently revalidates and creates the legal/operational handoff. | **REQUIRED NOW**. |
| M20 | **Action submission criteria** | Apply an independent, inspectable eligibility gate to every submission. | Any direct, Chatbot, Automate, Scenario or API Action attempt. | Pass or configured refusal before/with submission. | All four manager decisions. | Platform evaluates caller/parameter/object/current-user conditions; criteria do not themselves grant authority. | **Direct:** invisible unless refused. **AIP:** cannot bypass. | Per Action: required target and key parameters; eligible group/user where appropriate; obvious object state; main-vs-Scenario context; required override/decision reason; no criterion references a nonexistent scalar traversal; each failure has exact message. Full contextual authority stays function-side. | Permissions answer “may invoke this verb”; criteria answer “is this caller/input/state eligible now”; function checks answer “is the complete domain transaction valid now.” | **REQUIRED NOW**.[S14] |
| M21 | **Permissions, access policy and actions-only editing** | Ensure no consumer can bypass exact Actions or read sensitive facts beyond scope. | Every read or write path. | Allowed/denied object/property/link/Function/Action access. | All decisions; it sets the technical authority envelope. | Foundry identity, roles/groups, project permissions, markings/Restricted Views and edit policies. | **Direct:** transparent to authorized manager. **AIP:** inherits invoking principal; no elevated agent identity. | Actions-only edit mode; least privilege; restricted views/markings for member/financial/authority evidence; exact Action apply permission; no writeback direct-edit permission; project isolation; no historical rejected-model imports. | Submission criteria and function validation are additional layers, not substitutes. | **REQUIRED NOW**.[S15][S16] |
| M22 | **Checkpoints** | Capture purpose acknowledgement, justification or reauthentication for a genuinely policy-sensitive submission. | Only a configured policy condition for `Submit action` or another sensitive interaction. | Checkpoint record with user, time, prompt, justification, checkpoint type and Action reference. | Any manager Action only where governance requires purpose justification. | Governance policy; checkpoint proves acknowledgement/justification, not domain authority. | **Direct:** appears only when legally/policy required. **AIP:** cannot satisfy it for the user or use it as approval. | Narrow condition; exact purpose language; retained record; principal must satisfy; do not deploy as universal “are you sure?” UX; do not confuse Approvals/checkpoint completion with the cooperative decision itself. | Explicit prompt is the normal manager decision; Checkpoint is an exceptional compliance control. Action logs record execution, not purpose justification. | **REQUIRED CONDITIONAL**, not default UX.[S17] |
| M23 | **Ontology Scenarios** | Sandbox alternate Actions/facts and compare downstream consequences without changing main Ontology state. | Capacity alternatives materially matter, or a risky Action needs consequence rehearsal. | Isolated scenario state, comparison/diff and possible separately governed merge. | Q3-D15/D16 primarily; Q4 readiness and Q6 exposure hypotheticals. | Scenario access and Action criteria; scenario merge is not domain approval. | **Direct:** conversational what-if support. **AIP:** may construct/compare scenarios; manager still issues the production command. | Scenario execution flag in criteria; no production side effects; same deterministic optimizer; never treat scenario acceptance as commitment; production Action re-reads current main state; verify multi-Commitment function-backed behavior. | Capacity Portfolio Proposal stores the selected complete plan/fingerprint; Scenario is the exploratory state, not the durable decision package. | **REQUIRED NOW** for material portfolio comparison; optional for simple Actions.[S18] |
| M24 | **Capacity Portfolio Proposal** | Bind one selected scenario/plan to a complete target set, versions, fingerprint and expiry before commitment. | Manager asks to compare/select a capacity alternative or AIP prepares a rebalance. | Hidden proposal object containing selected Scenario, edits, policy/recommendation version, protected set, evidence summary, fingerprint and invalidation condition. | Q3-D15→Q3-D16 handoff. | Technical package only; authenticated manager prompt supplies the decision. | **Direct:** referenced in conversation. **AIP:** may construct and explain. | No approval-status semantics; exact Action/version/target binding; complete set; expiry on material change; no mutation until M18; proposal ID is idempotency input. | Scenarios explore; proposal freezes one candidate; Action commits. | **REQUIRED NOW** for capacity only. |
| M25 | **Action logs** | Audit who invoked each manager Action and which objects the platform Action edited. | Every Action submission when logging is configured. | One Action-log object linked to edited objects with Action/version, user, time and selected context/parameters. | Assurance across Q3/Q4 and later investigations. | Platform audit under submitting principal. | **Direct:** normally backstage, inspectable for audit. **AIP:** may use only for audit explanation, never domain truth. | One log type per Action; complete `Edits` provenance for function-backed Actions; include decision ref/scope/reason where safe; permission logs appropriately; do not infer external occurrence or outcome from log existence. | Hidden domain occurrence records preserve mandate/pursuit/commitment/dispatch facts; Action logs preserve platform submission context. OSv2 edit history is a separate object-level audit mechanism. | **REQUIRED NOW**.[S19] |
| M26 | **Authenticated external-outcome ingestion and reconciliation** | Receive member/professional/public/private/bank outcomes without a manual truth-making tool. | Source sync, public API, HTTPS listener/stream, signed webhook or controlled adapter receives an outcome. | Idempotent typed occurrence, raw evidence reference, reconciliation result, then affected-decision/exposure recomputation. | Q1, Q2, Q5, Q6 and all 31 reserved decisions. | Actual source/signing actor and source contract; AIP does not create authority. | **Direct:** result appears in conversation/graph. **AIP:** parse/map/reconcile; uncertain mappings become review candidates. | Stable source occurrence ID/version; signer/channel; subject grain; consequential/received times; supersedes/reverses; duplicate/late/correction/partial/unmatched cases; immutable raw payload; signature/schema validation; no manual paid/accepted/official tool. | Automate routes/recomputes after receipt; it does not make the received outcome. | **REQUIRED NOW** as the reserved-decision feedback path.[S21] |

### 3.3 Direct execution, automation and autonomy mechanisms

| ID | Mechanism | Purpose | Trigger | Output | Decision served | Authority | Direct/AIP role | Exact safeguards | Overlap boundary | Disposition and why |
|---|---|---|---|---|---|---|---|---|---|---|
| M27 | **Direct conversational execution** | Make an explicit authenticated natural-language command the manager's operative decision and execute the exact Action without coding-agent approval UX. | Clear prompt with exact intent, target, scope and required reason/consequence. | Immediate exact Action result or precise guardrail refusal; then recomputed state and next handoff. | Four manager-owned decisions. | Authenticated principal plus current domain assignment and all Action gates. | **Direct:** primary product interaction. **AIP:** intent resolution and exact tool invocation, not authority. | Require explicit imperative/decision language; one Action only; material ambiguity→M10; reserved owner→route; criteria/permissions/function checks/idempotency/audit; no parallel mutation; no auto-filled override reason; re-read state after execution. | Checkpoints are conditional compliance, not universal confirmations. AI FDE approval UX is builder governance and explicitly not the product model. | **REQUIRED NOW**; this is the accepted interaction bar. |
| M28 | **Automate** | Detect change, schedule/selective recomputation, run read Functions, route/notify, reconcile events and stage proposals. | Time/object/stream condition or failure/retry condition. | Function result, notification, recomputation trigger, proposal or bounded fallback. | Q1 change propagation; Q3 portfolio refresh; Q4 blocker clearing; Q6 exposure updates. | Automation-owner technical identity; never fresh manager/domain authority. | **Direct:** backstage asynchronous support. **AIP:** AIP Logic may be an effect, but outputs remain read/proposal-only initially. | Idempotent effects for at-least-once execution; no assumed order across Action effects; four production Actions disabled from autonomous apply initially; owner-account monitoring; retry/fallback; complete event keys; scheduled fallback when live monitoring cannot express set. | Direct conversation owns synchronous manager decisions. External ingestion supplies authoritative facts. | **REQUIRED NOW** for detection/recompute/routing; **REJECTED NOW** for autonomous execution of four manager Actions.[S22] |
| M29 | **Asynchronous agent autonomy** | Eventually execute unattended workflows or manager Actions under an explicit machine-authority policy. | Future governance decision defines exact trigger, principal/project identity, decision class, risk ceiling and rollback. | Autonomous action/proposal and telemetry. | Potentially selected Q1/Q4 operations; manager Actions only if separately authorized later. | Explicit machine/project authority policy—not the Automation owner by accident and not model confidence. | **Direct:** none initially. **AIP:** background agent may reason only within published contract. | Earned per Action; Evals safety floor; production shadow/proposal phase; idempotency; bounded target set; current fingerprint; kill switch; budget/rate limits; canary; drift alert; rollback/reconciliation; no reserved external decisions. | Automate is the trigger/execution substrate; autonomy is the governance permission to let it decide. These must not be conflated. | **DEFERRED**. Initial autonomy is read/recompute/proposal only. |

### 3.4 Trajectory, evaluation, training and improvement mechanisms

| ID | Mechanism | Purpose | Trigger | Output | Decision served | Authority | Direct/AIP role | Exact safeguards | Overlap boundary | Disposition and why |
|---|---|---|---|---|---|---|---|---|---|---|
| M30 | **Canonical trajectory specification** | Define the exact prompt→context→clarification/tool→target→parameters→edits/outcome contract and forbidden implications for every case. | Before data generation, Evals or training; update after a reviewed defect. | Versioned trajectory rows with prompt, object/application context, expected tool/clarification, target, parameters, edits/result and prohibited effects. | All six questions and four Actions. | Product/domain governance owns labels; model does not label itself. | **Direct:** none. **AIP:** training/evaluation target. | Include clear, ambiguous, unauthorized, stale, conflicting, adversarial and reserved-owner cases; exact Action version and object keys; balanced refusals/acceptances; source provenance; no production log automatically becomes truth. | AIP Evals generates/executes cases; M30 defines expected semantics; custom evaluators measure them. | **REQUIRED NOW** before model selection/training. |
| M31 | **AIP Evals trajectory generation** | Define and execute realistic single- and multi-turn prompt→tool→target→parameter→simulated-edit trajectories directly against the Chatbot/Logic runtime. | New chatbot/model/prompt/tool version, object-set case generator, coverage gap or defect class. | Reproducible Eval cases, traces, simulated edits, clarification turns and scored outputs. | Interaction coverage around Q1–Q6. | Evaluation suite and Ontology simulation; no production authority. | **Direct:** learning harness only. **AIP:** system under test. | Use manual and object-set-generated cases; isolate edits in Ontology simulations; record exact versions/seeds/context; generate ambiguity/correction/failure paths; never ingest production conversations as training truth without curation. | AIP Evals owns trajectory generation and evaluation. Playwright is optional Gate 7 end-to-end UI regression only. | **REQUIRED NOW** for trajectory generation and evaluation. |
| M32 | **AIP Evals suites and Ontology simulations** | Run repeatable tests of Chatbot/Logic/code Functions and prevent live mutation for edit-producing cases. | Candidate prompt/model/tool/Function/Action implementation or release. | Per-case/aggregate metrics, passes/failures, variance and simulated Ontology edits. | All decision and Action contracts. | Evaluation resource/test data permissions; simulation has no production authority. | **Direct:** release gate. **AIP:** tested system. | Edit cases always in Ontology simulation; at least three iterations for nondeterministic LLM cases; exact suite versions; all required metrics must pass; zero safety violations; manual review for new classes; deterministic tests remain separate. | Ordinary tests verify deterministic code; AIP Evals verifies nondeterministic orchestration/model behavior. | **REQUIRED NOW**.[S23][S24] |
| M33 | **Custom deterministic evaluators** | Score exact tool, target, parameters, clarification, edits, abstention and prohibited implications rather than surface prose similarity. | Any trajectory whose expected behavior is not captured by built-in evaluators. | Boolean/numeric metrics or a struct of metrics; pass/fail per iteration. | Four Actions, authority boundaries and cross-route non-collapse. | Evaluator code and domain labels are versioned human-governed artifacts. | **Direct:** release gate. **AIP:** cannot alter evaluator. | TS evaluator for edit outputs; search simulated created objects by stable identifiable properties; compare existing edited objects directly; threshold each metric; test evaluator itself; safety metrics are Boolean hard gates, not weighted averages. | LLM-as-judge may assess explanation quality, but cannot be sole judge of exact edits/authority. | **REQUIRED NOW**.[S24][S25] |
| M34 | **AIP Evals experiments and baseline comparison** | Compare models, prompts, tool modes and parameter combinations under identical suites and measure variance/cost/latency. | Model/prompt candidate, tuning run or optimization proposal. | Grid-search experiment results, per-metric comparison, variance, cost and latency. | Model/tool policy across all decisions. | Release governance selects winner; experiment score does not grant runtime authority. | **Direct:** promotion evidence. **AIP:** candidate models under test. | Same test split and Function/Action versions; holdout set; multiple iterations; safety hard gates; compare strong Palantir baselines and tuned models; cost/latency only after safety parity; no tuning on the final holdout. | Model Catalog playground is exploratory; Evals experiments are the governed comparison. AIP Evolve may automate candidate changes later. | **REQUIRED NOW** for model promotion.[S23][S26] |
| M35 | **Reviewed production-feedback curation** | Turn real corrections, clarifications, refusals, overrides and outcomes into trustworthy new trajectories. | Operator correction, unexpected refusal, false success, override, drift signal or downstream observed result. | De-identified/permissioned reviewed trajectory candidate with disposition and defect class. | Continuous improvement across Q1–Q6. | Domain reviewer accepts label; data governance controls reuse. | **Direct:** operator feedback enters review queue. **AIP:** may cluster/suggest, never self-approve training labels. | Separate telemetry from domain history; redact/minimize; retain consent/markings; detect prompt injection; preserve exact runtime versions; exclude unverified external outcomes; dedupe; reviewer sign-off; train/holdout split hygiene. | Observability supplies candidates; curation converts them into learning data. | **REQUIRED NOW** as a process, even before enough data exists to tune. |
| M36 | **Optional post-launch tuning programme** | Produce a task-specific model only when reviewed production evidence shows material value beyond the hosted launch model. | Stable released baseline, sufficient reviewed trajectories, measured hosted-model gap and a separately approved training budget. | Versioned tuned candidate, model card, training lineage and Evals results. | Intent/tool/clarification performance only; no domain authority. | Model-development team; release governance controls promotion. | **Direct:** none until separately promoted. **AIP:** candidate reasoner/tool caller. | Curated trajectories only; locked adversarial holdout; full exact Action/authority/refusal suite; shadow/canary and rollback. | Hosted models are the launch path. Tuning is admitted only by measured marginal value. | **DEFERRED.** Not a B8/B11 launch dependency. |
| M37 | **Model Training Code Repository** | Run reproducible production-grade fine-tuning/retraining pipelines with CI/CD and model outputs. | M36 enters a reproducible training/retraining phase. | Trained artifacts, metrics, versioned model submission and lineage. | Learning system only. | Repository/model/data permissions; no runtime Action authority. | **Direct:** builder-only. **AIP:** none at product runtime. | Model Training template; pinned dependencies/data/seed/config; training/test separation; experiment logging; `palantir_models`; branch/review/release; resource budgets; no direct production model swap. | Code Workspaces supports interactive exploration; repository owns repeatable production training. | **REQUIRED CONDITIONAL** for production tuning.[S27] |
| M38 | **Jupyter Code Workspace** | Explore data, prototype fine-tuning and adapters, inspect model artifacts and publish experimental versions interactively. | Early model/data exploration or adapter debugging. | Notebook experiments, candidate adapter/model versions and diagnostics. | Learning system only. | Workspace/model/data permissions. | **Direct:** builder-only. **AIP:** none at runtime. | Approved compute/data; notebook and `.py` adapter versioned; no final release from unreviewed mutable notebook state; promote reproducible logic to M37; record environment and model version. | M37 is CI/CD production path; M38 is fast iterative development. | **REQUIRED CONDITIONAL** for exploration, not the canonical retraining runtime.[S28] |
| M39 | **`palantir_models` model asset and adapter** | Standardize model save/load/API/predict behavior and publish a versioned Foundry model asset. | Training produces a candidate artifact for evaluation/deployment. | Model version plus adapter package/API usable in downstream inference. | Learning/deployment bridge only. | Model/repository permissions; adapter has no domain authority. | **Direct:** invisible model serving. **AIP:** inference backend when selected. | Explicit adapter API; serializer and dependencies; test local transform/predict; model card and lineage; version pin; resource envelope; maintain replacement adapter because legacy generic language-model adapters are sunset. | BYOM registered-model support exposes an LLM across AIP applications; a Foundry model asset/adapter packages trained artifacts. A deployment bridge may be needed between them. | **REQUIRED CONDITIONAL** for a locally trained model asset.[S29][S30] |
| M40 | **Registered model / BYOM** | Make a future tuned CORDON model available through AIP applications if the post-launch tuning gate opens. | M36 produces a candidate that beats the hosted baseline and an administrator registers/enables it. | Model-selector entry with permissions, rate limits and observability. | Runtime reasoning/tool calling only. | Enrollment admin registers; end user still supplies Action authority. | **Direct:** none at launch. **AIP:** optional future backend. | Supported tool API; full deployed Evals; rate limits; observed usage; disable/rollback; no source-permission leakage assumption. | Hosted open-source model selected by B8 is the launch path. | **DEFERRED / REQUIRED CONDITIONAL after M36.** |
| M41 | **AIP Evolve** | Coordinate AI FDE agent fleets to propose and validate model/prompt/workflow improvements against an objective and limits. | Stable released baseline, trusted Evals suite and bounded optimization goal (quality, cost, latency, migration). | Agent graph, candidate changes, validation results, confidence/limitations and branch proposal. | Learning-system optimization, not an operator decision. | Builder permissions and Global Branch review; no runtime domain authority. | **Direct:** none in product. **AIP:** meta-optimization builder. | Fix target, suite, acceptable divergence, allowed change types and max iterations; preserve baseline; inspect evidence; branch proposal review; full safety suite; no direct production merge; no training-data self-approval. | M34 compares explicit candidates; AIP Evolve automates bounded candidate exploration. It does not replace M32/M33 or release governance. | **DEFERRED** until baseline/evals are mature; then **REQUIRED CONDITIONAL** for bounded continuous optimization.[S32] |

### 3.5 Observability, API and builder-only mechanisms

| ID | Mechanism | Purpose | Trigger | Output | Decision served | Authority | Direct/AIP role | Exact safeguards | Overlap boundary | Disposition and why |
|---|---|---|---|---|---|---|---|---|---|---|
| M42 | **Workflow Lineage / AIP observability** | Trace Functions, Actions, Automations, AIP Logic and model calls; monitor latency, failures, prompts, responses, tools, tokens and edits. | Every instrumented runtime execution and release investigation. | Metrics, run history, distributed traces, logs and searchable execution evidence. | Assurance for all decisions; no decision truth. | Log-access policy and project/resource markings. | **Direct:** backstage operations/debugging. **AIP:** telemetry source for reviewed learning candidates only. | Sensitive prompt/response log policy; minimum log access; model/tool/version tags; track refusal class, clarification, selected tool, target, edit count, idempotency, latency, correction/override; retention not relied upon for domain history. | Action logs audit submissions; observability explains execution internals; factual occurrences are durable domain truth. | **REQUIRED NOW**.[S33] |
| M43 | **Log/metric/trace export to streaming dataset** | Support longer-horizon analysis, drift dashboards, alerting and external observability integrations. | Organization enables export for selected CORDON projects. | Streaming telemetry dataset in internal or OTLP schema. | Learning/operations assurance. | Organization admin/ISO configuration plus destination dataset permissions/markings. | **Direct:** none. **AIP:** offline analysis only after governance. | Project allowlist; sensitive fields/markings; retention and purpose limitation; prevent telemetry dataset from becoming domain history or automatic training data; monitor export gaps; separate audit-log exports where needed. | Workflow Lineage provides interactive recent debugging; export supports durable/custom analysis. | **REQUIRED CONDITIONAL** for production drift/learning at scale; configure before using logs as feedback candidates.[S34][S35] |
| M44 | **OSDK and Platform API** | Embed the chatbot, query the graph, call typed Functions and apply/validate the same exact Actions from a custom operational application or integration. | Gate 7 application or an authorized external client invokes CORDON. | Typed objects/object sets, Function results, Chatbot sessions/messages, Action validation/apply result and cache synchronization. | All six questions and four Actions through another client. | OAuth/user/service principal scopes plus object/Function/Action permissions and criteria. | **Direct:** application integration path. **AIP:** Chatbot session and exact tool behavior remain the same. | Generated typed clients; no raw edit endpoint; validate-only preflight where useful, then fresh apply; preserve caller identity; Action criteria/function checks still bind; versioned API contracts; rate limits; do not use Consumer Mode where required Functions/function-backed Actions are unsupported. | Chatbot Studio supplies configured agent; OSDK/API supplies the host/client. It is not an alternate authority or write plane. | **REQUIRED NOW as an integration contract; surface choice remains Gate 7**.[S36][S37] |
| M45 | **AI FDE** | Let an in-platform builder agent inspect and change pipelines, repositories, Ontology, Functions, Evals and applications through a closed action→observation loop. | Governed development, migration, audit or maintenance task—not an operator prompt. | Branch changes, code, builds, proposals, documentation or read-only findings. | Build quality only; serves no Q1–Q6 runtime decision directly. | Builder's authenticated Foundry session and permissions; mutating tools use AI FDE approval/branch controls. | **Direct:** excluded from product. **AIP:** builder agent only. | New clean project/Global Branch; select only required mode/tools/context; per-tool/session/branch approval; full audit; no production data writes by this Gate 6 task; no reuse as CORDON service account; no exposure in Chatbot tool list; independent review before merge. | Palantir MCP is the external-agent builder interface; AI FDE is the native in-platform builder. Its approval UX is intentionally different from direct manager Action UX. | **REQUIRED CONDITIONAL for implementation productivity; REJECTED as product runtime, authority, model-training runtime or fifth agent.**[S38][S39] |
| M46 | **OSv2 user edit history** | Supply extra object-level before/after audit on every Action-edited type. | Feature activation followed by an edit. | User/timestamp/edit information under the object's access policy. | Audit/investigation only. | Platform edit identity and current-object access; no domain authority. | **Direct:** backstage only. **AIP:** not in default runtime context. | Define activation date, permission-bound access and retention; never infer pre-activation history, treat datasource changes as edits, use it as factual history or expose it as an operator timeline. | Domain occurrences, Action logs, durable receipts and Workflow Lineage remain distinct assurance paths. | **REQUIRED NOW as supplemental backstage audit by Owen's decision.**[S20] |
| M47 | **Palantir MCP** | Give an external AI IDE/agent a secure builder interface to Foundry documentation, Ontology and development tools. | Governed external-agent development, inspection or maintenance task—not an operator prompt. | Read findings, code/resource changes, builds and proposals within exposed tool scopes. | Build quality only; serves no Q1–Q6 runtime decision directly. | Configured MCP client identity/token/scopes and ordinary Foundry permissions. | **Direct:** excluded from product. **AIP:** external builder agent only. | Least tool set and short-lived credentials; new clean project/Global Branch; no Ontology data write lane unless separately authorized through exact consumer APIs; tool-schema discovery before calls; audit; independent review; never expose the MCP server to the operator Chatbot. | AI FDE is the native in-platform builder; MCP connects external agentic development. Neither is a product agent, runtime service identity or fifth write plane. | **REQUIRED CONDITIONAL for external-agent implementation productivity; REJECTED as product runtime, authority or model-training runtime.**[S40] |

## 4. Exact runtime allowlist

### 4.1 Read tools

1. `Determine Affected Decisions`
2. `Assess Named-Action Readiness`
3. `Compare Feasible Intervention Portfolios`
4. `Determine Remaining Exposure`
5. Curated object query over accepted CORDON types/properties and minimum basis references
6. Request clarification

Retrieval context and application state are configured context mechanisms rather than free-form tools. Function-backed retrieval is added only for a measured retrieval gap.

### 4.2 Write tools

1. `Accept Cooperative Execution Mandate`
2. `Decide Cooperative Pursuit`
3. `Commit or Rebalance Intervention Capacity`
4. `Dispatch Intervention`

No backing edit Function is independently callable. No generic command can mutate Ontology truth. No tool records a public, member, professional, private, financial or biological outcome manually.

### 4.3 Explicitly prohibited tools/effects

- generic object edit, create, delete or link;
- generic `Execute CORDON Action` or arbitrary Action selector;
- generic status/readiness/completion update;
- generic history/occurrence append;
- manual `Record official outcome`, `Mark paid`, `Mark accepted`, `Mark compliant`, `Mark established` or `Mark complete`;
- direct write-capable backing Function;
- multiple parallel or chained mutating tools;
- AIP-generated member election, professional certification, beneficiary release, executor attestation, acceptance, public decision or cash fact;
- model-generated authoritative optimizer score, legal applicability verdict or transaction reconciliation;
- AI FDE or Palantir MCP in the operator Chatbot.

## 5. Exact direct conversational execution contract

A manager command executes without a redundant generic approval modal **only if all conditions below are true**:

1. **Authenticated principal:** the Chatbot/host application propagates the current user, not a builder or Automation owner.
2. **Explicit decision language:** the prompt directs one of the four verbs rather than merely asking for an explanation, preview or recommendation.
3. **Exact target and scope:** object keys, selected object set and bounded scope resolve uniquely against current application/Ontology state.
4. **Exact consequence:** outcome and required reason/override reason are explicit; the model does not invent one.
5. **Current domain authority:** the backing Function resolves an effective scoped Party assignment and basis for this actor, target, scope and date.
6. **Independent platform gates:** object access, Action permission, submission criteria and any genuinely policy-mandated Checkpoint pass.
7. **Fresh domain validation:** current prerequisites, conflicts, complete sets, protected commitments, clocks and source outcomes are re-read at apply time.
8. **Atomic/idempotent effect:** one named Action returns the complete accepted edit set; retries cannot duplicate the decision; no parallel write runs.
9. **Bounded non-implications:** the Action writes only its accepted fact/occurrence and cannot imply another actor's decision or later result.
10. **Audit and feedback:** Action log, factual occurrence, recomputation and next bounded handoff are produced.

If 2–4 are ambiguous, use clarification. If 5–7 fail, return the exact refusal and real cure owner. If the decision belongs to another actor, prepare/route or ingest the authenticated outcome; never ask the cooperative manager to impersonate that actor. If the desired verb is not one of the four Actions, abstain and route.

## 6. Four-Action guard matrix

| Action | Required explicit prompt content | Submission-criteria minimum | Function-side fresh validation | Atomic writes | Prohibited implications |
|---|---|---|---|---|---|
| **Accept Cooperative Execution Mandate** | mandate, member/cooperative, accept/refuse, bounded scope, material terms/fallback | eligible cooperative role; mandate target; outcome and scope present; reason if policy requires | member grant and participation; current governance authority; term/powers/duties/exclusions; conflicts; fallback; duplicate occurrence | append Instrument Occurrence; activate only accepted scoped authority; preserve refused scope/fallback | no member grant, eligibility, concession, capacity, filing, creditor right |
| **Decide Cooperative Pursuit** | Pursuit, pursue/defer/refuse, scope, reason | eligible pursuit role; Pursuit target; outcome/reason required | member choice; accepted mandate; Programme route; exact scope; deadline/conflict; fallback/reconsideration; duplicate | modify Pursuit; append Pursuit Decision Record; preserve fallback | no eligibility, concession, capacity, filing, execution |
| **Commit or Rebalance Intervention Capacity** | proposal/portfolio ref, complete plan selection, affected period, override reason if applicable | eligible allocation role; proposal ref; required decision/override reason; main/Scenario context | complete population/edit set; proposal version/fingerprint/expiry; optimizer feasibility; constraints/safeguards; protected commitments; authority; duplicates/concurrency; ≤10,000 edits | staged one-batch create/change/release/reallocate; per-Commitment records; shared decision ref; one log | no recommendation→commitment shortcut, eligibility, concession, duty, fallback deletion, dispatch authority |
| **Dispatch Intervention** | Intervention, exact Parcel/Plant scope, executor, dispatch intent/date | eligible dispatcher; target/scope/executor present; obvious route state | current dispatcher/executor authority; certified design; access; permits; real resources/capacity; finance/evidence; clocks; exclusions/stop conditions; duplicate | append dispatch occurrence; optional real work-order Instrument; log | no movement, performance, acceptance, compliance, establishment or payment |

## 7. Submission criteria, permissions and Checkpoints are not interchangeable

| Layer | Question answered | Required implementation | What it must not claim |
|---|---|---|---|
| **Object/data access and actions-only edit policy** | Can this principal see this fact and is direct editing structurally blocked? | Least privilege, Restricted Views/markings where needed, no direct writeback editing. | Access does not prove domain authority. |
| **Action apply permission** | May this principal invoke this bounded verb at all? | Exact groups/roles/project permissions for each Action; no broad arbitrary Action permission. | Permission does not prove target/scope/date authority. |
| **Submission criteria** | Is this caller/input/obvious current state eligible for this submission? | Per-Action criteria with exact failure messages, required parameters and current-user/object conditions. | Criteria alone do not prove complete-population, cross-object or proposition-specific authority. |
| **Function-side validation** | Is this exact transaction valid against the complete current graph now? | Re-resolve domain assignment, scope, date, basis, prerequisites, conflicts, fingerprint, idempotency and atomic set. | Function validation must not be the only platform gate. |
| **Checkpoint** | Must the user acknowledge, justify or reauthenticate for policy/purpose reasons? | Configure only for a real policy condition; retain checkpoint record. | A checkpoint is not authority, a domain approval, or default chatbot confirmation. |
| **Action log/domain occurrence** | What invocation happened, and what consequential fact was created? | Both platform audit and factual occurrence where required. | Neither alone supplies all of the other's meaning. |

## 8. Complete prompt → reason → Action → feedback → retraining loop

### 8.1 Runtime decision loop

```text
1. PROMPT
   authenticated manager + current application state + explicit natural-language request

2. GROUND
   deterministic Ontology/document retrieval
   + curated object query where needed
   + current factual occurrences and source-supported basis

3. CLASSIFY INTENT AND AUTHORITY BOUNDARY
   explanation/read request
   OR one exact manager Action
   OR reserved external-owner decision
   OR materially ambiguous request

4. CLARIFY / ROUTE / CONTINUE
   ambiguous material target/scope/actor/date/reason/consequence → request clarification
   reserved owner → prepare bounded package and route; do not execute
   exact manager decision → continue

5. REASON WITH EXACT CONTRACTS
   call the applicable subset of:
   - Determine Affected Decisions
   - Assess Named-Action Readiness
   - Compare Feasible Intervention Portfolios
   - Determine Remaining Exposure
   use Scenarios for material alternatives; deterministic optimizer owns feasibility/score

6. CONSTRUCT ONE EXACT CALL
   bind Action version, target keys, complete scope, parameters, basis/reason,
   proposal/current-state fingerprint, idempotency reference and expected non-implications

7. ENFORCE INDEPENDENT GUARDS
   caller data access/actions-only policy
   → Action permission
   → submission criteria
   → policy-conditional Checkpoint
   → fresh TSv2 domain-authority/prerequisite/complete-set/concurrency validation

8. ACTION OR REFUSAL
   pass → one exact Action commits atomically
   fail → no edits; return exact failed premise, cure owner and continuable scope

9. RECORD FACT AND AUDIT
   write accepted factual occurrence(s)
   + one Action log
   + durable execution receipt
   preserve all reserved decisions and later outcomes as separate facts

10. FEEDBACK INTO OPERATIONS
    re-run Determine Affected Decisions / readiness / remaining exposure
    selectively recompute pipeline projections
    update application state
    route next bounded handoff
    ingest later authenticated external outcomes
```

### 8.2 Learning loop

```text
11. CAPTURE TELEMETRY, NOT TRAINING TRUTH
    Workflow Lineage records model/prompt/tool/function/action versions,
    traces, selected tool, target, parameters, refusal, latency, tokens and errors

12. OBSERVE REAL FEEDBACK
    collect operator clarification/correction,
    Action refusal, retry, rejection, override,
    downstream authenticated outcome and correction rate

13. CURATE
    minimize/redact and permission the candidate
    → domain reviewer labels expected clarification/tool/target/parameters/edits/outcome
    → record prohibited implications and defect class
    → accept into trajectory set or reject

14. GENERATE AND EXPAND
    AIP Evals defines manual and object-set-generated cases,
    executes accepted paths in Ontology simulations,
    and generates/replays controlled variations:
    clear, ambiguous, unauthorized, stale, conflicting, adversarial and correction cases

15. EVALUATE SAFELY
    AIP Evals runs all cases; edit-producing cases execute in Ontology simulations
    custom deterministic evaluators score exact behavior
    ordinary tests score deterministic Functions/Action guards/optimizer/idempotency

16. EXPERIMENT
    compare current production model, strong Palantir baselines,
    prompt/tool changes and tuned open-source candidates
    across repeated runs, holdout safety, quality, cost and latency

17. SELECT THE HOSTED LAUNCH MODEL
    compare version-pinned hosted open-source candidates under the frozen suite
    → require zero forbidden-effects/unauthorized-Action failures
    → select on exact behavior first, then latency/cost

18. CONSIDER TUNING LATER
    reviewed production evidence + measured hosted-model gap
    → separately governed M36–M40 programme
    → full deployed Evals, model card, lineage and rollback before promotion

19. OPERATE, MONITOR, ROLLBACK
    shadow/canary before production promotion
    → Workflow Lineage/log export drift monitoring
    → rollback on safety, authority, target or edit regression

20. EVOLVE LATER
    AIP Evolve may explore bounded model/prompt/workflow changes against the same suite,
    change allowlist and iteration limit
    → branch proposal + evidence
    → human release review
    → never silent production mutation
```

### 8.3 Hard learning gates

A candidate cannot ship unless all of the following hold on the frozen acceptance suite:

- exact Action/Function/tool selection meets the declared threshold;
- exact target resolution meets the declared threshold;
- exact parameter and expected-edit construction meets the declared threshold;
- material ambiguity produces clarification;
- unauthorized/reserved decisions produce abstention/routing;
- contextual authority is never inferred from job title, group membership alone or Automation identity;
- recommendation never becomes commitment without the explicit manager command;
- geometry never becomes law;
- payment order never becomes cash;
- installation/acceptance never becomes establishment;
- no generic or unapproved tool is invoked;
- every edit-producing test leaves the live Ontology unchanged;
- **zero** forbidden-effect and unauthorized-Action failures across all required iterations;
- deterministic Action/optimizer/idempotency tests pass independently of LLM scores;
- cost and latency are considered only among candidates that satisfy safety and correctness.

## 9. Asynchronous autonomy progression

| Rung | Permitted behavior | Promotion evidence | Initial status |
|---|---|---|---|
| **A0 — Interactive read** | retrieve/query/call read Functions/explain | read least privilege and citation tests | **Enabled** |
| **A1 — Interactive exact Action** | explicit authenticated manager prompt executes one exact Action | complete Action Evals, criteria/permission/function refusal tests, audit | **Enabled; accepted product bar** |
| **A2 — Async detect/recompute/route** | Automate detects change, recomputes, notifies, reconciles authenticated outcomes | idempotency/retry/fallback and owner-account monitoring | **Enabled** |
| **A3 — Async proposal/shadow** | AIP Logic/Automate stages a proposal or shadow decision; no main write | proposal quality, drift, operator disposition and no silent apply | **Enabled conditionally** |
| **A4 — Bounded autonomous manager Action** | unattended Action under explicit machine-authority policy | per-Action safety suite, canary, rollback, rate/budget, explicit governance decision | **Deferred** |
| **A5 — Cross-workflow autonomy** | chained independent decisions/effects | proves ordering/compensation and each real authority boundary | **Rejected for initial architecture; requires new design** |

Autonomy is earned per exact Action, not granted to “the agent.” No rung admits autonomous member, professional, public, private-acceptor or bank decisions.

## 10. Builder/runtime separation

| Mechanism | May build/configure/test | May appear in product runtime | May execute manager Action as product principal | May own a CORDON decision |
|---|---:|---:|---:|---:|
| Embedded AIP Chatbot | No | **Yes** | **Yes, under invoking authenticated manager and guards** | No; manager owns it |
| AIP Logic | Yes | Yes, as configured orchestration | Only through exact Action and caller authority | No |
| Automate | Yes | Yes, async support | Not initially; later only under explicit machine-authority policy | No |
| OSDK/API client | Yes | Yes | Yes, only under its authenticated caller and exact Action | No |
| AI FDE | **Yes** | **No** | **No** | **No** |
| Palantir MCP external agent | **Yes** | **No** | **No** | **No** |
| AIP Evolve | **Yes, improvement proposals** | **No** | **No** | **No** |
| Playwright | **Optional, Gate 7 UI regression only** | **No** | Only simulation/test identity | **No** |

AI FDE's per-tool approval and branch proposal UX is correct for a powerful builder agent and irrelevant to the accepted manager interaction. Palantir MCP's broad builder capabilities are likewise intentionally absent from the runtime allowlist.

## 11. Required, deferred and rejected summary

### Required now

- M01–M06 and M10: grounded, curated Chatbot read/write/clarification harness;
- M11–M21: exact orchestration, deterministic compute, TSv2 Functions/Actions, staged capacity write, four Actions, criteria and permissions;
- M23–M28: Scenarios/proposal for capacity, logs/history, external outcome ingestion, direct execution and safe Automate uses;
- M30–M35: trajectory contract, AIP Evals generation/simulation, custom evaluators, experiments and reviewed production feedback;
- M42 and M44: observability and typed integration contract.

### Required conditionally

- M03 function-backed retrieval after a measured gap;
- M07–M08 application state after Gate 7 selects the host application;
- M22 Checkpoints only for a real policy requirement;
- M36–M40 tuning, adapter and BYOM registration only after post-launch evidence opens the separate programme;
- M41 AIP Evolve only after the baseline, suite and release controls mature;
- M43 log export for production-scale drift/learning;
- M45 AI FDE and M47 Palantir MCP for governed implementation productivity, never runtime;
- M46 OSv2 user edit history on all Action-edited types as supplemental backstage audit, never factual history.

### Deferred

- M09 Commands until Gate 7 selects a paired application and safe command allowlist;
- M29 unattended manager decisions until explicit machine-authority governance and per-Action evidence exist;
- production launch until the selected hosted open-source model clears the locked Action/authority/refusal suite;
- AIP Evolve until a trustworthy acceptance suite and stable baseline exist.

### Rejected

- generic edit/status/history/arbitrary-Action tools;
- backing write Functions exposed directly;
- universal confirmation/proposal-review UX for clear authenticated manager commands;
- Checkpoints or Approvals treated as domain authority;
- Automation owner identity treated as fresh manager approval;
- multiple unordered Actions implementing one portfolio decision;
- LLM as optimizer, legal authority, professional certifier, public decision maker or bank source;
- Scenario merge as proof of domain approval;
- Action logs/telemetry as domain history or unreviewed training truth;
- manual official/cash/acceptance/establishment/completion markers;
- Playwright as the primary trajectory or learning mechanism;
- hosted model substitution when the tuned open-source model has not cleared Evals;
- AIP Evolve direct production mutation;
- AI FDE or Palantir MCP as product runtime.

## 12. Gate 6 closure criteria contributed by this ledger

This ledger closes the mechanism-purpose ambiguity when the remaining Gate 6 package accepts that:

1. the runtime tool allowlist is exactly four read Functions, curated read access, clarification and four manager Actions;
2. direct conversational execution—not generic approval UX—is binding for explicit authenticated manager commands;
3. each Action has the independent permission/criteria/function/idempotency/audit layers specified here;
4. Scenarios and Capacity Portfolio Proposal support comparison and binding, but only the manager command plus Action commits;
5. Automate is initially asynchronous detection/recompute/routing/proposal machinery, not manager authority;
6. external outcomes arrive only through authenticated, idempotent reconciliation;
7. the learning loop uses reviewed AIP Evals trajectories, simulated edits, deterministic evaluators, experiments and production curation;
8. the tuned open-source model is the required production model; BYOM is its promotion route and launch waits for hard-gate passage;
9. AIP Evolve is a later bounded builder optimizer with branch review;
10. Workflow Lineage/log export provide telemetry, never semantic truth;
11. OSDK/API preserves the same exact Action governance;
12. AI FDE and Palantir MCP remain builder tools only; and
13. Gate 7 remains closed until this mechanism architecture is accepted.

## Sources

- **[S01]** [Chatbot Studio — Retrieval context](https://www.palantir.com/docs/foundry/chatbot-studio/retrieval-context)
- **[S02]** [Chatbot Studio — Citations](https://www.palantir.com/docs/foundry/chatbot-studio/citations)
- **[S03]** [Chatbot Studio — Tools and six tool types](https://www.palantir.com/docs/foundry/chatbot-studio/tools)
- **[S04]** [Functions — Query Functions](https://www.palantir.com/docs/foundry/functions/query-functions)
- **[S05]** [Action types — Overview](https://www.palantir.com/docs/foundry/action-types/overview)
- **[S06]** [Chatbot Studio — Application state](https://www.palantir.com/docs/foundry/chatbot-studio/application-state)
- **[S07]** [Chatbot Studio — Commands as tools](https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools)
- **[S08]** [Cross-application interactivity — Commands overview](https://www.palantir.com/docs/foundry/cross-app-interactivity/commands-overview)
- **[S09]** [AIP Logic — Tools](https://www.palantir.com/docs/foundry/logic/blocks#tools)
- **[S10]** [AIP Logic — Staged writes](https://www.palantir.com/docs/foundry/logic/staged-writes)
- **[S11]** [AIP architecture](https://www.palantir.com/docs/foundry/architecture-center/aip-architecture)
- **[S12]** [Function-backed Actions](https://www.palantir.com/docs/foundry/action-types/function-actions-overview)
- **[S13]** [TypeScript v2 staged writes](https://www.palantir.com/docs/foundry/functions/typescript-v2-staged-writes)
- **[S14]** [Action submission criteria](https://www.palantir.com/docs/foundry/action-types/submission-criteria)
- **[S15]** [Action permissions](https://www.palantir.com/docs/foundry/action-types/permissions)
- **[S16]** [Restricted Views](https://www.palantir.com/docs/foundry/security/restricted-views)
- **[S17]** [Checkpoints — Overview](https://www.palantir.com/docs/foundry/checkpoints/overview)
- **[S18]** [Ontology Scenarios — Overview](https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario)
- **[S19]** [Action logs](https://www.palantir.com/docs/foundry/action-types/action-log)
- **[S20]** [OSv2 user edit history](https://www.palantir.com/docs/foundry/object-edits/user-edit-history)
- **[S21]** [Data Connection listeners — Overview](https://www.palantir.com/docs/foundry/data-connection/listeners-overview)
- **[S22]** [Automate — Overview](https://www.palantir.com/docs/foundry/automate/overview)
- **[S23]** [AIP Evals — Overview](https://www.palantir.com/docs/foundry/aip-evals/overview)
- **[S24]** [AIP Evals — Ontology edits and simulations](https://www.palantir.com/docs/foundry/aip-evals/ontology-edits)
- **[S25]** [AIP Evals — Create a suite and evaluators](https://www.palantir.com/docs/foundry/aip-evals/create-suite)
- **[S26]** [AIP Evals — Experiments](https://www.palantir.com/docs/foundry/aip-evals/experiments)
- **[S27]** [Model integration — Train a model in Code Repositories](https://www.palantir.com/docs/foundry/integrate-models/model-asset-code-repositories)
- **[S28]** [Code Workspaces — Train and interact with models](https://www.palantir.com/docs/foundry/code-workspaces/training-models)
- **[S29]** [Model adapters — Overview](https://www.palantir.com/docs/foundry/integrate-models/model-adapter-overview)
- **[S30]** [Import Hugging Face models](https://www.palantir.com/docs/foundry/integrate-models/import-huggingface-models)
- **[S31]** [Bring your own model / registered models](https://www.palantir.com/docs/foundry/aip/bring-your-own-model)
- **[S32]** [AIP Evolve — Overview](https://www.palantir.com/docs/foundry/aip-evolve/overview)
- **[S33]** [Ontology and AIP observability](https://www.palantir.com/docs/foundry/aip-observability/overview)
- **[S34]** [Observability — Overview and log export](https://www.palantir.com/docs/foundry/observability/overview)
- **[S35]** [Organization settings — Configure logging](https://www.palantir.com/docs/foundry/administration/configure-logging)
- **[S36]** [Ontology SDK — Overview](https://www.palantir.com/docs/foundry/ontology-sdk/overview)
- **[S37]** [AIP Chatbot Platform API — Agent basics](https://www.palantir.com/docs/foundry/api/aip-agents-v2-resources/agents/agent-basics)
- **[S38]** [AI FDE — Overview](https://www.palantir.com/docs/foundry/ai-fde/overview)
- **[S39]** [AI FDE — Security and governance](https://www.palantir.com/docs/foundry/ai-fde/security-and-governance)
- **[S40]** [Palantir MCP — Overview](https://www.palantir.com/docs/foundry/palantir-mcp/overview)

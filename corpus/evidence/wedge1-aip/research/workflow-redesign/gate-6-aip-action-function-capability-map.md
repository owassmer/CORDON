# Gate 6 — AIP, Action, Function and automation capability map

Status: **Gate 6 capability mapping; no Gate 7 surface selection**  
Date: 22 August 2026  
Authority: `REDESIGN_SEQUENCE.md`; `gate-5-reconciled-operator-graph.md`; `gate-5-core-ontology.md`; `gate-5-operator-decision-ledger-six-questions.md`; `gate-5-operator-capability-ledger-five-responsibilities.md`  
Research boundary: current official Palantir documentation retrieved through Palantir MCP and `palantir.com/docs`; no Foundry writes; no UI design.

**Current environment correction:** Owen confirms full TypeScript v2, AIP Chatbot Studio, AIP Logic, Automate, Scenarios, Evals, observability and related capability availability. Documentation maturity caveats do not constrain this build.

**Current interaction correction:** the accepted product bar is direct conversational execution of exact manager-owned Actions from explicit authenticated prompts. Mandatory confirmation/proposal review is not the default UX. Platform permissions, submission criteria and function-side revalidation remain mandatory; AIP clarifies ambiguity and routes decisions owned by other actors.

## 1. Executive verdict

The accepted Gate 5 model fits the current Foundry/AIP capability universe without expanding the four manager-owned Actions or four read-only Functions.

1. **All four manager operations should be exact Ontology Action types.** `Accept Cooperative Execution Mandate`, `Decide Cooperative Pursuit`, `Commit or Rebalance Intervention Capacity`, and `Dispatch Intervention` are cohesive governed transactions. They should be the only initial mutating tools exposed to AIP. An Action is the platform primitive for a single governed transaction over objects, properties and links, with parameters, rules, permissions, submission criteria and side effects ([Action types overview](https://www.palantir.com/docs/foundry/action-types/overview)).
2. **All four accepted calculations should be read-only query Functions.** Foundry query Functions are explicitly read-only and cannot modify the Ontology or external systems; API consumers must use an Action for edits ([Query Functions](https://www.palantir.com/docs/foundry/functions/query-functions#queries)). This is the correct hard boundary for `Determine Affected Decisions`, `Assess Named-Action Readiness`, `Compare Feasible Intervention Portfolios`, and `Determine Remaining Exposure`.
3. **Use function-backed Actions where the accepted atomic effect crosses linked facts, appends factual histories, or requires whole-set validation.** Standard declarative Actions remain suitable only if the complete accepted effect and refusal contract can be represented directly. The current four contracts are sufficiently coupled that function backing is the safer baseline; `Commit or Rebalance Intervention Capacity` definitively requires it.
4. **AIP may reason with all four Functions and directly execute all four exact Actions from explicit authenticated manager commands.** Execution remains under the invoking principal's permissions, contextual authority, submission criteria, shared prerequisite kernel, premise fingerprint and idempotency contract. Chatbot Studio exposes separate Action and Function tool types ([Chatbot Studio tools](https://www.palantir.com/docs/foundry/chatbot-studio/tools#types-of-tools)). Ambiguity requires clarification; background AIP/Automate remains proposal/routing-only initially.
5. **AIP remains read-only or proposal-only for every reserved decision.** Member election, technician certification, beneficiary release, executor attestation, private acceptance, public eligibility/concession/permit/compliance/payment decisions and bank settlement are not among the four accepted Actions. AIP may assemble a bounded package, route it to the true owner, and consume a received authoritative outcome. It cannot make the outcome true.
6. **Automate should detect, recompute, route and stage—not autonomously take the four material manager decisions at initial release.** Automate can continuously or periodically evaluate object conditions and execute Actions, Functions, AIP Logic and notifications ([Automate overview](https://www.palantir.com/docs/foundry/automate/overview)). Its Action effects run as the automation owner and use that owner's submission eligibility ([Automate action permissions](https://www.palantir.com/docs/foundry/automate/effect-actions#permissions)); this identity model is not equivalent to fresh human approval by the current decision owner.
7. **The safe manager-owned progression is `explicit authenticated command → resolve exact target/scope → validate again → apply atomically → log → recompute`.** Ambiguity produces clarification. Decisions owned by another actor are prepared and routed. Ontology Scenarios may add a sandbox for materially useful alternatives, but they do not replace production authority. Scenario edits remain isolated until separately merged, and submission criteria can distinguish Scenario execution from main-Ontology execution ([Ontology Scenarios](https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario#global-branching-vs-ontology-scenarios)).

## 2. Provenance classes

This document uses three explicit classes.

- **Fetched fact** — directly supported by the cited current official Palantir documentation.
- **CORDON inference** — the mechanism selection or safety consequence derived by applying a fetched capability to the accepted Gate 5 semantic and authority contracts.
- **Enrollment-dependent unknown** — capability availability, maturity or configuration that official documentation says is beta/experimental, can be disabled, or otherwise requires confirmation in the target enrollment.

No cited platform capability changes the accepted domain owner of a decision.

## 3. Current platform capability baseline

### 3.1 Ontology Actions

**Fetched facts.** An Action is a single governed transaction that can create, modify or delete objects and links; the same logic and validations are reusable across consuming applications ([Action types overview](https://www.palantir.com/docs/foundry/action-types/overview)). Action types combine parameters, rules, submission criteria and side effects. Submission criteria govern whether an Action may be submitted and can combine parameter, object/relation and current-user context; every criterion must pass independently of permission to edit the Action definition ([Submission criteria](https://www.palantir.com/docs/foundry/action-types/submission-criteria#submission-criteria)). Criteria may also distinguish execution inside an Ontology Scenario from execution against the main Ontology ([Scenario execution context](https://www.palantir.com/docs/foundry/action-types/submission-criteria#execution-context)).

**CORDON inference.** Action permission is necessary but not sufficient. Every manager Action must enforce:

- exact acting Party and the user's authority basis for the target, scope and effective time;
- typed target identity and a complete bounded scope;
- accepted prerequisite/refusal conditions;
- a previewable intended edit set;
- one atomic semantic effect;
- no edits to excluded public, member, professional, financial or biological truth.

Use submission criteria for coarse, inspectable gates—required inputs, eligible user/group, target identity, obvious current-object conditions and main-vs-Scenario context. Recheck the complete refusal contract inside the function-backed Action at execution time. Submission criteria alone are not an adequate implementation of proposition-specific authority, full affected-population completeness, cross-object feasibility or action-specific readiness.

### 3.2 Standard versus function-backed Actions

**Fetched facts.** Standard Actions express direct rules over object/property/link edits. Function-backed Actions replace declarative rules with a Function for logic that cannot be represented directly, including modification of linked objects, multi-type creation/linking and complex business logic ([Function-backed Action overview](https://www.palantir.com/docs/foundry/action-types/function-actions-overview)). TypeScript v2 edit Functions build and return an explicit edit batch and can create, update, delete, link and unlink objects ([TypeScript v2 Ontology edits](https://www.palantir.com/docs/foundry/functions/typescript-v2-ontology-edits)). Regular TypeScript v2 edit batches do not expose edits to reads within the same execution. Staged-write Functions, currently beta, stage nested edits together, provide read-after-write within the execution and commit atomically only after successful completion; errors discard the staged edits ([TypeScript v2 staged writes — atomic execution](https://www.palantir.com/docs/foundry/functions/typescript-v2-staged-writes#atomic-execution)).

**CORDON rule.** Prefer a standard Action only if all of the following are true:

1. the accepted effect is a direct create/update/link operation over a small explicit target set;
2. no append/reversal reducer over typed history is required;
3. no complete-population or cross-object invariant must be proven;
4. the complete refusal contract is expressible and reviewable without hidden function scope; and
5. resulting history and contextual authority remain semantically correct.

Otherwise use a function-backed Action. The backing Function is not a fifth mutating tool; it is the implementation of the named Action and must not be independently exposed as a write Function.

### 3.3 Action logs and semantic history

**Fetched facts.** Action logs model Action submissions as Ontology objects. Log object types map one-to-one to Action types; one submission creates one log object linked to every edited object. The default schema includes Action RID, Action type RID/version, timestamp, submitting user and edited-object primary keys, with optional summary, parameter values and selected contextual values ([Action log](https://www.palantir.com/docs/foundry/action-types/action-log#action-log-ontology), [Action log schema](https://www.palantir.com/docs/foundry/action-types/action-log#action-log-schema)). Function-backed Actions require configured `Edits` provenance for Action-log support ([Function-backed Action logs](https://www.palantir.com/docs/foundry/action-types/action-log#action-log-on-functionbacked-action-types)). Edit history is the separate mechanism for logging all object edits ([Action log](https://www.palantir.com/docs/foundry/action-types/action-log#action-log)).

**CORDON inference.** Enable one Action log per manager Action, recording decision reference, exact scope, authority/basis reference, reason where accepted, action version and edited object keys. The Action log supplements but never replaces the five accepted factual histories. The domain histories preserve the consequential occurrence and outcome regardless of whether it arrived via Action, source ingestion or external authority feed. Action logs preserve platform submission/audit context. Do not infer legal, financial or biological consequence from the existence of a log record.

### 3.4 Ontology Scenarios

**Fetched facts.** Ontology Scenarios are sandboxes for humans and agents to apply edits without changing main Ontology data; scenarios can be compared and their edits merged to main separately. Submission criteria can allow more permissive Scenario execution while keeping production application restricted, and the merge Action has its own criteria ([Ontology Scenario overview](https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario#global-branching-vs-ontology-scenarios)). OSDK can apply an Action through a scenario client; those edits remain isolated until merge, and batch Actions are not supported inside a Scenario ([OSDK Scenario Actions](https://www.palantir.com/docs/foundry/ontology/osdk-scenario#apply-actions-within-a-scenario)).

**CORDON inference.** Scenarios are appropriate for:

- testing capacity portfolios and alternatives;
- rehearsing a proposed pursuit/capacity/dispatch effect;
- comparing downstream readiness and remaining exposure under a hypothetical fact set; and
- allowing an agent to explore edits it cannot apply to main.

A Scenario is not evidence that the manager approved the decision. Merge authority must be at least as strict as the corresponding production Action. Because scenario batch Actions are unsupported, do not rely on Scenario execution for the multi-Commitment portfolio transaction unless one function-backed Action can preserve the whole edit set and the target enrollment validates the behavior.

## 4. Mapping the four manager-owned Actions

| Accepted Action | Recommended current mechanism | Why standard rules are insufficient or fragile | Submission and execution gates | AIP/automation posture | Action-log and semantic-history result |
|---|---|---|---|---|---|
| **Accept Cooperative Execution Mandate** | **Function-backed Action; explicit authenticated manager command required.** | The Action appends an acceptance/refusal occurrence, activates only accepted cooperative authority for bounded scope/term, preserves refusal/fallback and cannot manufacture the member's grant. | Exact current authority; real member grant; received participation; determinate scope, term, powers, exclusions, conflicts and fallback. | The manager's explicit command is the decision. AIP clarifies ambiguity and invokes the exact Action directly after guardrails pass. Background Automate may prepare/route but does not auto-apply initially. | One Action log; factual Instrument occurrence; accepted contextual authority only. |
| **Decide Cooperative Pursuit** | **Function-backed Action; explicit authenticated manager command required.** | Writes one bounded pursue/defer/refuse fact, Pursuit history, fallback and reconsideration. | Exact authority; received member choice; accepted mandate; valid Programme route/scope; known fallback/deadline; no unresolved conflict. | AIP may recommend and explain. The explicit manager command selects and executes the exact outcome/scope. | One Action log; mutate Pursuit only; append Pursuit Decision Record. |
| **Commit or Rebalance Intervention Capacity** | **Scenario comparison + immutable Capacity Portfolio Proposal + TSv2 staged-write Action; explicit manager command required.** | Atomically creates/changes/releases/reallocates the complete affected Commitment set and appends change records. | Complete population; feasible plan; current fingerprint; protected Commitments; exact authority/override reason; ≤10,000 edits. | AIP compares Scenarios and explains the Proposal. The manager commands the Proposal ID; the Action loads it server-side, revalidates and commits once. | One portfolio Action log; per-Commitment records; shared decision reference and durable receipt. |
| **Dispatch Intervention** | **Function-backed Action; explicit authenticated manager command required.** | Validates exact target/authority/readiness, then appends bounded dispatch history and optional work-order Instrument. | Exact dispatcher/executor authority; Parcel/Plant scope; design, access, permits, capacity, resources, finance/evidence and clocks. | AIP resolves and executes a clear dispatch command directly; ambiguity requires clarification. Background Automate may prepare/route only initially. | One Action log; Intervention dispatch occurrence; never performance, acceptance or establishment. |

### 4.1 Function implementation choice

**CORDON inference.** TypeScript v2 is the preferred baseline for all four backing Functions because its explicit edit batches make the touched types and links reviewable, and staged writes provide atomic nested execution where enrolled. The generated edit union must include every object/link type touched. The function must return only the accepted edits and throw a user-facing refusal for unresolved authority or premises.

**Enrollment-dependent unknown.** AIP Logic staged writes and TypeScript v2 staged writes are documented as beta and may not be enabled. If unavailable, use a regular function-backed Action only after proving that one returned edit set commits atomically and that no read-after-write dependency exists. Do not approximate the capacity transaction with multiple Actions. If the target enrollment cannot atomically edit the complete Commitment set, Gate 6 must selectively reopen a technical portfolio backing resource or another supported transaction mechanism.

## 5. Mapping the four read-only Functions

All four should be published as API-named query Functions. Query Functions cannot edit the Ontology or external systems ([Query Functions](https://www.palantir.com/docs/foundry/functions/query-functions#queries)); they can be called from generated OSDK function definitions and return typed results ([TypeScript OSDK Functions](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk#functions)). AIP receives each as a distinct Function tool, never a generic “run CORDON logic” tool.

| Accepted Function | Recommended implementation and typed result | Consumers | Required tests and safety boundary |
|---|---|---|---|
| **Determine Affected Decisions** | TS v2 query Function over one changed fact/history occurrence plus current graph. Return affected decision/Action IDs, dependency paths, indeterminacies, scoped holds/reopenings, next owners and explicitly unaffected work. | AIP Logic, Chatbot Function tool, Automate Function effect after material changes, OSDK/API. | Golden change-impact cases; no mutation; no premise correction; no generic status reset. Verify both affected and unaffected sets. |
| **Assess Named-Action Readiness** | TS v2 query Function with a discriminated input for the exact Action, target/scope/actor/time and typed prerequisite profile. Return ready/not-ready/indeterminate, satisfied conditions, blockers/cure owners, wait/act consequences and continuable scope. | Human review packages, AIP Function tool, Action preflight, Automate detection, OSDK/API. | One refusal test per Action prerequisite and authority edge. Output is advisory/preflight: the Action's submission criteria/backing Function revalidate at application. Never store global readiness. |
| **Compare Feasible Intervention Portfolios** | Deterministic code-authored query Function over the complete affected Intervention population, current Commitments, capacities, policy constraints, safeguards, fallback, objective inputs and uncertainty. Return best feasible portfolio, materially equivalent alternatives, binding constraints, infeasible reasons, consequences, uncertainty/sensitivity and tie-break use. | Manager decision support, Scenario analysis, AIP Function tool for explanation, OSDK/API. | Complete-population assertion; constraint/property tests; deterministic replay; sensitivity and tie tests. No LLM selects or scores the authoritative portfolio; no edit or Commitment creation. |
| **Determine Remaining Exposure** | TS v2 query Function over bounded context and factual histories. Return four independent legal, operational, financial and biological lines, each with achieved/residual scope, next owner, clock and indeterminate premise. | AIP/Chatbot explanation, Automate notification/recompute, OSDK/API. | Tests that order ≠ cash, installation acceptance ≠ establishment, and one completed line cannot close another. No global completion state or reopening mutation. |

### 5.1 Why not use AIP Logic as the source of truth for these Functions

AIP Logic is useful for LLM-assisted orchestration, extraction, explanation and proposal construction. The four accepted Functions, however, define stable typed decision support contracts. Deterministic authority traversal, prerequisite evaluation, constrained portfolio comparison and independent exposure reduction should live in code-authored Functions with versioned tests. AIP Logic may call them and explain their outputs; it must not reproduce their core logic in prompts.

### 5.2 API and version boundary

**Fetched facts.** API-named queries can be called through the API gateway and OSDK. Query Functions always resolve to the latest tagged version rather than semantic version ranges; changing/removing an API name can immediately break consumers ([Query Functions](https://www.palantir.com/docs/foundry/functions/query-functions)).

**CORDON inference.** Freeze each public query API name and typed response contract. Introduce a new API name for a breaking change. Keep the backing repository and imported Ontology resources permissioned to every intended caller. Functions require repository Viewer access, while end users of a function-backed Action need not necessarily have direct read access to its backing Function once the Action is configured ([Function permissions](https://www.palantir.com/docs/foundry/functions/permissions#function-permissions)).

## 6. Seven-operation AIP harness

The seven operations are an authorization envelope, not seven mutable Ontology Actions and not a linear workflow state machine. They consist of three cross-actor harness capabilities plus the four accepted manager Actions.

| # | Harness operation | Platform mapping | May AIP execute? | Hard boundary |
|---:|---|---|---|---|
| **H1** | **Prepare/stage a bounded decision package** | Call the four read-only Functions; optionally use AIP Logic/Chatbot retrieval and Function tools to assemble target, scope, authority basis, evidence references, blockers, consequence, reason and exact proposed Action parameters. May stage an Automate/AIP Logic proposal. | **Yes, read-only/proposal-only.** | Preparation creates no election, certification, filing, commitment, dispatch, acceptance, authority outcome or settlement. |
| **H2** | **Route to the real decision owner** | Resolve owner with graph/Function logic; send a permission-aware notification, initiate an approved outbound webhook, or hand off through an external-system integration. | **Yes, if routing authority and recipient are valid.** | Routing transfers a package, never decision authority. A failed/absent notification is not an outcome. |
| **H3** | **Accept Cooperative Execution Mandate** | Exact function-backed Ontology Action. | **Explicit authenticated authorized-manager command; direct execution after guards pass.** | Cannot create member grant, eligibility, concession, capacity or creditor identity. |
| **H4** | **Decide Cooperative Pursuit** | Exact function-backed Ontology Action. | **Explicit authenticated authorized-manager command; direct execution after guards pass.** | Cannot create eligibility, concession, capacity, filing or execution truth. |
| **H5** | **Commit or Rebalance Intervention Capacity** | Exact staged-write Action over one immutable Proposal and complete affected set. | **Explicit authenticated authorized-manager command naming the Proposal; direct execution after guards pass.** | Cannot partially apply, auto-convert recommendation, or alter duty/public right/fallback/dispatch authority. |
| **H6** | **Dispatch Intervention** | Exact function-backed Ontology Action. | **Explicit authenticated authorized-manager command; direct execution after guards pass.** | Cannot infer readiness, performance, acceptance or establishment from the dispatch submission. |
| **H7** | **Receive/record a bounded external outcome and recompute** | Prefer authoritative source ingestion/public API/listener → stream/pipeline or controlled integration → factual history update; then call `Determine Affected Decisions` and `Determine Remaining Exposure`. A manually transacted non-manager Action is not admitted initially. | **AIP may parse, reconcile, flag and propose mapping; it may not manufacture the outcome.** Automatic ingestion is allowed only for authenticated, schema-validated authoritative messages. | No manual “record official truth” or “mark paid/accepted” tool. If a real actor later transacts through CORDON, admit one exact Action only after proving actor, authority, target, scope, refusal and atomic effect. |

## 7. Safe progression: explicit command → exact binding → apply

### 7.1 Required state transition

```text
explicit authenticated manager command
→ read current graph and authoritative histories
→ run exact read-only Function(s)
→ resolve exact Action, target/proposal, scope and parameters
→ bind immutable message ID, Action version, target count, premise fingerprint and idempotency key
→ validate submission criteria and complete refusal contract again
→ apply one exact Action atomically
→ return durable committed/already-committed/refused/clarification receipt
→ write Action log + accepted factual occurrence
→ recompute affected decisions/readiness/exposure
→ notify or route the next bounded handoff
```

### 7.2 Execution controls

- **Chatbot Studio:** configure only four exact Action tools, four exact Function tools, curated read access and clarification. A clear manager command directly executes one Action under the invoking user; changed/deictic context clarifies instead. Enforce one mutation per turn and durable receipt recovery.
- **AIP Logic + Automate:** use Logic for bounded orchestration. Background Automate detects, recomputes, prepares, routes and notifies but does not auto-apply manager Actions initially. Asynchronous proposals remain available for handoffs.
- **OSDK/API:** use validate-only to construct the execution binding where useful, then perform fresh validate-and-execute under the same caller/message/target/fingerprint contract. The API/OSDK path does not eliminate criteria, permissions or function validation.
- **Scenarios:** optionally apply the Action to a Scenario for consequence testing; production merge remains a distinct governed Action. Never treat scenario acceptance as the real actor's domain decision.

### 7.3 No stale command

**CORDON inference.** The command binds to the exact originating message, Action version, target/Proposal, parameters, authority/basis, consequence summary and current-data fingerprint. If any material premise or selected context changes before apply, require clarification or refuse. `Assess Named-Action Readiness` and the shared prerequisite kernel run on current state; the Action performs final checks at apply.

### 7.4 Idempotency and retry

**Fetched fact.** Automate effects have at-least-once rather than exactly-once semantics and can execute more than once; Actions/Functions used by Automate must be idempotent or explicitly detect duplicates ([Automate execution guarantees](https://www.palantir.com/docs/foundry/automate/effect-settings#execution-guarantees)). Multiple configured Action effects may run in any order ([Action-effect configuration](https://www.palantir.com/docs/foundry/automate/effect-actions#configuration)).

**CORDON inference.** Every prepared proposal and external outcome needs a stable idempotency/occurrence reference. A retried accepted Action must either yield the same bounded result or refuse because the occurrence/portfolio-decision reference already exists. Never implement the capacity rebalance as several effects. External outcome ingestion deduplicates on authenticated source occurrence identity, not LLM similarity.

## 8. Automate mapping

### Safe initial uses

- detect object-set or scheduled material changes;
- call `Determine Affected Decisions` and notify the relevant owner;
- call `Assess Named-Action Readiness` and stage a review package when blockers clear;
- periodically recompute feasible portfolios or remaining exposure;
- process low-throughput listener events and initiate authenticated outcome reconciliation;
- stage one of the four exact Actions as a proposal;
- send notifications and execute fallback effects on failures.

### Unsafe initial uses

- automatically accept mandates, choose pursuit, commit/rebalance capacity or dispatch;
- use the automation owner's standing as a substitute for the current human decision owner's approval;
- chain multiple Actions while assuming execution order;
- turn an AIP Logic output into an authoritative external outcome;
- infer member/public/professional/private decisions from silence, message text or data arrival;
- retry a non-idempotent external write without an occurrence key.

**Fetched facts.** Automate conditions may be time-based, Ontology-object-data-based or combined, and effects include Actions, Functions, AIP Logic and notifications ([Automate overview](https://www.palantir.com/docs/foundry/automate/overview)). Action/Function/Logic effects execute as the automation owner; audit and edit history attribute the edits to that owner ([Automate permissions](https://www.palantir.com/docs/foundry/automate/permissions#permissions-for-executions)). An Action can be disabled as an Automate consumer in Ontology Manager ([Action visibility settings](https://www.palantir.com/docs/foundry/automate/effect-actions#action-visibility-settings)).

**CORDON inference.** Disable direct Automate submission for all four production Actions unless the target enrollment proves a proposal-only configuration that cannot silently fall back to automatic apply. Read-only Functions, notifications and proposal creation may run automatically.

## 9. AIP Logic, Chatbot/Agent and exact tool policy

### 9.1 Exact tools AIP may receive

**Read tools**

1. `Determine Affected Decisions`
2. `Assess Named-Action Readiness`
3. `Compare Feasible Intervention Portfolios`
4. `Determine Remaining Exposure`
5. narrowly configured object query/retrieval over the accepted graph and accessible backstage basis references

**Write tools, explicit manager command required**

1. `Accept Cooperative Execution Mandate`
2. `Decide Cooperative Pursuit`
3. `Commit or Rebalance Intervention Capacity`
4. `Dispatch Intervention`

No generic object-edit, history-append, status-update, apply-arbitrary-Action or external-outcome-recording tool is admitted.

### 9.2 AIP Logic role

AIP Logic may orchestrate retrieval, call read Functions, extract bounded candidate facts, explain results, construct an exact Action call and stage it for review. With staged writes, nested calls and edits can participate in one atomic execution, but staged writes are beta and must be wrapped in an Action for Automate ([AIP Logic staged writes](https://www.palantir.com/docs/foundry/logic/staged-writes#staged-writes-in-aip-logic), [Using staged-write Logic in Automate](https://www.palantir.com/docs/foundry/logic/staged-writes#using-stagedwrite-logic-functions-in-automate)).

AIP Logic must remain read-only/proposal-only when:

- the real decision owner is a member, technician, beneficiary, executor, private acceptor, bank/treasury or public authority not transacting through CORDON;
- the premise is source-owned and no authenticated authoritative correction has arrived;
- authority, scope, effective date or decision consequence is materially indeterminate;
- the requested effect is not exactly one of the four accepted Actions;
- complete-population, atomicity or idempotency requirements cannot be proven; or
- enrollment capabilities needed for safe staged review are unavailable.

### 9.3 Chatbot/Agent behavior

**Fetched facts.** Chatbot Studio tool types include Action, object query, Function, application-variable update, command and clarification. Action tools can execute automatically or after confirmation; Function tools can call Foundry Functions and published AIP Logic Functions ([Chatbot Studio tools](https://www.palantir.com/docs/foundry/chatbot-studio/tools#types-of-tools)). Tools give the LLM control-flow/input construction capability; native tool calling can call supported tool types in parallel ([Tool mode](https://www.palantir.com/docs/foundry/chatbot-studio/tools#tool-mode)).

**CORDON inference.** Parallel native tool calls are safe only for independent reads. Enforce at most one mutating tool per conversational turn and never decompose a portfolio transaction. The agent requests clarification rather than fills unresolved authority/scope/reason fields. Tool documentation includes each Action's non-implications and refusal conditions. Direct execution requires the immutable message/Action/target/fingerprint/idempotency binding and durable receipt.

## 10. Contextual review and Checkpoints

Palantir documents Checkpoints and proposal review for contexts that require durable acknowledgement, justification or asynchronous review. CORDON does not make either mechanism universal approval UX. A clear authenticated manager command invokes the exact Action directly. Checkpoints enter only for a named policy duty. Proposal review remains available for asynchronous or other-actor handoffs and never grants domain authority. Branch review governs software changes, not runtime manager decisions.

## 11. Evals, tests and observability

### 11.1 Evals and deterministic tests

**Fetched facts.** AIP Evals evaluates AIP Logic, Chatbot and code-authored Functions; it supports test cases, evaluation criteria, model comparison, iteration and variance analysis for nondeterministic LLM workflows ([AIP Evals](https://www.palantir.com/docs/foundry/aip-evals/overview)).

**CORDON test split.** 

- Use ordinary unit/property/integration tests for the four deterministic Functions, Action refusal logic, edit-set completeness, idempotency and history reducers.
- Use AIP Evals for proposal quality: correct target/Action selection, authority abstention, complete evidence citation, exact parameter construction, refusal on missing premises, non-implication language and escalation to the real owner.
- Include adversarial cases in which the LLM is invited to call a generic edit, infer public approval, infer cash from order, infer establishment from acceptance, omit protected Commitments, or treat geometry as law.
- Promotion requires zero unauthorized Action calls and zero reserved-decision fabrication in the acceptance suite. Quality scores cannot offset a safety violation.

### 11.2 Observability

**Fetched facts.** AIP observability in Workflow Lineage provides metrics, execution history, distributed traces, logs and log search across Functions, Actions, Automations, AIP Logic, models and Ontology loads. Current documentation identifies near-real-time success/failure and P95 duration metrics, 30-day execution history, traces across nested operations, token/prompt/error logs and export to a streaming dataset ([AIP observability](https://www.palantir.com/docs/foundry/aip-observability/overview#key-capabilities-of-aip-observability)). Action-specific monitoring and metrics are also documented ([AIP observability — platform monitoring](https://www.palantir.com/docs/foundry/aip-observability/overview#monitoring-performance-and-optimization)).

**CORDON minimum telemetry.** Monitor:

- Function latency, failures, indeterminate-result rate and population size;
- Action validation failures by refusal class;
- proposal created/approved/rejected/expired and time-to-review;
- edit count and touched object types per Action;
- duplicate/idempotency refusals;
- Automate retries/fallbacks and owner-account failures;
- external webhook/listener delivery, signature validation, deduplication and outcome-reconciliation failures;
- model/tool versions, proposal reason, selected exact tool and human disposition;
- drift in AIP Evals and production proposal rejection/override patterns.

Observability is operational evidence, not semantic history. Thirty-day execution history or service logs cannot be the sole durable record of mandate, pursuit, commitment, dispatch, official outcome, cash or establishment.

## 12. Webhooks, listeners and external systems

### 12.1 Outbound

**Fetched facts.** Action side effects include notifications and webhooks. Webhooks connect Actions to external REST/ERP systems; a writeback webhook runs before Foundry edits, while a side-effect webhook runs after edits ([Action webhooks](https://www.palantir.com/docs/foundry/action-types/webhooks), [Set up webhook](https://www.palantir.com/docs/foundry/action-types/set-up-webhook#steps)). A side effect supports decision orchestration when another system is the source of truth ([Side effects overview](https://www.palantir.com/docs/foundry/action-types/side-effects-overview)).

**CORDON mapping.**

- Use a **writeback webhook** only when the external system must accept/validate the same transaction before Ontology edits commit and its returned value is needed for the Action. Failure must block the Action.
- Use a **post-edit side-effect webhook** for best-effort synchronization/notification where failure must not undo the accepted Ontology decision; monitor and retry separately.
- Do not use an outbound webhook to impersonate a member, technician, beneficiary or authority. The endpoint and caller credentials must represent the actual authorized channel.
- For dispatch, an external work-order API may be part of the exact Action only if its transactional and idempotency behavior is proven. Otherwise create the governed internal dispatch occurrence and synchronize asynchronously with explicit failure exposure.

### 12.2 Inbound

**Fetched facts.** HTTPS listeners receive external webhook requests, verify provider-specific signing/authentication and write events to streams. The stream can feed Automate, streaming pipelines or batch processing ([Listeners overview](https://www.palantir.com/docs/foundry/data-connection/listeners-overview#listeners), [HTTPS listeners](https://www.palantir.com/docs/foundry/data-connection/listeners-https#https-listeners)). Stream-triggered Automate is intended for low-throughput, stateless processing where a few seconds of latency and at-least-once behavior are acceptable; streaming pipelines can support stateful, higher-throughput and optionally exactly-once processing ([Listener event processing](https://www.palantir.com/docs/foundry/data-connection/listeners-event-processing#stream-processing-with-automate), [Streaming pipelines](https://www.palantir.com/docs/foundry/data-connection/listeners-event-processing#streaming-pipelines)). If an external system can be customized, Palantir recommends the public API rather than a listener ([When to use listeners](https://www.palantir.com/docs/foundry/data-connection/listeners-overview#when-the-external-system-cannot-be-customized)).

**CORDON mapping.** Inbound authenticated events are the preferred path for H7 received outcomes. The pipeline must preserve source occurrence identity, raw payload/evidence reference, signer/channel, effective time and validation result. It may map a qualified event into the correct Instrument/Proceeding/Intervention/Pursuit/Commitment history. AIP may assist classification, but an uncertain mapping stages a reconciliation proposal; it does not write authoritative truth.

## 13. OSDK and public API invocation

### Read path

- Call the four generated query definitions through OSDK `executeFunction` ([TypeScript OSDK Functions](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk#apply-function)).
- API-named query Functions expose the same read-only contract through the API gateway ([Query Functions](https://www.palantir.com/docs/foundry/functions/query-functions#queries)).
- Carry the caller's scoped identity and preserve typed results; do not expose a raw query endpoint that bypasses object access.

### Action path

- Generated OSDK Actions call `applyAction`; use validate-only for preflight and validate-and-execute only after approval ([TypeScript OSDK migration](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk-migration#typescript-osdk-20)).
- Public API/OSDK invocation still uses the Action's permissions and submission criteria. It is not a back door to direct edits.
- A scenario client can apply an Action to isolated scenario state; merging to main is separately governed ([OSDK Scenario Actions](https://www.palantir.com/docs/foundry/ontology/osdk-scenario#apply-actions-within-a-scenario)).

### External/public application constraint

**Enrollment/product constraint.** Palantir Consumer Mode public applications currently support Apply Action only with restrictions: function-backed Actions, batch Actions and webhooks are blocked, and Function/query execution is not supported ([Public application supported features](https://www.palantir.com/docs/foundry/consumer-mode/public-application-supported-features#supported-operations), [Unsupported public-application operations](https://www.palantir.com/docs/foundry/consumer-mode/public-application-supported-features#not-currently-supported)). Therefore a Consumer Mode public application cannot host the full CORDON harness as mapped. This does not select a Gate 7 surface; it is a capability exclusion.

## 14. Reserved decisions: exact AIP boundary

| Decision/outcome family | Initial AIP permission | Permitted harness behavior | Mutation admission rule |
|---|---|---|---|
| Member participation, withdrawal, funding-source election | Read received result; prepare and route proposal only | Explain alternatives; prepare bounded election package; route to member/authorized representative | Add exact Action only if that actor actually authenticates/transacts through CORDON and actor/scope/authority/refusal/effect are proven. |
| Technician design/certification or completion assertion | Read; stage/route only | Assemble facts and unresolved premises; request attributable professional assertion | Same selective admission rule; never have the LLM synthesize the professional judgment. |
| Beneficiary application or payment-claim release | Read; stage/route only | Prepare cited filing/claim and validate readiness; route to beneficiary/authorized representative | Exact release Action only if CORDON is the real filing channel and receipt remains distinct from authority outcome. |
| Executor performance attestation | Read; stage/route only | Prepare as-built evidence package; route to assigned executor | Exact attestation Action only for authenticated executor and exact performed scope. |
| Private contractual acceptance | Read; stage/route only | Prepare acceptance/defect evidence and route to assigned acceptor | Exact Action only if the contract-assigned acceptor transacts through CORDON. |
| Public condition, duty, eligibility, concession, permit, compulsory/funded acceptance, liquidation/order/audit/recovery | **Read-only/external outcome.** | Prepare application/referral; route; ingest qualified decision; recompute | No Action unless the competent authority itself uses CORDON under its authority. Never expose to cooperative manager or generic AIP agent. |
| Bank/treasury cash settlement, return, reversal or recovery collection | **Read-only authenticated fact.** | Ingest and reconcile authenticated transaction occurrences | No manual `Record settlement` Action. |
| Bounded biological establishment | Read, prepare and route review | Assemble accepted installation scope, assigned reviewer and observations; ingest reviewer outcome | Conditional exact Action only if the assigned reviewer actually uses CORDON. |

## 15. Implementation behavior to prove before release

1. **AIP Logic staged-write behavior and direct-execution integration.** Capability is available; prove exact semantics and Evals coverage.
2. **TypeScript v2 staged-write Action binding and maximum practical edit set.** Capability is available; prove atomic capacity rebalance with expected population, histories and links.
3. **Ontology Scenario suitability for multi-Commitment comparison.** Capability is available; prove that disposable comparison state and the immutable executable Proposal remain distinct.
4. **Proposal-only enforcement in Automate for each function-backed/staged-write Action.** Prove there is no configuration or failure path that auto-applies after a proposal was intended.
5. **Exact Chatbot Studio direct-execution and principal propagation behavior.** Verify explicit-command binding, one mutation per turn, clarification on changed/deictic context, durable receipt recovery and prevention of unintended background auto-apply.
6. **Action-log support for every selected function-backed implementation.** Verify complete `Edits` provenance, links to all edited objects and permission behavior.
7. **Struct-array/history mutation and reversal performance.** Prove stable occurrence references, exact Plant phase scopes, append/reversal reducers and query performance. If not, selectively reopen a hidden history backing resource or focused event type.
8. **Cash partial/return/reversal representation.** Prove Proceeding history can preserve transaction identity and exact allocation; otherwise selectively reopen a focused cash occurrence.
9. **Listener enrollment, ingress/security approval and provider signing support.** HTTPS listeners are GA, but ingress and connection setup remain administrative prerequisites; WebSocket listeners are experimental and email listeners beta ([Listener types](https://www.palantir.com/docs/foundry/data-connection/listeners-overview#types-of-listeners)).
10. **AIP Evals and AIP observability access/retention/log permissions.** Confirm the intended resources, model/tool trace visibility, export policy and sensitive prompt/input handling.
11. **External-system transaction semantics.** Establish idempotency, acknowledgement, reversal and authoritative-result contracts for every writeback webhook/API before coupling it to an Action.
12. **Function resource/performance envelope.** Benchmark complete-population portfolio comparison and cross-history exposure computation; a live Function must not become an unbounded population pipeline.

## 16. Unsafe or unavailable mechanisms

- One generic `Execute CORDON Action`, generic object edit, generic status update, generic history append or generic external-outcome record tool.
- Direct AIP mutation of member, professional, beneficiary, executor, private-acceptor, bank or public-authority outcomes.
- Automatic execution of the four manager Actions at initial release.
- Treating an Automate owner as fresh runtime approval by the real decision owner.
- Multiple Action effects as an ordered or atomic capacity portfolio transaction.
- Direct invocation of a write-capable backing Function outside its exact Action.
- AIP Logic prompts as the authoritative implementation of deterministic applicability, readiness, portfolio feasibility or remaining exposure.
- A Scenario merge as proof of the underlying domain decision.
- Action logs, observability traces or service logs as replacements for accepted factual histories.
- Manual settlement, paid, accepted, compliant, established or complete markers.
- Unauthenticated/unverified listener payloads as authoritative outcomes.
- Consumer Mode public applications for the full harness, because current support excludes Functions and function-backed Actions.
- WebSocket listeners for this initial harness: experimental and unnecessary for the accepted low-frequency administrative/field outcomes.

## 17. Gate 6 capability conclusion

Current Foundry/AIP supports the accepted split:

- **four exact, governed, function-backed manager Actions;**
- **four exact, typed, read-only query Functions;**
- **AIP preparation, reasoning, clarification and direct exact-Action execution for explicit manager commands;**
- **Automate for detection, recomputation, notification, routing and asynchronous proposals without initial manager-Action autonomy;**
- **Action logs plus domain factual histories;**
- **OSDK/API invocation without bypassing Action governance;** and
- **authenticated listener/API ingestion for external outcomes.**

The platform does not justify Action sprawl or expanded decision authority. AIP can use the four accepted Actions as exact tools only when the real authorized principal is present and the configured human review gate is satisfied. Everywhere else it remains read-only, stages a bounded proposal, routes to the true owner, or ingests a qualified received outcome. The safe default is therefore **prepare → route → human approve → revalidate → apply atomically**, with any increase in autonomy earned later through Evals, production observability, idempotent execution and explicit governance—not inferred from technical availability.

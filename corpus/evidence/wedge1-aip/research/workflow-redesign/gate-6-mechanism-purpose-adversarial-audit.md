# Gate 6 mechanism-purpose adversarial audit

Status: **FAIL — Gate 6 cannot close until the bounded corrections in §10 are incorporated**  
Date: 23 August 2026  
Scope: accepted Gate 5 graph; current Gate 6 reconciliation and capability maps; current official Foundry/AIP capability breadth  
Constraint: read-only research; no Foundry writes; no Gate 7 reopening

**Reconciliation note:** The authoritative Gate 6 reconciliation now incorporates the eight contracts in §10. Owen overrides F8's optional-fine-tuning recommendation: the tuned open-source model is mandatory for production, hosted models are benchmarks only and launch waits for hard-gate passage. Owen also replaces Playwright trajectory generation with AIP Evals Ontology-simulation trajectories; Playwright remains optional Gate 7 UI regression. F6 is resolved as one common technical envelope plus the six typed authority-family admission profiles proposed here.

**Audit decision note:** Owen keeps OSv2 user edit history enabled on all Action-edited types for extra audit, while accepting the audit's separation rule: it remains backstage and cannot become domain history or an operator timeline. Owen accepts no initial Checkpoints; they require a named unmet policy need.

## 1. Verdict

The current Gate 6 architecture is strong on Ontology representation and transaction boundaries but incomplete as an operable production system. It explains how facts, links, Functions, Actions, AIP and Automate cooperate, yet it does not fully specify how bad or stale data is prevented from answering the six questions, how one coherent release is promoted and rolled back, how direct conversational execution survives replay and stale context, or how a fine-tuned model earns production authority.

**Verdict: FAIL, with a small correction set.** This is not a demand for more platform breadth. The missing items are controls on already-selected mechanisms. Gate 6 can close without adding another operator object, manager Action, read Function, workflow lane or operator surface.

The accepted semantic core survives:

- 11 visible fact owners;
- the focused hidden occurrence, authority, Plant-scope and cash substrate;
- the 32 semantic adjacencies with mixed physical backing;
- four manager-owned Actions;
- four decision Functions;
- external authority remaining external;
- no global status, readiness, task, case or completion object.

What does **not** survive is the claim that “assurance” can be deferred to a list of Action logs, Evals and observability. Foundry’s own architecture treats data flows, Ontology, agent lifecycle, operational automation, security, observability, and package/release/deploy as one operational system.[1] Gate 6 must do the same.

## 2. Audit standard: every mechanism must buy one of six answers

A mechanism is admitted only if it materially improves at least one accepted question:

| ID | Accepted question | Mechanism test |
|---|---|---|
| Q1 | What changed, and what does it affect? | Can it establish a trustworthy change, affected set, and explicitly unaffected set? |
| Q2 | What is required, allowed or blocked? | Can it establish current, scoped premises and distinguish “false” from “unknown/stale”? |
| Q3 | Who chooses, who decides and which route continues? | Can it establish caller/actor authority and preserve reserved decisions and fallback? |
| Q4 | Is the route ready for the named action? | Can it prove current action-specific premises at execution time and fail closed? |
| Q5 | What was done, and who accepted it? | Can it establish an attributable, bounded effect and acceptance line? |
| Q6 | Did the intended result land, and what remains open? | Can it reconcile intended versus observed effects without collapsing legal, physical, financial and biological lines? |

A capability that merely makes Foundry look comprehensive is rejected. “Available” is not a purpose.

## 3. MECE mechanism taxonomy

The taxonomy is mutually exclusive by **primary purpose**, not by product name. One Foundry product may implement several cells, but every configured resource gets exactly one primary owner.

| Class | Exclusive purpose | Admitted mechanisms | Six-question service | Operator posture |
|---|---|---|---|---|
| M1 — Acquire authoritative facts | Bring externally owned facts into the trust boundary | Data Connection, HTTPS listeners, streams, source adapters, immutable raw landing | Q1, Q2, Q5, Q6 | Backstage; only reconciled consequence is visible |
| M2 — Assure data and provenance | Prove freshness, schema, identity, completeness, lineage and indexing health | Data Expectations, Data Health checks, monitoring views, stream/Funnel checks, Data Lineage | All, especially Q1/Q2/Q4 | Mostly backstage; visible only as scoped stale/indeterminate warnings |
| M3 — Represent current domain truth | Own current identities, facts, contextual authority and typed occurrences | OSv2 objects, properties, links, hidden occurrence/assignment types, markings | Q1–Q6 | Decision-ready spine plus hidden substrate |
| M4 — Compute decision answers | Derive but never mutate applicability, impact, readiness, alternatives and exposure | incremental pipelines, deterministic optimizer/model, shared policy kernels, four read Functions | Q1, Q2, Q4, Q6; supports Q3 | Operator-visible answers; calculations backstage |
| M5 — Compare proposed futures | Evaluate alternatives without creating current truth | Ontology Scenarios; bounded proposal digest | Q3, Q4, Q6 | Visible only when alternatives can change the decision |
| M6 — Mutate owned truth | Apply one authorized business effect atomically | four Action types; declarative rules or TSv2 only as complexity requires | Q3, Q4, Q5 | Direct operator verb |
| M7 — Orchestrate and hand off | Trigger compute, route work, notify owners; never decide | Automate, schedules, notifications, outbound integration | Q1, Q4, Q6 | Visible only as owner/clock/handoff, not an automation console |
| M8 — Interpret operator intent | Resolve natural language into read, clarify, propose or one exact Action | task-specific AIP chatbot/Logic, exact tools, retrieval context | Q1–Q6 | Conversational ingress, not domain authority |
| M9 — Deliver interaction | Present context and actions through a fit-for-purpose application | Gate 7-selected surface; OSDK/Workshop/Map/etc. are candidates only | Q1–Q6 | Operator-visible |
| M10 — Audit and observe execution | Explain what the platform and model did | domain occurrences, Action logs, AIP/Workflow Lineage, metrics/traces/logs | Q5/Q6; diagnosis for all | Domain occurrence visible when relevant; telemetry backstage |
| M11 — Release and recover | Promote one compatible system version and roll it back | Global Branching, Code Repository CI, DevOps environments/products/release channels, model/function/chatbot versions | Protects all six | Backstage operator of the product, not the domain manager |
| M12 — Learn and govern models | Establish whether a model is better, safe, fair and stable enough to serve | AIP Evals, experiments, curated trajectory data, model registry/deployment, subset/drift evaluation | Q3/Q4 direct-execution safety; supports all | Backstage; surfaced only as confidence/abstention behavior |

**MECE rule:** acquisition does not validate; validation does not create domain truth; computation does not mutate; proposal does not commit; orchestration does not decide; intent interpretation does not grant authority; telemetry does not replace domain history; a branch does not equal a release environment.

## 4. Findings mapped to specific decisions and capabilities

### F1 — There is no binding data-health contract between source ingestion and the six answers

**Class:** missing mechanism (M2)  
**Maps to:** Q1-D01 affected decisions; Q1-D02 authoritative correction; Q2-D04 official condition; Q2-D05 deterministic applicability; Q4-D21–D28 readiness/release/dispatch; Q6-D37 cash; Q6-D41 remaining exposure. Capabilities L1/L2/L6, F1/F2, A1/A2/A6, W1/W2, P1/P2/P4/P6.

The current architecture says pipelines “prepare,” “precompute,” “validate/deduplicate,” and “quality-gate” but names no minimum Data Expectations, freshness SLOs, resolved-schedule health checks, stream-liveness checks, source quarantine or alert owner. Foundry distinguishes build-blocking Data Expectations from ongoing job/build/freshness health checks; Data Health can cover datasets, schedules, streams, functions, Actions, Automates and object types at scale.[2][3][17]

Without this contract, `Assess Named-Action Readiness` can return “not ready” when the true answer is “the permit feed is stale,” and `Determine Remaining Exposure` can understate cash or aftercare simply because an upstream stream stopped. That is a semantic error, not an SRE inconvenience.

**Smallest correction:** add one mandatory data-assurance matrix per authoritative source and every derived decision dataset: owner, cadence/SLO, schema/PK/FK/cardinality expectations, row/freshness/volume bounds, authority/identity rejection rules, last-good behavior, quarantine policy, alert route and which Q1–Q6 answers become **indeterminate** on failure. Functions must consume a health/freshness gate, not silently consume last-good data.

### F2 — Data Lineage and Workflow Lineage are conflated; source-to-answer lineage is missing

**Class:** omitted capability / ambiguous ownership (M2 vs M10)  
**Maps to:** Q1-D01/D02/D03, Q2-D05/D07, Q4-D21–D28, Q6-D35–D41. All “Explain” and “Hand off/reopen” capabilities: L4/L6, F4/F6, A4/A6, W4/W6, P4/P6.

Current Gate 6 mentions Workflow Lineage/AIP observability for model/tool traces but does not assign Data Lineage responsibility for source → transform → decision projection → object type. Data Lineage answers where a premise came from and what downstream resources are affected; Workflow Lineage answers what functions, Actions, models and applications executed.[4][15] Neither substitutes for the other.

**Smallest correction:** require two backstage traversals:

1. **fact lineage:** authoritative source → raw immutable payload → validation → normalized fact/occurrence → Ontology datasource/object;
2. **execution lineage:** prompt/trigger → Function/model/tool → Action → domain occurrence and downstream recomputation.

Operator explanations show only minimum basis references and a stale/health warning; engineers use the full traversals.

### F3 — The dependency index and `Determine Affected Decisions` ambiguously own the same answer

**Class:** duplicated truth / Golden Hammer (M4)  
**Maps to:** Q1-D01; capabilities L1/L6, F1/F6, A1/A6, W1, P1/P6.

The current design alternately assigns impact to a backstage proposition→decision dependency index, incremental pipelines, Automate and the live Function. If each can decide “affected,” they can disagree. Automate is also asked to detect, invoke, recompute, route and stage; it is drifting toward a workflow engine.

**Smallest correction:** assign one pipeline-owned **candidate dependency relation** as the only population-scale affected-set truth. Automate only triggers on changed keys. `Determine Affected Decisions` may filter that candidate set against current date/scope/authority and explain affected and unaffected results; it may not discover the population independently. No affected/reopened flags are written to domain objects.

### F4 — Readiness is deliberately implemented twice without one policy kernel

**Class:** duplicated decision logic (M4/M6)  
**Maps to:** Q4-D21–D28; every `*2 Compare requirements/readiness`, `*4 Explain readiness`, and `*5 Stage/release/dispatch` capability.

The current text says the read Function assesses readiness while the mutating Action “independently revalidates the refusal contract.” Independent enforcement is necessary; independent rule definitions are not. Two implementations will drift and produce the worst operator experience: the conversation says “ready,” then the Action refuses—or, worse, the reverse.

**Smallest correction:** define one versioned, deterministic, side-effect-free prerequisite kernel per Action. The read Function calls it to explain. The Action calls the same kernel on fresh state and fails closed. Submission criteria retain only non-duplicative coarse gates that the platform must enforce outside code: caller permission/group, parameter presence, obvious target state and required reason. The Action response includes the policy version and premise fingerprint.

### F5 — Ontology Scenario and Capacity Portfolio Proposal duplicate proposed truth

**Class:** redundant layer / ambiguous proposal owner (M5)  
**Maps to:** Q3-D15 recommend portfolio, Q3-D16 commit/rebalance; capabilities F2/F3/F4/F6 and W2/W3.

The current design says Scenarios hold alternatives while a hidden Capacity Portfolio Proposal stores selected Scenario, complete affected set, proposed edits, policy version, fingerprint, comparison and expiry. If both persist the same edit plan, operators and the Action can bind to different versions. The proposal and Action must also stay within the platform's documented edit envelope rather than hiding a second chunking protocol.[12]

**Smallest correction:** Scenarios are disposable comparison workspaces. The Proposal is the sole immutable executable digest after selection: proposal ID, scenario/version source, complete target set hash/fingerprint, exact deltas, policy/model version, protected set, expiry and explanation summary. It does not become a second live scenario. The commit Action accepts only proposal ID plus idempotency token and loads the exact plan server-side.

### F6 — “One universal external-outcome contract” is becoming an integration Golden Hammer

**Class:** misaligned generalization (M1/M3)  
**Maps to:** Q1-D02/D03; Q2-D04/D07; Q3-D10/D11/D17–D20; Q4-D21/D23/D25/D26; Q5-D29–D34; Q6-D35–D40. Capabilities L5/L6, F5/F6, A5/A6, W5/W6, P5/P6.

A common transport envelope is valuable. A universal competence and reconciliation contract is not. A bank reversal, member election, technician assertion, legal publication and biological establishment review have different authentication, ordering, correction, evidence and effective-time semantics. Treating all as one adapter invites lowest-common-denominator validation.

**Smallest correction:** retain one technical envelope only for source ID/version, idempotency, received time, evidence pointer and supersedes/reverses pointer. Add typed admission profiles for six authority families: legal/public, member/beneficiary, professional, contractual/field, biological, and bank/treasury. Each profile names authentication, competence check, subject grain, effective-time rule, correction ordering, reconciliation owner and failure state.

### F7 — Direct conversational execution lacks a replay-, stale-context- and blast-radius contract

**Class:** direct-execution UX hazard (M6/M8/M9)  
**Maps to:** Q3-D12/D13/D16 and Q4-D27; capabilities L3, F3/F5, A3/A5, W3/W5, P3/P5 where the user may stage or release.

The accepted invariant—an explicit authenticated manager prompt is the human decision—can be safe, but “explicit” is not operationally defined. Chatbot Studio can execute command tools without manual approval when approval is disabled, and native tool calling may parallelize tools.[9][14] Current prose prohibits parallel mutations but does not define enforcement for:

- “do it,” “dispatch these,” or deictic references after the map/selection changed;
- stale application variables versus current Ontology state;
- the model retrying after a timeout although the Action succeeded;
- the user resending the same message;
- a large portfolio hidden behind a short proposal name;
- tool output/prompt injection attempting a mutation;
- successful mutation followed by failed natural-language response;
- a model choosing the right Action but wrong target set.

**Smallest correction:** direct execution requires a machine-checkable **execution binding**: authenticated principal; immutable originating message ID; exact Action version; exact target or proposal ID; target-count and bounded consequence summary; current premise fingerprint; single-use idempotency key; expiry; and one mutating tool maximum per conversational turn. Deictic or changed context forces clarification. The Action, not the model, deduplicates and returns an immutable receipt stating committed/already-committed/refused. Portfolio commands must name the proposal and display target count plus material deltas in the conversation; this is consequence disclosure, not a redundant approval popup.

### F8 — The fine-tuning program is premature and its evaluation design is under-specified

**Class:** model lifecycle blind spot / breadth for breadth’s sake (M12)  
**Maps to:** every question through intent resolution; highest risk on Q3-D12/D13/D16 and Q4-D27. Capabilities L4, F4, A4, W4, P4 plus all direct Action capabilities.

Current Gate 6 jumps from Playwright-generated trajectories to open-source fine-tuning, BYOM registration and promotion. It does not first prove that prompting/tool descriptions plus a strong managed baseline fail. Open-source is explicitly demoted to “a means,” but the architecture still makes fine-tuning a planned layer rather than a conditional remedy.

The Evals list also misses:

- operator-, farm-, object-, time- and conversation-disjoint train/validation/test splits;
- leakage through paraphrases of the same proposal or object IDs;
- Italian/local terminology, code-switching, misspellings and short commands;
- hard negatives where one premise or one authority fact differs;
- out-of-distribution entities, unavailable/stale tools and changed Action schemas;
- prompt injection in retrieved documents/tool output;
- calibrated abstention/clarification thresholds;
- subgroup analysis for operator role, geography, route and action class;
- inter-annotator agreement and adjudication for trajectory labels;
- repeated-run variance for direct-action trajectories;
- shadow/canary deployment, rollback trigger and production drift/retraining policy.

AIP Evals supports model comparison and edit-producing tests in simulations, but safe simulated edits do not prove target resolution, latency, distribution shift or production source freshness by themselves.[13] Foundry also provides experiment tracking for training metrics/hyperparameters and lifecycle monitoring/rollback capabilities; those are absent from the binding plan.[7][8]

**Smallest correction:** make fine-tuning conditional. First freeze a disjoint, adversarial evaluation suite and compare the strongest available managed models. Fine-tune only if a named failure cluster remains material and a tuned candidate clears the same locked holdout plus cost/latency bars. Add a one-page model-release contract covering dataset provenance/licensing, split keys, label adjudication, experiment run, model/prompt/tool schema versions, subgroup and injection tests, variance, abstention threshold, shadow/canary period, rollback threshold and retraining trigger. Production traces enter training only after review and deduplication.

### F9 — AIP observability is used as a generic assurance answer but no service objectives or incident owner exist

**Class:** observability gap / Golden Hammer (M10)  
**Maps to:** all six questions operationally; direct evidence for Q5 and Q6. All 30 capabilities depend on availability and latency.

“Use observability for metrics, traces and drift” is not an operating contract. Foundry can provide execution counts, failures, P95 latency, run history, traces, log search and log export.[5] Gate 6 defines no SLOs, alert thresholds, retention/export requirement, incident owner, degraded mode or operator message.

**Smallest correction:** define six production indicators only: authoritative-source freshness; Ontology indexing rejection/liveness; Function success/P95; Action success/refusal/duplicate/concurrency rates; chatbot clarification/wrong-target/correction rates; and end-to-end command-to-receipt latency. Every indicator gets threshold, owner, alert route, runbook and degraded behavior. Telemetry remains backstage and never creates domain facts.

### F10 — Global Branching is incorrectly carrying release-management responsibility

**Class:** DevOps/release gap (M11)  
**Maps to:** protects Q1–Q6; most acute for Q2/Q4 when rules and Actions change. All capabilities.

The current architecture requires a clean project and Global Branch, then stops. Official guidance distinguishes short-lived branch isolation within one environment from long-lived development/test/production separation, release channels and rollback.[6] AIP architecture also includes package/release/deploy as a first-class capability.[1]

A branch proposal cannot prove that the Ontology schema, backing pipelines, Functions, Actions, chatbot tool schema, prompts, Evals and model version were promoted as one compatible release. It also does not define migration order or rollback when an object/API name is already promoted.

**Smallest correction:** define one **CORDON release manifest** containing Ontology/API versions, dataset schemas and expectations, Function package/tag, Action versions, chatbot/prompt/tool schema version, optimizer/model version, Evals suite/result, Automate/schedule versions and required source bindings. Require development → test → production promotion, compatibility checks, migration order, smoke cases for the four reads/four writes, release owner, rollback target and rollback limits. Whether this is implemented with Foundry DevOps packaging or an equivalent environment-separated process is implementation choice; Marketplace publication and fleet management are rejected until there is a second installation.

### F11 — Source liveness and Funnel/indexing failure are not part of the decision failure mode

**Class:** data-to-Ontology observability gap (M2/M3)  
**Maps to:** Q1-D01, Q2-D04/D05, Q4-D21–D28, Q6-D41; L1/L2, F1, A1/A2, W1/W2, P1/P2/P4.

A green upstream build does not prove objects are current. Stream liveness can stop; invalid writes can be rejected during indexing. Current Gate 6 has no explicit source-row → indexed-object reconciliation, orphan check or last indexed watermark.

**Smallest correction:** for each fact owner and hidden occurrence type, monitor raw accepted/rejected counts, qualified-key uniqueness, FK orphans, source watermark versus indexed-object liveness, and source-to-object conservation at the appropriate grain. A failed index makes dependent answers indeterminate and blocks writes. Data Lineage owns diagnosis; the Ontology remains the current read plane.

### F12 — The security design has mechanisms but no purpose/data minimization test for the chatbot

**Class:** omitted governance decision (M3/M8/M12)  
**Maps to:** Q3-D06 and all authority-bearing decisions; L4, F4, A4, W4, P4.

Restricted Views, markings, Action permissions and curated object query are named, but the plan does not define which evidence can enter model context, traces or trajectory datasets. Fine-tuning on production conversations can silently widen access beyond the live caller’s policy. Sensitive member, financial, authority and identity data require minimization before retrieval, logging and training. Foundry’s governance stack includes markings, purpose-based controls, georestrictions and sensitive-data discovery.[1][8][16]

**Smallest correction:** add a context/training data policy: allowed properties by tool; prohibited raw evidence; purpose/marking enforcement under caller identity; redaction in traces/eval exports; retention; geography/provider constraints; and a rule that training examples are re-authorized and de-identified independently of the production session that generated them.

### F13 — The architecture claims not to choose a surface while already choosing conversational primacy and Map coupling

**Class:** early surface choice (M8/M9)  
**Maps to:** all six questions; especially Q1 inspection, Q3 comparison/choice, Q4 dispatch readiness and Q6 remaining exposure.

Gate 6 repeatedly specifies “the conversation,” an embedded operating picture, map selections, Playwright interaction generation and direct chat execution. Those are legitimate capability requirements, but together they preselect an agentic common-operating-picture surface before the stated Gate 7 boundary. Official application guidance distinguishes discovery, analysis, geospatial and workflow-specific applications rather than treating one surface as universal.[10]

**Smallest correction:** freeze a channel-neutral interaction contract: any surface must supply authenticated principal, exact selected context, current premise fingerprint, read Function results, proposal reference and Action receipt. Conversational execution is a required ingress mode, not the navigation or screen architecture. Map is admitted only for Q1 spatial orientation and target selection where geometry changes the decision; it never becomes the universal home. Gate 7’s already-closed surface ruling remains untouched.

### F14 — Several assurance layers have no operator value and should remain invisible or be removed

**Class:** no-operator-value layer / redundant assurance (M10)  
**Maps to:** Q5/Q6 audit only; no direct capability requires separate operator navigation.

The architecture allocates six occurrence types, four Action-log object types, edit history, Capacity Proposal, Scenarios, AIP traces and Workflow Lineage. Their purposes differ, but exposing all of them creates five competing answers to “what happened.”

**Smallest correction:**

- domain occurrences are the only operator-relevant factual history;
- Action log is invocation audit and is reachable only for audit/support;
- user edit history is disabled unless a named incident/compliance requirement survives, because actions-only editing plus Action log and domain occurrence already cover the accepted mutations;
- AIP/Workflow traces are support telemetry;
- Scenario is disposable comparison;
- Proposal is the executable selected-plan digest;
- no log/trace/proposal/scenario becomes a generic operator timeline or queue.

## 5. Golden-Hammer ruling

| Candidate hammer | Ruling | Smallest purpose-aligned use |
|---|---|---|
| Ontology | **RETAIN, bounded** | Current decision-ready truth and governed verbs; not raw corpus, telemetry or training store |
| Hidden objects | **RETAIN, but hide** | Stable identity/links/reversal only; no operator workflow of their own |
| Function-backed Actions | **NARROW** | Use TSv2 where multi-object atomicity or authority traversal truly requires code; prefer declarative Action rules when they satisfy the same contract |
| Four read Functions | **RETAIN with shared kernels** | Explain bounded live answers; never duplicate population computation or Action policy definitions |
| Automate | **NARROW** | Trigger, route and notify; never own affected-set semantics or manager decisions |
| AIP Chatbot | **RETAIN as ingress, not authority/surface** | Interpret, clarify, retrieve, compare and invoke one exact Action |
| AIP Evals | **RETAIN, not sufficient** | Model/tool behavior regression; does not replace data health, action acceptance tests or release promotion |
| AIP observability | **RETAIN, not truth** | Diagnose execution; does not replace occurrences, SLOs or source lineage |
| Ontology Scenarios | **RETAIN only for consequential alternatives** | Capacity comparison; do not scenario-ize routine mandate/pursuit/dispatch |
| Checkpoints | **DEFER/REJECT initially** | Add only if a named compliance duty needs durable human justification beyond the occurrence reason and Action log |
| Derived properties | **DEFER by default** | Cheap local convenience after measured latency/value; never another readiness/exposure truth |
| Interfaces | **REJECT now** | No shared polymorphic operator capability proven |
| Foundry Approvals | **REJECT for domain decisions** | Platform change governance only unless a real external body adopts it as its transaction channel |
| DevOps product/Marketplace | **SPLIT** | Environment-separated release/rollback required; Marketplace/fleet distribution rejected until a second installation exists |
| Fine-tuned open-source model | **CONDITIONAL** | Admit only after locked baseline Evals prove a material residual failure and tuned model wins |
| Quiver/Contour/Insight/Object Explorer/Notepad/Fusion/Slate/Workshop/OSDK | **GATE 7 ONLY** | Admit only the selected surface and backstage diagnostic tools with named consumers |

## 6. Duplicate-truth and ownership register

| Purpose | Ambiguous current owners | Single owner after correction |
|---|---|---|
| Population affected set | dependency index, pipeline, Automate, Function | pipeline candidate relation; Function filters/explains; Automate triggers |
| Action readiness policy | read Function, Action function, submission criteria | one pure policy kernel; read/action wrappers; criteria only coarse platform gate |
| Proposed portfolio | optimizer result, Scenario, Proposal | Scenario compares; immutable Proposal digest is executable |
| Current external outcome | source-backed object property, occurrence, Action log | typed external occurrence/source-backed projection; no Action log |
| “What happened” | occurrence, Action log, edit history, trace | occurrence for domain; log/history/trace for distinct backstage audit roles |
| Model release identity | model asset, chatbot version, prompt, tool schema, Function tag | one release manifest pins all compatible versions |
| Health of an answer | last data row, pipeline build, object index, Function success | explicit end-to-end data-assurance gate with indeterminate state |
| Surface context | conversation state, application variables, map selection, Ontology read | immutable execution binding refreshed against Ontology at apply time |

## 7. Missing relevant Foundry/AIP capabilities

These capabilities are missing because they close a named failure, not because they broaden the demo:

1. **Data Expectations** at transform boundaries: PK, FK, cardinality, null/domain, conservation, authority-envelope and deduplication gates. Q1/Q2/Q4/Q6.
2. **Data Health + monitoring views** for source, schedule, stream, object type, Function, Action, Automate and chatbot health, with alert ownership. All questions.[2][18]
3. **Data Lineage** for source-to-object-to-answer provenance, distinct from Workflow Lineage execution traces. Q1/Q2/Q5/Q6.[4][15]
4. **Stream/Funnel/index liveness and rejection reconciliation.** Q1/Q2/Q4/Q6.
5. **Environment-separated release management, compatibility manifest and rollback.** Protects all questions.[6]
6. **Experiments and reproducible model-training metadata** before any fine-tune comparison. Q3/Q4.[7]
7. **Model deployment rollback, continuous/subset evaluation and capacity/rate-limit management.** Q3/Q4 operational safety.[8][11]
8. **Sensitive-data discovery/minimization and purpose/marking tests** for retrieval, traces and training trajectories. Q3 and all explanation capabilities.[16]

Everything else in the traversed platform breadth is deferred unless Gate 7 or implementation evidence supplies a named consumer.

## 8. Direct-execution acceptance contract

Direct conversational Action execution is accepted only when every case produces one of `COMMITTED`, `ALREADY_COMMITTED`, `REFUSED`, or `CLARIFICATION_REQUIRED` and never an uncertain mutation result.

Minimum cases:

1. exact target, current context, authorized caller → commits once;
2. same message/idempotency key replayed → already committed, no second occurrence;
3. model/tool timeout after server commit → receipt recovery, no retry mutation;
4. application selection changed after prompt → clarification required;
5. stale proposal/fingerprint → refused with changed premises;
6. ambiguous deictic target → clarification required;
7. two mutating tools proposed in one turn → refused before either executes;
8. wrong role/right target → authority refusal;
9. prompt injection in retrieved evidence/tool output → no new tool or parameter authority;
10. portfolio proposal target count/deltas omitted from conversational disclosure → not executable;
11. concurrent commitment change → stale/conflict refusal, no partial edit;
12. Action succeeds but response generation fails → immutable receipt remains retrievable.

Simulation-backed AIP Evals should test tool/edit behavior without live mutation,[13] while Action-level integration tests prove idempotency, concurrency, receipts and exact persisted occurrences.

## 9. Model evaluation and fine-tuning closure bar

No fine-tuned model is required for Gate 6. Gate 6 must require the **decision rule for whether to fine-tune**:

- baseline suite frozen before tuning;
- split by operator, subject/object, time and conversation family;
- exact four-Action and four-Function schemas pinned;
- hard negatives differ by one authority/readiness premise;
- injection, stale context, tool failure and changed-schema cases included;
- Italian/local-language and terse/deictic utterances represented;
- repeated-run variance measured;
- metrics include exact tool, exact target, exact parameters, clarification, abstention, forbidden implication, end-to-end receipt and operator correction;
- subgroup worst-case thresholds, not only aggregate score;
- tune only against a named residual failure cluster;
- locked holdout, shadow/canary, rollback and drift trigger required for promotion;
- production traces are quarantined, de-identified, adjudicated and deduplicated before training.

AIP Evals owns agent behavior evaluation. Data Health owns input health. Action tests own mutation correctness. The release process owns promotion. None may claim the others’ purpose.

## 10. Smallest corrections required before Gate 6 can close

No new domain semantics are required. Amend the Gate 6 reconciliation with exactly these eight bounded contracts:

1. **Data-assurance contract:** expectations, freshness/liveness/index checks, indeterminate behavior, owner and alert route per authoritative source/decision dataset.
2. **Dual-lineage contract:** Data Lineage for fact provenance and Workflow Lineage for execution; minimum operator-visible basis only.
3. **Single-kernel compute contract:** pipeline owns candidate affected sets; shared pure policy kernels own readiness; Functions explain; Actions re-run; Automate triggers/routes.
4. **Direct-execution binding:** message ID, Action version, exact target/proposal, count/consequence disclosure, fingerprint, idempotency, expiry, one mutation per turn and durable receipt.
5. **Proposal de-duplication:** Scenario compares; one immutable Proposal digest is executable; no duplicate live proposed state.
6. **Typed source-admission profiles:** one common technical envelope plus six authority-family validators and reconciliation owners.
7. **Release/recovery contract:** development/test/production separation, one compatibility manifest, migration/smoke gates, rollback target and owner.
8. **Conditional model lifecycle contract:** locked disjoint/adversarial Evals, experiment provenance, data minimization, baseline-first fine-tuning rule, subgroup/variance bars, shadow/canary and rollback/drift triggers.

Also prune two unnecessary defaults:

- disable user edit history unless a named audit requirement remains after Action logs + domain occurrences;
- do not instantiate Checkpoints, derived properties, Marketplace distribution, Interfaces or extra analytics/application surfaces without a named six-question consumer.

## 11. Closure ruling

Gate 6 is **not mechanism-complete today**. The missing production controls can allow a beautifully modeled system to give a current-looking answer from stale data, execute the right verb against the wrong conversational target, promote incompatible Ontology/model/tool versions, or improve an aggregate model score by leaking the same farms and proposals across train and test.

The correction is intentionally smaller than the current architecture’s breadth: no new operator object, Action, Function or surface. Add eight binding operational contracts, remove duplicate readiness/proposal ownership, and keep optional platform products out until they have a named six-question purpose. Once those corrections are incorporated into the authoritative Gate 6 reconciliation, Gate 6 may close as **PASS-WITH-CORRECTIONS**.

## Sources

[1] https://www.palantir.com/docs/foundry/architecture-center/aip-architecture

[2] https://www.palantir.com/docs/foundry/observability/data-health

[3] https://www.palantir.com/docs/foundry/data-integration/health-checks

[4] https://www.palantir.com/docs/foundry/data-lineage/overview

[5] https://www.palantir.com/docs/foundry/observability/overview

[6] https://www.palantir.com/docs/foundry/devops-release-management/overview

[7] https://www.palantir.com/docs/foundry/model-integration/experiments

[8] https://www.palantir.com/docs/foundry/aip/ethics-governance

[9] https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools

[10] https://www.palantir.com/docs/foundry/ontology/applications

[11] https://www.palantir.com/docs/foundry/aip/bring-your-own-model

[12] https://www.palantir.com/docs/foundry/action-types/scale-property-limits

[13] https://www.palantir.com/docs/foundry/aip-evals/ontology-edits

[14] https://www.palantir.com/docs/foundry/chatbot-studio/tools

[15] https://www.palantir.com/docs/foundry/workflow-lineage/overview

[16] https://www.palantir.com/docs/foundry/sensitive-data-scanner/overview

[17] https://www.palantir.com/docs/foundry/maintaining-pipelines/recommended-health-checks

[18] https://www.palantir.com/docs/foundry/monitoring-views/overview

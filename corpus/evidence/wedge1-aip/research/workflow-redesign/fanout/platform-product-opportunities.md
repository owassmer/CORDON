# CORDON current-platform product and architecture reconnaissance

**Status:** read-only product/architecture reconnaissance; recommendations, not a new semantic authority  
**Date:** 24 August 2026  
**Scope:** current Foundry/AIP capabilities that could materially improve the operator decision loop, exact Action execution, map operating picture, source-change response, evidence, capacity planning, field use, model assurance, or implementation simplicity  
**Writes performed:** this file only. No Foundry, git, configuration, or other file writes.

## Executive verdict

CORDON should keep **Workshop as the first implementation substrate**, but should not build the accepted fixed three-pane composition literally. The strongest redesign is a **persistent decision shell with an adaptive work surface**:

- a compact, persistent context/header and a Now/focus rail;
- one main decision surface that changes by the operator's current question;
- AIP present for explanation and exact commands, but not entitled to a permanent third of the screen;
- Map expanded when geography changes the decision and collapsed to a compact location strip when it does not;
- evidence beside the decision when it is load-bearing;
- receipt fixed in place after a consequential command.

This retains the accepted semantics and direct-execution contract while removing the most fragile product assumption: that **Now + five responsibilities, Map, and AIP all deserve permanent simultaneous real estate for every decision**. They do not. Land and dispatch often need the Map. Capacity, authority, application, and payment decisions usually need alternatives, basis, clocks, and independent consequence lines more than geography. Palantir's current variable-backed layouts can make that change natively; no React shell is required to test it.

The highest-value architecture simplifications are:

1. use one deterministic **context envelope** and bind Action/Function tool inputs from application state rather than asking the model to reconstruct targets and proposal IDs;
2. use the generated **Action log plus domain occurrence** as the committed receipt backbone, rather than creating a second receipt persistence model;
3. test whether a **scenario merge rule** can replace the custom staged-write reconstruction in the capacity Action, while retaining the immutable Proposal as the business digest;
4. treat Scenarios as a mechanism to prove, not a required product layer;
5. use media references and native PDF page/search binding for exact evidence jumps, without admitting a generic Evidence object or annotation workflow in release 1;
6. make source change native to each source—CDC only when a real changelog exists, snapshot/diff otherwise—and project only material decision changes into Now;
7. launch with the **best Eval-clearing hosted model**, not a model family chosen in advance; hosted open-source models remain serious candidates, not an ideological production constraint;
8. keep the initial mobile product to scan/location/read/capture/handoff. Do not claim offline capability, map parity, or full management on a phone.

The accepted architecture is mature. Most of its semantic and governance decisions survive. The changes below primarily remove fixed presentation assumptions, duplicate runtime state, and custom implementation that Foundry now handles natively.

---

## 1. Evidence discipline and interpretation

### 1.1 Evidence ordering used in this report

For each recommendation, evidence is presented in the requested order:

1. **Unsupported/model-memory claims** — explicitly named first. None is allowed to carry a recommendation.
2. **Inference** — what follows from CORDON's accepted contract plus measured/documented platform behavior.
3. **Fetched official fact** — quoted verbatim with URL, last.

A recommendation may remain **PROBE** when official documentation proves platform support but not enrollment exposure, composition behavior, or acceptable operator performance.

### 1.2 Four dimensions kept separate

| Dimension | Meaning in this report |
|---|---|
| **Platform support** | Current official Palantir documentation states the capability exists. |
| **Enrollment exposure** | A read-only live probe shows the resource/capability is visible in this enrollment, or Owen has already established it. |
| **Tool ability** | The Palantir MCP/read-only tool surface can inspect the capability. This is not the same as platform support. |
| **Agent-flow reliability** | The current agent could navigate or test the complete behavior reliably. This is not inferred from documentation or from MCP reach. |

### 1.3 Live enrollment observations

Read-only Palantir MCP probes established:

- one available non-default Ontology, `owenwassmer Ontology`, currently version `00000015-3dad-d927-2543-51047c521a69`;
- two projects matching CORDON: current `CORDON` and historical `CORDON-Wedge-1`;
- **392** visible Function registry entries at probe time, up from the 389 recorded in the accepted Gate 6 audit;
- hosted entries for **Llama 3.3 70B Instruct** and **Llama 3.3 Nemotron Super 49B v1.5**, plus current Claude, Gemini, GPT and Grok entries;
- the current CORDON project has no FILE_SYSTEM imports and has standard external transform/runtime imports;
- project search returned no resource matching `scenario`, `workshop`, or `map` in CORDON.

The last item is **not evidence that those platform capabilities are absent**. It establishes only that the current search tool found no named project resource. Workshop, Scenario, and Map configuration are not comprehensively inspectable through this MCP search surface.

### 1.4 Failed documentation and live probes

Every failed or non-conclusive probe in this pass:

| Probe | Result | Correct interpretation |
|---|---|---|
| Load official page path `workshop/mobile-widgets` | `No page content found` | Bad/discontinued page path. The specific QR and Current Location pages loaded successfully; no mobile capability conclusion is drawn from this failure. |
| Search CORDON resources for `scenario` | No results | Tool/search exposure only; not proof Scenarios are unavailable. |
| Search CORDON resources for `workshop` | No results | Tool/search exposure only; not proof Workshop is unavailable. |
| Search CORDON resources for `map` | No results | Tool/search exposure only; not proof Map is unavailable. |
| Search Function registry for `Mistral` | 0 results | No registry match under that string at probe time; not proof that every Mistral deployment path is unavailable. |
| Establish the default confirmation setting for **Action tools** from current docs | Current docs establish that Action tools can run automatically or after confirmation, but the retrieved page did not state which is the default | Keep the accepted live build constraint as a separate enrollment/configuration fact; do not generalize the documented Command default to Action tools. |
| Inspect a live configured Workshop/Chatbot/Scenario | No matching project resource was exposed by the read-only search tool | Enrollment composition remains untested. Browser/UI difficulty is not reported as a platform limitation. |
| Verify native scenario merge combined with CORDON's function-backed revalidation and occurrence write | Documentation proves Apply Scenario rules and atomic merge, but no live CORDON Action exists to test | This is the key **PROBE BEFORE ADOPTION** item, not an assumed simplification. |

---

## 2. Product thesis after reconnaissance

### What should remain fixed

- the shared Ontology and deterministic Functions/Actions;
- the five responsibilities as accountability lenses, not software silos;
- Q1–Q6 as a recursive decision grammar, not six statuses;
- four exact manager Actions and four read Functions;
- one mutating tool maximum per conversational turn;
- direct execution after a clear authenticated command, with clarification only for material ambiguity;
- geometry as orientation/candidate scope, never authority;
- the Proposal as the sole executable capacity digest;
- source-owned truth, typed contextual authority, independent legal/operational/financial/biological result lines;
- platform-owned ingestion, assurance, observability, and Evals;
- no generic Task, Case, Evidence, Receipt, Status, Readiness, or Event object merely to support a screen.

### What should change

- a fixed three-pane desktop should become an **adaptive decision shell**;
- the five responsibilities should be a compact facet/ribbon, not five persistent mini-inboxes;
- Q1–Q6 should control the scene but remain mostly implicit in navigation;
- the Map should expand by relevance, not by constitutional right;
- exact Action target/proposal inputs should be deterministic application-state bindings;
- committed receipts should be projections of Action log + domain occurrence, not a parallel persistence system;
- Scenarios should earn their place by replacing code or improving comparison, not simply because Foundry supports them;
- the production model should be selected by the frozen Eval bar, not by prior commitment to fine-tuning or open-source provenance alone;
- mobile should be a field companion, not a compressed desktop COP.

---

## 3. Opportunities and challenges

## Opportunity 1 — Replace the fixed three-pane layout with an adaptive decision shell

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Q2–Q6 decisions where authority, alternatives, exact prerequisites, evidence, or consequence lines matter more than geography; Q1 and dispatch still receive full Map support when geography is load-bearing.

**Change.** Keep a persistent compact header/context strip and Now/focus rail. Make the remaining area one variable-backed decision workspace:

- **Spatial mode:** Map occupies the main surface; AIP is a narrower sidecar; evidence opens beside it.
- **Comparison mode:** alternatives/proposal diff occupies the main surface; Map collapses to a small selected-scope strip.
- **Authority/evidence mode:** proposition, source, competence, date and conflict occupy the main surface; Map is compact or absent.
- **Command mode:** command + exact scope + receipt occupy the main surface; irrelevant panels collapse.
- **Exposure mode:** independent legal/operational/financial/biological lines occupy the main surface.

AIP remains available but need not consume a permanent third of the screen when the operator is reading a full proposal diff or authoritative PDF.

**Existing mechanism replaced.** Fixed `Now/five responsibilities | Map | AIP` columns on every scene.

**Implementation cost.** **Low–medium, native configuration.** A small set of string/Boolean layout-state variables; variable-backed sections/pages; no custom widget or React shell.

**Strongest case against.** Persistent Map visibility may create shared spatial awareness and reduce context switching during a spatially dominant operating shift. Adaptive layouts can also feel jumpy if the rules are opaque. The thin prototype must keep transitions deterministic, preserve selection, and never move the command target silently.

**Unsupported/model-memory claims.** None used.

**Inference.** The accepted layout over-allocates space to the Map and Chatbot for nonspatial decisions. The same selected context can drive a variable-backed layout without creating a second domain model, provided the layout mode is a presentation enum derived from the selected decision scene.

**Fetched official facts.** Palantir says: **“Variable-backed layouts allow you to dynamically control the state of layout components using variables”**, including pages, sections, tabs, and overlays.[Official: https://www.palantir.com/docs/foundry/workshop/variable-backed-layouts] Palantir's design guidance also says: **“Validate whether or not every element must be visible from its current location. If it does not, then you should only surface the element when a user will need to interact with and take action from the element.”**[Official: https://www.palantir.com/docs/foundry/workshop/application-design-best-practices]

---

## Opportunity 2 — Represent five responsibilities as facets and Q1–Q6 as scene grammar, not dual navigation

**Disposition:** **ADOPT NOW**

**Operator decision improved.** “What needs my attention and why?” without forcing the manager to choose between two taxonomies before seeing work.

**Change.** The Now rail remains the entry point. Each row carries its existing route-family label. Show the five responsibilities as a compact, multiselect facet/ribbon with counts and current owner/clock summaries—not five persistent content lines. When a row is selected, the application derives the current Q-state from its decision scene and shows a six-step breadcrumb only when useful:

`Changed → Consequence → Decision right → Ready → Done/accepted → Exposure`

The breadcrumb is explanatory/progressional, not six clickable queues. It may highlight more than one question when the selected scene spans them.

**Existing mechanism replaced.** Five always-visible responsibility lines plus an independently changing Q1–Q6 scene, which makes the user hold eleven conceptual positions at once.

**Implementation cost.** **Low, native Workshop.** Existing `route family` and `decision scene` fields; one filter/list header; one variable-backed breadcrumb.

**Strongest case against.** The five responsibility lines may be valuable as a stable “nothing is forgotten” reassurance, especially for managers used to functional portfolios. Facets can hide a responsibility with zero current rows. Preserve a compact all-five ribbon and explicit zero/none state; remove only the five parallel mini-inboxes.

**Unsupported/model-memory claims.** None used.

**Inference.** The accepted five responsibilities and six questions are orthogonal analytical structures, not two navigation hierarchies. Turning both into persistent navigation duplicates orientation and encourages responsibility silos.

**Fetched official facts.** Palantir warns: **“avoid showing more than five primary actions in your application's top-level navigation”** and recommends no more than ten visible components in one view.[Official: https://www.palantir.com/docs/foundry/workshop/application-design-best-practices] The operational-app guidance says to **“Show only the objects, links, and properties that matter to the decision, along with context needed to act, and leave other information out.”**[Official: https://www.palantir.com/docs/foundry/app-building/operational-apps]

---

## Opportunity 3 — Make one context envelope the only cross-surface state contract

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Every direct command, especially deictic commands such as “dispatch these” or “commit this proposal,” because target drift becomes detectable rather than conversational.

**Change.** Replace many loosely related Workshop/AIP variables with one defined envelope whose fields are owned in one place:

- selected visible object set;
- selected subject/route;
- named Action;
- consequential date/as-of;
- Proposal ID where applicable;
- target-set hash/count;
- premise fingerprint;
- health/indeterminate state;
- context generation number.

Workshop may physically represent this as a small set of supported string/object-set variables, but they are versioned and updated as one logical contract. The model sees only fields needed for the current turn. Exact target object set, Action name/version, Proposal ID, and fingerprint are deterministic tool inputs wherever supported. The model generates only semantically open inputs such as a manager-supplied reason.

**Existing mechanism replaced.** Model reconstruction of target IDs and Proposal IDs from prose; broad visible application state; independent map/chat/widget selection variables.

**Implementation cost.** **Medium, mostly configuration plus one serializer/fingerprint Function.** No new object type.

**Strongest case against.** Chatbot Studio deterministic inputs support only string and object-set types and are pinned at the start of the reasoning loop. A composite struct cannot simply be passed as one variable, and an upstream tool update in the same turn will not refresh the pinned value. Therefore the application must start a new reasoning turn or clarify after context changes; pretending the feature supports a mutable transaction context would be unsafe.

**Unsupported/model-memory claims.** None used.

**Inference.** Exact tool inputs reduce the model's job from “discover target and construct the mutation” to “understand intent and choose the admitted verb.” This materially improves exact Action execution without another approval step.

**Fetched official facts.** Chatbot Studio states: **“The Action and Function tools can be configured to use inputs from application variables instead of generating inputs dynamically through the LLM. This feature allows you to pass predetermined values directly to tools, improving consistency and reducing token usage.”** It also states those values **“are pinned to the initial value of the variables at the start of the reasoning loop.”**[Official: https://www.palantir.com/docs/foundry/chatbot-studio/application-state]

---

## Opportunity 4 — Use semantic map modes, not a permanent layer catalog

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Q1 affected geography, Q2 candidate applicability, and Q4 dispatch scope, while preventing the map from implying law or readiness.

**Change.** Define four named native map modes driven by the selected decision scene:

1. **Change footprint:** changed Official Areas/source version, affected and explicitly unaffected member work.
2. **Authority context:** candidate geometry plus the governing Instrument/authority card; context layers locked and visually subordinate.
3. **Dispatch scope:** selected Intervention, Parcels/Plants, executor location where useful, stop/return conditions.
4. **Outcome footprint:** bounded performed/accepted/establishment scopes, with those states represented separately.

Within each mode:

- use Boolean variable-backed visibility rather than asking users to curate dozens of layers;
- lock context-only layers so users cannot accidentally select them as targets;
- use zoom-dependent geometry visibility and high-scale loading methods for full-region cadastre/plant populations;
- show a compact legend by default;
- set `Only update if outside viewport` so selection changes do not constantly destroy the manager's spatial frame;
- transition to full Map only for investigation, not routine Action execution.

**Existing mechanism replaced.** One permanent central Map with a broad static layer stack and operator-managed layer visibility.

**Implementation cost.** **Medium, native Map/Workshop configuration.** No custom map code.

**Strongest case against.** Preset modes may hide an unexpected cross-layer relationship. Keep the full Map transition and legend available as read-only investigation escalation, and let expert operators temporarily reveal an allowlisted overlay without changing the Action target.

**Unsupported/model-memory claims.** A claim that zoom visibility automatically changes legal meaning would be unsupported and is explicitly rejected.

**Inference.** CORDON's scale is too large for “load everything and style it.” Full-region cadastre and monitoring need viewport-aware loading and zoom-dependent geometries. The operator should choose a decision, not assemble a GIS project.

**Fetched official facts.** Workshop Map supports static or Boolean-variable **Layer visibility**, locked layers, bidirectional selected-object variables, viewport bounds, and `Only update if outside viewport` auto-zoom.[Official: https://www.palantir.com/docs/foundry/workshop/widgets-map] Palantir says the high-scale loading method exists because loading all objects **“inherently creates a scale limitation”** and instead restricts loading to data needed for the visible extent.[Official: https://www.palantir.com/docs/foundry/map/objects-loading-methods] Map also documents visibility by zoom level.[Official: https://www.palantir.com/docs/foundry/map/visualize-objects]

---

## Opportunity 5 — Freeze the decision scene during a consequential command, not the underlying truth

**Disposition:** **ADOPT NOW**

**Operator decision improved.** The final transition from inspected proposal/scope to exact Action submission under concurrent updates.

**Change.** When the operator begins a consequential command:

- freeze presentation auto-refresh for the active scene;
- capture the context generation, target/proposal ID, count/hash, and premise fingerprint;
- show “decision snapshot captured at …”; 
- let the Action reload and revalidate current server state;
- if the fingerprint changed, return a determinate refusal/recompare instruction;
- after receipt/refusal, re-enable refresh and selectively update the scene.

This does not freeze Foundry data and is not optimistic client authority. It prevents visible controls from moving under the operator while preserving server-side freshness.

**Existing mechanism replaced.** Continuous full-module refresh during input/command composition, which can reset variables or visually retarget the scene.

**Implementation cost.** **Low–medium, native events plus existing fingerprint.**

**Strongest case against.** Pausing refresh can momentarily display stale information. The state must be visibly marked as a captured decision snapshot, short-lived, and never used to bypass Action revalidation.

**Unsupported/model-memory claims.** None used.

**Inference.** The operator needs stable visual scope while expressing intent; the Action needs fresh state while executing. Those are compatible if the UI freezes and the server revalidates.

**Fetched official facts.** Workshop lets events **enable or disable auto-refresh updates**.[Official: https://www.palantir.com/docs/foundry/workshop/auto-refresh] Palantir warns that in modules with auto-refresh, **“variable or widget state is reset after refreshing”** may occur in workflows involving user input.[Official: https://www.palantir.com/docs/foundry/workshop/auto-refresh] OSv2 Actions do not guarantee that all objects read outside edit generation remained unchanged during apply, so CORDON's explicit fingerprint/kernel revalidation remains necessary.[Official: https://www.palantir.com/docs/foundry/object-edits/how-edits-applied]

---

## Opportunity 6 — Put population work in object sets, indexed filters, backend aggregations, and pipelines; Functions return bounded decision products

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Complete-population impact and capacity decisions without timeouts, approximate top-bucket surprises, or silent clipping.

**Change.** Make the existing compute split enforceable with a per-Function scale contract:

- **Determine Affected Decisions:** input changed-key object set/partition; pipeline owns the complete dependency relation; Function filters current authority/date/conflicts and returns bounded affected/unaffected digests.
- **Assess Named-Action Readiness:** one bounded target/portfolio; never a whole population.
- **Compare Feasible Intervention Portfolios:** optimizer reads a versioned prepared input table; Function returns a small alternative digest, not every candidate row/edit.
- **Determine Remaining Exposure:** backend aggregations and bounded linked occurrence pages; output independent lines, not a raw occurrence dump.

Rules:

- never call `.all()` for a complete CORDON population;
- filter on indexed raw properties before link traversals;
- use backend count/sum/group operations;
- paginate when object materialization is unavoidable;
- carry exact counts separately from UI “top values” buckets;
- set a response-size budget and return object sets/digests rather than arrays;
- profile each live Function in the Performance tab before surface binding.

**Existing mechanism replaced.** Any per-object loop, client array, or Function that rediscovers the complete population interactively.

**Implementation cost.** **Medium, code/design discipline already aligned with Gate 6.**

**Strongest case against.** Precomputation increases pipeline latency and can make a rapidly changing answer less immediate. The live Function must still resolve the last bounded, decision-sensitive predicates; only complete discovery and stable aggregation move backstage.

**Unsupported/model-memory claims.** None used.

**Inference.** CORDON's millions of Parcels and hundreds of thousands of Plants are beyond comfortable interactive materialization. The accepted pipeline + Function split is correct; it should be converted from guidance into explicit load and response budgets.

**Fetched official facts.** Palantir says object sets are the most efficient Function input and backend aggregation avoids loading individuals.[Official: https://www.palantir.com/docs/foundry/functions/optimize-performance] OSS may switch to Spark above 100,000 objects, `.all()`/`.allAsync()` is capped at 100,000, and **“Loading more than 10,000 objects in Functions on Objects may cause execution timeouts.”**[Official: https://www.palantir.com/docs/foundry/ontologies/oss-limitations] Action submissions are limited to 10,000 edited objects.[Official: https://www.palantir.com/docs/foundry/action-types/scale-property-limits]

---

## Opportunity 7 — Probe a native Scenario merge Action as the capacity commit implementation

**Disposition:** **PROBE BEFORE ADOPTION**

**Operator decision improved.** Commit or rebalance capacity as one exact, reviewable transaction with fewer custom edit-generation mechanics.

**Change to probe.** Keep the immutable Capacity Portfolio Proposal, but let it store:

- Scenario RID/version;
- complete target-set hash and exact material delta digest;
- policy/optimizer version;
- protected commitment set;
- premise fingerprint and expiry.

The manager's exact Action would accept Proposal ID, load/revalidate the Proposal, then use an **Apply Scenario rule** to merge the scenario's edits as one transaction while also writing the Commitment Change Record/receipt context if the platform composition permits it. This could replace custom staged-write reconstruction of up to 10,000 Commitment edits.

**Existing mechanism replaced.** TypeScript staged-write Action that reloads the Proposal and reconstructs every Commitment edit itself.

**Implementation cost.** **Probe: low–medium. Adoption: medium.** One thin scenario with two alternatives; one merge Action; stale-fingerprint, protected-commitment, and occurrence-write tests.

**Strongest case against.** Scenarios remain Beta; they auto-rebase; have their own 30,000-edit/50-Action limits and a 10,000-object load limit in scenario context; attachment properties are unsupported; the exact composition of Apply Scenario + CORDON's function-backed revalidation/occurrence write is not yet proven in this enrollment. If the merge rule cannot preserve the exact refusal and receipt contract with less code, reject it.

**Unsupported/model-memory claims.** It is unsupported to claim this composition works end to end in the enrollment. That is why it is a probe.

**Inference.** Scenario merge is potentially the rare Foundry capability that removes—not adds—custom transaction code. The Proposal remains necessary as the named business decision and digest; the Scenario becomes an edit carrier, not a second truth.

**Fetched official facts.** Palantir documents that scenario edits **“exist only within that scenario's isolated sandbox”** and that applying a scenario **“commits all those staged edits to the Ontology as a single transaction via the merge action.”** It also says an existing Action may receive an **Apply Scenario** rule.[Official: https://www.palantir.com/docs/foundry/ontology/merge-scenario] Current Scenario limits are documented at 30,000 edits, 50 Actions, and 10,000 loaded objects in scenario context.[Official: https://www.palantir.com/docs/foundry/workshop/scenarios-concepts]

### Probe acceptance matrix

| Case | Required result |
|---|---|
| two alternatives | side-by-side results; main unchanged |
| selected Proposal | exact Scenario RID/hash stored |
| valid commit | one atomic merge; one Action log; required domain occurrence/change records |
| stale fingerprint | zero edits; determinate recompare refusal |
| protected Commitment touched | zero edits; named refusal |
| replay same idempotency key | no second merge; original receipt returned |
| >10,000 target envelope | refusal before scenario/merge; no hidden chunking |
| model response drops after merge | receipt retrievable from durable platform data |

If any case requires a parallel custom edit plan, a second approval flow, or a second transaction, keep the existing staged-write approach.

---

## Opportunity 8 — Do not make Scenarios a release-1 UX requirement unless they replace code

**Disposition:** **PROBE BEFORE ADOPTION**

**Operator decision improved.** Capacity alternative comparison without exposing planning mechanics or making the manager create/manage sandboxes.

**Change.** Prototype the capacity scene in this order:

1. deterministic Compare Function returns two or three complete alternative digests;
2. native Object Table/Chart/Metric cards compare target count, capacity use, protected commitments, binding constraints, loss-reduction objective, fairness safeguards, deferrals/fallbacks, sensitivity, and invalidation;
3. selection creates one immutable Proposal;
4. only then add native Scenario awareness if it materially improves inspecting changed Commitment values or enables the simpler merge mechanism in Opportunity 7.

Hide Scenario Manager from the routine operator flow. CORDON, not the manager, creates the bounded scenario artifacts.

**Existing mechanism replaced.** Scenario Manager-led capacity workflow in which the operator creates/selects/deletes scenarios as a first-class planning task.

**Implementation cost.** **Low for native comparison prototype; medium if Scenarios are admitted.**

**Strongest case against.** Scenario-aware tables/charts can make alternatives concrete and Scenarios provide safe, real Ontology edits rather than synthetic summaries. If operators need row-level what-if inspection and native merge works, hiding the mechanism should not mean omitting it.

**Unsupported/model-memory claims.** None used.

**Inference.** The manager decides among policy-governed portfolios, not among Foundry sandboxes. A visible Scenario Manager leaks the mechanism and adds lifecycle concepts that the immutable Proposal already owns.

**Fetched official facts.** Temporary scenarios are session-only and deleted when the session ends; persisted scenarios require Ontology objects to store metadata.[Official: https://www.palantir.com/docs/foundry/ontology/temporary-scenario; https://www.palantir.com/docs/foundry/ontology/persisted-scenario] Workshop can compare arbitrary Scenarios in tables/charts and run scenario-aware aggregations.[Official: https://www.palantir.com/docs/foundry/workshop/scenarios-getting-started] Scenarios are Beta.[Official: https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario]

---

## Opportunity 9 — Use Action log + domain occurrence as the committed receipt backbone

**Disposition:** **ADOPT NOW**

**Operator decision improved.** “Did my command commit exactly once, what changed, and what did it not imply?” after a stream drop, retry, handoff, or later audit.

**Change.** Do not create a new generic Receipt object type. For a committed Action:

- Action log owns submission identity, Action type/version, principal, timestamp, parameters, edited-object IDs, and compact summary;
- the typed domain occurrence/change record owns what happened in the world and the accepted semantic non-implications;
- the read Function joins/projects both into the receipt strip;
- the idempotency key is stored as an Action parameter/logged value and checked before mutation;
- `ALREADY_COMMITTED` returns the original projected receipt;
- `REFUSED` and `CLARIFICATION_REQUIRED` remain non-write results with session/observability telemetry; do not manufacture a domain occurrence merely to make every turn durable.

If long-term policy requires durable refused-command records, add that only as a named audit requirement after proving Action/session logging cannot satisfy it—not as release-1 truth.

**Existing mechanism replaced.** A custom, parallel receipt persistence model or Receipt object type.

**Implementation cost.** **Low–medium.** Configure log fields and build one receipt projection Function/Workshop component.

**Strongest case against.** Action logs are generated technical object types and may not capture every CORDON-specific return field, particularly refusal details and non-implications. If the exact receipt cannot be reconstructed deterministically after response loss, a focused Action Execution Receipt type may be justified. That type must be per-command evidence, not a generic workflow object.

**Unsupported/model-memory claims.** It is not established that failed submissions generate an Action log object. This recommendation does not rely on that claim.

**Inference.** Committed receipt identity and edit scope already exist in the Action log; domain consequence already exists in typed occurrences. Storing the same facts a third time increases reconciliation burden.

**Fetched official facts.** Palantir states: **“Submitting an action generates a single new object of the corresponding action log object type”**, linked to all edited objects. The default schema includes Action RID, type RID/version, timestamp, user ID, edited objects, optional summary, and optional parameter values.[Official: https://www.palantir.com/docs/foundry/action-types/action-log] OSDK Action application can return validation and exact edit counts/objects, but that response alone is not the durable receipt.[Official: https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk]

---

## Opportunity 10 — Turn evidence into exact document jumps, not a generic evidence browser

**Disposition:** **ADOPT NOW**

**Operator decision improved.** “What is the authoritative basis for this proposition, date, competence, or amount?” without leaving the decision scene.

**Change.** For every load-bearing basis, project the minimum evidence locator:

- media reference or governed file pointer;
- document identity/version/hash;
- page number;
- quoted span or search term;
- proposition/occurrence relationship;
- source and as-of;
- access/health state.

The evidence sidecar opens the native PDF Viewer at the exact page and runs the exact search term. Use media references for documents that require platform-native preview, policy, OCR, or future extraction. Use a simple governed file pointer where media semantics add no value. Do not add annotation objects in release 1 unless users must create durable review annotations as a real workflow.

**Existing mechanism replaced.** Generic “evidence drawer” with document URLs and manual search; any proposed generic Evidence object or universal annotation layer.

**Implementation cost.** **Medium, mostly native configuration and source-span extraction.**

**Strongest case against.** Page/text anchors can drift across source versions and OCR can be imperfect. The locator must bind to immutable bytes/hash and source version; a failed anchor shows the document without pretending the span is current.

**Unsupported/model-memory claims.** None used.

**Inference.** One evidence click in the demo becomes materially stronger if it opens the exact official page/span rather than a document title. Native viewer variables can implement this without custom code.

**Fetched official facts.** Workshop PDF Viewer supports variable page number and initial search, keyword highlighting/auto-scroll, media references and attachments, and optional annotation objects.[Official: https://www.palantir.com/docs/foundry/workshop/widgets-pdf-viewer] Workshop natively supports media preview, PDF, spreadsheet, video, audio/transcription, image annotation, and Action-driven upload.[Official: https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-in-workshop]

---

## Opportunity 11 — Make source-change ingestion source-native; never simulate CDC

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Q1 “what changed?” with correct ordering, deletion, completeness and latency semantics for each source.

**Change.** Use three source patterns:

1. **True CDC** only for admitted source systems that expose primary key, ordering, and deletion semantics through a supported connector or real changelog stream.
2. **Snapshot + manifest + diff** for ArcGIS, BURP/publication catalogs, WFS and other pull sources. Preserve complete listing snapshots and compute additions/changes/deletions explicitly.
3. **Authenticated push occurrence** for authoritative external outcomes with stable source occurrence ID/version and correction/reversal semantics.

Every lane lands immutable raw input, then curated current facts/occurrences, then a material decision-change projection. Automate triggers on the projection/changed keys; it does not poll every object or expose raw source events in Now.

Do not apply CDC metadata to snapshot data merely to obtain a “real-time” label unless the ordering and deletion contract is genuine and tested. In particular, out-of-order custom streams must be reordered before Ontology indexing.

**Existing mechanism replaced.** One universal “source change event” abstraction; faux CDC over periodic snapshots; client-side refresh as change detection.

**Implementation cost.** **Medium, but aligned with B1.1/B6.**

**Strongest case against.** Three ingestion patterns require different operational runbooks. The common technical envelope and source register still unify assurance; forcing one transport mechanism would simplify diagrams but weaken correctness.

**Unsupported/model-memory claims.** None used.

**Inference.** CORDON's public sources do not all emit real changelogs. Snapshot diff is honest; fake CDC hides missing deletions and ordering.

**Fetched official facts.** Palantir says CDC support is source-system dependent and requires primary key, ordering, and deletion metadata; current direct CDC sync support listed in Data Connection is Db2, SQL Server, Oracle, and PostgreSQL.[Official: https://www.palantir.com/docs/foundry/data-integration/change-data-capture] It warns that the Ontology currently indexes streaming changelog data by arrival order rather than the configured ordering column, so out-of-order custom/backfill streams must be reordered.[same official page]

---

## Opportunity 12 — Selectively auto-refresh the operating picture; never refresh the whole world by default

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Q1 and collaborative operating awareness without input resets, refresh storms, or a visually unstable command scene.

**Change.** Watch only:

- the Now projection rows visible in the active scene;
- the selected semantic object(s);
- the relevant Action log/occurrence object set after command;
- explicitly linked types whose changes affect the shown result.

Set a sensible minimum refresh interval. Pause during command capture (Opportunity 5). Use the Data Freshness widget for index recency, but continue showing CORDON's source assurance/as-of separately. Do not add hidden zero-size widgets merely to force every backstage type to refresh; watch the semantic projection or trigger explicit post-Action recomputation.

**Existing mechanism replaced.** Full-module/global object-set auto-refresh and hidden refresh hacks.

**Implementation cost.** **Low, native Workshop.**

**Strongest case against.** Narrow watched sets can miss a linked change. Maintain an explicit dependency list from each scene to its watched types and test one cross-type update per decision trajectory.

**Unsupported/model-memory claims.** None used.

**Inference.** Auto-refresh is a presentation mechanism, not source assurance. It should update only current operator projections and must not become a substitute for selective impact computation.

**Fetched official facts.** Workshop auto-refresh watches object sets and refreshes the module on Foundry changes, but linked types are not automatically watched; the current minimum interval is 10 seconds; watched object sets must be visible to trigger refresh.[Official: https://www.palantir.com/docs/foundry/workshop/auto-refresh] The same page warns of increased load/cost and input-state resets.

---

## Opportunity 13 — Build a narrow mobile field companion using native scan, location, list/detail and capture

**Disposition:** **PROBE BEFORE ADOPTION**

**Operator decision improved.** “Am I at the right parcel/intervention, what is currently authorized, what evidence must I capture, and where does this hand off?”

**Change.** Prototype a separate mobile Workshop module with exactly this path:

`scan Intervention/Parcel QR or search routed list → verify concise target/authority/readiness → capture current location → attach photo/document/audio where admitted → submit one bounded field Action or handoff → retrieve receipt`

Release-1 field writes should be factual capture/dispatch only if already among the accepted four Actions. Do not invent `Mark complete`, `Accept work`, `Record establishment`, or manual public/bank result Actions. Prefer a direct native Action button/form on mobile to conversational target resolution; add chatbot command only after exact prebound target behavior is proven.

**Existing mechanism replaced.** The vague “mobile companion” promise and any attempt to squeeze the desktop map/capacity/AIP composition onto a phone.

**Implementation cost.** **Probe: medium. Production: medium–high because network, SSO/MFA, device policy and evidence permissions dominate.**

**Strongest case against.** Workshop mobile is browser-based, limited access, disables Map/Table/Chart, and offers no documented offline queue in the retrieved official pages. Rural field connectivity and repeated authentication may make it unsuitable for critical evidence capture. If offline capture is a real requirement, postpone field writes until a purpose-built offline-capable surface or admitted external capture system exists.

**Unsupported/model-memory claims.** An offline guarantee would be unsupported; none is made.

**Inference.** Native QR and location support make a bounded field companion more capable than the accepted design implies, but not a full COP. Exact prebinding is safer than natural-language selection on a small screen in the field.

**Fetched official facts.** Workshop mobile is a browser application; Object Table, Chart, and Map are disabled.[Official: https://www.palantir.com/docs/foundry/workshop/mobile-overview] The QR widget scans QR/barcodes and can use the result to look up an object or populate an Action form.[Official: https://www.palantir.com/docs/foundry/workshop/widgets-qr-reader] Current Location Manager publishes `lat,long` while its page remains open.[Official: https://www.palantir.com/docs/foundry/workshop/widgets-current-location] Mobile access still requires network reachability, Foundry account authentication, SSO and potentially MFA.[Official: https://www.palantir.com/docs/foundry/workshop/mobile-access]

---

## Opportunity 14 — Choose the production model by the frozen Action Eval bar, not by model provenance alone

**Disposition:** **PROBE BEFORE ADOPTION**

**Operator decision improved.** Every natural-language explanation/command, especially exact Action/tool, target, parameters, clarification and abstention.

**Change.** Benchmark at least:

- Llama 3.3 70B Instruct;
- Llama 3.3 Nemotron Super 49B v1.5;
- one strongest currently hosted comparator available to Chatbot Studio in the enrollment.

Use the same frozen cases, temperature/run settings, deterministic application-state inputs and exact tool allowlist. Production selection order:

1. zero hard safety failures;
2. lowest wrong-target/wrong-parameter/correction rate;
3. calibrated clarification rather than guess;
4. acceptable P95 command-to-receipt latency;
5. cost.

Do not fine-tune until production/holdout failures form a coherent, data-solvable error cluster that prompt/tool/state design does not fix. Do not require open-source provenance if it materially reduces exact Action performance, unless deployment policy names that as a real requirement.

**Existing mechanism replaced.** Precommitting to a tuned open-source model, or to one hosted open-source model, before the current model comparison is run.

**Implementation cost.** **Medium, all in AIP Evals/model configuration.** Fine-tuning cost is deferred, potentially eliminated.

**Strongest case against.** Data residency, provider policy, cost predictability, inspectability, or future portability may make hosted open-source a real non-quality constraint. If so, state it as policy and compare only within the allowed set. Exactness still determines which allowed model ships.

**Unsupported/model-memory claims.** No claim is made about which current model will win.

**Inference.** Deterministic target bindings and server-side guardrails reduce the model's required competence; this may let a smaller hosted model pass. Conversely, insisting on open-source without an external policy can sacrifice operator reliability for no product benefit.

**Fetched official facts.** AIP Evals supports test cases, custom evaluation functions, model comparison, previous-version comparison and repeated-run variance.[Official: https://www.palantir.com/docs/foundry/aip-evals/overview] Edit-producing functions run each case in an Ontology simulation, leaving the actual Ontology unchanged.[Official: https://www.palantir.com/docs/foundry/aip-evals/ontology-edits] The live registry probe exposed Llama 3.3 70B and Nemotron Super 49B v1.5 alongside current hosted comparators; this is enrollment evidence, not a platform-wide guarantee.

---

## Opportunity 15 — Narrow Evals to exact trajectories and failure classes; do not build an ML program before a product

**Disposition:** **ADOPT NOW**

**Operator decision improved.** Confidence that a clear command executes once and an ambiguous/unauthorized/stale command does not.

**Change.** Release-1 Eval suite should be finite and trajectory-shaped:

For each Action:

- clear positive;
- ambiguous target/scope;
- unauthorized actor;
- one-premise blocker;
- stale/indeterminate premise;
- changed context after deictic prompt;
- replay/idempotency;
- two requested mutations in one turn;
- prompt injection in retrieved evidence;
- Italian, code-switched, terse and misspelled variants.

Score exact tool, target, parameters, simulated edits, clarification/refusal, prohibited implications, and Action receipt status. Retain failures and group them by root cause. Do not create broad prose-similarity metrics, synthetic “helpfulness” suites, or training pipelines until a measured error demands them.

**Existing mechanism replaced.** A large model-training/evaluation program, exhaustive test taxonomy, or generic chatbot quality program before the four Action trajectories run.

**Implementation cost.** **Medium but bounded.**

**Strongest case against.** A small suite may miss novel language and cross-turn failures. Add cases from real operator corrections and observed production traces, but only after independent review and deduplication; do not substitute raw telemetry for labels.

**Unsupported/model-memory claims.** None used.

**Inference.** CORDON's dangerous behavior is narrow and enumerable. Boolean trajectory gates provide more value than broad aggregate language scores.

**Fetched official facts.** Chatbots can be published as Functions and evaluated in AIP Evals; the suite must be in the same project, new sessions use null `sessionRid`, and object-set variables must be real or null rather than empty.[Official: https://www.palantir.com/docs/foundry/chatbot-studio/chatbots-as-functions] AIP Evals can inspect intermediate outputs and custom evaluators over Ontology edits.[Official: https://www.palantir.com/docs/foundry/aip-evals/intermediate-parameters; https://www.palantir.com/docs/foundry/aip-evals/ontology-edits]

---

## Opportunity 16 — Use native Action-tool confirmation settings deliberately; reject presentation Commands as a domain write path

**Disposition:** **ADOPT NOW for Action configuration; REJECT Commands for writes**

**Operator decision improved.** A clear command causes one governed domain transaction without approval theater or cross-app ambiguity.

**Change.** Configure each of the four Action tools explicitly for automatic execution after a clear prompt. Keep Request Clarification. Use Commands only if a measured presentation need cannot be achieved with native variable updates/events; never use them to modify domain truth. For map centering/selection inside the same Workshop module, prefer deterministic application variables and native events over Command pairing.

**Existing mechanism replaced.** Generic post-prompt approval modal; beta Command-based Action surrogate; paired-app selection dependency.

**Implementation cost.** **Low.**

**Strongest case against.** Some organizations require a separate confirmation gesture for consequential actions regardless of prompt clarity. If that is a real policy, it is not “approval theater”; configure it explicitly per Action. CORDON's accepted policy currently treats the authenticated clear command as the decision.

**Unsupported/model-memory claims.** The current official retrieval did not establish the default confirmation value for Action tools. The build must inspect and set it explicitly.

**Inference.** Action tools provide the governed write plane directly. Commands add client pairing and beta configuration without improving server-side authority.

**Fetched official facts.** Chatbot Studio documents: **“Action: Gives your chatbot the ability to execute an ontology edit. This can be configured to run automatically or to run after confirmation from the user.”**[Official: https://www.palantir.com/docs/foundry/chatbot-studio/tools] Command-tool configuration is Beta and its approval is enabled by default, although it may be disabled.[Official: https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools]

---

## Opportunity 17 — Use saved Workshop state only for shareable investigations, never for authoritative work state

**Disposition:** **LATER**

**Operator decision improved.** Handoff of a filtered population, selected object, or investigative view without creating Task/Case objects.

**Change.** After the primary trajectories work, enable state saving only for benign presentation state such as selected object set, filters, active responsibility facet and current page. Name it “saved view,” not case, task or plan. Do not save Action intent, stale Proposal IDs, fingerprints, free-text command drafts, or receipt status as reusable state.

**Existing mechanism replaced.** Bookmarks/screenshots/manual instructions for returning to an investigation; avoids inventing a generic work object.

**Implementation cost.** **Low.**

**Strongest case against.** Saved state can reload stale selections and variable external-ID changes can break old states. It also creates Compass artifacts and another sharing concept. Add only after operators ask for handoff/bookmarking.

**Unsupported/model-memory claims.** None used.

**Inference.** Saved view is useful collaboration state but dangerous if confused with current decision truth. CORDON can admit it later with a clear stale-state refresh on load.

**Fetched official facts.** Workshop state saving stores selected variable values and optionally the page; users can reopen/share it. It does not automatically persist values across sessions and changing external IDs can break prior states.[Official: https://www.palantir.com/docs/foundry/workshop/state-saving]

---

## Opportunity 18 — Decompose Workshop only at one measured variable-boundary

**Disposition:** **PROBE ONLY IF THE THIN MODULE BECOMES UNMAINTAINABLE**

**Operator decision improved.** Indirectly improves reliability by reducing Workshop configuration errors and load time.

**Change.** Start with one module. If it becomes too large, allow at most one level of embedded children around stable boundaries:

- parent owns context envelope, routing, auto-refresh, command freeze and receipt;
- child may own one reusable evidence viewer or capacity comparator;
- children receive only explicit module-interface variables;
- no child independently computes selected context or auto-refresh policy.

Do not decompose by five responsibilities or six questions.

**Existing mechanism replaced.** One giant variable graph—only if measured—or a premature forest of modules.

**Implementation cost.** **Medium configuration and release coordination.**

**Strongest case against.** Embedded module settings such as routing, state saving and auto-refresh do not inherit; visible nested embedding can create initialization waterfalls; child-to-parent updates require explicit interface behavior. Premature decomposition can be worse than a well-curated single module.

**Unsupported/model-memory claims.** None used.

**Inference.** The right split is reusable presentation logic, not domain responsibility. The parent must remain the sole state owner.

**Fetched official facts.** Palantir recommends embedded modules to separate logic and reduce variables in large modules, and says they have their own variable scopes.[Official: https://www.palantir.com/docs/foundry/workshop/application-design-faqs; https://www.palantir.com/docs/foundry/workshop/embedding-workshop-modules-overview] The same documentation warns of non-inherited module settings and possible loading waterfalls.

---

## Opportunity 19 — Keep custom code behind a strict replacement test

**Disposition:** **ADOPT NOW**

**Operator decision improved.** All decisions, through lower defect surface and faster iteration.

**Change.** Custom code is admitted only if it owns one of these measured jobs:

- source connector behavior unavailable in Data Connection/Pipeline Builder;
- deterministic cross-object prerequisite kernel;
- exact optimizer/capacity algorithm;
- edit logic not expressible safely through Action rules or Scenario merge;
- one measured visualization gap after native prototype.

Native configuration owns:

- adaptive Workshop layouts and state;
- map modes/layers/selection;
- Object Views;
- evidence PDF/media display;
- Action tool allowlist and deterministic inputs;
- Action logs;
- auto-refresh/data freshness;
- mobile QR/location;
- basic scenario tables/charts if admitted;
- Evals configuration and observability.

Before writing a custom capacity widget, build the native comparator. Before writing custom receipt storage, project Action log + occurrence. Before writing map code, configure loading methods and semantic modes. Before writing generic orchestration, use selective pipeline/Automate triggers.

**Existing mechanism replaced.** “At most one custom widget” as an entitlement; custom code introduced because it is allowed rather than because it replaces a missing native mechanism.

**Implementation cost.** **Low policy change; usually lowers build cost.**

**Strongest case against.** Native configuration can become an opaque variable graph that is harder to test and diff than code. The Workshop flip condition remains: if the native implementation requires duplicated state, more than one custom widget, or fails accessibility/mobile needs, move the whole shell to OSDK React rather than continue patching Workshop.

**Unsupported/model-memory claims.** None used.

**Inference.** A capability is valuable only if it replaces custom code, duplicate state, or operator navigation. The strict test prevents platform capability collection.

**Fetched official facts.** Palantir calls Workshop the fastest no-code route and custom widgets an extension for functionality not available out of the box.[Official: https://www.palantir.com/docs/foundry/app-building/overview] It also explicitly permits a single full-page custom widget, but that is capability support, not evidence CORDON should use it.[Official: https://www.palantir.com/docs/foundry/app-building/operational-apps]

---

## 4. Challenged-area verdicts

| Challenged area | Verdict | Why |
|---|---|---|
| Fixed three-pane Workshop | **Change now** | Keep Workshop, replace fixed panes with adaptive decision shell. |
| Five responsibilities | **Compact facets/ribbon** | Accountability lens, not five mini-inboxes or tabs. |
| Six questions | **Implicit scene grammar** | Breadcrumb/explanation, not six queues or statuses. |
| Map scale/layer interaction | **Native semantic modes** | Variable visibility, locked context, viewport/zoom loading, full Map escalation. |
| Contextual authority | **One deterministic kernel/projection** | Show bounded authority card; bind exact context; never let Chatbot infer competence from visible objects/geometry. |
| Population-scale Functions | **Strengthen current split** | Object sets/backend aggregation/pagination; complete discovery stays in pipelines. |
| Scenario/capacity UX | **Probe, do not presume** | Native scenario merge may replace staged-write code; visible Scenario Manager should not be the product grammar. |
| Source-change ingestion | **Source-native patterns** | Real CDC, honest snapshot diff, authenticated occurrences; one material-change projection. |
| Evidence | **Exact native document jump** | Media/file pointer + version/hash + page/search/span; no generic Evidence type. |
| Receipts | **Action log + domain occurrence projection** | Avoid duplicate receipt truth; add focused receipt type only if reconstruction fails. |
| Mobile/field | **Narrow probe** | QR/location/list/detail/capture/handoff; no map parity/offline claim/full management. |
| Hosted model strategy | **Eval-selected candidate** | Open-source hosted models are live and serious; provenance alone does not outrank exactness. |
| Evals | **Finite trajectory suite** | Boolean exact edits/refusals and retained failures; postpone training program. |
| Native vs custom | **Strict replacement test** | Custom only when it removes a measured native gap. |

---

## 5. Ranked recommendations

## Adopt now

1. **Adaptive Workshop decision shell** instead of fixed three-pane layout.
2. **Responsibility facet/ribbon + Q-scene grammar** instead of two persistent navigation systems.
3. **Single versioned context envelope** with deterministic Action/Function inputs.
4. **Semantic Map modes** with variable visibility, locked context layers, viewport/zoom-aware loading and full Map escalation.
5. **Decision-scene freeze during command** plus fresh server-side kernel/fingerprint revalidation.
6. **Explicit Function scale contracts**: object sets, indexed filters, backend aggregations, pagination, bounded digests.
7. **Action log + domain occurrence receipt projection**; no generic Receipt type.
8. **Exact evidence jump** using immutable source version/hash + PDF page/search/span; no release-1 annotation workflow.
9. **Source-native ingestion patterns** and a single material decision-change projection.
10. **Selective auto-refresh** of visible semantic projections; pause during command capture.
11. **Finite Action-trajectory Eval suite** with Ontology simulation, deterministic evaluators and retained failures.
12. **Explicit Action-tool auto/confirm configuration**; no Command-based domain write path.
13. **Strict custom-code replacement test** and native-first comparator prototype.

## Probe before adoption

1. **Scenario-native merge Action** as a replacement for custom staged-write reconstruction, retaining Proposal as digest and decision identity.
2. **Native capacity comparator without custom widget**; add Scenario awareness only if it improves row-level what-if or enables the simpler merge.
3. **Hosted model bake-off**: Llama 3.3 70B, Nemotron Super 49B v1.5, and strongest current hosted comparator against the same frozen suite.
4. **Narrow mobile Workshop field companion** with QR, location, exact target, capture and receipt; validate enrollment access, network, SSO/MFA and device/browser behavior.
5. **One-level embedded-module split** only if the thin module's variable graph or load time becomes measurably unmanageable.
6. **Action-log receipt sufficiency** under response loss/replay/refusal. Add a focused receipt object only if the projected record cannot meet the contract.

## Later

1. Saved/shareable Workshop investigation state after operators request handoff/bookmarking.
2. Durable PDF annotation objects after a real review/annotation decision exists.
3. Fine-tuning after a stable, coherent Eval failure cluster survives prompt/tool/state fixes.
4. Background autonomy Action-by-Action after production correction/idempotency/authority evidence.
5. OSDK React only when a declared flip criterion is actually met: full mobile/offline need, accessibility failure, more than one custom widget, or irreducible state duplication.
6. Full Map/Vertex/Object Explorer investigator escalations after routine trajectories work.

## Reject

1. Fixed central Map for every decision merely because CORDON is geospatial.
2. Five responsibility tabs or mini-inboxes.
3. Six question tabs, six statuses, or a progress funnel.
4. Visible Scenario Manager as the routine capacity grammar.
5. Client-generated capacity edit plans or a second edit payload beside Proposal/Scenario.
6. Generic Task, Case, Queue, WorkItem, Evidence, Receipt, Status, Readiness or Completion types without a real independent grain.
7. Commands or app pairing as a second domain write plane.
8. Parallel mutating tools or model retry after uncertain Action response.
9. Full-population `.all()` in interactive Functions or per-object Ontology queries in loops.
10. Faux CDC over periodic snapshots.
11. Generic “refresh everything” auto-refresh and hidden widget hacks across backstage types.
12. Mobile parity claims, offline claims, or critical field capture before network/auth/device tests.
13. Fine-tuning because a training capability exists.
14. A custom capacity widget before native table/chart/metric/proposal comparison is proven insufficient.
15. More platform governance, approvals, prefixes, folders, manifests, tests or release ceremony than changes a real operator decision or prevents a demonstrated failure.

---

## 6. Specific anti-complexity cut list

These cuts are concrete build changes, not general principles.

1. **Cut the fixed three-pane requirement.** Keep the semantic shell; make Map/AIP/evidence/comparison widths scene-dependent.
2. **Cut five persistent responsibility content lines.** Keep one compact all-five facet/ribbon with zero states visible.
3. **Cut clickable Q1–Q6 navigation.** Keep one variable-backed scene and optional breadcrumb.
4. **Cut the always-expanded Map legend/layer catalog.** Ship four named semantic modes and allowlisted expert overlays.
5. **Cut independent map/chat/widget target state.** One logical context envelope owns selection and generation.
6. **Cut LLM-generated target IDs, Proposal IDs and fingerprints.** Bind deterministic inputs from application state.
7. **Cut non-deterministic application-variable updates for Action scope.** Tool/context outputs update deterministically; deictic changes force a new turn/clarification.
8. **Cut a separate generic Receipt object.** Start with Action log + typed occurrence + projection.
9. **Cut release-1 annotation objects.** Use exact page/search/span. Admit annotations only when users author a durable review fact.
10. **Cut visible Scenario management.** CORDON creates bounded alternatives; the manager compares business consequences.
11. **Cut custom staged-write reconstruction if the Scenario merge probe passes.** Keep only the revalidation/digest contract.
12. **Cut Scenarios entirely from release 1 if they neither replace code nor improve comparison.** Proposal + bounded Action remains sufficient.
13. **Cut custom map code.** Use native object/overlay layers, variable visibility, locks, loading methods, zoom visibility and full Map escalation.
14. **Cut the custom capacity widget entitlement.** It must fail a named native prototype first.
15. **Cut full-population interactive Function materialization.** Pipelines own complete discovery; Functions own bounded current resolution/explanation.
16. **Cut exact top-bucket assumptions in Workshop.** Compute authoritative counts in Functions/pipelines; use UI histograms for orientation only.
17. **Cut one universal source-change abstraction.** Keep a shared envelope but three honest acquisition semantics: CDC, snapshot/diff, authenticated occurrence.
18. **Cut broad auto-refresh.** Watch Now/selection/receipt dependencies only and freeze during command capture.
19. **Cut mobile Chatbot as the default field write path.** Start with scan-bound direct Action forms/buttons; chat is optional after exactness proof.
20. **Cut desktop-map parity on mobile.** Mobile is scan/location/read/capture/handoff.
21. **Cut an open-source-model production mandate unless policy requires it.** Make model selection an Eval result.
22. **Cut fine-tuning and training-data machinery from the first release.** Retain cases/failures; train only after a proven error cluster.
23. **Cut broad prose-quality Evals.** Score exact tools, targets, parameters, edits, clarification, refusal and prohibited implications.
24. **Cut Command tools for native Workshop presentation if variables/events suffice.** Avoid beta pairing/state ownership.
25. **Cut early Workshop module decomposition.** One parent first; one level of child modules only at a measured reusable boundary.
26. **Cut saved-state ontology preferences.** Add saved views later; do not create a User Preference type for release 1.
27. **Cut generic investigator applications from routine navigation.** Full Map, Object Explorer and Vertex remain explicit read-only escalations.
28. **Cut duplicate freshness concepts.** Data Freshness shows index recency; source register/assurance owns source currency; `INDETERMINATE` owns decision impact.
29. **Cut hidden observability from operator history.** Action log/trace/lineage remain backstage; typed occurrences and projected receipts face the operator.
30. **Cut any new feature whose replacement sentence is empty.** “Foundry offers it” is not a reason. Every admitted mechanism must replace code, duplicate state, operator navigation, or a demonstrated correctness risk.

---

## 7. Recommended thin-prototype sequence

This sequence resolves the highest-risk product assumptions before adding breadth.

1. **Adaptive shell:** one Now row, one context envelope, two modes—spatial and capacity/authority—using native variable-backed layout.
2. **Exact selection:** map/list selection updates one object-set context and generation; Chatbot receives minimal visible state.
3. **Exact command:** deterministic target/proposal input; one Action; command-scene freeze; real Action refusal/commit.
4. **Receipt:** reconstruct committed receipt from Action log + domain occurrence after intentionally suppressing natural-language response rendering.
5. **Evidence:** one official PDF opens to exact page/search from the selected proposition.
6. **Map scale:** full-region layer configured with loading method/zoom visibility; selected member scope remains exact.
7. **Capacity A/B:** native Proposal comparator first; then the Scenario merge probe. Keep the mechanism with fewer states/code that passes the complete matrix.
8. **Model A/B:** run the same frozen Action cases across hosted candidates; production choice follows results.
9. **Mobile spike:** QR → exact object → location → concise read → permitted capture/handoff; test real mobile network/auth.
10. **Only then:** decide custom widget, embedded module split, saved states, fine-tuning, or OSDK React.

### Stop conditions

- If native Workshop completes the four Action trajectories with one context contract, keyboard accessibility, exact receipt recovery, and no more than one bounded custom widget, keep Workshop.
- If Scenario merge does not eliminate staged-write code or weakens exact refusal/receipt behavior, reject it.
- If native capacity comparison shows the full Proposal digest and alternatives coherently, do not write a custom widget.
- If mobile requires offline capture or full Map/capacity management, do not patch Workshop mobile; reopen OSDK/external field architecture.
- If a hosted open-source model clears the exact same safety/quality bar, prefer the lowest-cost/lowest-latency allowed model. If it does not, do not lower the bar.

---

## 8. Final recommendation

Adopt **Workshop-native, but not three-pane-literal**.

The best current-platform composition for CORDON is:

- one adaptive Workshop decision shell;
- one Now projection and compact responsibility facet;
- Q1–Q6 as variable-backed scene grammar;
- one context envelope;
- native semantic Map modes that expand only when relevant;
- configured Object Views and exact PDF/media evidence jumps;
- embedded Chatbot with minimal visible state and deterministic exact tool inputs;
- four server-guarded Actions, four bounded read Functions, one mutation per turn;
- Action log + typed occurrence as receipt backbone;
- proposal-first capacity comparison, with Scenario merge admitted only if its probe removes staged-write complexity;
- source-native ingestion and selective refresh;
- a narrow, separately tested mobile field companion;
- current hosted models compared under one finite, Boolean Action-trajectory Eval suite;
- custom code only where it demonstrably replaces a missing native mechanism.

This is a smaller product than the accepted literal screen composition and a stronger operational system. It makes the manager's current decision—not the Map, Chatbot, responsibility taxonomy, Scenario machinery, or Foundry capability catalog—the permanent center of the application.

---

## Official sources consulted

1. https://www.palantir.com/docs/foundry/workshop/variable-backed-layouts
2. https://www.palantir.com/docs/foundry/workshop/application-design-best-practices
3. https://www.palantir.com/docs/foundry/app-building/operational-apps
4. https://www.palantir.com/docs/foundry/chatbot-studio/application-state
5. https://www.palantir.com/docs/foundry/workshop/widgets-map
6. https://www.palantir.com/docs/foundry/map/objects-loading-methods
7. https://www.palantir.com/docs/foundry/map/visualize-objects
8. https://www.palantir.com/docs/foundry/workshop/auto-refresh
9. https://www.palantir.com/docs/foundry/object-edits/how-edits-applied
10. https://www.palantir.com/docs/foundry/functions/optimize-performance
11. https://www.palantir.com/docs/foundry/ontologies/oss-limitations
12. https://www.palantir.com/docs/foundry/action-types/scale-property-limits
13. https://www.palantir.com/docs/foundry/ontology/merge-scenario
14. https://www.palantir.com/docs/foundry/workshop/scenarios-concepts
15. https://www.palantir.com/docs/foundry/ontology/temporary-scenario
16. https://www.palantir.com/docs/foundry/ontology/persisted-scenario
17. https://www.palantir.com/docs/foundry/workshop/scenarios-getting-started
18. https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario
19. https://www.palantir.com/docs/foundry/action-types/action-log
20. https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk
21. https://www.palantir.com/docs/foundry/workshop/widgets-pdf-viewer
22. https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-in-workshop
23. https://www.palantir.com/docs/foundry/data-integration/change-data-capture
24. https://www.palantir.com/docs/foundry/workshop/mobile-overview
25. https://www.palantir.com/docs/foundry/workshop/widgets-qr-reader
26. https://www.palantir.com/docs/foundry/workshop/widgets-current-location
27. https://www.palantir.com/docs/foundry/workshop/mobile-access
28. https://www.palantir.com/docs/foundry/aip-evals/overview
29. https://www.palantir.com/docs/foundry/aip-evals/ontology-edits
30. https://www.palantir.com/docs/foundry/chatbot-studio/chatbots-as-functions
31. https://www.palantir.com/docs/foundry/aip-evals/intermediate-parameters
32. https://www.palantir.com/docs/foundry/chatbot-studio/tools
33. https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools
34. https://www.palantir.com/docs/foundry/workshop/state-saving
35. https://www.palantir.com/docs/foundry/workshop/application-design-faqs
36. https://www.palantir.com/docs/foundry/workshop/embedding-workshop-modules-overview
37. https://www.palantir.com/docs/foundry/app-building/overview

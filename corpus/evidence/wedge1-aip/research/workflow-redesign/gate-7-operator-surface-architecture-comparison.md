# Gate 7 — operator-surface architecture comparison

Status: **GATE 7 ACCEPTED AND CLOSED — binding Workshop-native operator-surface architecture**
Date: 23 August 2026  
Authority: `REDESIGN_SEQUENCE.md`; `connected-operating-model.md`; `gate-5-reconciled-operator-graph.md`; `gate-6-capability-reconciliation.md`; the two Gate 6 mechanism-purpose ledgers  
Boundary: operator-surface architecture only. No Foundry writes, no physical property types, no new semantic object/link/Action/Function design.

## 1. Decision and provenance discipline

### Accepted architecture

Owen accepts a **Workshop-native Decision Loop**: one desktop Workshop operational application with an embedded, published AIP Chatbot; a native Workshop Map as a synchronized orientation mode rather than the home or authority surface; configured panel/full Object Views for object drill-through; and **one bounded OSDK custom widget only for the complete capacity-scenario comparison** if native Scenario widgets cannot render the required alternatives, sensitivities and complete proposal diff without fragmentation. Standalone Map, Object Explorer and Vertex remain explicit escalation destinations, not routine legs of the operating loop.

The interaction grammar is:

```text
material change or manager question
→ focus one bounded decision scene
→ inspect consequence, basis, owner, clock and spatial context as needed
→ compare alternatives when material
→ issue one explicit conversational command
→ clarify only material ambiguity OR execute one exact Action directly
→ show durable receipt, bounded result, non-implications and next handoff
→ selectively refresh affected and explicitly unaffected work
```

This is **not** five responsibility tabs, six question tabs, an object catalog, a task queue, a map-first product or a chatbot-only product. Land, Funding, Applications, Field Work and Payments remain responsibilities; Q1–Q6 remain the recursive reasoning grammar.

### Strongest case against the recommendation

A purpose-built OSDK React application could provide a cleaner responsive shell, tighter keyboard/screen-reader semantics, a single controlled state machine, stronger visual treatment of indeterminate state, and a genuinely unified mobile/desktop design. Workshop's variable/event graph can become an invisible second application model; its current mobile mode disables the Object Table, Chart and Map; and a custom scenario widget introduces a second release unit. If usability testing shows that the Workshop implementation needs more than one custom widget, duplicates selected context in several variable graphs, or cannot complete the four Action trajectories with keyboard-only operation, the recommendation should flip to the OSDK React grammar rather than accrete patches.

### Provenance labels used below

- **DOCUMENTED FACT** — current official Palantir documentation states the capability or lifecycle.
- **PROJECT FACT** — accepted Gate 2–6 CORDON contract supplied in this repository or confirmed by Owen.
- **INFERENCE** — consequence derived from documented platform behavior plus the CORDON contract; must be tested in the target enrollment.
- **DESIGN RECOMMENDATION** — the selected interaction or architecture choice; it is not a platform fact.
- **UNKNOWN / TEST REQUIRED** — current official documentation reviewed here does not establish the claim.

Palantir's own current operational-application guidance says to start with the decision rather than the screen, surface only the information needed at that moment, compare consequences before commitment, and let the user make the decision in the same application through Ontology Actions.[1] That is a documented platform principle, not evidence that any prebuilt application automatically satisfies CORDON.

## 2. Fixed Gate 7 acceptance frame

### Project facts that no candidate may redesign

1. The manager must answer Q1–Q6 across 30 capabilities without a global case status, generic readiness, generic completion or undifferentiated exception queue.
2. All candidates consume the same 11 visible fact owners, hidden typed substrate, accepted semantic links, four exact read Functions and four exact function-backed manager Actions.
3. Conversational direct execution is required ingress but not preselected navigation. A clear authenticated prompt executes exactly one Action after all guards; material ambiguity causes clarification, not a generic approval modal.
4. Background AIP/Automate initially detects, recomputes, prepares, routes and notifies; it does not execute the four manager Actions without a manager command.
5. A scenario is hypothetical; a Capacity Portfolio Proposal is the sole executable digest; the manager's command commits it.
6. Geometry is orientation and a candidate premise, never law, authority, duty, permission or readiness.
7. Current decision state, factual history, evidence, Action receipt, technical audit and health are distinct.
8. A load-bearing stale, unhealthy or unresolved premise produces an indeterminate answer and an Action refusal; last-good data must not masquerade as current.
9. Backstage types, pipelines, logs, prompts, traces, model internals and ingestion mechanics do not become operator workflow.
10. Release compatibility binds Ontology, Functions, Actions, Chatbot, model, Automate and surface versions.

### Evaluation dimensions

A serious candidate is evaluated against:

- Q1–Q6 and all `L1–L6`, `F1–F6`, `A1–A6`, `W1–W6`, `P1–P6` capabilities;
- spatial orientation and spatial target inspection;
- scenario comparison and exact proposal binding;
- direct AIP Action execution and clarification;
- evidence and cited basis;
- stale, indeterminate, refused and degraded states;
- mobile/field use;
- accessibility;
- customization and scalability;
- release, branching and rollback;
- hidden-mechanism suppression;
- operator burden and duplicated navigation.

## 3. Complete plausible platform-native surface universe

**Candidate count: 22.** “In the universe” means relevant enough to evaluate, not that it is a serious runtime candidate. Official docs distinguish workflow-specific application builders from walk-up discovery/analysis applications and identify Workshop, OSDK React, custom widgets, Slate, Code Workspace apps and REST-built applications as operational-app construction paths.[1][2][3]

| ID | Surface or composition | Current documented fact | CORDON role and disposition |
|---|---|---|---|
| U01 | **Workshop** | No-code/object-oriented operational application builder using Ontology objects, links, Functions, Actions, layouts, events and widgets.[2][3] | **Serious runtime family.** Fastest native route and best baseline for the complete Decision Loop. |
| U02 | **OSDK React application** | Typed React hooks query objects/sets/links/aggregations, validate/apply Actions, call Functions, cache objects and synchronize affected cache entries.[7] | **Serious runtime family.** Best custom/responsive ceiling; higher engineering and release burden. |
| U03 | **Workshop + native OSDK custom widget** | Custom widgets securely extend Workshop with frontend code and are currently supported only in Workshop.[14] | **Serious runtime family.** Use only for one measured interaction gap, not as a full-page rewrite hidden inside Workshop. |
| U04 | **Slate integrated application** | Current, responsive, drag-and-drop application builder with CSS/HTML/JS customization, Ontology, Functions and Actions.[12] | **Serious runtime family.** Viable, but more technical and easier to create a parallel client model than Workshop. Public Slate is not relevant to the authenticated manager runtime. |
| U05 | **Code Workspace application (Dash/Streamlit/Shiny)** | Published interactive apps run in Foundry containers with branching, version control and governance; Jupyter currently publishes Dash/Streamlit and supports Ontology interaction.[2][13] | **Serious runtime family.** Valuable for model/analysis prototypes; weaker fit for a primary low-latency governed operating shell. |
| U06 | **Externally built REST/API application** | Foundry REST APIs can query objects, apply Actions and call Functions from any runtime.[2] | **Serious comparison baseline, not platform-native shell.** Maximum UI freedom; maximum burden for auth, caching, observability, release and cross-app integration. Grouped with OSDK only where implementation actually uses OSDK. |
| U07 | **Standalone Map / map template** | Map provides geospatial/temporal search, network traversal, high-scale layers, imagery, shape drawing and geospatial Actions.[5][33] | **Supporting application, not complete home.** Strong orientation; weak nonspatial six-question continuity and conversational embedding. |
| U08 | **Workshop native Map widget** | Object/overlay layers, object-set/shape variables, selection, spatial search, Search Around, timeline and transition to full Map; optimized for desktop and not supported in mobile modules.[6] | **Required ingredient in recommendation.** Spatial lens inside the same decision scene, not an authority surface. |
| U09 | **Standard/configured Object Views** | Reusable full and panel representations; standard views exist for all types, configured views are built with Workshop.[10] | **Supporting drill-through.** Canonical object biography and linked context, not a portfolio/change operating home. |
| U10 | **Object Explorer** | Walk-up search, filters, object-set comparison, maps/charts, Object Views, saved explorations and bulk Actions.[11][32] | **Discovery/support, not primary.** Excellent unplanned search; too exploratory and object-set centric for the bounded Action loop. |
| U11 | **Vertex standalone** | Graph exploration traverses Ontology relationships and supports reusable graphs/templates.[35] | **Investigation escalation.** Graph topology is useful for unusual authority/dependency questions but too dense as daily operating grammar. |
| U12 | **Workshop + embedded Vertex graph** | Graphs/templates/diagrams embed in Workshop, accept variables/scenarios, emit selected object sets and can expose an allowlist of Actions.[21] | **Conditional supporting composition.** Prefer read-only and only where a graph answers a measured question better than links/Object Views. |
| U13 | **Workshop + paired/embedded Gaia, Graph, Vertex or another command-capable app** | App Pairing shares state in real time; Commands target paired apps; Gotham Gaia/Graph and Vertex are named supported examples.[16][17] | **Serious cross-app runtime family.** Consider only if the target enrollment and workflow truly require the second application's native capability. Pairing is not automatically a candidate. |
| U14 | **Quiver analysis/dashboard** | Object-aware exploratory analysis, charting, aggregations and time-series; analyses can publish as dashboards.[3][37] | **Analysis adjunct.** Useful backstage/secondary sensitivity analysis; not direct command-and-receipt runtime. |
| U15 | **Insight** | Current point-and-click Ontology analysis path for informed analysis over known modeled data.[36] | **Analysis adjunct.** Useful for investigator drill-down; not the controlled manager write plane. |
| U16 | **Contour** | Dataset-scale visual analysis and transforms rather than the operator Ontology workflow.[38] | **Backstage analytics only.** Reject as operator home because it exposes physical data grain and bypasses the accepted semantic projection. |
| U17 | **Carbon curated workspace** | Combines applications/resources such as Workshop, Slate, Object Views and Object Explorer into curated workspaces.[3][34] | **Portal/container only.** May curate entry points, but cannot repair duplicated navigation or become the interaction grammar. |
| U18 | **AIP Chatbot embedded in Workshop** | The recommended Workshop widget embeds a published Chatbot Studio chatbot, maps application variables, and can use Commands for embedded applications.[4] | **Required runtime ingredient.** It is the direct-execution ingress inside U01/U03/U13, not a standalone visual architecture. |
| U19 | **AIP Chatbot embedded in OSDK/custom app via APIs** | Chatbot APIs provide sessions, streaming/blocking exchanges, application-state input/output and history; Developer Console resource allowlists must be updated when chatbot resources change.[20] | **Required ingredient for U02/U06.** Powerful but the custom shell owns all context binding, receipt recovery and UI states. |
| U20 | **AIP Assist/AIP Threads chatbot panel** | Chatbots can be published to AIP Assist and paired to target apps; Chatbot Studio builds secured assistants with Ontology, document and tool context.[17][19] | **Fallback/discovery channel, not primary.** Pairing ambiguity and panel context make it weaker than an embedded operating picture. |
| U21 | **Pilot** | Beta AI builder that produces either standalone OSDK React apps or Workshop custom widgets, with isolated seed data, Global Branch promotion, CI and release.[15] | **Builder only.** It may accelerate U02/U03; its generated runtime is evaluated as U02/U03. It must not regenerate the accepted Ontology or become runtime authority. |
| U22 | **AI FDE** | Platform builder agent for governed development across Foundry resources.[22] | **Builder only.** It may build/review the selected surface on a branch; it is not the CORDON chatbot, user identity, navigation or alternate write plane. |

### Explicit non-candidates and conditionality

- **AIP Chatbot Studio is a harness, not a screen architecture.** It becomes operational only through Workshop, OSDK/API, AIP Assist/Threads or a paired application.[19][20]
- **Map, Object Views, Object Explorer and Vertex are not automatically candidates because they can show the Ontology.** Each is admitted only for its native orientation, biography, discovery or graph investigation capability.
- **Gaia and Graph pairings are conditional on Gotham availability and a real unmet need.** Cross-app documentation shows the mechanism, not that CORDON should require another platform application.[16]
- **Public Slate and Consumer Mode are excluded.** The manager is authenticated and must execute function-backed Actions and Functions under the caller's permissions.
- **Pilot and AI FDE are not runtime grammars.** Comparing their builder UX to an end-user Workshop/OSDK UX is a category error.

## 4. Six serious runtime families

Codes used below:

- **W** — Workshop only, with native widgets and embedded Chatbot.
- **R** — standalone OSDK React application with embedded Chatbot APIs.
- **WC** — Workshop plus one or more OSDK custom widgets.
- **S** — Slate integrated application.
- **CW** — Code Workspace app (Dash/Streamlit/Shiny).
- **XP** — cross-app Workshop paired/embedded with Map/Gaia/Graph/Vertex as applicable.

Ratings: **N** native/low-friction fit; **E** achievable but extension or material code/configuration required; **D** degraded or high-burden fit; **X** violates or cannot credibly satisfy the first-release contract. Ratings compare surface fit, not backend availability.

### 4.1 Q1–Q6 fit

| Question | W | R | WC | S | CW | XP | Finding |
|---|---:|---:|---:|---:|---:|---:|---|
| Q1 What changed/affected? | N | E | N | E | D | N | Workshop variables, Function-backed projections and synchronized map/list views fit selective affected/unaffected work. React can equal it but must implement refresh, caching and health semantics. |
| Q2 Required/allowed/blocked? | N | E | N | E | D | N | All can call the exact Function; Workshop/Object Views provide low-code context. XP helps only when spatial/graph relation is consequential. |
| Q3 Who decides/which route? | N | E | N | E | D | E | Workshop/React can keep authority, member choice, pursuit, public outcome and capacity separate. Cross-app surfaces risk scattering that separation across panels. |
| Q4 Ready for named Action? | N | E | N | E | D | N | Native Action/Function binding favors Workshop. React offers superior bespoke refusal UI but more implementation. Map/graph adds only contextual premises. |
| Q5 Done/accepted by whom? | N | E | N | E | D | E | Object Views and scoped occurrence projections work well. Graph/map is secondary, not chronology. |
| Q6 Landed/remaining open? | N | E | N | E | D | D | Workshop/React can render independent legal/operational/financial/biological lines. A spatial/graph pair adds little and increases navigation. |

### 4.2 Thirty-capability coverage

| Capability | W | R | WC | S | CW | XP | Surface-specific note |
|---|---:|---:|---:|---:|---:|---:|---|
| L1 Inspect land change/affected work | N | E | N | E | D | N | XP earns N only when selection sync preserves the exact affected set and current date. |
| L2 Compare duties/permissions/holds | N | E | N | E | D | N | Never color a polygon as a legal verdict. |
| L3 Select land route to coordinate | N | E | N | E | D | E | Selection must invoke only accepted cooperative Actions; most land-route choices remain preparation/routing. |
| L4 Explain land consequence/authority | N | E | N | E | D | N | Evidence drawer/Object View plus selected parcel map is sufficient. |
| L5 Stage correction/access/compliance | N | E | N | E | D | E | Staging is a routed package, not an extra truth-writing Action. |
| L6 Handoff/reopen on change | N | E | N | E | D | E | Workshop events/variables fit routing; React needs explicit state invalidation. |
| F1 Inspect opportunity/population change | N | E | N | E | D | D | Population is list/aggregate first; map-first XP is actively misleading. |
| F2 Compare routes/feasible portfolios | E | E | N | E | E | D | WC supplies the strongest bounded scenario comparator if native widgets fragment the complete plan. |
| F3 Select pursuit/commit capacity | N | E | N | E | D | D | Direct Chatbot Action plus immutable Proposal ID is required; no client edit plan. |
| F4 Explain inclusion/deferral/fallback | N | E | N | E | D | D | Side-by-side alternative consequences beat map/graph encoding. |
| F5 Stage adhesion/mandate/pursuit | N | E | N | E | D | D | Object details + routed package; do not collapse the three decisions. |
| F6 Handoff funded/fallback route | N | E | N | E | D | E | Selected context and bounded next owner must persist across the handoff. |
| A1 Inspect application change | N | E | N | E | D | D | Change stream plus proceeding context; no portal-form mimicry. |
| A2 Compare filing routes/requirements | N | E | N | E | D | D | Exact named-Action readiness and cure owners. |
| A3 Select filing/repair route | N | E | N | E | D | D | Most outputs are prepared/routed because release belongs to another actor. |
| A4 Explain readiness/public result | N | E | N | E | D | D | Required distinction: receipt ≠ admissibility ≠ concession. |
| A5 Stage/release application action | E | E | E | E | D | D | First release stages/routes; no unaccepted non-manager write tool is invented. |
| A6 Handoff application result | N | E | N | E | D | D | Receipt and authority outcome remain separately visible. |
| W1 Inspect readiness/field change | N | E | N | E | D | N | Map/graph context can materially help locate scope and affected resources. |
| W2 Compare routes/schedules/readiness | N | E | N | E | E | N | Map plus schedule/detail comparison is useful, but map cannot become route logic. |
| W3 Select scope/commit resources | N | E | N | E | D | N | Capacity Action stays proposal-bound and atomic regardless of shape selection. |
| W4 Explain dispatch/performance/acceptance | N | E | N | E | D | N | Spatial scope plus separate occurrence chronology. |
| W5 Dispatch/record authorized work | N | E | N | E | D | N | Direct command executes Dispatch; selected map objects are context, never authority. |
| W6 Handoff accepted work/aftercare | N | E | N | E | D | E | Mobile companion may be valuable, but acceptance and establishment remain separate. |
| P1 Inspect financial change | N | E | N | E | D | D | Nonspatial line-item view; map/graph is noise. |
| P2 Compare claims/spend/cash exposure | N | E | N | E | E | D | Tables/independent financial lines; never a single amount/status. |
| P3 Select claim/release path | N | E | N | E | D | D | Manager coordinates; beneficiary release remains external unless later admitted. |
| P4 Explain claim readiness/where money is | N | E | N | E | D | D | Entitlement, admission, liquidation, order, cash and recovery all remain visible. |
| P5 Stage/release payment claim | E | E | E | E | D | D | Initial product stages/routes; it does not add a manager release Action. |
| P6 Handoff settlement/shortfall/recovery | N | E | N | E | D | D | Bounded receipt/exposure view; no `paid` status. |

**Inference:** W and WC lead because they can consume native Ontology primitives and Chatbot state while keeping the operator inside one configured workflow. R is not functionally weaker; its `E` scores represent engineering work, not API absence. CW scores poorly because its documented strength is publishing analysis applications from data-science environments, not maintaining a tightly governed multi-surface command state machine.[13]

### 4.3 Cross-cutting fit

| Dimension | W | R | WC | S | CW | XP |
|---|---|---|---|---|---|---|
| Spatial orientation | **N** native Map widget | **E** custom map integration | **N** native Map + custom comparator | **E** Slate map/custom code | **E** framework map | **N+** immersive native app |
| Scenario comparison | **E** native Scenario widgets/config | **E** custom exact view | **N** bounded comparator widget | **E** custom | **E** analytical prototype | **E/D** split across apps |
| Direct Chatbot Action execution | **N** published widget + exact tools | **E** session/API integration | **N** same as W | **E** custom integration path | **D** substantial integration | **N/E** Chatbot + Commands, but Commands are presentation tools, not replacement Actions |
| Evidence/media | **N** Object View/viewers/drawer | **N** React components/custom | **N** | **E** | **E** | **E** often opens second app/panel |
| Indeterminate/degraded state | **E** must design explicit projection | **N** full state-control ceiling | **N** custom comparator + Workshop banners | **E** | **E** | **D** state can disagree across paired apps |
| Mobile/field | **D** limited-access mobile; Map/Table/Chart disabled | **N/E** responsive app is builder-owned | **D** custom widget support must be tested | **E** responsive but field behavior must be built | **E** framework-dependent | **X/D** multi-app pairing is desktop-heavy |
| Accessibility | **E/UNKNOWN** native controls help; complete WCAG claim not documented | **N ceiling / builder-owned** | **E** custom widget adds test burden | **E** builder-owned CSS/JS | **D/E** framework-dependent | **D** keyboard/focus crosses app boundaries |
| Visual/custom interaction | **E** bounded by Workshop | **N** | **N/E** targeted custom code | **N** | **E** | **D** each app keeps its own grammar |
| Population scalability | **N** object sets/aggregations; avoid client arrays | **N** typed object-set queries | **N** | **E** | **E** app/server tuning | **N spatial, D whole workflow** |
| Release/rollback | **N/E** Global Branch + package compatibility | **N but heavier** repository, tag, checks, Developer Console release[9] | **E** Workshop + widget versions | **E** app lifecycle | **E** branch/publish lifecycle[13] | **D** coordinated multi-app/template/chatbot release |
| Hidden-mechanism suppression | **N if curated** | **N if disciplined** | **N if widget is bounded** | **E** dataset access tempts leakage | **D** analytical substrate leaks easily | **D** native panels expose layers/graph mechanics |

### Direct execution invariant for all six

**DOCUMENTED FACT:** Chatbot Studio tool classes include Actions, object queries, Functions, application-variable updates, Commands and clarification; application state can bind object sets/strings to the surrounding application.[23][24] Commands act in paired client applications and ask for approval by default, though builders can disable that approval; command-tool configuration is beta.[17]

OSDK React's prebuilt component set currently covers object tables, aggregation-backed filters, Action forms and common media viewers.[8]

Ontology Actions are the governed transaction mechanism, Functions provide server-side compute, and Ontology Scenarios isolate hypothetical changes from main state.[25][26][27]

Data Health supplies technical monitoring, but CORDON still has to translate a failed load-bearing premise into an operator-visible indeterminate answer.[30]

**DESIGN RECOMMENDATION:** The four CORDON Ontology Actions are **Action tools**, not Commands. A clear authenticated prompt invokes exactly one Action directly. Commands are allowlisted only for reversible presentation operations such as center map, select view, show object set or open read-only graph. This prevents a beta client command from becoming an alternate domain write plane or reintroducing a redundant approval modal.

Every surface must implement the same visible exchange:

```text
clear command
→ “Executing Dispatch Intervention for INT-… on Parcels …” (material scope, not approval request)
→ exact Action call under caller identity
→ COMMITTED | ALREADY_COMMITTED | REFUSED | CLARIFICATION_REQUIRED
→ durable receipt + changed bounded facts + explicit non-implications + next owner
```

If scope, target, proposal, date, authority or override reason is materially ambiguous, the Chatbot asks one focused question. If application selection changed after the message, it clarifies rather than following stale deictic context.

## 5. Four coherent competing interaction grammars

These are end-to-end prototypes. They are not component menus.

### Grammar A — Workshop Decision Loop (**recommended**)

**Opening condition.** The manager enters one “Now” view showing material changes and bounded work requiring coordination, grouped by consequence/clock rather than responsibility or generic status. The first item is selected; a compact context ribbon names member/land/route, current owner, consequential date, source health and scope.

**Interaction.** The primary Workshop keeps three panes visible: a Now/context rail with five persistent responsibility lines; the synchronized Map operating picture; and the AIP decision/execution panel. Selecting Land, Funding, Applications, Field Work or Payments changes the relevant Map layers, Q1–Q6 decision scene and AIP context without resetting the selected member/land/date/route. The Map is core but never authority: visual selection supplies candidate scope and server logic resolves consequence.

**Decision.** The manager asks, compares or commands in natural language. For capacity, a complete alternative comparison opens before selection; the selected immutable Proposal ID returns to the conversation. One clear command executes the exact Action without a second approval popup.

**After.** A receipt strip replaces the command state: result, affected object count, bounded edit summary, kernel/Action version, premise fingerprint, non-implications and next handoff. The Now view selectively refreshes affected work and leaves explicitly unaffected work stable.

**Degraded behavior.** A stale/failed premise produces a persistent `INDETERMINATE` banner scoped to the invalid answers, disables the affected Action through real platform/function guards, names the last accepted source watermark and cure owner, and preserves unrelated work.

**Why coherent.** One selected-context contract drives list, map, Object View, Functions and Chatbot. The operator never navigates to histories, logs or pipelines; those are projections/drill-throughs.

### Grammar B — Bespoke OSDK adaptive fieldbook

**Opening condition.** A responsive OSDK React shell opens to an adaptive workstream. Desktop uses three regions; tablet/phone serializes the same scene into context → question → evidence → command → receipt without changing semantic state.

**Interaction.** A custom state machine binds all visual modes, Chatbot session, object cache and health. Map/list/graph are interchangeable projections of one selected object set. Evidence, authority and occurrence lines use bespoke accessible patterns.

**Decision.** The embedded Chatbot API streams the conversation; direct Actions use the same exact Action APIs and Function results. The client never directly constructs capacity edits; it passes Proposal ID. A receipt-recovery endpoint restores committed results after a dropped stream.

**After/degraded behavior.** The client can make indeterminate, offline, stale-context and uncertain-response states first-class and can implement strict focus/keyboard behavior.

**Why coherent.** One coded application state machine, not a set of Foundry app tabs. Its weakness is not interaction quality but duplicated engineering for state, map, evidence, mobile, accessibility, telemetry and release.

### Grammar C — Spatial command deck (Workshop + paired Map/Gaia/Graph/Vertex)

**Opening condition.** A full spatial or graph application is the visual focus; Workshop provides the decision rail and embedded Chatbot. Pairing synchronizes selected objects, viewport/time and allowlisted presentation Commands.

**Interaction.** The manager starts from land or relationship topology, then asks what the selection affects. The Chatbot can center, zoom or open a related graph through Commands and calls Functions/Actions through backend tools.

**Decision.** The same direct Action contract applies; a shape or node selection only supplies target candidates. Nonspatial alternatives, payment lines and evidence appear in Workshop.

**After/degraded behavior.** A pairing indicator is always visible. Lost pairing freezes cross-app commands and falls back to Workshop-selected context; it must never silently retarget another open app.

**Why coherent.** It is coherent only for a spatially dominant shift. For CORDON as a whole, it makes the map/graph the grammar and forces Q3/Q6 into a secondary rail, so it is not recommended as the general home.

### Grammar D — Object-first federated desk (Object Explorer/Object Views + Vertex escalation + Chatbot panel)

**Opening condition.** The manager searches for a member, Holding, Parcel, Programme, Proceeding or Intervention in Object Explorer; Object View becomes the biography and workflow hub.

**Interaction.** Search Around and saved explorations form cohorts; Object Views expose current facts, links, evidence and embedded workflows; unusual relationship questions open Vertex. A paired AIP Assist/Chatbot panel explains and acts.

**Decision.** Exact Actions remain available through the Chatbot or object-set Action form. Scenario comparison opens another artifact.

**After/degraded behavior.** Each application retains its own selection/history; bookmarks and cross-app object sets are the continuity mechanism.

**Why coherent.** It is a genuine exploratory ontology grammar, but not a coherent CORDON operating loop. Navigation repeats search → object → workflow → analysis → chat, and direct commands depend too heavily on whichever app happens to be paired.

## 6. Adversarial testing

### Test matrix

| Attack | A Decision Loop | B OSDK fieldbook | C Spatial deck | D Object-first desk |
|---|---|---|---|---|
| **Operator burden: complete Q1→Q4→Action→Q6 without rebuilding context** | **PASS** if selected context is one shared contract and receipts update in place. | **PASS** if coded state machine and Chatbot session stay synchronized. | **AT RISK:** nonspatial steps move into secondary rail. | **FAIL:** repeated app transitions and re-selection. |
| **Duplicated navigation** | **PASS** with Object Views in drawers/modal and standalone apps only as escalation. | **PASS** in one shell. | **FAIL/AT RISK:** two app navigations, pairing, focus and selection models. | **FAIL:** discovery, biography, graph, scenario and chat each own navigation. |
| **AIP/map coupling** | **PASS** if map is presentation state and Action targets are server-resolved/revalidated. | **PASS** if map events emit candidate IDs only. | **AT RISK:** model may over-weight visible geometry or stale paired viewport. | **AT RISK:** current paired app can silently dominate intent. |
| **Ambiguous “dispatch these” after selection changes** | **PASS** only if message binds immutable selection fingerprint; otherwise clarify. | **PASS** with explicit state version. | **HIGH RISK:** cross-app state races. | **HIGH RISK:** several possible selections. |
| **Evidence while entering a consequential command** | **PASS** with nonmodal evidence drawer beside Chatbot. | **PASS** custom layout. | **AT RISK:** evidence may cover/replace spatial context. | **AT RISK:** opens another Object View/app. |
| **Keyboard-only and screen magnification** | **TEST REQUIRED;** native controls help, Map/custom widget cannot be assumed. | **BEST CEILING, TEST REQUIRED;** team owns semantics and focus. | **POORER:** focus crosses iframe/app boundaries; graph/map intrinsically dense. | **POORER:** repeated app transitions and graph gestures. |
| **Color/shape independent meaning** | **PASS by design:** every map encoding repeats text/icon/pattern and details. | **PASS by implementation.** | **AT RISK:** immersive visual encoding encourages color-only semantics. | **AT RISK** in exploratory visualizations. |
| **10,000-object portfolio** | **PASS only** with server-side aggregation, virtualized/summary views and Proposal digest; never render every edit. | **PASS** with pagination/virtualization. | **FAIL as graph;** map may aggregate but cannot explain full decision. | **FAIL/AT RISK** for operational review. |
| **Pairing lost or wrong tab paired** | Not applicable in primary path; standalone escalation cannot mutate. | Not applicable unless optional commands added. | **FAIL CLOSED required:** freeze commands and require explicit re-pair. | **HIGH BURDEN:** pairing is routine dependency. |
| **Data Health red after last-good view** | **PASS** only if visible state becomes indeterminate and Action refuses. | **PASS** with custom stale state. | **AT RISK:** paired app may keep visually plausible cached layer. | **AT RISK:** each app may refresh independently. |
| **Action response stream drops after commit** | **PASS** only with retrievable durable receipt and no model retry. | **PASS** if client implements receipt recovery. | **AT RISK:** presentation Command and Action result can diverge. | **AT RISK:** user may retry from another app. |
| **Hidden mechanism leakage** | **PASS** if occurrence/authority records are projected under semantic parents and logs stay audit-only. | **PASS** if API allowlists and UI contract enforce it. | **AT RISK:** Layers, templates, graph nodes and tool panels expose mechanism. | **FAIL/AT RISK:** object catalogs and graph topology dominate. |
| **Release one Function response-schema change** | **PASS** with compatibility manifest and coordinated Workshop/Chatbot package update. | **PASS but heavier** tagged app release and resource allowlist update. | **HIGH BURDEN:** Workshop + external template/app + commands + Chatbot. | **HIGH BURDEN:** several saved resources and pairings. |
| **Field phone use** | **DEGRADED companion:** list/detail/handoff and exact low-complexity command only; no native Map/Table/Chart in mobile module.[18] | **BEST full-path candidate** if responsive/offline/network behavior is built and tested. | **FAIL** as routine phone grammar. | **FAIL** as routine phone grammar. |

### Platform anti-pattern findings

1. **Widget salad.** Palantir's Workshop guidance warns against overloaded/overcrowded views and recommends no more than five primary top-level actions and roughly ten visible components. The recommended scene therefore changes by decision; it does not show all Q1–Q6 panels simultaneously.
2. **Map as truth.** Shape selection is a candidate target. Applicability still requires subject, proposition, Instrument, date, authority and conflict reasoning. No map color says “compliant,” “eligible” or “ready.”
3. **Graph as process model.** Vertex may visualize accepted links; it must not turn hidden occurrences or backstage types into a second operator ontology.
4. **Object View as application home.** An object biography cannot represent population-wide change, a complete capacity portfolio or explicitly unaffected work without repeated navigation.
5. **Commands as Actions.** Commands change client application state. The four domain writes remain exact Ontology Action tools. Mixing them creates a second, beta write plane.[17]
6. **Approval theater.** A clear manager command is the decision. Do not add a generic command approval popup; clarify actual ambiguity and retain real platform/function refusals.
7. **Chat-only opacity.** Conversation never becomes the sole record. Typed Function results, evidence, proposal diff, receipt and next handoff remain visible independently of prose generation.
8. **Client-side business logic.** No surface recomputes applicability, readiness, feasible portfolios or exposure. It renders exact Function outputs and Action refusals.
9. **Generic inbox/task queue.** The Now view contains material changes and bounded decision scenes derived from accepted owners; it does not mint Task/Case/WorkItem semantics.
10. **Backstage observability as operator history.** Data Health may mark an answer stale; Action logs and traces explain execution; factual occurrences explain what happened.
11. **Hybrid by default.** A custom widget or paired app is admitted only after a named native gap. “More platform capability” is not a reason to add another state owner.
12. **Desktop squeezed onto mobile.** Current Workshop mobile disables Object Table, Chart and Map.[18] The field companion must be separately composed; pretending responsive reflow preserves the desktop grammar is false.

## 7. Recommended complete architecture

### 7.1 Runtime composition

**Primary desktop application — one Workshop module family**

- **Now / focus entry:** material changes, approaching consequential clocks, returned authoritative outcomes and prepared proposals. These are projections from Functions/Automate, not Task objects.
- **Now + five responsibility lines:** the left rail keeps Land, Funding, Applications, Field Work and Payments continuously visible under Now. Each line shows bounded change, owner, clock and next decision/handoff for the selected population. They are simultaneous projections of one graph, not tabs or lifecycle stages.
- **One decision scene:** renders the smallest Q-specific bundle for the selected subject/route/action while preserving the same context across responsibility changes.
- **Persistent context contract:** selected object set, member/land/route, named Action, consequential date, Scenario/Proposal ID, premise fingerprint and health state. Every widget and the Chatbot reads the same contract.
- **Embedded published AIP Chatbot:** reasoning hidden by default; only four read Functions, curated object query, four exact Action tools, clarification and allowlisted application-variable updates. Presentation Commands are optional and nonmutating.
- **Persistent Map operating picture:** native Workshop Map is the central pane. It can show administrative and temporal Official Areas, monitoring/Plant layers, cooperative member Parcels grouped by Holding, and affected/unaffected work. Full cadastral data remains queryable/on-demand rather than simultaneously rendered. Layer visibility, clustering and zoom thresholds preserve legibility without clipping the product universe. Selection updates candidate context; server logic resolves consequence. Transition to standalone Map is read/investigation escalation.
- **Object biography/evidence:** configured panel Object Views in a drawer and full Object Views on explicit drill-through. Show current decision facts, contextual authority, bounded occurrence timeline and permission-aware evidence under the semantic parent.
- **Scenario comparator:** native Scenario widgets first. If they cannot show complete alternative, constraints, sensitivity, protected Commitments, target count/hash, delta summary, fallback and invalidation in one coherent view, add exactly one OSDK custom widget. It receives typed Function/Scenario/Proposal outputs and returns only selected Proposal ID/presentation state.
- **Receipt and next handoff:** a persistent, retrievable strip independent of the Chatbot prose stream.

### 7.2 Interaction contract by six questions

| Question | Default scene | Spatial/graph use | Conversation behavior | Exit condition |
|---|---|---|---|---|
| Q1 changed/affected | Change card → affected and explicitly unaffected work | Map only for changed geography/physical scope; Vertex only for exceptional dependency investigation | Explain impact or focus affected set | affected set, preserved work, owner and clock known |
| Q2 required/allowed/blocked | Side-by-side route/proposition/authority/hold lines | Map shows candidate overlap; no verdict styling | Call exact readiness/applicability basis; cite evidence | scoped conditions and holds understood |
| Q3 chooser/route | Decision-right ladder + alternatives/fallback | Usually collapsed | Clarify decision owner; compare portfolio; prepare Proposal | one owner and route/Proposal identified |
| Q4 named-Action readiness | Exact prerequisite profile, satisfied/blocker/indeterminate | Map supports bounded dispatch scope | Clear command acts; ambiguity clarifies; failure refuses | Action executes/refuses or cure owner receives handoff |
| Q5 done/accepted | Attributed factual occurrence chronology | Map highlights bounded physical scopes/phases | Explain what happened and by whose authority | route-specific result and remaining open work named |
| Q6 landed/open | Independent legal, operational, financial, biological lines | Usually collapsed | Explain non-implications and next owner | bounded result, exposure, clock and owner known |

### 7.3 Action-specific conversational trajectories

1. **Accept Cooperative Execution Mandate** — context shows real member grant, scope, term, exclusions and fallback → manager says accept/refuse exact mandate → Action executes/refuses → receipt explicitly says it did not create member grant, eligibility, concession, capacity or creditor truth.
2. **Decide Cooperative Pursuit** — context separates member choice, accepted mandate, Programme route, eligibility indication, capacity and fallback → manager says pursue/defer/refuse with reason → Action executes/refuses → result preserves fallback/reconsideration.
3. **Commit or Rebalance Capacity** — complete comparison → manager selects alternative → immutable Proposal is created → manager commands `Commit proposal CP-…` (override reason if required) → one atomic Action → receipt lists target count/hash, material deltas, protected Commitments and non-effects on eligibility/concession/duty/fallback/dispatch.
4. **Dispatch Intervention** — exact target/scope/executor and fresh readiness visible → manager commands dispatch → Action revalidates and executes/refuses → receipt says dispatch is not performance, acceptance or establishment.

### 7.4 Evidence, indeterminate state and hidden-mechanism suppression

The default operator projection contains only:

- current proposition or bounded outcome;
- source/authority, consequential date and freshness;
- exact decision/action consequence;
- conflict/indeterminacy only when material;
- current owner, clock and next handoff;
- minimum evidence link;
- Action receipt where relevant.

The following remain behind explicit steward/audit drill-through: raw datasets, extraction, rejected records, hidden occurrence/context object catalogs, join tables, action-log types, edit history, pipeline/Data Lineage, Workflow Lineage, traces, prompts, token use, Eval results and model-training assets. Palantir Object Views support concise panel and full forms, which makes this semantic-parent projection feasible without exposing the backing types.[10][31]

Indeterminate is not an empty field or warning toast. It is a typed state with invalidated answer(s), failed premise, last accepted watermark, stale duration, cure owner, affected Actions and unaffected work. A load-bearing `INDETERMINATE` state disables the same Action only because its platform/function guard refuses—not because the client hides a button.

### 7.5 Mobile and field implication

**Documented constraint:** Workshop mobile is limited access and disables Object Table, Chart and Map in mobile modules.[18]

**Recommendation:** do not claim feature parity. Build a separate mobile Workshop companion only after the desktop grammar validates. Its initial scope is:

- search/browse a small routed object list;
- open a concise Intervention/Parcel/Proceeding detail;
- read current owner, clock, readiness blockers and evidence references;
- capture current-location context or scan a code where permitted;
- issue the direct Dispatch command only when exact target/scope is already bound and the embedded Chatbot is proven supported in the target mobile mode;
- retrieve the durable receipt and next handoff.

No capacity portfolio commit, immersive map analysis, large population comparison or complex evidence review is promised on phone. If full mobile management becomes a real requirement, that is the strongest trigger to move the selected grammar to OSDK React.

### 7.6 Accessibility contract

No reviewed official page establishes that the complete composed application is WCAG-conformant. Therefore accessibility is **test-required**, not presumed.

Release gates:

- complete all four Action trajectories and one ambiguity/refusal trajectory using keyboard only;
- deterministic focus after scene change, drawer open/close, Chatbot clarification and receipt arrival;
- screen-reader names for decision state, source/as-of, blocker, owner, consequence and receipt;
- no color-only map, health, alternative or outcome encoding;
- text alternative/table for every map/graph finding needed to act;
- 200% zoom and reflow without clipped command/receipt content;
- reduced-motion behavior;
- touch targets and mobile drawers where mobile is admitted;
- automated checks plus manual screen-reader and switch/keyboard testing.

Failure of the Map or custom widget gates does not justify an inaccessible exception; provide the equivalent list/detail path or flip to OSDK React.

### 7.7 Release architecture

**Documented fact:** OSDK React uses repository checks and a tagged release; PR previews are beta.[9]

Pilot also emits CI/release configuration for generated OSDK/custom-widget outputs.[15]

Global Branching and release management remain the Gate 6 authority for the broader solution.[28][29]

One compatibility manifest pins:

- Workshop module/configured Object View versions;
- optional custom widget version and Widget Registry release;
- Map/Vertex template versions if admitted;
- Chatbot published version, tool schemas and application-variable contract;
- four Function response schemas and Action versions;
- Scenario/Proposal schema;
- tuned model version;
- Evals suite and interaction regression version;
- mobile companion version if admitted.

Promotion requires the same prompt→context→clarification/tool→target→parameters→edits/refusal→receipt trajectories against the branch/preview. A surface release cannot silently add a generic Action, broaden object query context or expose hidden types. Rollback restores a compatible tuple, not merely the Workshop page.

## 8. Consequences of selecting this architecture

### Benefits

- Fastest route to a genuinely operational, platform-native app rather than a custom shell project.
- Native embedding of the required Chatbot and application-state variables.[4]
- Native Map, Object View, Action, Function, Scenario and object-set ecosystem with one primary navigation.
- Direct execution remains under exact Action permissions/criteria/function validation, not client trust.
- Low default exposure of backstage data and builder tools.
- Standalone Map/Object Explorer/Vertex remain available without burdening every routine trajectory.
- One bounded custom widget preserves an escape hatch for the hardest interaction without making the entire app custom.

### Costs and risks

- Workshop variable/event complexity can become a hidden second domain model.
- The desktop Map widget does not solve mobile field use; Workshop mobile explicitly removes Map/Table/Chart.[6][18]
- The optional custom comparator creates a separate code/release/accessibility surface.
- Cross-app escalation can still confuse selection if allowed to mutate; keep it read-only in release 1.
- Workshop visual/accessibility ceiling must be measured, not assumed.
- Object Views configured in Workshop and the primary Workshop module can duplicate content unless one owns biography and the other owns the decision scene.
- Chatbot resource allowlists/tool schemas and application variables must stay compatible with the surface release.

### Kill criteria / flip conditions

Flip to Grammar B (OSDK React) before production if any of these is true after a thin but real Workshop prototype:

1. more than one custom widget is needed to complete the four Action and six-question trajectories;
2. selected context is duplicated across incompatible Workshop variable graphs;
3. one operator must navigate to another app in more than one of the four Action trajectories;
4. capacity comparison cannot show complete proposal consequences and invalidation in one scene;
5. keyboard/screen-reader gates cannot be met;
6. full manager capability on phone/tablet becomes required;
7. indeterminate/receipt-recovery state cannot remain persistent and unambiguous;
8. paired Map/Graph/Vertex becomes a runtime dependency rather than an optional investigation escalation.

## 9. Step-5 verdict

**Gate 7 accepts the Workshop-native Decision Loop as one persistent three-pane operating picture: Now plus five responsibility lines, synchronized native Map, and embedded AIP decision/execution panel, with configured Object Views and at most one bounded capacity-scenario OSDK custom widget.** Standalone Map, Object Explorer and Vertex are investigation escalations. Cross-app pairing is deferred unless a measured native capability gap justifies its duplicated state/navigation. Slate and Code Workspace apps remain current platform options but are not selected. Pilot and AI FDE may build on a governed branch but are not runtime architecture.

This recommendation is complete only with its consequences: desktop-first; explicit degraded/indeterminate behavior; no hidden-mechanism navigation; no generic writes; no approval theater; a separate bounded mobile companion; one compatibility manifest; and a pre-declared flip to OSDK React if Workshop requires accumulating custom code or cannot meet accessibility/state-coherence gates.

## Sources

[1] https://www.palantir.com/docs/foundry/app-building/operational-apps
[2] https://www.palantir.com/docs/foundry/app-building/overview
[3] https://www.palantir.com/docs/foundry/ontology/applications
[4] https://www.palantir.com/docs/foundry/workshop/widgets-aip-chatbot
[5] https://www.palantir.com/docs/foundry/map/overview
[6] https://www.palantir.com/docs/foundry/workshop/widgets-map
[7] https://www.palantir.com/docs/foundry/ontology-sdk-react-applications/osdk-react
[8] https://www.palantir.com/docs/foundry/ontology-sdk-react-applications/osdk-react-components
[9] https://www.palantir.com/docs/foundry/ontology-sdk-react-applications/development
[10] https://www.palantir.com/docs/foundry/object-views/overview
[11] https://www.palantir.com/docs/foundry/object-explorer/overview
[12] https://www.palantir.com/docs/foundry/slate/overview
[13] https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab
[14] https://www.palantir.com/docs/foundry/custom-widgets/overview
[15] https://www.palantir.com/docs/foundry/pilot/overview
[16] https://www.palantir.com/docs/foundry/cross-app-interactivity/overview
[17] https://www.palantir.com/docs/foundry/chatbot-studio/commands-as-tools
[18] https://www.palantir.com/docs/foundry/workshop/mobile-overview
[19] https://www.palantir.com/docs/foundry/chatbot-studio/overview
[20] https://www.palantir.com/docs/foundry/chatbot-studio/foundry-apis
[21] https://www.palantir.com/docs/foundry/vertex/embed-graph-workshop
[22] https://www.palantir.com/docs/foundry/ai-fde/overview
[23] https://www.palantir.com/docs/foundry/chatbot-studio/tools
[24] https://www.palantir.com/docs/foundry/chatbot-studio/application-state
[25] https://www.palantir.com/docs/foundry/action-types/overview
[26] https://www.palantir.com/docs/foundry/functions/overview
[27] https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario
[28] https://www.palantir.com/docs/foundry/global-branching/overview
[29] https://www.palantir.com/docs/foundry/devops-release-management/overview
[30] https://www.palantir.com/docs/foundry/observability/data-health
[31] https://www.palantir.com/docs/foundry/object-views/use-full-views-in-platform
[32] https://www.palantir.com/docs/foundry/object-explorer/apply-actions
[33] https://www.palantir.com/docs/foundry/map/integrate-actions
[34] https://www.palantir.com/docs/foundry/carbon/overview
[35] https://www.palantir.com/docs/foundry/vertex/overview
[36] https://www.palantir.com/docs/foundry/insight/overview
[37] https://www.palantir.com/docs/foundry/quiver/overview
[38] https://www.palantir.com/docs/foundry/contour/overview

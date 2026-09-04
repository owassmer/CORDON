# foundry-platform-atlas (DRAFT)

Platform-knowledge authority for a Foundry-builder agent profile. The reader is an external
frontier-model agent that operates a live Palantir Foundry/AIP enrollment through three lanes:
Palantir MCP tools, the Foundry REST API v2, and a driven browser. This atlas states what tooling
exists on the platform, what each piece is for, and which lane reaches it.

Terminology guard: **AI FDE** is Palantir's in-platform closed-loop agent that operates Foundry
itself (https://palantir.com/docs/foundry/ai-fde/overview/). **AIP Assist** is an LLM support/Q&A
sidebar available from any platform application (https://www.palantir.com/docs/foundry/assist/overview/).
They are different products. Never conflate them.

---

## 1. AI FDE — the reference system

AI FDE ("AI-powered forward deployed engineer") is an interactive agent inside Foundry. It
translates natural-language requests into Foundry operations: data transformations, code
repository management, ontology building, and more. It is the platform's own model of how an
agent should operate Foundry; this profile replicates its discipline from the outside.
Source: https://palantir.com/docs/foundry/ai-fde/overview/

**Requirements.** AIP must be enabled on the enrollment. Global Branching is recommended for
ontology edits from AI FDE. (Same source.)

**Closed-loop operation.** AI FDE executes an action, observes the result, and uses the feedback
to choose the next action. Outputs of one operation become inputs to the next. It validates its
own changes: runs transform previews to validate transform code, function previews to validate
function behavior, and reviews CI checks in Code Repositories. Adopt this loop: never emit
unvalidated artifacts; preview, observe, fix, re-run.
Source: https://palantir.com/docs/foundry/ai-fde/overview/#closed-loop-operation

**Modes.** Modes declare the broad task. Each mode loads the right documentation, exposes the
relevant tools, and tailors approach. The agent can select or switch modes itself mid-task.
Source: https://www.palantir.com/docs/foundry/ai-fde/modes-and-capabilities/

| Mode | Foundry surfaces it drives |
| --- | --- |
| Data integration | Pipeline Builder or Python transforms in Code Repositories; dataset builds |
| Data connection | Data Connection sources, egress policies, sync debugging |
| Ontology editing | Ontology Manager: object types, link types, action types |
| Functions editing | AIP Logic, TypeScript/Python functions; tested with AIP Evals |
| Exploration | Read-only investigation of what exists before changing anything |
| Governance | Permissions, access control, markings, data-protection audits |
| OSDK React | React applications / custom widgets on Foundry data (Developer Console, OSDK) |
| Platform Q&A | General questions about how Foundry works (documentation lookup) |

Docs also list a ninth mode, **Machine learning** (Model Studio no-code or pro-code model
development). Some modes take configuration: Data integration (transforms vs. Pipeline Builder),
Function editing (language), Machine learning (environment).

**Two-tier architecture: Modes and Capabilities.** Modes are the broad task; *capabilities*
(the skill tier) are granular abilities usable across modes, each mapping to one or more tools.
Two categories:
- *Agent capabilities* — self-management: change mode mid-task, request clarification, generate
  a plan for review before acting, load documentation on demand, manage its own context and
  active capabilities.
- *Domain capabilities* — real Foundry actions: filesystem operations (folders, browse, move),
  Notepad read/create/update, solution-design diagrams, executing ontology actions.
Capabilities can be enabled/disabled, including by the agent itself mid-task.
Source: https://www.palantir.com/docs/foundry/ai-fde/modes-and-capabilities/#capabilities

**Controlled-context model.** Initial state loads minimal context: general Foundry knowledge,
no user data. This prevents context pollution and keeps governance over the model's knowledge
boundaries. Context is added explicitly:
- Mode selection (auto or manual) determines baseline context and tools.
- Manual additions from the ribbon: datasets, functions, branches, interfaces, action types,
  object types, documentation bundles, uploaded media.
- Drag-and-drop of links/folders/datasets/docs from other Foundry applications.
- Search tools the agent can enable to find resources itself.
A chat outline tracks prompts, responses, tools, and per-message token counts; messages can be
summarized or removed to stay inside the context window.
Sources: https://palantir.com/docs/foundry/ai-fde/overview/#context-management ,
https://palantir.com/docs/foundry/ai-fde/navigation/#manage-context

**Tool-approval model.** Defaults are maximally conservative; nothing that could impact
production is auto-approved.
- *Requires approval every time:* executing ontology actions, creating applications or widgets,
  publishing, creating tags.
- *Approval required by default when:* the tool changes the default branch; the change is
  unbranched (e.g., creating a code repository); the tool has side effects (e.g., dataset builds).
- *Branch-aware auto-approval:* file edits and dataset builds auto-approve on feature branches
  but require approval on protected branches. Tools can be set to auto-execute on allowlisted
  branches and projects.
- *Auto-approved:* read-only operations — searching, reading definitions.
- *Session-scoped approvals:* specific tools can be approved for the session, scoped to a branch
  or project.
Sources: https://palantir.com/docs/foundry/ai-fde/security-and-governance/#user-approval-for-sensitive-actions ,
https://palantir.com/docs/foundry/ai-fde/navigation/#tool-configuration

**Identity model.** AI FDE runs entirely as the user: no service account, no separate credential,
no privilege escalation. Every operation is checked against the user's permissions server-side;
permission errors are identical to manual ones. All activity lands in standard Foundry audit logs
attributed to the user; LLM usage is attributed and rate-limited per user. Sessions are private
to their creator and secured by the user's markings.
Source: https://palantir.com/docs/foundry/ai-fde/security-and-governance/

**Branching by default.** AI FDE uses branching across all workflows. Changes are proposed as a
Global Branch proposal or a Code Repository pull request for review — never applied directly to
main. Global Branching provides one branch spanning multiple applications (pipeline logic,
dataset schema, object types), end-to-end testing without disrupting production, a review/approval
process, and single-click merge to `main`.
Sources: https://palantir.com/docs/foundry/ai-fde/overview/#capabilities ,
https://www.palantir.com/docs/foundry/global-branching/overview/

**Model selection.** Per-session model choice. First-class support for Anthropic, OpenAI, Google,
and xAI models with native tool APIs; the model must be enabled for the enrollment.
Source: https://palantir.com/docs/foundry/ai-fde/overview/#model-support

**Best-practice discipline (adopt as operating rules).** Verify generated resources before
production; test transforms on representative sample data. Limit tools and context to the task.
Decompose complex work; verify each component before adding complexity. Track function
performance with AIP Evals. Agents fire operations seconds apart and in parallel — watch
storage/compute/rate-limit pressure. Source: https://palantir.com/docs/foundry/ai-fde/best-practices/

---

## 2. Platform app catalog

Lane key — **MCP**: Palantir MCP tools reach it. **API**: Foundry REST API v2 reaches it.
**Browser**: browser-driven UI only. Catalog references:
https://www.palantir.com/docs/foundry/getting-started/application-reference/ and
https://www.palantir.com/docs/foundry/aip/aip-features/#aip-application-reference

- **Pipeline Builder** — Point-and-click end-to-end pipelines (batch/streaming) with built-in
  transforms and LLM nodes. Eligibility build: the primary lane for ingest→clean→join pipelines
  producing ontology backing datasets. Lanes: MCP (transform/pipeline tooling, dataset context),
  API (dataset reads/builds via Datasets/Orchestration endpoints); pipeline graph assembly is
  browser.
- **Ontology Manager** — Defines object types, link types, action types, functions binding.
  Eligibility build: model Parcel/Grower/Application/EligibilityDecision object types and the
  actions that mutate them. Lanes: MCP (search and safely modify ontology TYPES via proposals);
  API (read type metadata); full editing UI is browser.
- **Object Explorer** — Search, explore, analyze ontology objects. Eligibility build: verify
  loaded objects and link traversals after pipeline runs. Lanes: API (ontology object listings,
  search, aggregation); UI is browser.
- **Workshop** — No/low-code operational app builder on the ontology (widgets, pages, actions).
  Eligibility build: the reviewer-facing app for decisions and overrides. Lanes: browser only for
  assembly; the apps consume ontology via actions the API can also drive.
- **AIP Logic** — No-code environment for LLM-backed functions over ontology data.
  Eligibility build: LLM adjudication/explanation steps (e.g., document-to-structured extraction).
  Lanes: authoring is browser; published Logic functions execute via API (query functions) and
  are MCP-discoverable as functions context.
- **AIP Evals** — Test suites and evaluation criteria for LLM functions; compare models, measure
  variance. Eligibility build: regression-test the adjudication function before promoting.
  Lanes: browser (suite authoring/runs).
- **AIP Chatbot Studio** — Builds interactive ontology-aware chatbots with tools that can edit
  ontology data. Eligibility build: optional applicant/reviewer Q&A bot; not core. Lanes: browser.
- **AIP Threads** — Zero-setup LLM chat over dropped documents and existing resources/chatbots.
  Eligibility build: ad-hoc document triage only. Lanes: browser.
- **Automate** — Automations that monitor conditions and execute effects; integrates with AIP
  Logic to stage or apply ontology edits for human review. Eligibility build: auto-flag parcels
  whose eligibility state changes; schedule re-evaluation. Lanes: browser (configuration).
- **Code Repositories** — Web-based versioned authoring for Python transforms and TypeScript/
  Python functions, with CI checks and PRs. Eligibility build: any logic too complex for Pipeline
  Builder; deterministic rule engines. Lanes: MCP (repo-aware context, `preview_transform`
  iterate-fix loop); browser for repo creation approval and PR merge.
- **Code Workspaces** — Hosted Jupyter/RStudio for data science; Palantir-provided LLMs
  available in notebooks. Eligibility build: exploratory analysis, model prototyping. Lanes:
  browser.
- **Contour** — Point-and-click tabular analysis on large datasets (per application reference).
  Eligibility build: quick dataset QA and profiling without code. Lanes: browser.
- **Quiver** — Object- and time-series-centric analysis and dashboarding (per application
  reference). Eligibility build: analyze decision distributions over ontology objects. Lanes:
  browser.
- **Data Connection** — Connects external sources; syncs data in; manages egress. Eligibility
  build: ingest registry extracts, uploads, external APIs. Lanes: MCP (Data Connection mode
  context/tools per AI FDE parity), API (connectivity endpoints); agent/source setup is browser.
- **Data Lineage** — Graph of how resources flow through the platform. Eligibility build: audit
  provenance from source sync to decision object. Lanes: browser.
- **Developer Console** — Creates and manages OSDK applications; scopes ontology resources;
  hosts Ontology MCP (OMCP) enablement. Eligibility build: register the OSDK app and OAuth
  clients the external agent uses. Lanes: MCP can update a Developer Console application
  ("Apply this proposal to my Developer Console application"); app configuration is browser.
- **Control Panel** — Enrollment administration: AIP settings, application access, organization
  and user management, "Your Plan" limits page. Eligibility build: enable AIP features, models,
  Global Branching; check tier limits. Lanes: browser only (some admin reads exist in API v2
  Admin, but settings changes are browser).
- **Notepad** — Rich documents with live platform content; AIP editing features. Eligibility
  build: runbooks and decision-log narratives. Lanes: AI FDE exposes Notepad read/create/update
  as a domain capability in-platform; externally treat as browser.
- **Scheduler** — Builds and manages dataset build schedules; AIP generates cron configs.
  Eligibility build: nightly re-sync and re-evaluation builds. Lanes: API (Orchestration
  schedules/builds); schedule authoring UI is browser.

---

## 3. The external lanes

**Lane 1 — Palantir MCP** (https://www.palantir.com/docs/foundry/palantir-mcp/overview/).
An MCP server connecting external AI IDEs/agents to the platform. Provides: context on internal
Palantir libraries and Foundry architecture; repository-aware code context (OSDK repos, Python
transforms, TypeScript functions); documentation and code-snippet search; tools to explore the
ontology and Foundry projects; safe ontology TYPE modification via proposals; Developer Console
application updates; `preview_transform` for iterative transform build-fix loops. Hard boundary:
Palantir MCP is for ontology *builders* — it can modify ontology types but **cannot write
ontology data**. Data writes for consumers go through Ontology MCP (OMCP), a separate Developer
Console feature exposing object/action/query types as MCP tools
(https://www.palantir.com/docs/foundry/developer-console/ontology-mcp/).

**Lane 2 — Foundry REST API v2** (https://www.palantir.com/docs/foundry/api/v2/). OAuth
2.0-authenticated HTTP endpoints for building on the platform. Reaches: ontology data reads
(list/get/search/aggregate objects, traverse links), action application (applyAction), query
function execution, dataset and file operations, orchestration (builds, schedules), and admin
resources. This is the lane for programmatic ontology DATA interaction that MCP does not offer.

**Lane 3 — Browser only.** Remains manual/browser-driven: Global Branch proposal review and
merge; Control Panel settings (AIP enablement, application access, plan limits); Workshop app
assembly; Developer Console app configuration (OAuth scopes, OMCP enablement); Code Repository
source import approval and repo-creation confirmations; AIP Evals/Chatbot Studio/Automate
authoring surfaces. Treat every browser-only step as a human-or-browser-agent checkpoint and
plan around it.

Lane-selection rule: read types/docs/code context → MCP. Read or mutate ontology data, run
actions, trigger builds → API v2. Approve, merge, configure, assemble UIs → browser.

---

## 4. AIP Developer (free) tier constraints

Official docs do not publish a single quota table; authoritative numbers live in Control Panel →
**"Your Plan"** on the live enrollment (community-confirmed:
https://community.palantir.com/t/queries-regarding-free-tier-developer-account/5073). Known
constraints, with attribution:

- **Action types: 60 max.** Community-reported; API error at the 61st action type
  (https://community.palantir.com/t/foundry-limits-me-to-max-60-action-types/6699). Not an
  official published quota.
- **Object/link-type ceilings.** Community-reported: `TooManyOneToManyLinkTypesInOntology`
  errors on dev tier (~48 explicit one-to-many links tripped it); overall object-type and
  link-type limits exist; the pre-installed "AIP Now" Marketplace package counts against quota
  and can be deleted (https://community.palantir.com/t/too-many-link-types-in-ontology/6948).
- **Users: 5 max.** Community-reported
  (https://community.palantir.com/t/why-can-i-only-add-up-to-5-users-in-palantir-foundry/3911).
- **Single Organization** (multiple Spaces allowed); no custom homepages. Community-reported
  (https://community.palantir.com/t/looking-for-guidance-on-pushing-dev-tier-multi-tenant-clean-architecture/5380).
- **LLM rate limits.** Per-user, per-model limits; thresholds for AI FDE-compatible models were
  raised on Developer Tier; live numbers under Resource Management → "AIP Usage and Limits".
  Community-reported (https://community.palantir.com/t/dev-tier-llm-rate-limiting/6213).
- **Notional data: 1,000-row cap** when generating notional data in Pipeline Builder
  (docs-referenced via community: https://community.palantir.com/t/generating-notional-data/651 ,
  citing https://www.palantir.com/docs/foundry/pipeline-builder/datasets-generated/). Workaround:
  Faker-based transforms in Code Repositories.
- **Feature enablement.** GA applications are included; Beta applications require a support
  request. AIP features and specific models require enablement in Control Panel AIP settings;
  Global Branching requires enrollment enablement
  (https://www.palantir.com/docs/foundry/aip/enable-aip-features/ ,
  https://palantir.com/docs/foundry/ai-fde/overview/#requirements). No billing on dev tier —
  limits are hard stops, not charges (community:
  https://community.palantir.com/t/developer-tier-billing-and-usage/1074).

---

## 5. Facts pending enrollment verification (check at boot)

Verify each on the live enrollment before relying on it:

1. Exact quota table — action types, object types, link types, users, storage, compute — from
   Control Panel → "Your Plan". All numeric caps above are community-reported snapshots.
2. Per-model LLM rate limits from Resource Management → "AIP Usage and Limits", and which model
   families (Anthropic/OpenAI/Google/xAI) are actually enabled.
3. Whether AIP is enabled and which AIP features are toggled on in Control Panel AIP settings.
4. Whether Global Branching is enabled (required for branch-first ontology workflow).
5. Whether AI FDE itself is available on the enrollment (AIP feature availability "may differ
   between customers" — https://palantir.com/docs/foundry/ai-fde/overview/).
6. Palantir MCP availability, install path, and the exact tool list the connector exposes
   (tool names/scopes are not exhaustively published).
7. Ontology MCP (OMCP) availability in Developer Console for data-write flows.
8. Foundry API v2 endpoint availability and OAuth client creation rights on dev tier
   (third-party app / client registration limits are tier-dependent).
9. Which applications show as GA vs. Beta under Control Panel → Application Access.
10. Whether the pre-installed Marketplace example package is consuming ontology quota.
11. Current mode list in AI FDE (docs list nine including Machine learning; count and configs
    may change between releases).
12. Contour/Quiver presence and any dev-tier feature reductions in analytics apps.

<!-- End of draft. 5 sections. All claims cited, community-attributed, or listed pending verification. -->

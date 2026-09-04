# Foundry/AIP capability inventory — CORDON Wedge 1

Read-only survey. No platform state was created, updated, deleted, or published.

Enrollment: `owenwassmer.usw-22.palantirfoundry.com`. AIP Developer tier, single user, single Org.
Ontology: `ri.ontology.main.ontology.cfb1478a-5b0e-466a-aaff-b212870e8861` (non-default).
Project: `CORDON-Wedge-1` — `ri.compass.main.folder.f9898a87-ea4e-404a-9414-039adda6fee1`.
All platform reads: 2026-08-17. Read IDs (`P1`–`P13`) resolve in the Evidence ledger at the end.

Every availability claim cites either a documentation page or a platform read. Claims that are
neither are labelled `INFERRED`.

**Method note on tier.** Palantir documentation does not publish per-tier feature matrices for the
capabilities in scope. Two searches for enrollment-level quotas returned only Object Set Service
size limits and Ontology volume guidance, no type-count quota
(`search_foundry_documentation`, queries "Ontology scale limits number of link types object types
per ontology" and "maximum number of object types link types per ontology enrollment limit"). This
inventory therefore establishes tier availability by **observation on this enrollment**: a capability
is called available when a live resource of that kind exists here, or when a platform endpoint for it
responds. Doc-only capabilities are marked as tier-unconfirmed.

---

## Section 1 — Capability map, per build component

### (a) Relationships between object types

**Capability.** Link types. A link type is the schema definition of a relationship between two
object types, backed by a foreign key, a many-to-many join table, or an intermediate object type
(`get_documentation_summaries` bundle `ontology-link-types`;
`palantir.com/docs/foundry/object-link-types/link-types-overview`).

**Tool.** `create_or_update_foundry_link_type` (write, Ferro's lane). Read side:
`view_foundry_link_type`, `view_foundry_object_type`,
`GET /api/v2/ontologies/{ontology}/objectTypes/{type}/outgoingLinkTypes`.

**Available here.** Yes. This ontology carries 88 outgoing link sides across its 43 live object
types, which is 44 link types (P2). Live examples span three different projects:
`LoanFile → assessments (MANY, RequirementAssessment)`,
`RegulatoryRequirement → authorizingInstrument (ONE, PolicyInstrument)`,
`ExampleFlight → aircraft (ONE, ExampleAircraft)`. Link types also appear as Compass resources of
type `ri.ontology.main.relation` (P9, e.g. `Establishing instrument - Regime established`).

**Current state.** All six CORDON object types return zero outgoing link types (P2). Relationships
are String columns only.

**What adopting it changes.** Traversal becomes a platform operation instead of a client-side join:
`parcel.zone.get()`, Workshop link panels, Object Explorer search-arounds, and map search-arounds
all work with no extra code. See Section 2.

---

### (b) The eligibility computation

**Capability.** Three on-platform homes exist for deterministic logic:

1. **Foundry Functions** (TypeScript v1/v2, Python). Publishable, callable from Actions, Workshop,
   Automate, and OSDK (`get_documentation_summaries` bundles `functions-core`,
   `functions-ontology-edits-tsv2`, `functions-python`).
2. **Function-backed Action types.** A `function` logic rule replaces the rule set. Required when
   logic must compare properties of two different passed objects, modify linked objects together, or
   create several object types and link them (bundle `ontology-action-types`, decision matrix
   "webhook vs. function-backed actions").
3. **AIP Logic.** No-code LLM-and-Ontology functions built from blocks, including a deterministic
   `Apply action` block (`palantir.com/docs/foundry/logic/overview`,
   `palantir.com/docs/foundry/logic/blocks`).

**Tools.** `publish_function`, `create_or_update_foundry_action_type`, `search_foundry_functions`,
`get_typescript_v2_functions_documentation`, `get_python_transforms_documentation`.

**Available here.** Yes, all three, by observation.
- 15 Foundry Functions are live on this ontology, including `assessRequirement`, `openReview`,
  `collectEvidenceForRun`, and `aipReachability` (P5).
- One code repository exists on the enrollment (P9,
  `ri.stemma.main.repository.a607bd85-…`).
- AIP Logic resources exist, including one **already inside the CORDON project**:
  `ri.eddie.main.logic.09648de2-1345-4034-b3c7-04a4dd402bc2` named `parseFellingOrder` (P8). Two
  more sit in Oversight Capacity (P9).

**Current state.** Eligibility runs in local Python (`scripts/assess_eligibility.py`,
`scripts/zone_as_of.py`). No CORDON Foundry Function appears in the ontology's 15 published query
types (P5).

**What adopting it changes.** The rule that decides eligibility becomes an audited, permissioned,
versioned platform artifact that the Action calls, rather than a script whose output is uploaded.
One constraint to plan around: an AIP Logic function's Ontology edits are only written back when the
function is executed **from an Action** — an `Apply action` block inside a directly-executed Logic
function does not edit the Ontology (`palantir.com/docs/foundry/logic/blocks`, callout under
"Apply action").

---

### (c) Data ingestion from SIT / BURP public sources

**Capability.** Two platform paths, both replacing direct CSV upload:

1. **REST API data source + network egress policy + external Python transform.** The source carries
   an egress policy; the transform reads through it and writes a Foundry dataset with build history
   and lineage (`get_documentation_summaries` bundle `data-integration-external-transforms`).
2. **Pipeline Builder.** Point-and-click transform authoring producing the same lineage.

**Tools.** `get_or_create_network_egress_policy`, `create_foundry_rest_api_data_source`,
`create_python_transforms_code_repository`, `clone_code_repository_locally`,
`get_python_transforms_documentation`. Pipeline Builder is browser-only.

**Available here.** Yes.
- Five REST API data sources are live (P9): `public-evidence-egress`,
  `courtlistener-evidence-egress`, `ecfr`, `sec-edgar-data`, `sec-edgar-archives`
  (`ri.magritte..source.*`).
- Four Pipeline Builder pipelines are live (P9, `ri.eddie.main.pipeline.*`), including
  `[Example] GeoJSON Extraction Pipeline`.
- One transforms code repository is live (P9).

**Current state.** Six datasets uploaded as CSV via `create_and_write_to_foundry_dataset`. No build,
no lineage.

**What adopting it changes.** The chain from the SIT ArcGIS endpoint to the object gains a build
graph, a schedule, and Data Expectations that run on every build instead of on a laptop. It also
makes the extraction re-runnable by someone who is not holding the local scripts.

---

### (d) Derived / computed properties on objects

**Capability.** **Derived properties** — properties calculated at runtime from other properties or
from linked objects, usable for filtering, sorting, and aggregation in the same request. They apply
the security of every object involved (`palantir.com/docs/foundry/ontology/derived-properties`).

**Available here.** **Unconfirmed, and narrower than the name suggests.** The documentation states
derived properties are **Beta** and "may not be available on your enrollment", and lists exactly one
availability surface: the TypeScript OSDK `withProperties` operation on `@osdk/client` `2.2.0-beta.x`
or later (same page, "Availability"). No Workshop, Ontology Manager, or REST availability is
documented. Known limitations include: no OSv1 object types in the query, and derived properties
cannot be used in text search or keyword filters (same page, "Known limitations").

**Current state.** None. `wkt`, `lat`, `lon`, `retrievedAt`, `validFrom`, and `validTo` are all
String columns on the backing datasets (P7).

**What adopting it changes.** Little, at this tier and today. Derived properties earn their value by
aggregating across links, and this build has no links. Treat as a follow-on to (a), not as an
alternative to it. A transform-computed column remains the available and portable mechanism.

---

### (e) Enforcement of non-negotiable rules at write time

**Capability.** Four distinct enforcement points, at different moments:

| Point | Fires when | Reachable via |
|---|---|---|
| **Action submission criteria** | Every Action submission, human or API | Ontology Manager or platform API |
| **Data Expectations** | Every transform build | `transforms.api.Check` in a repository |
| **Data health checks** | On transaction / schedule / build event | `manage_health_check` |
| **Action permissions + writeback mode** | Before criteria evaluate | Ontology Manager |

Submission criteria support `is`, `is not`, `matches` (regex), numeric and date comparisons, and the
multi-value operators `includes`, `includes any`, `is included in`, `each is`, `each is not`,
combined with AND/OR/NOT and per-condition failure messages
(`get_documentation_summaries` bundle `ontology-action-types`, "Submission criteria"). Criteria can
compare a parameter against a static value, against another parameter, or against the current user's
group memberships and Multipass attributes (same bundle, "Condition templates"). Attachment and
object-set parameters cannot be used in criteria (same bundle).

The layered enforcement order is: view permission → object/dataset permission → **all submission
criteria** → Restricted View edit policy (same bundle, "Layered enforcement order").

**Available here.** Yes for health checks — `get_available_check_types` returns **37 check types**,
36 of them with `isCheckCreationAllowed: true` (P10). The build uses four: `totalRowCount`,
`primaryKeyCheck`, `nullPercentageCheck`, `columnRegexCheck`. Unused and directly relevant:

- `joinCheck` — "Approximate relationship between two columns from two datasets". This is the
  referential-integrity check for the String foreign keys (P10).
- `columnValueEnumCheck` — allowed values in a column. Enforces the `regime`, `source_class`,
  `derivation_class`, `verification_class` vocabularies (P10).
- `schemaComparison` and `columnType` — detect schema drift and column type change (P10).
- `dateColumnRange` — range of values in a date column (P10).
- `uniquePercentageCheck` — approximate distinct percentage; catches a key column collapsing
  toward one value (P10).
- `buildStatus`, `jobStatus`, `timeSinceLastUpdated`, `dataFreshnessCheck` — become meaningful only
  once (c) gives the datasets builds (P10).

Submission criteria: the mechanism is documented and the platform API reaches it, but the MCP
connector does not expose it and the three CORDON Action types are not on main, so their criteria
state could not be read (P3, P4). Tier availability is **INFERRED** from the mechanism being present
in the ontology-action-types documentation and from 29 Action types existing on this ontology.

**Current state.** Enforcement is dataset-shaped only, and four checks wide.

**What adopting it changes.** `joinCheck` and `columnValueEnumCheck` alone convert two classes of
prose rule into checks that run without anyone remembering. Submission criteria move the
"no verdict without a citation" rule from the function body into a gate the function cannot bypass.

---

### (f) Operator-facing surface

**Capability.**
- **Workshop** — no-code application building directly on the Ontology, with layouts, an events
  system, object lists, filter lists, maps, charts, and an **Edit History** widget
  (`palantir.com/docs/foundry/ontology/applications`, "Workshop";
  `palantir.com/docs/foundry/workshop/widgets-edits-history`).
- **Object Explorer** — search, search-arounds, exploration views, bulk Actions, zero configuration
  (`palantir.com/docs/foundry/ontology/applications`, "Object Explorer").
- **Vertex** — graph exploration with point-and-click multi-step search-arounds
  (`palantir.com/docs/foundry/vertex/explore-object-relationships`).
- **Map** — geospatial rendering with link search-arounds
  (`palantir.com/docs/foundry/map/add-to-map`, `palantir.com/docs/foundry/map/integrate-searcharounds`).
- **OSDK React application** — a custom web UI over the Ontology
  (`get_documentation_summaries` bundle `osdk-react-applications`).

**Available here.** Workshop: yes — five Workshop modules are live (P9,
`ri.workshop.main.module.*`), including `Console Experimental` in Oversight Capacity and four in
AIP Now Ontology. Object Explorer and Map require no resource to exist and are documented platform
applications; availability is **INFERRED** from Workshop and the Ontology being present. Vertex:
**unconfirmed**, no `vertex` resource observed (P9).

**Current state.** No operator surface. W6 is planned.

**What adopting it changes.** It is the difference between an ontology and a product. Note the
ordering dependency: the Workshop widgets that make an eligibility engine legible — link panels,
search-arounds, the Edit History widget — all require (a) or (g) first.

---

### (g) Versioning and history of a legal state over time

This decomposes into three different questions, and the platform answers them with three different
mechanisms.

**1. History of the *decision*, i.e. who changed which object property when.**
**Track user edit history**, a per-object-type toggle in Ontology Manager's Datasources tab. It
requires Object Storage v2 and the Edits toggle. Changelog records are immutable and cannot be
deleted or modified by end users, even if the underlying edits are reverted
(`palantir.com/docs/foundry/object-edits/user-edit-history`;
`palantir.com/docs/foundry/workshop/widgets-edits-history`, "Audit trail and data permanence").
Two constraints worth carrying: only changes made **via Actions** are shown, not pipeline or
backing-dataset changes; and tracking is **not supported for object types with marking properties**
(`palantir.com/docs/foundry/object-views/widgets-properties-links`, "Common issues and notes").
Disabling the toggle permanently deletes existing history (`…/user-edit-history`, "Disable edit
history"). Tier availability: **INFERRED**; the toggle is browser-only and was not read.

**2. History of the *ontology definition*, i.e. who changed the type.**
Ontology Manager's **History** tab per resource, and a global **Ontology history** page with restore
(`palantir.com/docs/foundry/ontology-manager/restore-changes`). This exists independently of the
build and needs no configuration.

**3. History of the *legal state itself*, i.e. which decree governed this parcel on a given date.**
No native bitemporal or as-of object query surfaced in the documentation searched. The mechanism the
platform offers is the one this build already uses: explicit `validFrom` / `validTo` /
`supersededBy` properties, plus a link type from the versioned object to the act that produced it.
Live data confirms the versioning is modelled: `DemarcatedZone` holds 16 `current` and 7 `hist` rows
(P11). **Label: gap, see Section 4.**

**What adopting it changes.** (1) gives the eligibility record an audit trail the platform owns
rather than one the object's own properties assert. (3) stays a modelling responsibility; a link type
from `DemarcatedZone` to `Decree` makes "which act produced this zone version" a traversal instead of
a string comparison.

---

### (h) Search and aggregation across objects

**Capability.**
- **Ontology aggregation API** — `count`, `sum`, `avg`, `min`, `max`, `approximateDistinct`,
  `exactDistinct`, with grouping by exact value, duration bucket, fixed-width numeric bucket, or
  explicit ranges, and a filter tree supporting `and`/`or`/`not`, comparisons, `isNull`, `in`,
  `contains`, and full-text operators `containsAllTerms`, `containsAllTermsInOrder`,
  `containsAnyTerm`, `startsWith`, `wildcard` (`aggregate_ontology_objects` schema, P12).
- **Geospatial predicates** on the same surface: `withinDistanceOf`, `withinBoundingBox`,
  `intersectsBoundingBox`, `doesNotIntersectBoundingBox`, `withinPolygon`, `intersectsPolygon`,
  `doesNotIntersectPolygon` (P12).
- **Search-arounds** — link traversal as a query primitive. On Object Storage v2, in-memory up to
  100,000 objects, automatic Spark fallback above that, 10 million objects per search-around result
  set (`palantir.com/docs/foundry/ontologies/oss-limitations`, "Object Storage v2").
- **Ontology SQL** — SQL over object types. Many-to-many links require a defined link type;
  one-to-one and one-to-many links "can be used directly in Ontology SQL as defining the link type in
  Ontology Manager is not required". Interfaces, branching, scenarios, and writes are not supported
  (`palantir.com/docs/foundry/sql-warehousing/ontology-sql`, "Supported ontology features").
- **Semantic / KNN search** over a vector embedding property
  (`palantir.com/docs/foundry/ontology/using-palantir-provided-models-to-create-a-semantic-search-workflow`).

**Available here.** Aggregation: **verified against CORDON's own types**. `Parcel` grouped by
`regime` returns `buffer 20`, `containment 1`, `eradication 5`; `DemarcatedZone` grouped by
`layerKind` returns `current 16`, `hist 7`, both `REQUIRE_ACCURATE` with `excludedItems: 0` (P11).
Geospatial predicates: the query surface accepts them (P12) and `geoshape` and `geopoint` are live
property types on this enrollment — `ExampleRunway.geometry` is `geoshape`, and five `geopoint`
properties exist (P7). Semantic search: **not usable today** — the property-type census across all 43
live object types returns zero `vector` properties (P7).

**Current state.** Nothing consumes any of this. The geospatial predicates are unreachable for CORDON
because `Parcel.wkt` and `DemarcatedZone.wkt` are typed `string`, and `MonumentalTree.lat` / `.lon`
are typed `string` (P7).

**What adopting it changes.** Two things. First, aggregation is already available with no build work
— counts by regime, by measure, by window status are one call. Second, and larger: typing the
geometry properly turns point-in-polygon from a local Python step into a platform query
(`withinPolygon`, `intersectsPolygon`), and makes the Map surface in (f) real rather than a static
annex.

---

### (i) Materially relevant capabilities not currently used

**Automate.** Conditions checked continuously or on schedule, with effects that submit Foundry
Actions, trigger AIP Logic functions, execute Foundry Functions, or send platform and email
notifications with attachments (`palantir.com/docs/foundry/automate/overview`). Live monitoring
requires Object Storage v2 (`palantir.com/docs/foundry/automate/evaluation-frequency`, "Live
monitoring"). Automate integrates with Ontology Manager: object types and action types each carry an
Automations tab (`palantir.com/docs/foundry/automate/integrations`).
**Available here:** yes — two live monitors (P9, `ri.object-sentinel.main.monitor.*`:
`Collect evidence on COLLECTING`, `Run passes on each source`). Object Monitors are superseded by
Automate and are in sunset (`palantir.com/docs/foundry/object-monitors/overview`).
**Relevance:** this is the mechanism for the W5 deadline/claim loop. A funding window closing in
14 days is a time-based condition with a notification effect; no code.

**Action side effects and notifications.** Writeback webhooks run before rules and block edits on
failure; side-effect webhooks run after rules, best-effort; notifications support up to 500
template-rendered recipients, 250-character subjects (bundle `ontology-action-types`, "Decision
matrix" and "Notification limits"). **Relevance:** the deadline loop's outbound leg.

**Action overrides.** Parameter visibility, requiredness, default value, and constraints, changed
conditionally on other parameter values, with only the first matching override block executing
(bundle `ontology-action-types`, "Override patterns"). **Relevance:** progressive disclosure on
`Recompute eligibility` — show the derogation fields only when the parcel carries a monumental tree.

**Media sets.** `ri.mio.main.media-set.47ee3037-…`, a live PDF media set on this enrollment (P9);
documentation bundle `data-integration-unstructured-data`. **Relevance:** the BURP decree PDFs are
currently hand-extracted. A media set gives the source document a platform home, addressable from a
Function or AIP Logic, instead of a `sha256` string on `Decree`.

**Interfaces.** Shared property and link shapes across object types, with their own metadata
(`get_documentation_summaries` bundle `ontology-interfaces`). **Available here:**
`GET /api/v2/ontologies/{ontology}/interfaceTypes?preview=true` responds with `{"data":[]}` (P6) —
the endpoint exists, zero interfaces are defined enrollment-wide. Not supported in Ontology SQL
(`…/ontology-sql`). **Relevance:** low now. A `ProvenancedObject` interface carrying the three
orthogonal provenance fields would be the natural use, but it buys little at six types.

**Object type statuses.** `active`, `experimental`, `deprecated`. Active link types cannot be
deleted or have API names changed; an `experimental` object type cannot carry an `active` link type
(`get_documentation_summaries` bundle `ontology-link-types`, "Link type metadata fields";
`palantir.com/docs/foundry/object-link-types/metadata-statuses`). All six CORDON object types are
`EXPERIMENTAL` (P1). **Relevance:** this is why link types are currently cheap to add and cheap to
remove — and it stops being true at promotion.

**Marketplace.** The `AIP Now Ontology` project exists on this enrollment as an installed starter
product with its own object types, Workshop modules, pipelines, media set, and time series sync (P9,
P1). **INFERRED:** Marketplace product installation is available at this tier.

---

## Section 2 — Link types

### Does this tier impose a link-type quota?

**No quota is documented, and none is observable.**

- Documentation: two targeted searches returned no per-ontology or per-enrollment count limit for
  object types or link types. What the documentation does bound is **size**, not **count**:
  search-around result sets (10 million objects per operation, 30 million across all datasets in a
  query) and Ontology **volume**, which is driven by object count, property count and property size,
  and by join-table rows for many-to-many links
  (`palantir.com/docs/foundry/ontologies/oss-limitations`;
  `palantir.com/docs/foundry/ontologies/volume-usage`, "Factors that drive Ontology volume").
- Platform: this ontology already carries **44 link types** across 88 outgoing sides on 43 object
  types (P2), created by three unrelated projects. The densest single type, `Institution`, carries
  nine outgoing sides including a self-link (P2). Nothing in this enrollment's live state suggests a
  ceiling near the six-to-eight link types Wedge 1 would add.

The known dev-tier ceiling that *is* observable is on **Action types** — the build's own preflight
records ~60, and 29 exist on main today (P3). Link types are a different resource kind and are not
counted against it, on the evidence available.

**One caveat, and it is a real one:** many-to-many link types consume Ontology volume, because the
join table is indexed alongside the objects (`…/volume-usage`). All the link types Wedge 1 needs are
foreign-key backed, which requires no separate dataset (bundle `ontology-link-types`, "Link type
storage patterns"). Volume cost is therefore near zero.

### What link types would a legal-state ontology naturally carry?

Every one of these already has its foreign key present as a String property on the correct side
(P1, property listings). No dataset change is required to create them.

| Link type | Cardinality | FK property → PK | Storage |
|---|---|---|---|
| `Parcel` → `DemarcatedZone` | M:1 | `Parcel.currentZoneId` → `DemarcatedZone.zoneId` | FK |
| `DemarcatedZone` → `Decree` | M:1 | `DemarcatedZone.sourceDecreeId` → `Decree.decreeId` | FK |
| `DemarcatedZone` → `DemarcatedZone` (supersession) | M:1, self | `DemarcatedZone.supersededBy` → `DemarcatedZone.zoneId` | FK |
| `FundingWindow` → `Measure` | M:1 | `FundingWindow.measureRef` → `Measure.measureId` | FK |
| `FundingWindow` → `FundingWindow` (supersession) | M:1, self | `FundingWindow.supersedes` → `FundingWindow.windowId` | FK |
| `EligibilityAssessment` → `Parcel` | M:1 | `parcel_id` → `Parcel.parcelId` | FK |
| `EligibilityAssessment` → `Measure` | M:1 | `measure_id` → `Measure.measureId` | FK |
| `EligibilityAssessment` → `EligibilityAssessment` (supersession) | M:1, self | `superseded_by` → PK | FK |

Two that do **not** come free:

- `Measure` → `Decree` (legal basis). `Measure.legalBasis` is a free-text String, not a decree ID
  (P1). This needs a real FK column before it can be a link. That is a dataset change.
- `MonumentalTree` → `Parcel`. `MonumentalTree` carries `foglio` and `particella` but no
  `parcelId` (P1). A single-column FK does not exist. This needs a derived column, i.e. a dataset
  change, before it can be a link.

`EligibilityAssessment` is on the branch, not main: it appears in the CORDON project folder as
`ri.ontology.main.object-type.9e97095f-…` (P8) but not among the 43 main object types (P1). Its link
types must be created on the same branch as the type.

### What a link type buys that a String foreign key does not

**Object traversal.** With a link type, the relationship is a first-class API on the object: side A's
API name returns objects of type A, `company.employees.get()` / `employee.employer.get()` (bundle
`ontology-link-types`, "API name conventions"). Without one, every consumer — Function, OSDK app,
Workshop expression — re-implements the join by filtering the other object type on a string, and each
consumer can get it wrong differently. The bundle's own decision matrix states it directly: "You need
to traverse the relationship in OSDK/Functions → **Yes (link type)**; embedded property → Not
applicable" (bundle `ontology-link-types`, "Decision matrix: links vs. embedded properties").

**Workshop link panels and search-arounds.** Same matrix: "You need the relationship to power
Workshop search-arounds → **Yes (link type)**; embedded property → **No**." Search-arounds are the
traversal primitive across the operator surface — Object Explorer composes them visually
(`palantir.com/docs/foundry/ontology/applications`, "Object Explorer"), Vertex builds multi-step
filtered ones point-and-click (`palantir.com/docs/foundry/vertex/explore-object-relationships`), and
Map adds linked objects and draws the connecting line
(`palantir.com/docs/foundry/map/add-to-map`, "Search Around";
`palantir.com/docs/foundry/map/integrate-searcharounds` — "A user can Search Around from any
geospatial object to any geospatial objects it is linked to"). A String FK powers none of these. For
this build that is concrete: "show me every parcel in this zone version, and the decree that created
it" is a two-hop search-around with link types and a bespoke Function without them.

**Action-time referential integrity.** A foreign-key link is edited by modifying the FK property
through a **Modify Object** rule; no separate writeback dataset is needed (bundle
`ontology-link-types`, "Link editing and writeback"). Because the link type declares which PK the FK
resolves against, the relationship is validated by the Ontology at index time rather than asserted by
a column. Many-to-many links get explicit **Create Link** and **Delete Link** action rules (same
section). Note the honest limit: **one-to-one cardinality is an indicator, not enforced** — "Nothing
prevents multiple links from forming if the data allows it" (same bundle, "Cardinality options" and
"Gotchas" #2). Link types are not a substitute for a `joinCheck` on the underlying columns; they are
complementary.

**Search.** Ontology SQL supports one-to-one and one-to-many links without a defined link type, but
**many-to-many links require the link type to be defined in Ontology Manager**
(`palantir.com/docs/foundry/sql-warehousing/ontology-sql`, "Supported ontology features"). Derived
properties, whose entire value is aggregating or selecting across links, need links to exist at all
(`palantir.com/docs/foundry/ontology/derived-properties`). Search-around size limits only become
relevant at 100,000+ objects (`…/oss-limitations`), which this build is nowhere near.

**Costs, stated plainly.** Changing cardinality, the foreign key, or the backing datasource triggers
a reindex during which links are unavailable (bundle `ontology-link-types`, "Editing existing link
types"). Display names describe the link **to** that side, not from it, and getting this backwards
mislabels every consuming application (same bundle, "Gotchas" #7). Active link types cannot be
deleted or renamed — set `deprecated` or `experimental` first (same bundle, "Gotchas" #6); the six
CORDON object types are `EXPERIMENTAL` today (P1), so this window is open now.

---

## Section 3 — Ranked recommendations

Ranked by value to the product. "Requires re-merge" means the change alters an already-merged object
type or its backing dataset schema and therefore needs a new branch, proposal, and merge.

---

**1. Create the six free foreign-key link types.**
*Change:* `Parcel→DemarcatedZone`, `DemarcatedZone→Decree`, `DemarcatedZone→DemarcatedZone`,
`FundingWindow→Measure`, `FundingWindow→FundingWindow`, plus the three on
`EligibilityAssessment` when that branch is ready.
*Effort:* Low. Each is one `create_or_update_foundry_link_type` call naming an existing FK property
and an existing PK. No dataset change, no schema change, no new column.
*Risk:* Low. Display-name direction is the only trap (Section 2). Orphan FK values will simply not
form links — run a `joinCheck` (recommendation 3) alongside to see them.
*Reversible:* **Yes.** A link type is a separate ontology entity; deleting it removes the links and
leaves the object types untouched. All six CORDON types are `EXPERIMENTAL` (P1), so no active-status
guard applies yet.
*Re-merge:* **No.** Link types are additive entities. Merged object types are not modified.

**2. Attach submission criteria to the three Action types.**
*Change:* Encode "no verdict without a citation", "an official zone move requires an official
snapshot", and "Evaluate potential impact writes nothing" as criteria with failure messages.
*Effort:* Low to medium. Browser or platform API; the MCP connector does not expose criteria.
Read each action's live parameters first — a criterion phrased as a traversal is un-enterable if the
parameter is a scalar (bundle `ontology-action-types`, "Condition templates"; parameters are readable
at `GET /api/v2/ontologies/{ontology}/actionTypes/{apiName}`).
*Risk:* Low. Criteria are evaluated on every submission and bind human and API callers identically
(same bundle, "Layered enforcement order").
*Reversible:* **Yes.** Criteria are action configuration.
*Re-merge:* Action types are on a branch and not yet on main (P3, P4) — this is in-flight work, not
a change to merged state.

**3. Add the four unused health checks that map to existing prose rules.**
*Change:* `joinCheck` for each String FK pair; `columnValueEnumCheck` for `regime`, `source_class`,
`derivation_class`, `verification_class`; `columnType` and `schemaComparison` on all six datasets.
*Effort:* Low. `manage_health_check`, up to 750 checks per create call; all four have
`isCheckCreationAllowed: true` (P10).
*Risk:* Low. Checks report; they do not block a CSV upload.
*Reversible:* **Yes.** Checks are deletable.
*Re-merge:* **No.**

**4. Build the Workshop operator module.**
*Change:* The W6 surface — parcel list, filter list, assessment detail, link panels.
*Effort:* Medium, browser-only.
*Risk:* Low.
*Reversible:* **Yes.** A Workshop module is a standalone resource.
*Re-merge:* **No.** But it depends on recommendation 1: link panels and search-arounds require link
types (Section 2).

**5. Publish the eligibility computation as a Foundry Function bound to `Recompute eligibility`.**
*Change:* Move `assess_eligibility.py` / `zone_as_of.py` logic onto the platform and bind it as the
Action's logic rule.
*Effort:* Medium to high. A Functions repository, SDK generation, `resources.json` with `verbs`
grants, and a **tagged** release. Check first whether a `modify` rule suffices: a function is
structurally required only when the logic compares properties of two different passed objects
(bundle `ontology-action-types`, "Decision matrix").
*Risk:* Medium. The publish pipeline has several gates that each look like the previous one
succeeding.
*Reversible:* **Yes.** The Action can be rebound to rules; the local scripts remain the reference
implementation until it is proven.
*Re-merge:* **No** for the function itself. A Function can only reference object types present on
main — W1 and W2 are merged, so the six types are available.

**6. Use Automate for the W5 deadline/claim loop.**
*Change:* Time-based and object-data conditions with Action-submit and notification effects.
*Effort:* Low to medium, browser-only.
*Risk:* Low. Live monitoring needs Object Storage v2 (`…/automate/evaluation-frequency`); confirm
before relying on sub-hour latency.
*Reversible:* **Yes.** Automations are standalone resources; two already exist here (P9).
*Re-merge:* **No.**

**7. Enable Track user edit history on `EligibilityAssessment`.**
*Change:* Ontology Manager toggle, giving the assessment an immutable platform-owned changelog.
*Effort:* Low, browser-only.
*Risk:* Medium, and asymmetric. **Disabling it permanently deletes all existing edit history**
(`…/object-edits/user-edit-history`, "Disable edit history"). It records only Action-made changes,
not pipeline changes, and is **not supported on object types with marking properties**
(`…/object-views/widgets-properties-links`) — check this against any planned restricted field on
`Felling order`.
*Reversible:* **No, not cleanly.** The toggle flips back; the history does not come back.
*Re-merge:* **No.**

**8. Move SIT/BURP ingestion to REST source + egress policy + external transform.**
*Change:* Replace CSV upload with a built pipeline carrying lineage and Data Expectations.
*Effort:* High. Egress policy, source, repository, and — critically — two browser-only consents the
connector cannot reach: the source must permit code import, and the repository must import the
source.
*Risk:* Medium. Egress hostname lists must cover the whole redirect chain and any cross-host URLs
inside JSON payloads.
*Reversible:* Partly. The transform and source are removable, but **rebinding a merged object type
from its uploaded dataset to a transform output changes the object type's datasource**, which
triggers a reindex and needs a proposal.
*Re-merge:* **Yes, at the rebind step.** The transform can be built and proven against a new dataset
without touching the merged types; only the final rebind requires a branch and merge.

**9. Type the geometry properly: `wkt` → `geoshape`, `lat`/`lon` → `geopoint`.**
*Change:* Unlocks `withinPolygon`, `intersectsPolygon`, `withinDistanceOf` on the Ontology query
surface (P12) and makes Map real. Both types are live on this enrollment (P7).
*Effort:* High. The known constraint is that geoshape does not survive the MCP CSV dataset write
path, so this depends on recommendation 8 or on another dataset-write route.
*Risk:* Medium to high. A column whose rendered value contradicts its declared type fails the whole
object type's indexing, not just that column.
*Reversible:* Yes in principle — the property can be reverted to String — but every reversal is
another reindex.
*Re-merge:* **Yes. This invalidates merged work.** It changes the backing dataset schema and the
property types of `Parcel`, `DemarcatedZone`, and `MonumentalTree`, all merged in W1/W2. Do not
start this mid-remediation. **Sequence it after W3 closes**, and treat it as its own slice.

**10. Do not adopt derived properties yet.**
Beta, documented as possibly unavailable per enrollment, and reachable only from the TypeScript OSDK
`withProperties` operation (`palantir.com/docs/foundry/ontology/derived-properties`). Their value is
aggregation across links, which this build does not have. Revisit after recommendation 1.

**11. Do not adopt interfaces or semantic search yet.**
Zero interfaces exist enrollment-wide (P6) and interfaces are unsupported in Ontology SQL. Semantic
search needs a vector embedding property and the enrollment has zero vector properties across 43
object types (P7). Neither is blocked; neither earns its cost at this size.

---

## Section 4 — Explicit gaps

**Could not determine.**

1. **Tier-specific feature availability, as a document.** Palantir publishes no per-tier feature
   matrix that these searches reached. Every "available here" claim in this document rests on a live
   resource of that kind existing on this enrollment, or on an endpoint responding. Where only
   documentation supports a claim, it is labelled `INFERRED`. A capability with no live instance here
   may still be unavailable at this tier without any error surfacing until it is attempted.

2. **Link-type quota.** No documented limit found. The 44-link-type observation (P2) proves the
   floor, not the ceiling. If a ceiling exists, it will surface at creation time.

3. **Submission criteria on the three CORDON Action types.** Not readable. They live on a global
   branch: `view_foundry_action_type` on `ri.actions.main.action-type.d51f7aba-…` without a branch
   RID returns `404 Action type not found` (P4), and the main-branch action type listing returns 29
   types, none of them CORDON's (P3). The task brief states criteria are unconfigured; this survey
   neither confirmed nor refuted it. Re-read with the branch RID.

4. **Object Storage version of the CORDON object types.** Not directly read. Several
   recommendations depend on it — Automate live monitoring, Track user edit history, and derived
   properties all require OSv2. `timeseries` and `geoshape` properties are live on this enrollment
   (P7), which is suggestive, but suggestive is not confirmation. Confirm in Ontology Manager or by
   whether the platform accepts an `editOnly` property mapping.

5. **Scenarios.** Not surveyed. Ontology SQL documentation names scenarios as an unsupported
   feature (`…/ontology-sql`), which establishes the concept exists in the platform but says nothing
   about availability here. Potentially relevant to `Evaluate potential impact`, which is a what-if
   by design. Worth one dedicated read.

6. **Restricted Views and marking-based access control.** No restricted-view resource observed on
   this enrollment (P9). `RESTRICTED_VIEW` appears as a supported target type on several health
   checks (P10), which shows the concept in the API surface only. Relevant to the `Felling order`
   restricted owner-name field. Tier availability unconfirmed.

7. **Value types / semantic types.** Not surveyed. These would be the natural home for the
   `regime`, `source_class`, `derivation_class`, `verification_class` vocabularies at the ontology
   layer rather than the dataset layer. No read attempted; no availability claim made.

8. **Vertex.** No `vertex` graph resource observed (P9). The documentation is reachable
   (`palantir.com/docs/foundry/vertex/explore-object-relationships`) but nothing on this enrollment
   demonstrates it runs here.

9. **Native as-of / bitemporal object queries.** No such capability surfaced in the documentation
   searched. The searches performed were for object edit history and ontology history, both of which
   answer "who changed the record", not "what did the law say on 12 March". If a native mechanism
   exists it was not found, and the explicit `validFrom`/`validTo`/`supersededBy` modelling this
   build already uses remains the answer. Treat this as an unresolved question rather than a settled
   absence.

10. **The 84-tool MCP surface was not enumerated exhaustively.** Tool discovery was performed by
    keyword search, which returns up to 20 matches per query. Tools whose descriptions match none of
    the queries issued here are unlisted. A capability absent from this document may exist behind a
    tool that was never returned.

---

## Evidence ledger

All reads 2026-08-17. `$FH = owenwassmer.usw-22.palantirfoundry.com`,
`$ONT = ri.ontology.main.ontology.cfb1478a-5b0e-466a-aaff-b212870e8861`.

| ID | Read | Result |
|---|---|---|
| P1 | `GET /api/v2/ontologies/$ONT/objectTypes?pageSize=100` | 43 object types, no next page. Includes `Parcel`, `DemarcatedZone`, `Decree`, `Measure`, `FundingWindow`, `MonumentalTree`, all `status: EXPERIMENTAL`. Property listings per type captured. |
| P2 | `GET /api/v2/ontologies/$ONT/objectTypes/{type}/outgoingLinkTypes?pageSize=50`, all 43 types | 88 outgoing link sides = 44 link types. **0 on every CORDON type.** Non-zero on 33 other types. |
| P3 | `GET /api/v2/ontologies/$ONT/actionTypes?pageSize=100` | 29 action types on main. None are CORDON's. |
| P4 | `view_foundry_action_type({actionTypeRid: ri.actions.main.action-type.d51f7aba-dbae-4e1c-9fb2-be7fb121945f})`, no branch | `404 Action type not found` — confirms branch-local. |
| P5 | `GET /api/v2/ontologies/$ONT/queryTypes?pageSize=100` | 15 Foundry Functions live: `assessRequirement`, `openReview`, `openPolicyReview`, `collectEvidenceForRun`, `calibrationReadout`, `probeEvidenceSource`, `aipReachability`, `fetchSource`, `purgeDiscoveryIndexEvidence`, `extractCoverage`, `assembleClaimsDigest`, 4 × `xnWp6*`. |
| P6 | `GET /api/v2/ontologies/$ONT/interfaceTypes?pageSize=50&preview=true` | `{"data":[]}` — endpoint live, zero interfaces. |
| P7 | Property-type census over all 43 live object types (P1 payload) | string 476, double 94, long 47, integer 30, boolean 25, timestamp 20, date 14, **timeseries 12**, array 9, **geopoint 5**, float 2, **geoshape 1** (`ExampleRunway.geometry`). **vector 0.** |
| P8 | `list_resources_in_foundry_folder(ri.compass.main.folder.f9898a87-…)` | 12 resources: 3 action types, 4 object types (incl. branch-only `Felling order`, `Eligibility assessment`), 2 folders, and **`ri.eddie.main.logic.09648de2-…` `parseFellingOrder`** (AIP Logic). |
| P9 | `search_foundry_resources`, `search_foundry_projects` | Live on enrollment: 5 × `ri.workshop.main.module`, 4 × `ri.eddie.main.pipeline`, 3 × `ri.eddie.main.logic`, 2 × `ri.object-sentinel.main.monitor`, 5 × `ri.magritte..source`, 1 × `ri.stemma.main.repository`, 1 × `ri.mio.main.media-set`, 1 × `ri.time-series-catalog.main.sync`, 3 × `ri.notepad.main.notepad`, `ri.ontology.main.relation` (link types as Compass resources). 4 projects. |
| P10 | `get_available_check_types` | 37 check types; 36 with `isCheckCreationAllowed: true`. Build uses 4. |
| P11 | `aggregate_ontology_objects` on `Parcel` (groupBy `regime`) and `DemarcatedZone` (groupBy `layerKind`), `REQUIRE_ACCURATE` | Parcel: buffer 20, containment 1, eradication 5 (26). Zone: current 16, hist 7 (23). `excludedItems: 0`, `accuracy: ACCURATE`. |
| P12 | `aggregate_ontology_objects` tool schema | Aggregations count/sum/avg/min/max/approximateDistinct/exactDistinct; groupBy exact/duration/fixedWidth/ranges; geospatial predicates `withinDistanceOf`, `withinBoundingBox`, `intersectsBoundingBox`, `doesNotIntersectBoundingBox`, `withinPolygon`, `intersectsPolygon`, `doesNotIntersectPolygon`. |
| P13 | `GET /api/v2/ontologies` | Two ontologies: `default` (empty) and `ontology-4bf5e4f7-…` = `$ONT`, non-default. |

**Documentation pages cited**

- `palantir.com/docs/foundry/object-link-types/link-types-overview`
- `palantir.com/docs/foundry/object-link-types/create-link-type`
- `palantir.com/docs/foundry/object-link-types/link-type-metadata`
- `palantir.com/docs/foundry/object-link-types/metadata-statuses`
- `palantir.com/docs/foundry/ontology/derived-properties`
- `palantir.com/docs/foundry/ontologies/oss-limitations`
- `palantir.com/docs/foundry/ontologies/volume-usage`
- `palantir.com/docs/foundry/sql-warehousing/ontology-sql`
- `palantir.com/docs/foundry/ontology/applications`
- `palantir.com/docs/foundry/ontology/search-syntax`
- `palantir.com/docs/foundry/ontology/using-palantir-provided-models-to-create-a-semantic-search-workflow`
- `palantir.com/docs/foundry/object-edits/user-edit-history`
- `palantir.com/docs/foundry/object-edits/how-edits-applied`
- `palantir.com/docs/foundry/object-views/widgets-properties-links`
- `palantir.com/docs/foundry/workshop/widgets-edits-history`
- `palantir.com/docs/foundry/ontology-manager/restore-changes`
- `palantir.com/docs/foundry/automate/overview`
- `palantir.com/docs/foundry/automate/integrations`
- `palantir.com/docs/foundry/automate/evaluation-frequency`
- `palantir.com/docs/foundry/object-monitors/overview`
- `palantir.com/docs/foundry/logic/overview`
- `palantir.com/docs/foundry/logic/blocks`
- `palantir.com/docs/foundry/vertex/explore-object-relationships`
- `palantir.com/docs/foundry/map/add-to-map`
- `palantir.com/docs/foundry/map/integrate-searcharounds`

**Documentation bundles cited** (`get_documentation_summaries`): `ontology-link-types`,
`ontology-action-types`. Bundle index also lists `ontology-core`, `ontology-object-types`,
`ontology-interfaces`, `functions-core`, `functions-ontology-edits-tsv2`, `functions-python`,
`functions-using-embeddings-and-language-models`, `data-integration-external-transforms`,
`data-integration-unstructured-data`, `osdk-react-applications`, and 19 others not loaded here.

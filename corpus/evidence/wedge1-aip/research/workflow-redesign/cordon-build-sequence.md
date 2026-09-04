# CORDON build map

Status: **CURRENT CAPABILITY AND RELEASE-COMPLETENESS AUTHORITY** — not a serial execution gate
Date: 23 August 2026
Supersedes: `gate-7-ai-fde-ontology-handoff-prompts.md` prompts 03–14. Prompts 00–02 are complete; their outputs stand.
Unchanged: every Gate 5/6/7 design decision and every approved O0 semantic-pack sheet. The B labels group accepted capabilities and acceptance outcomes. They do not require Connor to finish or review one group before implementing an independent capability in another.

## Implementation control

Use the connected operator model's Question 2 for the build itself:

- **Allowed:** implement any accepted Gate decision whose real inputs and target resources are available; run non-contending data, Ontology, Function, Action, AIP and surface work concurrently; replace provisional mechanics with better platform-native mechanics without changing accepted meaning.
- **Required:** preserve the accepted nouns, fact owners, authority boundaries, four Actions, four Functions, kernels, non-implications, current real-world facts, platform-owned lineage and complete release inventory; run proportionate independent review after each coherent implemented unit.
- **Blocked:** only true Owen-owned ambiguity, absent real-world facts that cannot be acquired or authored within the accepted boundary, concurrent ownership of the same branch/resource/type/proposal, or a verified platform constraint. Batch numbering, prior plan status and review ceremony are not blockers.

## Why the build remains vertically coherent

The 14-prompt sequence was written before Gate 7 closed. It is **layer-first**: all 25 types, then all links, then all Functions, then all Actions, then AIP, then surface. Nothing is end-to-end testable until step 10 of 14.

Palantir's own Ontology guidance is the opposite:

> *"Prefer incremental improvement over big-bang refactors. A slightly imperfect Ontology that is in use and generating value is better than a theoretically perfect one that is still being designed."*
> *"Steer toward good design without being a roadblock. If something needs to be working within a tight deadline, build something reasonable now with a clear path to improvement."*
> *"Defend the critical invariants — naming quality, semantic clarity, and security design are hard to fix later. Cut corners on implementation details, not on these."*

The build remains **vertical and operator-centered**: implemented work connects real facts, semantic owners, decisions, execution and outcomes. Vertical coherence guides what is valuable; it does not force a serial order when independent resources can advance together.

## Cut from the prior sequence, with reasons

| Cut | Reason |
|---|---|
| API-name prefixes (`Cordon*`, `CordonBs*`) | Historical entities are orphaned shells that do not resolve on main; nothing can collide. Prefixes also violate *"name things for humans… intuitive and self-documenting."* Non-semantic types use the platform's **hidden flag**, which is the documented mechanism. |
| Name blocklist, 9-check clean-room matrix (C1–C9), type groups as governance | Governance theatre against a non-existent collision risk. Replaced by one rule: the branch diff contains only new resources. |
| 13-folder taxonomy | Five folders carry the same information. |
| 19-column RID ledger, per-prompt proposals-never-merged, role/group design | Recording overhead exceeding its own value at a one-principal enrollment. Ledger reduced to six fields. |
| Sandbox probe campaigns, historical-project permission remediation, `zz-preflight` deletion ceremony | Work on resources irrelevant to the build. The historical project is simply not referenced. |
| DevOps/release-management proof as a gate | Unevidenced on this enrollment and not on the path to a working system. Branch discard and manifest revert are the rollback story. |
| Plan-then-token gate on every step | Two round trips per step. Retained only where risk is real: capacity/staged writes and ingestion. |

## Kept, because they are load-bearing

Four shared prerequisite kernels (one implementation, two callers). The exact four-Action write plane, actions-only editing. Replay-safe execution binding and durable receipts. `INDETERMINATE` semantics per D1/D1a. Build-blocking Data Expectations. Hidden non-semantic substrate. Real records over fixtures. The reduced RID ledger.

## Live enrollment constraints — bake these in where they hit

| ID | Constraint | Where it applies |
|---|---|---|
| **X-15** | TSv2 repositories cannot join Global Branching | B3 onward: the repo uses local branches; its **published tag is the release event** |
| **X-16** | Function-backed Actions are branch-disabled by default | B3, B4, B5: enable the per-Action branch-execution toggle before any branch test; record it |
| **X-17** | Branch writes require object-type branch indexing; a missing index surfaces as an opaque 500 | B2 onward: every branch test plan includes a wait-for-index step |
| **staged-write preview** | Staged writes cannot be previewed | B4: keep logic in unit-tested pure helpers; the staged-write wrapper stays thin |
| **chatbot approval** | Approval-before-execution defaults ON | B7: disable it for the four Action tools |
| **edit-only ordering** | Edit-only properties require a permissioned backing dataset | Each backing dataset precedes the object type that consumes it; unrelated work continues |
| **X-04 — RESOLVED** | BYOM lacks marking support and is admin-only, but Llama-3.3-70B and Nemotron are already hosted | Hosted open-source model at launch (version-pinned). Fine-tuning is a post-build, separately-governed upgrade. Contract 8's tuning requirement is amended accordingly. |

## Compute locus — where work runs. Read this before every step.

**This rule was missing from the first version of this document and B1 was built without it. That was a specification failure, not an implementer failure.** It is now the first rule of the build.

Gate 6 fixes the end-to-end data path explicitly:

```
source system snapshot / increment / changelog
→ Data Connection batch, streaming or CDC sync
→ immutable raw dataset (received bytes, source version, transaction metadata)
→ Pipeline Builder / transform validation and normalization
→ Data Expectations: identity, referential integrity, authority envelope, geometry, row conservation
→ curated current-fact dataset + append-only occurrence dataset + M:M join datasets
→ OSv2 object-data funnel
```

Every mechanism in that chain is marked **REQUIRE** in the Gate 6 mechanism ledger: M01 Data Connection sync, M09 immutable raw datasets, M11 curated canonical datasets, M12 Pipeline Builder transforms, M14 Data Expectations, M28 geospatial normalization, M43 Data Lineage.

### The rule

**No acquisition, curation, validation, normalization or quarantine logic runs outside the platform.** Fetching, parsing, geometry work, key construction, deduplication, envelope checks and quarantine routing are **versioned platform resources** — external transforms and pipelines — not scripts on a builder's machine whose output is uploaded.

A locally-computed file uploaded into Foundry breaks four things at once:

1. **Lineage starts at "a file appeared."** M43 requires `source → raw → curated`. An upload has no upstream edge.
2. **The curation logic is unversioned and unreviewable.** It cannot be re-run, diffed, branch-tested or rolled back.
3. **Expectations validate the output of unversioned logic** rather than validating the transformation itself.
4. **B9's honest degradation has nothing to attach to.** Freshness SLOs and staleness detection require the platform to own the fetch. If curation happened on a laptop, the platform cannot know a source went stale — and `INDETERMINATE` becomes decorative. This is the serious one: the entire honest-degradation contract depends on platform-owned ingestion.

### The mechanism, confirmed available

**Source-based external transforms.** A Data Connection **REST API source** with an egress policy, imported into a **Python transforms repository**, using the `@external_systems` decorator and the source's pre-configured HTTPS client. Custom paging logic lives in the transform, which is the documented pattern for paged APIs. External transforms connected to sources **appear in Data Lineage**, which is what satisfies M43.

Constraint: a REST API source may not carry multiple domains. Create **one source per domain** (SIT ArcGIS, BURP, each municipal mirror).

### Two different check mechanisms — do not confuse them

| Mechanism | Behaviour | Where it belongs |
|---|---|---|
| **Data Expectations** (`transforms-expectations` in a transform) | **Build-blocking.** A violated expectation aborts the build; bad data never lands. | M14 / Contract 1 — every curated output, from B1.1 onward |
| **Data Health checks** | **Monitors.** They alert; they do not abort a write. | B9 — freshness SLOs, staleness, conservation drift |

Both are required, at different steps. A Data Health check is not an expectation and cannot stand in for one.

### Builder-side tooling is still allowed — for exactly two things

Read-only verification (querying the platform to check what landed) and one-off reconnaissance. **Never** for producing data that lands, or for logic the system depends on.

### Every step must state its locus

If a step does not say where its work runs, that is a defect in this document — raise it rather than choosing.

## Standing rules

- One project `CORDON`, one Global Branch. The TSv2 repository uses local branches; its published tag is the change event.
- **Intuitive names, no prefixes.** `CadastralParcel`, `InterventionOccurrence`, `DispatchIntervention`, `assessNamedActionReadiness`. Non-semantic types carry the **hidden** flag.
- The historical project is not referenced. That is the entire rule.
- Ledger row: `kind | display_name | full_rid | api_name | version_or_tag | build_step`. Append before reporting a step complete. Never a name-only success.
- No generic Event / Case / Status / Task / Queue / WorkItem type. No fifth Action. No generic edit, history-append, or manual outcome tool. No priority score.
- Real records wherever they exist. Notional rows only for the cooperative's private layer, where real data is genuinely underivable. Fixtures are never coverage.
- Every step ends with `State`, `Next`, `Escalations`.
- Plan-first applies only to **B4** and **B6**. Every other step plans and builds in one pass, then stops for review.

## The slices

```
B1  Foundation + duty-slice data      ─┐
B2  Duty-slice ontology                │ Slice A — first working trajectory
B3  Duty-slice logic + write plane    ─┘
B4  Capacity (Scenarios, staged writes)   Slice B — highest-risk integration, on proven scaffolding
B5  Complete the model                    breadth to 25 types / 32 links / 4 Actions / 4 Functions
B6  External outcome ingestion
B7  AIP harness
B8  Evals + hosted open-source model
B9  Automate, health, lineage
B10 Surface — Workshop Decision Loop
B11 Freeze, merge, demo
```

---

## B1 — Foundation and duty-slice data — **COMPLETE, with the data path superseded by B1.1**

Executed 2026-08-24. Report: `reviews/ferro-b1-data-spine.md`.

**Accepted and retained:** Global Branch `cordon-w1-build` (`ri.branch..branch.46351cc7-a8b0-45a8-909f-d91c1bbc8ce1`, dataset branch `cordon-w1-build-PvSFfb`); folders; RID ledger; the **acquisition facts** — 241,122 parcels with per-comune conservation verified by platform SQL, 28 official areas, 3,575 plants, seven acts with matching sha256 including DDS 92/2024 and DDS 39/2026 newly located; the curation *rules* derived (null-`NUMERO` sentinel `#NULL-{OBJECTID}`, `SEZIONE` strip, qualified key, WGS84 envelope); the 47-row manifest; the notional layer with zero collisions against 493,508 real identifiers.

**Superseded:** the data *path*. Acquisition ran via local `curl`, curation ran in `data-tmp/b1/curate_b1.py` on the builder's machine, and outputs were uploaded. The aborting gate was that local script. This violates M01, M09, M12, M14 and M43, and it is the specification's fault — B1 as written never named a compute locus.

**Retained as verification oracle:** every count and hash Ferro proved becomes the expected value B1.1 must reproduce. His work is not discarded; it becomes the independent check on the platform-native rebuild.

---

## B1.1 — Rebuild the data path platform-native

**Grill supersessions (Owen, 2026-08-24) — these govern over the step text below where they differ.** Binding detail: `b1.1-object-data-mapping.md`.

1. **Full-universe ingestion.** Current full-region cadastre comes solely from the authoritative AdE Puglia bulk package. Its packages follow cadastral units: E885/Manfredonia covers Zapponeta-area land. WFS has no B1.1 gap to fill. SIT Catasto has no product role and is purged entirely. Also ingest the full monumental registry (341,428), **all** monitoring sample layers, all zone layers and administrative boundaries as `OfficialArea` rows.
2. **Plant→Parcel is total**, populated by spatial containment against the full cadastre, corroborated by registry attributes; disagreement flagged; residual failures quarantine-and-verify.
3. **`GoverningInstrument` is discovered, never hand-listed.** BURP RSS heartbeat → `/documenti` catalog (primary, document-grain, full listing census; byte-fetch scoped by section/topic) → immutable raw PDFs + discovered-document records → copy admission → one curated `Governing Instrument Documents` Media Set → canonical MediaReference on the Instrument backing. `/bollettini` manifests = incremental completeness reconciliation. Measure pages = program reconciliation lane. The seven held instruments re-derive and must match known hashes and media items. Four invariants: no page-number-only cursoring; two-view reconciliation; heartbeat sync metadata recorded (SLA alarm is B9); raw listing snapshots and bytes preserved.
4. **`OfficialArea` existence from the instrument registry; geometry from the scheduled zone sync** with dated versions; diffs are change events; act-derived foglio coverage where no named layer exists; mismatches in both directions surface as facts.
5. **Row provenance is source reference + as-of only.** The `source_class`/`derivation_class`/`verification_class` taxonomy is first-build drift and is retired from all product schemas. Assurance lives in the source register and manifest.
6. **The notional private layer is out of B1.1 entirely** — composition is grilled with Owen (Q5) before any row exists.
7. **No branch/merge ceremony.** Owen controls the enrollment. Data lands on `master` directly; review gates are process gates (plan review, implementation review), not platform choreography.

**Locus: entirely on-platform.** Data Connection sources → external transforms → raw datasets → transforms → curated datasets, with build-blocking Data Expectations and real Data Lineage. Builder-side tooling is read-only verification only.

**Mode:** Data connection + Data integration. **Tools:** Data Connection source create, egress policy, Python transforms repository, external transforms, datasets, Data Expectations, Data Lineage read.

```text
Build the current source-owned data spine as versioned platform resources. AdE bulk is the sole Parcel source.

Read first: BUILD-SEQUENCE "Compute locus", the Gate 6 data mechanism ledger (M01, M09, M11, M12, M14, M28, M43), `b1.1-object-data-mapping.md`, and `fanout/ade-cadastre-preflight.md`. AdE bulk owns the complete Parcel snapshot. WFS and SIT Parcel are absent from B1.1.

1. CLEAR THE CORPSE
   The expected values are already recorded in `reviews/ferro-b1-data-spine.md` — per-comune counts, layer counts, seven act hashes, geometry envelopes. That report is dated evidence and is the oracle. The uploaded datasets are not needed to hold it.
   Per D11, trash B1's uploaded datasets so the rebuild takes the clean names. No `_oracle`, `_v2` or `_old` suffix survives anywhere. The two constructed quarantine rows go with them.

2. DATA CONNECTION SOURCES — one per domain
   - `ade-cadastre-bulk` -> wfs.cartografia.agenziaentrate.gov.it plus its download CDN (current semestral snapshot)
   - `sit-puglia-arcgis` -> webapps.sit.puglia.it (current non-cadastral Plant/Area domains only; no Catasto Parcel family)
   - `burp-regione-puglia` -> burp.regione.puglia.it (public)
   - `regione-puglia`      -> www.regione.puglia.it  (public)
   - one source per municipal mirror domain actually used
   Each with its own egress policy. Enable "Allow this source to be imported into code repositories" on each. Do not reuse the sources in the historical project.

3. PYTHON TRANSFORMS REPOSITORY
   One repository in `logic`. Import the sources via the External Systems panel. Use source-based external transforms — `@external_systems(sit=Source("<rid>"))` — not the legacy credential-based form.

4. EXTERNAL TRANSFORMS -> IMMUTABLE RAW
   Cadastre: preserve the immutable AdE regional ZIP, enumerate province/comune ZIPs, parse per-cadastral-unit GML, reconcile exact `numberMatched/numberReturned`, dissolve repeated geometry features by `NATIONALCADASTRALREFERENCE`, and quarantine blank references. Do not compare the 256 cadastral packages to the 257 current civil municipalities as if they were the same identity system. Civil municipality context comes from OfficialArea intersection. WFS is not built in B1.1.
   Other SIT ArcGIS domains retain the proven `returnIdsOnly` -> `OBJECTID IN (...)` GET batches of 400, outSR=4326, f=json path. `resultOffset` is a no-op and must not appear.
   Raw datasets preserve received payload plus provenance: source, request URL, where-clause, retrieved_at, source version where exposed. Raw is immutable and unvalidated.
   Acts: fetch PDFs through the BURP/regione sources into a media set or file-backed dataset, hashing on landing.

5. TRANSFORMS -> CURATED, WITH BUILD-BLOCKING EXPECTATIONS
   The rules in curate_b1.py move into versioned transforms: qualified-key construction, SEZIONE strip, null-NUMERO sentinel, geometry validation, WGS84 envelope, identity-class assignment for plants.
   Attach Data Expectations using `transforms-expectations` so a violation ABORTS THE BUILD. These are not Data Health checks. P01 already proved build-abort works on this enrollment (job ri.foundry.main.job.d757da9b-b15c-4ace-9bcc-46d79b3ea184).
   Cover: PK uniqueness, qualified-key collision, row conservation raw->curated, FK existence, geometry validity and envelope, null/domain on load-bearing fields.
   Curated data lands on `master`. The global branch carries ontology metadata only.
   Product rows carry only operator-relevant source reference and as-of. Source class, assurance, coverage and build-side seededness stay in the source register/manifests, never as product-row enums or UI states.
   Geometry is native geoshape/geopoint. The MCP CSV write path cannot emit them; use a path that can.

6. QUARANTINE — from real failures, not constructed ones
   Each family owns one reject output; no shared multi-producer quarantine. Rows failing a row-level rule route there with the source identity and reason.
   DDS 39/2026 currently supplies a real conflict: Rutigliano and Leverano mirrors disagree. Fetch both when reachable; the disagreeing copy routes to `instruments_rejects` with `source_conflict_unresolved`. This is a useful live exercise of the admission rule, not the product's definition. If Leverano is temporarily unavailable after bounded attempts through its admitted source, record the test UNTESTED and continue. Do not fabricate a replacement.

7. VERIFY CURRENT SOURCE COMPLETENESS; USE B1 AS DATED EVIDENCE
   Same-run source controls are the build gates: requested IDs equal returned IDs; raw accepted + rejected equals the source population; curated + family rejects equals raw; source identity survives curation one-to-one; every Plant resolves to a Parcel.
   The B1 report is dated evidence, not a product invariant. Its eight-comune counts, positive sample IDs and seven document hashes are reviewer comparisons that help distinguish source movement from transform defects. A difference is adjudicated; it does not automatically make yesterday's value override today's source.

8. SOURCE REGISTER / MANIFEST
   One platform-native source-register dataset is the sole assurance owner. It is produced from Data Connection source configuration and raw transactions, not authored locally. At minimum it carries source identity/URL, authoritative voice/family, covered object/fact grain, latest retrieval window, extraction method, raw transaction references, payload/listing coverage, license where stated, and admitted/blocked/degraded state. B9's freshness and coverage monitoring reads this dataset. Assurance does not return to product rows.

Done when:
- Data Lineage shows source -> raw -> curated for parcels, official_areas, plants and instruments. This is the acceptance criterion B1 could not meet.
- A deliberately broken transform aborts its build via an expectation — demonstrate it, then revert.
- Every observed real source conflict is quarantined by rule with its reason recorded; unavailable conflict sources are recorded as UNTESTED after bounded attempts.
- Current-source conservation and one-to-one identity gates pass; reviewer comparisons against B1 evidence are explained where they differ.
- The platform-native source register resolves every B1.1 source and raw transaction.
- No curation logic exists outside the repository.

Do not: create object types, Actions, Functions or AIP resources. Do not upload a computed file as a dataset. Do not fabricate a failing row.
```

### Rulings on B1's escalations

**Escalation 1 — "Data Lineage is folder+manifest, not a Pipeline Builder graph. Accept for B1?"** **No.** M12, M14 and M43 are REQUIRE, and D16 binds independently: *"Local code that executes inside that substrate is allowed; local computation that produces rows later asserted into it is not."* B1.1 closes it. Correctly raised.

**Escalation 2 — dataset residency: branch vs master. Ferro was right; my first ruling was wrong.** `AGENTS.md` owns wedge-local branch mechanics and states: *"Data lands on `master`; the global branch carries ontology metadata only."* Ferro cited Atlas to the same effect and observed the platform minting a `master` branch on every dataset create.

I had read Gate 6 M40's "branch-local … changes" as covering data. It covers resource *definitions* — pipeline, Ontology, Function, Action. Data residency is a different fact, and `AGENTS.md` owns it. **D12** settles why: after the ontology metadata merges, object types must resolve against backings the destination can read.

**Ruling: data lands on `master`; the global branch carries ontology metadata only.** B1.1 lands curated data on `master`. This removes the B2 residency risk rather than deferring it.

---

### Mechanism selection — codeless first, falsification recorded

The `AGENTS.md` pipeline rule prefers codeless Data Connection / Pipeline Builder, and permits a code repository *"only after documentation, catalog state, or a bounded platform probe falsifies the codeless path — not because a canvas interaction was expensive."*

**Falsification, from documentation plus live probe:** the REST connector's paging primitives are page-increment, offset-increment, cursor/next-link, and datetime-increment. This ArcGIS server **silently ignores `resultOffset`** — verified live, page 0 and page 1 return identical rows — which defeats both increment primitives. It exposes no cursor and no date paging. The only complete-fetch method is two-phase: `returnIdsOnly`, then `OBJECTID IN (…)` batches of 400, which requires array chunking and string joining. That is a transformation, not a paging primitive, and the connector's list loop would issue one call per id rather than per batch.

**Therefore: external transforms for the ArcGIS sources**, which is the documented mechanism for exactly this case — *"an existing Data Connection source type is not available… the capability offered through the Data Connection user interface does not have the desired features."* Codeless remains preferred for anything that does not hit this constraint, and act PDFs are a plain file sync.

**Cadastre mechanism ruling.** AdE bulk is the sole Parcel source. Package identity is cadastral, not current civil-administrative: E885/Manfredonia covers Zapponeta-area land. WFS attribute filtering is unsupported and B1.1 has no WFS gap to fill. SIT Catasto and all historical Parcel reconciliation are purged because they change no operator decision.

## B2 — Duty-slice ontology

**Mode:** Ontology editing. **Tools:** object/link type edit, datasource mapping, branch read.

**Locus:** on-platform Ontology Manager against the branch. Object types bind to the **B1.1 curated datasets**, not to the `_oracle` copies.

**Added acceptance item (X-17):** prove object-type **branch indexing** works against branch-scoped datasets — index, wait, then read and write on the branch. A missing index surfaces as an opaque 500. This is the mechanic behind B1's residency escalation; resolve it here rather than copying data to master.

```text
Index the duty trajectory into the Ontology. Read the Gate 5 graph and the minimum-properties sheet first.

Visible object types (7), intuitive names, backed by the B1 curated datasets:
OperatorParty, AgriculturalHolding, CadastralParcel, OfficialArea, IndividualPlant, GoverningInstrument, Intervention.

Hidden object types (4) — set the hidden flag; these are non-semantic technical resources, not operator surface:
InterventionOccurrence, ParcelStanding, HoldingPartyAssignment, InterventionPartyAssignment.

Keys: stable String primary keys with intuitive API names (`operatorPartyId`, not a mutable title). Qualified external references stay separate source-backed identity properties. IndividualPlant is populated only from registry identity or official sample identity (ID_CAMPIONE) — no detection mints a Plant.

Properties: exactly the Gate 5 minimum. Source-backed properties carry source and as-of. Cooperative-owned facts are edit-only and writable only by an Action. No status, stage, ready, complete, owner, assignee, notes, or timeline field on any type. Parcel and OfficialArea use geoshape; IndividualPlant uses geopoint.

Links for this slice:
- FK: IndividualPlant → CadastralParcel.
- M:M join tables: Holding operates Parcel; Instrument governs OfficialArea; Instrument is basis for Intervention; Intervention scopes Parcel; Intervention scopes identified Plant.
- Object-backed: ParcelStanding, HoldingPartyAssignment, InterventionPartyAssignment — each carrying Party, context owner, basis Instrument, role/standing kind, bounded scope, effective interval, consequential powers.

Enable actions-only editing on every type with edit-only properties. There is no direct-edit path.

Branch indexing: after creating types, wait for branch indexing to complete before any read or write test. A missing index reports as an opaque 500 (X-17).

Done when: all 11 types resolve on the branch; one Bari-belt parcel traverses to its zone(s), its identified plants, its governing instrument, and its intervention; a source-backed property cannot be overwritten by an edit; an edit-only property has no datasource column.

Do not: create Actions, Functions, or the remaining types. Do not add a type group or a naming prefix.
```

---

## B3 — Duty-slice logic and write plane → first working trajectory

**Mode:** Functions editing / TSv2. **Tools:** Code Repositories, OSDK generation, TSv2 Functions, publish/tag, Ontology Action editing, submission criteria, Action logs, tests.

**Locus:** on-platform. Kernel and Function code lives in the TSv2 repository; unit and property tests run in repository CI; the trajectory runs against the branch Ontology through action forms or a published test Function. A locally-run simulation of the trajectory is not evidence — the Action must actually execute on the platform and return a real receipt.

```text
Make the duty trajectory executable end to end. Read the approved kernel sheet for Dispatch Intervention and the chatbot tool schema (for the receipt contract) before writing code.

Repository: one TSv2 repository in `logic`. It uses LOCAL branches — TSv2 cannot join Global Branching (X-15). Its published tag is the release event; record every tag in the ledger.

Build:
1. `dispatchInterventionPrerequisites` — the shared kernel, implemented exactly as the approved sheet specifies: ordered predicates; missing→NOT_READY; stale→INDETERMINATE; source-conflict→INDETERMINATE with named resolution owner; NOT_READY dominates; the complete evaluation is always returned. Output carries verdict, satisfied premises, blockers with cure owners, indeterminate premises with failed assurance reference, continuable scope, kernel version, premise fingerprint.
2. `determineAffectedDecisions` — scoped to this slice: given a monitoring-positive change, return affected decisions AND explicitly unaffected work, with owners, clocks and indeterminate premises. It filters a pipeline-owned candidate relation; it does not rediscover the population.
3. `assessNamedActionReadiness` — dispatches to the kernel and returns its typed explanation. No stored readiness anywhere.
4. `DispatchIntervention` — function-backed Action calling the SAME kernel version on fresh state. Writes one InterventionOccurrence and an optional work-order Instrument link; nothing else. Submission criteria carry only coarse platform gates (caller permission, parameter presence, obvious target state); all domain logic lives in the kernel.
5. One Action log type with Edits provenance.
6. Durable receipt: authenticated principal, originating message id, Action RID and version, exact targets, target count, bounded delta summary, premise fingerprint, single-use idempotency key. Exactly one status returned: COMMITTED, ALREADY_COMMITTED, REFUSED, CLARIFICATION_REQUIRED. A committed receipt stays retrievable if response generation fails.

Enable the per-Action branch-execution toggle before branch testing (X-16); record it. Keep heavy logic in pure, unit-tested helpers.

Capacity premise at this step is route-conditional. PugliaOlive-controlled or contracted execution cannot reach READY without a real Capacity Commitment and therefore waits for B4. The DET 3/2026 ARIF route may use authenticated member election/ARIF assignment plus current external feasibility and clock evidence; this creates no cooperative Commitment. DET 3/2026 is historical: commit only in a dated simulation/replay, or use a currently operative basis for a live branch Action.

Done when this trajectory runs on the branch through action forms or a test harness — no chatbot yet:
  monitoring positive → determineAffectedDecisions returns affected AND unaffected
  → assessNamedActionReadiness REFUSES with a real blocker and its cure owner
  → cure the blocker → READY
  → DispatchIntervention → COMMITTED receipt with non-implications stated
  → replay the identical command → ALREADY_COMMITTED, no duplicate occurrence
  → kill a load-bearing source → the dependent answer returns INDETERMINATE and the Action refuses

Do not: build the other three Actions, Scenarios, staged writes, chatbot, or surface.
```

---

## B4 — Bounded capacity comparison and commitment

**Mode:** Ontology editing + Functions editing / TSv2. **PLAN FIRST — stop for review before implementing.**

```text
Add the smallest capacity feature that resolves a real cooperative scarcity decision on the proven B3 spine.

Required result:
- InterventionCapacityCommitment with the accepted owner/Intervention facts and history.
- `compareFeasibleInterventionPortfolios` over the accepted rolling 12-week weekly resource inputs and deterministic policy. It returns a small complete alternative set, binding constraints, deferrals/fallbacks and the exact edit count.
- one immutable selected-plan package only if the exact Action needs it for complete-set validation, idempotency and stale-state refusal.
- `commitOrRebalanceInterventionCapacity` revalidates the complete plan on current state and commits atomically with a durable receipt; protected commitments and >10,000 edits refuse with zero writes.

Mechanism order: use a bounded ordinary function-backed multi-edit Action when it satisfies atomicity and receipt semantics. Use staged writes only for a proven read-after-write/nested-edit need. Use Ontology Scenarios only if one bounded probe shows they replace custom comparison/edit code without adding a second transaction or approval. Native table/chart/metric comparison comes before any custom widget.

Done when: the manager compares two real alternatives, commits one exact plan, retrieves the receipt on replay, and sees a stale/protected plan refuse. Stop. Capacity is a supporting feature, not the product thesis or a never-cut demo beat.
```

---

## B5 — Complete the model

**Mode:** Ontology editing + Functions editing / TSv2.

```text
Bring the Ontology to the full accepted shape now that the spine works.
```

**Locus:** on-platform throughout. The funding-side data below is acquired the **same way B1.1 established** — Data Connection source, external transform, raw, curated, expectations, lineage. No local extraction, no uploaded file. This step reuses B1.1's sources and repository; it does not invent a second ingestion path.

```text

Remaining visible types: PublicProgrammeOrMeasure, PublicProceeding, CooperativePursuit (plus InterventionCapacityCommitment if B4 did not create it).
Remaining hidden types: InstrumentOccurrence, ProceedingOccurrence, PursuitDecisionRecord, CommitmentChangeRecord, CashOccurrence, InterventionPlantScope, CooperativeMembership, InstrumentPartyAssignment, ProceedingPartyAssignment — hidden flag on all.

Target inventory: 11 visible + 14 hidden domain types, plus one Action log per manager Action.
Target link map: exactly 7 FK, 19 metadata-free M:M join tables, 8 object-backed fact relationships. D10 Q5i narrows Holding→Parcel to a Parcel-side current-Holding FK. Each accepted adjacency has exactly one physical owner — no duplicate traversal.

Remaining kernels and Actions from the approved sheets: AcceptCooperativeExecutionMandate, DecideCooperativePursuit. Same pattern as B3 — one kernel, two callers, coarse criteria, exact effects, non-implications on every receipt.
Remaining read Function: `determineRemainingExposure` — independent legal, operational, financial and biological lines, each with owner, clock and indeterminate premise. It never infers order→cash or acceptance→establishment.

Populate the funding-side real data this requires: the Article 6 chain (DDS 377/2020 → rankings → DDS 40/2026 → DDS 53/2026 → DDS 120/2026), and SRD01.01B as programme/instrument/window rows only.

Done when: exact inventories verify (25 domain types, 4 log types, 7/19/8 links, 4 kernels, 4 Functions, 4 Actions); each Action's non-implication list is enforced by test; no accepted adjacency has two physical owners.
```

---

## B6 — External outcome ingestion

**Mode:** Data connection. **PLAN FIRST — stop for review before implementing.**

**Locus:** on-platform, extending the B1.1 source and repository pattern to the authenticated occurrence path. B1.1 established connectors, raw-dataset provenance and build-blocking expectations; B6 adds the admission profile, idempotency and reconciliation on top of that foundation rather than building a parallel one.

```text
Implement the legal/public admission profile end to end, and name the other five as contracts only.

Common technical envelope: source system, stable occurrence id, source version, received time, immutable raw evidence pointer with hash, idempotency key, supersedes/reverses pointer, reconciliation result.

Legal/public profile — the only one implemented now: authentication or official-publication proof; competence resolved by act, office and proposition; subject grain; legal effective and consequential dates; amendment, stay and supersession ordering; signed act plus annex as evidence; quarantine, conflict and indeterminate states.

Demo event: DDS 167/2025 (Sammichele final balance €12,955.54; PDF sha256 af68e7dd…557a7d, byte-verified). Its public chain is grant → advance → balance request → verification → liquidation. Ingest it as a ProceedingOccurrence.

The cash line stays INDETERMINATE. No public treasury settlement exists for any Italian Xylella payment chain — order ≠ cash is the public record's own shape, not a modelling choice. There is no manual Mark Paid, Record Outcome, or Mark Accepted tool anywhere in this system.

Test: replay the identical envelope → exactly one occurrence, no duplicate. Correction and supersession preserve prior occurrence identity. An invalid signature or wrong competent actor quarantines.

The other five profiles (member/beneficiary, professional, contractual/field, biological, bank/treasury) exist as written admission contracts with their producers explicitly unadmitted. No lowest-common-denominator validator.
```

---

## B7 — AIP harness

**Mode:** Functions editing / Logic + Chatbot Studio.

```text
Build the conversational execution layer against the approved tool schema sheet.

Runtime allowlist, exactly ten tools:
Reads — determineAffectedDecisions, assessNamedActionReadiness, compareFeasibleInterventionPortfolios, determineRemainingExposure, curated object query, request clarification.
Writes — AcceptCooperativeExecutionMandate, DecideCooperativePursuit, CommitOrRebalanceInterventionCapacity, DispatchIntervention.

Curated object query covers the 11 visible types only. Hidden substrate is reachable solely through parent-scoped projections and Function outputs.

Configure document context over `Governing Instrument Documents`. Every retrieved legal/basis passage claim cites the exact Media Set RID, Media Item RID and source PDF page. If page identity is unavailable, abstain from the passage-level claim rather than emit an unpaged legal citation. Retrieved prose supports explanation; it never creates authority, applicability or an external outcome.

DISABLE approval-before-execution for the four Action tools — it defaults ON. A clear authenticated manager command is the decision; a generic approval modal is not part of this product. Clarification asks what the manager meant; it never asks permission.

Direct-execution binding on every mutation: authenticated principal, immutable originating message id, Action RID and version, exact targets or proposal id, target count and material-delta summary, premise fingerprint, single-use idempotency key, expiry. At most ONE mutating tool per conversational turn. Never auto-retry a mutation after an uncertain response; retrieve the durable receipt instead.

Clarification triggers, closed list: ambiguous target; ambiguous or unbounded scope; deictic reference after the selection changed; missing required reason; unresolved acting authority; materially ambiguous consequence; more than one plausible proposal.

Decisions owned by other actors are prepared and routed, never executed or hand-recorded.

Done when: each of the four Actions executes from an explicit command with a durable receipt; an ambiguous command clarifies rather than guessing; an unauthorized command refuses server-side; two mutations proposed in one turn are refused before either executes.
```

---

## B8 — Evals and production model

**Mode:** Machine learning / Exploration (AIP Evals).

**Locus:** on-platform. Eval suites, cases and custom evaluators are platform resources; edit-producing cases run in Ontology simulations. Trajectory cases are generated from object sets on the platform, not authored as local files and uploaded.

```text
Freeze the evaluation suite and select the production model.

Model decision (accepted): a HOSTED open-source model is the production model at launch — Llama-3.3-70B-Instruct or Nemotron, version-pinned because several hosted models sunset 2026-09 through 11. BYOM is not used: it lacks marking support and is enrollment-admin only. Fine-tuning is a post-build, separately-governed upgrade; Contract 8's tuning requirement is amended accordingly and the amendment is recorded.

Trajectory cases per Action and per read Function: clear positive; ambiguous → clarification; unauthorized → refusal; stale → INDETERMINATE; duplicate replay → ALREADY_COMMITTED; hard one-premise negative; prompt injection in retrieved content; Italian and code-switched phrasing; terse deictic commands.

Every edit-producing case runs in an Ontology simulation. The live Ontology is unchanged before and after — verify it.

Custom deterministic evaluators score exact tool, exact target, exact parameters, exact edits, clarification, abstention, and prohibited implications. Prose similarity is not a metric.

For evidence-grounded cases, also score the exact cited Instrument/media item and page when the expected basis is page-specific. A correct answer citing the wrong act or copy fails.

Hard gates, Boolean, zero-failure: no unauthorized Action; no wrong target or wrong edit; no reserved-decision fabrication; no geometry→law, recommendation→commitment, order→cash, or acceptance→establishment collapse. Aggregate quality never compensates.

Retain failures. A suite with no recorded failures has not been run honestly.
```

---

## B9 — Automate, health, lineage

**Mode:** Governance.

```text
Wire operations. Automate detects, recomputes, routes, notifies and stages proposals. It does NOT submit any of the four manager Actions.

One visible automation: new monitoring snapshot detected → recompute affected decisions → notify the current owner. Idempotent effects; at-least-once execution assumed.

Data Health on the load-bearing sources: freshness SLO, build success, conservation counts, object-index liveness. A health failure makes dependent Function answers INDETERMINATE and makes the affected Action refuse — verify this end to end, since it is the honest-degradation behaviour the whole design rests on.

Dual lineage: Data Lineage for source→raw→curated→object; Workflow Lineage for command→Function→Action→occurrence. One screenshot-able trace of each.

Instrument evidence lineage extends source URL → raw PDF hash → Media Set item → Instrument MediaReference. Monitor broken references and Media Set/item availability; media health never substitutes for source freshness or legal effect.

Compatibility manifest pinning: object/link/property versions, dataset schemas and expectations, Function tags, Action versions, chatbot and tool-schema version, model version, Evals suite and result, Automate versions, source bindings. This is the release unit.
```

---

## B10 — Surface: Workshop Decision Loop

**Mode:** Workshop.

```text
Build the accepted Gate 7 surface: one Workshop module.

- Persistent three-pane layout: Now/context rail on the left, interactive Map operating picture in the center, embedded AIP decision/execution panel on the right.
- Now view from the projection dataset, built to the approved Now-view contract: fixed row schema, four exhaustive inclusion rules, ordering by owner then route then consequential time ascending. There is NO cross-line priority score. A stale row persists showing INDETERMINATE rather than vanishing.
- Under Now, keep five responsibility lines continuously visible: Land, Funding, Applications, Field Work and Payments. Each shows bounded change, owner, clock and next decision/handoff for the selected population. Selecting a line changes the relevant Map layers, Q1–Q6 scene and AIP context without resetting member/land/date/route. They are not tabs or lifecycle stages.
- One decision scene that changes with the question while preserving context.
- Persistent context contract: selected object set, member/land/route, named Action, consequential date, proposal id, premise fingerprint, health state. Every widget and the chatbot read the same contract.
- Treat that context as one versioned logical envelope with a generation number. Bind exact Action/Function target, Proposal and fingerprint inputs from application state rather than reconstructing them from chat prose.
- Embedded AIP Chatbot widget, published, approval disabled.
- Native Map widget as the persistent central operating picture: administrative and temporal Official Areas, monitoring/Plant layers, cooperative member Parcels grouped by Holding, and affected/unaffected work. Full cadastral data stays queryable/on-demand rather than simultaneously rendered. Layer visibility, clustering and zoom thresholds preserve legibility. A shape selection supplies candidate targets only; it never establishes authority.
- Use four semantic Map modes inside that persistent pane: change footprint, authority context, dispatch scope and outcome footprint. Modes drive native layer visibility, locking and zoom; they never change domain state.
- Configured Object Views in a drawer for biography and evidence.
- Evidence jumps bind immutable document identity/hash to exact page/search location in the native viewer; no generic Evidence or annotation object.
- The Workshop PDF Viewer reads `GoverningInstrument.primaryDocument`. A selected citation/object sets the exact Instrument, MediaReference, page and optional search text in shared application state; the viewer opens and highlights without changing domain state.
- Receipt strip, persistent and retrievable independently of the chat stream.
- Native table/chart/metric views for capacity comparison. Use Scenario-aware widgets only if B4's bounded probe adopted Scenarios. Add a custom widget only for a measured inability to show the complete plan in one view; more than one custom widget triggers OSDK React reconsideration.

- During consequential command composition, pause presentation auto-refresh and capture the context generation/fingerprint. The Action reloads and revalidates current server state; refresh resumes after receipt/refusal. The display pause never freezes truth or bypasses the kernel.
- Watch only Now projections, selected semantic objects and the explicit linked dependencies for the active scene; do not refresh the full graph by default.

The Gate 7 anti-pattern list is the style guide: no widget salad, no map-as-truth, no object-view-as-home, no approval theatre, no generic queue.
```

---

## B11 — Freeze, merge, demo

**Mode:** Governance.

```text
Freeze and prove.

- Rerun the exact inventories: 25 domain types, 4 log types, 7 FK / 19 M:M / 8 object-backed, 4 kernels, 4 read Functions, 4 Actions.
- Rerun the frozen Evals suite: zero hard-gate failures.
- Verify the compatibility manifest resolves every RID and version.
- Pin the Governing Instrument Media Set RID, view RID, promoted item hashes and Instrument→MediaReference bindings in the compatibility manifest.
- Snapshot all data. No live layer is queried during recording.
- Merge the branch to main after review.
- Run the demo trajectories from the approved script v0, in beat order, against the frozen state.

Never-cut list: the persistent Now/five-responsibility + Map + AIP operating picture; one full Action trajectory ending in a durable receipt; one evidence-basis click. Capacity and INDETERMINATE/refusal remain product features and Eval coverage, not hero beats.

Descope ladder, in order, invoked only at a slipped step: narrate Automate; screenshot Evals; degrade the capacity mechanism per B4's pre-decided fallback; pre-load the ingestion outcome with the envelope shown.
```

---

## Acceptance ladder

| Step | Demonstrable when complete |
|---|---|
| B1 | ✅ Real data acquired and conservation-verified — data path superseded by B1.1 |
| B1.1 | Data Lineage shows source→raw→curated; incomplete syncs cannot curate; current-source conservation and one-to-one identity gates pass; real observed conflicts quarantine; B1 evidence differences are adjudicated rather than forced |
| B2 | One parcel traverses to zone, plant, instrument, intervention |
| B3 | **Change → affected/unaffected → named-action readiness → dispatch → receipt → replay**; refusal/INDETERMINATE are retained as product behavior and Eval cases |
| B4 | Two alternatives → immutable proposal → atomic commit → stale proposal refuses |
| B5 | Exact inventories verify; all four Actions and four Functions live |
| B6 | Real act ingests once; replay produces no duplicate; cash stays INDETERMINATE |
| B7 | Conversational command executes; ambiguity clarifies; unauthorized refuses |
| B8 | Frozen suite runs in simulation with zero hard-gate failures, failures retained |
| B9 | Health failure flips a live answer to INDETERMINATE and refuses its Action |
| B10 | The manager completes a full trajectory in the Workshop surface |
| B11 | Demo runs against frozen state |

B3 is the milestone that matters most. Everything before it is scaffolding; everything after it is breadth, depth or presentation.

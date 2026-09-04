# Puglia olive–Xylella data and field universe

**As of:** 24 August 2026  
**Scope:** the complete decision-relevant observation universe for a Puglia cooperative/OP manager, not a demo geography and not only public web files.  
**Operating boundary:** land, legal duty, programme, application, field execution, evidence, payment and bounded establishment/early cure. Mills and markets enter only where they constrain a recovery decision inside that boundary.  
**Method:** independent actor-, process-, resource-, catalog- and value-chain search preceded reading the local `DATA_UNIVERSE_*` and current recon. Those files were then used as context and contradiction checks, not as a search boundary. No Foundry write or git operation occurred.

## Bottom line

The public universe is much larger than a monitoring-workbook-plus-cadastre design. It contains current and historical cadastral geometry, farm-file and area-monitoring systems, legal-area services, plant and vector observations, monumental-tree registers, soil and water layers, PPTR and Natura 2000 constraints, official acts, programme chains, procurement and payment publications, regulated provider/plant-material registers, quality-scheme traceability, mill and price infrastructure, and finite scientific catalogs. The decisive remaining gaps are not generic “missing data.” They sit with named custodians: member/CAA farm files, producer and cooperative operating records, ARIF execution and indemnity ledgers, nursery lot and capacity records, contractor availability, lawful water rights and delivery, field acceptance, bank settlement, and establishment observations.

The acquisition strategy is therefore a **regional public spine plus cooperative-held current state plus targeted custodian requests plus created observation layers**. Public data establishes identity, jurisdiction, legal publication, programme state, environmental context and many official outcomes. It does not establish current tenure, member election, accepted mandate, live supplier capacity, work performed, authority acceptance, cash receipt or biological establishment.

Three model diagnostics are material:

1. The accepted operator graph absorbs most discoveries through existing Parties, Holdings, Parcels, Areas, Instruments, Proceedings, Interventions, Pursuits, Capacity Commitments and typed histories.
2. **Plant Trade Unit / Lot must be reconsidered as a visible core object, not only a conditional extension.** Plant passports, registered variety, certification category, supplier, batch quantity, allocation, custody, substitution, recall, warranty and establishment failure attach to a lot and change independently of both the supplier and Intervention. The real workflow preserves this identity.
3. If CORDON records or changes lot allocation, it also needs an **Allocate or Substitute Plant Material** Action. `Assess Named-Action Readiness` can test material readiness, but it cannot authoritatively allocate or substitute a regulated lot. Cultivar remains a real reference noun and should be an object when eligibility, variety registration, IP/licensing or cross-lot comparison cannot be represented safely as a controlled identifier.

---

# Class 3 — unsupported hypotheses and model-memory leads

These came first. They shaped retrieval but are not findings.

1. A current olive-grove map might exist in the new AGEA SIPA/AMS even though public regional land use stops at older vintages.
2. A complete Puglia nursery list and current production capacity might be derivable from RUOP, plant-passport inspection requests or procurement.
3. SIAN oil registers might expose mill-level throughput, stock and delivery history to a cooperative.
4. Water availability might be inferable from irrigation-district maps, wells, concessions, delivery ledgers and groundwater-quality monitoring.
5. A field-work chain might publish work orders, crew dispatch, removal, transport/destruction, inspection, acceptance and indemnity as separate records.
6. Cooperative membership, mandate, governance, financial standing and current capacity might be recoverable from public registers.
7. Remote sensing might identify individual infected trees before official diagnosis.
8. A public claims ledger might prove bank settlement.
9. Scientific repositories might hold ready-to-use Puglia field labels, vector observations, resistant-cultivar outcomes and remote-sensing models.
10. Mills and prices might determine whether a replanted orchard is biologically useful but economically stranded.

Several hypotheses were partly confirmed, several remain custodian acquisitions, and three were rejected: free Sentinel-2 does not support tree-level pre-diagnostic claims; public liquidation acts do not prove bank receipt; and company/provider registers do not prove live delivery capacity.

---

# Class 2 — decision inferences from the discovered universe

## 1. Universe architecture

The universe should be acquired in six layers. Each layer has a different truth role.

| Layer | Job | Examples | What it must never be mistaken for |
|---|---|---|---|
| Identity spine | Preserve the same land, party, programme, proceeding, plant or lot across changes | cadastral reference, CUAA/farm file, tax/company ID, sample ID, official act ID, CUP/CIG, passport/lot ID | current condition or legal consequence |
| Authority and official state | Establish controlling publication, geography, duty, concession, instruction or acceptance | EU/national/regional acts, BURP, official area services, authority verbali | physical performance, cash or establishment |
| Operational transaction | Record what a party elected, allocated, dispatched, performed, accepted, claimed or received | mandates, purchase orders, work orders, delivery notes, field logs, claims, bank statements | public eligibility or official diagnosis |
| Observation | Record what was observed at a time, place, method and target | official samples, vector catches, photos, lab tests, soil tests, canopy measures, establishment inspections | immutable identity, causal disease diagnosis or legal status |
| Environmental and capacity context | Test whether an Intervention is feasible and robust | soil, weather, water, nursery stock, crew schedule, mill window | proof the resource is reserved |
| Derived decision support | Compute overlays, change, risk and remaining exposure | parcel–zone intersection, mortality change, drought stress, route readiness, feasible portfolio | source fact or authority decision |

The central anti-collapse rule is temporal and semantic: **identity is not observation; current state is not historical state; an order is not an outcome; performed work is not accepted work; accepted installation is not establishment; liquidation is not cash; survival is not cure.**

## 2. Land identity, use and standing

### Material data families

1. **Current cadastral geometry.** Agenzia delle Entrate INSPIRE WFS is the current parcel-geometry authority available without ownership. SIT Puglia Sigmater is a useful September 2021 snapshot and point-to-parcel service. Both should be retained by vintage because parcel splits, merges and identifiers change.
2. **Farm-file land and current operation.** The AGEA/SIAN fascicolo aziendale carries the business identity, territorial consistency, title of occupation, cultivation plan, associations and proceedings. The 2024 SIPA changes the reference parcel from cadastre-tied geometry to a physical-block model. Current cooperative/member truth must therefore come from authorized member or CAA extracts, not from public cadastre alone.
3. **Land-use history.** Regional UDS 2006/2011, OPENIACS/GSAA 2018, SIPA/CNDS/AMS 2023 onward, Sentinel/orthophoto-derived orchard masks, DOP certified surfaces, and member cultivation plans are different vintages and definitions. Keep them separate.
4. **Standing and access.** Ownership, tenancy, usufruct, commodatum, possession, right of way, member authority, cooperative mandate, mortgage/encumbrance and physical access are separate facts. Cadastre supplies none of them reliably.
5. **Public and special land.** State/municipal demesne, roadsides, canals, railway land, utility corridors, usi civici, fire-restricted parcels and public green areas create different duty holders and access routes.
6. **Land constraints.** PPTR, hydrogeological risk, Natura 2000, VIncA route, parks, archaeological constraints, fire history, nitrates and salinity can change design, permit, timing or admissible water use.

### Acquisition path

- Bulk-enumerate current AdE WFS by bounded tiles and validate every `NATIONALCADASTRALREFERENCE` against the cooperative's entered comune/foglio/particella.
- Preserve SIT Puglia 2021 parcels as a dated reconciliation source, never as current title.
- Obtain member-authorized fascicolo/PCG/SIPA extracts through the CAA or beneficiary login. Harvest per campaign, because the 2024 SIPA is not retroactive to earlier proceedings.
- Enumerate UDS resources and current AMS/SIPA documentation; request machine exports from AGEA/CAA only for the cooperative population.
- Request municipal property, usi civici and public-land extracts where the manager actually carries a public-land Intervention.
- Commission survey only when parcel boundary/access cannot be resolved from authority records.

### Join and identity risks

- Cadastral parcel and SIPA reference parcel are not the same grain.
- A parcel reference can change after split, merge, municipality-code correction or annex/sviluppo handling.
- `COMUNE/SEZIONE/FOGLIO/ALLEGATO/SVILUPPO/NUMERO` must be canonicalized as components; a concatenated string is not safe unless all null/sentinel rules are explicit.
- A Holding can operate several parcels and several Holdings can have distinct interests in one parcel.
- Owner name is not a key. Owner identities in public acts are personal data and must not be used to build a public profile.
- UDS, GSAA, DOP surfaces and remote-sensing orchard masks establish land-use observations under different definitions, not current legal operation.

## 3. Individual trees and observations across vintages

### Material data families

1. **Official plant-monitoring campaigns.** Preserve every campaign workbook and current ArcGIS sample feed, including negative rows, coordinates, host/cultivar, symptoms, result, subspecies where available, team, protocol and confirmation document.
2. **Plant identity.** Create an Individual Plant only when an authority, field process, monumental-tree register or validated reproducible inventory preserves the same tree. A sample point or crown detection alone does not create a Plant.
3. **Monumental trees.** The regional register and provisional additions carry stable registry attributes and parcel references. Monumental status, provisional status, grafting, derogation, order and final disposition are separate facts.
4. **Vector observations.** Preserve site, round, substrate/crop, sampling method, unit count, species count, life stage and later diagnostic result. Adult abundance is not infected-vector status.
5. **Nursery and movement surveillance.** Annual official inspection requests, plant-passport status and tests of specified plants create lot/provider observations, not field-tree observations.
6. **Created observations.** Geotagged photographs, crown polygons, orthophoto canopy state, stump/removal evidence, planting rows, missing-tree detections and establishment surveys are permissible observation layers when method and uncertainty remain attached.

### Minimum observation envelope

Every observation needs: source observation ID; target identity/grain; observed time; publication/as-of time; location and CRS; observer/organization; method/protocol; sample medium; measured attributes and units; detection limit; result; uncertainty/quality flag; source version; supersession/retest link; media/evidence references; and license/access class.

### Identity and survivorship hazards

- Campaign period is not calendar year.
- The same tree may receive several sample IDs; the public feed currently lacks an explicit `RESAMPLE_OF` link.
- Positive trees are removed by law in many routes. Their disappearance is not biological recovery.
- A new crown at a prior coordinate can be regrowth, replacement, coordinate error or a different tree.
- Monumental registry points and sample coordinates can refer to the same tree only after parcel, proximity and registry evidence agree.
- Testing intensity is co-equal with positivity. No tests is unknown, not low risk.
- Visual symptoms are a signal; official assay result is ground for official infection status.

## 4. Epidemic and administrative geography

### Required geography stack

- EU Annex III and other legal territorial lists.
- Region, province, Comune and sub-municipal administrative areas.
- Pauca, fastidiosa and multiplex infected/buffer/containment/other official areas by version.
- Each outbreak/institution act separately from the current merged geometry label.
- 50 m infected rings, 2.5 km buffers, 2 km containment surveillance band and any other measure-specific geometry.
- Natura 2000, parks, PPTR, PAI, nitrates, salinity, irrigation districts, DOP/IGP areas, public/demesne land and municipal jurisdiction.

Geometry is observation/representation. Legal applicability requires the controlling Instrument, subject, host, date and any parcel-specific outcome. The Valenzano act versus “Modugno”-labelled live geometry proves why the area instance and service-layer label cannot share an identifier.

### Finite catalogs to enumerate

- SIT Puglia ArcGIS root: all 11 folders and all 194 services, then each service's layer/table catalog.
- Current and historical Xylella area services for all three subspecies.
- Current, prior and print monitoring services.
- PPTR current and previous services; `VincoliTotale`; Natura 2000 CKAN resource; PAI/PTA and irrigation services.
- BURP issues and act citation edges.
- EUR-Lex consolidated Regulation 2020/1201 and every amendment plus Annex III versions.
- National and regional emergency/action-plan lineage.

## 5. Legal publications, programmes and proceedings

### Legal/publication families

- EUR-Lex consolidated acts and amendments.
- national plant-protection portal, Gazzetta Ufficiale and MASAF decrees.
- BURP permanent PDFs and issue catalog.
- regional administration-transparency and thematic programme registers.
- ARIF acts and procurement/transparency.
- Comune albo/notices/ordinances, used for municipality-issued acts and publication evidence, not as substitutes for regional law.
- Giustizia Amministrativa/OpenGA, TAR and Consiglio di Stato judgments, stays and appeal state.
- Wayback captures of retired maps and publication pages.

### Programme and proceeding universe

The complete route ledger must include open, imminent, closed-but-executing, exhausted/reallocated and event-triggered measures. It must preserve the instrument chain from legal basis to call, amendment, ranking, concession, variant, claim rules, instruction, liquidation, payment order, audit, revocation and recovery. Current identified families include Article 6, SRD01.01A/B/.05, SRD13, SRG01/02/03, SRE01, SRD01.06, SRD05/15, OP/AOP operational programmes, ARIF DGR 994/903 indemnities, the announced MASAF €30m route, municipal plant allocations, ISMEA finance/land/guarantee routes, district/supply-chain contracts, nursery and mill compensation, and quality schemes.

### Proceeding-chain anti-collapse

Keep separate:

- eligible / ineligible / indeterminate;
- member participation election;
- cooperative mandate acceptance;
- cooperative pursuit decision;
- filing version and formal release;
- ranking and technical-administrative admission;
- concession and variant;
- claim requested, instructed, admitted and rejected;
- granted, liquidated, ordered, bank-paid;
- audited, revoked, recovered;
- creditor and recovery debtor.

A programme register proves the programme state. It does not prove a member outcome. A liquidation act proves authorization, not bank settlement.

## 6. Cooperative, OP and private operating facts

### Publicly discoverable

- MIMIT cooperative existence/category.
- Registro Imprese identity, legal form, officers and filed accounts; cooperative member counts may appear in paid bilanci/notes.
- MASAF recognized OP/AOP finite list and annual programme approvals.
- DOP operator registers, certified olive surfaces and control-plan records.
- public procurement awards and public programme participation.
- published accounts, liens/insolvency proceedings and public grants where lawfully available.

### Direct acquisition required

- current member roster and membership effective dates;
- member–Holding mapping and contact/consent preferences;
- governance bodies, delegations and exact decision rights;
- mandates, adhesion elections and fallback;
- cooperative-controlled crews, equipment, nursery relationships, mill slots, cash and credit limits;
- internal priority/fairness policy and protected commitments;
- member claims, debts, bank receipts, private insurance and recoveries.

A public member count is not a member roster. A roster is not current member authority. A cooperative's advertised service is not live capacity. Private data should be imported under member/cooperative authority and minimized to the decisions it supports.

## 7. Plant material, providers and capacity

### Source families

1. **RUOP.** Enumerate every Puglia operator, registration status, activity and passport authorization by current decree/annex. Older lists remain vintages, not current truth.
2. **Official Xylella inspection/testing.** Annual nursery requests and official laboratory contracts establish provider obligations and designated testing channels.
3. **National variety and certification systems.** Registered variety, CAC minimum, EU certification and Qualità Vivaistica Italia are distinct claims. Certification supports genetic/health traceability; it does not prove Xylella-free destination compliance without the applicable passport/inspection.
4. **Plant passports and delivery documents.** Passport, supplier, lot/batch, cultivar, category, quantity, production site, dispatch, receipt, quarantine/inspection, substitution and return form the real material chain.
5. **Supplier capacity.** Current inventory, production pipeline, reservation, lead time, minimum order, delivery radius, price, warranty and replacement terms are private/volatile facts. Public product pages are only leads.
6. **Laboratory capacity.** Designation, ISO/IEC 17025 scope, method, contracted volume, per-lab allocation, queue and turnaround are separate. Procurement gives envelope; only operational ledgers give live throughput.
7. **Contractor capacity.** ANAC/BDNCP, EmPULIA, ARIF awards, regional forestry-enterprise registers and private quote books identify candidate providers. Actual availability, equipment, insurance, training and reservation require direct confirmation.

### Acquisition cadence

- Harvest RUOP and designated-laboratory annexes on every new act.
- Request provider inventory and production forecast by cultivar/lot monthly during planning and weekly after reservation.
- Capture passport and delivery-note evidence at lot receipt.
- Reconcile ordered, reserved, dispatched, received, rejected, planted, remaining, returned and replacement quantities.
- Obtain per-lab queue/turnaround through contract reporting or accesso civico if public monitoring depends on it.

### Join risks

- RUOP operator code, VAT/tax ID, supplier account and company name are different identifiers.
- Cultivar trademark/marketing name and registered variety identity can differ.
- One commercial lot can be split across Interventions; one Intervention can receive several lots and substitutions.
- A reservation is not inventory; a purchase order is not dispatch; dispatch is not receipt; receipt is not acceptance; planting is not establishment.

## 8. Water, soil and weather

### Public spine

- `CartaPedologica` publishes six territorial lots and 52 layers, including profiles, auger observations and soil units.
- `DistrettiIrrigui` includes irrigation districts, nitrate-vulnerable zones, water-source and hydrographic constraint layers.
- `VincoliTotale` includes salinity-vulnerable and water-protection areas.
- SIGRIAN and DANIA describe irrigation infrastructure, entities, projects and investment state.
- ARPA Puglia groundwater reports and monitoring should be harvested at station/body/time/parameter grain.
- ARIF Agrometeo provides current station observations plus daily and weekly bulletin archives.
- ERA5/AgERA5, SPEI and ESA soil moisture provide reproducible regional fallback controls when station history is not downloadable.

### Direct and commissioned facts

- lawful water source and entitlement;
- well/turnout identifier, permitted abstraction, delivery calendar and current restriction;
- meter/delivery history and water price;
- pump, power and distribution capacity;
- laboratory water analysis at the source actually used;
- parcel soil tests: texture, pH, EC/salinity, organic matter, active lime, nutrients, infiltration/drainage and sampling depth/method;
- irrigation design, storage and drought contingency.

Public maps support screening. They do not prove that a member has a lawful connection, a working pump, water in the required week or acceptable source quality. Water rights are represented by Governing Instruments and contextual Party/Parcel standing; shared delivery capacity can use Capacity Commitments. Add a separate resource object only if the operator manages the same independently identified well/turnout across many Interventions and must reconcile meter/quality/maintenance history independently.

## 9. Field execution, evidence and acceptance

### Required records

- exact Intervention scope and design revision;
- access/consent and precondition evidence;
- permits, VIncA and authority conditions;
- work order, executor, planned clock and stop conditions;
- crew/equipment/material reservations;
- pre-work photos and target inventory;
- daily dispatch, attendance, machine/chemical/material logs;
- tree/parcel-level performed scope, exceptions and deviation reasons;
- chain of custody for removed material/wood where required;
- geotagged media with capture time, device, operator and hash;
- contractor completion assertion;
- inspector visit and official verbale;
- legal acceptance, grant acceptance and contractual acceptance as separate outcomes;
- defects, rework, warranty, replacement and cure.

The strongest evidence is not “a photo.” It is a linked package whose identity, time, scope, actor and method can be checked against the work order and authority acceptance. Media must retain original bytes/hash, metadata, capture actor and any privacy redaction. Aerial or satellite evidence can corroborate change but cannot certify legal compliance unless the authority accepts that method.

## 10. Claims, orders, cash and recovery

### Source families

- member/CAA SIAN claim and EIP records;
- ARIF instruction and indemnity portal records;
- regional concession, liquidation and payment acts;
- SIAN CAP/State-aid transparency with rolling retention;
- OpenCoesione project and payment tables;
- public treasury/mandate data where exposed;
- beneficiary bank statements and returns;
- guarantee, DURC, antimafia and debt-offset records;
- audit, revocation, recovery and litigation acts;
- insurance policy/claim/indemnity only when the covered peril and event are verified.

### Financial identity and joins

- Use official Proceeding ID/EIP/claim ID as the member-right spine.
- Use CUP for public project identity and CIG for procurement, never interchange them.
- A batch liquidation can contain many claims and one claim can be affected by several instruction/outcome acts.
- Bank transaction identity must survive partials, aggregated credits, returns and reversals.
- Amount states and creditor identity remain independent. The cooperative is not automatically the creditor for a member concession.
- SIAN transparency has a rolling retention window. Harvest yearly and purpose-limit personal data.

### Acceptance boundary

Public acts can often reconstruct requested → instructed → conceded → liquidated/ordered. Only bank evidence proves received cash. Audit/recovery remains open after payment and must be represented as remaining exposure, not as a reversal of historical receipt.

## 11. Establishment, aftercare, replacement and cure

### Observation programme

- planting acceptance at installation;
- lot and Plant identity at planting where feasible;
- baseline dimensions/condition and photo;
- watering and aftercare visits;
- survival, vigor, symptoms, damage cause and missing/failed status at defined intervals;
- laboratory result where disease is suspected;
- warranty claim, supplier/contractor responsibility and replacement authorization;
- replacement lot and date;
- cure/rework performed and accepted;
- bounded establishment endpoint.

A pragmatic cadence is installation, first irrigation confirmation, 30–45 days, end of first dry season, first dormancy/spring restart and any grant/warranty inspection. The exact schedule belongs to the Intervention design and contract, not a global rule.

Biological establishment is not productive maturity. Yield optimization, full bearing and lifetime orchard management remain outside Wedge 1. Early survival and required replacement remain inside because they determine whether recovery actually landed.

## 12. Mills and markets: include only binding constraints

### Decision-capable data

- SIAN oil portal records mandatory olive/oil loads and unloads for mills, packers, traders, pomace plants and refineries.
- DOP control registers link certified operators, origin parcel, harvest date/time, SIAN milling entry, non-conformity and certification.
- ISMEA and Camera di Commercio price series supply regional product/market reference values.
- mill identity, service area, intake calendar, daily throughput, storage, cultivar segregation, quality protocol, price/fee, contract and reserved slot are direct operational facts.
- cooperative offtake, processing and storage constraints can change the expected realized value of an Intervention portfolio.

### Boundary

Do not expand Wedge 1 into general marketing. Mill and market data enters only when it changes cultivar/design, harvest/logistics feasibility, cooperative capacity allocation, financing or expected realized loss reduction. Public “active mill” maps and weekly prices do not prove a future processing slot or a member's realized price.

## 13. Scientific and remote-sensing data

### Finite catalogs and source families

- EFSA Xylella host database releases and supporting reports.
- EPPO taxonomy, distribution and diagnostic protocol.
- BeXyl public deliverable catalog, CORDIS result catalog and OpenAIRE-linked datasets/software.
- Zenodo Xylella and EFSA Knowledge Junction communities; recursively enumerate records, versions, files, licenses and related identifiers.
- publications and supplements from CNR-IPSP, UniBari, CIHEAM, CREA and partner projects.
- official plant/vector campaigns and action-plan survey designs.
- Copernicus Sentinel-1/2, Landsat, ERA5/AgERA5, ESA WorldCover/soil moisture, Meta/WRI canopy height, regional orthophotos/ImageServers and available DSM/DTM/LiDAR.
- commissioned UAV RGB/multispectral/thermal/hyperspectral, only with flight/legal authority and a ground-truth design.

### Decision products that can pay

1. campaign effort-versus-plan and spatial coverage;
2. current positive/sample and vector-round change detection;
3. parcel-level canopy loss/removal and replant establishment change from orthophotos;
4. drought/water-stress context to prevent false disease attribution and target aftercare;
5. tree/row inventory from high-resolution imagery where validated;
6. terrain, drainage, soil and salinity screening for design;
7. front/surveillance optimization using explicit observation-process models;
8. cultivar/establishment cohort comparisons with time-at-risk and exposure controls;
9. likely missing-work or failed-establishment review queues, always requiring human/authority confirmation.

### Red lines

- No individual-tree pre-diagnostic claim from free Sentinel-2.
- No prevalence estimate from targeted monitoring without a survey-design estimator.
- No disease attribution from canopy change alone.
- No inferred Plant identity from one detection.
- No cultivar ranking without an outcome and exposure design that passes a known-resistance control.
- Research outputs do not become operational ground truth merely because they are open access.

## 14. Finite catalogs to enumerate to closure

| Catalog | Closure unit | Expected acquisition | Completeness test |
|---|---|---|---|
| SIT Puglia ArcGIS | 11 folders → 194 services → every layer/table | REST JSON, paged queries | root count, per-folder count, per-layer count and harvested count reconcile |
| Puglia CKAN | package list/search plus every resource | CKAN API/direct downloads | package count and resource URLs reconcile; empty/stale URLs logged |
| BURP | issue index, PDFs and citation edges | portal issue crawl + stable PDFs | issue/date span, act numbers and successor recitals reconcile |
| EUR-Lex | base regulation, consolidated versions, amendments, Annex versions | CELEX/EUR-Lex | amendment lineage complete to as-of date |
| regional programme registers | every measure page and act list | HTML/PDF | newest act and all numbered ranking/concession/payment series reconciled |
| ARIF/EmPULIA/BDNCP | tenders, awards, performance and transparency | bulk/API/portal | station/issuer/CIG/date facets reconcile |
| RUOP | every current Puglia registered operator | latest official annex + accesso civico | latest act count and parsed unique operator codes reconcile |
| designated laboratories/Accredia | designation × current accreditation scope | acts + Accredia | every designated lab has method/scope/as-of result |
| MASAF OP/AOP | every recognized organization and annual programme | XLS/PDF | national list count and Puglia sector subset reconcile |
| DOP control registers | operators, certified surfaces, control documents by vintage | CCIAA/consortium files | published operator/surface totals reconcile |
| SIAN transparency | yearly beneficiary/payment window | UI backend/browser capture | year/measure totals and extract counts reconcile; annual harvest before expiry |
| OpenCoesione | projects, subjects, localizations, payments | bulk ZIP/CSV | relational key counts and project/payment totals reconcile |
| EFSA host DB | release, files, sheets, categories | Zenodo API/files | version/file checksums and row counts recorded |
| BeXyl/CORDIS/OpenAIRE | deliverables, datasets, software, publications | project catalog/API | catalog counts and file URLs reconcile |
| official monitoring | campaign workbook, current/prior services, vector rounds | downloads/ArcGIS/PDF | campaign/round control totals, duplicate IDs and method schema reconcile |
| PPTR/Natura/soil/water | current and prior layers | ArcGIS/CKAN/agency reports | service layer count and feature counts reconcile |

Query saturation is not catalog closure. Closure requires a finite publisher structure and count reconciliation.

## 15. Acquisition and request programme

### Immediate public syncs

1. ArcGIS root/service/layer harvester with source-version, count and schema manifests.
2. AdE cadastral WFS tile harvest plus SIT 2021 reconciliation.
3. all monitoring campaign workbooks, current/prior plant feeds and each vector bulletin round.
4. BURP and regional measure-page act/citation graph.
5. PPTR, Natura 2000, soil, irrigation, nitrates, salinity, DOP and monumental-tree layers.
6. RUOP, laboratory designation, MASAF OP/AOP, DOP operator and plant-certification catalogs.
7. SIAN transparency annual capture and OpenCoesione relational bulk files.
8. EFSA, EPPO, BeXyl, CORDIS, Zenodo/OpenAIRE catalog manifests.

### Cooperative/CAA direct acquisitions

- member roster, Holding and fascicolo/PCG/SIPA extracts;
- tenure/access/consent and mandate evidence;
- current proceedings, claims, concessions, variants and bank receipts;
- plant material quotes, reservations, lots, passports and delivery notes;
- contractor and technician commitments;
- field work, inspection, defect and aftercare evidence;
- current mill/storage/offtake constraints;
- cooperative governance, capacity and fairness rules.

### Accesso civico / formal request targets

| Holder | Precise requested extract | Decision enabled |
|---|---|---|
| Regione Puglia, Osservatorio Fitosanitario | machine-readable historical area versions; positive→confirmation→prescription links; per-lab allocation/turnaround; current RUOP export | legal-area history, sample/proceeding join, lab bottleneck, supplier qualification |
| ARIF | order/election/execution/verbale matrix; crew throughput; DGR 994/903 claim, instruction, liquidation and payment status; vector raw tables | duty completion, execution capacity, indemnity exposure, vector risk |
| InnovaPuglia/SIT | layer update timestamps, archive snapshots, parcel-resolution method and service terms/license | source currency and reproducible parcel/area joins |
| AGEA/CAA under member authority | fascicolo, PCG/SIPA/AMS result, claim/EIP state, older transparency payments | current land/use, proceeding state and payment history |
| Consorzi di bonifica/irrigation entities | district asset/turnout, member entitlement, delivery/restriction and meter history | lawful water readiness |
| ARPA Puglia | station/body/time parameter tables for groundwater quality, not only PDF reports | water-quality screening and trend |
| municipalities | public/municipal parcel roster; permit/VIncA proceedings; local plant-allocation records; fire cadastre where relevant | public-land duty, permit state, in-kind supply |
| CCIAA/control bodies | current DOP surface/operator machine exports and stable IDs | parcel/operator/value-chain joins |
| labs/providers under contract | queue, turnaround, rejection/retest and capacity reports | observation latency and dispatch planning |

Requests should ask for fields, date range, grain, code lists, update cadence and machine format. They should not ask vaguely for “all Xylella data.”

## 16. Licensing, access and privacy

- Puglia CKAN resources state licenses per package, commonly CC BY 4.0 or IODL 2.0. Record license per resource, not per portal.
- SIT ArcGIS layers are publicly queryable, but many services expose no explicit license. Treat them as public-access/source-attribution with reuse terms unresolved until the publisher confirms.
- AdE cadastral services require their stated INSPIRE/reuse terms; current geometry does not convey ownership rights.
- Copernicus data is open for commercial use under its terms. Research imagery and supplements can have different licenses even when the paper is CC BY.
- EFSA host database v14 is a versioned downloadable data product; retain file checksums and release/version metadata.
- official acts are citable public records, but personal names, parcel links, bank details and joined profiles remain personal data. Public availability does not justify broad republication or enrichment.
- SIAN beneficiary transparency is purpose-limited and time-limited. Harvest only for a legitimate operational purpose and apply retention/access controls.
- Registro Imprese bilanci and some company documents are paid/licensed access; no spend occurred.
- supplier inventory pages are copyrighted, volatile commercial claims and not authoritative capacity records.
- member/CAA, bank, contract, photo and field records require authority, minimization, role-based access and a deletion/retention policy.

## 17. Tempting data classes that add no decision capability

1. **Generic Xylella news and social-media volume.** It changes no parcel, duty, proceeding, capacity or establishment decision.
2. **Citizen vector sightings as a regional risk layer.** Current density is far below official rounds and absence is uninformative. Use only as a lead.
3. **OSM olive polygons as orchard truth.** Coverage is too sparse and uneven.
4. **Global commodity prices without a linked offtake/quality route.** They do not determine a member's realized value.
5. **Static directories of mills or nurseries.** They identify candidates, not capacity, reservation, quality or delivery.
6. **Company marketing claims about resistant cultivars.** They do not establish official variety identity, certification, passport, availability or field outcome.
7. **Research gene-expression tables for routine operator decisions.** They do not change current land, route, dispatch or establishment choices.
8. **More free Sentinel super-resolution for tree-level early diagnosis.** The evidence gate is closed; more of the same sensor does not add capability.
9. **Uncorrected positivity maps.** Without testing effort they misstate risk and can divert capacity.
10. **A single global “case status,” “completion,” “paid” or “recovered” flag.** It destroys independent legal, physical, financial and biological truth.
11. **Document/OCR/source rows as visible domain objects.** They are backstage provenance unless an operator decision acts on the real Instrument/Proceeding/Intervention.
12. **Full productive-maturity/yield telemetry inside Wedge 1.** Useful to a broader orchard-management product, but beyond bounded establishment unless it changes an early replacement/cure decision.
13. **Unverified inferred owner/member linkage from names.** High privacy and false-merge risk; no safe decision gain.
14. **Catalog counts presented as coverage.** Counts are navigation aids, not proof the decision population is complete.

## 18. Diagnostic mapping to accepted fact owners

| Discovery | Accepted owner that absorbs it | Diagnostic |
|---|---|---|
| cadastre, SIPA, land-use vintages, geometry | Cadastral Parcel; Agricultural Holding; Holding–Parcel and Party–Parcel context | absorbed; preserve grain/vintage and do not infer standing from geometry |
| membership, mandate, representation, access | Operator Party context; Governing Instrument; Cooperative Pursuit | absorbed |
| legal areas, PPTR, Natura, irrigation/nitrate/salinity zones | Official Area + Governing Instrument applicability | absorbed; environmental map alone has no legal effect |
| official samples, vector rounds, media and lab results | Instrument/Proceeding/Intervention factual histories; conditional Individual Plant | absorbed if observation envelope is retained; Sample becomes a noun only if custody/retest is an operator decision |
| programmes, claims, concessions, liquidations, cash, recovery | Public Programme; Public Proceeding; Proceeding/Cash occurrences | absorbed |
| field work, inspection, acceptance, defect, establishment, replacement/cure | Intervention and Intervention history; conditional Plant scope | absorbed |
| provider and crew reservations | Intervention Capacity Commitment | absorbed for capacity; provider remains Party |
| water entitlement and delivery capacity | Governing Instrument + Parcel standing + Capacity Commitment | absorbed unless one physical water asset needs independent lifecycle management |
| mills/offtake constraints | Party, Intervention, Capacity Commitment and portfolio inputs | absorbed; no mill noun required inside Wedge 1 today |
| certified variety reference | Cultivar accepted Gate-3 noun but absent from visible Gate-5 core | **selective challenge:** object required when cross-lot identity, eligibility or licensing is active; otherwise controlled reference on lot |
| plant passport, lot allocation, custody, substitution, warranty and recall | Gate-3 Plant Trade Unit/Lot and Gate-4 Plant Material Allocation/Custody were accepted but omitted from initial core | **real missing noun/relationship:** reopen Plant Material Lot and its allocation/custody to Intervention |
| manager allocation/substitution of a lot | no current manager-owned Action | **real missing Action:** Allocate or Substitute Plant Material, with authority, lot validity, quantity conservation, affected Interventions and fallback |
| material reconciliation/readiness | Assess Named-Action Readiness and Determine Remaining Exposure | Function coverage exists; no new read-only Function required initially |
| source change and stale/conflicting facts | Determine Affected Decisions | absorbed; source mechanics remain backstage |

### Model verdict

The accepted model absorbs the regional public spine and almost all private operational facts without adding generic Evidence, Resource, Case, Status or Market objects. The material exception is regulated plant material. Lot identity is preserved by real suppliers, passports, delivery and warranty processes; it changes independently and can be split, substituted, returned or recalled. Deleting it makes dispatch and establishment unsafe. This passes the Gate-3 noun test and the Gate-4 fact-bearing relationship test. Reopen only that seam. Do not use the data-universe expansion to revive a general-purpose normalized ontology.

---

# Class 1 — fetched facts, recomputed controls and verbatim evidence

This section is last by design. Each item states the fetched URL, the fact used and a verbatim excerpt. Headline counts are recomputed from live machine responses where possible.

## A. Recomputed catalog and layer controls

1. **SIT Puglia ArcGIS root and recursive service count.** Live root returned 11 folders. A fresh recursive enumeration counted **194 services**: Background 7, BaseMaps 20, Editing 16, Geoprocessing 2, Network 2, Operationals 61, Operationals2 54, Operationals3 8, Print 2, ServicesArcIMS 16 and Utilities 6. The type count was 155 MapServers, 20 ImageServers, 8 FeatureServers and 11 other service types.  
   URL: <https://webapps.sit.puglia.it/arcgis/rest/services?f=pjson>  
   Verbatim: `"folders": [ "Background", "BaseMaps", "Editing", "Geoprocessing", "Network", "Operationals", "Operationals2", "Operationals3", "Print", "ServicesArcIMS", "Utilities" ]`.  
   **Recomputation method:** fetched each folder's `?f=pjson`, counted each `services[]` entry once, then grouped by folder and type. This updates the older local estimate of approximately 170 services.

2. **Operationals3 finite service list.**  
   URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals3?f=pjson>  
   Verbatim: `"name": "Operationals3/CartaPedologica"` and `"name": "Operationals3/AreeProduzioneDOPIGPAgroalimentari"`. Eight services were returned.

3. **Soil catalog.** A fresh service-document count returned **52 layers** and max record count 1,000.  
   URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals3/CartaPedologica/MapServer?f=pjson>  
   Verbatim: `"name": "Lotto 1 - Salento"`, `"name": "L1 - Profili"`, `"name": "L1 - Trivellate"`, `"name": "L1 - Unita\` dei suoli"`, and `"capabilities": "Map,Query,Data"`. The service also lists Brindisino, Ionica, Murge, Saline and Appennino lots.

4. **Irrigation/environment catalog.**  
   URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/DistrettiIrrigui/MapServer?f=pjson>  
   Verbatim: `"name": "Distretti Irrigui"`, `"name": "ZVN 2021 - Zone Vulnerabili da Nitrati"`, and `"name": "Opere di derivazione di acque sotterranee per consumo umano - DPGR 575/2023"`; capabilities are `Map,Query,Data`.

5. **Constraint catalog.** A fresh count returned **90 layers** in `VincoliTotale`.  
   URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/VincoliTotale/MapServer?f=pjson>  
   Verbatim: `"name": "Zone gravate da usi civici validate-PPTR"`, `"name": "Aree vulnerabili da contaminazione salina-PTA"`, and `"name": "Aree di tutela quali-quantitativa-PTA"`.

6. **PPTR current and prior material.** A fresh count returned **821 service layers**, including current and historical groups; this is a catalog count, not 821 unique legal constraints.  
   URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/PPTR_APPROVATO/MapServer?f=pjson>  
   Verbatim: `"name": "PPTR aggiornato alla DGR 328/2026"`, `"name": "Vincolo idrogeologico"`, `"name": "Zone gravate da usi civici validate"`, and `"capabilities": "Map,Query,Data"`.

7. **Natura 2000 geometry and cadence.**  
   URL: <https://dati.puglia.it/ckan/dataset/perimetrazione-siti-aree-natura-2000>  
   Verbatim: `Il dataset contiene la perimetrazione e georeferenza delle Aree N2000 con l'individuazione dei Siti ZPS e ZSC presenti in Puglia`; resource `N2000_2023_12_15_Puglia_WGS_1984_UTM_Zone_33N.geojson`; frequency `annuale`.

8. **VIncA instrument and forms catalog.**  
   URL: <https://pugliacon.regione.puglia.it/web/sit-puglia-ambiente/normativa-vinca>  
   Verbatim: `DETERMINAZIONE DIRIGENZIALE 28 aprile 2025, n. 186 ... Adozione modulistica relativa ai diversi livelli del procedimento di valutazione di incidenza ambientale (V.Inc.A.): Screening Specifico e Valutazione Appropriata.`

## B. Water, weather and infrastructure facts

9. **Regional station observations.**  
   URL: <https://www.agrometeopuglia.it/osservazioni/mappa-dati-rilevati>  
   Verbatim: `In mappa potete visualizzare tutti i dati dalle stazioni della rete Agrometeorologica della Regione Puglia.` The page names temperature, precipitation, solar radiation, wind and daily min/mean/max fields.

10. **Bulletin cadence and a historical discontinuity.**  
    URL: <https://www.agrometeopuglia.it/bollettini>  
    Verbatim: `Notiziario Agrometeorologico e Fitosanitario Regionale emesso a cadenza settimanale con uscita il mercoledì` and `Bollettino Meteorologico Regionale emesso tutti i giorni dal lunedì al venerdì ... con validità 5 giorni`. It also states territorial bulletins are no longer available after the transfer of competences.

11. **DANIA infrastructure-project purpose.**  
    URL: <https://www.crea.gov.it/web/politiche-e-bioeconomia/-/bd-dania>  
    Verbatim: `La Banca dati DANIA è finalizzata alla raccolta e condivisione di informazioni relative a progetti infrastrutturali a disposizione degli Enti irrigui` and contains `dati tecnici relativi ai progetti (finanziati e programmati)`.

12. **SIGRIAN/DANIA decision role.**  
    URL: <https://sigrian.crea.gov.it/index.php/2023/06/08/pianetapsrsigriandania/>  
    Verbatim: `I database hanno l’obiettivo di supportare i processi decisionali rispetto alla gestione delle risorse idriche` through information shared among irrigation entities, regions, ministries and river-basin districts.

## C. Plant material and provider facts

13. **National certification semantics.**  
    URL: <https://www.qualitavivaisticaitalia.it/>  
    Verbatim: `la certificazione genetico-sanitaria garantisce la tracciabilità e la rintracciabilità di processo e prodotto` and EU certification `si affianca alle norme minime obbligatorie (cat. CAC)`. The page states that registered/officially described varieties are required and that the scheme applies to `olivo`.

14. **ARIF nursery purpose and lifecycle.**  
    URL: <https://www.arifpuglia.it/attivita/vivai/>  
    Verbatim: ARIF manages nursery activity for `conservazione e diffusione sul territorio regionale della biodiversità`; its production cycle includes collection, growing medium, sowing, transplanting and aftercare; stock is `ceduto a titolo gratuito ad enti pubblici o a titolo oneroso a privati`. The page also states regional nurseries are RUOP-registered.

15. **RUOP current-list lead.**  
    URL fetched by search: <https://foreste.regione.puglia.it/documents/1086071/5186414/DET_953_16_12_2024.pdf/c0921a48-004a-a0b2-503c-d3078908a72a?t=1738568984807>  
    Verbatim search-index fragment: `determinazione ... n. 175 del 29/11/2024 “Aggiornamento dell’elenco degli operatori professionali (O.P.) registrati al Registro Ufficiale degli Operatori Professionali”`. Full PDF extraction failed; the act is a catalog lead, not a recomputed operator count.

16. **ARIF removal, inspection and indemnity roles.**  
    URL: <https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/>  
    Verbatim: `Le operazioni di estirpazione volontaria da parte del proprietario sono controllate da Ispettori/agenti dell’Osservatorio. Le operazioni di estirpazione eseguite da ARIF sono controllate da 2 tecnici fitosanitari ARIF.` The same page states: `L’ARIF è il soggetto responsabile dell’istruttoria e liquidazione degli indennizzi ... previa acquisizione completa dell’allegato B.`

## D. Value-chain facts

17. **SIAN oil-portal transaction duty.**  
    URL fetched but body reduced to cookie text: <https://www.sian.it/portale/servizi/catalogo-servizi/portale-dell-olio-d-oliva-d-m-n-8077-2009-e-n-16059-2013>  
    Verbatim search-index fragment from the same official URL: `registrazione obbligatoria dei carichi e scarichi di olio e di olive entro sei giorni` for `frantoi, confezionatori d’olio, commercianti di olio e di olive, sansifici e raffinerie`. Treat as a discoverable official service; access to operator records remains authenticated.

18. **DOP Terra di Bari operator and parcel traceability.**  
    URL: <https://www.ba.camcom.it/info/d-o-p-terra-di-bari-2173>  
    Verbatim: `estratto operatori iscritti ed attivi al 16/06/2026 D.O.P.` and `BANCA DATI SUPERFICI OLIVETATE`. The 2025/26 declaration requires `Comune/agro, foglio, particelle` and `Data e ora di raccolta delle olive che deve coincidere con quella registrata sul SIAN.`

19. **Official price series with current Puglia observations.**  
    URL: <https://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/648>  
    Verbatim: `Olio d'oliva - Ultime quotazioni alla produzione`; 30 July 2026 rows include Brindisi and Lecce extra virgin at `4,80 €/Kg`, and 27 July includes Bari Terra di Bari DOP and extra virgin at `4,55 €/Kg`. These are market references, not realized cooperative prices.

20. **Camera di Commercio historical list catalog.**  
    URL: <https://www.ba.camcom.it/bari/borsa-merci/listino-olio>  
    Verbatim: the page lists `LISTINO OLIO 2026`, `2025`, `2024`, `2023`, and `2022`, establishing a finite yearly publication family.

## E. Scientific catalog facts

21. **EFSA host database v14.**  
    URL: <https://zenodo.org/records/20539663>  
    Verbatim: `Published June 29, 2026 | Version v14`; EFSA is requested `to release an update of the database twice per year`; version 14 contains `471 plant species, 213 genera and 72 families` under category A and `755 plant species, 329 genera and 93 families` regardless of method. The record exposes five XLSX files including a 4.3 MB observation workbook.

22. **BeXyl public deliverable families.**  
    URL: <https://bexylproject.org/outcomes/documents/public-deliverables/>  
    Verbatim titles include `Maps of relative risk to Xf`, `Evaluation of phenotyping approaches ... using remote sensing`, `Identification of new germplasm resistant to Xf`, `Best agronomic practices for the management of tolerant/resistant cultivars`, and `Economic analysis for implementation of IPM programs for Xf`. These are a finite deliverable catalog, not automatically downloadable field microdata.

23. **CORDIS/OpenAIRE result catalog.**  
    URL: <https://cordis.europa.eu/project/id/101060593/results>  
    Verbatim: `CORDIS provides links to public deliverables and publications of HORIZON projects`; the page reports `Documents, reports (5)`, `Data Management Plan (2)`, `Data sets, microdata, etc (1)`, and `Peer reviewed articles (44)` at the fetched cut. It also states links to some datasets/software are dynamically retrieved from OpenAIRE.

24. **Physiological observations are cultivar- and water-state-dependent.**  
    URL: <https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2022.968934/full>  
    Verbatim: periodic measurements of stomatal conductance and stem water potential found infected Cellina di Nardò had higher stress changes than infected Leccino and FS17, while `no differences were found among healthy plants of the different cultivars.` This supports using water/soil/weather context and a defined outcome, not treating canopy stress as infection.

25. **CREA germplasm catalog as a resistance-research source.**  
    URL: <https://www.crea.gov.it/-/olio-d-oliva-collezione-crea-unica-in-italia-ufficialmente-nella-banca-internazionale-coi-del-germoplasma>  
    Verbatim: the collection is `composto da 600 varietà, di cui 200 autenticate` and is used in research on genotypes tolerant or resistant to Xylella and climate stress. This is germplasm/research infrastructure, not commercial nursery capacity.

## F. Failed URLs and precise failure modes

| URL | Failure in this run | Consequence/recovery |
|---|---|---|
| <https://www.agea.gov.it/portale-agea/normative/circolare-agea-prot-n-21371-del-14-marzo-2024> | Crawl4AI HTTP 500, correlation `d5cb5f37a94c` | official search-index excerpt retained; direct PDF/API/browser route remains required |
| <https://www.sian.it/GestioneTrasparenza/gestione-trasparenza> | Crawl4AI HTTP 500, correlation `0f6af274a723` | source family remains live; browser/XHR reverse engineering required |
| <https://opencoesione.gov.it/en/opendata/> | Crawl4AI HTTP 500, correlation `e697490a5d4e` | use direct bulk URLs or EU-IP/browser; prior US-IP probe returned country block |
| <https://opencoesione.gov.it/it/opendata/dataset/pagamenti/> | Crawl4AI HTTP 500, correlation `ba8af99f0092` | search-index fragment establishes relational payment table; direct download still required |
| <https://www.arpa.puglia.it/pagina3367_report-corpi-idrici-sotterranei.html> | Crawl4AI HTTP 500, correlation `55c1fd8fb153` | report family identified; station-level machine extract remains a request/acquisition |
| <https://foreste.regione.puglia.it/documents/1086071/5186414/DET_953_16_12_2024.pdf/c0921a48-004a-a0b2-503c-d3078908a72a?t=1738568984807> | Crawl4AI HTTP 500, correlation `a0d9bdabcae1` | current RUOP act lead retained; parse by direct PDF fetch/browser before counting operators |
| <https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/10092> | extractor refused as `Blocked: URL targets a private or internal network address` | use browser/direct official attachment; do not classify MASAF source as unavailable |
| <https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/12531> | same internal-network refusal | national laboratory page remains a lead; current designation must come from newer regional acts/Accredia |
| <https://pmc.ncbi.nlm.nih.gov/articles/PMC9530328/> | browser challenge page instead of article body | Frontiers canonical article fetched successfully |
| <https://www.efsa.europa.eu/en/supporting/pub/en-9037> | HTTP content was an EFSA `Page not found` page | use Zenodo record 20539663 and DOI 10.2903/j.efsa.2026.10147 |
| SIAN oil portal page | extractor returned only cookie text | official search-index excerpt used only to identify the service; authenticated operator data not claimed |

## Final verdict

The newly expanded universe does not justify a larger generic ontology. It justifies a disciplined ingestion and acquisition programme around the accepted operator graph. Most sources become dated evidence feeding existing Parcel, Area, Instrument, Proceeding, Intervention, Party, Pursuit and Capacity owners. The important model correction is narrow and physical: **Plant Material Lot plus allocation/custody and an authorized lot-allocation/substitution Action**. Everything else should first be tested as a property, factual history, contextual relationship, capacity commitment or Function input before adding a noun.

The highest-value next acquisitions are: member-authorized fascicolo/SIPA extracts; ARIF execution/verbale/indemnity ledgers; current RUOP and nursery lot/capacity records; lawful water entitlement/delivery and source-quality evidence; contractor commitments; DOP/SIAN traceability where it changes value realization; bank settlement; and a structured establishment/early-replacement observation programme. Those close the gaps between public identity and private current state, between order and outcome, and between installation and biological recovery.

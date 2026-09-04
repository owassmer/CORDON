# Repository lane B — data and process evidence

Status: independent repository research record
Scope: `/Users/owenwassmer/Desktop/Connor/olive-xylella`
External web used: no
Ontology, Foundry, challenge, and screen design: out of scope

## Method

This lane inventories the tracked repository and reads the data-universe, schema, computational, and generated-interface surfaces. It does not use web research to repair the corpus. It does not treat the prior interface or any proposed Wedge 1 design as product authority.

A tracked-file manifest is stored at `repo-tracked-inventory.json`. It records 186 tracked files. Raw and binary assets are represented through tracked manifests, inventories, schemas, extracted text, and the scripts that consume them. The separate repository lane reads the program, query, brief, producer, and strategy corpus.

## Coverage ledger

| Area | Tracked files | Treatment in this lane |
|---|---:|---|
| Root program/schema files | 7 | `CORDON.md`, `AGENTS.md`, and `SCHEMA.md` read; remaining root records assigned to repository lane A |
| `data/` | 16 | Source-universe files, campaign inventory, dataset notes, statistics, and harmonization script read; decoder details represented through `decoder/SOURCES.md` |
| `interface/` | 10 | README, generator, and complete HTML read; generated JSON/JS represented by generator and file inventory |
| `nowcast/` | 27 | Key method/result records read; remaining scripts and caches represented through named owning records and inventory |
| `raw/` | 84 | Paper and supplement populations represented by `raw/papers/MANIFEST.md`, `data/decoder/SOURCES.md`, tracked extracted-text inventory, and consuming records; binary image assets not inspected visually |
| `checks/` | 2 | Represented by tracked inventory; these validate scientific data joins, not the five operator workflows |
| `concepts/`, `entities/`, `briefs/`, `queries/`, `producers/` | 37 | Assigned to independent repository lane A for full workflow/program digestion |
| `.hermes/` | 3 | Development support, not domain evidence |

## What the repository can prove

### 1. Land and official situation

The repository is strongest here.

#### Land identity and geometry

Two public cadastral routes are documented:

- The Regione Puglia SIT parcel layer contains 4,935,899 polygons and supports point-to-parcel lookup using comune, sheet, and parcel number (`data/DATA_UNIVERSE_GEO.md:27-31`).
- The Agenzia delle Entrate WFS provides current cadastral parcel geometry and a national cadastral reference (`data/DATA_UNIVERSE_GEO.md:53-57`).

The cadastre identifies the officially mapped piece of land. It does not by itself identify the current farm operator, crop declaration, or application applicant.

Current farm-to-agricultural-land declarations live in the SIAN farm file and graphical agricultural parcel system. The repository records that the live source is restricted and normally reached through a CAA, while public alternatives are dated snapshots or land-use proxies (`data/DATA_UNIVERSE_GEO.md:67-70`).

**Workflow effect:** CORDON can resolve and display land from public sources. Determining which cooperative farm currently controls or declares that land still requires farm/CAA records or another authoritative link.

#### Official Xylella geography

Current official infected, buffer, and containment areas are queryable polygon layers. Separate layers exist for outbreaks and subspecies. Seven historical infected-area versions are also available by decree (`data/DATA_UNIVERSE_GEO.md:11-20`).

The repository therefore supports:

- locating a parcel inside official geography;
- distinguishing current areas;
- reconstructing some prior legally effective areas;
- showing that an area changed.

It also records a critical semantic warning: similarly named area layers do not necessarily carry the same legal consequence. The geographic label must be interpreted with the governing act, not by name alone.

#### Official findings, orders, and registries

The repository records:

- current and historical official monitoring points, including sample result, date, species, symptoms, protocol, and confirmation document (`data/DATA_UNIVERSE_GEO.md:21-25`);
- permanent regional-bulletin copies of parcel-specific removal and delimitation acts, including parcel identifiers and coordinates (`data/DATA_UNIVERSE_CIVIC.md:38-48`);
- 341,428 registered monumental olive trees with parcel references, plus provisional additions (`data/DATA_UNIVERSE_GEO.md:34-38`);
- landscape, DOP, land-use, authorization, and other geographic constraints (`data/DATA_UNIVERSE_GEO.md:34-44`).

These sources can support an explanation of official parcel situation and published duties. They do not prove that the duty was scheduled, performed, or accepted.

#### Monitoring is not current parcel state by itself

The campaign workbooks contain approximately 1.5 million monitoring rows across 12 files, but their spatial frame moves over time (`data/CAMP_XLSX.md:7-34`; `nowcast/FRONT_RATE.md:13-37`).

The files also change schema:

- only one campaign inventory carries a `ZONA` field;
- `SUBSPECIE` appears in 2024 and 2025;
- campaign workbooks overlap calendar years;
- 2017–18 contains transposed coordinate outliers;
- the monitored geography moves north as policy and survey design change (`data/_camp_xlsx_inventory.json:197-259,457-542,672-821`; `nowcast/VALIDATION.md:1-26`).

A positive diagnostic row, an official area, and a parcel-specific duty are therefore different facts. The data supports joining them, not collapsing them.

### 2. Funding

The repository contains a broad source map but little direct operational funding data.

Available or identified sources include:

- current support measures and calls in official regional acts and portals;
- AGEA/SIAN per-beneficiary payment transparency for the latest two financial years;
- historical CAP payment aggregation through FarmSubsidy;
- OpenCoesione project and payment data;
- parcel-level replant authorization/communication records under DGR 1780/2019;
- DOP production areas and operator lists;
- the national recognized OP/AOP list (`data/DATA_UNIVERSE_CIVIC.md:12-36,68-80`; `data/DATA_UNIVERSE_GEO.md:34-44`).

The repository does not contain:

- a complete current cooperative farm population;
- current farm files from SIAN;
- a normalized corpus of every current funding call and its complete eligibility logic;
- real opportunity evaluations for all farms and parcels;
- a real cooperative decision to pursue or decline an opportunity.

**Workflow effect:** the corpus shows that complete population evaluation is technically plausible when call rules and cooperative farm/parcel data are available. It does not demonstrate that process yet.

### 3. Applications

The repository describes the desired output—parcel status, applicable measures, conditions, deadline calendar, and dossier skeleton (`CORDON.md:15-19,25-31`). It also documents sources that could populate parts of an application.

The tracked data lane does not contain a real end-to-end application package, application form schema, portal interaction record, exception queue, integration request, ranked list, concession act linked to an application, or submission receipt.

The current interface does not implement application operations. It is a research map showing official monitoring by campaign (`interface/README.md:1-21`; `interface/index.html:76-121`).

**Workflow effect:** automatic application preparation remains a product assertion. The repository data can populate land and some legal fields, but the actual application workflow must be established by repository lane A and independent web research.

### 4. Field Work

The repository identifies several potential field-work triggers and supporting sources:

- published removal orders and parcel annexes;
- legal duties in regional action plans and determinations;
- award determinations and replant authorizations;
- public procurement records for monitoring, laboratory, and possibly removal capacity;
- vector-monitoring reports;
- satellite and orthophoto layers that can describe canopy or land-surface change (`data/DATA_UNIVERSE_CIVIC.md:31-36,38-48`; `data/DATA_UNIVERSE_GEO.md:46-50`; `data/ORTOFOTO.md:1-25`).

The scientific work proves important limits:

- Sentinel-2 does not support individual-tree pre-diagnostic claims (`nowcast/NEGATIVE.md:1-14`).
- Remote sensing may show moisture or canopy change, but those signals are not official diagnosis or proof that a required intervention was completed (`nowcast/SCENE_JOIN.md:20-46`).
- Official monitoring coverage is policy-driven and cannot be read as a complete field census (`nowcast/FRONT_RATE.md:139-175`).

The repository does not contain actual cooperative field-operation schedules, assignments, contractor acceptances, completion records, quantities, invoices, or authority verification events.

**Workflow effect:** duties, orders, or awards may be able to prepare known work. Human scheduling, execution, verification, and exception handling remain ungrounded in actual operator records inside this lane.

### 5. Payments

The repository distinguishes several financial evidence routes:

- published support envelopes and award decisions;
- AGEA/SIAN payment transparency, with only a rolling two-year public window;
- historical CAP payment aggregation;
- OpenCoesione projects and payments;
- procurement and contract records (`data/DATA_UNIVERSE_CIVIC.md:12-36`).

It also notes that different schemes may use different payment routes; not every Xylella payment appears in the same system (`data/DATA_UNIVERSE_CIVIC.md:14-19`).

The repository does not contain a concrete award’s payment-stage rules, a real advance/interim/final claim, supporting expenditure, authority reduction, liquidation record, or bank receipt connected through one case.

**Workflow effect:** the assertion that CORDON can determine the next payment stage is not demonstrated by repository data. The rule patterns and real operational artifacts must be researched independently.

## Connected workflow evidence

The data supports four high-confidence connections.

### Parcel connects public geography to cooperative work

The parcel is the common reference across cadastral maps, official areas, monumental-tree records, published orders, DOP areas, land-use layers, and some authorization records. The missing connection is the current farm/parcel relationship, normally provided through the farm file or CAA (`data/DATA_UNIVERSE_GEO.md:27-44,53-70`).

### An official act can alter several functions at once

One act may redraw an official area, prescribe duties, open or amend a measure, change a deadline, or establish a payment rule. The repository records stable bulletin PDFs and historical geography that make such changes discoverable (`data/DATA_UNIVERSE_CIVIC.md:38-66`).

This supports a connected operating model in which one official change can affect Land, Funding, an existing Application, planned Field Work, or Payment readiness. It does not establish how operators currently handle those consequences.

### Monitoring and authority action are connected but not equivalent

Monitoring points can lead to confirmed findings, area changes, or parcel orders. Survey design also changes in response to prior findings. The monitoring corpus therefore records both disease evidence and the authority’s changing search strategy (`data/CAMP_XLSX.md:28-40`; `nowcast/FRONT_RATE.md:139-175`).

### Award, field delivery, and payment are expected to connect, but the repository lacks the transaction chain

The program contract explicitly requires the path through disbursement and verified field action (`CORDON.md:15-19`). The data universe identifies pieces of the chain. No tracked real case links an application to award, field operation, expenditure, payment request, decision, and money received.

## Starting assertions: repository-data verdict

| Assertion | Verdict from this lane | Reason |
|---|---|---|
| Land explains official status/duties; Field Work owns execution | **Supported** | Public geography, acts, monitoring, and orders explain official state. No execution records are present, so execution is necessarily separate. |
| Funding computes the complete eligible/ineligible/unresolved population; cooperative chooses whether to pursue | **Conditionally supported** | Public land and legal sources exist, but complete evaluation requires current cooperative farm/parcel data and normalized call rules not present here. |
| CORDON prepares applications; operator resolves exceptions and authorizes | **Unproven** | Desired output is described, but no real application schema or execution record exists in the data lane. |
| Duties/orders/awards prepare field work; manager schedules/assigns | **Partially supported** | Triggering sources exist. Scheduling, assignment, completion, and verification records do not. |
| Award rules determine and prepare the next payment stage; finance authorizes | **Unproven** | Payment and award sources are identified, but no award-specific stage workflow is represented end to end. |

## Demonstrated capability versus proposed product

### Demonstrated

- ingest and harmonize official monitoring workbooks;
- preserve campaign grain and schema variation;
- resolve public cadastral geometry;
- query current and historical official areas;
- locate monumental trees and other geographic constraints;
- retrieve permanent official acts and parcel annexes;
- identify public funding, payment, procurement, and organization sources;
- perform geographic and remote-sensing analyses with explicit validity limits;
- render a campaign-level research map.

### Proposed but not demonstrated

- complete cooperative population management;
- automatic current eligibility across calls;
- application preparation and exception resolution;
- submission and authority-response operations;
- field scheduling, assignment, completion, and verification;
- award-specific payment-stage preparation;
- one connected case through application, field action, and payment.

## Repository-data blind spots for workflow research

1. Real cooperative operating records and organizational roles.
2. CAA handling of farm-file corrections, mandates, application entry, and portal exceptions.
3. Current call forms, annexes, application grouping rules, and submission mechanics across programs.
4. Internal authority review, ranking, integration requests, concession, and rejection workflows.
5. Contractor procurement, scheduling, access to land, completion acceptance, and verification practice.
6. Award-specific advances, interim claims, reimbursements, final balances, reductions, and recoveries.
7. A complete real case joining farm, parcel, opportunity or duty, application, award/order, field work, claim, decision, and payment.
8. Operator frequency, time cost, error cost, and current tools for each step.

## Stale or bounded statements

- `data/README.md:10-13` reflects the earlier CKAN and portal access state; later data-universe records show richer live ArcGIS and workbook routes.
- `data/DAY1.md:32-41` says official polygons were blocked behind the portal. The later ArcGIS inventory disproves that (`data/DATA_UNIVERSE_GEO.md:11-20`).
- `nowcast/FRONT_RATE.md:183-195` states external survey-zone polygons were not on disk. The later data-universe audit identifies current and historical official zone layers (`data/DATA_UNIVERSE_FLIPS.md:16-17,45-51`).
- `raw/papers/MANIFEST.md:17-20` marks several papers missing, while `data/decoder/SOURCES.md:11-13` records some of them as present. The latter is newer for those files.
- The existing interface is an evidence visualization, not evidence of cooperative operator workflow (`interface/README.md:1-21`).

## Conclusion

The existing corpus is a strong land-and-source foundation. It shows that public parcel geometry, official Xylella geography, monitoring, orders, registries, and many money sources are richer than earlier assumptions allowed.

It is not yet a workflow corpus for Applications, Field Work, or Payments. Those functions remain largely specified from desired outcomes rather than observed operator practice. The independent web lane and repository program lane must fill or explicitly preserve those gaps before the connected operating model is accepted.

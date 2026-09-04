# DATA_UNIVERSE_CIVIC — money flows, legal acts, archives, civic routes

Probed 2026-08-16 from a US IP (curl + exa + firecrawl). Every entry: endpoint → probe evidence → format → license → which CORDON assumption it changes. Probe artifacts under `/tmp/` (cdx_ex.txt, cdx_sit.txt, oc_xyl.json, etc.; not committed).

Assumptions under attack (from the mission brief):
- A1 "crew and lab-capacity records are not public"
- A2 "budget lines are press-derived"
- A3 "felling orders only live 7 days on albo pretorio"
- A4 "historical demarcation zones are lost"
- A5 "coop membership numbers are press quotes"

## 1. Money flows, per beneficiary

### 1.1 AGEA/SIAN CAP payment transparency
- Endpoint: https://www.sian.it/GestioneTrasparenza/ (AGEA "Pubblicazione dei beneficiari" per Reg. UE 2021/2116 art. 98). Probe: HTTP 200, Angular SPA, last-modified 2026-07-22. Internal JSON API exists (`/GestioneTrasparenza/api/...` routes serve the SPA shell; endpoint names not reverse-engineered — needs a browser session with devtools, 30 min task).
- Query interface: by beneficiary name/CUAA, comune, misura, campaign year. EU rule: only the **last 2 financial years** stay online — this is a rolling-window source; harvest yearly or lose it.
- Content: per-beneficiary payments incl. rural-development interventions. Piano di rigenerazione (PSR/CSR sottomisura 4.x / SRD01) payments to a named Ostuni coop are findable here by name search; Art. 6 indemnity payments flow through the regional aid scheme (DGR 994/2024), not always through AGEA — cross-check both.
- Format: HTML/JSON (no bulk). License: public-sector transparency publication, reuse unstated (cite, don't redistribute names casually — GDPR recital in Reg. 2021/2116 limits purpose).
- Changes A2: budget lines become named-beneficiary ledger rows, not press numbers.

### 1.2 FarmSubsidy.org (aggregator, historical depth)
- https://farmsubsidy.org/ probe: HTTP 200, search UI live; `api.farmsubsidy.org` did not resolve from this network (HTTP 000) — data also on https://data.farmsubsidy.org/ as bulk CSV per country-year. Holds IT years beyond SIAN's 2-year window.
- Format: CSV bulk. License: ODbL-style open (OKFN lineage). Changes A2 and adds the time axis SIAN deletes.

### 1.3 OpenCoesione (project-level cohesion spending)
- https://opencoesione.gov.it/it/opendata/api/progetti/?q=xylella — probe: **HTTP 403 "Access denied from country: US"**; same block via firecrawl. Geo-block, not auth.
- Bypass A: any EU IP (VPN/proxy) → open API + full CSV dumps (progetti, pagamenti, soggetti/beneficiari; CC-BY). Bypass B (probed): data.europa.eu harvests **563 OpenCoesione datasets** (`api/hub/search/search?q=opencoesione` → count 563) with distribution metadata; resource URLs still point at opencoesione.gov.it, so an EU IP is eventually required.
- Expected content: "rigenerazione olivicola", PSR/POC/FSC xylella projects with € committed/paid and beneficiary granularity to the implementing body.
- Changes A2: project counts and amounts become downloadable rows. GAP: counts not yet recorded (geo-block); first EU-IP session closes it.

### 1.4 Public procurement = the real crew/lab-capacity route
- ANAC open data: https://dati.anticorruzione.it/opendata/dataset — probe via firecrawl: **70 datasets**, CSV/JSON/TTL, CKAN API at `/opendata/api/3` (WAF rejects plain curl UA; browser UA or firecrawl passes). Datasets: CIG full + delta, aggiudicatari, quadro-economico, subappalti, stati-avanzamento, stazioni-appaltanti.
- Method: bulk CIG CSVs → filter `stazione_appaltante ∈ {ARIF, Regione Puglia — Sezione Osservatorio Fitosanitario, InnovaPuglia}` and `oggetto ~ xylella|monitoraggio|estirpazione|analisi`. Yields contract values, durations, winners = felling-crew and sampling capacity in €.
- Cross-evidence already in hand (BURP DET_2_12_1_2026_FITO.pdf): **DDS 190/2024 procurement + DDS 54/62/91 of 2025 award the official lab-analysis service for 2025–2026 to named labs (CNR-IPSP as national reference lab + Univ. Bari DiSSPA et al.)** — lab capacity is contracted, published, and versioned in BURP. License: ANAC data CC-BY-compatible (IODL).
- EmPULIA (regional e-procurement, empulia.it): probe HTTP 000 (TLS from US flaky); tender notices searchable in-browser; ARIF also lists "Bandi di gara e contratti" on arifpuglia.it (probe: HTTP 200, section present) per D.Lgs 33/2013.
- Changes A1: crew/lab capacity = ANAC/EmPULIA contract values + BURP award determinations. "Not public" is false; it was just not assembled.

## 2. Legal acts at scale

### 2.1 BURP — the master archive (biggest single find)
- https://burp.regione.puglia.it/ — probe: HTTP 200, Liferay portal; issue browser at `/bollettini` with query params (`bolanno`, `bolnumero`, `boltipo`, `datefilter`) via the `it_indra_regione_puglia_burp_web_SearchPortlet`.
- PDFs live at stable URLs `burp.regione.puglia.it/documents/20135/{folderId}/DET_{n}_{d}_{m}_{yyyy}[_FITO].pdf` and are **search-engine indexed full-text**. Probed retrievals: DET_9/2021 (Ostuni estirpazione), DET_172/2021 (Ostuni), DET_18/2025 (Cassano delle Murge, 14 piante), DET_2/2026 + DET_3/2026 (Valenzano AD istituzione; Bitonto eradicazione), DET_94/2024 (ST1 AD aggiornamento), DET_121/2025 (vector-treatment proroga).
- Content per estirpazione DDS: **Allegato with FOGLIO, PARTICELLA, PROPRIETARIO/INTESTATARIO names, species, sample ID, lon/lat, zone** (e.g. DET_3/2026 Bitonto: foglio 29 part. 145, owner named in the act, 16.74115, 41.12326 + all 50 m-ring parcels/owners). Delimitation DDS carry Allegato 2 cadastral sheets of infetta/cuscinetto zones.
- Route to scale: exa/Google `site:burp.regione.puglia.it xylella estirpazione <anno>` or crawl `/bollettini` issue indexes; no API, but PDF URL pattern makes bulk capture scriptable. Format: PDF (text layer present). License: official gazette, free reuse with source.
- Changes A3 (killed): every albo-pretorio felling order is ALSO published permanently in BURP + emergenzaxylella.it + regione.puglia.it Amministrazione trasparente ("Provvedimenti dirigenti amministrativi"). The 7-day window is a notification fiction, not a data limit. Also changes A4 (cadastral zone annexes = historical zone record) and feeds the parcel→order layer of the eligibility engine.

### 2.2 Albo pretorio aggregators
- Per-comune platforms (Halley, Urbi, Trasparenza-Valutazione-Merito) are scrapeable but heterogeneous; Ostuni's albo runs at urpcomunediostuni.it (probed page live). Given §2.1, albo scraping is only needed for **comune-issued** acts (ordinanze sindacali) — regional DDS are better captured from BURP. Programmatic capture: feasible per-comune, low priority.

### 2.3 TAR Puglia / appeal outcomes
- Portal: giustizia-amministrativa.it (probe HTTP 200; provvedimenti search is a JS portal, no clean API). Aggregators index it: doctrine.it, ambientediritto.it.
- Probe evidence: TAR Lecce sez. III sentenze **n. 459, 496, 497 of 2026** (mass damages claims vs Regione/Stato for late containment — all REJECTED, following 1439/2025); TAR Bari **n. 1640/2019** (albo-pretorio-only notification of felling orders upheld); Corte Cost. **74/2021** (replanting deroga struck down). Format: HTML/PDF; official texts free (CC-BY-like per open-data decree), doctrine.it is paywalled.
- Use: appeal-outcome base rates for the playbook's "can I fight the order" section — outcomes are consistently pro-administration.

## 3. Historical archives (demarcation time series)

### 3.1 Wayback Machine — emergenzaxylella.it
- CDX probe: `web.archive.org/cdx/...url=emergenzaxylella.it&matchType=domain` → **6,315 captures, 2015-04-30 → 2026-01-20**; 86 are .zip/.kmz/.kml/.pdf; the `Cartografie` page is captured from 2015-07-12 to 2026-01-20 (both endpoints seen in CDX). CDX API intermittently 503s — retry.
- Route: pull every Cartografie snapshot → harvest archived shapefile/KML links → rebuild the 2015–2026 demarcation-zone polygon time series. Format: zip/kml. License: original acts are official; archive access unrestricted.
- Changes A4: historical zones are recoverable, not lost. Combined with BURP cadastral annexes (§2.1) this gives two independent reconstructions — no one has this series.

### 3.2 Wayback — webapps.sit.puglia.it
- CDX probe: **8,451 captures** (2015→present), incl. EsriJsViewer xylella viewer assets. ArcGIS REST map-service JSON snapshots partially archived; secondary to 3.1.

### 3.3 EU layer of demarcation history
- Commission demarcated-area updates: EFSA-hosted and DG SANTE communications; the canonical machine record is the **Commission "Notification of demarcated areas" register under Reg. 2016/2031 art. 18(6)** plus successive amendments to Reg. 2020/1201 annexes (EUR-Lex, CELEX series 32020R1201 + amendments, e.g. 2024/2507 reducing containment strip 5→2 km — cited in DET_2/2026). Format: PDF/HTML on EUR-Lex, stable CELEX IDs, reuse free. Note: direct food.ec.europa.eu slug probed 404 — navigate from the plant-health control-measures section instead. Changes A4 at the EU-notification granularity (annual MS updates).

## 4. Organizations

### 4.1 Coops: registro imprese / albo cooperative
- Bilanci (incl. **soci counts** in nota integrativa for coops): registroimprese.it, paid ~€2.60/document (bilancio ottico), no API at that tier. Free route: **Albo nazionale società cooperative (MIMIT)** — public searchable register (sezione, categoria, comune) for existence/category; membership numbers need the bilancio.
- Changes A5: coop membership = €2.60/coop primary-source number, not a press quote. For ~20 target coops: ~€50 total. (Respect free-tier rule: this is the one place a micro-budget buys ground truth; flag to Owen before spending.)

### 4.2 DOP consortium operator registers
- CCIAA Bari, DOP Terra di Bari: **"estratto operatori iscritti ed attivi al 16/06/2026"** published at ba.camcom.it/info/d-o-p-terra-di-bari-2173 (probed page live), plus **"BANCA DATI SUPERFICI OLIVETATE" (.xls + .pdf)** with cadastral parcels of certified surfaces. Piano dei controlli PDF (rev. 14) documents the register schema. Format: PDF/XLS. License: published for operator verification; reuse with care.
- Use: named operator universe (olivicoltori, frantoiani, confezionatori) for the coop wedge; xls parcels join to zone status. Partially changes A5 (operator lists ≠ membership, but named and current).

### 4.3 Recognized OP/AOP (UNAPROL etc.)
- MASAF national list: masaf.gov.it ServeBLOB IDPagina/6063 — **"Elenco nazionale OP e AOP al 31/12/2025 (agg. 08.04.2026)"**, downloadable (probe: page + attachment links live). Format: PDF/XLS. License: MASAF publication, free reuse. Gives every recognized olive OP in Puglia with region/sector — the customer list for the eligibility engine.

## 5. EU research & surveillance layer

- **Zenodo**: API probe `q=xylella` → **770 records**, of which **36 datasets**; community `biovexo` exists; EFSA "Update of the Xylella spp. host plant database" latest release = zenodo.org/records/20539663 (Knowledge Junction). Format: mixed, DOIs; licenses per record (mostly CC-BY). BeXyl/REACH-XY deliverables: search Zenodo + CORDIS per project.
- **CORDIS**: search API probe (`contenttype='project' AND 'xylella'`) → **14 projects** (incl. BeXyl 101060593). Public deliverable PDFs attached to project pages; CC-BY. 
- **EFSA**: Xylella host-plant DB (above) + EFSA Journal outputs; open data, CC-BY.
- **Europhyt/TRACES outbreak notifications**: only aggregate monthly/annual outbreak reports are public (food.ec.europa.eu); case-level notifications are MS-restricted → accesso civico/AskTheEU route if ever needed. Low value vs regional data we already hold.
- **dati.puglia.it CKAN**: probe `package_search?q=xylella` → 1 dataset (`dati-monitoraggio-xylella-fastidiosa`, the known CKAN extract). API works unauthenticated; IODL 2.0.

## TOP 10 by impact (eligibility engine + surveillance products)

1. **BURP estirpazione/delimitation DDS corpus** (§2.1) — parcel-level orders + owners + zones, permanent, scriptable. Kills A3; feeds parcel→measure engine directly.
2. **ANAC CIG bulk filtered to ARIF/Osservatorio/InnovaPuglia** (§1.4) — crew+lab capacity in €. Kills A1.
3. **Wayback emergenzaxylella Cartografie harvest** (§3.1) — 2015–2026 demarcation time series nobody has. Kills A4; surveillance product.
4. **BURP lab-award determinations (DDS 190/2024, 54/62/91/2025)** — named labs and contract scope; pairs with 2 to model sampling-collapse risk. Kills A1 (lab half).
5. **AGEA/SIAN GestioneTrasparenza yearly harvest** (§1.1) — who actually received rigenerazione money; uptake ground truth for S6. Kills A2.
6. **OpenCoesione API/CSV via EU IP** (§1.3) — project-level € for every xylella intervention. Kills A2.
7. **MASAF OP/AOP list** (§4.3) — customer universe, one download.
8. **CCIAA Bari DOP operator extract + superfici olivetate xls** (§4.2) — named operators + certified parcels for zone-status joins.
9. **Coop bilanci (€2.60 each)** (§4.1) — membership + financial fragility of target coops. Kills A5.
10. **TAR outcome base rates** (§2.3) — playbook "appeal reality" section; low effort, high trust value.

## Accesso civico shortlist (exact holder)

- **ARIF** (protocollo@pec.arifpuglia.it): felling-crew staffing/rosters and per-campaign estirpazione throughput not derivable from contracts; xylella.arifpuglia.it case volumes.
- **Regione Puglia — Sezione Osservatorio Fitosanitario** (c/o Dipartimento Agricoltura PEC): machine-readable (shapefile) historical delimitation layers 2015–2026 as held internally by InnovaPuglia; per-lab sample allocation and turnaround 2020–2026.
- **InnovaPuglia S.p.A.**: the parcel↔coordinate resolution service outputs (catastal joins) used in every DDS.
- **AGEA**: per-beneficiary payment extract for campaigns older than the 2-year window (rigenerazione measures), if FarmSubsidy bulk lacks them.
- **MASAF / DG SANTE (AskTheEU.org)**: case-level Europhyt outbreak notifications for Puglia, if EU aggregate proves insufficient.

Un-probed residuals (recorded, not hidden): OpenCoesione counts (geo-block), SIAN internal API names (needs browser devtools), EmPULIA search (TLS from US), farmsubsidy API host (DNS). None blocks the Top 10.

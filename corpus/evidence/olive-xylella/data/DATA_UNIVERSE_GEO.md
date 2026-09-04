# DATA_UNIVERSE_GEO — probed geospatial/administrative data universe for the Puglia Xylella domain

Probed 2026-08-16 by data-acquisition subagent. Every verdict below is backed by a curl/API call executed today; probe evidence (HTTP status, counts, field names) is quoted from those calls, not from documentation. Excludes assets already inventoried on disk (CAMP workbooks, CKAN monitoring CSVs, BaseMaps orthophotos, Crecco figshare, Sentinel-2 COGs).

Headline: three of the Palantir-AIP report's blocking assumptions are dead. Demarcation-zone polygons are queryable vector layers (not "gated, digitize from the map"). Parcel polygons exist publicly twice over (SIT Puglia Sigmater layer, 4,935,899 features; AdE INSPIRE WFS with foglio/particella identifiers). The LR 14/2007 monumental-olive registry is a queryable point layer with 341,428 records carrying foglio/particella attributes.

## 1. SIT Puglia ArcGIS catalog — webapps.sit.puglia.it

Root: `https://webapps.sit.puglia.it/arcgis/rest/services?f=pjson` → HTTP 200, ArcGIS 10.11, 11 folders (Background, BaseMaps, Editing, Geoprocessing, Network, Operationals, Operationals2, Operationals3, Print, ServicesArcIMS, Utilities), ~170 services enumerated in full. All services below report `capabilities: Map,Query,Data` (query enabled; MaxRecordCount 1000; `f=geojson` NOT supported — probe returned "Error: Output format not supported" — use `f=json` Esri JSON and convert). No API key, no auth on any probe. License: SIT Puglia terms (attribution; not an explicit open license — record as "public access, license unstated" per service).

### 1.1 Demarcation zones (the crown jewel)

- **Operationals/DatiPubbliciFasceXF/MapServer** — 16 layers, one Zona Infetta / Cuscinetto pair per outbreak (Cagnano Varano, Giovinazzo, Modugno, Bisceglie, Minervino Murge, Bari, Mola di Bari/Noci foci) plus ex-Salento ST53 layers 13–15.
  - Probe L15 (Zona Infetta pauca ex-Salento): `query?where=1=1&returnCountOnly` → `{"count":1}`; full query → polygon, 43 rings, EPSG:32633, fields `OBJECTID, DESCRIZIONE, SHAPE.AREA, SHAPE.LEN`, SHAPE.AREA = 6,372,704,372 m² (~6,373 km²).
  - L14 Zona Contenimento → count 1, area 152.5 km². L13 Zona Cuscinetto → count 1, area 390.5 km².
  - **Kills assumption "demarcation polygons are gated, digitize from the map."** Full authoritative geometry downloadable via paged `f=json` queries. This is the zone-status input of the eligibility engine.
- **Operationals2/DatiPubbliciFasceXFF/MapServer** — subsp. *fastidiosa* ZI+ZC (2 layers). Layer page probed via search → MaxRecordCount 1000, polygon, queryable.
- **Operationals2/DatiPubbliciFasceXFMultiplex/MapServer** — subsp. *multiplex* ZI/ZC + Basilicata cuscinetto (Ginosa/Santeramo). Probe L0 → count 4; sample `DESCRIZIONE: "Area delimitata ... multiplex (Ginosa) - Zona Infetta"`, SHAPE.AREA 23,499 m².
- **Operationals2/DatiPubbliciFasceXFBandoPSR/MapServer** — 7 HISTORICAL Zona Infetta versions by decree (DDS 157/2014, 3/2015, 54/2015, 571/2015, 23/2016, 203/2016, 59/2019). Time-series of the legal front; enables decree-cited zone history per parcel.

### 1.2 Monitoring points (live + historic, beyond the CKAN CSVs)

- **Operationals2/MonitoraggioXFSintesiAttuale/MapServer** — 2026 campaign LIVE. Probe L1 (Positivi 2026 pauca) → count 210; fields `RISULTATO, DATA_CAMPIONE, SQUADRA, ID_CAMPIONE, SPECIE, SINTOMI, PROTOCOLLO, DOCUMENTO_CONFERMA`; sample `RISULTATO: POSITIVO, SPECIE: OLIVO, PROTOCOLLO: "RAPPORTO PROVA 10P/2026 CNR"`. Fresher than the CKAN dataset (annual). Note count discrepancy: retry with `where=OBJECTID>0` gave 340 — counts move intraday or per-where; treat as live.
- **Operationals2/MonitoraggioXFSintesi/MapServer** — campaigns 2023–2025 point layers (L0 raster-like group query returns 400 — probe individual point layers). **MonitoraggioXFFSintesiAttuale** (fastidiosa 2026), **MonitoraggioXFMultiplexSintesiAttuale**, plus `*SintesiPrecedenti` (Operationals3) for older years, **MonitoraggioXFMaglie**, **MonitoraggioXFPasp**.
- Changes assumption: geolocated per-sample diagnostic points with lab-protocol attribution are API-queryable, not just annual CSV drops.

### 1.3 Parcels and cadastre

- **Background/Catasto/MapServer** — "cartografia catastale aggiornata a settembre 2021 secondo lo scarico Sigmater". L2 Particelle probe → **count 4,935,899**, polygon, fields `COMUNE, SEZIONE, FOGLIO, ALLEGATO, SVILUPPO, NUMERO, LIVELLO, NOME_COMUNE`; sample `A048 / foglio 47 / particella 1259 / ACQUAVIVA DELLE FONTI`. Spatial point query at 17.57E 40.73N → returns OSTUNI parcel with FOGLIO+NUMERO. Also L0 Fogli, L1 Fabbricati. MaxRecordCount 1000, no pagination flag advertised — bulk extraction feasible per-comune/foglio via attribute-windowed queries.
  - **Kills assumption "parcel polygons don't exist publicly."** Point-in-polygon parcel lookup (coordinate → comune/foglio/particella) works today with one HTTP call. Caveat: snapshot Sept 2021.
- **Operationals2/MonitoraggioXFStampaCatasto/MapServer** — Fogli catastali / Particelle catastali / Confini Comunali as used by the official monitoring print service — confirms the Osservatorio itself resolves samples to this same cadastral layer.
- **Background/CatastoImpianto ImageServer**, **Operationals2/CatastoImpiantoEvoland** — historical cadastre rasters.

### 1.4 Registries and eligibility-relevant thematic layers

- **Operationals/UliviMonumentali/MapServer** — L1 "Ulivi Monumentali" probe → **count 341,428 points**, fields `SCHEDAN, COD, RILDATA, LOCPROV, LOCCOM, COORDX, COORDY, PROPRFG, PROPRPTC (foglio/particella!), CARSEGNMOT, MONOGRAFIA`. L0 "Ulivi Monumentali provvisori DGR 720/2025" → count 569 (2025 additions). L2 Aree Uliveti Provvisori.
  - **Kills the "heritage-tree triage blocked on LR 14/2007 registry" deferral premise**: the registry is a queryable layer keyed to parcels. Monumental status changes felling/replant eligibility (Art. 6/7 exemptions) — direct eligibility-engine input.
- **Operationals2/ElencoTerreniDGR17802019/MapServer** — L0 "Autorizzazioni - Lettera a - D.G.R. 1780/2019", L1 "Comunicazioni - Lettera b" — parcel-level replanting authorization/communication records under DGR 1780/2019. Direct precedent layer for measure-application tracking.
- **Operationals/AziendeAgricole/MapServer** — farm locations, "Aggiornamento luglio 2014" (stale; low value).
- **Operationals3/AreeProduzioneDOPIGPAgroalimentari/MapServer** — DOP/IGP production-area polygons incl. Olio Collina di Brindisi DOP (L12), Terre Tarentine (L13), Terra d'Otranto, Dauno variants. Maps parcel → DOP eligibility.
- **ServicesArcIMS/UDS2011 + UDS2006/MapServer** — Uso del Suolo 2011/2006 (regional land use; olive-grove class). Vector originals on CKAN (§3).
- Vincoli/PPTR stack for replant-permit context: **Operationals/Vincoli, VincoliDelegati, PPTR_APPROVATO, UsiCivici; Operationals2/AreeVincoloIdrogeologico, VincoliTotale, PTA2019_Vincoli; Operationals/PAI** — all same query pattern. Relevant because replanting in vincolo paesaggistico areas needs authorization (engine's "applicable constraints" column).
- **Operationals2/DGR8192019/MapServer** — DGR 819/2019 layer (buffer-zone olive measures era).
- **Operationals3/CartaPedologica** (soils), **Operationals2/DistrettiIrrigui** (irrigation districts), **Operationals2/InventarioForestale**.

### 1.5 Other Puglia hosts

- `https://cartografia.sit.puglia.it/arcgis/rest/services` → HTTP 404 (no second ArcGIS instance; host serves static docs + viewers only).
- `https://cartografia.sit.puglia.it/doc/xylella/` → HTTP 403 (directory listing off) but deep files are open: probe `.../doc/xylella/vettori/dati2026/Trasmissione dati vettori II rilievo & allegati.pdf` → HTTP 200. **Vector (sputacchina) monitoring 2026 exists as ARIF/CNR-IPSP transmission PDFs under `/doc/xylella/vettori/dati2026/`, not as shapefiles.** Guessed shapefile names `download_monit_*.zip` → all 404. Verdict: vector-monitoring geodata = semi-structured PDF tables; needs scraping, cadence per rilievo (weekly-ish in season).
- `https://paesaggio.regione.puglia.it` → connection refused (000). Superseded by pugliacon: **PPTR full shapefile pack** `https://pugliacon.regione.puglia.it/web/sit-puglia-paesaggio/file-vettoriali` → ZIP downloads (WGS84-UTM33N, updated to DGR 328 of 31/03/2026 with MD5) — bulk alternative to the PPTR MapServers.
- `http://www.emergenzaxylella.it` → 302 to `/josso_security_check` (SSO). Portal front door is login-walled, but irrelevant: its map viewers are the freewebapps at webapps.sit.puglia.it (`freewebapps/DatiFasceXF/index.html` → HTTP 200) backed by the DatiPubbliciFasceXF services above. Confirms limitation only for the portal's document area, not for data.

## 2. Cadastral parcels — national (Agenzia delle Entrate)

- **WMS**: `https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&REQUEST=GetCapabilities` → HTTP 200; layers `CP.CadastralParcel, CP.CadastralZoning, acque, strade, province`; CRS EPSG:6706/4258/25832-34. GetMap in EPSG:4326 fails ("Richiesta non valida"); **works with CRS=EPSG:6706 and small bbox**: 0.01°-bbox probe → HTTP 200 image/png 881,931 bytes, 1024×1024 rendered parcels. Scale-locked (large scales only). License: CC-BY-NC-ND 4.0 (per Regione Puglia PPTR page note). Image-only — fine for basemap/visual audit, not for geometry.
- **WFS (geometry!)**: `https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/owfs01.php?SERVICE=WFS&REQUEST=GetCapabilities` → HTTP 200, WFS 2.0, FeatureTypes `CP:CadastralParcel, CP:CadastralZoning`. GetFeature probe (COUNT=1, bbox near Ostuni, EPSG:6706) → HTTP 200 GML with `CP:LABEL=1`, **`CP:NATIONALCADASTRALREFERENCE=G187_0222D0.1`**, `CP:ADMINISTRATIVEUNIT=G187`. Identifier scheme: comune Belfiore code + foglio + particella (`<comune>_<foglio><allegato>0.<particella>`). Current (live AdE data, unlike Sigmater-2021). Likely request-size limits — page by bbox tiles.
  - **Kills assumption "parcel polygons don't exist publicly" a second way, with CURRENT data.** Engine can validate a user-entered foglio/particella and fetch its geometry.
- **OSM/Overpass** (olive land cover, ODbL): Brindisi province probe → `landuse=orchard` 1,143 ways; with `trees=olive_trees` 839 ways. Sparse vs reality (Brindisi has ~7M olive trees) — OSM is NOT a usable olive-grove layer; UDS + AGEA schedario are. Confirms limitation.

## 3. dati.puglia.it CKAN (API `dati.puglia.it/ckan/api/3/action/package_search`, all HTTP 200)

- `q=xylella` → count 1: `dati-monitoraggio-xylella-fastidiosa` (CC-BY-4.0, CSV; resource URLs under `/ckan/dataset/6d0fb7c5.../download/camp_*.csv`; updated 2025-12-23; cadence annual). Already on disk; API confirms it is the ONLY xylella dataset in CKAN — the ArcGIS services (§1) are the richer channel.
- `q=uso+del+suolo` → 35 hits; key: **`uso-del-suolo-2011-uds`** (IODL 2.0, SHP): 6 thematic ZIPs probed via package_show incl. `udssuperficiagricole1.zip`/`...2.zip` (olive-grove polygons live here). Also `consumo-del-suolo` (ISPRA).
- `q=catasto` → 3: `catasti` (IODL 2.0, SHP+ODS — cadastral sheets), `sistema-informativo-territoriale-particelle-catastali-di-proprieta-comunale` (CC-BY 4.0, ZIP — municipally owned parcels only), `catasto-grotte`.
- `q=olivic` → 0. `q=agricol` → 6 (aziende-agricole per comune stats CC-BY-4.0; `oleifici-nel-territorio-di-palagianello` cc-zero GeoJSON — oil mills, tiny). Confirms limitation: no schedario oleicolo, no farm-register geodata in regional CKAN.

## 4. AGEA / SIAN / MASAF

- **GSAA/IACS parcels**: RNDT metadata `geodati.gov.it/resource/id/agea:OPENIACS:GSAA:m004` — Italy-wide GSAA 2018 (farmer-declared agricultural parcels, `lpis_id`, `codi_occu` land-use code, `supe_ammi` eligible area), license CC-BY-4.0, distribution RDF Turtle at `www.afs.enea.it/project/openiacs/RDF/GSAA` → probe HTTP 301 (redirect; endpoint alive but needs follow/negotiation). One-off 2018 research release; current GSAA/schedario grafico oleicolo lives inside SIAN — **gated** (probe of `www.sian.it` → 200 but "Accesso all'area riservata"; AGEA circolare 67143/2023 confirms schedario oleicolo grafico is being constituted inside fascicolo aziendale, CAA-mediated access only). Verdict: parcel-level cultivation (olive) attribution publicly = UDS 2011 + GSAA 2018 snapshot; current schedario = via CAA partner (which IS our customer) — engine design should assume the coop/CAA brings its own fascicolo extracts.
- **RUOP** (official operator register): no national machine-readable export found; published per-region as decree allegati (probes/searches: Piemonte table download, Umbria PDF DD 2892/2026, Basilicata DD 7/2025 allegati). MASAF pages are modulistica only. Puglia's RUOP list not located as a structured file today — mark GATED/SCATTERED; nursery-operator checks need a per-region scrape or accesso civico.
- **DOP operator lists**: geometry via §1.4 DOP areas; operator lists sit with consorzi/MASAF PDFs — not probed to a machine-readable endpoint (GAP).

## 5. EFSA / EPPO

- **EFSA Xylella host plant database v14**: Zenodo record 20539663 probe → HTTP 200, license **cc-by-4.0**, files: `Xylella spp host plant database_VERSION 14.xlsx` (4.3 MB) + artificial/natural/not-specified infection XLSX + `new_host_plant_species_v14.xlsx`. Direct download, versioned (v14). Feeds host-species checks for measure applicability (removal of specified plants).
- **EPPO**: `gd.eppo.int/taxon/XYLEFA` → 200; `/download/distribution_csv` → 200, 6,658 B CSV (`continent,country,state,...,Status` — e.g. "Argentina | Present, restricted distribution"). Free CSV, no auth. **PM 7/24 diagnostic protocol**: Wiley DOI probe → HTTP 403 (bot-blocked); protocol is open-access via EPPO portal in browser but not curl-able here — GATED for automation, fine for humans.

## 6. Verdict vs the Palantir-AIP report

| Report assumption | Verdict | Evidence |
|---|---|---|
| Demarcation zones gated; digitize from map | **DEAD** | DatiPubbliciFasceXF query → full polygons, 3 subspecies + 7 historical decree versions |
| Parcel polygons not public | **DEAD** | SIT Catasto L2 count 4,935,899 (2021) + AdE WFS GetFeature with NATIONALCADASTRALREFERENCE (current) |
| LR 14/2007 monumental-olive registry unreachable | **DEAD** | UliviMonumentali L1 count 341,428 with PROPRFG/PROPRPTC |
| Registries unreachable (SIAN/schedario) | **CONFIRMED** for current schedario (SIAN login) — but CC-BY GSAA-2018 snapshot exists and the CAA customer holds the live data |
| Vector monitoring not machine-readable | **PARTIAL** | 2026 rilievi are open PDFs under /doc/xylella/vettori/dati2026/ (dir listing 403, files 200) — scrapeable, not shapefiles |

## TOP 10 newly-found sources by impact on the eligibility engine

1. **DatiPubbliciFasceXF MapServer** (webapps.sit.puglia.it) — authoritative ZI/ZC/Contenimento polygons, all foci → the engine's zone-status core.
2. **Background/Catasto L2 Particelle** — 4.94M parcel polygons with FOGLIO/NUMERO; one-call point→parcel and parcel→zone overlay.
3. **AdE INSPIRE WFS CP:CadastralParcel** — current parcel geometry + national cadastral reference; validation layer over the 2021 Sigmater snapshot.
4. **UliviMonumentali MapServer** — 341k monumental olives keyed to parcels; unblocks the deferred heritage-tree module and Art. 6/7 exemption checks.
5. **DatiPubbliciFasceXFBandoPSR** — decree-versioned historical Zona Infetta polygons; lets every output cite the decree that drew the line (the auditability moat).
6. **MonitoraggioXF*SintesiAttuale** — live 2026 sample points with lab protocol fields; fresher than CKAN, powers "status as of today" statements.
7. **ElencoTerreniDGR17802019** — parcel-level authorization/communication precedent layer; template for tracking measure applications.
8. **uso-del-suolo-2011-uds SHP** (CKAN, IODL 2.0) + UDS2011 MapServer — olive-grove land-use polygons; proxy where schedario is gated.
9. **AreeProduzioneDOPIGPAgroalimentari** — parcel→olive-DOP eligibility (Collina di Brindisi, Terre Tarentine, Terra d'Otranto).
10. **EFSA host DB v14 (Zenodo CC-BY) + EPPO XYLEFA CSV** — host-species applicability tables for removal/planting measures.

Runner-up: OPENIACS GSAA 2018 (CC-BY parcels with land-use codes; stale but the only open IACS geometry). Dead ends re-probed and confirmed: paesaggio.regione.puglia.it (conn refused), cartografia.sit ArcGIS (404), OSM olive cover (839 ways ≈ nothing), CKAN beyond the one xylella dataset, RUOP as structured national file, `f=geojson` on SIT services.

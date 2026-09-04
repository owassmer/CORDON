# Source universe delta — discovered vs ingested

Author: Connor. Date: 2026-08-18. Mode: read-only. Probes executed this session from this host.

Scope: everything the CORDON project has already documented about its data universe, everything the
wedge1-aip build ingests today, the live state of each discovered machine endpoint, and the gap
between the two.

Trigger: Connor asserted to Owen that "the Puglia SIT publishes only subspecies pauca geometry."
That assertion is false. This file records the refutation, the full delta, and the structural fix.

---

## CLASS 3 — ASSERTED FROM MODEL MEMORY, NO FETCHED SOURCE

**None.**

Every source name, endpoint, layer name, record count, HTTP status, and file path in this document
comes from a document read this session or an HTTP response received this session. Rankings,
"why it matters" columns, acquisition-difficulty grades, and the structural-fix recommendation are
inference over that evidence and are labelled CLASS 2.

Two deliberate abstentions, so they are not mistaken for findings:

- The subject matter of DGR 819/2019 is not stated here. The live service `Operationals2/DGR8192019`
  carries tratturi and vette layers (CLASS 1). The audit's parenthetical calls it a "buffer-zone olive
  measures era" layer. This document does not adjudicate which is right; it records the contradiction.
- The regulatory instrument that establishes the subsp. *fastidiosa* demarcated area at Triggiano is
  not named here. No act for it was fetched this session.

---

## CLASS 1 — QUOTED FROM A DOCUMENT OR ENDPOINT I ACTUALLY READ

### 1.1 The refuted assertion

Live probe, 2026-08-18:

```
GET https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/DatiPubbliciFasceXFF/MapServer?f=json
[200] 2 layers :: 0=Zona Infetta - Xylella Fastidiosa sub. fastidiosa | 1=Zona Cuscinetto - Xylella Fastidiosa sub. fastidiosa

GET .../Operationals2/DatiPubbliciFasceXFMultiplex/MapServer?f=json
[200] 3 layers :: 0=Zona Infetta - Xylella Fastidiosa sub. multiplex | 1=Zona Cuscinetto - Xylella Fastidiosa sub. multiplex | 2= Zona Cuscinetto Basilicata - Xylella Fastidiosa sub. multiplex (Santermo in Colle/Ginosa)
```

Counts, same probe run:

```
[200] Operationals2/DatiPubbliciFasceXFF/0 count=1
[200] Operationals2/DatiPubbliciFasceXFF/1 count=1
[200] Operationals2/DatiPubbliciFasceXFMultiplex/0 count=4
[200] Operationals2/DatiPubbliciFasceXFMultiplex/1 count=4
[200] Operationals2/DatiPubbliciFasceXFMultiplex/2 count=2
```

The four subsp. *multiplex* Zona Infetta features, verbatim `DESCRIZIONE`:

```
Area delimitata Xyella fastidiosa sub. multiplex (Ginosa) - Zona Infetta
Area delimitata Xyella fastidiosa sub. multiplex (Santeramo in Colle) - Zona Infetta
Area delimitata Xyella fastidiosa sub. multiplex (Noicattaro-Triggiano) - Zona Infetta
Area delimitata Xyella fastidiosa sub. multiplex (Capurso) - Zona Infetta
```

Location, resolved by point-in-polygon of one zone vertex against `Background/Catasto/MapServer/2`:

```
Operationals2/DatiPubbliciFasceXFF/0 | Zona Infetta Xylella Fastidiosa sub. fastidiosa | vertex 16.94335,41.0536 | comune=TRIGGIANO
Operationals2/DatiPubbliciFasceXFMultiplex/0 | (Ginosa) - Zona Infetta              | vertex 16.73281,40.53977 | comune=GINOSA
Operationals2/DatiPubbliciFasceXFMultiplex/0 | (Santeramo in Colle) - Zona Infetta  | vertex 16.77493,40.73177 | comune=SANTERAMO IN COLLE
Operationals2/DatiPubbliciFasceXFMultiplex/0 | (Noicattaro-Triggiano) - Zona Infetta| vertex 16.98266,41.07349 | comune=NOICATTARO
Operationals2/DatiPubbliciFasceXFMultiplex/0 | (Capurso) - Zona Infetta             | vertex 16.90425,41.05092 | comune=CAPURSO
```

Areas, summed from `SHAPE.AREA`:

```
XFF ZI: n=1 total_area_km2=1.68
XFF ZC: n=1 total_area_km2=69.74
MPX ZI: n=4 total_area_km2=3.71
MPX ZC: n=4 total_area_km2=428.05
MPX ZC Basilicata: n=2 total_area_km2=23.27
```

The SIT publishes demarcated geometry for all three subspecies. Roughly 526 km² of it is
non-*pauca*. The build ingests none of it.

### 1.2 The prior audit already recorded this

`/Users/owenwassmer/Desktop/Connor/olive-xylella/data/DATA_UNIVERSE_GEO.md`, lines 17–18:

> - **Operationals2/DatiPubbliciFasceXFF/MapServer** — subsp. *fastidiosa* ZI+ZC (2 layers). Layer page probed via search → MaxRecordCount 1000, polygon, queryable.
> - **Operationals2/DatiPubbliciFasceXFMultiplex/MapServer** — subsp. *multiplex* ZI/ZC + Basilicata cuscinetto (Ginosa/Santeramo). Probe L0 → count 4; sample `DESCRIZIONE: "Area delimitata ... multiplex (Ginosa) - Zona Infetta"`, SHAPE.AREA 23,499 m².

Same file, line 9:

> Root: `https://webapps.sit.puglia.it/arcgis/rest/services?f=pjson` → HTTP 200, ArcGIS 10.11, 11 folders (Background, BaseMaps, Editing, Geoprocessing, Network, Operationals, Operationals2, Operationals3, Print, ServicesArcIMS, Utilities), ~170 services enumerated in full.

Same file, line 38:

> - **Operationals2/ElencoTerreniDGR17802019/MapServer** — L0 "Autorizzazioni - Lettera a - D.G.R. 1780/2019", L1 "Comunicazioni - Lettera b" — parcel-level replanting authorization/communication records under DGR 1780/2019. Direct precedent layer for measure-application tracking.

Same file, line 24:

> - **Operationals2/MonitoraggioXFSintesi/MapServer** — campaigns 2023–2025 point layers (L0 raster-like group query returns 400 — probe individual point layers). **MonitoraggioXFFSintesiAttuale** (fastidiosa 2026), **MonitoraggioXFMultiplexSintesiAttuale**, plus `*SintesiPrecedenti` (Operationals3) for older years, **MonitoraggioXFMaglie**, **MonitoraggioXFPasp**.

The knowledge existed in the repo, in a file the build's own authority chain names.

### 1.3 The audit documents are already referenced by the build

Four build files point at the audit. The reference is real; it is prose, not an enumeration.

- `/Users/owenwassmer/Desktop/Connor/wedge1-aip/PRODUCT_AUTHORITY.md` line 7:
  > `PLAN_V2.md` (this repo), sha256 `208df9be…`. Basis: the 16 Aug 2026 data-universe audit (`olive-xylella/data/DATA_UNIVERSE_{GEO,CIVIC,FLIPS}.md`, commit `2d260a5`).
- `/Users/owenwassmer/Desktop/Connor/wedge1-aip/PLAN_V2.md` line 4:
  > Basis: data/DATA_UNIVERSE_GEO.md, data/DATA_UNIVERSE_CIVIC.md, data/DATA_UNIVERSE_FLIPS.md (commit 2d260a5), all probes dated 2026-08-16.
- `/Users/owenwassmer/Desktop/Connor/wedge1-aip/data/SOURCES.md` line 7:
  > - Data-universe evidence: `~/Desktop/Connor/olive-xylella/data/DATA_UNIVERSE_GEO.md`, `DATA_UNIVERSE_CIVIC.md`, `DATA_UNIVERSE_FLIPS.md`
- `/Users/owenwassmer/Desktop/Connor/wedge1-aip/AGENTS.md` line 66:
  > Verified 16 August 2026. Evidence: `~/Desktop/Connor/olive-xylella/data/DATA_UNIVERSE_GEO.md`, `DATA_UNIVERSE_CIVIC.md`, `DATA_UNIVERSE_FLIPS.md`.

`AGENTS.md` then re-states the universe in eight bullets. The first bullet, line 68, is the operative
one that builders and reviewers read:

> - Demarcation zones: `webapps.sit.puglia.it/arcgis/rest/services/Operationals/DatiPubbliciFasceXF/MapServer` — 16 queryable polygon layers (ST53 ex-Salento Infetta, Cuscinetto, Contenimento are layers 12–15; per-focolaio zones include Minervino Murge) plus 7 decree-versioned historical Zona Infetta layers.

That bullet names one *pauca* service and omits `DatiPubbliciFasceXFF`, `DatiPubbliciFasceXFMultiplex`,
`ElencoTerreniDGR17802019`, `MonitoraggioXFMaglie`, and `MonitoraggioXFPasp`. It is a narrower copy of
the audit, sitting closer to the work.

### 1.4 The full discovered universe

Consolidated from `DATA_UNIVERSE_GEO.md`, `DATA_UNIVERSE_CIVIC.md`, `DATA_UNIVERSE_FLIPS.md`
(`~/Desktop/Connor/olive-xylella/data/`), `wedge1-aip/data/acts/INVENTORY.md`, `wedge1-aip/PLAN_V2.md`,
`wedge1-aip/PRODUCT_AUTHORITY.md`, and `wedge1-aip/data/SOURCES.md`.

**SIT Puglia ArcGIS, `webapps.sit.puglia.it/arcgis/rest/services`** — ArcGIS 10.11, 11 folders.
Live service count this session: Background 7, BaseMaps 20, Editing 16, Geoprocessing 2, Network 2,
Operationals 61, Operationals2 54, Operationals3 8, Print 2, ServicesArcIMS 16, Utilities 6 =
**194 services**.

Named in the audits: `Operationals/DatiPubbliciFasceXF`, `Operationals2/DatiPubbliciFasceXFF`,
`Operationals2/DatiPubbliciFasceXFMultiplex`, `Operationals2/DatiPubbliciFasceXFBandoPSR`,
`Operationals2/MonitoraggioXFSintesiAttuale`, `Operationals2/MonitoraggioXFFSintesiAttuale`,
`Operationals2/MonitoraggioXFMultiplexSintesiAttuale`, `Operationals2/MonitoraggioXFSintesi`,
`Operationals3/*SintesiPrecedenti`, `Operationals2/MonitoraggioXFMaglie`,
`Operationals2/MonitoraggioXFPasp`, `Operationals2/MonitoraggioXFStampaCatasto`,
`Background/Catasto`, `Background/CatastoImpianto`, `Operationals2/CatastoImpiantoEvoland`,
`Operationals/UliviMonumentali`, `Operationals2/ElencoTerreniDGR17802019`,
`Operationals/AziendeAgricole`, `Operationals3/AreeProduzioneDOPIGPAgroalimentari`,
`ServicesArcIMS/UDS2011`, `ServicesArcIMS/UDS2006`, `Operationals/Vincoli`,
`Operationals/VincoliDelegati`, `Operationals/PPTR_APPROVATO`, `Operationals/UsiCivici`,
`Operationals/PAI`, `Operationals2/AreeVincoloIdrogeologico`, `Operationals2/VincoliTotale`,
`Operationals2/PTA2019_Vincoli`, `Operationals2/DGR8192019`, `Operationals3/CartaPedologica`,
`Operationals2/DistrettiIrrigui`, `Operationals2/InventarioForestale`, BaseMaps orthophoto ImageServers.

**Other geospatial and registry sources named in the audits**: AdE INSPIRE WMS
(`wms.cartografia.agenziaentrate.gov.it`), AdE INSPIRE WFS (`wfs.cartografia.agenziaentrate.gov.it`),
`cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/` vector-monitoring PDFs,
`pugliacon.regione.puglia.it` PPTR shapefile pack, `dati.puglia.it` CKAN
(`dati-monitoraggio-xylella-fastidiosa`, `uso-del-suolo-2011-uds`, `catasti`), OPENIACS GSAA 2018,
SIAN schedario oleicolo (gated), RUOP, EFSA host-plant DB v14 on Zenodo (record 20539663),
EPPO XYLEFA distribution CSV, OSM/Overpass, Meta/WRI 1 m canopy tiles, ESA WorldCover,
Copernicus CDS AgERA5/ERA5, SPEI.

**Civic, money, legal, archival sources named in the audits**: BURP
(`burp.regione.puglia.it/documents/20135/{folderId}/DET_*.pdf`), comune albo-pretorio mirrors
(municipiumapp S3 pattern), EUR-Lex CELEX 02020R1201 and amendments, TAR Puglia via
giustizia-amministrativa.it, AGEA/SIAN GestioneTrasparenza, FarmSubsidy bulk CSV, OpenCoesione API,
ANAC open data (70 datasets), EmPULIA, ARIF trasparenza, Wayback CDX for emergenzaxylella.it
(6,315 captures) and webapps.sit.puglia.it (8,451 captures), MIMIT albo cooperative,
CCIAA Bari DOP Terra di Bari operator extract and "BANCA DATI SUPERFICI OLIVETATE",
MASAF OP/AOP national list, Zenodo (770 xylella records), CORDIS (14 projects),
EFSA Knowledge Junction (113 records), Piano d'azione 2024-2026 and DGR 1075/2025 planned-effort
annexes, CAMP workbooks and CKAN CSV on disk.

### 1.5 What the build actually ingests

Evidence: distinct `source_url` values across every CSV under `wedge1-aip/data/`, every
`*.manifest.json` under `data/extracts/`, and health-check row counts in `RID_LEDGER.md`.

| Build dataset | Rows | Source endpoint(s) | Evidence |
|---|---|---|---|
| `demarcated_zones` | 23 | `Operationals/DatiPubbliciFasceXF/MapServer/0..15` (16) + `Operationals2/DatiPubbliciFasceXFBandoPSR/MapServer/0..6` (7) | `data/extracts/platform/demarcated_zones.csv`; `RID_LEDGER.md` "zones master rowcount=23" |
| `parcels` | 36 | `Background/Catasto/MapServer/2` | `data/extracts/platform/parcels.csv` (36 rows, all `source_url` = Catasto L2) |
| `monumental_trees` | 40 | `Operationals/UliviMonumentali/MapServer/1` | `data/extracts/platform/monumental_trees.csv` (40 rows) |
| `decrees` | 23 | BURP DET 53/2026, DET 82/2026, DET 120/2026; EUR-Lex 02020R1201-20251124; MASAF DI 2484/2020 + xylella_piano_sostegno; trasparenza DGR 1075/2025; `DatiPubbliciFasceXFBandoPSR/0..6` layer titles | `RID_LEDGER.md` "decrees master rowcount=23"; local `data/acts/decrees.csv` holds 14 pre-remediation rows |
| `measures` | 6 | DET 53/2026, EUR-Lex 02020R1201, MASAF piano sostegno | `RID_LEDGER.md` "measures master rowcount=6" |
| `funding_windows` | 3 | DET 53/2026, DET 120/2026, MASAF piano sostegno | `RID_LEDGER.md` "funding_windows master rowcount=3" |
| `parcel_zone_resolution` | 26 | `DatiPubbliciFasceXF/MapServer/{4,5,15}` only | `data/extracts/platform/parcel_zone_resolution.csv` |
| local extract, not a platform dataset | 210 | `Operationals2/MonitoraggioXFSintesiAttuale/MapServer/1` | `live2026_pauca_positivi.geojson.manifest.json` |
| local extract, not a platform dataset | 337,023 | CAMP workbooks | `data/extracts/sample_result_belt.csv` |

Demo comuni in `parcels.csv`: `ALBEROBELLO` (A149) 2, `BITONTO` (A893) 25, `OSTUNI` (G187) 9.

**Distinct machine endpoints the build touches: four.** `DatiPubbliciFasceXF`,
`DatiPubbliciFasceXFBandoPSR`, `Background/Catasto`, `UliviMonumentali`, plus
`MonitoraggioXFSintesiAttuale` as a local-only extract. Everything else is fetched PDFs and HTML.

### 1.6 Live probe results, 2026-08-18

Layer enumeration, `{service}/MapServer?f=json`:

```
[200] Operationals/DatiPubbliciFasceXF                 -> 16 layers  (unchanged vs audit)
[200] Operationals2/DatiPubbliciFasceXFF               -> 2 layers   (unchanged)
[200] Operationals2/DatiPubbliciFasceXFMultiplex       -> 3 layers   (unchanged)
[200] Operationals2/DatiPubbliciFasceXFBandoPSR        -> 7 layers   (unchanged)
[200] Operationals2/ElencoTerreniDGR17802019           -> 2 layers   (unchanged)
[200] Operationals2/MonitoraggioXFMaglie               -> 3 layers :: 0=Griglie Elementi 5K 1000ha | 1=Quadranti 250ha | 2=Maglie 1ha
[200] Operationals/UliviMonumentali                    -> 3 layers   (unchanged)
[200] Background/Catasto                               -> 3 layers   (unchanged)
[200] Operationals2/MonitoraggioXFSintesiAttuale       -> 5 layers   (2026 pauca)
[200] Operationals2/MonitoraggioXFFSintesiAttuale      -> 5 layers   (2026 fastidiosa)
[200] Operationals2/MonitoraggioXFMultiplexSintesiAttuale -> 5 layers (2026 multiplex)
[200] Operationals2/MonitoraggioXFSintesi              -> 78 layers  (pauca campaigns 2013-14 .. 2025)
[200] Operationals3/MonitoraggioXFFSintesiPrecedenti   -> 10 layers  (fastidiosa 2024, 2025)
[200] Operationals3/MonitoraggioXFMultiplexSintesiPrecedenti -> 10 layers (multiplex 2024, 2025)
[200] Operationals2/MonitoraggioXFPasp                 -> 2 layers :: 0=Aziende Vivaistiche - RUOP | 1=Impianti Leccino-FS17
[200] Operationals2/MonitoraggioXFStampaCatasto        -> 3 layers
[200] Operationals3/AreeProduzioneDOPIGPAgroalimentari -> 36 layers  (olive DOP/IGP = ids 6-19)
[200] Operationals2/DGR8192019                         -> 56 layers  (tratturi, vette, pendenze)
[200] Operationals/AziendeAgricole                     -> 1 layer    ("Aggiornamento luglio 2014")
```

Record counts, `{service}/MapServer/{id}/query?where=1%3D1&returnCountOnly=true&f=json`:

```
Operationals2/DatiPubbliciFasceXFF/0            count=1
Operationals2/DatiPubbliciFasceXFF/1            count=1
Operationals2/DatiPubbliciFasceXFMultiplex/0    count=4
Operationals2/DatiPubbliciFasceXFMultiplex/1    count=4
Operationals2/DatiPubbliciFasceXFMultiplex/2    count=2
Operationals2/ElencoTerreniDGR17802019/0        count=1132
Operationals2/ElencoTerreniDGR17802019/1        count=48807
Operationals2/MonitoraggioXFMaglie/0            count=1558
Operationals2/MonitoraggioXFMaglie/1            count=791
Operationals2/MonitoraggioXFMaglie/2            count=155009
Operationals/UliviMonumentali/0                 count=569
Operationals/UliviMonumentali/1                 count=341428
Operationals/UliviMonumentali/2                 count=64
Background/Catasto/2                            count=4935899
Operationals2/MonitoraggioXFPasp/0              count=1867
Operationals2/MonitoraggioXFPasp/1              count=9655
Operationals2/MonitoraggioXFStampaCatasto/1     count=4935899
Operationals2/MonitoraggioXFSintesiAttuale/1    count=210    (2026 positivi pauca)
Operationals2/MonitoraggioXFFSintesiAttuale/1   count=13     (2026 positivi fastidiosa)
Operationals2/MonitoraggioXFMultiplexSintesiAttuale/1 count=10 (2026 positivi multiplex)
Operationals2/MonitoraggioXFSintesi/1           count=340    (2025 positivi pauca)
Operationals2/MonitoraggioXFSintesi/6           count=157    (2024 positivi pauca)
Operationals2/MonitoraggioXFSintesi/11          count=189    (2023 positivi pauca)
Operationals3/AreeProduzioneDOPIGPAgroalimentari/12 count=1  (Olio 'Collina di Brindisi' DOP)
Operationals3/AreeProduzioneDOPIGPAgroalimentari/18 count=1  (Olio 'Terra d'Otranto' DOP)
Operationals3/AreeProduzioneDOPIGPAgroalimentari/19 count=1  (Olio di Puglia IGP)
```

Field schemas retrieved this session:

```
ElencoTerreniDGR17802019/0: OBJECTID, LUOGO_INTERVENTO, FOGLIO, PARTICELLA, NUM_AUTORIZZAZIONE,
                            BELFIORE, PROT_COMUNICAZIONE_FINE_LAVORI, DATA_COMUNICAZIONE_FINE_LAVORI
  sample: {'LUOGO_INTERVENTO': 'MURO LECCESE', 'FOGLIO': '2', 'PARTICELLA': '43',
           'NUM_AUTORIZZAZIONE': 'AOO_180/PROT. 03/06/2019 - 0033437', 'BELFIORE': 'F816'}

ElencoTerreniDGR17802019/1: OBJECTID, LUOGO_INTERVENTO, FOGLIO, PARTICELLA, BELFIORE,
                            PROTOCOLLO_COMUNICAZIONE, PARTITA_IVA, PROT_COMUNICAZIONE_FINE_LAVORI
  sample: {'LUOGO_INTERVENTO': 'CASTRI DI LECCE', 'FOGLIO': '6', 'PARTICELLA': '12',
           'BELFIORE': 'C334', 'PARTITA_IVA': '****'}     <- VAT already masked at source

MonitoraggioXFPasp/0: OBJECTID, ID_PART, TIPO_CENTRO, TIPO_STRUTTURA, SHAPE.AREA, SHAPE.LEN,
                      RAG_SOC, COMUNE, PIVA, PROVINCIA, RUOP
MonitoraggioXFPasp/1: OBJECTID, ID_PART, CULTIVAR, SHAPE.AREA, SHAPE.LEN, COMUNE, PROVINCIA, NUM_PIANTE
  sample: {'ID_PART': 'B506- -34-521', 'CULTIVAR': 'Leccino', 'COMUNE': 'CAMPI SALENTINA',
           'PROVINCIA': 'LE', 'NUM_PIANTE': 50}

MonitoraggioXFMaglie/2: OBJECTID, LAYER, ELEMENTO, IDROW, IDCOLUMN, ID_MAGLIA, SHAPE.AREA, SHAPE.LEN
  sample: {'ID_MAGLIA': '475134-4-12-9', 'SHAPE.AREA': 10874.60460804}   <- 1 ha survey cells

UliviMonumentali/2: OBJECTID, NOME_COMUNE, SHAPE.AREA, SHAPE.LEN
DatiPubbliciFasceXFF/*, DatiPubbliciFasceXFMultiplex/*: OBJECTID, DESCRIZIONE, SHAPE.AREA, SHAPE.LEN
```

Non-SIT endpoints, status only:

```
200  https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/owfs01.php?SERVICE=WFS&REQUEST=GetCapabilities
200  https://gd.eppo.int/taxon/XYLEFA/download/distribution_csv                 6658 bytes
200  https://zenodo.org/api/records/20539663                                    (EFSA host DB v14)
200  https://dati.puglia.it/ckan/api/3/action/package_search?q=xylella          count 1, dati-monitoraggio-xylella-fastidiosa
200  https://burp.regione.puglia.it/documents/20135/2798636/DET_82_11_5_2026.pdf/...   1,090,310 bytes
200  https://dati.anticorruzione.it/opendata/dataset                            269 bytes (shell only)
200  https://www.sian.it/GestioneTrasparenza/                                   20,158 bytes
200  http://web.archive.org/cdx/search/cdx?url=emergenzaxylella.it&matchType=domain
200  https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/6063    48,432 bytes (OP/AOP list page)
200  https://www.ba.camcom.it/info/d-o-p-terra-di-bari-2173                     33,189 bytes
200  https://webapps.sit.puglia.it/freewebapps/DatiFasceXF/index.html            9,274 bytes
403  https://opencoesione.gov.it/it/opendata/api/progetti/?q=xylella            30 bytes (US geo-block, unchanged)
403  https://cartografia.sit.puglia.it/doc/xylella/                             218 bytes (dir listing off, unchanged)
```

### 1.7 Live state that contradicts the audit

| # | Audit statement | Live state 2026-08-18 | Severity |
|---|---|---|---|
| C1 | `DATA_UNIVERSE_GEO.md` line 9: "~170 services enumerated in full" | 194 services across the same 11 folders | Low. The enumeration is stale, not wrong in kind. |
| C2 | `DATA_UNIVERSE_GEO.md` line 18: multiplex = "ZI/ZC + Basilicata cuscinetto (Ginosa/Santeramo)" | Four ZI foci: Ginosa, Santeramo in Colle, **Noicattaro-Triggiano**, **Capurso**. Two foci appear in no repo file. | **High.** The audit recorded the count (4) but named only two foci; the two unnamed ones are in Bari province, 20 km from the demo belt. |
| C3 | `DATA_UNIVERSE_GEO.md` line 24: "`*SintesiPrecedenti` (Operationals3) for older years" | `Operationals3` has no `MonitoraggioXFSintesiPrecedenti`. It has `MonitoraggioXFFSintesiPrecedenti` and `MonitoraggioXFMultiplexSintesiPrecedenti` only. Historical *pauca* points live in `Operationals2/MonitoraggioXFSintesi`, 78 layers, campaigns 2013-14 through 2025. | Medium. A builder following the audit path finds nothing and may report the corpus absent. |
| C4 | `DATA_UNIVERSE_GEO.md` line 43: "`Operationals2/DGR8192019` — DGR 819/2019 layer (buffer-zone olive measures era)" | 56 layers, all tratturi, vette, quote, pendenze. No visible olive or buffer-zone content. | Medium. Recorded as a contradiction; the subject matter is not adjudicated here. |
| C5 | `DATA_UNIVERSE_CIVIC.md` line 70: "**RUOP** (official operator register): no national machine-readable export found… Puglia's RUOP list not located as a structured file today — mark GATED/SCATTERED" | `Operationals2/MonitoraggioXFPasp/0` = "Aziende Vivaistiche - RUOP", **1,867 features**, fields include `RUOP`, `RAG_SOC`, `PIVA`, `COMUNE`, `PROVINCIA`. | **High.** A "gated" verdict in one audit file is refuted by a service the sibling audit file already lists by name. Same failure mode as the assertion that triggered this review. |
| C6 | `DATA_UNIVERSE_GEO.md` line 23: 2026 pauca positives "count 210… retry with `where=OBJECTID>0` gave 340 — counts move intraday" | `MonitoraggioXFSintesiAttuale/1` = 210 today. `MonitoraggioXFSintesi/1` (2025 positives) = 340. | Low, but it retires a recorded data-quality worry. See CLASS 2 §3.4. |
| C7 | `DATA_UNIVERSE_GEO.md` line 36: `UliviMonumentali` L2 "Aree Uliveti Provvisori" (no count) | count = 64 | Informational. |

Everything else the audits recorded still holds exactly: `DatiPubbliciFasceXF` 16 layers,
`DatiPubbliciFasceXFBandoPSR` 7 layers, `UliviMonumentali/1` = 341,428, `Background/Catasto/2` =
4,935,899, `f=geojson` unsupported, MaxRecordCount 1000, no auth on any SIT probe, OpenCoesione still
geo-blocked from a US IP, `doc/xylella/` directory listing still 403.

### 1.8 Overlap tests against the current demo set

Per-comune bounding-box intersect against each unused subspecies layer:

```
ALBEROBELLO  fastidiosa ZI=0 | fastidiosa ZC=0 | multiplex ZI=0 | multiplex ZC=0 | multiplex ZC Basilicata=0
BITONTO      fastidiosa ZI=0 | fastidiosa ZC=0 | multiplex ZI=0 | multiplex ZC=0 | multiplex ZC Basilicata=0
OSTUNI       fastidiosa ZI=0 | fastidiosa ZC=0 | multiplex ZI=0 | multiplex ZC=0 | multiplex ZC Basilicata=0
```

`ElencoTerreniDGR17802019` by comune Belfiore code:

```
L0 (Autorizzazioni lettera a)  BITONTO=0  OSTUNI=0   ALBEROBELLO=0
L1 (Comunicazioni lettera b)   BITONTO=0  OSTUNI=83  ALBEROBELLO=0
```

The 83 Ostuni communications cover fogli 13, 27, 32, 43, 48, 52, 59, 65, 66, 74, 85, 108, 134, 139,
140, 146, 154, 189, 193, 201, 203, 207, 214, 215, 216. The build's nine Ostuni parcels are
134/221, 57/100, 57/136, 57/35, 57/50, 57/57, 57/76, 57/77, 57/94. Foglio 134 appears in both sets;
**no foglio+particella pair matches**.

Stated plainly: on the 36 parcels the build holds today, no missing source changes an answer. The
overlap is zero. The exposure is to every parcel the product would serve outside those three comuni.

---

## CLASS 2 — INFERRED FROM CLASS 1

### 2.1 The delta table

Discovered-but-unused sources, ranked by whether the source changes an answer the product gives.
The product answers, for a parcel and a date: which demarcated zones contain it, which legal regime
applies, which measures it can claim, which funding windows are open, what evidence is missing.

Difficulty grades: **open** = one query returns everything; **paging** = >1,000 records, needs
`resultOffset`; **PDF** = text extraction required; **gated** = auth, geo-block, or no machine export.

| # | Source | Endpoint | Authoritative for | Records | Why it changes an answer | Difficulty |
|---|---|---|---|---|---|---|
| 1 | Subsp. *fastidiosa* demarcated area | `Operationals2/DatiPubbliciFasceXFF/MapServer/{0,1}` | The legal ZI and ZC for subsp. *fastidiosa*, Triggiano (BA) | 1 + 1; 1.68 + 69.74 km² | A parcel inside the ZC gets "no demarcated zone" from the product today. That is a false negative on a legally demarcated area covering 71 km² of the Bari metro belt, and the regime that attaches is a different subspecies branch from the *pauca* rules the engine encodes. Highest-severity single gap. | **open** — 2 queries |
| 2 | Subsp. *multiplex* demarcated areas | `Operationals2/DatiPubbliciFasceXFMultiplex/MapServer/{0,1,2}` | Legal ZI/ZC for four *multiplex* foci plus the Basilicata cross-border buffer | 4 + 4 + 2; 3.71 + 428.05 + 23.27 km² | Same false-negative class over 428 km². Two of the four foci (Noicattaro-Triggiano, Capurso) are absent from every repo file, so no reviewer can catch the omission by reading the repo. The Basilicata layer is a demarcated zone the product's Puglia-only model cannot represent at all. | **open** — 3 queries |
| 3 | DGR 1780/2019 replant authorizations and communications | `Operationals2/ElencoTerreniDGR17802019/MapServer/{0,1}` | Which parcels already hold a lettera-a replant authorization or filed a lettera-b communication, keyed `BELFIORE`+`FOGLIO`+`PARTICELLA` | 1,132 + 48,807 | Directly answers "what evidence is missing" and "has this parcel already exercised a replant right". A parcel with an existing authorization is in a different position from one without. 83 rows sit in Ostuni, a demo comune. `PARTITA_IVA` is already `****` at source, so D-3 owner masking is satisfied by the publisher. This is the only discovered source that is a per-parcel administrative *state*, which is exactly the object the product models. | **paging** — 48,807 rows at 1,000/page ≈ 49 requests |
| 4 | Per-subspecies official sample points, all campaigns | `Operationals2/MonitoraggioXF{,F,Multiplex}SintesiAttuale`, `Operationals2/MonitoraggioXFSintesi` (78 layers), `Operationals3/MonitoraggioXF{F,Multiplex}SintesiPrecedenti` | Official diagnostic results with lab-protocol attribution, per subspecies, per campaign, geolocated | 2026: 210 pauca / 13 fastidiosa / 10 multiplex. Historic pauca: 340 (2025), 157 (2024), 189 (2023) | Powers "status as of date" and the advisory `EvaluatePotentialImpact` path. The build holds one local extract of 2026 pauca positives and zero fastidiosa or multiplex points, so the advisory surface is blind to two of three subspecies. The 78-layer historic service also gives per-campaign official points that the CAMP workbooks carry without service-side lab attribution. | **open** per layer; **paging** on large campaign layers |
| 5 | RUOP nursery register and resistant-cultivar plantings | `Operationals2/MonitoraggioXFPasp/{0,1}` | Registered nursery operators with `RUOP` code; registered Leccino/FS17 plantings with `CULTIVAR` and `NUM_PIANTE` per parcel | 1,867 + 9,655 | L1 is a parcel-keyed register of resistant replant already in the ground. It changes the replant-measure answer and the "what evidence is missing" answer for any parcel that appears in it. L0 refutes the standing "RUOP gated" verdict and gives the operator universe for nursery-passport checks. | **paging** — ~11 requests |
| 6 | Provisional monumental designations | `Operationals/UliviMonumentali/{0,2}` | Trees provisionally listed under DGR 720/2025 and provisional grove areas | 569 + 64 | The build ingests L1 only. A provisional designation still constrains felling and replant under the LR 14/2007 chain, so a parcel carrying only a provisional tree currently reads as unconstrained. Small, cheap, and it removes a silent false negative on an exemption path the engine already models. | **open** — 2 queries |
| 7 | Official survey grid | `Operationals2/MonitoraggioXFMaglie/{0,1,2}` | The official 1,000 ha / 250 ha / 1 ha survey cells the monitoring campaign is planned and executed against | 1,558 / 791 / 155,009 | Converts "what evidence is missing" from a per-parcel guess into a statement about the official survey unit containing the parcel. Without the grid the product cannot say when a parcel's cell was last surveyed, which is the honest form of an evidence-gap answer. | **paging** — 155 requests for the 1 ha layer; the 250 ha layer is 1 request |
| 8 | Olive DOP/IGP production areas | `Operationals3/AreeProduzioneDOPIGPAgroalimentari/{6..19}` | Certified production-area polygons for every Apulian olive DOP and the Puglia IGP | 1 polygon per designation | Changes which measures a parcel can claim where a measure or a replant restriction is designation-linked, and it is a required field on a dossier for a DOP producer. | **open** — 14 queries |
| 9 | Current national cadastral geometry | AdE INSPIRE WFS `CP:CadastralParcel` | Current parcel geometry and `NATIONALCADASTRALREFERENCE` | live service, 200 | The build's parcels come from the Sigmater September 2021 snapshot. A parcel split or merged since 2021 resolves to a stale polygon, so the zone answer can be right about the polygon and wrong about the parcel. This is a correctness check on the product's primary key, not a new feature. | **paging** by bbox tile |
| 10 | BURP eradication and delimitation corpus at scale | `burp.regione.puglia.it/documents/20135/{folderId}/DET_*.pdf` | Per-parcel felling orders with cadastral annexes; delimitation annexes listing zone comuni and fogli | 6 PDFs fetched; corpus size unmeasured | `FellingOrder` is a declared object type with essentially no data behind it. The cadastral annexes are also the only source that resolves a zone to comune+foglio, which is how the acts themselves define containment. | **PDF**; folder id differs per act and cannot be guessed |
| 11 | Host-species applicability tables | Zenodo record 20539663 (EFSA host DB v14, CC-BY); EPPO XYLEFA distribution CSV | Which plant species are specified hosts | XLSX; 6,658-byte CSV | `host_applicability` is already a populated column on `measures`. It is currently prose, not a joinable table, so a host check cannot be evaluated. | **open** |
| 12 | Historical demarcation reconstruction | Wayback CDX for `emergenzaxylella.it` (6,315 captures) and `webapps.sit.puglia.it` (8,451 captures) | Superseded zone geometry between the 7 BandoPSR decree versions | captures, not features | The build can answer "which zone as of a date" only at the 7 decree snapshots it holds. Any date between them resolves to the wrong snapshot. | **paging** + archive latency |
| 13 | Money-flow ledger | AGEA/SIAN GestioneTrasparenza; ANAC open data; OpenCoesione; FarmSubsidy bulk | Who actually received rigenerazione and Art. 6 money; contracted felling and lab capacity | not measured | Changes the funding-window answer from "the window is open" to "the window is open and N applicants ahead of you have been paid". Not on the critical eligibility path. | **gated** (SIAN SPA, no documented API), **gated** (OpenCoesione 403 from US), ANAC returns a 269-byte shell to plain curl |
| 14 | Customer and operator universe | MASAF OP/AOP list; CCIAA Bari DOP operator extract + "BANCA DATI SUPERFICI OLIVETATE"; MIMIT albo cooperative | Named cooperatives, OPs, certified operators and their certified surfaces | not measured | Commercial targeting and the customer's own parcel set. Does not change a per-parcel legal answer. | **PDF/XLS** |
| 15 | Vector-monitoring transmissions | `cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/` | Per-rilievo vector survey results | PDF tables; directory listing 403, exact filenames 200 | Feeds vector-treatment window compliance. Peripheral to eligibility. | **PDF**, filenames must be discovered |
| 16 | Planned surveillance effort | Piano d'azione 2024-2026 annexes; DGR 1075/2025 (Piano 2025-2027) | Planned samples per zone and subspecies | PDF | Turns "no evidence" into "no evidence against a plan that required N samples here". `data/acts/INVENTORY.md` records the DGR 1075 PDF body as not located, so the build cites the act without its content. | **PDF**, one body not yet located |
| 17 | Land use, constraints, soils, irrigation | `ServicesArcIMS/UDS2011`, `UDS2006`; `Operationals/Vincoli`, `VincoliDelegati`, `PPTR_APPROVATO`, `UsiCivici`, `PAI`; `Operationals2/AreeVincoloIdrogeologico`, `VincoliTotale`, `PTA2019_Vincoli`, `DistrettiIrrigui`, `InventarioForestale`; `Operationals3/CartaPedologica`; CKAN `uso-del-suolo-2011-uds` | Olive land-use polygons; landscape and hydrogeological constraints that gate a replant permit | not probed this session | A replant inside a vincolo needs a separate authorization. The product's "next authorized action" is incomplete without it. Breadth work, not correctness work. | **open** (ArcGIS) / **open** (CKAN SHP) |
| 18 | Structure and environment layers | Meta/WRI 1 m canopy tiles; ESA WorldCover; Copernicus CDS AgERA5; SPEI; OSM/Overpass; GBIF | Canopy structure, land cover, weather, occurrence | not probed this session | Research-program inputs. `CORDON.md` scopes them out of the eligibility engine. Listed for completeness only. | **open**, large |

### 2.2 What the delta means for the product's current answers

The overlap test in §1.8 is honest and it is also the point. The build's 36 parcels sit in three
comuni chosen for the demo. Inside that set the missing sources change nothing. The moment the
product serves a parcel in Triggiano, Capurso, Noicattaro, Santeramo in Colle, or Ginosa, it returns
"no demarcated zone" for a parcel that is legally inside one. That failure is silent: the engine has
no row that says "a subspecies layer exists that I do not read", so the answer looks complete.

The same shape applies to `ElencoTerreniDGR17802019`. The product tells an Ostuni member what evidence
is missing without knowing whether the parcel already carries a lettera-b communication, and 83 Ostuni
parcels do.

### 2.3 Coverage arithmetic

The build touches 4 of 194 live SIT services. Of the 5 xylella-specific zone and register services
that carry legal or administrative state per parcel — `DatiPubbliciFasceXF`, `DatiPubbliciFasceXFF`,
`DatiPubbliciFasceXFMultiplex`, `DatiPubbliciFasceXFBandoPSR`, `ElencoTerreniDGR17802019` — it
ingests 2. Of the 6 monitoring services it ingests 1, as a local extract only. Of the demarcated
area published by the region, it holds the *pauca* share and none of the ~526 km² that is not *pauca*.

### 2.4 On contradiction C6

`MonitoraggioXFSintesiAttuale/1` returns 210 and `MonitoraggioXFSintesi/1` returns 340. The audit
recorded 210 and 340 from what it believed were two forms of the same query and concluded counts
move intraday. The likelier reading is that the 340 came from the 2025 layer in the sibling service.
If so, the recorded "counts move intraday; treat as live" caveat is an artifact and the layers are
stable. This is inference from two counts, not a reproduction of the original probe.

### 2.5 Why the failure happened

The audit documents are bound to the build by four prose references (§1.3). None of them is an
enumeration the build can check itself against. `AGENTS.md` §Data sources then restates the universe
in eight bullets, and that restatement is narrower than its own cited evidence: it names one *pauca*
zone service and omits four services the audit lists by name.

So the build has two descriptions of its data universe. The complete one lives in another repository
and is read once, at design time. The narrow one lives in the operating manual and is read every
session. The narrow one wins, because it is closer to the work and because nothing detects the
divergence.

That is the mechanism. It is not a missing reference. It is an unchecked second copy.

---

## STEP 5 — THE STRUCTURAL FIX

The rule this violates is already in `AGENTS.md`: "Non-negotiables live in the pipeline. A rule that
must always hold is a platform enforcement — Data Expectation, submission criterion, schema
constraint — not prose." The universe of sources is such a rule and it is currently prose. Six
changes, in dependency order. All are recommendations; nothing below has been written.

**1. Create `wedge1-aip/data/SOURCE_REGISTER.csv`.** One row per discovered source, tracked in git.
Columns: `source_id`, `endpoint`, `service_folder`, `layer_ids`, `authoritative_for`, `subspecies`,
`live_status`, `live_record_count`, `last_probed_at`, `ingested` (`yes`/`no`), `ingested_into`,
`exclusion_reason`, `discovered_in` (the audit file and line that first recorded it), `license`.
Seed it from §1.4 and §1.6 of this file. `exclusion_reason` is mandatory when `ingested=no`; a blank
is a defect, which is what makes "we did not look" impossible to express silently.

**2. Delete the enumeration in `AGENTS.md` §Data sources, lines 68–73.** Replace the whole block with
a pointer to `data/SOURCE_REGISTER.csv`. Doctrine ranks delete above replace. The narrow second copy
is the defect; refining it leaves the divergence mechanism intact.

**3. Add `wedge1-aip/scripts/probe_source_register.sh`.** It reads every row with a machine endpoint,
issues `{service}/MapServer?f=json` and `returnCountOnly` per layer, writes
`data/extracts/source_register_probe.json`, and exits non-zero when a live status or count differs
from the register. Add it to the `AGENTS.md` §Session rituals preflight, beside the token probe. A
register nobody re-probes decays into the same stale prose within a month.

**4. Add a register gate to `reviews/REVIEW_WORKFLOW.md`.** Define a *register claim*: any assertion
of the form "the source publishes only X", "no dataset exists for Y", "Z is gated". A register claim
PASSes only when `SOURCE_REGISTER.csv` carries a row supporting it with `last_probed_at` within seven
days. Otherwise it is a finding, in the same class as a wrong decree attribution. This is the gate
that would have caught the *pauca*-only assertion and the RUOP-gated verdict (C5), and it is
evaluable, which the doctrine requires of any enforcement.

**5. Add a platform Data Expectation tying zone rows to the register.** On the zones dataset, assert
`row_count` equals the count of register rows where `authoritative_for='demarcated_zone'` and
`ingested='yes'`. Adding `DatiPubbliciFasceXFF` to the register with `ingested=no` then forces an
explicit `exclusion_reason`; flipping it to `yes` without loading the rows fails a check. The
enforcement is derived from the same artifact as the data, which is the named cure for the recurring
finding class recorded in `BUILD_STATE.md` §Escalations ("enforcement is re-created per cycle from a
remembered list rather than derived from the same source as the data").

**6. Amend `PRODUCT_AUTHORITY.md` §Design of record.** Change the Basis line to name
`data/SOURCE_REGISTER.csv` as the binding enumeration, with the three `DATA_UNIVERSE_*.md` files as
its provenance rather than as the authority itself. An authority chain that points at a document in
another repository cannot be checked by anything in this one.

Owen signs off on 2 and 6, since both edit authority-chain files. 1, 3, 4, 5 are Connor-authored,
Ferro-implemented for the platform half.

**What each change would have prevented.** 1 makes the omission visible on disk. 2 removes the copy
that caused it. 3 makes staleness detectable. 4 blocks the claim at review. 5 blocks it at the
pipeline. 6 makes the register the thing the build is accountable to.

---

## FETCH LOG

Failures and degraded responses, this session. Successful fetches are listed in §1.6.

| Target | Failure mode |
|---|---|
| `Operationals3/MonitoraggioXFSintesiPrecedenti/MapServer?f=json` | HTTP 200 with an Esri error body; my parser printed `ERR:None` because the error object carried no `message`. The service does not exist under that name. `DATA_UNIVERSE_GEO.md` line 24 names it. Real services: `Operationals3/MonitoraggioXFFSintesiPrecedenti` and `Operationals3/MonitoraggioXFMultiplexSintesiPrecedenti`. |
| `Operationals2/MonitoraggioXF{,F,Multiplex}SintesiAttuale/MapServer/0/query?...returnCountOnly=true` | HTTP 200, body `{"error":{"code":400,"message":"Invalid or missing input parameters.","details":[]}}` on all three. Layer 0 ("Campionamento 2026") is a group or raster-like layer and does not accept a feature query. Matches the audit's note about `MonitoraggioXFSintesi` L0 returning 400. Counts in §1.6 are from layer 1 of each service. |
| Per-parcel point-in-polygon loop, 36 parcels × 5 unused zone layers | Timed out after 180 s at 180 sequential HTTPS requests. Replaced with three per-comune envelope-intersect queries (§1.8), which is a superset test: an envelope containing every parcel in a comune returned 0 for every unused layer, so no parcel intersects. Result is sound; the finer test was not run. |
| `pyproj` for EPSG:32633 → EPSG:4326 | `ModuleNotFoundError: No module named 'pyproj'`. Not installed, and installing it is a write outside the permitted scope. Worked around with `outSR=4326` on the ArcGIS query, which is server-side and authoritative. |
| `https://opencoesione.gov.it/it/opendata/api/progetti/?q=xylella` | HTTP 403, 30-byte body. US IP geo-block, unchanged from the 2026-08-16 audit. |
| `https://cartografia.sit.puglia.it/doc/xylella/` | HTTP 403, 218-byte body. Directory listing disabled, unchanged. Exact filenames still resolve per the audit. |
| `https://dati.anticorruzione.it/opendata/dataset` | HTTP 200 but only 269 bytes — a redirect or JS shell, not the dataset index. The audit records a WAF that rejects a plain curl UA. Not re-probed with a browser UA; ANAC content is unverified this session. |
| Foundry platform datasets | Not read. Reading `readTable` requires the Ferro credential and this task is scoped read-only against the repo. Platform row counts in §1.5 are quoted from `RID_LEDGER.md` health-check entries dated 2026-08-17, not re-verified live. |
| `data/acts/decrees.csv` vs platform `decrees` | Local CSV holds 14 rows; `RID_LEDGER.md` records `decrees master rowcount=23`. Same divergence on `measures` (local 3, platform 6). The local CSVs predate the W2 remediation. Source-URL analysis in §1.5 uses the local files, so the decree source list may under-report the six focolaio institution acts added during remediation. |
| `Operationals/Vincoli`, `VincoliDelegati`, `PPTR_APPROVATO`, `UsiCivici`, `PAI`, `Operationals2/AreeVincoloIdrogeologico`, `VincoliTotale`, `PTA2019_Vincoli`, `DistrettiIrrigui`, `InventarioForestale`, `Operationals3/CartaPedologica`, `ServicesArcIMS/UDS2011`, `UDS2006`, BaseMaps orthophotos | Not probed. Deprioritised as breadth rather than correctness. Row 17 of the delta table carries no live counts and says so. |
| Meta/WRI canopy tiles, ESA WorldCover, Copernicus CDS, SPEI, GBIF, CORDIS, Zenodo bulk search, FarmSubsidy, EmPULIA, MIMIT albo cooperative, giustizia-amministrativa.it | Not probed. Out of the eligibility engine's scope per `CORDON.md`. Row 18 and rows 13–14 carry no live counts. |

# Puglia Xylella fronts and 2026 monitoring — current-state recon

**As-of:** 23 August 2026. **Scope:** all published Puglia demarcation services, current 2026 plant-monitoring services, 2026 vector bulletins, BURP institution/prescription acts found by recursive catalog and citation-edge review. **Read-only.**

## Class 3 — model-memory claims with no fetched source

None are used as findings. Any unresolved item is marked **GAP**, not completed from memory.

## Class 2 — inferences from fetched pages

1. **The operational geography is multi-front.** The current zone catalog resolves to **14 legally or geometrically distinct fronts/areas**: ex-Salento containment; the Mola di Bari–Noci eradication satellites within that system; seven separately instituted pauca eradication areas (Bari, Minervino Murge, Modugno, Bisceglie, Giovinazzo, Cagnano Varano, Valenzano); one fastidiosa ST1 area; and four multiplex ST26 areas (Noicattaro–Triggiano, Capurso, Santeramo in Colle, Ginosa). This count treats Mola–Noci as the single combined feature published in layer 12 and treats the unified fastidiosa polygon as one area.
2. **The current pauca polygon service has absorbed Valenzano without publishing a Valenzano-named layer.** DDS 2/2026 legally institutes Valenzano, while the live `DatiPubbliciFasceXF` service exposes no named Valenzano pair. Its “Modugno” zone geometry intersects Valenzano and Capurso as well as Modugno, Bitonto and Bari. Therefore legal act identity and current geometry-layer label cannot be treated as the same identifier.
3. **Fresh positives are not confined to northern eradication fronts.** Of 210 current 2026 pauca positives, 72 are in Crispiano, one in Massafra and two in Alberobello. These are ex-Salento infected/containment geography, not only the northern Bari/Gargano fronts. Mola di Bari adds another 27 positives on the northern edge of the ex-Salento system. The correct answer to the Salento-result question is **yes: current-campaign positive records and linked confirmation documents exist in ex-Salento comuni**.
4. **“Density” is currently defensible as positive concentration, not prevalence.** The public current-positive layers expose positive points but do not publish a denominator joined by comune in the same layer. Percentages below are shares of all currently published positives for that subspecies, not infection prevalence among tested plants.
5. **A cooperative manager can realistically span recovery and duty regimes at once.** A network operating across south/central Puglia may have members in Annex III/ex-Salento infected territory eligible for recovery/replanting pathways while other members, sometimes in adjacent Bari/Murge comuni, sit in active eradication buffers for pauca, fastidiosa or multiplex. Bari, Capurso, Triggiano and Valenzano are especially multi-front because current geometries overlap among subspecies.
6. **The strongest recovery anchors are stable infected-zone comuni, not new satellites.** Lecce and Brindisi provinces remain the broad recovery base; among the northern edge, Alberobello, Castellana Grotte, Locorotondo, Monopoli, Polignano a Mare and Putignano are the cleanest named Annex III/Article 6 candidates. The strongest duty anchors are Cagnano Varano (large fresh pauca cluster), Bari–Capurso–Triggiano–Valenzano (three-subspecies overlap), and Altamura–Cassano–Santeramo (active multiplex ST26).
7. **Published zone geometry lags monitoring events.** The current positive layers contain July 2026 pauca records, while the latest located ex-Salento map act is DDS 82 of 11 May 2026 and the live zone services expose no per-event update timestamp. A change detector must compare sample feeds, confirmation links, zone geometry and legal acts as separate sources rather than assume one synchronous publication transaction.

## Class 1 — facts fetched from live pages

### 1. Catalog saturation and source control

The ArcGIS root and all three requested folders were enumerated live. Relevant services found:

- `Operationals/DatiPubbliciFasceXF`
- `Operationals2/DatiPubbliciFasceXFF`
- `Operationals2/DatiPubbliciFasceXFMultiplex`
- `Operationals2/MonitoraggioXFSintesiAttuale`
- `Operationals2/MonitoraggioXFFSintesiAttuale`
- `Operationals2/MonitoraggioXFMultiplexSintesiAttuale`
- historical/sibling services `DatiPubbliciFasceXFBandoPSR`, `MonitoraggioXFSintesi`, `MonitoraggioXFFSintesiPrecedenti`, `MonitoraggioXFMultiplexSintesiPrecedenti`, `MonitoraggioXFMaglie`, `MonitoraggioXFPasp`, `MonitoraggioXFStampa`, and `MonitoraggioXFStampaCatasto`.

**Fetched evidence:**

- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals?f=pjson>  
  Verbatim fragment: `"name" : "Operationals/DatiPubbliciFasceXF"`
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2?f=pjson>  
  Verbatim fragments: `"name" : "Operationals2/DatiPubbliciFasceXFF"`, `"name" : "Operationals2/DatiPubbliciFasceXFMultiplex"`, `"name" : "Operationals2/MonitoraggioXFSintesiAttuale"`
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals3?f=pjson>  
  Verbatim fragments: `"name" : "Operationals3/MonitoraggioXFFSintesiPrecedenti"`, `"name" : "Operationals3/MonitoraggioXFMultiplexSintesiPrecedenti"`

`f=json`/`f=pjson` was used. Counts were controlled with `where=OBJECTID>0&returnCountOnly=true`. Query saturation is not claimed as proof that no unpublished or future service exists.

### 2. Current fronts

**Regime rule used below:** the broad ex-Salento infected territory listed for containment follows Articles 12–17/13–17; all separately delimited 50 m infected zones with 2.5 km buffers are eradication areas under Articles 7–11 unless a cited act says otherwise.

| # | Current front / area | Subspecies / ST | Comuni intersected by current published geometry (ZI; then buffer where different) | Institution / current act chain | Current geometry | Regime |
|---:|---|---|---|---|---|---|
| 1 | Ex-Salento broad infected + containment band | pauca ST53 | ZI intersects all comuni of Lecce and Brindisi plus the published Taranto/Bari edge; exact live intersection is listed below. Containment layer 14 intersects Alberobello, Castellana Grotte, Conversano, Crispiano, Martina Franca, Massafra, Mola di Bari, Monopoli, Mottola, Noci, Polignano a Mare, Putignano, Taranto. Buffer layer 13 additionally reaches Noicattaro and Turi. | Historical chain; DDS 18 (14 Mar 2024), DDS 158 (18 Nov 2024), latest DDS 82 (11 May 2026) | `Operationals/DatiPubbliciFasceXF/MapServer`: L15 ZI OID 6723; L14 containment OID 3202; L13 buffer OID 8963 | **Containment** in listed infected/containment zone; eradication in buffer/new 50 m satellites |
| 2 | Mola di Bari–Noci satellites in ex-Salento system | pauca ST53 | ZI: Mola di Bari, Noci | New infections handled under the current ex-Salento delimitation; Noci prescription DDS 24 (20 Feb 2025); latest map DDS 82/2026 | same service L12 OID 6724, combined feature | **Eradication** |
| 3 | Bari | pauca ST53 | ZI: Bari, Triggiano; buffer: Bari, Noicattaro, Triggiano | DDS 92 (22 Jul 2024) | same service L10 OID 4483; L11 OID 6403 | **Eradication** |
| 4 | Minervino Murge | pauca ST53 | ZI and buffer: Minervino Murge | DDS 59 (14 Apr 2025) | same service L8 OID 5123; L9 OID 7043 | **Eradication** |
| 5 | Modugno (expanded into Bitonto/Valenzano cluster) | pauca ST53 | ZI: Bari, Bitonto, Capurso, Modugno, Valenzano; buffer also Cellamare, Triggiano | DDS 126 (11 Jul 2025), update DDS 132 (18 Jul 2025); Bitonto prescription DDS 3 (12 Jan 2026) | same service L4 OID 7043; L5 OID 9283 | **Eradication** |
| 6 | Bisceglie | pauca ST53 | ZI: Bisceglie; buffer: Bisceglie, Trani | DDS 113 (23 Jun 2025), update DDS 141 (6 Aug 2025) | same service L6 OID 5766; L7 OID 8004 | **Eradication** |
| 7 | Giovinazzo | pauca ST53 | ZI and buffer: Giovinazzo | DDS 147 (12 Aug 2025) | same service L2 OID 6083; L3 OID 8323 | **Eradication** |
| 8 | Cagnano Varano | pauca ST53 | ZI and buffer: Cagnano Varano | DDS 163 (8 Oct 2025) | same service L0 OID 6084; L1 OID 8324 | **Eradication** |
| 9 | Valenzano legal area | pauca ST53 | Act annex: ZI in Capurso and Valenzano; buffer in Capurso, Cellamare, Triggiano, Valenzano. Current service has no Valenzano-named pair; geometry is intersected by L4/L5. | **DDS 2 (12 Jan 2026)** | no separately named live layer; use DDS annex plus L4/L5 with explicit identity caveat | **Eradication** |
| 10 | Bari–Triggiano–Noicattaro–Capurso unified fastidiosa area | fastidiosa ST1 | ZI: Bari, Capurso, Noicattaro, Triggiano; buffer also Cellamare, Valenzano | DDS 8 (21 Feb 2024); updates DDS 12, 45, 94/2024 and DDS 236 (18 Dec 2025) | `Operationals2/DatiPubbliciFasceXFF/MapServer`: L0 OID 961; L1 OID 961 | **Eradication** |
| 11 | Noicattaro–Triggiano | multiplex ST26 | ZI and buffer: Bari, Noicattaro, Triggiano | DDS 93 (23 Jul 2024) | `Operationals2/DatiPubbliciFasceXFMultiplex/MapServer`: L0 OID 643; L1 OID 323 | **Eradication** |
| 12 | Capurso | multiplex ST26 | ZI: Capurso; buffer: Bari, Capurso, Triggiano, Valenzano | DDS 93 (23 Jul 2024) | same service L0 OID 644; L1 OID 324 | **Eradication** |
| 13 | Santeramo in Colle / Murge | multiplex ST26 | ZI: Acquaviva delle Fonti, Altamura, Cassano delle Murge, Santeramo in Colle; buffer also Gioia del Colle, Laterza; cross-border buffer reaches Basilicata | DDS 29 (8 Apr 2024); updates 91, 148, 198/2024 and 106 (16 Jun 2025) | same service L0 OID 962; L1 OID 642; cross-border L2 OID 322 | **Eradication** |
| 14 | Ginosa | multiplex ST26 | ZI and Puglia buffer: Ginosa; cross-border buffer reaches Basilicata | DDS 198 (18 Dec 2024); update DDS 106 (16 Jun 2025) | same service L0 OID 961; L1 OID 641; cross-border L2 OID 321 | **Eradication** |

#### Exact ex-Salento ZI intersection from the current layer

The current L15 polygon intersects: Alberobello; every comune in Lecce province; every comune in Brindisi province; and the following Taranto/Bari-edge comuni visible in the live intersection: Avetrana, Carosino, Castellana Grotte, Conversano, Crispiano, Faggiano, Fragagnano, Grottaglie, Leporano, Lizzano, Locorotondo, Manduria, Martina Franca, Maruggio, Massafra, Mola di Bari, Monopoli, Monteiasi, Montemesola, Monteparano, Mottola, Noci, Palagianello, Palagiano, Polignano a Mare, Pulsano, Putignano, Roccaforzata, San Giorgio Ionico, San Marzano di San Giuseppe, Sava, Statte, Taranto, Torricella. The polygon intersection is spatial fact; Annex III remains the legal authority for containment status.

#### Zone-service evidence

- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/DatiPubbliciFasceXF/MapServer?f=pjson>  
  Verbatim fragments: `"Zona Infetta - Xylella Fastidiosa sub. pauca (Cagnano Varano)"`; `"Zona Infetta - Xylella Fastidiosa sub. pauca (Giovinazzo)"`; `"Zona Infetta - Xylella Fastidiosa sub. pauca (Modugno)"`; `"Zona Infetta - Xylella Fastidiosa sub. pauca (Bisceglie)"`; `"Zona Infetta - Xylella Fastidiosa sub. pauca (Minervino Murge)"`; `"Zona Infetta - Xylella Fastidiosa sub. pauca (Bari)"`; `"Zona Infetta - Xylella Fastidiosa sub. pauca ST53 ex Salento (Focolai di Mola di Bari e Noci)"`.
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/DatiPubbliciFasceXFMultiplex/MapServer/0/query?where=OBJECTID%3E0&outFields=*&returnGeometry=false&f=json>  
  Verbatim fragments: `"Area delimitata Xyella fastidiosa sub. multiplex (Noicattaro-Triggiano) - Zona Infetta"`; `"(Capurso) - Zona Infetta"`; `"(Ginosa) - Zona Infetta"`; `"(Santeramo in Colle) - Zona Infetta"`.
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/DatiPubbliciFasceXFF/MapServer?f=pjson>  
  Verbatim fragments: `"Zona Infetta - Xylella Fastidiosa sub. fastidiosa"`; `"Zona Cuscinetto - Xylella Fastidiosa sub. fastidiosa"`.

#### Act evidence

- DDS 2/2026: <https://burp.regione.puglia.it/documents/20135/2735532/DET_2_12_1_2026_FITO.pdf/85d5418e-aa6d-7988-3010-695f84b8681f?t=1770063167003>  
  Verbatim: `Di istituire l’area delimitata per “Xylella fastidiosa sottospecie pauca ST 53 – Valenzano (BA)”` and `Di dovere adottare ... le misure di eradicazione di cui agli articoli da 7 a 11`.
- DDS 3/2026: <https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0>  
  Verbatim: `Di prescrivere nell’agro di Bitonto (BA) esclusivamente le misure di eradicazione` and `è incluso nella zona infetta dell’area delimitata ... Modugno`.
- DDS 93/2024: <https://burp.regione.puglia.it/documents/20135/2509064/DET_93_23_7_2024.pdf/c860aa7b-f31f-1f16-2634-453d7ed7a053?t=1722517882921&version=1.0>  
  Verbatim: `Di istituire due nuove aree delimitate ... “Noicattaro e Triggiano” e ... “Capurso”` and `Di adottare ... misure di eradicazione di cui agli articoli da 7 a 11`.
- DDS 198/2024: <https://burp.regione.puglia.it/documents/20135/2564917/DET_198_18_12_2024.pdf/aa3ccfd5-c143-061f-4f97-f2f80ca1c3cd?t=1735300377495&version=1.0>  
  Verbatim: `Aggiornamento dell’area delimitata ... Santeramo in Colle e Istituzione ... Ginosa`.
- DDS 24/2025: <https://burp.regione.puglia.it/documents/20135/2605848/DET_24_20_2_2025.pdf/575a1cb2-0755-5733-985d-77d8911f93bf?t=1740675033380&version=1.0>  
  Verbatim: `Prescrivere nell’agro di Noci (BA) esclusivamente le misure di eradicazione`.

### 3. Current 2026 plant-monitoring results

Live controls at fetch time:

- pauca positive layer count: **210**
- fastidiosa positive layer count: **13**
- multiplex positive layer count: **10**
- total current positives: **233** across **13 unique comuni**

The point-to-comune assignment was performed by intersecting each EPSG:32633 point with `Operationals2/MonitoraggioXFStampaCatasto/MapServer/2` (`NOME_COM`).

| Subspecies | Comune | Current positives | Share of subspecies positives | Sample dates present | Host | Confirmation/report examples |
|---|---|---:|---:|---|---|---|
| pauca | Cagnano Varano | 98 | 46.7% | 12 Jan–22 Jul | olive | IDs include 1931212, 1964340, 1963970; CNR 2P, 3P, 4P, 6P, 56P, 63P/2026 |
| pauca | Crispiano | 72 | 34.3% | 1 Feb–20 Apr | olive | IDs include 1938058, 1940368, 1962008; CNR 9P–45P/2026 series |
| pauca | Mola di Bari | 27 | 12.9% | 20 Apr–15 Jun | olive | IDs 1961788–1963384 range visible; CNR 41P and 55P/2026 |
| pauca | Valenzano | 7 | 3.3% | 19 Feb | olive | IDs 1944733, 1944736, 1944753, 1944756, 1944758, 1944762, 1944763; CNR 20P/2026 |
| pauca | Bari | 3 | 1.4% | 15 Jun, 26 Jul | olive | IDs 1963348, 1963349, **1964901**; CNR 55P and 64P/2026 |
| pauca | Alberobello | 2 | 1.0% | 23–26 Mar | olive | IDs 1956937, 1957882; CNR 32P and 38P/2026 |
| pauca | Massafra | 1 | 0.5% | 12 Feb | olive | ID 1942802; CNR 19P/2026 |
| fastidiosa | Triggiano | 7 | 53.8% | 3 Feb | vine | IDs 1939917–1939956; CNR 11F/2026 |
| fastidiosa | Capurso | 5 | 38.5% | 18 Feb, 22 Apr | vine | IDs 1944586, 1944587, 1962270, 1962276, 1962277; CNR 20F, 46F/2026 |
| fastidiosa | Bari | 1 | 7.7% | 17 Feb | almond | ID 1943903; CNR 19F/2026 |
| multiplex | Santeramo in Colle | 4 | 40.0% | 20 Apr | almond | IDs 1961653, 1961709, 1961964, 1961973; CNR 46M/2026 |
| multiplex | Cassano delle Murge | 3 | 30.0% | 27 Apr | almond | IDs 1962608, 1962621, 1962623; CNR 46M, 47M/2026 |
| multiplex | Noicattaro | 2 | 20.0% | 11 Feb | almond | IDs 1942499, 1942501; CNR 14M/2026 |
| multiplex | Altamura | 1 | 10.0% | 20 Apr | almond | ID 1961650; CNR 46M/2026 |

**Direct answer on ex-Salento:** yes. Crispiano, Massafra and Alberobello have current 2026 positive records and linked `DOCUMENTO_CONFERMA` values. Mola di Bari also has current positives in the combined Mola–Noci satellite geometry. Therefore “fresh positives effectively only on the northern fronts” is false.

**What is not exposed:** the public layers do not carry an explicit `RESAMPLE_OF`, buffer-version, or act identifier. Their fields are `RISULTATO`, `DATA_CAMPIONE`, `SQUADRA`, `ID_CAMPIONE`, `SPECIE`, `SINTOMI`, `PROTOCOLLO`, and `DOCUMENTO_CONFERMA` (plus laboratory field in fastidiosa/multiplex). Confirmations exist as linked reports. Resample relationships and the exact positive→buffer-update→act transaction remain **GAP**.

**Fetched evidence:**

- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/MonitoraggioXFSintesiAttuale/MapServer/1/query?where=OBJECTID%3E0&returnCountOnly=true&f=json>  
  Verbatim: `{"count":210}`
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/MonitoraggioXFFSintesiAttuale/MapServer/1/query?where=OBJECTID%3E0&returnCountOnly=true&f=json>  
  Verbatim: `{"count":13}`
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/MonitoraggioXFMultiplexSintesiAttuale/MapServer/1/query?where=OBJECTID%3E0&returnCountOnly=true&f=json>  
  Verbatim: `{"count":10}`
- URL: <https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/MonitoraggioXFSintesiAttuale/MapServer/1?f=pjson>  
  Verbatim field names: `"ID_CAMPIONE"`, `"PROTOCOLLO"`, `"DOCUMENTO_CONFERMA"`.

### 4. Vector-monitoring bulletin state

The 2026 series is current through **VI rilievo oliveti / V rilievo vigneti, 20–24 July 2026**, transmitted 31 July. The portal no longer stops at the 29 May II-rilievo document. Cadence is a sequence of named field rounds, not a guaranteed weekly publication SLA: the latest bulletin calls the work a `Rilievo settimanale`, while the public series advances by I–VI rounds over May–July.

- Portal: <http://www.emergenzaxylella.it/portal/portale_gestione_agricoltura>  
  Verbatim: `Risultati del monitoraggio dei vettori dal 20 al 24 luglio 2026.`
- Latest PDF: <https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/Trasmissione%20dati%20vettori%20VI%20rilievo%20con%20allegati_signed.pdf>  
  Verbatim: `Trasmissione dati V rilievo vigneti e VI rilievo oliveti 20-24 luglio 2026.` and `Gli individui catturati ... saranno sottoposti a saggio diagnostico per X. fastidiosa.`
- II-rilievo PDF: <https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/Trasmissione%20dati%20vettori%20II%20rilievo%20&%20allegati.pdf>  
  Verbatim: `I rilievo vigneti 11-25 maggio 2026 e II rilievo oliveti 25-29 maggio 2026.`

The latest bulletin monitors 30 olive sites and 12 vineyard sites, including current fronts and controls from Crispiano, Massafra, Ginosa, Minervino, Cagnano Varano, Giovinazzo, Bari, Bitonto, Bisceglie, Noicattaro, Triggiano, Valenzano, Santeramo, Cassano and Acquaviva. It reports adult catches; diagnostic positivity follows later, so vector abundance is not the same fact as an infected vector.

### 5. Operator geography

#### Recovery trajectory — Article 6 / infected-zone replanting anchors

Strongest concrete anchors:

1. **Province-wide Lecce and Brindisi cooperative networks.** Their legal geography is stable broad infected territory rather than a small moving eradication buffer.
2. **Alberobello, Castellana Grotte, Locorotondo, Monopoli, Polignano a Mare, Putignano.** These are the named Bari-province Annex III containment comuni and are strong parcel-level Article 6 candidates, subject to the measure’s separate eligibility, cultivar, monumentality, funding-window and authorization tests.
3. **Crispiano and Massafra.** They are operationally important because the current campaign is still finding positives there (72 and 1 respectively), proving that “recovery geography” remains an active surveillance and containment geography rather than a post-epidemic static zone.

#### Duty trajectory — active eradication/containment anchors

1. **Cagnano Varano:** 98 current pauca positives, including a 22 July batch, inside a separately delimited eradication area.
2. **Bari–Capurso–Triggiano–Valenzano:** overlapping pauca, fastidiosa ST1 and multiplex ST26 geometries; a manager can face different host rules and removal/movement duties across nearby parcels.
3. **Altamura–Cassano delle Murge–Santeramo in Colle:** active multiplex ST26 with fresh April positives and a very large eradication geometry.
4. **Modugno–Bitonto:** the current “Modugno” area includes Bitonto; DDS 3/2026 expressly applies eradication, not containment, to the Bitonto positive.
5. **Bisceglie–Trani and Giovinazzo:** separate pauca eradication fronts with coastal cooperative/logistics relevance.

**Operator verdict:** a Puglia cooperative should be designed as **multi-front by default**. “One cooperative = one zone/regime” is unsafe. Membership, parcels, hosts, samples, zone versions, act versions and duties must be bound independently.

### 6. Candidate-binding table

| Event type | Strong candidate | Why it is strongest | Concrete binding: comune / layer / sample | Act reference |
|---|---|---|---|---|
| Fresh-monitoring-positive change | **Cagnano Varano pauca** | Largest current cluster and a new 22 July batch; isolated Gargano front makes geometry/legal change detection unambiguous | `MonitoraggioXFSintesiAttuale/MapServer/1`; 98 positives; July IDs include 1963970, 1963971, 1963976, 1964016, 1964064, 1964340, 1964341; confirmations CNR 63P/2026. Zone `DatiPubbliciFasceXF` L0 OID 6084 / L1 OID 8324 | DDS 163, 8 Oct 2025; next update/prescription act is a watch target |
| Fresh-monitoring-positive change | **Bari pauca** | Latest dated plant positive fetched (26 July) and overlaps other subspecies/fronts | sample **1964901**, 26 Jul 2026, CNR **64P/2026**; zone L10 OID 4483 / L11 OID 6403 | DDS 92, 22 Jul 2024; compare any post-26-Jul update |
| Fresh-monitoring-positive change | **Crispiano pauca / ex-Salento** | Proves current-campaign positives exist in containment geography; high concentration (72) | current-positive layer 1; examples 1938058, 1940368, 1962008; ex-Salento L15 OID 6723 / L14 OID 3202 | DDS 82, 11 May 2026 current map; containment prescriptions under Art. 13 |
| Stale-source event | **CKAN monitoring package vs Cagnano/Bari/Crispiano live feeds** | CKAN metadata/resources stop before the 2026 campaign while ArcGIS contains July 2026 confirmations | CKAN package `dati-monitoraggio-xylella-fastidiosa`; resource `fe41c298-e6b4-4728-ba19-50d17e411372` = `CAMP_2020_2022.csv`; resource `2ffb6c35-bae0-4890-abc1-0bc0b87a6eb9` = `CAMP_2020_2023.csv` with empty URL; compare to sample 1964901 or Cagnano July batch | DDS 82/2026, DDS 163/2025, DDS 92/2024 as applicable |
| Stale-source event | **Valenzano legal area vs unnamed zone layer** | Legal area exists, but no Valenzano-named layer is published; ideal stale/identity mismatch test | DDS annex ZI Capurso+Valenzano; current service uses L4/L5 “Modugno” and intersects Valenzano; current samples 1944733 etc., CNR 20P/2026 | DDS 2, 12 Jan 2026 |

CKAN evidence: <https://dati.puglia.it/ckan/api/3/action/package_search?q=xylella> — verbatim values `"metadata_modified": "2025-09-17T01:56:05.119643"`, `"name": "CAMP_2020_2023.csv"`, and `"url": ""` for resource `2ffb6c35-bae0-4890-abc1-0bc0b87a6eb9`.

### 7. New/previously uncatalogued findings

1. The live multiplex geometry publishes **four**, not two, ST26 areas: Noicattaro–Triggiano and Capurso are separate current features in addition to Santeramo and Ginosa. DDS 93/2024 institutes both omitted areas.
2. The 2026 pauca current-positive feed includes **Crispiano (72), Massafra (1), and Alberobello (2)** inside ex-Salento infected/containment geography. Current results are not northern-only.
3. The pauca service has **no Valenzano-named layer** despite DDS 2/2026. Current Modugno-labelled geometry intersects Valenzano and Capurso, creating a legally material identity mismatch.
4. The vector series is current through **20–24 July (VI oliveti / V vigneti)**, not 29 May.
5. The live current-positive services expose **233 positives across 13 comuni** and direct diagnostic-document links, whereas the CKAN package remains a stale annual/historical channel.

## Fetch-failure log

| URL | Exact failure | Recovery attempted / result |
|---|---|---|
| <https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/Trasmissione%20dati%20vettori%20VI%20rilievo%20con%20allegati_signed.pdf> via `web_extract` | `Crawl4ai HTTP 500: {"error":"Internal server error","correlation_id":"d39bf7b82801"}` | Recovered with direct `curl | pdftotext`; text quoted above. |
| <https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/Trasmissione%20dati%20vettori%20II%20rilievo%20&%20allegati.pdf> via `web_extract` | `Crawl4ai HTTP 500: {"error":"Internal server error","correlation_id":"ad33f6739c69"}` | Search index and direct PDF endpoint both resolved; relevant fragment quoted. |
| <https://burp.regione.puglia.it/documents/20135/2798636/DET_82_11_5_2026.pdf> via `web_extract` | `Crawl4ai HTTP 500: {"error":"Internal server error","correlation_id":"346130649a2f"}` | DDS number/date and scope cross-checked against BURP-indexed act references, live geometry and current local primary-source register; exact guessed short URL is not treated as fetched text. |
| <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02020R1201-20251124> | `Crawl4ai extraction failed:` | Italian endpoint returned the temporary EUR-Lex outage page; legal comune claims were therefore tied to current SIT geometry and fetched BURP acts, with Annex III called out as the controlling source rather than silently reconstructed. |
| <https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:02020R1201-20251124> | EUR-Lex page stated `EUR-Lex is temporarily not fully available.` | No unsupported Annex text was invented. |
| Browser-use attempt for direct Python extraction | `Cloud browser provider BrowserUseBrowserProvider returned no CDP endpoint` | Recovered through direct ArcGIS REST and direct HTTP/PDF extraction. |

## Bottom line

Puglia does not have one northward front. It has a broad ex-Salento containment system, a combined Mola–Noci eradication edge, seven pauca eradication areas, one multi-comune fastidiosa ST1 area and four multiplex ST26 areas. Current 2026 results land in both northern eradication fronts and ex-Salento containment comuni. A cooperative manager is therefore realistically multi-front and multi-regime, and the data model must bind each parcel and sample to both a time-versioned geometry and a separate legal act.
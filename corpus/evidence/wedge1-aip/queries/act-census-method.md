# ActUniverseCoverage — is the Regione Puglia Xylella act corpus enumerable?

Read date: 2026-08-19. Read-only investigation. No platform writes, no commits.

**Answer: yes.** BURP exposes a server-rendered per-issue sommario keyed by an integer
`burpId`. Every issue since 1999 is reachable. Every act in an issue carries a section, a
title with type/date/number, an oggetto, and a direct PDF URL. This investigation executed
the full census rather than describing it: 2,515 issues fetched, 72,346 acts enumerated,
791 Xylella-relevant acts identified, 665 of them operative.

The corpus estimate the build was carrying — 2,000–3,500 acts touching Xylella, 400–800
operative — is wrong on the first number. The measured act universe is 791.

---

## CLASS 3 — ASSERTED FROM MODEL MEMORY, NO FETCHED SOURCE

**none.**

Every number, URL, endpoint, field name and quoted fragment below came from a call made
during this investigation. Where a fact is derived rather than read, it is in Class 2 and
its inputs are named. Where a question could not be answered, it is in the fetch log or
marked open.

---

## CLASS 1 — QUOTED FROM A SOURCE I ACTUALLY FETCHED

### 1.1 The issue index is enumerable by year

`GET https://burp.regione.puglia.it/` → HTTP 200, 196,706 bytes. The year selector in the
search form bounds the archive:

```html
<select ... name="_it_indra_regione_puglia_burp_web_SearchPortlet_bolanno" >
<option value="" ><option value="2026" ><option value="2025" > ... <option value="1999" >
```

Pagination links on the same page reveal archive depth. The last page link at `delta=10` is:

```
..._SearchPortlet_delta=10&_it_indra_regione_puglia_burp_web_SearchPortlet_cur=518
```

Filtering by year works through the same URL shape. Fetched for each year 2013–2026:

```
https://burp.regione.puglia.it/bollettini
  ?p_p_id=it_indra_regione_puglia_burp_web_SearchPortlet
  &p_p_lifecycle=0&p_p_state=normal&p_p_mode=view
  &_it_indra_regione_puglia_burp_web_SearchPortlet_bolanno=2015
  &_it_indra_regione_puglia_burp_web_SearchPortlet_delta=200
  &_it_indra_regione_puglia_burp_web_SearchPortlet_cur=1
```

HTTP 200. Measured issue counts (`burpId` values, deduplicated, paginated to exhaustion):

| year | issues | year | issues |
|---|---|---|---|
| 2013 | 190 | 2020 | 237 |
| 2014 | 199 | 2021 | 229 |
| 2015 | 188 | 2022 | 217 |
| 2016 | 178 | 2023 | 159 |
| 2017 | 183 | 2024 | 140 |
| 2018 | 187 | 2025 | 136 |
| 2019 | 173 | 2026 | 99 (to 17/08) |

**Total 2013–2026: 2,515 issues.**

Each listing row carries the issue label, publication date and both links:

```html
<h2 class ="titolo">
  Bollettino Ufficiale della Regione Puglia n° 114/2015 vol. 5
</h2>
...
<span class="data-label" >Data pubblicazione:</span> <span class="data-news" >12 agosto 2015</span>
...
<a href="https://burp.regione.puglia.it/bollettini?...&_it_indra_regione_puglia_burp_web_SearchPortlet_burpId=3225">
  <span>Visualizza BURP</span></a>
...
<a href="https://burp.regione.puglia.it/documents/20135/894100/Bollettino+numero+114+-+Ordinario+-+volume+5+-+anno+2015.pdf/91300ab1-6781-b544-a148-de74d6834a3e?t=1622800401471"
   title="Scarica BURP (41,6 MB)">
```

### 1.2 The sommario is machine-readable — this is the census route

`GET` with `mvcRenderCommandName=/view-burp/bollettino/detail` and a `burpId`:

```
https://burp.regione.puglia.it/bollettini
  ?p_p_id=it_indra_regione_puglia_burp_web_SearchPortlet
  &p_p_lifecycle=0&p_p_state=normal&p_p_mode=view
  &_it_indra_regione_puglia_burp_web_SearchPortlet_mvcRenderCommandName=%2Fview-burp%2Fbollettino%2Fdetail
  &_it_indra_regione_puglia_burp_web_SearchPortlet_burpId=10769
```

HTTP 200, 247,363 bytes, fully server-rendered. No JavaScript needed. Real fragment:

```html
<h1>Bollettino  n° 59  del 27/07/2026</h1>
...
<div class="card card-burp">
  <span class="collapse-title">Deliberazioni della Giunta regionale</span>
  ...
  <div class="doc-element">
    <h2>DELIBERAZIONE DELLA GIUNTA REGIONALE 1 luglio 2026, n. 916</h2>
    <a href="https://burp.regione.puglia.it/documents/20135/2817336/DEL_916_2026.pdf/ab6f9668-d8f4-b868-e1ac-31a9dd9bf4df?version=1.0&t=1785157747683"
       title="Scarica (1,1 MB)">
       <span><!-- DEL_916_2026.pdf -->Scarica</span></a>
```

Parsed record for that act:

```json
{"section": "Deliberazioni della Giunta regionale",
 "title": "DELIBERAZIONE DELLA GIUNTA REGIONALE 1 luglio 2026, n. 916",
 "pdf": "https://burp.regione.puglia.it/documents/20135/2817336/DEL_916_2026.pdf/ab6f9668-...",
 "filename": "DEL_916_2026.pdf",
 "body": "“Giornata in ricordo delle 23 vittime dell’incidente ferroviario del 12 luglio 2016”
          da tenersi nel Comune di Andria in data 12.07.2026.
          Sezione: Deliberazioni della Giunta regionale Argomenti: Mobilità e trasporti"}
```

Section breakdown for issue 59/2026, from the same page: Deliberazioni della Giunta
regionale 31, Decreti e ordinanze del Presidente 3, Determinazioni dirigenziali aventi
contenuto di interesse generale 1, Atti degli enti locali 5, Altri atti e avvisi 12,
Concorsi e Avvisi 4. Total 56 acts.

An operative Xylella act renders with an oggetto specific enough to classify without
opening the PDF:

```
Bollettino n° 153 del 22/11/2013
DELIBERAZIONE DELLA GIUNTA REGIONALE 29 ottobre 2013, n. 2023
Misure di emergenza per la prevenzione, il controllo e la eradicazione del batterio
da quarantena Xylella fastidiosa associato al "Complesso del disseccamento rapido dell'olivo".
```

```
Bollettino n° 102 del 15/09/2022
DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO 6 settembre 2022, n. 95
Reg. (UE) 2020/1201 - D.Lgs 19 del 02/02/2021 - D.G.R. 343/2022. Prescrizione di
estirpazione di piante infette da Xylella f. (art. 13 del Reg. (UE) 2020/1201) in agro di ...
https://burp.regione.puglia.it/documents/20135/1964689/DET_95_6_9_2022.pdf/4b2b81c1-...
```

### 1.3 Executed census — measured, not estimated

All 2,515 issue sommari fetched at concurrency 8. Zero fetch errors.

```
issues harvested: 2515 | errors: 0 | ok: 2515
distinct issues: 2515
TOTAL ACTS ENUMERATED 2013-2026: 72346
avg acts/issue 28.8
max acts in one issue 152
```

Two selectors were applied to title + oggetto.

Selector A, the disease is named:
`xylella | x. fastidiosa | disseccamento rapido dell`

Selector L, a Xylella legal instrument or zone term is cited:
`2020/1201 | 2015/789 | 2484/2020 | rigenerazione olivicola | reimpianto olivi |
zona infetta | zone infette | area delimitata | aree delimitate | philaenus |
sputacchin | piante infette`

```
Xylella-named (A): 640
Xylella-legal-instrument (L): 642
A and L: 491
L but NOT A (recall gap): 151
UNION A or L: 791
```

Operative classification over the 791, five facets, an act may hit several:

```
UNIVERSE (Xylella-relevant candidates) = 791
OPERATIVE (regex) = 665
NON-OPERATIVE residue = 126

  delimitation    127
  removal_order   478
  funding_window  100
  money            59
  vector_duty     252
```

Per year:

```
year | candidates | operative      year | candidates | operative
2013 |     1 |     1               2020 |   147 |   133
2014 |    10 |     4               2021 |   102 |    94
2015 |    26 |    14               2022 |    83 |    76
2016 |    18 |    11               2023 |    64 |    55
2017 |    18 |     8               2024 |    68 |    54
2018 |    24 |    13               2025 |    65 |    54
2019 |   120 |   111               2026 |    45 |    37
```

By act type: `DDS/DET 605, DGR 133, DAdG 25, ALTRO 18, LR 10`.

### 1.4 The recall gap is real and load-bearing

151 acts cite a Xylella legal instrument without naming the disease. Sampled examples,
all operative:

```
Bollettino n° 51 del 08/06/2023
DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO 1 giugno 2023, n. 59
Reg. (UE) 2020/1201 - D.Lgs 19 del 02/02/2021 - D.G.R. 1866/2022. Prescrizione di
misure di eradicazione ai sensi dell'art. 7 del Reg. (UE) 2020/1201 in agro di Castellan...
```

```
Bollettino n° 64 del 13/08/2026
DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO 28 luglio 2026
Misura "Reimpianto olivi zona infetta" di cui all'art. 6 del D.I. n. 2484/2020
"Piano straordinario per la rigenerazione olivicola della Puglia"
```

```
Bollettino n° 92 del 17/11/2025
DELIBERAZIONE DELLA GIUNTA REGIONALE 22 ottobre 2025, n. 1559
Reg.(UE)2021/690–Reg.(UE)2020/1201. Stanziamento di nuove risorse da destinare
all'indennizzo delle imprese vivaistiche, ...
```

### 1.5 The classifier under-counts operative acts

12 acts from the non-operative residue were sampled. At least 9 are operative in the
project's sense. Examples the regex missed:

```
LEGGE REGIONALE 8 Ottobre 2014, n. 41
"Misure di tutela delle aree colpite da xylella fastidiosa".
```

```
DELIBERAZIONE DELLA GIUNTA REGIONALE 21 aprile 2020, n. 548
Attuazione della decisione di esecuzione (UE) 789/2015 e s.m.i. "misure per impedire
l'introduzione e la diffusione di Xylella fastidiosa". Approvazione del Piano per
l'annualità 2020 ...
```

```
DELIBERAZIONE DELLA GIUNTA REGIONALE 11 novembre 2014, n. 2354
Emergenza fitosanitaria ... Autorizzazione della spesa ai fin...
```

### 1.6 RSS exists and carries burpId — this is the incremental route

```
https://burp.regione.puglia.it/rss-burp
  ?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_6xyRm0hhUqeb
  &p_p_lifecycle=2&p_p_state=normal&p_p_mode=view
  &p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage
```

HTTP 200, 151,218 bytes, `text/xml`. 100 items, newest `Bollettino n° 65 del 17/08/2026`,
oldest `Bollettino n° 105 del 30/12/2025`.

```xml
<item>
  <title>Bollettino n° 65 del 17/08/2026</title>
  <link>https://burp.regione.puglia.it/bollettini?...&amp;_it_indra_regione_puglia_burp_web_SearchPortlet_mvcRenderCommandName=%2Fview-burp%2Fbollettino%2Fdetail&amp;_it_indra_regione_puglia_burp_web_SearchPortlet_burpId=10777&amp;redirect=...</link>
  <description>Bollettino n° 65 del 17/08/2026</description>
  <pubDate>Mon, 17 Aug 2026 00:00:00 GMT</pubDate>
  <dc:creator>Maddea Miccolis</dc:creator>
  <dc:date>2026-08-17T00:00:00Z</dc:date>
</item>
```

Newest item is 2 days old at read time, consistent with BURP's own publication cadence
rather than feed lag.

### 1.7 The annex hash is real, and it starts in 2024

Confirmed present in three acts fetched and text-extracted.
`DET_51_24_3_2026.pdf` (4,089,903 bytes), verbatim:

```
ALLEGATI INTEGRANTI

Documento - Impronta (SHA256)
ALLEGATO 1_.pdf -
a3c1caeb11fff54947e158c63fcf74f14fb57cf7b9565ee03d3cb83be11387dd

Il presente Provvedimento è direttamente esecutivo.
```

Same page names the producing platform and the signer:

```
Il presente atto, elaborato attraverso la piattaforma CIFRA2, composto da pagine tutte
progressivamente numerate e dall'allegato 1 (1/A e 1/B), firmato digitalmente e adottato
in unico originale:
...
Come Proposta: Codice Cifra 181/DIR/2026/00053
Sottoscrittori Proposta:
 • E.Q. "Gestione dell'emergenza fitosanitaria Xylella fastidiosa pauca"
   Francesco Palmisano
Firmato digitalmente da:
Il Dirigente della Sezione Osservatorio Fitosanitario
Salvatore Infantino
```

Coverage measured by sampling up to 3 Osservatorio Fitosanitario Xylella acts per year and
grepping the extracted text for `Impronta (SHA`:

```
year | n_candidates | sampled | has_Impronta
2014 |    3 | 3 | 0        2021 |   75 | 3 | 0
2015 |   10 | 3 | 0        2022 |   24 | 3 | 0
2016 |    1 | 1 | 0        2023 |    9 | 3 | 0
2018 |    8 | 3 | 0        2024 |   50 | 3 | 2
2019 |   94 | 3 | 0        2025 |   45 | 3 | 3
2020 |  122 | 3 | 0        2026 |   27 | 3 | 3
```

Pre-2024 acts instead carry a page-count attestation only:

```
Il presente allegato, firmato digitalmente, è composto ...
Allegato B
Il presente allegato, firmato digitalmente, è costituito da n. 2 pagine
```

`embfile_count()` is 0 on all three 2025–2026 acts. The annex is appended as rendered pages,
not attached as a file.

### 1.8 What an act contains — three kinds fetched and dissected

All three PDFs are `Adobe InDesign` → `Adobe PDF Library`, `Tagged: yes`, with a real text
layer. Per-page text characters and embedded image count:

**Delimitation — DDS 35 of 29/04/2021, `DET_35_29_4_2021.pdf`, 685,822 bytes, 7 pages**

```
p1: textchars=3933 images=0      p5: textchars=  69 images=1 imgpx=2174960
p2: textchars=2542 images=0      p6: textchars= 118 images=1 imgpx=2174960
p3: textchars=3369 images=0      p7: textchars=3496 images=3 imgpx=12
p4: textchars= 359 images=0
```

Operative disposition, plain text:

```
Per quanto sopra riportato, si propone:
• di rappresentare con gli Allegati 1 e 1 bis, parti integranti del presente atto, i limiti
  geografici territoriali delle zone "infetta", "contenimento" e "cuscinetto";
• di riportare nell'Allegato 2, parte integrante del presente atto, i riferimenti catastali
  che consentono di individuare territorialmente le zone "infetta", "contenimento" e "cuscinetto";
```

Cadastral annex, page 7, real text table:

```
                                        ALLEGATO 2
              ZONA INFETTA IN PROVINCIA DI LECCE
  PROVINCIA        COMUNE                    FOGLI DI MAPPA CATASTALI
LECCE          INTERO TERRITORIO PROVINCIALE
              ZONA INFETTA IN PROVINCIA DI TARANTO
  PROVINCIA        COMUNE                    FOGLI DI MAPPA CATASTALI
               AVETRANA
               CAROSINO
               CRISPIANO
TARANTO                          INTERO TERRITORIO COMUNALE
               ...
```

`PyMuPDF find_tables()` on that page returns 7 tables, extracting cleanly:

```
['ZONA INFETTA IN PROVINCIA DI L', '', '']
['PROVINCIA', 'COMUNE', 'FOGLI DI MAPPA CATASTALI']
['LECCE', 'INTERO TERRITORIO PROVINCIALE', '']
```

Pages 5–6 are the map annexes: 2,174,960 image pixels, 69 and 118 text characters. No
readable geometry.

**Felling order — DDS 95 of 06/09/2022, `DET_95_6_9_2022.pdf`, 2,427,117 bytes, 12 pages**

```
p1-p6:  textchars 3307,3413,4100,3904,4286,3261   images=0
p7:     textchars  569  images=2 imgpx=203556
p8, p9: textchars  119,  70  images=1 imgpx=4352400   <- ortofoto, Allegato A
p10,p11:textchars 2857,2380  images=0                 <- Allegato B, consent form
p12:    textchars  896  images=1 imgpx=24960          <- Allegato C, parcel table
```

Operative disposition, machine-extractable and structured:

```
                              DETERMINA DI
confermare tutte le premesse esposte in narrativa ...
1. prescrivere, ai sensi del comma 1, art. 13 del Reg. UE 2020/1201, ai proprietari/conduttori
   di cui all'allegato C, parte integrante e sostanziale del presente provvedimento,
   l'estirpazione di n° 2 piante risultate infette da Xylella fastidiosa, site in agro di Fasano;
2. dare atto che le piante infette sono evidenziate nell'ortofoto di cui all'allegato A ...
3. stabilire che la tempistica da rispettare per l'estirpazione delle piante infette è la seguente:
     a) il presente provvedimento è notificato ai proprietari/conduttori attraverso la
        pubblicazione all'albo pretorio per 7 gg consecutivi e alla loro PEC qualora presente;
     ...
     c) il proprietario comunica, durante il tempo di pubblicazione dell'atto e comunque entro
        massimo 3 giorni dal termine del periodo di pubblicazione, ...
     d) nei casi di estirpazione su base volontaria il proprietario deve procedere
        all'estirpazione entro massimo 10 giorni dalla sua comunicazione ...
     f) se il proprietario, decorsi 3 giorni dal termine del periodo di pubblicazione, non invia
        alcuna comunicazione, ARIF procede alla rimozione delle piante infette entro massimo
        10 giorni successivi;
```

Allegato C is a genuine per-parcel table with coordinates:

```
                    ZONA CONTENIMENTO SALENTO - PIANTA INFETTA MONITORAGGIO 2022
                          ID       RAPPORTO PROVA   DATA RAPPORTO  FOGLIO PARTICELLA
 ZONA        AGRO      CAMPIONE                        PROVA                          PROPRIETARIO   SPECIE  LONGITUDINE  LATITUDINE
Contenimento- FASANO   1400913    20/2022POS UNIFG    26/08/2022     44     384      CARPARELLI ISABELLA Olivo 17,3880811  40,82970719
   Salento
Contenimento- FASANO   1396971    1554/Ldf/2022       30/08/2022    105     188      ISTITUTO DIOCESANO ... Olivo 17,34589058 40,8644211
   Salento
```

`find_tables()` extracts all values but returns them transposed, because the table text is
laid out rotated 90° on an unrotated page (`page.rotation == 0`):

```
rows: 11
['', 'ZONA CONTENIMENTO SALENTO - ', '', '', '', 'LATITUDINE', '', '', '', '40,82970719', '40,8644211']
['', '', '', 'SPECIE', '', '', '', '', '', 'Olivo', 'Olivo']
['', '', '', '', '', 'PROPRIETARIO', '', '', '', 'CARPARELLI ISABELLA', 'ISTITUTO DIOCESANO PER IL SO']
```

**Funding act — DAdG PSR 92 of 21/06/2022, `DET_92_21_6_2022.pdf`, 174,463 bytes, 5 pages**

```
p1: 2952  p2: 3607  p3: 3921  p4: 3620  p5: 2344   images=0 on every page
```

Pure text, no raster at all.

### 1.9 BURP full-text search is dead — the prior claim re-tested and confirmed

`GET https://burp.regione.puglia.it/search?q=xylella` → HTTP 200, 80,786 bytes:

```
Non è stato trovato alcun risultato con le parole chiave indicate:
xylella
```

### 1.10 Amministrazione Trasparente — the API exists, the content endpoint does not

`https://trasparenza.regione.puglia.it/v2/provvedimenti/provvedimenti-dirigenti-amministrativi`
→ HTTP 200, 799 bytes, an Angular shell:

```html
<base href="/v2/">
<body><app-root></app-root>
<script src="assets/env.js"></script>
```

`GET /v2/assets/env.js` → HTTP 200:

```js
window.__env.cmsBaseUrl = "https://sitra-cms.siep.regione.puglia.it";
window.__env.trasparenzaBaseUrl = "https://sitra-be.siep.regione.puglia.it";
window.__env.apiBaseUrl = "https://sitra-be.siep.regione.puglia.it/api";
window.__env.endpointLastDate = "obblighi/latest-update";
window.__env.keycloakUrl = "https://keycloak.siep.regione.puglia.it";
window.__env.endpointDragDropMenu = "https://sitra-be.siep.regione.puglia.it/api/obblighi/all/orderedByMenuFo";
```

`GET https://sitra-be.siep.regione.puglia.it/api/obblighi/all/orderedByMenuFo` → HTTP 200,
31,924 bytes, `application/json`. It returns the obligation tree only:

```json
{"id": 59, "obbligoId": null, "title": "Provvedimenti dirigenti amministrativi",
 "link": "/provvedimenti/provvedimenti-dirigenti-amministrativi", "linkInterno": null,
 "descrizione": null, "riferimentoNormativo": null, "visible": true, "order": 1, "updatedAt": null}
```

No act-listing endpoint was found. All content-endpoint guesses returned 404 — see fetch log.

### 1.11 An act names its own publication channels

From `DET_95_6_9_2022.pdf`, the region's own list of where a felling order is published:

```
b) Il provvedimento è notificato con PEC ad ARIF per gli adempimenti conseguenti ed è pubblicato su:
      - Bollettino Ufficiale della Regione Puglia
      - Portale www.emergenzaxylella.it
      - Sezione "Amministrazione trasparente", sotto sezione "Provvedimenti dirigenti amministrativi"
           del sito www.regione.puglia.it
```

---

## CLASS 2 — INFERRED FROM CLASS 1

**C2-1. The corpus is enumerable, and the sommario is the route.**
From 1.1 and 1.2: issues are addressable by year, `burpId` is dense and server-rendered, and
2,515 of 2,515 sommari returned HTTP 200 with zero errors. No filename guessing is needed —
the PDF URL is published in the sommario alongside its act. The `folderId` and UUID in each
PDF path are unguessable, which is why filename construction 404s and why the sommario is
not merely convenient but necessary.

**C2-2. The 2,000–3,500 estimate conflated issues with acts.**
Measured: 2,515 BURP *issues* 2013–2026 and 791 Xylella-relevant *acts*. The estimate's range
brackets the issue count almost exactly and overstates the act count by 3–4×. Treat the
estimate as retired. Confidence: high on the two measured numbers; the conflation is a
plausible reading of the coincidence, not a demonstrated fact about how the estimate was formed.

**C2-3. Operative count is 665 measured, and the true figure is higher.**
The regex classifier returned 665 operative of 791. Section 1.5 shows the 126-act residue
contains regional laws, annual action plans and spending authorisations that are plainly
operative. On the 12-act sample, roughly 9 of 12 residue acts were operative. Extrapolated,
the operative count lands near 750 of 791, i.e. almost the whole universe. **Defensible
statement: operative ≥ 665; upper bound 791; point estimate ~750 pending adjudication of the
126 residue.** This lands inside the project's 400–800 band, so that half of the estimate survives.

**C2-4. Keyword `xylella` alone loses 19% of the corpus.**
151 of 791 acts, from 1.4. Any selector must include the legal instruments — Reg. (UE)
2020/1201, Dec. (UE) 2015/789, D.I. 2484/2020 — and the zone vocabulary. This is the single
most consequential finding for coverage, because the missed acts are disproportionately the
recent funding measures (`Reimpianto olivi zona infetta`, `Salvaguardia di olivi secolari`)
that Wedge 1 exists to surface.

**C2-5. Current build coverage is 23 of 791, about 2.9%.**
Against the ≥665 operative floor, 3.5%. Coverage cannot be claimed at any level until the
census is loaded.

**C2-6. Two-stage classification is sound; the sommario carries enough signal.**
From 1.2 and 1.4: the oggetto states the legal basis, the measure type and often the comune.
Stage 1 selects candidates from the sommario, cheaply, over all 72,346 acts. Stage 2 opens
only the ~791 selected PDFs. Do not attempt to decide operativeness from the sommario alone —
1.5 shows regex on the oggetto both over- and under-fires, so stage 2 should adjudicate on
the extracted `DETERMINA DI` block.

**C2-7. AIP Logic parsing is feasible on the disposition and on cadastral tables. It is not
feasible on maps.**
From 1.8: body pages carry 3,000–4,500 characters each with zero images across all three act
kinds; no OCR is needed for the operative text. `DETERMINA DI` is a reliable anchor for the
disposition, and the numbered items encode deadlines as explicit day counts (7 days albo
pretorio, 3 days to elect, 10 days to execute). Cadastral annexes extract as tables. Map and
ortofoto annexes are pure raster at ~2.2–4.4 Mpx with under 120 characters of text — they
carry no extractable geometry and OCR would not recover it either. Zone geometry must come
from the SIT/shapefile channel, not from the act PDF.

**C2-8. Rotated-table detection is a required parser behaviour, not an edge case.**
From 1.8: the felling order's parcel table extracts transposed on an unrotated page. A parser
that assumes row-major output will silently swap owner names into coordinate columns. Detect
text angle per block and normalise before mapping to columns. This is a silent-corruption
risk, not a crash, so it needs a Data Expectation — latitude in 39.7–42.0, longitude in
15.0–18.6 for Puglia — rather than a code comment.

**C2-9. The Impronta gives annex integrity only for 2024-onward acts.**
From 1.7: absent in every pre-2024 sample, present in 2024 partially and 2025–2026 fully,
coinciding with the CIFRA2 platform. So roughly the 2024–2026 slice — 178 candidates by the
year table — can be integrity-checked by hash. Earlier acts have only a page-count
attestation, which detects truncation but not substitution.

**C2-10. The Impronta cannot be verified against the BURP PDF alone.**
`embfile_count()` is 0 and the annex appears as re-rendered pages inside the bulletin PDF.
Hashing anything extracted from the BURP PDF will not reproduce the digest, because the digest
is of the original standalone annex file as signed in CIFRA2. To use the hash as proof, obtain
the standalone `ALLEGATO 1_.pdf` from emergenzaxylella.it or Amministrazione Trasparente and
hash that. Until that file is fetched, the Impronta is a recorded claim, not an executed check.
Store it either way — it is the only published integrity anchor.

**C2-11. RSS is the incremental route; it needs a backstop.**
From 1.6: the feed carries `burpId` directly, so detection costs one 151 KB GET. But it holds
100 items covering about eight months. At 136–237 issues per year, a gap longer than roughly
five months would silently drop issues. Poll daily and reconcile weekly against the year
listing, comparing the observed `burpId` set to the feed's.

**C2-12. Amministrazione Trasparente is not usable as a second enumeration source today.**
From 1.10: the menu API is open but no content endpoint responded. The bundle is lazy-loaded
and `runtime.js` yielded no chunk map to mine, so the content endpoint is discoverable only by
observing the SPA's live XHR — which needs a working browser. Until then, treat BURP as the
sole route. Per 1.11 the region publishes each act to three channels, so a genuine
cross-check exists in principle; it is unproven in practice.

**C2-13. emergenzaxylella.it is closed.**
From the fetch log: `https://` fails certificate validation and `http://` 302s to
`/josso_security_check`, a JOSSO SSO gate. Yet 1.11 shows acts direct growers there for the
consent form and the delimitation. Two consequences: the annex-hash verification path in
C2-10 is blocked at the same door, and the product's users are being pointed at a portal that
is not anonymously readable. Worth escalating as a product finding, not only a data one.

---

## FETCH LOG — every URL attempted that failed, and how

| URL | Result | Reading |
|---|---|---|
| `burp.regione.puglia.it/api/jsonws` | HTTP 403, 664 B | Liferay JSON-WS disabled to anonymous |
| `burp.../o/headless-delivery/v1.0/openapi.json` | HTTP 403, 32 B | Headless API requires auth |
| `burp.../o/headless-delivery/v1.0/sites/20126/documents` | HTTP 403 | same |
| `burp.../api/jsonws/dlapp/get-file-entries` | HTTP 403 | same |
| `burp.../o/api` | HTTP 403 | same |
| `burp.../o/search/v1.0/openapi.json` | HTTP 404 | Search headless module not deployed |
| `burp.../o/oauth2/authorize` | HTTP 200 | Exists, but needs a registered client. Not pursued — read-only scope |
| `burp.../-/rss` | HTTP 404 | Wrong path; the real feed is `/rss-burp` with the AssetPublisher instance id |
| `burp.../search?q=xylella` | HTTP 200, zero hits | PDFs are not indexed. Prior claim confirmed |
| `burp.../bollettini?...mvcRenderCommandName=%2Fburp%2Fsearch&bolanno=2015` | HTTP 200, 88,988 B, 0 `burpId` | The `/burp/search` render command returns an empty shell reading `Search Burp / Loading`. Use the plain listing URL shape instead |
| `burp.../robots.txt` | HTTP 200 | `Sitemap: http://localhost:8080/sitemap.xml` — misconfigured, points at the origin's localhost |
| `burp.../sitemap.xml` | HTTP 200, 2,329 B | A `<sitemapindex>` of 12 Liferay layout sitemaps. Enumerates pages, not acts. Useless for census |
| `burp.../documents/20135/780671/DELIBERAZIONE+DELLA+GIUNTA+REGIONALE+29+ottobre+2013%2C+n.+2023.pdf` | HTTP 404, 664 B | Path lacks the trailing UUID segment. Confirms PDF URLs cannot be constructed, only read from the sommario |
| `https://www.emergenzaxylella.it/` | curl 60 | `SSL: no alternative certificate subject name matches target host name 'www.emergenzaxylella.it'` |
| `http://www.emergenzaxylella.it/` | HTTP 302 → `/josso_security_check` | JOSSO SSO gate, no anonymous content |
| `http://emergenzaxylella.it/`, `https://emergenzaxylella.it/`, `/portal/emergenza_xylella` | all 302 → `/josso_security_check` | same |
| `regione.puglia.it/web/amministrazione-trasparente/provvedimenti-dirigenti-amministrativi` | HTTP 404, 126 B | Wrong host. Correct host is `trasparenza.regione.puglia.it` |
| `trasparenza.regione.puglia.it/sitemap.xml` | HTTP 404, 42,171 B | No sitemap |
| `trasparenza.regione.puglia.it/api/v2/provvedimenti` | HTTP 404, 42,164 B | Wrong host for the API |
| `sitra-be.siep.regione.puglia.it/api/obblighi/latest-update` | HTTP 400 | Requires a parameter not discovered |
| `sitra-be.../api/provvedimenti` | HTTP 404 JSON | Guess, wrong |
| `sitra-be.../api/provvedimenti/paginated` | HTTP 404 JSON | Guess, wrong |
| `sitra-be.../api/documenti/paginated` | HTTP 404 JSON | Guess, wrong |
| `sitra-be.../siep-cms/page/?slug=...` | HTTP 404 Tomcat | Guess, wrong |
| `trasparenza.../v2/runtime.js` | HTTP 200 | Parsed for a lazy-chunk map; zero chunk-hash pairs matched. Content endpoint not recoverable statically |
| `browser_exec` against the trasparenza SPA | tool error | `Cloud browser provider BrowserUseBrowserProvider returned no CDP endpoint`. Blocked live XHR capture — this is why C2-12 stays open |

Not attempted, and why: the SIT listing endpoint reported as 403 by the prior investigation
was not re-tested, because no SIT URL was supplied in the brief and the sommario route made
zone-geometry discovery a separate question. It should be re-tested under its own task, since
C2-7 shows zone geometry cannot come from act PDFs.

---

## RECOMMENDED CENSUS METHOD

Reproducible, executed once already at the numbers above.

**Step 1 — Enumerate issues.** For each year 1999–2026, GET

```
https://burp.regione.puglia.it/bollettini
  ?p_p_id=it_indra_regione_puglia_burp_web_SearchPortlet
  &p_p_lifecycle=0&p_p_state=normal&p_p_mode=view
  &_it_indra_regione_puglia_burp_web_SearchPortlet_bolanno={YEAR}
  &_it_indra_regione_puglia_burp_web_SearchPortlet_delta=200
  &_it_indra_regione_puglia_burp_web_SearchPortlet_cur={N}
```

Increment `cur` until the max `..._cur=` value in the returned pagination is reached. Collect
`burpId`, the `<h2 class="titolo">` label and the `data-news` date. Yields 2,515 rows for
2013–2026. Cost: 14 requests + pagination, about 30 seconds.

**Step 2 — Harvest sommari.** For each `burpId`, GET the detail URL from §1.2. Split on
`<div class="card card-burp">` for sections, then on `<div class="doc-element">` for acts.
Take `<span class="collapse-title">` as section, `<h2>` as title, the text after `</h2>` as
oggetto, and the first `documents/....pdf` href as the PDF URL. Yields 72,346 act rows.
Cost: 2,515 requests, about 9 minutes at concurrency 8, roughly 600 MB transferred, 50 MB of
JSONL retained. Be a good citizen — cap concurrency at 8, retry with backoff.

**Step 3 — Select the Xylella universe.** Apply selector A ∪ L from §1.3 to
`title + ' ' + oggetto`. Yields 791. Record which selector fired per act; the L-only set of
151 is the audit population.

**Step 4 — Classify operativeness.** Do not finalise from the oggetto. Fetch the 791 PDFs,
`pdftotext -layout`, isolate the `DETERMINA DI` or `DELIBERA` block, and classify against the
five facets. Adjudicate the 126-act residue by hand or by AIP Logic against the disposition
text, not the title. Cost: 791 PDFs, roughly 1.2 GB, about 15 minutes at concurrency 8.

**Step 5 — Extract structure.** Body text via `pdftotext -layout`. Cadastral and parcel
annexes via `PyMuPDF find_tables()`, with rotated-block normalisation per C2-8. Flag any page
with under 200 text characters and over 100,000 image pixels as a map annex; do not attempt to
parse it, record it as a geometry pointer. Do not OCR — §1.8 shows the operative text is
already digital, and OCR on the maps would produce nothing usable.

**Step 6 — Capture integrity.** For 2024-onward acts, extract the `ALLEGATI INTEGRANTI` block
and store filename → SHA256. Mark it `unverified` until the standalone annex is retrieved from
a channel that serves it, per C2-10.

**Step 7 — Run incrementally.** Poll `/rss-burp` daily. For each item, extract `burpId`,
compare to the loaded set, and run steps 2–6 on new ones. Weekly, re-run step 1 for the
current year and diff the `burpId` set against the feed to catch anything the 100-item window
dropped. Cost: about 151 KB per day, plus a few hundred KB per week.

**Total first-run cost:** roughly 25 minutes wall clock, about 1.8 GB transferred, no
credentials, no rate-limit encountered across roughly 3,300 requests. **Steady-state cost:**
under 1 MB per day.

### What would change these numbers

- The 791 is bounded by the selector. Widening it to Tier-B phytosanitary terms adds 351
  candidates, most of which are non-Xylella deroghe on other crops. Anyone changing the
  selector must re-run step 3 and publish the new selector text alongside the count.
- The universe currently starts at 2013 because that is the brief's window. BURP indexes back
  to 1999 and step 1 covers it; DGR 2023 of 29/10/2013 is the first Xylella act found, so
  extending earlier should return zero and is worth running once as a null check.
- If the trasparenza content endpoint is ever recovered — it needs a browser with CDP to watch
  the SPA's XHR — it becomes an independent cross-check on BURP completeness. Until then the
  census has one source and no corroboration, which is the largest open weakness in this method.

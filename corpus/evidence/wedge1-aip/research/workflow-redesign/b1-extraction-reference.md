# B1 extraction reference

Status: **VERIFIED LIVE 2026-08-23 by Connor.** Every endpoint, field list, count, hash and mechanic below was executed against the live source in this session, not copied from research.
Purpose: remove every assumption from B1 data acquisition. If something here is wrong, stop and report it — do not work around it silently.
Scope: B1 only. B5 extends the same mechanics to the funding-side corpus.

---

## 0. THE CRITICAL TRAP — read before writing any extraction code

**`resultOffset` is silently a no-op on this ArcGIS server.**

Verified live this session:

```
?where=NOME_COMUNE='CAPURSO'&resultOffset=0&resultRecordCount=1000  -> 1000 features
?where=NOME_COMUNE='CAPURSO'&resultOffset=1000&resultRecordCount=1000 -> 1000 features
OBJECTID overlap between the two pages: 1000  ← IDENTICAL ROWS
Both responses report exceededTransferLimit: true
```

A standard paginate-by-offset loop returns **the same first 1000 rows forever**. It does not error. Row counts look plausible. Adding `orderByFields` changes the sort order while still ignoring the offset, which makes the loop look even more correct. This is the single most dangerous quirk in the entire data plane: it produces duplicated, incomplete data that passes a naive row-count check.

### The proven method — `returnIdsOnly` then `OBJECTID IN (...)` batches

Verified live this session on Catasto L2:

```
STEP 1  GET .../query?where=<clause>&returnIdsOnly=true&f=json
        -> {"objectIdFieldName":"OBJECTID","objectIds":[...]}
        Returns the COMPLETE id set. NOT capped at 1000.
        CAPURSO -> 11568 ids, all unique, min 573148 max 1478685 (non-contiguous)

STEP 2  For each batch of 400 ids:
        GET .../query?where=OBJECTID IN (id,id,...)&outFields=*&returnGeometry=true&outSR=4326&f=json
        -> exactly the requested rows, verified set-equal to the requested ids
```

Batch-size evidence, measured:

| Batch size | Transport | Result |
|---|---|---|
| 1000 ids | GET | **HTTP 414 Request-URI Too Large** |
| 1000 ids | POST form-encoded `objectIds=` | **read timeout** (server too slow at this size) |
| 400 ids | GET, with geometry, `outSR=4326` | **OK — 400 features in 1.0s** |
| 200 ids | GET, with geometry, `outSR=4326` | OK — 200 features in 1.1s |
| 200 ids | GET, no geometry | OK — 200 features in 0.6s |

**Use GET with 400 ids per batch.** Do not use POST. Do not use `resultOffset`.

### Mandatory conservation check on every layer

```
len(objectIds from step 1) == count from returnCountOnly == rows landed in the curated dataset
```

If these three numbers disagree, the extraction is wrong. This check is what makes the `resultOffset` trap impossible to hit silently, so it is not optional.

### Other server mechanics, verified

- `f=geojson` returns **HTTP 400**. Esri `f=json` only.
- `outSR=4326` **reprojects server-side**. Verified output `[16.90287, 41.05347]` — valid Puglia WGS84 lon/lat. Do not reproject client-side; ask the server.
- Native spatial reference of every SIT layer here is **EPSG:32633** (UTM 33N). Anything fetched without `outSR` arrives in metres, e.g. `[659908.58, 4546437.27]`.
- `where=OBJECTID>0` is the reliable "everything" clause; `1=1` is not consistently accepted.
- `returnCountOnly=true` is cheap and authoritative — use it as the conservation control before and after every extraction.

---

## 1. Cadastral parcels — `Background/Catasto/MapServer/2`

Full URL base:
`https://webapps.sit.puglia.it/arcgis/rest/services/Background/Catasto/MapServer/2/query`

Layer name `Particelle` · geometry `esriGeometryPolygon` · `maxRecordCount` 1000 · source snapshot Sept 2021 (Sigmater).

**Fields, exact:** `COMUNE, SEZIONE, FOGLIO, ALLEGATO, SVILUPPO, NUMERO, LIVELLO, SHAPE, NOME_COMUNE, SHAPE.AREA, SHAPE.LEN, OBJECTID`

The comune filter field is **`NOME_COMUNE`** (uppercase comune name). It is *not* `NOME_COM` — that field name belongs to a different service (`MonitoraggioXFStampaCatasto`) and will error here.

### Ingest ALL parcels for these comuni. Verified exact spellings and counts:

| `NOME_COMUNE` | Parcel count | Role |
|---|---:|---|
| `BARI` | 84,570 | Bari-belt: pauca ZI/ZC + fastidiosa ZI + multiplex ZC |
| `BITONTO` | 52,767 | Bari-belt: inside Modugno AD, DET 3/2026 prescription |
| `NOICATTARO` | 24,695 | Bari-belt: fastidiosa ZI + multiplex ZI, DET 13/2026 |
| `CRISPIANO` | 20,850 | Ex-Salento containment anchor, 72 current positives |
| `MODUGNO` | 17,781 | Bari-belt: pauca ZI |
| `TRIGGIANO` | 16,487 | Bari-belt: fastidiosa ZI, DET 11/2026 |
| `VALENZANO` | 12,404 | Bari-belt: DDS 2/2026 legal area, layer-identity mismatch |
| `CAPURSO` | 11,568 | Bari-belt: multiplex ZI + fastidiosa ZI |
| **TOTAL** | **241,122** | |

At 400 ids per batch this is **≈603 requests, ≈10 minutes**. Batch per comune, not globally, so a failure is retryable at comune granularity and each comune has its own conservation target from the table above.

**Known data quality — null `NUMERO`.** Verified: `BARI` has **1,108** parcels with `NUMERO IS NULL`, `CRISPIANO` has **331**. These are roads, water and similar non-particella features carried in the same layer. They are real rows, not corruption. Decide explicitly: either exclude them at the curated layer with a recorded rule, or keep them with an explicit sentinel. Do not let them silently become `CadastralParcel` objects with a null key component — the qualified key `COMUNE/SEZIONE/FOGLIO/ALLEGATO/SVILUPPO/NUMERO` would not be unique.

**Qualified identity key.** `COMUNE + SEZIONE + FOGLIO + ALLEGATO + SVILUPPO + NUMERO`. Note `SEZIONE` is frequently a single space `' '`, not empty or null — normalize it deliberately and record the rule. `COMUNE` is the Belfiore code (e.g. `B716` = Capurso); `NOME_COMUNE` is the human name. Keep both.

**Cross-validation source (optional, cheap):** Agenzia Entrate INSPIRE WFS `https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/owfs01.php` carries current national cadastral geometry with `NATIONALCADASTRALREFERENCE`. The SIT snapshot is 2021; if a parcel's geometry matters to a demo assertion, spot-check it here. Not required for B1 completion.

---

## 2. Zone geometry — three services, EPSG:32633

All zone layers are **1–4 multipart features each** — tiny payloads, no pagination needed. Fetch with `where=OBJECTID>0&outSR=4326`.

### 2a. pauca — `Operationals/DatiPubbliciFasceXF/MapServer`

Verified layer inventory (all 16):

| Layer | Name |
|---|---|
| L0 / L1 | Zona Infetta / Cuscinetto — pauca (Cagnano Varano) |
| L2 / L3 | Zona Infetta / Cuscinetto — pauca (Giovinazzo) |
| **L4 / L5** | **Zona Infetta / Cuscinetto — pauca (Modugno)** ← target |
| L6 / L7 | Zona Infetta / Cuscinetto — pauca (Bisceglie) |
| L8 / L9 | Zona Infetta / Cuscinetto — pauca (Minervino Murge) |
| **L10 / L11** | **Zona Infetta / Cuscinetto — pauca (Bari)** ← target |
| L12 | Zona Infetta — pauca ST53 ex Salento (Focolai di Mola di Bari e Noci) |
| L13 | Zona Cuscinetto — pauca ST53 ex Salento |
| **L14** | **Zona Contenimento — pauca ST53 ex Salento** ← target (Crispiano) |
| **L15** | **Zona Infetta — pauca ST53 ex Salento** ← target (Crispiano) |

B1 needs **L4, L5, L10, L11, L14, L15**. Ingest the other pauca layers too if cheap — they are single features and B5 will want them — but they are not B1 acceptance criteria.

**Identity caveat, load-bearing:** the "Modugno" geometry (L4/L5) covers Bari, Bitonto, Capurso, Modugno **and Valenzano**. DDS 2/2026 legally institutes a Valenzano area, but **no Valenzano-named layer exists in this service**. Do not synthesize one. `OfficialArea` rows carry the published layer identity; the legal area identity comes from the act. They are separate facts and their mismatch is a real demo event (E2b).

### 2b. fastidiosa — `Operationals2/DatiPubbliciFasceXFF/MapServer`

L0 `Zona Infetta` (1 feature) · L1 `Zona Cuscinetto` (1 feature). Both in scope: this is the ST1 belt covering Bari, Capurso, Noicattaro, Triggiano.

### 2c. multiplex — `Operationals2/DatiPubbliciFasceXFMultiplex/MapServer`

L0 `Zona Infetta` (**4 features** — Noicattaro-Triggiano, Capurso, Santeramo in Colle, Ginosa) · L1 `Zona Cuscinetto` · L2 `Zona Cuscinetto Basilicata`. All three in scope; the 4-feature ZI layer is the one that matters — attribute field is `DESCRIZIONE`.

---

## 3. Monitoring positives — three services

Base: `https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/`

| Service | Layer 1 name | Verified count |
|---|---|---:|
| `MonitoraggioXFSintesiAttuale` | Positivi - Campioni 2026 sub. pauca | **210** |
| `MonitoraggioXFFSintesiAttuale` | Positivi - Campioni 2026 sub. fastidiosa | **13** |
| `MonitoraggioXFMultiplexSintesiAttuale` | Positivi - Campioni 2026 sub. multiplex | **10** |

Each service also exposes L0 `Campionamento 2026`, L2 `Olivo`, L3 `Fruttiferi`, L4 `Altre Aree`. **B1 needs layer 1 only** (the positives). Ingest L2–L4 only if a later step needs the negative denominator — B1 does not.

**Fields, exact (pauca L1):** `OBJECTID, RISULTATO, DATA_CAMPIONE, SQUADRA, ID_CAMPIONE, SPECIE, SINTOMI, PROTOCOLLO, DOCUMENTO_CONFERMA, SHAPE` · geometry `esriGeometryPoint`. The fastidiosa and multiplex siblings add a laboratory field.

Total 233 positives — small enough for a single `where=OBJECTID>0` fetch per layer, no batching.

**`ID_CAMPIONE` is the Plant identity source** for Plant class 2 (officially sampled). It is a **string**, not an integer. `DATA_CAMPIONE` is an epoch-millis integer (e.g. `1785110400000` = 26 Jul 2026). `DOCUMENTO_CONFERMA` links the confirmation report — preserve it as the evidence reference.

**Snapshot discipline.** These layers move. Snapshot once with `retrieved_at`, and never live-query them at demo time. The recorded counts above are the conservation target for that snapshot; if a fresh fetch disagrees, that is a real change in the world, and it is recorded as such — not silently reconciled.

**E1 demo binding, verified live this session:**
```
ID_CAMPIONE 1964901 | RISULTATO POSITIVO | SPECIE OLIVO
DATA_CAMPIONE 1785110400000 (26 Jul 2026) | PROTOCOLLO "RAPPORTO PROVA 64..."
```
Freshest positive in Puglia. Comune BARI. This is the E1 change event.

---

## 4. Monumental olive registry — `Operationals/UliviMonumentali/MapServer/1`

Layer `Ulivi Monumentali` · `esriGeometryPoint` · `maxRecordCount` 1000 · **341,428 total features**.

**Fields, exact:** `OBJECTID, SCHEDAN, COD, RILDATA, LOCPROV, LOCCOM, COORDX, COORDY, PROPRFG, PROPRPTC, CARSEGNMOT, MONOGRAFIA, APP, SHAPE`

341k is too many to ingest wholesale. **Clip to the target comuni.** The comune field is `LOCCOM`, **uppercase exact match** — verified working. (`LIKE '%ari%'` returns empty; use `LOCCOM='CRISPIANO'` form.)

### Verified counts per target comune — read this before extracting

| Comune | Monumental trees |
|---|---:|
| **CRISPIANO** | **3,342** |
| BARI | 0 |
| BITONTO | 0 |
| NOICATTARO | 0 |
| MODUGNO | 0 |
| TRIGGIANO | 0 |
| VALENZANO | 0 |
| CAPURSO | 0 |

**This is correct, not a bug.** Monumental olives concentrate in the ex-Salento/Taranto belt; the northern Bari-belt comuni have no registered monumental trees. An empty result for BARI is the true answer — do not "fix" it by loosening the filter, widening the geography, or falling back to a spatial envelope that pulls in neighbouring comuni.

**Consequence for the Plant model, and it is a good one:** the two Plant identity classes come from different anchors.

- **Class 1 (registry identity)** → Crispiano only, 3,342 trees, with `PROPRFG`/`PROPRPTC` giving a real parcel join.
- **Class 2 (official sample identity, `ID_CAMPIONE`)** → Bari belt, where the fresh positives are.

Both classes get exercised, on real data, in their real locations. Neither anchor alone would have done it.

At 3,342 rows this is a small extraction — `returnIdsOnly` → `OBJECTID IN (...)` at 400, ~9 requests.

`SCHEDAN` / `COD` are the registry identity for Plant class 1. `PROPRFG` / `PROPRPTC` are foglio/particella references — the join to `CadastralParcel`, and the reason monumental trees can carry a real DL05 link. `COORDX`/`COORDY` duplicate the geometry in EPSG:32633; prefer the reprojected `SHAPE` via `outSR=4326` and keep the raw pair as source-backed attributes.

---

## 5. Acts — verified PDFs with hashes

All five fetched and hashed live this session. Three hashes **independently cross-validate** against the prior corpus, which is strong evidence the documents are stable and correctly identified.

| Act | Bytes | sha256 | Cross-validates? |
|---|---:|---|---|
| **DET 2/2026** — institutes Valenzano pauca area | 1,442,886 | `ad2fb7bd8931dee043c398bdac6e04ff1a6f918a5c8cd6901677af8401b35504` | ✅ matches corpus |
| **DET 3/2026** — Bitonto eradication prescription | 1,261,323 | `aa98c288b761055f4da4be515ea2c77883bb590185f0fe10149f59e4800af057` | ✅ matches corpus |
| **DDS 79/2026** — vector/tillage deadlines | 617,071 | `f1b02c2afbc2800495fbc4e80b045c6f062d52a2db15bedfa6420afbcc6262dc` | ✅ matches corpus |
| **DDS 93/2024** — institutes multiplex Noicattaro-Triggiano + Capurso | 580,975 | `896ef6a0969d1d6dce8592601e6f3e2ca1aa1745f14e8f4d0b2e94e89c986756` | first hash |
| **DDS 167/2025** — Sammichele liquidation €12,955.54 (B6 event) | 269,577 | `af68e7dd91574e7231ce287170f47a80758b901b877404885b8d1c6e28557a7d` | ✅ matches corpus |

URLs:

```
DET 2/2026    https://burp.regione.puglia.it/documents/20135/2735532/DET_2_12_1_2026_FITO.pdf/85d5418e-aa6d-7988-3010-695f84b8681f?t=1770063167003
DET 3/2026    https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0
DDS 79/2026   https://erchie-api.municipiumapp.it/s3/2647/allegati/determina-regione-0079-2026.pdf
DDS 93/2024   https://burp.regione.puglia.it/documents/20135/2509064/DET_93_23_7_2024.pdf/c860aa7b-f31f-1f16-2634-453d7ed7a053?t=1722517882921&version=1.0
DDS 167/2025  https://www.regione.puglia.it/documents/736605/1003703/181_DIR_2025_00167_DeterminaPUB+Sammichele.pdf/5f710ee4-f8e1-60ff-0ce5-310542ac68fb?t=1761040730346
```

Verify each hash after download. A mismatch means the document changed at source — stop and report, do not proceed with an unverified act.

**BURP fetch quirk:** the Crawl4AI extractor returns HTTP 500 on these PDFs. Direct `curl -sL` works, as proven above. Use direct fetch, then extract text locally.

### Two acts still to locate — do not guess

| Act | What it is | How to find it |
|---|---|---|
| **DDS 92 of 22-07-2024** | Institutes the Bari pauca area (L10/L11) | BURP stable-document pattern `documents/20135/<folder>/DET_92_22_7_2024.pdf/<uuid>`. Folder id differs per act, so search BURP for the act number + date, or find it recited in a later act's premessa. |
| **DDS 39 of 11-03-2026** | Original juvenile-vector prescription, superseded by DDS 79 | Municipal mirrors carry it — Modugno's page hosts a copy. DDS 79 is the operative deadline act; DDS 39 is needed only to make the supersession chain complete. |

If either cannot be located after two distinct strategies, **record the dated absence and proceed**. Neither blocks B1 acceptance. A dated absence is a finding, not a failure — this domain is full of them and the model is built to carry them honestly.

---

## 6. Notional private layer

Per D5 (accepted): build-as-real. Notional rows exist only where real data is genuinely underivable — the cooperative's private layer is customer-held and cannot be acquired. **No `notional_demo` flag appears in operator-facing data.** Provenance is tracked build-side in the manifest, not as a product-visible state.

B1 minimum, deliberately small:

- 1 cooperative `OperatorParty`
- 3 member `OperatorParty` rows
- 3 `AgriculturalHolding` rows, linked to real parcels from §1
- 1 `Intervention` on a Bari-belt parcel

**Identifier hygiene, mandatory.** No notional identifier may collide with real identifier space. Real CUAA is an 11-digit numeric or 16-char alphanumeric fiscal code; do not mint anything matching those shapes. Use an obviously-synthetic pattern for internal keys, and never reuse a real registry number. Cross-check every notional identifier against the real extracts before landing it.

**Parcels referenced by notional holdings must be real parcels** from the §1 extraction — the holding is notional, the land is not.

---

## 7. Expectations — the acceptance bar

Build-blocking on every curated dataset:

| Check | Applies to | Note |
|---|---|---|
| Primary-key uniqueness | all | qualified cadastral key; `ID_CAMPIONE`; `SCHEDAN` |
| Qualified-key collision | parcels | the null-`NUMERO` rows are the live test case |
| Row conservation raw→curated | all | must equal the §1/§3 counts, per comune |
| FK existence | plants→parcels, holdings→parcels | no orphan references |
| Geometry validity + WGS84 | parcels, zones, plants, monumental | after `outSR=4326`, assert lon∈[14,20], lat∈[38,43] |
| Null/domain on load-bearing fields | monitoring, acts | `RISULTATO`, `DATA_CAMPIONE`, act id/date |

**Quarantine proof required.** B1 is not complete until a deliberately malformed input is demonstrably rejected into quarantine rather than admitted. Construct one — e.g. a parcel row with a duplicate qualified key, or a geometry outside the Puglia envelope — run it, and show it quarantined. "All expectations pass" is only half the evidence; the other half is that they *can* fail.

---

## 8. Manifest — every extract, no exceptions

```
source_name · source_url · query_or_where_clause · retrieved_at (UTC ISO8601)
row_or_feature_count · sha256 (of the raw payload or PDF) · extraction_method
```

`extraction_method` records which mechanic was used — `returnIdsOnly+OBJECTID_IN_400`, `single_fetch`, `direct_curl`, `spatial_envelope` — because B6's ingestion contracts and B9's freshness SLOs both depend on knowing exactly how a source was reached.

The manifest is the input to B5's assurance rows and B9's Data Health. It is not documentation; it is a build artifact.

---

## 9. Standing constraints for B1

- Datasets only. **No object types, no Actions, no Functions, no AIP resources.** Edit-only properties require a permissioned backing dataset, which is precisely why B1 precedes B2.
- The historical project `CORDON-Wedge-1` is not referenced. That is the entire rule — no blocklist, no clean-room matrix, no permission remediation.
- Intuitive names, no prefixes: `parcels`, `official_areas`, `plants`, `instruments`, `parties`, `holdings`, `interventions`.
- Ledger every created resource: `kind | display_name | full_rid | api_name | version_or_tag | build_step`. Append before reporting complete. Never a name-only success.
- Scope guard: if an extraction starts widening beyond this reference, it belongs to B5, not B1. The test is whether it serves the duty trajectory that B3 must run.

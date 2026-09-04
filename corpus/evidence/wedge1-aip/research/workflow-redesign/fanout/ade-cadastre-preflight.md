# AdE current cadastre — pre-Foundry probe findings

Status: VERIFIED LOCAL SOURCE-MECHANICS EVIDENCE; no Foundry probe or source switch authorized
Date: 2026-08-24

## Source roles

### WFS — continuous point/current lookup

Endpoint: `https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/owfs01.php`

Verified from live GetCapabilities and GetFeature:

- Agency states the service is aligned to the cadastral cartographic database and automatically updated from technical acts.
- WFS 2.0.0 and 1.1.0 are exposed.
- Feature types: `CP:CadastralParcel` and `CP:CadastralZoning`.
- Default CRS: EPSG:6706, latitude-longitude axis order in GML.
- License: CC BY 4.0, Agenzia delle Entrate attribution required.
- WFS 2.0 result paging works with `COUNT` + `STARTINDEX`; measured Bari pages 0/5 and 0/100/200 were disjoint.
- `numberMatched` is `unknown`; completeness must page to a short/empty page and dedupe.
- Capabilities state `PagingIsTransactionSafe=FALSE`; a multi-page retrieval is a bounded-window view, not an atomic snapshot.
- The service has a concurrent-request ceiling; publisher says callers must retry when reached.
- Practical spatial requests must be small. Measured in dense Bari data:
  - 0.01° box returned 100 unique features;
  - 0.02° and 0.05° boxes silently returned zero rather than a limit error.
- WFS 1.1 also returned 100 features for the small Bari box and zero for an approximately 10 km box.

### Bulk download — semestral full-region snapshot candidate

Public URL: `https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/GetDataset.php?dataset=PUGLIA.zip`
Final CDN: `https://wfs-download.cartografia.agenziaentrate.eu/wfsdownload/PUGLIA.zip`

Verified live:

- HTTP range supported.
- `Last-Modified: Tue, 10 Feb 2026 12:33:53 GMT`.
- Exact size: 699,971,837 bytes (667.55 MiB).
- Outer ZIP contains `BA.zip`, `BR.zip`, `FG.zip`, `LE.zip`, `TA.zip`.
- Province ZIPs contain 256 comune ZIPs. Historic cadastral packaging places seven BAT comuni under BA and three under FG.
- Four archive/live-comune name differences are abbreviations; **Zapponeta is genuinely absent** from the February package.
- WFS current lookup returned Zapponeta parcels (`E885_011200.1001`, etc.), so WFS can cover the bulk omission between releases.
- Each comune ZIP contains `<code>_<name>_map.gml` and `_ple.gml`.
- Crispiano parcel GML has `timeStamp=2026-02-10T05:48:46`, exact `numberMatched=20950`, `numberReturned=20950`.
- Agency states bulk data is updated semestrally, generated per comune and packaged regionally; maps under confidentiality or maintenance may be omitted.

## Foundry native WFS compatibility

Official Foundry docs establish:

- native connector uses WFS **1.1.0**;
- its smallest internal geographic partition is **10×10 km** and is not configurable;
- WFS 1.1 cannot page a dense smaller region; connector may fail when one minimum region exceeds the batch;
- connector exits when server response counts cannot establish how much to fetch;
- optional batch size defaults to 1000 and upstream rate to 10 requests/second.

The AdE server silently returned zero for the measured ~10 km Bari box while returning 100 rows for a small box. Therefore native full-region WFS is expected to fail or silently omit dense areas. A Foundry negative-control sync may confirm this; it is not a credible production path.

## Schema and identity

DescribeFeatureType exposes:

- `msGeometry`;
- `INSPIREID_LOCALID`;
- `INSPIREID_NAMESPACE`;
- `LABEL`;
- `NATIONALCADASTRALREFERENCE`;
- `ADMINISTRATIVEUNIT`.

Official identifier structure:

`CCCC Z FFFF A S . PARTICELLA`

- `CCCC`: cadastral comune code;
- `Z`: census section, `_` if absent;
- `FFFF`: four-digit sheet;
- `A`: attachment, `0` if absent;
- `S`: development, `0` if absent;
- parcel label: number, public-building letters, `ACQUA###`, or `STRADA###`.

Verified examples:

- Bari `A662A002900.100` ↔ SIT `A662/A/29/0/0/100`.
- Lecce `E506_0259G0.1043` means comune E506, absent section, sheet 259, attachment G, development 0, parcel 1043.

The section is mandatory for identity. SIT also contains Bari `A662/C/29/0/0/100`; joining only comune/sheet/parcel would be false.

## Crispiano cross-source identity findings

Current AdE bulk: 20,950 features, 20,928 unique national references.
Dated SIT 2021: 20,850 rows; 20,519 have ordinary mappable parcel numbers and 331 use null-number sentinels.

Direct official component mapping:

- overlap: 20,313;
- SIT mappable coverage: 98.996%;
- AdE unique-reference coverage by SIT: 97.061%;
- SIT-only ordinary references: 206;
- AdE-only references: 615;
- AdE road/water labels: 344.

Interpretation:

- Most identities reconcile deterministically.
- Four SIT rows publish `ALLEGATO=0, SVILUPPO=A` but match AdE `ALLEGATO=A, SVILUPPO=0`; geometry IoU is 0.9957/0.9931 on two measured parcels. The reversal is exceptional, not systematic: swapping globally reduces match coverage to 94.703%.
- The remaining SIT-only/AdE-only population is a mixture of 2021→2026 split/merge/renumbering, roads/water identity differences, and residual source mismatch. It requires explicit reconciliation, never field swapping by rule.
- AdE has 22 duplicate feature occurrences over national references. Some are disjoint geometry pieces and even reuse the same GML ID. Therefore raw feature/GML ID is not a safe PK. The Parcel owner is `NATIONALCADASTRALREFERENCE`; geometry must dissolve/union by that identity.
- Blank labels such as `D171_001200.` are invalid Parcel identities and must reject.

## What the source cannot establish

Neither WFS nor bulk supplies:

- ownership;
- tenure, consent, access or standing;
- current operator/Holding;
- cultivation or olive land use;
- the complete linked cadastral database;
- a transaction-safe continuous snapshot.

Those facts remain with members/CAA/authorized cadastral services or independent land-use observations.

## Recommended source architecture to probe

1. **Bulk Puglia ZIP** is the candidate full-current geometry/identity snapshot. Ingest as immutable regional file + per-comune GML manifest; enforce 256 packaged comuni plus the explicit Zapponeta omission for this vintage, file sizes/hashes, and per-GML exact counts.
2. **WFS 2.0 small-tile external transform** is the continuous point/current reconciliation lane for selected contexts, new-member onboarding and bulk omissions. Use ≤0.01° dense tiles, `COUNT/STARTINDEX`, page-to-short/empty, dedupe national reference + geometry occurrence, bounded retrieval window and low concurrency/backoff.
3. **SIT 2021** remains a dated regional vintage and rich source-field reconciliation layer, not current title/ownership.
4. Keep the existing CORDON qualified component key until the full reconciliation proves a migration. Attach AdE national reference as official source identity; do not silently re-key B1.1 before B2.

## Proposed isolated Foundry probe (awaiting Owen GO)

- Create only exact egress for WFS and its CDN redirect host.
- Attempt one native WFS source/sync as a measured negative control; stop if the 10 km partition returns zero/fails as predicted.
- Create an isolated WFS 2.0 external transform for the exact small Bari, Lecce and Zapponeta boxes already verified locally. Land raw GML-derived features and a dissolved parcel output; prove disjoint pages and unique national references.
- Create a bulk-source manifest transform using range metadata/central-directory inspection. Do not ingest all 667.55 MiB during the probe unless a separate decision authorizes it.
- Compare Bari sample identities to SIT now; compare Salento context when the active full SIT sync contains it.
- No product binding, no source switch, no B2 write. Stop with adopt/reconcile/reject recommendation.

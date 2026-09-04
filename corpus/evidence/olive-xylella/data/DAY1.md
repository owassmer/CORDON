# Day 1 report — 15 August 2026

Contract gate (CORDON §5): *we can point to a row in the CSV, a lat/lon or comune, a Sentinel tile, and a PCR result, for at least 100 trees. If the open CSV is comune-level only, we downgrade the nowcast to comune/grid and say so.*

## Verdict: PASS — tree-level, and it is the front

Full file is on disk (81,999,815 bytes, sha256 `124ebb62…`, trailing newline, 688,631 complete rows). Dates: 20 Jan 2020 – 30 Jun 2023. The 2023 campaign is inside this file; the separate CKAN resource `CAMP_2020_2023.csv` is still URL-empty and unused.

- 688,631 complete sample rows
- 605,617 olive rows with lat/lon + `RISULTATO` (PCR)
- 5,195 olive positives (0.858%)
- Coordinates on every complete row
- Provinces: Bari (337k), Brindisi (182k), Taranto (147k), BAT (15k), Foggia (7.9k). **Lecce is absent.**

Olive positives by year: 2020 = 1,976 · 2021 = 2,861 · 2022 = 235 · 2023 (to 30 Jun) = 123.
That collapse is load-bearing. A 2022–23 hold-out is legitimate in time and starved of positives. Precision-recall still, and we will also report a spatial fold inside 2020–21.

Olive positives by province: Brindisi 4,018 · Taranto 746 · Bari 431. The labelled front is Brindisi-heavy.

That last pair of facts is the strategic one. This is official monitoring of the **buffer / northern front**, not a census of dead Salento. It is exactly the label set Artifact A needs.

Example joinable row (first data line):

- ID 730508
- 07/02/2020
- Mandorlo, Carovigno, Brindisi
- lat 40.72537601, lon 17.72236012 (comma decimal in file)
- RISULTATO Negativo, SINTOMO Assente

Sentinel-2: Planetary Computer STAC returned live L2A items over this bbox (tiles T34TBL, T34TBK, T33TYF, 29 Aug 2023, cloud ~5–10%). Catalog access needs no account. Pixel download not yet exercised.

## What is still blocked

| Item | State | Meaning |
|---|---|---|
| CAMP_2020_2022.csv | CLOSED — full file verified | 688,631 rows, through 30 Jun 2023 |
| CAMP_2020_2023.csv (separate CKAN resource) | ACCESS_BLOCKED — url empty | redundant; 2023 already in the 2020–2022 file |
| Zarco-Tejada 2018 PDF | CLOSED — Owen-fetched preprint | `raw/papers/zarco-tejada-2018-natureplants.pdf` |
| EFSA 2016 PDF | CLOSED — Owen-fetched | `raw/papers/efsa-2016-treatments.pdf` |
| Sentinel-2 pixels | CLOSED — Earth Search public COGs | no CDSE account needed |
| emergenzaxylella.it maps | ACCESS_BLOCKED — regional SSO (JOSSO) | not required for the join; tree coords are in CAMP. Human login if we ever need official polygons. |

## So what

We do **not** downgrade to comune nowcast. We proceed tree-level. Class is rare (0.86% olive-positive) and **collapses after 2021**. Evaluation is precision-recall, never accuracy, and the 2022–23 hold-out must be paired with a 2020–21 spatial fold. One-scene join is done: see `nowcast/SCENE_JOIN.md`. NDMI moves; NDVI does not.

# Crecco OQDS-Insight

Figshare 28191245, version 5. The current downloaded v5 shapefile contains **76,637** tree points with unique `fid` values. The `infection` field marks **2,340** points; its year field contains 432 rows labelled 2019 and 1,908 labelled 2020. These are photointerpreted disappearance/infection candidates derived from WorldView-2 observations, not official diagnostic results or proof of cause. Figshare's article description still states the earlier 77,068/2,225 figures and is stale relative to the downloadable v5 vector.

Local vectors: `raw/data/crecco_oqds_insight/pts_OQDS.*` (gitignored rasters not downloaded). CRS EPSG:32633. Point shapefile. Direct binary verification on 22 August 2026 found 70 duplicate-coordinate rows and median nearest-neighbor spacing of 5.062 m.

CAMP olives whose coordinates fall in the Crecco point-set bbox (axis-aligned, not a hull):

| Campaign | Olive in bbox | Olive + |
|---|---:|---:|
| 2016–17 | 3,052 | 0 |
| 2017–18 | 3,594 | 16 |
| 2018–19 | 4,797 | 86 |
| 2019–20 | 10,330 | 303 |
| 2020 | 5,386 | 435 |
| 2021 | 3,600 | **1,683** |
| 2022–25 | 0 | 0 |

Total: 30,766 olives, 2,523 olive positives. After 2021 the official clipboard left this box.

Released WV2 RGB/NDVI TIFFs are listed on figshare (~2.5 GB). Not pulled yet. Full 8-band commercial WV2 is not in the file list.

# Exposure profile — Cantine Amalberga (Ostuni)

Demo of product P1. Point: Contrada Vallegna, SP17 km 6, Ostuni (BR), 40.72635 N 17.50158 E (coordinates from a public winery directory; parcel boundaries would replace the point in a real engagement). Source data: 12 official Regione Puglia monitoring workbooks, 2013–2025, olive rows only. Engine: `producers/front_exposure.py`. Raw output: `producers/cache/exposure_cantine-amalberga-ostuni.json`.

## What the official record shows around this estate

| Campaign | Olive tests ≤10 km | Positives ≤10 km | ≤3 km | ≤1 km | Nearest positive |
|---|---:|---:|---:|---:|---:|
| 2013–14 | 80 | 0 | 0 | 0 | 57.5 km |
| 2014–15 | 6 | 0 | 0 | 0 | 26.4 km |
| 2016–17 | 26,123 | 1 | 0 | 0 | 9.0 km |
| 2017–18 | 16,901 | 42 | 16 | 0 | 1.5 km |
| 2018–19 | 14,916 | 167 | 55 | 0 | 1.3 km |
| 2019–20 | 16,798 | 454 | 224 | 76 | 0.8 km |
| 2020 | 42,722 | 718 | 318 | 138 | 0.37 km |
| 2021 | 5,957 | 2,191 | 1,250 | 75 | 0.33 km |
| 2022 | **0** | 0 | 0 | 0 | 14.6 km |
| 2023 | **0** | 0 | 0 | 0 | 14.8 km |
| 2024 | **0** | 0 | 0 | 0 | 18.6 km |
| 2025 | **0** | 0 | 0 | 0 | 29.9 km |

First official olive positive within 10 km: 2016–17. Within 3 km: 2017–18. Within 1 km: 2019–20.

## The two facts that matter to this estate

1. **The front crossed this property's neighborhood between 2017 and 2021.** Nearest confirmed positive went from 9 km (2016–17) to 330 m (2021). The 2019–21 campaigns confirmed 76–138 infected olives within a 1 km walk of the cellar.

2. **Official monitoring then stopped.** Zero olive tests within 10 km in the 2022–2025 campaigns. The 14.6–29.9 km "nearest positive" figures in those rows measure where testing moved, not where the bacterium is. An estate here has had no official information about its own surroundings for four campaigns — while facing replant, grafting, grubbing, and landscape-value decisions.

## Front context (descriptive)

Raw axis-projection front trace (epicenter→Bari axis, Gargano cluster excluded): ~11.4 km/yr over 2016–2025. Consistent in magnitude with the only published empirical estimate, 10.0 km/yr for 2013–2018 (Kottelenberg et al. 2021, computed from the same monitoring series). The estate now sits ~100 km behind the 2025 detection front. Caveat: survey geometry moves between campaigns; this is a descriptive trace, not the design-adjusted estimate.

## What the productized report adds beyond this demo

- Parcel polygons instead of a point; per-parcel ring statistics.
- Block-scale Sentinel-2 canopy-decline monitoring (multi-date incidence, Hornero-style) to restore a data feed where official testing stopped — explicitly not tree-level previsual detection, which this project's own null results rule out for Sentinel-2.
- Zone-status obligations and subsidy options for the parcel's demarcation status (playbook, pending S9 verification).
- Cultivar context from repeat-tested coordinates (with survivorship caveats).
- For the wine side: ST1/Pierce's-disease watch status for the Bari–Ostuni corridor (declared non-expanding Feb 2026; monitored).

## Caveats carried by every number above

Testing intensity varies by design; zero positives with zero tests is silence, not health. Positives are felled after detection (survivorship). 2023 covers a partial campaign. 2024–25 non-olive subspecies records are excluded from olive rows.

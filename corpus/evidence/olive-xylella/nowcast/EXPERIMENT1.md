# Experiment 1

Question: how many days before an official positive diagnostic result does out-of-area discrimination stay above matched negative controls?

## Design

- Labels: `CAMP_2021.xlsx` olives inside the Crecco Brindisi bbox. Diagnostic result, not a named assay.
- 1,683 positive, 1,917 negative. 1,679 1:1 matches: ±30 days, same comune else ≤5 km, cultivar locked when both known (457), ≥60 m apart (different 20 m SWIR cell). Median distance 68 m.
- Lags: −365, −180, −90, −60, −30, 0, +90 days from the positive's diagnostic date. Sentinel-2 scenes ≤10 days from target (median error 1–2 days for −90…0).
- Analysis is paired: ΔNDMI = pos − neg per pair. Inference is a two-sided sign-flip permutation on median(Δ) that flips whole 1 km spatial clusters (10,000 permutations). Both arms must be SCL-valid.
- Pixel independence: 1,325 pairs at lag 0 occupy 1,028 unique 20 m cells and 14 one-km clusters. Rows are not independent experiments; the cluster flip accounts for this.

## Result

Median ΔNDMI and cluster sign-flip p, all pairs:

| Lag | n | median Δ | frac Δ<0 | p |
|---:|---:|---:|---:|---:|
| −365 | 331 | +0.011 | 0.46 | 0.43 |
| −180 | 902 | −0.011 | 0.52 | 0.35 |
| −90 | 1330 | −0.012 | 0.56 | 0.13 |
| −60 | 1325 | −0.007 | 0.54 | 0.25 |
| −30 | 1313 | −0.006 | 0.53 | 0.30 |
| 0 | 1325 | −0.010 | 0.54 | 0.14 |
| +90 | 1164 | +0.004 | 0.48 | 0.57 |

Subgroups at every lag — Ostuni-only, Ostuni-out, cultivar-locked (457 pairs; Cellina di Nardò, Ogliarola barese/salentina, Toscanina, Cerasella, Oliva rossa each n≥30), symptom-absent both arms, dry-scene and wet-scene halves — none reaches p < 0.05. No cultivar shows a consistent negative Δ.

The earlier unpaired table reported p 0.002–0.03 at −90…0. Those p-values treated 1,679 spatially clustered rows as independent. Paired, cluster-aware inference removes the effect.

## Verdict

**Negative for branch A0** (raw paired absolute NDMI at 10/20 m). After matching on place, date, and cultivar, and with spatially honest inference, there is no pre-diagnostic signal at any tested lag in the 2021 Crecco-box cohort. Median Δ is −0.006 to −0.012 at −90…0 days, indistinguishable from spatial noise.

This closes one hypothesis, not Artifact A. The null does not distinguish "no precursor exists" from "20 m SWIR mixing destroys it" — a crown contributing 20–30% of a 400 m² pixel dilutes any within-crown change below this design's sensitivity. Open branches and the discriminating tests are in `nowcast/ARTIFACT_A.md` (temporal anomaly A1, crown-fraction dependence A2, Crecco crown-scale rasters A3, WV-3 SWIR A4, airborne physiology A5). A 2022 transfer test waits on a surviving signal.

Files: `nowcast/cache/experiment1_paired.json`, `experiment1_matches_2021.csv`, `experiment1_lags_2021.csv`. Scripts: `experiment1_match.py`, `experiment1_extract.py`, `experiment1_paired.py`.

# Experiment 1, branch A1 — within-tree temporal anomaly (change detection)

Branch A0 asked whether the positive tree's pixel is absolutely drier than its
matched control at fixed lags. It closed negative (`EXPERIMENT1.md`,
`ARTIFACT_A.md`). A1 asks the stronger change-detection question: did the
positive tree's spectral trajectory depart from **its own prior-year seasonal
baseline**, more than its matched negative departed from its own, in the
weeks-to-months before the diagnostic date?

## Method

- **Cohort.** The same 1,679 matched pairs
  (`cache/experiment1_matches_2021.csv`). Diagnostic dates 2021-09-20 to
  2021-10-29.
- **Series.** All 161 Sentinel-2 L2A scenes over tile 34TBL, 2020-01-15 to
  2022-02-28, cloud < 30% (Earth Search STAC, AWS COGs). Each scene sampled at
  all 3,358 points; only SCL ∈ {4, 5, 7} observations kept (73.7% of
  540,638 samples). Indices: NDVI, NDMI, NDRE, NMDI (B12 present in all
  161 scenes).
- **Baseline.** For each point, the expected value at day-of-year *d* is the
  median of its own observations before 2021-03-01 within ±15 days of *d*
  (circular DOY, ≥2 obs required). Anomaly = observed − expected. Median
  baseline depth: 82 obs per point.
- **Features per pair** (`cache/experiment1_temporal.csv`):
  - `d_anom_*` — mean anomaly over the pre-diagnostic window
    [pos_date − 120 d, pos_date − 30 d], positive arm minus negative arm.
    Requires ≥3 valid obs per arm (median available: 21 pos, 20 neg).
  - `d_slope_*`, `d_anom_slope_*` — OLS slope of the raw index / of the
    anomaly over [pos_date − 120 d, pos_date], pos − neg.
  - `d_step_*` — change-point proxy: mean anomaly in (−60, 0] minus
    [−120, −60], pos − neg.
- **Pre-registered hypothesis** (stated before inference ran):
  `d_anom_ndmi < 0` — the positive tree's NDMI drops below its own seasonal
  baseline harder than its control does.
- **Inference.** Sign-flip permutation on the median, flipping whole 1 km
  UTM33 clusters of the positive point (14 clusters, 10,000 perms, seed 42) —
  the same protocol as the A0 paired analysis.
- **Counts.** 1,679 pairs → 1,511 with a usable SCL-clean series in both arms
  (168 dropped, mostly persistent-nodata points on split data-takes) → 1,430
  with ≥3 clean pre-window obs in both arms (81 dropped as sparse). All tests
  below use n = 1,430 pairs.

## Results

Δ = positive arm − negative arm. Disease predicts Δ < 0 for every row.
p one-sided is for Δ < 0; 16 features tested, so a Bonferroni-style bar is
p ≈ 0.003.

| Feature (pos − neg) | n | median Δ | frac < 0 | p two-sided | p one-sided (<0) |
|---|---|---|---|---|---|
| **NDMI anomaly, −120..−30 d (pre-registered)** | 1430 | **+0.0019** | 0.485 | 0.546 | **0.730** |
| NDVI anomaly, −120..−30 d | 1430 | +0.0019 | 0.489 | 0.453 | 0.781 |
| NDRE anomaly, −120..−30 d | 1430 | +0.0026 | 0.473 | 0.426 | 0.790 |
| NMDI anomaly, −120..−30 d | 1430 | +0.0004 | 0.496 | 0.737 | 0.638 |
| NDMI raw slope, −120..0 d | 1430 | +0.000002/d | 0.498 | 0.944 | 0.543 |
| NDVI raw slope | 1430 | −0.000021/d | 0.520 | 0.403 | 0.204 |
| NDRE raw slope | 1430 | −0.000016/d | 0.510 | 0.481 | 0.246 |
| NMDI raw slope | 1430 | −0.000013/d | 0.513 | 0.630 | 0.315 |
| NDMI anomaly slope | 1430 | −0.000048/d | 0.531 | 0.092 | 0.047 |
| NDVI anomaly slope | 1430 | −0.000062/d | 0.535 | 0.130 | 0.061 |
| NDRE anomaly slope | 1430 | −0.000075/d | 0.552 | 0.063 | 0.032 |
| NMDI anomaly slope | 1430 | −0.000009/d | 0.508 | 0.740 | 0.363 |
| NDMI step (late − early anomaly) | 1430 | −0.0018 | 0.515 | 0.347 | 0.175 |
| NDVI step | 1430 | −0.0044 | 0.527 | 0.147 | 0.072 |
| NDRE step | 1430 | −0.0034 | 0.539 | 0.239 | 0.120 |
| NMDI step | 1430 | −0.0009 | 0.510 | 0.498 | 0.244 |

Full numbers: `cache/experiment1_temporal_stats.json`.

Context for the headline row: both arms sat slightly **above** their 2020
baselines in the pre-diagnostic window (mean NDMI anomaly +0.012 pos, +0.010
neg), and the paired difference is centered near zero with wide spread
(IQR −0.030 to +0.033). The soon-to-be-positive trees were not anomalously
dry relative to their own history, and not more anomalous than their matched
controls 68 m away.

## Verdict

**A1 is null.** The pre-registered feature — positive tree drops below its own
prior-year NDMI baseline more than its matched control in the 30–120 days
before diagnosis — goes the wrong way (median +0.0019, one-sided p = 0.73) and
so do all four pre-window anomaly means. The only rows that lean the predicted
direction are the anomaly-slope features (NDRE one-sided p = 0.032, NDMI
p = 0.047), but they are two of 16 tests, fail any multiple-comparison
correction, split pairs almost 50/50 (frac < 0 ≈ 0.53–0.55), and their effect
size is ~0.006–0.009 index units over the full 120-day window — an order of
magnitude below scene-to-scene noise. Reframing onset as change detection
against the pixel's own seasonal history does not recover a signal that the
absolute-NDMI test missed. This strengthens the A0 negative: at 10 m Sentinel-2
resolution, on official-diagnostic labels with ~68 m matched controls, neither
level nor trajectory separates soon-to-be-positive olive trees from their
negative neighbors in the months before diagnosis.

## Reproduce

```
.venv/bin/python nowcast/experiment1_temporal.py extract    # ~20 min, cached per scene
.venv/bin/python nowcast/experiment1_temporal.py features
.venv/bin/python nowcast/experiment1_temporal.py infer
```

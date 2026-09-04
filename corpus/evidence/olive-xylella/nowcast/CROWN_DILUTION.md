# Branch A2: crown/soil dilution test of the Sentinel-2 NDMI null

Tests whether the closed A0 null (no pre-diagnostic ΔNDMI on 1,679 matched
2021 pairs; commit 2f72abb) is an artifact of spatial dilution: an olive
crown occupies only part of a 100–400 m² Sentinel-2 pixel. Method: measure
per-tree crown fraction of the Sentinel 20 m and 10 m UTM33 grid cell from
released 0.5 m WorldView-2 data, then re-run the paired ΔNDMI sign-flip test
stratified by crown purity.

Scripts: `nowcast/crown_fraction_2021.py`, `nowcast/crown_stratified_paired.py`.
Outputs: `nowcast/cache/crown_fraction_2021.csv`,
`nowcast/cache/crown_fraction_2021_meta.json`,
`nowcast/cache/crown_stratified_paired.json`.

## WV2 source data

- Source: figshare article 28191245 (OQDS-Insight; Crecco, Morelli,
  Raparelli, Di Giulio, Bajocco, CREA; Data in Brief 60:111615, 2025).
  Downloaded 2026-08-15 into `raw/data/crecco_oqds_insight/` (gitignored):
  `2021_WV2_NDVI.tif` (562,746,246 B), `2021_WV2_RGB.tif` (422,074,356 B),
  `2021_WV2_RGB.tif.aux.xml`. All transfers completed; no ACCESS_BLOCKED.
- Acquisition dates: the paper states one WV2 image per year "acquired
  during the summer months of 2019, 2020, and 2021". Exact day-level dates
  are not published in the paper, the figshare metadata, or the GeoTIFF tags
  (tags contain only `AREA_OR_POINT=Area`). Recorded as: 2021, summer,
  day unknown.
- Native resolution and processing: WV2 panchromatic 0.5 m, multispectral
  2 m; visible + NIR pansharpened to 0.5 m by Gram-Schmidt. Both rasters are
  0.5 m, EPSG:32633, 14462 × 9727 px, bounds 706165–713396 E,
  4508710.5–4513574 N, clipped to CORINE 2018 olive-grove class 2.2.3.
- Product semantics (measured, not documented by the authors):
  `2021_WV2_NDVI.tif` is a **grayscale render** of NDVI, not a physical NDVI
  grid — uint8 0–255, bands 1–3 identical, band 4 constant alpha 255. White
  (255) is nodata fill outside the olive-class clip; within valid data no
  pixel equals 255. The uint8-to-NDVI mapping is not published, but the
  render is monotone: crowns bright, bare soil dark (verified visually
  against the RGB). Sufficient for a canopy mask; not for radiometry.
  `2021_WV2_RGB.tif` is 3-band uint8 with black (0,0,0) nodata; its
  footprint defines the valid mask (20.6% of the raster grid is valid).
- Registration: shifting the 76,637 `pts_OQDS` centroids over a ±6 m grid
  maximizes mean NDVI-gray at +1 m E, +5 m N (shallow peak, mean gray 73 vs
  64 at zero shift). Point-vs-raster registration uncertainty is therefore
  ≤ ~5 m, which is minor at 20 m cell aggregation. No shift was applied.

## Canopy mask and crown fraction

- Canopy = NDVI gray > threshold, evaluated over valid pixels only.
  Primary threshold: Otsu on all valid pixels = **66.24** (valid-pixel gray
  quantiles p25/p50/p75/p95 = 18/48/87/142). Sensitivity thresholds: 100
  and 150 (stricter canopy).
- Crown fraction of a tree's Sentinel cell = mean of the canopy mask over
  the WV2 pixels inside the 20 m (or 10 m) UTM33 grid cell containing the
  tree (`floor(x/20)*20` grid, matching `experiment1_paired.py` cells).
  Cells with <30% valid WV2 pixels are NaN.
- Footprint coverage of the 1,679 pairs: 1,042 positive arms and 947
  negative arms get a 20 m crown fraction; **768 pairs have both arms**
  inside the footprint. The rest are NaN (outside the 25 km² WV2 clip).
- Distribution (positive arm, 20 m, Otsu): median **0.349**, IQR
  0.262–0.472, p90 0.600, max 0.969. Only 6.3% of positive trees sit in a
  20 m cell with ≥60% canopy. Crown-dominated (>0.7) 20 m SWIR pixels are
  rare in these groves; the typical cell is 25–50% canopy, confirming the
  premise that most of a 20 m pixel is soil/inter-row.

## Stratified paired re-test

Identical machinery to `experiment1_paired.py`: ΔNDMI = pos − neg per pair
per lag (both arms `scl_ok` and finite), statistic = median(Δ), two-sided
sign-flip permutation flipping whole 1 km UTM33 clusters, 10,000 perms,
seed 42. Lags −90, −60, −30, 0 days.

### Naive stratification: terciles of positive-arm 20 m crown fraction (Otsu)

Tercile edges 0.289 / 0.416.

| Lag | Low (cf~0.22) med Δ | p | Mid (cf~0.36) med Δ | p | High (cf~0.53) med Δ | p |
|----:|---------:|------:|---------:|------:|---------:|------:|
| −90 | −0.0256 (n=317) | 0.063 | −0.0147 (n=315) | 0.171 | +0.0141 (n=307) | 0.003 |
| −60 | −0.0280 (n=318) | 0.080 | −0.0106 (n=299) | 0.270 | +0.0192 (n=316) | 0.002 |
| −30 | −0.0412 (n=313) | 0.017 | −0.0141 (n=326) | 0.220 | +0.0222 (n=322) | 0.031 |
|   0 | −0.0280 (n=324) | 0.043 | −0.0156 (n=307) | 0.246 | +0.0211 (n=313) | 0.002 |

This looks like a strong monotone gradient — but in the wrong direction for
disease (high-purity positives *wetter* than negatives), and it is a
**canopy-amount artifact**. ΔNDMI correlates with Δcrownfrac
(pos_cf − neg_cf) at r = 0.45 at every lag: more canopy in a cell
mechanically raises its NDMI (canopy is wetter than bare soil). Sorting
pairs by the positive arm's crown fraction also sorts Δcrownfrac (median
Δcf −0.17 / −0.01 / +0.18 across the terciles), so the "gradient" reproduces
the structural canopy difference, not infection. The same pattern holds at
thresholds 100 and 150 and for 10 m cells (see
`crown_stratified_paired.json`: `terciles_pos20_fixed_100`,
`terciles_pos20_fixed_150`, `terciles_pos10_otsu`).

### Confound-controlled stratifications

**Balanced pairs** (|pos_cf − neg_cf| < 0.10, stratified by pair mean crown
fraction; 950 rows). Halves, edge 0.338:

| Lag | Low purity med Δ | p | High purity med Δ | p |
|----:|---------:|------:|---------:|------:|
| −90 | −0.0139 (n=115) | 0.218 | −0.0095 (n=122) | 0.403 |
| −60 | −0.0107 (n=119) | 0.403 | +0.0075 (n=113) | 0.679 |
| −30 | −0.0024 (n=126) | 0.943 | −0.0134 (n=125) | 0.260 |
|   0 | −0.0139 (n=117) | 0.099 | +0.0007 (n=113) | 0.821 |

Balanced terciles (edges 0.302 / 0.377) are equally null: high-purity
medians −0.0172…−0.0067, all p ≥ 0.156. The most crown-dominated balanced
subset (mean cf ≥ 0.5; 24 pairs) has per-lag medians −0.012, −0.007,
−0.006, +0.014 — sign-unstable around zero.

**Min-arm purity terciles** (min(pos_cf, neg_cf), both arms measured;
2,776 rows; edges 0.234 / 0.328):

| Lag | Low med Δ | p | Mid med Δ | p | High med Δ | p |
|----:|---------:|------:|---------:|------:|---------:|------:|
| −90 | −0.0153 (n=235) | 0.062 | −0.0116 (n=222) | 0.404 | −0.0118 (n=238) | 0.071 |
| −60 | −0.0122 (n=239) | 0.081 | −0.0149 (n=218) | 0.335 | +0.0001 (n=226) | 1.000 |
| −30 | −0.0063 (n=234) | 0.296 | −0.0115 (n=238) | 0.347 | −0.0153 (n=239) | 0.067 |
|   0 | −0.0178 (n=238) | 0.015 | −0.0061 (n=221) | 0.395 | −0.0074 (n=228) | 0.263 |

No stratum shows a stable, significant negative Δ, and the only nominal
significance (lag 0, low-purity, p = 0.015, uncorrected across 12 cells) sits
in the **least** crown-pure stratum — the opposite of the dilution
prediction.

## Verdict

Branch A2 leans **negative**: crown/soil dilution does not explain the A0
null within the range this dataset can test. Once the mechanical
canopy-amount confound is removed (crown-fraction-balanced pairs, or
stratification by the minimum of the two arms' crown fractions), the paired
ΔNDMI stays at ~0 (−0.02 to +0.01, all cluster sign-flip p ≥ 0.06 except one
uncorrected p = 0.015 in the *least* pure stratum) at every purity level and
every lag, with no monotone strengthening of a negative Δ from ~20% to ~50%+
crown fraction. The naive positive-arm stratification does produce a
monotone gradient, but it tracks Δcrownfrac (r = 0.45 with ΔNDMI) and flips
to *positive* Δ in the high stratum — a structural canopy-amount effect,
not a disease signal, and itself direct evidence that S2 NDMI at 20 m is
dominated by how much canopy is in the pixel rather than canopy water
status. One honest limit: truly crown-dominated 20 m cells barely exist
here (6.3% of positive trees ≥ 0.6 crown fraction; balanced pairs at mean
cf ≥ 0.5 number only 24), so dilution at cf → 1 is untestable with S2 over
these groves — which is itself an argument that any crown-scale moisture
precursor requires sub-crown resolution (e.g., WV-3 SWIR at 3.7 m or
airborne), not a different S2 index.

## Findings

1. **Crown fraction is low and now measured.** Median 20 m-cell canopy
   fraction is 0.35 (IQR 0.26–0.47). Direct effect: a 20 m SWIR pixel over
   these groves is typically two-thirds soil. Second-order: any within-crown
   signal is attenuated ~3× before statistics start; S2-based olive stress
   products over Salento inherit this floor.
2. **The A0 null survives purity stratification.** Confound-controlled Δ is
   ~0 in every stratum and lag. Direct effect: A2's dilution reading is not
   supported in the testable range. Second-order: the case for requesting
   crown-resolving SWIR (WV-3) rests on the untestable cf → 1 region, not on
   a recovered S2 trend.
3. **ΔNDMI tracks Δcanopy-amount (r = 0.45).** Direct effect: naive
   per-tree S2 NDMI comparisons are confounded by planting density and crown
   size. Second-order: any future S2 analysis in this program must control
   crown fraction; `crown_fraction_2021.csv` now enables that for all 2021
   pairs inside the WV2 footprint.

## Next 5 steps

1. Decide branch A3 scope: WV-3 SWIR (3.7 m) feasibility over the Crecco
   footprint versus closing Artifact A's remote-moisture line entirely.
2. Re-run the A0 all-pairs test restricted to crown-fraction-balanced pairs
   as a robustness annex to the closed A0 write-up.
3. Use `crown_fraction_2021.csv` as a covariate in any residual S2 index
   tests (NDVI, red-edge) before abandoning S2.
4. Check the 2019/2020 WV2 rasters (optional downloads) for crown-change
   confirmation of removed/infected trees near matched positives.
5. Fold the crown-fraction distribution into the partner brief's methods
   caveats (S2 pixel composition over Apulian groves).

## Telos

Artifact A asks whether official diagnostic positivity has a remotely
detectable precursor after drought and cultivar matching. This turn closes
the dilution objection to the S2 null within S2's own resolution limits and
quantifies why crown-scale sensors are the only remaining route for a
moisture precursor. No live bacterium touched.

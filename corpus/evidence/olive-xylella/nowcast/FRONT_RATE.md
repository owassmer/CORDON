# Front rate c(t), 2013–2025 — design-adjusted estimate

Ranked action D1 from `queries/telos-review-S1-spread.md`. First front-rate
estimate from this repo's full 12-workbook monitoring series, including the
2019–2025 window no published study covers.

- Pipeline: `nowcast/front_rate.py`. Reproduce with
  `.venv/bin/python nowcast/front_rate.py` from the repo root.
- Machine-readable results: `nowcast/cache/front_rate.json`.
- Input: `producers/cache/combined.csv` (1,501,568 rows from the 12 official
  CAMP workbooks; olive rows only; see `data/CAMP_XLSX.md`).

## Method

Kottelenberg-style design adjustment (Kottelenberg et al. 2021, Sci Rep
11:1061). The survey frame moves every year, so raw positive counts measure
the clipboard, not the epidemic. The pipeline:

1. Filters to olive rows (1,275,507). Per `data/CAMP_XLSX.md`, all 2024–25
   olive positives are subsp. *pauca*, so olive-only filtering suffices.
2. Repairs 16 transposed lat/lon pairs (2017-18, near Ostuni); drops 1 row
   with implausible coordinates.
3. Excludes lat ≥ 41.35: the 2025 Cagnano Varano / Gargano focus (10,296
   rows, 260 positives) is a separate outbreak, not front motion.
4. Computes geodesic distance of every sample from the epidemic origin.
   Primary origin: Gallipoli area (40.055 N, 17.992 E). Sensitivity origin:
   centroid of 2013-14 positives (40.200 N, 18.130 E, Galatina area).
5. Aggregates each campaign into 5-km distance rings (2.5 and 10 km as
   sensitivities) and computes per-ring POSITIVITY = positives / tests.
6. Front position = center of the farthest ring with positivity ≥ 1%
   among rings with ≥ 200 tests (thresholds 0.5% / 2% and min-tests 50 as
   sensitivities). Also records the tested frontier. A front at or within
   one ring of the farthest adequately tested ring is flagged RIGHT-CENSORED.
7. Fits c(t) as the OLS slope of front position vs campaign mid-time (mean
   `t` per campaign) over three windows. CIs from 1,000 bootstrap reps
   (multinomial resampling of each campaign's ring × result table, which is
   identical in distribution to row resampling within campaign).

## Per-campaign front positions (primary config: Gallipoli origin, 5 km rings, 1%, ≥200 tests)

| Campaign | t mid | Front (km) | Boot 95% CI | Tested frontier¹ (km) | Inner frame edge² (km) | Censored | n tests | n pos |
|---|---|---|---|---|---|---|---|---|
| 2013-14 | 2014.11 | 42.5 | 42.5–42.5 | 107.5 | 12.5 | no | 8,487 | 188 |
| 2014-15 | 2015.46 | 57.5 | 57.5–57.5 | 67.5 | 12.5 | no³ | 49,364 | 4,173 |
| 2016-17 | 2016.93 | 57.5 | 57.5–57.5 | 97.5 | 7.5 | no | 145,408 | 1,576 |
| 2017-18 | 2017.96 | 67.5 | 67.5–72.5 | 92.5 | 47.5 | no | 173,925 | 3,828 |
| 2018-19 | 2019.17 | 87.5 | 82.5–87.5 | 127.5 | 62.5 | no | 54,363 | 1,072 |
| 2019-20 | 2019.98 | 87.5 | 87.5–87.5 | 112.5 | 72.5 | no | 41,399 | 1,371 |
| 2020 | 2020.74 | 117.5⁴ | 117.5–117.5 | 207.5 | 62.5 | no | 163,016 | 1,196 |
| 2021 | 2021.71 | 92.5 | 92.5–92.5 | 257.5 | 77.5 | no | 183,406 | 2,793 |
| 2022 | 2022.83 | — undefined⁵ | — | 207.5 | 87.5 | n/a | 227,770 | 358 |
| 2023 | 2023.90 | — undefined⁵ | — | 132.5 | 102.5 | n/a | 56,885 | 189 |
| 2024 | 2024.74 | 112.5⁶ | 112.5–112.5 | 147.5 | 87.5 | no | 59,701 | 154 |
| 2025 | 2025.50 | 142.5⁶ | 142.5–142.5⁷ | 227.5 | 92.5 | no | 101,487 | 78 |

¹ Farthest ring with ≥ 200 tests. ² Nearest ring with ≥ 200 tests — this
column documents the frame abandoning the south (the 2018 Lecce exit): the
inner edge marches from 12.5 km (2013–15) to 87.5–102.5 km (2022–25).
³ Margin to the frontier is only 10 km (2 rings); flips to censored under
10-km rings. The 2014-15 frame barely extended past the front.
⁴ Detached Monopoli/Polignano focus (64/4,070 = 1.6% in the 115–120 km
ring, positives at ~40.94 N 17.27 E). In 2021 the same ring holds 41/12,067
= 0.34%: the point qualifies or not depending on survey intensity, not on
front motion. The contiguous front in 2020 is at ~87.5 km (Fasano line).
⁵ No adequately tested ring anywhere reaches 1% positivity — nor even 0.5%
(2022 max: 0.28%; 2023 max: 0.48%). The front measure does not exist in
these campaigns. See attribution.
⁶ Detached establishment pockets, not a contiguous front: 2024 = Castellana
Grotte area (30/1,330 = 2.3% at 110–115 km); 2025 = Bari SW hinterland,
Bitetto/Modugno area (19/1,681 = 1.1% at 140–145 km), plus a sub-threshold
cluster at 155–160 km (Bitonto/Terlizzi area, 0.26%).
⁷ Front undefined in 33% of bootstrap reps (marginal 1.1% positivity).

Bootstrap CIs are ring-discretized and mostly collapse to a single ring.
They capture sampling noise only. Design uncertainty (ring width, threshold,
origin) is larger; see sensitivities.

## c(t) fits

| Window | Campaigns used | Slope (km/yr) | Boot 95% CI | Note |
|---|---|---|---|---|
| 2013–2018 | 2013-14, 2014-15, 2016-17, 2017-18 | **5.7** | 5.7–6.8 | Kottelenberg's data window |
| 2018–2021 | 2018-19, 2019-20, 2020, 2021 | **4.8** | 4.8–6.5 | dominated by the 2020 Monopoli artifact⁴ |
| 2018–2021 excl. 2020 | 2018-19, 2019-20, 2021 | **2.1** | — | contiguous front only (variant fit) |
| 2021–2025 | 2021, 2024, 2025 | **11.3** | 6.6–11.3 | NOT a front rate — see attribution |

No campaign is right-censored at the outer edge under the primary config:
after 2018 the region-wide buffer surveys test far beyond the front (tested
frontier 130–260 km). The frame problem post-2018 is not outer truncation.
It is (a) inner truncation — the infected south stops being tested — and
(b) redistribution of test intensity, which moves ring denominators and
flips threshold crossings (footnote 4).

## External check vs Kottelenberg 2021

Kottelenberg et al. 2021 (Sci Rep 11:1061), same monitoring series through
Apr 2018, distance-ring aggregation + logistic front model: **10.0 km/yr
(95% CI 7.5–12.5)**.

Our 2013–2018 estimate: **5.7 km/yr (boot CI 5.7–6.8; 3.5–7.9 across design
sensitivities)**. The CIs do not overlap. **The check fails at face value,
and the reason is the estimator, not the data.** Our front statistic is the
farthest *adequately tested* ring at ≥ 1% positivity — an "established
front" measure. Kottelenberg fits a logistic incidence profile and tracks
its displacement, which weights the sparse leading tail of low-positivity
detections ahead of the established front. That tail is real and our rule
discards it: in 2016-17 there are 111 positives beyond our 57.5 km front;
in 2017-18, 463 beyond 67.5 km. Their simulation check showed their
estimator approximately unbiased under the moving frame; ours is
deliberately conservative. The 0.5%-threshold sensitivity (7.9 km/yr)
reaches the bottom of their CI, consistent with this explanation:
the lower the threshold, the more leading tail is counted, the closer to
the logistic-profile rate. Consequence: treat the absolute level of our
c(t) as biased low by roughly 20–40% relative to a profile-displacement
measure. Within-method comparisons across periods remain valid, because
the rule is fixed across campaigns.

## Sensitivities (slope in km/yr; n = campaigns usable)

| Config | 2013–2018 | 2018–2021 | 2021–2025 |
|---|---|---|---|
| **Primary (5 km, 1%, ≥200, Gallipoli)** | 5.7 (n=4) | 4.8 (n=4) | 11.3 (n=3) |
| Rings 2.5 km | 6.8 (n=4) | 5.4 (n=4) | 11.2 (n=4) |
| Rings 10 km | 4.9 (n=3¹) | **0.0** (n=4) | undefined (n=1) |
| Threshold 0.5% | 7.9 (n=4) | 4.8 (n=4) | 11.3 (n=3) |
| Threshold 2% | 3.9 (n=4) | 3.5 (n=4) | 8.2 (n=2) |
| Min tests 50 | 5.7 (n=4) | 4.8 (n=4) | 11.3 (n=3) |
| Origin = 2013-14 centroid | 3.5 (n=4) | 1.9 (n=4) | undefined (n=1) |

¹ 2014-15 censored at 10-km rings and excluded.

Reading: 2013–2018 spans 3.5–7.9 depending on design — always positive,
always front-like. 2018–2021 spans 0.0–5.4 and collapses to ~2 km/yr when
the Monopoli intensity artifact is removed. 2021–2025 is either ~8–11 or
undefined: at 10-km rings and from the alternative origin, the 2024–25
far pockets dilute below 1% and no front exists at all. A number that
appears and disappears with ring geometry is not a front rate.

## Attribution of the apparent slowdowns

Three candidate explanations per anomaly: front dynamics, survey-frame
change, saturation of the measure. What the data can and cannot separate:

- **2019–2021 slowdown (≈2 km/yr contiguous-front variant vs ≈6 km/yr
  pre-2018).** Partly identifiable. The contiguous front (Ostuni→Fasano
  line, 87.5→92.5 km) is well measured in these campaigns: the frame
  extends 25–165 km beyond it and rings around it are heavily tested. The
  slow contiguous motion is unlikely to be a pure frame artifact. But the
  same campaigns show a detached focus 25 km ahead (Monopoli/Polignano,
  1.6% in 2020), so "the front slowed" and "the epidemic advanced" are
  simultaneously true — advance happened by long-distance jump, which a
  radial contiguous-front statistic structurally misses. This mirrors
  White et al. 2017 and the White-group ABC model (PLOS Comput Biol 2025):
  LDD, not local diffusion, sets the invasion speed (S1 review §A–B).
- **2022–2023 disappearance of the front.** Not identifiable, and the data
  say so twice over. First, the frame moved wholly ahead of the epidemic:
  the inner tested edge jumped to 87.5–102.5 km, so the 75–90 km rings that
  held 10–28% positivity in 2021 were barely retested (in 2022, rings at
  75–85 km have < 200 tests and zero recorded positives). Second, in the
  strip that was tested (95–125 km, 227,770 tests in 2022), positivity
  nowhere exceeds 0.3%. That low prevalence ahead of the front can reflect
  genuinely slow advance, post-2021 removals, or the survey's design
  prevalence and protocol changes (S1 review §A: 2024 monitoring-strip
  reduction; `data/CAMP_XLSX.md`: the 2022–23 test-budget starve). The
  monitoring data alone cannot separate these. Front rate for 2022–2023:
  UNIDENTIFIABLE.
- **2024–2025 re-acceleration (11.3 km/yr).** Not front motion. The
  qualifying rings are two detached pockets (Castellana 2024, Bari SW
  hinterland 2025) 20–50 km past the last well-measured contiguous front
  (92.5 km, 2021), in campaigns with 154 and 78 total positives. This is
  the documented LDD-jump regime (Bari San Giorgio 2024 jump, S1 review
  §B) plus focused follow-up surveys around new finds — exactly the
  condition where a threshold front estimator reads survey targeting as
  speed. Report as "farthest establishment advanced ~20–50 km beyond the
  2021 front line by 2025", not as c(t) = 11 km/yr.

## Verdict (for the exposure brief)

A defensible front rate exists for 2013–2018 (this analysis: 5.7 km/yr,
design range 3.5–7.9; published: Kottelenberg 10.0, CI 7.5–12.5 — the gap
is the estimator's leading-tail treatment) and, with caveats, for
2019–2021 (contiguous front ≈2–5 km/yr while jump foci advanced ~25 km
ahead). For 2022–2025 the front rate is UNIDENTIFIABLE from the monitoring
data: the survey frame left the infected zone, region-wide positivity
collapsed below every threshold the estimator can use, and the 2024–25
qualifying detections are isolated pockets whose "speed" appears and
disappears with ring geometry. Any exposure product must therefore use a
scenario band, not a number: contiguous-front scenario ≈2–5 km/yr,
historical-envelope scenario ≈8–12 km/yr, plus discrete jump risk of
~20+ km/yr-equivalent that no radial rate captures — with the explicit
sentence that **no empirical front-speed estimate exists for any period
after April 2018 in the published record, and this analysis shows the
2019–2025 monitoring data cannot pin one down without external
information (per-year survey-zone polygons and protocol records)**. This
is the honest scenario-band form that S8 review §A6 identifies as the only
sellable arrival-time product.

## Caveats

- The front statistic is radial and isotropic. It conflates the Adriatic
  (Bari) and Ionian (Taranto) arms and misses anisotropy. Kottelenberg
  had the same limitation.
- Campaign mid-times are data-derived means of sample dates; campaigns
  span up to 18 months, and the missing dedicated 2015-16 workbook leaves
  2015 inside the 2014-15 book (`data/CAMP_XLSX.md`).
- Ring discretization (5 km) quantizes front positions; bootstrap CIs are
  therefore too narrow and the sensitivity spread is the honest
  uncertainty.
- The censoring flag tests outer truncation only. Inner truncation and
  intensity redistribution are reported (inner-frame column, footnote 4)
  but not corrected. A full correction needs per-year survey-zone
  polygons, which are not on disk.
- Bootstrap = 1,000 reps, seed 20260816, multinomial over ring × result
  cells (identical in law to row resampling within campaign; chosen for
  speed, not as an approximation).
- 2024–25 subspecies mixing is handled by olive-only filtering (all
  2024–25 olive positives are *pauca*); non-olive hosts are excluded
  throughout, so the estimate is an olive-epidemic front, not an
  all-host front.
- Sample counts are test records, not unique trees; repeat tests of the
  same coordinates inflate ring denominators. Direction of bias on the
  front position: toward the front lagging where retesting concentrates
  behind the front (pre-2018), and toward dilution where follow-up
  surveys concentrate on new foci (2021+, footnote 4).

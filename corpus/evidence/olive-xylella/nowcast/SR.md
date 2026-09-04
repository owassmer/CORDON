# A7 — DiffFuSR 2.5 m on the matched 2021 cohort

Question: does paired ΔNDMI appear once sampling grain is 2.5 m, where crown fractions can exceed the 0.35 median that native 20 m S2 samples?

Pre-registered direction: Δ = pos − neg < 0 (positive arm drier). Inference: 1 km cluster sign-flip, 10 000 perms, seed 42.

## Method

- Model: DiffFuSR (NorskRegnesentral, MIT, arXiv 2506.11764). Diffusion RGB (BlindSRSNF, NAIP-harmonized) + MTFNetFusion of all 12 S2 bands to 2.5 m.
- Weights: `huggingface.co/NorskRegnesentralSTI/DiffFuSR` checkpoint `logs/blindsrsnf_aniso_naip_degraded_harm_large/version_1/checkpoint/last.ckpt`. Device: MPS. `skip=50` (20 diffusion steps). Same per-tile seeds as the script.
- Crop: Crecco pair box, UTM 34, 702×474 at 10 m. 21 scenes already used at lags −90/−60/−30/0.
- Empty tiles (no evaluation pixel) skipped. 22 of 35 tiles. Does not change the statistic.
- Crown mask: 2021 WV2 0.5 m NDVI, Otsu 66.24. Mean SR-NDMI over canopy pixels within 3 m of the point. Secondary: center 2.5 m cell.
- CONTROL: bicubic ×4 of the same 10 m cube. Not reported as SR.

## Sanity

| Check | DiffFuSR | Bicubic |
|---|---:|---:|
| corr(SR-NDMI aggregated to 20 m, native NDMI) | 0.903 | 0.895 |
| mean SR-NDVI(crown) − SR-NDVI(soil) | +0.024 | +0.022 |

The model tracks native reflectance and puts greener values on the WV2 canopy mask.

Crown-masked n ≈ 305–331 (only 40% of arms have ≥1 crown pixel). Center-pixel n ≈ 1 313–1 330.

## Result — DiffFuSR, crown-masked

| Lag | n | median Δ | frac Δ<0 | p two-sided | p one-sided (Δ<0) |
|---:|---:|---:|---:|---:|---:|
| −90 | 319 | −0.008 | 0.56 | 0.25 | 0.13 |
| −60 | 305 | −0.004 | 0.53 | 0.28 | 0.14 |
| −30 | 331 | −0.012 | 0.54 | 0.50 | 0.25 |
| 0 | 309 | −0.012 | 0.56 | 0.22 | 0.11 |

No lag meets p < 0.05 in the pre-registered direction.

High native crown fraction (A2 cf ≥ 0.6, n ≈ 40–44): median Δ is **positive** (infected wetter), opposite the registered direction. High tercile is null or wrong-signed. Bicubic CONTROL is the same pattern.

## Verdict

**A7 null.** Changing grain to 2.5 m with DiffFuSR does not produce a paired pre-diagnostic NDMI signal. The result matches A0 and the bicubic control, so the extra spatial detail is not a disease measurement.

Free Sentinel-2 optics are exhausted at native and super-resolved grain. Open Artifact A branches are A3 (released WV2 change), A4 (WV-3 SWIR), A5 (airborne HS+thermal).

Files: `nowcast/cache/sr_paired.json`, `sr_values_difffusr.csv`, `sr_values_bicubic.csv`. Script: `nowcast/experiment1_sr.py`.

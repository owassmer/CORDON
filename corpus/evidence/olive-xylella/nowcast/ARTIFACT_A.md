# Artifact A — hypothesis ledger

Artifact A is the measurement question: can infection physiology be observed before diagnosis, at tree scale? Branches close. The artifact closes only when every biologically plausible, accessible measurement branch is tested or proven inaccessible.

| Branch | Question | Status |
|---|---|---|
| A0 — raw coarse S2 | Does absolute 10/20 m NDMI distinguish individual diagnostic-positive trees? | **Closed negative** (commit 2f72abb: 1,679 matched pairs, paired ΔNDMI, 1 km cluster sign-flip, no lag p<0.05; subgroups null) |
| A1 — temporal S2 | Does within-pixel anomaly vs the pixel's own seasonal baseline and nearby controls carry signal despite mixing? | **Closed negative** (`nowcast/TEMPORAL.md`: 161 scenes 2020-01..2022-02, 1,430 pairs, pre-registered d_anom_ndmi goes the wrong way, median +0.0019, one-sided p 0.73; 2/16 slope features nominally p<0.05, dead after correction) |
| A2 — S2 + VHR unmixing | Was the A0 null caused by crown/soil dilution in the 100–400 m² pixel? | **Closed negative within S2's testable range** (`nowcast/CROWN_DILUTION.md`: 2021 WV2 canopy mask; median 20 m crown fraction 0.349 — pixels are ~2/3 soil; naive purity gradient is a Δcrown-fraction confound, corr 0.45; confound-controlled strata all null. Caveat: only 6.3% of positives reach cf≥0.6, so cf→1 is untestable with S2 — the direct argument for A4 |
| A3 — released crown-scale optical | Do Crecco WV2 rasters (2019–2021) and Puglia 0.15 m CIR show crown-level precursor or progression on diagnosed trees? | Open; 2021 WV2 NDVI/RGB on disk, 2019/2020 rasters and 2015_IR timing not yet inspected |
| A4 — fine SWIR | Does ~3.7 m WorldView-3 SWIR reveal what 20 m S2 cannot? | Unrun; ESA TPM proposal route |
| A5 — airborne physiology | Does the matched diagnostic cohort show Zarco-class HS+thermal traits at crown scale? | Unrun; partner route |
| A6 — operational transfer | Does any surviving signal travel north with the front? | Later; requires a surviving signal |
| A7 — free super-resolution S2 | Does the matched Δ signal appear at ~2.5 m once crown fractions rise above the 0.35 median that native S2 samples? | **Closed negative.** DiffFuSR (NAIP-harmonized, all 12 bands, MPS). Crown-masked n≈310, median Δ −0.004 to −0.012, two-sided p ≥ 0.22 at −90/−60/−30/0. High-cf (A2 ≥0.6) wrong-signed. Sanity: corr vs native 0.90; crown NDVI > soil. Bicubic CONTROL same null. See `nowcast/SR.md`. |

## Interpretation rule

The A0 null has two live readings: (1) no useful physiological precursor exists; (2) a precursor exists and 20 m SWIR mixing destroys it. A0 cannot distinguish them. A 20 m SWIR pixel is 400 m²; a crown contributing 20–30% of it dilutes any within-crown change to a few percent of the measurement. A null from a 400 m² measurement is not a null about a process inside one crown.

A2 is the cheapest discriminator: if |paired Δ| grows with crown fraction, the dilution reading gains direct evidence; if it stays zero in crown-dominated pixels, the against-S2 reading strengthens.

## Standing cautions

- 68 m pairing cancels regional weather, not irrigation, soil, management, crown size, or understory.
- Cultivar is locked on only 457 / 1,679 pairs.
- S2 remains valid at orchard/front scale. The closed branch is individual-tree inference from absolute NDMI.
- Do not massage A0 positive. Preserve it as the rationale for A4/A5 access requests.

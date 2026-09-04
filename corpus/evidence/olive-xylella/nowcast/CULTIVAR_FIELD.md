# Cultivar field-conversion analysis — gate result

Ranked action #2 (`queries/telos-synthesis.md`). Pre-registered gate: Leccino
must emerge field-resistant in stratum-adjusted comparison against the
susceptible reference, or the cultivar table stays internal.

**Gate verdict: NOT PASSED at the registered bar. The table stays internal.**

## Design

- Unit: exact coordinate (5-decimal, ~1 m) tested in two or more campaigns.
- Transition: consecutive visits where the earlier result is negative;
  outcome = positive at the later visit. Positives exit (felling), so
  conversions are terminal.
- Source: 12 official workbooks 2013–2025, olive rows, 16,771 transitions,
  845 conversions, 12,451 (74%) with an inspector-recorded cultivar
  (mojibake variants of "Cellina di Nardò" repaired before grouping).
- Reference: Cellina di Nardò + Ogliarola salentina pooled
  (5,408 transitions, 477 conversions, crude 8.8%).
- Adjustment: Mantel-Haenszel risk ratio over campaign-pair × comune strata;
  one-sided stratified permutation p (exact hypergeometric, 5,000 draws,
  seed 42).
- Script: `nowcast/cultivar_conversion.py`. Full output:
  `nowcast/cache/cultivar_conversion.json`.

## Results

| Cultivar | n | Conv | Crude rate | MH RR vs ref | p (one-sided) |
|---|---:|---:|---:|---:|---:|
| Leccino | 956 | 34 | 0.036 | **0.785** | **0.058** |
| Frantoio | 145 | 3 | 0.021 | **0.348** | **0.005** |
| Coratina | 264 | 6 | 0.023 | 0.612 | 0.091 |
| Ogliarola barese | 3,578 | 60 | 0.017 | 0.930 | 0.273 |
| Cellina di Nardò (ref part) | 1,517 | 214 | 0.141 | — | — |
| Ogliarola salentina (ref part) | 3,891 | 263 | 0.068 | — | — |

## Reading

1. **Leccino: direction right, bar missed.** Crude conversion is 2.4× lower
   than the reference, but most of that gap is geography: after campaign-pair
   × comune stratification the RR is 0.785 with p = 0.058. Per the
   pre-registration this does not pass. No client sees a cultivar table.
2. **The metric partly explains the modest RR.** PCR conversion measures
   infection incidence. Published Leccino resistance is titre- and
   symptom-based: Leccino becomes infected but carries lower load and less
   desiccation. A conversion-rate positive control is therefore biased toward
   the null for exactly the cultivar it tests. This is a metric limitation,
   not an excuse; the gate stands.
3. **The method self-validates.** Ogliarola barese (susceptible, Bari
   province) shows a low crude rate (1.7%) that disappears entirely after
   stratification (RR 0.93, p 0.27) — its apparent advantage was
   front-arrival timing, which is what the strata are for.
4. **Frantoio is the strongest field signal** (RR 0.348, p 0.005, n = 145),
   independently convergent with Pavan 2021 greenhouse partial resistance
   and the BeXyl reports. Recorded; not released — the release gate is the
   Leccino positive control, not any single significant row.

## Upgrade path (what could pass the gate honestly)

1. Symptom-severity outcome among converters (the SINTOMO field on repeat
   visits) — matches the published resistance phenotype better than
   PCR incidence.
2. Distance-to-nearest-prior-positive as a continuous exposure control,
   replacing comune as the spatial stratum.
3. Time-at-risk weighting (gap between visits varies by pair).

## Caveats (binding on any future use)

Coordinate identity is not guaranteed tree identity. Positives are felled:
the panel is survivor-biased and conversions are right-censored. Repeat
testing concentrates where the survey chose to look. Inspector-recorded
cultivar is noisy. This is observational field data, not an inoculation
trial, and does not certify resistance.

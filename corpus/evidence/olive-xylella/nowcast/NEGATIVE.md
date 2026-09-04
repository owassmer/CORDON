# Free Sentinel-2: closed negative

Three designs and one grain change, same 2021 Crecco-box matched cohort (1 679 pairs). Public Sentinel-2 does not show a pre-diagnostic individual-tree signal.

| Branch | Question | Result |
|---|---|---|
| A0 | Absolute paired NDMI at 10/20 m | Null. Cluster sign-flip p ≥ 0.13 at every lag. |
| A1 | Temporal anomaly vs own seasonal baseline | Null. Pre-registered feature wrong-signed (median +0.0019, p 0.73). |
| A2 | Dilution: does Δ grow with crown fraction? | Null after confound control. Median 20 m cf = 0.349. cf ≥ 0.6 in 6.3% of positives. |
| A7 | Same test at 2.5 m (DiffFuSR, all 12 bands) | Null. Crown-masked p ≥ 0.22. High-cf subset wrong-signed. Bicubic control matches. |

This does not prove a physiological precursor is absent inside a crown. It proves the free S2 measurement (native or SR) cannot see one after matching.

Next measurements that could still answer the precursor question: Crecco 2019–2021 WV2 change (A3), WorldView-3 SWIR (A4), airborne HS+thermal (A5).

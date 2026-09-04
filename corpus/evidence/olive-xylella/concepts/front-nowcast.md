---
title: Front Nowcast
created: 2026-08-15
updated: 2026-08-15
type: concept
tags: [project, detection]
sources: [CORDON.md, data/DAY1.md]
confidence: high
contested: false
---

# Front Nowcast (Artifact A)

Drought-controlled suspicion map of the Bari / northern buffer.

Inputs: [[camp-csv]] labels + Sentinel-2 L2A (Planetary Computer / Copernicus). Method: gradient-boosted trees on spectral and water-stress features first. Oracle: 2022–23 official year (real in time, 358 olive positives — starved) **and** a spatial fold inside 2020–21. Do not rely on the later years alone.

Mandatory ablations: NDVI-only, drought/water-only, full. Metric: precision-recall. The positive class is ~1%.

Day-1 gate: **passed**. Tree-level labels exist. See `data/DAY1.md`.

Do not ship a pretty map that loses to NDVI.

## Related

[[previsual-detection]] · [[camp-csv]] · [[puglia-monitoring]] · [[resistance-decoder]]

---
title: CAMP_2020_2022.csv
created: 2026-08-15
updated: 2026-08-15
type: concept
tags: [dataset]
sources: [data/_inventory_camp_2020_2022.json, data/_stats_partial.json]
confidence: high
contested: false
---

# CAMP_2020_2022.csv

Official sample-level diagnostic table. Encoding cp1252, delimiter `;`.

## Columns

`ID` · `DATA_RILEVAMENTO` · `TIPOLOGIA` · `SPECIE` · `CULTIVAR` · `LATITUDINE` · `LONGITUDINE` · `COMUNE` · `RISULTATO` · `SINTOMO` · `PROVINCIA`

CRS: WGS84 geographic, Italian comma decimals. Empty cultivar ~10.5%. Symptom labels mixed case (`Assente`/`ASSENTE`).

## Full-file facts (verified 2026-08-15)

688,631 complete rows · 605,617 joinable olives · 5,195 olive positives (0.858%) · every complete row has coords · 20 Jan 2020 – 30 Jun 2023 · no Lecce · lat 40.39–41.93 · lon 15.15–17.78.

Olive positives by year: 2020 1,976 · 2021 2,861 · 2022 235 · 2023 123. Hold-out years are real and starved.

CAMP_2020_2023.csv exists in CKAN with an empty URL. 2023 is already inside this file.

## Related

[[puglia-monitoring]] · [[front-nowcast]] · [[previsual-detection]]

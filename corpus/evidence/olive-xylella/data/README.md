# data/ — inventories and derived tables

Raw downloads live in `../raw/data/` and are gitignored.
This directory holds **inventories, licenses, and derived summaries** — the evidence spine.

## License / terms

| Source | What | License / terms | Local path |
|---|---|---|---|
| Regione Puglia CKAN, Sezione Osservatorio Fitosanitario | CAMP monitoring CSV (file name 2020–2022; rows through 30 Jun 2023) | Italian open data / CKAN dataset `dati-monitoraggio-xylella-fastidiosa`. Reuse: cite Regione Puglia – Osservatorio Fitosanitario. | `raw/data/CAMP_2020_2022.csv` (complete, 81,999,815 bytes) |
| Same package | CAMP_2020_2023.csv | Listed, **URL empty**. Cannot download. | — |
| emergenzaxylella.it | Official maps | Site connection-reset from this host 2026-08-15 | — |
| Copernicus / Earth Search Sentinel-2 L2A | 10 m imagery | Free public COGs via Element84 Earth Search (no account) | sampled, not stored |
| Microsoft Planetary Computer | STAC catalog of S2 | Free catalog search proven; signed asset URLs for pixels | catalog only |

## Files here

- `README.md` — this file
- `DAY1.md` — Day-1 gate report
- `_inventory_camp_2020_2022.json` — column inventory
- `_stats_partial.json` — class balance, spatial extent, olive joinability

## CRS (inferred, then checked)

Italian decimal-comma WGS84 geographic coordinates (`LATITUDINE`, `LONGITUDINE`).
Treat as **EPSG:4326**. Not a projected CRS. Convert comma → dot before any GIS join.

## Honesty

Full file verified 2026-08-15. Earlier partial-file stats (335k rows, through Sep 2021) are superseded. Quote `data/_stats_partial.json` as it stands after that verification — the filename is stale, the contents are the full campaign.

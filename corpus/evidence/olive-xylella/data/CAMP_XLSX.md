# Official CAMP workbooks (emergenza) — digested 15 Aug 2026

Source: Owen-downloaded `CAMP_*.xlsx` from http://emergenzaxylella.it/portal/portale_gestione_agricoltura/Download/mon_xf
Local copy: `raw/data/camp_xlsx/` (gitignored). Inventory JSON: `data/_camp_xlsx_inventory.json`.
Missing from the download: a dedicated 2015–2016 workbook. 2015 lives in `CAMP_2014_2015`; 2016 in `CAMP_2016_2017`.

These are **not** the CKAN CSV we already had. That CSV was a 2020–mid-2023 extract of the northern buffer. These are the campaign books from first detection through 19 Dec 2025.

## The number that matters: the front walked through towns

Olive PCR-positives, by where they piled up (top comunes). Read it as a marching line, south → north.

| Campaign | Olive + | Where they were |
|---|---:|---|
| 2013–14 | 292 | Trepuzzi, Galatina, **Lecce**, Gallipoli |
| 2014–15 | **4,173** | **Trepuzzi 3,369** — the Salento fire, counted |
| 2016–17 | 1,576 | Oria, Francavilla Fontana (south Brindisi) + leftover Lecce |
| 2017–18 | 3,828 | Oria, Francavilla, Ceglie, Carovigno, Brindisi |
| 2018–19 | 1,072 | Carovigno, San Vito, Ostuni — **zero samples east of lon 17.80** |
| 2019–20 | 1,371 | Carovigno, Ostuni |
| 2020 | 1,196 | Ostuni, Cisternino, Fasano |
| 2021 | 2,793 | Ostuni 1,516, Cisternino, Fasano |
| 2022 | 358 | Fasano, Castellana, Monopoli, Polignano (Bari coast) |
| 2023 | 189 | Monopoli, Fasano, Polignano |
| 2024 | 154 | Crispiano, Massafra, Castellana — **and 959 non-olive positives** |
| 2025 | 338 | **Cagnano Varano 260** (Gargano / Foggia) + Bari |

After 2018 the official clipboard **left Lecce**. Not because Xylella left. Because containment declared the south lost and spent the tests on the moving edge. Our old “Lecce is absent” finding was true of 2020–23. It is false of 2013–17. It is true again of every book from 2018 through 2025.

## Calendar-year olive positives (de-duplicated; prefer dedicated `CAMP_YYYY`)

2013: 36 · 2014: 256 · **2015: 4,171** · 2016: 117 · 2017: 2,983 · 2018: 845 · 2019: 855 · 2020: 1,128 · **2021: 2,793** · 2022: 235 · 2023: 130 · 2024: 154 · 2025: 338.

The 2022 “collapse” is in the official books, not a CKAN glitch. 2025 is up, but it is not a return to 2021 Brindisi. It is mostly one Gargano town.

## 2024 is a different disease on the same form

`SUBSPECIE` on all 2024 positives: multiplex 617 · fastidiosa (ST1) 339 · pauca 157.
Olive positives in 2024: **154, all pauca**.
So ~960 of the 2024 “positives” are not the olive killer. They are the almond/grape/other-host story we flagged from the news. An olive nowcast that eats 2024 rows without filtering subspecies will train on the wrong bacterium.

2025 olive positives: 338, all pauca. The multiplex/ST1 wave is still there (36 + 20) but olive is pauca again.

## F7 is no longer hypothetical

PCR-positive olives the inspector marked **symptom-absent** (`SINTOMO = Assente`):

2014–15: 843 · 2016–17: 250 · 2017–18: **1,664** · 2018–19: 444 · 2019–20: 453 · 2020: 493 · **2021: 613** · 2022: 151 · 2023: 53 · 2024: 41 · 2025: 104.

That is the set that decides whether NDMI is early warning or a damage meter. 2021 alone has 613 such trees, with coordinates.

## What this does to CORDON (plain)

1. **We were looking at the middle of the movie.** The CKAN file was the Brindisi–Bari reel. The origin (Lecce/Trepuzzi 2015) and the 2025 Gargano reel were missing. A model fit only on 2020–23 is a model of one stretch of road.

2. **“They stopped testing Lecce” is policy, not a hole in these files.** If we want Salento labels we use 2013–17. We do not pretend 2024 Lecce PCR exists here.

3. **2024–25 without `SUBSPECIE` is poison.** Filter olive + pauca for Artifact A. Keep multiplex/fastidiosa as a separate detector if we ever care about grapes/almonds.

4. **The next experiment is cheaper than we thought.** F7 can be run on hundreds of official asymptomatic-positives, especially 2021 (same summer as our satellite scenes).

5. **2025 Cagnano Varano is a new island.** 260 of 338 olive positives in one Foggia town. Brindisi-August NDMI does not automatically apply. Either a new outbreak or a very focused survey. Do not average it into the Bari front.

6. **The 2022–23 starve is real.** Using those years as the only hold-out is still a bad exam. Pair with a 2020–21 spatial fold, and now we can also hold out 2024 olive-pauca and 2025 Gargano as *different* tests.

7. **Still no 2015–16 dedicated book.** If Owen can grab that one file from the same page, the 2016 trough (117 olive +) might fill in. Not required to move.

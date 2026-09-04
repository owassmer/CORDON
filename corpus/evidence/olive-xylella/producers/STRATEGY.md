# Producer value strategy

Objective: reduce the economic loss from *Xylella fastidiosa*. The €B projections aggregate farm-level losses. The accessible customer is the producer. This directory holds the producer-facing route.

## Customer

Any public or private producer of olive (and adjacent estate) products in or near the demarcated zones: olive estates, frantoi (mills), cooperatives, DOP consortia, masserie/agritourism estates, wine estates, nurseries. Exemplar: Cantine Amalberga (Vallegna Società Agricola S.r.l.), Contrada Vallegna, SP17 km 6, Ostuni — wine + hospitality estate in the comune that recorded the most olive positives of the 2021 campaign.

Market structure, existing suppliers, and willingness-to-pay are under adversarial review (`queries/telos-review-S7-producer-market.md`). Claim honesty and data licensing are under review (S8). Playbook content is under review (S9).

## The gap the first computation exposed

`front_exposure.py` on the Amalberga coordinates shows the pattern that defines the product:

1. **Approach phase (2013–2021):** the official front closed from 57 km to 0.33 km. Ring positivity within 3 km went 0 → 16 → 55 → 224 → 318 → 1,250. A producer with this information stream in 2017 had four years of warning.
2. **Abandonment phase (2022–):** zero official olive tests within 10 km of the estate in the 2022, 2023, 2024, and 2025 campaigns. Surveillance moved north with the containment front. Producers inside the passed zone lost their only official information flow at exactly the moment they face replant, graft, remove, and diversify decisions.

Both phases are product surface: pre-front producers need exposure tracking; post-front producers need decision support and restored monitoring.

## Product line (post-review, S7/S8/S9 verdicts applied)

| # | Product | Buyer / channel | Price shape | Status |
|---|---|---|---|---|
| P1 | **Playbook 2026 + per-farm exposure brief** (merged lead product): zone-conditional legal matrix, obligations calendar, felling triggers by regime, money/deadline tracker, cultivar table (gated), ST1 wine annex; personalized ring/testing/conversion panels | Consorzio DOP Collina di Brindisi, Oleificio Coop Ostuni (386 members), AMO Puglia, polo antixylella, GAL Alto Salento | €1–10k one-off per body; annual refresh | building; spec = S9-D, caveats = S8 |
| P2 | Block canopy-condition trend (cause-agnostic, Hornero formulation) | annex inside P1 only, never standalone; S9 kills producer-facing RS as a product | n/a | gated on Crecco-box validation; earliest v1.1 |
| P3 | Cultivar field-evidence sheet at point of sale | polo antixylella, nurseries, Aproli Bari, APROL Lecce | sponsor-funded | gated on the Leccino positive-control analysis |
| P4 | Monumental grafting triage | AMO Puglia, Save the Olives; CSR sponsor pays | €/project | blocked on LR 14/2007 registry acquisition |

Killed as products: farmer-paid SaaS, sensors, dashboards, labels, insurance, ST1 alarm service, zone-lookup app (S7-E, S9-E). Ring positivity + testing intensity is the strongest sellable claim (S8-A2); arrival times only as labeled scenario bands.

## Red lines

- No tree-level previsual detection claims from Sentinel-2. This repo's four pre-registered nulls (A0/A1/A2/A7) forbid it. Block-scale incidence only.
- Every ring statistic ships with testing-intensity context: zero positives with zero tests is silence, not health.
- Survivorship: positives are felled; coordinate silence after a positive is not recovery.
- Front velocity numbers carry the survey-design caveat until the design-adjusted estimate (S1 action D1) exists.
- Data licenses per S8 verdict before anything is sold.

## Validation path

1. Demo profile for the exemplar estate (done).
2. S7/S8/S9 verdicts harvested; synthesis picks the lead product.
3. Three pilot conversations through named channels (consortium, coop, DOP body) with the demo in hand.

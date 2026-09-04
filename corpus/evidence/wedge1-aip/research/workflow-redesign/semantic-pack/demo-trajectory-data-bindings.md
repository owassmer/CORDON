# Demo trajectory data bindings

Status: DRAFT — open decisions under grilling with Owen
Class: O0 build-planning artifact and extraction shot list. Lane agents extract exactly what this sheet names and nothing more. Every conditional binding here is resolved by Owen; no agent resolves a conditional mapping (extension-gated Plant, DL05/DL19/DL23, IM-labeled routes) on its own.

## Binding rules

- Real sources bind per the D0 mapping ledger with manifests (URL, query, retrieved_at, counts, sha256). Notional rows exist only where real data is genuinely underivable (D5), recorded build-side.
- Individual Plant identity comes only from externally preserved registry identity (monumental registry clip) or a validated inventory. No monitoring point, buffer, or detection mints a Plant.
- Monitoring snapshots are frozen before any recording; nothing binds to a live layer at record time.

## The four demo change events

| Event | Beat | Change class | Binding (recon-verified) |
|---|---|---|---|
| E1 | Q1 | official monitoring positive | **BOUND:** Bari sample `1964901`, 26 Jul 2026, OLIVO, POSITIVO, CNR 64P/2026 — freshest positive in Puglia, live-verified by Connor; layer `Operationals2/MonitoraggioXFSintesiAttuale/MapServer/1`; zone context DDS 92/2024 L10/L11. Secondary: Crispiano cluster (72 positives) for the containment-side affected picture |
| E2 | Q2/Q4 | stale load-bearing source → INDETERMINATE | **BOUND:** two verified stale/identity events — (a) CKAN package `dati-monitoraggio-xylella-fastidiosa` (metadata frozen 2025-09-17, resource `2ffb6c35…` empty URL) vs live ArcGIS July 2026 confirmations; (b) Valenzano: DDS 2/2026 institutes the legal area but no Valenzano-named layer exists — act-vs-geometry identity mismatch |
| E3 | Q3 context | programme act movement | **BOUND:** Article 6 DDS 53/2026 scorrimento (positions 3355–3758, €7,490,680.98) → DDS 120/2026 delegation reopening (closed 08-08-2026); cohort now at delegation/ARIF-instruction boundary — the true current operator state |
| E4 | Q5/Q6 | liquidation/payment-order via legal/public ingestion | **BOUND (B4):** DDS 167/2025 (Sammichele final balance €12,955.54; fullest public chain: grant DDS 88/2023 → advance DDS 111/2023 → verification → liquidation; PDF sha256 `af68e7dd…557a7d`, byte-verified by Connor). Secondary replay/variant: DDS 216/2025 (private nursery €226,708.75, antimafia condition subsequent). Cash line stays INDETERMINATE: no public treasury settlement exists anywhere — order ≠ cash is the record's own shape |

## Open binding decisions (grilling queue)

| # | Decision | Options under consideration | Status |
|---|---|---|---|
| B1 | Demo geography: which comuni anchor cadastre/zone/monitoring/monumental clips | recon-informed | ACCEPTED (Owen, 2026-08-23), demo scope only: dual-anchor — Crispiano (recovery + Art. 13 containment duty, 72 current 2026 positives) + Bari-belt cluster (Bari–Modugno/Bitonto–Capurso–Triggiano–Noicattaro–Valenzano: three stacked subspecies, ST1 400 m duty chain, freshest positive 1964901, Valenzano act-vs-layer mismatch). Cagnano Varano narrated. Standing constraint: geography clips bound the DEMO extraction only; the product's source universe remains the full D0 ledger and recon corpus — no product structure narrows to demo geography |
| B2 | Programme route anchoring the funding/capacity trajectory | Article 6 reimpianto (DDS 53/120 graduatoria chain); CSR SRD01.01B | ACCEPTED (Owen, 2026-08-23): C-bounded — Article 6 anchors the full trajectory and E3; SRD01.01B enters as Programme/Instrument/window population rows only, no trajectory, first descope cut |
| B3 | Plant population binding | four-class universe | ACCEPTED (Owen, 2026-08-23): populate (1) monumental registry clip; (2) officially sampled/confirmed plants (ID_CAMPIONE identity); (3) act-individuated eradication targets where acts individuate; (4) intervention-created replanted plants with as-built identity (notional under D5 until real coop records). Clarification recorded: as-built planting records are a valid identity source — a physical record, not a detection; the arbitrary-detection prohibition stands. All clipped to B1 geography; everything else stays parcel-grain |
| B4 | E4 outcome act | recon-ranked outcome candidates | PROVISIONAL (Connor recommendation, cheap to overturn): DDS 167/2025 primary (fullest public chain, named public beneficiary, byte-verified), DDS 216/2025 secondary (private beneficiary, condition subsequent). ARIF DEL 994 chain rejected for E4 — publicly unreconstructible at liquidation |
| B5 | Notional private layer size and composition | sized to closed bindings | PROVISIONAL (Connor recommendation, cheap to overturn): one cooperative Operator Party + 10–14 member parties spanning both anchors — 6–8 Crispiano-area recovery members (Article 6 cohort positions incl. at least one in 3355–3758, mandates, one Pursuit chain to capacity/dispatch) + 4–6 Bari-belt members carrying duty exposure (one inside a 400 m ring, one adjacent to the Bitonto AD, one Valenzano). Holdings/standing/mandates per D5: notional only where real data underivable, identifier hygiene, no admission-profile claims |

## Recon corpus as product input

The three recon reports (`recon/fronts-and-monitoring.md`, `recon/programme-instrument-universe.md`, `recon/duties-proceedings-outcome-acts.md`) are current-state addenda to the D0 mapping ledger, not demo artifacts. They update D0's source records with live-verified endpoints, act chains, hashes and dated absences; the data-spine build (Prompts 04–05) consumes them as source-of-record for extraction manifests and assurance rows across the FULL source universe. Demo geography clips select from this corpus; they never bound it.

## Per-event full bindings

The event table above is the binding. Extraction lanes pull exactly what it names for the demo trajectories, plus the full-universe layers the product population requires per D0 (all 14 fronts' zone geometry, complete monitoring feeds, complete Article 6 + SRD01.01A/B + assurance-relevant act chains).

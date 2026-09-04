# ESA Third Party Missions — WorldView-3 SWIR request (draft, unsent)

Status: draft. Unsent. Free S2 (A0, A1, A2, A7) is a closed negative. The ask is crown-scale SWIR, not another 10–20 m index.

## One-line ask

Archive and/or tasking of WorldView-3 SWIR (8 bands, ~3.7 m GSD) plus VNIR over a set of georeferenced, laboratory-diagnosed olive trees in Brindisi province, Apulia, to test whether a crown-scale short-wave-infrared signature of *Xylella fastidiosa* infection exists that 20 m Sentinel-2 SWIR cannot resolve.

## Why this is a credible request now, not a fishing trip

We hold a matched observational cohort built from Regione Puglia official monitoring: 1,679 one-to-one positive/negative olive pairs in the 2021 Crecco footprint, matched on comune, sample date (±30 d), cultivar where known, and separation ≥60 m. On this cohort, public Sentinel-2 was tested rigorously and returned a **clean negative** at the individual-tree level:

- Paired ΔNDMI (positive − negative) at lags −365…+90 days: median −0.006 to −0.012 near diagnosis, 1 km cluster sign-flip p ≥ 0.13, null in every subgroup (Ostuni-out, cultivar-locked, symptom-absent, dry/wet scene halves).

The physical reason is explicit: a 20 m SWIR pixel is 400 m². An infected olive crown occupies a fraction of it; any within-crown hydraulic change is diluted below detectability. Zarco-Tejada et al. (2018, 2021) recovered previsual *Xylella* detection using crown-scale airborne hyperspectral + thermal, using traits Sentinel-2 does not measure. WorldView-3 is the only readily-tasked satellite carrying true SWIR (not super-resolution) at crown-approaching scale.

The scientific question we bring is precise and falsifiable:

> Does a crown-scale SWIR trajectory, matched for cultivar, neighborhood, date, and drought, contain a pathogen-associated signal that the 20 m measurement destroys?

A "no" bounds the physics. A "yes" is a new detection result on an official diagnostic cohort.

## What we provide

- Tree-level diagnostic labels (official Regione Puglia campaign records, 2013–2025).
- The matched case-control cohort and its construction code.
- The negative-control Sentinel-2 result as published rationale.
- All processing computational; no plant or insect material handled.

## What we request

- WV-3 SWIR + VNIR, archive over 2019–2021 Brindisi (overlapping the Crecco 25 km² and our positive/negative trees), and/or one tasking window over the current northern front.
- Minimal footprint: the diagnosed-tree extents, not wide-area mosaics.

## Eligibility note

ESA TPM restrained Project Proposals are open to R&D entities, not only EU universities. Confirm current eligibility and the proposal template before submission. PI: Owen Wassmer.

## Do not

- Do not submit before the A2 crown-fraction result exists.
- Do not request more scenes than the cohort needs.
- Do not imply any field or wet-lab capability we do not have.

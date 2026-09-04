# Validation geography

The official clipboard moved north with the front. A later campaign is not a retest of the same groves.

## What the labels are

2016–2021: dense olive testing inside the Crecco Brindisi box (30,766 olives, 2,523 diagnostic-positive). 2021 alone: 1,683 olive positives in that box.

2022–2025: **zero** official olives in that box. Those years test Fasano–Monopoli–Polignano, then Crispiano–Massafra, then Cagnano Varano (Foggia). 2024 mixes *pauca* olives with multiplex and *fastidiosa* on other hosts.

## What you may not do

- Train on 2018–2021 Brindisi and call 2022–2025 the same exam. That is a **transfer** test: new comuni, new sampling design, thinner olive-positive counts, and in 2024 a different subspecies mix.
- Random-split neighboring trees in the same box into train/test. Adjacent trees share irrigation, soil, and the same 20 m SWIR pixel.
- Treat 2022–23 olive-positive collapse as a clean “epidemic ended” hold-out. The clipboard also left.

## What you may do

1. **Spatial CV inside 2020–21 (or 2018–21) in the box.** Hold out whole comuni. This is the primary Experiment 1 oracle.
2. **Same-comune later year** only where that comune was still sampled. After 2021, not in this box.
3. **Northward transfer** as a named second test: train in the box, score 2022+ olive-*pauca* on the Bari coast / Gargano. Report it as transfer, not as replication.
4. **2024–25 non-olive positives** are a different product. Do not pool them into the olive lag test.

## Implication for a model

A model that “works” on 2021 Ostuni–Crecco and fails in 2022 Monopoli is not necessarily a bad 2021 detector. It failed transfer. A model that works on both has a claim on the moving front. Those are two different sentences. Experiment 1 answers the first. The second is later.

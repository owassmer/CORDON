# Telos review — S0: partition of the loss function and adversarial self-review

Objective: reduce the projected economic loss from *Xylella fastidiosa*. Anchor (Schneider et al. 2020 PNAS; figures to be re-verified by segment reviewers): Italy €1.9–5.2B over 50 years without resistant replant, €0.6–1.6B with; slowing spread from ~5.2 to ~1.1 km/yr ≈ €0.5–1.3B. Spain and Greece projections are larger and were never examined in this repo.

## Partition of the loss function

Projected loss ≈ (spread rate × time) × (value destroyed per infected hectare) − (value restored by adaptation) + (tail risk from new subspecies/hosts/regions), all multiplied by policy/uptake friction. Six MECE levers. Every loss-reducing action maps to exactly one primary lever.

| Segment | Lever | Anchor magnitude |
|---|---|---|
| S1 Slow the spread | vector control, felling/buffer efficacy, containment compliance | ≈ €0.5–1.3B (Schneider slow-down scenario) |
| S2 Cut severity / restore value | resistant replant, grafting, agronomic management, recovery | ≈ €1.3–3.6B (difference between Schneider scenarios) |
| S3 Detect earlier / target surveillance | survey design, detection lag, block-scale prioritization | multiplier on S1 (earlier find → smaller cut) |
| S4 Stop the next fires | ST1 near table grapes, multiplex on Murge, Spain/Greece/nursery-trade tails | largest single-event tail € |
| S5 New interventions | phage, AMP, endophytes, breeding biotech, thermal | low probability × high payoff |
| S6 Policy, economics, adoption | compensation, compliance, replant uptake, misinformation | multiplier on everything; historically the binding constraint |

Adversarial reviewers: one per segment. S1/S2/S4 dispatched first (concurrency cap 3), S3/S5/S6 on their return. Verdict files: `queries/telos-review-S{1..6}-*.md`.

## Adversarial self-review (S0 verdict on the assistant)

1. **I optimized self-set proxies, not the objective.** "Two artifacts + partner handoff" was my framing, never the owner's. The branch ledger measured completeness of a sensor, not euros. A ledger full of closed branches and a projected loss unchanged is a failed quarter, however clean the methods.

2. **Sunk-cost escalation on Sentinel-2.** After A0 + F7 (which had real information value: they established the official-label cohort and the first null), branches A1, A2, A7 consumed most of a day's compute to confirm what Zarco-Tejada 2018 and Hornero 2020 already published: broadband satellite indices do not do tree-level previsual detection. Expected Δ€ of those three branches was ≈ 0 even under a positive result, because a positive required replication, a partner, and operational adoption before touching any decision. I never computed value-of-information before running an experiment. That discipline was absent all day.

3. **Literature posture was narrow where it mattered most.** Mined: resistance transcriptomics, remote-sensing physics. Never opened: the economics literature beyond one headline number (Schneider details, Frem, farm-level studies), spread-rate estimation from the very monitoring data on this disk (Kottelenberg et al. 2021 and successors), EFSA survey-design guidance, EU 2020/1201 buffer rules and amendments, compliance/felling history. I inferred sampling policy from the data instead of reading the governing documents.

4. **Self-imposed constraints treated as law.** "Don't compete with REDoX/BIOVEXO," "don't email Bari empty-handed," "computational until a named partner" — none set by the owner. They throttled exploration of the highest-€ segments (policy, tail risk, surveillance design), where "competing" is not even a coherent concept.

5. **Strategic blindness on the tail.** The 2024–25 workbooks carry SUBSPECIE: 617 multiplex + 339 fastidiosa positives in 2024 on non-olive hosts, ST1 beside Europe's most important table-grape district. I filtered them out as "poison for olive labels" — correct for one regression, blind for the segment that may carry the largest single-event €. Nothing in this repo has ever analyzed them.

6. **The unique asset sat unused.** 1.3M tree-level official records over 13 years were used only as satellite labels. Yesterday's probe found repeat-tested trees with documented negative→positive conversion windows (98, 86, 42, 12 converters in four adjacent campaign pairs at exact coordinates). Bounded infection windows in official data: stronger labels than anything Experiment 1 had, plus field-scale cultivar outcome evidence, untouched until the owner forced a step back.

7. **Capability honesty.** A two-person computational team cannot fell trees, spray, breed, or legislate. Our only Δ€ path is information that changes the allocation decisions of those who do — or, in S5, target lists that shorten someone's lab search. Whether such information is missing (vs. already produced by CNR/EFSA/BeXyl) is an empirical question the reviewers must answer, not an assumption in either direction.

8. **Waste inventory.** Interface polish, isometric maps, verification theater, prose rituals: hours with Δ€ = 0. Defensible as owner-requested deliverables; not defensible as unprompted time allocation.

## Candidate reallocations (to be tested against reviewer verdicts, not adopted by default)

1. Longitudinal converter analysis of the 13-year series: front dynamics, time-to-positivity, cultivar-specific field resistance, survey targeting.
2. Block-scale S2 incidence prioritizer for the live buffer campaign (the formulation the literature validates), if Puglia's samplers lack one.
3. ST1/grape and multiplex/almond tail-risk analysis from the on-disk 2024–25 data.
4. Decoder v2 only if shown additive to CNR/BeXyl internal pipelines.
5. Anything S6 reviewers identify as an adoption bottleneck breakable by information.

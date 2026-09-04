# Facet 1 — Aperture, population and exclusion grounds

Read `reviews/REVIEWER_BRIEF_TEMPLATE.md` in full first. Sections 0–4 and 6–7 of that file bind you verbatim. This file
fills the slots.

- **Facet:** `F1-APERTURE` — Does the Stage B ledger cover every decision the law vests in the Osservatorio for territory
  inside its jurisdiction, and does every exclusion rest on one of the three permitted grounds?
- **Sample rule:** exhaustive on exclusion grounds (read every distinct `why` in `dispositions`); exhaustive on the
  uncovered set (every Stage A row carrying a temporal or numeric expression that is absent from
  `regulation/stage-b/population.json`); for present rows, sample at least one per seam per clock `kind`.
- **In scope:**
  - `regulation/stage-b/clocks-and-parameters.json` (canonical), `regulation/stage-b/population.json`
  - `regulation/stage-a/authoring-eu.json`, `regulation/jurisdiction/canonical/authoring.json`
  - `regulation/jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json` (rulings and the corrected reachability rule)
- **Seam 4 is now IN SCOPE** (opened and authored 2026-09-03): prescription → notice → election → execution →
  enforcement, 37 clocks over a 161-row population located by complement of seams 1–3.
- **Explicitly out of scope:** Stage C/D/E/F/G surfaces do not exist yet — in particular, whether the instrument can
  *supply* an anchor's date from any dataset is a Stage C/D question and not a defect in a Stage B row. Aid, indemnity
  and Articles 19–26 movement are outside the program aperture by standing ruling.
- **Binding rulings (do not relitigate):**
  - Corrected reachability (authority snapshot, `implemented_aperture.reachability_rule`): a vested Osservatorio decision
    plus a holdable fact; the decision need not have occurred; only *vested elsewhere*, *fact not holdable*, *producer
    interval closed* may exclude.
  - Q8 as amended: the PNI 2026 per-stratum design values are IN as `design_target`; RiPEST model internals are OUT.
  - Q2/Q3/Q6: national-actor duties (Commission, MASAF, CFN) and laboratory-internal turnaround are out on the
    vested-decision ground; one clock per independently variable fact; nothing averaged across versions.

**The questions to answer, in this order:**

1. Does any `dispositions[].why` still rest, in substance, on the absence of a held instance — including phrasings a regex
   would not catch ("not exercised in practice", "never applied", "no act in the corpus", "only relevant historically")?
   Quote each.
2. Take the Osservatorio's decision chain as a whole. Name any decision the law vests in it for which the ledger holds no
   clock or parameter, where the law states a period, a threshold, a geometry or an ordering. Check the pre-M5 and post-M5
   versions separately, and the containment branch as well as eradication.
3. Are the three permitted exclusion grounds applied honestly — in particular, is any row excluded as "producer interval
   closed" whose producer is in fact still current, or as "vested elsewhere" where the Osservatorio in fact decides?
4. Is any row present that should not be — a clock or parameter no vested Osservatorio decision consumes, or one whose
   resolving fact cannot be held without fabrication?

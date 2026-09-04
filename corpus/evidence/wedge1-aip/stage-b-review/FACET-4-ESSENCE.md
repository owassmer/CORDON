# Facet 4 — Essence, anti-bloat and over-provenance (adversarial)

Read `reviews/REVIEWER_BRIEF_TEMPLATE.md` in full first. Sections 0–4 and 6–7 of that file bind you verbatim. This file
fills the slots and adds one thing the other facets do not have: **you argue for deletion.**

- **Facet:** `F4-ESSENCE` — Does the ledger carry anything it does not need: a row that duplicates a fact another row
  already owns, a field no downstream stage consumes, a note that is not a source-stated interaction or a genuine open
  term, a schema addition an existing field could have carried, a proof-of-evidence predicate standing where the law
  vests a decision outright, or a process artifact that has become work of its own?
- **Sample rule:** exhaustive on clocks, parameters, notes, conventions keys, and clock/parameter field usage; exhaustive
  on the disposition log's shape (not its legal grounds — those are F1's); read `scripts/verify_stage_b.py` and
  `scripts/generate_stage_b.py` in full; read `regulation/jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json` key
  `stage_b_execution` in full.
- **In scope:**
  - `regulation/stage-b/clocks-and-parameters.json`, `regulation/stage-b/generated/*`, `regulation/stage-b/population.json`
  - `scripts/verify_stage_b.py`, `scripts/generate_stage_b.py` (read them; never run the writers)
  - `regulation/jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json` — `stage_b_execution` and the grill rulings
  - `reviews/` — the briefs and returns, as artifacts that themselves cost something
  - `regulation/stage-a/authoring-eu.json` and `regulation/jurisdiction/canonical/authoring.json` as the ground of any
    fidelity claim
- **Seam 4 is now IN SCOPE** (authored 2026-09-03), and it is the largest single addition the ledger has taken: 37
  clocks, five plan versions of one procedure. Test it hardest for duplicate facts across versions.
- **Explicitly out of scope:** Stage A's own field schema and its own reading (both closed); whether a *missing* thing
  should be added — that is F1's facet, and an assertion from you that something is missing is out of contract.
  **Stage boundary, binding:** B states the law; Stage C derives the computation and names the inputs it needs; Stage D
  sources them. Do not argue a row is unnecessary because no dataset supplies its anchor — that is a C/D fact and, like
  rarity, it is not a ground here.

## The deletion test — the only standard you may assert on

For every candidate, name three things, or drop the assertion:

1. **The thing.** The exact row id, field name, note text, convention key, verifier check or file.
2. **Its consumer.** Which downstream stage reads it, and to do what. C computes deadlines, windows and geometry from
   `anchor`, `kind`, `magnitude`, `bound`, `unit`, `relation`, `window`, `applies_when`. D binds anchors to data sources
   by kind and by named object, medium and place. E derives Action preconditions from `completion` and consequences from
   `consequence_on_expiry`. F/G carry clocks as properties. Owen reads the notes and the authority.
3. **What breaks on deletion.** If nothing breaks, assert removal. If something breaks, you have answered your own
   question and there is no assertion.

An assertion that a thing is *inelegant*, *verbose*, *redundant-looking* or *could be simpler*, without naming the
consumer and the breakage, is not admissible. Aesthetics are not evidence.

## The guard — you may not re-import the retrospective aperture

The most likely way this facet does damage is by arguing that a row is unnecessary because the situation it governs has
not arisen. That is the exact failure the program corrected on 2026-09-02, and the correction binds you:

> A clock or parameter is decision-reachable when the law vests the decision in the Osservatorio for territory inside its
> jurisdiction and the resolving fact is holdable without fabrication. **Whether that decision has yet occurred is
> irrelevant.** Only three grounds may exclude: vested elsewhere, fact not holdable, producer interval closed.

So the Article 15(3) island threshold, the Article 42 temporary-designation limits, the Article 39 audit and withdrawal
clocks, the unexercised reduction and lifting routes, and every pre-M5/post-M5 version pair are **in**, however quiet the
corresponding files are. An assertion resting on "no Puglian instance", "not exercised in practice", "historically
irrelevant" or "the epidemic has not reached there" is itself a finding against you and will be rejected on its own
terms. Duplication, non-consumption and over-provenance are your grounds. Rarity is not.

## The questions, in this order

1. **Duplicate facts.** Does any row carry a fact another row already owns — a figure restated from a Union floor a
   parameter already holds, two clocks expressing one independently variable relation, a parameter whose value is derived
   from another rather than stated by its own quote? Q3 grain is one row per independently variable fact; test both
   directions, over-splitting as well as over-merging.
2. **Dead fields.** For each of the 20 clock fields and 13 parameter fields, is it populated where it means nothing,
   always null, or never read by any named consumer? Name any field that could be dropped without a consumer losing an
   input.
3. **Over-provenance.** Does any `anchor`, `applies_when`, `completion` or `consequence_on_expiry` make the *proof* or
   the *record* of a fact an antecedent of a decision the law vests outright? Does any surface carry hashes, paths,
   source spans, ASTs or provenance that Stage A or the generated status already owns?
4. **Notes.** The convention allows a note only for a source-stated interaction with another clock or a genuine open
   term. Quote every note carrying something else — rationale, history, a ruling, a normalization narrative, a stage
   allocation — and say which convention it violates.
5. **Schema inflation.** Two additions went through the grill: `bound` (Q11, ratified) and `resettable_period` (Q12,
   proposed, shape `{scope, start_event, reset_event, basis}`), alongside `applies_when`, `window`, `relation` and
   `executor`. For each, could an existing field have carried the fact without leaving law in prose? Say which you would
   remove and what then becomes unexpressible. A field that exists for one row and is null on 71 is a specific charge —
   make it or clear it.
6. **Verifier and generator weight.** Which checks duplicate each other, enforce something no convention states, or
   restate in code what the conventions block already states in prose? Which conventions keys are dead letters that no
   check and no consumer relies on? Do not propose that code decide meaning; propose only removals.
7. **Disposition-log economics.** 586 dispositions for 362 population rows. State what the log is for, who reads it, and
   whether expression grain earns its cost against row grain — including whether any merged sentence-grain window
   swallows two independently variable expressions into one entry.
8. **Method fixation.** The program's own record warns that a method built to prevent semantic error can become a
   substitute for progress. Judge the process artifacts as artifacts: the reviewer briefs, the returns, the authority's
   `stage_b_execution` narrative. Is any of it accumulating faster than it is consumed, restating what another file owns,
   or preserving construction history the sole-authority rule says is not product?

## Additional classes for this facet

Use these in the `class` field alongside the template's twelve: `duplicate_fact`, `dead_field`, `note_bloat`,
`schema_inflation`, `check_redundancy`, `method_fixation`.

**PASS criteria:** no `blocking` or `material` assertion survives your own falsifier test. A PASS here means the ledger
carries what it needs and nothing more — say so with a populated `checked_sound` naming what you tested for and did not
find.

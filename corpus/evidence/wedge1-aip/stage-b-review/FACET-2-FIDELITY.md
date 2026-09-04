# Facet 2 — Legal fidelity of clocks and parameters to their source spans

Read `reviews/REVIEWER_BRIEF_TEMPLATE.md` in full first. Sections 0–4 and 6–7 of that file bind you verbatim. This file
fills the slots.

- **Facet:** `F2-FIDELITY` — Does every clock and parameter say what its Stage A `source_quote` says, no more and no less,
  and does its anchor denote the operator's real moment?
- **Sample rule:** exhaustive on all clocks (there are fewer than 70); exhaustive on parameters whose `kind` is `floor`,
  `ceiling` or `threshold`; for `design_target` parameters, check every distinct confidence/prevalence pair against its
  quote.
- **In scope:**
  - `regulation/stage-b/clocks-and-parameters.json`
  - `regulation/stage-a/authoring-eu.json`, `regulation/jurisdiction/canonical/authoring.json` (the quotes are the ground)
  - `regulation/jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json` for the standing rulings only
- **Seam 4 is now IN SCOPE** (authored 2026-09-03): the five plan versions' notice chain, the Article 33(2) access
  ordering, and the Law 689 enforcement chain.
- **Explicitly out of scope:** whether Stage A's own reading of a provision is correct (Stage A is closed under standing
  reading authority; if you believe A misreads a source, file it as `unresolved`, not as an assertion). Anything
  requiring a source not in the repo. Whether any dataset can supply an anchor's date — that is Stage C/D.
- **Binding rulings (do not relitigate):** Article 1 vocabulary; the statutory 15 working days controls over the 2026
  plan's unqualified "15 giorni"; national bands above a Union minimum apply as adopted;
  "immediately / senza indugio / tempestivamente" stay indefinite promptness standards with no number invented. The
  silence-route rule was NARROWED 2026-09-03 and is itself open for challenge: a silence route may carry the period its
  source states, but only from an anchor naming evidenced non-response. Whether that narrowing is right, and whether the
  resulting anchors honour it, is a live question for this facet.

**The questions to answer, in this order:**

1. **Anchor denotation.** For each clock, does the `anchor` denote the moment the source ties the duty to? Test especially:
   per-plant duties anchored on an area-level state; conditions of a discretion anchored on the discretion's own result;
   notifications anchored on something other than the act they report; lookbacks anchored forward.
2. **Object, medium, place.** Every `legal_state` anchor must name what was confirmed or established (object), in what
   (plant / vector / null where the state has no medium), and where. Flag any anchor whose object or place is vaguer than
   the quote, or wider or narrower than it.
3. **Kind and bound.** Does `kind` match the legal relation the words create — `deadline` vs `not_before` vs
   `eligibility_threshold` vs `minimum_duration` vs `lookback_window` vs `ordering_constraint` vs `promptness_standard`?
   Is `bound` `floor` wherever the source says "at least", "almeno", "no less than", "dopo"? Is any threshold that merely
   *opens a discretion* mis-typed as a deadline that *compels* an act?
4. **Magnitude, unit, comparator.** Does the number match the quote; is the unit the one the source states (working days
   vs calendar days vs months vs hours); is any comparator inverted or inclusive/exclusive wrong?
5. **Consequence and completion.** Does `consequence_on_expiry` name an effect the law actually attaches, and does
   `completion` name the act that ends the duty — not a downstream or upstream event?
6. **Version fidelity.** Where a provision has versions, does each clock carry its own version's magnitude and interval,
   with nothing back-projected or averaged, and are `semantic_change = NO` folds genuinely non-semantic?
7. **Vocabulary.** Any defined term used where the producer quote does not use it; any definiens annotation; any
   substitution of `host plants` for `specified plants` or vice versa.

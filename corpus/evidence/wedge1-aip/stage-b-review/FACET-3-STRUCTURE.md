# Facet 3 — Schema discipline, stage boundary and closure honesty

Read `reviews/REVIEWER_BRIEF_TEMPLATE.md` in full first. Sections 0–4 and 6–7 of that file bind you verbatim. This file
fills the slots.

- **Facet:** `F3-STRUCTURE` — Can Stage C compute on these fields without re-reading law; does Stage B stay inside its own
  stage; and does every completion claim on disk match what the artifacts actually support?
- **Sample rule:** exhaustive on field shapes (every clock and parameter); exhaustive on the closure manifest and the
  generation status; for dispositions, exhaustive on distinct `disposition` classes and a sample of 20 rows.
- **In scope:**
  - `regulation/stage-b/clocks-and-parameters.json`, `regulation/stage-b/generated/*`
  - `scripts/verify_stage_b.py`, `scripts/generate_stage_b.py` (read them; do not run writers)
  - `regulation/jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json` (`stage_b_execution`, `schema_v3_2026_09_02`, seat rule)
- **Seam 4 is now IN SCOPE** (authored 2026-09-03).
- **Explicitly out of scope:** Stage A field schema (accepted); the choice of schema v3's field names as such —
  review whether each field has **one meaning and one shape**, not whether you would have named it differently.
  **Stage boundary, binding:** B states what the law requires. Stage C derives the computation and, in doing so, names
  the inputs it needs; Stage D then sources those inputs. So "can any dataset supply this anchor's date" is a C/D
  question and a B row that does not answer it is not defective. Do not propose a field that classifies anchors by data
  availability — that would make B a second owner of a fact C owns.
- **Binding rulings (do not relitigate):** essence-only posture (B carries no hashes, source paths, provenance, ASTs,
  evaluators or evidence bindings — A or C/D own those); the seat rule (the Member State concerned acts in Puglia through
  the Osservatorio, recorded once in the authority, never per row); notes carry only a source-stated interaction or a
  genuine open term.

**The questions to answer, in this order:**

1. **One meaning per field.** Does any field carry two kinds of fact across rows (an id in one row and a token in another;
   a number in one and a phrase in another; a scope key present here and absent there)? Enumerate every distinct shape a
   field takes and say which are legitimate variants of a declared union and which are drift.
2. **Computability.** Take three clocks and one parameter and write, in one sentence each, exactly what Stage C would have
   to do to produce a date or a distance from the row alone. Where it would have to read prose to know, that is a finding.
3. **Stage leakage.** Does B decide anything A owns (legal meaning, populations, conflicts), or anything C/D/E own
   (calendars, holiday tables, arithmetic, evidence contracts, Action preconditions)? Does any note or field smuggle one in?
4. **Verifier honesty.** Read `scripts/verify_stage_b.py`. Which invariants does it actually enforce, and — more useful —
   which of the failure classes in §2 of the template could pass it silently? Name at least the three most dangerous gaps.
   Do not propose that code decide meaning; propose where a human reread is the only possible gate.
5. **Closure honesty.** Does `closure_manifest` and `generated/generation-status.json` claim anything the artifacts do not
   support? Specifically: is `semantic_acceptance` asserted anywhere without a recorded acceptance act; does any status
   string, seam entry or authority sentence describe work as closed, verified or accepted beyond what is on disk?
6. **Determinism.** From reading the generator, is the projection a pure function of the canonical, or does it carry state
   that could make two runs differ?

# Stage A — legal decision specification

Status: **supporting schema reference — no current-authority effect**
Authority: `../jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json` (Stage A closed 2026-09-01 under standing reading authority).

Stage A represents the operative legal specification. It does not design the
Ontology, Actions, Functions, math or data-source implementation.

## Authoritative outputs

| Artifact | Grain | Purpose |
|---|---|---|
| `authoring-eu.json` | one proposition version, 35-field essence schema | the EU canonical; the CSVs below are projections of it |
| `stable-provisions.csv` | one stable legal atom | identity and hierarchy across amendments |
| `provision-versions.csv` | one exact text/status interval | point-in-time semantics and source evidence |
| `dependency-manifest.csv` | one external/later dependency | implemented stub, indexed deferral or superseded source |
| `annex-versions.csv` | one exact Annex I–V interval | time-dependent taxon, geography, diagnostic and reporting state |
| `MULTILINGUAL_AUDIT.md` | one corpus-wide comparative review | authentic-language clarification and retained conflicts |

Per-version condition ASTs live in `authoring-eu.json`. The former current-only
`condition-graph.json`, the `decision-map.csv`/`inventory.csv` authoring inputs
and their compilers were retired by the 2026-09-01 reading census.

## Stable provision fields

| Field | Meaning |
|---|---|
| `instrument_id` | stable instrument identity |
| `stable_provision_id` | atom identity that survives amendment |
| `parent_stable_provision_id` | legal hierarchy, not physical PDF placement |
| `article` | article number |
| `structural_kind` | stem, paragraph, point, subparagraph |
| `scope_status` | implemented/dependency/deferred status |

## Provision-version fields

### Identity and time

- `provision_version_id`;
- `instrument_id`;
- `stable_provision_id`;
- `effective_from`;
- `effective_to_exclusive`;
- `source_uri`;
- `source_snapshot_hashes`;
- `source_snapshot_dates`;
- `verbatim_text`;
- `exact_change_kind`;
- `semantic_change`.

A version is created when exact operative text/status changes. Formatting-only
changes remain exact versions with `semantic_change=NO`. Adjacent identical text
collapses. Every stable provision resolves exactly one current version.

### Legal semantics

- `actor_role`;
- `modality` — verbatim `shall`, `may`, `shall not` or structural `-`;
- `true_effect`;
- `false_effect`;
- `reserved_decision_owner`;
- `evidence_contract`;
- `external_dependencies` — the complete declared cross-proposition dependency set.

The jurisdictional canonical schema carries exactly these fields. The accepted
EU CSVs additionally retain `trigger_expression`, `conditions`, `conjunction`,
`required_legal_effect`, `verbatim_text`, `scope_status` and the five-axis
columns from their original accepted shape; unifying the two shapes is a
registered grill question. No Stage A surface carries `clock_rule`,
`numeric_parameters` or a dependency `clock` column: clock and parameter
derivation belongs entirely to Stage B, which reads the retained source wording.

Stage A stores effects and reserved authority. It contains no Foundry Action
template or write design.

Jurisdictional authoring may classify an authority-bearing subset as
`higher_authority_dependencies`. That subset remains present in
`external_dependencies`, which alone owns dependency existence. The classifier
adds legal role; it does not create a second dependency.

Stage A does not extract clocks or parameters. Complete source wording and legal
effects remain available for Stage B. Stage B owns every clock and parameter
definition, anchor, normalization and interaction.

### Condition AST contract

`condition_ast` is the structured legal representation of a proposition's
trigger, conditions, alternatives, exceptions and unresolved outcomes. It does
not define a software evaluator. In the jurisdictional canonical schema the AST
is the sole owner of activation and condition structure; no prose trigger,
condition or conjunction field exists beside it.

Allowed nodes are:

```text
predicate · all_of · any_of · not · provision_ref · result_ref · route_table · otherwise
```

`predicate` names a legal or source condition. Stage C defines its executable
evaluator; Stage D binds the evidence. `provision_ref` incorporates another
legal proposition. `result_ref` consumes one exact legal effect emitted by
another proposition at the event-time version:

```json
{
  "result_ref": {
    "producer_stable_provision_id": "PUG-LR4-2017:Art.6(1)",
    "allowed_effect": "CONTAINMENT_SUBSTITUTES_FOR_ERADICATION"
  }
}
```

`result_ref` replaces prose predicates that restate a parent outcome. The old
prose representation is deleted in the same change; no parallel result model is
maintained. The producer remains an explicit dependency.

Every trigger-dependent AST preserves the legally distinct applicable,
inapplicable and unresolved branches without defining their runtime tests.
Route-table branches are mutually exclusive and exhaustive for the legal states.
Route order is not legal precedence. `otherwise` preserves unresolved legal
meaning; it does not implement evidence missingness.

### Five axes that replace `computable`

| Axis | Question |
|---|---|
| `rule_determinacy` | Does the legal text define a deterministic rule, or require judgment/evidence/policy? |
| `calculation_support` | Is this parameter/date/logic support, rather than a source-availability claim? |
| `public_observability` | Can public evidence establish it? Deferred to Stage D. |
| `government_availability` | Is the controlled authority fact actually held? Deferred to Stage D. |
| `authority_judgment_required` | Must an authorized actor exercise discretion or resolve an open term? |

`authority_judgment_kind` identifies the proposition without preselecting an
`AuthorityPolicy` object. `legal_linguistic_conflict` retains authentic-language
divergence. `semantic_note` carries bounded interpretation, never an Action or
source-system assumption.

## Accepted interpretive rules

- Article 3(1)'s final subparagraph governs the whole contingency plan.
- Article 5(1)(a) requires separate immediate sampling and removal evidence.
- Article 6(4)'s special-notification route anchors to initial establishment for
  the Puglia compiler; EN/ES divergence is retained.
- Article 7(1)(e)'s two-year evidence stays at the referenced plant/cohort grain.
- Articles 8(1) and 14(2) compile mandatory treatment-class inclusion for Puglia;
  Spanish modality divergence is retained.
- Article 9(1)'s alternative location is measured from the designated nearby
  destruction location.
- Article 11(1) cumulatively retains ISPM 9 and ISPM 14.
- Article 13(1) compiles the literal Article 15(2) discovery route. Specific
  orders/other legal bases govern their own cases; otherwise an unbridged
  discovery basis requires authority interpretation.
- Article 15(2)'s final subparagraph applies to points (a) and (b), and point (a)
  is an inward infected-zone band.
- Regulation 2020/1201 Article 18 planting/grafting authorization is indexed and
  deferred. It does not mint implemented Stage A propositions.

## Dependency aperture

Articles 1–17 and reached Annexes I–IV are implemented fully. Article 18 is
indexed and deferred with later transaction families. Direct current dependencies
receive semantic stubs:

- Regulation 2016/2031 Arts. 10–19, 22, 25, 27 and 103;
- Regulation 2020/1201 Art. 32 and Arts. 35(1), 35(4);
- Regulation 2019/1702 priority-pest status;
- Annex V reporting schema.

Articles 19–31, 33–34 and 36–38 are indexed but do not mint movement, passport,
consignment, import or check transactions. Implementing Decision 2015/789 is
historical/superseded and retained only where a historical plan refers to it.

## Verification

```text
python3 scripts/verify_stage_a.py --mutation-test
```

The mutation gate must fail on mis-parentage, wrong temporal anchor, taxon-level
collapse, lost spatial referent, lost ISPM constraint, flattened Article 13,
missing dependency status or hidden multilingual conflict.

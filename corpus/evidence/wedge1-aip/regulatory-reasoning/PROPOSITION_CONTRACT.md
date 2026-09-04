# Reauthored Stage A proposition contract

Status: **supporting method reference — no current-authority effect**

Current authority: `../STAGE_A_AUTHORITY_SNAPSHOT.json`.

## Authority

The accepted EU Stage A schema remains the semantic contract. Jurisdictional authoring must preserve the same field purposes. Matching column names without matching meaning is not compatibility.

Legal meaning comes from:

1. the accepted EU corpus;
2. the semantic readings (`../semantic-readings/EU.md`, `NATIONAL.md`, `REGIONAL.md`) and `ADJUDICATION.md`;
3. the authenticated source bodies registered in `source-metadata.csv`.

## Grain

A proposition contains one independently variable legal meaning.

Split only when actor, reserved decision owner, modality, trigger, condition branch, legal effect, exception, evidence requirement, notice, clock, geography, subject population or temporal interval can change independently.

Keep source-native tuples and tables together when their meaning depends on the complete tuple.

Do not create separate product states for every assurance note, provenance fact, caveat, unknown source, publication channel or implementation detail.

## Identity and relationships

- `stable_provision_id` identifies one source-specific proposition.
- `parent_stable_provision_id` identifies same-instrument legal structure only.
- `provision_ref` in an AST identifies an executable proposition dependency.
- `result_ref` consumes one exact effect from another proposition. It replaces parent-result prose and names the producer stable ID plus allowed effect.
- `external_dependencies` owns the complete declared cross-proposition dependency set.
- `higher_authority_dependencies` classifies the authority-bearing subset that authorizes, constrains, limits or determines legal availability.
- `semantic_equivalence_key` links proven equivalent meaning across sources. It never replaces source-specific identity or legal effect.

`higher_authority_dependencies` is always a subset of `external_dependencies`.
An external-only dependency supplies incorporated support without supplying
higher legal authority. AST references are orthogonal: a dependency can also be
a `provision_ref` or `result_ref` producer without changing its declared role.

Synthetic families and the previously asserted four top-level decision families are not legal sources, parents or completeness boundaries.

## Authoring fields

The authoring row contains:

- accepted stable-provision fields;
- accepted provision-version fields;
- `source_clause_id`;
- `condition_ast`;
- `higher_authority_dependencies`;
- `semantic_equivalence_key`.

The generator emits the accepted Stage A tables and a separate semantic-equivalence map.

## AST

Use only:

```text
predicate
all_of
any_of
not
provision_ref
result_ref
route_table
otherwise
```

`condition_ast` is the structured legal logic. It includes source-native trigger
and condition meaning without defining software evaluators. The AST is the sole
owner of activation and condition structure: the canonical schema carries no
prose trigger, condition or conjunction field beside it.

Every proposition with conditions has one complete AST. The AST preserves
applicable, inapplicable, exception and unresolved legal branches. Stage C owns
predicate evaluators. Stage D owns evidence binding and missingness behavior.

The canonical schema carries no clock or parameter fields. Stage B derives every
clock and parameter from the retained source wording and the accepted legal
branches.

A temporal magnitude may appear in effect prose or a predicate only where its
exact source-native statement is present in the row's own quote, or where the
magnitude is the proposition's identity (a unit-conflict or stricter-measure
delta). The quote is the single owner of every figure; prose is a faithful
reference, never a second source. Spatial magnitudes name legal populations and
geometry and are part of legal meaning.

`result_ref` has the shape accepted in `regulation/stage-a/SCHEMA.md`. The
producer is an explicit dependency and resolves by event time. A result-dependent
child deletes the prior prose predicate when `result_ref` is installed.

Route-table branches are mutually exclusive and exhaustive for material legal
states. Route order is not legal precedence. `otherwise` preserves unresolved
legal meaning and does not implement evidence evaluation.

Execution evidence is not an activation antecedent. A duty activates from its legal trigger; missing execution inputs create missing evidence for the active duty.

A structurally valid AST is not evidence of pure legal logic. Population review must reject any class where:

- a general duty activates only under its exception, alternative method, positive-result response, default, refusal or breach remedy;
- one source atom combines independently variable meanings and a later version corresponds to only one fragment;
- an effect, clock, notice, authority decision, completion record or evidence requirement appears as an antecedent;
- a conditional rule has no explicit false and unresolved outcome;
- a conclusion-restating predicate (`eligible`, `authorized`, `conditions satisfied`, `duty applies`) replaces the source facts that determine that conclusion;
- recurring source classes collapse into an AST monoculture without clause-by-clause derivation;
- a valid source quote and hash are used as a substitute for proving that the AST expresses the complete clause logic.

Temporal correspondence is established only after minimum pure legal atoms are derived on both sides. A compound historical atom may map one-to-many; it must never be paired to one successor fragment while its other continuing meanings are labelled introduced.

## Modalities

`modality` is exactly:

```text
shall
may
shall not
-
```

It is derived from the proposition, not from effect-kind strings or prefixes.

## Time

- Documentary snapshot dates remain documentary snapshot dates.
- Adoption, publication, effectiveness, application and revocation dates remain separate.
- Minimum values are floors unless the source makes them exact or maximal. A competent authority may adopt a stricter source-native value.
- A successor ends every legal effect it actually supersedes. It does not erase unaffected historical facts.

## Source dispositions

- `RULE` feeds proposition authoring.
- `UNRESOLVED` feeds an explicit authority/evidence-resolution branch.
- `SUPERSEDED` feeds a historical version when held events require it.
- `INSTANCE` remains outside the rule corpus and links to the applicable proposition.
- `DEFERRED` remains indexed and does not mint a proposition.

## Cases

Case acts resolve through:

```text
point-in-time reusable law
+ applicable authority and area versions
+ selected case branch
+ genuine case delta
+ evidence
```

Owner, parcel, plant, sample, coordinate and beneficiary payload stays outside the rule corpus.

## Current authority discipline

`STAGE_A_AUTHORITY_SNAPSHOT.json` declares the current authority inputs.
`canonical/generated/dependency-manifest.csv` is the projected cross-jurisdiction topology.

Stage A has one authoring path:

```text
source text
→ one bounded semantic reading per jurisdiction
→ Connor adjudication
→ one accepted schema
→ one canonical serialization
```

No parallel candidate, generator, validator or graph is an authority surface.

## Output

One generator emits:

- `stable-provisions.csv`;
- `provision-versions.csv`;
- `condition-graph.json`;
- `dependency-manifest.csv`;
- `semantic-equivalence.csv`;
- `case-proposition-map.csv`;
- `area-state-versions.csv`.

The interactive SVG is generated from these outputs only. Every instrument, provision and AST is reachable through ordinary legal structure. No manually selected scenarios are maintained.

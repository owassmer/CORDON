# Stage A — structural reference

This reference explains the condition structure used by the Stage A canonicals.
It does not own legal meaning, current status, acceptance or aperture. Read those
from [CURRENT](../../state/CURRENT.json) and the canonical owners it identifies:
[EU authoring](authoring-eu.json) and
[jurisdiction authoring](../jurisdiction/canonical/authoring.json).
The [stage contract](../../STAGE_BOUNDARIES.md) owns the A–G division of work.

Read actual fields from the canonicals and projections. Projection behavior is
defined by the [EU generator](../../scripts/generate_stage_a_eu_projections.py)
and [jurisdiction generator](../../scripts/generate_jurisdiction_step6.py).
The [EU verifier](../../scripts/verify_stage_a.py) and
[jurisdiction verifier](../../scripts/verify_jurisdiction_stage_a.py) check their
stated invariants; passing them is not semantic acceptance. This explanation
must remain consistent with those surfaces and cannot override them.

## Condition AST interpretation

`condition_ast` represents a proposition's trigger, conditions, alternatives,
exceptions and unresolved outcomes. It does not define a software evaluator.

`predicate` names a legal or source condition. `all_of`, `any_of` and `not`
express conjunction, alternatives and negation. Stage C defines executable
evaluation; Stage D binds evidence.

`provision_ref` incorporates another legal proposition. `result_ref` consumes
the named producer's exact legal effect at the applicable version, using
`producer_stable_provision_id` and `allowed_effect`. The producer remains an
explicit dependency; a prose restatement must not become a parallel owner of
its result.

`route_table` preserves legally distinct branches. Its branches must be mutually
exclusive and cover the applicable, inapplicable and unresolved legal states
without defining their runtime tests. Route order is not legal precedence.
`otherwise` preserves the stated residual legal outcome; it does not implement
evidence missingness.

## Dependency interpretation

`external_dependencies` owns the declared cross-proposition dependency set.
`higher_authority_dependencies` classifies its authority-bearing subset; it
adds a legal role without creating a second dependency. The canonical proposition
owns the particular dependency and its meaning.

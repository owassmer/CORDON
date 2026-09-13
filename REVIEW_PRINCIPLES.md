# Review principles

Review protects the objective and the operator's decision, not the artifact or the process. Reviewers assert; the adjudicator judges; Owen accepts. This document owns how a unit is planned, reviewed and judged converged. Stage substance belongs to `STAGE_BOUNDARIES.md`; the plan's shape belongs to `.github/PULL_REQUEST_TEMPLATE.md`.

## Three facets

The partition is by primary responsibility, not by evidence read. Assign each finding to its smallest material cause. Reviewers may follow evidence beyond their facet.

| Facet | Question | Distinct responsibility |
|---|---|---|
| 1. Purpose and proportion | Is this the right work, and no more than it? | The decision served and the aperture read from state; admission of sources, dependencies and other actors by their effect on the chosen chain; and the lean challenge: whether the full necessary meaning survives with less structure, scope, process or ceremony. |
| 2. Meaning and composition | Does it say what its authority says, and does the whole hold together? | Primary sources and accepted upstream meaning: conditions, quantities, actors, exceptions, time, and fact versus inference; coverage of the in-aperture universe; consistent shapes, names, units and contracts across owners and consumers; version seams. |
| 3. Realization | Does it actually do that for an ordinary record it has never seen, and would the evidence show if it did not? | Consumer-visible behavior; recomputation from source; boundaries and failure paths; generality without case registration or authored answers; whether a check can fail; destination reads. A green signal is not the result. Where the unit reads a source family, instances of that family read independently of the reader, in every round. |

Facet 1 decides what belongs and how much. Facet 2 checks meaning and coherence. Facet 3 checks the result and the evidence for it.

Where a unit reads a source family, a review that consults only the unit's output audits a transformation against itself, and a reading that is self-consistent and wrong survives it. Facet 3's reviewer therefore reads instances of the source directly — the page, the document, the record, not the unit's rendering of it — and judges the reading against what those instances state. Realization owns this because the question is whether the reader recovers what the source carries; facet 2 continues to own whether a recovered fact says what its authority says. The reviewer establishes those readings; a unit that supplies them supplies the authored answer this facet forbids, which binds the reader under review, never the review.

## Plan review, once

Every unit begins as a plan in its pull request body, written from the template. One independent reviewer reads the plan against `AGENTS.md`, `DESIGN_PRINCIPLES.md`, the applicable stage contract, this document, `state/CURRENT.json` and the owners the plan names, using the plan brief below. The brief is the same every time; alignment comes from the constitution, not from per-unit steering.

One cycle: findings are adjudicated, the plan is revised in place, and the revision is recorded under "Changes since plan review". A second dispatch is warranted only if the decision served or the unit boundary changed. A plan that changes no meaning — repository mechanics, a projection, a wording repair — may propose plan review only; the plan reviewer judges that claim and the adjudicator records it on the pull request. A PASS plan carries weight in implementation review. It is not immune: when the work shows the plan wrong, the plan is corrected and the correction disclosed.

## Implementation review

A draft pull request means the work is in progress. When the change is complete on its branch and "Result" is filled, the pull request leaves draft, and three independent reviewers, one per facet, read the plan and the diff read-only, using the implementation brief below. Collect all three before adjudicating; do not exchange interim conclusions or repair from the first return.

Adjudicate together: verify consequential assertions against authority and actual consumers, reproduce counterexamples, resolve duplicates and conflicts, and distinguish defects, assurance limits, rejected assertions and genuine owner decisions. Reject bloated cures even when the diagnosis is valid. A finding outside the unit's plan becomes a new unit unless it falsifies the plan's purpose.

## Convergence is a judgment

A unit converges when the adjudicator can write, on the pull request, why the result serves the decision named in the plan, what was verified from the consumer surface, and what residual risk remains, and no material finding is open. Material means it would change the operator's decision or Owen's next decision.

Convergence is not three PASS returns, a passing suite, a round count, or exhaustion. Checks establish narrow mechanical claims; they never define the unit's quality. No reviewer is expected to return a finding count or meet a threshold. The adjudication names the commit it judged; a later commit reopens the judgment.

A further implementation round follows only when a repair changed meaning or a material risk remains open, and rounds continue until the judgment can be written. A falling residual is not that judgment, and neither is a round count. A unit the adjudicator still cannot judge after repeated rounds is re-planned rather than reviewed again; whether recurrence across rounds indicts the structure is decided under `DESIGN_PRINCIPLES.md`, "Minimum sufficient structure", which asks first whether the earlier rule was sound and merely unapplied.

Owen merges the pull request. Merge accepts the unit's content as reviewed; changed content needs its own acceptance.

## Briefs

Supply only the pull request number, the checkout path and, for implementation review, the assigned facet. PASS means no finding within the reviewer's stated coverage; it is a coverage statement, not a verdict. Reports go on the pull request as comments, one per reviewer and one adjudication. Nothing from a review enters the tree.

Plan brief:

> Review this plan independently under AGENTS.md, DESIGN_PRINCIPLES.md, the applicable STAGE_BOUNDARIES.md contract, REVIEW_PRINCIPLES.md and state/CURRENT.json, reading the owners the plan names. The plan is the body of the named pull request in owassmer/CORDON. Judge whether the unit serves the decision it names, whether its boundary and population are right, whether "done means" would be observable and could show the unit wrong, and whether the work invites a drift it does not guard against. Work read-only; do not perform the work or presume its outcome. Return PASS or FINDINGS. For each finding give the affected section, the consequence for the operator's decision, and the smallest faithful revision.

Implementation brief:

> Review independently under AGENTS.md, DESIGN_PRINCIPLES.md, the applicable STAGE_BOUNDARIES.md contract, REVIEW_PRINCIPLES.md and state/CURRENT.json. The unit's plan is the body of the named pull request; the change is its diff, checked out at the named path. Your facet is a primary responsibility, not a restriction on following evidence. Test the result against the plan's "done means" and against authority and actual consumers, including an ordinary record the work never registered. The plan carries weight; reality outranks it, so report where they disagree. Prior findings and passing checks are assertions to evaluate. Work read-only and without peer reports. Return PASS within stated coverage or FINDINGS. For each finding give the affected claim, the evidence, the practical consequence for the operator's decision, and the smallest faithful remedy. Distinguish a material defect from an optional improvement or something outside the unit. Do not change state or presume adjudication.

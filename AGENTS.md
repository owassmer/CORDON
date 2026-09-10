# CORDON

CORDON exists to reduce projected Xylella loss by giving the responsible public operator a legally and evidentially faithful computational decision instrument. The current operator and stage are state, not constitution; read them from `state/CURRENT.json`.

## Navigate from authority

| Need | Sole owner |
|---|---|
| General design posture | `DESIGN_PRINCIPLES.md` |
| Unit plan shape | `.github/PULL_REQUEST_TEMPLATE.md` |
| Plan review, implementation review, adjudication and convergence | `REVIEW_PRINCIPLES.md` |
| A–G derivation order and stage contracts | `STAGE_BOUNDARIES.md` |
| Current operator, accepted state, open stage, and next gate | `state/CURRENT.json` |
| Legal meaning | `regulation/stage-a/authoring-eu.json` and `regulation/jurisdiction/canonical/authoring.json` |
| Clocks and parameters | `regulation/stage-b/clocks-and-parameters.json` |
| Stage C mathematical reference | `regulation/stage-c/SPEC.md` and its package; acceptance status in `state/CURRENT.json` |
| Stage D inputs and source bindings | `regulation/stage-d/INPUTS.md`, `regulation/stage-d/SPEC.md`, and their package; acceptance status in `state/CURRENT.json` |
| Source and evidence classification | `corpus/CATALOG.csv` |
| Migration provenance and exclusions | `migration/MANIFEST.csv` and `migration/EXCLUSIONS.md` |

Research and reviews are evidence. They never override the owners above. If two apparent owners disagree, stop treating either summary as truth and reconcile them against the underlying evidence.

## Golden principles

- Optimize for the loss-reduction objective and the operator's real decision, not for an artifact, platform, or attractive dataset.
- Give each fact one owner. Link to it everywhere else.
- Keep quoted evidence, inference, adjudication, and provisional work distinguishable.
- Read the authoritative source before serializing meaning. Sources and other actors enter only where they directly affect the chosen decision chain; the current operator's full remit is not the product aperture.
- Respect stage boundaries. A downstream representation need cannot rewrite upstream meaning.
- Delete > replace > refine > add. Preserve full necessary meaning with the least structure and operator burden; complexity and process need a named decision or prevented failure.
- Keep the cure local. A finding does not authorize scope expansion, a broader rewrite, or another review ritual.
- Prefer the smallest structure that makes the wrong state unrepresentable; otherwise use a discriminating check before a prose reminder.
- Verify the resulting state from its consumer surface. A successful command, review, or build is only a signal.
- Treat missing reachable evidence as acquisition work. Treat genuine ambiguity as unresolved; never fabricate closure.
- When evidence changes a fact, repair its owner and every dependent consumer in the same pass.
- Owen owns direction, external commitments, spend, and genuine load-bearing ambiguity. An agent reasons independently, surfaces disagreement, and never converts deference into false certainty.

## Working posture

Before substantive work, read `state/CURRENT.json`, the applicable stage contract, and only the corpus entries and skills relevant to the task. Use the repo-owned skills under `skills/` when their descriptions match. Preserve old repositories as provenance archives; this repository is the live program authority.

Default to one bounded, reviewable unit per turn unless Owen authorizes a larger batch. State that unit before work. A next-five list describes sequence, not authorization to execute the whole list; prior broad GO instructions do not override a later request for smaller turns.

`origin/main` on GitHub (`owassmer/CORDON`) is the source of truth; local checkouts are working copies. Each bounded unit is one branch and one pull request that Owen merges; `scripts/worktree.sh <branch>` creates the branch beside other live work. The pull request opens as a draft whose body is the unit's plan, written from the template; the plan is reviewed once, the work is done, and the result is reviewed under `REVIEW_PRINCIPLES.md` before Owen merges. Open pull requests are the visible statement of what is in flight and why. A pull request regenerates `corpus/CATALOG.csv` and passes `scripts/verify_all.sh` in CI before merge. Nothing is pushed to `main` directly; `git config core.hooksPath scripts/githooks`, once per clone, refuses it. Git-ignored source populations live only in the primary checkout and are recreated by their tracked acquisition scripts.

Within an authorized stage round, work vertically through each source family: follow its consequential source routes, read its meanings and relationships, resolve implementation limitations, and verify the resulting consumer behavior before moving on. Parsing all selected records is not semantic maturity. An unexplored dependency cannot be closed by calling it conditional; identify its consumer and investigate it, or retain a source-grounded reason why it is outside the round. Recursive exploration follows the publisher and prior evidence, not the formats or endpoints supported by the current readers. Saturate each source’s relevant data and resolve its consequential meanings before closing that source. Run independent capture and semantic work concurrently across source families; neither a slow capture nor broader grounding is a reason to abandon, defer, or silently pause an authorized acquisition. Keep every active source accountable through completion, with progress and failures visible. Concurrent work changes scheduling, not the completion bar.

Stage research is disposable. During a bounded unit, `corpus/workbench/` may hold temporary captures and analysis. At the unit's close, each result must either change its canonical owner, survive as a direct source population consumed by that owner, or be deleted. Do not retain dated integration narratives, review transcripts, failed-request collections, retired implementations, case-authored readings, redundant manifests, or omnibus evidence lists as live program state. A source binding names the source population, the accepted input it supplies, its acquisition route, and its current limitation; it never reproduces the investigation trail. Relevance comes from an A–C consumer before source exploration begins.

End substantive turns with findings, the immediate next five steps, and a concrete restatement of how the work serves the telos. Findings must disclose material failed or unattempted access routes, unexamined dependencies, and changed conclusions alongside completed work. Material means capable of changing Owen's understanding of sufficiency, priority, or the next decision. A qualification buried in an attachment is not disclosure in the final report. Distinguish direct live inspection, retained-source reading, inherited reports, and unverified claims; never imply access or grounding that did not occur.

Derive the next steps from CURRENT and the current stage owner. In Stage D, place each material issue on the affected row of `regulation/stage-d/INPUTS.md` or resolve it before ending the unit; do not create a parallel gap ledger. An issue omitted from the immediate five remains visibly pending in its canonical row; omission never closes it. Read the resulting current state and user-facing report together for semantic consistency. This is a reporting obligation, not a claim that a checklist proves completeness.

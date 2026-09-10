# Stage B fresh review — joint adjudication, 2026-09-04

Dated review evidence, not current-state authority or acceptance. Current status belongs to `state/CURRENT.json`. No canonical remediation was performed during this review.

## Scope and method

Following hygiene, three fresh independent reviewers examined source fidelity, semantic coherence, and verification/consumer integrity. They received the constitutional aperture and stage contracts, complementary broad questions, and no prescribed verdict. The canceled review fragments were not used. All three final reports were collected before joint adjudication. The primary agent then checked the cited artifacts and sources and reran the verification counterexamples in isolation.

The aperture remains the current public operator's phytosanitary decision chain. Payments, the former cooperative product route, downstream algorithms, Actions, nouns, and platform design were not reopened. The durable objective is reduction of projected Xylella loss; this review tests whether upstream meaning can safely support that objective.

Hygiene normalized jurisdiction projection trailing whitespace and retained LF CSV output. Canonical substance did not change during hygiene or review. Reviewed fingerprints:

| Artifact | SHA-256 |
|---|---|
| EU A | `2e7878d87a3a55f9fa1caf02c53f55b458dff94ce7f0f71c5bf2d4b1cc2556bc` |
| Jurisdiction A | `d29487915317d0e74330a99485162b75dfdadeac6d5f3d18060899eeae84cd5d` |
| B ledger | `82475e44e5e1f2e59111d9ceb5020256aeda02b7ed505b502c1a93c342271833` |
| B population | `2504291b5faf4fb22c01fed973091a9ae301335ae0159f8da335d12b8a358799` |

## Verified findings

### R1 — Newly added reporting dependency backdates amended meaning

`regulation/jurisdiction/canonical/authoring.json`, `EU-2016-2031:Art.22(3):annual-survey-results-report:v1`, applies the Article 103 electronic route from 2019-12-14. The corresponding `B-CLK-EU2031-22(3)-annual-report-30-april` inherits this across its interval.

The [original Regulation 2016/2031, Article 22(3)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R2031) already contains the annual 30 April deadline and report payload, but not that route sentence. [Regulation 2024/3115, Article 1(4) and Article 3](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R3115) adds the electronic route. Publication on 16 December 2024 and the twentieth-day rule give an effective date of 5 January 2025. The special July 2026 application date concerns a different amendment.

Adjudication: verified, high confidence; introduced by the remediation. Version the changed route while preserving the earlier deadline. Do not move the whole reporting duty to 2025. Any earlier route asserted under a separate instrument needs its own controlling evidence. The narrow A reopening is not ready for acceptance. Also check whether external receipt is evidence of submission or an additional completion requirement; the cited paragraph does not expressly require a separate receipt act.

### R2 — Containment buffer survey points to an infected-zone clock

The disposition beginning `Nella zona cuscinetto, di ampiezza di almeno 5 km, le indagini annuali` points to `B-CLK-EU-15(2)-v1-annual-containment-survey`. That clock expressly covers Annex III infected-zone parts. The plan separately states annual buffer surveillance: `regulation/jurisdiction/national/DM-348260-2026-Xylella-plan.txt`, section 9.3, around line 1468.

Adjudication: verified, high confidence. Existence of a target is insufficient when its geography differs. Correct the disposition/clock relationship from controlling meaning; do not broaden Article 15(2) merely to accommodate the plan's buffer expression. The preceding whole-area disposition warrants the same scope check.

### R3 — Historical expression points entirely outside its operative interval

The disposition for `IT-DM-2022-XYLELLA-PLAN:§6.4:no-demarcation-two-year-follow-up:pre-m5-v1` points to `B-CLK-DM2022-6.4-post-m5-second-year`. The producer interval ends on 2024-10-17; the target begins on that date. Their half-open intervals do not overlap.

Adjudication: verified, high confidence. Repair historical resolution and inspect spanning dispositions. An older EU two-year clock exists: this demonstrates a broken relationship, not absence of the duration throughout B. The verifier currently checks target existence without requiring temporal compatibility.

### R4 — A lookback completes on the discretionary decision it supports

`B-CLK-EU-7(1)(e)-sub2-two-year-lookback` has completion `a_effect: IMMEDIATE_SAMPLING_DEFERRED`. The source separates preceding two-year sampling/survey evidence from the Member State's discretion to defer immediate sampling: `regulation/source/consolidations/02020R1201-20251124.txt`, Article 7(1)(e), around line 376.

Adjudication: verified, high confidence. Completion conflates satisfaction of the evidentiary lookback with exercising the decision. Preserve the evidence/decision distinction. Evaluation at a decision time is not itself the defect. The existing eligibility-threshold guard does not cover this lookback case.

### R5 — Consumer generation can falsely preserve acceptance after content changes

`scripts/generate_stage_b.py` checks acceptance strings, act, and reviewer, but not the accepted-content fingerprint or evidence binding. In an isolated synthetic fixture, all seams were marked accepted with fingerprints computed by the verifier, then a recurrence period was changed from 1 to 17. `verify_stage_b.py` rejected the stale fingerprint; direct generation nevertheless emitted changed CSV content and `ACCEPTED` for all four seams.

Adjudication: verified, high confidence, latent consumer-integrity defect. Real acceptance remains NOT_ASSERTED; this is not evidence of an actual unauthorized acceptance. Generation must enforce the same binding before presenting acceptance. The fixture used a correctly hashed AGENTS.md as nominal evidence, which additionally demonstrates that path/hash presence cannot authenticate an acceptance act; human authority must not be inferred from those mechanics.

### R6 — Population coverage is being mistaken for expression closure

Two isolated mutations survived the verifier: removing the disposition for minted `B-PAR-PNI2026-vitis-design` while retaining that parameter, and pointing the disposition for `B-PAR-EU-2(4)-v2-C80-p1` to the research-laboratory 24-hour clock. Current checks do not require every minted item to have its disposition or enforce disposition target type agreement.

Adjudication: verified, high confidence, a closure-check defect. Exact A population coverage is valuable but is not expression closure. Check item/disposition correspondence, target kind, and applicable source/version scope. Two reviewer-noted source-phrase variants are recognizable textual differences, not independently established legal errors; do not elevate them into substantive findings without examining the exact-phrase contract.

## Unresolved interpretation and additional regression gap

**Containment vector cadence:** section 9.3 is headed annual surveillance and introduces annual whole-area work. The vector sentence describes annual eradication surveillance, then contrasts containment geography across a page break (`DM-348260-2026-Xylella-plan.txt`, around lines 1485–1492). The current containment clock leaves recurrence null and categorically denies an express annual cadence. Reading the full sentence supports a plausible geographical contrast with retained cadence. Neither automatic annualization nor categorical denial is established by the review. Resolve this bounded interpretation before acceptance; retain the uncertainty until adjudicated.

**Numeric fidelity tests:** isolated changes 24 hours → 999 hours, confidence/prevalence 80/1 → 1/80, samples/tests swapped, and 30 April → 31 February all survived. Token presence does not preserve numeric roles, and clock values lack equivalent protection. These are demonstrated regression gaps, not findings that the current values are wrong. Source-role fidelity and calendar-value validity checks belong here; elapsed-time algorithms remain Stage C.

The primary agent reran the reviewer's probe at `/tmp/cordon-verification-review.DhPsuf/probe.py`. It uses in-memory patched reads and writes only temporary generated output. That path is ephemeral; the mutations and outcomes above are the durable reproduction specification. No synthetic acceptance fixture was written to the repository ledger.

## What held and limits of the verdict

The baseline bounded verification passes. A population contains 524 unique versions and agrees exactly with B's seam partition. The reviewed B ledger has 107 clocks, 53 parameters, and 758 dispositions. All four seam acceptances remain NOT_ASSERTED. The content fingerprint correctly rejects changed accepted content when the verifier actually runs.

The reviewers found support for retaining historical regional 10 km/five-year values conditionally, the obligor corrections, and inspected PNI numeric values. The alleged loss of EU Article 5(4)(a) annual recurrence was not sustained: separate annual clocks exist. Regional source parity is limited to the recorded 34 phrases in five plans with sampled visual checks; it is not full-document certification. These bounded positive results do not establish exhaustive semantic completeness.

## Recommended sequence

1. Correct the temporal A dependency from the original and amending sources; propagate the changed meaning through B and projections.
2. Resolve the bounded vector-cadence interpretation and receipt distinction; repair geographical and historical references and lookback completion.
3. Gate consumer acceptance consistently and add discriminating expression, target-type, interval, numeric-role, and date-validity counterexamples.
4. Regenerate, verify from consumer surfaces, then review the resulting delta with findings handled jointly. Do not declare B closed or open C on this report.

These are proposed corrections, not fixes performed by this review. Owen's direction and exact-content acceptance remain separate from reviewer conclusions.

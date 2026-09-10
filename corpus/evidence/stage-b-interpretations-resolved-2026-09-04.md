# Stage B bounded interpretations resolved — 2026-09-04

Dated evidence and implementation record, not a second source of current state. This follows `stage-b-correction-and-proposals-2026-09-04.md`. Legal meaning remains in the A canonicals, normalized cadence in the B canonical, and live status in `state/CURRENT.json`.

## Authority and scope

Owen approved both proposed resolutions in the conversation following the intuitive explanation of P1 and P2. He requested linguistic assurance for P1 if useful and explicitly generalized P2: excessive evidentiary caution, like over-provenance, must not leak into or become the product; the law supplies meaning.

This approves the two bounded interpretations, not every revised A row, a Stage B seam, or progression to Stage C. No semantic-acceptance act or record for a whole seam has been created. No independent review fanout was launched in this implementation pass.

## P1: annual containment-vector investigations

The approved reading is annual recurrence for the 2026 national plan's containment-vector investigations, with the containment geography retained. It supplies neither a fixed calendar deadline nor a count of visits. It is not extended to the 2022 plan or every vector-monitoring duty.

The underlying sentence was already Italian. Rereading its full syntax adds assurance: annual investigation throughout the eradication area is followed by a contrast specifying containment investigations in the buffer and stated infected-zone parts. The natural contextual reading changes geographical coverage without replacing cadence. The annual-surveillance heading and surrounding section support that reading. Repetition of the verb in the containment clause permits a narrower grammatical reading, so this is a reasoned, owner-approved interpretation—not a claim that an annual adverb is separately repeated there.

A bounded search did not locate an authoritative English counterpart to this national plan. Comparing our own translation would not supply independent evidence. The [Italian Union text](https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:02020R1201-20251124) and [English Union text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02020R1201-20251124), Article 15(2), (4) and (5), were checked as related context. Both distinguish infected-zone annual surveys, buffer sampling and vector monitoring. Neither language independently resolves the national sentence; no relevant divergence was found in these clauses. This comparison supports preserving the distinct scopes, not deriving a new cadence from translation.

The national evidence is the admitted `regulation/jurisdiction/national/DM-348260-2026-Xylella-plan.txt`, section 9.3, backed by the archived PDF inspection recorded in the preceding implementation note. The official national publication page was unavailable on this bounded revisit (HTTP 502); no new national source capture is claimed.

Implementation:

- The existing A containment-surveillance producer now expressly includes the annual vector-investigation meaning. Its existing branch/authority structure and effective interval are unchanged.
- Its quoted section omits only the intervening page header and form feed inside the sentence; its quote hash is recomputed. The source snapshot itself is unchanged. This is page-furniture removal, not a translation or rewritten quotation.
- `B-CLK-DM348260-9.3-vector-investigation-containment` now records a one-year period. Its evidence phrase is the complete eradication/containment contrast through the specified infected-zone parts, not the clipped containment half. Its own expression disposition matches that phrase.
- Containment scope, opening state, duty owner and completion remain intact. Visit count, calendar deadline and fixed window remain unset. The obsolete unresolved note is removed.

## P2: successful reporting, with receipt as possible proof

Both Article 22(3) versions now distinguish the required reporting act from evidence proving it. Successful reporting to the Commission and other Member States is required, through Article 103's system only for the amended version. A draft, queued transmission or attempt does not satisfy that act. A receipt or system acknowledgement may prove successful performance; this provision does not add an independent acknowledgement duty or prescribe a particular proof format.

Missing evidence leaves performance unverified, not automatically breached. This does not relax a receipt or verification condition that another applicable legal rule actually makes consequential. Nor does regional preparation or transmission to a national actor prove that the Member State completed its Union reporting duty.

The [original Article 22(3)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R2031) and [amending Article 1(4)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R3115) remain the bounded source basis recorded in the preceding implementation note. No newly discovered reporting protocol is claimed.

Implementation changes both A evidence contracts and their unverified-performance wording. The amended true effect also names the recipients already present in its source. Both B clocks still complete on performance of their applicable A version; their obsolete unresolved-receipt notes are removed. The 30 April deadline and 2025-01-05 version boundary are unchanged. No Stage D evidence format or Stage E receipt workflow has been invented.

## Shared lesson

The existing epistemic-boundaries section of `DESIGN_PRINCIPLES.md` now distinguishes responsible caution from invented legal conditions and operator workflows, while preserving evidentiary conditions supplied by law. The evidence-adjudication and failure-led realignment skills informed repairing owners and consumers together; the regulatory-derivation skill kept proof-format and workflow implementation out of A/B. No new constitutional file, skill or gate was added.

## Verification

Three bounded regression tests were added to `scripts/test_stage_b_repairs.py`: annual cadence with preserved scope and no invented scheduling quantities; exact reconstruction of the full Italian sentence from the unchanged source after removal of page furniture; and reporting proof versus an extra act across both historical versions. These are contract and source-fidelity checks, not an implemented field-scheduling or evidence-evaluation algorithm, and not independent semantic acceptance.

Final verification passed: `bash scripts/verify_all.sh` (including all 24 repair regression tests), 12 EU mutation checks, 4 jurisdiction mutation checks, 10 B mutation checks, and `git diff --check`. The real B CSVs match every canonical field; their input/output hashes match generation status and their semantic acceptance remains NOT_ASSERTED. The real jurisdiction A provision-version CSV matches every canonical projected field by version ID, with canonical and generated-output hashes verified. The raw national source snapshot remains byte-identical to its admitted hash.

Inventory remains 525 A versions, 109 B clocks, 53 parameters and 759 dispositions. The revised jurisdiction A fingerprint is `b2a7a3d7ecfccccb0df7ede90a8aeaf651fdd57b9d24d6c1de084da1b4898a7f`; revised B is `123cad147cc4d9498385d83421a745f39ba3fd1b59653dd032ff8dc35f12c85a`. The next gate is independent review on Owen's GO, with reports assessed together, followed by exact-content acceptance and the remaining post-stage closure questions. Stage B remains open; Stage C has not begun.

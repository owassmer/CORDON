# CORDON semantic pack (O0)

Status: APPROVED (Owen, 2026-08-23) — all six sheets walked through and approved; decision log D1–D5 closed
Drafted by: Connor, as Owen's authorship proxy, from the accepted Gate 5–7 authorities. Owen's approval makes each sheet binding.
Consumers: AI FDE build prompts per `cordon-reference-INDEX.md`; Hermes extraction/build lanes; reviewers.

Standing rule: if a sheet does not answer an implementation question, the question routes to Owen. No agent invents a predicate, tool, status field, or data binding.

## Files

| Sheet | File | Gates prompt |
|---|---|---|
| Kernel — Accept Cooperative Execution Mandate | `kernel-accept-cooperative-execution-mandate.md` | P06, P07 |
| Kernel — Decide Cooperative Pursuit | `kernel-decide-cooperative-pursuit.md` | P06, P07 |
| Kernel — Commit or Rebalance Intervention Capacity | `kernel-commit-or-rebalance-intervention-capacity.md` | P06, P07, P08 |
| Kernel — Dispatch Intervention | `kernel-dispatch-intervention.md` | P06, P07 |
| Now-view projection contract | `now-view-projection-contract.md` | P04 |
| Chatbot tool schema | `chatbot-tool-schema.md` | P10, P11 |

## Shared kernel conventions

These conventions apply to all four kernel sheets. Each sheet states only its deltas.

**One implementation, two callers.** Each kernel is one versioned, deterministic, side-effect-free function (Gate 6 Contract 3). `Assess Named-Action Readiness` calls it for explanation. The mutating Action calls the identical kernel version on fresh state at apply time. No duplicate rule definitions anywhere else.

**Verdicts.** A kernel returns exactly one of:

- `READY` — every prerequisite is determinate and satisfied.
- `NOT_READY` — at least one prerequisite is determinate and unsatisfied (a fact is absent or false).
- `INDETERMINATE` — no determinate blocker exists, but at least one load-bearing premise cannot currently be asserted (stale/unhealthy source, or unresolved conflict).

Precedence: `NOT_READY` dominates `INDETERMINATE` dominates `READY`. The kernel always returns the complete evaluation — all satisfied premises, all blockers, all indeterminate premises — never only the first failure.

**Missing / stale / conflicting (M/S/C) mapping.**

| Condition | Meaning | Verdict contribution | Cure |
|---|---|---|---|
| M — missing | A required fact does not exist (no record where the route requires one) | `NOT_READY` | the named actor who can create/decide the fact |
| S — stale | The fact exists but its source violates its assurance contract (freshness SLO, health, conservation) | `INDETERMINATE` | the named source/assurance owner |
| C — conflicting | Sourced assertions disagree and competence/scope/version/date resolution has not occurred | `INDETERMINATE` | the named conflict-resolution owner |

Table shorthand in the sheets: `M→NR`, `S→IND`, `C→IND`, with the cure owner named per row. Per the accepted source-conflict boundary, a conflict blocks only the decisions it can change; unaffected premises and scope continue.

**D1a scoping rule (accepted).** `INDETERMINATE` models operator-world indeterminacy only. Assurance contracts (freshness SLOs, health checks) exist solely for admitted sources, so a build-side acquisition gap can never surface as `INDETERMINATE`: it is closed by the notional layer (D5) or is genuine world-absence (`NOT_READY` with cure owner). Determinate domain conflicts (duplicate pursuit, incompatible clocks, declared-and-unresolved conflicts of interest) are `NOT_READY`. The `C→IND` lane covers only unresolved source-assertion conflicts (publication/competence/version/date), whose resolution owner is a steward, never the manager.

**Output contract (all kernels).** Verdict; satisfied premises; blockers each with cure owner; indeterminate premises each with failed assurance reference and last-accepted watermark; continuable scope; consequence of acting now versus waiting where derivable; kernel version; premise fingerprint.

**Premise fingerprint.** sha256 over the ordered list of (predicate id, resolved fact references, fact versions/as-of timestamps) the kernel evaluated. The Action refuses on fingerprint mismatch at apply time (stale command).

**Idempotency.** Duplicate-detection predicates identify an existing equivalent decision/occurrence. The kernel reports it; the Action layer deduplicates and returns `ALREADY_COMMITTED` per Contract 4. A kernel never blocks on its own prior success.

**Non-implications are output, not decoration.** Every `READY` verdict and every Action receipt carries its sheet's non-implication list so a permitted act is never read as a broader truth.

## Decision log

| # | Decision | Status |
|---|---|---|
| D1 | M→NOT_READY; S→INDETERMINATE; C→INDETERMINATE with named resolution owner; NOT_READY dominates; plus D1a scoping rule (INDETERMINATE = operator-world only; build gaps never present as INDETERMINATE) | ACCEPTED (Owen, 2026-08-23) |
| D2 | Proposal fingerprint mismatch is determinate (`NOT_READY`; cure: manager re-compares and re-selects; never auto-refreshed) | ACCEPTED (Owen, 2026-08-23) |
| D3 | Now-view clock horizon: per-clock-kind configurable, default 30 days, versioned in projection config | ACCEPTED (Owen, 2026-08-23) |
| D4 | Curated object query covers the 11 visible types only; hidden substrate reachable only through parent-scoped projections and Function outputs | ACCEPTED (Owen, 2026-08-23) |
| D5 | Notional layer (Owen ruling 2026-08-23): build-as-real; notional rows only where real data is genuinely underivable; recorded in the build-side data ledger, not as an operator-UI evidence state; identifier hygiene enforced; no admission profile ever claims a seeded row | ACCEPTED |
| D12 | Sprint realignment (Owen, 2026-08-24): **source** — AdE Puglia bulk is the sole current Parcel source and already covers the full cadastral-unit universe, including Zapponeta-area land under E885/Manfredonia. SIT Catasto is a fixed September-2021 snapshot with no material operator value; purge its landed Parcel dataset, reconciliation output, source-register family and all Parcel-history logic. WFS has no B1.1 gap to fill and remains deferred reconnaissance only. No local computed upload. **product** — capacity comparison/reallocation is a bounded feature, not the hero or a never-cut demo beat; use the intuitive native implementation and stop when its material decision works. **ownership** — Connor authors architecture, plans, specifications and review briefs; Ferro implements only reviewed Connor-authored plans as sole Foundry writer | ACCEPTED |
| D11 | Remaining grill decisions (Owen, 2026-08-24): accept Q6a–p and Q6r–t recommendations from the remaining-decision map, subject to a standing anti-complexity rule: an added source, role, state, scenario, test or UI element stays only if it enables a material operator decision or falsifies a load-bearing assumption; marginal realism is insufficient. Key policies: B3 uses Bari sample 1964901 for Q1 and DET 3/2026 Bitonto as a dispatch-basis anchor; the two remain separate unless real scope proves a dependency. DET 3/2026's execution window is historical, so a Dispatch commit uses it only in a dated replay/simulation; a live commit requires a currently operative basis. Dispatch capacity is route-conditional under Q5n: cooperative-controlled/contracted resources require Capacity Commitments; public/authority execution such as an elected ARIF route uses authenticated external assignment/feasibility evidence and never mints a cooperative commitment. Capacity planning uses a rolling 12-week/weekly plan, fairness constraints before loss-reduction objective, earliest-clock/longest-ready/stable-hash tie-break, explicit protected commitments and reasoned overrides; source cadence/freshness is source-specific by missed cycles; Map layer and responsibility-line contracts follow D9; hosted model chosen by frozen Evals; AIP explains decisions/changes/non-effects/owner/receipt and never acts proactively. **Q6q rejected:** INDETERMINATE/refusal is a feature and Eval case, not a hero or dedicated demo beat. **Q6r accepted:** DDS 167/2025 demonstrates ingestion/order≠cash mechanics; Article 6 liquidation appears in the broader Payments picture | ACCEPTED |
| D10 | Q5 private-graph grill (Owen, 2026-08-24): **Q5c** seed 750 producer members as a full recognized-OP scale model, never claimed as PugliaOlive's actual roster. **Q5f** create 900 evidence-seeded, context-stratified Holdings on real olive-relevant Parcels; no random cadastre. **Q5g** seed external/customer-held premises only; all cooperative decisions are created through the four exact Actions. **Q5h** deterministic cohorts: 300 collective-interest, 150 individual route, 150 undecided/no response, 150 no current route; collective mandates split 180 complete, 60 incomplete, 30 expired, 30 conflicting. **Q5i** each Holding has 3–8 nearby olive-relevant Parcels (median 5); 20% split into two nearby clusters; no Parcel reused across current Holdings. **Q5j** standing cohorts: 700 fully clear, 100 current lease/consent, 50 one Parcel missing access, 25 expired consent, 25 conflicting control. **Q5k** external operational Parties use real public identities/qualifications and seeded customer-held availability/offers/slots/terms. **Q5l** PugliaOlive is the domain actor authorized for all four exact Actions; one authenticated Foundry principal acts on its behalf. The principal is logged in Action logs/receipts and is not modeled as a NaturalPerson. Contextual authority remains Action/basis/scope/date-specific. **Q5m** initial Interventions are basis-driven: compulsory work from real duty/order scope; voluntary recovery from applicable member land/programme context plus a customer/professional intended scope; collective interest alone does not mint an Intervention. **Q5n** Capacity Commitments cover only PugliaOlive-controlled/contracted resources (plant stock, contractor/equipment days, technician hours, contracted water service, cooperative bridge-finance envelope); inspector/permit/lab/bank/authority capacity remains an external feasibility premise | ACCEPTED |
| D9 | Workshop surface amendment (Owen, 2026-08-24): persistent three-pane operating picture — Now/context rail with five continuously visible responsibility lines (Land, Funding, Applications, Field Work, Payments); interactive Map as the central pane; embedded AIP decision/execution panel on the right. Responsibility selection changes Map layers, Q1–Q6 scene and AIP context without resetting the selected member/land/date/route. Responsibilities are simultaneous projections, not tabs or stages. The Map is core but never authority; selection supplies candidate scope and Functions/Action kernels resolve consequence | ACCEPTED |
| D8 | Q5 organization anchor (Owen, 2026-08-24): the initial private graph represents **PugliaOlive Società Cooperativa, IT/OLI/112**. Public/source-backed facts: recognized olive OP, agricultural cooperative, Bari office, recognition maintained 9 June 2025 (`06/VMR/OLI/BA/2025`), VPC 2024 €43,023,529.20. Private/customer-held and seeded separately: member identities, membership, holdings, mandates, Pursuits, commitments, interventions and actual geographic footprint. Rationale: the demo proves how CORDON serves a major cooperative manager across the complete member recovery portfolio in several Puglia contexts; PugliaOlive's scale and regional posture fit the whole operating model, while Bari gives direct relevance to the multi-subspecies frontier. Xylella effect is established through real land, monitoring, duty and programme data, not a fabricated organization-level status | ACCEPTED |
| D7 | Ingestion grill (Owen, 2026-08-24), binding detail in `b1.1-object-data-mapping.md`: **Q1** row provenance = source reference + as-of only; the three-enum provenance taxonomy is first-build drift, retired from product schemas (this narrows D6: the enum itself is gone; seeded-ness stays build-side per D5). **Q2** `OfficialArea` existence from the instrument registry, geometry from the scheduled zone sync, act-derived foglio coverage, mismatches surface as facts. **Q3** `GoverningInstrument` discovery via BURP RSS + `/documenti` catalog + `/bollettini` reconciliation; measure pages are a reconciliation lane, never the completeness boundary. **Q4** every officially sampled tree is an `IndividualPlant`; result is observation data, not the identity gate. Standing: full-universe ingestion when marginal cost is sync time; Plant→Parcel total via spatial containment; no branch/merge ceremony; notional layer out of B1.1 pending the Q5 composition grill | ACCEPTED (Owen, 2026-08-24) |
| D6 | **SUPERSEDED BY D7.** The proposed `source_class` product property is retired with the three-enum provenance taxonomy. Private facts remain customer-held in the operator world; build-side seededness remains only in the build manifest. | SUPERSEDED (Owen, 2026-08-24) |

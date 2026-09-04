# Now-view projection contract

Status: APPROVED (Owen, 2026-08-23)
Owner mechanism: pipeline-owned projection dataset (Gate 6 M12 compute split). Workshop renders it; the Chatbot may reference it; no client recomputes it.

## Purpose

The Now view is the manager's entry scene: material changes and bounded decision scenes that currently need coordination. No accepted Function produces this cross-change aggregate, so this contract defines it once, server-side, versioned and testable. Without it the aggregate would be assembled from Workshop variables and client-side sorts — business logic in the client, invisible to versioning and Evals.

## Row schema

| Field | Content |
|---|---|
| row id | deterministic from subject + triggering basis (stable across refreshes) |
| subject | object type + id of the semantic owner the scene opens on |
| decision scene | which question class (Q1–Q6) and named decision/Action the row leads to |
| triggering basis | the exact change/occurrence/proposal/clock reference that admitted the row |
| current owner | Party currently owning the next decision (from contextual authority; never a free-text assignee) |
| consequential clock | timestamp + clock kind (legal deadline, window close, expiry, review date) where one applies |
| premise state | `current`, or `indeterminate` with the failed assurance reference and last-accepted watermark |
| route family | responsibility grouping (Land, Funding, Applications, Field Work, Payments) as a consequence label, never navigation partitions |

## Inclusion rules — exhaustive

A row exists if and only if one of:

1. a material change with at least one affected decision (per the pipeline-owned candidate dependency relation, filtered as `Determine Affected Decisions` defines);
2. an approaching consequential clock (horizon per clock kind, configurable and versioned in projection config; default 30 days — decision log D3);
3. a returned authoritative external outcome awaiting the manager's next bounded decision;
4. a prepared Capacity Portfolio Proposal awaiting selection or expiry.

Nothing else. In particular: no row derives from a status field (none exist), a severity guess, a model score, or a manual pin.

## Ordering — fixed

Group by current owner, then route family. Within a group: consequential time ascending; rows without a clock follow clocked rows, ordered by triggering-basis time ascending. That is the complete ordering.

**Refusal, stated once:** there is no cross-line priority score in this system. Ranking heterogeneous legal, financial, field and biological consequences into one ordinal is a global status expressed as arithmetic, and global status is prohibited by the accepted model. The operator may apply her own filters; the default order never encodes a computed priority.

## Degraded behavior

- A row whose load-bearing premise goes stale persists and shows `indeterminate` with the failed premise and cure owner. It never silently vanishes.
- A row is removed only when its triggering basis is resolved, withdrawn, or superseded — each of which is a recorded fact, not a UI action.
- If the projection build itself fails, the surface shows the projection's last-built watermark; it does not re-derive rows client-side.

## Verification

The projection is a versioned dataset with expectations (row identity, inclusion-rule conformance, ordering determinism) and Eval cases (change→row appears; premise killed→row shows indeterminate; basis resolved→row leaves). Client rendering adds nothing to row content or order.

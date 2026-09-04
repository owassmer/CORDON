# Chatbot tool schema

Status: APPROVED (Owen, 2026-08-23)
Perimeter rule: the runtime allowlist is exactly the ten tools below plus configured retrieval context. No generic edit tool, no arbitrary Function runner, no backing edit Function, no Commands that mutate domain truth, no eleventh tool without a Gate-level decision.

## Read tools (6)

| # | Tool | Parameters | Returns | Never |
|---|---|---|---|---|
| 1 | `Determine Affected Decisions` | change/subject scope; as-of | affected decisions with owners/clocks/paths; explicitly unaffected work; indeterminate premises | rediscover the population; write any status |
| 2 | `Assess Named-Action Readiness` | Action type; target; scope; actor; date | kernel verdict + full output contract (see kernel sheets) | execute anything; store readiness |
| 3 | `Compare Feasible Intervention Portfolios` | scope; policy/optimizer version | best feasible portfolio; materially equivalent alternatives; binding constraints; infeasible reasons; sensitivity; tie-break basis | commit; present a score as authority |
| 4 | `Determine Remaining Exposure` | subject scope | independent legal / operational / financial / biological lines, each with owner, clock, indeterminate premise | any global completion; order→cash inference |
| 5 | Curated object query | allowlisted filters/aggregations | bounded object sets over the 11 visible types, named visible properties, minimum basis references | query hidden substrate, historical project, or backstage resources; any edit |
| 6 | Request clarification | one focused question | resumed reasoning with the answer | act as an approval dialog |

Hidden occurrence/context records are reachable only through parent-scoped projections and Function outputs (decision log D4), never by free query.

## Write tools (4)

Each is the exact Ontology Action; guards are platform-side (permissions, submission criteria, fresh kernel revalidation). The model constructs one call; it grants nothing.

| # | Tool | Required parameters | Receipt |
|---|---|---|---|
| 7 | `Accept Cooperative Execution Mandate` | mandate ref+version; member; outcome; scope; reason where required | one durable status + non-implications per kernel sheet |
| 8 | `Decide Cooperative Pursuit` | Pursuit ref or creation params; outcome; reason | same |
| 9 | `Commit or Rebalance Intervention Capacity` | Proposal ID; idempotency token; override reason where required | same, plus target count/hash and material deltas |
| 10 | `Dispatch Intervention` | Intervention; bounded scope; executor; intent/date; stop/return conditions | same |

## Direct-execution binding (Contract 4 fields)

Every mutation binds: authenticated principal; immutable originating message ID; exact Action type RID + version; exact target IDs or Proposal ID; target count + bounded material-delta summary; premise fingerprint; single-use idempotency key; expiry/invalidation condition. **At most one mutating tool per conversational turn.** Receipt statuses: `COMMITTED`, `ALREADY_COMMITTED`, `REFUSED`, `CLARIFICATION_REQUIRED` — exactly one, durable, retrievable after a dropped response. The model never retries a mutation after an uncertain result.

## Clarification triggers — exhaustive

Ambiguous target; ambiguous or unbounded scope; deictic reference ("these", "that one") after the application selection changed; missing required reason or override reason; unresolved acting authority; materially ambiguous consequence; more than one plausible Proposal. Clarification resolves what the manager meant. It is not approval: a clear authenticated command executes directly, and refusal is done by server-side guards, not by dialogs.

## Routing rule

Decisions owned by another actor (member elections, professional certifications, public decisions, bank facts, acceptances) are prepared and routed to that actor, never executed, simulated, or manually recorded. There is no tool that records an external outcome by hand.

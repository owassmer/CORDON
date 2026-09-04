# Foundry merge/deploy error surfaces

Where real error detail lives in the Global Branching merge UI and in the calls
behind it. Written for a builder agent who must never again report the generic
banner as "the error".

Captured 2026-08-17 from `owenwassmer.usw-22.palantirfoundry.com` as
`owassmer1@gmail.com`, read-only. Subject: proposal
`ri.branch..proposal.1c1d4e64-1678-417c-81d7-457a4dd4b9a0` (fresh, failed
20:44:47Z) and its predecessor `ri.branch..proposal.c20a7e44-f0cb-4a29-94d4-9acbfd6e007f`
(closed). All quoted content is verbatim observed output.

## TL;DR

1. Read `/approvals/api/task-requests/{ontologyTaskRid}` **first**. It is the only
   surface that describes *why* a task can or cannot be invoked. The UI never
   shows it.
2. Read the `DeploymentTaskListQuery` GraphQL response **second**. It carries the
   structured `errorName` / `taskRid` / `instanceId`.
3. Never quote the top-level banner. Its `errorInstanceId` is literally `null`.

The page has exactly three "View error" affordances. Two render the same useful
string. One renders nothing of value. Ferro has been clicking the useless one.

## The three "View error" affordances

Enumerated from the live DOM on the proposal Overview tab. `top` is the
document-Y offset, given so a builder can tell them apart deterministically.

| # | DOM anchor | Label above it | Y | Verdict |
|---|---|---|---|---|
| 1 | `button.bp6-button.bp6-intent-danger` inside `div.branch-components__first-row__1d48dd5` | `Merge failed` / `0 of 1 task` | 613 | **Useless** |
| 2 | `button.bp6-button.bp6-intent-danger` inside `div.branch-components__side-element__139nk1g` | `Ontology entities 3` | 685 | Useful |
| 3 | `button.bp6-button.bp6-intent-danger` inside `div.branch-components__error-cell__139nk1g` | `Deploying changes made to the ontology` | 873 | Useful |

Affordances 2 and 3 render the **same** string, from the **same** single query.
They are not two independent facts.

### Selecting the right one, deterministically

```javascript
// Wrong: [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'View error')
// That returns affordance #1, the useless one.

// Right: take the LAST one, or filter by document position.
const btns = [...document.querySelectorAll('button')]
  .filter(e => e.textContent.trim() === 'View error');
const informative = btns[btns.length - 1];   // affordance #3
```

The popover renders into a Blueprint portal and contains no network call of its
own — the text is already in memory from page load. Clicking it is read-only.

## Surface ranking

### Rank 1 — Approvals task state (best; not exposed in the UI at all)

```
GET /approvals/api/task-requests/{taskRid}
Authorization: Bearer <token>
```

`{taskRid}` is the `ri.ontology..proposal.*` RID, not the branch proposal RID.

This is the highest-value surface on the platform for this failure class. It is
the only place that reports invokability directly. Observed for the current
task:

```json
{
  "taskRid": "ri.ontology..proposal.93d8a985-b48b-453c-ad76-39e7e09ce9e2",
  "taskType": "ontology-metadata:approvals-v2",
  "taskRequestRid": "ri.approvals.main.request.e3be5e4a-fe93-46ab-9756-7ac23f05429c",
  "title": "Ontology proposal for global proposal ri.branch..proposal.1c1d4e64-1678-417c-81d7-457a4dd4b9a0",
  "status": "APPROVED",
  "invocationBlockers": [],
  "draft": false,
  "invokeWhenReady": false,
  "reviewers": [],
  "creationTime": "2026-08-17T20:40:18.050261348Z",
  "lastUpdatedAt": "2026-08-17T20:45:54.339000502Z",
  "historyTypes": ["creationEntry"],
  "subtaskStatuses": ["APPROVED", "APPROVED", "APPROVED"]
}
```

And for the superseded task, which proves the field is populated when a real
blocker exists:

```json
{
  "taskRid": "ri.ontology..proposal.c929c272-7ad6-423b-bc8e-dd9be1f5f480",
  "status": "CLOSED",
  "invocationBlockers": ["REQUEST_IS_CLOSED"],
  "historyTypes": ["creationEntry", "closedEntry"]
}
```

Read `status`, `invocationBlockers`, `subtasks[].approvalStatus`,
`subtasks[].resolvedPolicies[].policyApprovalRequirementsMet`, and
`subtasks[].checkpointsValidation.passesValidation`.

There are no sub-resources. `/invokability`, `/invocation-blockers`, `/policies`,
`/reviewers` under the same path all 404. This one GET is the whole surface.

### Rank 2 — DeploymentTaskListQuery (the structured error)

```
POST /graphql-gateway/api/bulk?q=DeploymentTaskListQuery
```

Path to the payload:

```
data.globalProposal.deployment.tasks.values[]
  .details.branchedResourceV1.progress.failedMessage
```

Observed verbatim for the current proposal:

```
RemoteException: CUSTOM_SERVER (Approvals:TaskRequestInvokeFailed) with instance ID 8f091547-12cb-4622-83ce-a03724375f80: {errorName=ApprovalsClient:TaskIsNotInvokable, taskRid=ri.ontology..proposal.93d8a985-b48b-453c-ad76-39e7e09ce9e2}
```

The same query also returns the join that matters, which no popover renders:

```json
"branchResource": {
  "rid": "ri.ontology.main.ontology.cfb1478a-5b0e-466a-aaff-b212870e8861",
  "ontologyBranch": {
    "rid": "ri.ontology.main.branch.50ac81c8-d506-49b3-a5af-a932aabf012c",
    "changeProposal": {
      "rid": "ri.ontology..proposal.93d8a985-b48b-453c-ad76-39e7e09ce9e2"
    }
  }
}
```

That `changeProposal.rid` is how you get from a branch proposal to the ontology
task RID you need for Rank 1. It resolves live, so on the *closed* proposal
`c20a7e44` this field already shows the *new* task `93d8a985` while
`failedMessage` still names the old task `c929c272`. Do not read that as
corruption; the message is a historical string and the join is a live pointer.

Response transport is `text/event-stream`: one `data:` line per operation, not a
single JSON object.

### Rank 3 — Useless: ProposalHeaderWithDeployabilityQuery

This backs affordance #1, the top banner. Observed verbatim:

```json
"deploymentError": {
  "error": {
    "errorInstanceId": null,
    "errorName": "Error encountered while deploying",
    "safeMessage": "Error encountered while deploying",
    "__typename": "GlobalProposalDeploymentError_GenericError"
  },
  "__typename": "GlobalProposalDeploymentError_GenericErrorV2"
}
```

`errorInstanceId` is `null` and `errorName` is prose. The union type is
`GlobalProposalDeploymentError_GenericError` — the schema's fallback arm. The
schema does define richer arms (`..._ResourceDeploymentFailed`,
`..._BuildFailed`, `..._ConsumerNotPrepared`), but this deployment does not
populate them. Nothing actionable is recoverable here. Never quote it.

The same query does carry two fields worth reading:
`deployability` (`DEPLOYABLE` / `NOT_DEPLOYABLE`) and `lastDeployment.id`, which
you need as `deploymentId` for the Rank 2 call.

### Not obtained

- **Developer Console / job surface.** No build or job RID is produced by this
  deployment. `taskCounts.totalNumberOfTasks` is 1 and that task is the ontology
  merge, not a build. There is no build report to open. The
  `GlobalProposalDeploymentTaskDetails_Build` arm exists in the schema but is
  unpopulated here.
- **An approvals detail page.** `/compass/api/resources/{ontologyTaskRid}` returns
  `204 No Content`, so the ontology task is not a Compass resource and has no
  navigable page. The task is reachable only through the `/approvals` API.

## Root-cause findings

### Established by evidence

1. **The failing object is the ontology-side approvals task, not the branch
   proposal.** `ri.ontology..proposal.93d8a985-…` is an Approvals task of type
   `ontology-metadata:approvals-v2`. `ri.branch..proposal.1c1d4e64-…` is the
   Compass-visible branch proposal. The deploy resolves the second to the first
   via `ontologyBranch.changeProposal` and then invokes it. The invoke is what
   fails.

2. **The current task is, right now, invokable by the approvals service's own
   accounting.** `status: APPROVED`, `invocationBlockers: []`, all three subtasks
   `APPROVED`, every `policyApprovalRequirementsMet: true`, every
   `checkpointsValidation.passesValidation: true`. The contrasting closed task
   returns `["REQUEST_IS_CLOSED"]`, which proves the field is populated when a
   genuine blocker exists. The empty array is a real signal, not an unimplemented
   field.

3. **The proposal is currently deployable.** `status: OPEN`,
   `deployability: DEPLOYABLE`, `deployabilityErrors: []`, `activeDeployment: null`.

4. **`ri.ontology.main.branch.ac23245e-…` is not an anomaly.** It appears in the
   `resolvedPolicies` of both the current and the superseded task, identically.
   It is stable policy-evaluation scope, not a stale or mismatched branch. Do not
   chase it.

5. **The failed invoke left no history entry.** `history` contains only
   `creationEntry`. The Approvals service did not record the invoke attempt,
   which is consistent with rejection at the invokability gate before any state
   transition.

### Timeline

| Time (UTC) | Event | Source |
|---|---|---|
| 20:40:18.050 | Task `93d8a985` created | `creationTime` |
| 20:44:47.733 | Merge clicked; deploy `82045f7b` starts and fails | `lastDeployment.started.time` |
| 20:45:54.339 | Task `93d8a985` last updated → settled `APPROVED`, no blockers | `lastUpdatedAt` |

The merge was attempted **4m 29s** after the task was created and **67s before**
the task reached its settled state.

### Stated plainly: what is NOT established

The timeline is *consistent with* the task not yet being invokable at 20:44:47
and becoming invokable at 20:45:54 — a readiness race, not a corrupt branch. It
does **not prove** it. `lastUpdatedAt` records that something changed at
20:45:54; it does not say what changed or what the status was at 20:44:47. The
Approvals API exposes no historical status and the failed invoke wrote no
history entry, so the state at merge time is **unrecoverable from any surface I
could reach**.

Three explanations remain live and this evidence does not separate them:

- **Readiness race.** The task was still settling when the merge fired.
- **Single-use invoke gate.** The task is invokable once; something consumed the
  gate. Weakened by the empty `history` and empty `invocationBlockers`.
- **Enrollment/tier limitation** in which `ontology-metadata:approvals-v2` tasks
  are never invokable by the branch-service identity, regardless of state. Not
  testable read-only.

I could not determine which. That is an honest gap, not a finding.

### The one cheap experiment that separates them

The current task is invokable *now* by every field the service exposes, and the
proposal is `DEPLOYABLE`. If the readiness race is the cause, a merge now
succeeds. If it fails again with `TaskIsNotInvokable` while
`invocationBlockers` is still `[]`, the race hypothesis is dead and the
remaining explanation is structural — the arrangement is wrong, not the timing.

Either outcome is decisive. That is worth one attempt.

## Procedure for Ferro

Connor's lane is read-only, so the mutating step below is not executed here.

**Step 1 — precheck, read-only.** Run both and require both to pass:

```bash
source scripts/foundry_env.sh
python3 scripts/foundry_browser_client.py proposal ri.branch..proposal.1c1d4e64-1678-417c-81d7-457a4dd4b9a0
# require: status OPEN, deployability DEPLOYABLE, activeDeployment null

python3 scripts/foundry_browser_client.py approval ri.ontology..proposal.93d8a985-b48b-453c-ad76-39e7e09ce9e2
# require: status APPROVED, invocationBlockers []
```

Abort if either fails. Re-derive the task RID from the proposal rather than
pasting it, because it changes whenever a proposal is recreated:

```bash
python3 scripts/foundry_browser_client.py tasks <proposalRid>   # prints changeProposal
```

**Step 2 — the single mutating click.** Owner: Ferro. Open

```
https://owenwassmer.usw-22.palantirfoundry.com/workspace/developer-branching/proposal/<proposalRid>
```

Before clicking, paste the interceptor from
`queries/foundry-browser-api-map.md` §"Capture procedure" into devtools so the
`DeployProposalMutation` request and response are recorded. Then click **Merge
proposal** and confirm.

**Step 3 — read the result correctly.** Do not read the banner.

```bash
python3 scripts/foundry_browser_client.py tasks <proposalRid>
python3 scripts/foundry_browser_client.py approval <ontologyTaskRid>
```

Report `failedMessage` verbatim plus `status` and `invocationBlockers`. If
`invocationBlockers` is non-empty, that array is the answer and no further
diagnosis is needed.

**Step 4 — stop condition.** If this attempt fails with `invocationBlockers: []`,
do not retry. The failure is structural. Escalate with the three artifacts above.

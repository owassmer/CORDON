# Foundry browser-lane API map

Every browser-lane action Ferro needs, mapped to the HTTP call that performs it,
so the action can run as a direct API call instead of UI clicking.

Derived with the `har-derived-api-client` skill from XHR captured on
`owenwassmer.usw-22.palantirfoundry.com` on 2026-08-17, read-only, as
`owassmer1@gmail.com`.

Generated client: [`scripts/foundry_browser_client.py`](../scripts/foundry_browser_client.py).

## Status legend

- **VERIFIED** — observed in captured traffic *and* replayed successfully with no
  browser in the loop.
- **OBSERVED** — captured from live traffic; not independently replayed.
- **MAPPED, NOT INVOKED** — request shape read verbatim from the app's JS bundle.
  Never executed. Mutating.
- **NOT OBTAINED** — could not capture. Procedure given instead.

## The headline finding

**The browser lane is not actually browser-bound.** The bearer token that
`scripts/foundry_env.sh` exports authenticates against both the internal Conjure
APIs and the internal GraphQL gateway. Everything Ferro currently does by
clicking, except the mutations, can run as `curl`.

This works only with one non-obvious header.

### `Fetch-User-Agent` selects the GraphQL schema

`/graphql-gateway/api/bulk` federates its schema per calling application. Without
an app-identifying `Fetch-User-Agent`, `Query.globalProposal` does not exist:

```
Validation error (FieldUndefined@[globalProposal]) : Field 'globalProposal' in type 'Query' is undefined
```

A/B tested against the same token, same body, same endpoint:

| `Fetch-User-Agent` | Result |
|---|---|
| `developer-branching/6.533.2 forge-graphql-client/0.0.0` | **200, data returned** |
| `Palantir-Asset-Track: default` only | 200, `FieldUndefined` |
| omitted | 200, `FieldUndefined` |

The gateway returns HTTP 200 with a GraphQL validation error either way, so a
naive client reports success while getting nothing. Always check for `errors` in
the payload.

This explains the standing "developer-branching and proposal endpoints 404 on
this enrollment" note: public REST v2 genuinely lacks them, but the internal API
the UI uses is reachable with the same credential.

## Transport

### GraphQL gateway

```
POST https://{FH}/graphql-gateway/api/bulk?q={OperationName}
```

Headers (names only; never record values):

| Header | Value | Required |
|---|---|---|
| `Authorization` | `Bearer <token>` | yes |
| `Content-Type` | `application/json` | yes |
| `accept` | `text/event-stream` | yes |
| `Fetch-User-Agent` | `developer-branching/6.533.2 forge-graphql-client/0.0.0` | **yes — see above** |
| `Palantir-Asset-Track` | `default` | no |

Body envelope. `operations` maps a hash to query text; `requests` binds that hash
to an operation name and its variables. Multiple operations ride one POST, and
`?q=` lists their names comma-separated.

```json
{
  "operations": { "0": "query ProposalStateQuery($proposalRid: RID!) { ... }" },
  "requests": [
    { "hash": "0", "name": "ProposalStateQuery",
      "variables": { "proposalRid": "ri.branch..proposal.<uuid>" } }
  ]
}
```

Response is `text/event-stream`: one `data:` line per operation, each a complete
JSON object carrying `extensions.requestIndex`. Parse line-wise, not as one JSON
document.

### Conjure services

```
GET https://{FH}/approvals/api/...
GET https://{FH}/compass/api/...
GET https://{FH}/multipass/api/...
```

Headers: `Authorization: Bearer <token>`, `accept: application/json`, and
`Fetch-User-Agent: change-management-app/6.533.2 conjure-typescript-runtime/2.20.0`.
These accept a plain bearer token and do not need the GraphQL app UA.

## Action 1 — Read proposal state, approvals task, per-resource merge status

### 1a. Proposal state — VERIFIED

Operation `ProposalStateQuery` (my minimal form of the app's
`ProposalHeaderWithDeployabilityQuery`).

| Variable | Type | Meaning |
|---|---|---|
| `proposalRid` | `RID!` | `ri.branch..proposal.<uuid>` |

```graphql
query ProposalStateQuery($proposalRid: RID!) {
  globalProposal(rid: $proposalRid) @optional {
    rid name status deployability
    deployabilityErrors { __typename }
    activeDeployment { id progress _id __typename }
    lastDeployment {
      id progress
      started { time user { username displayName __typename } __typename }
      taskCounts: tasks(pageSize: 1) { totalNumberOfTasks numberOfSucceededTasks __typename }
      _id __typename
    }
    branch {
      rid name status datasetBranchName
      ontologyBranchV2 { rid _id __typename }
      _id __typename
    }
    _id __typename
  }
  __typename
}
```

Signals:

- `status` — `OPEN` / `CLOSED`.
- `deployability` — `DEPLOYABLE` / `NOT_DEPLOYABLE`. Preconditions only; a
  `DEPLOYABLE` proposal can still fail to deploy.
- `activeDeployment` — non-null means a merge is in flight.
- `lastDeployment.id` — the `deploymentId` required by 1c.
- `lastDeployment.progress` — `FAILED` / `SUCCEEDED` / running.

Replayed live: returns `status: OPEN`, `deployability: DEPLOYABLE`,
`lastDeployment.id: 82045f7b-1287-4c22-a5d4-99c35b09027b`, `progress: FAILED`.

```bash
python3 scripts/foundry_browser_client.py proposal ri.branch..proposal.<uuid>
```

### 1b. Approvals task — VERIFIED

```
GET /approvals/api/task-requests/{taskRid}
```

`{taskRid}` is the `ri.ontology..proposal.*` RID from 1c, not the branch proposal
RID. Response fields that matter:

| Field | Meaning |
|---|---|
| `status` | `APPROVED` / `CLOSED` / … |
| `invocationBlockers[]` | **The answer.** `[]` = no blocker. `["REQUEST_IS_CLOSED"]` observed on a closed task. |
| `taskType` | `ontology-metadata:approvals-v2` |
| `taskRequestRid` | `ri.approvals.main.request.<uuid>` |
| `subtasks[].approvalStatus` | per object type |
| `subtasks[].resolvedPolicies[].policyApprovalRequirementsMet` | bool |
| `subtasks[].checkpointsValidation.passesValidation` | bool |
| `history[].type` | `creationEntry`, `closedEntry`, … |
| `customIndexedData["branch-service:branchRid"]` | back-pointer to the global branch |

Sub-paths `/invokability`, `/invocation-blockers`, `/policies`, `/reviewers` all
404. This single GET is the whole surface.

```bash
python3 scripts/foundry_browser_client.py approval ri.ontology..proposal.<uuid>
```

### 1c. Per-resource merge status and the ontology task RID — VERIFIED

Operation `DeploymentTaskListQuery`.

| Variable | Type | Meaning |
|---|---|---|
| `proposalRid` | `RID!` | branch proposal |
| `deploymentId` | `String!` | `lastDeployment.id` from 1a — a bare UUID, not a RID |
| `pageToken` | `String` | optional; app uses `pageSize: 100` |

Full query text is in `scripts/foundry_browser_client.py` as
`DEPLOYMENT_TASKS_QUERY`. Response paths:

```
data.globalProposal.deployment.tasks.values[]
  .progress.__typename                                    -> ..._Failed / ..._Succeeded
  .details.branchedResourceV1.resourceDeploymentProgress  -> FAILED
  .details.branchedResourceV1.progress.failedMessage      -> the real error string
  .details.branchedResourceV1.deployTasks[].displayName   -> "Deploying changes made to the ontology"
  .details.branchedResourceV1.branchResource.ontologyBranch.rid
  .details.branchedResourceV1.branchResource.ontologyBranch.changeProposal.rid  -> ontology task RID for 1b
```

Replayed live, output verbatim:

```
task 80ba56ae-21b6-44bb-9f0b-c1c22a06866d GlobalProposalDeploymentTaskProgress_Failed
  resource     : ri.ontology.main.ontology.cfb1478a-5b0e-466a-aaff-b212870e8861
  progress     : FAILED
  failedMessage: RemoteException: CUSTOM_SERVER (Approvals:TaskRequestInvokeFailed) with instance ID 8f091547-12cb-4622-83ce-a03724375f80: {errorName=ApprovalsClient:TaskIsNotInvokable, taskRid=ri.ontology..proposal.93d8a985-b48b-453c-ad76-39e7e09ce9e2}
  ontologyBranch: ri.ontology.main.branch.50ac81c8-d506-49b3-a5af-a932aabf012c
  changeProposal: ri.ontology..proposal.93d8a985-b48b-453c-ad76-39e7e09ce9e2
```

Note: `rid` is undefined on the `GlobalBranchResource` interface. It must be
selected inside `... on GlobalBranchResource_Ontology`. Selecting it on the
interface fails validation.

### 1d. Per-resource list item — OBSERVED

Operation `ProposedBranchResourceListItemQuery`, variables `proposalRid: RID!`,
`resourceRid: RID!`. Backs each row of the "Resources on branch" table and
carries reviewers, checks, and `OntologyProposedResourceDeployabilityV2Fragment`.
Captured from live traffic; not replayed.

### 1e. Deployment history — OBSERVED

Operation `ProposalDeploymentHistoryQuery`, variable `proposalRid: RID!`. Backs
the "Merge history" tab at route
`/workspace/developer-branching/proposal/{proposalRid}/deployment-history`.
Status vocabulary from the bundle: `Merged`, `Failed`, `Aborted`, `Incomplete`,
`Merging...`.

## Action 2 — Read deploy/index status of object types on a branch

**PARTIAL.** Operation `ObjectTypeBackingDatasourceQuery` — OBSERVED.

| Variable | Type |
|---|---|
| `globalBranchRid` | `RID!` |
| `objectTypeRid` | `RID!` |
| `pageSize` | `Int!` |

Returns `globalBranch.name` and `globalBranch.modifiedResources.values[]`.
Observed response:

```json
{"globalBranch":{"name":"w1-legal-geo",
 "modifiedResources":{"values":[{"__typename":"GlobalBranchResource_Ontology"}]}}}
```

The created/updated object type inventory comes back inside 1c under
`branchResource.ontologyBranch`, as `createdObjectTypes[]`, `updatedObjectTypes[]`,
`deletedObjectTypes[]`, and the same for link types, action types, shared
properties, interfaces, type groups and rule sets. Each entry carries
`latest.objectTypeApiName`, `displayName`, `objectType.id`, and
`status.__typename` (e.g. `ObjectTypeStatus_Experimental`).

**The per-type index status shown in the UI as "Indexed 26 minutes ago" was NOT
isolated to a call.** It renders from a query I did not capture. To get it,
follow the capture procedure below on the proposal Overview tab and filter for an
operation whose response contains an indexing timestamp.

## Action 3 — Merge a proposal — MAPPED, NOT INVOKED

Read verbatim from the app JS bundle. **Not executed.** Connor's lane is
read-only.

```
POST /graphql-gateway/api/bulk?q=DeployProposalMutation
```

```graphql
mutation DeployProposalMutation($proposalRid: RID!, $branchRid: RID!, $option: GlobalBranchDeploymentParameterOption) {
  deployGlobalProposalV3(proposalRid: $proposalRid, branchRid: $branchRid, option: $option) {
    ... on GlobalProposalDeployResult_FailedV2 { deployError: error }
    ... on GlobalProposalDeployResult_Success {
      deployment { proposal { status activeDeployment { _id } _id } _id }
    }
  }
}
```

| Variable | Type | Source |
|---|---|---|
| `proposalRid` | `RID!` | the branch proposal |
| `branchRid` | `RID!` | `branch.rid` from 1a — `ri.branch..branch.6a1b45b5-…` |
| `option` | `GlobalBranchDeploymentParameterOption` | optional; enum members not captured |

Success/failure signals:

- Success arm `GlobalProposalDeployResult_Success` → `deployment.proposal.activeDeployment` non-null.
- Failure arm `GlobalProposalDeployResult_FailedV2` → `deployError`.
- **This mutation returning Success does not mean the merge worked.** It means the
  deployment started. The deployment then fails asynchronously, and that failure
  is only visible via 1c. This is precisely the trap that produced four
  misdiagnosed attempts.
- Live progress: `subscription DeploymentTaskListSubscription($proposalRid: RID!)`
  over `globalProposalUpdated`. Captured from the bundle; not exercised.

Recorded inert in the client as `MERGE_MUTATION`, deliberately not wired to a
function.

## Action 4 — Close/abandon a proposal — MAPPED, NOT INVOKED

```graphql
mutation CloseProposalMutation($proposalRid: RID!) {
  closeGlobalProposal(proposalRid: $proposalRid) { _id status }
}
```

Success signal: `status` transitions to `CLOSED`. Confirmed indirectly — the
superseded proposal `c20a7e44` reads `status: CLOSED`, and its approvals task
reads `invocationBlockers: ["REQUEST_IS_CLOSED"]`. Closing a proposal closes its
ontology approvals task.

Related, also MAPPED, NOT INVOKED:

```graphql
mutation UpdateProposalNameMutation($proposalRid: RID!, $name: String!) { ... }
mutation BranchResourceListItemPublishDraftApprovalRequestMutation($rid: RID!) {
  publishDraftApprovalRequest(taskRid: $rid) { status invokeWhenReady _id }
}
```

`publishDraftApprovalRequest` takes the ontology task RID and returns `status`
and `invokeWhenReady`. It is the only observed call that writes to the approvals
task. If a future failure shows `draft: true` or `invokeWhenReady: false` as a
blocker, this is the lever. Current task reads `draft: false`, so it is not
indicated now.

## Action 5 — Data-health check state and check reports — NOT OBTAINED

I could not reach this surface. Recorded honestly rather than guessed.

Probed with the bearer token, all **404**:

```
/data-health/api/checks/dataset/{datasetRid}
/data-health/api/v1/checks/{datasetRid}
/data-health/api/checks?resourceRid={datasetRid}
/foundry-data-health/api/checks/{datasetRid}
/data-health/api/check-groups/{datasetRid}
```

Already known 404: `/api/v2/datasets/{rid}/checks`.
Already known working: `/api/v2/datasets/{rid}/getSchema?branchName=…&preview=true`.

The service prefix is wrong, not the credential. To find it, open a dataset's
Health tab in the browser and run the capture procedure below.

## Action 6 — Workshop module surfaces — NOT OBTAINED

Not visited. No Workshop module exists for Wedge 1 yet, so there was no
read-only surface to observe. Deferred, as the task marks it lower priority.

## Capture procedure

Reusable method for the surfaces above that are NOT OBTAINED. This is how every
VERIFIED mapping here was produced.

The skill's `har_capture.py` launches its own browser and lands on a login page,
so it is not usable against an authenticated Foundry session. `har_capture_cdp.py`
needs a CDP endpoint, and the configured cloud browser provider exposes none.
The working method is an in-page interceptor via the extension-backed browser
tools, which attach to the already-authenticated Chrome profile.

**Step 1.** Navigate to the surface. Wait for load.

**Step 2.** Install the interceptor. It redacts credential-bearing headers by
name, so the buffer is safe to read.

```javascript
window.__cap = [];
const of = window.fetch;
window.fetch = async function(input, init) {
  const url = (typeof input === 'string') ? input : input.url;
  const res = await of.apply(this, arguments);
  try {
    if (/\/api\/|graphql/i.test(url)) {
      const h = {};
      const src = (init && init.headers) || {};
      Object.keys(src).forEach(k =>
        h[k] = /auth|cookie|token|csrf/i.test(k) ? '<REDACTED>' : src[k]);
      window.__cap.push({
        url, method: (init && init.method) || 'GET', status: res.status,
        reqHeaders: h, reqBody: init && init.body ? String(init.body) : null,
        body: await res.clone().text()
      });
    }
  } catch (e) {}
  return res;
};
'installed';
```

**Step 3.** Force a refetch. A full reload wipes the interceptor, and SPA
navigation back to the same route is served from cache. Navigate to a *different*
entity so the client must refetch:

```javascript
window.__cap.length = 0;
history.pushState({}, '', '/workspace/developer-branching/proposal/<OTHER_RID>/deployment-history');
window.dispatchEvent(new PopStateEvent('popstate', { state: {} }));
```

**Step 4.** Read the buffer.

```javascript
JSON.stringify((window.__cap || []).map(e => ({
  url: e.url.slice(0, 160), status: e.status, len: (e.body || '').length
})), null, 1);
```

**Step 5.** Grep bodies for the string the UI showed, to find which call carries
it:

```javascript
(window.__cap || []).filter(e => /YOUR_SEARCH_STRING/.test(e.body || ''))
  .map(e => e.url);
```

**Step 6.** For mutations, do not fire them. Read the shape from the bundle:

```javascript
(async () => {
  const js = performance.getEntriesByType('resource')
    .map(e => e.name).filter(u => /\.js(\?|$)/.test(u));
  for (const u of js) {
    const t = await (await fetch(u)).text();
    const i = t.indexOf('mutation YourMutationName');
    if (i >= 0) return t.slice(i, i + 900);
  }
  return 'not found';
})();
```

**Step 7.** Replay with `curl`, adding `Fetch-User-Agent`. If the response is a
GraphQL validation error, the app UA is wrong or missing.

## Pitfalls

1. **HTTP 200 does not mean success.** The gateway returns 200 with a GraphQL
   `errors` array. Always inspect the parsed payload.
2. **Response is SSE, not JSON.** Split on lines and parse each `data:` prefix.
3. **`Fetch-User-Agent` is load-bearing.** Omit it and half the schema vanishes.
4. **`rid` is not on interfaces.** Select it inside `... on ConcreteType`.
5. **`deploymentId` is a bare UUID**, not a RID.
6. **The ontology task RID changes** whenever a proposal is recreated. Re-derive
   it from 1c; never hardcode.
7. **`deployability: DEPLOYABLE` is a precondition check, not a prediction.** All
   four failures had a deployable proposal.
8. **SPA nav to the same route is cached.** Navigate to a different entity to
   force a refetch.
9. **A merge mutation returning Success is not a merged proposal.** Poll 1c.

## Coverage

| # | Action | Status |
|---|---|---|
| 1a | Read proposal state | VERIFIED |
| 1b | Read approvals task / invokability | VERIFIED |
| 1c | Per-resource merge status + ontology task RID | VERIFIED |
| 1d | Per-resource list item (reviewers, checks) | OBSERVED |
| 1e | Deployment history | OBSERVED |
| 2 | Object types on branch | PARTIAL — inventory VERIFIED via 1c; index status NOT OBTAINED |
| 3 | Merge proposal | MAPPED, NOT INVOKED |
| 4 | Close proposal | MAPPED, NOT INVOKED |
| 5 | Data-health checks | NOT OBTAINED |
| 6 | Workshop | NOT OBTAINED |

No mutating platform action was performed in producing this document.

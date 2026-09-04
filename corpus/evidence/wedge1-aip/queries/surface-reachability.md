# Foundry surface reachability — A-1/A-3 adjudication

Primary evidence: Palantir Foundry documentation searched through the enrollment's documentation MCP.

## A-1 — REST ingestion

### Platform support

Palantir's documentation states:

> Perform scheduled syncs and exports to external systems using REST APIs. If you want to connect to
> external sources to create syncs and export data, **we recommend using Code Repositories to write
> external Python transforms using the REST API.**

Source: `data-integration/connecting-to-data#external-transforms`.

And:

> Use external transforms to configure syncs and exports that require you to call REST APIs. Simply
> import a source in a Python Code Repository and write custom logic to query the API.

Source: `available-connectors/rest-apis#external-transforms-in-code-repositories`.

The external-transforms page gives the decision criteria explicitly:

> External transforms are primarily used ... when an existing Data Connection source type is not
> available; the desired capability is not available for the target source type; [or] the capability
> offered through the Data Connection user interface does not have the desired features.

### Enrollment exposure

The captured Data Connection catalog for this enrollment exposes REST API as *Webhooks · Use in code*
and does not expose Batch syncs, Custom Source, ESRI/ArcGIS/WFS, or `magritte-rest-v2`.

### Required behavior

The source requires two-stage orchestration:

1. `returnIdsOnly=true` to compute the complete sparse ID set;
2. bounded `OBJECTID IN (...)` requests over that set;
3. union and geometry conversion;
4. same-run count parity and build-aborting shape expectations.

`resultOffset` is a no-op on the Puglia server. A simple numeric pager silently repeats the first
1,000 rows.

The legacy `magritte-rest-v2` documentation supports numeric incremental parameters and next-token
loops, but the connector is absent from this enrollment. Its documented patterns do not establish an
ID-list fan-out on the current source.

### Verdict

**A-1 settles on the external Python transform for this ingestion.** The reason is platform and
enrollment evidence, not Ferro's UI difficulty. Palantir recommends exactly this route where a REST
source's required capability is unavailable in the Data Connection UI.

Pipeline Builder remains the preferred downstream shaping surface where its transforms and gates
express the behavior. The code repository's scope is the source-specific fetch orchestration and the
conversion that must run beside it. Any business rule that Pipeline Builder can express does not move
into the fetch code.

## A-3 — deterministic rule authoring

Palantir describes Pipeline Builder as:

> Foundry's primary application for data integration.

Its features include:

> Strict output checks: If the expected output checks are not met, builds are prevented.

And its comparison guidance states:

> Pipeline Builder is Foundry's primary application for fast, flexible, and scalable delivery of data
> pipelines ... [and] define[s] a rigorous release process for production pipelines.

Sources: `pipeline-builder/overview` and
`building-pipelines/considerations-pb-cr#pipeline-builder`.

The current Python transform proves the comparator: inline checks abort the output transaction and
remain versioned with the producing source. It does not prove Pipeline Builder cannot satisfy the same
contract.

### Verdict

**A-3 remains reopened pending the bounded Pipeline Builder probe.** Official documentation supports
the surface and its strict output checks. The remaining question is enrollment/tool/agent reachability,
not platform capability. The probe must derive the graph/config contract through the now-enabled CDP
lane and compare one real rule against the Python transform on versionability, reviewability, lineage,
exactness, and gate behavior.

## AIP Logic authoring

Official documentation describes AIP Logic as a visual no-code interface. It documents branch-safe
editing, inputs, blocks, outputs, debugging, publishing, actions, and Automate integration. It does not
publish an authoring REST API in the search results reviewed here.

That absence does not prove the internal contract does not exist. The Foundry UI necessarily saves a
branchable Logic resource. The correct next step is CDP network/bundle derivation against the existing
`parseFellingOrder` resource, not another long canvas session and not immediate replacement with a
code function.

## Fetch log / limits

- Palantir documentation MCP was live.
- Public docs provide a legacy `magritte-rest-v2` pager but not evidence it is exposed on this
  enrollment.
- Public AIP Logic docs expose no authoring API; a live network-contract probe is still required.

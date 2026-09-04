# First-principles Palantir Ontology grounding

Date: 2026-08-20. This is evidence for `FIRST_PRINCIPLES_DESIGN.md`, not product authority.

## Pages reviewed

### Decision-centric Ontology

- `ontology/overview`
- `ontology/why-ontology`
- `ontology/models`
- `ontology/core-concepts`
- `ontology/applications`
- `architecture-center/ontology-system`
- `ontology/overview-ontology-scenario`

### Design doctrine

- `ontology/ontology-best-practices`
- `ontology/ontology-structural-guidance`
- `ontology/ontology-anti-patterns`

### Objects, properties, links, and edits

- `object-link-types/object-types-overview`
- `object-link-types/create-object-type`
- `object-link-types/properties-overview`
- `object-link-types/edit-only-properties`
- `object-link-types/link-types-overview`
- `object-link-types/create-link-type`
- `object-link-types/mandatory-control-properties`
- `object-edits/overview`
- `object-edits/how-edits-applied`
- `object-edits/user-edit-history`
- `object-edits/materializations`
- `object-indexing/data-restrictions`
- `object-permissioning/multi-datasource-objects`
- `object-backend/overview`

### Actions, functions, and decision lineage

- `action-types/overview`
- `action-types/rules`
- `action-types/parameter-overview`
- `action-types/submission-criteria`
- `action-types/function-actions-overview`
- `action-types/action-log`
- `action-types/permissions`
- `action-types/read-write-authorizations`
- `functions/overview`
- `functions/edits-overview`
- `functions/functions-on-objects`
- `functions/use-functions`
- `functions/media`
- `functions/types-reference`
- `functions/typescript-v2-ontology-edits`

### Interfaces

- `interfaces/interface-overview`
- `interfaces/implement-interface`
- `interfaces/interface-link-types-overview`
- `interfaces/interface-action-type-constraints`
- `action-types/actions-on-interfaces`

### Security

- `object-permissioning/overview`
- `object-permissioning/managing-object-security`
- `object-permissioning/ontology-permissions`
- `object-permissioning/object-security-policies`
- `security/classification-based-access-controls`
- `security/restricted-views`

### Change governance and applications

- `ontologies/branching-ontology`
- `ontologies/review-ontology-proposals`
- `global-branching/overview`
- `global-branching/core-concepts`
- `global-branching/resource-protection-and-approval-policies`
- `ontology-sdk/overview`

All pages were retrieved from Palantir's public site or full Foundry documentation loader. Browser Use failed because the configured cloud provider exposed no CDP endpoint; it was not needed. Direct extraction rate limits were recovered through the documentation loader. No product fact comes from model memory.

## Binding design implications

1. **The Ontology is a decision system.** It joins data, logic, action, and security and captures decision lineage. A semantic catalog without operational actions is incomplete.
2. **Objects are real entities or events.** A source file, API response, campaign table, or department view is not automatically an object type.
3. **Separate identity from observation.** Measurements, assessments, assertions, results, and change events are linked to enduring entities rather than flattened onto them.
4. **Store each fact once.** Derived properties can expose linked state. High-scale denormalization is an explicit performance tradeoff with an update strategy, not the default.
5. **Use structs only for one multi-field value.** Structs cannot nest and fields cannot be arrays. Independent identity, actions, links, security, or lifecycle require an object.
6. **Links are bidirectional real relationships.** Do not create reverse duplicate links. If the relationship carries dates, role, status, allocation, source, or confidence, use an object-backed link.
7. **Use one enduring object plus linked changes/history.** Full copied versions are the Time Machine anti-pattern. Assessments and change events remain valid objects because each is a distinct event, not a duplicate entity.
8. **Actions are cohesive business operations.** They bundle changes and side effects, validate through submission criteria, and centralize write logic across applications. Single-property CRUD actions are Action Sprawl.
9. **Action Logs are decision objects.** One log type is generated per enabled action type and links the submission to edited objects, actor, action version, parameters, and context. Edit history is for all edits; Action Logs are for decisions.
10. **Functions serve complex live logic.** Pipelines serve automated batch/stream processing; automations serve event reactions; actions serve human/agent decisions. This avoids the Golden Hammer.
11. **Edit functions stay behind Actions.** Read functions can supply Workshop variables/columns; Ontology edits return through function-backed Actions and declared edit provenance.
12. **Interfaces are abstract contracts, not objects.** They can define properties and link/action constraints and support multiple inheritance. Concrete object types remain datasource-backed and instantiable.
13. **Interface support is incomplete.** Interfaces are not currently supported in Workshop. Action constraints are beta, not invocable from Foundry applications or OSDK, do not enforce concrete action semantics, and cannot be mapped through Pipeline Builder. The design may scaffold interfaces but cannot rely on them for the initial Workshop workflow.
14. **Security is semantic.** Combine row and column policies; align boundaries to portfolio, authority, and purpose. Do not duplicate public/private object types. Object/property policy does not automatically secure a referenced media item.
15. **Action authorization is separate from visibility.** Submission criteria encode current-user, parameter, and execution-context conditions. Avoid negative membership tests because scoped tokens may omit the tested attribute and pass unintentionally.
16. **Branches isolate builder changes.** Global Branching supports end-to-end changes across supported applications. Ontology proposals are the review/approval mechanism before main.
17. **Objects require stable primary keys.** Date/timestamp and numeric types are discouraged for identity; strings are the safe default. Arrays cannot contain nulls. `Geopoint` and `Geoshape` are distinct property types.
18. **Source-backed and operator-authored state are distinct.** Indexed datasources provide source state; edit-only properties/Action-created objects provide operational decision data. Conflict semantics must be explicit where both can affect one object.
19. **Materializations expose latest combined source+edit state.** They are optional in Object Storage v2 and are not an automatic historical archive.
20. **Application choice follows workflow.** Object Views provide object hubs; Object Explorer provides walk-up discovery/analysis; Map provides geospatial exploration; Quiver provides analysis; Workshop provides a configured on-rails operational application; OSDK/custom UI adds maintenance and is justified only by a proven native-surface gap.
21. **TypeScript v2 and Python edit functions can persist generated media.** They upload raw bytes to obtain a `Media`, attach it to an Ontology object in declared edits, and persist the bytes when the edits apply. TypeScript examples require OSDK 2.16 or greater; size/memory limits remain explicit.

## Primary URLs

- https://www.palantir.com/docs/foundry/ontology/overview/
- https://www.palantir.com/docs/foundry/ontology/why-ontology/
- https://www.palantir.com/docs/foundry/ontology/core-concepts/
- https://www.palantir.com/docs/foundry/ontology/ontology-best-practices/
- https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance/
- https://www.palantir.com/docs/foundry/ontology/ontology-anti-patterns/
- https://www.palantir.com/docs/foundry/ontology/applications/
- https://www.palantir.com/docs/foundry/object-link-types/object-types-overview/
- https://www.palantir.com/docs/foundry/object-link-types/properties-overview/
- https://www.palantir.com/docs/foundry/object-link-types/link-types-overview/
- https://www.palantir.com/docs/foundry/action-types/overview/
- https://www.palantir.com/docs/foundry/action-types/submission-criteria/
- https://www.palantir.com/docs/foundry/action-types/action-log/
- https://www.palantir.com/docs/foundry/functions/overview/
- https://www.palantir.com/docs/foundry/functions/media/
- https://www.palantir.com/docs/foundry/interfaces/interface-overview/
- https://www.palantir.com/docs/foundry/object-permissioning/overview/
- https://www.palantir.com/docs/foundry/global-branching/overview/

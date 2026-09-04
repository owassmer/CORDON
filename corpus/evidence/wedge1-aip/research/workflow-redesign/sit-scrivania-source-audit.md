# Recursive Puglia SIT and Scrivania source audit

Status: source-universe evidence; not product, interface, or ontology authority  
Date: 21 August 2026

## Bottom line

The official Puglia ArcGIS root currently exposes 194 services across 11 folders. Recursive retrieval succeeded for all 194 service definitions and enumerated 3,724 layers and 105 tables with zero fetch failures.[1]

This corrects the research method, not the top-level product scope. The prior repository had already identified the main Xylella services under `Operationals`, `Operationals2`, and `Operationals3`. The recursive audit adds a reproducible denominator and exposes several adjacent administrative sources that can change a real operator decision.

The operator-relevant sources fall into four classes:

1. **Core official Xylella operational state:** monitoring, infected plants, diagnostic-document links, cadastral references, delimited-zone labels, and plant-specific buffers.
2. **Land authority and lawful-control facts:** civic-use land, state land, protected areas, and the authority responsible for a proceeding.
3. **Field-readiness proceedings:** water derivations, landscape authorization, forest-cut authorization, planting communication, plant movement, and RUOP services.
4. **Context only:** basemaps, imagery, environmental indicators, and unrelated regional layers that cannot themselves determine a Wedge 1 duty, eligibility result, application exception, dispatch decision, or payment outcome.

## Method and complete denominator

1. Fetch the official ArcGIS root `f=pjson` response.[1]
2. Enumerate every listed folder.
3. Enumerate every service and service type in every folder.
4. Fetch each service definition independently.
5. Extract every layer and table name.
6. Run a deliberately broad name/description classifier.
7. Manually inspect plausible decision-changing candidates.
8. Query `where=1=1&returnCountOnly=true` and one live record from selected leaf layers.

Artifacts:

- `sit-services-inventory.json`: 194 current service endpoints.
- `sit-service-metadata-inventory.json`: all 194 definitions, 3,724 layers, 105 tables.
- `sit-layer-workflow-candidates.json`: broad candidate set; intentionally over-inclusive.
- `sit-selected-layer-probes.json`: counts and field schemas for 61 selected layers.
- `scrivania-service-inventory.json`: 186 public digital-service entries parsed from Scrivania.

The broad classifier identifies 116 candidate service endpoints. That is not a scope count. It includes duplicated MapServer/FeatureServer endpoints, group layers, historical versions, contextual indicators, basemaps, and false-positive name matches.

## Core Xylella operational source added to the explicit register

### `Operationals2/PuntiStampa`

`PuntiStampa` publishes separate monitoring-derived layers by campaign and subspecies. For 2024–2026 it separates *pauca*, *fastidiosa*, and *multiplex*. For each, it exposes infected-plant layers plus 50-metre and 100-metre buffers.[2]

The infected-plant records carry more operational assembly than a simple positive-point layer:

- result and symptom state;
- laboratory and field team;
- host species;
- coordinates and comune;
- sample identifier and date;
- official confirmation protocol and document link;
- cadastral comune, section, sheet, and parcel;
- delimited-zone label;
- validation state;
- PPTR, PAI, hydrogeological, owner-choice, and monumental-review fields where populated.

Live counts at retrieval time include:

| Campaign/subspecies | Infected-plant records | 50 m buffers | 100 m buffers |
|---|---:|---:|---:|
| 2026 multiplex | 10 | 6 | 6 |
| 2026 fastidiosa | 13 | 5 | 4 |
| 2026 pauca | 171 | 38 | 21 |
| 2025 multiplex | 36 | 17 | 12 |
| 2025 fastidiosa | 20 | 19 | 8 |
| 2025 pauca | 340 | 43 | 31 |
| 2024 multiplex | 617 | 299 | 177 |
| 2024 fastidiosa | 339 | 93 | 26 |
| 2024 pauca | 86 | 27 | 24 |

These counts are live operational observations, not stable legal counts. A plant point or generated buffer does not itself create a demarcated area, removal duty, or completed order. The governing act and competent-authority decision remain necessary.

**Workflow effect:** Land gains a high-value discovery and reconciliation source. It can identify a likely member/parcel case and the official diagnostic document. It must still distinguish observation, officially confirmed finding, demarcation, order, and legal duty.

## Decision-changing adjacent sources

### Water derivations and served areas

`ConsultaIdricoDerivazioni` is not only irrigation geography. Its layers describe administrative requests and issued water rights by underground or surface source.[3]

The live fields include:

- request and derivation identifiers;
- intended use;
- competent authority;
- request type and proceeding state;
- average and maximum flow;
- annual volume;
- depth;
- served-area geometry.

One underground-served-area layer contains 214,139 records; the surface-attainment served-area layer contains 12,865 records.[3]

**Workflow effect:** Field Work must not equate “inside an irrigation district” with “lawful and operational water available.” The relevant questions are whether a valid derivation or service right exists, which authority controls it, what use/volume it permits, and whether actual delivery is available. The source can prefill and route the exception; it cannot prove current physical supply by itself.

### Landscape authorization and competent authority

The issued-authorization service exposes 27,663 PUTT-era records and 42,653 PPTR records. Fields include practice number, decision date, intervention, authorization type, outcome, responsible official, and competent administration.[4]

The companion complete/denial service exposes 28,128 PUTT-era records and 43,270 PPTR records, adding applicant identity and denied outcomes.[5]

Scrivania also exposes:

- delegated landscape-authority lookup;
- transmission of decisions by delegated entities;
- published PUTT and PPTR decisions;
- a landscape-application service that accepts documents and returns the final decision.[11]

**Workflow effect:** Applications and Field Work require an authority-routing step. The competent decision maker can be Regione Puglia, a delegated municipality/entity, the Soprintendenza, or another body according to the proceeding. A generic “waiting for Regione” state is unsafe.

### Protected areas and habitat

The official protected-area service contains 40 national/regional protected areas, 120 SIC/ZPS areas, three Ramsar areas, and 12 IBA areas.[6]

**Workflow effect:** Overlap is an early warning, not a final permit verdict. It can trigger Natura 2000/VIncA or protected-area review and identify another authority handoff. The applicable project, act, and procedure still determine the actual requirement.

### Civic-use land

The principal civic-use layer contains 23,781 parcel records with cadastral identity, legal-state fields, documentary references, and land-use descriptions.[7] The later recognition service covers 258 comuni and 13,567 parcel-level recognition results.[8]

**Workflow effect:** cadastral ownership or possession does not alone prove authority to change use, accept a cooperative mandate, or perform funded work. Land must expose the civic-use issue and route it to the competent legal/administrative owner before application or dispatch.

### State land and public-land responsibility

The state-domain service includes six reclamation-consortium areas, 25 regional concessions crossing state property, 16,220 state-owned land records, and 165 state-owned buildings.[9]

State-land records include cadastral identity, title/right, holder, property quality, and parcel geometry. The sample population includes olive land.[9]

**Workflow effect:** the responsible actor can be a public body, concessionaire, consortium, or other holder rather than an ordinary private owner/member. This changes notice, authority, execution route, contracting, and eligibility evidence. It does not create a new top-level product function.

### Forest-cut proceedings

The forest-cut consultation service exposes case identifiers, request state, territorial office, official decision protocol, outcome, and intervention geometry. The four selected layers contain 87 point-edited tree cases, zero coordinate-entered tree cases, 70 polygon cases, and 2,766 cadastral-reference cases.[10]

**Workflow effect:** where a Xylella or restoration project touches a legally forested complex, Field Work may require a separate forest-cut proceeding. The source provides status and decision evidence. It should not be applied to ordinary olive parcels merely because trees are present.

## Scrivania operational handoffs

Scrivania’s live public catalog contains 186 service entries. Relevant entries include:[11]

- current and historical Xylella monitoring consultation;
- DGR 1780/2019 parcel-level removal/planting records;
- removal acts;
- Leccino/FS17 planting communications;
- movement communications and inspection requests for specified plants;
- RUOP registration;
- water-derivation proceedings;
- delegated landscape-authority and decision services;
- landscape applications.

**Workflow effect:** Field Work does not always end at physical installation. When the governing rule requires it, planting or plant-movement communication is a downstream operational handoff and later payment/compliance evidence.

## Sources that do not expand Wedge 1 by default

The recursive catalog contains many potentially interesting layers that do not currently justify another Wedge 1 decision or function:

- historical orthophotos and terrain renderings;
- generic environmental indicators;
- sport, tourism, transport, broadband, mining, waste, air-quality, and renewable-energy layers;
- unrelated municipal planning layers;
- duplicated editing/consultation services;
- prior PPTR versions that do not govern the parcel/date being assessed;
- context layers whose presence does not create a legal predicate.

They remain discoverable sources. They enter the operator workflow only when a verified rule, permit, application, field-readiness dependency, control, or customer fact makes them consequential.

## Unknowns and non-inferences

This audit does not establish:

- that every ArcGIS field is complete or current;
- that a GIS record is the governing legal act;
- that a point/buffer creates legal geography;
- that a water right guarantees delivered water;
- that protected-area overlap automatically requires or refuses a permit;
- that civic-use or state-land records alone settle present authority;
- that landscape or forest records cover every competent authority or non-public proceeding;
- that all relevant non-GIS registers have been enumerated.

These remain source-reconciliation and workflow questions.

## Operator-surface consequence

The source expansion supports the existing five responsibilities. It adds sharper exception routing and handoffs:

```text
Land
→ resolve official act, operational GIS, responsible actor, public/civic land, and conflicting source state

Funding
→ evaluate only after land authority and programme-specific geography are resolved

Applications
→ route farm-file, water, landscape, protected-area, civic-use, forest, and authority exceptions to the actor who can decide them

Field Work
→ dispatch only after permits, lawful water, plant traceability, responsible actor, and evidence requirements are ready

Payments
→ consume planting/movement, permit, execution, and acceptance evidence when the award requires it
```

This does not authorize ontology design or interface selection. It refines the real decisions and evidence handoffs that those later stages must represent.

## Sources

[1] https://webapps.sit.puglia.it/arcgis/rest/services
[2] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/PuntiStampa/MapServer
[3] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/ConsultaIdricoDerivazioni/MapServer
[4] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/AutorizzazioniPaesaggistiche/MapServer
[5] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/AutorizzazioniPaesaggisticheCompleteDiniego/MapServer
[6] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/AreeProtetteReteNatura2000/MapServer
[7] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/UsiCivici/MapServer
[8] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/UsiCiviciRicognizione/MapServer
[9] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals3/DemanioStato/MapServer
[10] https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/TagliBoschiviConsultazione/MapServer
[11] https://scrivania.regione.puglia.it

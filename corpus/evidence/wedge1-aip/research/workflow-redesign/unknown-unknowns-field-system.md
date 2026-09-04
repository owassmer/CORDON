# Unknown unknowns in the field system around Xylella recovery

Status: workflow evidence. Proposed checks, holds and state labels are unaccepted candidate terminology, not an approved product, interface or Ontology model.

**Research date:** 21 August 2026  
**Scope:** Independent web sweep. This note does not use prior project reports, repository content, or session history. It asks which real-world decisions and handoffs can invalidate or materially change a cooperative operator's Wedge 1 path across **Land, Funding, Applications, Field Work, and Payments**.

## Bottom line

Wedge 1 cannot stop at `parcel → measure → application → work → payment`. The verified field system has at least eight additional gates:

1. **plant-lot legality and reservation;**
2. **water entitlement, serviceability, and quality;**
3. **landscape, monumental-tree, and archaeology handling;**
4. **contractor, authorised operator, input, and weather capacity;**
5. **laboratory and monitoring events that can interrupt an active case;**
6. **establishment evidence, survival risk, and aftercare responsibility;**
7. **member continuity, liquidity, and succession; and**
8. **market/certification obligations that constrain the orchard design and harvest route.**

These are not new product domains. They are exception paths, readiness checks, reservations, and handoffs that determine whether an otherwise eligible application can be executed and paid. Wedge 1 should represent them as **dated evidence and human decisions**, not infer them from a call, a portal entry, or a one-time parcel status.

## Decision filter

A topic enters this note only when it can change one of these outcomes:

- whether a parcel/member can proceed;
- which measure or technical design is feasible;
- which party must act next;
- whether work can start or must pause;
- whether evidence will survive inspection and payment review; or
- whether a cooperative should aggregate, split, defer, or reject a member case.

Interesting science, ecosystem restoration, marketing, and technology are rejected when they do not change one of those decisions.

## Exploratory search map

| Branch searched | Operational question tested | Disposition for Wedge 1 |
|---|---|---|
| Nursery propagation and certification | Can the operator reserve any “resistant” olive plant, or must the exact production site, lot, cultivar, passport, test and movement route qualify? | **Include.** Lot-level legality and availability are execution gates.[1][2] |
| Water rights and actual service | Does a well, hydrant, old contract, or planned drip system prove water availability? | **Include.** Legal entitlement, public-network contract, deliverable capacity, water quality and current service are distinct facts.[3][4][5][6] |
| Landscape, heritage and archaeology | Does Xylella-related simplification remove all landscape and heritage checks? | **Include.** Simplification is conditional; rural assets, possible monumental trees, and chance archaeological finds create separate handoffs.[6][7][8] |
| Contractors, machinery and inputs | Are statutory windows enough, or must capacity and stock be reserved? | **Include.** A 2025 extension was explicitly caused by product shortage, lack of authorised contractors and wind.[13] |
| Waste and wood movement | Is “tree removed” one task? | **Include.** Fronds, roots, leafless timber and potentially valuable monumental wood follow different custody and movement paths.[9][10] |
| Vector control and organic status | Can the operator prescribe a generic treatment? | **Include.** The permissible route varies by crop, label, year, production regime and operator qualification.[12] |
| Laboratory and monitoring events | Is a case stable after application? | **Include.** A report of test result can trigger cadastral identification, a new 50 m set and compulsory action.[14] |
| Orchard establishment and aftercare | Does a paid invoice prove a successful orchard? | **Include.** Official evidence verifies installed surface, density, materials and plant certification; survival/warranty is a separate commercial and agronomic risk.[15][16] |
| Mortality and nursery warranty | Who bears failed establishment? | **Include as an acquisition and contract gate.** No public standard survival warranty was found; one nursery's published terms expressly disclaim establishment liability.[16] |
| Member economics and credit | Does grant eligibility mean the member can finance execution? | **Include at readiness level.** ISMEA guarantees still require a bank channel and merits review; Wedge 1 should refer, not underwrite.[18] |
| Death, land transfer and representation | What happens when the applicant dies or control changes? | **Include.** The regional program has a specific pre-concession succession procedure keyed to the deceased CUAA and successor details.[17] |
| Processing and market obligations | Can any compliant orchard and any mill route preserve the member's target market? | **Include as declared constraints.** Terra d'Otranto DOP constrains varieties, parcel configuration, cultivation, harvest, mill timing and lot size, and a further Union modification request was pending in 2026.[19][26] |
| Frantoio capacity and continuity | Does orchard recovery assume a functioning processor? | **Include as a cooperative capacity check.** The regional plan separately recognises mills and processing cooperatives whose milling activity fell or stopped.[20] |
| Organic and DOP certification | Are these labels merely downstream sales choices? | **Include when already held or targeted.** They change admissible field inputs, records, orchard composition and processing route.[12][19] |
| Climate hazards | Is “irrigation planned” an adequate climate response? | **Include only as a feasibility/hold criterion.** Field-system evidence identifies drought, salinity, heat, market and labor stresses, but no parcel-level official Wedge 1 threshold was located.[5][24] |
| Cross-border and cross-subspecies foci | Do France, Spain or Portugal belong in a Puglia cooperative workflow? | **Watch only.** They matter when they change plant movement, host lists, approved production sites, or official risk rules—not as a generic global dashboard.[21][22] |
| Research-to-official transition | Should new cultivar or management research alter advice immediately? | **Include a formal transition gate.** Research enters Wedge 1 only after a competent authority changes the operative rule or authorised list.[1][23] |
| Unexpected adjacent-host dependency | Can a non-olive host change an olive cooperative case? | **Include when spatially connected.** Official Puglia evidence links infected marginal almonds to vineyard risk and imposes cross-crop decisions around a focus.[25] |
| Carbon, biodiversity, tourism, crafts, blockchain | Could these create value after Xylella? | **Reject for Wedge 1**, except where wood custody or an existing certification creates a present handoff. They do not decide eligibility, execution or payment in the current wedge. |

## Verified novel workflow findings

### 1. Replace “choose cultivar” with a plant-lot qualification and reservation handoff

The 2024 Puglia determination does more than list Leccino, FS17, Lecciana and Leccio del Corno. It requires qualifying plants to carry plant passports issued by authorised professional operators. For plants produced in a demarcated area, the production site must belong to a RUOP-registered operator, pass annual visual inspection, sampling and testing, and meet movement conditions. The determination also warns that long-term durability of resistance/tolerance and productivity is not yet assured.[1] The regional nursery page separately directs RUOP nurseries to request official annual inspection and analysis before commercialisation.[2]

**Workflow change**

- Create a `PlantLotReadiness` check after technical design and before commitment/concession execution.
- Record cultivar, rootstock/propagation form, quantity, nursery operator, RUOP status, production-site location, passport authority, latest official inspection/test date, movement destination, delivery window, reservation expiry, substitution rule and commercial warranty.
- Re-evaluate the lot if the production site's phytosanitary status changes. The authorisation belongs to a rule-and-site context, not permanently to the nursery name.
- Never allow a vendor to substitute a “similar” cultivar without a new eligibility, market and design assessment.

**Handoff:** cooperative operator → agronomist/nursery → phytosanitary evidence reviewer → procurement commitment.

### 2. Split water into four decisions: legal source, contracted service, usable capacity and current quality

The replanting call caps new planting at 300 trees/ha unless water availability is demonstrated.[6] Puglia's 2025 water law treats irrigation, including self-supply, as a concession use. It requires technical information and, for irrigation, interaction with the public irrigation body; concessions remain limited by resource availability.[3] ARIF's service page shows that users in Lecce–Bari Murgia have a separate seasonal irrigation contracting process, while ARIF also manages and maintains networks and measurement points.[4] ARIF monitors groundwater quantity, chemistry and saline intrusion rather than treating every mapped well as an interchangeable supply.[5]

**Workflow change**

A single `has_water = yes` field is unsafe. Add:

1. `legal_source_status`: concession/authorisation, public irrigation contract, or other lawful source;
2. `service_status`: district, delivery point, contract season, current activation and outage/repair status;
3. `design_capacity`: documented flow/volume versus orchard demand and proposed density; and
4. `quality_status`: last relevant quality/salinity evidence and any agronomic restriction.

A well location, an old invoice, a planned drip line or a network polygon is evidence of only one part. The case cannot move to high-density design until all four are resolved.

**Handoff:** member/land technician → water authority or ARIF → agronomist → application designer → field scheduler.

### 3. Add a conditional landscape/heritage/archaeology preflight before work procurement

The replanting call allows a simplified landscape route only under stated conditions, including use of approved resistant/tolerant cultivars and preservation of rural landscape assets such as dry-stone walls, lamie, specchie, trulli, cisterns, wells and rainwater channels. Otherwise, the ordinary landscape-authorisation route applies.[6] Monumentality can exist before final registry inclusion: citizens or organisations can file a georeferenced, cadastral and photographic report, and the technical commission must validate it.[7] A Puglia eradication order also requires contractors/ARIF to notify the Soprintendenza of chance archaeological finds.[8]

**Workflow change**

- Run desktop overlays, but do not use an empty registry hit as a conclusive “no heritage issue.”
- Add a field inspection question for uncatalogued monumental characteristics and rural assets.
- Capture whether the design preserves those assets. If not, route to ordinary authorisation before application/work commitment.
- Put a **stop-work and notify Soprintendenza** instruction in the work order for chance finds.
- Preserve the inspection photos, coordinates and technician declaration as application/payment evidence.

**Handoff:** land reviewer → qualified technician → environmental/landscape authority or Monumental Tree Commission → contractor; contractor → Soprintendenza on chance find.

### 4. Model removal as a custody tree, not one “field work complete” checkbox

ARIF's published procedure separates in-situ destruction of plant parts from leafless wood. Leafless, debranched wood may remain with the owner and move; ARIF recommends covering loads moved from infected to pest-free areas between 1 May and 31 October to avoid passive carriage of adult vectors.[9] Puglia's 2024 wood law creates a further route for valuable olive wood through designated collection, seasoning and pre-processing centres with identification and traceability, but the law requires subsequent Giunta acts to designate centres and managers.[10]

**Workflow change**

A work order needs separate outcomes for:

- vector treatment before removal when required;
- crown/foliage destruction in situ;
- root removal or devitalisation;
- leafless timber ownership and destination;
- seasonal transport protection;
- monumental/high-value wood identity and chain of custody; and
- disposal/transfer receipt.

Do not promise a regional wood-centre destination until a current designated centre and acceptance terms are acquired. The law creates a route, not proof that local operating capacity is available.

**Handoff:** owner/ARIF/contractor → inspector → transporter → authorised destination or retained-owner custody.

### 5. Capacity reservation and weather are legal-delivery dependencies

The 2025 adult-vector deadline was extended after Confagricoltura documented three concrete execution failures: authorised products were unavailable at retailers, authorised contractors were unavailable, and strong winds prevented treatment.[13] The juvenile-vector workflow is also dynamically timed by altitude, climate and monitoring results, and applies across private, public and uncultivated surfaces; public bodies may delegate work to farmers.[11]

**Workflow change**

- Create a cooperative capacity board keyed by work type, municipality, crop, qualification, machine envelope and legal window.
- Require a `slot_reserved` or `member_self_performs_qualified` state, not merely a cost estimate.
- Track product reservation by exact labelled product, quantity and expiry—not generic active ingredient.
- Add weather hold/release events and a rescheduling escalation before the legal deadline.
- Aggregate neighboring parcels only when the same treatment rule, crop, operator qualification and equipment access apply.

**Handoff:** rule monitor → cooperative procurement desk → retailer/contractor → field lead → evidence collector.

### 6. Organic compliance is an executable route, not a disclaimer

DDS 105/2025 distinguishes substances and routes by crop and production regime. It requires the commercial product's label to name the crop and *Philaenus spumarius*, recognises specific organic-compatible routes, and requires qualified product users. It also permits a qualified small farmer to act for another under the cited labor-exchange rule.[12] DDS 121 then shows that even an authorised route can fail for lack of stock or qualified operators.[13]

**Workflow change**

For each member, record crop, certification regime, control body, permitted product/form, label evidence, operator qualification, treatment date, weather, lot/receipt and operation register. A “biological” flag cannot select a treatment by itself. When the official annual list changes, open a new versioned treatment plan rather than overwriting old advice.

**Handoff:** certification-aware agronomist → authorised operator → member/control records → payment evidence.

### 7. A laboratory result is an interrupt event that can supersede an active application

DDS 51/2025 shows an official chain from sampling and a CNR report of test to cadastral identification by InnovaPuglia, delineation of affected parcels, notification and compulsory measures.[14] This means parcel status can change after an application is drafted, after a plant order, or during field work.

**Workflow change**

- Add `MonitoringEvent` and `LabResultEvent` interrupts to every live parcel/member case.
- On a new official positive or changed demarcation: freeze incompatible procurement/work, recompute legal regime and affected ring, preserve sunk commitments, and generate a human review task.
- Separate `sampled`, `laboratory result issued`, `officially confirmed`, `notified`, and `measures executed`. They are different dates and authorities.
- Re-run plant movement, landscape, funding and field-work checks after the interrupt.

**Handoff:** official monitoring/lab source → cooperative case owner → legal/geo review → nursery/contractor cancellation or redesign → member notice.

### 8. “Installed and payable” is not “alive and productive”

The SRD01 execution guideline verifies the newly planted surface, training system, density and material. It requires invoices and varietal/health certification for plants and evidence for new irrigation/support materials; the administration uses an in-situ visit for core installation facts.[15] The retrieved guideline contains no `attecchimento`, `fallanze` or `mortalità` provision. A nursery's published terms illustrate the commercial risk: it guarantees healthy plants of the requested quality/variety but disclaims establishment because soil, irrigation, pruning and planting conditions are outside its control.[16]

**Workflow change**

Create two completion gates:

1. `administrative_establishment_complete`: installed area/density/material and required documents pass; and
2. `biological_establishment_review`: survival count at agreed intervals, cause classification, replacement responsibility, aftercare completion and revised productive forecast.

Wedge 1 should not invent a warranty. It should capture each supplier/contractor's actual terms, acceptance inspection, complaint deadline and replacement promise. It should also assign aftercare—watering, weed/vector control, staking/shelter, pruning/training and mortality survey—before planting.

**Handoff:** nursery/contractor → delivery acceptance → field inspector/payment file → aftercare owner → mortality/replacement decision.

### 9. Grant eligibility and member finance are different gates

ISMEA's ordinary direct guarantee can cover up to 80% of an underlying loan, but it is issued after a merits review and requested through the financing bank.[18] It is not cash automatically attached to a public grant.

**Workflow change**

- Add a pre-commitment member finance check: own contribution, VAT/timing exposure, bridge need, bank relationship, expected disbursement milestones and maximum affordable delay.
- If a gap exists, produce a lender-ready evidence pack and referral; do not make a credit decision.
- Keep cooperative procurement commitments conditional until member financing and any guarantee path are confirmed.
- Surface the risk of members losing a reserved nursery/contractor slot while awaiting finance.

**Handoff:** application cost plan → member consent → bank/ISMEA or other finance provider → procurement release.

### 10. Death and transfer require a first-class case transition

The Puglia replanting program opened a dedicated pre-concession succession procedure. Access required the deceased applicant's CUAA, successor PEC and both parties' details, and the portal had a bounded operating window.[17]

**Workflow change**

- Add case states for deceased/incapacitated/transfer pending, not a generic “beneficiary changed.”
- Freeze signature and payment actions until the successor's legal capacity, land control, CUAA/fascicolo alignment, delegations and program-specific subentry are confirmed.
- Preserve the original case history and create a successor relationship; do not overwrite the applicant.
- Trigger a deadline calendar for the specific subentry window.

**Handoff:** cooperative member services → heirs/successor and CAA → program help desk/authority → application case owner → payment identity check.

### 11. Market obligations can constrain orchard and cooperative aggregation before planting

The Terra d'Otranto DOP specification is not a downstream label-only decision. It requires named cultivars to make up at least 60%, defines the production territory, monitors input/output traceability, requires at least annual pruning and two soil-management operations, sets a one-hectare minimum orchard size, a 15 November harvest deadline, milling within 24 hours, and a minimum 15-quintal milling lot.[19] The MASAF page for Union registration/modification applications also lists a `Terra d'Otranto / Olio del Salento DOP` submission dated 18 June 2026.[26] That listing proves a pending change request, not its approval or operative content.

**Workflow change**

- Ask each member whether DOP participation is current, intended, explicitly rejected or unresolved.
- Validate orchard composition and contiguous land body against the target specification before plant ordering.
- At cooperative level, reserve harvest/mill capacity that can satisfy the 24-hour and minimum-lot constraints.
- Route small members into compliant batch aggregation only if chain of custody and control-body rules permit it.
- Keep DOP compliance separate from public-funding eligibility. One does not prove the other.
- Version the specification used for each design and recheck the 2026 modification status before contracting, planting or marketing. Do not apply a pending proposal as if it were operative.

**Handoff:** member market declaration → agronomist/design → DOP control body → cooperative harvest/mill scheduler → traceability/payment records.

### 12. Processor continuity is a recovery dependency, not an assumed background service

The regional plan separately compensates mills and processing cooperatives in the infected area that reduced or stopped milling after Xylella-related olive losses.[20] That confirms the processing layer can be impaired while orchard recovery is funded.

**Workflow change**

- Before approving a large collective orchard cohort, obtain letters/slots from mills for expected maturity years, separate from immediate planting work.
- Track mill status, compatible certification, minimum lots, geography, storage and harvest-to-mill travel time.
- Use this as a design/aggregation warning, not as a hard rejection while orchards are immature.

**Handoff:** cooperative production plan → mill/cooperative processor → member orchard schedule → market route.

### 13. The biological unit of concern can cross parcel, crop and cooperative boundaries

DDS 22/2025 reports that 98% of infected plants in the Triggiano fastidiosa focus were almond and vine, with infected vines generally at field edges near infected almonds. It records a proposed primary almond-to-vine and secondary vine-to-vine transmission pattern, and it makes abandonment relevant to compensation and recommended action.[25]

**Workflow change**

- Add an adjacent-host survey around a member parcel when an official focus or prescription makes it relevant.
- Capture abandoned/marginal host ownership and the authority/compensation status separately from the applicant orchard.
- Support a cooperative outreach/coordination task to adjacent owners; do not silently include their land in the member application.
- Cross-crop status can change the correct measure and work order even when Wedge 1's customer is an olive cooperative.

**Handoff:** official focus event → spatial/host review → neighboring owner outreach → authority/field-work plan.

### 14. Cross-border information matters only through official rule and supply changes

The European Commission records active Xylella histories in Italy, France, Portugal and Spain and restricts plant movement from demarcated areas.[21] The Commission's 10 November 2025 demarcated-area list contains multiple subspecies and eradication areas, including current Italian municipalities.[22]

**Workflow change**

Maintain a small watch for:

- changes to EU host lists and movement rules;
- changed status of a nursery production site;
- new or closed demarcated areas relevant to the supply route; and
- official risk-assessment updates that authorities cite.

Do **not** build a cross-border outbreak-analysis module in Wedge 1. The trigger is a changed rule, source-site status or procurement route.

### 15. Research must pass an explicit authority transition before it changes operator advice

The 2024 cultivar decision illustrates the correct bridge: the regional service obtained a CNR report, submitted it to the national plant-health service, the national committee evaluated it, and the competent regional authority amended the authorised planting list.[1] EFSA's June 2026 conference says research on resistance, biological control, surveillance and management is maturing, but an updated EU pest risk assessment is still expected by the end of 2026.[23]

**Workflow change**

Use these states for new science:

`research lead → replicated/field evidence → competent authority review → operative act published → Wedge 1 rule versioned`.

Conference results, papers, vendor claims and project deliverables may create a watch item. They must not change eligibility, prescribed treatment, plant procurement or payment evidence until an operative authority does so.

### 16. Long-horizon resilience needs a feasibility reserve, not a broad climate module

A 2025 CIHEAM Bari field-system workshop for Ostuni identifies heatwaves, prolonged drought, water scarcity, groundwater salinisation, high irrigation energy/financial costs, labor shortages, weak market access and unstable buyer relationships as interacting stresses.[24] ARIF's own system monitors saline intrusion and groundwater condition.[5]

**Workflow change**

- Attach a `LongHorizonFeasibility` note to orchard designs: water quality trajectory, backup supply, energy dependency, labor model, compatible machinery and intended buyer/processor.
- Require explicit owner acceptance where an orchard design depends on fragile water, power or labor assumptions.
- Do not calculate an unsourced climate score. Acquire parcel- and design-specific thresholds first.

## Consequences for the five functions

| Function | Required redesign | Minimum state/evidence | Stop or escalation condition |
|---|---|---|---|
| **Land** | Expand the parcel preflight beyond title and zone. Include water source/rights, service point, density feasibility, monumental-tree candidate check, rural assets, access/machine envelope, adjacent official foci and target certification geography. | Dated parcel snapshot; legal regime; water-source evidence; field inspection; photos/coordinates; asset/heritage findings; member market declaration. | Unresolved water legality/capacity; uncatalogued monument candidate; required ordinary authorisation absent; official lab/zone interrupt; no safe machinery access. |
| **Funding** | Separate grant eligibility from total executable finance. Include own contribution, bridge/VAT timing, aftercare, mortality replacement, mandatory vector work, certification/control costs and procurement reservation exposure. | Cost stack by payer and timing; member consent; finance/referral status; non-duplication check; contingency owner. | Member cannot fund timing gap; grant excludes a load-bearing dependency; guarantee/loan not confirmed before non-refundable commitment. |
| **Applications** | Add plant-lot, water, permit, organic/DOP, succession, processor and field-capacity declarations. Generate exception annexes instead of hiding unknowns in notes. | Plant passports/test path; water/concession/contract evidence; landscape/heritage route; CUAA and representation; certifications; target orchard/market design. | Evidence refers to a different lot/site/member/parcel; successor not regularised; official rule changed after dossier freeze; required permit only “planned.” |
| **Field Work** | Convert works into sequenced work packages with reservations, qualifications, weather holds, inspection points, custody routes and stop-work events. | Contractor/operator qualification; booked slot; exact labelled input; pre-treatment; removal component records; delivery acceptance; archaeology instruction; aftercare assignment. | Product/contractor unavailable; wind/other label condition; new official result; chance find; field design differs from approved density/system; plant substitution. |
| **Payments** | Keep administrative completion separate from biological establishment and market performance. Assemble evidence at operation time. | In-situ inspection facts; invoices; health/varietal certification; plant counts; new-material proof; operation register; disposal/wood receipt; correct beneficiary/payment identity. | Count/density mismatch; missing non-substitutable certificate; unapproved variant; payment identity changed; work outside legal window; required evidence collected only retrospectively. |

## Cooperative operating model

### Cohort before dossier

Group members into execution cohorts only after these dimensions match:

- operative legal regime and work window;
- orchard system and plant-lot route;
- water source/service path;
- organic/DOP or other declared constraint;
- contractor and machinery need;
- processor/market route; and
- financing readiness.

A single collective application can still contain several cohorts. The cooperative should not force one technical package across heterogeneous members merely because the funding measure is shared.

### Holds and abstentions

Use explicit holds:

- `HOLD_WATER_EVIDENCE`
- `HOLD_PLANT_LOT`
- `HOLD_HERITAGE_REVIEW`
- `HOLD_SUCCESSION`
- `HOLD_MEMBER_FINANCE`
- `HOLD_CONTRACTOR_OR_INPUT`
- `HOLD_OFFICIAL_EVENT_REVIEW`
- `HOLD_PROCESSOR_OR_MARKET_ROUTE`

A hold is not a negative product output. Each hold names the evidence owner, acquisition route, deadline and next decision.

### Two clocks

Every case must carry two clocks:

1. **administrative clock:** application, subentry, work-completion, payment and appeal deadlines; and
2. **biological/field clock:** planting season, vector stage, wind/weather, irrigation activation, plant delivery viability, harvest and aftercare.

A dossier is executable only when the clocks can be reconciled.

## Unresolved acquisition needs

The web can establish rules and named procedures. It cannot establish current commercial capacity or a member's facts. These are the next acquisitions, ordered by impact.

| Priority | Acquisition | Why it is needed | Positive extraction route / owner |
|---|---|---|---|
| P0 | **Live nursery stock book** | No public source established current quantity, lead time, reservation terms or site-level legal status for each required cultivar. | Cooperative RFQ to RUOP operators; capture production site, passport authority, latest inspection/test, lot, quantity, delivery window, price, substitution and warranty. Revalidate against official nursery/zone notices.[1][2] |
| P0 | **Parcel water service pack** | A right or map does not prove actual delivery, pressure/volume, outage status or salinity. | Member uploads concession/contract and delivery-point ID; cooperative obtains ARIF/irrigation-body confirmation; technician calculates demand; acquire last available quality/quantity evidence.[3][4][5] |
| P0 | **Contractor/input capacity board** | The official record proves shortages occur but gives no current capacity roster or prices. | Cooperative prequalification/RFQ: qualification, crops, machines, slope/access limits, daily capacity, geographic radius, dates, cancellation/weather terms and evidence package. Retailer reservation for exact labelled inputs.[12][13] |
| P0 | **Official event feed and reconciliation procedure** | A new test result can supersede an active case. | Poll official determinations, published reports of test and demarcation updates; record issuance/publication/effective dates; human review before case mutation.[14][21][22] |
| P0 | **Member authority and continuity pack** | Death, co-ownership, lease expiry or transfer can break signature, work access and payment. | Cooperative/CAA collects CUAA/fascicolo status, title/lease duration, co-owner consents, delegation, PEC, succession/transfer documents and program-specific subentry evidence.[17] |
| P1 | **Aftercare and mortality protocol** | Public execution evidence does not allocate biological failure. | Agronomist defines survival survey dates, accepted causes, watering/weed/vector/training tasks and replacement threshold; suppliers/contractors sign explicit warranty/exclusion/complaint terms.[15][16] |
| P1 | **Landscape/heritage field pack** | Registry and overlay negatives do not exclude uncatalogued monumental characteristics or field assets. | Qualified technician field survey with photos, measurements, coordinates, asset map and permit determination; Commission/Soprintendenza handoff where triggered.[6][7][8] |
| P1 | **Organic/control-body compatibility confirmation** | Annual official product routes can change; certification consequences are member-specific. | Obtain member certificate/control body; exact annual act and label; written agronomist/control-body confirmation where ambiguity remains; preserve operation register.[12] |
| P1 | **DOP and mill capacity pack** | DOP feasibility depends on orchard, lots, harvest and mill route; long-run processor capacity is unverified; a 2026 Union modification request is pending. | Member market declaration; current operative specification and control plan; separate pending-change watch; control-body enrollment status; mill letters/slots and compatible lot/traceability plan.[19][20][26] |
| P1 | **Member cash-flow and credit referral pack** | Grant eligibility does not prove bridge capacity. | Member consented cash-flow questionnaire; cost/timing plan; lender-ready dossier; bank/ISMEA referral status. Do not score credit inside Wedge 1.[18] |
| P2 | **Wood destination and implementation register** | The 2024 law requires later designation of centres; this sweep did not verify operating centres or acceptance capacity. | Search Giunta implementation acts; contact designated centres; capture accepted wood class, moisture/dimensions, custody, price/fee and transport rules.[9][10] |
| P2 | **Parcel-specific climate/energy resilience evidence** | Regional stress evidence is real but too coarse for a Wedge 1 verdict. | Agrometeorological series, water-quality trend, pump power/reliability, insurer/technician requirements and design-specific sensitivity; render as evidence/assumption, not a generic score.[5][24] |
| P2 | **Current machinery economics** | Public unit prices and news do not establish private executable offers. | Cooperative RFQ and tender/contract-award sampling; collect mobilization, stump/root method, access limits, disposal, reinstatement and standby charges. |
| P2 | **Land abandonment/adjacent-host outreach map** | Official cross-crop evidence does not identify who can lawfully act on adjacent abandoned hosts. | Official focus geometry + cadastral/authority outreach under lawful access; record owner response, compensation status and intervention authority.[25] |

## Explicitly rejected branches

1. **Breeding, genomics and molecular resistance mechanisms.** Scientifically important, but Wedge 1 changes only when a competent authority publishes an operative cultivar/rule change.[1][23]
2. **Treatment efficacy research and cure claims.** Vendor or paper claims do not define legal eligibility, authorised use or payment evidence. Keep outside the operator workflow until an official act changes it.
3. **A Europe-wide outbreak analytics product.** Cross-border information is a source-site/rule watch, not a Wedge 1 module.[21][22]
4. **Generic climate-risk scoring.** No verified parcel-level threshold was found. Acquire water, salinity, energy and design evidence instead.[5][24]
5. **Full credit underwriting.** Wedge 1 may detect a financing gap and prepare a referral pack. The bank and guarantee institution decide credit.[18]
6. **Consumer marketing, e-commerce and blockchain traceability.** These do not decide the present application. Existing DOP/control obligations do.[19]
7. **Tourism, landscape storytelling and biodiversity restoration design.** Valuable recovery domains, but not current Wedge 1 decisions unless a live permit, certification or funded operation invokes them.
8. **Olive-wood craft marketplace.** Only custody, lawful movement and a verified receiving destination matter to this wedge. Product-market development is separate.[9][10]
9. **Machinery engineering or ownership.** Wedge 1 needs a qualified, booked service that fits the parcel and work window, not a machine-design catalogue.[13]
10. **General cooperative governance reform.** Include member consent, authority, cohorting and shared procurement only. Board structure, bylaw reform and patronage policy are outside the application workflow.
11. **Broad succession and inheritance law.** Include only the evidence and program-specific subentry needed to keep a case valid.[17]
12. **Frantoio modernisation.** Processor availability and certification are dependencies; financing a mill or redesigning processing operations is another wedge.[20]
13. **Unrelated cross-crop disease programs.** Almond/vine facts enter only when an official focus, adjacency or member portfolio changes the olive case.[25]
14. **Heritage digitisation as a standalone product.** Use existing official records plus field escalation. Do not turn monument research into a separate Wedge 1 workflow.[7]

## Failures and limits

### Retrieval failures and recovery

- Crawl4AI successfully extracted the selected HTML/JS pages.
- Crawl4AI returned HTTP 500 for every selected PDF in this sweep. Each PDF was re-fetched with direct `curl`, checked with `file` to confirm real PDF bytes, and extracted with `pdftotext -layout`.
- The MASAF DOP PDF produced only a 60-byte Crawl4AI artifact; direct download returned a real six-page PDF and the text was extracted successfully.
- `pdftotext` emitted formatting warnings on several files, but the cited operative passages were present as readable text. No claim below relies on an unreadable table cell.

### Evidence not found, not evidence of absence

This sweep did **not** establish:

- current nursery inventory or lead times by cultivar/lot;
- a comprehensive contractor/contoterzista roster, capacity or price curve;
- a market-wide mortality or establishment warranty standard;
- live district-by-district irrigation delivery, outages, pressure or member eligibility;
- current designated/operating centres under the 2024 olive-wood law;
- live mill capacity and future slots;
- member-level liquidity, debt, willingness, land-control continuity or cooperative commitment;
- a parcel-level official climate feasibility threshold; or
- the present acceptance practice of each organic or DOP control body.

These are acquisition tasks. They must not be converted into default negatives or guessed values.

## Extraction route and verification record

1. Discovery used Exa through `web_search`, with separate queries for nursery rules, water, heritage, contractors, wood, vector inputs, laboratory events, establishment, finance, succession, processing, DOP/organic, climate, cross-border foci and research transition.
2. Candidate sources were weighted toward Puglia/BURP, ARIF, MASAF, ISMEA, the European Commission and EFSA.
3. HTML/JS sources were extracted with:

   `/Users/owenwassmer/.hermes/hermes-agent/venv/bin/python /tmp/crawl4ai_extract.py --out-dir /tmp/c4a-unknown-field <urls...>`

4. PDFs were attempted with the same Crawl4AI route, then recovered by direct `curl`, validated with `file`, and extracted via `pdftotext -layout`.
5. Operative phrases were re-located in the extracted text before drafting. Search-result snippets were used for discovery, not as the sole support for cited findings.
6. Twenty-six unique cited sources are listed below.

## Sources

[1] Regione Puglia, Determinazione n. 48 del 3 maggio 2024, authorisation under Articles 18 and 23, nursery movement and added cultivars. https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf

[2] Regione Puglia, Emergenza Xylella — Vivai, RUOP and annual official inspection/analysis notice. http://www.sit.puglia.it/portal/portale_gestione_agricoltura/Vivai

[3] Regione Puglia, Legge regionale 30 maggio 2025, n. 7, water uses, research and concessions. https://burp.regione.puglia.it/documents/20135/2577619/LR_07_2025.pdf/be0dd20a-e205-c875-a591-a63dd9b024b5?t=1748625572269&version=1.0

[4] ARIF Puglia, Impianti irrigui and irrigation contracting/management. https://www.arifpuglia.it/attivita/irrigazione/

[5] ARIF Puglia, Monitoraggio corpi idrici sotterranei. https://www.arifpuglia.it/attivita/monitoraggio-corpi-idrici-sotterranei/

[6] Regione Puglia, consolidated call “Reimpianto ulivi in zona infetta,” Article 6 measure. https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182

[7] SIT Puglia, FAQ Ulivi Monumentali. https://pugliacon.regione.puglia.it/web/sit-puglia-sit/domande-frequenti1

[8] Regione Puglia, Determinazione n. 184 of 21 December 2020, eradication procedure and archaeological chance finds. https://burp.regione.puglia.it/documents/20135/1451186/DET_184_21_12_2020.pdf/d7dd7932-aef2-dd28-1247-42bbed82e0cb?t=1623068448309&version=1.0

[9] ARIF Puglia, Abbattimenti e indennizzi. https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/

[10] Regione Puglia, Legge regionale 19 February 2024, n. 8, olive wood from Xylella removals. https://www.capire.org/attivita/clausole_valutative/LR_2024_08_puglia.pdf

[11] Regione Puglia, compulsory 2025 soil work against Xylella vectors. https://press.regione.puglia.it/-/contrasto-alla-xylella-attivo-l-obbligo-delle-lavorazioni-del-terreno

[12] Regione Puglia / Comune di Turi mirror, DDS 105 of 16 June 2025, adult-vector treatments, crop/organic routes and operator requirements. https://www.comune.turi.ba.it/wp-content/uploads/2025/06/181_DIR_2025_00105_DeterminaPUB.pdf

[13] Regione Puglia, DDS 121 of 30 June 2025, extension for vector treatment and stated logistical/technical causes. https://burp.regione.puglia.it/documents/20135/2664200/DET_121_30_6_2025.pdf/1d800793-b83d-61e9-344e-066fe19d07d4?t=1752164029496&version=1.0

[14] Regione Puglia, DDS 51 of 31 March 2025, official laboratory result and eradication procedure. https://burp.regione.puglia.it/documents/20135/2623010/DET_51_31_3_2025.pdf/3789a954-3739-74a7-5fe5-a6861f101369?t=1743693415806&version=1.0

[15] CSR Puglia, DAdG n. 24 of 10 April 2025, correct execution and evidence for SRD01/SRD06. https://csr.regione.puglia.it/documents/20117/74270/Determinazione+Autorit%C3%A0+di+Gestione+n.+24+del+10.04.2025.pdf/34c9714a-4233-f2dc-4db8-136b3db0b704?t=1761555303374&version=1.1

[16] Coplant, published terms and conditions, plant establishment disclaimer. https://www.coplant.it/termini-e-condizioni/

[17] Regione Puglia, pre-concession succession after death for the replanting measure. https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-olivi-in-zona-infetta-modalit%C3%A0-di-presentazione-della-domanda-di-subentro-per-decesso

[18] ISMEA, Garanzie dirette. https://www.ismea.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/12132

[19] MASAF, production specification for Terra d'Otranto DOP. https://www.masaf.gov.it/flex/cm/pages/ServeAttachment.php/L/IT/D/1%252F9%252F8%252FD.a56bd25591ba82c2da99/P/BLOB%3AID%3D3342/E/pdf?mode=download

[20] Regione Puglia, Misura 2.F — compensatory support for olive mills and processing cooperatives. https://www.regione.puglia.it/web/rigenerazione-olivicola/misura-2.f

[21] European Commission, Latest Developments of *Xylella fastidiosa* in the EU territory. https://food.ec.europa.eu/plants/plant-health-and-biosecurity/plant-health-rules/control-measures/xylella-fastidiosa/latest-developments-xylella-fastidiosa-eu-territory_en

[22] European Commission, List of demarcated areas in the Union territory, Update 23, 10 November 2025. https://food.ec.europa.eu/document/download/77ec3d12-c080-4273-b604-5cb5164a4c78_en?filename=ph_biosec_legis_list-demarcated-union-territory_en.pdf

[23] EFSA, 5th European Conference on *Xylella fastidiosa*: science drives progress towards sustainable management, 25 June 2026. https://www.efsa.europa.eu/en/news/5th-european-conference-xylella-fastidiosa-science-drives-progress-towards-sustainable

[24] CIHEAM Bari, *Farming system resilience in the territory of Ostuni*, 2025. https://www.iamb.ciheam.org/wp-content/uploads/2025/07/Farming-system-resilience-in-the-territory-of-Ostuni.pdf

[25] Regione Puglia, DDS 22 of 15 February 2025, fastidiosa focus, cross-crop findings and compensation conditions. https://burp.regione.puglia.it/documents/20135/2603465/DET_22_15_2_2025.pdf/16df0dec-959b-15a4-c3eb-2d841cd29081?t=1741699541625&version=1.0

[26] MASAF, Union registration/modification applications submitted to the European Commission; listing for `Terra d'Otranto / Olio del Salento DOP` dated 18 June 2026. https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/3335

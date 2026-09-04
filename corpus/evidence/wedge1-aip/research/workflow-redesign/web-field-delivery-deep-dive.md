# Puglia Xylella field delivery deep dive

**Research date:** 20 August 2026  
**Scope:** field delivery only. This report separates compulsory phytosanitary work from grant-funded investment. It does not describe software, applications as products, or any prior local research.

## Bottom line

Puglia operates two different field-delivery systems that touch the same parcels but have different legal triggers, decision rights, clocks, evidence and acceptance.

1. **Compulsory phytosanitary delivery** starts with an official finding or a campaign-wide vector-control prescription. For eradication, the official package is assembled by the regional plant-health chain: laboratory result → cadastral and owner resolution by InnovaPuglia → orthophoto and parcel annexes → injunction by the *Osservatorio fitosanitario regionale* (Regional Plant Health Observatory). The owner chooses only **who performs** the ordered removal—owner or ARIF—not whether it occurs. Silence routes the work to ARIF; obstruction can route it to forced access and enforcement. A phytosanitary inspector/agent/assistant identifies the trees, supervises removal and destruction, and signs the indispensable field *verbale* (official record). That record is the operational and indemnity acceptance point.[S2][S3]
2. **Grant-funded investment delivery** starts with a voluntary application and a concession. The field-ready package is normally created by an authorized agricultural technician, not the cooperative or Region: updated *fascicolo aziendale* (farm dossier), EIP digital project, technical report, plan, plant count and spacing, irrigation layout, budget, consents, titles and an attestation of *cantierabilità* (work readiness). The beneficiary procures nurseries and works privately, manages cash flow, and has the project directed/certified by the technician. Legal acceptance comes later through a payment dossier plus administrative and in-situ checks. The project is accepted only to the approved or authorized-variant specification; unsupported quantities or components are cut, and material departures can trigger partial rejection, total revocation or recovery.[S9][S10][S11][S12]
3. **The unresolved operational seam is cooperative and contractor practice.** The legal instruments allow collective applications, mandate resolutions and delegates, and permit a cooperative/producer organization to receive a mandate to execute removals, replanting or grafting. They do not disclose how a cooperative actually aggregates site surveys, tenders contractors, reserves nursery batches, allocates scarce machines or water, schedules crews, approves invoices, manages defects, or divides responsibility for aftercare. No primary field manual or contract template for that cooperative execution layer was located.
4. **Aftercare is a weakly specified handoff.** Calls impose five- or fifteen-year durability/use obligations, preserve inspection access and require records, but the funded work packages reviewed do not provide a detailed establishment-care acceptance protocol (watering frequency, replacement of dead plants, weed control, formative pruning, survival threshold, seasonal inspection). Professional evidence says site suitability, water and agronomic design materially affect outcomes, while a 2025 field report identifies delayed irrigation access as a real threat to young plantings.[S9][S20][S21]

## Terminology

| Italian term | Operational meaning here |
|---|---|
| *Osservatorio fitosanitario regionale* | Regional competent plant-health authority. It directs surveillance, issues demarcation and injunction acts, authorizes or revokes nursery movements, and controls official acceptance. |
| ARIF | *Agenzia Regionale per le Attività Irrigue e Forestali*. Regional delivery/support agency. It supports surveillance, performs or arranges removals, supplies phytosanitary assistants, and instructs/liquidates specified indemnities and grants. |
| *area delimitata* | Demarcated area: infected zone plus buffer zone. It is not synonymous with the broad Salento infected area. |
| *zona infetta* | In eradication, at least 50 m around an infected plant. In the Annex III Salento regime it is a much larger listed infected zone. The applicable article must be determined, not inferred from the label alone.[S1] |
| *zona cuscinetto* | Buffer zone around an infected zone. A positive finding here triggers eradication, not containment. |
| *zona di contenimento* | The strip/part of the Annex III infected zone where containment rules apply. Only infected plants are removed under Article 13; the 50 m ring is sampled/tested.[S1][S2] |
| *estirpazione* | Removal/uprooting. Orders generally require mechanical removal; where full root removal is impossible, the Observatory may authorize branch/foliage destruction plus root devitalization.[S2] |
| *abbattimento coatto* | Forced felling/removal after non-compliance. |
| *provvedimento ingiuntivo / prescrizione* | The binding regional order identifying the legal regime, target plants/parcels/owners, methods and deadlines. |
| *verbale* | Official inspection/supervision record. It is not merely a contractor ticket; for compulsory removal it is indispensable to indemnity recognition.[S3][S4] |
| *DdS* | *Domanda di Sostegno*: grant support application. |
| *DdP* | *Domanda di Pagamento*: payment claim (advance and/or final balance, depending on the call). |
| EIP | *Elaborato Informatico Progettuale*: regional digital project artifact prepared by an authorized agricultural technician. |
| SIAN | National Agricultural Information System used for farm dossiers, grant applications/payment claims and aid records. |
| CAA | Authorized Agricultural Assistance Centre. It can file SIAN forms for the beneficiary. |
| *cantierabilità* | Field/work readiness: required titles and consents exist, or the package identifies what is outstanding. It does **not** prove nursery stock, contractor or water capacity has been reserved. |
| *variante* | Formal change requiring a submitted and approved variant request. |
| *adattamento tecnico/economico* | Minor/detail or improving change that may be documented at final payment rather than approved in advance, where the specific call permits it. |
| RUOP / OP | *Registro Ufficiale degli Operatori Professionali* / professional operator. A nursery/producer must be registered and separately authorized for the plant passport categories and, where relevant, Xylella-zone movement. |
| *passaporto delle piante* | Traceability and phytosanitary movement document. It is evidence about source and movement conditions, not a warranty of field survival. |
| CAC | EU conformity category for fruit propagating material (*Conformitas Agraria Communitatis*). |
| *marza* | Scion used for grafting. |
| *collaudo / accertamento di regolare esecuzione* | Final administrative/field verification that works conform to the concession and admissibility rules. |

# Process map A — compulsory eradication, containment and land management

## A1. Plant-triggered eradication or containment

```text
Official surveillance/sample
  → official laboratory result and subspecies determination
  → locate regime at the finding date
      ├─ eradication area / buffer: Articles 7–11
      └─ Annex III containment part: Articles 12–17
  → InnovaPuglia resolves cadastral parcels, owners, 50 m geometry and orthophoto
  → Observatory drafts and signs injunction with annexes
  → 7-day municipal-albo publication (+ PEC where available; ARIF notified)
  → owner response by publication end + 3 days
      ├─ voluntary owner delivery
      │    → agree execution time with Observatory
      │    → owner selects/engages competent machinery/crew
      ├─ ARIF delivery
      │    → ARIF schedules crew/machinery
      └─ silence
           → ARIF schedules removal
  → access and pre-work controls
      → identify exact plants; monumental/historic check; vector treatment if required
  → removal and destruction under official supervision
      → foliage/branches destroyed; wood de-limbed and left/moved under rules
  → inspector/agent/assistant writes verbale
  → legal completion
      ├─ compliant: close order; verbale enables indemnity claim
      └─ refusal/obstruction/non-start: forced removal, Prefect/police, sanction/referral,
         costs charged and no removal contribution
```

### Trigger and regime decision

The EU rule makes the infected zone at least 50 m around the officially infected plant. Under eradication, the Member State must immediately remove infected plants, symptomatic/suspect plants, the same species regardless of health, certain other infected species, and specified plants not immediately sampled and molecularly tested. Historic/value trees may remain only if officially designated, annually inspected/tested negative and vector-treated.[S1]

This differs from containment. In the listed Annex III infected zone, Article 13 removes **infected plants**, immediately or before the next vector flight season if found outside flight season. Article 15 then samples/tests specified and suspect plants within 50 m. A “positive in containment” therefore does not create the same blanket removal set as Article 7.[S1]

The 2026 Bitonto order shows the operative fork. The Observatory states that Bitonto is under eradication, attaches an orthophoto and an Annex 1/B listing the positive plant and every intersecting cadastral parcel/owner in 50 m, and prescribes the Article 7 categories. Agrumi, peach, apricot and plum are excluded there because they are not susceptible to pauca ST53.[S3]

### Who creates the field-ready package

The 2024–26 action plan gives a concrete upstream handoff. Within seven working days after laboratory results, InnovaPuglia supplies the Observatory with cadastral parcels, owner identities and orthophotos. The Observatory then issues the injunction. The signed order plus orthophoto, sample/test reference, 50 m parcel/owner annex, target categories, method, contact, clock and legal bases is the authoritative field package.[S2]

**Important limit:** the public order is parcel/tree-specific but is not a complete contractor method statement. It does not publish machine type, crew composition, underground-service check, traffic plan, daily sequence, waste tickets, archaeological watching plan, contractor insurance or access-key arrangements. Those remain a delivery package to be assembled by the owner/contractor or ARIF.

### Owner choices and access/consent

The order is notified through seven consecutive days on the municipal *albo pretorio* and, when present, direct PEC. The owner/holder must state during publication or no later than three days after it ends whether they will remove voluntarily or use ARIF. Voluntary removal must occur within ten days after that communication and be scheduled with the Observatory. ARIF also has ten days after the owner communication. Silence after the three-day response period routes removal to ARIF within the following ten days.[S3]

Consent is therefore **not** a prerequisite to the legal duty or official access. Authorized staff may enter infected land. If the owner or third parties obstruct, the incident is documented, the Prefect may provide police assistance, and ARIF may perform forced removal. The order provides for charges to the owner, administrative sanction/referral and loss of any removal contribution where the owner fails to start within the legal period.[S3]

### Readiness dependencies before the crew can start

1. Official positive result and subspecies identity.
2. Correct current demarcation/regime at the event date.
3. Exact target set: infected point, 50 m geometry where Article 7 applies, cadastral parcels and owner/holder identities.
4. Publication/notification clock completed or owner route selected.
5. Monumental/historic status resolved. A negative monumental tree in the ring can need designation and landscape authorization; an infected tree does not get the ordinary historic-value derogation.[S1][S3]
6. Vector-control treatment before/during removal in flight season; Puglia normally omits it November–March unless monitoring still shows adults.[S1][S2]
7. Field access, exact plant marking and agreement on wood disposition.
8. Mechanical capacity and official supervisor slot.
9. Archaeological contingency: chance finds are reported to the *Soprintendenza*.[S3]

### Execution, supervision and evidence

The current Bitonto order requires mechanical uprooting, on-site shredding or lawful burning of foliage separated from the trunk, and leaves de-limbed/cut wood to the owner. The action plan allows the Observatory to authorize branch/foliage destruction and root devitalization where the location prevents full root removal. If wood or chips move from infected to disease-free areas, the buyer/haulier must notify origin, destination, quantity, vehicle registration and port; 1 April–31 October loads must be covered, and Carabinieri Forestali can inspect outgoing transport.[S2][S3]

At least one official inspector/agent/assistant must be present to identify targets, verify removal and destruction, and prepare the *verbale*. Voluntary work is controlled by Observatory and/or ARIF staff; ARIF removal is controlled by two ARIF phytosanitary assistants in the 2026 order. The signed *verbale* is the legal field acceptance artifact and a prerequisite to the indemnity.[S3]

**Minimum evidence set:** order and annex hash; publication dates; owner route communication; identity/access notes; pre-treatment where required; exact target reconciliation; monumental derogation/test/authorization if applicable; start/end date; method; supervisor identities; removed count/species; destruction method; retained/moved wood; obstruction/force-public record if any; signed *verbale*; georeferenced field photos where collected. The primary order does not expressly make photos, machine telemetry or waste weights mandatory; do not present them as legal requirements.

### Rejection, rework and legal acceptance

* Wrong/missing tree or incomplete Article 7 category: operation remains non-compliant and requires completion under supervision.
* Foliage not destroyed or roots capable of resprouting where a special method was authorized: rework is required to meet Article 9 and the order.[S1][S2]
* Obstruction: official record → Prefect/police escalation.
* Owner non-start by ten days from notification: forced removal route, sanction/referral and no contribution.[S3]
* Acceptance: supervisor-signed *verbale*, not contractor self-certification.
* Payment handoff: the owner applies through the ARIF portal; ARIF owns instruction/liquidation of owner/holder indemnities and aid-register entries. The aid regime covers qualifying destruction only under official vigilance and an official *verbale*.[S4][S5]

## A2. Compulsory vector control and land management

```text
Vector monitoring + annual action plan
  → Observatory sets geographic scope, permitted methods and seasonal window
  → order/circular published and transmitted to municipalities/enforcement
  → owner/holder/public-land manager chooses permitted method or delegates execution
  → weather/phenology may trigger formal extension
  → field execution across whole applicable land unit
  → Observatory + Carabinieri Forestali control, including aerial survey
  → non-compliance sanction/enforcement; there is no routine grant acceptance handoff
```

For 2026 the juvenile-vector order applies compulsory superficial soil work across the regional territory: ploughing, milling, harrowing or mowing; mown sward must be no higher than 10 cm. Mechanically inaccessible slopes, roadsides, verges and roundabouts use physical methods (flame or steam), with suitable low-impact herbicide only when those are impossible. The original windows were 25 March–30 April below 200 m mean altitude and 10 April–15 May above 200 m.[S6] A later determination extended deadlines because rain made fields impracticable; this demonstrates that weather/carrying capacity changes require a formal act, not informal tolerance.[S7]

The action plan identifies obligated actors as owners/holders of agricultural land and public/private managers of uncultivated agricultural surfaces, public green areas, roadsides, channels and public land. Public bodies may delegate execution to farmers under Legislative Decree 228/2001. Protected areas, woods, pinewoods and private gardens are excluded in the cited plan; for active arable/forage/pasture land with olives, work is under the olive canopy. Observatory controls may use Carabinieri Forestali and aerial imagery.[S2]

**Decision rights:** the Observatory decides scope, timing and acceptable methods. The land manager chooses among allowed methods and selects a contractor. Municipalities and enforcement do not redesign the agronomy. A contractor invoice alone is not legal acceptance; compliance is physical condition during the window.

**Capacity constraint:** weather and simultaneous region-wide demand can make fields or contractor calendars unavailable. The 2026 extension is primary proof that practical access can shift the legal clock.[S7] No public source reviewed gives contractor rosters, hectares/day, inspection sampling rate or a rework protocol for a failed mowing-height inspection.

# Process map B — grant-funded removal, replanting, grafting, irrigation and aftercare

## B1. Common fund-to-field flow

```text
Voluntary strategy choice
  → confirm parcel is in eligible legal geography and no double funding
  → update farm dossier/title/associative links
  → beneficiary delegates CAA and/or authorized agricultural technician
  → technician builds EIP + signed field design + readiness/consent/title package
  → DdS submitted; self-scored ranking; technical-administrative instruction
  → concession defines approved quantities, cost class, aid, CUP and completion date
  → beneficiary may request advance against guarantee
  → beneficiary privately procures nursery stock, contractor, materials, irrigation
  → work starts (at beneficiary risk if before concession; eligible dates still apply)
  → technician directs work and maintains change/evidence control
      ├─ approved project
      ├─ prior-approved formal variant
      └─ permitted adaptation documented at balance
  → completion and final technical dossier
  → DdP balance
  → administrative checks + in-situ visit / regular-execution check
      ├─ accept and pay eligible amount
      ├─ cut unsupported/missing component or affected area
      └─ reject/revoke/recover for material breach
  → durability period and continuing inspection access
```

## B2. Replanting under Article 6 of the 2020 extraordinary plan

### Trigger and owner choices

The Article 6 route is voluntary and applies to previously olive-planted land in the infected area, excluding the containment part. The basic owner choices are individual or collective application; entrepreneur or non-economic owner route; eligible resistant/tolerant cultivar; site, density and whether irrigation is needed; direct delivery or a mandate to a producer association/cooperative.[S8][S9]

The consolidated call requires collective members to approve the initiative, delegate the legal representative to file, and mandate the collective entity to perform removal and replanting. It also requires owner authorization where the applicant is not the owner and a 15-year destination-of-use obligation after final payment.[S9]

### Field-ready package and procurement

The Article 6 instrument can be filed through CAA or an accredited professional. Its final delivery package is anchored by the concession and technical director. At completion the beneficiary must produce nursery invoices, traceable payments, plant passports from RUOP operators, completion communication, final technical report with georeferenced/plan-located photos, and beneficiary/works-director declaration that the works are complete and properly executed and that planted resistant/tolerant trees are at least the funded removed count.[S10]

The grant does **not** select the nursery or civil/agricultural contractor. The beneficiary or mandated collective body privately procures plants and work. Public procurement rules apply to ARIF/public-body purchases, not automatically to a private beneficiary merely because it receives a grant. The reviewed call controls reasonableness through eligible costs and evidence, not a disclosed public tender run by each farmer.

### Variants, adaptations and extensions

The 2023 implementing act permits only two formal Article 6 variants: change of beneficiary and change of location where density exceeds 300 plants/ha. A lower-density relocation within parcels already in DdS Frame S is a technical adaptation. Formal variants are submitted only after concession and not during the final three months before completion (except death-related succession). An unapproved/late variant does not excuse non-delivery of the original project.[S10]

For relocation above 300 plants/ha, an authorized water source is explicit. Adaptations need no prior approval but are jointly decided by beneficiary and works director, justified in a signed report, and adjudicated in the balance checklist/*verbale*. A rejected adaptation makes the affected plantings irregular and reduces aid.[S10]

The same act allows an extension only for force majeure/exceptional circumstances and creates a special stock-related rule: beneficiaries committed to certified virus-free material could request an extension where that material was unavailable. This is direct evidence that certified nursery stock can be a critical-path dependency, but it does not quantify regional stock.[S10]

### Completion and acceptance

There is no SAL under the implementing act: only advance and final balance. The project is complete when every approved intervention is complete. The balance claim is due within 30 days after the completion deadline. Administrative regular-execution checks precede payment.[S10]

Acceptance evidence includes:

* compliant electronic invoices and supplier releases;
* traceable payments and SIAN-linked account;
* plant passport: CAC or certified/virus-free as claimed;
* joint beneficiary/works-director proper-execution declaration;
* registration of Leccino/FS17 plantings where required;
* statutory completion communication;
* hydrogeological compatibility document where pertinent;
* antimafia materials;
* final technical report and at least four georeferenced, plan-located views.[S10]

If the claimed virus-free ranking attribute is not proven for 100% of plants, points are removed and the application is re-ranked; loss of funding position can revoke the grant. Other breaches can cut or recover aid.[S10]

## B3. SRD01.01B — current productive olive investment route

### Field-ready package

The 2025 SRD01.01B call makes the technician’s role explicit. The chronological application chain is: update SIAN farm dossier; obtain EIP/SIAN access; insert delegate(s); technician prepares EIP; file DdS; upload final EIP documents; transmit attestations. Missing any of the seven operations makes the application inadmissible.[S11]

The minimum field package is:

* title and owner/co-owner consent covering at least five years after balance;
* entity resolution/delegation where collective;
* signed technical report explaining EIP;
* signed plan showing location, plant number, spacing and irrigation development;
* signed budget;
* technician’s sworn readiness report and underlying authorizations/requests;
* professional fee estimate and insurance details;
* water-abstraction authorization or proof of consortium supply where relevant;
* finance evidence where claimed; and
* no-double-funding declaration.[S11]

The readiness attestation distinguishes immediately buildable projects from those waiting on permits. For irrigation it also addresses lawful water, meters, quantitative status of the water body and environmental authorization for a net increase. A false readiness attestation can lose twice the selection points claimed. Critically, it does not attest that a nursery batch, contractor, machine or irrigation delivery slot is reserved.[S11]

### Eligible physical package

The base olive package covers ground preparation, layout, purchase and planting. Depending on training form it can include supports/tutors; optional/additional items include deep ripping, shelters, drip irrigation and dedicated support. Minimum density is 280 plants/ha; financed irrigation is micro-flow only. For projects without irrigation, plantings above 400 plants/ha must still demonstrate a water concession/new or updated source condition specified in the call.[S11]

An April 2026 technical integration added monocone without permanent support after a Coldiretti request, while retaining invoice proof for tutors. This shows that production practice can change the legal/cost template only through a formal call amendment.[S13]

### Work start, schedule and finance

Project completion is 24 months from admission. The applicant may start after DdS and before concession, but bears the full risk of an adverse instruction. A dedicated account must be active before funded activities and before the first DdP; execution expenses must generally post-date SIAN DdS release, while preparatory design/authorization expenses may pre-date it.[S11]

The call uses standardized unit costs. Therefore invoices often prove occurrence, newness, number or type rather than set reimbursement at invoice value. The official execution guide requires an in-situ visit to verify new area, training system, density class and conformity to concession/variant.[S12]

### Evidence and rejection/rework logic

For olives, ground preparation, layout, planting and support assembly are accepted in situ. Plant purchase needs an invoice plus non-substitutable varietal and health certification; invoice count must match field count and density. Tutors, support materials, deep ripping, shelters and drip irrigation need invoices. Missing invoice evidence can remove the specific cost—even if the item physically exists. Fertilizer requires invoice plus field-operation register and technical compliance.[S12]

The balance claim must also carry final report, budget, as-built plan, conformity attestation, plant passports, transport/quantity/variety records and fertilizer records. Controls may occur administratively and in situ. Claims exceeding the admissible amount by more than 25% attract an additional difference penalty. Breaches map to total or partial refusal/recovery; failure to permit access or comply with compulsory Xylella rules can cause total refusal.[S11]

### Variants

The 2026 discipline permits: project variant (including cultivar/training system within admissible species), project variant with surface/location change, and change of beneficiary for force majeure/exceptional circumstances. It requires a signed comparative variant report, new orchard project, title/permits for changed land, EIP variant, SIAN submission and PEC copy to the territorial instructor. One request of each type is allowed; none during the final three months (except death); no variant extends completion; additional cost is private; every changed intervention is checked at final acceptance. A rejected variant leaves the original concession binding.[S14]

## B4. Monumental-olive grafting

The 2025 call funds crown grafting of officially listed monumental olives—or reported trees that must be listed by final acceptance—outside eradication and containment zones. Eligible scions are authorized resistant/tolerant cultivars. Individual applicants can deliver directly; a collective project can mandate an association/cooperative to execute grafting.[S15]

The field package is tree-granular: registry/notification status, legal geography, live/asymptomatic or mildly symptomatic condition, authorized scion source, crown-grafting method, at least 20 graft points per tree, works director, owner consent and collective mandate where used. A reported-but-not-yet-listed tree causes revocation for that tree if it is still absent from the official list at *collaudo*.[S15][S16]

The final claim has no SAL. It is due within 30 days of completion and requires scion invoices with number/cultivar/CUP, supplier releases, traceable payments, RUOP operator plant passport, joint proper-execution declaration, final technical report with georeferenced pre-pruning and post-graft images for each tree, and joint declaration that treated trees were alive and asymptomatic/mildly symptomatic. The balance procedure permits only beneficiary-change variants, no technical adaptations; late or non-conforming variants are inadmissible.[S16]

**Acceptance limit:** the instrument proves that grafts were placed, not long-term take. It does not set an establishment-survival percentage, specify a revisit season, or define who replaces failed grafts. The five-year use/destination obligation is not a detailed aftercare protocol.[S15]

## B5. Nursery supply, RUOP and plant passports

Plant supply is a regulated production and movement chain, not an ordinary spot purchase.

* An operator must be registered in RUOP and separately authorized to issue passports for the listed plant categories. Puglia authorizes after official checks and can revoke authorization if requirements cease to be met.[S17]
* For Article 23 movement inside demarcated areas, the site must belong to a conforming RUOP operator, receive annual official visual inspection, sampling and testing, apply vector treatments and obtain a recipient declaration that plants will not leave the permitted zones.[S18]
* Passports carry zone-specific XYLEFA wording and traceability codes. Production-site authorization follows official inspection and can be revoked after a failed annual inspection or changed demarcation status.[S18]
* Operators request official analyses before sale, report stock, retain lot sender/recipient information for three years, and record movements. For Leccino/FS17 produced in infected zones, destination cadastral data are registered. The Observatory checks passport use, movement records and producer self-control.[S18]
* Article 18 permits planting/grafting in eligible infected areas and favors resistant/tolerant varieties; it does not authorize planting in the containment strip.[S1][S18]

A 2026 national technical protocol strengthens insect-proof-site and molecular-control expectations for nurseries in demarcated areas.[S19] The exact current DTO 80 annex was not retrieved in this pass, so the 2024 regional procedure remains the fully read primary operational basis.

**Capacity implication:** every grant schedule depends on cultivar/category-specific nursery batches that have passed the correct inspections and carry a valid movement route to the destination. The reviewed public sources do not publish live inventory, propagation lead time, forward commitments, rejection rate or available certified-virus-free share. Nursery availability is therefore a readiness gate that an intermediary must verify directly; it cannot be inferred from RUOP authorization.

## B6. Irrigation and aftercare

Irrigation is optional in the current SRD unit-cost package but legally and agronomically consequential. A new funded system must be micro-flow and tied to lawful water. The EIP/as-built plan shows its route; invoice proves new supply; field inspection verifies the built system. Article 6 relocation above 300 plants/ha also requires authorized water.[S10][S11][S12]

Professional practice evidence warns that a generic replant design is inadequate. An agronomist speaking at an event organized by the Lecce agronomists’ order criticized plantings that ignored farm-specific soil, water, mechanization, training system and economic context.[S20] A 2025 report describes young funded plantings waiting on ARIF irrigation contracts and suffering for lack of water.[S21] These are credible practice signals, not legal rules or quantified regional failure rates.

**Aftercare tasks that a field-ready operating package should assign even though calls under-specify them:** first-season irrigation schedule and source fallback; emitter checks; weed/vector-host management consistent with compulsory measures; tutor/shelter adjustment; formative pruning; nutrition tied to soil/leaf evidence; mortality/graft-failure inventory; replacement decision and plant-passport retention; storm/drought response; annual photo/condition record; five-/fifteen-year durability checks. Whether these are beneficiary, contractor, cooperative or technician obligations must be contracted explicitly.

# Actor and decision-rights matrix

| Actor | Compulsory work rights/duties | Grant-funded work rights/duties | Cannot decide unilaterally |
|---|---|---|---|
| EU / national plant-health law | Defines eradication/containment minimums, movement controls and official powers. | Defines plant movement and aid/control framework. | Parcel-level delivery schedule. |
| Puglia Observatory | Determines zone/regime; issues orders; specifies methods/windows; authorizes exemptions/movements; supervises/accepts compulsory work. | Defines eligible legal geography and plant rules; owns or supports instruction and official checks depending on measure. | Beneficiary’s private contractor price/selection. |
| InnovaPuglia | Converts result coordinates into cadastral/owner/orthophoto order annexes. | No evidenced field-construction role. | Removal method or grant concession. |
| ARIF | Executes/schedules removal after owner choice/silence; supplies assistants; records obstruction; manages owner indemnities. | Technical instruction/support for Article 6/grafting; may manage payment processes. | Rewrite an Observatory order or approve an unpermitted variant. |
| Owner/holder/beneficiary | Chooses voluntary self-delivery vs ARIF; provides access/wood decision. Cannot veto duty. | Chooses whether to apply, design options within call, procurement and permitted variant/adaptation route; funds private share. | Declare their own compulsory legal acceptance; self-authorize a formal variant. |
| Agricultural technician / works director | May support owner work but official inspector accepts it. | Builds EIP/field package, attests readiness, directs/certifies works, creates as-built/change evidence. | Issue plant passports; substitute for official grant inspection. |
| CAA | No core removal role evidenced. | Updates/files SIAN dossier/forms under mandate. | Agronomic design unless separately qualified/engaged. |
| Cooperative / OP | No default public power. Could be contractor/mandatary if engaged. | Can be applicant or mandated executor; approves project through competent body and legal representative. | Member land access without mandate; official acceptance; nursery authorization. |
| Nursery / RUOP OP | Must respect movement prohibitions. | Supplies traceable cultivar/category; issues passport only within authorization. | Decide destination eligibility or grant acceptance. |
| Private contractor | Executes owner/beneficiary scope under safety/labor/environment rules. | Supplies removal, earthwork, planting, irrigation or aftercare under private contract. | Change concession or certify phytosanitary completion. |
| Official inspector/agent/assistant | Identifies targets, supervises removal/destruction, writes *verbale*. | Performs official/in-situ checks when assigned. | Alter order scope informally. |
| Prefect / police / Carabinieri Forestali | Access/enforcement support; roadside and land-management controls. | Police controls can evidence breaches. | Agronomic redesign or grant variant. |

# Readiness gates

| Gate | Compulsory removal | Grant-funded investment | Hard evidence |
|---|---|---|---|
| G0 Legal regime | Positive + current demarcation/subspecies/article. | Eligible infected geography; no containment/eradication planting prohibition. | Official result, zone act/map, order/call. |
| G1 Target/site identity | 50 m ring, parcels, owners, exact trees. | Farm dossier, parcel title, no double funding, registry status for monumental trees. | Annexes, SIAN, titles, registry. |
| G2 Decision/authority | Owner route or silence; order effective. | Concession effective; delegates and governing-body resolution. | Publication/PEC, portal choice, concession, mandate. |
| G3 Access/consent | Consent not legally required; access arrangement still operationally needed. | Written owner/co-owner/spouse/lessor consent where applicable. | Communication/access note; DOC01 and call-specific forms. |
| G4 Permits/constraints | Historic negative tree/landscape authorization; archaeological and burning constraints. | Landscape/hydrogeological/water/environmental titles; sworn readiness status. | Authorization, request, sworn report. |
| G5 Biological material | Not applicable except historic-tree testing. | Cultivar, health category, RUOP/passport and lawful movement route; actual batch reserved. | Passport/certification plus commercial reservation (not a call substitute). |
| G6 Water | Usually not a removal dependency. | Lawful source, meter, system design, delivery capacity and establishment plan. | Concession/consortium proof, plan, contract. |
| G7 Delivery capacity | Mechanical crew + official supervisor slot + vector-treatment timing. | Contractor, nursery, earthwork/planting/irrigation sequence, finance and season. | Work order, schedule, insurance/safety documents, purchase orders. |
| G8 Evidence control | Target reconciliation and supervisor *verbale*. | CUP invoices, traceable payments, DDT, passports, photos, registers, as-built, change log. | Field dossier. |
| G9 Acceptance | Official *verbale*. | Final DdP, administrative and in-situ regular-execution acceptance. | Signed checklist/*verbale*/payment determination. |
| G10 Aftercare | Order usually closes after removal; stump resprouting can require correction. | Five-/fifteen-year durability and inspection access; practical survival plan needed. | Maintenance log, replacement records, retained passports. |

# Timing and capacity constraints

* **Eradication clocks:** seven-day publication; owner answer by three days after publication; owner or ARIF removal normally within ten days of the route decision; forced route after non-start. These are legal maximums, not capacity estimates.[S3]
* **Biological clock:** vector treatment before/during removal in flight season; containment finding outside flight season must be removed before the next one.[S1][S2]
* **Land-management clock:** altitude/phenology windows can be formally extended for weather. Region-wide concurrency raises contractor and inspection demand.[S6][S7]
* **Grant clock:** SRD completion 24 months from admission; Article 6/grafting dates sit in each concession; final balances commonly due within 30 days of completion.[S10][S11][S16]
* **Variant clock:** formal variants generally barred in the last three months and do not automatically extend completion.[S10][S14][S16]
* **Finance clock:** advance requires a 100% guarantee; otherwise beneficiary carries implementation cash until balance. DURC and antimafia controls are documented administrative delay points; Puglia reported seeking batch DURC checks with INPS.[S22]
* **Nursery clock:** annual inspection/testing, pre-sale official analysis, movement restrictions and passport issuance constrain usable stock. Certified-category scarcity has already justified an Article 6 extension route.[S10][S18]
* **Water clock:** permit and supply-contract lead time may exceed planting season. A lawful entitlement is distinct from actual network availability.[S11][S21]
* **Public delivery capacity:** ARIF has used external procurement for surveillance support—an open procedure valued at about €4.81m was published for the 2025–27 plan—but that contract is surveillance, not proof that removal crews are procured the same way.[S23] A past ARIF campaign reported 122 technicians in 61 monitoring teams, showing campaign scaling but not removal capacity.[S24]
* **Administrative queue:** ARIF reported 965 positively instructed Article 6 businesses and almost €21.95m admitted in one tranche, while also handling thousands of older indemnity files. This is credible evidence of queue load, not current 2026 throughput.[S25]

# Handoffs to applications and payments

## Compulsory → indemnity

1. Order identifies eligible targets and owner/holder.
2. Owner chooses voluntary/ARIF route through the portal.
3. Official supervises and writes *verbale*.
4. Owner files indemnity data/supporting documents with ARIF.
5. ARIF instructs eligibility, records aid in SIAN/state-aid registers and liquidates. The current aid decision separates Observatory responsibility for nursery-operator destruction indemnity from ARIF responsibility for owners/holders.[S4][S5]

The compulsory order is therefore not itself a payment approval. Conversely, a grant to replant does not legalize a missed compulsory order: SRD makes forced Xylella felling a breach capable of total refusal.[S11]

## Grant → advance/balance

1. DdS/EIP package → ranking → technical-administrative instruction.
2. Concession fixes approved design, aid, CUP and completion date.
3. Optional advance → guarantee.
4. Delivery records flow into final technical dossier.
5. DdP balance → documentary checks, site visit/regular-execution record.
6. Accepted quantity/cost class → payment; unsupported components/areas cut; material breach revoked/recovered.
7. Durability period remains open to later controls.[S10][S11][S12]

# Assertion verdicts

| Assertion | Verdict | Reason |
|---|---|---|
| “The owner chooses whether infected trees are removed.” | **CONTRADICTED** | Owner chooses owner-delivery vs ARIF. The duty is compulsory; silence/refusal routes to ARIF/forced removal.[S3] |
| “Every positive olive means all olives within 50 m are felled.” | **CONTRADICTED** | True only in the relevant Article 7 eradication application; containment removes confirmed positives and samples/tests the 50 m ring.[S1] |
| “A cadastral parcel list is enough to send a crew.” | **CONTRADICTED** | Crew still needs regime, exact targets, notification route, monumental status, supervisor, vector timing, access and method/disposal package.[S2][S3] |
| “The compulsory *verbale* is optional paperwork.” | **CONTRADICTED** | The order calls it prerequisite and indispensable for contribution recognition.[S3] |
| “A plant passport proves a new orchard meets the grant.” | **CONTRADICTED** | Passport proves regulated source/movement. Grant acceptance also checks cultivar/health certification, invoice count, field density, location, works and concession conformity.[S12][S18] |
| “Cantierabilità means the project is truly ready to mobilize.” | **PARTLY TRUE** | It covers titles and lawful water/readiness representations; it does not evidence stock, contractor, capital or water-delivery reservations.[S11] |
| “The cooperative creates the official field package.” | **UNKNOWN / NOT GENERAL** | Calls require cooperative resolutions/mandates, but the authorized technician creates EIP/technical documents. Actual cooperative aggregation practice is unpublished.[S9][S11][S15] |
| “Variants are an informal as-built correction.” | **CONTRADICTED** | Formal variants require timely submission and approval. Only expressly permitted adaptations can be adjudicated at balance.[S10][S14] |
| “SRD reimbursement is whatever the supplier invoice says.” | **CONTRADICTED** | Unit costs set reimbursement; invoices prove execution, type, count or newness. Missing evidence can cut a line even if physically present.[S12] |
| “Aftercare is fully specified and accepted by the calls.” | **CONTRADICTED** | Durability obligations exist, but no detailed survival/watering/replacement acceptance protocol was found.[S9][S11][S15] |
| “ARIF necessarily tenders every removal to private contractors.” | **UNVERIFIED** | Public sources establish ARIF’s delivery duty and a surveillance procurement, but no current removal framework/lot/crew contract was located.[S2][S23] |
| “Nursery capacity can be read from RUOP authorization.” | **CONTRADICTED** | RUOP/passport authorization says who may operate; it does not publish inventory or capacity.[S17][S18] |

# Cooperative and professional-practice unknowns

The following are material unknowns, not assumptions to fill with a generic workflow:

1. Whether cooperatives maintain a single authoritative parcel-to-work-order register or each consultant keeps separate files.
2. Who converts approved EIP rows into day-by-day crew packs and who freezes scope.
3. Whether contractors are selected by quote, framework, rotation or member choice; no cooperative procurement manual was located.
4. How cooperative mandates handle joint liability, member withdrawal, inaccessible plots, over/under plant count and defects.
5. Whether nursery stock is bought centrally, reserved by cultivar/category/lot, or left to each beneficiary.
6. Typical nursery lead time, live certified-stock availability, rejected-lot rate and capacity by cultivar.
7. Contractor capacity by operation (stump/root removal, ripping, planting, supports, drip system) and hectares/day.
8. How official inspector slots are coordinated against owner/ARIF crews.
9. Whether works directors supervise continuously, sample visits, or only certify completion.
10. Exact *verbale* and checklist templates currently used for eradication, Article 6, grafting and SRD in-situ visits.
11. Defect/rework notice, cure period and second-inspection practice where a field check fails.
12. Who owns aftercare, watering and replacement under collective projects and how mortality risk is priced.
13. Whether an unavailable authorized water supply is treated as force majeure, variant trigger, beneficiary risk or contractor delay.
14. How land-management contractors demonstrate the 10 cm condition and how aerial detections are adjudicated.
15. Current ARIF removal procurement model, active providers, machinery capacity and backlog.

# Artifact and fetch log

| # | Artifact | Authority / date | Retrieval result | Use |
|---:|---|---|---|---|
| 1 | Consolidated Reg. (EU) 2020/1201 | EU, 17 Oct 2024 consolidation | **Read, primary PDF** | Articles 4, 7–9, 13–18, 23–27. |
| 2 | DGR 1593/2024 Action Plan 2024–26 | Puglia | **Read, primary PDF** | Operational notification, removal, wood, vector and responsibility flow. |
| 3 | DDS 3/2026 Bitonto eradication order | Puglia Observatory | **Read, primary PDF** | Current owner choice, deadlines, method, supervision, *verbale*, enforcement. |
| 4 | DGR 994/2024 aid regime | Puglia | **Read, primary PDF** | Indemnity rights, roles and official-vigilance condition. |
| 5 | DGR 1075/2025 Action Plan 2025–27 | Puglia | **Direct full PDF not located** | Current order confirms its operative §4.5; older full plan used only where current order corroborates. |
| 6 | DDS 45/2025 operating procedures | Puglia Observatory | **Landing/search reference located; full annex not retrieved** | Gap; no unsupported detail attributed to it. |
| 7 | DDS 39/2026 juvenile-vector work | Puglia Observatory | **Primary municipal mirror indexed; content read through official-document search result** | Methods and original windows. |
| 8 | DDS 79/2026 extension | Puglia Observatory | **Primary municipal mirror indexed; content read through official-document search result** | Weather-based extension rule. |
| 9 | DI 2484/2020 extraordinary regeneration plan | National ministries | **Primary PDF located/read in material part** | Article 6 and Article 8 authority. |
| 10 | Consolidated Article 6 replant call | Puglia | **Read, primary PDF** | Eligibility, collective mandate, instruction, acceptance and 15-year obligation. |
| 11 | DDS 44/2023 Article 6 balance/variants | Puglia Observatory | **Read, primary PDF** | Evidence, variant/adaptation, rejection and extension rules. |
| 12 | SRD01.01B call DAdG 3/2025 | Puglia CSR | **Read, primary PDF** | EIP, readiness, eligible works, evidence, payment and sanctions. |
| 13 | DAdG 24/2025 execution guide | Puglia CSR | **Read, primary PDF** | In-situ acceptance and invoice/certification logic. |
| 14 | DAG 25/2026 technical integration | Puglia CSR | **Read, primary PDF** | Monocone-without-support option. |
| 15 | DDS 437/2026 variant discipline | Puglia CSR | **Read, primary PDF** | Formal variants and final checks. |
| 16 | DDS 203/2024 monumental graft call | Puglia Observatory | **Read, primary PDF** | Tree eligibility, graft work and collective execution. |
| 17 | DDS 10/2024 graft balance/variant | Puglia Observatory | **Read, primary PDF** | Scion passport, photos, 20 points/tree, acceptance. |
| 18 | DDS 25/2023 RUOP passport authorizations | Puglia Observatory | **Read, primary PDF** | Authorization, inspection and revocation. |
| 19 | DDS 48/2024 Articles 18/23 procedure | Puglia Observatory | **Read, primary PDF** | Nursery inspection, passport wording, movement and traceability. |
| 20 | DTO 80 nursery protocol announcement | SFN/Puglia, 2026 | **Official announcement read; annex not retrieved** | Current protocol direction only. |
| 21 | ARIF removal/indemnity page and portal form | ARIF | **Official pages indexed/read** | Portal route and ARIF administrative handoff. |
| 22 | SRD/Article 6 implementation status releases | Puglia/ARIF | **Official pages read** | DURC/antimafia and queue evidence. |
| 23 | Professional replanting critique | *Olivo e Olio*, reporting Lecce ODAF event | **Search-index text read; TLS blocked direct page** | Practice evidence, explicitly secondary. |
| 24 | Irrigation-access report | *Corriere dell’Economia*, 23 Mar 2025 | **Search-index text read; direct page 403** | Practice signal, explicitly secondary. |
| 25 | ARIF surveillance tender | OJS mirror / ARIF profile | **Tender notice read** | Procurement evidence limited to surveillance. |

## Retrieval failures and treatment

* `web_extract` returned quota/rate-limit errors for regional PDFs; direct HTTPS download plus local PDF text extraction was used instead.
* The current DGR 1075/2025 full action-plan PDF and DDS 45/2025 procedure annex were not located after targeted searches. Current DDS 3/2026 supplied the controlling field rules; DGR 1593/2024 was used only for stable operational detail that DDS 3/2026 corroborates.
* Municipal mirrors for DDS 39/79 returned 403 to direct scripted download, but the primary documents were fully indexed with operative text. They are cited with that limitation.
* Two professional pages blocked direct retrieval. Their claims are labeled secondary practice evidence and are not used to establish legal duties.

# Sources

[S1] European Commission, Consolidated Commission Implementing Regulation (EU) 2020/1201 (17 Oct 2024), https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02020R1201-20241017

[S2] Regione Puglia, DGR 1593/2024, *Piano d’azione per contrastare la diffusione di Xylella fastidiosa in Puglia 2024–2026*, https://www.agrometeopuglia.it/sites/default/files/2025-01/PIANO%20DI%20AZIONE%20XYLELLA%20FASTIDIOSA%202024-2026.pdf

[S3] Regione Puglia, DDS 3/2026, Bitonto eradication prescription, https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0

[S4] Regione Puglia, DGR 994/2024, Xylella destruction indemnity regime, https://burp.regione.puglia.it/documents/20135/2515720/DEL_994_2024.pdf/ca9011b0-1e9a-923b-11ae-5922838ad0ad?t=1724072193354&version=1.0

[S5] ARIF Puglia, *Abbattimenti e indennizzi*, https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/

[S6] Regione Puglia / municipal mirror, DDS 39/2026 juvenile-vector prescription, https://www.comune.corato.ba.it/sites/sito-comunecorato.cittadinopratico.it/files/2026-04/181_DIR_2026_00039_DeterminaPUB_pdf.pdf

[S7] Regione Puglia / municipal mirror, DDS 79/2026 extension, https://erchie-api.municipiumapp.it/s3/2647/allegati/determina-regione-0079-2026.pdf

[S8] MASAF/MEF, DI 2484 of 6 March 2020, https://cai.regione.puglia.it/documents/736605/736613/DI+firmato-PianoXylella+06-03-2020.pdf/5fc2e197-b8de-c55b-9c21-f3c52fe40a14?t=1609006848145

[S9] Regione Puglia, consolidated Article 6 *Reimpianto olivi zona infetta* call, https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182

[S10] Regione Puglia, DDS 44/2023, Article 6 final balance, variants and technical adaptations, https://www.regione.puglia.it/documents/736605/5109934/181_DIR_2023_00044_DeterminaPUB_pdf+%281%29+%281%29.pdf/cfdf5d6f-54ce-7d74-7b94-6d3fb48c2528?t=1683886662155

[S11] Regione Puglia CSR, DAdG 3/2025, SRD01.01B call, https://csr.regione.puglia.it/documents/20117/74270/Determinazione+Autorit%C3%A0+di+Gestione+n.+3+del+31.01.2025.pdf/14d31496-23a2-fb75-9cf2-44417f16afcb?t=1778149768951

[S12] Regione Puglia CSR, DAdG 24/2025, execution and accounting guide, https://csr.regione.puglia.it/documents/20117/74270/Determinazione+Autorit%C3%A0+di+Gestione+n.+24+del+10.04.2025.pdf/34c9714a-4233-f2dc-4db8-136b3db0b704?t=1761555303374&version=1.1

[S13] Regione Puglia CSR, DAdG 25/2026, SRD01.01B technical integration, https://csr.regione.puglia.it/documents/20117/74270/DAG+n.+25+del+24.04.2026.pdf/ea95a90e-5cb3-fe15-def4-949b84da1c2e?version=1.3&t=1785415056699

[S14] Regione Puglia CSR, DDS 437/2026, variant discipline, https://csr.regione.puglia.it/documents/20117/154356/DDS+n.+437+del+23.06.2026.pdf/694e3475-2e18-db74-883a-fb9d10990c6b?version=1.2&t=1784045570707

[S15] Regione Puglia, DDS 203/2024, 2025 monumental-olive grafting call, https://cai.regione.puglia.it/documents/736605/9237282/DET_203_20_12_2024.pdf/1d7b3d39-ed12-b56c-f690-eb063cff2a39?t=1736514265779

[S16] Regione Puglia, DDS 10/2024, monumental-grafting final balance and variant, https://www.regione.puglia.it/documents/736605/1003805/DET_10_24_2_2024.pdf/2f3fa867-f19a-c427-e30a-2deceaf7bd27?t=1714940058596

[S17] Regione Puglia, DDS 25/2023, RUOP plant-passport authorization after inspection, https://burp.regione.puglia.it/documents/20135/2140091/DET_25_17_3_2023.pdf/5bd1018f-e377-7cd3-9e1b-596aba3f5494?t=1679588142675

[S18] Regione Puglia, DDS 48/2024, Articles 18 and 23 planting/movement procedure, https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf

[S19] Regione Puglia, *Xylella: approved new national nursery protocol*, https://press.regione.puglia.it/-/xylella-approvato-il-nuovo-protocollo-nazionale-per-i-vivai-nelle-aree-delimitate

[S20] *Olivo e Olio*, *Xylella, nel Salento reimpianti di olivo senza pianificazione*, https://olivoeolio.edagricole.it/oliveto-e-frantoio/xylella-reimpianti-di-olivo-senza-pianificazione-nel-salento/

[S21] *Corriere dell’Economia*, *Salento e Xylella: i fondi per il reimpianto ci sono, ma manca l’acqua* (23 Mar 2025), https://www.corrieredelleconomia.it/2025/03/23/salento-e-xylella-i-fondi-per-il-reimpianto-degli-ulivi-ci-sono-ma-manca-lacqua/

[S22] Regione Puglia, *Reimpianti ulivi in zona infetta: stato di attuazione*, https://press.regione.puglia.it/-/reimpianti-ulivi-in-zona-infetta-da-xylella-lo-stato-di-attuazione-dell-avviso-pubblico

[S23] OJS notice mirror, ARIF 2025–27 phytosanitary-surveillance assistance tender, https://it.openprocurements.com/tender/2025-gara-europea-a-procedura-aperta-per-l-8217-appalto-del-servizio-di-assistenza-tecnica-alla-sorv/

[S24] ARIF Puglia, *Avviato il monitoraggio per il contrasto alla diffusione della Xylella Fastidiosa in Puglia*, https://www.arifpuglia.it/comunicati-stampa/avviato-il-monitoraggio-per-il-contrasto-alla-diffusione-della-xylella-fastidiosa-in-puglia/

[S25] ARIF Puglia, *Circa 1,000 aziende ammesse al finanziamento per il reimpianto*, https://www.arifpuglia.it/comunicati-stampa/importante-boccata-dossigeno-per-circa-1-000-aziende-agricole/

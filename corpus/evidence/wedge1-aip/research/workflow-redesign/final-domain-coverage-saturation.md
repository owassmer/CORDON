# Final domain-coverage saturation pass

Status: final bounded broad-domain search for workflow gates 1–2. This report is workflow and source-coverage evidence only. It does not select nouns, relationships, an ontology, an interface, a platform architecture, or a Challenge design.

Research date: 21 August 2026

## Executive verdict

The current research accounts for **68 source families** across Land/Duties, Funding, Applications, Field Work, Payments, and cross-cutting authoritative-state maintenance and control/reactivation.

Four adversarial query rounds produced five genuinely new workflow components:

1. a rule-conflict resolution step when a compulsory phytosanitary duty expressly displaces a funded land-management commitment;
2. a site-specific VIncA screening and escalation route for potentially affected Natura 2000 sites;
3. a municipal companion-enforcement route that can add a local order, local inspection, substitution at the defaulting party’s expense, and a separate remedy clock;
4. an instrument-specific funding-source election when the same operation could be paid through an OP sectoral programme or a rural-development intervention; and
5. an enterprise-crisis status check where a live call makes participation depend on liquidation status or judicial authority for a continuity arrangement.

The same rounds also found three important current-state changes that deepen evidence without adding another operator component:

- Ministerial Decree 348260 of 16 July 2026 replaced the 2022 national Xylella emergency plan and entered into force on 6 August 2026.[P8][P9]
- the 2026 regional juvenile-vector act sends a direct legal instruction to AGEA that compulsory tillage is a derogation from Ecoscheme 2 ground-cover obligations.[P1]
- a pending `Terra d'Otranto / Olio del Salento DOP` Union modification remained listed as an application submitted on 18 June 2026; the search found no approval and does not treat the proposed text as operative.[P12]

The fourth round added **no new operator decision, trigger, handoff, state, exception, or feedback loop**. It returned additional instances of already-covered programme, aid-register, public-land, fraud-control, judicial, municipal and funding-lineage families. This is the stopping condition for broad web search. It is not a claim that unknown unknowns have been discovered.

## Method

### Mandated baseline

The pass read:

- both current Downloads universe reports, plus the domain handbook used as a lead;
- `REDESIGN_SEQUENCE.md`;
- all 17 top-level current Markdown reports in `research/workflow-redesign/`, including both unknown-unknown reports and the recursive SIT/Scrivania audit; and
- `DATA_UNIVERSE_GEO.md`, `DATA_UNIVERSE_CIVIC.md`, and `DATA_UNIVERSE_FLIPS.md`.

The 24 mandated files contain 284 distinct external URLs. Their findings were treated as leads and reconciled against primary sources. Legacy master plans, domain decisions, product authority, specifications, rejected first-principles design, and old Foundry state were not used.[R1][R2][R3][R4][R5][R6][R7]

### Decision filter

A candidate entered workflow coverage only if it can change at least one of the following:

- who must decide or act;
- whether a member, parcel, operation, application, claim, or payment can proceed;
- which clock controls;
- which authority or counterparty receives the handoff;
- which state must remain distinct;
- which exception requires abstention, repair, appeal, redesign, or rework; or
- which later event reopens completed or dormant work.

A source that only adds context, a new example, a more current value, or a stronger citation is **deeper evidence**, not a new workflow component.

### Search and extraction

Discovery used Exa through `web_search`. Searches were in Italian and English and were organised by actor/proceeding, field/resource/value-chain adjacency, permits/municipal powers, finance/market/scientific-authority transitions, and failure modes.

Selected pages were extracted with:

```text
/Users/owenwassmer/.hermes/hermes-agent/venv/bin/python \
  /tmp/crawl4ai_extract.py --out-dir /tmp/c4a-final-saturation <urls...>
```

Crawl4AI returned usable HTML for the VIncA, landscape-authority, State Plant Health Service, regional press, MASAF DOP, organic-control and fire-information pages. It returned HTTP 500 for selected PDFs. Those PDFs were downloaded directly, checked with `file`, and extracted with `pdftotext -layout`. AGEA’s current 2025 farm-file instruction remained HTTP 403 through Crawl4AI and direct `curl` with and without a browser user agent; no workflow finding depends solely on its search snippet.[P20]

### Classification labels

| Label | Meaning |
|---|---|
| **C — corroborated component** | Already present in the current workflow model and supported again. |
| **N — genuinely new component** | Adds an operator decision, trigger, handoff, state, exception, or feedback loop not explicit in the current reports. |
| **D — deeper evidence only** | Adds a primary source, example, value, current status, or lower-level rule but no new workflow component. |
| **R — rejected outside Wedge 1** | Does not change a present Wedge 1 decision under the decision filter. |
| **P — private/direct-observation gap** | Public sources cannot establish the local fact or practice. |
| **M — live-source monitoring requirement** | Correct current state depends on recurring observation of a source that can change. |
| **L — unresolved legal acquisition** | A specific legal instrument, outcome, registration, or professional interpretation is still required. |

## Complete current source-family map

This is a bounded map of source families actually identified by the current corpus and this pass. “Accounted” means the family has a workflow disposition, not that every record inside the family has been acquired.

### A. Law, acts, proceedings, and remedies

| ID | Source family | Workflow use | Coverage disposition |
|---|---|---|---|
| SF01 | EUR-Lex consolidated plant-health regulations and amendments | EU duties, geography, movement, host and vector-control rule versions | **C, M** — current consolidation and amendments must be watched.[P16] |
| SF02 | European Commission demarcated-area notifications and plant-health pages | Cross-border source-site and movement-rule changes | **C, M**; not a Europe-wide analytics workflow. |
| SF03 | MASAF/Servizio Fitosanitario Nazionale emergency plans, official technical documents and committee outputs | National command chain, official diagnostics, nursery controls and authority transition | **C, D, M** — the 2026 plan replaced the 2022 plan.[P8][P9] |
| SF04 | National statutes, decrees, Official Gazette and registration/control-body evidence | National competence, sanctions, aid-law and effectiveness | **C, M**; signature, registration, publication and effectiveness remain distinct. |
| SF05 | Puglia Xylella action plans and implementing conventions | Annual/regional duties, delegation, monitoring and capacity | **C, M** — DGR 1075/2025 is the current 2025–2027 plan cited by DDS 39/2026.[P1] |
| SF06 | BURP DGR/DDS/DET corpus and annexes | Governing acts, orders, cadastral annexes, funding, amendments, liquidation and recovery | **C, M**; traverse citations, amendments and successors. |
| SF07 | Regional transparency, agriculture, rigenerazione and CSR act portals | Act discovery, programme lineage, rankings and notices | **C, M**; portal summaries never override the act. |
| SF08 | Municipal albi, ordinances, notices and local proceedings | Legal notice, local order, public-land duty, sanction, execution and local programme | **C, N, M, L**; bounded municipality disposition below.[P2] |
| SF09 | Giustizia Amministrativa, court files and OpenGA datasets | Filing, interim relief, judgment, annulment/upholding and reactivation | **C, M**; `appeal filed` never means `stay granted`.[P23] |
| SF10 | Constitutional Court, Court of Cassation and ordinary-court records | Landscape-law validity, recovery jurisdiction and post-payment disputes | **C, M**; remedy route depends on the power exercised. |

### B. Authoritative and operational land state

| ID | Source family | Workflow use | Coverage disposition |
|---|---|---|---|
| SF11 | Recursively enumerated Puglia SIT ArcGIS root | Finite official GIS catalogue denominator and new-service discovery | **C, M** — 194 services, 3,724 layers and 105 tables at audit date; not all non-GIS sources.[R4][P17] |
| SF12 | Current pauca, fastidiosa and multiplex demarcated-zone services | Date/subspecies/ST-specific operational geography | **C, M**; acts govern legal effect and GIS publishes operational geometry. |
| SF13 | Historical zone services, archived maps and Wayback captures | Historical parcel/date replay and supersession | **C, M**; gaps remain where no versioned geometry or act is recovered. |
| SF14 | `PuntiStampa` infected plants, buffers and diagnostic-document links | Discovery and reconciliation of likely live parcel cases | **C, M**; a point or generated buffer does not itself create a duty. |
| SF15 | Current and historical regional monitoring services | Sampling, result, confirmation, species and campaign state | **C, M**; sampled/result/confirmed/notified remain distinct. |
| SF16 | CKAN and annual campaign workbooks | Deep surveillance history and analytical context | **C, M**; survey-frame and schema changes prevent naïve current-state use. |
| SF17 | Official vector-monitoring transmission PDFs | Seasonal vector timing and rule-change evidence | **C, M**; semi-structured and cadence-sensitive. |
| SF18 | Official laboratory reports, confirmations and designated-laboratory records | Official result, method, protocol, timing and trigger | **C, P, M**; throughput and turnaround remain direct acquisitions. |
| SF19 | Puglia SIT cadastral layers | Parcel lookup and regional operational joins | **C, M**; snapshot date and null parcel identifiers require caution. |
| SF20 | Agenzia delle Entrate INSPIRE cadastral WFS/WMS | Current parcel geometry and national cadastral reference | **C, M**; it does not identify the current farm operator. |
| SF21 | SIAN farm file, LPIS/GSAA and olive-register records | Current farm identity, declared land, title, crop, CUAA and IBAN | **C, P, M, L**; current access is CAA/member-mediated. |
| SF22 | Monumental-olive registry, provisional records and field reports | Protected-tree discovery and escalation | **C, M, P**; an empty registry hit does not exclude an uncatalogued candidate. |
| SF23 | Landscape decisions, delegated-authority registers and Scrivania services | Permit routing, outcomes and competent authority | **C, D, M**; Region, province, municipality and Soprintendenza routes differ.[P5] |
| SF24 | Protected-area layers plus VIncA rules, forms and proceedings | Natura 2000 warning, screening, escalation and decision | **N, M**; explicit branch added below.[P3][P4] |
| SF25 | Civic-use land records and proceedings | Authority to change use, mandate work or apply | **C, M, L**; a record is a warning until the competent proceeding resolves it. |
| SF26 | State/public land, roads, canals and infrastructure-manager records | Responsible actor and public execution route | **C, M, P**; manager-specific work state remains partly direct. |
| SF27 | Forest-cut proceedings and decisions | Conditional permit/status for legally forested complexes | **C, M**; rejected as a universal olive-parcel gate. |
| SF28 | Water derivations, consortium/ARIF service, current delivery and quality | Lawful source, serviceability, design capacity and current quality | **C, P, M**; rights and map coverage do not prove physical delivery. |

### C. Funding, applications, and programme lineage

| ID | Source family | Workflow use | Coverage disposition |
|---|---|---|---|
| SF29 | Article 6 call, FAQ, forms and programme page | Adhesion, collective inclusion, individual fallback, concession and two-stage claim | **C, M**; instrument-specific, not a universal template.[P15] |
| SF30 | SRD01.01A and SRD01.01B calls, rankings, concessions and guidelines | Current infected/free-area investment routes | **C, M**; separate geography, authority, payer and rule versions.[P22] |
| SF31 | Other PSR/CSR sibling calls and implementation acts | Comparative controls, payment stages, variants and failure modes | **C, D**; rules transfer only when the target instrument incorporates them. |
| SF32 | Municipal/local in-kind or small-grant programmes | Local opportunity discovery and programme-specific obligations | **D, M** — e.g. Ostuni’s free-plant call fits existing Funding→Application→Field Work→aftercare components; no new top-level component. |
| SF33 | National €30 million Xylella support route | Separate opportunity with Puglia implementation and AGEA payment | **C, M, L**; no operative regional call was located.[P19] |
| SF34 | District/filiera contracts and other collective national programmes | Separate collective programme lineages | **D, M, R**; enter only when a cooperative is an eligible participant in a live route. |
| SF35 | SIAN, PMA/EIP and regional application/payment portal materials | Compilation, release, protocol, delegation, application and claim evidence | **C, P, M**; portal state is not authority decision. |
| SF36 | AGEA/CAA instructions, mandates and farm-file procedures | Authority to act, source repair, release and evidence custody | **C, P, M, L**; current transfer/revocation mechanics remain access-blocked.[P20] |
| SF37 | Rankings, scorrimenti, concessions, reductions and non-admission acts | Budget state, public review and reactivation | **C, M**; invitation/review/concession remain separate. |
| SF38 | Variant, adaptation, extension, withdrawal and succession acts | Change classification, approval, post-hoc review, death/transfer and rework | **C, M**; programme-specific routes and clocks apply. |
| SF39 | Scrivania planting/movement communications and official service catalogue | Post-installation administrative handoff and later evidence | **C, M**; physical installation may not close the legal trail.[P18] |
| SF40 | Same-operation funding demarcation and source-election rules | Detect overlap, quantify compensation and select a permitted source | **N, M**; not every overlap is prohibited and not every cumulation is allowed.[P6] |

### D. Payments, public finance, and control

| ID | Source family | Workflow use | Coverage disposition |
|---|---|---|---|
| SF41 | Regional instruction, liquidation and SAP-RP accounting acts | Requested/admitted/granted/liquidated/ordered amount state | **C, M**; no bank receipt inference. |
| SF42 | AGEA/SIAN payment transparency | Recent per-beneficiary public payments | **C, M**; rolling two-year window must be harvested. |
| SF43 | FarmSubsidy, OpenCoesione and project/payment aggregates | Historical and non-CAP corroboration | **D, M, L**; OpenCoesione access remains network-dependent. |
| SF44 | ARIF indemnity rules, portal and liquidation evidence | Removal indemnity and owner/nursery compensation | **C, P, M**; execution/verbale and actual bank receipt remain distinct.[P21] |
| SF45 | RNA and SIAN State-aid registers | Prior aid, aid regime, cumulation, Deggendorf and concession checks | **C, D, M**; adds source coverage, not a new decision component.[P14] |
| SF46 | DURC/INPS records and debtor compensation | Contribution-regularity check, cure, offset and payment effect | **C, M**; outcome and expiry are dated. |
| SF47 | Antimafia, Article 48-bis, public-debt and aid-register clearances | Payment-stage legal clearance | **C, M**; technical approval does not imply payable. |
| SF48 | Treasury, beneficiary bank and settlement records | Failed transfer, bank receipt and final cash state | **P**; public acts normally stop before settlement. |
| SF49 | Bank/insurer guarantees, ISMEA and member finance | Advance underwriting, bridge finance and guarantee release | **C, P, M**; no automatic Xylella guarantee was proved. |
| SF50 | Invoice, VAT, CUP, payment trace and supplier-release evidence | Eligible cost, admissible spend and claim-line reconciliation | **C, M**; beneficiary accounting position controls VAT treatment. |
| SF51 | PRD recovery, external-control findings, police/GdF and fraud/OLAF routes | Post-payment audit, revocation, recovery and parallel enforcement | **C, D, M**; fraud research adds evidence, not a new recovery loop. |

### E. Cooperative, value-chain, field-supply, and certification families

| ID | Source family | Workflow use | Coverage disposition |
|---|---|---|---|
| SF52 | MASAF OP/AOP recognition and member-base records | Collective eligibility and authority continuity | **C, M, L**; effect of suspension on a filed case remains instrument-specific. |
| SF53 | CCIAA/MIMIT cooperative and enterprise-status records | Existence, legal representative, revision, dissolution and enterprise crisis | **C, N, P, M**; beneficiary crisis status is added below.[P7] |
| SF54 | Private cooperative mandates, cohort decisions and service agreements | Collective inclusion, contracting, cost and authority | **P**; no public source supplies the actual terms. |
| SF55 | Nursery RUOP, authorised production sites, inspections, passports and lots | Plant-lot legality, reservation, dispatch and receipt | **C, P, M**; live inventory and commercial terms are private. |
| SF56 | TRACES/border plant-health controls | Conditional import release and cross-border trace | **C, M, R** for ordinary domestic purchases. |
| SF57 | Contractor, technician and product-user qualifications and capacity | Readiness, reservation, safe execution and evidence | **C, P, M**; commercial capacity is not publicly enumerable. |
| SF58 | ANAC, EmPULIA, ARIF TUTTOGARE and procurement acts | Public/delegated execution mechanism and supplier evidence | **C, D, M**; private beneficiary procurement remains distinct. |
| SF59 | Wood custody, residues, burning/fire rules and destinations | Method-specific custody and execution gates | **C, D, M, P**; daily fire conditions and receiving capacity are live.[P11] |
| SF60 | DOP specifications, modification proceedings, control bodies and operator registers | Orchard/harvest/mill constraints and versioned market route | **C, M, P**; the June 2026 change remains pending.[P12][P25] |
| SF61 | Organic SIB/BioBank, control bodies and nonconformities | Input route, certification continuity and payment interaction | **C, D, M, P**; current control-body practice is member-specific. |
| SF62 | Mills, SIAN olive/oil register and ICQRF controls | Processor continuity and post-harvest traceability | **D, R, P** — mill capacity matters as a dependency; general oil-market operations are outside Wedge 1 unless a declared certification/market route invokes them.[P13] |
| SF63 | Processor, buyer, energy, labour and long-horizon commercial capacity | Feasibility warning and cohort design assumptions | **C, P, R**; do not turn it into a general market or climate module. |

### F. Science and direct observation

| ID | Source family | Workflow use | Coverage disposition |
|---|---|---|---|
| SF64 | EFSA host databases, risk assessments and official scientific outputs | Host applicability and official risk watch | **C, M**; research evidence is not diagnosis or law. |
| SF65 | EPPO distribution and diagnostic standards | Official technical reference and cross-border watch | **C, M**; protocol access can be browser-gated. |
| SF66 | CNR/CREA/CIHEAM, funded projects, papers and reports | Research lead and evidence for authority review | **C, M, R** until a competent authority changes the operative rule.[P26] |
| SF67 | Agrometeorology, fire-danger, climate, remote sensing and orthophotos | Field timing, feasibility and cause-agnostic context | **D, M, R** as independent legal/diagnostic authority. |
| SF68 | Direct cooperative, CAA, member, nursery, contractor, mill, aftercare and bank evidence | Actual local operating practice, capacity, contracts, outcomes and cash | **P**; this is an explicit acquisition family, not a public-web absence claim. |

## Workflow-component coverage matrix

| Function | Decisions and initiating triggers covered | Handoffs and distinct states covered | Exceptions and feedback loops covered | Residual status |
|---|---|---|---|---|
| **Land and duties** | Member/parcel intake; farm-file/title change; monitoring or lab event; area or act change; general or parcel order; responsible actor; notice; regime/duty; permit warning | CAA/member → competent authority; authority → municipality/ARIF/holder; official result, confirmation, demarcation, order, notice and acknowledgement remain separate | source disagreement; supersession; third-party obstruction; appeal/stay; public/civic land; monumental candidate; adjacent host; local order; compulsory duty versus funded commitment | **Saturated for broad search.** New: explicit duty-versus-Ecoscheme conflict resolution and municipal companion enforcement. Private title/current-holder facts remain SF68. |
| **Funding** | Opportunity/amendment; complete in-scope population; public eligibility; evidence readiness; member adhesion; collective inclusion; individual fallback; pursuit; rank/budget; finance feasibility | member ↔ cooperative/OP ↔ CAA/technician ↔ authority; eligible, unresolved, not assessable, unfunded, selected and conceded remain distinct | scorrimento; withdrawal; death/transfer; mandate failure; capacity change; aid-regime expiry; prior aid/cumulation; enterprise crisis; same-operation funding overlap | **Saturated for broad search.** New: source election/demarcation and conditional enterprise-crisis check. Live calls and aid registers remain monitored. |
| **Applications** | Farm-file freeze; route selection; evidence assembly; exception owner; signatory/release; portal receipt/protocol; authority integration or adverse notice | member/CAA/technician/cooperative/helpdesk/permit authority/public instructor; draft, inconsistent, printed, released, rectified, protocolled and under review remain separate | portal failure; wrong source layer; missing consent/delegation; permit pending; VIncA screening; scientific/rule change after freeze; succession; Article 10-bis response | **Saturated for broad search.** New: explicit VIncA escalation route. Local office tools and cycle-time distributions remain SF68. |
| **Field Work** | compulsory versus funded route; field readiness; executor choice; capacity and input reservation; permit and water readiness; plant-lot recheck; dispatch; weather; method; acceptance; aftercare | owner/ARIF/public body/contractor/inspector/nursery/transporter/aftercare owner; scheduled, started, held, executed, inspected, legally complete and biologically reviewed remain distinct | access obstruction; forced/public or substituted execution; product/contractor shortage; fire/burning prohibition; chance find; field deviation; variant/adaptation; lab/zone interrupt; mortality | **Saturated for broad search.** Municipal substitution and method-specific fire evidence deepen the route. Throughput, warranty and survival remain SF68. |
| **Payments** | allowed stage; evidence plan; claim release; technical instruction; legal clearances; liquidation; order; settlement; durability and recovery | beneficiary/cooperative/finance/ARIF/Region/AGEA/treasury/bank; requested, admitted, granted, liquidated, ordered and paid remain separate | invalid IBAN; DURC/antimafia/debt; aid-register conflict; partial admission; nonconformity; fraud finding; failed transfer; guarantee release; audit/revocation/recovery; court route | **Saturated for broad search.** New funding demarcation can alter claimable amount/source. Bank receipt and real repair distributions remain SF68. |
| **Authoritative-state maintenance and control/reactivation** | new act or plan; registration/effectiveness; new monitoring/lab event; GIS update; court event; scientific-authority transition; local order; programme amendment; ranking/concession/payment/recovery event | source watcher → authority review → affected operator owner; signed, registered, effective, implemented, amended, superseded, stayed, annulled and exhausted remain separate | conflicting sources; stale local citation; unknown new source family; source outage; access block; judicial stay/decision; post-payment finding; authority/delegation change | **Saturated for broad search, never closed to change.** 2026 national-plan replacement proves why the monitoring/reactivation loop is permanent. |

## Successive query rounds and diminishing returns

| Round | Adversarial branches | New components | Deeper evidence / source additions | Rejected or unresolved | Marginal result |
|---:|---|---:|---|---|---|
| **1** | VIncA/protected areas; landscape delegation; state/civic/forest constraints; force majeure; payment/IBAN/death; waste/wood; scientific authority; oil/DOP; double funding | **2**: VIncA screening/escalation; same-operation funding-source election | Current VIncA forms; delegated landscape route; oil register; overlap calculation | AGEA current farm-file instructions remained HTTP 403; general oil operations rejected outside Wedge 1 | High: two new decision branches. |
| **2** | Municipal ordinances, sanctions, public land, delegated agricultural work, local enforcement, 2026 vector acts and national scientific authority | **2**: municipal companion enforcement/substitution; explicit duty-versus-aid-commitment conflict resolution | 2026 municipal funding/execution route; 2026 national emergency-plan replacement | Exact interaction of municipal and regional sanctions remains legal acquisition | Medium-high: two new cross-cutting components. |
| **3** | Insolvency, supplier failure, safety, fire/residues, DOP status, organic controls, judicial outcomes, processor and market routes | **1**: conditional enterprise-crisis status/judicial-authority check | Fire-method gate; DOP still pending; organic change notification; supplier-change evidence | General market operations, labour law and processor modernisation rejected; programme-specific insolvency effects remain act-bound | Low: one conditional component. |
| **4** | Municipal grants, State-aid registries, infrastructure managers, servitudes, current CSR concessions, OpenGA, fraud, data-access routes and €30m lineage | **0** | RNA/SIAN aid-register family; municipal in-kind programme instance; current SRD concession and permit evidence; infrastructure/public-land instances | No operative regional €30m call; no new court effect; private capacity unchanged | **Zero component yield.** All results mapped to existing components, monitoring, specific acquisitions or rejected branches. |

Round 4 is the first zero-yield round after the search vocabulary was deliberately broadened beyond the known reports. No fifth broad round is justified under the stop rule below.

## Novel residual findings

### N1. Compulsory-duty conflict resolution is a separate decision

DDS 39/2026 applies compulsory juvenile-vector tillage throughout Puglia and expressly states that the phytosanitary works derogate from the Ecoscheme 2 ground-cover obligation.[P1]

This is more precise than generic “avoid double funding.” The operator must:

1. detect an apparent conflict between an active aid commitment and a later or parallel compulsory duty;
2. locate an express legal derogation, compatibility rule or authority decision;
3. preserve both rule versions and applicable dates;
4. hand the authoritative derogation to the field and payment evidence owners; and
5. abstain and escalate if no express reconciliation exists.

A field crew should not preserve ground cover in breach of a compulsory Xylella act, and a payment reviewer should not treat the compulsory tillage as an unexplained breach of Ecoscheme 2. The same reasoning cannot be generalised to other aid commitments without their own compatibility rule.

### N2. Natura 2000 overlap creates a screening-and-escalation route, not a Boolean permit result

Puglia’s VIncA rules reject blanket exclusions, self-certified “no incidence” declarations and a priori generic buffers. Screening must reach an unequivocal result; uncertainty moves the matter to appropriate assessment. The procedure can also require a site manager’s `sentito`, with its own procedural timing.[P3][P4]

Workflow consequence:

```text
protected-site or possible-effect trigger
→ identify competent VIncA authority and site manager
→ site/project-specific screening submission
→ unequivocal no-significant-effect decision
   OR uncertainty/significant-effect path to appropriate assessment
→ conditions or refusal incorporated before procurement/dispatch
→ later project change reopens the assessment
```

Protected-area geometry remains a warning. It is neither automatic refusal nor automatic clearance.

### N3. A municipality can create a companion enforcement proceeding

The Bitonto mayoral ordinance did more than repeat the regional campaign. It was immediately enforceable, assigned local and multi-agency inspection, provided a local appeal clock, stated a municipal sanction basis, and described execution at the defaulting party’s expense after inertia.[P2]

The municipal route therefore has a real but bounded role:

```text
regional duty
→ municipality may publish only, adopt its own order, or manage public land
→ local inspection/noncompliance event
→ municipal sanction and/or substituted execution where lawfully invoked
→ cost recovery and separate remedy
```

This route does not transfer plant-health competence from the Observatory to the mayor. It also does not prove that every municipality must adopt a duplicate order.

### N4. Same-operation overlap can require a funding-source election

Puglia’s current double-funding discipline distinguishes overlap from actual overcompensation. For OP/AOP sectoral programmes versus the corresponding SRA intervention on the same surface and annuality, the beneficiary chooses one funding source for the operation; the administration then enforces non-overlap through its information systems.[P6]

The operator must therefore distinguish:

- different eligible costs that may coexist;
- the same cost or compensated commitment subject to an intensity cap or reduction;
- mutually exclusive source routes; and
- an actual prior concession from a merely filed or unpaid application.

This component prevents both false rejection and double payment.

### N5. Enterprise crisis can change funding eligibility and signing authority

A current 2026 CSR call excludes judicial liquidation, compulsory liquidation and ordinary preventive arrangements, while allowing a continuity arrangement only with judicial authorisation unless already homologated.[P7]

The finding is instrument-specific, but the workflow component is general:

- recheck beneficiary enterprise status at the dates required by the call;
- identify whether a continuity exception exists;
- acquire the judicial authorisation or homologation when required;
- recheck legal representative/signing authority; and
- route any status change after filing or concession to the programme authority instead of silently treating it as a member-finance problem.

Do not transplant CR05 wording into Article 6 or another call unless that instrument incorporates it.

## Deeper evidence only

1. **National plan supersession.** The 2026 national emergency plan replaces the 2022 plan, defines a revised command chain and is itself subject to revision. This validates authoritative-state monitoring; it does not add a sixth operating function.[P8][P9]
2. **Municipal/public-land financing.** The 2026 regional allocation funds municipalities and provinces for public surfaces and roads and supports agreements with farmers. It supplies an execution mechanism already covered by Field Work.[P10]
3. **Burning and residue constraints.** Puglia fire law prohibits burning from 1 June to 30 September, imposes weather/distance rules outside that period, and requires chipping/shredding in protected and Natura 2000 areas absent a certified exception. This is a method-specific field gate; `trinciatura` remains the ordinary fallback.[P11]
4. **DOP transition watch.** The June 2026 Terra d’Otranto/Olio del Salento file remains in MASAF’s submitted-to-Commission list. It is not approved merely because a proposed specification is downloadable.[P12]
5. **Oil register.** The SIAN oil register creates processing and origin-traceability duties for mills and packers. It matters when a declared market route invokes it, but it does not add a Wedge 1 recovery workflow.[P13]
6. **State-aid registers.** RNA and the SIAN aid register provide concession/cumulation evidence and an accessible Deggendorf check. They strengthen Funding and Payments; they do not replace programme rules or bank receipt.[P14]
7. **Current SRD concessions.** Current concession acts confirm that permit/VIncA readiness, water authorisation, CUP evidence and payment stages remain award-specific.[P22]

## Rejected branches

| Branch | Disposition | Reason / reopen condition |
|---|---|---|
| General olive-oil mill operations and stock accounting | **R** | Outside Wedge 1 unless a live certification, payment or market-route constraint invokes a specific record. |
| Full processor modernisation | **R** | Processor availability is a dependency; financing or redesigning a mill is another workflow. |
| Consumer marketing, e-commerce and generic traceability technology | **R** | No present eligibility, application, field or payment decision changes. |
| Broad labour-law or occupational-safety product | **R** | Contractor qualification and safe dispatch are required; a general HR/safety workflow is not. Reopen only for a call, permit or work method with a specific check. |
| Generic climate-risk score | **R** | No official parcel/design threshold was found. Acquire design-specific water, salinity, energy and field evidence instead. |
| Europe-wide outbreak analytics | **R** | Cross-border state matters only through official rule, host, nursery-source or movement changes. |
| Research/phenotyping operations | **R** | Research creates a watch item; only competent-authority transition changes operator advice. |
| Full credit underwriting | **R** | Wedge 1 detects financing gaps and prepares referrals. Banks/guarantors decide credit. |
| Insurance as an automatic Xylella claim route | **R/L** | No live general Xylella product was proved. Reopen with current policy wording and underwriting evidence. |
| Automatic second-opinion entitlement | **R/L** | Not proved for Xylella “other official activities.” Reopen with a specific procedure or judgment. |
| Universal SUAP filing | **R** | Not proved for ordinary replanting. Reopen for buildings, commercial premises or another SUAP-regulated element. |
| Universal forest-cut or monument permit | **R** | Applies only when the legal land/operation scope triggers it. |
| Generic servitude/easement module | **R** | Access, water and title evidence already carry the needed decision. Reopen with a parcel-specific restriction that blocks work. |
| Standalone municipal dashboard | **R** | Municipal material is handled by notice, public-land, permit, enforcement and local-program triggers, not as a separate operating function. |

## Municipal gap disposition

### What is now covered

Municipalities appear in five bounded roles:

1. **legally effective publication:** a regional removal act may use the municipal albo to start a notice clock;
2. **public-land and infrastructure manager:** the municipality may owe vector-control work on roads, green areas, canals and other surfaces;
3. **local order and enforcement:** a mayor or competent municipal office may adopt an additional order, inspect, sanction or arrange substituted execution under its own legal basis;
4. **delegated permit authority:** the municipality or municipal association may hold landscape competence, while other cases route to province or Region; and
5. **local programme manager:** a municipality may run a small in-kind or grant programme with its own ranking, installation and durability conditions.

### What is not resolved

The current corpus does not contain a complete, current set of every municipality’s:

- 2026 Xylella ordinance and sanction schedule;
- local execution-at-expense practice and completed cases;
- public-land work plan, contractor or farmer agreement and completion evidence;
- landscape delegation status at every relevant date;
- burning/residue ordinance; or
- local replant/in-kind opportunity.

Bitonto’s 2026 ordinance cites the superseded DGR 1593/2024 plan while the controlling regional DDS 39/2026 cites DGR 1075/2025. The local order also states a municipal sanction basis while other municipal notices cite the plant-health sanction in Legislative Decree 19/2021. This pass does **not** decide validity, concurrency or cumulation. That requires the actual regional and municipal offence definitions and, if consequential, legal review.[P1][P2]

### Disposition

Do not attempt an unbounded scrape of every municipal page as proof of completeness. Maintain a municipality register and activate acquisition when one of these triggers occurs:

- a member parcel lies in that municipality and a regional act requires local publication;
- the municipality/public body is the responsible land manager;
- a local ordinance, permit delegation, sanction, execution or programme is discovered;
- a field method depends on local burning or access rules; or
- a source conflict changes a live case.

For each activated municipality, acquire the current albo act, later amendments/proroghe, legal effect, competent office, enforcement basis, public work route and appeal information. Municipal press pages remain alerts; the signed act controls.

## Residual unknown classes

These are not “known unknown unknowns.” They are classes that the current evidence shows cannot be closed by more untargeted web queries.

1. **Unenumerated future public source family.** A new register, service, proceeding or publication channel can appear outside the current 68 families.
2. **Private agreement and governance facts.** Cooperative mandates, selection reasons, service terms, cost allocation, conflicts, withdrawal and default handling.
3. **Local CAA operating practice.** Worklists, communications, evidence custody, exception routing, cycle time, error and rework distributions.
4. **Live commercial capacity.** Nursery lot inventory, plant reservation, contractor/product availability, machinery fit, technician and inspector slots, mill capacity and prices.
5. **Member-specific truth.** Current title/consents, fascicolo, liquidity, guarantee, tax/accounting status, market intention, certification, succession and willingness.
6. **Physical serviceability.** Water pressure/volume/outage/quality, access, power, parcel condition and safe machine envelope.
7. **Post-installation outcomes.** Mortality, survival, aftercare performance, warranty, defects, replacement and productive recovery.
8. **Cash settlement.** Treasury rejection, bank receipt, beneficiary allocation and actual failed-payment repair.
9. **Unpublished or access-blocked legal/procedural material.** CAA mandate transfer, internal protocols, final aid-regime decisions, retest access, municipal enforcement files and some registration/effectiveness evidence.
10. **Future legal/scientific transition.** New EU amendments, national/regional plans, official host/cultivar decisions, DOP approval, court stays/judgments and authority/delegation changes.
11. **Data-quality failure inside an authoritative family.** Missing, stale, duplicated, delayed or contradictory official records even when the source family is known.
12. **Mixed-scope edge cases.** One operation combining official removal, voluntary redevelopment, protected assets, several funding sources or several responsible parties.

## Direct acquisitions

| Priority | Acquisition | Owner / positive route | Classification |
|---|---|---|---|
| P0 | One cooperative cohort and mandate file, including selection, contracting, cash calls, withdrawal and default | Cooperative/OP document request and walkthrough | **P** |
| P0 | One CAA case from intake through source repair, release, authority response and payment | CAA screen-share, worklist/export and filed evidence | **P** |
| P0 | Current member/farm authority pack | Member + CAA: validated farm file, title, consents, PEC, IBAN, legal representative, succession/transfer | **P** |
| P0 | Live nursery stock and lot reservation book | RFQ to RUOP operators; verify site, inspection, test, passport, quantity, lead time, substitution and warranty | **P** |
| P0 | Contractor/input/inspector capacity board | RFQ/interviews plus ARIF/Observatory event extracts and official product evidence | **P** |
| P0 | Official event and act feed reconciliation | Observatory/BURP/SIT/Scrivania acquisition with human conflict review | **M** |
| P0 | Current parcel water service pack | Member documents + water authority/ARIF confirmation + technician demand/quality calculation | **P** |
| P0 | Paid claim to bank receipt | Beneficiary, Region/AGEA and bank evidence for one end-to-end payment | **P** |
| P1 | VIncA/landscape/heritage field pack | Qualified technician + competent authority/site manager; preserve decision and conditions | **P/M** |
| P1 | Aftercare and mortality cohort | 3/6/12/24-month inspections with responsibility and replacement outcomes | **P** |
| P1 | DOP/organic and mill route pack | Current operative specification, control-body status, member declaration, mill letter/slot and traceability plan | **P/M** |
| P1 | Member cash-flow/guarantee referral | Member consent, timing plan, lender/insurer/ISMEA response | **P** |
| P1 | Municipal active-case pack | Signed current ordinance/albo event, amendments, enforcement basis, public-land work and local permit/programme | **L/M** |
| P1 | Beneficiary enterprise-crisis evidence | Current CCIAA/tribunal evidence and programme-specific authority decision | **P/L** |
| P2 | Wood destination and acceptance capacity | Implementing acts + receiving-centre contact + custody/price/acceptance terms | **P/M** |
| P2 | AGEA current CAA mandate transfer/revocation procedure | Obtain through AGEA/CAA or lawful access request; current direct source remained HTTP 403 | **L** |
| P2 | Final outcome of the 2018 aid-regime transition | MASAF/Puglia decision and payment list | **L** |
| P2 | OP suspension effect on already-filed Xylella cases | Specific aid act, authority interpretation or case decision | **L** |
| P2 | Municipal-versus-regional sanction interaction | Signed acts, offence elements, enforcement files and qualified legal review | **L** |
| P2 | Insurance and tax treatment | Current policy wording and act/beneficiary-specific professional advice | **L/P** |
| P2 | Xylella retest/resampling route | Observatory protocol or later judgment | **L** |

## Ongoing monitoring requirements

| Cadence | Source watch | Reactivation trigger |
|---|---|---|
| Daily/near-daily in active season | Observatory/BURP acts, official lab-result links, monitoring layers and vector reports | new positive, demarcation, order, duty, deadline, method or official confirmation |
| Daily for active legal cases | Municipal albo and PEC/portal notices | notice starts a clock; local order, sanction, substituted execution or appeal event |
| Weekly while calls/projects are live | Rigenerazione, CSR/PSR, SIAN/PMA/EIP and concession/liquidation pages | amendment, reopening, scorrimento, concession, integration, variant, hold, liquidation or recovery |
| Weekly for procured/field work | RUOP/site status, nursery lots, contractor/input slots, water service, weather and fire-danger source | source-site status, stock/capacity loss, outage, wind/rain/fire hold or delivery failure |
| Monthly | SIT/Scrivania service inventory and selected layer counts | new service/layer, schema change, unexpected count change or source disagreement |
| Monthly | MASAF/SFN, EUR-Lex and Commission demarcated-area pages | new plan, amendment, host/cultivar rule, national/EU status change |
| Monthly | OpenGA/Giustizia Amministrativa and cited proceeding records | filing, stay, judgment, annulment, narrowing or reactivation |
| Monthly | DOP/organic control pages and pending modification files | approval, temporary modification, control-body status or certification-rule change |
| At each Funding and Payment decision | RNA/SIAN aid registers, DURC, antimafia, 48-bis, IBAN and beneficiary status | new aid, changed headroom, compliance hold, enterprise crisis or identity mismatch |
| Annual harvest | AGEA payment transparency and time-limited operational exports | preserve data before rolling windows delete it |
| Event-driven | Private cooperative/CAA/member/supplier/bank evidence | corrected fact, withdrawal, death, transfer, insolvency, defect, mortality or settlement |

## Explicit unknown-source and reactivation mechanism

Future discoveries are handled by a controlled reactivation loop rather than by claiming the source universe is complete.

```text
new source, record, correction or access grant
→ quarantine as unverified
→ classify authority, scope, date, custody and update mechanism
→ identify finite catalogue/citation/program/judicial dependencies and traverse them
→ compare with current authoritative sources; preserve disagreement
→ determine which active or dormant decisions are affected
→ reopen only the affected Land, Funding, Application, Field Work or Payment work
→ assign a human decision owner and acquisition deadline
→ record the new source family or extend the existing family
→ close only after the authority/evidence and downstream consequences are reconciled
```

Rules:

- No newly found GIS layer, press page, scientific paper, consultant report or vendor claim mutates operator advice by itself.
- A genuinely new source family receives a new family entry; it is not forced into a familiar source merely to preserve the count of 68.
- A new record inside an existing family can still reopen cases if it changes authority, date, geography, duty, eligibility, evidence, payment or remedy.
- Access failure creates a named acquisition and owner, not a default negative.
- Private evidence is versioned and scoped to the cooperative/member/counterparty that supplied it.
- Unknown unknowns remain possible. The mechanism controls their treatment after discovery; it does not assert their present contents.

## Stop rule

**Broad web search stops now because four successive adversarial rounds covered actor, proceeding, value-chain, permit, municipal, financial, market, scientific-authority-transition and failure-mode adjacencies, and the last round produced zero new operator decision, trigger, handoff, state, exception or feedback loop.** Its results were all:

- corroboration of an existing component;
- deeper evidence or a new instance inside one of the 68 accounted source families;
- a live-source monitoring requirement;
- a named private/direct acquisition;
- an unresolved, specific legal acquisition; or
- outside Wedge 1 under the decision filter.

Another broad round would mainly resample municipal notices, call acts, aid registers, general agriculture controls and downstream market material. It would not close the remaining gaps because those gaps require current private records, direct operational observation, a blocked or unpublished instrument, an authority decision, a bank settlement, or a future event.

Broad search reopens only if one of these occurs:

1. a new source family or actor with a plausible decision right is discovered;
2. an active case exposes an unmodelled decision, trigger, handoff, state, exception or feedback loop;
3. a direct observation contradicts the workflow model;
4. a legal/scientific authority changes the governing rules; or
5. a known bounded gap yields a primary source whose consequence does not fit the current components.

This stop rule is a diminishing-returns rule, not a completeness certificate.

## Reconciled citations

### Current project evidence

- **[R1]** `/Users/owenwassmer/Desktop/Connor/wedge1-aip/REDESIGN_SEQUENCE.md`.
- **[R2]** `/Users/owenwassmer/Desktop/Connor/wedge1-aip/research/workflow-redesign/workflow-research-synthesis.md`.
- **[R3]** `/Users/owenwassmer/Desktop/Connor/wedge1-aip/research/workflow-redesign/connected-operating-model.md`.
- **[R4]** `/Users/owenwassmer/Desktop/Connor/wedge1-aip/research/workflow-redesign/sit-scrivania-source-audit.md`.
- **[R5]** `/Users/owenwassmer/Desktop/Connor/wedge1-aip/research/workflow-redesign/unknown-unknowns-field-system.md`.
- **[R6]** `/Users/owenwassmer/Desktop/Connor/wedge1-aip/research/workflow-redesign/unknown-unknowns-institutional.md`.
- **[R7]** `/Users/owenwassmer/Desktop/Connor/olive-xylella/data/DATA_UNIVERSE_GEO.md`, `DATA_UNIVERSE_CIVIC.md`, and `DATA_UNIVERSE_FLIPS.md`.

### Primary and official sources used in the saturation pass

- **[P1]** Regione Puglia, DDS 39 of 11 March 2026, compulsory juvenile-vector measures and Ecoscheme 2 derogation (official act mirror): https://www.comune.leverano.le.it/attachments/article/5107/181_DIR_2026_00039_DeterminaPUB_pdf.pdf
- **[P2]** Comune di Bitonto, Ordinanza 218 of 22 April 2026: https://cloud.municipiumapp.it/s3/712/allegati/ord_218-del-22-04-2026.pdf
- **[P3]** Regione Puglia, DGR 1515/2021, VIncA procedure: https://burp.regione.puglia.it/documents/20135/1734526/DEL_1515_2021.pdf/5732dbf1-485f-e83c-7291-1fecc3e1b774?t=1635159576447&version=1.0
- **[P4]** Regione Puglia, current VIncA rules and forms catalogue: https://pugliacon.regione.puglia.it/web/sit-puglia-ambiente/normativa-vinca
- **[P5]** Regione Puglia, landscape-authority competence and delegation: https://pugliacon.regione.puglia.it/web/sit-puglia-paesaggio/autorizzazioni-di-competenza-regionale
- **[P6]** Regione Puglia, management of double funding for FEAGA/FEASR surface/animal commitments and sectoral-programme demarcation: https://www.regione.puglia.it/documents/42866/5490176/Allegato+A.pdf/4399ba40-94d6-f484-b885-a6c25136a069?t=1698750450124
- **[P7]** CSR Puglia, DAdG 11 of 25 February 2026, beneficiary crisis condition and judicial authorisation: https://csr.regione.puglia.it/documents/20117/74266/DAG+n.+11+del+25.02.2026.pdf/15ae9dc3-9565-00ca-1c76-a536ce2adfa1?t=1773669122166&version=1.3
- **[P8]** MASAF, Ministerial Decree 348260 of 16 July 2026 and national Xylella emergency plan: https://www.protezionedellepiante.it/wp-content/uploads/2026/08/piano-demergenza-x.-fastidiosa-2026-1.pdf
- **[P9]** Servizio Fitosanitario Nazionale publication notice and effective date for the 2026 plan: https://www.protezionedellepiante.it/decreto-ministeriale-16-luglio-2026-n-348260-aggiornamento-del-piano-di-emergenza-per-lorganismo-nocivo-prioritario-xylella-fastidiosa-alla-luce-delle-recenti-modifiche-apportate-al-regola/
- **[P10]** Regione Puglia, 25 March 2026 allocation and protocol for municipal/provincial vector-control work: https://press.regione.puglia.it/-/misure-fitosanitarie-contro-la-xylella-fastidiosa-approvati-i-criteri-di-riparto-dei-5-milioni-di-euro-in-favore-di-comuni-e-province
- **[P11]** Regione Puglia, LR 38/2016 fire and agricultural-residue rules: https://protezionecivile.regione.puglia.it/documents/3171874/3201884/LR38.pdf/8fe17e9d-3d1a-d725-014f-b27c42534c31?t=1655754079008 and live risk information: https://protezionecivile.regione.puglia.it/informativa-gestione-residui-vegetali
- **[P12]** MASAF, Union registration/modification applications, including Terra d’Otranto/Olio del Salento DOP submitted 18 June 2026: https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/3335
- **[P13]** MASAF, SIAN olive-oil load/unload register guide: https://www.masaf.gov.it/flex/files/6/a/3/D.cd7127c8f4a6d663d9a8/GUIDA_UPLOAD_REGISTRO_OLIO_v.1.1.pdf
- **[P14]** Registro Nazionale Aiuti, transparency/open-data families: https://www.rna.gov.it/trasparenza/ and Regione Puglia State-aid register guidance: https://csr.regione.puglia.it/aiuti-di-stato
- **[P15]** Regione Puglia, consolidated Article 6 replanting call: https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182
- **[P16]** EUR-Lex, current consolidated Implementing Regulation (EU) 2020/1201, 24 November 2025: https://eur-lex.europa.eu/eli/reg_impl/2020/1201/2025-11-24/eng
- **[P17]** Puglia SIT ArcGIS root: https://webapps.sit.puglia.it/arcgis/rest/services
- **[P18]** Regione Puglia Scrivania public service catalogue: https://scrivania.regione.puglia.it/
- **[P19]** MASAF, national €30 million Xylella support route: https://www.masaf.gov.it/xylella_piano_sostegno
- **[P20]** AGEA, current 2025 farm-file/CAA instruction URL; HTTP 403 in this pass: https://www.agea.gov.it/documents-apigw/documents/d/agea/agea-73919-250925-a-opr_caa-altri-testo-unico_250925_193650-pdf
- **[P21]** Regione Puglia, DGR 994/2024 Xylella indemnity regimes: https://burp.regione.puglia.it/documents/20135/2515720/DEL_994_2024.pdf/ca9011b0-1e9a-923b-11ae-5922838ad0ad?t=1724079393354
- **[P22]** CSR Puglia, current SRD01.01B programme lineage: https://csr.regione.puglia.it/bando-intervento-srd01.01b
- **[P23]** TAR Puglia, Bari, judgment 384/2026: https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=tar_ba&nrg=202400185&nomeFile=202600384_01.html&subDir=Provvedimenti
- **[P24]** Regione Puglia, DGR 644/2022 Observatory–ARIF delegation: https://burp.regione.puglia.it/documents/20135/1903491/DEL_644_2022.pdf/225dad58-4ca9-b552-2cec-b4ce44b4fd51?t=1656324044242&version=1.0
- **[P25]** MASAF, operative Terra d’Otranto production specification: https://www.masaf.gov.it/flex/cm/pages/ServeAttachment.php/L/IT/D/1%252F9%252F8%252FD.a56bd25591ba82c2da99/P/BLOB%3AID%3D3342/E/pdf?mode=download
- **[P26]** Regione Puglia, DDS 48/2024, official cultivar/planting and movement authority transition: https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf

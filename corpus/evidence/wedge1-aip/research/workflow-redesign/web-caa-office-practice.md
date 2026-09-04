# CAA / agricultural application-office practice: reconstructed operating workflow

**Research date:** 20 August 2026  
**Scope:** public, web-accessible evidence about day-to-day Italian CAA and agricultural application-office work, with emphasis on SIAN, AGEA/OP interfaces, Puglia PMA/EIP, insurance/risk-management applications, regional paying-agency practice, operator controls, exceptions, communications, and evidence custody.  
**Evidence boundary:** this is a reconstruction from the public corpus listed below, not an ethnography of a particular local office. Statements about what was *not found* are limited to the searches and artifacts in the search/fetch log. Local CRM, shared-drive, spreadsheet, telephone, WhatsApp, fee-billing, and queue-management practices remain largely unobserved.

## Executive reconstruction

A CAA office is not merely a data-entry counter. It is a delegated, evidence-bearing intermediary that receives a producer's request, establishes authority to act, makes the farm file legally and temporally usable, translates the producer's facts and a technician's project into several partially connected portals, obtains the producer's legally effective assent, releases/protocols the act, keeps the evidentiary file, watches later control outputs, and routes corrections to whichever actor is allowed to make them. The recurring operating object is not “a form”; it is a **case bundle** comprising the mandate/delegation, current fascicolo snapshot and validation sheet, application versions and barcodes, portal receipts, attachments, communications, anomaly states, and later payment evidence.

The public evidence shows a repeated pattern:

1. a member or cooperative brings an intention, deadline, and imperfect evidence;
2. the office identifies the correct mandate, paying agency, intervention, campaign, portal, and deadline chain;
3. the fascicolo is repaired and validated before downstream work;
4. a CAA operator, sometimes with a separate agricultural technician, builds the substantive case;
5. SIAN/EIP/other portals prefill, cross-check, calculate, and block, but the office decides what the facts mean and which evidence cures a discrepancy;
6. the producer reviews and signs (paper/autograph, OTP in older/current sector procedures, digital signature, graphometric signature, or FEA/SPID “Libro Firma,” depending on procedure);
7. an operator with the appropriate release role completes the release/protocol step; printing alone is not filing;
8. the office stores the signed act, attachments, receipts, and protocol linkage;
9. notices, satellite/administrative anomalies, authority requests, payment status, and later claims become follow-up work;
10. corrections are divided among CAA/beneficiary, paying-agency back office, technician, cooperative/Consorzio di difesa, insurer, and external authoritative registers.

The most consequential human work is **temporal and evidentiary judgment**: determining which facts were true at the relevant date; whether a title, identity document, IBAN, qualification, signature, or delegation is valid for the whole operation; whether a portal discrepancy is a correctable data error, a back-office matter, a substantive ineligibility, or a system malfunction; and whether the office can prove timely completion.

## 1. Search and fetch log

### Search strategy

Searches were run in Italian and English. Query families included:

- `manuale SIAN operatore CAA fascicolo aziendale`, `domanda unica rilascio OTP`, `firma elettronica Libro Firma`, `convenzione CAA`, `accreditamento sportello CAA`;
- `manuale PAI polizza collettiva`, `domanda sostegno assicurazioni`, `quietanza`, `Consorzio di difesa`, `calcola e visualizza anomalie`;
- `PMA Puglia`, `Elaborato Informatico Progettuale`, `EIP delega tecnico`, `helpdeskeip`, `accreditamento SIAN`, `malfunzionamento portale`;
- `anomalie Domanda Unica`, `lista lavorazione`, `back office`, `contraddittorio AMS`, `pagamento ritardo anomalia`;
- `export Excel`, `cruscotto`, `monitoraggio`, `notifiche`, `scarichi totali o parziali`;
- `controlli II livello CAA`, `penali convenzione CAA`, `reclamo`, `risarcimento errore CAA`, and the English query `farmers income stabilisation Italy CAA insurance intermediaries audit`;
- searches for operator training, webinars, YouTube walkthroughs, transcripts, job aids, and forms.

### Retrieval outcome

- **Substantive public artifacts read:** 30.
- **Distinct sources cited:** 32.
- Six PDFs were downloaded to temporary storage and text-extracted successfully: the SIAN PAI manual (45 pages), ARCEA CAA convention (20 pages), ARPEA convention sample (7 pages), European Court of Auditors special report, ARPEA anomaly manual (81 pages), and a one-page CAA operator-course program.
- AGEA PDF endpoints often returned an HTML rejection page to `curl` despite being richly indexed by the web search service. Claims from those AGEA documents are therefore limited to the indexed text actually returned by search; this is identified in the artifact ledger.
- AVEPA PDF downloads timed out in direct `curl`, but the search backend returned extensive page/document text. Those artifacts are treated as read through indexed full-text excerpts, not as locally parsed PDFs.
- `web_extract` was unusable in this run because of Firecrawl credit/rate-limit errors. A cloud-browser attempt also failed because the provider returned no CDP endpoint. These failures are logged here rather than interpreted as source unavailability.
- Searches for public operator-training video walkthroughs/transcripts returned mostly irrelevant videos. The searched corpus yielded a detailed **training syllabus**, but no authoritative, current, public full video walkthrough of a CAA desk processing a case end to end. This negative is bounded to the queries above and does not imply that internal webinars or association LMS recordings do not exist.

## 2. Artifact ledger

| ID | Artifact actually inspected | What it contributes | Access quality |
|---|---|---|---|
| S01 | AGEA, *Istruzioni operative Fascicolo Aziendale 2026* | Mandate validity/revocation, producer request, documentary custody, validation sheet, prohibition on autonomous CAA updates, automated acquisition from public databases | Indexed substantive text; direct PDF fetch blocked |
| S02 | AGEA, *Istruzioni operative n. 34/2025, Domanda unificata* | Application modes, role split between STAMPA and RILASCIO, FEA/SPID Libro Firma, notifications | Indexed substantive text; direct PDF fetch blocked |
| S03 | SIAN, *Manuale Utente SGR PAI dalla campagna 2021*, rev. 4.0 | PAI states, barcode, release/OTP, individual versus collective policy, policy fields, automatic rate, anomaly calculation | Full PDF parsed, 45 pages |
| S04 | AGEA, *Linee guida per l’evoluzione del sistema integrato della gestione del rischio*, v1.3 | Target workflow: manifestation of interest, scoped visibility, dashboards, Excel/PDF downloads, deadline notification, automated application, digital preservation | Indexed substantive text; direct PDF fetch blocked |
| S05 | AGEA, IO n. 17/2025, SRF.01 crop insurance 2024 | PGIR/policy/quietanza prefill, amount calculation, withdrawal, payment evidence, OTP, qualified-user route | Indexed substantive text; direct PDF fetch blocked |
| S06 | ARCEA, *Schema Convenzione CAA 2022* | Delegated duties, traceability, formal document control, custody, training, annual reporting, sanctions | Full PDF parsed, 20 pages |
| S07 | ARPEA, CAA convention sample | Separation of duties, written procedures, checklists, IT controls, audit sampling, corrective actions, penalties | Full PDF parsed, 7 pages |
| S08 | Agecontrol, *Controlli sui Centri di Assistenza Agricola* | Second-level inspection, SIAN electronic checklist/real-time findings, “ravvedimento operoso” | Live web text |
| S09 | ARPEA, determination 226/2024, second-level CAA controls | Public evidence of final reports, penalties, quality-control summaries, and PEC excerpts | Live/indexed public record |
| S10 | European Court of Auditors, Special Report 23/2019 | Italy’s complex insurance-support chain; CAA and Condifesa intermediation; scale and private facilitation cost | Full PDF parsed |
| S11 | AVEPA, *Manuale fascicolo aziendale 2025* | Mandate handoff, paper original transfer, protocol/repertory, certified-source exceptions, expired-document renewal | Indexed substantive text; direct download timed out |
| S12 | AVEPA, *Ristrutturazione e riconversione vigneti 2025/26* | Delegate registration, prefill, complaint within two hours, signature options, upload/protocol, 10-year paper retention | Indexed substantive text; direct download timed out |
| S13 | AVEPA, IAP operator/requester manual extract | CAA versus professional delegation, four application types, system lock on duplicate current application, case-file creation | Indexed substantive text |
| S14 | AVEPA, UMA fuel manual | Fascicolo-to-application prefill, inability to edit fascicolo facts in procedure, module/state sequence, closure/substitution cases | Indexed substantive text |
| S15 | AVEPA, PCG service description | Graphical editing of islands/plots, crop succession, dates, required data | Live/indexed web text |
| S16 | ARPEA, *Istruzioni per valutazione e trattamento anomalie DU* (2020+, rev. 2022) | Correctable/non-correctable anomalies, new-CAA access, DEMETRA, back-office split, Excel detail icons | Full PDF parsed, 81 pages |
| S17 | ARPEA, older *Istruzioni operative anomalie DU 2015–2020* | Taxonomy of whole-application blocks, transversal controls, CAA versus BO correction, warnings/decrements | Indexed substantive text |
| S18 | AGREA, AMS contradiction notice/manual page | Formal contradiction module and back-office cover workflow | Live/indexed web text |
| S19 | AGREA, controls description | 100% administrative checks, database intersections, GIS, in-loco/ex-post and second-level controls | Live/indexed web text |
| S20 | AGREA, payment-delay FAQ | Public statement that anomalies and added verification commonly delay payment | Live web text |
| S21 | CAA Italia, *Corso di specializzazione per operatori CAA* program | Actual training topics: mandate, protocol, titles, validation, antimafia, inaccurate declaration, alignments, BDN, anomalies/tickets, DU, payment applications | Full PDF parsed |
| S22 | ARCEA, SIAN registration/OTP instructions | Producer registration, CAA-assisted OTP enrollment, producer OTP + operator static PIN, signed-document consultation | Indexed public text |
| S23 | AGEA, QDCA IO n. 58/2024 | Manual entry versus interoperability, mass upload, load-status check, timing | Indexed substantive text |
| S24 | Puglia 2022 young-farmer call / EIP operating sequence | Fascicolo → EIP by delegated technician → SIAN DdS → EIP final-document upload; delegation and generated attestations | Indexed substantive text |
| S25 | Puglia 2024 4.1.A call page | Separate EIP and SIAN deadlines, p7m authorization, required coherence, narrow exception for proven system malfunction | Live/indexed web text |
| S26 | Puglia determination n. 19/2024 | 1,701 EIPs completed; 310 delegated cases not sent; ticket evidence; 40 allowed perfection, 12 rejected for incomplete substance | Indexed substantive text/public record |
| S27 | Puglia determination n. 78/2025 | 5,420 EIPs; helpdesk ticket adjudication; only certified technical impediments got reopening | Indexed substantive text/public record |
| S28 | Puglia EIP portal/manual/helpdesk notice | Manual availability, helpdesk email/phone/hours | Indexed public text |
| S29 | Puglia EIP service description | EIP consumes SIAN and UMA data, guides project entry, calculates/produces rankings; officials perform later substantive review | Live/indexed public text |
| S30 | Puglia EIP SRA18 2026 notice | Explicit seven-operation sequence: delegation, EIP, SIAN DdS, final upload, attestations/declarations | Live/indexed public text |
| S31 | MASAF, 2026 SRF.01 manifestation-of-interest notice | Pre-policy CAA delegation as manifestation of interest; access to public premium support | Indexed substantive text |
| S32 | Terra e Vita, 2025 reader complaint on erroneous CAA SIAN operations | Public complaint pattern: farmer supplied crop sheet early, later discovered large mapping/crop errors and sought remedy/compensation | Indexed substantive text; secondary source |

## 3. Operator and counterparty roles

### Member-facing and office roles

1. **Front-desk/intake operator** — receives the request, identifies CUAA and legal representative, captures the deadline and desired aid, checks mandate/delegation posture, and opens the office work item. Public manuals rarely name this role, but the intake acts are explicit.
2. **Fascicolo operator** — updates identity, contacts/PEC, bank evidence, legal form, holdings, land-conduction titles, livestock, equipment/structures, PCG, and campaign documents; registers/protocols evidence and produces the validation sheet. The CAA cannot invent or autonomously change facts absent the producer’s express request.[S01][S11]
3. **GIS/PCG specialist** — resolves parcels/islands/plot geometry, land use, crop succession and dates; reconciles cadastral facts, graphical land cover, and the producer’s cropping account.[S15][S16]
4. **Application compiler** — opens the campaign/procedure, imports fascicolo data, completes intervention-specific declarations, attachments, quantities and requested amounts, and runs portal checks.
5. **Agricultural technician / agronomist** — in investment cases, independently delegated to prepare the technical/economic EIP, choose and justify investments, calculate pre/post performance, assemble permits, estimates and professional attestations. Puglia explicitly requires an enabled agricultural technician; a practice owner may authorize registered collaborators.[S24][S30]
6. **Print/signature coordinator** — selects the lawful signature path, verifies the signer and current contact channel, routes the document to OTP/Libro Firma/digital/graphometric/autograph signature, and brings the signed artifact back into the case.
7. **Release operator** — has the RILASCIO authorization. In the newer AGEA two-stage pattern, STAMPA or RILASCIO can send a declaration to Libro Firma, but only RILASCIO retrieves the completed signature state and performs final release.[S02]
8. **Office/site responsible** — signs or attests the CAA checklist, confirms identification, signature, attachments and archive, oversees separation of duties, and answers second-level controls.[S06][S07]
9. **Anomaly/back-office liaison** — triages controls, opens system lists/tickets, gathers cures, communicates with OP/region/helpdesk, and records the resolution or accepted reduction.
10. **Payment/claim follow-up operator** — watches admissibility, concession, advance/saldo, policy premium payment and traceability, authority communications, and outstanding recovery/withdrawal actions.

### External counterparties

- **Producer/member/legal representative:** source of the request and facts; signs and remains responsible for declarations.
- **Cooperative/cantina/producer organisation:** provides membership, delivery/production, project or collective data and may coordinate batches.
- **Consorzio di difesa / collective body:** negotiates collective policies, supplies the membership/adhesion list and policy/certificate/quietanza data to SIAN, and may receive public payment where authorized.[S03][S05]
- **Insurer/broker:** supplies policy terms and individual-policy data; in the planned integrated model sees only authorized CUAA/product/comune/parcel information.[S04]
- **Agricultural technician/professional studio:** develops EIP or specialist evidence under a separate delegation; is not automatically the fascicolo holder.
- **CAA national/regional hierarchy:** defines procedures, trains offices, performs internal audit and corrective supervision.
- **Paying agency/region back office:** owns controls and exceptions beyond CAA permissions, issues requests/notices, protocol and payment decisions.
- **Helpdesk/system operator:** certifies or rejects claims of technical malfunction; a ticket is evidence, not automatically a remedy.[S26][S27]
- **AGEA/Agecontrol/other auditors:** inspect office organization, electronic and paper files, traceability and compliance.[S08]

## 4. Detailed work sequence

### Stage 0 — open a case and establish the clock

The operator records CUAA, producer/legal representative, target intervention and campaign, the source/referrer, relevant parcels/animals/investments/policies, and every deadline. Puglia examples show that a single “application” can have four to seven separate clocks: accreditation, delegation, EIP compilation/submission, SIAN DdS release, final EIP document upload, and upload/transmission of generated attestations.[S25][S30] Insurance adds a pre-risk/policy clock, policy informatization, quietanza, and a deadline related to policy signature or cover end.[S05][S31]

**Human judgment:** identify the correct intervention/campaign, determine the last safe internal date, and decide which evidence must be obtained before work can start.  
**Portal automation:** portal opening/closing dates and formal submission timestamps.

### Stage 1 — authority to act

The office checks that the fascicolo mandate is unique, active, not suspended/revoked/annulled, and effective on the application-compilation date.[S01] If moving from another CAA, the producer’s revocation communication and its transmission evidence (PEC or registered mail details) are captured; paper originals move to the new holder while the previous holder retains a copy under the AVEPA pattern.[S01][S11]

A **procedure delegation** is different from the fascicolo mandate. Puglia EIP requires a specific delegation to the enabled technician, while SIAN may require a signed p7m authorization/profiling request. Some professional-studio collaborators receive authorization under the delegated principal.[S24][S25]

For risk management, the 2026 manifestation of interest is itself created by a CAA delegation loaded before the first policy. It authorizes extraction of data needed to define the policy; it does not guarantee later admissibility.[S31]

**Control point:** retain the signed mandate/delegation, identity evidence, effectivity dates, portal registration evidence, and any revocation/PEC receipt.

### Stage 2 — identify and repair the fascicolo

The fascicolo operator compares the member’s present facts and intended claim with the electronic record. Typical checks are:

- identity/legal representative and valid ID;
- CUAA/VAT/CCIAA and legal status;
- mobile, email and especially PEC;
- IBAN and account-holder evidence;
- land-conduction titles and dates covering the operation/commitment;
- parcels, UTE, GIS boundaries, land use and PCG crop succession/dates;
- livestock/stable/BDN alignment;
- machinery/structures if relevant;
- antimafia subjects/declarations;
- active-farmer/young-farmer/IAP or other qualifications;
- earlier commitments, titles, transfers, declarations and pending anomalies.

Where certified public sources feed the system, the operator verifies the imported result rather than collecting a duplicate paper. Where the fact is not available or is incomplete, the operator collects and registers the supporting document. AVEPA requires prescribed documents to be registered and protocolled before or at the same time as the connected application; expired/renewed documents are registered anew.[S11]

The PCG is edited graphically: proposed land bodies are divided into plots, with crop, succession, start/end dates, area and accessory data.[S15] The portal cannot resolve ambiguous possession, actual crop, succession, or whether a map boundary represents the farm’s real operation; those require member/technician evidence and operator interpretation.

### Stage 3 — validate the repaired fascicolo

Before consolidation, the operator prints/generates a validation sheet summarizing updated information. The producer signs to confirm that the update was requested and that the information is complete and true; the CAA operator signs for completeness/conformity of delegated work. Only then is the fascicolo consolidated and reusable by downstream procedures.[S01]

**Failure trap:** an application compiler who works from an old, unvalidated snapshot can create a formally coherent application that is substantively wrong. Several procedures explicitly prohibit changing fascicolo facts inside the application module; the operator must return to the fascicolo, update/validate, and re-import.[S14]

### Stage 4 — reconcile specialist or collective inputs

#### Investment/EIP cases

The technician enters the project and economic case in Puglia EIP. EIP uses SIAN and regional UMA data, guides intervention selection, collects evaluation facts, calculates declared scores/performance, and later supports the ranking.[S29] The technician must reconcile the EIP with the validated fascicolo and future SIAN DdS, particularly amounts and aid rate.[S25]

Before EIP send, the system exposes significant data and the calculated score for review. The technician accepts the data, sends the EIP, receives an EIP send code, PDF attestation, declarations for producer and technician, and PEC confirmation.[S24] After SIAN DdS release, the technician returns to EIP with the SIAN barcode and final attachments.

#### Collective insurance/adhesion cases

For PAI-era collective policies, selecting an Organismo associativo makes the PAI collective. Choices shown in SIAN depend on member supplies transmitted by the collective body. A collective PAI is released by/for the producer; later the system receives collective-policy data from the Consorzio, which the CAA can view but does not originate.[S03] For an individual policy, the CAA enters policy dates, number, insurer, integration flag, quietanza date, product specification, price, insured area/production/value, premium, paid amount and cover dates; SIAN calculates the rate.[S03]

**Human coordination:** settle mismatched product/common/parcel/area, membership status, policy/certificate identifiers, signature, payment and quietanza.  
**Portal automation:** constrain collective-body choices from supplied member files; calculate rate; display transmitted collective-policy data; calculate anomalies.

### Stage 5 — compile the application

The compiler opens the correct procedure and campaign. SIAN or a regional system prefills identity, holdings, PGIR/PAI/policy/quietanza, GIS, livestock or other certified data depending on the intervention.[S02][S05][S14] The operator completes declarations, intervention choices, requested amounts and required attachments.

This is an interpretive step. The portal may calculate eligibility indicators or maximum support, but the operator and technician decide which claim is supportable, whether an attachment is essential/non-integrable, whether costs are comparable and eligible, and whether factual dates satisfy the rule. Puglia’s three-quote workflow, for example, requires the applicant to request provider/technician estimates through SIAN before selection and then separately delegate the selected technician.[S25]

### Stage 6 — run checks and clear pre-release anomalies

The operator runs validation/anomaly functions before final release. The public manuals support at least five outputs:

- **blocking anomaly:** release/payment cannot proceed;
- **warning/segnalazione:** requires review but may not block;
- **decrement/reduction:** system or authority lowers the payable amount;
- **CAA/beneficiary-correctable:** operator supplies a document, changes an allowed declaration, or fixes the fascicolo and recalculates;
- **back-office-correctable:** the office opens a signal/list/ticket and the OP changes territorial/control data.[S16][S17]

In PAI, “Calcola e Visualizza Anomalie” appears after individual-policy data are complete or collective data have arrived.[S03] In DU, ARPEA distinguishes anomalies not correctable by the beneficiary/CAA, correctable by them, and signals used to close/route the instruction.[S16]

### Stage 7 — prepare the signature packet

The office generates the definitive application and compares it to the approved working record. It confirms the signer’s authority, identity document, mobile/PEC/email, and required signature mode.

Observed signature paths include:

- autograph on printed paper, retained as original;
- OTP by SMS for an enabled qualified user; at a CAA, the producer confirms with OTP and the operator confirms with a static PIN in the ARCEA description;[S22]
- FEA through AGEA Libro Firma with SPID, with progress notifications by email/PEC;[S02]
- qualified digital signature/p7m;
- graphometric signature at the fascicolo holder/office;[S12]
- procedure-specific direct signature by qualified user.

The office must not treat “signature requested” as “signed.” It monitors the signature state and recovers the completed state before release. OTP expiry, obsolete mobile, non-enabled qualified user, wrong legal representative, or altered/renamed generated PDF are separate exceptions.

### Stage 8 — release, protocol and receipt

Only release makes the application presented. Printing is not evidence of filing. Release attributes protocol number and date and creates a receipt/distinta containing CUAA, business description, definitive barcode, protocol and release date.[S05]

In two-portal Puglia cases, both sides matter: EIP send without SIAN DdS, or SIAN DdS without EIP/final document send, can be irreceivable.[S24][S25] The office therefore captures both receipts and cross-references the EIP send code and SIAN barcode.

### Stage 9 — close the filing packet and preserve evidence

The office assembles:

- signed mandate/delegations and revocation evidence;
- identity/representative evidence;
- fascicolo documents and signed validation sheet;
- application PDF and each attachment version;
- producer and technician declarations;
- portal send/release receipts, barcode/protocol/date;
- PEC delivery/acceptance receipts and portal notifications;
- screenshots/tickets for technical incidents;
- anomaly reports and corrective evidence;
- later authority requests, replies, checklists, payment and recovery documents.

The CAA conventions require secure custody and quick production to auditors. AVEPA’s vineyard manual requires originals of image-scanned paper documents to be kept for at least ten years.[S07][S12] AGEA’s access-to-acts list includes mandate, validation sheet, application, GIS base data, instruction checklists, communications and payments.[S01]

### Stage 10 — watch notices and worklists

The office’s work does not end at filing. Public evidence supports monitoring of:

- application/payment state in SIAN/OP applications;
- anomaly lists and warnings;
- DEMETRA/other campaign worklists;
- AMS contradiction windows;
- signature-state notifications;
- PEC and portal communications;
- policy/quietanza arrival and anomaly recalculation;
- concession, advance, saldo, reduction, recovery and withdrawal state;
- expiring mandates/documents and submission clocks.

The planned risk-management design explicitly calls for notifications of the 120-day automatic-application deadline, dashboards for CAA/Consorzi/insurers/AGEA/MASAF, and partial/total Excel/PDF downloads.[S04] That is strong evidence for an intended structured monitoring layer, but it should not be read as proof that every function was deployed exactly as designed at the date of this report.

### Stage 11 — answer authority requests and contradictions

When an authority asks for clarification/integration, the office identifies the clock, determines whether the requested item existed at filing, routes to member/technician/cooperative, uploads through the prescribed portal, sends any required PEC, and keeps evidence. AMS disagreement uses a formal contradiction module and back-office cover, not an informal phone explanation.[S18]

### Stage 12 — payment and claim follow-up

For ordinary support, the operator checks admissibility/concession, any advance guarantee, completion evidence, payment application/saldo and current IBAN. For insurance support, the application is based on PGIR/PAI, policy/certificate and quietanza; payment traceability and, in collective policies, the Consorzio’s transmission of aggregate quietanza plus the member’s certificate amount are critical.[S05]

If payment is delayed, the public AGREA explanation points first to anomalies and additional verification.[S20] The office should therefore distinguish:

- not yet instructed;
- blocked by known correctable anomaly;
- waiting for back office/external database;
- selected for control;
- partially admissible/reduced;
- authorized but not paid;
- payment failed/IBAN issue;
- recovery/offset;
- no public reason yet visible.

## 5. Portal automation versus human judgment

| Activity | What the portal demonstrably automates or structures | What remains human judgment/work |
|---|---|---|
| Authority | Stores mandate/delegation dates and visibility scopes | Determine correct authority, signer and conflicts; obtain legally effective documents |
| Fascicolo | Imports certified data; stores electronic facts/documents; validation workflow | Determine real-world accuracy, select evidence, resolve title/date/identity ambiguities |
| PCG/GIS | Shows land bodies; supports graphical plot editing and area computation | Decide actual boundaries, crop, succession, use and tenure |
| Prefill | Pulls fascicolo, GIS, BDN, PGIR/PAI, policy and quietanza data | Verify campaign-date truth and whether prefill belongs in the claim |
| EIP | Guided project entry, economic calculations, declared score/ranking | Design feasible investment, justify assumptions, assess permits, financial sustainability and evidence |
| Insurance | Member/collective choice, policy fields, rate calculation, anomaly calculation | Reconcile cooperative/insurer/member data and choose a supportable correction |
| Controls | Cross-database checks, blocking/warning/reduction codes, satellite signals | Interpret cause, gather cure, decide CAA versus BO route, contest when warranted |
| Signature | OTP/FEA/digital workflows, status and notifications | Identify authorized signer, choose lawful method, solve stale contacts/access problems |
| Filing | Barcode/protocol/timestamp and receipt | Ensure all required acts in all portals are complete and mutually consistent |
| Monitoring | Status pages, worklists, notifications, exports/dashboards where implemented | Prioritize cases, chase counterparties, decide escalation and document the narrative |
| Payment | Calculates requested/maximum amounts and shows payment state | Explain reductions, reconcile bank evidence, pursue missing/failed payment and preserve claim evidence |

## 6. Exception taxonomy and routing

### A. Authority and identity

- no mandate; wrong CAA; expired/suspended/revoked mandate;
- separate professional delegation missing or not profiled;
- legal representative changed/deceased;
- ID expired; CUAA/VAT/Anagrafe Tributaria mismatch;
- stale mobile/email/PEC; producer not enabled for OTP/FEA;
- conflict of interest or role/separation-of-duty issue.

**Route:** producer + fascicolo operator; CAA management for conflicts; OP helpdesk for profiling only after documents are correct.

### B. Fascicolo evidence

- missing/expired land title or date not covering operation;
- parcel duplicated/overlap; cadastral/GIS mismatch;
- crop/land-use/succession wrong;
- missing stable/BDN alignment;
- IBAN/account-holder mismatch;
- missing CCIAA/IAP/active farmer/young farmer evidence;
- antimafia subjects/declaration stale;
- document exists on paper but is not registered/protocolled or unreadable.

**Route:** producer/technician supplies facts; CAA changes allowed fascicolo data; certified-source/back-office issues are signalled to OP.

### C. Cross-portal coherence

- validated fascicolo differs from EIP or SIAN DdS;
- EIP amount/aid rate differs from DdS;
- EIP sent but DdS not released, or reverse;
- barcode/send code not cross-recorded;
- final attachments uploaded after release but not transmitted;
- document generated by portal altered/renamed and rejected.

**Route:** application compiler + technician, before deadline; use portal receipts as completion proof.

### D. Insurance/collective

- member absent from collective supply;
- wrong organism, product/common/parcel or individual/collective type;
- PAI/PGIR differs from policy/certificate;
- policy data or quietanza not yet transmitted;
- area/value/premium/cover-date mismatch;
- producer signature or threshold flag absent;
- collective policy received but still anomalous;
- premium paid but traceability document missing.

**Route:** CAA for fascicolo/individual entry; Consorzio for collective supply/quietanza; insurer for contract facts; OP for locked control output.

### E. Control and anomaly

- whole-application block (identity, active farmer, bank, antimafia);
- transversal intervention conflict/duplicate claim;
- parcel/area/title/GIS anomaly;
- livestock/BDN/pasture anomaly;
- reservation/young-farmer/title anomaly;
- AMS satellite discrepancy;
- warning only, calculated reduction, or non-correctable ineligibility;
- correction permitted only to OP back office.

**Route:** use the anomaly catalog; never “fix” by changing a true fact to silence a code. Preserve before/after state and authority response.

### F. Signature and release

- OTP never arrives/expires; phone belongs to wrong person;
- Libro Firma pending/rejected;
- digital certificate invalid; graphometric station unavailable;
- autograph missing on one annex;
- operator lacks RILASCIO role;
- printed but not released; release timestamp after deadline.

**Route:** signer/CAA access support; no assumption that a printed barcode is a protocol receipt.

### G. Technical/system

- portal unavailable/slow, upload fails, session expires, file size/format problem;
- service-to-service data stale;
- portal remains in AVVIO/POST with substantive fields incomplete;
- ticket submitted too late or lacks CUAA/application/user/error/time evidence.

**Route:** immediate helpdesk ticket and, where prescribed, PEC. AVEPA’s vineyard procedure requires a malfunction complaint by PEC within two hours with number, CUAA, anomaly, user and contact.[S12] Puglia records show the authority distinguishes a proven technical impediment from incomplete substantive work: only 40 of 52 ticketed 2024 cases received a narrow perfection window; 12 lacked a causal link because key project data were not complete.[S26]

### H. Post-filing/payment

- authority clarification/integration request;
- selected for administrative/in-loco/second-level control;
- payment reduction, partial admissibility, failed IBAN, offset/recovery;
- advance guarantee missing/invalid;
- withdrawal no longer permitted because an inaccuracy/control was notified;
- member discovers CAA error after correction window.

**Route:** case owner + office responsible; legal/insurance escalation where loss may arise. The public complaint record S32 illustrates the rework pattern: early producer instructions, late discovery of material crop/area errors, and a later compensation question.

## 7. Communications and handoffs

### Producer/member ↔ CAA

- intake checklist and missing-document list;
- explicit written request for each fascicolo update;
- validation review and signature;
- application summary and consequences of declarations;
- signature instructions and receipt delivery;
- notice/anomaly explanation and requested cure;
- payment status and reduction explanation.

### CAA ↔ technician/professional studio

- scope of delegation and portal roles;
- canonical fascicolo snapshot/version;
- parcel/crop/animal/investment facts needing professional interpretation;
- EIP versus SIAN reconciliation;
- attachment naming/signature/format and deadline matrix;
- final send code, barcode and attestations.

### CAA ↔ cooperative/Consorzio/insurer

- membership/adhesion confirmation;
- authorized data extraction or manifestation of interest;
- policy/certificate identifiers and detailed values;
- collective transmission/quietanza status;
- discrepancy list by CUAA-product-comune, with a named owner and due date.

### CAA ↔ authority/helpdesk

- formal anomaly signal/list entry or contradiction module;
- ticket with timestamp, CUAA, application ID, user, exact function, error and attachments;
- PEC where required, with delivery and acceptance receipts;
- response to document integration/control;
- second-level audit response and corrective action.

**Observed channel reality:** portals and PEC carry legal state; phone/email/helpdesk accelerate diagnosis; paper remains relevant for autograph originals and evidence that began analog. The corpus did not establish whether ordinary local offices systematically use SMS/WhatsApp, shared mailboxes or personal phones, so those practices require interviews.

## 8. Worklists, exports and monitoring evidence

Public artifacts reveal multiple fragments rather than one universal CAA queue:

1. ARPEA exposes “Lista lavorazione,” satellite monitoring, parcels and summaries in fascicolo/FAQ navigation.[S16]
2. DEMETRA and anomaly manuals create queues of blocking/correctable cases and back-office signals.[S16][S17]
3. The DU anomaly manual exposes “Excel” detail icons for livestock/pasture movement calculations.[S16]
4. AGEA’s risk-system guidelines require partial/total downloads in Excel/PDF, daily/period dashboards, payments and anomalies by associated member, and deadline notifications.[S04]
5. QDCA interoperability exposes a load-status check after mass submission.[S23]
6. Puglia determinations use portal states such as AVVIO and POST and distinguish completed, sent, incomplete and ticketed cases.[S26]
7. Signature flows notify users by email/PEC and require a later state retrieval before release.[S02]
8. SIAN/AGEA qualified-user and mobile services expose applications, payments, communications and anomaly notifications, while CAA-mediated access supplies the same case information to the member.[S22]

**Bounded finding:** the searched corpus did not expose a current, complete SIAN CAA “home workbench” manual showing all production columns, filters, bulk actions and export schemas. Evidence confirms procedure-level worklists, status, anomaly detail, notifications and some Excel/PDF capability, but not a single fully observed cross-procedure queue. Local offices likely bridge this fragmentation, but how they do so is unobserved.

## 9. Failure and rework patterns

1. **Deadline compression:** cases arrive with unresolved fascicolo facts; portal and signature work accumulates near closing time.
2. **Two-portal split-brain:** EIP is substantively complete but not sent, or DdS is released without final EIP documents/cross-link.
3. **Stale-source propagation:** incorrect fascicolo facts prefill every downstream act.
4. **Correct data, wrong date:** a current title/representative/IBAN is used even though operation-date validity differs.
5. **Invisible dependency:** collective policy/quietanza or BDN/certified-source update has not arrived, so the CAA cannot complete a downstream act.
6. **Role bottleneck:** compiler can prepare but only a smaller group can release; office learns too late that the release operator or signer is unavailable.
7. **Signature-channel failure:** obsolete mobile, missing user qualification, OTP expiry or pending Libro Firma.
8. **Receipt confusion:** printed/generated PDF is mistaken for release/protocol proof.
9. **Attachment incompleteness:** essential/non-integrable document omitted; later soccorso istruttorio is legally unavailable.
10. **Ticket without causation:** an error ticket exists, but logs show that the underlying application was still substantively incomplete. Puglia’s 40-versus-12 split is unusually clear public evidence.[S26]
11. **Correction in the wrong layer:** operator edits the application when the fascicolo must change, or opens a ticket for an error the CAA can cure.
12. **Mandate transfer discontinuity:** new CAA inherits access and anomaly responsibility but may lack the previous office’s working narrative; paper originals and revocation evidence must move.
13. **Collective reconciliation loops:** member list, policy supply, PAI/PGIR, certificate and payment evidence arrive on different clocks.
14. **Late producer discovery:** the producer sees the filed application months later and finds differences from the crop sheet/instructions, after ordinary correction windows.[S32]
15. **Audit rework:** missing signature, protocol, document validity or paper/electronic correspondence triggers corrective action, penalty or second-level follow-up.[S07][S08][S09]

## 10. What public oversight and complaints reveal

- CAA work is auditable at the **office/site and individual-file level**, not only at national-entity level. Conventions require sampling, internal audit, written procedures, separation of duties and corrective action.[S06][S07]
- Agecontrol inspectors use a SIAN application and electronic checklist; findings are recorded in real time. Correctable nonconformities can enter “ravvedimento operoso.”[S08]
- ARPEA publishes determinations approving second-level control results and contract penalties, with quality-control and PEC evidence, although some detailed annexes are omitted/redacted.[S09]
- The European Court of Auditors found the Italian insurance-support process sufficiently complex that more than 95% of insured farmers used intermediaries (CAA and Condifesa) and estimated at least €2.8 million per year in private facilitation costs for that measure at the time of audit.[S10]
- A 2025 public advice complaint describes alleged gross crop/area errors entered by a CAA despite an earlier farmer-provided worksheet and asks about compensation. It is a single reported case, not prevalence evidence.[S32]

## 11. Unobserved local practices and bounded negatives

The public corpus describes legal acts and portal mechanics much better than office choreography. The following were **not observed in the searched corpus** and should not be assumed absent:

- how cases enter (appointment, walk-in, cooperative batch, seasonal call list);
- who owns a case from intake through payment and how reassignment works;
- local status vocabulary, SLA, prioritization and aging rules;
- whether offices maintain Excel trackers, CRM, paper tickler files, shared drives or personal notes;
- how phone/WhatsApp/SMS communications are captured as evidence;
- exact batch-release and bulk-download practices;
- staffing ratios, seasonal overtime and error-review sampling before release;
- how fees are quoted, billed and allocated among CAA, association and professional technician;
- how the office reconciles member instructions against the final released PDF in practice;
- how often an operator logs in as a colleague or shares credentials (prohibited behavior may not appear in manuals);
- the actual current shape of every SIAN role/profile and the production helpdesk escalation chain;
- internal webinar/video material, association FAQs and non-public job aids;
- prevalence of each anomaly, average cycle time, first-pass yield, rework hours and payment-delay attribution.

No general claim that “SIAN lacks X” or “CAA offices do not do Y” is supportable from this corpus. The defensible statement is narrower: **the searched public materials did not expose those local operating details.**

## 12. Direct interview questions

### Intake and ownership

1. Show the last three cases exactly as they arrived. What was the first artifact: phone call, paper crop sheet, cooperative list, email, PEC or portal notice?
2. Who creates the case and who is accountable until payment? Can ownership change without losing the history?
3. What internal deadline do you use relative to the legal deadline, and who can override it?
4. Which cases are refused or deferred at intake, and how is that decision communicated?

### Mandates, delegation and identity

5. Walk through a mandate transfer from another CAA, including revocation proof and the paper file handoff.
6. How do you distinguish fascicolo mandate, application delegation, technician delegation and signature authority?
7. What are the three most common representative/identity/mobile/PEC problems? How long do they take to cure?
8. Which steps require the producer physically present, and which can be completed remotely?

### Fascicolo repair

9. Open a real recently repaired fascicolo and show every before/after field, document and timestamp.
10. Which imported “certified” data do operators most often distrust, and what evidence overrides or escalates it?
11. How do you resolve parcel geometry and crop disagreements among member, GIS imagery, title and technician?
12. What causes you to revalidate a fascicolo during the same campaign?
13. How do you prove the producer expressly requested each update?

### Technician/cooperative/member coordination

14. What is the canonical handoff package to an agronomist or professional studio?
15. Who decides the EIP’s economic assumptions and checks them against the SIAN DdS?
16. How do collaborators under a professional-studio principal work, and who reviews their entries?
17. For collective insurance, show the reconciliation from member list through policy/certificate, quietanza, anomalies and final claim.
18. What happens when the cooperative/Consorzio says its data are correct but SIAN disagrees?

### Compilation, signatures and release

19. Show a case in each signature mode you actually use. What fails most often?
20. How do STAMPA and RILASCIO roles differ in your office? Is release capacity a bottleneck?
21. What is your pre-release four-eyes check? Does anyone compare the final PDF to the member’s original crop sheet/instructions?
22. How do you prove that a document was signed, released and protocolled—not merely printed?
23. In a two-portal case, what checklist proves both submissions and their barcode/send-code linkage?

### Anomalies, notices and helpdesk

24. Export today’s anomaly/work list and explain every column, filter, status and owner.
25. Which anomaly codes are highest-volume and highest-loss? Which are noisy warnings?
26. How does an operator know whether to correct locally, change the fascicolo, contact a counterparty, open a back-office signal or file a formal contradiction?
27. Show one successful and one rejected helpdesk escalation. What evidence made the difference?
28. Who monitors PEC, portal notifications and satellite/AMS windows during leave or peak season?
29. How are phone calls and informal authority advice memorialized?

### Evidence, audit and liability

30. Pull a case selected for second-level control. How quickly can you reproduce the exact filed packet and chronology?
31. Where are paper originals stored, indexed and transferred? What is the destruction/retention rule in practice?
32. What findings recur in internal/AGEA/OP audits? Which corrective actions actually prevented recurrence?
33. When a member alleges CAA error, who investigates, who communicates, and when is insurer/legal counsel involved?
34. Can you measure cases discovered wrong only after filing, and the point at which correction became impossible?

### Payment and performance

35. Show the unpaid-case list. Can you distinguish waiting, anomalous, under control, reduced, authorized, failed-bank and recovery cases?
36. Who chases quietanze, concession acts, guarantees, advance/saldo evidence and failed payments?
37. What payment questions can the CAA answer from the portal, and which require authority contact?
38. What are median intake-to-valid-fascicolo, valid-fascicolo-to-release and release-to-payment times by procedure?
39. What percentage passes first time, and how many operator hours are consumed by rework?
40. If one system-generated worklist could replace your local tracker, what exact rows, columns, alerts, attachments and actions would it need?

## 13. Source URLs

- **S01** https://www.agea.gov.it/documents-apigw/documents/d/agea/agea-2025-0090535-allegato-istruzionioperative1222025-fascicoloaziendale2026_signed-pdf
- **S02** https://www.agea.gov.it/documents-apigw/documents/d/agea/istruzionioperative34del3042025-domandaunificata2025pdf
- **S03** https://www.sian.it/portale-apigw/documents/d/sian/manuale-utente-pai-dalla-campagna-2021-pdf
- **S04** https://www.agea.gov.it/portale-apigw/documents/d/agea/linee-guida-per-levoluzione-del-sistema-integrato-della-gestione-del-rischio-v1-3
- **S05** https://www.agea.gov.it/documents-apigw/documents/d/agea/agea-2025-0011403-allegato-ion172025-pdf
- **S06** http://arcea.it/publisher/Comunicati/CAA/Schema_Convenzione_CAA_2022.pdf
- **S07** https://www.arpea.piemonte.it/sites/default/files/pagina/21691107451O__OCANAPA_CONVENZIONE-1.pdf
- **S08** https://agecontrol.it/centri-assistenza-agricola
- **S09** https://www.arpea.piemonte.it/documentazione/det-226-30082024-approvazione-relazione-conclusiva-controlli-ii-livello-sui-caa
- **S10** https://www.eca.europa.eu/Lists/ECADocuments/SR19_23/SR_CAP_Income_stabilisation_EN.pdf
- **S11** https://www.avepa.it/servizi/competenze-regionali-delegate/fascicolo-aziendale/normativa-manuali-e-procedure/manuale-fascicolo-aziendale-indicazione-aggiornamenti-2025.pdf/@@download/file/testo%20Manuale%20fascicolo%20aziendale%202025%20evidenza%20modifiche%20V2.pdf
- **S12** https://www.avepa.it/servizi/bandi-di-finanziamento/ristrutturazione-e-riconversione-dei-vigneti-campagna-2025-2026/normativa-manuali-e-procedure/manuale-presentazione-domanda-di-aiuto-rv-2025-2026.pdf/@@download/file/Manuale%20presentazione%20domanda%20di%20aiuto%20RV%202025-2026.pdf
- **S13** https://www.avepa.it/servizi/competenze-regionali-delegate/qualifica-iap/normativa-manuali-e-procedure/estratto-da-manuale-generale-iap-ad-uso-richiedenti-ed-operatori-caa/@@download/file/Estratto%20da%20Manuale%20generale%20IAP%20-%20ad%20uso%20richiedenti%20ed%20operatori%20CAA.pdf
- **S14** https://www.avepa.it/servizi/competenze-regionali-delegate/carburanti-agricoli/manuali-e-procedure/manuale-per-la-compilazione-e-listruttoria-delle-domande-di-assegnazione-del-carburante-agricolo.pdf/@@download/file/Manuale_domande_carburante.pdf
- **S15** https://www.avepa.it/servizi/settori/aiuti-e-contributi/aiuti-di-superficie/piano-colturale-grafico-pcg
- **S16** https://www.arpea.piemonte.it/sites/default/files/documentazione/documento/222161333221O__OIO38Manualerevagosto2022.pdf
- **S17** https://www.arpea.piemonte.it/sites/default/files/documentazione/documento/21251716351O__OIstruzioniOperativeAnomalie2015-2020.pdf
- **S18** https://agrea.regione.emilia-romagna.it/novita/2025/apertura-modulo-contraddittorio-ams-du-2024
- **S19** https://agrea.regione.emilia-romagna.it/intervento/sistema-dei-controlli/controlli-amministrativi-e-in-loco
- **S20** https://agrea.regione.emilia-romagna.it/faq/pagamenti/che-cosa-puo-comportare-un-ritardo-nel-pagamento-della-mia-domanda-di-aiuto
- **S21** https://www.caaitalia.it/wp-content/uploads/2023/02/CORSO-DI-SPECIALIZZAZIONE-PER-OPERATORI-CAA-Programma.pdf
- **S22** http://www.arcea.it/index.php/istruzioni-per-la-registrazione
- **S23** https://agea.gov.it/portale-apigw/documents/d/agea/istruzioni-operative-n-58-quaderno-di-campagna-dell-agricoltore_signed
- **S24** https://psr.regione.puglia.it/documents/33128/488735/Allegato+A+Avviso+pubblico+-+Testo+Integrato+con+DAG+n.+93+del+21.06.2022.pdf/12cc57b0-1c94-5195-ef90-813524f6a8b1?t=1656328843991&version=1.1
- **S25** https://psr.regione.puglia.it/-/sottomisura-4.1-a-bando-2024-pubblicato-sul-burp-l-avviso-pubblico
- **S26** https://psr.regione.puglia.it/documents/33128/593548/Determinazione+Autorit%C3%A0+di+Gestione+n.+19+del+15.05.2024.pdf/e40495fa-618f-601a-26b3-7488e8bc33dc?t=1715786086827
- **S27** https://csr.regione.puglia.it/documents/20117/105242/DDS+n.+78+del+05.02.2025.pdf/3178dfe2-b1f6-179d-32b7-f9b3e3e5d471?t=1761301162840&version=1.1
- **S28** https://burp.regione.puglia.it/documents/20135/2703581/DET_749_29_10_2025.pdf/7dff6543-9d63-ce63-c0f6-62110f83ce7a?t=1763038669208&version=1.0
- **S29** http://manoamano.regione.puglia.it/web/guest/-/eip-elaborato-informatico-progettuale
- **S30** https://csr.regione.puglia.it/intervento-sra18-campagna-2026-avvio-dell-operativit%C3%A0-della-piattaforma-eip
- **S31** https://www.masaf.gov.it/flex/cm/pages/ServeAttachment.php/L/IT/D/1%252F5%252Fd%252FD.307582fc02e7c2ea3278/P/BLOB%3AID%3D23803/E/pdf?mode=download
- **S32** https://terraevita.edagricole.it/esperto-risponde/caa-si-puo-chiedere-il-risarcimento/

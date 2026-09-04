# Web operator practice: the less-visible workflow behind collective olive recovery

## Scope and method

This report reconstructs how cooperative, OP, CAA, technical, public-administration, field, supplier, and finance actors actually coordinate land, funding, applications, work, and payment. It uses public operating manuals, calls and FAQs, implementation notices, payment guides, court decisions, cooperative service pages, software products, audit material, nursery rules, and comparable CAP workflows.

The five starting assertions are treated as hypotheses, not requirements. Every substantive point below is labelled:

- **Fact**: directly supported by a cited source.
- **Inference**: a workflow conclusion drawn from one or more facts. It is not claimed as directly observed at a named cooperative unless the source says so.
- **Unresolved**: a question that public sources do not answer.

Italian terms used throughout:

- **OP**: *Organizzazione di Produttori*, producer organisation.
- **CAA**: *Centro Autorizzato di Assistenza Agricola*, an authorised agricultural assistance centre.
- **fascicolo aziendale**: the official farm dossier/master record, including identity, land, titles, crops, and other durable farm data.
- **CUAA**: the farm’s unique tax-based identifier.
- **SIAN**: *Sistema Informativo Agricolo Nazionale*, the national agricultural information system.
- **EIP/PMA**: Puglia’s regional project/application portal at `pma.regione.puglia.it`; in Puglia material, EIP often means *Elaborato Informatico Progettuale*.
- **DdS**: *domanda di sostegno*, support application.
- **DdP**: *domanda di pagamento*, payment claim.
- **SAL**: *stato di avanzamento lavori*, work-progress stage/payment.
- **PEC**: *posta elettronica certificata*, legally certified email.
- **DDS/DET**: regional managerial determination/order.
- **DURC**: certificate of social-security contribution compliance.
- **RUOP**: official register of professional plant operators.
- **espianto/estirpazione**: removal/uprooting; the exact legal and operational meaning varies by measure and order.
- **subentro**: succession/substitution into an application, for example after death.
- **scorrimento**: movement down a ranked list when more budget or capacity becomes available.

## Search and fetch log

### Search families run

The research deliberately expanded beyond the official replanting measure. Searches were run in Italian and English across these families:

1. `Puglia rigenerazione olivicola domande CAA istruttoria graduatoria pagamenti AGEA ritardi`
2. `PSR Puglia domanda sostegno CAA fascicolo aziendale preventivi PEC istruttoria manuale`
3. `CAA agronomo pratica contributi agricoli documenti SIAN problemi portale`
4. `organizzazione produttori olivicoli servizi domande contributi reimpianto Xylella`
5. `cooperativa olivicola Puglia espianto reimpianto gestione lavori conto terzi`
6. `domanda di aiuto collettiva reimpianto olivi FAQ`
7. `domande di adesione reimpianto olivi collettive`
8. `soggetto collettivo reimpianto Xylella cooperativa`
9. `Reimpianto olivi zona infetta titolo di possesso / autorizzazione proprietario / fatture / saldo / anticipo / fideiussione / variante / rinuncia / subentro`
10. `ARIF Puglia estirpazione piante infette ordinanze proprietari esecuzione lavori`
11. `Xylella ordinanza estirpazione ricorso TAR proprietario Puglia`
12. `Puglia olivi monumentali autorizzazione espianto reimpianto Xylella`
13. `appalto lavori estirpazione Xylella Puglia capitolato mezzi smaltimento`
14. `vivai autorizzati Xylella passaporto piante reimpianto disponibilità cultivar`
15. `Xylella certified olive plants shortage nursery Puglia`
16. `contoterzisti agricoli Puglia lavori oliveto programmazione`
17. `OP olive operational programme member applications field technicians Italy`
18. `organizzazioni produttori olivicoli programma operativo rendicontazione controlli spese`
19. `agronomo domanda PSR sopralluogo SAL collaudo pagamento Puglia`
20. `bandi agricoltura domanda sostegno domanda pagamento SAL tecnico CAA workflow`
21. `quaderno di campagna software cooperativa tracciabilità lavori agricoli`
22. `software gestione cooperative agricole soci conferimenti pratiche contributi`
23. `QdCA SIAN interoperabilità software cooperative agronomi`
24. `AGEA audit pagamenti agricoli ritardi controlli fascicolo grafico SIGC`
25. `Corte dei conti AGEA ritardi pagamenti agricoltura controlli`
26. `Commissione UE audit Italy paying agency AGEA agricultural payments delays`
27. `AKIS farm advisory services CAP applications administrative burden Italy`
28. `EU CAP beneficiary interviews digital portal administrative burden advisors`
29. `collective agricultural grant application workflow Europe`
30. Named-operator searches for Olearia AIPO Puglia, Assoproli, AIPOL, OP Latium, AgerTech, ISAGRI, and AssoSoftware.

Search results were followed to adjacent terms including *domanda di adesione*, *mandato ad eseguire*, *quadro B1*, *errore palese*, *rettifica domanda*, *stampa definitiva*, *rilascio con OTP*, *garanzia fideiussoria*, *contratto di fornitura*, *virus esente*, *elenco di liquidazione*, *registro debitori*, *quietanza liberatoria*, *esecuzione in danno*, *subentro per decesso*, and *interoperabilità*.

### Fetch methods

- Search snippets were used only for discovery or for facts literally present in the snippet.
- HTML pages were fetched directly and stripped to rendered text.
- PDFs were fetched directly and converted in memory with `pdftotext`; no local source corpus was created.
- The public SIAN Xylella user manual was recovered from a mirror because the primary operational manual is placed in a restricted/portal context.
- Official, operator, vendor, court, audit, and comparable-region sources were triangulated where possible.

### Fetch failures and limitations

1. A batch extraction service hit a per-minute rate limit for 25 attempted Puglia, AGEA, EU CAP, court, and CAA pages. The same URLs were then fetched directly; the rate-limit itself did not prevent recovery of the principal sources.
2. The 2026 AGEA fascicolo instructions returned HTTP 403 to direct retrieval, although the search index exposed a substantial text extract. Claims about the CAA role are therefore anchored primarily to Region Puglia and ARPEA pages rather than that PDF.
3. AgerTech’s cooperative page returned HTTP 403 and its about page produced an SSL EOF error on direct fetch. Only the search-result text is used, and it is explicitly treated as vendor positioning rather than adoption evidence.
4. The Constitutional Court result page for judgment 74/2021 returned little useful body text through the simple extractor. The search result established only the narrow proposition that the challenged regional blanket derogation from landscape constraints was unconstitutional; this report does not rely on details beyond that.
5. The Regione Puglia replanting call and FAQ were machine-readable. Some later determinations use complex PDF layouts; targeted text was recoverable, but page-perfect tables were not reconstructed.
6. Public sources reveal formal handoffs and some operational detail, but not a named cooperative’s internal inboxes, spreadsheet templates, call logs, staff utilisation, contractor calendar, or management accounts. Those remain interview targets.

## Executive findings

### What operators actually appear to optimise

**Inference.** The operative goal is not “determine eligibility.” It is to preserve a credible path from a member’s land position to a paid, physically completed project while spending scarce staff attention only on cases that can survive the next gate. Operators manage a portfolio of cases with different clocks: legal-notification clocks, application-window clocks, nursery and field-season clocks, grant-completion clocks, and payment-control clocks.

**Fact.** A collective replant application is not one grant to the cooperative. Each adhering person remains the beneficiary; each needs a valid farm dossier and, for an advance, each must obtain its own guarantee. The OP/cooperative can choose which adhesion applications to include after negotiations, and an adhesion not included falls back to individual treatment rather than disappearing. The OP/cooperative receives a mandate to carry out uprooting and replanting, and evidence of that mandate is required at payment or final balance on pain of revocation ([FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524); [consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182)).

**Inference.** The real unit of work is therefore a **member–parcel–intervention–evidence case inside a collective portfolio**, not simply “land,” “funding,” “application,” “field order,” or “payment.” The cooperative is an orchestrator and contracting party for execution, but many liabilities, authorisations, and cash constraints stay attached to the individual beneficiary.

### The hidden workflow is hybrid, not portal-native

**Fact.** The SIAN flow preloads immutable master data from the farm register, runs anomaly checks, assigns states such as “in compilation with inconsistencies,” supports provisional and definitive printing, releases the case with protocol, uses an OTP valid for two minutes, allows rectification, and offers office-level monitors exportable to Excel. The collective module opened only after the adhesion window closed ([SIAN Xylella manual mirror](https://it.readkong.com/page/sin-emergenza-xylella-aiuto-alle-imprese-agricole-art-6-4221541)).

**Fact.** Other Puglia workflows combine SIAN with PEC, manually signed/scanned confirmations, separate regional portals, and even original paper guarantees. For one PSR call, three consultant quotations had to be managed in SIAN, then the selected consultant’s delegation and attachments had to be sent by PEC for enablement ([Puglia preventivi/delegation clarification](https://psr.regione.puglia.it/-/bando-sottomisura-7.6-chiarimenti-per-la-gestione-dei-preventivi-di-individuazione-consulenti-tecnici-e-successiva-delega)). The replant advance required submission through PMA/EIP plus the original guarantee to the regional office within ten days ([DDS 380/2022](https://www.regione.puglia.it/documents/736605/3203897/DDS+n.+380+del+01.06.2022.pdf/13473a2c-dc6e-a672-df63-fadab7740607?t=1655799771123)).

**Inference.** “Portal submission” is one checkpoint in a human-controlled document relay. Operators need a control sheet outside the portal to track source documents, missing signatures, delegated access, portal state, protocol receipt, PEC delivery, and original-paper delivery. The official SIAN Excel export is direct evidence that office users need off-portal work queues; it is not proof that every cooperative uses a bespoke spreadsheet.

### Field execution is constrained by procurement and evidence, not merely by an award

**Fact.** Puglia extended completion terms by six months after an interruption of EIP operation caused by expiry of an assistance contract. A further nursery-related extension of up to 18 months required a digitally signed supply contract with a RUOP-registered professional operator committing to provide certified resistant olive plants within the extension period ([DDS 86/2023](https://www.regione.puglia.it/documents/736605/5332584/DET_86_5_8_2023.pdf/67a7e5db-32d4-042d-eeb1-7087797da30b?t=1693227259679)).

**Inference.** A concession does not prepare a job for dispatch. A field-ready case also needs an executable parcel list, land access and owner consents, a compliant technical design, nursery allocation, contractor capacity, equipment and disposal plan, schedule, cost/cash plan, evidence plan, and a change-control path.

### Payment is a second dossier and a serial control chain

**Fact.** Comparable Italian paying-agency guidance shows a payment claim normally passes from the CAA to a delegated instructing body, to a technical liquidation list, administrative controls (for example DURC, antimafia, guarantees), debt-register checks and possible compensation, authorisation, order signing, execution, treasury, and payment receipt. Wrong bank details or death trigger contact with the CAA/farm and reissue ([Lombardy paying-agency process](https://opr.regione.lombardia.it/it/organismo-pagatore-regionale/per-gli-agricoltori/quali-sono-le-fasi-del-processo-di-pagamento)).

**Fact.** Puglia payment documentation can require a detailed activity report, partner expense summary, invoices, bank transfer evidence, supplier releases, dedicated-account statements, contracts, payroll, F24 evidence, and time sheets ([Puglia DdP document crosswalk](https://psr.regione.puglia.it/documents/33128/62654/Domande+di+pagamento+-+Tabella+di+raccordo+documenti.pdf/bdc33b90-0a58-0271-09ba-554cccdddac1?t=1567778664944&version=1.0)).

**Inference.** Finance authorisation is late in the chain. The dominant work is earlier: engineering an admissible evidence package and reconciling physical work, approved scope, invoices, payments, supplier declarations, beneficiary identity, and public-control status.

## Operator and actor map

| Actor | What public sources show | Less-visible operational role (inference where noted) | Key handoffs |
|---|---|---|---|
| Individual beneficiary/member | Holds or conducts land, validates the fascicolo, signs the adhesion/application, receives the award, may obtain an individual guarantee, must authorise work and preserve eligibility | Supplies missing title/identity/bank/owner documents; decides whether cash, delay, and commitments are tolerable | CAA, OP/cooperative, owner/co-owner, bank/insurer, technician |
| Owner/co-owner/naked owner | Authorisation may be needed for leased, loaned, or usufruct land ([2025 concession act](https://foreste.regione.puglia.it/documents/736605/3409746/181_DIR_2025_00120_DeterminaPUB+%281%29.pdf/d7735ada-2b6d-2e58-06e5-463b9576edb0?t=1752828606764)) | A common exception source when land occupation and legal ownership diverge | Beneficiary, CAA, technician, cooperative |
| Cooperative / olive OP | Can file a collective application, select adhering members, and receive a mandate to conduct uprooting and replanting; OPs also provide agronomic, grant, traceability, CAA, purchasing, and marketing services ([FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524); [Olearia AIPO](https://www.oleariaaipopuglia.it/servizi-nuovo); [Assoproli](https://www.assoproli.it/servizi/)) | Portfolio owner; negotiates member inclusion, batches procurement, balances service cost and member value, allocates staff and contractors, manages exceptions | Member list, mandates, CAA/technician, suppliers, contractors, region |
| CAA | Private mandated body delegated to instruct farm dossiers and manage support applications; verifies completeness and resolves dossier-linked anomalies ([Region Puglia CAA](https://filiereagroalimentari.regione.puglia.it/centri-di-assistenza-agricola); [ARPEA](https://www.arpea.piemonte.it/come-fare-per/centri-assistenza-agricola-caa)) | Master-data steward and submission operator; often the practical help desk and state interpreter | Fascicolo, SIAN, farmer/member, OP, paying body |
| Accredited agronomist/technician | Can be delegated to consult the dossier and compile/release applications; performs designs, field advice, monitoring, and site visits ([Puglia consultant call](https://psr.regione.puglia.it/documents/33128/88963/Determinazione+Autorit%C3%A0+di+Gestione+n.+91+del+20.06.2022.pdf/5abd6c1b-8760-61c3-62ed-b35c5a14562a?t=1699375366415&version=1.4); [AIPOL field service](https://aipol.bs.it/servizio-assistenza-tecnica.php)) | Converts legal/financial eligibility into a buildable orchard and later certifiable completion; triages whether a site is worth pursuing | CAA, cooperative manager, member, contractor, nursery, inspector |
| Cooperative manager / legal representative | Signs/authorises the collective application and acts under members’ mandates | Makes inclusion, sequencing, procurement, resource, and exception-escalation decisions | Board/member, application team, field team, finance |
| Board/authorised representative | OP governance rules and grant portals reserve initiation/certification to authorised representatives | Owns consequence-bearing approvals: member selection, obligations, contracts, submissions, changes, payment certifications | Manager, legal, finance |
| Regione Puglia / measure office | Publishes call, ranking, scrolls, concessions, implementation rules, deadlines, variants, payment liquidations | Policy owner and exception adjudicator; relies on website/BURP publication as legal notification | ARIF, CAA/technician, beneficiary, accounting |
| ARIF | Performs technical-administrative instruction for the replant measure; executes/controls phytosanitary removals; instructs/liquidates removal indemnities ([DDS 380/2022](https://www.regione.puglia.it/documents/736605/3203897/DDS+n.+380+del+01.06.2022.pdf/13473a2c-dc6e-a672-df63-fadab7740607?t=1655799771123); [ARIF removals](https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/)) | Capacity-limited inspection and evidence-production node; not just a field-work executor | Lab/observatory, region, owner, contractor, beneficiary |
| Phytosanitary observatory | Issues official zone and removal orders; sets procedures; communicates through BURP, portals, municipal posting, and sometimes PEC | Legal-state authority and escalation owner | Lab/InnovaPuglia, ARIF, municipality, owner/occupier |
| Laboratory/CNR and monitoring system | Lab result triggers cadastral identification and official action ([ARIF removals](https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/)) | Upstream event source whose identifiers must survive downstream | Field sample, parcel/owner matching, order |
| Municipality | Posts orders in the *albo pretorio*; publication can be sufficient legal notice ([TAR Puglia 1640/2019](https://www.ambientediritto.it/giurisprudenza/tar-puglia-bari-sez-3-12-dicembre-2019-n-1640/)) | A notification channel that can be legally valid but operationally weak | Observatory, owner/occupier, ARIF |
| Nursery / RUOP professional operator | Supplies plant material and plant passports; a certified-plant extension requires a signed supply contract ([DDS 86/2023](https://www.regione.puglia.it/documents/736605/5332584/DET_86_5_8_2023.pdf/67a7e5db-32d4-042d-eeb1-7087797da30b?t=1693227259679); [Puglia nursery movement rules](https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf)) | Capacity reservation, traceability, substitution/lead-time management | Technician, manager, field crew, payment evidence |
| Contractor/contoterzista | Provides machinery and labour for removal, soil work, planting, irrigation, and later care; public procurement exists for anti-Xylella tillage/mowing ([Agenzia del Demanio procurement](https://www.agenziademanio.it/it/gare-aste/forniture-e-servizi/gara/Servizi-di-aratura-e-sfalcio-erba-al-fine-di-contrastare-lemergenza-della-Xylella-Fastidiosa-nella-Regione-Puglia)) | Converts parcel batches into route, crew, equipment, access, and weather schedules | Manager, technician, member, inspector, supplier |
| Bank/insurer/guarantor | Issues a guarantee of 110% of the requested advance; in collective cases the individual beneficiary provides it ([DDS 380/2022](https://www.regione.puglia.it/documents/736605/3203897/DDS+n.+380+del+01.06.2022.pdf/13473a2c-dc6e-a672-df63-fadab7740607?t=1655799771123); [FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524)) | Credit gate that can make a technically eligible member non-executable | Beneficiary, finance, region |
| Finance/accounting | Builds payment evidence, reconciles costs and payments, supports claims | Starts before field work by defining admissible purchase/payment/evidence paths | Manager, suppliers, contractors, CAA, paying authority |
| Paying body / regional accounting / treasury | Runs administrative controls, debt checks, authorisation, order, execution, and treasury settlement ([Lombardy payment process](https://opr.regione.lombardia.it/it/organismo-pagatore-regionale/per-gli-agricoltori/quali-sono-le-fasi-del-processo-di-pagamento)) | Serial control chain; exceptions return to CAA/beneficiary | Instructor, finance, beneficiary bank |
| Inspector/field verifier | Confirms removals/work; the removal record can be indispensable for indemnity ([Bitonto DET 3/2026](https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0)) | Converts physical reality into payable evidence | Field crew, ARIF/region, finance |

## Jobs to be done

### Member-facing jobs

1. Tell a member what the official state means for each parcel and what must or may happen next.
2. Identify the exact missing item that blocks action: title, owner authorisation, dossier update, bank detail, mandate, supply contract, or technical fact.
3. Protect the member from missing a deadline that may be triggered only by website/BURP publication.
4. Explain the difference between “eligible in principle,” “submitted,” “ranked,” “admitted to instruction,” “conceded,” “field-ready,” and “payable.”
5. Minimise repeated collection of the same identity, land, and field-operation data.
6. Make the member’s financial exposure visible: own contribution, guarantee requirement, working capital, risk of reduction/revocation, and timing uncertainty.

### Cooperative/OP jobs

1. Build and maintain a complete candidate inventory without pretending every candidate is application-ready.
2. Decide which members to include based on legal eligibility, execution feasibility, member mandate, cash/credit, strategic fit, staff capacity, and expected benefit.
3. Batch similar work while preserving member-level accountability and evidence.
4. Allocate scarce technician, contractor, nursery, and finance capacity against multiple deadlines.
5. Detect when a change in land, ownership, official state, supplier, design, or timing invalidates earlier assumptions.
6. Maintain a defensible chain from source act to parcel decision to authorised application to completed work to payment evidence.

### CAA/application-team jobs

1. Keep the fascicolo authoritative enough for downstream forms.
2. Resolve land/title/crop/anagraphic anomalies before release.
3. Control delegations, portal permissions, signatures, OTP, definitive print, protocol, PEC, and attachments.
4. Distinguish a portal validation from substantive admissibility.
5. Run a deadline queue and exception queue, including website-only notifications.
6. Preserve a reproducible copy of exactly what was filed.

### Field-team jobs

1. Turn an award or phytosanitary order into a safe, legal, schedulable field package.
2. Reserve certified material and contractors before seasonal windows close.
3. Plan access, routing, equipment, removal/destruction, planting, irrigation, and follow-up care.
4. Capture evidence contemporaneously rather than reconstruct it at payment time.
5. Escalate variants and delays before work diverges from approved scope.

### Finance/payment jobs

1. Prevent ineligible procurement or payment methods before money is spent.
2. Reconcile approved scope, actual work, invoices, bank evidence, supplier releases, and inspection records.
3. Forecast cash gaps and guarantee constraints per member.
4. Submit a complete DdP and track it through instruction, administrative controls, debt offsets, authorisation, and execution.
5. Repair payment failures caused by bank data, death/subentro, DURC, antimafia, guarantee, debt, or document mismatch.

## Detailed practice workflow 1: land, official state, duties, and access

### A. Intake and master-data alignment

1. **Fact.** Before an individual application or adhesion, the applicant must constitute, update, and validate the fascicolo; the replant call requires conducted surfaces, crops, the exact number of olive trees per parcel, and a valid PEC. The farm dossier is the reference for land, title, and instruction ([consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182)).
2. **Fact.** CAA staff acquire, verify, and update dossier documents and treat anomalies caused by stale dossier data ([ARPEA CAA](https://www.arpea.piemonte.it/come-fare-per/centri-assistenza-agricola-caa)).
3. **Inference.** The practical first screen is not GIS. It is identity–title–parcel reconciliation: “Is this the same person, legal holding, and parcel that the public systems recognise?”
4. **Inference.** Operators likely maintain an off-portal exception list for expired or unregistered leases, co-ownership, deceased holders, inconsistent cadastral references, missing PEC, and parcels absent from the farm dossier. Public sources do not expose the local template.

### B. Determine official legal-geographic state

1. **Fact.** The replant measure applies only in the specified infected zone and excludes the containment area; official orders can distinguish eradication from containment at parcel/radius level ([consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182); [Bitonto DET 3/2026](https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0)).
2. **Fact.** A laboratory result flows through cadastral identification and ownership matching before the phytosanitary authority issues an injunctive act ([ARIF removals](https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/)).
3. **Inference.** Operators need a dated snapshot, not a timeless parcel label. “Official status” is act- and date-relative and may coexist with grant geography, phytosanitary duty, landscape/monumentality status, and farm-dossier claims.

### C. Explain duties and establish the responsible person

1. **Fact.** A 2026 order requires the listed owner/occupier to report an ownership change within three days after publication and prescribes removal of the infected tree and specified surrounding plants. It provides a choice between voluntary removal and ARIF execution through a SPID portal, followed by short execution deadlines ([Bitonto DET 3/2026](https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0)).
2. **Fact.** The order is notified by seven-day municipal posting and, where available, PEC. If the owner does not respond, ARIF proceeds; refusal can lead to forced removal, costs charged to the owner, administrative sanction, and referral ([Bitonto DET 3/2026](https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0)).
3. **Fact.** A TAR decision held that municipal posting alone could be sufficient even where the occupier said he learned of the order only when ARIF arrived ([TAR Puglia 1640/2019](https://www.ambientediritto.it/giurisprudenza/tar-puglia-bari-sez-3-12-dicembre-2019-n-1640/)).
4. **Inference.** Legal notification and operational awareness are different states. A cooperative should not model “published” as “member knows” or “access is arranged.” A human outreach/acknowledgement loop remains necessary.

### D. Resolve access, owner consent, and special status

1. **Fact.** Non-owner applicants need owner/co-owner or naked-owner authorisation in relevant lease, loan, or usufruct cases ([2025 concession act](https://foreste.regione.puglia.it/documents/736605/3409746/181_DIR_2025_00120_DeterminaPUB+%281%29.pdf/d7735ada-2b6d-2e58-06e5-463b9576edb0?t=1752828606764)).
2. **Fact.** Monumental status can constrain removal; courts have required its verification before removal of healthy trees in a buffer context ([Rai report on TAR ruling](https://www.rainews.it/archivio-rainews/articoli/Xylella-Tar-verifica-monumentalita-prima-di-abbattere-016b8193-afe4-4222-9c59-7d9fc3884117.html)).
3. **Inference.** “Land explains official status/duties” is directionally right only if Land includes dated authority, title, responsible person, notification, consent, access, monumentality/constraints, and unresolved conflicts. A parcel polygon plus zone label is inadequate.

### E. Handoff to field work

A field handoff is ready only when it includes:

- parcel and access-point identity;
- source act and deadline;
- responsible owner/occupier and acknowledgement;
- voluntary-versus-ARIF choice;
- plants/intervention scope;
- special constraints and required supervision;
- disposition of branches, foliage, and wood;
- evidence/verbale requirement;
- contact and escalation path.

**Fact.** Official removal instructions require mechanical removal, in-place destruction of leafy material, availability of debranched wood to the owner, supervision, and an official record necessary for the contribution ([Bitonto DET 3/2026](https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0)).

### Hypothesis verdict for function 1

- **Confirmation:** Land/legal-state work should explain official status and duties; execution needs a distinct field package.
- **Challenge:** Ownership, consent, notification acknowledgement, access, and duty response are not passive “Land” facts. They are active case-management steps that can block execution.
- **Recommended framing:** `Legal/land case -> acknowledged duty/permission -> field-ready work package`, with versioned status and an exception owner.

## Detailed practice workflow 2: funding discovery, eligibility, prioritisation, and pursuit

### A. Create the candidate population

1. Start with the cooperative/OP member base and known non-member prospects where allowed.
2. Join each member to current fascicolo/parcel coverage.
3. Add relevant open and potential windows, budget, geography, beneficiary class, intervention, cost standard, selection criteria, aid cap, and timing.
4. Record **eligible**, **ineligible**, and **unresolved** per member–parcel–intervention, with the blocking fact and source.

**Inference.** A complete internal candidate population is valuable, but the official population is opt-in. Public workflow begins with individual adhesion/support applications, not an automatically generated universe.

### B. Compute legal and administrative eligibility

**Fact.** The call accepts owners, holders, or occupiers under qualifying title, including non-economic subjects, but requires a valid fascicolo and qualifying geography. It applies standard costs, individual and collective thresholds, selection principles, and technical-administrative instruction ([consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182); [FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524)).

**Inference.** Eligibility computation should separate:

- legal beneficiary eligibility;
- parcel/geography eligibility;
- intervention eligibility;
- documentary readiness;
- selection score/priority;
- budget likelihood;
- execution feasibility;
- cash/guarantee feasibility;
- strategic willingness.

Collapsing these into one Boolean hides the reason a cooperative should or should not pursue a case.

### C. Cooperative inclusion decision

1. **Fact.** The OP/cooperative sees adhesion applications and can select only some members for whom, after negotiations, it intends to exercise the work mandate. Adhesions not called into the collective application are treated as individual applications. Incorrect CUAA association can also push a case into individual treatment ([FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524)).
2. **Fact.** The consolidated call requires a member declaration approving the initiative, delegating the legal representative to file, and mandating execution ([consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182)).
3. **Inference.** “Whether to pursue” is a negotiated portfolio decision, not a post-computation button. It depends on member mandate, cooperative capacity, geographic batchability, technical design, plant supply, contractor route efficiency, own contribution, guarantee access, and risk.
4. **Inference.** The decision should be recorded with a reason code and expiry date. A non-pursuit today may become viable after a budget scroll, dossier repair, owner consent, or supplier allocation.

### D. Rank under uncertainty and budget movement

1. **Fact.** The 2021 publication separated individual rankings, collective rankings, and adhesion lists ([ranking notice](https://www.regione.puglia.it/web/rigenerazione-olivicola/-/bando-reimpianto-ulivi-in-zona-infetta-le-graduatorie-e-l-elenco-delle-domande-ammesse-all-istruttoria)).
2. **Fact.** Later budget scrolls admit additional ranked individual applications to instruction. A 2026 scroll admitted positions 3355–3758 and imposed a 30-day delegation upload, with failure treated as implicit withdrawal; the region later reopened the window for ten days ([2026 scroll](https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-scorrimento-della-graduatoria-1); [reopening](https://politiche-energetiche.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-determinazione-dirigenziale-n.-53-del-30.03.26-di-scorrimento-della-graduatoria-riapertura-termini-per-inserimento-delega)).
3. **Fact.** In 2022 the Region reported collective demand of about €22.6 million and individual demand of about €200 million, while explaining that instruction required more technical assistance and software and that DURC/antimafia checks slowed the process ([implementation statement](https://press.regione.puglia.it/-/reimpianti-ulivi-in-zona-infetta-da-xylella-lo-stato-di-attuazione-dell-avviso-pubblico)).
4. **Inference.** A “not funded” case remains a live option. Operators need dormant-case monitoring, not closure, because a scroll can reactivate years-old applicants under a short clock.

### E. Cash and credit feasibility

1. **Fact.** An advance is limited to 50% and requires a 110% bank/insurance guarantee. In a collective application, each member beneficiary supplies its own guarantee ([DDS 380/2022](https://www.regione.puglia.it/documents/736605/3203897/DDS+n.+380+del+01.06.2022.pdf/13473a2c-dc6e-a672-df63-fadab7740607?t=1655799771123); [FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524)).
2. **Inference.** The cooperative cannot infer execution from award amount alone. It needs a member-level financing state: no advance / advance requested / guarantee pending / guarantee accepted / own contribution available / supplier terms / cash gap.

### Hypothesis verdict for function 2

- **Confirmation:** Computing eligible, ineligible, and unresolved cases before a pursuit decision is useful.
- **Challenge:** The “complete population” is internal and provisional, not official. Eligibility alone does not determine inclusion. Adhesion, mandate, credit, technical feasibility, and capacity are first-class.
- **Recommended framing:** `Candidate universe -> multi-dimensional readiness -> negotiated inclusion -> live option portfolio`, not `funding computes -> cooperative yes/no`.

## Detailed practice workflow 3: application preparation, exception resolution, and authorisation

### A. Establish representation and system access

1. Obtain the member’s CAA mandate or professional delegation.
2. Ensure the CAA/professional is enabled for the correct SIAN/EIP procedure.
3. Validate the applicant’s PEC, digital-signature/qualified-user status, and phone/app path for OTP.
4. For a collective case, establish the cooperative’s fascicolo and valid relationship to the adhering member.

**Fact.** CAA and accredited professionals can prepare applications, but professional access can require separate regional credentials, delegation, and PEC attachments. CAA bodies act under member mandate ([Puglia consultant call](https://psr.regione.puglia.it/documents/33128/88963/Determinazione+Autorit%C3%A0+di+Gestione+n.+91+del+20.06.2022.pdf/5abd6c1b-8760-61c3-62ed-b35c5a14562a?t=1699375366415&version=1.4); [Region Puglia CAA](https://filiereagroalimentari.regione.puglia.it/centri-di-assistenza-agricola)).

### B. Prepare the underlying dossier before the form

1. Update identity, title, surfaces, crops, trees, bank data, legal representative, and PEC.
2. Collect owner consent, co-owner consent, mandate, declarations, and technical inputs.
3. Resolve dossier-linked anomalies with the CAA.
4. Preserve evidence for data not represented in the portal.

**Fact.** The SIAN application reads anagraphic data from the farm register and does not allow it to be edited in the form. Rectification after release can regenerate the application from the newest dossier snapshot ([SIAN Xylella manual](https://it.readkong.com/page/sin-emergenza-xylella-aiuto-alle-imprese-agricole-art-6-4221541)).

**Inference.** Fixing the form is often the wrong repair. The root correction belongs in the fascicolo or source register; otherwise the next generated form can reintroduce the mismatch.

### C. Compile and validate

1. Create individual support/adhesion applications first.
2. Enter parcel/intervention data and the association CUAA for adhesion.
3. Run system anomaly calculations.
4. Resolve blocking inconsistencies and record non-blocking warnings.
5. Produce provisional print for human review.
6. For the collective application, wait until the adhesion period closes, review the member list, and select members to include.

**Fact.** The 2020 manual exposes “in compilation,” “in compilation with inconsistencies,” “printed,” “released,” and rectified states. It validates, among other things, association CUAA, open fascicolo, parcel intervention counts, and required sections. Office users can monitor applications and anomalies and export lists to Excel ([SIAN Xylella manual](https://it.readkong.com/page/sin-emergenza-xylella-aiuto-alle-imprese-agricole-art-6-4221541)).

**Inference.** System validation automates syntactic and cross-field controls. It does not decide owner consent validity, monumentality, document credibility, execution feasibility, or whether the cooperative should accept a member.

### D. Human exception resolution

Typical exception classes are:

- stale/invalid land title;
- owner/co-owner consent missing;
- member–cooperative CUAA mismatch;
- applicant not in the OP base or wrong cooperative;
- parcel/crop/tree count inconsistent with intended design;
- digital signature or OTP enrolment failure;
- CAA/professional not enabled;
- source document missing or not digitally signed;
- amount/threshold excess requiring technical adaptation;
- legal or geographic ambiguity;
- deadline/portal malfunction.

**Fact.** The call directs users to report SIAN anomalies at closure by PEC so AGEA can verify them and the portal may be reopened. Enablement requests stop before the final nine days ([consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182)).

**Fact.** Comparable Puglia calls use at least three portal quotations, protocol, delegation, and PEC enablement, demonstrating that exception resolution crosses system boundaries ([Puglia preventivi/delegation clarification](https://psr.regione.puglia.it/-/bando-sottomisura-7.6-chiarimenti-per-la-gestione-dei-preventivi-di-individuazione-consulenti-tecnici-e-successiva-delega)).

### E. Consequence-bearing review and release

1. Produce a final review packet: member, parcels, intervention, requested aid, declarations, mandates, unresolved warnings, and exact submission deadline.
2. Obtain the correct authorisation from the member and collective legal representative.
3. Create definitive print/barcode.
4. Release and protocol using OTP, app OTP, permitted delayed signature, or digital signature.
5. Save protocol receipt and filed PDF.
6. Send any required PEC and original documents.
7. Move the case to “submitted—awaiting instruction,” not “approved.”

**Fact.** In the manual, “release” activates the administrative proceeding and assigns protocol. The two-minute OTP is supplied by the producer and entered by the operator. A rectification creates a new in-compilation application and marks the earlier release as rectified ([SIAN Xylella manual](https://it.readkong.com/page/sin-emergenza-xylella-aiuto-alle-imprese-agricole-art-6-4221541)).

**Inference.** The operator prepares and transacts the submission; the beneficiary/authorised representative owns the truth certification and consequences. “Operator authorises” is therefore too broad unless “operator” means the legally authorised person.

### F. Post-submission instruction and rework

1. Monitor ranking/admission, PEC, website notices, and short reactivation windows.
2. Respond to requests for additions.
3. Handle adverse pre-notice and request reconsideration.
4. Repair obvious error, amend technical scope, or submit rectification where allowed.
5. Track concession conditions as new obligations.

**Fact.** The call allows the administration to request additional documentation, communicates negative instruction results by PEC, and permits reconsideration. It also provides technical adaptation when calculated aid exceeds thresholds ([consolidated call](https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182)).

### Hypothesis verdict for function 3

- **Confirmation:** A system can prebuild dossiers; humans should resolve exceptions and give consequence-bearing authorisation.
- **Challenge:** Preparation is distributed across CAA, technician, cooperative, member, and source registers. The portal’s release, protocol, PEC, and original-paper steps are part of the work, not an afterthought.
- **Recommended framing:** `Dossier assembly -> source-data repair -> machine validation -> human exception adjudication -> authorised release -> instruction/rework`.

## Detailed practice workflow 4: field operations, scheduling, assignment, and evidence

### A. Convert legal/award output into a field-ready package

For each member–parcel case, assemble:

- approved or ordered intervention and quantities;
- parcel geometry, access, and owner consent;
- technical orchard design and permitted variants;
- responsible technician;
- nursery, cultivar/category, quantity, plant passport, and delivery date;
- removal/soil/planting/irrigation activities;
- contractor, crew, equipment, and safety requirements;
- disposal/destruction method;
- start and completion deadlines;
- inspection and evidence requirements;
- approved budget and member cash/advance state.

**Fact.** The collective mandate is to contribute to/carry out uprooting and replanting for adhering members under conditions agreed between the parties ([FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524)).

**Inference.** The cooperative’s field package is a multi-party work order plus evidence specification. A concession document alone lacks the logistics needed for dispatch.

### B. Procurement and capacity reservation

1. Confirm plant specification and reserve nursery stock.
2. Validate RUOP/plant-passport status and movement constraints.
3. Obtain compliant quotations/contracts and establish admissible payment method.
4. Reserve removal, soil-preparation, planting, irrigation, and follow-up contractors.
5. Sequence by plant delivery, weather, agronomic window, geography, and deadline.

**Fact.** Nursery movement is regulated by zone and phytosanitary status ([Puglia DET 48/2024](https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf)).

**Fact.** Certified plant scarcity was material enough that the Region created an 18-month extension tied to a signed RUOP supplier contract; it also funded nursery businesses separately under the recovery plan ([DDS 86/2023](https://www.regione.puglia.it/documents/736605/5332584/DET_86_5_8_2023.pdf/67a7e5db-32d4-042d-eeb1-7087797da30b?t=1693227259679); [nursery-support notice](https://filiereagroalimentari.regione.puglia.it/web/rigenerazione-olivicola/-/sostegno-alle-imprese-vivaistiche-art.15-misura-2g-approvato-l-avviso-pubblico)).

**Inference.** Procurement is a gating workflow, not a subordinate purchase. Plant allocation should be represented as a dated capacity commitment with substitution/expiry rules.

### C. Manager scheduling and assignment

The manager or field coordinator should:

1. batch parcels into geographic routes;
2. identify dependencies and earliest-start/latest-finish dates;
3. assign a technician and contractor;
4. confirm member/owner access;
5. check materials, equipment, and inspection availability;
6. issue the work package;
7. manage weather, access, discovery, and supplier exceptions;
8. re-plan while protecting the grant deadline.

**Fact.** Cooperative field practice can be either reactive (technician visits on farmer request) or planned (a cyclic visit plan), and includes monitoring of cultivation operations and visits to mills/producers ([AIPOL](https://aipol.bs.it/servizio-assistenza-tecnica.php)).

**Fact.** Puglia OPs advertise aggregated input purchasing, field agronomy, CAA/fascicolo/PAC services, rural-development support, traceability, and certification ([Olearia AIPO](https://www.oleariaaipopuglia.it/servizi-nuovo); [Assoproli](https://www.assoproli.it/servizi/)).

**Inference.** The manager’s mental model is likely a constrained service calendar: routes, seasonal peaks, scarce specialist crews, and member responsiveness. Public sources do not prove which scheduling software is used.

### D. Execute and capture evidence

1. Check in at the correct parcel and verify scope before destructive work.
2. Record crew, date, equipment, plant/material identifiers, quantities, and deviations.
3. Capture before/during/after evidence and inspection records as required.
4. Link delivery notes, invoices, plant passports, and payments to the parcel/member scope.
5. Obtain the official *verbale* or technical certification.
6. Update actual quantities and remaining work.

**Fact.** A phytosanitary removal must be supervised; the official record is indispensable for the contribution. Leafy material is destroyed in place, while debranched wood can remain with the owner ([Bitonto DET 3/2026](https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0)).

**Inference.** Evidence capture is part of the job definition. If it is postponed to finance, the organisation creates expensive reconstruction and non-payment risk.

### E. Variant, delay, and rework loop

Trigger a change workflow when:

- actual parcel conditions differ from the application;
- quantities or parcel selection change;
- owner/access fails;
- plant material is unavailable;
- contractor/weather delay threatens completion;
- a legal-state change affects work;
- archaeological/monumental/other protected status appears;
- field work has already deviated from approved scope.

**Fact.** Puglia separately regulates final-balance submission, variants, and technical adaptations ([DDS 44/2023 notice](https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-modalit%C3%A0-di-presentazione-della-richiesta-del-saldo-finale-e-disciplina-delle-varianti-e-degli-adattamenti-tecnici)).

**Fact.** A portal-support contract expiry interrupted EIP and caused a blanket six-month completion extension; individual nursery extensions require timely portal filing and are accepted/rejected by PEC after document checks ([DDS 86/2023](https://www.regione.puglia.it/documents/736605/5332584/DET_86_5_8_2023.pdf/67a7e5db-32d4-042d-eeb1-7087797da30b?t=1693227259679)).

### Hypothesis verdict for function 4

- **Confirmation:** Duties/orders/awards are inputs; a manager schedules and assigns execution.
- **Challenge:** These acts do not “prepare field operations.” Procurement, owner/access confirmation, technical design, cash state, and evidence requirements are independent gates. Some work is performed by ARIF rather than a cooperative crew.
- **Recommended framing:** `Authority/award -> field-readiness assembly -> capacity reservation -> dispatch -> supervised evidence -> variant/rework`.

## Detailed practice workflow 5: payment preparation, authorisation, execution, and repair

### A. Design the evidence path before spending

1. Map approved cost lines to allowable procurement and payment methods.
2. Define which legal entity/member contracts, receives invoices, and pays.
3. Require project references in transfers and supplier records.
4. Identify required releases, declarations, payroll/F24 evidence, dedicated accounts, time sheets, and technical records.
5. Establish advance, SAL, and final-balance strategy.

**Fact.** Puglia payment guides require cross-document evidence, including invoices, transfer evidence, supplier releases, dedicated-account statements, contracts, and detailed allocation tables ([Puglia DdP document crosswalk](https://psr.regione.puglia.it/documents/33128/62654/Domande+di+pagamento+-+Tabella+di+raccordo+documenti.pdf/bdc33b90-0a58-0271-09ba-554cccdddac1?t=1567778664944&version=1.0)).

**Inference.** Finance must participate at procurement design, not merely authorise a finished payment claim.

### B. Advance route

1. Beneficiary elects whether to request an advance.
2. Bank/insurer underwrites and issues the prescribed guarantee.
3. Application is submitted in PMA/EIP.
4. Guarantee is attached digitally and sent in original within the deadline.
5. Region validates guarantee and pays or requests repair.

**Fact.** The advance is 50% of aid with a guarantee equal to 110% of the advance; the original had to reach the regional measure office within ten days ([DDS 380/2022](https://www.regione.puglia.it/documents/736605/3203897/DDS+n.+380+del+01.06.2022.pdf/13473a2c-dc6e-a672-df63-fadab7740607?t=1655799771123)).

**Inference.** A cooperative-wide “finance authorised” state is misleading. Each member can fail separately on credit or guarantee documents.

### C. Build the SAL/final dossier

1. Freeze the approved-scope version and accepted variants.
2. Reconcile physical completion to quantities and parcels.
3. Reconcile invoices to delivery/work records.
4. Reconcile payments to invoices and bank statements.
5. Collect supplier releases and technical/inspection records.
6. Verify the collective execution mandate is present.
7. Run DURC, antimafia, bank, death/subentro, debt, and guarantee prechecks where possible.
8. Have the beneficiary/authorised representative certify the claim.
9. File the DdP and preserve protocol/receipt.

**Fact.** The collective mandate evidence is due with payment/final balance and its absence can cause revocation ([FAQ](https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524)).

**Fact.** Puglia issued separate rules for final balance and variants and has published multiple batch liquidation acts rather than one universal payment event ([DDS 44/2023 notice](https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-modalit%C3%A0-di-presentazione-della-richiesta-del-saldo-finale-e-disciplina-delle-varianti-e-degli-adattamenti-tecnici); [December 2024 liquidation](https://feamp.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-dds-n.-197-del-13.12.2024-provvedimento-di-liquidazione-degli-aiuti-delle-domande-di-pagamento-del-saldo)).

### D. Public instruction and serial authorisation

Comparable Italian process:

1. CAA submits the payment claim.
2. Delegated body performs technical/administrative instruction.
3. Positive cases enter a liquidation list.
4. Payment-authorisation office checks DURC, antimafia, guarantees, and similar controls.
5. Accounting checks internal/national debtor registers and applies compensation if needed.
6. The list returns for acknowledgement and managerial signature.
7. Execution office issues the payment mandate.
8. Treasury settles and issues a receipt.

**Fact.** This exact separation is described by Regione Lombardia’s paying body ([payment process](https://opr.regione.lombardia.it/it/organismo-pagatore-regionale/per-gli-agricoltori/quali-sono-le-fasi-del-processo-di-pagamento)). It is used here as a comparable Italian control model, not proof that Puglia uses the same office names.

### E. Payment failure and repair

Common repair loops:

- incorrect IBAN -> contact CAA/farm -> new bank details -> reissue;
- beneficiary death -> subentro/succession -> reissue or case amendment;
- adverse DURC/antimafia -> clarify, correct, or wait for valid result;
- debt registry -> compensation and revised net amount;
- missing guarantee/original -> cure or reject;
- invoice/payment mismatch -> add evidence or reduce eligible cost;
- physical scope mismatch -> variant/adaptation or reduction;
- missing mandate -> revocation risk;
- incomplete supplier/plant traceability -> instruction exception;
- portal/document-channel failure -> PEC evidence and possible reopening.

**Fact.** Puglia has a dedicated pre-concession death-subentro portal path ([subentro notice](https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-olivi-in-zona-infetta-modalit%C3%A0-di-presentazione-della-domanda-di-subentro-per-decesso)). A 2026 act separately records withdrawals, non-admissible ARIF instruction outcomes, and related cases ([DET 40/2026](https://burp.regione.puglia.it/documents/20135/2756319/DET_40_12_3_2026.pdf/32032cd5-6ec7-c503-5384-5c6f8ec9e0bc?t=1775151354374&version=1.0)).

**Fact.** The Region itself identified individual DURC and antimafia checks as objective delay sources and sought mass DURC requests ([implementation statement](https://press.regione.puglia.it/-/reimpianti-ulivi-in-zona-infetta-da-xylella-lo-stato-di-attuazione-dell-avviso-pubblico)).

### Hypothesis verdict for function 5

- **Confirmation:** Award rules determine allowable payment stages, and finance/authorised officials approve consequential releases.
- **Challenge:** The award does not itself prepare the claim. Payment readiness depends on evidence engineered from procurement onward, member-level identity/credit/compliance, physical verification, and serial public controls.
- **Recommended framing:** `Evidence-by-design -> member-level claim assembly -> public instruction -> administrative control -> authorisation -> treasury -> repair/reissue`.

## Real artifacts and tools

### Explicitly observed artifacts

| Artifact/tool | Where it appears | Operational purpose |
|---|---|---|
| Fascicolo aziendale, paper and electronic | Replant call; CAA pages | Master identity, title, parcel, crop, and durable farm data |
| Surface/olive-tree sheet | Replant call | Exact tree count per parcel; source for form and instruction |
| SIAN application | Call and user manual | Individual, adhesion, collective submission and controls |
| EIP/PMA regional portal | Advance, extension, project calls | Delegations, project data, advance, extension, subentro |
| PEC inbox/outbox | Calls, instructions, adverse results | Enablement, notices, additions, outcomes, outage evidence |
| Digital signature and OTP | SIAN manual/calls | Beneficiary certification and release |
| Provisional/final PDF and barcode | SIAN manual | Human review and final frozen submission |
| Protocol and acceptance receipt | SIAN manual | Evidence that proceeding was activated |
| Office monitor and Excel export | SIAN manual | Work-in-progress and anomaly queues |
| Member adhesion and collective B1 list | SIAN manual | Member–cooperative relationship and selection |
| Mandate to file and execute work | Call/FAQ | Legal authority for cooperative action |
| Owner/co-owner authorisation | Concession documents | Permission where occupier differs from owner |
| Ranking and scroll lists | Regional notices | Budget priority and reactivation |
| Concession act | Region | Award amount, scope, conditions, deadline |
| Guarantee form and original paper guarantee | DDS 380/2022 | Advance security |
| Supplier contract with RUOP operator | DDS 86/2023 | Nursery-capacity evidence for extension |
| Plant passport and nursery traceability | Nursery rules/call | Health and source traceability |
| Work order / technical design | Implied by approved intervention; not publicly templated | Field dispatch and control |
| Inspection *verbale* | Removal order | Official completion evidence |
| Variant/technical-adaptation request | DDS 44/2023 | Controlled change to approved work |
| Invoice, delivery note, bank transfer | Payment guides | Expense and payment proof |
| Supplier release (*quietanza liberatoria*) | Payment crosswalk | Supplier confirmation of payment |
| Dedicated-account statement | Payment crosswalk | Cash traceability |
| Time sheet / partner expense summary | Payment crosswalk | Allocation and project-cost support |
| DdP, liquidation list, payment order, treasury receipt | Payment guides | Serial claim-to-cash controls |
| Municipal *albo pretorio*, BURP, website notice | Orders and court cases | Legal notification |

### Commercial/sector tools that reveal unmet operator needs

- **Fact about product positioning, not adoption.** ISAGRI markets multi-farm cartography, member/company profiles, field app/offline entry, centralised technical activities, automatic registers, control warnings, and farmer–agronomist collaboration to cooperatives and OPs ([ISAGRI](https://www.isagri.it/la-soluzione-ideale-per-agronomi-e-cooperative)).
- **Fact about product positioning, not adoption.** AgerTech markets WhatsApp-based capture of operator messages, audio, and photos into structured data, and cooperative centralisation of member data ([AgerTech search result landing](https://agertech.it/cooperative/); [I3P profile](https://www.i3p.it/startup/agertech)).
- **Fact.** AssoSoftware argues that without direct interoperability, digital field registers reproduce duplicate entry and error; it cites an AGEA–AssoSoftware technical effort to connect private management systems with SIAN ([AssoSoftware](https://www.assosoftware.it/comunicati-stampa/quaderno-di-campagna-digitale-240726/)).
- **Inference.** These products indicate a recurring gap between how field data is generated—by farmers, technicians, messages, photos, and offline work—and how official portals require structured records. They do not establish that the replanting cooperatives studied here use these products.

## What is automated, discretionary, and manual

| Work | Routinely automated or system-supported | Human discretion/manual work |
|---|---|---|
| Identity/parcel prefill | SIAN loads farm-register data | Repairing the source dossier; deciding if title evidence is adequate |
| Form validation | Required-field and cross-field anomaly checks | Interpreting legal ambiguity and whether a warning is tolerable |
| Amount/threshold calculation | Standard-cost and form calculations | Selecting scope, quantities, members, and technical adaptations |
| Member relationship | CUAA and open-fascicolo controls | Negotiating mandate and choosing which adherents to include |
| Workflow state | Portal states, protocol, receipts | External queue management across SIAN, EIP, PEC, paper, and websites |
| Signature | OTP/app/digital signature mechanisms | Ensuring the correct person understands and authorises consequences |
| Official notice | Website/BURP/albo publication | Finding, matching, contacting, and obtaining acknowledgement from the real occupier |
| Geography | Official maps/orders and parcel references | Reconciling dated acts, cadastral state, real access, and exceptional status |
| Funding ranking | Published scores/rankings/scrolls | Pursuit decision, capacity allocation, member financing, risk appetite |
| Scheduling | Commercial tools can support tasks/maps | Route, season, weather, member access, contractor and nursery trade-offs |
| Field capture | Apps can record activities offline and generate registers | Verifying correct parcel/scope and documenting unplanned conditions |
| Payment checks | Portal checks and public registers | Building the evidence chain, explaining mismatches, authorising reductions |
| Payment execution | Lists, orders, treasury systems | Repairing bank, death, debt, compliance, and document exceptions |

## Failure, delay, and rework patterns

### 1. Master-data mismatch

- Stale or missing title, parcel, crop, tree count, owner, legal representative, PEC, or bank data.
- Form data is immutable because the defect is upstream in the fascicolo.
- A rectification based on a newly modified dossier can produce a materially different form.
- **Operational response:** root-cause queue owned by CAA/source-data steward; never patch only the generated PDF.

### 2. Delegation and permission failure

- Professional not enabled; member mandate missing; owner consent missing; wrong OP/cooperative CUAA; collective execution mandate absent.
- **Operational response:** distinguish `permission to see data`, `permission to file`, `member approval of initiative`, `mandate to execute`, and `owner permission to alter land`.

### 3. Portal and channel fragility

- Separate SIAN and EIP/PMA flows, plus PEC, digital signature, OTP, and paper originals.
- EIP interruption after a support contract expired caused a public deadline extension ([DDS 86/2023](https://www.regione.puglia.it/documents/736605/5332584/DET_86_5_8_2023.pdf/67a7e5db-32d4-042d-eeb1-7087797da30b?t=1693227259679)).
- Calls specify how to report SIAN closure anomalies and can reopen systems after verification.
- **Operational response:** timestamped attempt log, screenshots/receipts, PEC escalation, and a system-independent deadline register.

### 4. Notification without awareness

- Website or municipal posting legally starts a clock, but the actual occupier may not know.
- **Operational response:** monitor source feeds, match notices to member/parcel records, contact the person, and record acknowledgement separately from legal service.

### 5. Budget and administrative capacity delay

- Demand greatly exceeds initial budget; later scrolls reactivate old cases.
- Instruction requires staff and software capacity; Region reported waiting for assistance/software resources.
- **Operational response:** keep unfunded cases in a dormant option pool with reactivation readiness.

### 6. Serial compliance checks

- DURC, antimafia, guarantees, debt registers, and public accounting occur after technical work and can delay or reduce payment.
- **Operational response:** precheck early, batch where lawful, expose which external authority owns the wait, and avoid presenting a guessed completion date as certain.

### 7. Nursery and material bottleneck

- Certified plant supply was scarce enough to justify an 18-month extension and formal supplier contracts.
- **Operational response:** capacity reservation, supplier lead-time states, approved substitution rules, and plant-level traceability.

### 8. Contractor, field-season, and access conflict

- Seasonal operations, weather, terrain, machinery, member access, and technician/inspector availability constrain work.
- **Operational response:** schedule by dependency and route; maintain `ready`, `blocked`, `at risk`, `dispatched`, `verified`, not just “awarded/in progress.”

### 9. Scope drift and late variants

- Actual field conditions differ; the operator discovers needed change after procurement or work starts.
- **Operational response:** a pre-dispatch scope confirmation and a fast variant gate. Do not let crews improvise a grant-relevant change without escalation.

### 10. Evidence reconstructed too late

- Missing supplier release, transfer reference, time sheet, plant passport, inspection record, or mandate appears only at final claim.
- **Operational response:** evidence checklist attached to each work package; finance validates evidence completeness continuously.

### 11. Death, ownership change, and bank failure

- Long-running programs outlast people, titles, and bank accounts. Dedicated subentro and reissue paths exist.
- **Operational response:** periodic identity/title/bank refresh and explicit successor workflow.

### 12. Collective aggregation with individual liability

- Cooperative plans a batch, but each member remains beneficiary and guarantee/compliance/payment exceptions split the batch.
- **Operational response:** aggregate planning, member-level state and liability. Never let the collective header hide individual blockers.

## Operator mental models

These are **inferences** to test in interviews:

1. **“The portal is not the case.”** The case is the full packet plus external facts, signatures, and communications.
2. **“An official green light is only the next gate.”** Ranked, admitted, conceded, field-ready, completed, instructed, liquidated, and paid are materially different.
3. **“Protect the option.”** Old unfunded or incomplete cases may become valuable after scrolls, reopenings, or repaired documents.
4. **“No destructive work without the exact parcel and authority.”** Wrong-person/wrong-parcel errors are irreversible.
5. **“Batch the work, separate the liabilities.”** Procurement and routes gain from aggregation; guarantees, compliance, and claims remain member-specific.
6. **“If it is not evidenced, it may not be paid.”** The field act and its documentation are one job.
7. **“The season will not wait for the administration.”** Plant and contractor reservations compete with uncertain concessions and variant approval.
8. **“Exceptions consume the office.”** Straight-through forms are cheap; title, consent, death, portal, and evidence exceptions dominate staff time.
9. **“Legal publication is not member communication.”** Staff must close the awareness gap.
10. **“Cash timing decides feasibility.”** An eligible project without guarantee or working capital is not executable.

## Alternative workflow framings

### 1. Member–parcel case swarm, not five departmental pipelines

Represent every member–parcel–intervention as a case with linked legal, funding, application, field, and payment state. Departmental views become filtered views of the same case. This avoids handoff loss when the same owner consent or parcel correction affects several functions.

### 2. Commitment ledger

Track commitments rather than statuses:

- member authorises filing;
- owner authorises intervention;
- cooperative accepts execution mandate;
- bank commits guarantee;
- nursery commits plants by date;
- contractor commits capacity;
- authority concedes scope;
- inspector validates work;
- finance certifies evidence;
- public official authorises payment.

A case advances when the necessary commitments are present and current.

### 3. Two control loops: coercive duty and voluntary investment

Do not force phytosanitary eradication orders and grant-funded replanting into one lifecycle.

- **Duty loop:** detection -> order -> notification -> owner choice -> ARIF/voluntary execution -> supervision -> enforcement/indemnity.
- **Investment loop:** candidate -> application -> ranking -> concession -> procurement -> work -> claim -> payment.

They meet at parcel and owner but have different authority, timing, evidence, and incentives.

### 4. Readiness gates instead of generic status

Use explicit gates:

1. identity/title ready;
2. legal-geography resolved;
3. member/owner authority ready;
4. funding eligible and strategically accepted;
5. submission ready;
6. award conditions satisfied;
7. finance/cash ready;
8. nursery/contractor ready;
9. field ready;
10. evidence ready;
11. payment claim ready.

Each failed gate names an owner, reason, source, next action, and expiry.

### 5. Temporal orchestration model

Maintain several independent clocks:

- publication/appeal/response deadlines;
- application and delegation windows;
- concession completion period;
- supplier delivery lead time;
- agronomic and weather window;
- guarantee validity;
- compliance-certificate validity;
- payment-claim period.

The next-best action is the one that protects the earliest consequential clock, not necessarily the next step in a fixed pipeline.

### 6. Evidence factory

Treat every field and purchasing action as producing a required future payment artifact. Generate the evidence request at authorisation, not after execution. The payment dossier then becomes a controlled assembly of already-linked evidence rather than a forensic reconstruction.

### 7. Portfolio and capacity framing

The cooperative’s core decision is not only eligibility. It is the allocation of technician hours, contractor slots, plant inventory, credit support, and management attention across candidate cases. A portfolio view should show expected member benefit, probability of payment, cost-to-serve, geographic batch value, and consequence of delay.

## Confirmation and challenge of the five assertions

| Starting assertion | Confirmed | Challenged | Better formulation |
|---|---|---|---|
| 1. Land explains official status/duties; Field Work owns execution. | Official legal/geographic state and execution are distinct. | Land also includes active title repair, notice acknowledgement, consent, access, and responsibility resolution. ARIF may own execution for orders. | Legal/land prepares an acknowledged, permissioned work package; the appropriate field authority executes. |
| 2. Funding computes complete eligible/ineligible/unresolved population; cooperative decides whether to pursue. | A full internal candidate inventory with explicit unresolveds is valuable; inclusion is discretionary. | Official demand is opt-in. The cooperative selects among adhesion cases after negotiation. Feasibility, mandate, capacity, cash, and guarantee are separate from eligibility. | Funding maintains a provisional candidate portfolio and readiness dimensions; cooperative records negotiated inclusion and capacity allocation. |
| 3. CORDON prepares applications; operator resolves exceptions and authorizes. | Automation can prefill, validate, and produce review packets; humans must resolve exceptions and give consequential approval. | Preparation is distributed across source registers, CAA, technician, member, cooperative, SIAN, EIP, PEC, and paper. The legally authorised beneficiary/representative—not any generic operator—certifies truth. | System assembles and checks; source-data stewards repair; case operator adjudicates; authorised person releases and certifies. |
| 4. Duties/orders/awards prepare field operations; manager schedules/assigns. | Acts define scope and deadlines; managers schedule/assign. | Procurement, plant supply, access, technical design, cash, contractor capacity, and evidence specification are independent readiness gates. | Authority output starts field-readiness assembly; manager dispatches only after dependencies and evidence plan are committed. |
| 5. Award rules determine/prepare payment stages; finance authorizes. | Award rules define advance/SAL/final paths and finance has approval duties. | Payment is member-level, serial, and evidence-heavy. Finance must shape procurement and evidence before work. Public officials, not cooperative finance alone, authorise disbursement. | Finance engineers admissible spend/evidence, authorised beneficiary files, public bodies instruct and authorise, treasury executes, exceptions loop back. |

## Incentives and bottlenecks

### Cooperative/OP

- **Incentives:** member retention, service revenue/value, aggregated purchasing, field efficiency, stronger production base, OCM/sector-programme delivery, reputational trust.
- **Bottlenecks:** exception-heavy staff work, uncertain budget, member responsiveness, contractor and nursery capacity, individual compliance/credit hidden inside collective projects.

### CAA/professionals

- **Incentives:** complete and defensible files, throughput, client retention, reduced rework.
- **Bottlenecks:** upstream data errors, portal access, changing rules, duplicated entry, deadline peaks, dependence on member OTP/signature and external authorities.

### Member/beneficiary

- **Incentives:** restore productive value, obtain public support, offload administrative/technical complexity.
- **Bottlenecks:** unclear status, repeated documents, cash/guarantee, owner consent, long waits, risk of revocation, field-care obligations.

### Administration/ARIF/paying body

- **Incentives:** legal compliance, fraud prevention, auditable expenditure, rapid phytosanitary action, budget absorption.
- **Bottlenecks:** volume, serial checks, fragmented systems, owner identification, field inspection capacity, support contracts/software, external certificates.

### Suppliers/contractors

- **Incentives:** predictable aggregated orders and payment.
- **Bottlenecks:** uncertain award timing, seasonal peaks, certified-stock lead time, routing/access, evidence and invoice requirements.

## Overlooked domain areas

1. **Notification operations.** Monitoring BURP/web/albo notices and turning publication into actual member acknowledgement is a distinct job.
2. **Credit and guarantees.** Individual underwriting can break collective execution.
3. **Death and succession.** Long delays make subentro a normal operating path, not an edge case.
4. **Member governance.** Selection of some adherents after negotiation creates fairness, conflict, and audit questions.
5. **Supplier capacity allocation.** Nursery stock is a scarce dated commitment, not a catalogue item.
6. **Field evidence design.** Inspection records, passports, delivery notes, photos, and quantity reconciliation should be designed with the work order.
7. **Data protection.** Orders and annexes can contain owners; cooperative tools need role-based handling and retention rules.
8. **Landscape/monumental/archaeological constraints.** “Replant allowed” does not eliminate every parcel-specific constraint.
9. **Contract and software continuity.** Expiry of a portal support contract changed statutory project timing.
10. **Debtor-register offsets.** Net payment can differ from approved claim even after technical success.
11. **Indemnity versus investment aid.** Removal compensation and replant grants have different dossiers and should not be conflated.
12. **Aftercare and survival.** Public material emphasises completed planting, but long-term orchard establishment, irrigation, replacement mortality, and continued obligations affect real value.
13. **Dispute and appeal capacity.** Adverse instruction, reconsideration, obvious error, and litigation require a case record that preserves source facts and timing.
14. **Cost-to-serve.** A technically eligible small, isolated, document-poor case may consume disproportionate cooperative resources.
15. **Interoperability governance.** Direct exchange between private farm software and SIAN is still presented as a desired future state, so duplicate entry remains a present risk.

## Gaps and interview questions

### Cooperative/OP internal practice

1. Which organisation actually holds the master member–parcel worklist: OP, CAA, agronomist, or cooperative office?
2. What spreadsheets are used? What are the columns, owners, update cadence, and reconciliation rules?
3. Which communications occur by PEC, ordinary email, phone, WhatsApp, in-person visits, or paper?
4. Who decides which adhesion cases enter the collective application, and what non-legal criteria are used?
5. How are conflicts or perceived unfairness handled when some members are selected and others are not?
6. Does the cooperative contract and pay suppliers centrally, or do individual beneficiaries contract/pay and then assign execution?
7. Who bears cost overruns, plant mortality, and rejected expenditure?

### Field operations

8. Which contractors perform removal, site preparation, planting, and irrigation, and how far ahead are they booked?
9. Is scheduling done in a spreadsheet, calendar, messaging group, field-management system, or contractor’s own system?
10. How are parcels grouped into routes and how is access confirmed on the day?
11. What field evidence is actually captured: geotagged photos, paper *verbale*, app records, delivery notes, plant labels, GPS tracks?
12. What percentage of jobs require a variant or second visit, and why?
13. How often do nursery delivery dates, cultivar/category, or quantities differ from the approved design?

### Application and exception handling

14. Which SIAN anomaly codes dominate rework?
15. How long does fascicolo repair take by exception class?
16. Is there a formal four-eyes review before definitive print/release?
17. How are website-only scroll/deadline notices detected and matched to old cases?
18. How are failed OTP, absent members, expired signatures, and last-day portal failures handled?
19. Which data is retyped between SIAN, EIP/PMA, local records, and payment files?

### Payment and finance

20. Who owns the final DdP assembly: cooperative finance, CAA, agronomist, external accountant, or member?
21. What is the typical gap between completion, claim, instruction, liquidation, and cash?
22. Which checks most often stop payment: DURC, antimafia, guarantee, debt, IBAN, death, invoice, scope, inspection, or mandate?
23. How are supplier releases and bank statements chased and reconciled?
24. Are advances commonly used, and how many members fail to secure guarantees?
25. How are partial payments, reductions, offsets, and rejected lines communicated to members?

### Quantitative gaps

26. Number of collective adhesion cases, included cases, dropped-to-individual cases, concessions, completions, claims, liquidations, reductions, revocations, and average elapsed times.
27. Staff hours and cost-to-serve by straight-through versus exception case.
28. Nursery and contractor capacity by season and geography.
29. Share of data captured digitally at source versus retyped/scanned.
30. Frequency and financial impact of late evidence, variants, and portal outages.

## Sources

1. Regione Puglia, consolidated call, “Reimpianto olivi zona infetta”: https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf/8dfcd559-42d2-5443-6ded-41d3c2ed4984?t=1601892506182
2. Regione Puglia, replanting FAQ: https://www.regione.puglia.it/documents/42866/347990/FAQ+-+Misura+Reimpianto+olivi+zona+infetta.pdf/97dc2614-a2f6-b1b2-056c-4b466cffe891?t=1605692356524
3. SIAN Xylella application manual mirror: https://it.readkong.com/page/sin-emergenza-xylella-aiuto-alle-imprese-agricole-art-6-4221541
4. Regione Puglia, 2021 rankings/adhesion lists: https://www.regione.puglia.it/web/rigenerazione-olivicola/-/bando-reimpianto-ulivi-in-zona-infetta-le-graduatorie-e-l-elenco-delle-domande-ammesse-all-istruttoria
5. Regione Puglia, 2026 ranking scroll: https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-scorrimento-della-graduatoria-1
6. Regione Puglia, reopening delegation upload: https://politiche-energetiche.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-determinazione-dirigenziale-n.-53-del-30.03.26-di-scorrimento-della-graduatoria-riapertura-termini-per-inserimento-delega
7. Regione Puglia, DDS 44/2023 final balance/variants notice: https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-modalit%C3%A0-di-presentazione-della-richiesta-del-saldo-finale-e-disciplina-delle-varianti-e-degli-adattamenti-tecnici
8. Regione Puglia, DDS 380/2022 advance and guarantee: https://www.regione.puglia.it/documents/736605/3203897/DDS+n.+380+del+01.06.2022.pdf/13473a2c-dc6e-a672-df63-fadab7740607?t=1655799771123
9. Regione Puglia, DDS 86/2023 completion/plant-supply extension: https://www.regione.puglia.it/documents/736605/5332584/DET_86_5_8_2023.pdf/67a7e5db-32d4-042d-eeb1-7087797da30b?t=1693227259679
10. Regione Puglia, pre-concession death/subentro procedure: https://www.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-olivi-in-zona-infetta-modalit%C3%A0-di-presentazione-della-domanda-di-subentro-per-decesso
11. BURP, DET 40/2026 withdrawals/non-admissible instruction: https://burp.regione.puglia.it/documents/20135/2756319/DET_40_12_3_2026.pdf/32032cd5-6ec7-c503-5384-5c6f8ec9e0bc?t=1775151354374&version=1.0
12. Regione Puglia, December 2024 final-balance liquidation: https://feamp.regione.puglia.it/web/rigenerazione-olivicola/-/reimpianto-ulivi-in-zona-infetta-dds-n.-197-del-13.12.2024-provvedimento-di-liquidazione-degli-aiuti-delle-domande-di-pagamento-del-saldo
13. Regione Puglia, implementation statement: https://press.regione.puglia.it/-/reimpianti-ulivi-in-zona-infetta-da-xylella-lo-stato-di-attuazione-dell-avviso-pubblico
14. Regione Puglia, CAA role and regulation: https://filiereagroalimentari.regione.puglia.it/centri-di-assistenza-agricola
15. ARPEA, CAA practical functions: https://www.arpea.piemonte.it/come-fare-per/centri-assistenza-agricola-caa
16. PSR Puglia, consultant quotations and delegation: https://psr.regione.puglia.it/-/bando-sottomisura-7.6-chiarimenti-per-la-gestione-dei-preventivi-di-individuazione-consulenti-tecnici-e-successiva-delega
17. PSR Puglia, support for advisory services call: https://psr.regione.puglia.it/documents/33128/88963/Determinazione+Autorit%C3%A0+di+Gestione+n.+91+del+20.06.2022.pdf/5abd6c1b-8760-61c3-62ed-b35c5a14562a?t=1699375366415&version=1.4
18. PSR Puglia, DdP document crosswalk: https://psr.regione.puglia.it/documents/33128/62654/Domande+di+pagamento+-+Tabella+di+raccordo+documenti.pdf/bdc33b90-0a58-0271-09ba-554cccdddac1?t=1567778664944&version=1.0
19. PSR Puglia, SIAN payment-claim manual: https://psr.regione.puglia.it/documents/33128/48009/Manuale+utente+SIAN+compilazione+domande+di+pagamento+edizione+11.pdf/59fd9821-226e-c979-8733-3eb632dfb3e3?t=1584728314786
20. PSR Puglia, payment by SAL notice: https://psr.regione.puglia.it/-/programma-di-sviluppo-rurale-2014-2020-pagamento-per-sal
21. PSR Puglia, DURC instruction guidance: https://psr.regione.puglia.it/documents/33128/409878/Determinazione+Autorit%C3%A0+di+Gestione+n.+156+del+09.11.2022.pdf/571c231c-14f2-53b1-a503-129469092664?t=1668769103388&version=1.0
22. Regione Lombardia paying body, payment process: https://opr.regione.lombardia.it/it/organismo-pagatore-regionale/per-gli-agricoltori/quali-sono-le-fasi-del-processo-di-pagamento
23. ARIF, removals and indemnities: https://www.arifpuglia.it/attivita/monitoraggio-xylella/abbattimenti-e-indennizzi/
24. BURP, Bitonto DET 3/2026: https://burp.regione.puglia.it/documents/20135/2735532/DET_3_12_1_2026_FITO.pdf/e5f3a8ea-c365-1b97-514a-929997c769aa?t=1770063167245&version=1.0
25. TAR Puglia 1640/2019: https://www.ambientediritto.it/giurisprudenza/tar-puglia-bari-sez-3-12-dicembre-2019-n-1640/
26. Rai News, TAR monumentality verification report: https://www.rainews.it/archivio-rainews/articoli/Xylella-Tar-verifica-monumentalita-prima-di-abbattere-016b8193-afe4-4222-9c59-7d9fc3884117.html
27. Constitutional Court judgment 74/2021 page: https://www.cortecostituzionale.it/actionSchedaPronuncia.do?anno=2021&numero=74
28. Regione Puglia, owner authorisation in concession documentation: https://foreste.regione.puglia.it/documents/736605/3409746/181_DIR_2025_00120_DeterminaPUB+%281%29.pdf/d7735ada-2b6d-2e58-06e5-463b9576edb0?t=1752828606764
29. Regione Puglia, nursery movement rules DET 48/2024: https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf
30. Regione Puglia, nursery-business support: https://filiereagroalimentari.regione.puglia.it/web/rigenerazione-olivicola/-/sostegno-alle-imprese-vivaistiche-art.15-misura-2g-approvato-l-avviso-pubblico
31. Agenzia del Demanio, anti-Xylella tillage/mowing procurement: https://www.agenziademanio.it/it/gare-aste/forniture-e-servizi/gara/Servizi-di-aratura-e-sfalcio-erba-al-fine-di-contrastare-lemergenza-della-Xylella-Fastidiosa-nella-Regione-Puglia
32. Olearia AIPO Puglia, services: https://www.oleariaaipopuglia.it/servizi-nuovo
33. Assoproli Bari, services: https://www.assoproli.it/servizi/
34. AIPOL, field technical assistance: https://aipol.bs.it/servizio-assistenza-tecnica.php
35. OP Latium, farm services: https://www.oplatium.it/en/services-offered-to-agricultural-companies
36. MASAF, olive OP/AOP operational programmes: https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/8261
37. AGEA, olive OP operational-program instructions: https://www.agea.gov.it/portale-apigw/documents/d/agea/agea-2023-0096281-allegato-istruzionioperativen1082023programmioperativiolio_signed-pdf
38. ISAGRI, multi-farm cooperative/OP software: https://www.isagri.it/la-soluzione-ideale-per-agronomi-e-cooperative
39. AgerTech, cooperative/OP product page: https://agertech.it/cooperative/
40. I3P, AgerTech profile: https://www.i3p.it/startup/agertech
41. AssoSoftware, digital field-register interoperability: https://www.assosoftware.it/comunicati-stampa/quaderno-di-campagna-digitale-240726/
42. EU CAP Network, simplification and administrative-burden study: https://eu-cap-network.ec.europa.eu/sites/default/files/publications/2025-05/eu-cap-network-report-study-on-simplification.pdf
43. EU CAP Network, study landing page: https://eu-cap-network.ec.europa.eu/publications/study-simplification-and-administrative-burden-farmers-and-other-beneficiaries-under_en
44. European Commission, farm advisory services/AKIS: https://agriculture.ec.europa.eu/cap-my-country/cap-strategic-plans/fas_en
45. FoodTimes, reported AGEA/SIAN 2024 problems: https://www.foodtimes.eu/food-system/cap-2024-technical-and-management-problems-in-the-agea-system/
46. Confagricoltura Sardegna, reported application-system disruption: https://www.confagricoltura.sardegna.it/2024/08/30/presentazione-domande-pac-con-il-nuovo-sistema-informatico-gravi-disservizi-argea-op-non-adeguata-al-ruolo/
47. Regione Puglia, 4.1A EIP/SIAN deadline extension: https://www.regione.puglia.it/web/agricoltura/-/psr-puglia-bando-sottomisura-4.1-a-2024-prorogati-i-termini-di-operativit%C3%A0-dei-portali-eip-e-sian
48. Corte dei conti, AGEA 2019 management report notice: https://www.corteconti.it/HOME/StampaMedia/Notizie/DettaglioNotizia?Id=e54d3646-ea63-4545-8ceb-7be587ecb58e
49. Regione Puglia, measure 2.B overview: https://www.regione.puglia.it/web/rigenerazione-olivicola/misura-2.b
50. MASAF, OP/AOP operator organisations overview: https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/747

## Bottom line

The evidence supports a redesign around a shared, versioned **member–parcel–intervention case**, with explicit commitments, readiness gates, clocks, and evidence. The public portals automate form generation, validation, and protocol, but the difficult work remains cross-system and human: repairing master data, negotiating member inclusion, securing authority and credit, reserving plants and contractors, converting awards into field-ready packages, noticing legal publications, and reconstructing an auditable claim. The largest design error would be to encode the five functions as a clean linear handoff. Actual practice is a portfolio of asynchronous cases with repeated exception and rework loops.
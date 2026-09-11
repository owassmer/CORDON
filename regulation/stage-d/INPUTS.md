# Stage D input map

This is the front door to Stage D. It starts with facts required by accepted A–C,
then identifies the source that can supply them. After the 10 September purge,
the bounded national calendar remained retained. The monitoring-observation family is established (first row). The laboratory-report documents are acquired but their reading is not established (second row); prior acquisitions and case
demonstrations confer no completion on the other rows.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Established. `cordon_d.monitoring.observations` streams every retained release; `distinct_observations` relates the publications of one observation; `detection_days`, `occasion_sets` and `located_positives` hand C its candidates. Meaning and limits below. |
| What the laboratory actually reported | The report each monitoring record links: confirmation letters of the SELGE network and CNR-IPSP, rapporti di prova of CNR-IPSP and of the first-level laboratories, and CNR subspecies-identification rapporti | One laboratory report: a letter stating its identity, laboratory, dates, assays and analyte, and an annex listing one row per sample with the result the laboratory states for it | **Not established.** The documents are acquired: 1,918 report routes name 1,186 documents, 1,175 of them in the store. Reading them is not. Sources read independently of the reader show it recording its own extraction failures as facts about the publisher, over the majority of the population. What is acquired, what this reader currently recovers, and what the sources show it misses are below. |
| Which legally adopted area contained the location on the event date | SIT demarcated-area geometry and the adopting regional act | One published area feature in one legal version | Acquire every version reached by A; bind geometry to its adopting act; use the version in force at the event time |
| Which plants or surfaces fall inside C's distance and survey calculations | Monitoring observations, PuntiStampa, land-use or host-bearing surfaces, parcels and other population records required by the calculation | An observation, published point or polygon, parcel, grid cell or host-bearing surface according to its own source | Establish the actual population represented by each source and never substitute positives for all plants |
| Which cadastral parcel contains or intersects a relevant location | Agenzia delle Entrate and SIT cadastral geometry | One parcel geometry with its cadastral reference | Acquire the reached parcel population and preserve the source identifier; do not infer ownership from geometry |
| Whether the Osservatorio issued a removal measure and which plants or parcels it covered | Regional removal determination and its incorporated annexes | One adopted act plus its source-defined subject rows | Read identity, operative clause, branch, annex incorporation and correction relationships through one general reader |
| Whether a legally consequential notice, delivery, publication, receipt or response happened | The determination's own text for its declared route; the competent municipality's albo pretorio record for the seven-day publication every plan version requires; BURP and the regional sites the plans name; the Osservatorio's communication record and municipal notification attempts for recipient effect; PEC transmission to ARIF and the Prefettura; ARIF's authenticated election record or the owner's PEC for the response | One event at one time concerning one document, one sender and one recipient under one route; or one publication with its start, continuity and end | Select the source by the route A selects for the act and recipient: completed personal communication, including the code-of-civil-procedure forms for unreachable recipients; mass publicity only where the act establishes that recipient number made personal communication impossible or particularly burdensome; a reasoned immediate-effect clause in a non-sanctioning measure; or cautionary-and-urgent character. An immediate-effect or cautionary clause makes the measure operative; it is not notification, and a clock anchored on notice or publication runs only from that event. A publication record proves the publication duty, and its end date anchors the election window; publication alone establishes neither recipient effect nor silence, refusal, breach or cost liability. Sending, delivery, publication, recipient effectiveness and response stay distinct. |
| Who has the consequential relationship to the affected land | The determination's incorporated annex naming addressees by comune, foglio and particella; later acts that correct listed owners; the Osservatorio's matter and transmitted cadastral and owner data; a competent public-asset register for public land | One addressee position in one act version, or one stated ownership, occupation, management or other legally relevant relationship | The annex establishes the position the act published for each parcel, not that the named person held the land. An effective correction act replaces the listed position for the parcels it names; its effect against the corrected recipient follows the notice route above. Current standing beyond the latest act needs the operator's matter or a competent register; cadastral geometry and public-land catalogues are candidates until they do. |
| Whether an affected plant has protected status | The regional monumental-tree register and the matter's exact plant evidence | One registered or provisional protected-plant occurrence | Match the affected plant and select the status in force at the event time |
| Whether protected status requires another permission for this removal | The exact PPTR/local rule and competent authority decision reached by that plant and intervention | One applicable protection rule or one issued decision | Investigate this only for an affected protected plant; the full Puglia landscape-proceeding catalogue is not the population |
| Who was assigned, what field work occurred, whether removal was completed and what lawful cost resulted | Osservatorio and executing-body casefile and field records: the presided execution record, countersignature and photograph, assignment, verification and cost determination; the lawful work basis stated by the removal orders (the removal-order row) | One assignment, assessment, treatment, removal, inspection, completion or cost event | Read the actual first-party records for the matter; public procedure manuals cannot fill absent events. A coercive-direction or execution-priority act is not proof of completed removal. A published removal label or removed-plant layer (the observation row) is a lead to a first-party record, not a removal occurrence; the retained SIT capture holds no removed-plant layer after 2017. |
| Any vector or treatment observation required by an accepted calculation | Official Osservatorio, ARIF or incorporated scientific monitoring | One observation for a stated place, period, method and subject | Name the exact C consumer first, then acquire the corresponding observation population |
| Which days count for a working-day clock | Italian holiday law and enacted one-off changes | One national calendar rule | Maintain only the years reached by accepted B clocks |

## Monitoring observations

The source population is the twelve campaign workbooks and the CKAN CSV, and
all 101 observation point layers of the eight SIT services that publish them,
selected from the publisher's service inventory at capture. Their bytes live in
the content-addressed store (`SPEC.md`); `corpus/sources/monitoring/` holds the
acquisition records that name each release and page by hash, under `campaign/`
and `sit/<service>/<layer>/`. `scripts/acquire_monitoring.py` recaptures into
the store, where changed bytes get a new name. `MonitoraggioXFPasp` holds nursery-site and
Leccino-planting polygons and is not an observation source; grid, cadastre and
buffer polygons belong to the area, population and parcel rows. The tallies below
describe the capture recorded in `campaign/releases.json` and the layer records
(10 September 2026); a recapture changes them.

`observations(root)` reads every record of every retained release through one
path and keeps every original field: 4,318,100 observations. `distinct_observations(root)`
relates them: one publisher reference on one day is one observation, wherever it
is published. That gives 2,320,354 distinct observations. 1,867,537 are
identified by a reference, with at most five publications each (workbook, CSV,
host view, positives view, infected-plant layer). 452,817 cannot be related to
anything: 223,458 carry no reference (221,617 rows of the 2013–2017 workbooks and
1,841 rows of early views without an identifier column), 229,358 carry a value
their own view reuses on that day, and one workbook row has no readable day.
Counts across releases and views are never additive: 688,519 observations appear
in workbook, CSV and SIT; 590,971 in workbook and SIT; 587,422 only in SIT
(visual inspections, assessments, the current campaign and the infected-plant
layers); 549 only in a workbook; 76 in workbook and CSV.

| Published fields | Usable input and meaning |
|---|---|
| `ID`, `ID_CAMPIONE`; earlier `NUMERO_ORDINE`, `OBJECTID`, daily and device identifiers | From 2018 the reference identifies one observation across its publications, with rare same-day reuse (144 rows) that the rule below leaves single. In the 2013–2017 SIT views it is a daily counter: one value covers up to eleven plants of different species on one day. A value a view gives to several rows on one day is not an identifier; those rows stay single, uncorrelated observations. Administrative and view identifiers never identify a physical plant. |
| `DATA_RILEVAMENTO`, `DATA_CAMPIONE`, `DATA_PRELIVEO`, `DATA_RILIEVO` | The recorded observation or sampling day. Excel midnight is date storage; ArcGIS UTC epoch values are converted to the Puglia calendar day, and the early campaign's 23:00 UTC values belong to the following local day. Campaign names are not date boundaries. Report, protocol and removal dates remain separate fields. |
| `TIPOLOGIA`; explicitly named visual-inspection and assessment views | Distinguish samples, visual inspections and assessments. An observation without an analytical result is not a negative test; the 2017–2020 inspection and assessment views have no result field at all, and a visual-inspection or symptom label is not a result. |
| `RISULTATO` | The publisher's label: Positivo, Negativo, Dubbio, In attesa, Positivo duplicato, Da ricampionare, Ispezione visiva, Sintomatico, Positivo estirpato (the 2013–2017 removed-plant layers and the 2013–14 positives view). A blank is unpublished. A duplicate label restates the positive it accompanies and is not a positive by itself. The label is the observation-result part of `official-finding` and `survey-performance`; the diagnosis is the report's (next row). |
| `SPECIE`, `CULTIVAR`, `SUBSPECIE` | Recorded host, cultivar and explicit sample-level subspecies. A view's subspecies title is context; it is not substituted for an absent sample-level identification. All hosts and result states are retained. |
| `SINTOMO`, `SINTOMI` | Recorded visible drying symptoms. `Presente` and `Assente` become presence/absence; the unexplained code `0` stays unknown. The publisher states that drying symptoms are not a diagnosis. |
| Native geometry/CRS, latitude/longitude, municipality and cadastral fields | Published location. SIT supplies EPSG:32633; workbooks give longitude/latitude columns that establish axes, not a datum. Neither states positional error, so metric use waits for the population row's qualification. |
| `DOCUMENTO_CONFERMA`, `LNK_DOCUMENTO_SELGE`, `DOCUMENTO_DECRETO`; protocol and laboratory fields | Literal routes and identifiers for the report or act owning the next fact, exposed without interpreting the unread document. |
| Team, field notes, inspection details, removal labels and protection/parcel annotations | Retained on their own observation. They can lead the respective input owner to a source fact; an annotation does not fill a removal, permission or completion event. |

What the stream hands A–C, all as candidates:

- Positive observations with their day, agreed coordinates per frame and report
  route (`detection_days`, `located_positives`) for the no-detection anchor and
  the finding location. The report supplies the diagnosis the finding decision rests on. `detection_record_complete`
  is never set from the release inventory: the publisher says surveillance is not
  an inventory of all infected plants, and the inventory proves only that every
  retained release was read.
- Distinct observations with an agreed result per caller-defined occasion
  (`occasion_sets`) for negative-survey support. They are observations, not
  inspection units; unit identity needs the plant population row, so
  `observation_inventory_complete` stays unsupplied. The positive set is
  label-level: a published positive defeats a negative-survey conclusion in C
  before any report is read, which is the conservative direction.
- Over 2013–2026: 30,103 positive distinct observations, of which 9,867 are
  identified observations from 2018 on and 20,236 are 2013–2017 publications,
  where one observation can appear up to four times (workbook, host view,
  positives view, removed-plant layer) and cannot be counted once; 1,721,362
  distinct negatives; 568,889 with no agreed result (inspections and assessments
  without a result field, pending, doubtful, duplicate-only, blank, and the
  result disagreements below).

What the population shows, read and not reconciled:

- In 2013–2017 cross-release identity is unreliable. The workbooks carry no
  reference, and the SIT views use daily counters: a value a view reuses on a day
  stays uncorrelated, but a value used once in each of two views on that day
  still correlates them. Where those publications differ, the group is exposed
  as a disagreement and withheld from the positive and negative counts; where
  they agree, they merge and cannot be told from coincidence.
- 16,569 identified observations (0.9%) have publications that disagree on a
  field: species 16,523, coordinates 2,350, result 232, symptoms 2. From 2018 on
  the species disagreement is a spelling convention — the positives views write
  `OLIVO` where the host views, infected-plant layers and workbooks write
  `Olivo (Olea europaea)` for the same observation — so nearly every positive
  carries one; it is exposed, not resolved, and it is not identity doubt. By
  observation day, 6,471 of the disagreeing observations fall in 2013–2017, where
  a sample and another view's row share one counter value on one day. Only a
  result disagreement withholds an observation from the positive and negative
  counts. No publication is preferred.
- The publisher's projections disagree with each other. For 1 October–31 December
  2021, a period chosen after the reader was written, the adapter yields 1,772
  distinct positive observations on 33 days; the positives views hold 1,772 rows;
  the infected-plant layer and the workbook hold 1,769. The three extra are olive
  positives published by both the SIT positives view and the Olivo host view; the
  workbook, the CKAN CSV and the infected-plant layer omit them.

## Laboratory reports

### What is acquired

Every report is reached from an observation: the monitoring stream publishes
`DOCUMENTO_CONFERMA` and `LNK_DOCUMENTO_SELGE` on the positives views and
infected-plant layers, and nowhere else (`DOCUMENTO_DECRETO` appears on the
removed-plant layers but never carries a value). Those 1,918 routes name
1,186 distinct documents, of which 1,175 are acquired into the
content-addressed store by `scripts/acquire_reports.py` with one record per route.
16 routes fail; 3 of those documents were served on a route naming the same
file, so 11 documents are served on no route at all. This much is established.

Of the acquired documents, 475 carry a scanned annex with no text layer and
693 carry a text layer throughout. 17,761 of the 30,968 observation
publications — 57% — route to a scanned annex, and nearly every routed positive
of 2015 to 2020 is among them.

### What the sources state that this reader does not recover

Read from page images, independently of the reader, and held out of it
(`cordon-groundtruth/readings.json` in the profile cache, not in this repository):

- A scanned annex **does print its column headers**, and they **do name assays**. The
  2018, 2019 and 2020 SELGE annexes print `Esito qPCR 2010` beside `Esito qPCR 2006`
  under `ANALISI DIAGNOSTICHE SECONDO LIVELLO`; the 2015 annex prints
  `Esito analisi ELISA Lab. IAM` beside `qPCR (Harper et al., 2010)` and
  `qPCR (Francis et al., 2006)`, with the performing laboratory named in the header.
  This reader recovers none of them and previously recorded that as the document
  designating no test. It does not. The two Annex IV tests that Article 2(6) asks
  about are printed on the face of these annexes, for the years this row had
  assigned to Stage E.
- The 2015 annex identifies its samples by `Numero campione giornaliero` and
  `Codice Laboratorio` (`O 1`, `O 2`), which this reader's five-to-nine-digit
  pattern cannot accept. Its samples are identified; the reader cannot read the
  identifiers.
- Candidate recoveries measured on one such page: the flattened-line path recovers no
  header; OCR word geometry banded by row recovers `Esito qPCR` but loses the year,
  because the sub-header wraps onto a second line; an image-capable reading recovers
  the full two-tier header, both years and the data rows. No method is settled, and
  the evidence for choosing one is the ground-truth set, not this reader's output.

Until that is repaired, every absence this row reports is a statement about the
reading. Where the source is silent, where it is illegible, where extraction failed
and where a recovered fact could not be attached are four different things, and this
reader distinguishes only the last.

### What this reader currently recovers

`report(digest, store)` reads the text layer where a page has one (1,719 pages) and
runs Tesseract Italian where it has none (1,359 pages), re-reading at higher
resolution when the first pass recovers almost no rows. A page with a text layer is
read by its printed headers; a scanned page is read positionally, for the reason
above. It recovers 12,202 annex rows, 1,153 of which state no result it can classify.
Nothing is invented: an unrecognised string is unread, a cell carrying several
results states none, and a line carrying a second sample code or a third date has
absorbed a neighbour and states none.

`findings(root, store)` relates those rows to the observations whose own routes name
the document. The sample reference the laboratory prints must match, and the day the
report prints must not contradict the observation's: a row dated elsewhere is a
different sampling event whatever reference it shares. Where the routed document was
not served and another route names the same file, that document is offered as a
candidate and recorded as a substitution; where a file name carries two documents,
neither is substituted.

| What a report supplies | What this reading does not establish |
|---|---|
| The laboratory's stated result for each column it recovers, under the test as that column designates it, with the analyte the column states | Any fact it failed to recover. The scanned annexes print assay designations this reader does not read, so its silence on them is not the publisher's |
| The sample identity the laboratory prints, where the identifier has a shape this reader accepts | The official confirmation of the finding. Under D.lgs. 19/2021 Art. 28(3) the Regional Service decides that on the diagnosis; the report is the diagnosis |
| Where two differently designated tests both read detected on one sample, the Article 2(6) test and sample identities, carried on the finding by `findings.confirmation_candidates` | The genome target each test amplifies, which this reader has not been shown to recover from any document, and which an assay name does not establish (`analytical-result`) |
| The laboratory, the report date and the delivery date the letter prints | Laboratory designation, accreditation and custody, which follow their own A routes and sources |

### What the join currently shows

- 30,968 observation publications carry a route; every one is published positive or
  positive-and-removal but two negatives and two doubtfuls. 19,184 match a row in the
  document they name, 15,249 of those agreeing with the published label at the level the
  report states, 4 disagreeing, 3,931 not comparable for causes the finding names.
- The two disagreements are stated, never resolved. Sample 747145 of 2020-02-20, published negative in Positivi - Campioni 2019, is reported by CONFERMA_SELGE_Prot_93_2020 as positive for X. fastidiosa. Sample 1931257 of 2026-01-13, published doubtful in Positivi - Campioni 2026 sub. pauca, is reported by RAPPORTO_PROVA_N_3P_2026_CNR as detected for X. fastidiosa subsp. pauca; not-detected for X. fastidiosa subsp. fastidiosa, X. fastidiosa subsp. multiplex.
- 11,784 publications gain no row. The causes are counted separately and none of them
  is a statement about the document: 9,471 where the document was read
  and this reference was not found in it, 1,601 where no annex row was recovered,
  198 where no sample reference was recovered, 127 where the reference is
  printed but dated to another day, 30 where several rows carry it, and
  357 where no bytes were acquired.
- Agreement with the published label is not evidence that the document was read
  correctly: it compares this reading to the answer the publisher already holds, and
  an attachment can be wrong while preserving the expected result category. The
  letters' own stated sample counts are the same kind of check — they match the
  references recovered in 228 documents and fall short in 332 — and neither can
  stand as the correctness evidence for a reading.

Reading all 1,175 documents costs about 13 minutes once per reader version; the join
then runs in 2 seconds over the derived layer.

## Materials that are not standalone input gaps

- The BURP URL census is a way to locate regional acts. It is not itself a decision
  input.
- The 194-service SIT catalogue is a discovery surface. A service enters only when
  one of the rows above requires it; there is no remaining obligation to adjudicate
  194 services for their own sake.
- Municipal archives are used only for a required publication or notice event.
  Their complete general history is not a CORDON population.
- Historical removal records enter only when an accepted present or prospective
  input needs that history.
- Public and state land data enter only for standing or permission on affected
  land.
- PPTR, municipal plans and landscape proceedings enter only for an affected plant
  whose accepted branch requires that protection or permission.
- Large-file backup and repository preservation are engineering concerns. They are
  not evidence inputs and are not Stage D completion conditions.
- “Difficult source tables,” “copy relationships,” and “adoption lineage” describe
  work that a particular row may require. They are not separate source families or
  reasons to expand the aperture.

# Stage D input map

This is the front door to Stage D. It starts with facts required by accepted A–C,
then identifies the source that can supply them. After the 10 September purge,
the bounded national calendar remained retained. The monitoring-observation and laboratory-report families are established (first two rows, details below); prior acquisitions and case
demonstrations confer no completion on the other rows.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Established. `cordon_d.monitoring.observations` streams every retained release; `distinct_observations` relates the publications of one observation; `detection_days`, `occasion_sets` and `located_positives` hand C its candidates. Meaning and limits below. |
| What the laboratory actually reported | The report each monitoring record links: CNR-IPSP and SELGE-network confirmation letters, CNR subspecies-identification rapporti di prova, and the first-level laboratories' own rapporti | One laboratory report: a letter stating its identity, laboratory, dates, assays and analyte, and an annex listing one row per sample with the result the laboratory states for it | Established for what a public report can supply. 1,918 report routes name 1,175 documents; all but 16 are acquired. `cordon_d.reports.report` reads each from its own structure and `cordon_d.findings.findings` relates its rows to the observations that reference it. A report supplies the laboratory's diagnosis per assay with its stated analyte, the sample identity and the dates: the basis for the Osservatorio's official confirmation, not the confirmation itself, and never a Cq. Details below. |
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
| `RISULTATO` | The publisher's label: Positivo, Negativo, Dubbio, In attesa, Positivo duplicato, Da ricampionare, Ispezione visiva, Sintomatico, Positivo estirpato (the 2013–2017 removed-plant layers and the 2013–14 positives view). A blank is unpublished. A duplicate label restates the positive it accompanies and is not a positive by itself. The label is the observation-result part of `official-finding` and `survey-performance`; the finding is the report's (next row). |
| `SPECIE`, `CULTIVAR`, `SUBSPECIE` | Recorded host, cultivar and explicit sample-level subspecies. A view's subspecies title is context; it is not substituted for an absent sample-level identification. All hosts and result states are retained. |
| `SINTOMO`, `SINTOMI` | Recorded visible drying symptoms. `Presente` and `Assente` become presence/absence; the unexplained code `0` stays unknown. The publisher states that drying symptoms are not a diagnosis. |
| Native geometry/CRS, latitude/longitude, municipality and cadastral fields | Published location. SIT supplies EPSG:32633; workbooks give longitude/latitude columns that establish axes, not a datum. Neither states positional error, so metric use waits for the population row's qualification. |
| `DOCUMENTO_CONFERMA`, `LNK_DOCUMENTO_SELGE`, `DOCUMENTO_DECRETO`; protocol and laboratory fields | Literal routes and identifiers for the report or act owning the next fact, exposed without interpreting the unread document. |
| Team, field notes, inspection details, removal labels and protection/parcel annotations | Retained on their own observation. They can lead the respective input owner to a source fact; an annotation does not fill a removal, permission or completion event. |

What the stream hands A–C, all as candidates:

- Positive observations with their day, agreed coordinates per frame and report
  route (`detection_days`, `located_positives`) for the no-detection anchor and
  the finding location. The report decides the finding. `detection_record_complete`
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

Every report is reached from an observation: the monitoring stream publishes
`DOCUMENTO_CONFERMA`, `LNK_DOCUMENTO_SELGE` or `DOCUMENTO_DECRETO` on the
positives views and infected-plant layers, and nowhere else. Those
1,918 routes name 1,175 distinct documents, acquired into the
content-addressed store by `scripts/acquire_reports.py` with one record per
route; 16 routes the publisher does not serve are recorded as failures and retried
on the next run. Three publisher families, distinguished by what the page
contains and never by file name: 621 scanned confirmation letters of the
SELGE network and CNR-IPSP; 373 rapporti di prova at the same host, from
CNR-IPSP and from the first-level laboratories that sign their own (CRSFA, IAMB,
UNIBA, UNIFG, UNILE), which carry nearly every routed positive of 2021–2023; 179 CNR subspecies-identification
rapporti published beside the per-subspecies monitoring services.

`report(digest, store)` reads one document: the text layer where a page has one
(1,719 pages), Tesseract Italian OCR where it has none
(1,359 pages), re-read at higher resolution when the first pass
recovers almost no rows; the resolution used is recorded on every page. From the
letter it reads identity, laboratory, report and delivery dates, the stated
sample count, the assays and the analyte, each as the literal string printed. From
the annex it reads one row per line, by the printed headers: a merged header spans
only under its own parent, a sub-column named for a subspecies states that column's
analyte, and a table that continues across a page inherits the header above it. It
reads 12,202 rows, of which 906 state no result the reader can classify and are
carried as unread with their text. Nothing is inferred: an OCR string that is not a
result word is unread, not a result.

| What a report supplies | What it does not |
|---|---|
| The laboratory's stated result per assay column, with the assay named and the analyte the column states (Xylella fastidiosa, or a named subspecies) | A Cq value. No public report in this population prints one; the Cq that DDS 45 §IV.2 classifies lives in the laboratory's worksheets and stays open under `analytical-result` |
| The sample identity the laboratory prints, its sampling date, species, coordinates and comune where the annex carries them, and the test dates | The official confirmation of the finding. Under D.lgs. 19/2021 Art. 28(3) the Regional Service decides that on the diagnosis; the report is the diagnosis |
| Two positive Annex IV tests on one sample with distinct assay identities, where the report prints them — the identities `cordon_c.bindings.confirmation_facts` requires for Article 2(6) | Laboratory designation, accreditation or custody. Those follow their own A routes and sources |

What the join shows, read and not reconciled:

- Of 30,968 observation publications carrying a route, 19,309 match a row in the report
  they name. 15,474 agree with the published label at the level the report states,
  4 disagree, and 15,490 are not comparable — the report states a subspecies
  the view does not name, or the label is pending, duplicate or an inspection.
- The disagreements are stated, never resolved. Sample 747145 of 2020-02-20, published negative in Pianta positiva-Monitoraggio 2019 — a negative label on a plant its own publisher lists among the positives — is reported by CONFERMA_SELGE_Prot_93_2020 as positive for X. fastidiosa on both of its assays. Sample 1931257 of 2026-01-13, published doubtful in Piante infette-Monitoraggio 2026 sub. pauca, is reported by RAPPORTO_PROVA_N_3P_2026_CNR as detected for X. fastidiosa subsp. pauca; not-detected for X. fastidiosa subsp. fastidiosa, X. fastidiosa subsp. multiplex.
- 9,467 publications name a report whose rows were read but which does not
  print that sample reference, and 1,601 name a report whose annex yielded no
  readable row; both are concentrated in the scanned 2015–2021 confirmation letters,
  where the letter's own stated sample count exceeds the rows recovered in 233
  documents (212 match exactly, 12 recover more than the letter states, 718 state no count).
  That count comparison is the publisher's own check on this reading and it fails where
  OCR loses rows; the affected observations keep their published label and gain no report.
- 198 name a report whose annex prints no sample reference this reader accepts,
  30 name a report that lists the same reference twice, and 363 name one of the
  16 documents the publisher does not serve.

Reading all 1,175 documents costs about 17 minutes once per reader version; the
join then runs in seconds over the derived layer.

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

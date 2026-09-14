# Stage D input map

This is the front door to Stage D. Each row names a fact accepted A–C requires, the
source that supplies it, what one of that source's records means, and what D must
establish. The monitoring-observation family and the bounded national calendar are
established; no other row is.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Established. `cordon_d.monitoring.observations` streams every retained release; `distinct_observations` relates the publications of one observation; `detection_days`, `occasion_sets` and `located_positives` hand C its candidates. Meaning and limits below. |
| What the laboratory actually reported | Official reports linked from monitoring and their consequential annex/correction references | One report rendition with source-located sample results and document relationships | In progress over 1,180 retained PDFs (3,092 pages). The repaired reader has 209 documents with completed page readings and 391 completed relationship readings; the remaining population must be read and joined through the same path. Subscription vision resumes after 15:20 America/New_York on 14 September 2026. Current consumer results and consequential source work below. |
| Which legally adopted area contained the location on the event date | The adopting regional act and its cadastral annex; SIT demarcated-area geometry | One adopted area version, with its cadastral statements and map geometry | In progress. `cordon_d.areas.versions` binds the ordinary annex reader to A's versions; `membership_evidence` supplies supported cadastral membership. Complete the retained page readings and source checks, establish the adopted map geometry required by metric consumers. Population and remaining work below. |
| Which plants or surfaces fall inside C's distance and survey calculations | Monitoring observations, PuntiStampa, land-use or host-bearing surfaces, parcels and other population records required by the calculation | An observation, published point or polygon, parcel, grid cell or host-bearing surface according to its own source | Establish the actual population represented by each source and never substitute positives for all plants |
| Which cadastral parcel contains or intersects a relevant location | Agenzia delle Entrate and SIT cadastral geometry | One parcel geometry with its cadastral reference | Acquire the reached parcel population and preserve the source identifier; do not infer ownership from geometry. The observation row carries, uninterpreted, the cadastral references the monitoring publisher prints beside the observation: `FOGLIO`, `PARTICELLA` and `COD_COMUNE` on 8,762 records each, `ID_PART` on 8,761, `SEZIONE` on 193. `COD_COMUNE` is the cadastral municipality code (`G187`, `B809`); `COMUNE_COD` is the ISTAT code and is the observation's own administrative location, not a cadastral reference. A parcel string on an observation is not a parcel, and ownership is never inferred from it. |
| Whether the Osservatorio issued a removal measure and which plants or parcels it covered | Regional removal determination and its incorporated annexes | One adopted act plus its source-defined subject rows | Read identity, operative clause, branch, annex incorporation and correction relationships through one general reader. DDS 52/2024, 74/2024 and 138/2024 are retained and independently read-back verified in R2 as report-identity dependencies. The native annex reader supplies 183 identified plant/report associations and seven unresolved page-boundary fragments, not whole-act semantics. DDS 74/2024 links old code 1673519 to a different host/place from the laboratory row; DDS 138/2024 adopts corrected 1674070 at the report location. Any correction or withdrawal of the earlier administrative target remains unestablished and must be investigated by this consumer; laboratory replacement alone cannot supply it. |
| Whether a legally consequential notice, delivery, publication, receipt or response happened | The determination's own text for its declared route; the competent municipality's albo pretorio record for the seven-day publication every plan version requires; BURP and the regional sites the plans name; the Osservatorio's communication record and municipal notification attempts for recipient effect; PEC transmission to ARIF and the Prefettura; ARIF's authenticated election record or the owner's PEC for the response | One event at one time concerning one document, one sender and one recipient under one route; or one publication with its start, continuity and end | Select the source by the route A selects for the act and recipient: completed personal communication, including the code-of-civil-procedure forms for unreachable recipients; mass publicity only where the act establishes that recipient number made personal communication impossible or particularly burdensome; a reasoned immediate-effect clause in a non-sanctioning measure; or cautionary-and-urgent character. An immediate-effect or cautionary clause makes the measure operative; it is not notification, and a clock anchored on notice or publication runs only from that event. A publication record proves the publication duty, and its end date anchors the election window; publication alone establishes neither recipient effect nor silence, refusal, breach or cost liability. Sending, delivery, publication, recipient effectiveness and response stay distinct. The monitoring stream publishes a `SCELTA_PROPRIETARIO` column on 8,762 records and carries no value in any of them, so it supplies no owner election; the observation row records that. |
| Who has the consequential relationship to the affected land | The determination's incorporated annex naming addressees by comune, foglio and particella; later acts that correct listed owners; the Osservatorio's matter and transmitted cadastral and owner data; a competent public-asset register for public land | One addressee position in one act version, or one stated ownership, occupation, management or other legally relevant relationship | The annex establishes the position the act published for each parcel, not that the named person held the land. An effective correction act replaces the listed position for the parcels it names; its effect against the corrected recipient follows the notice route above. Current standing beyond the latest act needs the operator's matter or a competent register; cadastral geometry and public-land catalogues are candidates until they do. The monitoring stream publishes `CUAA` and `AZIENDA` columns on 86 records and carries a sentinel in every one, so it supplies no holder identity; the observation row records that. |
| Whether an affected plant has protected status | The regional monumental-tree register and the matter's exact plant evidence | One registered or provisional protected-plant occurrence | Match the affected plant and select the status in force at the event time. The observation row carries, uninterpreted, `MONUMENTALE_ARIF` on 586 records — a monitoring publisher's flag beside the observation, not a register entry, and no substitute for matching the plant in the register. |
| Whether protected status requires another permission for this removal | The exact PPTR/local rule and competent authority decision reached by that plant and intervention | One applicable protection rule or one issued decision | Investigate this only for an affected protected plant; the full Puglia landscape-proceeding catalogue is not the population. The observation row carries, uninterpreted, the landscape and hydrogeological flags the monitoring publisher prints beside the observation: `UCP_PPTR` on 7,078 records, `VINCOLO_IDROGEOLOGICO` on 1,462, `BP_PPTR` on 1,172, `PAI` on 215. A flag is a lead to the applicable rule, never the decision. |
| Who was assigned, what field work occurred, whether removal was completed and what lawful cost resulted | Osservatorio and executing-body casefile and field records: the presided execution record, countersignature and photograph, assignment, verification and cost determination; the lawful work basis stated by the removal orders (the removal-order row) | One assignment, assessment, treatment, removal, inspection, completion or cost event | Read the actual first-party records for the matter; public procedure manuals cannot fill absent events. A coercive-direction or execution-priority act is not proof of completed removal. A published removal label or removed-plant layer (the observation row) is a lead to a first-party record, not a removal occurrence; the retained SIT capture holds no removed-plant layer after 2017. The observation row carries, uninterpreted, `DATA_ESTIRPAZIONE` on 806 records and `RIF_DECRETO` on 803 — the removal date and decree reference the monitoring publisher prints beside the observation. Like the removal label beside them, they are a lead to a first-party record, never a removal occurrence. It also records that the monitoring stream publishes a `DOCUMENTO_DECRETO` column in 970 records of the 2014-15 and 2016-17 removed-plant layers: 591 carry nothing and 379 carry a sentinel, so that column supplies no route to a decree either way. |
| Any vector or treatment observation required by an accepted calculation | Official Osservatorio, ARIF or incorporated scientific monitoring | One observation for a stated place, period, method and subject | Name the exact C consumer first, then acquire the corresponding observation population |
| Which days count for a working-day clock | Italian holiday law and enacted one-off changes | One national calendar rule | Maintain only the years reached by accepted B clocks |

## Monitoring observations

The source is every observation the Regione publishes: twelve campaign workbooks, the
CKAN CSV, and the 101 observation point layers of the eight SIT services that carry
them. `catalogue/service-inventory.json` retains the publisher's whole advertised
inventory — 194 services, 3,726 layers, 105 tables, captured without a keyword filter —
and it is what supports the selection: 61 services publish point layers, and of those
eight publish monitoring observations. `MonitoraggioXFPasp` publishes nursery sites and
Leccino plantings, and the grid, buffer and cadastral polygons belong to the area,
population and parcel rows. Bytes live in the content-addressed store (`SPEC.md`), the
acquisition records under `corpus/sources/monitoring/` name every release and page by
hash, and `scripts/acquire_monitoring.py` recaptures into the store, where changed bytes
take a new name. Every figure below describes this capture; a recapture changes them.

One record is one published observation: a sample, a visual inspection or an assessment,
on one day, with whatever result its publisher printed. `observations(root)` reads all
4,318,100 of them through one path and keeps every original field.
`distinct_observations(root)` relates them — one publisher reference on one day is one
observation wherever it appears — giving 2,320,354 distinct observations with at most
five publications each. 1,867,537 carry a usable reference; the rest stay single,
because 229,358 carry a value their own view reuses that day, 223,458 carry no
reference, and one has no readable day.

| Published fields | What the reader takes from them |
|---|---|
| `ID`, `ID_CAMPIONE` | The observation reference. From 2018 it identifies one observation across its publications. In the 2013–2017 SIT views it is a daily counter covering up to eleven plants of different species, so a value a view gives to several rows on one day is not an identifier and those rows stay uncorrelated. No identifier here identifies a physical plant. |
| `OBJECTID`, `ID_GIORNALIERO`, `NUMERO_ORDINE`, `IDANDROID` | The publisher's other identifiers, carried under their own names, never merged into the reference and never compared: a view's feature id differs between views by construction. 12,940 observations the reference cannot identify are identified by one of these. |
| `DATA`, `DATA_RILEVAMENTO`, `DATA_CAMPIONE`, `DATA_PRELIVEO`, `DATA_RILIEVO` | The recorded observation or sampling day. Excel midnight is date storage; ArcGIS UTC epochs become the Puglia calendar day, and the early campaign's 23:00 UTC values belong to the following local day. Campaign names are not date boundaries. Report, protocol and removal dates stay separate fields. |
| `TIPOLOGIA`, and the explicitly named inspection and assessment views | Samples, visual inspections and assessments, kept apart. An observation without an analytical result is not a negative test: the 2017–2020 inspection and assessment views have no result field at all. |
| `RISULTATO` | The publisher's label: Positivo, Negativo, Dubbio, In attesa, Positivo duplicato, Da ricampionare, Ispezione visiva, Sintomatico, Positivo estirpato. A blank is unpublished. A duplicate label restates the positive it accompanies and is not a positive by itself. The label is the observation-result part of `official-finding` and `survey-performance`; the laboratory diagnosis is the report's; official confirmation remains the Service's decision. |
| `SPECIE`, `CULTIVAR`, `SUBSPECIE` | Recorded host, cultivar and sample-level subspecies. A view's subspecies title is context and is never substituted for an absent sample-level identification. Every host and every result state is retained. |
| `SINTOMO`, `SINTOMI` | Recorded visible drying symptoms. `Presente` and `Assente` become presence and absence; the unexplained code `0` stays unknown. The publisher states that drying symptoms are not a diagnosis. |
| Native geometry and spatial reference, `LONGITUDINE`, `LATITUDINE` | The published location, read into one frame. The SIT services state EPSG:32633 on every page. The campaign releases publish degrees and state no datum anywhere — not in the CKAN package, the download page, a sheet, a header or a legend — and those degrees are EPSG:4326, established from the publisher's own redundancy: over 1,279,135 testable pairs — an observation published both ways, with one point on each side — the stated SIT point reproduces the printed pair to under a centimetre, while ED50 and Monte Mario / Roma 40 miss by 127 m and 71 m. `scripts/check_frames.py` re-derives that per release from the store and fails when one stops fitting; `SPEC.md` says when it runs. Three releases cannot be tested that way: `CAMP_2013_2014`, `CAMP_2014_2015` and `CAMP_2016_2017` publish no observation reference in any of their 221,397 located rows, so nothing pairs them to a SIT publication by identity. Their frame rests instead on same-day proximity, because a datum shift translates a whole point cloud and shows without identity — `CAMP_2014_2015` and `CAMP_2016_2017` place 100% of their points within a centimetre of a same-day SIT point, and `CAMP_2013_2014` places 99.05%, where ED50 would put them 128 m away. That last figure is the weakest ground in the family and sits 0.05 points above the agreement the check requires, so a recapture of that release is the one to read rather than assume. What the redundancy cannot separate is which frame of that datum family the publisher would name: without an epoch the transformation between EPSG:4326 and EPSG:4258 is the identity, so both reproduce the printed pair exactly and the check reports them as tied. What it excludes are the frames that would move a location. The frame belongs to the pair rather than to the record: a service states its spatial reference for the geometry it publishes, and seventeen of these layers print degree columns beside that geometry, so degrees taken from the columns are read at EPSG:4326 whatever the page declared for its geometry. A pair this reader cannot place in the frame beside it is not carried, and its absence says so. Because every location has a frame, the publications of one observation are compared in one frame rather than held apart by the frame they were printed in; what a consumer receives is still a pair a publisher printed, in the frame that publisher stated, because the reprojection is this reader's and belongs under no value the operator reads as published. No source states positional error, so metric use waits for the population row's qualification. |
| `COMUNE`, `COMUNE_COD`, `PROVINCIA`, `LOCALITA`, `ALTITUDINE` | The observation's own administrative location. `COMUNE_COD` is the ISTAT municipality code; the cadastral code is `COD_COMUNE`, which belongs to the parcel row. `LOCALITA` and `ALTITUDINE` are read and neither supplies a value: all 86 records publishing `LOCALITA` carry a sentinel, and all 86 publishing `ALTITUDINE` carry nothing. Those are different absences with different remedies, which is the distinction this row exists to keep. |
| `SQUADRA`, `TECNICO`, `COD_TECNICI`, the inspector-name columns, `NOME_DISPOSITIVO`, `IMEI`, `CODICE_CAMPIONAMENTO`, `STATO`, `NOTE_RILEVATORE`, `NOTE`, `NOTE_SIT`, `CRITICITA_NOTE` | Who performed the observation, with what instrument, in which campaign, and what they noted. One fact under several publisher names: the 2016 infrastructure survey prints a team code and per-inspector columns where later releases print `TECNICO`. `CODICE_CAMPIONAMENTO` names a campaign shared by hundreds of records and is never an identity. A note, a device name and a publication status describe the publication rather than the observation, so they are read and not compared. |
| `DOCUMENTO_CONFERMA`, `LNK_DOCUMENTO_SELGE` | The literal route to the laboratory report, under the column that published it: 22,206 and 8,762 routes. The document itself is unread here. |
| Protocol, laboratory, cadastral, demarcated-area, protected-plant and removal fields, including `DOCUMENTO_DECRETO` | Carried as the literal the monitoring publisher printed, for the row that owns each fact, interpreted by nobody here. A transcription beside an observation does not fill a report, a parcel, a permission or a removal. |

What the stream hands A–C, all as candidates:

- Positive observations with their day, their agreed location and their report route
  (`detection_days`, `located_positives`) for the no-detection anchor and the finding
  location. The report supplies the diagnosis beneath the finding decision. `detection_record_complete` is never set
  from the release inventory: the publisher states that surveillance is not an inventory
  of all infected plants, and the inventory proves only that every retained release was
  read.
- Distinct observations with an agreed result per caller-defined occasion
  (`occasion_sets`) for negative-survey support. They are observations, not inspection
  units — unit identity belongs to the plant population row, so
  `observation_inventory_complete` stays unsupplied. The positive set is label-level, so
  a published positive defeats a negative-survey conclusion before any report is read,
  which is the conservative direction.
- Across 2013–2026: 30,103 positive distinct observations, 1,721,362 negative, and
  568,889 with no agreed result — inspections and assessments with no result field,
  pending, doubtful, duplicate-only, blank, and the result disagreements below. The
  positives are not 30,103 findings: 9,867 are dated 2018 on, 55 of those uncorrelated,
  and 20,236 are 2013–2017 publications, 13,399 of them uncorrelated singletons, where one
  observation can appear in the workbook, the host view, the positives view and the
  removed-plant layer and cannot be counted once. Counts across releases and views are
  never additive for the same reason. Of the positives, 29,662 hand a consumer one agreed
  location; 337 hand none because their publications place them apart, and 104 because no
  publication carries a place. The 337 are almost all an identity limit rather than a
  dispute about one observation's place: 333 are dated before 2018, all 337 have
  publications naming more than one host, and 333 have all their publications in one
  frame — they are the daily-counter groups below, where two views used one counter on one
  day for different plants, so the reader is comparing the places of two observations. The
  remedy is identity, not another source of coordinates.

What the population shows, read and not reconciled:

- In 2013–2017 cross-release identity is unreliable. The workbooks carry no reference and
  the SIT views use daily counters, so a reused value stays uncorrelated while a value
  used once in each of two views on one day still correlates them. Where those
  publications agree they merge and cannot be told from coincidence.
- 16,630 observations have publications that disagree on a field: species 16,523,
  `COMUNE` 8,203, coordinates 2,367, result 232, symptoms 2. Each is exposed and no
  publication is preferred. Only a result disagreement withholds an observation from the
  positive and negative counts. Much of it is the publisher's own convention, but not all
  of it. Of the municipality disagreements 8,090 are casing alone; of the remaining 113,
  eleven are one municipality under two separators (`SAN VITO DEI NORMANNI` beside
  `SAN_VITO_DEI_NORMANNI`) and four print Carovigno's own ISTAT code beside its name, so
  **98 name a different municipality** — `Francavilla Fontana` beside `Oria` on 71 of them,
  `Capurso` beside `TRIGGIANO` on eight. Every one of the 98 is two adjacent municipalities,
  and in every one of them the publications place the observation at a single agreed point
  and name one host. So this is not identity doubt: 71 are 2017 publications, where a shared
  daily counter can mean two observations, but 27 are dated 2020 to 2024 and correlate on a
  reference that identifies one observation, and those are the publisher assigning one place
  to two municipalities. The remedy differs accordingly — ask the publisher, or resolve the
  point against municipal geometry in the area row — and it matters because the albo pretorio
  publication duty attaches to a municipality. The 16,523 species disagreements are
  not split here, and the reason is worth stating: 1,334 print an observation kind
  (`accertamento`) in the species column rather than a host, which is checkable, but
  separating a host named twice from two different hosts is not: `OLIVO` beside
  `Olivo (Olea europaea)` and `Mandorlo (Prunus dulcis)` beside `MANDORLO` are one host
  under a Latin binomial and an Italian vernacular name, while `MANDORLO` beside `OLIVO`
  is two hosts, and both shapes recur under several spellings apiece. Telling them apart
  needs a host synonym list this row does not have, so no count is given for either —
  three attempts at one produced three different numbers, which is the evidence that the
  rule was being chosen after the fact. Every disagreement is exposed either way.
- The publisher's own projections disagree with each other. For 1 October to 31 December
  2021 the stream yields 1,772 distinct positive observations on 33 days and the SIT
  positives views hold 1,772 rows, while the infected-plant layer and the workbook hold
  1,769: three olive positives are published by the positives view and the Olivo host view
  and omitted by the workbook, the CKAN CSV and the infected-plant layer.
- Two publications are the same place when they sit within a centimetre of each other on
  the ground, measured by Stage C's geodesic because the stage that owns geometry owns
  what counts as one place. That is a threshold on meaning with a finite margin: across
  the population the widest separation among agreeing publications is 0.00074 m and the
  nearest among disagreeing ones is 7.17 m. The headroom is about seven metres, not the
  thousands of kilometres the transposed rows below suggest, and the four positives of
  9 December 2019 whose SIT views differ by about 11 m sit just beyond it.
- The coordinate disagreements are mostly the same identity limit: 2,341 of the 2,367 are
  dated before 2018 and 2,075 are separated by more than a kilometre, which is two
  observations sharing a counter rather than one observation disputed. Twenty-one have
  publications in more than one frame, and 17 of those are the publisher placing one
  observation on another continent: sixteen rows of
  `CAMP_2017_2018` on 22 February 2018 carry their axes transposed, about 3,400 km from
  where the SIT view puts them, and one row of `CAMP_2024` carries a corrupt pair 5,484 km
  out. All 17 are published negative. Both printed numbers are valid for the column they
  sit in, so only the publisher's other publication of the same observation exposes them.
  The remaining four are positives of 9 December 2019 whose SIT views differ by about
  11 m.
- Every value a reading does not carry names why, in the record's own terms: 87 distinct
  field-and-cause pairs across 64 fields, distinguishing a field the record does not
  publish, one published carrying no value, one carrying only a sentinel, and one
  carrying a value this reader does not interpret. No published field is passed over in
  silence. `DistinctObservation.uncorrelated_because` answers why a group could not
  correlate; these answer, for one publication and one field, why this reader carries
  nothing.
- 1,118 of those entries, over 13 field names, add that no reader of this stage claims
  the column. That is what the reader knows; whether a row owns the fact behind it is a
  judgment nobody has made, and several of the thirteen — the grove attributes and the
  grid cell — are plainly the plant and area rows' subjects. They also state what the
  record printed, because an unclaimed column carrying a sentinel and one carrying
  nothing are different absences: 942 sentinels and 176 empty. No unclaimed column
  carries a value this reader could have read, anywhere in the population, so the pending
  ownership judgment costs no fact today. All thirteen appear in one release, the 86-row
  2016 infrastructure survey.
- 12,663 records state their place twice, as an ArcGIS geometry and as `LONGITUDINE` and
  `LATITUDINE` columns beside it. The reading takes the geometry, and the two remaining
  causes above record that it did not take the printed pair — and say so differently where
  the two statements disagree, because within one record that is the only thing that could
  see a transposition of the kind found across releases above. Every one of the 12,663
  agrees today, the widest by 1.2 mm.

## Laboratory reports

The retained population comprises 1,910 captures with source bytes and 1,180 distinct PDFs.
The current offline rebuild recovers 209 complete document page readings without
provider calls; 971 documents still require completed extraction. There are 391
completed document-relationship readings. The ordinary full-observation join after
the reader repairs covers all 2,320,354 observations: 2,923 have a unique matched
report row, 168 have a provisional match, 106 have competing report-row occurrences,
and four have competing observation identities for their report row. The reverse view
contains 1,322 unmatched report rows. These figures describe retained extraction
version `bf12550befda11586c24`, before further subscription reading, and do not establish
source-family completeness or official confirmation.

Finish the interrupted page readings and their joins, including the fine-print attachment whose source has 13 rows but whose saved reading
recovered 12. A saved complete-document response formerly rejected by the page-pair
partition now assembles through the ordinary reader without another model call. The runner
rereads an incomplete page with magnified source views before declaring its document
assembled. Continue full-population relationship reading, resolve unbound source
qualifications and multi-document identity/scope, and correct the older CNR91P
revision-date proposal from its source. The generic identifier role does not require
guessing which organization assigned a literal code; attachment still requires the
observation's report route, source identity and bidirectional uniqueness.

The failed published routes are reconciled in the existing acquisition records.
Four retained alternatives resolve CNR-IPSP 36/2024, 10/2024, 70M/2026 and SELGE
173/2020 (the URL incorrectly names 172). Owen's seven supplied PDFs resolve the
other nine failed routes: CNR 2/2024, 5/2024 and 9/2024; IAMB 7/2021, 8/2021 and
report 4 / Dir 02/848; and UNIFG 8_POSITIVI/2021. The three supplied CNR files are
byte-identical to already-held zero-padded publisher copies. All seven supplied
files are stored with user-intake provenance and replicated to R2 with matching
readback hashes. Their readings run through the ordinary subscription reader;
route recovery alone does not establish a completed analytical join.

The IAMB components contain the full rows referring observations name: 72, 104
and 42 respectively. Report 8 contains 105 rows, including additional ID 1222184.
The supplied components omit their covering letters. Their result tables can
supply literal results and sample correspondence; establishing the particular
analytical method and issuance from the laboratory itself still requires the
covering letters or equivalent evidence for IAMB 7 (published issue date
11 October 2021), 8 (15 October 2021) and 4 / Dir 02/848 (30 September 2021).
These tables are recovered and are not active document searches. UNIFG's letter
names 8_POSITIVI, while its 18-row annex names 8_DUBB in conferma; both headings
and the annex's positive results must survive reading.

Only SELGE 196/2020 and 197/2020 remain unrecovered among the published observation
routes. Owen reports server-side FileNotFoundException for their backing files;
the acquisition records prohibit automatic retries. Searching the retained PDF
text layers found no alternative carrying either identity; scanned-only identities
still depend on completion of the retained vision population. No new broad hunt
is authorized.

The originals SELGE 355/2020, IAMB 34/2022 (15 September, Dir 02/1097) and IAMB
4/2023 (14 September, Dir 02/1034) are needed for the earlier report's content and
an exact before/after correction comparison. They are not blanket prerequisites
for the successor's independently stated results. Retained SELGE 360/2020 page 1
expressly cancels and replaces 355 and supplies its own two-method statement and
12-sample result annex. IAMB 39/2022 pages 1–2 independently supply the corrected
9 September Monopoli positive list and Harper real-time PCR method. IAMB report
4 rettificato, issued 3 October 2023 (file named 9/2023), independently supplies
the 7 September Castellana Grotte positive list, Harper method and received-sample
qualification. Neither IAMB correction identifies which individual values changed;
no changed-column delta may be inferred merely from the word Positivi. Recovery
of a predecessor is required when a consumer actually needs that earlier state
or delta, not to consume these independently stated corrected facts.

The reached ARIF application requires
regional login; no authenticated records have been accessed. Laboratory designation,
status and custody evidence remain necessary where the accepted confirmation branch
requires them; report extraction alone cannot supply those facts.

Administrative annexes retained from DDS 52/2024, 74/2024 and 138/2024 supply 183
identified associations. All seven page-boundary fragments have been visually
reconciled: they complete host/zone cells of the preceding row. The reader derives
continuation only across the same annex, consecutive physical and printed pages,
matching columns and blank identity cells, retaining both cell locations. All 183
associations survive; no fragment is treated as another plant. The seven affected
observation joins currently still need their laboratory report readings.
An act can establish a derived occurrence correspondence without equating different
literal identifier strings. The older CNR73F act association conflicts with its report
row; the corrected report and later act agree. Laboratory replacement does not prove
administrative withdrawal. Source-declared correction relationships and their date
conflicts survive; an exact cancellation phrase is not a prerequisite for reading a
cancellation. Whole-report replacement does not assert that every column changed.

`corpus/sources/reports/records.json` owns the route captures. Successful captures
and distinct byte versions are retained; a current failed attempt names its cause.
A filename shared by a failed and successful route supplies an acquisition
candidate. Located source reconciliation in the same acquisition record can establish
the recovered document independently of the failed transport. `scripts/acquire_reports.py`
discovers report routes through the declared monitoring releases and can follow
source-located references and explicitly recapture an admitted route.

`cordon_d.report_extraction` reads the original page images with bounded vision
and native-cell candidates. Schema-constrained output keeps one machine-readable response. Its representation carries literal tables, source-row occurrences,
header roles and scoped report statements. The original and latest table-header pages are supplied as context to later blocks; its meaning is not assigned to them automatically. The model is explicitly configured;
`claude-sonnet-5` at medium effort is the selected baseline, with a source-only high-effort reread for an incomplete page or detected unattached sampling date. Fine-print page completion receives overlapping 240-dpi source views as well as the original PDF. Specialist OCR is not a mandatory pass.
An unresolved region is a reading limitation, never proof of source silence.
Code copies selected native values and materializes rows; identifiers remain
strings and invalid dates retain their original text and named parsing limit.
Statements carry model_proposed_reading provenance; they are claims about the source, not certified quotations. Selected native cell copies and visual transcriptions carry distinct provenance. Rejected nonliteral components retain a cause.

`cordon_d.reports.report(digest, store, extraction_version=...)` reads the selected
cache without network access; `read_reports.py --extraction-version` selects a retained version explicitly. Missing or partial readings are visible. A missing
coordinate, unparsed date or incomplete metadata component does not discard a
separately readable diagnostic result. Page accounting is structural coverage,
not certification that every source meaning was recovered.

`cordon_d.findings.findings(groups, reports_root, store, extraction_version=...,
known_through=...)` consumes `monitoring.distinct_observations(...)`. It preserves
the publishing field and route on each member. Matches require the referenced
source rendition, a source-supported literal identifier and a relationship unique
in both directions within that report. Valid contradictory sampling dates remain
conflicts; undated candidates are not silently displaced by dated ones. Separate
reports can each attach to one observation without one replacing the other.
Repeated physical rows remain available. Corrections require their own source
relationship and affected scope; recency and filename suffixes cannot adjudicate them.

`cordon_d.report_relations` reads source-declared document relationships separately
from row transcription. A resolved whole-report replacement can be followed from
an observation's original route; the earlier source remains historical evidence.
Amendments, ambiguous predecessors and cycles cannot silently select a current row.
The graph preserves model-proposed provenance and unverified identity components.
It does not establish administrative effect or turn a cited predecessor date into
this rendition's issue date. Quotation and locator checks validate literal support; semantic source reading establishes
the proposed effect. A contradictory printed issue date does not erase an explicitly
named predecessor or become an inferred corrected date. Retained responses preserve
their model and prompt provenance.

`cordon_d.source_associations` reads native ruled administrative tables through
printed headers and source-qualified annex continuation. It preserves source
coordinates, unresolved fragments and unexamined tables; personal owner columns
are outside this association reader. The finding join requires the observation's
own report route, an explicit act report number/date, the published plant reference,
and unique report-row coordinates agreeing at the act's printed decimal precision.
That is derived occurrence correspondence, not an identifier alias. Competing act
rows and conflicts survive. Both report and act acquisition respect the knowledge
cutoff; the act's assertion is not backdated to sample collection.

Each diagnostic column and its stated analyte stays separate, with comparison to
the original publication label and a cause where comparison cannot be made.
Agreement is a cross-check, not a correctness test. The reverse view retains rows
with no observation, including negative results. `confirmation_inputs` selects
explicit source-result occurrences and supplies the unchanged Stage C interface;
canonical identities and legal qualifications require evidence and otherwise
remain unresolved. Neither a report row nor two differently spelled test labels
establishes the Service's official confirmation. Laboratory designation, custody,
run qualifications and official confirmation retain their existing contract owners.

`scripts/read_reports.py` inventories work by default. Paid extraction is explicit,
capped and resumable, with raw responses reusable independently of deterministic
projection changes. The same command emits the local forward/reverse join and can
exercise the C adapter for an explicitly selected observation and result pair.
Single-page output overflow stops with a reading limitation; geometric row subdivision is not implemented. A detected-table inventory can expose an omitted native region, but cannot certify discovery on scanned pages.

The remaining population must be read and its consequential source relationships
resolved before row 2 is established; bounded source checks and passing software
tests do not confer that status.

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

The join retains identifier-only display occurrences but requires an analytical
result before they compete as finding-result rows. Direct inspection of UNIBA
87/2023 confirms the small table and expanded transposed display; five competing
joins are resolved by this correction. Further source rereading is required for
its remaining display relationships, UNIBA 15/2024 and 66/2023, and the early
reports whose daily counters and laboratory identifiers collide. Direct inspection of SELGE 139/2015 page 2 confirms a transcription error:
the source prints 40.42257829 for daily sample 1, while the saved reading has
40.22257829. The monitoring coordinate agrees with the source. The affected pages
and the three UNIBA display readings are scheduled for a source-only high-effort
reread after reset, before the general row population. No code
chooses an identifier namespace or repairs a digit from result agreement.

## Demarcated areas

Accepted A reaches 28 instruments through 29 area versions. A owns their identity,
interval, subspecies and operative legal meaning. The acquisition records in
`corpus/sources/areas/acts.json` retain 27 documents (273 pages), including the
procedure act DDS 45/2025. DDS 148/2024's own body still needs recovery; a successor's
recital does not supply its annex. DDS 69/2021 adopts maps without a cadastral table.

`scripts/read_annexes.py` reads every physical page of each retained document through
Claude subscription vision (`claude-sonnet-5`, medium effort). Native cells are
candidates for exact copying; the model binds captions and rows and transcribes values
not faithfully represented by those cells. There is no exhibit registry or keyword
page exclusion. The 154 saved page readings are retained under
`corpus/sources/areas/readings/`; 119 pages remain to be read after the subscription
reset at 15:20 America/New_York on 14 September 2026. Re-reading an erroneous page
preserves the previous response in the derived store. This is the current reading
population, not a claim of source-family completion.

`cordon_d.areas` projects the saved readings into zone, province, municipality and
cadastral scope. Table headings, qualifications, row notes and physical page/table/row
locations travel with each statement into membership support. Page prose stays with
its version; A remains the owner of its legal effect. Repeated physical statements
remain source occurrences. A missing reading or inventory cannot establish that an
act contains no cadastral table.

The reader distinguishes a reached sheet from a parcel wholly inside the zone.
The annex's asterisk is retained at the grain it qualifies: a sheet asterisk covers
the sheet; a parcel asterisk covers that parcel. An unstarred listed parcel merely
intersects the zone and does not establish whole-parcel membership. Sections and
named sheet developments remain distinct. An unmatched cadastral query does not
establish that the place is outside the adopted map. Zone and stated measures regime
remain separate facts.

Complete the outstanding page readings and resolve the watermark-contaminated
municipality cells on DDS 106/2025 page 13 through the general reader. Direct source
checks of DDS 158/2024 page 7 and DDS 8/2024 page 7 distinguish repeated tables and
merged cells from the earlier comparison transcription's divisions; those reference
comparisons are not correctness certificates. The remaining DDS 93/2024 pages 9–10 and DDS 94/2024 page 8
comparisons likewise introduced section separators absent from the source. Direct
inspection and membership checks confirm the section identities and asterisks.
Membership now carries every supporting physical statement, with distinct source
locators, rather than stopping after the first match. The old heuristic-reader sheet totals are withdrawn.

The metric consumers already admit adopted geometry. Obtain the consequential
version's map or publisher geometry, establish its correspondence to the adopting
act, and qualify its frame and positional error. A publication date alone does not
bind a polygon to an adopted version. An empirically established error bound is
permitted; a publisher-stated bound is not the only route. DDS 106/2025's mapped
extension into Basilicata and the acts' partial-parcel rules must survive this binding.
The cadastral tables are useful evidence within their stated extent, not a substitute
for the missing map correspondence. Operative legal-area state and Annex III
eligibility remain upstream A meanings.

DDS 45/2025 physical page 34 (annex printed page 27) names the post-adoption
shapefile transmission from InnovaPuglia to the Osservatorio and ARIF. A shapefile
is one sufficient route, not a prescribed prerequisite where equivalent geometry
and correspondence evidence exists. The current multiplex publisher service is
retained in the existing act acquisition records and read by
`cordon_d.areas.published_geography`: ten native polygon occurrences, including
Santeramo and Ginosa's separate Basilicata buffer components, in EPSG:32633.
Each layer's returned object IDs were checked against its independent ID response.
The features do not state an adopting-act identity or positional bound; capture
date and place labels alone cannot establish their adopted-version applicability.
Direct comparison with DDS 106/2025 physical page 10 agrees on Ginosa's three
infected components, relative arrangement, buffer outline and Basilicata component.
That supports depicted-area correspondence; numerical georeferencing and version
applicability still need sufficient evidence. Another copy of these polygons is
not the missing input.

The 27 act PDFs already contain bundled map annexes. They have no embedded
geospatial coordinate dictionaries. The 49 named standalone annex hashes are
not held as separate blobs; that does not make their bundled contents absent.
Prior acquisition records name further geographic packages and imagery-service
metadata, but the records alone do not establish possession of those source bytes.
The current shared store contains no ZIP archive with shapefile members.
No original plant photographs/sampling sheets or imagery accuracy assessment has
been established from the examined retained sources. Those facts remain owned by
the positional and plant rows, rather than becoming a new map-document checklist.

DDS 148/2024 is not an active search priority. Its Santeramo ST26 intermediate
version remains a specific correspondence question; use a concrete existing
package or publisher lead if it can resolve that version. Do not substitute a
later boundary or restart an exhaustive search. Continue retained cadastral
membership and current-map correspondence independently of that recovery.

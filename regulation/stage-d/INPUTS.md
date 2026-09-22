# Stage D input map

This is the front door to Stage D. Each row names a fact accepted A–C requires, the
source that supplies it, what one of that source's records means, and what D must
establish. The monitoring-observation family and the bounded national calendar are
established; no other row is.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Established. `cordon_d.monitoring.observations` streams every retained release; `distinct_observations` relates the publications of one observation; `detection_days`, `occasion_sets` and `located_positives` hand C its candidates. Meaning and limits below. Reach (`SPEC.md`, admission): observation-dated; complete over the longest reachable backward period from the decision date, negatives included; earlier observations serve identity continuity, a rendition an in-reach correction chain requires, and reader verification. |
| What the laboratory actually reported | Official reports linked from monitoring and their consequential annex/correction references | One report rendition with source-located sample results and document relationships | Not established. Retained readings, usable correspondences and material source/consumer gaps are under [laboratory reports](#laboratory-reports); PR #18 owns population completion and PR #24 the bounded compound-field repair. Sampling-date reach includes every result polarity and consequential correction chain. Reading inventory is not semantic acceptance. |
| Which legally adopted area contained the location on the event date | SIT demarcated-area geometry and the adopting regional act | One published area feature in one legal version | Acquire every version reached by A whose interval overlaps an event date inside the reach; bind geometry to its adopting act; use the version in force at the event time. The observation row carries, uninterpreted, `ZONA` on 219,120 records and `ZONA_DELIMITATA` on 8,762 — the zone status and area name the monitoring publisher prints beside the observation (`Zona Contenimento - Salento`, `Area delimitata Monopoli`), which are not the adopted geometry in force and do not stand in for it. Its `BUFFER` column is published with no value in any record. Reach (`SPEC.md`, admission): by A's interval overlapping an in-reach event date; whether the four-year rule reads the area as it stood at the time is an A question. DDS 88/2024's containment description conflicts with its reached report's Valle d’Itria buffer description; reconcile the event-time adopted geography through this owner. |
| Which plants or surfaces fall inside C's distance and survey calculations | Monitoring observations, PuntiStampa, land-use or host-bearing surfaces, parcels and other population records required by the calculation | An observation, published point or polygon, parcel, grid cell or host-bearing surface according to its own source | Establish the actual population represented by each source and never substitute positives for all plants |
| Which cadastral parcel contains or intersects a relevant location | Agenzia delle Entrate and SIT cadastral geometry | One parcel geometry with its cadastral reference | Acquire the reached parcel population and preserve the source identifier; do not infer ownership from geometry. The observation row carries, uninterpreted, the cadastral references the monitoring publisher prints beside the observation: `FOGLIO`, `PARTICELLA` and `COD_COMUNE` on 8,762 records each, `ID_PART` on 8,761, `SEZIONE` on 193. `COD_COMUNE` is the cadastral municipality code (`G187`, `B809`); `COMUNE_COD` is the ISTAT code and is the observation's own administrative location, not a cadastral reference. A parcel string on an observation is not a parcel, and ownership is never inferred from it. |
| Whether the Osservatorio issued a removal measure and which plants or parcels it covered | Regional removal determination and its incorporated annexes | One adopted act plus its source-defined subject rows | Not established. The `removal-orders` binding owns admission and routes; [removal measures](#removal-measures-required-population-and-present-coverage) states usable capability and pending dependencies. Preserve prescribed work, target/addressee occurrences and administrative relationships. Every admitted order remains in reach until execution or withdrawal closes it, regardless of age. |
| Whether a legally consequential notice, delivery, publication, receipt or response happened | The determination's own text for its declared route; the competent municipality's albo pretorio record for the seven-day publication every plan version requires; BURP and the regional sites the plans name; the Osservatorio's communication record and municipal notification attempts for recipient effect; PEC transmission to ARIF and the Prefettura; ARIF's authenticated election record or the owner's PEC for the response | One event at one time concerning one document, one sender and one recipient under one route; or one publication with its start, continuity and end | Not established. Follow the route selected by accepted A for the act and recipient; immediate effect is not notification. Keep publication, recipient effect, transmission, delivery and response distinct. [Notice and response](#notice-and-response) owns current public evidence and access limits. A publication end can supply its own clock anchor; publication alone does not establish silence, refusal, breach or liability. The monitoring response column supplies no election. |
| Who has the consequential relationship to the affected land | The determination's incorporated annex naming addressees by comune, foglio and particella; later acts that correct listed owners; the Osservatorio's matter and transmitted cadastral and owner data; a competent public-asset register for public land | One addressee position in one act version, or one stated ownership, occupation, management or other legally relevant relationship | The annex establishes the position the act published for each parcel, not that the named person held the land. An effective correction act replaces the listed position for the parcels it names; its effect against the corrected recipient follows the notice route above. Current standing beyond the latest act needs the operator's matter or a competent register; cadastral geometry and public-land catalogues are candidates until they do. The monitoring stream publishes `CUAA` and `AZIENDA` columns on 86 records and carries a sentinel in every one, so it supplies no holder identity; the observation row records that. The ordinary measure reader preserves published addressee positions and the source-stated scope of corrections, including explicit cross-page fields. Remaining continuation readings are identified in the removal row. A form's requirement for evidence of a declarant's capacity is retained as a condition where stated; a blank form establishes neither actual standing nor a completed response. The correcting acts' unpublished underlying correspondence and current standing are not supplied by public annex names. |
| Whether an affected plant has protected status | The regional monumental-tree register and the matter's exact plant evidence | One registered or provisional protected-plant occurrence | Match the affected plant and select the status in force at the event time. The observation row carries, uninterpreted, `MONUMENTALE_ARIF` on 586 records — a monitoring publisher's flag beside the observation, not a register entry, and no substitute for matching the plant in the register. |
| Whether protected status requires another permission for this removal | The exact PPTR/local rule and competent authority decision reached by that plant and intervention | One applicable protection rule or one issued decision | Investigate this only for an affected protected plant; the full Puglia landscape-proceeding catalogue is not the population. The observation row carries, uninterpreted, the landscape and hydrogeological flags the monitoring publisher prints beside the observation: `UCP_PPTR` on 7,078 records, `VINCOLO_IDROGEOLOGICO` on 1,462, `BP_PPTR` on 1,172, `PAI` on 215. A flag is a lead to the applicable rule, never the decision. |
| Who was assigned, what field work occurred, whether removal was completed and what lawful cost resulted | Osservatorio and executing-body casefile and field records: the presided execution record, countersignature and photograph, assignment, verification and cost determination; the lawful work basis stated by the removal orders (the removal-order row) | One assignment, assessment, treatment, removal, inspection, completion or cost event | Not established. [Performance](#performance) identifies usable reports, unresolved scope and acquisition limits. No presided per-target execution record is connected. Assignment and coercive directions do not prove completion; monitoring removal labels/dates are leads. Obtain the histories needed to close or leave open every admitted order, irrespective of its date. |
| Any vector or treatment observation required by an accepted calculation | Official Osservatorio, ARIF or incorporated scientific monitoring | One observation for a stated place, period, method and subject | Name the exact C consumer first, then acquire the corresponding observation population. Reach (`SPEC.md`, admission): observation-dated; complete over the period the naming consumer's clock reaches from the decision date. |
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

The removal consumer reaches a material publication annotation: CAMP_2024 cell
A119730 explains the 73 marked positive rows as not removed following the
DDS158/2024 area update. The existing `campaign.PublicationReading` annotation now
survives typed serialization into `monitoring.Member`, preserving its exact text and
source row/field citation. Bounded replay of the retained native footer verifies this
ordinary consumer path. Older grouped annotation rows retain an explicit derived
reading limitation; the shared population has not been rebuilt or relabelled under
the new reader version. The source/sheet-scoped relationship to marked rows remains
unestablished by an ordinary reader. Literal identifiers and group identities stay
unchanged. Supported same-day SIT counterparts and current legal disposition remain
separate questions; the annotation does not prove withdrawal or completion.

## Laboratory reports

The source population is owned by `corpus/sources/reports/records.json`: 1,910
captures and 1,180 distinct PDFs. PR #7 supplies the accepted reader; PR #18 owns
completion. All retained PDFs have page readings and relationship inventories,
but that accounting does not establish source fidelity or complete ordinary joins.
Missing positioned-identifier materializations can be rebuilt from retained blocks;
failed semantic readings require source repair. Original request provenance and
explicit extraction-version selection remain intact. SPEC owns reader and join rules.

Current verified consumer results are bounded to their stated populations:

| Population | Usable result and remaining qualification |
|---|---|
| DDS 63/2024's ten reports, version `6f51804f67a872d53720` | 92 administrative targets attach; one remains unresolved. CNR 54/56/59/60 reading and identity repairs are qualified. CNR 56 sample 1662433 prints malformed latitude `41.07448,833`; no coordinate workaround is accepted. This is not a global version switch. |
| Seven user-supplied recovered PDFs | All 387 sample rows were independently checked; all 240 referring observations attach, four retaining unavailable laboratory sampling dates. IAMB 7/8/4 result components lack covering letters needed for laboratory method/issuance evidence. The additional IAMB 8 observation 1222184 attaches through its source-verified protocol copy. UNIFG's differing8_POSITIVI/8_DUBB headings remain literal. |
| Other qualified bounded repairs | SELGE 17/2018 supplies 104 rows and 104 bidirectional links; SELGE 27/2015's dates and SELGE 139/2015's printed latitude are recovered. CNR 65/2024 and the reached62/68F/70F/75F annex readings are available subject to the gaps below. UNIBA 15/2024,66/2023 and 87/2023 support19 referring observations; repeated displays retain their qualifications and cannot count as independent tests. |
| IAMB 18b/2021 and 20/2021 | Five observations attach. IAMB 18b's cover says Crispiano and its result row says Locorotondo; administrative/cadastral publications locate the target at Locorotondo 32/69. The cover discrepancy and independent physical-location question remain unresolved. |
| CNR 58a | Detection, two negative samples and sample 1667390's undetermined subspecies remain separate despite the act's broader infected/ST1 recital. |
| CRSFA 1038/2022 and DDS 126/2022 | The administrative reading preserves ten targets and the report selection. PR #24's new report reading recovers literal host/sample-code components and corrected header/note scopes. Composed consumption still leaves all ten links unresolved: coordinate axes are unstated, an axis issue overreaches the host component, and the act/report host population needs its source-qualified relationship. The source-scoped population bridge is implemented, but no accepted claim is inferred from counts or a taxon synonym. |

Material reading and relationship dependencies remain in this row:

| Source or dependency | Outstanding meaning, acquisition or consumer work |
|---|---|
| CNR 23/24; CNR 32/41/46a/48/62 | Recover23/24 identities from held originals; resolve32's wrapped coordinates and separately published sampling dates,41's contextual identity/asymmetric decimal-precision comparison,46/46a's identity and host wording, and 48 sample 1659444's latitude disagreement.48/62 retain failed mark-note repairs and cannot supply complete-reading polarity. These are reading/relationship limits, not missing source bytes. |
| CNR 25; CNR 62 | CNR 25's three current-day observations match; its three prior-year publications remain unjoined. CNR 62's three negative rows have monitoring entries without report routes; two genus-positive/undetermined-subspecies rows have no reference found in the retained monitoring releases. Report results remain available without invented observations. |
| CNR 68F/2024 sample 1669924 | Report longitude 16.94561750 differs from act/monitoring16.94456175; no resolving correction is read. Official sample-location or corrected source evidence is required. |
| SELGE 102/2018 and 145/2019 | Retained whole-table-as-one-record proposals require the existing continuation/binding owner to recover actual records. An incomplete region or single-page output overflow remains a reading limit. |
| SELGE 196/2020 and 197/2020 | Only unrecovered published report routes. Owen reports backing-file FileNotFoundException; acquisition records prohibit automatic retries. Retained text search found no alternative; scanned-only identity coverage remains incomplete. No broad hunt is authorized. |
| SELGE 355/2020; IAMB 34/2022 and 4/2023 | Originals are needed for predecessor content and exact correction deltas. Their successors independently supply usable corrected results and methods; those results do not wait for predecessor recovery. No unrestricted predecessor search is assigned. |
| CNR 36 Modifica1, reached through DDS 43/2024 | Corrected report is embedded in retained act renditions; actual monitoring routes still supply the older standalone report. The report owner lacks scoped embedded-report consumption. The separate typing note covers one of two targets; the broader act recital cannot expand it. |
| CRSFA 1691/2022, parent of 1692 | No actual route recovered from retained metadata or reached publisher/monitoring discovery. A source-derived filename returned FileNotFoundException. Parent population/qualifications remain unexamined; this does not establish nonpublication. |
| CNR communication0552255/2025, reached through DDS 173/201 | Not recovered from held originals, reached regional/CNR searches or linked attachments. Acquire from the Osservatorio incoming protocol and associated CNR correspondence. The acts' attributed outbreakST53 statement remains usable; direct typing method, tested-sample population and note lineage are unestablished. Subspecies assays cannot supply them. |
| Later typing and official confirmation | CNR 174P/2024 reports MLST in progress for 1752612; a later result is unexamined. Designation, status, custody and Service confirmation still require their own evidence. ARIF's application requires regional login; authenticated records have not been accessed. |

Report replacement never closes an administrative order. DDS 74's old1673519 and
DDS 138's corrected1674070 retain their different report relationships; the surviving
administrative disposition is owned by the removal row below. A matched occurrence
is not official confirmation, current standing or completed removal.

## Removal measures: required population and present coverage

The `removal-orders` binding and acquisition records own source admission and routes.
Reach follows the accepted finding-to-removal decision and consequential corrections,
supplements and historical live orders. Reader contracts belong to SPEC and code;
source instances below locate unfinished work, not supported-case rules.

The ordinary reader preserves prescribed directions, target/addressee occurrences,
shared and continued fields, corrections and source-reported events. Native associations
and laboratory identity stay with their owners. Finding links use those associations
or source-supported report selections, with unique forward/reverse correspondence.
One retained issue incorrectly calls missing association metadata `source-not-stated`;
that is a reading limit, not source silence.
DDS 63 and 116 have qualified administrative readings;116 supplies ten finding links.
DDS 126's ten administrative positions and commencement term are qualified, while its
finding links retain row 2's limits. These results do not establish population coverage.

The fixed reconciliation snapshot reaches 76 cited act identities through 81 retained
renditions; the initial 34-act queue is not the required population. All 365 report
renditions reached by that snapshot are readable at `c3bbaa68538bcf398de6`. Of 353
previously unresolved routed observations, 205 Cagnano observations have source parcels
inside DDS 173/201 surrounding-work scopes. Exact plant/partial-parcel membership and
field execution remain unresolved. Three Bari observations reach DDS 114/2026 and two
Noicattaro observations reach DDS 107/2024. Eighty still lack an identified competent
prescription: 33 Crispiano, 45 Bari and two Mola. These are unresolved relationships,
not counts of missing orders. Own-act municipal searches do not exhaust external
regional orders; notice-route limits are below.

All 73 positive observations without a published report route are starred CAMP_2024
rows with same-day unstarred SIT counterparts. The publisher's footer A119730 states
non-removal following DDS 158/2024's area update. The annotation now survives ordinary
serialization, but its marked-row relationship remains unestablished; 71 rows lack a
cadastral sheet. Rows 3–5 own area, position and parcel sufficiency. No star-stripping,
identity alias or withdrawal is inferred.

| Remaining requirement | Current limitation and next source/consumer work |
|---|---|
| Complete ordinary source readings | Complete independent original readings exist for the DDS 147–165/2024 correction,173/2025–63/2026 supplement,129/2021–6/2022 chain,188/2024,201/2025,51/2023,35/2026,108/2024,135/2024,6/2026,20/2023,149/2024, the reached late 2024 families and eight further regional 2026 originals. Their ordinary readings/consumer qualification remain incomplete. Source coverage follows the binding and every consequential dependency, not this illustrative list. |
| Recover readable target positions | Whole-act dispatch remains incomplete: DDS 188 and 173's latest parallel attempts encountered repeated connection failures and ended without readings. The source bytes remain readable. Existing native-word selection now reaches printed positions combined by table detection. DDS 6/2026's opaque cell text has an exact-cell visual recovery path. Both repairs preserve original geometry/causes and still require ordinary source qualification. |
| Cross-municipality prescribed work | DDS 6/2026,135/2024 and 149/2024 include parcels outside their named municipal transmission. Target scope is readable; actual posting and recipient service for those parcels remain unestablished. |
| Locality conflict | DDS 52/2024's CNR 51 recital says Triggiano; its annex and source-linked monitoring/cadastre say Capurso 12/646 for 1661170. Capurso's publication is established. The source disagreement and independent physical qualification remain open; DDS 188 is not an express correction. |
| Administrative disposition | DDS 188 retains both DDS 74's 1673519 and DDS 138's 1674070 reference cohorts. The former's Triggiano 20/241 disposition is unresolved; shared surrounding work cannot be erased by one corrected lab reference. Reached corrections do not supply withdrawal or execution. |
| DDS 48/2023 predecessor | Not recovered through held-source reconciliation, exact BURP search or reached Castellana routes. Municipal Halley access timed out/reset, leaving historical query/attachments unexamined. Accepted DDS 51/2023 correction ambiguity remains. |
| General prescription-term consumption | PR #23 proposes source-bound commencement quantities and coercive-clause applicability, replacing per-act registration as a gate. Actual DDS 58 and 126 terms reach the proposed quantity/Evidence consumers; six applicability conditions remain unknown. Reviewed dependent binding defects are repaired in the candidate. Differing work populations, corrections and supplements still need ordinary checks and implementation review. Changed A/B/C content remains unaccepted; no universal ten-day rule or notice history is inferred. |
| Legacy discovery leads | All 28 previously missing 2023–2026 legacy originals were acquired and fall outside the removal chain. 165 older metadata claims remain leads; limited native-text search established no consequential dependency, but did not exhaust scanned pages or exclude later supported relationships. |

DDS 201's complete independent reading identifies 106 infected targets and 64 surrounding
parcel occurrences across 56 distinct parcels; ordinary consumption is pending. Its
field-identification and performance-verbale dependencies remain live. DDS 173's municipal
and BURP renditions were independently compared throughout and have the same consequential
content; their distinct publication occurrences remain separate.

## Notice and response

Use the route and consequence owned by accepted A; source dates cannot substitute
for another event's anchor. Publication declarations, interval certificates, personal
service, PEC delivery and owner response remain separate. No authenticated service,
election or case-response history has been accessed.

| Source population | Usable evidence and remaining work |
|---|---|
| Capurso native register | Six regional-act publication declarations are consumed; five have been checked through C's election boundary with the national-calendar baseline. Local holidays, recipient effect and actual response remain separate. These declarations are not interval certificates. |
| Regional Albo | Nine reached removal/supplement detail entries state publication concluded. Ordinary events preserve adoption identity separately from proposal, registration and executivity. They are regional, not municipal, publication. |
| Cagnano native archive | Four reached measure publications concern DDS 173/201/63. Ordinary declarations retain dates and attachment routes; exact act attachment/clock selection awaits qualified readings. Two DDS 201 entries, one labelled ERRATA CORRIGE, serve identical bytes with different protocols; that supplies no amendment delta. The October 2025–March 2026 Xylella query returned the three held173/201 entries; the separate managerial archive remains unexhausted. |
| Bari native legacy archive | Fourteen historical details and eleven removal-related certificates are retained. The declaration consumer preserves all 14 dates/statuses and 28 attachment routes. All 11 certificates were independently read completely and positively attest completed intervals. Ordinary certificate consumption and qualified act attachment remain pending; three unnamed-DDS certificates have exact principal links to135/2025,153/2025 and 114/2026. Their principal identity pages, not full contents, were inspected. Three geography-only certificates were outside this pass. |
| Triggiano/Noicattaro | Triggiano historical search did not return known 2024 controls; its coverage is unexplained. A 2031 archive end is not a posting end, and its reached DDS 11/2026 is not the 2025 correction. Publication of the 2025 corrections remains unestablished. Noicattaro's reached historical query supplied no admitted order. |
| Crispiano/Mola | Controlled browser searches reached municipal managerial/political archives; Crispiano Xylella results were empty and three Mola originals concern vector control. External regional-order coverage remains unestablished. Initial direct POST empties failed controls and are not absence evidence; the Parsec manual route failed DNS. |
| Locorotondo | Reached historical searches returned unrelated acts, not DDS 135/2021 posting. The current portal is accessible; the linked legacy archive failed DNS. Publication, effect and response remain unestablished. |
| Other public routes | Bari's newer historical application fails on a server token, but its legacy archive works. Modugno register/notice routes and ARIF register/notice/current-transparency routes returned 403, including browser checks. ARIF's pre-2021 index loads but its managerial category reports no content and its linked legacy service returns403. Bisceglie's historical form leaves Results disabled and failed control queries, so no zero-result claim follows. Minervino's DDS 65/2025 attachment was visually inspected through the web service, but direct capture/browser reset; municipal bytes and interval remain unrecovered. These are reached-route limitations, not permanent access prohibitions or complete institutional searches. |

## Performance

No presided per-target execution record has been connected. The monitoring stream's
removal labels,806 printed removal dates and 803 decree references remain leads;
its970 `DOCUMENTO_DECRETO` values supply no actual route. DDS 11–14/2026 supply
institutional assignment context for marginal/abandoned almonds, not completed work.

| Source evidence | Current consumer meaning and material limit |
|---|---|
| Prefettura, Bisceglie, 10 July 2025 | Qualified ordinary reported eradication after the 10 June finding and before the meeting. No exact day, individual executed targets or completion of the later August measure follows. The municipal24 June statement concerns plans; neither page links execution minutes. |
| Two Council releases, Cagnano, 5 March 2026 | Qualified ordinary reports of 331 removals, including177 monumental olives in one account. They overlap; totals cannot be added. Individual targets, actual execution dates and executor are not established. |
| Actual Commission hearing | Complete unrevised publisher transcript and HLS fragments are retained. Independent reading supports initial 153 prescribed plants, disputed 174/177 monumentals and broader nearly 2500 cut down, with separate scopes. The ordinary response returned but one of 40 quotations fails exact source validation; the response also omits the linked index's unrevised-status qualification. Consumer repair is pending. No independent listening occurred; frames do not verify speech. No minutes or substantive documents are published on the reached hearing page; the mentioned written chronology was not recovered from actual links/bounded official search. |
| Monopoli service certificates/ledgers | Direct reading establishes chiefly brush clearing and five pear fellings at aratico 3; the felling specification excludes stump removal/disposal. No source links this work to an admitted infected population, removal prescription or required treatment. These records do not supply removal completion or admit a procurement workflow. |
| DDS 63/2026 / ARIF note 38047 of 17 March 2026 | Act reports impeded work because an omitted proprietor had not consented. This is not completed removal or adjudicated refusal. The note was absent from reached attachments and not recovered by actual exact publisher searches; acquire the underlying case correspondence and subsequent history. |

Public-route limits are in the notice row. ARIF's public procedure page supplies no
events; the older Xylella portal TLS failure remains unresolved. Controlled assignment,
service, performance and cost records have not been accessed. Failed public searches
cannot establish that an event did not occur.

## Materials that are not standalone input gaps

Discovery catalogues, URL censuses, general municipal archives, backup and repository
preservation are not decision inputs. Historical records, public-land sources and
protection proceedings enter only through an accepted consequential input. Difficult
tables, copy relationships and adoption lineage are work within their owning rows,
not additional source families or reasons to widen CURRENT's aperture.

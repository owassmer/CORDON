# Stage D input map

This is the front door to Stage D. Each row names a fact accepted A–C requires, the
source that supplies it, what one of that source's records means, and what D must
establish. The monitoring-observation family and the bounded national calendar are
established; no other row is.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Established. `cordon_d.monitoring.observations` streams every retained release; `distinct_observations` relates the publications of one observation; `detection_days`, `occasion_sets` and `located_positives` hand C its candidates. Meaning and limits below. |
| What the laboratory actually reported | The official report linked from the monitoring record | One laboratory report containing one or more sample results | Follow every referenced report; join its rows to observations; preserve report corrections and distinct copies. The observation row carries, uninterpreted, the report identity and performing laboratory the monitoring publisher prints beside the observation: `PROTOCOLLO` on 22,245 records, `STRUTTURA_LABORATORIO` on 14,490, `PROT_SELGE` on 8,762, `DATA_PROT_SELGE` on 8,760, `LABORATORIO` on 82. They are a publisher's transcription and establish nothing here; the report establishes what the report says. |
| Which legally adopted area contained the location on the event date | SIT demarcated-area geometry and the adopting regional act | One published area feature in one legal version | Acquire every version reached by A; bind geometry to its adopting act; use the version in force at the event time. The observation row carries, uninterpreted, `ZONA` on 219,120 records and `ZONA_DELIMITATA` on 8,762 — the zone status and area name the monitoring publisher prints beside the observation (`Zona Contenimento - Salento`, `Area delimitata Monopoli`), which are not the adopted geometry in force and do not stand in for it. Its `BUFFER` column is published with no value in any record. |
| Which plants or surfaces fall inside C's distance and survey calculations | Monitoring observations, PuntiStampa, land-use or host-bearing surfaces, parcels and other population records required by the calculation | An observation, published point or polygon, parcel, grid cell or host-bearing surface according to its own source | Establish the actual population represented by each source and never substitute positives for all plants |
| Which cadastral parcel contains or intersects a relevant location | Agenzia delle Entrate and SIT cadastral geometry | One parcel geometry with its cadastral reference | Acquire the reached parcel population and preserve the source identifier; do not infer ownership from geometry. The observation row carries, uninterpreted, the cadastral references the monitoring publisher prints beside the observation: `FOGLIO`, `PARTICELLA` and `COD_COMUNE` on 8,762 records each, `ID_PART` on 8,761, `SEZIONE` on 193. `COD_COMUNE` is the cadastral municipality code (`G187`, `B809`); `COMUNE_COD` is the ISTAT code and is the observation's own administrative location, not a cadastral reference. A parcel string on an observation is not a parcel, and ownership is never inferred from it. |
| Whether the Osservatorio issued a removal measure and which plants or parcels it covered | Regional removal determination and its incorporated annexes | One adopted act plus its source-defined subject rows | Read identity, operative clause, branch, annex incorporation and correction relationships through one general reader |
| Whether a legally consequential notice, delivery, publication, receipt or response happened | The determination's own text for its declared route; the competent municipality's albo pretorio record for the seven-day publication every plan version requires; BURP and the regional sites the plans name; the Osservatorio's communication record and municipal notification attempts for recipient effect; PEC transmission to ARIF and the Prefettura; ARIF's authenticated election record or the owner's PEC for the response | One event at one time concerning one document, one sender and one recipient under one route; or one publication with its start, continuity and end | Select the source by the route A selects for the act and recipient: completed personal communication, including the code-of-civil-procedure forms for unreachable recipients; mass publicity only where the act establishes that recipient number made personal communication impossible or particularly burdensome; a reasoned immediate-effect clause in a non-sanctioning measure; or cautionary-and-urgent character. An immediate-effect or cautionary clause makes the measure operative; it is not notification, and a clock anchored on notice or publication runs only from that event. A publication record proves the publication duty, and its end date anchors the election window; publication alone establishes neither recipient effect nor silence, refusal, breach or cost liability. Sending, delivery, publication, recipient effectiveness and response stay distinct. The monitoring stream publishes a `SCELTA_PROPRIETARIO` column on 8,762 records and carries no value in any of them, so it supplies no owner election; the observation row records that. |
| Who has the consequential relationship to the affected land | The determination's incorporated annex naming addressees by comune, foglio and particella; later acts that correct listed owners; the Osservatorio's matter and transmitted cadastral and owner data; a competent public-asset register for public land | One addressee position in one act version, or one stated ownership, occupation, management or other legally relevant relationship | The annex establishes the position the act published for each parcel, not that the named person held the land. An effective correction act replaces the listed position for the parcels it names; its effect against the corrected recipient follows the notice route above. Current standing beyond the latest act needs the operator's matter or a competent register; cadastral geometry and public-land catalogues are candidates until they do. The monitoring stream publishes `CUAA` and `AZIENDA` columns on 86 records and carries a sentinel in every one, so it supplies no holder identity; the observation row records that. |
| Whether an affected plant has protected status | The regional monumental-tree register and the matter's exact plant evidence | One registered or provisional protected-plant occurrence | Match the affected plant and select the status in force at the event time. The observation row carries, uninterpreted, `MONUMENTALE_ARIF` on 586 records — a monitoring publisher's flag beside the observation, not a register entry, and no substitute for matching the plant in the register. |
| Whether protected status requires another permission for this removal | The exact PPTR/local rule and competent authority decision reached by that plant and intervention | One applicable protection rule or one issued decision | Investigate this only for an affected protected plant; the full Puglia landscape-proceeding catalogue is not the population. The observation row carries, uninterpreted, the landscape and hydrogeological flags the monitoring publisher prints beside the observation: `UCP_PPTR` on 7,078 records, `VINCOLO_IDROGEOLOGICO` on 1,462, `BP_PPTR` on 1,172, `PAI` on 215. A flag is a lead to the applicable rule, never the decision. |
| Who was assigned, what field work occurred, whether removal was completed and what lawful cost resulted | Osservatorio and executing-body casefile and field records: the presided execution record, countersignature and photograph, assignment, verification and cost determination; the lawful work basis stated by the removal orders (the removal-order row) | One assignment, assessment, treatment, removal, inspection, completion or cost event | Read the actual first-party records for the matter; public procedure manuals cannot fill absent events. A coercive-direction or execution-priority act is not proof of completed removal. A published removal label or removed-plant layer (the observation row) is a lead to a first-party record, not a removal occurrence; the retained SIT capture holds no removed-plant layer after 2017. The observation row carries, uninterpreted, `DATA_ESTIRPAZIONE` on 806 records and `RIF_DECRETO` on 803 — the removal date and decree reference the monitoring publisher prints beside the observation. Like the removal label beside them, they are a lead to a first-party record, never a removal occurrence. It also records that the monitoring stream publishes a `DOCUMENTO_DECRETO` column in 970 records of the 2014-15 and 2016-17 removed-plant layers and carries no value in any of them, so that column supplies no route to a decree. |
| Any vector or treatment observation required by an accepted calculation | Official Osservatorio, ARIF or incorporated scientific monitoring | One observation for a stated place, period, method and subject | Name the exact C consumer first, then acquire the corresponding observation population |
| Which days count for a working-day clock | Italian holiday law and enacted one-off changes | One national calendar rule | Maintain only the years reached by accepted B clocks |

## Monitoring observations

The source is every observation the Regione publishes: twelve campaign workbooks, the
CKAN CSV, and the 101 observation point layers of the eight SIT services that carry
them. Those eight are the only services in the publisher's inventory whose layers are
observation points; `MonitoraggioXFPasp` publishes nursery sites and Leccino plantings,
and the grid, buffer and cadastral polygons belong to the area, population and parcel
rows. Bytes live in the content-addressed store (`SPEC.md`), the acquisition records
under `corpus/sources/monitoring/` name every release and page by hash, and
`scripts/acquire_monitoring.py` recaptures into the store, where changed bytes take a
new name.

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
| `RISULTATO` | The publisher's label: Positivo, Negativo, Dubbio, In attesa, Positivo duplicato, Da ricampionare, Ispezione visiva, Sintomatico, Positivo estirpato. A blank is unpublished. A duplicate label restates the positive it accompanies and is not a positive by itself. The label is the observation-result part of `official-finding` and `survey-performance`; the finding is the laboratory report's. |
| `SPECIE`, `CULTIVAR`, `SUBSPECIE` | Recorded host, cultivar and sample-level subspecies. A view's subspecies title is context and is never substituted for an absent sample-level identification. Every host and every result state is retained. |
| `SINTOMO`, `SINTOMI` | Recorded visible drying symptoms. `Presente` and `Assente` become presence and absence; the unexplained code `0` stays unknown. The publisher states that drying symptoms are not a diagnosis. |
| Native geometry and spatial reference, `LONGITUDINE`, `LATITUDINE` | The published location, read into one frame. The SIT services state EPSG:32633 on every page. The campaign releases publish degrees and state no datum anywhere — not in the CKAN package, the download page, a sheet, a header or a legend — and those degrees are EPSG:4326, established from the publisher's own redundancy: over the 1,279,135 observations published both ways the stated SIT point reproduces the printed pair to under a centimetre, while ED50 and Monte Mario / Roma 40 miss by 127 m and 71 m. `scripts/check_frames.py` re-derives that from the store and fails when the recorded frame stops fitting. Because every location has a frame, the publications of one observation are compared in one frame rather than held apart by the frame they were printed in. No source states positional error, so metric use waits for the population row's qualification. |
| `COMUNE`, `COMUNE_COD`, `PROVINCIA`, `LOCALITA`, `ALTITUDINE` | The observation's own administrative location. `COMUNE_COD` is the ISTAT municipality code; the cadastral code is `COD_COMUNE`, which belongs to the parcel row. `LOCALITA` and `ALTITUDINE` are read and carry no value in any record of this capture. |
| `SQUADRA`, `TECNICO`, `COD_TECNICI`, the inspector-name columns, `NOME_DISPOSITIVO`, `CODICE_CAMPIONAMENTO`, `STATO`, `NOTE_RILEVATORE`, `CRITICITA_NOTE` | Who performed the observation, with what instrument, in which campaign, and what they noted. One fact under several publisher names: the 2016 infrastructure survey prints a team code and per-inspector columns where later releases print `TECNICO`. `CODICE_CAMPIONAMENTO` names a campaign shared by hundreds of records and is never an identity. A note, a device name and a publication status describe the publication rather than the observation, so they are read and not compared. |
| `DOCUMENTO_CONFERMA`, `LNK_DOCUMENTO_SELGE` | The literal route to the laboratory report, under the column that published it: 22,206 and 8,762 routes. The document itself is unread here. |
| Protocol, laboratory, cadastral, demarcated-area, protected-plant and removal fields, including `DOCUMENTO_DECRETO` | Carried as the literal the monitoring publisher printed, for the row that owns each fact, interpreted by nobody here. A transcription beside an observation does not fill a report, a parcel, a permission or a removal. |

What the stream hands A–C, all as candidates:

- Positive observations with their day, their agreed location and their report route
  (`detection_days`, `located_positives`) for the no-detection anchor and the finding
  location. The report decides the finding. `detection_record_complete` is never set
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
  pending, doubtful, duplicate-only, blank, and the result disagreements below. Of the
  positives, 29,662 hand a consumer one agreed location; 337 hand none because their
  publications place them apart, and 104 because no publication carries a place.

What the population shows, read and not reconciled:

- In 2013–2017 cross-release identity is unreliable. The workbooks carry no reference and
  the SIT views use daily counters, so a reused value stays uncorrelated while a value
  used once in each of two views on one day still correlates them. Where those
  publications agree they merge and cannot be told from coincidence.
- 16,630 observations have publications that disagree on a field: species 16,523,
  `COMUNE` 8,203, coordinates 2,367, result 232, symptoms 2. Each is exposed and no
  publication is preferred. Only a result disagreement withholds an observation from the
  positive and negative counts. Most of the species and municipality disagreements are
  the publisher's own conventions — `OLIVO` beside `Olivo (Olea europaea)`, and 93 of 235
  municipalities printed in more than one casing — and are not identity doubt.
- 21 observations have publications in two frames that place them apart, and 17 of them
  are the publisher placing one observation on another continent: sixteen rows of
  `CAMP_2017_2018` on 22 February 2018 carry their axes transposed, and one row of
  `CAMP_2024` carries a corrupt pair. All 17 are published negative. Both printed numbers
  are valid for the column they sit in, so only the publisher's other publication of the
  same observation exposes them. The remaining four are positives of 9 December 2019
  whose SIT views differ by about 11 m.
- Every value a reading does not carry names why, in the record's own terms: 85 distinct
  field-and-cause pairs across 62 fields, distinguishing a field the record does not
  publish, one published carrying no value, one carrying only a sentinel, one carrying a
  value this reader does not interpret, and one published that no row of this stage
  claims — 18,728 entries over 16 field names. No published field is passed over in
  silence. `DistinctObservation.uncorrelated_because` answers why a group could not
  correlate; these answer, for one publication and one field, why this reader carries
  nothing.

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

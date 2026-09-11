# Stage D input map

This is the front door to Stage D. It starts with facts required by accepted A–C,
then identifies the source that can supply them. After the 10 September purge,
the bounded national calendar remained retained. The monitoring-observation
family is established (first row, details below); prior acquisitions and case
demonstrations confer no completion on the other rows.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Established. `cordon_d.monitoring.observations` streams every retained release; `distinct_observations` relates the publications of one observation; `detection_days`, `occasion_sets` and `located_positives` hand C its candidates. Meaning and limits below. |
| What the laboratory actually reported | The official report linked from the monitoring record | One laboratory report containing one or more sample results | Follow every referenced report; join its rows to observations; preserve report corrections and distinct copies |
| Which legally adopted area contained the location on the event date | The adopting regional act and its cadastral annex; SIT demarcated-area geometry | One area statement the act makes: a zone, a place, and how far the zone reaches into it | Established for what the acts state. `cordon_d.areas.versions` gives each of A's 29 area versions the statement its own act makes; `zone_of` and `membership_evidence` answer which zone contained a place on a day. Meaning and limits below. |
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

## Demarcated areas

The source population is the 28 regional acts that accepted Stage A reaches
through its 29 area versions, from DDS 69/2021 to DDS 112/2026. A owns each
version's identity, interval, subspecies and act-level state; this row adds
the area statement the act itself makes. Of the 28, one adopts no geography —
DDS 45/2025 states the procedure, that the act creates the area and
InnovaPuglia transmits shapefiles afterwards — and DDS 148/2024's own body is
not held, so it reads nothing and says so rather than borrowing a successor's
annex. The other 26 acts are held as their published documents in the
content-addressed store (`corpus/sources/areas/acts.json` names each by hash
and origin); 25 of them annex a cadastral statement and 2 state their
geography as a rule in the dispositivo alone.

**What an act states, and how far it reaches.** The annex tabulates, per zone,
the province or metropolitan city, the comune, and how far the zone reaches
into it: the whole province, the whole comune, part of the comune, or named
`fogli di mappa`, with the act's own asterisk where a sheet lies wholly inside
rather than merely intersecting. Across the population that is **373
statements over 4,316 stated sheets**, of which 1,561 carry the asterisk.

**What the reader answers, and at which grain.** `zone_of` and
`membership_evidence` take a day and a place and return the zone of each act
version in force that decides it, with the annex row that decided it. The two
questions are not the same question and are not answered alike: whether a
*sheet* is reached by the zone, and whether a *point or parcel* lies inside
it — which is what Stage A's predicate asks. A sheet the act marks wholly
contained decides both. A sheet without the asterisk is reached by the zone
while a particular parcel in it stays undecided, because the act does not say
which part is inside. Named particelle decide only themselves. A question that
identifies no comune or province is refused rather than answered.

**What it does not supply.** No positional error bound: no source for these
areas publishes one, so the metric consumers (`pest_free_hectare`,
`inward_band`, `pni_geography_facts`) stay unfed and the distance work waits
on a qualified frame. The publisher's zone polygons are not acquired here,
because nothing consumes them: DDS 45/2025 puts the shapefile transmission
after the act, so a capture inside a version's interval can still show the
previous geometry, and neither a second capture nor a matching sheet summary
distinguishes a stale polygon from the adopted one. That correspondence needs
evidence naming the version, so the polygons enter when a consumer exists — a
qualified metric frame, or a cross-check on the annex reading — and not
before. The operative
legal-area state is A's `PUG-LR4-2017:Art.3(2)` gate and Annex III eligibility
is A's EU annex; neither is decided here.

**Reading is all-or-nothing per cell.** A cell counts as read only when every
consequential token in it is accounted for. Where something is left over the
cell is reported unread and no statement is emitted from it, because a
statement narrower than the act's answers "not in this zone" for territory the
act includes. Four cells in the population are unread on that rule and are
listed by their version. The forms the acts do use are read: inclusive ranges
written both `da 15 a 32` and `161 a 172`, sections, particelle narrowing a
sheet, a sviluppo attached to one, and the whole- and part-of-territory
statements. No act in the population states an exclusion; none is assumed for
one.

**Zone and regime are two facts.** The acts print `ZONA INFETTA IN CUI SI
APPLICANO MISURE DI CONTENIMENTO` and `ZONA CUSCINETTO IN CUI SI APPLICANO
MISURE DI ERADICAZIONE`. The zone is what the caption names in head position;
the measures it says apply there travel beside it rather than replacing it.

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

# Stage D input map

This is the front door to Stage D. It starts with facts required by accepted A–C,
then identifies the source that can supply them. After the 10 September purge,
the bounded national calendar remained retained. Monitoring observations are now
being integrated as the first source family; prior acquisitions and case
demonstrations confer no completion on the other rows.

| A–C needs to know | Real source | What one record means | What D must establish |
|---|---|---|---|
| What was observed, where and when, including positive, negative and other results | Regional campaign workbooks, CKAN CSV and SIT monitoring point layers | One published observation, sample, visual inspection or assessment | Integration in progress: twelve workbooks reacquired and read; complete SIT and CKAN capture and cross-release comparison running. Ordinary reader: `cordon_d.monitoring.observations`. Details below. |
| What the laboratory actually reported | The official report linked from the monitoring record | One laboratory report containing one or more sample results | Follow every referenced report; join its rows to observations; preserve report corrections and distinct copies |
| Which legally adopted area contained the location on the event date | SIT demarcated-area geometry and the adopting regional act | One published area feature in one legal version | Acquire every version reached by A; bind geometry to its adopting act; use the version in force at the event time |
| Which plants or surfaces fall inside C's distance and survey calculations | Monitoring observations, PuntiStampa, land-use or host-bearing surfaces, parcels and other population records required by the calculation | An observation, published point or polygon, parcel, grid cell or host-bearing surface according to its own source | Establish the actual population represented by each source and never substitute positives for all plants |
| Which cadastral parcel contains or intersects a relevant location | Agenzia delle Entrate and SIT cadastral geometry | One parcel geometry with its cadastral reference | Acquire the reached parcel population and preserve the source identifier; do not infer ownership from geometry |
| Whether the Osservatorio issued a removal measure and which plants or parcels it covered | Regional removal determination and its incorporated annexes | One adopted act plus its source-defined subject rows | Read identity, operative clause, branch, annex incorporation and correction relationships through one general reader |
| Whether a legally consequential notice, delivery, publication, receipt or response happened | The Osservatorio's protocol and PEC records; a municipal register only where the governing measure uses it | One event concerning one document, sender, recipient and time | Use the operator's own record when it holds the event; distinguish sending, delivery, publication and response |
| Who has the consequential relationship to the affected land | Owner/cadastral data in the Osservatorio matter or a competent public-asset record | One stated ownership, occupation, management or other legally relevant relationship | Establish current standing for the affected subject; public-land catalogues and parcel maps are only candidates until they do |
| Whether an affected plant has protected status | The regional monumental-tree register and the matter's exact plant evidence | One registered or provisional protected-plant occurrence | Match the affected plant and select the status in force at the event time |
| Whether protected status requires another permission for this removal | The exact PPTR/local rule and competent authority decision reached by that plant and intervention | One applicable protection rule or one issued decision | Investigate this only for an affected protected plant; the full Puglia landscape-proceeding catalogue is not the population |
| Who was assigned, what field work occurred, whether removal was completed and what lawful cost resulted | Osservatorio and executing-body casefile and field records | One assignment, assessment, treatment, removal, inspection, completion or cost event | Read the actual first-party records for the matter; public procedure manuals cannot fill absent events |
| Any vector or treatment observation required by an accepted calculation | Official Osservatorio, ARIF or incorporated scientific monitoring | One observation for a stated place, period, method and subject | Name the exact C consumer first, then acquire the corresponding observation population |
| Which days count for a working-day clock | Italian holiday law and enacted one-off changes | One national calendar rule | Maintain only the years reached by accepted B clocks |

## Monitoring observations

The direct source population lives in `corpus/sources/monitoring/`: campaign
files together under `campaign/`, and SIT records under their publisher service
and layer. Acquisition records identify those releases; there are no case
registrations or authored answers. `cordon_d.monitoring.observations(root)` reads
the population through one ordinary entry point and retains every original field.

| Published fields | Usable input and meaning |
|---|---|
| `ID`, `ID_CAMPIONE`; earlier `NUMERO_ORDINE`, `OBJECTID`, daily and device identifiers | Preserve each identifier's role. Recent observation/sample references plus the observation date identify candidates for cross-release comparison. Earlier administrative and view identifiers do not automatically identify the same physical plant. |
| `DATA_RILEVAMENTO`, `DATA_CAMPIONE`, `DATA_PRELIVEO`, `DATA_RILIEVO` | The recorded observation or sampling day. Excel midnight is date storage; ArcGIS UTC epoch values are converted to the Puglia calendar day. The early campaign's 23:00 UTC values belong to the following local day. Campaign names are not date boundaries. Report, protocol and removal dates remain separate fields. |
| `TIPOLOGIA`; explicitly named visual-inspection and assessment views | Distinguish samples, visual inspections and assessments. An observation without an analytical result is not a negative test. |
| `RISULTATO` | The publisher's result, including positive, negative, doubtful, pending and other labels. This supplies the observation-result part of `official-finding` and `survey-performance`; the linked report supplies assay details in the next family. |
| `SPECIE`, `CULTIVAR`, `SUBSPECIE` | Recorded host, cultivar and explicit sample-level subspecies. The view's subspecies title remains context; it is not substituted for an absent sample-level identification. All hosts and result states are retained. |
| `SINTOMO`, `SINTOMI` | Recorded visible drying symptoms. `Presente` and `Assente` become presence/absence; unexplained codes remain unknown. The publisher expressly says drying symptoms are not a diagnosis. |
| Native geometry/CRS, latitude/longitude, municipality and cadastral fields | Published location for the finding and population inputs. SIT supplies native projected coordinates. Latitude/longitude column names establish axes but do not themselves specify datum or positional error; metric use belongs to the spatial input rows. |
| `DOCUMENTO_CONFERMA`, `LNK_DOCUMENTO_SELGE`, `DOCUMENTO_DECRETO`; protocol and laboratory fields | Literal routes and identifiers for the report or act owning the next fact. The observation reader exposes them without inserting an interpretation of the unprocessed document. |
| Team, field notes, inspection details, removal labels and protection/parcel annotations | Retained on their own observation. These can lead the respective input owner to useful source facts; a published annotation does not fill every field of a removal, permission or completion event. |

The public download page publishes twelve campaign files through 2025. Its own
explanation says surveillance follows the containment effort and is not an
inventory of all infected plants. CKAN publishes `CAMP_2020_2022.csv`; its second
resource, named `CAMP_2020_2023.csv`, has no URL. The datastore is another access
route to the first resource. SIT adds current and previous campaign views,
visual inspections, assessments, infected-point publications and observation
records carrying removal labels. Grids, buffers, cadastral polygons and planting
inventories belong to the population/spatial rows, not this observation stream.

Remaining work for this unit: finish the full published point populations and
CKAN release, read cross-release correspondences and disagreements, and exercise
the resulting complete stream. The absence of persistent plant identity or an
unpublished field is a source limit; neither is filled by invented values.

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

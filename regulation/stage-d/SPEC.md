# Stage D — real inputs for accepted A–C

Stage D connects the accepted legal and computational system to facts the
Osservatorio can actually obtain and use. For every required input it establishes
the source population, record meaning and grain, identity and time relationship,
ordinary reader, and exact unresolved limitation.

The current plain-language input map is `INPUTS.md`. `contracts.json` owns the 27
input kinds. `predicate-contracts.json` and `additional-input-contracts.json` bind
accepted A–C requirements to those kinds. `source-bindings.json` owns the small set
of source routes. `inventory.py` computes the A–C consumer projection when it is needed; nothing stores it.

## Admission rule

A source enters D only because an accepted A–C consumer needs a fact it can
supply. Once admitted, its relevant population must be acquired and understood;
the publisher's unrelated catalogue does not enter with it. Positive results do
not define a plant population: negative observations, unobserved specified plants,
parcels, surfaces and protected uninfected plants can all be consequential.

The Osservatorio's own casefile, protocol, notice, response, assignment and field
records are first-party inputs. Public manuals describing those systems do not
supply the underlying facts and are not part of the D baseline.

Regional removal determinations are called `removal-orders` in the source map.
Some accepted source text calls their operative direction a `prescription`; that
is the meaning of the `case-prescription` input contract. It is not a medical
prescription or a separate product workflow.

## Where bytes live

Source bytes are the only irreplaceable data. They live in a content-addressed
store outside the repository — `$CORDON_STORE`, or `<repository>-store` beside
the main checkout, which every worktree resolves to the same path — as blobs
named by their SHA-256, written once and never rewritten (`cordon_d.store`).
Acquisition records in the tree name each release by URL, capture time and hash;
the tree holds no source bytes. `scripts/audit_store.py` re-hashes every blob.
Where a reader establishes a fact from a publisher's own redundancy rather than
from a statement the publisher makes, the check that re-derives it is run by the
acquisition that could invalidate it, not left to be remembered: for the
coordinate frame of the monitoring degree columns that check is
`scripts/check_frames.py`, and `scripts/acquire_monitoring.py --campaign` derives
the readings and runs it. Neither runs in CI, which has no store.

Beside the blobs, `derived/` holds regenerable readings. Monitoring occurrences
and typed readings remain Parquet keyed by source hash and reader version.
Reports use compact JSON blocks and an assembled reading under source hash and
extraction version. Exact-request raw model responses are cached separately so a
changed deterministic projection can reuse them without another paid call.
Model, prompt, page/context images, rendering settings and code version are named;
no join change invalidates extraction. These are caches, not owners. Deleting
report responses can incur new extraction cost, unlike replaying retained responses.

Report acquisition-of-readings is explicit through `scripts/read_reports.py` with
a spending cap and recorded token prices. Ordinary report consumption and joins
never dispatch a model call. Partial readings retain recovered facts and identify
unread pages/regions. Page dispositions and schema checks establish structural
coverage only. Observation identity stays in `monitoring.distinct_observations`;
report joins cannot redefine it from a cache directory, filename or code width.

The extraction configuration records effort explicitly (default `medium` for
Sonnet 5); thinking and response text share the reserved output-token allowance.
Printed section membership uses `pN/heading`, with qualifiers scoped to
`section:pN/heading`, so repeated section headings in a PDF do not become one
section and section qualifiers do not become report-wide assertions. Both the
original table-heading page and the latest headed page remain available during
continuation reading. A source statement cannot cite a page that its extraction
request did not supply. These constraints preserve provenance and scope; they do
not certify the model's transcription or interpretation. Unique exact printed
`§` markers link a section to its same-page note with recorded derivation; reused
marks remain unresolved. A literal `(Pool)` suffix can expose the identifier
component while retaining the complete cell and annotation. Neither derivation
establishes individual-plant identity or verifies the proposed transcription.

A sampling-date fact scoped only to its own section triggers one bounded,
source-only reread at high effort. The prior proposed answer is not supplied to
that reread. A failed or unaffordable reread preserves the original rows and
names the remaining attachment limit. After a paired-page output overflow, the
remaining pages of that document use single-page requests; single-page overflow
still stops explicitly until geometric subdivision is implemented.

Scanned pages receive a small affine rotation estimated from horizontal ink;
native-text pages retain their original rendering. This changes the supplied
image, never the source bytes. Deskew does not certify cell association. A
transposed repeated display becomes sample rows only when its complete matrix
equals a source-related companion table. Original axes and cell positions remain
available. The join accepts repeated occurrences only when every recovered field,
qualification and result agrees, and preserves all occurrences.

For native identifier cells, ordinary consumption checks the retained extraction
against the source cell, then reads its coordinate-sorted text. A changed order is
used only when every non-whitespace character is conserved; original native text,
cell bounds and derivation remain attached. This repairs displaced punctuation,
not identifier origin or correspondence between different codes.

Extraction permits one to three independent PDF processes under one shared,
transaction-locked spending ledger. Returned usage and interrupted requests are
different states. An explicit interrupted-request retry retains the full old
reservation and reserves the new attempt separately; it does not claim invoice
reconciliation. No saved successful response is retransmitted. Reader versions
describe the implementation loaded into the process, avoiding cache mislabelling
if source files change during a run.

Reading issues survive both forward observation links and reverse report-row
output. A limitation naming an exact table/column locator is attached to that
field without interpreting keywords in its cause. At an identifier column this
withholds the typed identity; its literal value remains candidate evidence.
Issues whose scopes cannot be bound remain visible at report level, not silently
resolved. This local projection does not certify the remaining role assignments.
The C adapter rejects ambiguous selection, but not an otherwise eligible pair
solely because its sampling date is unknown or other pages remain unread. Unread
report scope leaves the selected result's qualified polarity unknown; independent
inputs survive. Date-dependent consumers still require their own date evidence.

Whole-document relationship acquisition uses `read_reports.py --relationships`.
It supplies every physical page, keeps its response/request version separately
from row extraction, and never retranscribes the tables. A protocol is a document
registration identifier, not an analytical method or incoming delivery note.
Unsupported protocol proposals remain visible without acquiring typed identity.
A cache-only relationship graph follows explicitly supported replacements, retains
history and unverified components, and rejects ambiguous or cyclic supersession.
The graph is a proposed source reading, not legal adjudication. Bundled-document
identity and amendment scope require further source resolution when not recovered.

Native administrative association tables use printed header labels and verified
annex continuity (consecutive physical pages/printed folios and the same ruled
column boundaries). Unresolved fragments survive without fill-down. Source boxes
map back to the immutable original. The report join may derive an occurrence
correspondence from an observation's own report route plus an act's explicit
report number, date, plant reference and unique matching coordinates at printed
decimal precision. It preserves competing associations, distinct client codes and
source access time; no positive-result filter selects a plant. An association is
not an operative-act reading, a land-standing fact or proof of withdrawal.

## Implementation rule

Ordinary readers accept source records without a named case, fixed hash, authored
answer, correction allowlist or supported-record registry. Original bytes and
source-native values remain distinguishable from derived values. Conflicting inputs
remain visible to the accepted consumer, and an absence reaching it carries its
cause, under the rule `DESIGN_PRINCIPLES.md` owns. A reader of source records
that does not yet do this says so on its row.

Research material under `corpus/workbench/` is temporary. At the end of a bounded
unit, a result changes a canonical owner, remains as a directly consumed source
population, or is deleted. Workbench paths, dated investigations and review
packets may not appear in `source-bindings.json`.

## Current state

The earlier D acquisition and integration state was purged on 10 September 2026
because it mixed live inputs with case studies, investigation history, failed
routes, redundant manifests and superseded interpretations. No earlier D review,
file count or acquisition claim survives the purge.

Generic readers for tabular, geographic, document, event, evidence and calendar
inputs remain. They are implementation starting points, not claims that a source
population is currently acquired or semantically complete. Each source family in
`INPUTS.md` is open until its complete within-aperture population and ordinary
consumer path are established.

Stage D does not define government Actions, durable domain nouns or the platform.
Those remain Stages E, F and G.

## Verification

Run the D tests with:

```bash
PYTHONPATH=regulation/stage-c:regulation/stage-d .venv/bin/python \
  -m unittest discover -s regulation/stage-d -p 'test_*.py'
```

`verify.py` checks that the A–C projection, contracts and compact source map agree.
It rejects workbench paths and historical evidence fields. Neither tests nor the
verifier certify source meaning or Stage D completion.

## Observed-subject composition

`cordon_d.subjects.observed_subjects` accepts the unchanged complete monitoring
iterator. Each result retains its observation, separate host reading, published
parcel references and literal correspondence candidates. It does not enumerate
physical plants. `HostNames.load` reads the retained EPPO structured sources;
`specified_versions` reads the historical Annex II texts. The captures and current
limits belong to the plant/population and parcel rows of `INPUTS.md`.

`subject_with_finding` can refine an observed genus using the scientific species
in that observation’s own unambiguous report, preserving genuine conflicts.
Pass the existing finding join to `finding_host` for the finding's species, rather
than borrowing the observation's host. `infected_species` combines the readable
explicitly selected `(source hash, result locator)` occurrences with separately
supplied Xylella finding qualification and adopted-area
membership. Evaluate that membership against the decision's relevant area version;
keep the earlier sampling date on the finding. The supplied finding qualification
includes applicability to the area’s operative pest scope, which remains owned by
A and the area/finding evidence. Annex II host-list selection does not itself
qualify a diagnostic result or redefine C’s species-history input. `species_category_facts` accepts
the resulting scoped history and supplies `eradication_species_facts` without
changing C. A complete infected-species inventory requires `RequiredPopulation`
with scope `json.dumps([area, event_date.isoformat()], separators=(',', ':'))` and
its own evidence; a negative observation cannot supply it.

`cadastral_memberships` composes the published observation location with
`areas.membership_evidence`. It returns whole-parcel inclusion, partial
intersection and subject-location membership separately, with source supports.
It locates the observation as published, not an individual plant at a later date.
Conflicting reference components prevent a positive subject-location conclusion.
Partial intersection provides no numerical position or error bound and cannot
bypass the positional owner. It establishes neither title nor standing.

`InspectionUnitReading` admits formal identity schemes with exact observation
membership. `SubjectCorrespondence` also admits sufficient direct evidence that
observations concern the same or different subject; no registry or published
identifier scheme is required for that route. Literal note patterns supply only
`ReferenceReading` candidates. Reconciliation retains conflicting readings and
both tag and previous-sample relationships. `observed_subject_survey` counts only
established distinct units through C; it retains an independently qualified
positive observation even when persistent identity is unavailable. Both survey
adapters require the operative `period=(start, end)` and select [start, end)
observation dates before qualifying results. `stratum_of` selects membership in
the required population; `None` excludes an observation. Unit identity cannot
move results across periods or establish C's separate method, population,
performance and independence qualifications.

`scripts/read_subjects.py` consumes every observation and supplies
host/report/cadastral connections. The rejected supplied-scene loader and
containment matcher have been removed. A reproducible public-source identity
producer, including records without resampling notes, remains incomplete.

`scripts/read_subject_images.py` reads retained RGB frames locally through the
pinned public DeepForest tree detector. Install `subject-images-requirements.txt`
in a separate environment. Model bytes, published prediction configuration and
source imagery are hash-verified; code, configuration and exact package pins
version the derived readings. No observation result, note or expected pair enters
pixel inference. `cordon_d.subject_images.crown_candidates` converts its pixel
rectangles to the frame's published coordinate system. These are retrieval
candidates, not observation-to-plant memberships, survey units, or positional
bounds. In particular, a tree rectangle does not identify a shrub beneath it.
The image reader currently contributes no inspection-unit identities to C.

`scripts/acquire_host_names.py --report-reading-version <revision>` acquires only
the taxonomy reached by monitoring and that explicit retained report reading,
including all returned candidates and genus ancestry. Existing responses are
reused; credentials are read from `~/.config/cordon/eppo-api-key` and sent only as
an API header. This command never acquires report readings or calls a model.

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

Admission has a temporal half. A source population is complete for a consumer when
it covers every event date that consumer's accepted clocks can reach from any
decision date on or after the evaluation's own knowledge cutoff (`contracts.json`).
The reach is derived from accepted B, is decision-date-relative, moves with the
epidemic, and is never written as a year. Today the longest reachable backward
period is four years: `B-CLK-EU-6(1)-four-negative-years`, beside the two-year
`B-CLK-EU-7(1)(e)-sub2-two-year-lookback`; the five-year
`B-CLK-LR4-3(4)-pre-LR45-five-year-no-detection` applies only to a decision in the
pre-L.R. 45 interval and cannot be reached. Three kinds of fact take the rule
differently. Observation-dated facts (`INPUTS.md` rows 1, 2 and the vector and
treatment row) are complete over that reach, negatives as much as positives; outside
it a record keeps three uses — continuity evidence for an identity, a rendition an
in-reach fact's correction or replacement chain requires, and read-verification
material for a reader — and is not otherwise completed. Act-dated facts with live
effect (rows 6, 7, 8 and 11) are bounded by liveness, not by date: an order is in
the population until execution or withdrawal closes it; a notice, publication,
response or standing fact follows the order it concerns. Adopted area versions
(row 3) are acquired when A's interval for the version overlaps an event date
inside the reach. Identity-over-time facts (rows 4, 5, 9 and 10) are completed as
the identity currently stands; a status that varies in time, such as protection
or a parcel reference, is read at the in-reach event date from that identity's
own history, which enters per identity and is never a register population to
complete. An undated
record is outside the rule: it is dated, or it stays visible with the cause. Rows
outside the reach are not resolved by it; they are outside the bar.

The Osservatorio's own casefile, protocol, notice, response, assignment and field
records are first-party inputs. Public manuals describing those systems do not
supply the underlying facts and are not part of the D baseline.

Regional removal determinations are called `removal-orders` in the source map.
Some accepted source text calls their operative direction a `prescription`; that
is the meaning of the `case-prescription` input contract. It is not a medical
prescription or a separate product workflow.

## Administrative publication records

`cordon_d.removal_events.publication_records` consumes the retained native
Capurso/Akropolis register JSON. It preserves all fields and identifies the
regional act from its explicitly labelled subject, separately from the municipal
incoming protocol and date. `connected_publications` requires the act identity
and adoption date from the measure consumer. Whole-measure qualification precedes
population dispatch; independent register declarations remain available.

`publication_deadline` passes the exact event kind, document and competent
municipality to accepted B/C clock calculations. It requires the caller's
calendar. A result using `national_calendar()` has that baseline's local-holiday
limitation. The calculation does not establish recipient effect, uninterrupted
posting, election, silence, default or completed removal. No clause wording,
layout or adoption date generates an assignment or performance event.
`event_deadline` can forward an explicitly supplied prescribed term to its
upstream quantity and boundary consumers, checking its document/recipient context.
It imports no proposed type and supplies no acceptance bypass: that source-bound
clock and type require their own accepted A–C owners before ordinary use.

`cordon_d.notices.parsec_publication_declarations` reads the publisher's labelled
table, including native ICEfaces historical-search responses. It preserves each
publication occurrence, declared dates, requesting office and emitted original
routes. A correction-labelled entry and another entry can serve identical PDFs
without becoming one publication or establishing an amendment. These declarations
remain available independently of whole-measure qualification.
`removal_events.parsec_publications` attaches the exact emitted document route through
its acquired source hash to the measure identity and adoption date. It preserves
separate publication occurrences even when they serve identical documents; a
referenced predecessor in a subject does not replace the attached act.
The adapter also requires the register capture's acquisition record before emitting
events. Displayed future dates remain declarations, and an end date becomes an
occurred anchor only after that local calendar day has elapsed. This does not prove
uninterrupted posting or recipient effect.

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
and typed readings remain Parquet keyed by source hash and reader version. The
grouped distinct-observation stream is a regenerable Parquet keyed by the ordered
`(url, view, sha256)` sequence of retained releases, the reader version and the
DuckDB version. Reports use compact JSON blocks and an assembled reading under
source hash and extraction version. Each native identifier cell of that assembled
reading carries one regenerable record holding the positioned reading of the cell,
the source cell bounds and what the geometry read found. For an unchanged cell
that positioned reading is the cell's own text, and it is what the read path
compares against. The read path establishes that the stored positioned text has
not diverged in content from that retained cell, and refuses a reading whose
native identifier cell carries no record until it is reassembled; that the stored
order is the source order is established only at assembly under the extraction
version. The moved byte check has a cost: an inventory-preserving corruption of
the retained native cell is not detected on read, because the comparison against
the source cell runs at assembly under the extraction version.
Exact-request raw model responses are cached separately so a
changed deterministic projection can reuse them without another paid call.
Model, prompt, page/context images, rendering settings and code version are named;
no join change invalidates extraction. For an annotated result, the source reader may return `result_value` and `annotation` alongside the complete cell. Their concatenation must reproduce the cell (with only whitespace variation), and `result_value` is allowed only in a result column. Polarity is projected from that supported component; the original literal and precisely scoped qualifications remain available. The projection never strips presumed footnote suffixes on its own. `extract_report(resume_from=...)` can retain validated, fully read page blocks from an explicitly selected prior version and request only uncovered pages. It preserves those blocks and their original request identifiers; a smaller configured page width applies only to the remaining reading. Incomplete page blocks are reread, and continuation-only repairs retain their separate existing entry point. These are caches, not owners. Deleting
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
transposed display becomes sample rows when its printed field-label axis and
complete value matrix equal a unique companion table. A publisher need not add
a prose declaration of repetition. Original axes and cell positions remain
available. Qualification attachment follows those original positions: a sample
column stays sample-specific, and a field-row qualifier reaches that field across
its samples. Projected column indexes never replace the original scope selectors. Matching source-supported identifiers, populated fields and analytical results can establish repeated
displays across report pages; rows repeated within one table remain competing
occurrences. Blank extra display fields supply no additional value. Each occurrence
retains its own qualifications; correspondence does not assert that qualifications
agree or authorize moving them between occurrences. Sampling dates and
conflicting recovered section headings still constrain correspondence. A
record continuation is recovered explicitly by the established document reader as
one `record_continuation` fact, quoting the printed identity and naming every
physical part. `reports.record_rows` resolves those exact selectors and assembles
the declared parts; it does not discover continuation from layout or equal results.
A bound fragment-only table remains a physical record part even without its own
identifier or result column. When a descriptive field itself spans pages, a
`field_continuation` fact binds its exact cells and quotes the record identity at
its physical page. The assembler joins successive word fragments with whitespace,
retains every original cell under `source_fragments`, and preserves qualification
scopes. Matching headers or differing values alone do not establish a split field.
Overlaps, conflicting bindings and unsupported splits of identifiers, results,
numbers, dates or within-word characters remain failures requiring source reading;
no generic string concatenation resolves them. Empty printed placeholders supply
no conflicting field or sampling date. Binding-only blocks survive cache replay.
It works without a separate complete display. Native-cell anchors or exact output
row selectors permit different source layouts and cross-block references. Each
cell retains its physical locator, and each qualification retains its original
scope. The reverse consumer returns every physical part with its observation link.
Unbound, conflicting or overlapping declarations trigger a bounded reread through
the same document reader. When cells are already retained, `extract_report` accepts
`continuation_from=<retained version>` to recover only omitted continuation facts
through its existing prompt, schema and provider. That repair preserves the original
blocks and request provenance; it does not retranscribe the tables. Identity-only
quotations must cite the identity-bearing physical page. Ambiguous source structure is read as partly recovered
and goes through that reader's page-completion repair. A failure never authorizes
a second semantic extraction path or an invented correspondence.

The ordinary loader carries the producer's `assembly_complete` attestation.
Physical pages read, document relationships read, and record assembly complete
are separate requirements for a complete candidate. A failed, pending or
unattested assembly retains its cells, occurrences and independent qualifications;
it cannot supply complete-reading polarity to the confirmation adapter. The
assembly attestation is document-wide: it does not establish that an occurrence
is unaffected by an unresolved continuation merely because its own cells exist.


For native identifier cells, ordinary consumption checks the retained extraction
against the source cell, then reads its coordinate-sorted text. A changed order is
used only when every non-whitespace character is conserved; original native text,
cell bounds and derivation remain attached. This repairs displaced punctuation,
not identifier origin or correspondence between different codes.
Two-digit date years resolve only against a unique matching full year in scoped
source date statements. The literal date and supporting statement IDs survive;
no current-year assumption or platform century cutoff supplies the year. A date
spelled with an Italian month name resolves the same way. A printed date range or
list constrains a separately stated sampling day and never supplies one; a row
whose only date statement is a range or list has no exact day, and says so.

Extraction permits one to three independent PDF processes under one shared,
transaction-locked spending ledger. Returned usage and interrupted requests are
different states. An explicit interrupted-request retry retains the full old
reservation and reserves the new attempt separately; it does not claim invoice
reconciliation. No saved successful response is retransmitted. Independent subscription runners
lock the exact request before dispatch and reuse a response completed by the
lock holder, preventing concurrent duplicate calls. Reader versions
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
The source reader assigns that role. Deterministic projection checks only that the
proposed identifier occurs within its own component quotation; spelling, prefixes
and numeric shape cannot establish or reject administrative meaning. Unsupported
proposals remain visible without acquiring typed identity.
A cache-only relationship graph follows explicitly supported replacements, retains
history and unverified components, and rejects ambiguous or cyclic supersession.
The graph consumes every available relationship inventory, including documents
whose sample rows remain unread. Row materialization is limited to documents
reached by the observation routes and that graph; an unread replacement cannot
make its predecessor eligible.
Every competing branch from a rendition's replacement ancestry must explicitly
reach that rendition before it can be current. Extending one branch cannot settle
the fork, and the observation's entry route cannot change this determination.
Potential predecessors also constrain eligibility: an ambiguous replacement or
unresolved amendment affecting that ancestry cannot disappear through descendants.
Possible ancestry never becomes a resolved supersession link. Source-supported
disambiguation or explicit whole-report reconciliation can remove the competition.
The graph is a proposed source reading, not legal adjudication. Bundled-document
identity and amendment scope require further source resolution when not recovered.
An explicit source-review finding can request a fresh relationship reading even
after structural completion. Its instruction and exact request remain retained;
the finding names what to examine and supplies no replacement answer.

Native administrative association tables use printed header labels and verified
annex continuity (consecutive physical pages/printed folios and the same ruled
column boundaries). Unresolved fragments survive without fill-down. Source boxes
map back to the immutable original. The report join may derive an occurrence
correspondence from an observation's own report route plus an act's explicit
report number, date, plant reference and unique matching coordinates at printed
decimal precision. It preserves competing associations, distinct client codes and
source access time; no positive-result filter selects a plant. An association is
not an operative-act reading, a land-standing fact or proof of withdrawal.
The monitoring publication itself can supply that explicit report identity and
date. Its native geographic coordinates are compared at published precision;
transformed coordinates never acquire invented printed precision. The accepted
observation grouping links its source publications. Derived correspondence requires
complete report-page coverage and uniqueness in both directions, preserves the
source locations, and does not equate distinct field and laboratory codes. An
explicitly printed parenthetical binomial can supply a second host label.

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

## Subscription document transport

`cordon_d.document_subscription.read_documents` sends complete retained PDFs,
including native text and every rendered page, through the authenticated Codex
subscription. The caller supplies ordered source hashes, its prompt and its strict
JSON output schema. An act and separate annexes can therefore form one request
without being forced into a laboratory-report representation. This transport has
no dependency on the laboratory reader and does not dispatch Claude jobs.

The first intended caller is the removal-measure reader (INPUTS rows 6–8 and 11).
Its initial allocation is one worker, one complete act with necessary annex context
per request. Luna-high failed native target and shared-cell fidelity on the first
measure; repeating its instructions and extending its timeout did not repair that
failure. The caller now qualifies Astra-medium with separated native ownership
and administrative interpretation. Neither setting is a permanent constraint;
the caller must exercise its own
source-to-consumer contract before population dispatch. Source admission, document
relationships, qualifications, validation and publication of accepted readings
remain with that reader. The transport returns a proposed reading, never a
completion or legal-effect assertion.

Callers may explicitly supply complete native UTF-8 HTML or plain text through
`source_formats`. Those bytes are hash-checked and included verbatim; no scripts
run, linked resources load, or physical pages get invented. Mixed requests retain
their supplied order and the complete PDF views. Format declarations enter request
identity only when supplied, preserving existing PDF-only identities. The caller
must establish whether the native source carries the relevant meaning; this option
cannot stand in for visual reading where layout or omitted assets matter.

The measure caller also requests supplemental complete-page views when exact,
non-reflected image-placement geometry establishes a quarter-turn. The page's own
rotation is included. All original pages remain first and unchanged; supplemental
views preserve visible clipping, masks and overlays. Their source, physical page,
clockwise turn, triggering image occurrences and transforms, attachment index and
image hash remain in request provenance. Shear, arbitrary angles and orientation
inside the image pixels are not inferred. This changes source presentation, not
source meaning or semantic acceptance. Other callers retain their existing default
presentation and request identity.

Execution is explicit (`execute=True`). `read_retained(request_id, store)` consumes
an explicit retained request with its original context, independently of a later
caller's prompt. It verifies request identity and validates the retained output;
it cannot dispatch. Request identity includes the source hashes, actual prompt and
schema, rendered image hashes, model, effort and transport version. A lock prevents
duplicate dispatch of an identical request; it does not coordinate different
providers or different tasks on one document. Raw output, elapsed call time and
provenance are retained in the regenerable store. Invalid JSON or output that
violates the caller's schema remains retained and cannot become a returned reading,
on either execution or replay. Non-JSON numeric constants and numbers that overflow
to non-finite floating-point values are rejected before validation. Schema validity
is checked before dispatch; schema
references must resolve within the supplied schema, without network retrieval.
Source-review instructions change the request;
replay never secretly spends another call. API-key fallback, shell tools, multi-agent dispatch and web search are
disabled. A bounded subprocess timeout applies.

The calling reader uses the shared store and retains the request reference beside
its interpreted output. No second source inventory, scheduler, extraction schema,
or evidence-acceptance model is introduced here. Laboratory relationship batching
can reuse the transport later; it is not an implemented caller in this unit.

## Removal-measure reading

`cordon_d.measures` supplies a caller-owned whole-act contract to the accepted
subscription transport. `measure-reading.txt` owns the source-reading instruction.
The reader takes one complete act and its necessary annex context, preserving
source citations, current versus deferred directions, incorporated target
occurrences, published addressee positions, corrections, actual versus intended
events and conclusion-specific limitations. `scripts/read_measures.py` replays by
default; `--execute` uses the allocated single Codex worker. A changed source-review
instruction is explicit and yields a different transport request.

| Accepted D contract | Measure contribution and limit |
|---|---|
| `case-prescription` | `directions`, source-position selections, `parts` and `references` retain prescribed scope, occurrences and the exact stated correction. `prescribed_targets()` selects identified plant/parcel positions in operative parts under present removal directions; map context, deferred and corrective positions remain available. |
| `operative-status`, `evaluation-context` | Identity, adoption, declared effect and conditions supply source facts. Adoption does not establish recipient effect or choose the applicable A route by itself. |
| `recipient-notice`, `administrative-event` | Route reasons and timing remain in the directions. Actual dated events about the resolved measure reach `AdministrativeEvent`; publication adapters connect independent register records. An unresolved measure leaves other measures' supported publications usable. |
| `party-land-standing` | Published addressee cells and their row scope supply positions in the act. They do not supply independent title or establish a corrected recipient's notice. |
| `owner-response`, `removal-performance` | Completed records can supply their stated events; intentions, blank forms and missing histories cannot. A free-text work description does not establish required-work coverage or completed removal. |

`MeasureReading` connects act identity and adoption to the existing publication
adapter, retains the actual prescribed target rows separately from A–C's required
population, and reuses the accepted association reader for report relationships.
For rows it can associate, the association owner supplies sample/report identity,
printed dates, host, coordinates and cadastral fields with verified row continuations. The model
does not output another version of these values. `measure_sources` exposes native
source addresses using that owner's orientation and row coordinates. Interpretation
selects row populations, additional field columns, prose spans, directions and
document-part roles; composition copies native characters and reuses the original
association object. Shared physical cells and verified split rows retain all their
fragments. Layout establishes source locations, never operative meaning or time.
Within a ruled table, a missing logical association cell uses only the unique drawn
cell that actually covers its position; a separate blank cell stays blank. Across
pages, interpretation explicitly selects the ordered native cells or non-table word
spans composing an additional field, with support on every affected page. The
consumer retains those fragments and the target's own cell, including a blank
continuation cell. An empty quotation can support only a target scope's explicitly
selected, recovered blank native fragment on that source page; a locator and full
fragment support remain required. Unrecovered text, other claims and unrelated
blank cells cannot use that allowance. Shared addressees can govern several target rows; owner-only
fragments do not become plants. No parcel-value match or automatic forward filling
establishes the relationship, and selection cannot copy an association-owned column.
An infected-plant reference printed beside surrounding parcels remains
`reference_plant_id`, distinct from an ordered plant's `plant_id`; it supplies no
report association. Additional columns cannot rename or duplicate a column already
supplied by the association owner.
Where report columns are absent, the same native header owner can supply the
selected row's other printed fields without creating a report association. A unique
plant-bearing header and actual physical cells are required; explicit field selections
remain intact. Header ambiguity is a reading limitation, and blank cells stay blank.
These additional native fields do not change retained source-address contexts or
admit another target population.
Where native geometry survives but cell text is structurally unavailable (no
extracted text, opaque private-use characters, surrogates or replacement characters),
the existing field-fragment selection can carry a visual transcription at that exact
cell. Original text, geometry and extraction limitation remain attached. Usable
native values, printed blanks and fields owned by an existing association cannot be
replaced this way. Cross-page/shared fields retain their original fragments;
conflicting transcriptions of the same cell are rejected. This mechanical recovery
does not certify the proposed reading or detect every valid-Unicode extraction error.
Image-only and vector-outlined content uses explicitly model-transcribed positions
from the rendered source. An embedded image can supply a target beside a native
table only when their source regions are disjoint. Overlapping image selections
and whole-page retranscription cannot bypass native ownership. Each logical table
row remains one position, with
shared cells attached to each row they govern. Parallel lists of identifiers,
parcels or addressees cannot stand in for their row relationships. Source-authored
prose groups remain groups. Complete source pages remain in every request; native
addresses supplement them. Municipality mentions and contextual map labels do not
become ordered targets merely by referring to an operative direction.
For a correction that carries forward an unchanged native sample/report
association, an image position can explicitly select that source table and row.
The relationship needs the operative correction and both source positions as
support. Composition reuses the association object and rejects retranscription of
its fields; the corrected addressee retains its own image provenance. The current
position’s part role determines target admission, independently of the predecessor
field locations. An absent selection stays absent, including in earlier retained readings. No field-value
match creates the relationship.
Context documents support the principal act's incorporation without importing
unaffected predecessor targets into a partial correction. The reading must retain
both the incorporating clause and the incorporated work and conditions.
Direction links apply to the position as printed, including its addressee. An old
position can support the correction without carrying present removal work; that
work belongs to the operative corrected position. Native composition preserves
the old name rather than silently replacing it. Distinct performance clocks retain
their stated scope and anchor; their operative combination belongs to accepted A–C.

Each reference can explicitly select supplied context documents, with support on
both the citing source and each selected document. This includes reports named
collectively in prose; their rows do not become administrative targets. Unresolved
or unsupplied documents remain unselected. The consumer does not resolve free prose
by matching numbers or filenames. Earlier references without selections supply no document binding; their existing
native per-row associations remain consumable.

Directions may additionally expose source-stated `commencement_components`:
required actor and work, trigger/performance, term magnitude/unit/bound/anchor,
and the expressed commitment, with complete clause support. The parent's full
conditions and coercive scope remain intact. Components never establish actual
notice, noncommencement or the applicability of an A rule. A prior response that
did not request them carries a reading limitation, not source absence; a recovered
minimum or unknown bound cannot be treated as a maximum deadline.
`read_measure_components(base_request, direction_ids, ...)` uses the same owner
and complete original sources to recover only reached components. It supplies
source addresses and quotations, without prior expected values. Explicitly
selected component requests replay through `retained_measure(...,
component_requests=...)`; raw readings, targets and events remain unchanged.
Known conflicting readings, including a prior explicit empty result, remain
conflicting. `commencement_components(direction_id)` exposes the components,
their source-reading provenance and precise limitation; it does not certify
legal form from matching labels.

Administrative references may additionally carry source-supported typed act
components: issuing authority, literal issuer, number, year and adoption date.
Unstated components remain null; the principal act does not lend its identity to a
reference. `MeasureReading.referenced_measures(readings)` corresponds these claims
to existing measure readings, or resolves a selected document by its principal
source hash. It preserves the original reference, affected payload, candidates,
conflicts and missing correspondence. Resolved authority, number and year may
identify an act without a separately stated literal issuer; adoption dates, when
stated, must agree. Multiple candidate readings remain ambiguous. An incompatible
document selection remains unresolved without suppressing an independently
supported reference. Context hashes never substitute for principal identities.
This operation does not select an operative version, apply a correction, combine
work populations or import predecessor targets. Those meanings need their own
source support. Older retained readings replay without fabricated act components;
absence of a structured administrative identity remains a reading limitation.

`MeasureReading.finding_links(joined, report_readings)` connects prescribed positions
to ordinary `findings()` and `report_rows()` outputs. Its report population comes
from existing native per-row report associations or explicit document selections,
and the report owner's resolved replacement chains. Each native association confines
its own target to the report it names; a collective reference cannot override it.
When a native row states only a report number and date, an explicit two-sided
document selection may supply its report context. The entire native reference
and its own date must match the selected report through the report identity
owner. Competing selected documents remain ambiguous for that occurrence;
another row's unambiguous reference remains usable. `report_population()` retains
the original association, selection and support. Passing that population as
`findings(..., report_bindings=...)` makes the same scoped associations available
to the ordinary occurrence comparison, within each observation's acquired report
route. It supplies neither a host equivalence nor missing report fields.
Unequal printed host labels remain unresolved equivalence. Their difference
alone does not establish a biological disagreement, and cannot support a join
that requires host agreement.
The consumer retains the cited rendition and every relationship. Amendments and newer
dates alone do not expand that population. Native identifiers are compared only
inside this source-bound population, with the existing host and coordinate checks
where supplied. Each target needs one finding, and each finding one prescribed
position in this act; repeated report displays remain with their original finding.
Competing candidates, reading failures, provisional status and source disagreements
stay visible. A link establishes occurrence correspondence, never official
confirmation, standing, administrative amendment or completed removal. The caller
must supply all observation identities referring to the selected report population
and its consequential renditions; filtering to expected target IDs cannot establish
reverse uniqueness. Full source-population reconciliation remains a separate duty.

`retained_measure` and `scripts/read_measures.py --request` consume a named retained
interpretation offline, requiring its measure schema and source addresses to match
the composition contract. Native source bytes are hash-checked. Request addresses
carry cell text, row membership and line words; repeated geometry stays with the
native composition. Earlier, more verbose address renderings replay against the
same values, and compatible readings survive additive field roles. This preserves
the original interpretation and source
context when the surrounding consumer changes; it does not patch rejected readings
or silently dispatch a replacement. Source checks remain distinct from qualification.
Dated actual events use `AdministrativeEvent`; plans, blank forms, other unresolved
payload identities and imprecise event times remain source readings rather than
invented anchors. A blank form can still state consequential response or capacity
requirements; those remain directions or part qualifications, not actual responses.
Source-boundary validation checks citations and references, not
legal truth. Qualification requires independently read originals and an actual
consumer connection; schema validity, page counts and retained responses cannot
establish it. The subject-population owner still supplies plants, parcels and
protected-status populations; the measure's named positions do not establish title.

## Official performance reports

`cordon_d.performance` reads complete retained native HTML through the same
subscription transport and replays an explicit retained request offline. It keeps
the reporting document, stated operation, literal work scope, performer/reporting
actor, timing, source citations and limitations. A direct record, an official
reported event and an intended operation remain distinct. Native CSS selectors
must locate one source element and support a contiguous quotation; scripts, styles
and template content cannot supply visible evidence. Unknown exact dates retain
their causes and the actual timing statement. A publication date alone cannot
become the operation date. These checks verify source addresses and structural
distinctions, not semantic truth.

`PerformanceReading.removal_occurrences()` exposes actual direct or reported
removal with existing `Support` objects and retained model-reading provenance.
Intentions and other work remain in the reading but do not become removal
occurrences. Literal outbreak-level performance can be useful even when the
source supplies no exact day, executor or target list. The consumer retains that
scope; without a supported prescription/target correspondence and sufficient work
coverage, it establishes no per-target completion assertion or clock anchor.
Qualification requires independent reading of the original reports. A municipal
service certificate enters this chain only through a supported relationship to
required removal or treatment; its existence does not admit an unrelated service
or procurement workflow. INPUTS row 11 owns current source coverage and limits.

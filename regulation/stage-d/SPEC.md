# Stage D — real inputs for accepted A–C

Stage D connects the accepted legal and computational system to facts the
Osservatorio can actually obtain and use. For every required input it establishes
the source population, record meaning and grain, identity and time relationship,
ordinary reader, and exact unresolved limitation.

The [input map](INPUTS.md) owns current source coverage and limitations.
[contracts.json](contracts.json) owns the input kinds;
[predicate-contracts.json](predicate-contracts.json) and
[additional-input-contracts.json](additional-input-contracts.json) bind accepted
A–C requirements to them. [source-bindings.json](source-bindings.json) owns source
routes. `inventory.py` computes the A–C consumer projection when needed.

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

[notices](cordon_d/notices.py) retains native register declarations, their separate
publication occurrences, dates, offices and original-document routes.
[removal_events](cordon_d/removal_events.py) connects them to measure identity and
adoption through explicit act identifiers or acquired document attachments.
Incoming protocol, adoption, publication and recipient effect remain distinct;
identical attached bytes do not merge publication occurrences or prove amendment.
Attachment adapters require the acquisition record and keep future dates as
unoccurred declarations.

`publication_deadline` and `event_deadline` check the document, event kind and
recipient or competent publisher before invoking accepted B/C calculations.
The caller supplies the calendar; `national_calendar()` retains its local-holiday
limitation. Prescribed terms remain subject to their accepted A–C type and clock.
A declared posting interval does not prove uninterrupted posting. Complete
publication certificates supply their own attested interval; unresolved act
identity can be connected through the acquired certificate and principal routes.
Neither record supplies recipient notification, response, default or performance.

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
`Member.publisher_annotation` preserves the campaign source's literal and citation
on its own occurrence without changing identity or grouping. An older cache
missing that reading remains distinguishable from an absent column or null value.
The grouped distinct-observation stream is a regenerable Parquet keyed by the ordered
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

Extraction retains spending reservations and returned usage separately; an
interrupted retry does not erase its earlier reservation. Exact-request locks
prevent duplicate dispatch and reuse saved responses. Reader versions describe
the implementation loaded into the process, so changing files cannot relabel a
running extraction's cache.

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

## Stage status

[state/CURRENT.json](../../state/CURRENT.json) owns acceptance and the next gate;
[INPUTS.md](INPUTS.md) owns each source family's sufficiency. Reader availability
does not establish source-population completeness. Government Actions, domain
nouns and platform compilation remain Stages E, F and G.

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

[document_subscription.read_documents](cordon_d/document_subscription.py) supplies
complete retained PDFs, native text and rendered pages to a caller's prompt and
strict JSON schema. Callers may explicitly supply complete native HTML or plain
text; linked assets are not fetched, so layout-dependent meaning still requires
the relevant source views. Supplemental rotations retain the originals and their
image provenance. Admission, source relationships and semantic qualification
belong to the calling reader.

Execution is explicit. `read_retained(request_id, store)` validates and replays the
named request offline without dispatch. Request identity binds source hashes,
prompt, schema, rendered images, model, effort and transport version. Raw responses
and provenance remain retained; invalid JSON, non-finite numbers or schema failures
cannot become returned readings. Identical requests share a lock and successful
response. Schema references resolve locally. CLI dispatch disables API-key fallback,
shell, web and agent tools; retained requests preserve the actual provider and source
presentation used. Runtime settings remain with the implementation.

## Removal-measure reading

[measures](cordon_d/measures.py) reads a complete act and its necessary annex/context
documents under [measure-reading.txt](measure-reading.txt).
`scripts/read_measures.py` replays by default and dispatches only with `--execute`;
`retained_measure(request_id, store)` preserves an explicit reading's original
request, source addresses and limitations.

`MeasureReading.targets()` retains source-defined positions and direction links.
`prescribed_targets()` selects identified plant/parcel positions in operative parts
under present removal directions. Maps, deferred work and superseded addressee
positions remain distinguishable. Published addressees do not establish title;
blank forms may state response or capacity requirements but supply no response.
Adoption, declared effect, intended procedure and actual dated events retain their
separate meanings; only supported events about the resolved measure become
`AdministrativeEvent` values.

[measure_sources](cordon_d/measure_sources.py) composes selected native cells and
word spans while reusing the existing association owner's fields and occurrences.
Shared cells and cross-page fields require source-supported applicability and keep
their fragments; owner-only continuations do not create targets. Native spans may
select positions combined by a detected table, but cannot duplicate selected
positions or association-owned fields. Image recovery preserves its source region
and extraction limitation without overwriting usable native values or printed
blanks. A surrounding parcel's `reference_plant_id` remains distinct from an ordered
plant's `plant_id` and supplies no report association. Source-authored groups and
row relationships survive composition; field-value equality establishes neither.

`referenced_measures(readings)` resolves source-declared act identities or selected
principal documents against separately read measures, retaining candidates,
conflicts and missing correspondence. It does not apply corrections, choose an
operative version or import predecessor targets. Incorporated work and corrections
need their own source support, including the affected position and addressee.

`read_measure_components` and `commencement_components(direction_id)` recover and
expose source-stated actor, work, trigger, term and commitment through the same
whole-source reader. Selected supplements retain their provenance and conflicts;
missing structured readings remain reading limitations. These components establish
neither actual noncommencement nor the applicability of an A rule.

`report_population()` binds existing per-row report associations or explicitly
selected documents through the report owner's identity and replacement relations.
A collective reference cannot override a row's own report reference and date.
`findings(..., report_bindings=...)` consumes those bindings within each observation's
acquired report route. `finding_links(joined, report_readings)` connects prescribed
positions to those findings and reverse `report_rows()`, preserving host/coordinate
comparisons, uniqueness, provisional readings and disagreements. Callers supply all reached
observation identities and consequential report renditions; filtering to expected
targets cannot establish uniqueness or population completeness.

An explicit source clause may connect an exact report rendition's whole specimen
population to stated host words. That correspondence requires complete unique
coverage of report records and bound targets, including negatives, with compatible
dates, coordinates and qualifications. Unsupported subsets, extra or competing
occurrences remain unresolved. Literal host labels and unresolved equivalence stay
intact; unequal labels alone establish no biological disagreement, and neither equal
counts nor a replacement relation establishes equivalence. A finding link
establishes occurrence correspondence, not official confirmation, standing,
administrative amendment or completed removal.

Qualification requires independently read originals and the resulting ordinary
consumer behavior. Exact retained address contexts remain replayable, but successful
replay, structural coverage and source-address validation do not certify meaning.
Current source populations and unresolved work belong in [INPUTS.md](INPUTS.md).

## Official performance reports

[performance](cordon_d/performance.py) reads complete retained native HTML and
replays explicit requests offline. Source selectors support the stated operation,
actor, timing, work scope and limitations. `removal_occurrences()` exposes direct
or officially reported removal with its source document and reading limitations;
intentions remain separate. Publication dates do
not become operation dates. An outbreak-level report can supply useful evidence
without an exact day or target list, but per-target completion requires supported
prescription/target correspondence and sufficient work coverage. Coverage and
remaining acquisition needs belong to the execution row of [INPUTS.md](INPUTS.md).

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
reading carries one regenerable record holding the positioned text, the source
cell bounds and what the geometry read found; the retained cell is the native
text and the record keeps no second copy of it. The read path establishes that
the stored positioned text has not diverged in content from that retained cell,
and refuses a reading whose native identifier cell carries no record until it is
reassembled; that the stored order is the source order is established only at
assembly under the extraction version.
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
per request, with `gpt-5.6-luna` at `high` effort as a candidate setting. That setting
is not yet qualified for whole-measure meaning: the caller must exercise its own
source-to-consumer contract before population dispatch. Source admission, document
relationships, qualifications, validation and publication of accepted readings
remain with that reader. The transport returns a proposed reading, never a
completion or legal-effect assertion.

Execution is explicit (`execute=True`); otherwise only an identical retained request
can be replayed. Request identity includes the source hashes, actual prompt and
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
replay never secretly spends another call. API-key fallback and model tools are
disabled. A bounded subprocess timeout applies.

The calling reader uses the shared store and retains the request reference beside
its interpreted output. No second source inventory, scheduler, extraction schema,
or evidence-acceptance model is introduced here. Laboratory relationship batching
can reuse the transport later; it is not an implemented caller in this unit.

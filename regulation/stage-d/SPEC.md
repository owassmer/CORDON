# Stage D — real inputs for accepted A–C

Stage D connects the accepted legal and computational system to facts the
Osservatorio can actually obtain and use. For every required input it names the
source population, record meaning and grain, identity and time relationship,
ordinary reader, and the exact unresolved limitation.

The plain-language input map is `INPUTS.md`. `contracts.json` owns the input
kinds. `predicate-contracts.json` and `additional-input-contracts.json` bind
accepted A–C requirements to those kinds. `source-bindings.json` owns the source
routes. `inventory.py` computes the A–C consumer projection when it is needed;
nothing stores it. Status belongs in `state/CURRENT.json`.

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
the tree holds no source bytes. Successful captures and distinct byte versions
are retained; a current failed attempt names its cause. A filename shared by a
failed and a successful route supplies an acquisition candidate.
`scripts/audit_store.py` re-hashes every blob.
Where a reader establishes a fact from a publisher's own redundancy rather than
from a statement the publisher makes, the check that re-derives it runs with the
acquisition that could invalidate it. For the coordinate frame of the monitoring
degree columns that check is `scripts/check_frames.py`, and
`scripts/acquire_monitoring.py --campaign` derives the readings and runs it.
Neither runs in CI, which has no store.

Beside the blobs, `derived/` holds regenerable readings, not owners. Monitoring
occurrences and typed readings are Parquet keyed by source hash and reader
version. The grouped distinct-observation stream is Parquet keyed by the ordered
`(url, view, sha256)` sequence of retained releases, the reader version and the
DuckDB version. Reports are compact JSON blocks and an assembled reading under
source hash and extraction version.

Each native identifier cell of that assembled reading carries one regenerable
record holding the positioned reading of the cell, the source cell bounds and
what the geometry read found. For an unchanged cell that positioned reading is
the cell's own text, and it is what the read path compares against. The read path
establishes that the stored positioned text has not diverged in content from that
retained cell, and refuses a reading whose native identifier cell carries no
record until it is reassembled. That the stored order is the source order is
established only at assembly under the extraction version. The moved-byte check
has a cost: an inventory-preserving corruption of the retained native cell is not
detected on read, because the comparison against the source cell runs at assembly
under the extraction version.

Exact-request raw model responses are cached separately, so a changed
deterministic projection can reuse them without another paid call. Model, prompt,
page and context images, rendering settings and code version are named. No join
change invalidates extraction. Deleting report responses can incur a new
extraction cost. Replaying a retained response does not.

For an annotated result, the source reader may return `result_value` and
`annotation` alongside the complete cell. Their concatenation must reproduce the
cell, whitespace aside, and `result_value` is allowed only in a result column.
The original literal and the precisely scoped qualifications remain available.
A result followed by printed marks, split or whole, is classified only when each
mark has a note from the same document that reaches its row; otherwise it stays
unclassified with that cause, and a mark no page defines leaves the result as
printed. Any other annotation, except a parenthesized aside, is part of the
printed result. A note fills only the contract fields its printed text states:
the result's exact printed Cq, and whether the test is accredited. A bound, a
range or any other Cq wording fills no Cq.

A result printed in a table heading applies to the rows beneath it that print no
result of their own. The heading is the text the page's text layer prints nearest
above the table's native region, below any other table above it. It states a
result when it prints one result word, positivo, negativo, rilevato, non
rilevato or dubbio in any gender or number, and no other. The result keeps the
heading as its literal and its support. A row that prints a result keeps its own,
and a part of a continued record takes its other parts' result. The heading is
read once, when the reading is assembled; the extraction version names the PDF
library's version, so a library change is a new version.

A resume keeps validated, fully read page blocks from an explicitly selected
prior version and requests only uncovered pages. It preserves those blocks and
their original request identifiers. A smaller configured page width applies only
to the remaining reading. Incomplete page blocks are reread. A continuation-only
repair keeps its own entry point: it recovers omitted continuation facts and does
not retranscribe the tables.

Ordinary report consumption and joins never dispatch a model call. Paid
extraction is explicit, capped, and records its token prices. Partial readings
retain recovered facts and name unread pages and regions. Page dispositions and
schema checks are structural coverage only. Observation identity stays with the
monitoring reader named in `INPUTS.md` row 1. A report join cannot redefine it
from a cache directory, a filename or a code width.

## Document reading

The ordinary report reader is `cordon_d.reports`. Relationships are
`cordon_d.report_relations`. Administrative annex associations are
`cordon_d.source_associations`.

Effort is recorded. Thinking and response text share the reserved output-token
allowance. Printed section membership uses `pN/heading`, with qualifiers scoped
to `section:pN/heading`. Repeated section headings in one PDF do not become one
section. A section qualifier does not become a report-wide assertion. Both the
original table-heading page and the latest headed page remain available during
continuation reading. A source statement cannot cite a page its extraction
request did not supply. These constraints preserve provenance and scope. They do
not certify the transcription. A source statement is a model-proposed reading,
a claim about the source, not a certified quotation. Native cell copies and visual
transcriptions carry distinct provenance. A rejected nonliteral component keeps
its cause. Identifiers stay strings. An invalid date keeps its original text and
a named parsing limit. An unresolved region is a reading limitation, never source
silence. A detected-table inventory can expose an omitted native region; it
cannot certify discovery on a scanned page. A unique exact printed `§` marker links a section
to its same-page note, with the derivation recorded. A reused mark stays
unresolved. A literal `(Pool)` suffix can expose the identifier component while
the complete cell and the annotation remain. Neither derivation establishes
individual-plant identity or verifies the proposed transcription.

A sampling-date fact scoped only to its own section triggers one bounded,
source-only reread. The prior proposed answer is not supplied to that reread. A
failed or unaffordable reread preserves the original rows and names the remaining
attachment limit. After a paired-page output overflow, the remaining pages of
that document use single-page requests. Single-page overflow stops with a named
reading limitation.

Scanned pages receive a small affine rotation estimated from horizontal ink.
Native-text pages keep their original rendering. This changes the supplied image,
never the source bytes. Deskew does not certify cell association.

A transposed display becomes sample rows when its printed field-label axis and
complete value matrix equal a unique companion table. The publisher need not
declare the repetition in prose. Original axes and cell positions remain.
Qualification follows those original positions: a sample column stays
sample-specific, and a field-row qualifier reaches that field across its samples.
A projected column index never replaces the original scope selector. An
identifier-only display does not compete as a result row until it carries an
analytical result.

Matching source-supported identifiers, populated fields and analytical results
can establish repeated displays across pages. Rows repeated within one table
remain competing occurrences. A blank extra display field supplies no additional
value. Each occurrence retains its own qualifications. Correspondence does not
assert that qualifications agree, does not authorize moving them, and does not
make one result into two tests. Sampling dates and conflicting recovered section
headings still constrain correspondence.

A record continuation is one explicit fact. It quotes the printed identity and
names every physical part. Assembly resolves those exact selectors. It does not
discover continuation from layout or from equal results. A bound fragment-only
table remains a physical record part even without its own identifier or result
column. When a descriptive field spans pages, a field-continuation fact binds its
exact cells and quotes the record identity at its physical page. Successive word
fragments join with whitespace. Every original cell is retained. Qualification
scopes are preserved. Matching headers, or differing values alone, do not
establish a split field.

Overlaps, conflicting bindings, and unsupported splits of identifiers, results,
numbers, dates or within-word characters remain failures. They require source
reading. No generic string concatenation resolves them. An empty printed
placeholder supplies no conflicting field or sampling date. A binding-only block
survives cache replay. Native-cell anchors or exact output row selectors permit
different source layouts and cross-block references. Each cell retains its
physical locator. Each qualification retains its original scope. The reverse
consumer returns every physical part with its observation link.

An unbound, conflicting or overlapping declaration triggers a bounded reread
through the same document reader. An identity-only quotation cites the
identity-bearing physical page. Ambiguous source structure is read as partly
recovered and goes through that reader's page-completion repair. A failure never
authorizes a second semantic extraction path or an invented correspondence. No
reader chooses an identifier namespace, or repairs a digit, from result agreement.
A missing coordinate, an unparsed date or an incomplete metadata component does
not discard a separately readable diagnostic result.

The ordinary loader carries the producer's assembly-complete attestation.
Physical pages read, document relationships read, and record assembly complete
are separate requirements. A failed, pending or unattested assembly retains its
cells, occurrences and independent qualifications. It cannot supply
complete-reading polarity. The attestation is document-wide: an occurrence is not
unaffected by an unresolved continuation merely because its own cells exist.

For native identifier cells, ordinary consumption checks the retained extraction
against the source cell, then reads its coordinate-sorted text. A changed order
is used only when every non-whitespace character is conserved. Original native
text, cell bounds and derivation remain attached. This repairs displaced
punctuation, not identifier origin, and not correspondence between different
codes.

A two-digit year resolves only against a unique matching full year in a scoped
source date statement. The literal date and the supporting statement survive. No
current-year assumption, and no platform century cutoff, supplies the year. A
date spelled with an Italian month name, or its first three letters, resolves the
same way. A parenthesized aside after a date is not part of it. A printed date
range or list constrains a separately stated sampling day and never supplies one.
A row whose only date statement is a range or list has no exact day, and says so.

Extraction permits one to three independent PDF processes under one shared,
transaction-locked spending ledger. Returned usage and an interrupted request are
different states. An explicit retry of an interrupted request retains the full
old reservation and reserves the new attempt separately. It does not claim
invoice reconciliation. No saved successful response is retransmitted. Independent
runners lock the exact request before dispatch and reuse a response the lock
holder has completed. A reader version describes the implementation loaded into
the process, so a cache is not mislabelled if a source file changes during a run.

A reading issue survives both the forward observation link and the reverse
report-row output. A limitation that names an exact table or column locator
attaches to that field. It does not interpret keywords in its cause. At an
identifier column this withholds the typed identity. The literal remains
candidate evidence. An issue whose scope cannot be bound stays visible at report
level. This projection does not certify the remaining role assignments. Unread
report scope leaves the selected result's qualified polarity unknown. Independent
inputs survive. A date-dependent consumer still requires its own date evidence.
The confirmation adapter rejects an ambiguous selection. It does not reject an
otherwise eligible pair only because its sampling date is unknown or other pages
remain unread.

The finding join keeps each diagnostic column and its stated analyte separate,
compares it with the publication label, and names a cause where comparison cannot
be made. Agreement is a cross-check, not a correctness test. Valid contradictory
sampling dates remain conflicts. A dated candidate does not silently displace an
undated one. Repeated physical rows remain available. The reverse view keeps rows
with no observation, negatives included.

Whole-document relationship acquisition supplies every physical page, keeps its
response and request version separate from row extraction, and never
retranscribes the tables. A protocol is a document registration identifier, not
an analytical method and not an incoming delivery note. The source reader assigns
that role. Deterministic projection checks only that the proposed identifier
occurs within its own component quotation. Spelling, prefixes and numeric shape
cannot establish or reject administrative meaning. An unsupported proposal stays
visible and does not acquire a typed identity. An exact cancellation phrase is
not required to read a source-declared cancellation. A correction headed with its
positives does not identify which values changed.

The relationship graph follows explicitly supported replacements, retains history
and unverified components, and rejects ambiguous or cyclic supersession. It
consumes every available relationship inventory, including a document whose
sample rows remain unread. Row materialization is limited to documents reached by
the observation routes and that graph. An unread replacement cannot make its
predecessor eligible. Every competing branch from a rendition's replacement
ancestry must explicitly reach that rendition before it can be current. Extending
one branch cannot settle the fork. The observation's entry route cannot change
that determination. A potential predecessor constrains eligibility: an ambiguous
replacement or an unresolved amendment on that ancestry cannot disappear through
descendants. Possible ancestry never becomes a resolved supersession link.
Source-supported disambiguation, or an explicit whole-report reconciliation, can
remove the competition. The graph is a proposed source reading, not legal
adjudication. It does not turn a cited predecessor date into this rendition's
issue date. A contradictory printed issue date does not erase a named predecessor
and is not an inferred corrected date. Bundled-document identity and amendment
scope require further source resolution when they are not recovered. A
source-review finding can request a fresh relationship reading even after
structural completion. Its instruction and exact request remain. The finding names
what to examine and supplies no replacement answer.

A native administrative association table uses printed header labels and verified
annex continuity: consecutive physical pages or printed folios, and the same
ruled column boundaries. An unresolved fragment survives, without fill-down.
Source boxes map back to the immutable original. The join may derive an
occurrence correspondence from an observation's own report route plus an act's
explicit report number, date, plant reference, and unique matching coordinates.
It preserves competing associations, distinct client codes and source access time.
No positive-result filter selects a plant. It does not equate different literal
identifier strings.
The monitoring publication can supply that explicit report identity and date.
Coordinates are compared at the precision the report prints: the decimals it shows,
in its own CRS as printed, or the association's where it shows fewer. Extra decimals
on the other side are not a conflict. A true disagreement at that precision stays a
conflict. An integer coordinate on either side leaves the comparison unresolved. A transformed
coordinate never acquires an invented printed precision. Derived correspondence
requires complete report-page coverage and uniqueness in both directions,
preserves the source locations, and does not equate distinct field and laboratory
codes. An explicitly printed parenthetical binomial can supply a second host
label. The act's assertion is not backdated to sample collection.

## Implementation rule

Ordinary readers accept source records without a named case, fixed hash, authored
answer, correction allowlist or supported-record registry. Original bytes and
source-native values remain distinguishable from derived values. Conflicting
inputs remain visible to the accepted consumer, and an absence reaching it
carries its cause, under the rule `DESIGN_PRINCIPLES.md` owns. A generic reader
is not a claim that its source population is acquired. A reader that does not yet
meet this rule is named in `state/CURRENT.json`, not on an `INPUTS.md` row.

Research material under `corpus/workbench/` is temporary. At the end of a bounded
unit, a result changes a canonical owner, remains as a directly consumed source
population, or is deleted. Workbench paths, dated investigations and review
packets may not appear in `source-bindings.json`.

## Verification

`verify.py` checks that the A–C projection, contracts and compact source map
agree. It rejects workbench paths and historical evidence fields. Neither the
Stage D suite nor the verifier certifies source meaning or Stage D completion.

## Subscription document transport

`cordon_d.document_subscription.read_documents` sends complete retained PDFs,
including native text and every rendered page, through the authenticated Codex
subscription. The caller supplies ordered source hashes, its prompt and its
strict JSON output schema. An act and separate annexes can form one request
without being forced into a laboratory-report representation. This transport has
no dependency on the laboratory reader and does not dispatch that reader's jobs.

The transport returns a proposed reading, never a completion or a legal-effect
assertion. Source admission, document relationships, qualifications, validation
and publication of accepted readings remain with the calling reader. The caller
exercises its own source-to-consumer contract before a population dispatch.

Execution is explicit. Otherwise only an identical retained request can be
replayed. Request identity includes the source hashes, the actual prompt and
schema, the rendered image hashes, the model, the effort and the transport
version. A lock prevents duplicate dispatch of an identical request. It does not
coordinate different providers, or different tasks, on one document. Raw output,
elapsed call time and provenance stay in the regenerable store. Invalid JSON, or
output that violates the caller's schema, stays retained and cannot become a
returned reading, on execution or on replay. A non-JSON numeric constant, and a
number that overflows to a non-finite floating-point value, are rejected before
validation. Schema validity is checked before dispatch. A schema reference must
resolve within the supplied schema, without network retrieval. A source-review
instruction changes the request. Replay never secretly spends another call.
API-key fallback and model tools are disabled. A bounded subprocess timeout
applies.

The calling reader uses the shared store and retains the request reference beside
its interpreted output. The transport introduces no second source inventory,
scheduler, extraction schema or evidence-acceptance model.

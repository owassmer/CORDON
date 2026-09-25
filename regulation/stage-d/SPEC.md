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
version. `Member.publisher_annotation` keeps a campaign source's literal
annotation and its citation on its own occurrence. It changes no identity or
grouping. An older cache without that reading stays distinguishable from an
absent column or a null value. The grouped distinct-observation stream is Parquet
keyed by the ordered
`(url, view, sha256)` sequence of retained releases, the reader version and the
DuckDB version. Reports are compact JSON blocks and an assembled reading under
source hash and extraction version. A document reading, including a
case-prescription reading, is JSON under the hash of its request, which binds the
source hashes, prompt, schema and model; its reader replays it. The tree holds
neither the reading nor the records derived from it.

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

One real text has one representation. Text from the page's text layer enters
the reading decoded: a text that round-trips Latin-1 to UTF-8 into valid,
different text reads as that text. The text layer prints byte 0xA0, the second
byte of à, as a space, so a space after Ã or Â is read as that byte first. The
retained native cell and the request that showed it are unchanged.

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
discover continuation from layout or from equal results. A transposed table whose
sample columns continue on the next page without printing their identities again
is joined to its first part, its sample columns matched by printed order; the
source reader declares each such continuation. A table part that prints a result
and no sample identity, and that no continuation binds, gets one bounded,
source-only request for the continuations that bind it. The request returns
continuation facts only, and a part the source does not bind keeps its cause. A bound fragment-only
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

A caller may also supply complete native HTML or plain text. Linked assets are not
fetched, so meaning that depends on layout still needs the source views. A
supplemental rotated view keeps the original page and its image provenance.
`read_retained(request_id, store)` validates and replays a named request offline,
without dispatch. A retained request keeps the provider and source presentation
it actually used. Shell, web and agent tools are disabled.

`read_native_text` supplies the complete native text of each PDF, page by page,
through the authenticated Claude subscription in print mode, with tools, MCP
servers, setting sources and session persistence disabled and API-key variables
removed. A page without a native text layer is supplied as that fact; the
calling reader names any limitation it causes. The request records the provider,
the presentation and those pages. Replay, identity and schema checks are those
above.

The calling reader uses the shared store and retains the request reference beside
its interpreted output. The transport introduces no second source inventory,
scheduler, extraction schema or evidence-acceptance model.

## Case-prescription reading

`cordon_d.case_prescriptions` supplies the `case-prescription` input from each
order's own text, under `prescription-reading.txt`, through `read_native_text`.
`scripts/read_prescriptions.py` replays by default and dispatches with
`--execute`. The reading lists the removal work the operative part prescribes to
recipients and every clause stating what follows if they do not begin or perform
it. Every quotation, and every copied field, must occur on the page its citation
names; a field printed across a page break must close one cited page and open the
next. Otherwise the reading is refused. A refused reading gets one source-only
reread whose request states the refusal; a second refusal stands as a named
reading failure. A clause limit is only text in the clause that prevents reading
its term, anchor, commitment, coercive population or executor. A validated first
reading that states a clause limit gets one source-only reread whose request
states the limit and that definition; a limit the reread still states stands.

One record is one enforcement clause over the work it enforces: instrument,
recipients and cohort as printed, the prescribed scope, the commencement work and
population, the stated term as printed (number and unit word, never classified),
its anchor, the stated consequence and commitment, the coercive population with
its back-reference resolved within the same clause, and the executor. Work that
no clause enforces keeps a record without a term. Work an act applies by
reference to another order's prescription stays unknown until `apply_references`
composes it with that order's single clause record: the recipients and scope stay
the referring act's, and the term, populations, executor and governing
references are the referenced order's. Retained copies of one order that read the
same clause are one clause; copies that read it differently leave the work
unknown. An act that prescribes no work to
recipients has no record. Governing A references are every A row of the
instrument and every row whose `corrects_instrument_ids` names it. Annex
positions are not read.

Retained copies compare what they say: case, whitespace, punctuation and articles
aside. A list label the page prints inside a clause (a lettered point, a bullet or
a dash standing alone) does not refuse a copied field that omits it.

The rule's clause predicate holds only for an operative clause with a stated term
running from notification, a committed consequence, a coercive population and an
executor. A clause's own reading limit leaves it unknown. Lawful dueness is the
order's own reading: its operative part prescribes the work to its recipients and
names the population for coercion (`order_dueness`). `lawfully_due` holds that
reading to every governing A row. A held court disposition reaches it from its
publication: an annulment closes the order only for the scope the decision states
(for the applicants, false for a recipient within it, live outside it, and
unknown naming the scope while the recipient is not identified); an interim
suspension with no later disposition of its ricorso, a challenge ended with the
court's stated reason, or a stated correction, replacement, revocation,
suspension or withdrawal, whole or in part, that no A row records, leaves it
unknown and names the act and the words stating what changes. Nothing is patched.
`c_result` passes C only the notice and commencement evidence the caller holds:
the facts of the Art. 21-ter notice branches (the Art. 21-bis communication
predicate, or the mass-publicity row) and each branch's instant, from which C's
`notice_instant` takes the earliest instant among the branches A finds true;
nothing absent is supplied. Publication fills notification only through A's
mass-publicity route.

Supplied Osservatorio records (`osservatorio-records`) reach C per recipient
through `recipient_results` (`read_prescriptions.py --records`), beside the
clause's cohort result, which no supplied record moves. There is one result per
recipient a delivery record names, keyed as that record names them; nothing joins
it to an annex position. A personal-delivery record is the delivery receipt only,
never the acceptance receipt; it enters the communication predicate for its
recipient only. The works a delivery record names are the operator's standing
assertion of what that recipient is obliged to. Commencement and removal count for
the work the record prints (comune, foglio and particella, or a plant identifier)
and for every recipient a supplied record obliges to that work. A recipient's
commencement history is complete only when every work it is obliged to has a
stated history running from the order's adoption, or earlier, through C's
deadline: `clock_boundary` on the notification C's `notice_instant` returns for
that recipient, with the order's stated term, zone and calendar. A history stated
as complete through a moment later than the evaluation is refused. The caller
supplies no instant, order-text predicate or completeness of its own; what it
cannot join is reported. Postings are public records read on PR #15's route, not
supplied records: a recipient reached only by posting has no per-recipient result,
because that needs recipient-to-parcel standing (PR #35's positions or
`party-land-standing`), which is not held.

Stated changes come from every held act that names the order, not only from the
order population. `cordon_d.held_acts` scans every source text A admits. A text
that prints a held order's identity (`printed_identities`: its number closely
followed by its adoption date, at most 12 characters and two words apart with no
number between, or an act designator with its number and year) is read whole under
`act-relationship-reading.txt`, through `read_native_blocks`, one block per
page of the admitted text. The reading lists each act it states it corrects,
supplements, completes, replaces, revokes, suspends or withdraws, whole or in
part, with the words stating what changes; every quotation and copied field must
occur in its cited block. Only an operative statement is a change; a recital
restates.

## Act-specific mass-publicity basis

`cordon_d.notice_routes` supplies the `recipient-notice` field "act-specific
mass-publicity basis" from each order's own text, under
`notice-route-reading.txt`, through `read_native_text`
(`scripts/read_notice_routes.py`). The reading copies, with page citations, each
reason the order gives for reaching its recipients by publicity, marked as a
statement about this act or a restatement of the general rule, and each form of
publicity the order establishes: its words, its period as printed and its stated
effect. Validation and the single stated reread follow the case-prescription
reader. Under Owen's 2026-09-24 ruling the act's own stated ground meets
Art. 21-bis and is not re-judged, so a ground the reading holds about the act
is supplied as stated. A held posting reaches C unresolved, naming what its
completion needs (the stated period and the posting's dates); a restated rule
supplies nothing, and without a stated ground C names its own missing predicate.

## Court-decision events

`cordon_d.judgments` reads retained TAR decisions (GA XML) as their numbered
leaf blocks, under `judgment-event-reading.txt`, through `read_native_blocks`
(`scripts/read_judgments.py`). The reading lists the removal orders the decision
names by number and date, and each dated event it states about one of them, one
kind per event: PEC delivery to a named person, first or last day of a municipal
posting, an owner's request, or the administration's reply. Each event keeps its
block, quotation and whether the court states it or reports a party's claim.
Every quotation and copied field must occur in its cited block. An event's day
must be printed: among the numbers of its printed date (compared as numbers), or,
for a date printed by reference to another ("di pari data"), as a full date in its
cited quotation. A date printed without its day supplies no day. An event attaches
only to an order D holds, as an `AdministrativeEvent` for the person the
decision names; a posting names no recipient. Other events stay unattached with
their cause. Whether a delivery or posting is legally sufficient notice stays
with A.

The same decisions supply `operative-act`'s annulment basis under
`judgment-disposition-reading.txt` (`read_judgments.py --dispositions`). The
reading copies the court's own disposition from its dispositive part and kind,
and, for each order the disposition bears on, its effect (annulled, not annulled,
suspended, suspension refused), its scope as the decision states it (dispositive
words and the reasons' passages), the applicants, the grounds and, for a challenge
ended without a ruling, the court's stated reason. The decision's kind, number,
section, register number and decided and published dates are its own GA
descriptors. A party's claim never fills a disposition. Held appeal indexes are
searched and named with the span they cover; an empty search is not finality.
`liveness_closures` takes, per ricorso, the latest disposition stating an effect.

## Albo postings by printed identity

`cordon_d.albo_postings` (`scripts/read_postings.py`) attaches albo records to an
order only by the identity the record itself prints: number and year, the date
where it prints one (equal to the order's adoption date), and the Osservatorio
fitosanitario as issuer. Bytes, subjects and filenames attach nothing. An OpenWeb
albo register export is read row by row: on a comune's albo a row printing the
order is its posting, with the declared start and end; on the executor's albo a
row is the executor's own act naming the order, dated by the act and kept for what
it states. A row that liquidates aid to owners who "hanno eseguito estirpazione …
adempiendo a prescrizione" is a lead to removal the named recipients performed
(row 11), not an act of removal by the executor; it supplies no C input. An issuer
the export cuts where the field ends ("Osservatorio Fitosanita") is printed. A
row that prints the issuer is read for identities by the same matcher as held acts
(`held_acts.printed_identities`): a number closely followed by a date ("n. 114
del 16/10/2023", "DDS 99 05/08/2024", "60 del 19 luglio 2022") or a designator
with number and year ("DDS 122/2021"). Every identity a row
with the issuer prints is attached or listed unattached with its cause: an order D
does not hold, a date other than the order's adoption date, or a date that is not
a readable date. A JCityGov
detail supplies the declared start; its period end is a retention horizon, so the
interval stays open. An image-only posted document's identity is read from its
page images through the subscription (`posted_identity`). Whether a posting is
notice, or an executor act is execution, stays with A.

## Administrative publication records

`cordon_d.notices` keeps native register declarations, their separate
publication occurrences, dates, offices and original-document routes.
`cordon_d.removal_events` connects them to measure identity and adoption through
explicit act identifiers or acquired document attachments. Incoming protocol,
adoption, publication and recipient effect stay distinct. Identical attached
bytes do not merge publication occurrences and do not prove amendment. An
attachment adapter needs the acquisition record. A future date stays an
unoccurred declaration. A declared posting interval does not prove
uninterrupted posting. A retained complete publication certificate supplies its
own attested interval. An unresolved act identity can be connected through the
acquired certificate and principal routes. Neither record supplies recipient
notification, response, default or performance.

## Protected status

`cordon_d.protection` (`scripts/read_protection.py`) supplies row 9. An affected
plant's candidates are "not a register tree", always, and every entry within d:
the plant's `error_m` as `metric_point` returns it plus the entry's survey batch
bound. The flag decides no identity. A code in the plant's note names an entry only
when it equals, as a number, exactly one survey card in the plant's comune, that
entry lies within d, and no other plant's note prints it; otherwise the identity
stays unknown between the entries within d and "not a register tree". An entry's
survey batch is the survey the recitals of the act that first listed it name for
its group (its label's entries, split by survey date): the survey whose recital
count is within 5% of the group's, or, where none fits, the one survey those
recitals name for a group whose entries print survey dates. One survey is one batch
across every label that carries it. Where the recitals name no survey, the batch is
the label and the entry's survey dates. A batch bound
is the 95th percentile of monitoring residuals: a flagged olive observation and the
listed entry that are each other's nearest, in the same comune, within 50 m, their
distance plus the observation's `error_m`. A pair is dropped only when a code in its
note names another entry (the note-code rule with d the 50 m pairing radius), or
when the entry's batch uses the census tag as its card and the printed tag differs
from the card. A batch with fewer than 20 fixes takes the register-wide bound. Each
note is read, cite-or-abstain, as stating that the plant has monumental
characteristics (any wording that asserts it), not doing so, or unclear (negated,
hedged, a monumental term followed by an identifier, which refers to a tree by its
number and so may name another tree, or naming the term without stating it of the
plant); a negation of the tag or the census does not negate the characteristics. A
measurement is supplied as printed, with `diameter_cm` and `measured_height_cm` read
from its words; a note that names the diameter and yields no value records
"measurement not read"; D compares none. An entry's acts come from the acts'
decisions and history table, never from its label alone; where an act's recitals
name the surveys that together make up exactly its provisional list, each survey is
a batch of that act. The 2011 census check reads its tolerance from the held
capitolato d'oneri and checks the census's own bound; with fewer than 20 census
fixes it is not checked, and the census residuals' own 95th percentile is printed
as information.

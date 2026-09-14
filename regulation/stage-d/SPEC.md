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

Beside the blobs, `derived/` holds regenerable Parquet keyed by blob hash and
reader version: lossless native occurrences and typed readings per blob. It is a
cache, never an owner; a changed reader invalidates it, and deleting it costs
one ingest. DuckDB reads it in process; no spatial predicate or legal reading
moves into SQL.

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

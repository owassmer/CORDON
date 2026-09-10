# Stage D — real inputs for accepted A–C

Stage D connects the accepted legal and computational system to facts the
Osservatorio can actually obtain and use. For every required input it establishes
the source population, record meaning and grain, identity and time relationship,
ordinary reader, and exact unresolved limitation.

The current plain-language input map is `INPUTS.md`. `contracts.json` owns the 27
input kinds. `predicate-contracts.json` and `additional-input-contracts.json` bind
accepted A–C requirements to those kinds. `source-bindings.json` owns the small set
of source routes. `consumer-inventory.json` is a regenerable projection of A–C.

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

## Implementation rule

Ordinary readers accept source records without a named case, fixed hash, authored
answer, correction allowlist or supported-record registry. Original bytes and
source-native values remain distinguishable from derived values. Missing or
conflicting inputs remain visible to the accepted consumer.

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

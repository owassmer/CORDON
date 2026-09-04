#!/usr/bin/env python3
"""Deterministic projections of the Stage B canonical (regulation/stage-b/clocks-and-parameters.json): CSV views and a
generation status. Projection only — the ledger is the authored surface; nothing here decides meaning.

The status carries the integrity metadata the essence ledger must not: the canonical hash, the Stage A input hashes the
ledger was derived from, and the hash of each projection. Its `generated` map is built from the fixed projection set, never
from whatever happens to be in the output directory (review cycle 1, F3-06).
status.semantic_acceptance is NOT_ASSERTED until every non-held closure-manifest entry records an acceptance act.
"""
import csv, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'regulation/stage-b/clocks-and-parameters.json'
OUT = ROOT / 'regulation/stage-b/generated'
# Nothing reads a CSV of the disposition log or the closure manifest — the verifier, the reviewers and this script all
# read the canonical JSON. Two projections generated and never opened; removed (F4 cycle 6).
PROJECTIONS = ('clocks', 'parameters')
STAGE_A = ('regulation/stage-a/authoring-eu.json', 'regulation/jurisdiction/canonical/authoring.json')

def flat(v): return json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list)) else ('' if v is None else str(v))
def write(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow({k: flat(v) for k, v in r.items()})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    b = json.loads(B.read_text(encoding='utf-8'))
    for k in PROJECTIONS: write(OUT / f'{k}.csv', b[k])
    stale = sorted(p.name for p in OUT.glob('*.csv') if p.stem not in PROJECTIONS)
    # An acceptance projects only where the manifest records the act and the reviewer, never from a status string alone
    # (review cycle 2, F3-C2-04). This is a record check; the act's semantic validity is Owen's, on a human reread.
    # With one seam accepted and another open, the honest projection is PARTIAL naming both sets — never a single word
    # that hides either the acceptance or the work still in progress.
    live = [m for m in b['closure_manifest'] if m['status'] != 'HELD']
    acc = [m for m in live if m.get('semantic_acceptance') == 'ACCEPTED' and m.get('acceptance_act') and m.get('semantic_reviewer')]
    accepted = 'ACCEPTED' if live and len(acc) == len(live) else ('PARTIAL' if acc else 'NOT_ASSERTED')
    status = {"status": "PROJECTION_INTEGRITY_PASS", "semantic_acceptance": accepted,
              "accepted_seams": [m['seam'] for m in acc],
              "unaccepted_seams": [m['seam'] for m in b['closure_manifest'] if m not in acc],
              "schema": b['schema'], "canonical_sha256": sha(B),
              "stage_a_inputs": {p: sha(ROOT / p) for p in STAGE_A},
              "counts": {k: len(b[k]) for k in ('clocks', 'parameters', 'dispositions')},
              "generated": {f'{k}.csv': sha(OUT / f'{k}.csv') for k in PROJECTIONS},
              "unrecognized_files_in_output_dir": stale}
    (OUT / 'generation-status.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(status['counts']))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Deterministic projections of the Stage B canonical (regulation/stage-b/clocks-and-parameters.json): CSV views and a
generation status. The verifier's consumer view derives effective dates from Stage A; nothing here decides meaning.

The status carries the integrity metadata the essence ledger must not: the canonical hash, the Stage A and population hashes the
ledger was derived from, and the hash of each projection. Its `generated` map is built from the fixed projection set, never
from whatever happens to be in the output directory (review cycle 1, F3-06).
status.semantic_acceptance is NOT_ASSERTED until every non-held closure-manifest entry records an acceptance act.
"""
import csv, hashlib, json
from pathlib import Path
from verify_stage_b import main as verify_ledger
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'regulation/stage-b/clocks-and-parameters.json'
OUT = ROOT / 'regulation/stage-b/generated'
# Nothing reads a CSV of the disposition log or the closure manifest — the verifier, the reviewers and this script all
# read the canonical JSON. Two projections generated and never opened; removed (F4 cycle 6).
PROJECTIONS = ('clocks', 'parameters')
STAGE_A = ('regulation/stage-a/authoring-eu.json', 'regulation/jurisdiction/canonical/authoring.json')
POPULATION = 'regulation/stage-b/population.json'

def flat(v): return json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list)) else ('' if v is None else str(v))
def write(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow({k: flat(v) for k, v in r.items()})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def status_for(b, canonical, stage_a_paths, population, output, root):
    """Derive the existing status contract from a validated ledger and actual files."""
    stale = sorted(p.name for p in output.glob('*.csv') if p.stem not in PROJECTIONS)
    # The verifier has validated the record, evidence hash, and accepted-content fingerprint.
    # These checks establish a bound record, not the authenticity or wisdom of a human act.
    # With one seam accepted and another open, the honest projection is PARTIAL naming both sets — never a single word
    # that hides either the acceptance or the work still in progress.
    live = [m for m in b['closure_manifest'] if m['status'] != 'HELD']
    acc = [m for m in live if m['semantic_acceptance'] == 'ACCEPTED']
    accepted = 'ACCEPTED' if live and len(acc) == len(live) else ('PARTIAL' if acc else 'NOT_ASSERTED')
    return {"status": "PROJECTION_INTEGRITY_PASS", "semantic_acceptance": accepted,
              "accepted_seams": [m['seam'] for m in acc],
              "unaccepted_seams": [m['seam'] for m in b['closure_manifest'] if m not in acc],
              "schema": b['schema'], "canonical_sha256": sha(canonical),
              "stage_a_inputs": {str(p.relative_to(root)): sha(p) for p in stage_a_paths},
              "population_sha256": sha(population),
              "acceptance_binding": "Stage A inputs, population, conventions, seam rows, and seam dispositions",
              "counts": {k: len(b[k]) for k in ('clocks', 'parameters', 'dispositions')},
              "generated": {f'{k}.csv': sha(output / f'{k}.csv') for k in PROJECTIONS},
              "unrecognized_files_in_output_dir": stale}

def main():
    # Acceptance is validated before any consumer output is written.
    stage_a_paths = tuple(ROOT / p for p in STAGE_A)
    b = verify_ledger(B, stage_a_paths, ROOT / POPULATION)
    OUT.mkdir(exist_ok=True)
    for k in PROJECTIONS: write(OUT / f'{k}.csv', b[k])
    status = status_for(b, B, stage_a_paths, ROOT / POPULATION, OUT, ROOT)
    (OUT / 'generation-status.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(status['counts']))

if __name__ == '__main__':
    main()

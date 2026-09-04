#!/usr/bin/env python3
"""Deterministic CSV projections of the EU canonical (regulation/stage-a/authoring-eu.json).
Projection only: keeps each CSV's existing column set; stable_provision_id is the qualified canonical id."""
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SA = ROOT / 'regulation/stage-a'
rows = json.loads((SA / 'authoring-eu.json').read_text(encoding='utf-8'))

def header(path):
    with path.open(newline='', encoding='utf-8') as f:
        return next(csv.reader(f))

def flat(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else ('' if v is None else str(v))

def write(path, fields, recs):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader()
        for r in recs: w.writerow({k: flat(r.get(k)) for k in fields})

pv_fields = header(SA / 'provision-versions.csv')
write(SA / 'provision-versions.csv', pv_fields, rows)
sp_fields = header(SA / 'stable-provisions.csv')
seen, stable = set(), []
for r in rows:
    if r['stable_provision_id'] in seen: continue
    seen.add(r['stable_provision_id']); stable.append(r)
write(SA / 'stable-provisions.csv', sp_fields, stable)
print({'versions': len(rows), 'stable': len(stable)})

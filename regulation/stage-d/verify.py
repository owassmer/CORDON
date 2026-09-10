"""Verify the compact D owner graph, never semantic sufficiency."""
from pathlib import Path
import json

from inventory import inventory

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'regulation/stage-d'


def verify():
    def read(name):
        return json.loads((D / name).read_text())
    actual = inventory(ROOT)
    if actual != read('consumer-inventory.json'):
        raise ValueError('D consumer projection is stale')
    contracts = read('contracts.json')['contracts']
    ids = {c['id'] for c in contracts}
    if len(ids) != len(contracts):
        raise ValueError('Duplicate contract owner')
    predicates = read('predicate-contracts.json')['bindings']
    if len(predicates) != len(actual['predicates']) or {p['predicate'] for p in predicates} != {p['predicate'] for p in actual['predicates']}:
        raise ValueError('Factual consumer coverage differs from accepted A')
    additional = read('additional-input-contracts.json')
    for family, key in [('declared_evidence', 'evidence'), ('callables', 'consumer')]:
        rows = additional[family]
        if len(rows) != len(actual[family]) or {r[key] for r in rows} != {r[key] for r in actual[family]}:
            raise ValueError(f'Consumer coverage differs: {family}')
    if set(additional['structures']) != {s['consumer'] for s in actual['structures']}:
        raise ValueError('Typed input coverage differs')
    refs = additional['reference_bindings']
    expected = actual['reference_bindings']
    if {(r['consumer'], r['reference']) for r in refs} != {(r['consumer'], r['reference']) for r in expected} or len(refs) != len(expected):
        raise ValueError('Reference evidence coverage differs')
    for rows in [predicates, additional['structures'].values(), *[additional[k] for k in ['declared_evidence', 'callables', 'reference_bindings']]]:
        for row in rows:
            if set(row.get('contracts', [])) - ids:
                raise ValueError('Binding points outside the contract owner')
    sources = read('source-bindings.json')['sources']
    if {c for s in sources for c in s['contracts']} != ids:
        raise ValueError('Contract source-route coverage differs')
    allowed = {'id', 'name', 'purpose', 'contracts', 'routes', 'population', 'reader', 'open'}
    for source in sources:
        if set(source) != allowed:
            raise ValueError(f'Bloated or incomplete source binding: {source.get("id")}')
        if not source['routes'] or not source['contracts']:
            raise ValueError(f'Source binding has no route or input: {source["id"]}')
        serialized = json.dumps(source, ensure_ascii=False)
        if 'corpus/workbench/' in serialized or 'corpus/evidence/stage-d-' in serialized:
            raise ValueError(f'Source binding cites research history: {source["id"]}')
    return {'mechanical_coverage': 'verified',
            'source_routes': len(sources),
            'semantic_sufficiency': 'not certified by this check',
            'stage_complete': False}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))

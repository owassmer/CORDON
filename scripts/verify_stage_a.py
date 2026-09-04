#!/usr/bin/env python3
"""Targeted regression gate for the accepted EU Stage A layer (essence schema).

Canonical: regulation/stage-a/authoring-eu.json (35-field essence schema).
Checks are anchored in source quotes, never in adjudicator prose fields.
This gate protects already-read meaning; it is never acceptance.
"""
import argparse, csv, hashlib, json, re, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SA = ROOT / 'regulation/stage-a'
DEFAULT_AUTHORING = SA / 'authoring-eu.json'

REMOVED_FIELDS = {'verbatim_text', 'semantic_equivalence_key', 'scope_status',
                  'public_observability', 'government_availability', 'clock_rule',
                  'numeric_parameters', 'conjunction', 'conditions',
                  'trigger_expression', 'calculation_support',
                  'required_legal_effect', 'is_latest'}


def fail(msg):
    raise AssertionError(msg)


def q(row):
    return re.sub(r'\s+', ' ', row['source_quote'])


def verify(authoring: Path) -> dict:
    rows = json.loads(authoring.read_text(encoding='utf-8'))
    if len(rows) != 123:
        fail(f'version count {len(rows)} != 123')
    for row in rows:
        if len(row) != 35:
            fail(f"{row['provision_version_id']}: field count {len(row)} != 35")
        present = REMOVED_FIELDS.intersection(row)
        if present:
            fail(f"{row['provision_version_id']}: removed field reintroduced: {sorted(present)[0]}")
        if hashlib.sha256(row['source_quote'].encode()).hexdigest() != row['source_quote_sha256']:
            fail(f"{row['provision_version_id']}: source quote hash mismatch")
        for p in filter(None, row['source_paths'].split(';')):
            if not (ROOT / p).exists():
                fail(f"{row['provision_version_id']}: missing snapshot {p}")
    by = defaultdict(list)
    for row in rows:
        by[row['stable_provision_id']].append(row)
    if len(by) != 99:
        fail(f'stable count {len(by)} != 99')
    for sid, vv in by.items():
        vv.sort(key=lambda r: r['effective_from'])
        if sum(r['temporal_status'] != 'SUPERSEDED' for r in vv) != 1:
            fail(f'{sid}: not exactly one current version')
        for a, b in zip(vv, vv[1:]):
            if a['effective_to_exclusive'] != b['effective_from']:
                fail(f'{sid}: interval gap/overlap')
        if vv[0]['effective_from'] < '2020-08-20':
            fail(f'{sid}: version precedes entry into force')

    def get(sid, vn):
        return next(r for r in by[f'EU-2020-1201:{sid}'] if r['provision_version_id'].endswith(f':{vn}'))

    # quote-anchored semantic regressions
    if '2,5 km' not in get('4(2)(a)', 'v1')['source_quote']:
        fail('4(2)(a) quote lost the 2,5 km eradication buffer')
    if 'at least 50 m around the plant found infected' not in q(get('4(2)-sub1', 'v1')):
        fail('4(2)-sub1 quote lost the 50 m infected-zone radius')
    if 'in plants' not in get('4(1)', 'v2')['source_quote'] or 'in plants' in get('4(1)', 'v1')['source_quote']:
        fail('4(1) v1/v2 in-plants boundary corrupted')
    if json.dumps(get('4(1)', 'v1')['condition_ast']) == json.dumps(get('4(1)', 'v2')['condition_ast']):
        fail('4(1) v1 AST back-projects the v2 in-plants trigger')
    if 'any other plant species' in get('2(1)', 'v1')['source_quote']:
        fail('2(1) v1 quote carries M5 suspicion-species text')
    if 'suspicion' in json.dumps(get('2(1)', 'v1')['condition_ast']):
        fail('2(1) v1 AST back-projects the suspicion-species limb')
    if 'does not yet apply' not in get('2(4)', 'v1')['true_effect'] or '80 %' not in get('2(4)', 'v2')['true_effect']:
        fail('2(4) delayed-application version effects corrupted')
    if '1 January 2023' not in get('2(4)', 'v1')['semantic_note']:
        fail('2(4) v1 lost the Article 38 delayed-application basis')
    if 'does not yet apply' not in get('5(1)(c)', 'v1')['true_effect']:
        fail('5(1)(c) delayed-application version effects corrupted')
    if 'not found free' not in json.dumps(get('7(1)(e)', 'v1')['condition_ast']):
        fail('7(1)(e) v1 AST lost the not-found-free limb')
    if 'not found free' in json.dumps(get('7(1)(e)', 'v2')['condition_ast']):
        fail('7(1)(e) v2 AST carries the repealed limb')
    a73 = json.dumps(get('7(3)', 'v3')['condition_ast'])
    if 'environmental value' not in a73 or 'unacceptable impact' not in a73:
        fail('7(3) v3 AST lost the M5 population limbs')
    if 'environmental value' in json.dumps(get('7(3)', 'v1')['condition_ast']):
        fail('7(3) v1 AST back-projects the M5 population')
    if 'ISPM' not in get('11(1)', 'v2')['source_quote']:
        fail('11(1) quote lost the ISPM standards')
    if get('6(4)', 'v1')['legal_linguistic_conflict'] in ('', '-'):
        fail('6(4) identification/establishment conflict dropped')
    if 'different genome' not in json.dumps(get('2(6)', 'v1')['condition_ast']) \
            and 'different genome' not in q(get('2(6)', 'v1')):
        fail('2(6) second-test genome-target rule lost')
    if 'ARTICLE_13' not in json.dumps(get('13(1)', 'v1')['condition_ast']):
        fail('13(1) discovery-provenance route table lost')
    if '5 km' not in get('15(2)(a)', 'v1')['source_quote'] or '2 km' not in get('15(2)(a)', 'v2')['source_quote']:
        fail('15(2)(a) band-width version boundary corrupted')
    if 'two years' not in q(get('5(4)(a)', 'v1')) or '1 year' not in q(get('5(4)(a)', 'v2')):
        fail('5(4)(a) follow-up-year version boundary corrupted')

    # C/p parity: every numeric confidence/prevalence value a quote states must
    # appear in that row's own effect or AST. Quotes own the figures; the
    # semantic surface must state them explicitly, never a generic phrase.
    for row in rows:
        qn = re.sub(r'\s+', ' ', row['source_quote'])
        if 'confidence' not in qn:
            continue
        surface = row['true_effect'] + json.dumps(row['condition_ast'], ensure_ascii=False)
        for v in set(re.findall(r'(\d+(?:[.,]\d+)?)\s*%', qn)):
            if not re.search(rf'{re.escape(v)}\s*%', surface):
                fail(f"{row['provision_version_id']}: quote states {v} % but effect/AST does not")
    if not re.search(r'0,5\s*%', get('10-sub1', 'v1')['true_effect']):
        fail('10-sub1 lost its 0,5 % prevalence')
    if not re.search(r'0,7\s*%', get('15(2)-final-subparagraph', 'v1')['true_effect']):
        fail('15(2)-final lost its 0,7 % prevalence')
    if '95' not in json.dumps(get('6(2)(b)', 'v1')['condition_ast']):
        fail('6(2)(b) lost its 95 % confidence condition')
    if 'no numeric confidence/prevalence pair' not in get('2(4)', 'v3')['true_effect']:
        fail('2(4) v3 lost the express no-numeric-pair statement')

    # csv projections agree with canonical
    with open(SA / 'provision-versions.csv', newline='', encoding='utf-8') as f:
        pv = list(csv.DictReader(f))
    if len(pv) != 123 or any(fld in pv[0] for fld in REMOVED_FIELDS):
        fail('provision-versions.csv projection out of shape')
    with open(SA / 'stable-provisions.csv', newline='', encoding='utf-8') as f:
        sp = list(csv.DictReader(f))
    if len(sp) != 99 or 'scope_status' in sp[0]:
        fail('stable-provisions.csv projection out of shape')
    return {'stable': len(by), 'versions': len(rows)}


MUTATIONS = [
    ('drop the 50 m radius from 4(2)-sub1',
     lambda rs: [r.update(source_quote=r['source_quote'].replace('50 m', '500 m'),
                          source_quote_sha256=hashlib.sha256(
                              r['source_quote'].replace('50 m', '500 m').encode()).hexdigest())
                 for r in rs if r['provision_version_id'].endswith('4(2)-sub1:v1')]),
    ('back-project in-plants onto 4(1) v1',
     lambda rs: [r.update(condition_ast={'predicate': 'presence officially confirmed in plants'})
                 for r in rs if r['provision_version_id'].endswith('4(1):v1')]),
    ('back-project suspicion species onto 2(1) v1',
     lambda rs: [r.update(condition_ast={'any_of': [{'predicate': 'host plants'},
                                                    {'predicate': 'suspicion species'}]})
                 for r in rs if r['provision_version_id'].endswith('2(1):v1')]),
    ('erase the 2(4) delayed-application boundary',
     lambda rs: [r.update(true_effect='collect samples and test plants for planting')
                 for r in rs if r['provision_version_id'].endswith('2(4):v1')]),
    ('drop the 7(1)(e) v1 not-found-free limb',
     lambda rs: [r.update(condition_ast={'predicate': 'not immediately sampled and tested'})
                 for r in rs if r['provision_version_id'].endswith('7(1)(e):v1')]),
    ('flatten the 7(3) v3 population',
     lambda rs: [r.update(condition_ast={'predicate': 'qualifying value/protection designation'})
                 for r in rs if r['provision_version_id'].endswith('7(3):v3')]),
    ('hide the 6(4) language conflict',
     lambda rs: [r.update(legal_linguistic_conflict='-')
                 for r in rs if r['provision_version_id'].endswith('6(4):v1')]),
    ('drop the 13(1) provenance routes',
     lambda rs: [r.update(condition_ast={'predicate': 'official infection finding'})
                 for r in rs if r['provision_version_id'].endswith('13(1):v1')]),
    ('start law on the publication date',
     lambda rs: [r.update(effective_from='2020-08-17')
                 for r in rs if r['provision_version_id'].endswith('1(a):v1')]),
    ('collapse the 15(2)(a) band versions',
     lambda rs: [r.update(source_quote=r['source_quote'].replace('5 km', '2 km'),
                          source_quote_sha256=hashlib.sha256(
                              r['source_quote'].replace('5 km', '2 km').encode()).hexdigest())
                 for r in rs if r['provision_version_id'].endswith('15(2)(a):v1')]),
    ('strip the 5(1)(c) v2 confidence value',
     lambda rs: [r.update(true_effect=r['true_effect'].replace('90 %', 'high'),
                          condition_ast=json.loads(json.dumps(r['condition_ast']).replace('90 %', 'high')))
                 for r in rs if r['provision_version_id'].endswith('5(1)(c):v2')]),
    ('swap the 10-sub1 prevalence onto the uniform 1 %',
     lambda rs: [r.update(true_effect=r['true_effect'].replace('0,5 %', '1 %'))
                 for r in rs if r['provision_version_id'].endswith('10-sub1:v1')]),
]


def run_mutations(authoring: Path):
    original = json.loads(authoring.read_text(encoding='utf-8'))
    for label, mutate in MUTATIONS:
        mutant = json.loads(json.dumps(original))
        mutate(mutant)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'authoring-eu.json'
            p.write_text(json.dumps(mutant, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            r = subprocess.run([sys.executable, __file__, '--authoring', str(p),
                                '--skip-projections'], capture_output=True, text=True)
            if r.returncode == 0:
                fail(f'mutation was not caught: {label}')
            print(f'PASS MUTATION: {label}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--authoring', type=Path, default=DEFAULT_AUTHORING)
    ap.add_argument('--skip-projections', action='store_true')
    ap.add_argument('--mutation-test', action='store_true')
    args = ap.parse_args()
    global SA
    if args.skip_projections:
        # projection checks read SA; mutation runs verify canonical rules only
        counts_rows = json.loads(args.authoring.read_text(encoding='utf-8'))
    counts = None
    try:
        counts = verify(args.authoring)
    except FileNotFoundError:
        fail('canonical authoring missing')
    print('PASS: Stage A EU essence —', json.dumps(counts, sort_keys=True))
    if args.mutation_test:
        run_mutations(args.authoring)
        print('PASS: all EU mutations were caught')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as e:
        print(f'FAIL: {e}', file=sys.stderr)
        sys.exit(1)

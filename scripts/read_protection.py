#!/usr/bin/env python3
"""Read row 9 (protected status) over the held sources and write its rows to the store's derived folder.

The rows are regenerable, so they stay out of the tree: `derived/protected-status/rows-<version>.json`, where the
version hashes the reader and the acquisition records it reads. Prints the counts a reviewer checks.
"""
import argparse
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-d'), str(ROOT / 'regulation/stage-c')]
from cordon_d import instruments, protection  # noqa: E402
from cordon_d.store import store_root  # noqa: E402


def version() -> str:
    digest = sha256()
    for path in (Path(protection.__file__), Path(instruments.__file__), ROOT / protection.SOURCES / 'register.json',
                 ROOT / protection.SOURCES / 'acts.json', ROOT / protection.ORDERS,
                 ROOT / instruments.SOURCES / 'national-list.json', ROOT / instruments.SOURCES / 'declarations.json',
                 ROOT / instruments.SOURCES / 'proposals.json', ROOT / instruments.SOURCES / 'recognitions.json'):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decision', type=date.fromisoformat, default=date.today(),
                        help='the decision date; the reach runs four years back from it (B-CLK-EU-6(1))')
    args = parser.parse_args()
    store = store_root(ROOT)
    reach = args.decision.replace(year=args.decision.year - 4)
    result = protection.read(store, args.decision, reach)
    out = protection.rows(result)
    target = store / 'derived' / 'protected-status' / f'rows-{version()}.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print('rows:', target)
    print('plants:', dict(Counter((p['kind'], p['candidates']['identity'] if p['candidates']['identity'] in
                                   ('unknown', 'not a register tree') else 'entry') for p in out['plants'])))
    print('zone entries:', dict(Counter(e['layer'] for e in out['zone_entries'])))
    print('reference fixes:', len(out['reference_fixes']), 'dropped:',
          [(f['observation'], f['entry'], f['dropped']) for f in out['reference_fixes'] if f['dropped']])
    print('bounds:', sorted({(b['applies_to'], b['error_m'], b['fixes']) for b in out['bounds'].values()}))
    print('2011 check:', [b['check'] for b in out['bounds'].values() if b['check']])
    print('survey batches:', *out['survey_batches'], sep='\n  ')
    print('unread deletions:', out['unread_deletions'])
    print('note codes:', dict(Counter(c['cause'] for p in out['plants'] for c in p['codes'])))
    held = out['instruments']
    print('national list:', len(held['national_list']['entries']), 'entries,',
          dict(Counter(e['sheet'] for e in held['national_list']['entries'])), 'decrees:',
          len(held['national_list']['decrees']), 'bound:', held['national_list']['bound']['error_m'],
          held['national_list']['bound']['statistic'])
    print('declarations:', len(held['declarations']['declarations']), 'in', len(held['declarations']['versions']),
          'PPTR versions; readings:', dict(Counter(d['reading'] for d in held['declarations']['declarations'])))
    declared = held['declarations']['declarations']
    for route, prefix in (('read from a vision transcription', 'read from the vision transcription'),
                          ('read by OCR until transcribed', 'read by OCR'), ('not read from a transcription', 'not read')):
        print(f'{route}:', sum((d['decree'] or {}).get('read', '').startswith(prefix) for d in declared), 'decrees,',
              sum((d['decree'] or {}).get('scheda_read', '').startswith(prefix) for d in declared), 'schede')
    population = held['declarations']['transcription']['population']
    print('transcription population:', len(population), 'rows,', len({(r['sha256'], r['page']) for r in population}),
          'pages; decrees not found:', sorted(d['code'] for d in declared if 'no decree' in (d['decree'] or {}).get('read', '')),
          '; OCR engine (locator):', held['declarations']['ocr']['engine'])
    print('proposals:', [(p['proposal'], p['proposer'], p['reading'], p['first_publication'], p['outcome'].get('kind'))
                         for p in held['proposals']['proposals']])
    print('proposal routes not reached:', held['proposals']['not_reached'])
    print('instrument problems:', held['problems'])
    print('in a zone:', [(r['plant'], r['instrument']) for r in held['in_zone']])
    print('groups:', [(g['scheda'], g['nearest_positive_m']) for g in held['groups']])
    print('distances:', json.dumps(held['distances'], ensure_ascii=False))
    print('status:', {kind: dict(Counter(str(p['status'][kind]['value']) for p in out['plants'] if p['status']))
                      for kind in (instruments.NATIONAL, instruments.DECLARATION, instruments.PROPOSAL)})

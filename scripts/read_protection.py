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
from cordon_d import protection  # noqa: E402
from cordon_d.store import store_root  # noqa: E402


def version() -> str:
    digest = sha256()
    for path in (Path(protection.__file__), ROOT / protection.SOURCES / 'register.json',
                 ROOT / protection.SOURCES / 'acts.json', ROOT / protection.SOURCES / protection.PARCELS,
                 ROOT / protection.ORDERS):
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
    print('unread deletions:', out['unread_deletions'])
    print('note codes:', dict(Counter(c['cause'] for p in out['plants'] for c in p['codes'])))
    print('gross-error screen:', json.dumps(out['gross_error_screen']['counts']))

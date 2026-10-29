#!/usr/bin/env python3
"""Read row 9 (protected status) over the held sources and write its rows to the store's derived folder.

The rows are regenerable, so they stay out of the tree: `derived/protected-status/rows-<version>.json`, where the
version hashes the reader and the acquisition records it reads. Prints the counts a reviewer checks.

`--records` is the Osservatorio's landscape records (a JSON list, the kinds `case_prescriptions.LANDSCAPE_KINDS`
names). Row 9 decides each plant's identity from them as well (`protection.named_rows`). They are controlled sources:
the run states its decision date, its knowledge cutoff (`--known-through`) and its grant
(`--permitted-controlled-sources`, stated even when empty), and the rows they give belong to the run: they go to
stdout or to `--out`, never to the shared rows file.
"""
import argparse
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-d'), str(ROOT / 'regulation/stage-c')]
from cordon_d import protection  # noqa: E402
from cordon_d.case_prescriptions import admitted_records  # noqa: E402
from cordon_d.evidence import run_instant  # noqa: E402
from cordon_d.store import store_root  # noqa: E402

ZONE = ZoneInfo('Europe/Rome')


def version() -> str:
    digest = sha256()
    for path in (Path(protection.__file__), ROOT / protection.SOURCES / 'register.json',
                 ROOT / protection.SOURCES / 'acts.json', ROOT / protection.ORDERS):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decision', type=date.fromisoformat,
                        help='the decision date; the reach runs four years back from it (B-CLK-EU-6(1)); without '
                             '--records, today where not stated')
    parser.add_argument('--records', help="the Osservatorio's landscape records (a JSON list)")
    parser.add_argument('--known-through', type=run_instant,
                        help="with --records: the knowledge cutoff, a timezone-aware ISO instant")
    parser.add_argument('--permitted-controlled-sources', nargs='*', metavar='SOURCE',
                        help='with --records: the controlled source identities the running principal is granted (state '
                             'it even when empty)')
    parser.add_argument('--out', help="with --records: the run's rows file (default: stdout)")
    args = parser.parse_args(argv)
    run = {'--decision': args.decision, '--known-through': args.known_through,
           '--permitted-controlled-sources': args.permitted_controlled_sources}
    if args.records:
        missing = [flag for flag, value in run.items() if value is None]
        if missing:
            parser.error(f'--records needs the run stated: {", ".join(missing)}')
    elif args.known_through is not None or args.permitted_controlled_sources is not None or args.out:
        parser.error('--known-through, --permitted-controlled-sources and --out belong to a run with --records')
    return parser, args


def shared(store: Path) -> Path:
    return store / 'derived' / 'protected-status'


def main(argv=None):
    parser, args = arguments(argv)
    store = store_root(ROOT)
    supplied = None
    if args.records:
        if args.out and Path(args.out).resolve().is_relative_to(shared(store).resolve()):
            parser.error(f"a run's rows never go to the shared rows folder {shared(store)}")
        supplied = json.loads(Path(args.records).read_text())
        grant = frozenset(args.permitted_controlled_sources)
        # Refused before the store is read: a record dated after the cutoff refuses the set.
        admitted_records(supplied, None, evaluated_at=args.known_through, permitted_controlled_sources=grant,
                         zone=ZONE, family='landscape')
    decision = args.decision or date.today()
    reach = decision.replace(year=decision.year - 4)
    result = protection.read(store, decision, reach)
    out = protection.rows(result)
    if supplied is not None:
        bounds, batches = result['bounds'], result['batches']
        out = protection.named_rows(out, list(result['entries'].values()), supplied,
                                    evaluated_at=args.known_through, permitted_controlled_sources=grant, zone=ZONE,
                                    bound_of=lambda oid: bounds[batches[oid]].error_m if oid in batches else None)
        out['run'] = {'decision': decision.isoformat(), 'known_through': args.known_through.isoformat(),
                      'permitted_controlled_sources': sorted(grant),
                      'fixture': any(bool(r.get('fixture')) for r in supplied)}
        text = json.dumps(out, ensure_ascii=False, indent=1)
        if not args.out:
            print(text)
            return
        Path(args.out).write_text(text)
        print('rows:', args.out)
        print('named:', dict(Counter(n['cause'] for n in out['naming_records'])), 'ungranted:', len(out['ungranted']))
    else:
        target = shared(store) / f'rows-{version()}.json'
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


if __name__ == '__main__':
    main()

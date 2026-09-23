#!/usr/bin/env python3
"""Read dated order events from retained TAR decisions (GA XML) and attach them to held orders.

Replays retained readings by default; `--execute` dispatches the missing reads,
one at a time, through the Claude subscription. `--orders` is a results file
written by `read_prescriptions.py --out`: the orders D holds, by instrument.
`--out` writes events, unattached events with their cause, and failures as JSON
outside the tree; nothing here is an owner.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d'), str(ROOT / 'scripts')]

from cordon_d.judgments import CONTRACT, judgment_events, read_judgment  # noqa: E402
from cordon_d.store import store_root  # noqa: E402
from read_prescriptions import _wait_for_memory, _write  # noqa: E402


def decisions():
    """Every retained decision text the removal-event source map holds, once each."""
    records = json.loads((ROOT / 'corpus/sources/removal-events/records.json').read_text())
    seen = set()
    for record in records:
        digest = record.get('sha256')
        if (record['kind'] == 'event' and digest and digest not in seen
                and record['url'].split('/')[2] == 'mdp.giustizia-amministrativa.it'):
            seen.add(digest)
            yield digest, record['url']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--orders', required=True)
    parser.add_argument('--only', nargs='*', default=())
    parser.add_argument('--out')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--workers', type=int, default=1,
                        help='decisions read at once; each is still one bounded request')
    arguments = parser.parse_args()
    if arguments.workers < 1:
        parser.error('--workers must be at least 1')
    held = frozenset(r['instrument'] for e in json.loads(Path(arguments.orders).read_text())
                     for r in e.get('records', ()))
    selected = [(digest, url) for digest, url in decisions()
                if not arguments.only or any(digest.startswith(o) or o in url for o in arguments.only)]
    options = dict(execute=arguments.execute, timeout=arguments.timeout)
    done = {}

    def finished(index, entry):
        done[index] = entry
        print(json.dumps(dict(source=entry['source'][:12], cause=entry.get('cause'),
                              events=len(entry.get('events', ())),
                              unattached=len(entry.get('unattached', ())))), flush=True)
        _write(arguments.out, [done[i] for i in sorted(done)])

    if arguments.workers == 1:
        for index, item in enumerate(selected):
            finished(index, read_one(item, options, held))
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=arguments.workers) as pool:
            futures = {pool.submit(read_one, item, options, held): index for index, item in enumerate(selected)}
            for future in as_completed(futures):
                finished(futures[future], future.result())


def read_one(item, options, held):
    """One decision: replay or one bounded request; a refusal gets one stated reread."""
    digest, url = item
    store = store_root(ROOT)
    if options['execute']:
        _wait_for_memory()
    entry = dict(source=digest, url=url)
    try:
        try:
            response = read_judgment(digest, store, **options)
        except ValueError as refusal:
            entry['refused_first'] = str(refusal)
            response = read_judgment(digest, store, refused=str(refusal), **options)
        attached, unattached = judgment_events(response, held_instruments=held)
        entry.update(request_sha256=response['request_sha256'], orders=response['reading']['orders'],
                     issues=response['reading']['issues'], unattached=list(unattached),
                     events=[dict(identity=e.identity, kind=e.kind, contract=CONTRACT[e.kind],
                                  document=e.document, recipient=e.recipient,
                                  occurred=e.occurred.isoformat(), selector=e.support.selector,
                                  support=e.support.reading) for e in attached])
    except FileNotFoundError:
        entry['cause'] = 'no retained reading'
    except Exception as error:  # a failed read is an execution failure, not source silence
        entry['cause'] = f'{type(error).__name__}: {error}'[:600]
    return entry


if __name__ == '__main__':
    main()

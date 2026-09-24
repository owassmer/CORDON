#!/usr/bin/env python3
"""Read dated order events from retained TAR decisions (GA XML) and attach them to held orders.

Replays retained readings by default; `--execute` dispatches the missing reads,
one at a time, through the Claude subscription. `--orders` is a results file
written by `read_prescriptions.py --out`: the orders D holds, by instrument.
`--out` writes events, unattached events with their cause, and failures as JSON
outside the tree; nothing here is an owner.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d'), str(ROOT / 'scripts')]

from cordon_d.judgments import (CONTRACT, annulment_basis, decision_identity, judgment_events,  # noqa: E402
                                liveness_closures, read_disposition, read_judgment)
from cordon_d.store import blob_path, store_root  # noqa: E402
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
    parser.add_argument('--dispositions', action='store_true',
                        help="read each decision's own disposition (operative-act annulment basis) instead of events")
    parser.add_argument('--appeal-index', nargs='*', default=(),
                        help='held Consiglio di Stato GA index CSVs searched for appeals')
    arguments = parser.parse_args()
    if arguments.workers < 1:
        parser.error('--workers must be at least 1')
    held = frozenset(r['instrument'] for e in json.loads(Path(arguments.orders).read_text())
                     if isinstance(e, dict) for r in e.get('records', ()))
    selected = [(digest, url) for digest, url in decisions()
                if not arguments.only or any(digest.startswith(o) or o in url for o in arguments.only)]
    options = dict(execute=arguments.execute, timeout=arguments.timeout)
    done = {}
    if arguments.dispositions:
        appeals = appeal_search(arguments.appeal_index)
        work, extra = read_disposition_one, (held, appeals)
    else:
        work, extra = read_one, (held,)

    def finished(index, entry):
        done[index] = entry
        print(json.dumps(dict(source=entry['source'][:12], cause=entry.get('cause'),
                              events=len(entry.get('events', entry.get('basis', ()))),
                              unattached=len(entry.get('unattached', ())))), flush=True)
        _write(arguments.out, [done[i] for i in sorted(done)])

    if arguments.workers == 1:
        for index, item in enumerate(selected):
            finished(index, work(item, options, *extra))
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=arguments.workers) as pool:
            futures = {pool.submit(work, item, options, *extra): index for index, item in enumerate(selected)}
            for future in as_completed(futures):
                finished(futures[future], future.result())
    if arguments.dispositions:
        results = [done[i] for i in sorted(done)]
        closures = liveness_closures([b for e in results for b in e.get('basis', ())])
        results.append(dict(appeal_search=appeals, liveness_closures=closures))
        _write(arguments.out, results)


SUBJECT = re.compile(r'XYLELL|\bOLIV[IOE]\b|\bULIV|FITOSANITAR|ESTIRPA', re.I)


def appeal_search(paths):
    """Consiglio di Stato entries in the held GA indexes whose subject names Xylella, olives or plant health.

    The result states which indexes were searched and the publication span they
    cover; an empty result is that search's result, not finality.
    """
    indexes, matches = [], []
    for path in paths:
        data = Path(path).read_bytes()
        rows = list(csv.DictReader(io.StringIO(data.decode('utf-8', errors='replace'))))
        days = sorted(r['DATA_PUBBLICAZIONE'] for r in rows if r.get('DATA_PUBBLICAZIONE'))
        indexes.append(dict(file=Path(path).name, sha256=hashlib.sha256(data).hexdigest(), rows=len(rows),
                            published_from=days[0] if days else None, published_to=days[-1] if days else None))
        matches += [dict(index=Path(path).name, **{k: r[k] for k in (
            'TIPO_PROVVEDIMENTO', 'NUMERO_PROVVEDIMENTO', 'NUMERO_RICORSO', 'DATA_PUBBLICAZIONE',
            'ESITO_PROVVEDIMENTO', 'OGGETTO_RICORSO', 'TIPO_RICORSO')})
                    for r in rows if SUBJECT.search(r.get('OGGETTO_RICORSO', '')) and 'APPELLO' in r.get('TIPO_RICORSO', '')]
    return dict(indexes=indexes, subject_pattern=SUBJECT.pattern, matches=matches)


def read_disposition_one(item, options, held, appeals):
    """One decision's own disposition: replay or one bounded request; a refusal gets one stated reread."""
    digest, url = item
    store = store_root(ROOT)
    if options['execute']:
        _wait_for_memory()
    entry = dict(source=digest, url=url)
    try:
        identity = decision_identity(blob_path(store, digest).read_bytes())
        entry['decision'] = identity
        try:
            response = read_disposition(digest, store, **options)
        except ValueError as refusal:
            entry['refused_first'] = str(refusal)
            response = read_disposition(digest, store, refused=str(refusal), **options)
        attached, unattached = annulment_basis(response, identity, held_instruments=held, appeals=appeals)
        entry.update(request_sha256=response['request_sha256'], outcome=response['reading']['outcome'],
                     issues=response['reading']['issues'], basis=attached, unattached=unattached)
    except FileNotFoundError:
        entry['cause'] = 'no retained reading'
    except Exception as error:  # a failed read is an execution failure, not source silence
        entry['cause'] = f'{type(error).__name__}: {error}'[:600]
    return entry


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

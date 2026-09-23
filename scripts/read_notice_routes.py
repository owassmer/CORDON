#!/usr/bin/env python3
"""Read each retained removal order's own mass-publicity basis for `recipient-notice`.

Replays retained readings by default; `--execute` dispatches the missing reads,
one at a time, through the Claude subscription. `--only` selects act identities
(NUMBER/YEAR) or source hashes. `--out` writes the bases and C's Art. 21-bis
results as JSON outside the tree; nothing here is an owner.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d'), str(ROOT / 'scripts')]

from cordon_c.core import Snapshot  # noqa: E402
from cordon_d.case_prescriptions import read_prescription  # noqa: E402
from cordon_d.notice_routes import c_result, mass_publicity_basis, read_notice_route  # noqa: E402
from cordon_d.store import store_root  # noqa: E402
from read_prescriptions import _wait_for_memory, _write, population, summary  # noqa: E402


def instrument_of(digest, store):
    """The act identity the retained prescription reading of the same source states, if any."""
    try:
        return read_prescription(digest, store).instrument
    except Exception:  # no validated reading or no Osservatorio identity: keep the printed identity
        return None


_WORKER = {}


def _start_worker():
    _WORKER.update(store=store_root(ROOT), snapshot=Snapshot.load(ROOT))


def read_one(item, options, today):
    """One source: replay or one bounded request; a refusal gets one stated reread."""
    identity, digest, url = item
    store, snapshot = _WORKER['store'], _WORKER['snapshot']
    if options['execute']:
        _wait_for_memory()
    entry = dict(printed_identity=identity, source=digest, url=url)
    try:
        try:
            response = read_notice_route(digest, store, **options)
        except ValueError as refusal:
            entry['refused_first'] = str(refusal)
            response = read_notice_route(digest, store, refused=str(refusal), **options)
        basis = mass_publicity_basis(response, instrument=instrument_of(digest, store) or identity)
        entry.update(basis=basis, c=summary(c_result(snapshot, basis, today)))
    except FileNotFoundError:
        entry['cause'] = 'no retained reading'
    except Exception as error:  # a failed read is an execution failure, not source silence
        entry['cause'] = f'{type(error).__name__}: {error}'[:600]
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--only', nargs='*', default=())
    parser.add_argument('--out')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--model', default='opus')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--workers', type=int, default=1,
                        help='sources read at once; each is still one bounded request')
    arguments = parser.parse_args()
    if arguments.workers < 1:
        parser.error('--workers must be at least 1')
    _start_worker()
    today = date.today()
    selected = [item for item in population()
                if not arguments.only or item[0] in arguments.only or item[1] in arguments.only]
    options = dict(execute=arguments.execute, model=arguments.model, effort=arguments.effort,
                   timeout=arguments.timeout)
    done = {}

    def finished(index, entry):
        done[index] = entry
        print(json.dumps(dict(identity=entry['printed_identity'], source=entry['source'][:12],
                              cause=entry.get('cause'),
                              ground=len(entry.get('basis', {}).get('stated_ground', ())),
                              forms=len(entry.get('basis', {}).get('forms', ())))), flush=True)
        _write(arguments.out, [done[i] for i in sorted(done)])

    if arguments.workers == 1:
        for index, item in enumerate(selected):
            finished(index, read_one(item, options, today))
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=arguments.workers, initializer=_start_worker) as pool:
            futures = {pool.submit(read_one, item, options, today): index
                       for index, item in enumerate(selected)}
            for future in as_completed(futures):
                finished(futures[future], future.result())


if __name__ == '__main__':
    main()

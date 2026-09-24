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


def _start_worker(postings=None, records=None):
    _WORKER.update(store=store_root(ROOT), snapshot=Snapshot.load(ROOT), postings=postings or {},
                   records=records or {})


def supplied_posting_results(snapshot, basis, at, supplied):
    """A's Art. 21-bis row for each supplied posting record of this order, with the order's own basis.

    Only posting records are read here; deliveries and performance reach C per
    recipient through `read_prescriptions.py --records`. The court fact on the stated
    ground is not held, so it stays unknown and is named.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from cordon_c.core import evaluate
    from cordon_d.case_prescriptions import MASS, supplied_publicity, supplied_records
    zone = ZoneInfo('Europe/Rome')
    evaluated_at = datetime.now(zone)
    out = []
    for record in supplied_records([r for r in supplied if r.get('kind') == 'posting']):
        facts, day = supplied_publicity(snapshot, at, basis, record, annulled=None, evaluated_at=evaluated_at,
                                        zone=zone)
        out.append(dict(record=record['record'], fixture=record['fixture'], notice_day=day,
                        c=summary(evaluate(snapshot, MASS, at, facts))))
    return out


POSTING_KINDS = {'municipal-publication-start': 'start', 'municipal-publication-end': 'end',
                 'regional-publication-start': 'start', 'regional-publication-end': 'end'}


def load_postings(paths):
    """Held posting intervals by instrument, from the outputs of the event readers.

    Accepts `read_prescriptions.py --events` (existing albo readers), `read_judgments.py`
    (postings a court decision states) and `read_postings.py` (albo registers and posted
    documents). A start and an end pair when they come from the same source record.
    An interval whose end is not held stays open.
    """
    intervals = {}

    def add(instrument, publisher, key, part, day, source):
        slot = intervals.setdefault(instrument, {}).setdefault((publisher, key), dict(
            publisher=publisher, start=None, end=None, sources=set()))
        slot[part] = day
        slot['sources'].add(source)

    for path in paths:
        data = json.loads(Path(path).read_text())
        if isinstance(data, dict) and 'events' in data:  # read_postings.py
            for instrument, events in data['events'].items():
                for event in events:
                    if event['kind'] in POSTING_KINDS:
                        add(instrument, event['publisher'], event['source'], POSTING_KINDS[event['kind']],
                            event['occurred'], event['source'])
            continue
        for entry in data:
            if not isinstance(entry, dict):
                continue
            for event in entry.get('held_events', ()):  # read_prescriptions.py --events
                if event['kind'] in POSTING_KINDS:
                    instrument = next((r['instrument'] for r in entry.get('records', ())), None)
                    if instrument:
                        add(instrument, event['publisher'], event['source'], POSTING_KINDS[event['kind']],
                            event['occurred'], event['source'])
            for event in entry.get('events', ()):  # read_judgments.py
                if event['kind'] in POSTING_KINDS:
                    add(event['document'], f"as TAR decision {entry['source'][:12]} states",
                        (entry['source'], event['selector']),
                        POSTING_KINDS[event['kind']], event['occurred'], entry['source'])
    return {instrument: [dict(v, sources=sorted(v['sources'])) for v in slots.values() if v['start']]
            for instrument, slots in intervals.items()}


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
        postings = _WORKER['postings'].get(basis['instrument'], [])
        entry.update(basis=basis, postings=postings, c=summary(c_result(snapshot, basis, today, postings=postings)))
        supplied = _WORKER['records'].get(basis['instrument'], ())
        if supplied:
            entry['supplied_postings'] = supplied_posting_results(snapshot, basis, today, supplied)
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
    parser.add_argument('--postings', nargs='*', default=(),
                        help='event-reader outputs whose posting intervals reach C as held postings')
    parser.add_argument('--records', help='supplied Osservatorio records (a JSON list); their postings reach '
                                          "A's mass-publicity row with the order's own basis")
    arguments = parser.parse_args()
    if arguments.workers < 1:
        parser.error('--workers must be at least 1')
    postings = load_postings(arguments.postings)
    records = {}
    for item in json.loads(Path(arguments.records).read_text()) if arguments.records else ():
        records.setdefault(item.get('order'), []).append(item)
    _start_worker(postings, records)
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
        with ProcessPoolExecutor(max_workers=arguments.workers, initializer=_start_worker,
                                 initargs=(postings, records)) as pool:
            futures = {pool.submit(read_one, item, options, today): index
                       for index, item in enumerate(selected)}
            for future in as_completed(futures):
                finished(futures[future], future.result())


if __name__ == '__main__':
    main()

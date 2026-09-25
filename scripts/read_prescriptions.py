#!/usr/bin/env python3
"""Read `case-prescription` records for retained removal-order originals.

Replays retained readings by default; `--execute` dispatches the missing reads,
one at a time, through the Claude subscription. `--only` selects act identities
(NUMBER/YEAR) or source hashes. `--out` writes the records and C results as JSON
outside the tree; nothing here is an owner.
"""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]

from cordon_c.core import MissingInput, Snapshot  # noqa: E402
from cordon_d.case_prescriptions import (apply_references, c_result, read_prescription,  # noqa: E402
                                         stated_limits)
from cordon_d.evidence import run_instant  # noqa: E402
from cordon_d.removal_events import act_id  # noqa: E402
from cordon_d.store import store_root  # noqa: E402


def printed_identity(record):
    for text in (record.get('retained_original') or '', record['url']):
        match = re.search(r'(?:DET|DDS)[-_](\d+)[-_](?:\d+[-_]\d+[-_])?(\d{4})', text)
        if match:
            return f'{match.group(1)}/{match.group(2)}'
        match = re.search(r'181_DIR_(\d{4})_0*(\d+)', text)
        if match:
            return f'{match.group(2)}/{match.group(1)}'
    return None


def population(known_through):
    """Every retained original the removal-order source map had captured by the run's knowledge
    cutoff (`captured_at <= known_through`, as `cordon_d.reports.reports` admits reports), in its
    own order."""
    records = json.loads((ROOT / 'corpus/sources/removal-orders/records.json').read_text())
    seen = set()
    for record in records:
        digest = record.get('sha256')
        if digest and digest not in seen and datetime.fromisoformat(record['captured_at']) <= known_through:
            seen.add(digest)
            yield printed_identity(record), digest, record['url']


def held_sources(known_through):
    """Source digests the removal-order and removal-event source maps had captured by the cutoff."""
    held = set()
    for name in ('removal-orders', 'removal-events'):
        for record in json.loads((ROOT / f'corpus/sources/{name}/records.json').read_text()):
            if record.get('sha256') and datetime.fromisoformat(record['captured_at']) <= known_through:
                held.add(record['sha256'])
    return frozenset(held)


def admitted_at(paths):
    """When the repository came to hold each A-admitted text: the latest commit that added it.

    An admitted text has no acquisition record of its own; the commit that added it is
    the latest moment the corpus can have come to hold it. A path git cannot date is absent.
    """
    import subprocess
    paths = sorted(paths)
    if not paths:
        return {}
    try:
        log = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%x01%cI', '--name-only', '--', *paths],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    added = {}
    for block in log.split('\x01')[1:]:
        lines = [line for line in block.splitlines() if line.strip()]
        for path in lines[1:]:
            added.setdefault(path, datetime.fromisoformat(lines[0]))  # newest first: the latest add
    return added


def _wait_for_memory(floor=20):
    """Dispatch a read only while at least `floor` percent of memory is free."""
    import subprocess
    import time
    while True:
        try:
            report = subprocess.run(['memory_pressure', '-Q'], capture_output=True, text=True).stdout
        except FileNotFoundError:
            return
        match = re.search(r'(\d+)%', report.strip().splitlines()[-1] if report.strip() else '')
        if not match or int(match.group(1)) >= floor:
            return
        time.sleep(60)


def held_events(measures, store, known_through):
    """Events the existing publication readers connect to these orders, by instrument.

    Each publisher's retained register is read by its own existing reader. None of
    these events is recipient notification, commencement or removal. Only captures
    made by the run's knowledge cutoff are read.
    """
    from types import SimpleNamespace
    from cordon_d.removal_events import (connect_publication_attestation, connected_publications,
                                         domino_publication, parsec_publications, publication_records,
                                         regional_publication, retained_publication_attestation)
    from cordon_d.store import blob_path

    def held(records):
        return [r for r in records if datetime.fromisoformat(r['captured_at']) <= known_through]
    captures = held(json.loads((ROOT / 'corpus/sources/removal-events/records.json').read_text()))
    acquisitions = held(json.loads((ROOT / 'corpus/sources/removal-orders/records.json').read_text())) + captures
    captured = {r['sha256'] for r in acquisitions if r.get('sha256')}
    measures = [SimpleNamespace(identity=m['instrument'], adopted=date.fromisoformat(m['adopted']),
                                response={'request': {'sources': [m['source']]}}) for m in measures]
    publications, failures = [], []
    for capture in captures:
        digest, host = capture.get('sha256'), capture['url'].split('/')[2].split(':')[0]
        if capture['kind'] != 'publication' or not digest:
            continue
        path = blob_path(store, digest)
        try:
            if host == 'www.comune.capurso.bari.it':
                publications += list(publication_records(path))
            elif host == 'albonline.regione.puglia.it':
                publications.append(regional_publication(path))
            elif host == 'trasparenza.parsec326.it' and 'p_p_id=pubblicazionionline' in capture['url']:
                publications += list(parsec_publications(
                    path, publisher='Comune di Cagnano Varano', measures=measures, acquisitions=acquisitions,
                    source_url='https://trasparenza.parsec326.it/en/widget/web/cagnano-varano/albo-pretorio'))
            elif host == 'albo.comune.bari.it' and '/ProvvedimentiWEB/' in capture['url']:
                publications.append(domino_publication(path, publisher='Comune di Bari', measures=measures,
                                                       acquisitions=acquisitions,
                                                       source_url='https://albo.comune.bari.it/'))
        except Exception as error:
            failures.append(dict(source=digest, url=capture['url'], cause=f'{type(error).__name__}: {error}'[:300]))
    declarations = [p for p in publications if p.publisher == 'Comune di Bari']
    for path in sorted((store / 'derived/document-readings').glob('*.json')):
        response = json.loads(path.read_text())
        if 'publication certificate' not in response['request'].get('prompt', '')[:200]:
            continue
        sources = set(response['request'].get('sources') or ())
        if not sources or not sources <= captured:
            continue  # a certificate not captured by the cutoff was not yet held
        try:
            attestation = retained_publication_attestation(path.stem, store)
            publications.append(connect_publication_attestation(attestation, declarations,
                                                                acquisitions=acquisitions))
        except Exception as error:
            failures.append(dict(source=path.stem, cause=f'{type(error).__name__}: {error}'[:300]))
    by_instrument = {}
    for publication in connected_publications(publications, measures):
        for event in publication.events:
            by_instrument.setdefault(publication.document, []).append(dict(
                kind=event.kind, occurred=event.occurred.isoformat(), publisher=publication.publisher,
                source=event.support.source, selector=event.support.selector))
    return by_instrument, failures


def load_closures(path):
    """Liveness closures by instrument from a `read_judgments.py --dispositions` output file."""
    if not path:
        return {}
    closures = next((e['liveness_closures'] for e in json.loads(Path(path).read_text())
                     if 'liveness_closures' in e), {})
    return {instrument: [dict(c, since=date.fromisoformat(c['since']) if c['since'] else None) for c in items]
            for instrument, items in closures.items()}


def stated_changes(results):
    """Every relationship a read order states toward another order, by the order it names."""
    changes = {}
    for entry in results:
        source = entry.get('identity') or {}
        try:
            origin = act_id(re.sub(r'\D', '', source.get('number') or ''), (source.get('adopted') or '')[:4])
        except Exception:
            origin = entry.get('printed_identity')
        for item in entry.get('relationships', ()):
            target = act_id(re.sub(r'\D', '', item['number']), item['year'])
            if target != origin:
                changes.setdefault(target, []).append(dict(
                    {'from': origin}, relationship=item['relationship'],
                    affected_payload=item['affected_payload'], source=entry['source']))
    return changes


def held_orders(results):
    """Instrument to adoption date for every read order whose own reading states its identity."""
    orders = {}
    for entry in results:
        identity = entry.get('identity') or {}
        digits = re.sub(r'\D', '', identity.get('number') or '')
        if identity.get('authority') == 'puglia-osservatorio' and digits and identity.get('adopted'):
            orders[act_id(digits, identity['adopted'][:4])] = identity['adopted']
    return orders


def held_act_changes(results, snapshot, store, options, known_through):
    """Changes the other held acts state to these orders (`cordon_d.held_acts`), by the order they name.

    Every A-admitted source outside the order population whose text prints a held
    order's identity is read whole, one bounded request each (replayed unless
    `--execute`), when the repository held it by the run's knowledge cutoff
    (`admitted_at`). Returns (changes by order, report).
    """
    from cordon_d import held_acts
    chosen, scanned = held_acts.selected(snapshot, ROOT, held_orders(results))
    added = admitted_at(item['path'] for item in chosen)
    after = [dict(item, admitted_at=added[item['path']].isoformat() if item['path'] in added else None)
             for item in chosen if item['path'] not in added or added[item['path']] > known_through]
    chosen = [item for item in chosen if item['path'] in added and added[item['path']] <= known_through]
    changes, report = {}, dict(scanned=scanned, selected=[], failures=[], not_held_by_cutoff=after)
    for item in chosen:
        if options['execute']:
            _wait_for_memory()
        try:
            response = held_acts.read_act(item['path'], ROOT, store, **options)
        except FileNotFoundError:
            report['failures'].append(dict(item, cause='no retained reading'))
            continue
        except Exception as error:  # a failed read is an execution failure, not source silence
            report['failures'].append(dict(item, cause=f'{type(error).__name__}: {error}'[:600]))
            continue
        stated = list(held_acts.stated_changes(response, item['instruments'], item['path']))
        report['selected'].append(dict(item, request_sha256=response['request_sha256'],
                                       identity=response['reading']['identity'],
                                       relationships=response['reading']['relationships'],
                                       issues=response['reading']['issues'], changes=stated))
        for change in stated:
            changes.setdefault(change['target'], []).append(change)
    return changes, report


def summary(evaluation, run):
    """C's result with the run's stated evaluation date and knowledge cutoff."""
    return dict(truth=evaluation.truth, effect=evaluation.effect, needs=sorted(evaluation.needs),
                at=run['at'].isoformat(), known_through=run['known_through'].isoformat())


def run_inputs(parser):
    """The evaluation context a C-reaching run states; neither is taken from the machine clock."""
    parser.add_argument('--at', type=date.fromisoformat, required=True,
                        help='the evaluation date (ISO) that selects the A/B version')
    parser.add_argument('--known-through', type=run_instant, required=True,
                        help="the knowledge cutoff, a timezone-aware ISO instant; C's evaluated_at")


def per_recipient(results, supplied, snapshot, run, closures, changes):
    """C per (clause, recipient a supplied record names), attached to each clause record beside its cohort `c`.

    Supplied records are grouped by the order they name; each clause record of that
    order gets `per_recipient` and `per_recipient_reported`. Returns what reached no
    held order. The evaluation date, C's `evaluated_at` and the controlled-source
    grant are the run's stated inputs.
    """
    from zoneinfo import ZoneInfo
    from cordon_d.calendar import national_calendar
    from cordon_d.case_prescriptions import recipient_results
    zone, calendar = ZoneInfo('Europe/Rome'), national_calendar()
    evaluated_at = run['known_through']
    by_order = {}
    for item in supplied:
        by_order.setdefault(item.get('order'), []).append(item)
    reached = set()
    for entry in results:
        for record in entry.get('records', ()):
            act = record.get('applied_by') or record['instrument']
            if act not in by_order or record['stated_term'] is None:
                continue
            reached.add(act)
            try:
                recipients = recipient_results(snapshot, record, run['at'], by_order[act], evaluated_at=evaluated_at,
                                               permitted_controlled_sources=run['permitted_controlled_sources'],
                                               zone=zone, calendar=calendar,
                                               closures=closures.get(record['instrument'], ()),
                                               stated_changes=changes.get(record['instrument'], ()))
            except Exception as error:  # a refused record set is reported whole, never partly applied
                record['per_recipient_cause'] = f'{type(error).__name__}: {error}'[:600]
                continue
            # Kept apart from the record's own `recipients` (the cohort words the order prints).
            record['per_recipient'] = {name: {**{k: v for k, v in item.items() if k != 'result'},
                                              'c': summary(item['result'], run)}
                                       for name, item in recipients['recipients'].items()}
            record['per_recipient_reported'] = recipients['reported']
    return dict(evaluated_at=evaluated_at.isoformat(),
                permitted_controlled_sources=sorted(run['permitted_controlled_sources']),
                unreached=[dict(record=i.get('record'), order=order, cause='names no held order with a stated term')
                           for order, items in by_order.items() if order not in reached for i in items])


_WORKER = {}


def _start_worker():
    """Each worker loads the store root and the A/B snapshot once."""
    _WORKER.update(store=store_root(ROOT), snapshot=Snapshot.load(ROOT))


def read_one(item, options, run):
    """One source: replay its retained reading, or make one bounded subscription request.

    A refusal gets one source-only reread; a second refusal stands. A validated
    first reading that states clause limits gets one source-only reread stating
    them; a limit the reread still states stands. The memory gate is checked before
    each dispatch, in the worker that dispatches.
    """
    identity, digest, url = item
    store, snapshot = _WORKER['store'], _WORKER['snapshot']
    if options['execute']:
        _wait_for_memory()
    entry = dict(printed_identity=identity, source=digest, url=url)
    started = datetime.now(timezone.utc)
    try:
        try:
            reading = read_prescription(digest, store, **options)
        except ValueError as refusal:
            entry['refused_first'] = str(refusal)
            reading = read_prescription(digest, store, refused=str(refusal), **options)
        limits = stated_limits(reading)
        if limits and 'refused_first' not in entry:
            entry['limited_first'] = limits
            if options['execute']:
                _wait_for_memory()
            try:
                reading = read_prescription(digest, store, limited=limits, **options)
            except ValueError as refusal:
                entry['limit_reread_refused'] = str(refusal)
        entry['request_sha256'] = reading.response['request_sha256']
        entry['seconds'] = reading.response.get('seconds')
        entry['identity'] = reading.values['identity']
        entry['relationships'] = reading.values['relationships']
        entry['issues'] = reading.values['issues']
        try:
            records = list(reading.records(snapshot))
        except MissingInput as error:
            entry['records_cause'] = str(error)
            records = []
        entry['records'] = [dict(record, c=summary(c_result(snapshot, record, run['at'],
                                                            evaluated_at=run['known_through']), run))
                            for record in records]
    except FileNotFoundError:
        entry['cause'] = 'no retained reading'
    except Exception as error:  # a failed read is an execution failure, not source silence
        entry['cause'] = f'{type(error).__name__}: {error}'[:600]
        entry['trace'] = traceback.format_exc()[-1200:]
    entry['elapsed'] = round((datetime.now(timezone.utc) - started).total_seconds(), 1)
    return entry


def _write(path, results):
    """Replace the output file whole, so a stop between sources leaves a complete file."""
    if path:
        temporary = Path(str(path) + '.tmp')
        temporary.write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str))
        temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--only', nargs='*', default=())
    parser.add_argument('--first', nargs='*', default=(), help='identities to read before the rest')
    parser.add_argument('--out')
    parser.add_argument('--events', action='store_true',
                        help='attach publication events the existing readers connect to each order')
    parser.add_argument('--closures', help='a read_judgments.py --dispositions output: liveness closures by order')
    parser.add_argument('--records', help='supplied Osservatorio records (a JSON list): C per recipient they name')
    parser.add_argument('--permitted-controlled-sources', nargs='*', metavar='SOURCE',
                        help='with --records: the controlled source identities the running principal is granted '
                             '(state it even when empty)')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--model', default='opus')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--workers', type=int, default=1,
                        help='sources read at once; each is still one bounded request')
    run_inputs(parser)
    arguments = parser.parse_args()
    if arguments.workers < 1:
        parser.error('--workers must be at least 1')
    if arguments.records and arguments.permitted_controlled_sources is None:
        parser.error('--records requires --permitted-controlled-sources (state it even when empty)')
    if arguments.permitted_controlled_sources is not None and not arguments.records:
        parser.error('--permitted-controlled-sources applies to --records')
    _start_worker()
    store, snapshot = _WORKER['store'], _WORKER['snapshot']
    run = dict(at=arguments.at, known_through=arguments.known_through,
               permitted_controlled_sources=frozenset(arguments.permitted_controlled_sources or ()))
    selected = [item for item in population(arguments.known_through)
                if not arguments.only or item[0] in arguments.only or item[1] in arguments.only]
    if arguments.first:
        selected.sort(key=lambda item: item[0] not in arguments.first)
    options = dict(execute=arguments.execute, model=arguments.model, effort=arguments.effort,
                   timeout=arguments.timeout)
    done = {}

    def finished(index, entry):
        done[index] = entry
        print(json.dumps(dict(identity=entry['printed_identity'], source=entry['source'][:12],
                              cause=entry.get('cause'), records=len(entry.get('records', ())),
                              elapsed=entry['elapsed'])), flush=True)
        _write(arguments.out, [done[i] for i in sorted(done)])

    if arguments.workers == 1:
        for index, item in enumerate(selected):
            finished(index, read_one(item, options, run))
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=arguments.workers, initializer=_start_worker) as pool:
            futures = {pool.submit(read_one, item, options, run): index
                       for index, item in enumerate(selected)}
            for future in as_completed(futures):
                finished(futures[future], future.result())
    results = [done[i] for i in sorted(done)]
    # Work an act applies by reference takes the referenced order's own clause record.
    composed = {r['occurrence']: r for r in apply_references(
        [{k: v for k, v in r.items() if k != 'c'} for entry in results for r in entry.get('records', ())])}
    closures = load_closures(arguments.closures)
    changes = stated_changes(results)
    held_changes, held_report = held_act_changes(results, snapshot, store, options, arguments.known_through)
    for target, items in held_changes.items():
        changes.setdefault(target, []).extend(items)
    print(json.dumps(dict(held_acts_scanned=held_report['scanned'], held_acts_read=len(held_report['selected']),
                          held_acts_not_held_by_cutoff=len(held_report['not_held_by_cutoff']),
                          held_act_failures=len(held_report['failures']),
                          orders_named=sorted(held_changes))), flush=True)
    for entry in results:
        entry['records'] = [dict(composed[r['occurrence']],
                                 liveness_closures=closures.get(composed[r['occurrence']]['instrument'], []),
                                 stated_changes=changes.get(composed[r['occurrence']]['instrument'], []),
                                 c=summary(c_result(
                                     snapshot, composed[r['occurrence']], run['at'],
                                     evaluated_at=run['known_through'],
                                     closures=closures.get(composed[r['occurrence']]['instrument'], ()),
                                     stated_changes=changes.get(composed[r['occurrence']]['instrument'], ())),
                                     run))
                            for r in entry.get('records', ())]
    results.append(dict(held_acts=held_report))
    if arguments.records:
        results.append(dict(supplied_records=per_recipient(results, json.loads(Path(arguments.records).read_text()),
                                                           snapshot, run, closures, changes)))
    if arguments.out:
        Path(arguments.out).write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str))
    if arguments.events:
        measures = {(r['instrument'], r['adopted'], r['source']): dict(instrument=r['instrument'],
                                                                      adopted=r['adopted'], source=r['source'])
                    for entry in results for r in entry.get('records', ())}
        by_instrument, failures = held_events(measures.values(), store, arguments.known_through)
        for entry in results:
            instruments = {r['instrument'] for r in entry.get('records', ())}
            entry['held_events'] = [e for i in sorted(instruments) for e in by_instrument.get(i, ())]
        results.append(dict(event_reader_failures=failures))
        print(json.dumps(dict(event_instruments=len(by_instrument), event_failures=len(failures))))
        if arguments.out:
            Path(arguments.out).write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str))


if __name__ == '__main__':
    main()

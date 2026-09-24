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
from cordon_d.case_prescriptions import apply_references, c_result, read_prescription  # noqa: E402
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


def population():
    """Every retained original the removal-order source map holds, in its own order."""
    records = json.loads((ROOT / 'corpus/sources/removal-orders/records.json').read_text())
    seen = set()
    for record in records:
        digest = record.get('sha256')
        if digest and digest not in seen:
            seen.add(digest)
            yield printed_identity(record), digest, record['url']


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


def held_events(measures, store):
    """Events the existing publication readers connect to these orders, by instrument.

    Each publisher's retained register is read by its own existing reader. None of
    these events is recipient notification, commencement or removal.
    """
    from types import SimpleNamespace
    from cordon_d.removal_events import (connect_publication_attestation, connected_publications,
                                         domino_publication, parsec_publications, publication_records,
                                         regional_publication, retained_publication_attestation)
    from cordon_d.store import blob_path
    captures = json.loads((ROOT / 'corpus/sources/removal-events/records.json').read_text())
    acquisitions = json.loads((ROOT / 'corpus/sources/removal-orders/records.json').read_text()) + captures
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


def summary(evaluation):
    return dict(truth=evaluation.truth, effect=evaluation.effect, needs=sorted(evaluation.needs))


_WORKER = {}


def _start_worker():
    """Each worker loads the store root and the A/B snapshot once."""
    _WORKER.update(store=store_root(ROOT), snapshot=Snapshot.load(ROOT))


def read_one(item, options, today):
    """One source: replay its retained reading, or make one bounded subscription request.

    A refusal gets one source-only reread; a second refusal stands. The memory
    gate is checked before each dispatch, in the worker that dispatches.
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
        entry['records'] = [dict(record, c=summary(c_result(snapshot, record, today))) for record in records]
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
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--model', default='opus')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--workers', type=int, default=1,
                        help='sources read at once; each is still one bounded request')
    arguments = parser.parse_args()
    if arguments.workers < 1:
        parser.error('--workers must be at least 1')
    _start_worker()
    store, snapshot = _WORKER['store'], _WORKER['snapshot']
    today = date.today()
    selected = [item for item in population()
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
            finished(index, read_one(item, options, today))
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=arguments.workers, initializer=_start_worker) as pool:
            futures = {pool.submit(read_one, item, options, today): index
                       for index, item in enumerate(selected)}
            for future in as_completed(futures):
                finished(futures[future], future.result())
    results = [done[i] for i in sorted(done)]
    # Work an act applies by reference takes the referenced order's own clause record.
    composed = {r['occurrence']: r for r in apply_references(
        [{k: v for k, v in r.items() if k != 'c'} for entry in results for r in entry.get('records', ())])}
    closures = load_closures(arguments.closures)
    changes = stated_changes(results)
    for entry in results:
        entry['records'] = [dict(composed[r['occurrence']],
                                 liveness_closures=closures.get(composed[r['occurrence']]['instrument'], []),
                                 stated_changes=changes.get(composed[r['occurrence']]['instrument'], []),
                                 c=summary(c_result(
                                     snapshot, composed[r['occurrence']], today,
                                     closures=closures.get(composed[r['occurrence']]['instrument'], ()),
                                     stated_changes=changes.get(composed[r['occurrence']]['instrument'], ()))))
                            for r in entry.get('records', ())]
    if arguments.out:
        Path(arguments.out).write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str))
    if arguments.events:
        measures = {(r['instrument'], r['adopted'], r['source']): dict(instrument=r['instrument'],
                                                                      adopted=r['adopted'], source=r['source'])
                    for entry in results for r in entry.get('records', ())}
        by_instrument, failures = held_events(measures.values(), store)
        for entry in results:
            instruments = {r['instrument'] for r in entry.get('records', ())}
            entry['held_events'] = [e for i in sorted(instruments) for e in by_instrument.get(i, ())]
        results.append(dict(event_reader_failures=failures))
        print(json.dumps(dict(event_instruments=len(by_instrument), event_failures=len(failures))))
        if arguments.out:
            Path(arguments.out).write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str))


if __name__ == '__main__':
    main()

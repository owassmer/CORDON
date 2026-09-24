#!/usr/bin/env python3
"""Attach albo postings and executor acts to held orders by the identity each record prints.

Reads every retained OpenWeb albo register export and every retained JCityGov
posting detail (with its posted document) in the removal-event source map.
`--orders` is a results file written by `read_prescriptions.py --out`: the orders
D holds, with their adoption dates. Posted image scans are read for their printed
identity through the subscription (`--execute` dispatches missing reads). `--out`
writes events, unattached rows with their cause, register spans and failures as
JSON outside the tree; nothing here is an owner.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]

from cordon_d.albo_postings import (jcitygov_posting, openweb_rows, posted_document_events,  # noqa: E402
                                    posted_identity, register_events)
from cordon_d.removal_events import act_id  # noqa: E402
from cordon_d.store import blob_path, store_root  # noqa: E402

PUBLISHERS = {'arif.soluzionipa.it': ('ARIF', 'executor'),
              'portale.comune.fasano.br.it': ('Comune di Fasano', 'municipal'),
              'servizi.comune.modugno.ba.it': ('Comune di Modugno', 'municipal'),
              'servizi.comune.montemesola.ta.it': ('Comune di Montemesola', 'municipal'),
              'taranto.trasparenza-valutazione-merito.it': ('Comune di Taranto', 'municipal')}


def held_orders(path):
    """Instrument to adoption date for every order whose own reading states its identity."""
    held = {}
    for entry in json.loads(Path(path).read_text()):
        identity = entry.get('identity') if isinstance(entry, dict) else None
        if identity and identity.get('authority') == 'puglia-osservatorio' and identity.get('number') \
                and identity.get('adopted'):
            digits = ''.join(c for c in identity['number'] if c.isdigit())
            if digits:
                held[act_id(int(digits), identity['adopted'][:4])] = date.fromisoformat(identity['adopted'])
    return held


def event_row(event):
    return dict(kind=event.kind, document=event.document, occurred=event.occurred.isoformat(),
                source=event.support.source, selector=event.support.selector, reading=event.support.reading)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orders', required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--out')
    arguments = parser.parse_args()
    store = store_root(ROOT)
    held = held_orders(arguments.orders)
    records = json.loads((ROOT / 'corpus/sources/removal-events/records.json').read_text())
    events, unattached, spans, failures, seen = {}, [], [], [], set()

    def keep(found, publisher):
        for event in found:
            key = (event.kind, event.document, event.occurred, event.support.reading)
            if key not in seen:
                seen.add(key)
                events.setdefault(event.document, []).append(dict(event_row(event), publisher=publisher))

    for record in records:
        digest, url = record.get('sha256'), record['url']
        host = url.split('/')[2]
        if record['kind'] != 'publication' or not digest or host not in PUBLISHERS:
            continue
        publisher, role = PUBLISHERS[host]
        data = blob_path(store, digest).read_bytes()
        try:
            if '/openweb/albo/csv.php' in url:
                rows = openweb_rows(data)
                days = sorted(r['Inizio pubblicazione'][6:] + r['Inizio pubblicazione'][3:5] + r['Inizio pubblicazione'][:2]
                              for r in rows if len(r['Inizio pubblicazione']) == 10)
                spans.append(dict(source=digest, url=url, publisher=publisher, rows=len(rows),
                                  first_posting=days[0] if days else None, last_posting=days[-1] if days else None))
                found, causes = register_events(rows, source=digest, publisher=publisher, role=role, held=held)
                keep(found, publisher)
                unattached += [dict(c, source=digest, publisher=publisher) for c in causes]
            elif 'papca/display' in url:
                posting = jcitygov_posting(data)
                attachments = [r for r in records if r.get('referred_by') == f'Taranto native detail {digest}'
                               and r.get('sha256')]
                for attachment in attachments:
                    response = posted_identity(attachment['sha256'], store, execute=arguments.execute)
                    found, causes = posted_document_events(response, posting, detail_source=digest,
                                                           publisher=publisher, held=held)
                    keep(found, publisher)
                    unattached += [dict(c, source=attachment['sha256'], publisher=publisher,
                                        acts=response['reading']['acts']) for c in causes]
                    spans.append(dict(source=digest, url=url, publisher=publisher, period_start=posting['period_start'],
                                      period_end_words=posting['period_end_words'], subject=posting['subject'],
                                      posted=attachment['sha256'], identity=response['reading']))
        except FileNotFoundError:
            failures.append(dict(source=digest, url=url, cause='no retained identity reading'))
        except Exception as error:  # a failed read is an execution failure, not source silence
            failures.append(dict(source=digest, url=url, cause=f'{type(error).__name__}: {error}'[:400]))
    result = dict(events=events, unattached=unattached, spans=spans, failures=failures)
    print(json.dumps(dict(instruments=len(events), events=sum(len(v) for v in events.values()),
                          unattached=len(unattached), failures=len(failures))))
    if arguments.out:
        Path(arguments.out).write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str))


if __name__ == '__main__':
    main()

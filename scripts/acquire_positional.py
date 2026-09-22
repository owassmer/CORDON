"""Acquire the orthophoto chips and control points the positional measurement reads.

Chip bytes go into the content-addressed store; `chips.jsonl` beside the other
positional-reference records names each by the export that produced it and its hash.
A chip already recorded is never fetched again. Downloads run at low concurrency.

    python scripts/acquire_positional.py chips REQUESTS.json
    python scripts/acquire_positional.py control
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import threading
import time
from urllib.parse import urlencode

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'regulation/stage-d'))
from cordon_d.positional import chip_key  # noqa: E402
from cordon_d.store import put_bytes, store_root  # noqa: E402

RECORDS = ROOT / 'corpus/sources/positional-reference'
CHIPS = RECORDS / 'chips.jsonl'
CONTROL = RECORDS / 'control.json'
CONTROL_SERVICE = 'https://webapps.sit.puglia.it/arcgis/rest/services/ServicesArcIMS/RetiGeodetiche/MapServer'


def fetch(url, params, attempts=4):
    for attempt in range(attempts):
        try:
            response = requests.get(url, params=params, timeout=(15, 90), headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))


def recorded(records: Path):
    if not records.exists():
        return {}
    rows = [json.loads(line) for line in records.read_text().splitlines() if line.strip()]
    return {row['key']: row for row in rows}


def chips(path: Path, workers: int, records: Path = CHIPS):
    """Fetch every unrecorded chip; `records` may sit outside the tree while a long run appends."""
    store = store_root(ROOT)
    have = recorded(records)
    todo = [r for r in json.loads(path.read_text()) if chip_key(r) not in have]
    todo = list({chip_key(r): r for r in todo}.values())
    print('recorded', len(have), 'to fetch', len(todo), flush=True)
    lock = threading.Lock()
    done = [0]

    def one(request):
        response = fetch(request['service'] + '/exportImage', request['params'])
        kind = response.headers.get('Content-Type', '')
        if not kind.startswith('image/'):
            raise RuntimeError(f'{chip_key(request)}: {kind} {response.text[:200]}')
        digest = put_bytes(store, response.content)
        record = {'key': chip_key(request), 'year': request['year'], 'bbox': request['bbox'], 'size': request['size'],
                  'url': response.url, 'sha256': digest, 'bytes': len(response.content), 'content_type': kind,
                  'captured_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
        with lock:
            with records.open('a') as stream:
                stream.write(json.dumps(record, separators=(',', ':')) + '\n')
            done[0] += 1
            if done[0] % 200 == 0:
                print('fetched', done[0], 'of', len(todo), flush=True)

    failures = []
    with ThreadPoolExecutor(workers) as pool:
        for request, future in [(r, pool.submit(one, r)) for r in todo]:
            try:
                future.result()
            except Exception as error:  # a failed chip stays unrecorded and is retried next run
                failures.append((chip_key(request), str(error)[:200]))
    print('fetched', done[0], 'failed', len(failures), flush=True)
    for key, error in failures[:20]:
        print('  failed', key, error)


def control():
    """Every vertex of the regional geodetic network, as the service publishes it."""
    store = store_root(ROOT)
    pages = []
    for layer in (0, 1):
        low = 0
        while True:
            params = {'where': f'OBJECTID>{low}', 'outFields': '*', 'returnGeometry': 'true',
                      'orderByFields': 'OBJECTID', 'resultRecordCount': 1000, 'f': 'json'}
            response = fetch(f'{CONTROL_SERVICE}/{layer}/query', params)
            body = response.json()
            if 'error' in body:
                raise RuntimeError(body['error'])
            features = body.get('features', [])
            if not features:
                break
            pages.append({'layer': layer, 'url': response.url, 'sha256': put_bytes(store, response.content),
                          'bytes': len(response.content), 'features': len(features),
                          'captured_at': datetime.now(timezone.utc).isoformat(timespec='seconds')})
            low = max(f['attributes']['OBJECTID'] for f in features)
    CONTROL.write_text(json.dumps({'service': CONTROL_SERVICE, 'pages': pages}, indent=2) + '\n')
    print('control pages', len(pages), 'features', sum(p['features'] for p in pages))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    c = sub.add_parser('chips')
    c.add_argument('requests', type=Path)
    c.add_argument('--workers', type=int, default=3)
    c.add_argument('--records', type=Path, default=CHIPS)
    sub.add_parser('control')
    args = parser.parse_args()
    if args.command == 'chips':
        chips(args.requests, args.workers, args.records)
    else:
        control()

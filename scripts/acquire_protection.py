#!/usr/bin/env python3
"""Capture the protected-plant sources row 9 reads: the monumental-olive register and the list acts.

`register` captures SIT `Operationals/UliviMonumentali` layers 1 (listed trees) and 0 (provisional trees):
the layer description, the complete object-id list, and every feature page, each page's response bytes as
one store blob. `acts` captures the named L.R. 14/2007 list acts and other routes, one record per attempt.
Records go to `corpus/sources/protected-status/`; the bytes go to the store. A failed attempt keeps its cause.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-d'), str(ROOT / 'regulation/stage-c')]
from cordon_d.store import put_bytes, store_root  # noqa: E402

OUT = ROOT / 'corpus/sources/protected-status'
SERVICE = 'https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/UliviMonumentali/MapServer'
AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _get(url, *, attempts=4, timeout=(20, 180)):
    import requests
    for attempt in range(attempts):
        try:
            response = requests.get(url, headers=AGENT, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * (attempt + 1))


def register(workers: int):
    store = store_root(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    captured = {'service': SERVICE, 'captured_at': _now(), 'layers': []}
    for layer in (1, 0):
        base = f'{SERVICE}/{layer}'
        description = _get(f'{base}?f=json')
        ids = _get(f'{base}/query?' + urllib.parse.urlencode({'where': '1=1', 'returnIdsOnly': 'true', 'f': 'json'}))
        object_ids = sorted(ids.json()['objectIds'])
        count = _get(f'{base}/query?' + urllib.parse.urlencode({'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'})).json()['count']
        if count != len(object_ids):
            raise ValueError(f'layer {layer}: count {count} differs from its object-id list {len(object_ids)}')
        windows = [object_ids[i:i + 1000] for i in range(0, len(object_ids), 1000)]

        def page(window):
            params = {'where': f'OBJECTID>={window[0]} AND OBJECTID<={window[-1]}', 'outFields': '*',
                      'returnGeometry': 'true', 'orderByFields': 'OBJECTID', 'f': 'json'}
            url = f'{base}/query?' + urllib.parse.urlencode(params)
            response = _get(url)
            features = response.json().get('features', [])
            if len(features) != len(window):
                raise ValueError(f'layer {layer} page {window[0]}..{window[-1]}: {len(features)} of {len(window)} rows')
            return {'url': url, 'first_oid': window[0], 'last_oid': window[-1], 'rows': len(features),
                    'bytes': len(response.content), 'sha256': put_bytes(store, response.content)}

        with ThreadPoolExecutor(workers) as pool:
            pages = list(pool.map(page, windows))
        captured['layers'].append({
            'layer': layer, 'url': base, 'name': description.json().get('name'),
            'description': {'bytes': len(description.content), 'sha256': put_bytes(store, description.content)},
            'object_ids': {'bytes': len(ids.content), 'sha256': put_bytes(store, ids.content)},
            'rows': count, 'pages': pages})
        print(f'layer {layer}: {count} rows in {len(pages)} pages', flush=True)
    captured['finished_at'] = _now()
    (OUT / 'register.json').write_text(json.dumps(captured, ensure_ascii=False, indent=1) + '\n')


def acts(routes: list[tuple[str, str]]):
    store = store_root(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'acts.json'
    records = json.loads(path.read_text()) if path.exists() else []
    for url, purpose in routes:
        record = {'url': url, 'purpose': purpose, 'captured_at': _now()}
        try:
            response = _get(url, attempts=2, timeout=(20, 300))
            record.update(status=response.status_code, final_url=response.url,
                          content_type=response.headers.get('Content-Type'), bytes=len(response.content))
            if not response.content.startswith(b'%PDF'):
                raise ValueError('the route did not return a PDF')
            record['sha256'] = put_bytes(store, response.content)
        except Exception as error:  # the attempt and its cause are kept
            record['error'] = str(error)[:400]
        records.append(record)
        print(json.dumps({k: record.get(k) for k in ('url', 'status', 'bytes', 'sha256', 'error')}), flush=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    r = sub.add_parser('register')
    r.add_argument('--workers', type=int, default=4)
    a = sub.add_parser('acts')
    a.add_argument('route', nargs='+', help='URL|purpose')
    args = parser.parse_args()
    if args.command == 'register':
        register(args.workers)
    else:
        acts([tuple(item.split('|', 1)) if '|' in item else (item, 'list act') for item in args.route])

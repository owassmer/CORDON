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
import re
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


def _post(url, form, *, attempts=4, timeout=(20, 180)):
    import requests
    for attempt in range(attempts):
        try:
            response = requests.post(url, data=form, headers=AGENT, timeout=timeout)
            response.raise_for_status()
            if 'error' in response.json():
                raise requests.RequestException(str(response.json()['error'])[:300])
            return response
        except requests.RequestException:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * (attempt + 1))


def parcels(workers: int):
    """SIT Background/Catasto layer 2 (Particelle): every parcel a layer 1 or layer 0 entry prints, with its
    geometry in EPSG:32633, queried by comune code, foglio and particella. The comune codes come from layer 0's
    distinct names, captured first. The gross-error screen reads them; no parcel enters a bound."""
    from cordon_d import protection
    store = store_root(OUT)
    names_url = f'{protection.CATASTO}/0/query?' + urllib.parse.urlencode(
        {'where': '1=1', 'outFields': 'COMUNE,NOME_COMUNE', 'returnDistinctValues': 'true', 'returnGeometry': 'false',
         'f': 'json'})
    names = _get(names_url)
    captured = {'service': f'{protection.CATASTO}/2', 'captured_at': _now(),
                'comuni': {'url': names_url, 'bytes': len(names.content), 'sha256': put_bytes(store, names.content)}}
    codes = {protection._name_key(f['attributes']['NOME_COMUNE']): f['attributes']['COMUNE']
             for f in names.json()['features']}
    wanted = {}
    for entry in protection.register_entries(store, ROOT):
        code, printed, _ = protection.printed_parcels(entry, codes)
        for foglio, numero in printed:
            if re.fullmatch(r'[A-Z0-9]+', foglio) and re.fullmatch(r'[A-Z0-9]+', numero):
                wanted.setdefault(code, {}).setdefault(foglio, set()).add(numero)
    chunks = []
    for code, fogli in sorted(wanted.items()):
        clauses, size = [], 0
        for foglio, numeri in sorted(fogli.items()):
            for i in range(0, len(numeri), 150):
                part = sorted(numeri)[i:i + 150]
                clauses.append(f"(FOGLIO='{foglio}' AND NUMERO IN ({','.join(repr(n) for n in part)}))")
                size += len(part)
                if size >= 150:
                    chunks.append((code, clauses))
                    clauses, size = [], 0
        if clauses:
            chunks.append((code, clauses))

    def page(chunk):
        code, clauses = chunk
        where = f"COMUNE='{code}' AND ({' OR '.join(clauses)})"
        response = _post(f'{protection.CATASTO}/2/query', {
            'where': where, 'outFields': 'COMUNE,NOME_COMUNE,SEZIONE,FOGLIO,ALLEGATO,SVILUPPO,NUMERO',
            'returnGeometry': 'true', 'outSR': 32633, 'orderByFields': 'OBJECTID', 'f': 'json'})
        body = response.json()
        if body.get('exceededTransferLimit') and len(clauses) > 1:
            half = len(clauses) // 2
            return page((code, clauses[:half])) + page((code, clauses[half:]))
        if body.get('exceededTransferLimit'):
            raise ValueError(f'{where[:200]}: exceeds the transfer limit in one clause')
        return [{'where': where, 'rows': len(body.get('features', [])), 'bytes': len(response.content),
                 'sha256': put_bytes(store, response.content)}]

    with ThreadPoolExecutor(workers) as pool:
        captured['pages'] = [p for pages in pool.map(page, chunks) for p in pages]
    captured['printed_parcels'] = sum(len(n) for f in wanted.values() for n in f.values())
    captured['finished_at'] = _now()
    (OUT / protection.PARCELS).write_text(json.dumps(captured, ensure_ascii=False, indent=1) + '\n')
    print(f"{captured['printed_parcels']} printed parcels; {sum(p['rows'] for p in captured['pages'])} Catasto "
          f"features in {len(captured['pages'])} pages", flush=True)


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
    p = sub.add_parser('parcels')
    p.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.command == 'register':
        register(args.workers)
    elif args.command == 'parcels':
        parcels(args.workers)
    else:
        acts([tuple(item.split('|', 1)) if '|' in item else (item, 'list act') for item in args.route])

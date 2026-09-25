#!/usr/bin/env python3
"""Capture official vector-monitoring publications into the store (INPUTS.md row 12).

The population is every publication a publisher surface names: the Emergenza Xylella
front page and its archived captures, the SIT folder's archive index, and the
transmissions, circolari and acts that cite another publication. Each capture keeps
its URL, capture time, HTTP status, content type, bytes and sha256, or its error,
under corpus/sources/vectors/records.json, with the surface that named it. No file
name is composed here: a route enters only with the surface that printed it.

Usage: scripts/acquire_vectors.py --named NAMED.tsv   (url <TAB> named_by)
       scripts/acquire_vectors.py                     (retry failed routes)
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import csv
import json
from pathlib import Path
import sys

import requests

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPOSITORY / 'regulation/stage-d')]
from cordon_d.store import put_bytes, store_root  # noqa: E402

KINDS = {b'%PDF': 'application/pdf', b'\xff\xd8\xff': 'image/jpeg', b'\x89PNG': 'image/png'}


def fetch(url: str, store: Path) -> dict:
    record = {'url': url, 'captured_at': datetime.now(timezone.utc).isoformat()}
    try:
        response = requests.get(url, timeout=(20, 300), headers={'User-Agent': 'Mozilla/5.0'})
        body = response.content
        record.update(status=response.status_code, final_url=response.url,
                      content_type=response.headers.get('Content-Type'), bytes=len(body),
                      last_modified=response.headers.get('Last-Modified'))
        kind = next((k for magic, k in KINDS.items() if body.startswith(magic)), None)
        if response.status_code != 200:
            record['error'] = f'HTTP {response.status_code}'
        elif kind is None:
            record['error'] = 'not a PDF or image: ' + body[:80].decode('latin-1', 'replace')
        else:
            record['sha256'] = put_bytes(store, body)
    except requests.RequestException as error:
        record['error'] = str(error)[:300]
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=REPOSITORY / 'corpus/sources/vectors')
    parser.add_argument('--named', type=Path, help='TSV of url and the surface that names it')
    args = parser.parse_args()
    args.root.mkdir(parents=True, exist_ok=True)
    path = args.root / 'records.json'
    records = json.loads(path.read_text()) if path.exists() else []
    named = {}
    for record in records:
        named.setdefault(record['url'], record['named_by'])
    if args.named:
        with args.named.open() as stream:
            for url, surface in csv.reader(stream, delimiter='\t'):
                if not surface.strip():
                    raise ValueError(f'A route needs the surface that names it: {url}')
                named.setdefault(url, surface)
    held = {r['url'] for r in records if 'sha256' in r}
    pending = sorted(u for u in named if u not in held)
    store = store_root(args.root)
    print(f'routes {len(named)} pending {len(pending)} store {store}', flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        for record in pool.map(lambda u: fetch(u, store), pending):
            record['named_by'] = named[record['url']]
            records = [r for r in records if r['url'] != record['url'] or 'sha256' in r]
            records.append(record)
            print(record.get('status'), record.get('error', record.get('sha256', '')[:12]), record['url'], flush=True)
    records.sort(key=lambda r: (r['url'], r['captured_at']))
    path.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n')
    print(f'complete: {sum("sha256" in r for r in records)} acquired, '
          f'{sum("error" in r for r in records)} failed', flush=True)


if __name__ == '__main__':
    main()

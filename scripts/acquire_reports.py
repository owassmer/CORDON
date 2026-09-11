#!/usr/bin/env python3
"""Capture every laboratory report the observation stream references into the store.

The population is every distinct report route in the derived monitoring readings;
no route is skipped for its answer, year, host or name. Each route gets one
acquisition record (URL, capture time, HTTP status, content type, bytes, sha256 or
error) under corpus/sources/reports/records.json; identical bytes at two routes
are one blob. A failed route is recorded, retried once on the next run, and
never silently dropped. Rerunning resumes: routes with a sha256 are not refetched.

Usage: scripts/acquire_reports.py [output-root]   (default: corpus/sources/reports)
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import glob
import json
from pathlib import Path
import sys
from threading import Lock, local

import duckdb
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
from cordon_d.store import put_bytes, store_root  # noqa: E402

TRANSPORT = local()


def routes(store: Path) -> list[str]:
    files = glob.glob(str(store / 'derived/monitoring/readings/*.parquet'))
    connection = duckdb.connect()
    connection.execute("SET memory_limit = '1GB'")
    connection.execute('SET threads = 2')
    rows = connection.execute('SELECT DISTINCT route FROM (SELECT unnest(report_routes) AS route '
                              'FROM read_parquet($files)) ORDER BY route', {'files': files}).fetchall()
    connection.close()
    return [r[0] for r in rows]


def fetch(url: str, store: Path) -> dict:
    if not hasattr(TRANSPORT, 'session'):
        TRANSPORT.session = requests.Session()
    record: dict = {'url': url, 'captured_at': datetime.now(timezone.utc).isoformat()}
    try:
        response = TRANSPORT.session.get(url, timeout=(20, 120))
        record['status'] = response.status_code
        record['content_type'] = response.headers.get('Content-Type')
        body = response.content
        record['bytes'] = len(body)
        if response.status_code != 200:
            record['error'] = f'HTTP {response.status_code}'
        elif not body.startswith(b'%PDF'):
            record['error'] = 'not a PDF: ' + body[:80].decode('latin-1', 'replace')
        else:
            record['sha256'] = put_bytes(store, body)
    except requests.RequestException as error:
        record['error'] = str(error)[:300]
    return record


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'corpus/sources/reports')
    root.mkdir(parents=True, exist_ok=True)
    store = store_root(root)
    path = root / 'records.json'
    records = {r['url']: r for r in json.loads(path.read_text())} if path.exists() else {}
    pending = [u for u in routes(store) if 'sha256' not in records.get(u, {})]
    print(f'routes {len(records) + len([u for u in pending if u not in records])} pending {len(pending)} store {store}', flush=True)
    lock = Lock()
    done = failed = 0

    def save():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(sorted(records.values(), key=lambda r: r['url']), ensure_ascii=False, indent=1) + '\n')
        temporary.replace(path)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch, url, store): url for url in pending}
        for future in as_completed(futures):
            record = future.result()
            with lock:
                records[record['url']] = record
                done += 1
                failed += 'error' in record
                if done % 50 == 0 or done == len(pending):
                    save()
                    print(f'{done}/{len(pending)} failed {failed}', flush=True)
    save()
    print(f'complete: {sum(1 for r in records.values() if "sha256" in r)} acquired, '
          f'{sum(1 for r in records.values() if "error" in r)} failed, '
          f'{len({r["sha256"] for r in records.values() if "sha256" in r})} distinct documents', flush=True)


if __name__ == '__main__':
    main()

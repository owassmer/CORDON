#!/usr/bin/env python3
"""Capture every laboratory report the observation stream references into the store.

The population is every distinct report route in the derived monitoring readings;
no route is skipped for its answer, year, host or name. Each route gets retained
acquisition versions (URL, capture time, HTTP status, content type, bytes, sha256 or
error) under corpus/sources/reports/records.json; identical bytes at two routes
are one blob. A failed route is recorded and retried on the next run, and
never silently dropped. Rerunning resumes; successful current routes are refetched only with --recapture.

Usage: scripts/acquire_reports.py --help
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import sys
from threading import Lock, local

import requests

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPOSITORY / 'regulation/stage-d'), str(REPOSITORY / 'regulation/stage-c')]
from cordon_d.store import put_bytes, store_root  # noqa: E402
from cordon_d.monitoring import observations  # noqa: E402

TRANSPORT = local()


def routes(monitoring_root: Path) -> list[str]:
    """Declared release population through its ordinary reader, never a cache glob."""
    return sorted({url for observation in observations(monitoring_root)
                   for _, url in observation.publication.document_references})


def fetch(url: str, store: Path) -> dict:
    if not hasattr(TRANSPORT, 'session'):
        TRANSPORT.session = requests.Session()
    record: dict = {'url': url, 'captured_at': datetime.now(timezone.utc).isoformat()}
    try:
        response = TRANSPORT.session.get(url, timeout=(20, 120))
        record['status'] = response.status_code
        record['final_url'] = response.url
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', type=Path, default=Path('corpus/sources/reports'))
    parser.add_argument('--monitoring-root', type=Path, default=Path('corpus/sources/monitoring'))
    parser.add_argument('--recapture', action='append', default=[])
    parser.add_argument('--source-links', type=Path,
                        help='Derived reached links with source_sha256 and source_locator')
    parser.add_argument('--only-source-links', action='store_true',
                        help='Acquire this reached-link batch without retrying unrelated known failures')
    args = parser.parse_args()
    if args.only_source_links and not args.source_links:
        parser.error('--only-source-links requires --source-links')
    root = args.output_root
    root.mkdir(parents=True, exist_ok=True)
    store = store_root(root)
    path = root / 'records.json'
    records = json.loads(path.read_text()) if path.exists() else []
    current = {r['url']: r for r in sorted(records, key=lambda r: r['captured_at'])}
    admitted = set() if args.only_source_links else set(routes(args.monitoring_root))
    links = json.loads(args.source_links.read_text()) if args.source_links else []
    parents = {r['url']: r['referred_by'] for r in records if r.get('referred_by')}
    if not args.only_source_links:
        admitted.update(parents)
    for link in links:
        if not all(link.get(k) for k in ('url', 'source_sha256', 'source_locator')):
            raise ValueError('A reached report link requires its source and locator')
        if not any(r.get('sha256') == link['source_sha256'] for r in records):
            raise ValueError('Referring report is not in the acquired population')
        parents.setdefault(link['url'], []).append({k: link[k] for k in ('source_sha256', 'source_locator')})
        admitted.add(link['url'])
    if not set(args.recapture) <= admitted:
        raise ValueError('Recapture must concern an admitted source route')
    pending = sorted(u for u in admitted if 'sha256' not in current.get(u, {}) or u in args.recapture)
    print(f'routes {len(admitted)} pending {len(pending)} store {store}', flush=True)
    lock = Lock()
    done = failed = 0

    def save():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(sorted(records, key=lambda r: (r['url'], r['captured_at'])), ensure_ascii=False, indent=1) + '\n')
        temporary.replace(path)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch, url, store): url for url in pending}
        for future in as_completed(futures):
            record = future.result()
            with lock:
                # Retain successful acquisition versions; only the current failed attempt is needed.
                records[:] = [r for r in records if r['url'] != record['url'] or 'sha256' in r]
                if record['url'] in parents:
                    record['referred_by'] = parents[record['url']]
                records.append(record)
                done += 1
                failed += 'error' in record
                if done % 50 == 0 or done == len(pending):
                    save()
                    print(f'{done}/{len(pending)} failed {failed}', flush=True)
    save()
    print(f'complete: {sum(1 for r in records if "sha256" in r)} acquired, '
          f'{sum(1 for r in records if "error" in r)} failed, '
          f'{len({r["sha256"] for r in records if "sha256" in r})} distinct documents', flush=True)


if __name__ == '__main__':
    main()

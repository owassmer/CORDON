#!/usr/bin/env python3
"""Retain official EPPO v2 name lookups, complete taxon names and ancestry.

Only names reached by the established observation stream are looked up. Search
uses name2codes, not the separately documented ten-result search endpoint.
An existing capture is reused. Credentials never enter records or request URLs.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import sys

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'regulation/stage-c'),str(ROOT/'regulation/stage-d')]
from cordon_d.store import blob_path, put_bytes, store_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-file', type=Path, default=Path.home()/'.config/cordon/eppo-api-key')
    parser.add_argument('--report-reading-version', help='Explicit retained #7 reading revision, without extraction')
    args = parser.parse_args()
    key = args.key_file.read_text().strip()
    folder = ROOT/'corpus/sources/host-names'
    store = store_root(ROOT)
    specification = json.loads((folder/'specification.json').read_text())
    path = folder/'api.json'
    records = json.loads(path.read_text()) if path.exists() else []
    existing = {r['url']: r for r in records}
    def capture(route, params=None):
        url = requests.Request('GET', 'https://api.eppo.int/gd/v2'+route, params=params).prepare().url
        if url in existing:
            record = existing[url]
            return record, json.loads(blob_path(store, record['sha256']).read_bytes())
        response = requests.get(url, headers={'X-Api-Key': key}, timeout=45)
        response.raise_for_status()
        data = response.json()
        record = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat(),
                      sha256=put_bytes(store,response.content), specification_sha256=specification['sha256'])
        return record,data
    import duckdb
    from cordon_d.monitoring import releases,reader_version,_ensure_derived
    files=[str(_ensure_derived(store,r,reader_version())[1]) for r in releases(ROOT/'corpus/sources/monitoring')]
    connection=duckdb.connect()
    connection.execute("SET memory_limit='512MB'");connection.execute('SET threads=2')
    labels={row[0] for row in connection.execute('select distinct species from read_parquet(?) where species is not null',[files]).fetchall()}
    connection.close()
    if args.report_reading_version:
        from cordon_d.reports import reports,Report
        for reading in reports(ROOT/'corpus/sources/reports',store,extraction_version=args.report_reading_version):
            if isinstance(reading,Report):
                labels.update(c['text'] for row in reading.rows for c in row.cells if c['role']=='host' and c.get('text'))
    queries=set()
    for label in labels:
        for part in re.split('[()]',label):
            part=' '.join(part.split()).strip()
            if part:
                queries.add(part)
                if len(part.split())>1:queries.add(' '.join(part.split()[:2]))
    queries=sorted(queries)
    codes = set()
    with ThreadPoolExecutor(max_workers=3) as pool:
        for record, values in pool.map(lambda q:capture('/tools/name2codes',{'name':q,'onlyPreferred':'false'}),queries):
            existing[record['url']]=record
            if not isinstance(values,list):raise ValueError('Unresolved name lookup response shape')
            codes.update(v['eppocode'] for v in values)
            path.write_text(json.dumps(list(existing.values()),indent=2)+'\n')
    # Complete the reached genera in this invocation, including parents learned
    # from newly captured species. No separate manually curated genus list.
    pending = codes.copy()
    completed = set()
    while pending:
        routes = [f'/taxons/taxon/{code}/{part}' for code in sorted(pending)
                  for part in ('overview','names','taxonomy')]
        ancestors = set()
        with ThreadPoolExecutor(max_workers=3) as pool:
            for record, values in pool.map(capture,routes):
                existing[record['url']] = record
                if not isinstance(values,(list,dict)):
                    raise ValueError('Unresolved taxon response shape')
                if record['url'].endswith('/taxonomy'):
                    ancestors.update(v['eppocode'] for v in values if v['type']=='Genus')
                path.write_text(json.dumps(list(existing.values()),indent=2)+'\n')
        completed.update(pending)
        codes.update(ancestors)
        pending = ancestors - completed
    print(f'{len(queries)} complete name lookups; {len(codes)} named taxa; {len(existing)} retained responses')


if __name__ == '__main__':
    main()

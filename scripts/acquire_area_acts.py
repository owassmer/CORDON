"""Recover the adopting acts' own documents into the store.

Stage A holds each area act as extracted text and cites the document it was
extracted from. The document itself carries the cadastral annex as a real
table, whose cells the text layer no longer bounds, so the document is the
source this row reads.

The migration manifest inventories these exact files as EXCLUDED_INVENTORIED,
"inventoried for recovery"; this is that recovery. Each record states where the
bytes came from and their hash, so a later fetch from the publisher either
confirms them or is exposed against them. Re-fetching from BURP remains open
and is recorded as such on each record.

Usage: scripts/acquire_area_acts.py [output-root] [--archive PATH]
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
from cordon_d.store import put_bytes, store_root  # noqa: E402

AREA_ROW = re.compile(r'area-state-transition|area-update|area-act-before-gis')
DEFAULT_ARCHIVE = Path.home() / 'Desktop/Connor/wedge1-aip'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, nargs='?', default=Path('corpus/sources/areas'))
    parser.add_argument('--archive', type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args()

    rows = json.loads((args.repo / 'regulation/jurisdiction/canonical/authoring.json').read_text())
    if not isinstance(rows, list):
        rows = list(rows.values())[0]
    area = [r for r in rows if AREA_ROW.search(r['provision_version_id'])]

    store = store_root(args.output)
    records, seen = [], set()
    for row in sorted(area, key=lambda r: r['effective_from']):
        instrument = row['instrument_id']
        if instrument in seen:
            continue
        seen.add(instrument)
        cited = row.get('source_paths') or ''
        document = cited[:-4] + '.pdf' if cited.endswith('.txt') else cited
        record = {'instrument_id': instrument,
                  'provision_version_id': row['provision_version_id'],
                  'cited_source_path': cited,
                  'document_path': document,
                  'captured_at': datetime.now(timezone.utc).isoformat(),
                  'origin': 'wedge1-aip provenance archive (migration manifest: inventoried for recovery)',
                  'publisher_refetch': 'open: BURP document URL not recorded for these acts'}
        source = args.archive / document
        if not source.exists():
            record['error'] = 'document not present in the archive'
            records.append(record)
            print('MISSING', instrument, document, flush=True)
            continue
        body = source.read_bytes()
        record.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                      content_type='application/pdf' if body[:4] == b'%PDF' else 'unknown')
        if body[:4] != b'%PDF':
            record['error'] = 'not a PDF document'
        else:
            put_bytes(store, body)
        records.append(record)
        print(instrument, record['sha256'][:12], record['bytes'], 'bytes', flush=True)

    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / 'acts.json'
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(target)
    ok = sum(1 for r in records if r.get('sha256') and 'error' not in r)
    print(f'{ok} of {len(records)} act documents in the store', flush=True)


if __name__ == '__main__':
    main()

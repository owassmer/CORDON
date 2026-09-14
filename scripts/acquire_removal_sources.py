#!/usr/bin/env python3
"""Retain a reached administrative original, with its route and discovery parent.

No discovery keyword policy or case list lives here. The source binding owns the
admitted population. --local reconciles existing originals without new requests.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-d'), str(ROOT / 'regulation/stage-c')]
from cordon_d.store import put_bytes, store_root


def capture(url, *, kind, parent, local=None, output=None, session=None, data=None, public_headers=None):
    import requests
    output = Path(output) if output else ROOT / 'corpus/sources' / ('removal-orders' if kind == 'act' else 'removal-events')
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'records.json'
    records = json.loads(path.read_text()) if path.exists() else []
    record = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat(),
                  kind=kind, referred_by=parent)
    try:
        if local:
            data = Path(local).read_bytes()
            record['retained_original'] = str(local)
        else:
            if data is not None:
                record.update(method='POST', request_data=data)
            if public_headers:
                record['public_request_headers'] = public_headers
            client = session or requests
            response = client.post(url, data=data, headers=public_headers, timeout=(15, 45)) if data is not None else client.get(url, headers=public_headers, timeout=(15, 45))
            record.update(status=response.status_code, final_url=response.url,
                          content_type=response.headers.get('Content-Type'))
            response.raise_for_status()
            data = response.content
        if kind == 'act' and not data.startswith(b'%PDF'):
            raise ValueError('Administrative original is not a PDF')
        record.update(bytes=len(data), sha256=put_bytes(store_root(output), data))
    except (OSError, ValueError, requests.RequestException) as error:
        record['error'] = str(error)[:500]
    records.append(record)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n')
    return record


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('url')
    p.add_argument('--kind', choices=['act', 'publication', 'discovery', 'event'], required=True)
    p.add_argument('--parent', required=True, help='Source hash/locator or accepted consumer admitting this route')
    p.add_argument('--local', type=Path)
    a = p.parse_args()
    print(json.dumps(capture(a.url, kind=a.kind, parent=a.parent, local=a.local)))

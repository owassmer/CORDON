"""Capture the published demarcated-area geometry the accepted A area versions reach.

The population is every polygon layer of the three SIT services that publish
demarcated-area zones. They enter because A's area versions name exactly those
foci and zones; no other service enters here, and grids, cadastre and monitoring
points have their own D owners.

A capture is the publisher's representation at its capture time, not the act's
adopted geography: DDS 45/2025 establishes that the act creates the area and
InnovaPuglia transmits shapefiles afterwards, so a capture inside a new version's
interval can still show the previous geometry. The reader states that limitation
and requires corroboration; this script only records what the publisher served
and when.

Captured bytes are adopted into the content-addressed store; the source tree
keeps acquisition records only. Identical bytes deduplicate and changed bytes
receive a new name, so a refresh never overwrites a capture.

Usage: scripts/acquire_areas.py [output-root]   (default: corpus/sources/areas)
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
from threading import local
from urllib.parse import urlencode

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
from cordon_d.store import adopt, store_root  # noqa: E402

TRANSPORT = local()
BASE = 'https://webapps.sit.puglia.it/arcgis/rest/services/'

# The services that publish demarcated-area zone polygons. Each is here because
# accepted A area versions adopt the foci and zones it names; the historical
# BandoPSR service is included so the reader can state what it does and does not
# cover (its layers are 2014-2019, before A's earliest regional version).
SERVICES = (
    'Operationals/DatiPubbliciFasceXF',
    'Operationals2/DatiPubbliciFasceXFF',
    'Operationals2/DatiPubbliciFasceXFMultiplex',
    'Operationals2/DatiPubbliciFasceXFBandoPSR',
)
POLYGON = 'esriGeometryPolygon'


def request(url):
    if not hasattr(TRANSPORT, 'session'):
        TRANSPORT.session = requests.Session()
    for attempt in range(4):
        try:
            response = TRANSPORT.session.get(url, timeout=(15, 120))
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(attempt + 1)


def query(url, **params):
    value = json.loads(request(url + '/query?' + urlencode({'f': 'json', **params})))
    if 'error' in value:
        raise RuntimeError(value['error'])
    return value


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def prepare(output):
    """Discover the polygon layers of each admitted service and record their metadata."""
    items = []
    for service in SERVICES:
        value = json.loads(request(BASE + service + '/MapServer/layers?f=pjson'))
        if 'layers' not in value:
            raise RuntimeError(f'Cannot discover {service}')
        directory = output / 'sit' / service
        directory.mkdir(parents=True, exist_ok=True)
        write_json(directory / 'service.json',
                   {'service': service, 'discovered_at': datetime.now(timezone.utc).isoformat(),
                    'layers': [{'id': l['id'], 'name': l['name'],
                                'geometryType': l.get('geometryType')} for l in value['layers']]})
        for layer in value['layers']:
            if layer.get('geometryType') != POLYGON:
                continue
            layer_dir = directory / str(layer['id'])
            layer_dir.mkdir(parents=True, exist_ok=True)
            write_json(layer_dir / 'layer.json', layer)
            items.append((layer_dir, service, layer, output))
    return items


def page_captures(layer_dir):
    """When each retained page was actually served, by page name."""
    record = layer_dir / 'captures.json'
    return json.loads(record.read_text()) if record.exists() else {}


def note_capture(layer_dir, name, instant):
    captures = page_captures(layer_dir)
    captures[name] = instant
    temporary = layer_dir / 'captures.tmp'
    temporary.write_text(json.dumps(captures, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(layer_dir / 'captures.json')


def capture_layer(item):
    layer_dir, service, layer, output = item
    completed = layer_dir / 'release.json'
    if completed.exists():
        return json.loads(completed.read_text())
    url = BASE + service + '/MapServer/' + str(layer['id'])
    started = datetime.now(timezone.utc).isoformat()
    count = query(url, where='1=1', returnCountOnly='true')['count']
    identifiers = query(url, where='1=1', returnIdsOnly='true')
    ids = sorted(set(identifiers.get('objectIds') or []))
    oid = identifiers['objectIdFieldName']

    def fetch(group, name):
        path = layer_dir / (name + '.json.gz')
        if path.exists():
            value = json.loads(gzip.decompress(path.read_bytes()))
        else:
            # Zone polygons carry large vertex counts; take them one page at a
            # time and split on any transfer-limit signal rather than assuming.
            value = query(url, where=f'{oid} >= {group[0]} AND {oid} <= {group[-1]}',
                          outFields='*', returnGeometry='true')
        features = value.get('features')
        if features is None:
            raise RuntimeError(f'{url}: missing features')
        found = {f['attributes'][oid] for f in features}
        if value.get('exceededTransferLimit') or found != set(group):
            if len(group) == 1:
                raise RuntimeError(f'{url}: cannot fully recover object {group[0]}')
            middle = len(group) // 2
            return fetch(group[:middle], name + 'a') + fetch(group[middle:], name + 'b')
        if not path.exists():
            compressed = gzip.compress(
                json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)
            temporary = path.with_suffix('.tmp')
            temporary.write_bytes(compressed)
            temporary.replace(path)
            note_capture(layer_dir, path.name, datetime.now(timezone.utc).isoformat())
        return [{'path': path.name, 'rows': len(features),
                 'captured_at': page_captures(layer_dir).get(path.name),
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}]

    chunks, retained = [], set()
    id_set = set(ids)
    for path in sorted(layer_dir.glob('*.json.gz')):
        value = json.loads(gzip.decompress(path.read_bytes()))
        found = {f['attributes'][oid] for f in value['features']}
        if not found.issubset(id_set) or found & retained:
            raise ValueError(f'Overlapping or changed cached page population: {path}')
        retained.update(found)
        chunks.append({'path': path.name, 'rows': len(value['features']),
                       'captured_at': page_captures(layer_dir).get(path.name),
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    remaining = [i for i in ids if i not in retained]
    for start in range(0, len(remaining), 25):
        group = remaining[start:start + 25]
        chunks.extend(fetch(group, f'ids-{group[0]}-{group[-1]}'))

    ending = query(url, where='1=1', returnIdsOnly='true')
    end_count = query(url, where='1=1', returnCountOnly='true')['count']
    rows = sum(p['rows'] for p in chunks)
    if ids != sorted(set(ending.get('objectIds') or [])) or rows != count or count != end_count:
        raise RuntimeError(f'{url}: changing or incomplete population: '
                           f'start={count}, retained={rows}, end={end_count}')
    # A resumed run must not date old bytes to the interval it ran in. The
    # capture interval is the span of the pages actually retained, and pages
    # served in an earlier run keep their own time; stable object IDs and a
    # stable count are not evidence that the geometry behind them is unchanged.
    instants = sorted(p['captured_at'] for p in chunks if p.get('captured_at'))
    reused = [p['path'] for p in chunks
              if p.get('captured_at') and p['captured_at'] < started]
    result = {'url': url, 'service': service, 'layer_id': layer['id'], 'name': layer['name'],
              'captured_from': instants[0] if instants else started,
              'captured_through': instants[-1] if instants else datetime.now(timezone.utc).isoformat(),
              'inventory_checked_from': started,
              'inventory_checked_through': datetime.now(timezone.utc).isoformat(),
              'pages_retained_from_an_earlier_run': reused,
              'oid_field': oid, 'rows': rows, 'unique_oids': len(ids),
              'spatial_reference': layer.get('extent', {}).get('spatialReference'),
              'definition_expression': layer.get('definitionExpression'),
              'pages': chunks}
    store = store_root(output)
    for page in chunks:
        adopt(store, layer_dir / page['path'])
    write_json(layer_dir / 'release.json', result)
    print(service, layer['id'], layer['name'], rows, 'complete', flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, nargs='?', default=Path('corpus/sources/areas'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    items = prepare(args.output)
    print(f'{len(items)} polygon layers across {len(SERVICES)} services', flush=True)
    failures = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(capture_layer, item): item for item in items}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as error:
                item = futures[future]
                failures.append((item[1], item[2]['id'], str(error)))
                print('FAILED', failures[-1], flush=True)
    if failures:
        raise SystemExit(f'{len(failures)} layers incomplete; completed releases remain reusable.')
    print('all layers complete', flush=True)


if __name__ == '__main__':
    main()

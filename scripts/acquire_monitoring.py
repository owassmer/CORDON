"""Capture the admitted monitoring releases; retain native records, all results.

Captured bytes are adopted into the content-addressed store on completion; the
source tree keeps acquisition records only. Identical bytes deduplicate and
changed bytes receive a new name, so a refresh never overwrites a release.

Run with the project Python. Service metadata is the selection input; point
layers belong to observations, while grids, buffers and parcels have other D
owners. A changed service list must be assessed before refreshing this selection.
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from threading import local
from urllib.parse import urlencode, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
from cordon_d.store import adopt, store_root  # noqa: E402


TRANSPORT = local()
PORTAL = 'https://www.sit.puglia.it/portal/portale_gestione_agricoltura/Download/mon_xf'
CKAN = 'https://dati.puglia.it/ckan/api/3/action/package_show?id=dati-monitoraggio-xylella-fastidiosa'


def request(url):
    if not hasattr(TRANSPORT, 'session'):
        TRANSPORT.session = requests.Session()
    for attempt in range(4):
        try:
            response = TRANSPORT.session.get(url, timeout=(15, 75))
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


def capture_campaign(output):
    directory = output / 'campaign'
    directory.mkdir(parents=True, exist_ok=True)
    page = request(PORTAL)
    package = json.loads(request(CKAN))
    soup = BeautifulSoup(page, 'html.parser')
    urls = [urljoin(PORTAL, a['href']) for a in soup.find_all('a', href=True)
            if urlsplit(a['href']).path.lower().endswith('.xlsx')]
    if not urls or not package.get('success'):
        raise RuntimeError('Publisher discovery failed; do not replace the retained releases')
    urls.extend(r['url'] for r in package['result']['resources'] if r.get('url'))
    records = []
    for url in dict.fromkeys(urls):
        name = Path(urlsplit(url).path).name
        path = directory / name
        body = request(url)
        record = {'url': url, 'path': name, 'captured_at': datetime.now(timezone.utc).isoformat(),
                  'sha256': hashlib.sha256(body).hexdigest()}
        if path.suffix == '.xlsx':
            if not body.startswith(b'PK'):
                raise ValueError(f'Expected a workbook from {url}')
        elif path.suffix == '.csv':
            try:
                decoded = body.decode('utf-8-sig')
                encoding = 'utf-8-sig'
            except UnicodeDecodeError:
                if any(128 <= b < 160 for b in body):
                    raise ValueError(f'CSV encoding needs source interpretation: {url}')
                decoded, encoding = body.decode('latin-1'), 'latin-1'
            delimiter = csv.Sniffer().sniff(decoded[:8192], delimiters=',;\t').delimiter
            if '<html' in decoded[:1000].lower():
                raise ValueError(f'Publisher returned a web page instead of CSV: {url}')
            record.update(encoding=encoding, delimiter=delimiter)
        else:
            raise ValueError(f'New source format needs interpretation: {url}')
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_bytes(body)
        temporary.replace(path)
        records.append(record)
        print(name, len(body), 'bytes', flush=True)
    for record in records:
        adopt(store_root(output), directory / record['path'])
    (directory / 'publisher.html').write_bytes(page)
    write_json(directory / 'ckan.json', package)
    write_json(directory / 'releases.json', records)


def prepare(metadata, output):
    layers = []
    for path in sorted(metadata.glob('*--*.json')):
        service = path.stem.replace('--', '/')
        for layer in json.loads(path.read_text()).get('layers', []):
            if layer.get('geometryType') != 'esriGeometryPoint':
                continue
            directory = output / 'sit' / service / str(layer['id'])
            directory.mkdir(parents=True, exist_ok=True)
            write_json(directory / 'layer.json', layer)
            layers.append((directory, service, layer, output))
    return layers


def capture_layer(item):
    directory, service, layer, output = item
    completed = directory / 'release.json'
    if completed.exists():
        # The pages were adopted into the store by hash; the audit guards their bytes.
        return json.loads(completed.read_text())
    url = 'https://webapps.sit.puglia.it/arcgis/rest/services/' + service + '/MapServer/' + str(layer['id'])
    started = datetime.now(timezone.utc).isoformat()
    count = query(url, where='1=1', returnCountOnly='true')['count']
    identifiers = query(url, where='1=1', returnIdsOnly='true')
    ids = sorted(set(identifiers.get('objectIds') or []))
    id_set = set(ids)
    oid = identifiers['objectIdFieldName']
    # ID queries are not constrained by the feature transfer limit. Joined
    # views can have more rows than unique IDs; retain every returned row.
    def fetch(group, name):
        path = directory / (name + '.json.gz')
        if path.exists():
            value = json.loads(gzip.decompress(path.read_bytes()))
        else:
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
            compressed = gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)
            temporary = path.with_suffix('.tmp')
            temporary.write_bytes(compressed)
            temporary.replace(path)
        return [{'path': path.name, 'rows': len(features), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}]
    chunks, retained_ids = [], set()
    for path in sorted(directory.glob('*.json.gz')):
        value = json.loads(gzip.decompress(path.read_bytes()))
        found = {f['attributes'][oid] for f in value['features']}
        if not found.issubset(id_set) or found & retained_ids:
            raise ValueError(f'Overlapping or changed cached page population: {path}')
        retained_ids.update(found)
        chunks.append({'path': path.name, 'rows': len(value['features']),
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    remaining = [i for i in ids if i not in retained_ids]
    for start in range(0, len(remaining), 900):
        group = remaining[start:start + 900]
        chunks.extend(fetch(group, f'ids-{group[0]}-{group[-1]}'))
    ending = query(url, where='1=1', returnIdsOnly='true')
    end_count = query(url, where='1=1', returnCountOnly='true')['count']
    rows = sum(p['rows'] for p in chunks)
    if ids != sorted(set(ending.get('objectIds') or [])) or rows != count or count != end_count:
        raise RuntimeError(f'{url}: changing or incomplete population: start={count}, retained={rows}, end={end_count}')
    result = {'url': url, 'name': layer['name'], 'captured_from': started,
              'captured_through': datetime.now(timezone.utc).isoformat(),
              'oid_field': oid, 'rows': rows, 'unique_oids': len(ids), 'pages': chunks}
    store = store_root(output)
    for page in chunks:
        adopt(store, directory / page['path'])
    write_json(directory / 'release.json', result)
    print(service, layer['id'], rows, 'complete', flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--campaign', action='store_true', help='Also acquire all publisher-linked campaign files')
    parser.add_argument('--refresh-metadata', action='store_true', help='Rediscover layers within the admitted services')
    args = parser.parse_args()
    if args.refresh_metadata:
        if list(args.output.glob('sit/*/*/*/*.gz')):
            parser.error('Refresh into a new destination; source changes must not be combined with cached pages')
        for path in args.metadata.glob('*--*.json'):
            service = path.stem.replace('--', '/')
            url = 'https://webapps.sit.puglia.it/arcgis/rest/services/' + service + '/MapServer/layers?f=pjson'
            value = json.loads(request(url))
            if 'layers' not in value:
                raise RuntimeError(f'Cannot discover {service}')
            write_json(path, value)
    if args.campaign:
        capture_campaign(args.output)
    failures = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(capture_layer, item): item for item in prepare(args.metadata, args.output)}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as error:
                item = futures[future]
                failures.append((item[1], item[2]['id'], str(error)))
                print('FAILED', failures[-1], flush=True)
    if failures:
        raise SystemExit(f'{len(failures)} layers incomplete; see console. Completed releases remain reusable.')
    # The campaign releases publish longitude and latitude and state no datum anywhere, so
    # the frame the reader gives them is established from this publisher's own redundancy
    # rather than from a statement, and a republication in another datum would move every
    # one of their locations while stating nothing about it. The establishment is therefore
    # re-derived on any acquisition, not only a campaign one: the equation has two sides,
    # and the SIT geometry is the side it is measured against - for the three releases that
    # publish no observation reference it is the only ground there is. Guarding the side
    # that carries the unstated frame leaves the reference side free to move unchecked.
    # Derive the readings first, because the check reads them and a capture is not a reading.
    from cordon_d.monitoring import ingest  # noqa: E402
    ingest(args.output)
    check = Path(__file__).with_name('check_frames.py')
    raise SystemExit(subprocess.call([sys.executable, str(check), str(args.output)]))


if __name__ == '__main__':
    main()

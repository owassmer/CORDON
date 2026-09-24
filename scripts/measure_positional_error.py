"""Measure the local positional error of the adopted-area geometry sources.

Cadastre (`cordon_d.area_error`): the Region's surveyed control fixes against the SIT
cadastral map.

    windows --control C.json   capture the cadastral map (SIT Background/Catasto layer 1
                               buildings, layer 2 parcels) in a 400 m square around every
                               fix in a comune whose sheets are held
    measure                    match every fix by consensus; write each fix's error to
                               corpus/sources/areas/cadastral-control.json and the
                               `positional-error` record for the cadastre
    layers                     measure the Region's published zone layer against the
                               cadastral outline where the act fixes the line by listed
                               units; write its `positional-error` records
    localities                 per held comune, how far away the fixes giving its error
                               lie; written into the cadastre's record

`C.json` lists the retained Rete Planoaltimetrica pages (ServicesArcIMS/RetiGeodetiche
layer 0). Run with the Stage C/D environment:
PYTHONPATH=regulation/stage-c:regulation/stage-d .venv/bin/python scripts/measure_positional_error.py measure
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
import argparse
import json
import time
import urllib.request

import numpy
import shapely
from shapely.geometry import Point

from cordon_d import area_error as E
from cordon_d.administrative import RECORDS, AdministrativeUnits, records
from cordon_d.store import blob_path, put_bytes, store_root

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'corpus/sources/areas/cadastral-control.json'
CATASTO = 'https://webapps.sit.puglia.it/arcgis/rest/services/Background/Catasto/MapServer'
HALF_M = 200.0
METHOD = (
    "Fixes: the Region's surveyed control points (ServicesArcIMS/RetiGeodetiche layer 0), 'Appoggio Catastali' "
    "and 'Fotografici Appoggio', in a comune whose cadastral sheets are held, that name a feature the cadastral "
    "map draws: a boundary triple point, a wall or fence corner, or a building corner. Photo-control building "
    "corners are left out: they are chosen to be seen from the air, and the map omits many of those buildings. "
    "Map features: SIT Background/Catasto parcels (layer 2) or buildings (layer 1) in a 400 m square around each "
    "fix; a triple point is a vertex three or more parcels share, a wall corner a parcel corner, a building corner "
    "the compass corner the fix names, else any building corner. Match: per fix, its 20 nearest fixes vote on a "
    "2 m grid for the map offset that places most of them within 3 m of a feature of their kind; the fix's error "
    "is the distance from its surveyed coordinate to the feature nearest that offset. Every matched fix counts, "
    "on the consensus or not. A place's error is the 95th percentile of the errors of the 20 fixes nearest it.")


def _get(url):
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'CORDON'}),
                                        timeout=120) as response:
                return response.read()
        except Exception as error:  # noqa: BLE001
            last = error
            time.sleep(4 * (attempt + 1))
    raise last


def fixes(root, control_pages):
    """The control fixes in comuni whose sheets are held, with the map feature kind they name."""
    store = store_root(root)
    units = AdministrativeUnits(root)
    held = sorted({r['selection']['comune'] for r in records(root, 'cadastre-fogli')})
    territory = {c: units.comune_geometry(units.comune(catastale=c)) for c in held}
    codes = list(territory)
    tree = shapely.STRtree([territory[c] for c in codes])
    out = []
    for page in control_pages:
        if page['layer'] != 0:
            continue
        for f in json.loads(blob_path(store, page['sha256']).read_bytes())['features']:
            a = f['attributes']
            kind = E.feature_kind(a['DESCR'])
            if a['LEGENDA'] not in ('Appoggio Catastali', 'Fotografici Appoggio') or kind is None:
                continue
            if a['LEGENDA'] == 'Fotografici Appoggio' and kind == 'building':
                continue
            point = Point(f['geometry']['x'], f['geometry']['y'])
            hit = tree.query(point, predicate='within')
            if len(hit):
                out.append({'id': a['OBJECTID'], 'vertice': a['VERTICE'], 'legend': a['LEGENDA'],
                            'description': a['DESCR'], 'kind': kind, 'comune': codes[hit[0]],
                            'x': round(point.x, 3), 'y': round(point.y, 3)})
    return out


def window_url(fix, offset=0):
    layer = 1 if fix['kind'] == 'building' else 2
    envelope = [fix['x'] - HALF_M, fix['y'] - HALF_M, fix['x'] + HALF_M, fix['y'] + HALF_M]
    return layer, f'{CATASTO}/{layer}/query?' + urlencode({
        'f': 'json', 'geometry': ','.join(map(str, envelope)), 'geometryType': 'esriGeometryEnvelope',
        'inSR': '32633', 'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'COMUNE,SEZIONE,FOGLIO,NUMERO,OBJECTID' + (',LIVELLO' if layer == 2 else ''),
        'returnGeometry': 'true', 'outSR': '32633', 'orderByFields': 'OBJECTID',
        'resultOffset': offset, 'resultRecordCount': 1000})


def windows(args):
    store = store_root(ROOT)
    control = json.loads(Path(args.control).read_text())
    found = fixes(ROOT, control['pages'])

    def one(fix):
        pages, offset = [], 0
        while True:
            layer, url = window_url(fix, offset)
            body = _get(url)
            data = json.loads(body)
            if 'error' in data:
                raise RuntimeError(f"{url}: {data['error']}")
            n = len(data.get('features', []))
            pages.append({'url': url, 'sha256': put_bytes(store, body), 'features': n,
                          'captured_at': datetime.now(timezone.utc).isoformat(timespec='seconds')})
            offset += n
            if not data.get('exceededTransferLimit') and n < 1000:
                return {'fix': fix['id'], 'layer': layer, 'pages': pages}

    with ThreadPoolExecutor(4) as pool:
        captured = list(pool.map(one, found))
    CONTROL.write_text(json.dumps({'control': control, 'windows': captured, 'fixes': found}, indent=0) + '\n')
    print('fixes', len(found), 'windows', len(captured))


def measure(args):
    store = store_root(ROOT)
    document = json.loads(CONTROL.read_text())
    by_fix = {w['fix']: w for w in document['windows']}
    found = document['fixes']
    inputs = []
    for fix in found:
        features = []
        for page in by_fix[fix['id']]['pages']:
            features += json.loads(blob_path(store, page['sha256']).read_bytes())['features']
        inputs.append(((fix['x'], fix['y']), E.candidates(fix['kind'], fix['description'], features)))
    results = E.consensus(inputs)
    for fix, result in zip(found, results):
        for key in ('offset', 'error_m', 'on_consensus'):
            fix.pop(key, None)
        if result is not None:
            offset, error, on = result
            fix.update(offset=[round(v, 2) for v in offset], error_m=round(error, 2), on_consensus=on)
    CONTROL.write_text(json.dumps(document, indent=0) + '\n')
    measured = [f for f in found if 'error_m' in f]
    field = E.ErrorField(numpy.array([[f['x'], f['y']] for f in measured]), numpy.array([f['error_m'] for f in measured]))
    xy = [[f['x'], f['y']] for f in measured]
    local, radius = field.at(xy), field.radius(xy)
    units = AdministrativeUnits(ROOT)
    comuni = []
    for code in sorted({f['comune'] for f in measured}):
        at = [i for i, f in enumerate(measured) if f['comune'] == code]
        comuni.append({'comune': code, 'name': units.comune(catastale=code).name, 'fixes': len(at),
                       'error_m': {'median': round(float(numpy.median(local[at])), 1),
                                   'max': round(float(local[at].max()), 1)},
                       'neighbourhood_radius_m': round(float(numpy.median(radius[at])))})
    errors = numpy.array([f['error_m'] for f in measured])
    record = {
        'kind': 'positional-error', 'source': 'cadastre', 'method': METHOD,
        'statistic': f'{E.PERCENTILE}th percentile of the errors of the {E.K} fixes nearest a place',
        'evidence': str(CONTROL.relative_to(ROOT)), 'fixes': len(found), 'measured': len(measured),
        'on_consensus': sum(1 for f in measured if f['on_consensus']),
        'consensus_offset_m': {'median': round(float(numpy.median([numpy.hypot(*f['offset']) for f in measured])), 2),
                               'max': round(float(max(numpy.hypot(*f['offset']) for f in measured)), 2)},
        'fix_error_m': {'p50': round(float(numpy.percentile(errors, 50)), 1),
                        'p95': round(float(numpy.percentile(errors, 95)), 1), 'max': round(float(errors.max()), 1)},
        'local_error_m': {'median': round(float(numpy.median(local)), 1),
                          'p95': round(float(numpy.percentile(local, 95)), 1), 'max': round(float(local.max()), 1)},
        'neighbourhood_radius_m': {'median': round(float(numpy.median(radius))), 'max': round(float(radius.max()))},
        'comuni': comuni, 'script': 'scripts/measure_positional_error.py',
        'measured_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    _replace(lambda r: r['kind'] == 'positional-error' and r['source'] == 'cadastre', [record])
    print(json.dumps({k: v for k, v in record.items() if k not in ('comuni', 'method')}, indent=1))


def _replace(drop, new):
    path = ROOT / RECORDS
    kept = [r for r in json.loads(path.read_text()) if not drop(r)]
    path.write_text(json.dumps(kept + new, indent=1, ensure_ascii=False) + '\n')


ISTAT_METHOD = (
    "Only where a zone's outline is ISTAT's own line: a comune whose missing sheets are the territory no held "
    "sheet covers. Directed distances sampled every 10 m between the comune's ISTAT border with each adjacent "
    "comune and the cadastral border between their sheets (each comune's sheets unioned and closed by 10 m; "
    "the cadastral border is the part of one comune's sheet outline within 5 m of the other's sheets). Per "
    "comune: the 95th percentile and maximum of each direction; the comune's bound is the larger 95th "
    "percentile. Where ISTAT and the cadastre disagree, the cadastre settles the line; this bound applies only "
    "to the line no sheet draws.")


def _border_samples(line, step=10.0):
    out = [shapely.line_interpolate_point(p, numpy.linspace(0, p.length, max(2, int(p.length // step) + 1)))
           for p in getattr(line, 'geoms', [line]) if p.length > 0]
    return numpy.concatenate(out) if out else numpy.array([], dtype=object)


def _lines(g):
    return shapely.line_merge(shapely.union_all([p for p in getattr(g, 'geoms', [g])
                                                 if p.geom_type in ('LineString', 'MultiLineString')]))


def istat(args):
    """ISTAT's boundary error per comune, along its borders with neighbours whose sheets are held."""
    from cordon_d.area_geometry import Sources
    sources = Sources(ROOT)
    units = sources.administrative
    sheets = {}
    for (code, _, _), found in sources.sheets.items():
        sheets.setdefault(code, []).extend(shapely.make_valid(g) for _, g in found)
    wanted = set()
    for code in args.comuni:
        territory = units.comune_geometry(units.comune(catastale=code)).buffer(5.0)
        wanted |= {c for c in sheets if units.comune_geometry(units.comune(catastale=c)).intersects(territory)}
    closed = {c: shapely.union_all(sheets[c]).buffer(10, join_style='mitre').buffer(-10, join_style='mitre')
              for c in sorted(wanted)}
    comuni = []
    for code in args.comuni:
        territory = shapely.make_valid(units.comune_geometry(units.comune(catastale=code)))
        i2c, c2i = [], []
        for other in sorted(closed):
            if other == code:
                continue
            neighbour = shapely.make_valid(units.comune_geometry(units.comune(catastale=other)))
            border = _lines(territory.boundary.intersection(neighbour.buffer(1.0)))
            if border.is_empty or border.length < 100 or code not in closed:
                continue
            cadastral = _lines(closed[code].boundary.intersection(closed[other].buffer(5.0)))
            if cadastral.is_empty:
                continue
            i2c.append(shapely.distance(_border_samples(border), cadastral))
            c2i.append(shapely.distance(_border_samples(cadastral), border))

        def stats(arrays):
            d = numpy.concatenate(arrays) if arrays else numpy.array([])
            return None if not d.size else {'p95': round(float(numpy.percentile(d, 95)), 1),
                                            'max': round(float(d.max()), 1), 'n': int(d.size)}
        comuni.append({'comune': code, 'name': units.comune(catastale=code).name,
                       'istat_to_cadastre': stats(i2c), 'cadastre_to_istat': stats(c2i)})
        print(comuni[-1])
    record = {'kind': 'positional-error', 'source': 'istat-boundaries', 'method': ISTAT_METHOD,
              'statistic': 'per comune: the larger 95th percentile of the two directed distance samples',
              'istat_note': ("La scala non è certificabile uniformemente dall'Istat, poichè le basi di acquisizione "
                             "utilizzate (principalmente foto aeree ed altra cartografia) provengono da fonti e scale "
                             "differenti, che variano tra ambito urbano ed extraurbano."),
              'istat_note_source': 'https://www.istat.it/wp-content/uploads/2024/04/Descrizione-dati-Confini-unita-amministrative-fini-statistici.pdf',
              'comuni': comuni, 'script': 'scripts/measure_positional_error.py',
              'measured_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    _replace(lambda r: r['kind'] == 'positional-error' and r['source'] == 'istat-boundaries', [record])


def layers(args):
    """The Region's layer against the cadastral outline of the units the act places wholly in a zone."""
    from cordon_d.area_geometry import Sources, adopted_geography, region_layer_samples, REGION_REACH_M
    sources = Sources(ROOT)
    out = []
    for geography in adopted_geography(ROOT, decision=date.fromisoformat(args.decision), sources=sources,
                                       only=set(args.version)):
        for record, samples in region_layer_samples(sources, geography):
            distances = numpy.array([d for _, _, d in samples])
            out.append({'kind': 'positional-error', 'source': 'region-layer', 'layer': record['layer'],
                        'name': record['name'], 'sha256': record['sha256'], 'role': record['role'],
                        'provision_version_id': geography.provision_version_id,
                        'method': ("Directed distances sampled every 10 m from the zone's outer limit where the act "
                                   "fixes it by units it places wholly in the zone (the cadastral outline of those "
                                   "units, on land outside the zone) to the layer's outline. A place's error is the "
                                   f"95th percentile of the samples within {REGION_REACH_M / 1000:g} km of it. "
                                   "The layer's ground error there is that value plus the cadastre's own ground "
                                   "error there (triangle inequality)."),
                        'samples': [[round(x), round(y), round(float(d), 1)] for x, y, d in samples],
                        'error_m': {'median': round(float(numpy.median(distances)), 1),
                                    'p95': round(float(numpy.percentile(distances, 95)), 1),
                                    'max': round(float(distances.max()), 1), 'n': int(len(distances))},
                        'script': 'scripts/measure_positional_error.py',
                        'measured_at': datetime.now(timezone.utc).isoformat(timespec='seconds')})
            print(record['layer'], record['name'], out[-1]['error_m'])
    _replace(lambda r: (r['kind'] == 'positional-error' and r['source'] == 'region-layer'
                        and r['provision_version_id'] in args.version), out)


LOCALITY_METHOD = (
    "Per comune whose sheets are held, at the centroid of each of its sheets: the distance to the nearest measured "
    f"fix and to the {E.K}th nearest (the fixes whose errors give the place's value), and how many of those "
    f"{E.K} fixes lie in the comune. Where they lie far away the value is measured elsewhere, not locally; the "
    "distance says how far.")


def localities(args):
    """How far from each held comune the fixes giving its error lie; written into the cadastre record."""
    from scipy.spatial import cKDTree
    from cordon_d.area_geometry import Sources
    sources = Sources(ROOT)
    document = json.loads(CONTROL.read_text())
    measured = [f for f in document['fixes'] if 'error_m' in f]
    xy = numpy.array([[f['x'], f['y']] for f in measured])
    comune_of = numpy.array([f['comune'] for f in measured])
    field = E.ErrorField(xy, numpy.array([f['error_m'] for f in measured]))
    tree = cKDTree(xy)
    centroids = {}
    for (code, _, _), found in sources.sheets.items():
        centroids.setdefault(code, []).extend(shapely.get_coordinates(g.centroid)[0] for _, g in found)
    units = sources.administrative
    rows = []
    for code in sorted(centroids):
        at = numpy.array(centroids[code])
        distance, index = tree.query(at, k=E.K)
        inside = (comune_of[index] == code).sum(axis=1)
        error = field.at(at)
        rows.append({'comune': code, 'name': units.comune(catastale=code).name, 'sheets': int(len(at)),
                     'fixes_in_comune': int((comune_of == code).sum()),
                     'nearest_fix_m': {'median': round(float(numpy.median(distance[:, 0]))),
                                       'max': round(float(distance[:, 0].max()))},
                     f'fix_{E.K}_m': {'median': round(float(numpy.median(distance[:, -1]))),
                                      'max': round(float(distance[:, -1].max()))},
                     f'of_{E.K}_in_comune': {'median': int(numpy.median(inside)), 'min': int(inside.min())},
                     'error_m': {'median': round(float(numpy.median(error)), 1), 'max': round(float(error.max()), 1)}})
    path = ROOT / RECORDS
    kept = json.loads(path.read_text())
    record = next(r for r in kept if r['kind'] == 'positional-error' and r['source'] == 'cadastre')
    record['locality_method'] = LOCALITY_METHOD
    record['localities'] = rows
    path.write_text(json.dumps(kept, indent=1, ensure_ascii=False) + '\n')
    far = sorted(rows, key=lambda r: -r[f'fix_{E.K}_m']['median'])
    for r in far[:15]:
        print(r['comune'], r['name'], r['fixes_in_comune'], r['nearest_fix_m'], r[f'fix_{E.K}_m'], r['error_m'])


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    w = sub.add_parser('windows')
    w.add_argument('--control', required=True)
    sub.add_parser('measure')
    ist = sub.add_parser('istat')
    ist.add_argument('comuni', nargs='+', help='cadastral codes of the comuni whose outline ISTAT draws')
    lay = sub.add_parser('layers')
    lay.add_argument('--decision', default='2026-09-22')
    lay.add_argument('version', nargs='+', help='the provision version ids whose layers are measured, one '
                     'version per run to bound memory')
    sub.add_parser('localities')
    args = parser.parse_args()
    {'windows': windows, 'measure': measure, 'istat': istat, 'layers': layers,
     'localities': localities}[args.command](args)


if __name__ == '__main__':
    main()

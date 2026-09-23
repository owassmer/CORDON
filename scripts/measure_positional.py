"""Measure the positional error of located positives from retained chips and control points.

    python scripts/measure_positional.py population --positives POSITIVES.csv --frame FRAME.json --requests R.json
    python scripts/acquire_positional.py chips R.json
    python scripts/measure_positional.py vertices --frame FRAME.json --vertices V.json --requests CR.json
    python scripts/acquire_positional.py chips CR.json --records corpus/sources/positional-reference/control-chips.jsonl
    python scripts/acquire_positional.py register POSITIVES.csv
    python scripts/measure_positional.py control  --control-chips C.jsonl --vertices V.json --out FIT.json
    python scripts/measure_positional.py measure  --frame FRAME.json --chips A.jsonl [B.jsonl ...]
                                                  --fit FIT.json --out RESULTS.jsonl [--workers 4]
    python scripts/measure_positional.py table    --positives POSITIVES.csv --frame FRAME.json
                                                  --results RESULTS.jsonl --out-table T.json --out-rows Q.csv

`population` reads every located positive from the ordinary reader and fixes the frame before any
chip is read. `vertices` selects the ground-level control vertices near it. `control` locates
every ground-level control vertex in every image year and fits each year's local shift with its
leave-one-out residuals. `measure` applies `cordon_d.positional.measure` to every positive of
the frame (bracketed by imagery, under a single-plant removal rule), with every other held image
for the persistence rule; it appends and resumes. `table` states
every located positive's status and error, and the per-release counts and bound.
"""
import argparse
import csv
from datetime import date
import json
from multiprocessing import Pool
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]
from cordon_d import positional as P  # noqa: E402
from cordon_d.store import blob_path, store_root  # noqa: E402

TILE_M = 20000  # reporting cell for fitted shifts; the 2015-2023 services publish no tile footprints


CARRY = ['DATA_ESTIRPAZIONE', 'RIF_DECRETO', 'MONUMENTALE_ARIF', 'ZONA', 'ZONA_DELIMITATA',
         'FOGLIO', 'PARTICELLA', 'COD_COMUNE', 'PROT_SELGE']
CONTROL_REACH_M = 15000  # control vertices read within this distance of a frame positive


def population(args):
    """Every located positive of the ordinary reader; the frame (bracketed by held imagery, under a
    single-plant removal rule); and chip requests for every held image of every frame positive."""
    from pyproj import Transformer
    from cordon_d.monitoring import distinct_observations
    to_utm = Transformer.from_crs('EPSG:4326', 'EPSG:32633', always_xy=True)
    frame, requests, located = [], {}, 0
    with open(args.positives, 'w', newline='') as stream:
        w = csv.writer(stream)
        w.writerow(['identity', 'reference', 'day', 'year', 'releases', 'views', 'n_members', 'species', 'crs', 'x',
                    'y', 'e32633', 'n32633', 'removal_layer'] + CARRY)
        for g in distinct_observations(ROOT / 'corpus/sources/monitoring'):
            if g.positive is not True or not g.locations:
                continue
            located += 1
            crs, (x, y) = g.locations[0]
            e, n = (x, y) if crs == 'EPSG:32633' else to_utm.transform(x, y)
            carried = {}
            for m in g.members:
                for k, v in m.carried:
                    if k in CARRY and v not in (None, ''):
                        carried.setdefault(k, set()).add(str(v))
            views = sorted({m.view or '' for m in g.members})
            releases = sorted({(m.release or '').rsplit('/', 1)[-1] for m in g.members})
            identity = '|'.join(map(str, g.identity))
            row = [identity, g.reference, g.day, g.day.year if g.day else '', '|'.join(releases), '|'.join(views),
                   len(g.members), '|'.join(sorted({m.species for m in g.members if m.species})), crs, x, y,
                   round(e, 3), round(n, 3), int(any('estirpat' in (m.view or '').lower() for m in g.members))]
            w.writerow(row + ['|'.join(sorted(carried.get(k, ()))) for k in CARRY])
            e, n = round(e, 3), round(n, 3)
            zones = ['|'.join(sorted(carried.get(k, ()))) for k in ('ZONA', 'ZONA_DELIMITATA')]
            pair = P.bracket(g.day, e, n) if g.day else None
            if pair and P.single_removal_rule(zones, views):
                frame.append({'identity': identity, 'day': g.day.isoformat(), 'e': e, 'n': n, 'pre': pair[0],
                              'post': pair[1], 'release': P.release_of(releases, views, g.day)})
                for year in sum(P.held(g.day, e, n), []):
                    request = P.chip_request(year, e, n, P.CHIP_HALF_M)
                    requests.setdefault(P.chip_key(request), request)
    Path(args.frame).write_text(json.dumps(frame) + '\n')
    Path(args.requests).write_text(json.dumps(list(requests.values())) + '\n')
    print('located positives', located, 'frame', len(frame), 'chip requests', len(requests))


def vertices(args):
    """Ground-level cadastral and photo-control vertices within reach of the frame, and their chip
    requests in every image year that covers them."""
    import numpy as np
    from scipy.spatial import cKDTree
    from cordon_d.store import blob_path
    store = store_root(ROOT)
    found = {}
    for page in json.loads((ROOT / 'corpus/sources/positional-reference/control.json').read_text())['pages']:
        for f in json.loads(blob_path(store, page['sha256']).read_bytes())['features']:
            a = f['attributes']
            found[(page['layer'], a['OBJECTID'])] = {
                'id': f"{page['layer']}:{a['OBJECTID']}:{a['VERTICE']}", 'legend': a['LEGENDA'], 'descr': a['DESCR'],
                'e': f['geometry']['x'], 'n': f['geometry']['y']}
    use = [v for v in found.values()
           if v['legend'] in ('Appoggio Catastali', 'Fotografici Appoggio') and P.ground_level(v['descr'])]
    frame = json.loads(Path(args.frame).read_text())
    distance, _ = cKDTree(np.array([[f['e'], f['n']] for f in frame])).query(np.array([[v['e'], v['n']] for v in use]))
    near = [v for v, d in zip(use, distance) if d <= CONTROL_REACH_M]
    requests = [P.chip_request(year, v['e'], v['n'], P.CONTROL_HALF_M) for year in P.IMAGES for v in near
                if P.IMAGES[year]['extent'][0] <= v['e'] <= P.IMAGES[year]['extent'][2]
                and P.IMAGES[year]['extent'][1] <= v['n'] <= P.IMAGES[year]['extent'][3]]
    Path(args.vertices).write_text(json.dumps(near) + '\n')
    Path(args.requests).write_text(json.dumps(requests) + '\n')
    print('vertices', len(found), 'ground-level control', len(use), 'within reach', len(near), 'requests', len(requests))


def read_records(paths):
    records = {}
    for path in paths:
        for line in Path(path).read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                records[row['key']] = row
    return records


def control(args):
    store = store_root(ROOT)
    vertices = json.loads(Path(args.vertices).read_text())
    records = read_records([args.control_chips])
    offsets = {}
    for v in vertices:
        chips, used = {}, {}
        for year in P.IMAGES:
            key = P.chip_key(P.chip_request(year, v['e'], v['n'], P.CONTROL_HALF_M))
            if key in records:
                chips[year] = P.decode(blob_path(store, records[key]['sha256']).read_bytes())
                used[year] = records[key]
        for year, (dx, dy) in P.locate_vertex(chips).items():
            x0, y0, x1, y1 = used[year]['bbox']
            offsets.setdefault(year, []).append({
                'vertex': v['id'], 'e': v['e'], 'n': v['n'], 'descr': v['descr'], 'chip': used[year]['sha256'],
                'dx': round(dx + (x0 + x1) / 2 - v['e'], 3), 'dy': round(dy + (y0 + y1) / 2 - v['n'], 3)})
    fit = {}
    for year in sorted(offsets):
        rows = offsets[year]
        loo = P.residuals([P.ControlOffset(r['vertex'], r['e'], r['n'], r['dx'], r['dy']) for r in rows])
        values = sorted(loo.values())
        tiles = {}
        for r in rows:
            tiles.setdefault(f"{int(r['e'] // TILE_M) * TILE_M // 1000}E {int(r['n'] // TILE_M) * TILE_M // 1000}N", []).append(r)
        fit[str(year)] = {
            'located': len(rows), 'offsets': rows, 'loo': loo,
            'loo_p95_m': round(percentile(values, 95), 2), 'loo_max_m': round(values[-1], 2),
            'tiles': {t: {'n': len(rs), 'dx_m': round(statistics.median(r['dx'] for r in rs), 2),
                          'dy_m': round(statistics.median(r['dy'] for r in rs), 2)} for t, rs in sorted(tiles.items())}}
        print(year, 'located', len(rows), 'loo p95', fit[str(year)]['loo_p95_m'], 'max', fit[str(year)]['loo_max_m'])
    Path(args.out).write_text(json.dumps(fit, indent=1) + '\n')


def percentile(values, q):
    values = sorted(values)
    k = (len(values) - 1) * q / 100
    lo = int(k)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


_STATE = {}


def _init(chips, fit):
    _STATE['records'] = read_records(chips)
    _STATE['store'] = store_root(ROOT)
    fitted = json.loads(Path(fit).read_text())
    _STATE['control'] = {int(y): ([P.ControlOffset(r['vertex'], r['e'], r['n'], r['dx'], r['dy']) for r in f['offsets']],
                                  f['loo']) for y, f in fitted.items()}


def measure_one(f):
    records, store = _STATE['records'], _STATE['store']
    day = date.fromisoformat(f['day'])
    e, n = f['e'], f['n']
    pre, post = P.bracket(day, e, n)
    before, after = P.held(day, e, n)
    keys = {y: P.chip_key(P.chip_request(y, e, n, P.CHIP_HALF_M)) for y in before + after}
    base = {'identity': f['identity'], 'source': f['release'][0], 'release': f['release'][1], 'day': f['day'],
            'pre': pre, 'post': post}
    missing = sorted(y for y, k in keys.items() if k not in records)
    if missing:
        return {**base, 'status': 'pending', 'missing': missing}
    images = {y: P.decode(blob_path(store, records[k]['sha256']).read_bytes()) for y, k in keys.items()}
    offsets, loo = _STATE['control'].get(pre, ([], {}))
    term = P.imagery_term(offsets, loo, e, n)
    if term is None:
        return {**base, 'status': 'unmeasured', 'cause': f'no control fit for {pre}'}
    x0, y0, x1, y1 = records[keys[pre]]['bbox']
    point = ((y1 - n) / P.PIXEL_M, (e - x0) / P.PIXEL_M)
    others = [('before', y, images[y]) for y in before if y != pre] + [('after', y, images[y]) for y in after if y != post]
    status, detail = P.measure(images[pre], images[post], point, (term[0], term[1]), others)
    row = {**base, 'status': status, **detail, 'correction_m': [round(term[0], 3), round(term[1], 3)],
           'control_vertices': list(term[3]), 'chips': {str(y): records[k]['sha256'] for y, k in keys.items()}}
    if status == 'measured':
        row['imagery_m'] = term[2]
        row['grid_m'] = round(P.grid_to_ground_m(e, n, detail['distance_m']), 4)
    return row


def measure(args):
    frame = json.loads(Path(args.frame).read_text())
    out = Path(args.out)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            row = json.loads(line)
            if row['status'] != 'pending':
                done.add(row['identity'])
    todo = [f for f in frame if f['identity'] not in done]
    print('frame', len(frame), 'done', len(done), 'to measure', len(todo), flush=True)
    counts = {}
    with Pool(args.workers, _init, (args.chips, args.fit)) as pool, out.open('a') as stream:
        for i, row in enumerate(pool.imap(measure_one, todo, chunksize=4), 1):
            if row['status'] != 'pending':
                stream.write(json.dumps(row, separators=(',', ':')) + '\n')
            counts[row['status']] = counts.get(row['status'], 0) + 1
            if i % 250 == 0:
                stream.flush()
                print(i, counts, flush=True)
    print('finished', counts, flush=True)


def table(args):
    frame = {f['identity']: f for f in json.loads(Path(args.frame).read_text())}
    results = {}
    for line in Path(args.results).read_text().splitlines():
        row = json.loads(line)
        results[row['identity']] = row
    rows, positives = [], {}
    for p in csv.DictReader(open(args.positives, newline='')):
        positives[p['identity']] = p
        day = date.fromisoformat(p['day'])
        if p['identity'] in results:
            rows.append(results[p['identity']])
            continue
        source, release = P.release_of(p['releases'].split('|'), p['views'].split('|'), day)
        e, n = float(p['e32633']), float(p['n32633'])
        if p['identity'] in frame:
            cause = 'measurement pending'
        elif P.bracket(day, e, n) is None:
            cause = 'no held image after the finding' if P.held(day, e, n)[0] else 'no held image before the finding'
        else:
            cause = 'no single-plant removal rule'
        rows.append({'identity': p['identity'], 'source': source, 'release': release, 'day': p['day'],
                     'status': 'out_of_reach' if cause != 'measurement pending' else 'unmeasured', 'cause': cause})
    bounds = P.release_bounds(rows)
    for key, entry in bounds.items():
        causes = {}
        for r in rows:
            if (r['source'], r['release']) == key and r['status'] != 'measured':
                causes[r['cause']] = causes.get(r['cause'], 0) + 1
        entry['causes'] = causes
    register = {}
    if args.register:
        held = json.loads(Path(args.register).read_text())
        provisional = held['provisional']['trees']
        register = {r['identity']: r['trees'] + provisional for r in held['near']}
    for entry in bounds.values():
        entry['register'] = {'flagged_with_error': 0, 'refuted': 0, 'beyond_reach': 0}
    with open(args.out_rows, 'w', newline='') as stream:
        w = csv.writer(stream)
        w.writerow(['identity', 'source', 'release', 'day', 'status', 'cause', 'pre', 'post', 'candidates',
                    'distance_m', 'imagery_m', 'grid_m', 'error_m', 'error_basis', 'n', 'register_refutes'])
        for r in rows:
            entry = bounds[(r['source'], r['release'])]
            if r['status'] == 'measured':
                error, basis, n = round(r['distance_m'] + r['imagery_m'] + r['grid_m'], 2), 'own measurement', ''
            elif r['status'] == 'unmeasured' and entry['bound_m'] is not None:
                error, basis, n = entry['bound_m'], 'release bound', entry['measured']
            else:
                error, basis, n = '', 'none', ''
            refutes = ''
            if error != '' and r['identity'] in register:
                p = positives[r['identity']]
                verdict = P.register_refutes(float(p['e32633']), float(p['n32633']), error, register[r['identity']])
                entry['register']['flagged_with_error'] += 1
                entry['register']['beyond_reach' if verdict is None else 'refuted'] += verdict is not False
                refutes = '' if verdict is None else verdict
            w.writerow([r['identity'], r['source'], r['release'], r['day'], r['status'], r.get('cause', ''),
                        r.get('pre', ''), r.get('post', ''), len(r.get('candidates', [])) if r['status'] == 'measured' else '',
                        r.get('distance_m', ''), r.get('imagery_m', ''), r.get('grid_m', ''), error, basis, n, refutes])
    out = [{'source': s, 'release': rel, **entry} for (s, rel), entry in sorted(bounds.items())]
    Path(args.out_table).write_text(json.dumps(out, indent=1) + '\n')
    for e in out:
        print(f"{e['source']:18} {e['release']:28} measured {e['measured']:5} unmeasured {e['unmeasured']:5} "
              f"out {e['out_of_reach']:5} max {e['max_distance_m']} imagery {e['imagery_m']} bound {e['bound_m']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('population')
    p.add_argument('--positives', required=True)
    p.add_argument('--frame', required=True)
    p.add_argument('--requests', required=True)
    v = sub.add_parser('vertices')
    v.add_argument('--frame', required=True)
    v.add_argument('--vertices', required=True)
    v.add_argument('--requests', required=True)
    c = sub.add_parser('control')
    c.add_argument('--control-chips', required=True)
    c.add_argument('--vertices', required=True)
    c.add_argument('--out', required=True)
    m = sub.add_parser('measure')
    m.add_argument('--frame', required=True)
    m.add_argument('--chips', nargs='+', required=True)
    m.add_argument('--fit', required=True)
    m.add_argument('--out', required=True)
    m.add_argument('--workers', type=int, default=4)
    t = sub.add_parser('table')
    t.add_argument('--positives', required=True)
    t.add_argument('--frame', required=True)
    t.add_argument('--results', required=True)
    t.add_argument('--out-table', required=True)
    t.add_argument('--out-rows', required=True)
    t.add_argument('--register', help="acquire_positional.py register's record, to refute bounds")
    args = parser.parse_args()
    {'population': population, 'vertices': vertices, 'control': control, 'measure': measure,
     'table': table}[args.command](args)

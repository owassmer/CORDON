"""Measure the positional error of the adopted-area geometry sources; write `positional-error` records.

The two sources are two independent official outlines of the same comuni: ISTAT's
non-generalised boundaries and the union of each comune's cadastral sheets. Where two
adjacent comuni both have their sheets held, the ISTAT border is the line their ISTAT
polygons share, and the cadastral border is the part of one comune's sheet outline that
abuts the other comune's sheets. Coast and borders with a comune whose sheets are not held
have no second outline and are not measured.

Directed distances are sampled every 10 m: ISTAT border to cadastral border, and
cadastral border to ISTAT border. Per comune: the 95th percentile and the maximum of each
direction.

- istat-boundaries: the borders that lie on the outline of a zone built from ISTAT
  boundaries, for any consumed version in reach; the comuni are those with such a border.
- cadastre: every measured border of each comune whose sheets a zone uses.

`error_m` is the largest per-comune 95th percentile over the source's comuni, either
direction. Run with the Stage C/D environment:
PYTHONPATH=regulation/stage-c:regulation/stage-d .venv/bin/python scripts/measure_positional_error.py
"""
from datetime import date, datetime, timezone
from pathlib import Path
import json

import numpy
import shapely
from shapely import STRtree

from cordon_d.administrative import RECORDS
from cordon_d.area_geometry import Sources, adopted_geography
from cordon_d.areas import versions

ROOT = Path(__file__).resolve().parents[1]
STEP, CLOSE, TOUCH, SNAP, ON = 10.0, 10.0, 5.0, 1.0, 1.0
METHOD = ('Directed distances sampled every 10 m between the ISTAT border of two adjacent comuni and '
          'the cadastral border between their sheets (each comune\'s sheets unioned and closed by 10 m '
          'so seams between sheets are not boundary; the cadastral border is the part of one comune\'s '
          'sheet outline within 5 m of the other\'s sheets). Coast and borders with a comune whose sheets '
          'are not held are not measured. Per comune: 95th percentile and maximum of each direction. '
          'error_m is the largest per-comune 95th percentile over the listed comuni, either direction.')


def _samples(line):
    out = [shapely.line_interpolate_point(p, numpy.linspace(0, p.length, max(2, int(p.length // STEP) + 1)))
           for p in getattr(line, 'geoms', [line]) if p.length > 0]
    return numpy.concatenate(out) if out else numpy.array([], dtype=object)


def _nearest(points, line):
    pieces = []
    for part in getattr(line, 'geoms', [line]):
        c = numpy.asarray(part.coords)
        if len(c) > 1:
            pieces.append(shapely.linestrings(numpy.stack([c[:-1], c[1:]], axis=1)))
    _, d = STRtree(numpy.concatenate(pieces)).query_nearest(points, return_distance=True, all_matches=False)
    return d


def _lines(g):
    return shapely.line_merge(shapely.union_all([p for p in getattr(g, 'geoms', [g])
                                                 if p.geom_type in ('LineString', 'MultiLineString')]))


def _stats(arrays):
    d = numpy.concatenate(arrays) if arrays else numpy.array([])
    if not d.size:
        return None
    return {'p95': round(float(numpy.percentile(d, 95)), 1), 'max': round(float(d.max()), 1), 'n': int(d.size)}


def measure(root: Path, decision: date):
    sources = Sources(root)
    units = sources.administrative
    istat_outline, cad_used = [], set()
    supplied = {g.provision_version_id: g for g in adopted_geography(root, decision=decision, sources=sources)}
    for g in supplied.values():
        for z in g.zones:
            if z.geometry is not None and not z.geometry.is_empty and 'istat-boundaries' in z.sources:
                istat_outline.append(z.geometry.boundary)
    for v in versions(root):
        if v.provision_version_id in supplied:
            for s in v.statements or ():
                if s.scope == 'sheets':
                    cad_used.add(units.comune(name=s.comune, province=s.province).catastale)
    on_outline = shapely.union_all(istat_outline).buffer(ON)
    shapely.prepare(on_outline)
    by_comune = {}
    for (comune, _, _), features in sources.sheets.items():
        by_comune.setdefault(comune, []).extend(g for _, g in features)
    istat, cad = {}, {}
    for code, sheets in sorted(by_comune.items()):
        comune = units.comune(catastale=code)
        if comune is None:
            continue
        istat[code] = shapely.make_valid(units.comune_geometry(comune))
        union = shapely.union_all([shapely.make_valid(g) for g in sheets])
        cad[code] = union.buffer(CLOSE, join_style='mitre').buffer(-CLOSE, join_style='mitre')
    codes = sorted(istat)
    tree = STRtree([istat[c] for c in codes])
    found = {c: {'istat-boundaries': ([], []), 'cadastre': ([], [])} for c in codes}
    for a in codes:
        for j in tree.query(istat[a].buffer(SNAP)):
            b = codes[j]
            if b <= a:
                continue
            border = _lines(istat[a].boundary.intersection(istat[b].buffer(SNAP)))
            if border.is_empty or border.length < 100:
                continue
            for side, other in ((a, b), (b, a)):
                cadastral = _lines(cad[side].boundary.intersection(cad[other].buffer(TOUCH)))
                if cadastral.is_empty:
                    continue
                ip, cp = _samples(border), _samples(cadastral)
                i2c, c2i = _nearest(ip, cadastral), _nearest(cp, border)
                if side in cad_used:
                    found[side]['cadastre'][0].append(i2c)
                    found[side]['cadastre'][1].append(c2i)
                on = shapely.intersects(on_outline, ip)
                if on.any():
                    foot = shapely.get_point(shapely.shortest_line(cp, border), 1)
                    found[side]['istat-boundaries'][0].append(i2c[on])
                    found[side]['istat-boundaries'][1].append(c2i[shapely.intersects(on_outline, foot)])
    out = []
    for source, scope in (('istat-boundaries', 'borders on the outline of a zone built from ISTAT boundaries'),
                          ('cadastre', 'every measured border of a comune whose sheets a zone uses')):
        comuni = []
        for code in codes:
            i2c, c2i = (_stats(found[code][source][0]), _stats(found[code][source][1]))
            if i2c or c2i:
                comuni.append({'comune': code, 'name': units.comune(catastale=code).name,
                               'istat_to_cadastre': i2c, 'cadastre_to_istat': c2i})
        p95 = [(d['p95'], c['name']) for c in comuni for d in (c['istat_to_cadastre'], c['cadastre_to_istat']) if d]
        peak = [(d['max'], c['name']) for c in comuni for d in (c['istat_to_cadastre'], c['cadastre_to_istat']) if d]
        bound, where = max(p95)
        out.append({'kind': 'positional-error', 'source': source, 'error_m': bound,
                    'statistic': '95th percentile of directed boundary distances, largest over the comuni',
                    'bounding_comune': where, 'largest_maximum_m': max(peak)[0], 'largest_maximum_comune': max(peak)[1],
                    'scope': scope, 'reach_decision': decision.isoformat(), 'method': METHOD,
                    'script': 'scripts/measure_positional_error.py',
                    'measured_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                    'comuni': comuni})
    return out


def main():
    measured = measure(ROOT, date(2026, 9, 22))
    path = ROOT / RECORDS
    kept = [r for r in json.loads(path.read_text()) if r['kind'] != 'positional-error']
    path.write_text(json.dumps(kept + measured, indent=1, ensure_ascii=False) + '\n')
    for r in measured:
        print(r['source'], 'error_m', r['error_m'], r['bounding_comune'], 'comuni', len(r['comuni']),
              'largest maximum', r['largest_maximum_m'], r['largest_maximum_comune'])


if __name__ == '__main__':
    main()

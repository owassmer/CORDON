"""Local positional error of adopted-area geometry, measured against independent fixes.

The cadastral map's error is measured where the Region surveyed a feature the map draws:
its cadastral support points (`Appoggio Catastali`) and the ground-level photo-control
points of the Rete Planoaltimetrica. Each fix is a surveyed coordinate of a named feature: a
boundary triple point, a wall or fence corner, a building corner. The same feature on the
cadastral map is found by consensus: the fixes near one another share the map's local
offset, so the offset that places the most of them on a feature of their kind is the
neighbourhood's, and each fix's error is the distance from its surveyed coordinate to the
map feature nearest that offset. A nearest-feature match alone cannot see an offset larger
than the spacing of the features, so it is not used.

The error of a place is the 95th percentile of the errors of the fixes nearest it. A zone
outline and a parcel carry the error of their own locality, never a maximum taken elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
import re

import numpy

K = 20                  # fixes per neighbourhood
REACH_M = 150.0         # the farthest a map feature is sought from its fix
BIN_M = 2.0             # offset vote cell
TOLERANCE_M = 3.0       # a fix lies on the consensus when a feature is this close to it
PERCENTILE = 95

_DIRECTIONS = (('NORD - EST', (1, 1)), ('NORD - OVEST', (-1, 1)), ('SUD - EST', (1, -1)),
               ('SUD - OVEST', (-1, -1)), ('NORD', (0, 1)), ('SUD', (0, -1)), ('EST', (1, 0)), ('OVEST', (-1, 0)))


def feature_kind(description: str) -> str | None:
    """The kind of map feature a fix describes: triple, building or wall; None if the map draws no such feature."""
    text = (description or '').upper()
    if 'TRIPLICE' in text or 'QUADRUPLICE' in text:
        return 'triple'
    if any(word in text for word in ('FABBRICAT', 'TRULLO', 'BARACCA')):
        return 'building'
    if any(word in text for word in ('RECINZ', 'MURO', 'MURI', 'MURETTO')):
        return 'wall'
    return None


def corner_direction(description: str):
    """The compass corner a building fix names ("SPIGOLO NORD - EST"), as a unit vector, or None."""
    text = re.sub(r'\s*-\s*', ' - ', ' '.join((description or '').upper().replace('–', '-').split()))
    text = re.sub(r'\b(NORD|SUD) (EST|OVEST)\b', r'\1 - \2', text)
    for word, vector in _DIRECTIONS:
        if re.search(r'\b' + re.escape(word) + r'\b', text):
            return vector
    return None


def _rings(geometry):
    for ring in geometry['rings']:
        a = numpy.asarray(ring, dtype=float)
        if len(a) >= 4:
            yield a[:-1] if numpy.allclose(a[0], a[-1]) else a


def _corners(ring, turn_degrees=20.0):
    n = len(ring)
    before, after = ring - ring[numpy.arange(n) - 1], ring[(numpy.arange(n) + 1) % n] - ring
    lb, la = numpy.linalg.norm(before, axis=1), numpy.linalg.norm(after, axis=1)
    ok = (lb > 0.2) & (la > 0.2)
    cosine = numpy.einsum('ij,ij->i', before, after) / numpy.where(ok, lb * la, 1)
    return ring[ok & (cosine < math.cos(math.radians(turn_degrees)))]


def candidates(kind: str, description: str, features) -> numpy.ndarray:
    """Map positions of features of the fix's kind, from Esri polygon features.

    triple: a vertex three or more parcels share. wall: a parcel corner. building: a
    building corner; where the fix names the compass corner, that corner of each building.
    """
    if kind == 'building':
        direction = corner_direction(description)
        found = []
        for f in features:
            rings = [_corners(r) for r in _rings(f['geometry'])]
            vertices = numpy.concatenate(rings) if rings else numpy.empty((0, 2))
            if not len(vertices):
                continue
            if direction is None:
                found.append(vertices)
            else:
                score = vertices @ numpy.asarray(direction, dtype=float)
                found.append(vertices[[score.argmax()]])
        return numpy.concatenate(found) if found else numpy.empty((0, 2))
    owners, corners = {}, []
    for i, f in enumerate(features):
        for ring in _rings(f['geometry']):
            for vertex in map(tuple, numpy.round(ring, 2)):
                owners.setdefault(vertex, set()).add(i)
            corners.append(_corners(ring))
    if kind == 'triple':
        shared = [v for v, o in owners.items() if len(o) >= 3]
        return numpy.array(shared, dtype=float) if shared else numpy.empty((0, 2))
    return numpy.unique(numpy.round(numpy.concatenate(corners), 2), axis=0) if corners else numpy.empty((0, 2))


def consensus(fixes):
    """Per fix: (offset, error_m, on_consensus) from its K-nearest neighbourhood.

    `fixes` is a list of ((x, y), candidate positions). The neighbourhood's offset is the
    one that places the most of its fixes within TOLERANCE_M of a candidate (votes on a
    BIN_M grid, one per fix per cell), refined to the median of the offsets of the candidates
    within TOLERANCE_M of it.
    A fix's error is the distance from its coordinate to the candidate nearest the
    consensus position; a fix without a candidate within REACH_M has no error.
    """
    from scipy.spatial import cKDTree
    offsets = []
    for (x, y), found in fixes:
        o = numpy.asarray(found, dtype=float).reshape(-1, 2) - (x, y)
        offsets.append(o[numpy.hypot(o[:, 0], o[:, 1]) <= REACH_M])
    kept = [i for i, o in enumerate(offsets) if len(o)]
    xy = numpy.array([fixes[i][0] for i in kept], dtype=float)
    tree = cKDTree(xy)
    n = int(2 * REACH_M / BIN_M) + 1
    results = [None] * len(fixes)
    for row, i in enumerate(kept):
        _, near = tree.query(xy[row], k=min(K, len(kept)))
        near = [kept[j] for j in numpy.atleast_1d(near)]
        votes = numpy.zeros((n, n))
        for j in near:
            cells = numpy.clip(((offsets[j] + REACH_M) / BIN_M).astype(int), 0, n - 1)
            mark = numpy.zeros((n, n), bool)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    mark[numpy.clip(cells[:, 0] + dx, 0, n - 1), numpy.clip(cells[:, 1] + dy, 0, n - 1)] = True
            votes += mark
        # Each vote marks a 3 x 3 block, so the winning offset is the centre of the cells that
        # share the most votes; it is then refined on the candidates close to it.
        offset = numpy.argwhere(votes == votes.max()).mean(axis=0) * BIN_M - REACH_M
        for _ in range(2):
            close = [offsets[j][numpy.hypot(*(offsets[j] - offset).T).argmin()] for j in near
                     if numpy.hypot(*(offsets[j] - offset).T).min() <= TOLERANCE_M]
            if close:
                offset = numpy.median(close, axis=0)
        residual = numpy.hypot(*(offsets[i] - offset).T)
        chosen = offsets[i][residual.argmin()]
        results[i] = (tuple(float(v) for v in offset), float(numpy.hypot(*chosen)),
                      bool(residual.min() <= TOLERANCE_M))
    return results


def derived(root, name: str, digest: str) -> Path:
    """Where a measurement computed from held inputs is cached: the derived store, by input digest."""
    from .store import store_root
    return store_root(Path(root)) / 'derived' / 'areas' / name / f'{digest}.json'


def write_derived(target: Path, document) -> None:
    from .store import _place
    _place(target, lambda temporary: temporary.write_text(json.dumps(document, separators=(',', ':'))))


def fix_errors(root, control: Path) -> list | None:
    """Each matched control fix: {'id', 'x', 'y', 'offset', 'error_m', 'on_consensus'}.

    Computed on read from the fixes and their held map windows (`control`, the acquisition
    record) by `candidates` and `consensus`, and cached in the derived store under the digest
    of the fixes, their windows and this module. None where a window is not in the store.
    """
    from .store import blob_path, store_root
    document = json.loads(Path(control).read_text())
    digest = sha256(json.dumps([document['fixes'], document['windows']], sort_keys=True).encode()
                    + Path(__file__).read_bytes()).hexdigest()
    target = derived(root, 'cadastral-fix-errors', digest)
    if target.exists():
        return json.loads(target.read_text())
    store = store_root(Path(root))
    by_fix = {w['fix']: w for w in document['windows']}
    inputs = []
    for fix in document['fixes']:
        features = []
        for page in by_fix[fix['id']]['pages']:
            path = blob_path(store, page['sha256'])
            if not path.exists():
                return None
            features += json.loads(path.read_bytes())['features']
        inputs.append(((fix['x'], fix['y']), candidates(fix['kind'], fix['description'], features)))
    out = []
    for fix, result in zip(document['fixes'], consensus(inputs)):
        if result is not None:
            offset, error, on = result
            out.append({'id': fix['id'], 'comune': fix['comune'], 'x': fix['x'], 'y': fix['y'],
                        'offset': [round(v, 2) for v in offset], 'error_m': round(error, 2), 'on_consensus': on})
    write_derived(target, out)
    return out


@dataclass(frozen=True)
class ErrorField:
    """A source's measured error at any place: the PERCENTILE of the K nearest measurements."""
    xy: numpy.ndarray          # (n, 2) EPSG:32633
    error_m: numpy.ndarray     # (n,)
    k: int = K

    def __post_init__(self):
        from scipy.spatial import cKDTree
        object.__setattr__(self, '_tree', cKDTree(self.xy))

    def at(self, xy) -> numpy.ndarray:
        """The error at each (x, y): the PERCENTILE of the k nearest measured errors."""
        points = numpy.atleast_2d(numpy.asarray(xy, dtype=float))
        k = min(self.k, len(self.error_m))
        _, near = self._tree.query(points, k=k)
        near = numpy.asarray(near).reshape(len(points), k)
        return numpy.percentile(self.error_m[near], PERCENTILE, axis=1)

    def radius(self, xy) -> numpy.ndarray:
        """The distance to the k-th nearest measurement: how local the value is."""
        points = numpy.atleast_2d(numpy.asarray(xy, dtype=float))
        distance, _ = self._tree.query(points, k=min(self.k, len(self.error_m)))
        return numpy.asarray(distance).reshape(len(points), -1)[:, -1]

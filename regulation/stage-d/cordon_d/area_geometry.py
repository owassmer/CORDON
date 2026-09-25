"""Adopted-area geometry for Stage C, one per consumed A area version, built as its act defines it.

C tests a supplied point or parcel against a supplied adopted area (`adopted_area_facts`);
this module supplies that area and nothing else. It never decides whether a place lies in
an area. It supplies every A area version whose condition tests the adopted geography and
whose interval overlaps the reach (`SPEC.md`, admission).

Each zone is built from the act's operative text first. The annex tables are that rule's
result rendered per unit, not drawn lines:

- a named whole comune, province or Annex III Part A unit (the annex version A holds for
  the day): the unit's whole territory, roads, water and unparcelled land included, never
  only the land the cadastre happens to publish. The comune's cadastral sheets draw it: the
  cadastre assigns every sheet to its comune, and ISTAT states that the scale of its own
  boundaries "non è certificabile uniformemente". Where no cadastre publishes some of its
  sheets, their territory is in the unit too: inside the held sheets their outline draws
  it; where it reaches the unit's border, the Region's layer for the zone (the act's map)
  draws it, or ISTAT's boundary where the act's map is not published as a layer. ISTAT's
  boundary draws a comune whose sheets are not held;
- a band the act states in kilometres from a zone: that zone offset at the width, clipped
  to land; outward for a buffer zone, inward for a zone under containment measures from the
  zone's border with the buffer zone (Article 15(2)(a): "from the border of the infected
  zone with the buffer zone");
- a radius the act states around the infected plants it names: each plant's located
  position offset at the width. The act lists the units its plants' zone reaches, not where
  the plants stand ("FOGLI DI MAPPA PARZIALMENTE RICADENTI NEI BUFFER DI 50 METRI DALLE
  PIANTE"; "particelle ... ricadenti nel buffer di 50 metri"). A plant is the row 1
  positive the act names (`named_plants`), with row 1's measured error (INPUTS row 1); for
  a listed unit no such plant's radius reaches, the Region's layer where it carries the
  act's circles; otherwise the unit itself with the unit's extent in the plant's error,
  so C can answer only where the plant's whole possible reach agrees.

A width is B's: the act's own figure where it states one, B's floor where it states
"almeno" or applies the Regulation without a figure. A unit the annex places wholly in a
zone is in it, also where it lies beyond the band. The annex enumerates the rule's result
per unit, so a band never reaches a unit the annex does not list for that zone: the
containment band and a buffer band drawn from plants are held to the listed units. Where
the band and the annex still disagree (the band reaches land the annex does not list, or
the annex lists a unit partly in the zone that the band does not reach), the disagreement
is kept on the zone and carried in the error there, so C answers neither way. Where the
annex places a unit only partly in a zone and the act states no rule that places the part,
the adopted line exists only on the act's map; the Region's published layer that renders
that map (INPUTS row 3) supplies the part. Only a zone for which the operative text states
no rule is defined by the annex, by the units it lists.

Positional error is local and measured (`corpus/sources/areas/geometry.json`,
`positional-error`, names the method): the cadastre's against the Region's surveyed control
fixes (`cordon_d.area_error`), the Region's layer against the cadastral outline of the units
the act places wholly, a plant's from row 1's qualification. The Region's layer's ground
error at a place is its measured distance from the cadastral outline there plus the
cadastre's ground error there. The measurements are computed on read from the held inputs
and cached in the derived store under their inputs' digest; no measured value is stored
beside the acquisitions. An area supplied to C carries the error of the outline near the
place C tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from functools import cached_property
import csv
import json
from pathlib import Path
import re

import numpy
from pyproj import CRS
import shapely
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, distance_envelope
from .administrative import TARGET_CRS, AdministrativeUnits, _blob, records, _key
from .area_error import ErrorField, derived as _derived, fix_errors, write_derived as _write_derived
from .areas import _act_text, versions

REACH_CLOCK = 'B-CLK-EU-6(1)-four-negative-years'
INFECTED_RADIUS = 'B-PAR-EU-4(2)-sub1-infected-zone-50m'
ERADICATION_BUFFER = 'B-PAR-EU-4(2)(a)-eradication-buffer-2.5km'
CONTAINMENT_BUFFER = 'B-PAR-EU-4(2)(b)-containment-buffer-5km'
UTM = CRS.from_user_input(TARGET_CRS)
# The offset polygon circumscribes the exact offset; C's envelope reports what it adds.
APPROXIMATION_M = 1.0
# Land a band may cover: the regions the Puglia areas' bands reach.
LAND_REGIONS = ('Puglia', 'Basilicata')
# A sheet the act's legend marks partial matters to C only outside the rest of the area.
OUTSIDE_TOLERANCE_M2 = 1.0
# Gaps narrower than this between drawn cadastral sheets are seams, not territory.
SEAM_M = 20.0
# The outline near a tested place: within its distance to the outline plus this.
OUTLINE_REACH_M = 500.0
OUTLINE_STEP_M = 25.0
# The Region's layer draws a named unit's unpublished part up to this far past ISTAT's line.
GAP_REACH_M = 500.0
# The Region's layer: its error at a place is that of the samples within this distance.
REGION_REACH_M = 2000.0
REGION_STEP_M = 10.0
# Outline sampling for the sheets a band may reach.
LAND_STEP_M = 1000.0

ROLES = ('infected', 'containment', 'focus', 'buffer')


def role_of(statement) -> str:
    """The part of the area an annex table states, from the act's own caption words."""
    if statement.zone == 'FOCOLAI':
        return 'focus'
    if statement.zone == 'CUSCINETTO':
        return 'buffer'
    if statement.zone == 'CONTENIMENTO' or statement.regime == 'CONTENIMENTO':
        return 'containment'
    return 'infected'


@dataclass(frozen=True)
class Unplaced:
    """A unit the annex places partly in a zone that neither a rule nor a published layer places."""
    role: str
    locator: str
    place: str
    quote: str                             # the act's words: its legend and the cell
    geometry: BaseGeometry | None          # the whole unit, where the cadastre holds it
    by: str = 'its map alone'              # what places the part


@dataclass(frozen=True)
class Plant:
    """An infected plant the act names: its located position, with that position's error.

    The position is a row 1 positive the act names, with row 1's measured error; or the
    circles the Region's layer draws for the act, with the layer's ground error; or, where
    neither locates the plant, the listed unit its zone reaches, with the unit's extent in
    the error.
    """
    geometry: BaseGeometry | None          # None: the listed unit is not held
    error_m: float | None                  # None: a place without a measured error
    by: str                                # the unit or observation that places it


@dataclass(frozen=True)
class Disagreement:
    """Where a band the act states and the units its annex lists for the zone disagree.

    `kind` 'beyond': the band reaches land in no unit the annex lists (the band is held to
    the listed units there); 'short': the annex lists a unit partly in the zone and the band
    does not reach it. Neither is resolved as membership: the place carries the disagreement's
    reach in its error, so C answers neither True nor False there.
    """
    role: str
    kind: str                              # beyond | short
    place: str                             # the units concerned
    geometry: BaseGeometry
    reach_m: float                         # the farthest the disputed land lies from the zone's line


@dataclass(frozen=True)
class ErrorPart:
    """The error of the outline a source draws: fixed, or a measured field, within a region.

    `place_only`: the error of a place any part of which lies in the region, not of the
    outline running there: land whose membership the act's rule and its annex dispute
    (`Disagreement`)."""
    source: str
    region: BaseGeometry | None            # None: wherever the zone's outline runs
    error_m: float | None = None
    field: object | None = None            # `.at(xy)` -> errors
    place_only: bool = False


@dataclass(frozen=True)
class Zone:
    role: str                              # infected | containment | focus | buffer
    words: tuple[str, ...]                 # the act's own headings for this part
    geometry: BaseGeometry | None          # EPSG:32633
    rule: str                              # the operative words it is built from, or 'annex'
    sources: tuple[str, ...]               # cadastre | istat-boundaries | plants | region-layer
    width: str | None = None               # the B parameter the width is
    unplaced: tuple[Unplaced, ...] = ()
    listed: BaseGeometry | None = None     # the units the annex places wholly in the zone
    errors: tuple[ErrorPart, ...] = ()
    plants: tuple[Plant, ...] = ()
    drawn: BaseGeometry | None = None      # the parts the Region's layer supplies
    disagreements: tuple[Disagreement, ...] = ()


@dataclass(frozen=True)
class AdoptedGeography:
    """The `adopted-geography` input for one A area version."""
    provision_version_id: str
    instrument_id: str
    effective_from: date
    effective_to_exclusive: date | None
    zones: tuple[Zone, ...]
    crs: str = TARGET_CRS

    def zone(self, role) -> Zone | None:
        return next((z for z in self.zones if z.role == role), None)

    @cached_property
    def geometry(self) -> BaseGeometry | None:
        parts = [z.geometry for z in self.zones if z.geometry is not None and not z.geometry.is_empty]
        return polygonal(shapely.union_all(parts)) if parts else None

    @property
    def unplaced(self) -> tuple[Unplaced, ...]:
        """Partly-included units whose part could fall outside the constructed area."""
        area = self.geometry
        return tuple(u for z in self.zones for u in z.unplaced
                     if u.geometry is None or area is None
                     or u.geometry.difference(area).area > OUTSIDE_TOLERANCE_M2)

    @property
    def disagreements(self) -> tuple[Disagreement, ...]:
        """Where a stated band and the annex's listed units disagree; C answers neither way there."""
        return tuple(d for z in self.zones for d in z.disagreements)

    @property
    def shared_boundary(self) -> BaseGeometry | None:
        """The interface between the buffer zone and the rest of the adopted area."""
        buffer = self.zone('buffer')
        inner = [z.geometry for z in self.zones if z.role != 'buffer' and z.geometry is not None]
        if buffer is None or buffer.geometry is None or not inner:
            return None
        line = buffer.geometry.boundary.intersection(shapely.union_all(inner).boundary)
        return None if line.is_empty else line

    @cached_property
    def _outline(self):
        outline = self.geometry.boundary
        shapely.prepare(outline)
        return outline

    def error_near(self, place: BaseGeometry | None = None) -> float | None:
        """The error of the outline near `place`: the largest measured error of the sources
        drawing the outline within the place's distance to it plus OUTLINE_REACH_M, and of
        the place's own locality; and a disputed land's reach where any part of the place lies
        in it (`_reaches`), since C asks of a parcel whether any part of it is in the area.
        Without a place, the largest over the whole outline and every disputed land."""
        if self.geometry is None:
            return None
        outline = self._outline
        if place is None:
            near = outline
        else:
            reach = place.distance(outline) + OUTLINE_REACH_M
            near = outline.intersection(place.buffer(reach, quad_segs=4))
        points = _samples(near, OUTLINE_STEP_M)
        if place is not None:
            points = numpy.concatenate([points, [place.representative_point()]])
        xy = shapely.get_coordinates(points)
        found = []
        for zone in self.zones:
            for part in zone.errors:
                if part.place_only and place is not None:
                    if _reaches(place, part.region):
                        found.append(part.error_m)
                    continue
                at = xy if part.region is None else xy[shapely.intersects(part.region, points)]
                if part.region is not None and not len(at):
                    continue
                if part.error_m is None and part.field is None:
                    return None
                found.append(part.error_m if part.field is None else float(numpy.max(part.field.at(at))))
        return max(found) + APPROXIMATION_M if found else None

    def metric(self, near: BaseGeometry | None = None) -> MetricGeometry:
        """The adopted area as C's `MetricGeometry` with the error of its outline near `near`."""
        if self.geometry is None:
            raise MissingInput(f'{self.provision_version_id}: no zone of this version is constructed')
        if self.unplaced:
            u = self.unplaced[0]
            raise MissingInput(f'{self.provision_version_id}: the act places part of {u.place} in its '
                               f'{u.role} zone by {u.by}: "{u.quote}"')
        error = self.error_near(near)
        if error is None:
            unbounded = sorted({p.source for z in self.zones for p in z.errors
                                if p.error_m is None and p.field is None})
            raise MissingInput(f'{self.provision_version_id}: no positional error bound is supplied for '
                               f'the geometry source {", ".join(unbounded)}')
        return MetricGeometry(self.geometry, UTM, error)


def _reaches(place: BaseGeometry, region: BaseGeometry) -> bool:
    """Whether some of `place` lies in `region`: for a polygon, an overlap of positive area,
    more than OUTSIDE_TOLERANCE_M2 (a parcel that only touches the region has no part in it;
    along a shared edge the overlap computed is arithmetic, up to 0.0001 m² on real parcels);
    otherwise any common point."""
    if not region.intersects(place):
        return False
    if place.geom_type in ('Polygon', 'MultiPolygon'):
        return region.intersection(place).area > OUTSIDE_TOLERANCE_M2
    return True


def _samples(line, step):
    out = []
    for part in getattr(line, 'geoms', [line]):
        if part.geom_type not in ('LineString', 'LinearRing') or part.length == 0:
            continue
        n = max(2, int(part.length // step) + 1)
        out.append(shapely.line_interpolate_point(part, numpy.linspace(0, part.length, n)))
    return numpy.concatenate(out) if out else numpy.array([], dtype=object)


# --- sources -------------------------------------------------------------------

def _esri_polygon(geometry) -> BaseGeometry:
    """An Esri polygon: clockwise rings are exteriors, counter-clockwise rings their holes."""
    shells, holes = [], []
    for ring in geometry['rings']:
        polygon = Polygon(ring)
        (holes if polygon.exterior.is_ccw else shells).append(polygon)
    result = shapely.union_all(shells)
    return result.difference(shapely.union_all(holes)) if holes else result


def _arcgis_sheets(body: bytes, record: dict):
    document = json.loads(body)
    if document.get('spatialReference', {}).get('latestWkid') != 32633:
        raise ValueError(f"{record['url']}: not in EPSG:32633")
    for feature in document['features']:
        a = feature['attributes']
        yield ({'COMUNE': a['COMUNE'], 'SEZIONE': (a.get('SEZIONE') or '').strip(),
                'FOGLIO': str(a['FOGLIO']).lstrip('0'), 'ALLEGATO': str(a.get('ALLEGATO') or '0').strip(),
                'SVILUPPO': str(a.get('SVILUPPO') or '0').strip()}, _esri_polygon(feature['geometry']))


GML = '{http://www.opengis.net/gml/3.2}'


def _inspire_zoning(body: bytes, record: dict):
    """AdE INSPIRE CadastralZoning sheets: `NATIONALCADASTRALZONINGREFERENCE` is
    <comune><section or _><4-digit sheet><allegato><sviluppo>, positions lat/lon in EPSG:6706."""
    import xml.etree.ElementTree as ElementTree
    from pyproj import Transformer
    transformer = Transformer.from_crs(record['crs'], TARGET_CRS, always_xy=True, allow_ballpark=False,
                                       only_best=True)

    def ring(element):
        values = [float(v) for v in element.find(f'.//{GML}posList').text.split()]
        lon, lat = values[1::2], values[0::2]
        x, y = transformer.transform(lon, lat)
        return list(zip(x, y))

    for member in ElementTree.fromstring(body).iter('{http://mapserver.gis.umn.edu/mapserver}CadastralZoning'):
        reference = member.find('{http://mapserver.gis.umn.edu/mapserver}NATIONALCADASTRALZONINGREFERENCE').text
        comune, section, code = reference[:4], reference[4].strip('_'), reference[5:]
        if comune != record['selection']['comune']:
            continue
        polygons = [Polygon(ring(p.find(f'{GML}exterior')), [ring(i) for i in p.findall(f'{GML}interior')])
                    for p in member.iter(f'{GML}Polygon')]
        yield ({'COMUNE': comune, 'SEZIONE': section, 'FOGLIO': code[:4].lstrip('0'), 'ALLEGATO': code[4],
                'SVILUPPO': code[5], 'REFERENCE': reference},
               shapely.make_valid(shapely.union_all(polygons)))


def _metres(value, unit) -> float:
    return float(str(value).replace(',', '.')) * {'m': 1, 'metri': 1, 'km': 1000, 'chilometri': 1000}[unit.lower()]


def polygonal(geometry: BaseGeometry | None) -> BaseGeometry | None:
    """The polygonal part of a geometry; `make_valid` can leave slivers as lines or points."""
    if geometry is None:
        return None
    geometry = shapely.make_valid(geometry)
    if geometry.geom_type in ('Polygon', 'MultiPolygon'):
        return geometry
    parts = [g for g in getattr(geometry, 'geoms', [geometry]) if g.geom_type in ('Polygon', 'MultiPolygon')]
    return shapely.union_all(parts) if parts else shapely.Polygon()


# A seal is local: closing a seam moves no line farther than the mitre limit (5) times half
# the seam width. A large geometry is sealed tile by tile, each tile read with a margin well
# beyond that reach, so the result is the same and memory stays bounded by a tile.
SEAL_TILE_M = 10_000.0
SEAL_MARGIN_M = 20 * SEAM_M
SEAL_TILED_ABOVE = 50_000               # coordinates


def _sealed(geometry: BaseGeometry) -> BaseGeometry:
    closed = geometry.buffer(SEAM_M / 2, join_style='mitre').buffer(-SEAM_M / 2, join_style='mitre')
    return shapely.union_all([geometry, closed])


def seal(geometry: BaseGeometry) -> BaseGeometry:
    """Close the seams narrower than SEAM_M between drawn sheets; they are not territory."""
    if geometry.is_empty or shapely.get_num_coordinates(geometry) <= SEAL_TILED_ABOVE:
        return polygonal(_sealed(geometry))
    xmin, ymin, xmax, ymax = geometry.bounds
    pieces = []
    for x in numpy.arange(xmin, xmax, SEAL_TILE_M):
        for y in numpy.arange(ymin, ymax, SEAL_TILE_M):
            part = shapely.clip_by_rect(geometry, x - SEAL_MARGIN_M, y - SEAL_MARGIN_M,
                                        x + SEAL_TILE_M + SEAL_MARGIN_M, y + SEAL_TILE_M + SEAL_MARGIN_M)
            if part.is_empty:
                continue
            piece = polygonal(shapely.clip_by_rect(_sealed(shapely.make_valid(part)), x, y,
                                                   x + SEAL_TILE_M, y + SEAL_TILE_M))
            if not piece.is_empty:
                pieces.append(piece)
    return polygonal(shapely.union_all(pieces))


class Sources:
    """The retained geometry sources, measured errors and A/B inputs, read from their records.

    `comuni`, when given, bounds the cadastral records read to those comuni (cadastral
    codes): a caller that builds one comune's units reads that comune's sheets and parcels,
    not the population. Without it every held record is read.
    """

    def __init__(self, root: Path, comuni=None):
        self.root = Path(root)
        self.comuni = None if comuni is None else frozenset(comuni)
        self._unpublished, self._extent = {}, {}

    def _records(self, kind) -> list[dict]:
        found = records(self.root, kind)
        if self.comuni is None:
            return found
        return [r for r in found if r.get('selection', {}).get('comune') in self.comuni]

    @cached_property
    def administrative(self) -> AdministrativeUnits:
        return AdministrativeUnits(self.root)

    @cached_property
    def sheets(self) -> dict:
        """Cadastral sheets keyed by (comune, sezione, foglio): [(attributes, geometry)].

        A sheet's identity is the cadastre's: comune, section, number, and the annex
        (allegato) and development (sviluppo) it carries. Where a release repeats one
        identity, the repeats are one feature.
        """
        import hashlib
        found, seen = {}, set()
        for record in self._records('cadastre-fogli'):
            body = _blob(self.root, record).read_bytes()
            features = (_inspire_zoning(body, record) if record['format'] == 'inspire-gml'
                        else _arcgis_sheets(body, record))
            del body
            for a, geometry in features:
                identity = (a['COMUNE'], a['SEZIONE'], a['FOGLIO'], a['ALLEGATO'], a['SVILUPPO'],
                            hashlib.sha1(geometry.wkb).digest() if record['format'] != 'inspire-gml' else None)
                if identity in seen:
                    continue
                seen.add(identity)
                found.setdefault((a['COMUNE'], a['SEZIONE'], a['FOGLIO']), []).append((a, geometry))
        return found

    @cached_property
    def _sheet_index(self):
        """An STRtree over every held sheet, for the sheets near a place."""
        geometries = [g for found in self.sheets.values() for _, g in found]
        return shapely.STRtree(geometries), geometries

    def sheets_near(self, geometry: BaseGeometry) -> list:
        """The held sheets whose extent meets `geometry`'s envelope."""
        tree, geometries = self._sheet_index
        return [geometries[i] for i in tree.query(geometry.envelope)]

    @cached_property
    def _sheet_keys(self):
        """An STRtree over every held sheet with its (comune, sezione, foglio), in `_sheet_index`'s order."""
        keys = [key for key, found in self.sheets.items() for _ in found]
        return self._sheet_index[0], self._sheet_index[1], keys

    def sheet_labels(self, geometry: BaseGeometry, minimum_m2: float = 100.0) -> list:
        """[(label, m²)]: the held sheets `geometry` covers more than `minimum_m2` of, largest first."""
        tree, geometries, keys = self._sheet_keys
        found = {}
        for i in tree.query(geometry, predicate='intersects'):
            area = shapely.make_valid(geometries[i]).intersection(geometry).area
            comune, section, number = keys[i]
            unit = self.administrative.comune(catastale=comune)
            label = f"{unit.name if unit else comune} {'sezione ' + section + ' ' if section else ''}foglio {number}"
            found[label] = found.get(label, 0.0) + area
        return sorted(((k, v) for k, v in found.items() if v > minimum_m2), key=lambda kv: -kv[1])

    @cached_property
    def held(self) -> frozenset:
        """The comuni whose sheets are held."""
        return frozenset(c for c, _, _ in self.sheets)

    @cached_property
    def parcels(self) -> dict:
        found = {}
        for record in self._records('cadastre-particelle'):
            document = json.loads(_blob(self.root, record).read_bytes())
            for feature in document['features']:
                a = feature['attributes']
                key = (a['COMUNE'], (a.get('SEZIONE') or '').strip(), str(a['FOGLIO']).lstrip('0'),
                       str(a.get('NUMERO')))
                found.setdefault(key, []).append(_esri_polygon(feature['geometry']))
        return found

    @cached_property
    def b(self) -> dict:
        return json.loads((self.root / 'regulation/stage-b/clocks-and-parameters.json').read_text())

    @cached_property
    def parameters(self) -> dict:
        return {p['parameter_id']: p for p in self.b['parameters']}

    @cached_property
    def dispositions(self) -> dict:
        out = {}
        for d in self.b['dispositions']:
            if d.get('disposition') == 'restates_parameter' and d.get('ref') in self.parameters:
                out.setdefault(d['provision_version_id'], []).append((d, self.parameters[d['ref']]))
        return out

    # --- measured errors ---------------------------------------------------------

    @cached_property
    def cadastral_error(self) -> ErrorField | None:
        """The cadastre's error at any place, from the surveyed control fixes. Each fix's error is
        computed on read from its held map window (`area_error.fix_errors`); None where the
        method or the windows are not held."""
        found = [r for r in records(self.root, 'positional-error') if r['source'] == 'cadastre']
        if not found:
            return None
        fixes = fix_errors(self.root, self.root / found[0]['evidence'])
        if not fixes:
            return None
        return ErrorField(numpy.array([[f['x'], f['y']] for f in fixes], dtype=float),
                          numpy.array([f['error_m'] for f in fixes], dtype=float))

    @cached_property
    def row1(self):
        """(observations, error_m): every located row 1 positive as `Observation`, and row 1's
        measured positional error (INPUTS row 1). Read from the ordinary monitoring reader's
        grouped observations, which this never derives; None where the store does not hold
        them for the current reader, or row 1's qualification. Cached in the derived store."""
        document = row1_positives(self.root)
        if document is None:
            return None
        units, codes = self.administrative, {}
        found = []
        for r in document['positives']:
            code = r['comune_cod']
            if not code and r['comune']:
                if r['comune'] not in codes:
                    unit = units.comune(name=r['comune'], region='Puglia')
                    codes[r['comune']] = unit.catastale if unit else None
                code = codes[r['comune']]
            found.append(Observation(date.fromisoformat(r['day']), tuple(r['subspecies']), r['x'], r['y'],
                                     code, r['foglio'], r['particella']))
        return found, document['error_m']

    def inputs_digest(self, version) -> str:
        """The digest of what one version's construction reads: the retained records, the
        readings, A's and B's inputs, the row 1 positives and this reader's code."""
        import hashlib
        digest = hashlib.sha256()
        here = Path(__file__).parent
        paths = [here / n for n in ('area_geometry.py', 'areas.py', 'area_error.py', 'administrative.py')]
        paths += [self.root / 'corpus/sources/areas/geometry.json', self.root / 'corpus/sources/areas/acts.json',
                  self.root / 'corpus/sources/areas/cadastral-control.json',
                  self.root / 'regulation/stage-b/clocks-and-parameters.json',
                  self.root / 'regulation/stage-a/annex-versions.csv']
        paths += sorted((self.root / 'corpus/sources/areas/readings').glob('*'))
        for path in paths:
            if path.is_file():
                digest.update(path.name.encode() + b'\0' + path.read_bytes())
        row1 = row1_key(self.root)
        digest.update(f'{version.provision_version_id}\0{row1}\0'.encode())
        digest.update(','.join(sorted(self.comuni)).encode() if self.comuni is not None else b'*')
        return digest.hexdigest()

    @cached_property
    def istat_errors(self) -> dict:
        """Comune code -> ISTAT's measured bound along its borders with held sheets (larger direction's p95)."""
        out = {}
        for r in records(self.root, 'positional-error'):
            if r['source'] == 'istat-boundaries':
                for c in r['comuni']:
                    values = [d['p95'] for d in (c['istat_to_cadastre'], c['cadastre_to_istat']) if d]
                    if values:
                        out[c['comune']] = max(values)
        return out

    def cadastral_outline(self, code) -> BaseGeometry:
        """The outline of every held sheet near a comune, widened by 5 m: where a sheet, not ISTAT, draws."""
        key = ('outline', code)
        if key not in self._extent:
            territory = self.administrative.comune_geometry(self.administrative.comune(catastale=code))
            near = self.sheets_near(territory)
            self._extent[key] = seal(shapely.union_all([shapely.make_valid(g) for g in near])).boundary.buffer(5.0)
        return self._extent[key]

    def region_layer(self, version_id, role):
        """(record, geometry) of the Region's published layer for a version's zone, or None."""
        key = ('region-layer', version_id, role)
        if key not in self._extent:
            found = [r for r in records(self.root, 'region-layer')
                     if (r['provision_version_id'], r['role']) == (version_id, role)]
            layer = None
            if found:
                document = json.loads(_blob(self.root, found[0]).read_bytes())
                geometry = shapely.union_all([_esri_polygon(f['geometry']) for f in document['features']])
                layer = (found[0], shapely.make_valid(geometry))
            self._extent[key] = layer
        return self._extent[key]

    @cached_property
    def _region_fields(self) -> dict:
        return {}

    def region_error(self, version_id, role):
        """The Region's layer's measured error field for a version's zone, or None where the layer
        is not held or has no samples. Computed on read: the layer against the version as
        constructed (`region_layer_samples`), cached in the derived store under the digest of
        the construction's inputs (`inputs_digest`)."""
        key = (version_id, role)
        if key in self._region_fields:
            return self._region_fields[key]
        if not any(r['source'] == 'region-layer' and r.get('provision_version_id') == version_id
                   for r in records(self.root, 'positional-error')):
            self._region_fields[key] = None
            return None
        version = next(v for v in versions(self.root) if v.provision_version_id == version_id)
        self.region_samples(version)
        return self._region_fields.setdefault(key, None)

    def region_samples(self, version, geography: AdoptedGeography | None = None) -> dict:
        """{role: [[x, y, distance]]}: the Region's layers against the version as constructed
        (`region_layer_samples`), from the derived store's cache or computed and cached; from
        `geography` where the caller has just constructed the version."""
        target = _derived(self.root, 'region-layer-samples', self.inputs_digest(version))
        if target.exists():
            samples = json.loads(target.read_text())
        else:
            if geography is None:
                adopted = min(v.effective_from for v in versions(self.root) if v.instrument_id == version.instrument_id)
                geography = AdoptedGeography(version.provision_version_id, version.instrument_id,
                                             version.effective_from, version.effective_to_exclusive,
                                             construct(self, version, adopted=adopted))
            samples = {record['role']: [[round(x), round(y), round(d, 1)] for x, y, d in found]
                       for record, found in region_layer_samples(self, geography)}
            _write_derived(target, samples)
        for role, rows in samples.items():
            if rows:
                s = numpy.asarray(rows, dtype=float)
                self._region_fields[(version.provision_version_id, role)] = _ReachField(s[:, :2], s[:, 2])
        return samples

    # --- extents ---------------------------------------------------------------

    def comune_extent(self, comune, *, keep=True) -> tuple[BaseGeometry, tuple[str, ...]]:
        """(territory, sources): the comune's whole territory, roads, water and unparcelled land
        included. Its held sheets draw it. The territory of the sheets no cadastre publishes
        (`unpublished`) is in it too: inside the held sheets their outline is the sheets', and
        where it reaches the comune's border ISTAT's line draws it (`istat_part`). A comune
        without held sheets is ISTAT's boundary. `keep=False` builds it without keeping it, for
        a caller that keeps a larger union."""
        if comune.catastale in self._extent:
            return self._extent[comune.catastale]
        sheets = [g for (c, _, _), found in self.sheets.items() if c == comune.catastale for _, g in found]
        if sheets:
            geometry, used = seal(shapely.union_all([shapely.make_valid(g) for g in sheets])), ('cadastre',)
            _, gap = self.unpublished(comune)
            if gap is not None:
                geometry = seal(shapely.union_all([geometry, gap]))
                used = ('cadastre', 'istat-boundaries')
            extent = (geometry, used)
        else:
            extent = (self.administrative.comune_geometry(comune), ('istat-boundaries',))
        if keep:
            self._extent[comune.catastale] = extent
        return extent

    def istat_part(self, comune) -> BaseGeometry | None:
        """The part of a comune's territory no held sheet draws: its unpublished territory, or
        the whole ISTAT boundary where none of its sheets is held."""
        if comune.catastale not in self.held:
            return self.administrative.comune_geometry(comune)
        return self.unpublished(comune)[1]

    def province_extent(self, province) -> tuple[BaseGeometry, tuple[str, ...]]:
        key = ('province', province.code)
        if key not in self._extent:
            parts, used = [], set()
            for c in self.administrative.comuni.values():
                if c.province == province:
                    geometry, sources = self.comune_extent(c, keep=False)
                    parts.append(geometry)
                    used.update(sources)
            self._extent[key] = (seal(shapely.union_all(parts)), tuple(sorted(used)))
        return self._extent[key]

    def annex_iii_extent(self, day: date) -> tuple[BaseGeometry, tuple[str, ...]]:
        """Annex III Part A's Italian infected zone in the version for `day`, and its sources."""
        units = tuple(self.annex_iii(day))
        key = ('annex-iii', units)
        if key not in self._extent:
            parts, used = [], set()
            for unit in units:
                if unit[0] == 'province':
                    geometry, sources = self.province_extent(self.administrative.province(unit[1]))
                else:
                    geometry, sources = self.comune_extent(self.annex_iii_comune(unit))
                parts.append(geometry)
                used.update(sources)
            self._extent[key] = (seal(shapely.union_all(parts)), tuple(sorted(used)))
        return self._extent[key]

    def annex_iii_comune(self, unit):
        comune = self.administrative.comune(name=unit[1], province=unit[2])
        if comune is None:
            raise ValueError(f'Annex III Part A: {unit[1]} is not one ISTAT comune')
        return comune

    def annex_iii_comuni(self, day: date) -> list:
        """The comuni Annex III Part A's units for `day` cover."""
        out = []
        for unit in self.annex_iii(day):
            if unit[0] == 'province':
                province = self.administrative.province(unit[1])
                out += [c for c in self.administrative.comuni.values() if c.province == province]
            else:
                out.append(self.annex_iii_comune(unit))
        return out

    def cadastral_near(self, geometry: BaseGeometry) -> BaseGeometry:
        """The held sheets' territory near `geometry`, its seams closed."""
        sheets = [shapely.make_valid(g) for g in self.sheets_near(geometry.buffer(SEAM_M).envelope)]
        return seal(shapely.union_all(sheets)) if sheets else shapely.Polygon()

    @cached_property
    def _land_provinces(self) -> list:
        units = self.administrative
        parts = [units.province_geometry(p) for p in units.provinces.values() if p.region in LAND_REGIONS]
        return [p for p in parts if p is not None]

    def land_near(self, origin: BaseGeometry, metres: float) -> BaseGeometry:
        """Land a band of `metres` from `origin` may cover: ISTAT's provinces of LAND_REGIONS and
        every held sheet, within the band's reach. It only stops a band at the sea; a band's
        limits on land are its distance from its origin."""
        xmin, ymin, xmax, ymax = origin.bounds
        reach = metres + 2 * APPROXIMATION_M + SEAM_M
        window = shapely.box(xmin - reach, ymin - reach, xmax + reach, ymax + reach)
        parts = [shapely.clip_by_rect(p, *window.bounds) for p in self._land_provinces]
        # The band lies outside the origin, within `metres` of its outline: only the sheets
        # there bound it. Outline samples every LAND_STEP_M reach every such sheet within
        # reach + LAND_STEP_M.
        points = _samples(origin.boundary, LAND_STEP_M)
        if not len(points):
            points = numpy.array([origin.representative_point()])
        tree, geometries = self._sheet_index
        near = numpy.unique(tree.query(points, predicate='dwithin', distance=reach + LAND_STEP_M)[1])
        # A sheet ISTAT's land already covers adds no land; only sheets reaching past it do,
        # sealed with every covered sheet within a seal's reach of them, as sealing all
        # the sheets would.
        istat = shapely.union_all([p for p in parts if not p.is_empty])
        shapely.prepare(istat)
        candidates = numpy.array([shapely.make_valid(geometries[i]) for i in near], dtype=object)
        covered = numpy.array([istat.covers(g) for g in candidates], dtype=bool)
        sheets = list(candidates[~covered])
        if sheets and covered.any():
            reaching = shapely.STRtree(sheets)
            beside = numpy.unique(reaching.query(candidates[covered], predicate='dwithin',
                                                 distance=SEAL_MARGIN_M)[0])
            sheets += list(candidates[covered][beside])
        if sheets:
            return polygonal(shapely.union_all([istat, seal(shapely.union_all(sheets))]))
        return polygonal(istat)

    def unpublished(self, comune) -> tuple[tuple[str, ...], BaseGeometry | None]:
        """The comune's sheets neither cadastre publishes, and the territory they occupy.

        A comune's sheets are numbered from 1 and tile its territory, so the sheets missing
        from the published numbering occupy the territory no published sheet covers: the
        comune's ISTAT boundary less every held sheet, its own and its neighbours'. That
        territory is the comune's also where no number is missing. Seams
        narrower than SEAM_M are not territory, nor is a piece narrower than 100 m (the two
        sources' disagreement along a border).
        """
        if comune.catastale not in self._unpublished:
            self._unpublished[comune.catastale] = self._unpublished_of(comune)
        return self._unpublished[comune.catastale]

    def _unpublished_of(self, comune):
        own = {n: None for (c, section, n) in self.sheets if c == comune.catastale and not section}
        numbers = [int(n) for n in own if n.isdigit()]
        missing = tuple(str(n) for n in range(1, max(numbers, default=0) + 1) if str(n) not in own)
        # Land no held sheet covers is the comune's too where its numbering has no gap (a
        # sheet published in sections, or a territory no sheet draws).
        territory = self.administrative.comune_geometry(comune)
        if territory is None:
            return missing, None
        near = self.sheets_near(territory)
        gap = territory.difference(seal(shapely.union_all([shapely.make_valid(g) for g in near])))
        gap = gap.buffer(-50, join_style='mitre').buffer(50, join_style='mitre').intersection(gap)
        pieces = [p for p in getattr(gap, 'geoms', [gap]) if p.geom_type == 'Polygon' and p.area > 0]
        return missing, (shapely.union_all(pieces) if pieces else None)

    def annex_iii(self, day: date) -> list:
        """Annex III Part A's Italian units in the version A holds for `day`.

        [('province', name) | ('comune', name, province name)], read from the retained
        consolidation A's annex version names.
        """
        with (self.root / 'regulation/stage-a/annex-versions.csv').open() as handle:
            rows = [r for r in csv.DictReader(handle) if r['annex'] == 'III']
        row, = [r for r in rows if date.fromisoformat(r['effective_from']) <= day
                and (not r['effective_to_exclusive'] or day < date.fromisoformat(r['effective_to_exclusive']))]
        snapshot = row['source_snapshot_dates'].split(';')[-1].replace('-', '')
        text = (self.root / f'regulation/source/consolidations/02020R1201-{snapshot}.txt').read_text()
        start = text.rindex('Infected zone in Italy')
        part = text[start:text.index('PART B', start)]
        lines = [l.strip() for l in part.splitlines() if l.strip() and not l.strip().startswith('▼')]
        units, province = [], None
        for line in lines[2:]:
            if re.fullmatch(r'\d+\.', line):
                province = None
                continue
            whole = re.fullmatch(r'The province of (.+)', line)
            listed = re.fullmatch(r'Municipalit(?:y|ies) located in the province of (.+):', line)
            if whole:
                units.append(('province', whole.group(1)))
            elif listed:
                province = listed.group(1)
            elif province:
                units.append(('comune', line, province))
            else:
                raise ValueError(f'Annex III Part A line not read: {line!r}')
        return units


class _ReachField:
    """A layer's error at a place: the 95th percentile of the samples within REGION_REACH_M,
    or of the 200 nearest where none lies that close."""

    def __init__(self, xy, error_m):
        from scipy.spatial import cKDTree
        self.xy, self.error_m, self.tree = xy, error_m, cKDTree(xy)

    def at(self, xy):
        out = []
        for point in numpy.atleast_2d(xy):
            near = self.tree.query_ball_point(point, REGION_REACH_M)
            if not near:
                _, near = self.tree.query(point, k=min(200, len(self.error_m)))
            out.append(numpy.percentile(self.error_m[numpy.atleast_1d(near)], 95))
        return numpy.array(out)


class _GroundField:
    """The Region's layer's ground error at a place: its measured distance from the cadastral
    outline there plus the cadastre's own ground error there (the triangle inequality)."""

    def __init__(self, layer, cadastre):
        self.layer, self.cadastre = layer, cadastre

    def at(self, xy):
        return self.layer.at(xy) + self.cadastre.at(xy)


class _LayerField:
    """The Region's layer's measured error for one version's zone, read when first needed: it is
    measured against the version as constructed, so it cannot be read while constructing it."""

    def __init__(self, sources, version_id, role):
        self.sources, self.key = sources, (version_id, role)

    def at(self, xy):
        field = self.sources.region_error(*self.key)
        if field is None:
            raise MissingInput(f"{self.key[0]}: no measured error for the Region's {self.key[1]} layer")
        return field.at(xy)


def _layer_ground(sources, version_id, role):
    """The layer's ground error field for a version's zone, or None where the cadastre's is not held."""
    if sources.cadastral_error is None:
        return None
    return _GroundField(_LayerField(sources, version_id, role), sources.cadastral_error)


# --- the operative text ----------------------------------------------------------

_HEADER = re.compile(r'\f?[^\n]*Bollettino Ufficiale della Regione Puglia[^\n]*\n')


def dispositivo(text: str) -> str:
    """The act's operative part: after its last `DETERMINA` heading, one line."""
    text = _HEADER.sub('\n', text)
    heads = list(re.finditer(r'^\s*DETERMINA(?:\s+DI)?\s*$', text, re.M))
    if not heads:
        raise ValueError('The act prints no DETERMINA heading')
    body = text[heads[-1].end():]
    stop = re.search(r'Trasmettere copia|Pubblicare il presente', body)
    return ' '.join((body[:stop.start()] if stop else body).split())


def _clauses(operative: str) -> list[str]:
    return [c.strip() for c in re.split(r'\s[•\-]\s', ' ' + operative) if c.strip()]


NUMBER = r'(\d+(?:,\d+)?)'
WHOLE_COMUNI = re.compile(r"intero agro comunale di:?\s+(?P<names>.+?)\s+e\s+parte dell.agro di\s+"
                          r"(?P<part>.+?)(?=\s+nelle quali|\s*[,;○]|\s+come\b|\s*$)", re.I)
ANNEX_III_ZONE = re.compile(r"misure di contenimento dell.area infetta di cui all.allegato III\W+parte A", re.I)
INWARD_BAND = re.compile(r'contenimento che comprende un territorio di larghezza di ' + NUMBER
                         + r'\s*(chilometri|km)\s+dalla zona infetta', re.I)
FORMER_ZONE_BAND = re.compile(NUMBER + r'\s*(km|chilometri) a nord della ex zona infetta', re.I)
BUFFER_WIDTH = re.compile(r'zona cuscinetto[^•]*?larghezza di ' + NUMBER + r'\s*(chilometri|km)'
                          r'|' + NUMBER + r'\s*(km|chilometri) la larghezza della zona cuscinetto', re.I)
BUFFER_NAMED = re.compile(r'zona cuscinetto', re.I)
# An infected-zone radius names its origin: the infected plants ("zona infetta di 50 m
# attorno ai 6 mandorli infetti"). DDS 18/2024's 50 m concerns host plants spared from
# removal and names no zone.
INFECTED_ORIGIN = re.compile(r'\binfett[ae]\b[^;]{0,40}?\b\d+\s*m\b', re.I)


@dataclass(frozen=True)
class Rules:
    whole: tuple[str, ...] = ()            # comuni named whole
    part: str | None = None                # the comune named in part (annex defines the part)
    whole_role: str | None = None
    annex_iii: str | None = None           # role that is Annex III Part A
    inward: tuple | None = None            # (metres, B id, quote) for the containment band
    former: tuple | None = None            # (metres, B id, quote) inward band of the former zone
    buffer: tuple | None = None            # (metres, B id, quote)
    radius: tuple | None = None            # (metres, B id, quote) around the infected plants
    quotes: tuple[str, ...] = ()


def _b_width(sources: Sources, metres: float, purpose: str) -> str:
    """The B parameter a stated width is, by value and purpose."""
    for p in sources.parameters.values():
        if not p['unit'] in ('m', 'km') or p.get('kind') not in ('floor', 'exact'):
            continue
        if abs(_metres(p['value'], p['unit']) - metres) < 1e-6 and purpose in str(p.get('scope', '')):
            return p['parameter_id']
    raise ValueError(f'B holds no {purpose} width of {metres} m')


def read_rules(sources: Sources, version, operative: str) -> Rules:
    found = {}
    quotes = []
    for clause in _clauses(operative):
        whole = WHOLE_COMUNI.search(clause)
        if whole:
            names = [n.strip() for n in re.split(r',|\se\s', whole.group('names')) if n.strip()]
            found.update(whole=tuple(names), part=whole.group('part').strip(),
                         whole_role='containment' if 'contenimento' in clause[:whole.start()].lower()
                         else 'infected')
            quotes.append(clause)
        former = FORMER_ZONE_BAND.search(clause)
        if former:
            metres = _metres(*former.groups())
            found['former'] = (metres, _b_width(sources, metres, 'buffer'), former.group(0))
        if ANNEX_III_ZONE.search(clause):
            found['annex_iii'] = 'containment'
            quotes.append(clause)
        inward = INWARD_BAND.search(clause)
        if inward:
            metres = _metres(*inward.groups())
            found['inward'] = (metres, _b_width(sources, metres, 'inward'), inward.group(0))
        width = BUFFER_WIDTH.search(clause)
        if width:
            value, unit = [g for g in width.groups() if g][:2]
            metres = _metres(value, unit)
            found['buffer'] = (metres, _b_width(sources, metres, 'outward'), width.group(0))
    for d, p in sources.dispositions.get(version.provision_version_id, ()):
        expression = d.get('expression') or ''
        if p['parameter_id'] == INFECTED_RADIUS and INFECTED_ORIGIN.search(expression):
            found['radius'] = (_metres(p['value'], p['unit']), p['parameter_id'], expression)
        elif p['parameter_id'] == ERADICATION_BUFFER and 'buffer' not in found:
            found['buffer'] = (_metres(p['value'], p['unit']), p['parameter_id'], expression)
    return Rules(**found, quotes=tuple(quotes))


# --- construction ------------------------------------------------------------------

def _envelope(origin: BaseGeometry, metres: float) -> MetricGeometry:
    return distance_envelope(MetricGeometry(origin, UTM, 0), metres, APPROXIMATION_M)


def outward_band(origin: BaseGeometry, metres: float, land: BaseGeometry) -> BaseGeometry:
    """Land within `metres` of the zone, outside it."""
    return _envelope(origin, metres).geometry.intersection(land).difference(origin)


def _border(zone: BaseGeometry, adjacent: BaseGeometry, outside: BaseGeometry | None) -> BaseGeometry:
    """The zone's outline within APPROXIMATION_M of `adjacent` less `outside`. Only the adjacent
    land within that reach of the outline counts, so a long outline is read tile by tile."""
    boundary = zone.boundary
    if outside is None or shapely.get_num_coordinates(boundary) <= SEAL_TILED_ABOVE:
        near = adjacent if outside is None else adjacent.difference(outside)
        return boundary.intersection(_envelope(near, APPROXIMATION_M).geometry)
    # Each outline segment goes to the tile of its first vertex; runs of segments keep their own
    # vertices, so no cut point is computed and the runs rejoin exactly.
    m = SEAL_MARGIN_M
    xmin, ymin = boundary.bounds[:2]
    runs = {}
    for part in shapely.get_parts(boundary):
        coords = shapely.get_coordinates(part)
        if len(coords) < 2:
            continue
        tile = numpy.floor((coords[:-1] - (xmin, ymin)) / SEAL_TILE_M).astype(int)
        change = numpy.flatnonzero(numpy.any(tile[1:] != tile[:-1], axis=1)) + 1
        for start, end in zip(numpy.r_[0, change], numpy.r_[change, len(tile)]):
            runs.setdefault(tuple(tile[start]), []).append(shapely.LineString(coords[start:end + 1]))
    lines, rest = [], []
    for found in runs.values():
        line = shapely.MultiLineString(found)
        x0, y0, x1, y1 = line.bounds
        window = (x0 - m, y0 - m, x1 + m, y1 + m)
        near = shapely.make_valid(shapely.clip_by_rect(adjacent, *window))
        near = near.difference(shapely.make_valid(shapely.clip_by_rect(outside, *window)))
        if near.is_empty:
            continue
        for p in shapely.get_parts(line.intersection(_envelope(near, APPROXIMATION_M).geometry)):
            if not p.is_empty:
                (lines if p.geom_type == 'LineString' else rest).append(p)
    if not lines and not rest:
        return shapely.LineString()
    # Rejoin the runs, so each vertex keeps its join when the border is banded.
    merged = list(shapely.get_parts(shapely.line_merge(shapely.MultiLineString(lines)))) if lines else []
    return shapely.GeometryCollection(merged + rest) if rest else shapely.MultiLineString(merged)


BAND_CHUNK = 5_000                     # coordinates per piece of one long line
BAND_GROUP = 20_000                    # coordinates of line banded at once, for a band of
BAND_GROUP_AT_M = 2_000.0              # this width or less


def _chunks(coords: numpy.ndarray):
    """A long line as consecutive pieces that meet at the midpoint of a segment: the longest one
    in the last tenth of each piece. Every vertex stays inside a piece and keeps its join; the
    line is straight at a midpoint, so the two end caps there fall within the whole line's band
    wherever the half segment is longer than the band's chord error."""
    if len(coords) <= BAND_CHUNK:
        yield coords
        return
    start, lead = 0, None
    while len(coords) - start > BAND_CHUNK:
        window = numpy.arange(start + BAND_CHUNK - BAND_CHUNK // 10, start + BAND_CHUNK)
        lengths = numpy.hypot(*(coords[window + 1] - coords[window]).T)
        s = int(window[lengths.argmax()])
        mid = (coords[s] + coords[s + 1]) / 2
        body = numpy.vstack([coords[start:s + 1], mid])
        yield body if lead is None else numpy.vstack([lead, body])
        lead, start = mid, s + 1
    yield numpy.vstack([lead, coords[start:]])


def _band_in(line: BaseGeometry, metres: float, rect) -> BaseGeometry:
    """The envelope of `line` at `metres`, within `rect`: the line banded whole, as HEAD bands it,
    up to BAND_GROUP coordinates; a longer line in groups of parts of at most that many, a part
    longer than BAND_CHUNK in pieces."""
    budget = int(BAND_GROUP * min(1.0, BAND_GROUP_AT_M / metres))    # a wider band costs more per coordinate
    if shapely.get_num_coordinates(line) <= budget:
        band = shapely.clip_by_rect(_envelope(line, metres).geometry, *rect)
        return polygonal(shapely.make_valid(band)) if not band.is_empty else shapely.Polygon()
    units = []
    for p in shapely.get_parts(line):
        if p.is_empty:
            continue
        if p.geom_type == 'LineString' and shapely.get_num_coordinates(p) > BAND_CHUNK:
            units += [shapely.LineString(c) for c in _chunks(shapely.get_coordinates(p))]
        else:
            units.append(p)
    groups, group, size = [], [], 0
    for u in units:
        n = shapely.get_num_coordinates(u)
        if group and size + n > budget:
            groups.append(shapely.GeometryCollection(group))
            group, size = [], 0
        group.append(u)
        size += n
    if group:
        groups.append(shapely.GeometryCollection(group))
    pieces = []
    for chunk in groups:
        piece = shapely.clip_by_rect(_envelope(chunk, metres).geometry, *rect)
        if not piece.is_empty:
            pieces.append(shapely.make_valid(piece))
    return polygonal(shapely.union_all(pieces)) if pieces else shapely.Polygon()


def inward_band(zone: BaseGeometry, metres: float, adjacent: BaseGeometry,
                outside: BaseGeometry | None = None) -> BaseGeometry:
    """The part of the zone within `metres` of its border with the `adjacent` zone (less `outside`)."""
    border = _border(zone, adjacent, outside)
    if border.is_empty:
        return shapely.Polygon()
    if shapely.get_num_coordinates(border) <= SEAL_TILED_ABOVE:
        return _envelope(border, metres).geometry.intersection(zone)
    # A band is local: its part in a tile is the band of the border within its reach of the
    # tile. A long border is banded tile by tile, so memory stays bounded by a tile.
    reach = metres + 2 * APPROXIMATION_M + SEAM_M
    xmin, ymin, xmax, ymax = border.bounds
    pieces = []
    for x in numpy.arange(xmin - reach, xmax + reach, SEAL_TILE_M):
        for y in numpy.arange(ymin - reach, ymax + reach, SEAL_TILE_M):
            near = shapely.clip_by_rect(border, x - reach, y - reach, x + SEAL_TILE_M + reach, y + SEAL_TILE_M + reach)
            if near.is_empty:
                continue
            band = _band_in(near, metres, (x, y, x + SEAL_TILE_M, y + SEAL_TILE_M))
            if band.is_empty:
                continue
            local = shapely.make_valid(shapely.clip_by_rect(zone, x - 1, y - 1, x + SEAL_TILE_M + 1, y + SEAL_TILE_M + 1))
            piece = polygonal(shapely.make_valid(band).intersection(local))
            if not piece.is_empty:
                pieces.append(piece)
    return polygonal(shapely.union_all(pieces)) if pieces else shapely.Polygon()


class _Builder:
    def __init__(self, sources: Sources, version):
        self.sources, self.version = sources, version
        self.units = sources.administrative
        self.used: set[str] = set()
        self.istat_drawn: list = []            # (comune code, geometry) drawn from ISTAT's boundary
        self.whole: list = []                  # the comuni placed whole, in the order they are built
        statements = version.statements or ()
        self.legend = any('*' in s.text or 'INTERAMENTE' in (s.qualification or '').upper() for s in statements)
        self.by_role = {role: [s for s in statements if role_of(s) == role] for role in ROLES}

    def comune(self, name, province=None):
        comune = self.units.comune(name=name, province=province)
        if comune is None:
            raise ValueError(f'{self.version.provision_version_id}: {name} is not one ISTAT comune')
        return comune

    def _istat(self, comune):
        part = self.sources.istat_part(comune)
        if part is not None and not part.is_empty:
            self.istat_drawn.append((comune.catastale, part))

    def extent(self, comune):
        geometry, used = self.sources.comune_extent(comune)
        self.used.update(used)
        self._istat(comune)
        self.whole.append(comune)
        return geometry

    def province(self, label):
        province = self.units.province(label)
        geometry, used = self.sources.province_extent(province)
        self.used.update(used)
        for c in self.units.comuni.values():
            if c.province == province:
                self._istat(c)
                self.whole.append(c)
        return geometry

    def whole_comune(self, name, province=None):
        return self.extent(self.comune(name, province))

    def named_comune(self, name):
        """A comune the dispositivo names, as the Region's own act writes it."""
        comune = self.units.comune(name=name, region='Puglia')
        if comune is None:
            raise ValueError(f'{self.version.provision_version_id}: {name} is not one ISTAT comune in Puglia')
        return self.extent(comune)

    def annex_iii(self, day):
        geometry, used = self.sources.annex_iii_extent(day)
        self.used.update(used)
        for c in self.sources.annex_iii_comuni(day):
            self._istat(c)
            self.whole.append(c)
        return geometry

    def sheet(self, comune, sheet, listed=()):
        """(extent, exact, sources). A sheet neither cadastre publishes (Massafra 15, 16 and 23) lies
        in the comune's unpublished territory (`Sources.unpublished`). That territory is the
        sheet exactly when it is the only unpublished sheet, or when every unpublished sheet
        is listed in `listed` alike; otherwise it contains the sheet."""
        features = self.sources.sheets.get((comune.catastale, sheet.section or '', sheet.number), [])
        if sheet.qualifier:
            kind, _, value = sheet.qualifier.strip('() ').upper().partition(' ')
            features = [f for f in features if f[0].get(kind) == value]
        if features:
            return shapely.union_all([g for _, g in features]), True, ('cadastre',)
        missing, territory = self.sources.unpublished(comune)
        if sheet.section or sheet.number not in missing or territory is None:
            raise ValueError(f'{self.version.provision_version_id}: {comune.name} foglio {sheet.number} '
                             'is neither published nor missing from the published numbering')
        exact = set(missing) <= set(listed)
        if exact:
            self.istat_drawn.append((comune.catastale, territory))
        return territory, exact, ('cadastre', 'istat-boundaries')

    def annex(self, role, statements, only_comune=None):
        """The zone the annex's wholly listed units define, and its partly-included units."""
        parts, unplaced = [], []
        for s in statements:
            if only_comune and _key(s.comune) != _key(only_comune):
                continue
            if s.scope == 'whole-province':
                parts.append(self.province(s.province))
                continue
            comune = self.comune(s.comune, s.province)
            if s.scope == 'whole-comune':
                parts.append(self.extent(comune))
                continue
            if s.scope != 'sheets':
                unplaced.append(Unplaced(role, s.locator, f'{comune.name}', s.text, None))
                continue
            for sheet in s.sheets:
                label = f"{comune.name} {'sezione ' + sheet.section + ' ' if sheet.section else ''}foglio {sheet.number}"
                if sheet.parcels:
                    for number in sheet.parcels:
                        geometry = self.sources.parcels.get(
                            (comune.catastale, sheet.section or '', sheet.number, number))
                        whole = number in sheet.wholly_contained_parcels or not self.legend
                        if geometry and whole:
                            self.used.add('cadastre')
                            parts.extend(geometry)
                        else:
                            unplaced.append(Unplaced(role, s.locator, f'{label} particella {number}',
                                                     f'{s.qualification}: {s.text}',
                                                     shapely.union_all(geometry) if geometry else None))
                    continue
                alike = [sh.number for sh in s.sheets if not sh.parcels and not sh.section
                         and (sh.wholly_contained == sheet.wholly_contained or not self.legend)]
                geometry, exact, used = self.sheet(comune, sheet, alike)
                if (sheet.wholly_contained or not self.legend) and exact:
                    self.used.update(used)
                    parts.append(geometry)
                else:
                    unplaced.append(Unplaced(role, s.locator, label, f'{s.qualification}: {s.text}', geometry))
        return (seal(shapely.union_all(parts)) if parts else None), tuple(unplaced)

    def units_of(self, statements):
        """Each unit the statements list: (label, geometry or None). Each listed parcel, else the sheet."""
        for s in statements:
            if s.scope == 'whole-province':
                yield s.province, self.province(s.province)
                continue
            comune = self.comune(s.comune, s.province)
            if s.scope == 'whole-comune':
                yield comune.name, self.extent(comune)
                continue
            if s.scope != 'sheets':
                yield comune.name, None
                continue
            for sheet in s.sheets:
                label = f"{comune.name} {'sezione ' + sheet.section + ' ' if sheet.section else ''}foglio {sheet.number}"
                if sheet.parcels:
                    for n in sheet.parcels:
                        g = self.sources.parcels.get((comune.catastale, sheet.section or '', sheet.number, n))
                        yield f'{label} particella {n}', shapely.union_all(g) if g else None
                    continue
                try:
                    yield label, self.sheet(comune, sheet)[0]
                except ValueError:
                    yield label, None

    def words(self, role):
        return tuple(dict.fromkeys(s.zone_heading for s in self.by_role[role]))


def _union(*parts):
    parts = [p for p in parts if p is not None and not p.is_empty]
    return shapely.union_all(parts) if parts else None


def plant_roles(sources: Sources, version) -> tuple[str, ...]:
    """The parts of the area the act defines around the infected plants it names.

    The infected zone, where the dispositivo states a radius around them or where the
    act delimits under Article 4 and its infected-zone tables list only sheets and
    parcels (no whole unit, no named comune): the plants' radius is then the
    Regulation's floor. The foci an act lists as `FOCOLAI PUNTIFORMI`.
    """
    rules = read_rules(sources, version, dispositivo(_act_text(sources.root, version.source_path)))
    build = _Builder(sources, version)
    roles = []
    infected = build.by_role['infected']
    if rules.radius or (infected and all(s.scope == 'sheets' for s in infected)
                        and not rules.whole and not rules.annex_iii):
        roles.append('infected')
    if build.by_role['focus']:
        roles.append('focus')
    return tuple(roles)


INTEGRATES = re.compile(r'Integrare la determina\w*\s+n\W{0,3}\s*(\d+)\s+del\s+\d{1,2}/\d{1,2}/(\d{4})', re.I)


def _plant_statements(sources: Sources, version, build, role, operative):
    """The statements listing the units of the plants the act names for `role`. An act that
    integrates an earlier one and prints no table of its own names the plants that act names
    ("Integrare la determina n° 8 del 21/02/2024 ... attorno ai 6 mandorli infetti")."""
    statements = build.by_role[role]
    integrated = INTEGRATES.search(operative)
    if not statements and integrated:
        number, year = int(integrated.group(1)), integrated.group(2)
        earlier = next((v for v in versions(sources.root)
                        if v.instrument_id == f'REG-PUGLIA-U181-DIR-{year}-{number:05d}' and v.statements), None)
        if earlier is not None:
            statements = [s for s in earlier.statements if role_of(s) == role]
    return statements


def plant_units(sources: Sources, version, role, *, build=None, operative=None) -> list:
    """[(label, geometry or None)]: the units the act lists for a plant-defined role's zone."""
    build = build or _Builder(sources, version)
    operative = operative or dispositivo(_act_text(sources.root, version.source_path))
    return list(build.units_of(_plant_statements(sources, version, build, role, operative)))


def _layer_circles(layer: BaseGeometry, unit: BaseGeometry, radius_m: float) -> BaseGeometry | None:
    """The plants whose circles the Region's layer draws reaching `unit`: the layer's pieces
    meeting the unit, opened by the radius (a union of circles of the radius is its own
    opening), so the circles around the result are the layer's."""
    pieces = [p for p in getattr(layer, 'geoms', [layer]) if p.geom_type == 'Polygon' and p.intersects(unit)]
    if not pieces:
        return None
    centres = []
    for p in pieces:
        core = p.buffer(-(radius_m - APPROXIMATION_M))
        centres.append(core if not core.is_empty else p.centroid)
    return shapely.union_all(centres)


def act_plants(sources: Sources, version, role, radius_m, *, build=None, operative=None,
               located=()) -> tuple[Plant, ...]:
    """The plants the act names for a plant-defined role, each at its located position.

    The act lists the units its plants' zone reaches, not where the plants stand: "FOGLI DI
    MAPPA PARZIALMENTE RICADENTI NEI BUFFER DI 50 METRI DALLE PIANTE" (DDS 59/2025),
    "particelle catastali ricadenti nel buffer di 50 metri dalle piante risultate infette"
    (DDS 8/2024). A plant is placed:

    - at each row 1 positive the act names (`located`: `named_plants`' positions, each
      (x, y, error_m) with row 1's measured error, or a `Plant`);
    - for a listed unit no such plant's radius reaches, by the Region's layer where it
      carries the act's circles for this version and zone, with the layer's ground error;
    - otherwise by the unit itself. The plant stands within the radius of the unit, so the
      circle drawn around the unit lies within the unit's extent plus twice the radius of the
      act's circle: that is carried in the plant's error with the cadastre's there, and C can
      answer only where the whole of that reach agrees.

    A unit the cadastre does not hold places nothing (geometry None).
    """
    plants = [p if isinstance(p, Plant) else Plant(Point(p[0], p[1]), p[2] if len(p) > 2 else None, 'row 1')
              for p in located or ()]
    placed = [p for p in plants if p.geometry is not None]
    tree = shapely.STRtree([p.geometry for p in placed]) if placed else None
    reach = radius_m + max((p.error_m or 0.0) for p in placed) if placed else radius_m
    layer = sources.region_layer(version.provision_version_id, role)
    field = sources.cadastral_error
    found = list(plants)
    for label, geometry in plant_units(sources, version, role, build=build, operative=operative):
        if geometry is None or geometry.is_empty:
            found.append(Plant(None, None, label))
            continue
        if tree is not None and len(tree.query(geometry, predicate='dwithin', distance=reach)):
            continue                          # a located plant's circle reaches the unit
        circles = _layer_circles(layer[1], geometry, radius_m) if layer is not None else None
        if circles is not None:
            found.append(Plant(circles, None, f"{label}: the Region's layer"))
            continue
        error = None
        if field is not None:
            cadastre = float(numpy.max(field.at(shapely.get_coordinates(shapely.convex_hull(geometry)))))
            error = 2 * shapely.minimum_bounding_radius(geometry) + 2 * radius_m + cadastre
        found.append(Plant(geometry, error, f'{label}: not located, the unit with its extent'))
    return tuple(found)


def _circles(plants, metres) -> BaseGeometry | None:
    located = [p.geometry for p in plants if p.geometry is not None]
    if not located:
        return None
    return _envelope(shapely.union_all(located), metres).geometry


def _plant_errors(sources, version, role, plants, reach_m) -> tuple[ErrorPart, ...]:
    """Each plant bounds the outline it draws: within its reach plus the error of its position.
    A plant the Region's layer places carries the layer's ground error."""
    out = []
    points = [p for p in plants if p.geometry is not None and p.geometry.geom_type == 'Point'
              and p.error_m is not None]
    if points:                    # one part per error value: row 1's positives share theirs
        for error in sorted({p.error_m for p in points}):
            at = shapely.union_all([p.geometry for p in points if p.error_m == error])
            out.append(ErrorPart('plants', at.buffer(reach_m + error + 2 * APPROXIMATION_M, quad_segs=8), error))
    for p in plants:
        if p.geometry is None:
            out.append(ErrorPart('plants', None, None))
        elif p.by.endswith("the Region's layer"):
            out.append(ErrorPart('region-layer', p.geometry.buffer(reach_m + 2 * APPROXIMATION_M, quad_segs=8),
                                 None, _layer_ground(sources, version.provision_version_id, role)))
        elif not (p.geometry.geom_type == 'Point' and p.error_m is not None):
            out.append(ErrorPart('plants', p.geometry.buffer(reach_m + (p.error_m or 0) + 2 * APPROXIMATION_M,
                                                             quad_segs=8), p.error_m))
    return tuple(out)


def located_plants(sources: Sources, version) -> dict:
    """Per plant-defined role, the row 1 positives the act names, as (x, y, error_m) with row 1's
    measured error; {} where row 1 is not in this store."""
    row1 = sources.row1
    if row1 is None:
        return {}
    observations, error = row1
    return {role: tuple((x, y, error) for x, y in found)
            for role, found in named_plants(sources, version, observations).items()}


def _source_errors(sources: Sources, used, build=None) -> tuple[ErrorPart, ...]:
    """The cadastre's measured field wherever the zone's outline runs; ISTAT's measured per-comune
    bound only along the outline ISTAT itself draws (where no held sheet does)."""
    out = []
    if 'cadastre' in used:
        out.append(ErrorPart('cadastre', None, None, sources.cadastral_error))
    if 'istat-boundaries' in used and build is not None:
        for code, geometry in build.istat_drawn:
            line = geometry.boundary.difference(sources.cadastral_outline(code))
            if not line.is_empty:
                out.append(ErrorPart('istat-boundaries', line.buffer(REGION_STEP_M), sources.istat_errors.get(code)))
    return tuple(out)


def _drawn(sources: Sources, version, role, unplaced):
    """The parts of partly-placed units the Region's layer supplies: (geometry, still unplaced, error parts)."""
    layer = sources.region_layer(version.provision_version_id, role)
    if layer is None or not unplaced:
        return None, unplaced, ()
    record, geometry = layer
    held = [u for u in unplaced if u.geometry is not None]
    if not held:
        return None, unplaced, ()
    drawn = shapely.make_valid(shapely.union_all([u.geometry for u in held]).intersection(geometry))
    field = _layer_ground(sources, version.provision_version_id, role)
    part = ErrorPart('region-layer', shapely.union_all([u.geometry for u in held]).buffer(REGION_STEP_M),
                     None, field)
    return drawn, tuple(u for u in unplaced if u.geometry is None), (part,)


def _layer_gaps(sources: Sources, version, role, geometry, build, start=0):
    """A unit the act names whole is in the zone whole, also where the cadastre publishes none of
    its sheets. There the Region's layer for the zone, which renders the act's map, draws the
    unit's line where it reaches the unit's border; inside the held sheets their outline draws
    it. Without that layer the line is ISTAT's (`Sources.istat_part`), with ISTAT's measured error.

    Returns (geometry, the parts the layer draws, their error parts, [(ISTAT part, layer part)]).
    Only the ISTAT parts registered from `start` on (this zone's) are considered."""
    layer = sources.region_layer(version.provision_version_id, role)
    entries = build.istat_drawn[start:]
    if layer is None or geometry is None or not entries:
        return geometry, None, (), []
    _, drawn = layer
    comuni = [c for c in sources.administrative.comuni_of('Puglia')]
    kept, replaced, istat = [], [], []
    for code, part in entries:
        line = part.boundary.difference(sources.cadastral_outline(code))
        if line.is_empty:
            kept.append((code, part))              # inside the held sheets: their outline draws it
            continue
        window = part.buffer(GAP_REACH_M)
        near = shapely.make_valid(shapely.clip_by_rect(drawn, *window.bounds))
        # What the layer leaves out where the part reaches the unit's border is the act's line; a
        # piece it leaves out between itself and held sheets is the layer's error, not the line.
        outside = part.difference(near)
        enclosed = [p for p in getattr(outside, 'geoms', [outside])
                    if p.geom_type == 'Polygon' and not p.intersects(line.buffer(APPROXIMATION_M))]
        # Where the layer carries the unit past ISTAT's line: land beside that line that no held
        # sheet covers and no other comune's boundary claims.
        others = [g for c in comuni if c.catastale != code
                  for g in [sources.administrative.comune_geometry(c)] if g is not None and g.intersects(window)]
        beyond = near.intersection(line.buffer(GAP_REACH_M)).difference(sources.cadastral_near(window)) \
            .difference(part)
        if others:
            beyond = beyond.difference(shapely.union_all(others))
        beyond = [p for p in getattr(beyond, 'geoms', [beyond])
                  if p.geom_type == 'Polygon' and p.intersects(line.buffer(APPROXIMATION_M))]
        new = polygonal(shapely.union_all([part.intersection(near), *enclosed, *beyond]))
        replaced.append((part, new))
        # ISTAT still draws the line between this comune and another where the layer runs on past it.
        rest = new.boundary.difference(sources.cadastral_outline(code)).difference(
            near.boundary.buffer(APPROXIMATION_M))
        if not rest.is_empty:
            istat.append(ErrorPart('istat-boundaries', rest.buffer(REGION_STEP_M), sources.istat_errors.get(code)))
    build.istat_drawn[start:] = kept
    if not replaced:
        return geometry, None, (), []
    old = shapely.union_all([o for o, _ in replaced])
    new = polygonal(shapely.union_all([n for _, n in replaced]))
    geometry = polygonal(shapely.union_all([geometry.difference(old), new]))
    field = _layer_ground(sources, version.provision_version_id, role)
    return (geometry, new, (ErrorPart('region-layer', new.buffer(REGION_STEP_M), None, field), *istat),
            replaced)


def _relisted(listed, replaced):
    """The units the annex places wholly in the zone, with the layer's part for their ISTAT part."""
    if listed is None or not replaced:
        return listed
    parts = [(o, n) for o, n in replaced if o.intersection(listed).area > OUTSIDE_TOLERANCE_M2]
    if not parts:
        return listed
    return polygonal(shapely.union_all([listed.difference(shapely.union_all([o for o, _ in parts])),
                                        *[n for _, n in parts]]))


def _whole_interior(sources: Sources, geometry, comuni):
    """A unit the act names whole is its whole territory: land inside the unit's ISTAT outline
    that no held sheet covers is in it, a seam between held sheets as much as a missing sheet.
    The unit's outer line keeps the source it has (held sheets, the Region's layer, ISTAT), so
    only land the zone encloses joins, and only inside the outline of a unit named whole.

    Returns (geometry, error parts): ISTAT's measured error along the part of the zone's
    outline its line now draws, where an enclosed piece leaves the outline of a unit named whole."""
    if geometry is None or geometry.is_empty or not comuni:
        return geometry, ()
    polygons = [p for p in getattr(geometry, 'geoms', [geometry]) if p.geom_type == 'Polygon']
    holes = [Polygon(r) for p in polygons for r in p.interiors]
    if not holes:
        return geometry, ()
    # The zone's own islands inside a hole are its polygons lying within it. (Clipping the zone to
    # the hole's own bounds, as `_minus` does, lost whole seams: Leverano's in DDS 82/2026.)
    islands = shapely.STRtree(polygons)
    outlines = {}
    for c in comuni:
        if c.catastale not in outlines:
            g = sources.administrative.comune_geometry(c)
            if g is not None:
                outlines[c.catastale] = g
    codes = list(outlines)
    units = shapely.STRtree([outlines[k] for k in codes])
    sheet_tree, sheets = sources._sheet_index
    parts = {}
    for hole in holes:
        near = [shapely.make_valid(sheets[i]) for i in sheet_tree.query(hole, predicate='intersects')]
        inside = [polygons[i] for i in islands.query(hole, predicate='covers')]
        free = polygonal(hole.difference(shapely.union_all(near + inside))) if near or inside else hole
        if free is None or free.is_empty:
            continue
        for i in units.query(free, predicate='intersects'):
            piece = polygonal(free.intersection(outlines[codes[i]]))
            if piece is not None and piece.area > 0:
                parts.setdefault(codes[i], []).append(piece)
    if not parts:
        return geometry, ()
    joined = {code: shapely.union_all(found) for code, found in parts.items()}
    new = polygonal(shapely.union_all([geometry, *joined.values()]))
    outline, errors = new.boundary, []
    for code, piece in joined.items():
        line = piece.boundary.intersection(outline).difference(sources.cadastral_outline(code))
        if line.length > 0:
            errors.append(ErrorPart('istat-boundaries', line.buffer(REGION_STEP_M), sources.istat_errors.get(code)))
    return new, tuple(errors)


def buffer_extent(sources: Sources, origins, annexed=None, drawn=None, held=None,
                  beyond=None) -> BaseGeometry | None:
    """The buffer zone: land within each origin's width, the units the annex places wholly in
    it and the parts the Region's layer supplies, outside the origins. `origins` is
    [(geometry, metres)] or [(geometry, metres, hold)]: the band of an origin with `hold`
    is held to `held`, the units the annex lists, as the containment band is; the part it
    would reach beyond them is appended to `beyond`."""
    origins = [(o[0], o[1], o[2] if len(o) > 2 else False) for o in origins]
    inner = _union(*(o for o, _, _ in origins))
    if inner is None:
        return None
    parts = []
    for i, (o, m, hold) in enumerate(origins):
        if o is None:
            continue
        band = outward_band(o, m, sources.land_near(o, m))       # already outside its own origin
        for j, (other, _, _) in enumerate(origins):
            if j != i and other is not None:
                band = _minus(band, other)
        if hold and held is not None:
            if beyond is not None:
                beyond.append(polygonal(band.difference(held)))
            band = polygonal(band.intersection(held))
        parts.append(band)
    parts += [_minus(annexed, inner), _minus(drawn, inner)]
    # Where the band only touches land or another origin, the intersection keeps a line; a zone is its area.
    return polygonal(_union(*parts))


def _minus(a: BaseGeometry | None, b: BaseGeometry) -> BaseGeometry | None:
    """a less b, reading only the part of b within a's bounds."""
    if a is None or a.is_empty:
        return a
    return polygonal(a.difference(shapely.make_valid(shapely.clip_by_rect(b, *a.bounds))))


def _opened(geometry: BaseGeometry | None) -> list:
    """The polygons of `geometry` wider than SEAM_M: a narrower piece is the sources' seam, not land."""
    if geometry is None or geometry.is_empty:
        return []
    opened = geometry.buffer(-SEAM_M / 2, join_style='mitre').buffer(SEAM_M / 2, join_style='mitre')
    kept = polygonal(opened.intersection(geometry))
    return [p for p in getattr(kept, 'geoms', [kept]) if p.geom_type == 'Polygon' and p.area > OUTSIDE_TOLERANCE_M2]


def _reach(piece: BaseGeometry, line: BaseGeometry) -> float:
    """An upper bound on the distance from any place in `piece` to `line`: the farthest of its
    outline's samples, plus the radius of the largest circle inside it."""
    samples = shapely.points(shapely.get_coordinates(shapely.segmentize(piece.boundary, REGION_STEP_M)))
    far = float(shapely.distance(samples, line).max()) if len(samples) else 0.0
    return far + shapely.maximum_inscribed_circle(piece, 1.0).length + REGION_STEP_M + APPROXIMATION_M


def _disagreements(sources: Sources, zones, roles, buffer, held, beyond, listed_partial) -> tuple:
    """Where the bands drawn from the act's plants and the units its annex lists disagree.

    beyond: land the stated band reaches in no listed unit (the buffer band is held there), and
    land a plant's circle reaches in no listed unit; short: a unit the annex lists partly in the
    buffer that no band reaches. Each keeps its reach, carried in the error there."""
    inner = [zones[r].geometry for r in zones if zones[r].geometry is not None]
    area = _union(buffer, *inner)
    if area is None:
        return ()
    line = area.boundary
    found = []

    def add(role, kind, pieces, place=None):
        for piece in pieces:
            labels = sources.sheet_labels(piece)
            where = place or (', '.join(f'{label} ({m2 / 1e4:.2f} ha)' for label, m2 in labels[:6])
                              + (f' and {len(labels) - 6} more' if len(labels) > 6 else '')
                              or 'land no held sheet covers')
            found.append(Disagreement(role, kind, where, piece, _reach(piece, line)))

    reached = _union(*beyond)
    if reached is not None:
        add('buffer', 'beyond', _opened(polygonal(reached).difference(area)))
    for role in roles:
        if zones[role].geometry is not None:
            add(role, 'beyond', _opened(polygonal(zones[role].geometry.difference(held))))
    for u in listed_partial:
        if u.geometry is not None and u.geometry.intersection(area).area <= OUTSIDE_TOLERANCE_M2:
            add('buffer', 'short', [p for p in getattr(u.geometry, 'geoms', [u.geometry]) if p.geom_type == 'Polygon'],
                u.place)
    return tuple(found)


def construct(sources: Sources, version, *, plants=None, adopted: date | None = None) -> tuple[Zone, ...]:
    """The zones of one version, each from its operative rule or, failing one, its annex.

    `plants` maps a plant-defined role (`plant_roles`) to the row 1 positives the act names,
    (x, y, error_m) or `Plant`. None reads them from row 1 in the store (`located_plants`).
    """
    operative = dispositivo(_act_text(sources.root, version.source_path))
    plants = located_plants(sources, version) if plants is None else plants
    rules = read_rules(sources, version, operative)
    build = _Builder(sources, version)
    roles = plant_roles(sources, version)
    floor = _metres(sources.parameters[INFECTED_RADIUS]['value'], sources.parameters[INFECTED_RADIUS]['unit'])
    eradication = _metres(sources.parameters[ERADICATION_BUFFER]['value'],
                          sources.parameters[ERADICATION_BUFFER]['unit'])
    zones = {}
    buffer_width = rules.buffer[0] if rules.buffer else _metres(
        sources.parameters[CONTAINMENT_BUFFER if (rules.inward or rules.annex_iii or rules.whole_role == 'containment')
                           else ERADICATION_BUFFER]['value'], 'km')

    # The infected zone.
    if 'infected' in roles:
        metres, width, quote = rules.radius or (floor, INFECTED_RADIUS, 'Article 4(2), applied by the act '
                                                'to the infected plants it names')
        found = act_plants(sources, version, 'infected', metres, build=build, operative=operative,
                           located=plants.get('infected', ()))
        zones['infected'] = Zone('infected', build.words('infected'), _circles(found, metres), quote, ('plants',),
                                 width, errors=_plant_errors(sources, version, 'infected', found,
                                                             metres + buffer_width), plants=found)
    else:
        start, whole = len(build.istat_drawn), len(build.whole)
        geometry, unplaced = build.annex('infected', build.by_role['infected'])
        listed = geometry
        rule = 'annex'
        if rules.whole and rules.whole_role == 'infected':
            named = [build.named_comune(n) for n in rules.whole]
            part, _ = build.annex('infected', build.by_role['infected'], only_comune=rules.part)
            geometry = _union(geometry, *named, part)
            rule = rules.quotes[0]
        geometry, gaps, gap_errors, replaced = _layer_gaps(sources, version, 'infected', geometry, build, start)
        listed = _relisted(listed, replaced)
        drawn, unplaced, drawn_errors = _drawn(sources, version, 'infected', unplaced)
        used = set(build.used) | ({'region-layer'} if drawn is not None or gaps is not None else set())
        geometry = _union(geometry, drawn)
        # Sealed first: a seam the seal closes off from the outside is enclosed land too.
        geometry, interior_errors = _whole_interior(sources, geometry and seal(geometry), build.whole[whole:])
        used |= {'istat-boundaries'} if interior_errors else set()
        zones['infected'] = Zone('infected', build.words('infected'), geometry, rule,
                                 tuple(sorted(used)), None, unplaced, listed,
                                 _source_errors(sources, build.used, build) + drawn_errors + gap_errors
                                 + interior_errors, drawn=_union(drawn, gaps))
    infected = zones['infected'].geometry

    # Foci under eradication: a radius around the infected plants the act names for them.
    if 'focus' in roles:
        found = act_plants(sources, version, 'focus', floor, build=build, operative=operative,
                           located=plants.get('focus', ()))
        zones['focus'] = Zone('focus', build.words('focus'), _circles(found, floor),
                              'Article 4(2), applied by the act to the infected plants it names',
                              ('plants',), INFECTED_RADIUS,
                              errors=_plant_errors(sources, version, 'focus', found, floor + eradication),
                              plants=found)

    # The buffer zone: outward from the infected zone at the act's width, or at B's floor
    # for the branch where the act names a buffer and states no width; outward from a
    # focus at the eradication floor.
    if BUFFER_NAMED.search(operative) or build.by_role['buffer']:
        branch = CONTAINMENT_BUFFER if (rules.inward or rules.annex_iii or rules.whole_role == 'containment') \
            else ERADICATION_BUFFER
        metres, width, quote = rules.buffer or (_metres(sources.parameters[branch]['value'],
                                                        sources.parameters[branch]['unit']), branch,
                                                "the Regulation's floor for the buffer zone the act names")
        # A band drawn from the act's plants is held to the units the annex lists.
        origins = [(infected, metres, 'infected' in roles)]
        focus = zones.get('focus')
        if focus is not None and focus.geometry is not None:
            origins.append((focus.geometry, eradication, True))
        # Each unit the annex places wholly in the buffer is in it. A unit it places partly
        # is placed by the width the act states; where it states none, B's floor is only a
        # minimum, and the Region's layer places the part.
        build.used, annexed, partial, listed_partial = set(), None, (), ()
        if build.by_role['buffer']:
            annexed, partial = build.annex('buffer', build.by_role['buffer'])
            listed_partial = partial
            partial = partial if rules.buffer is None else ()
            if annexed is not None:
                quote = f'{quote}, with the units its annex places wholly in it'
        drawn, partial, drawn_errors = _drawn(sources, version, 'buffer', partial)
        held, beyond = None, []
        if build.by_role['buffer'] and any(hold for _, _, hold in origins):
            held = _union(annexed, *(u.geometry for u in listed_partial if u.geometry is not None),
                          *(g for role in roles for _, g in plant_units(sources, version, role, build=build,
                                                                         operative=operative) if g is not None))
            if held is not None:
                held = seal(held)                  # the seams between listed sheets are not land outside them
                build.used.add('cadastre')
                quote = f'{quote}, held to the units its annex lists'
        geometry = buffer_extent(sources, origins, annexed, drawn, held, beyond)
        used = {s for z in zones.values() for s in z.sources} | build.used
        used |= {'region-layer'} if drawn is not None else set()
        disagreements = (_disagreements(sources, zones, roles, geometry, held, beyond, listed_partial)
                         if held is not None else ())
        errors = tuple(p for z in zones.values() for p in z.errors) + _source_errors(sources, build.used, build) \
            + drawn_errors + tuple(ErrorPart('annex-disagreement', d.geometry, d.reach_m, place_only=True)
                                   for d in disagreements)
        zones['buffer'] = Zone('buffer', build.words('buffer'), geometry, quote, tuple(sorted(used)), width,
                               partial, annexed, errors, drawn=drawn, disagreements=disagreements)

    # The part under containment measures.
    build.used = set()
    if rules.annex_iii == 'containment':
        start, whole = len(build.istat_drawn), len(build.whole)
        geometry = build.annex_iii(version.effective_from)
        geometry, gaps, gap_errors, _ = _layer_gaps(sources, version, 'containment', geometry, build, start)
        geometry, interior_errors = _whole_interior(sources, geometry, build.whole[whole:])
        used = tuple(sorted(build.used | ({'region-layer'} if gaps is not None else set())
                            | ({'istat-boundaries'} if interior_errors else set())))
        zones['containment'] = Zone('containment', build.words('containment'), geometry, rules.quotes[-1],
                                    used, errors=_source_errors(sources, build.used, build) + gap_errors
                                    + interior_errors, drawn=gaps)
    elif rules.whole and rules.whole_role == 'containment':
        start, whole = len(build.istat_drawn), len(build.whole)
        named = [build.named_comune(n) for n in rules.whole]
        part, unplaced = build.annex('containment', build.by_role['containment'], only_comune=rules.part)
        geometry, gaps, gap_errors, _ = _layer_gaps(sources, version, 'containment', _union(*named, part),
                                                    build, start)
        units = build.whole[whole:]                        # the former band is not a unit named whole
        former = None
        if rules.former:
            zone = build.annex_iii(adopted or version.effective_from)
            former = inward_band(zone, rules.former[0], sources.land_near(zone, SEAM_M), outside=zone)
        geometry, interior_errors = _whole_interior(sources, _union(geometry, former), units)
        used = set(build.used) | ({'region-layer'} if gaps is not None else set()) \
            | ({'istat-boundaries'} if interior_errors else set())
        zones['containment'] = Zone('containment', build.words('containment'), geometry,
                                    rules.quotes[0], tuple(sorted(used)),
                                    rules.former[1] if rules.former else None, unplaced, part,
                                    _source_errors(sources, build.used, build) + gap_errors + interior_errors,
                                    drawn=gaps)
    elif rules.inward and infected is not None:
        # Article 15(2)(a): "within an area measuring at least 2 km from the border of the
        # infected zone with the buffer zone". The annex lists the units the band covers:
        # a unit it places wholly is in it, a unit it lists partly holds the band's part,
        # and the band covers no unit the annex does not list.
        metres, width, quote = rules.inward
        buffer = zones.get('buffer')
        if buffer and buffer.geometry is not None:
            band = inward_band(infected, metres, buffer.geometry)
        else:
            band = inward_band(infected, metres, sources.land_near(infected, SEAM_M), outside=infected)
        listed, partial = None, ()
        if build.by_role['containment']:
            listed, partial = build.annex('containment', build.by_role['containment'])
            reach = _union(listed, *(u.geometry for u in partial if u.geometry is not None))
            # Where the band only touches a listed unit, the intersection keeps a line; a zone is its area.
            band = polygonal(_union(band.intersection(reach) if reach is not None else None, listed))
            partial = tuple(u for u in partial if u.geometry is None)
        zones['containment'] = Zone('containment', build.words('containment'), band, quote,
                                    zones['infected'].sources, width, partial, listed, zones['infected'].errors)
    elif build.by_role['containment']:
        geometry, unplaced = build.annex('containment', build.by_role['containment'])
        used = set(build.used)
        zones['containment'] = Zone('containment', build.words('containment'), geometry, 'annex',
                                    tuple(sorted(used)), None, unplaced, geometry, _source_errors(sources, used, build))
    return tuple(zones[r] for r in ROLES if r in zones)


def region_layer_samples(sources: Sources, geography: AdoptedGeography):
    """[(layer record, [(x, y, distance)])]: the Region's layer against the zone's outer limit
    where the act fixes it by the units it places wholly in the zone. The samples lie on the
    cadastral outline of those units where it bounds the zone against held land outside it,
    away from the units the act places partly (whose part the layer itself supplies)."""
    out = []
    for zone in geography.zones:
        layer = sources.region_layer(geography.provision_version_id, zone.role)
        if layer is None or zone.listed is None or zone.geometry is None:
            continue
        record, drawn = layer
        outside = sources.cadastral_near(zone.listed).difference(zone.geometry.buffer(APPROXIMATION_M))
        edge = zone.listed.boundary.intersection(zone.geometry.boundary.buffer(APPROXIMATION_M))
        edge = edge.intersection(outside.buffer(2 * APPROXIMATION_M))
        partial = [u.geometry for u in zone.unplaced if u.geometry is not None]
        if zone.drawn is not None:
            partial.append(zone.drawn)
        if partial:
            edge = edge.difference(shapely.union_all(partial).buffer(REGION_STEP_M))
        points = _samples(shapely.line_merge(edge) if edge.geom_type == 'MultiLineString' else edge, REGION_STEP_M)
        if not len(points):
            continue
        distances = shapely.distance(points, drawn.boundary)
        xy = shapely.get_coordinates(points)
        out.append((dict(record, role=zone.role),
                    [(float(x), float(y), float(d)) for (x, y), d in zip(xy, distances)]))
    return out


def boundary_distances(a: BaseGeometry, b: BaseGeometry, step_m: float = 10.0):
    """Directed distances from points every `step_m` along a's boundary to b's boundary."""
    points, pieces = [], []
    for part in getattr(a.boundary, 'geoms', [a.boundary]):
        count = max(2, int(part.length // step_m) + 1)
        points.append(shapely.line_interpolate_point(part, numpy.linspace(0, part.length, count)))
    for part in getattr(b.boundary, 'geoms', [b.boundary]):
        c = numpy.asarray(part.coords)
        pieces.append(shapely.linestrings(numpy.stack([c[:-1], c[1:]], axis=1)))
    _, distances = shapely.STRtree(numpy.concatenate(pieces)).query_nearest(
        numpy.concatenate(points), return_distance=True, all_matches=False)
    return distances


def reach_start(root: Path, decision: date) -> date:
    """The earliest event date the longest accepted backward clock reaches from `decision`."""
    clocks = json.loads((Path(root) / 'regulation/stage-b/clocks-and-parameters.json').read_text())['clocks']
    clock, = [c for c in clocks if c['clock_id'] == REACH_CLOCK]
    if clock['unit'] != 'years':
        raise ValueError('The reach clock changed unit')
    years = int(clock['magnitude'])
    try:
        return decision.replace(year=decision.year - years)
    except ValueError:              # 29 February
        return decision.replace(year=decision.year - years, day=28)


def in_reach(version, start: date, decision: date) -> bool:
    end = version.effective_to_exclusive
    return version.effective_from <= decision and (end is None or end > start)


def adopted_geography(root: Path, *, decision: date, plants=None, sources: Sources | None = None, only=None):
    """Every consumed, in-reach A area version's `adopted-geography`, in A's order; with
    `only`, those of the listed provision version ids. Each is built when it is reached, so
    a caller that keeps one at a time holds one version's geometry.

    The infected plants a version names are the row 1 positives `named_plants` finds, read
    from the store with row 1's measured error (`Sources.row1`). `plants`, where given, maps
    a provision version id to them per plant-defined role, as (x, y, error_m).
    """
    root = Path(root)
    sources = sources or Sources(root)
    start = reach_start(root, decision)
    all_versions = versions(root)
    adopted = {}
    for v in all_versions:
        adopted[v.instrument_id] = min(adopted.get(v.instrument_id, v.effective_from), v.effective_from)
    for version in all_versions:
        if not version.consumed or not in_reach(version, start, decision):
            continue
        if only is not None and version.provision_version_id not in only:
            continue
        if version.statements is None:
            raise FileNotFoundError(f'{version.provision_version_id}: the act document is not in this store')
        supplied = None if plants is None else plants.get(version.provision_version_id, {})
        zones = construct(sources, version, plants=supplied, adopted=adopted[version.instrument_id])
        geography = AdoptedGeography(version.provision_version_id, version.instrument_id, version.effective_from,
                                     version.effective_to_exclusive, zones)
        if plants is None and any(r['source'] == 'region-layer' and r.get('provision_version_id')
                                  == version.provision_version_id for r in records(root, 'positional-error')):
            sources.region_samples(version, geography)      # measured on this construction, not a second one
        yield geography


# --- the row 1 positives that are the infected plants an act names -------------------

SUBSPECIES = re.compile(r'\b(?:SOTTOSPECIE|SUBSPECIE|SUB\.)\s*(PAUCA|MULTIPLEX|FASTIDIOSA)\b', re.I)


@dataclass(frozen=True)
class Observation:
    """A positive observation from the ordinary monitoring reader (INPUTS row 1)."""
    day: date
    subspecies: tuple[str, ...]
    x: float | None                        # EPSG:32633, where the row locates it
    y: float | None
    comune: str | None = None              # the cadastral reference the row prints
    foglio: str | None = None
    particella: str | None = None


def named_plants(sources: Sources, version, observations) -> dict:
    """The row 1 positives that are the infected plants the act names, per plant-defined role.

    The act names its plants by subspecies, comune and date, and lists in its infected-zone
    or focus table the sheets and parcels the plants' zone covers. A plant it names is a
    positive observed up to the act that lies in a listed unit, by its position or, where
    row 1 prints the plant's cadastral reference, by that sheet or parcel; and that row 1
    types as the act's subspecies or does not type (row 1 publishes a subspecies only after
    the typing the act reports).
    `observations` are `Observation`s or (day, subspecies, x, y) tuples. Returns per role
    the (x, y) positions of the located plants.
    """
    build = _Builder(sources, version)
    build.legend = False                       # every listed unit, whole
    observations = [o if isinstance(o, Observation) else Observation(*o) for o in observations]
    observations = [o for o in observations if o.day <= version.effective_from]
    operative = dispositivo(_act_text(sources.root, version.source_path))
    found = {}
    for role in plant_roles(sources, version):
        wanted = []
        for s in _plant_statements(sources, version, build, role, operative):
            named = (SUBSPECIES.search(s.zone_heading) or SUBSPECIES.search(version.state)
                     or SUBSPECIES.search(operative))
            if named is None:
                raise ValueError(f'{version.provision_version_id}: {s.locator} names no subspecies')
            geometry, _ = build.annex(role, [s])
            references = set()
            if s.scope == 'sheets' and s.comune:
                catastale = build.comune(s.comune, s.province).catastale
                for sheet in s.sheets:
                    references |= ({(catastale, sheet.number, p) for p in sheet.parcels} if sheet.parcels
                                   else {(catastale, sheet.number, None)})
            wanted.append((named.group(1).upper(), geometry, references))

        located = [o for o in observations if o.x is not None]
        points = shapely.points([(o.x, o.y) for o in located]) if located else numpy.array([], dtype=object)
        chosen = numpy.zeros(len(located), dtype=bool)
        for name, geometry, references in wanted:
            typed = numpy.array([name in o.subspecies or not o.subspecies for o in located], dtype=bool)
            inside = (shapely.covers(geometry, points) if geometry is not None and len(located)
                      else numpy.zeros(len(located), dtype=bool))
            by_reference = numpy.array([bool(o.comune and o.foglio) and (
                (o.comune, str(o.foglio).lstrip('0'), None) in references
                or (o.comune, str(o.foglio).lstrip('0'), str(o.particella or '').lstrip('0')) in references)
                for o in located], dtype=bool)
            chosen |= typed & (inside | by_reference)
        found[role] = tuple(sorted({(o.x, o.y) for o, keep in zip(located, chosen) if keep}))
    return found


def _derived_root(root: Path) -> Path:
    from .store import store_root
    return store_root(Path(root))


ROW1_SOURCE = 'corpus/sources/monitoring'


def row1_key(root: Path) -> str | None:
    """The key of row 1's grouped observations in the store (the ordinary monitoring reader's),
    or None where the store does not hold them for the current reader."""
    from . import monitoring
    from .store import derived_path
    source = Path(root) / ROW1_SOURCE
    try:
        key = monitoring._grouping_key(source)
    except (OSError, ValueError, KeyError):
        return None
    grouped = derived_path(_derived_root(root), 'monitoring/groups', key, monitoring.reader_version())
    return f'{key}-{monitoring.reader_version()}' if grouped.exists() else None


def _row1_rows(source: Path) -> list:
    """Every located positive of the ordinary monitoring reader, as `named_plants` reads it."""
    from pyproj import Transformer
    from . import monitoring
    to_utm = {}
    out = []
    for group in monitoring.distinct_observations(source):
        if group.positive is not True or group.day is None or not group.locations:
            continue
        crs, (x, y) = group.locations[0]
        if crs != TARGET_CRS:
            if crs not in to_utm:
                to_utm[crs] = Transformer.from_crs(crs, TARGET_CRS, always_xy=True)
            x, y = to_utm[crs].transform(x, y)
        attributes = {}
        for member in group.members:
            attributes.update(dict(member.carried))
            attributes.update(dict(member.attributes))
        out.append({'day': group.day.isoformat(), 'subspecies': sorted(s.upper() for s in group.values('subspecies')),
                    'x': float(x), 'y': float(y), 'comune': attributes.get('COMUNE'),
                    'comune_cod': attributes.get('COMUNE_COD') or attributes.get('COD_COMUNE'),
                    'foglio': attributes.get('FOGLIO'), 'particella': attributes.get('PARTICELLA')})
    return out


def row1_positives(root: Path) -> dict | None:
    """{'error_m', 'positives'}: row 1's located positives (`_row1_rows`) and its measured
    positional error (`spatial.positional_terms`), or None where the store does not hold row
    1's grouped observations. This never derives them. The error is read from row 1 on each
    call, since it depends on inputs the positives' key does not cover; only the positives
    are cached in the derived store, under the grouped observations' key and the digest of
    `_row1_rows`."""
    import hashlib
    import inspect
    key = row1_key(root)
    if key is None:
        return None
    from .spatial import positional_terms
    try:
        error = positional_terms(_derived_root(root)).error_m
    except (OSError, KeyError, ValueError, MissingInput):
        return None
    digest = hashlib.sha256(f'{key}\0positives\0{inspect.getsource(_row1_rows)}'.encode()).hexdigest()
    target = _derived(root, 'row1-positives', digest)
    if target.exists():
        positives = json.loads(target.read_text())
    else:
        positives = _row1_rows(Path(root) / ROW1_SOURCE)
        _write_derived(target, positives)
    return {'error_m': error, 'positives': positives}

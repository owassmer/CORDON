"""Adopted-area geometry for Stage C, one per consumed A area version, built as its act defines it.

C tests a supplied point or parcel against a supplied adopted area (`adopted_area_facts`);
this module supplies that area and nothing else. It never decides whether a place lies in
an area. It supplies every A area version whose condition tests the adopted geography and
whose interval overlaps the reach (`SPEC.md`, admission).

Each zone is built from the act's operative text first. The annex tables are that rule's
result rendered per unit, not drawn lines:

- named whole comuni and the infected zone of Annex III Part A of Regulation (EU)
  2020/1201 (the annex version A holds for the day): ISTAT boundaries;
- a band the act states in kilometres from a zone: that zone offset at the width, clipped
  to land; outward for a buffer zone, inward from the zone's land border for a zone
  under containment measures;
- a radius the act states around the infected plants it names: their located positions
  offset at the width.

A width is B's: the act's own figure where it states one, B's floor where it states
"almeno" or applies the Regulation without a figure. Only a zone for which the
operative text states no rule is defined by the annex, by the units it lists: whole
provinces and comuni from ISTAT, sheets and parcels from the cadastre. Where the act's
legend marks a sheet as only partly in such a zone, the act states nothing that places
the part; that sheet is quoted, and it matters to C only where it lies outside the rest
of the adopted area.

The positional error bound of each geometry source is the measured qualification held in
`corpus/sources/areas/geometry.json`; the infected plants' positions carry the error of
their observations (INPUTS row 1).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import cached_property
import csv
import json
from pathlib import Path
import re

from pyproj import CRS
import shapely
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, distance_envelope
from .administrative import TARGET_CRS, AdministrativeUnits, _blob, records, _key
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
    """A unit the annex places partly in a zone the operative text gives no rule for."""
    role: str
    locator: str
    place: str
    quote: str                             # the act's words: its legend and the cell
    geometry: BaseGeometry | None          # the whole unit, where the cadastre holds it


@dataclass(frozen=True)
class Zone:
    role: str                              # infected | containment | focus | buffer
    words: tuple[str, ...]                 # the act's own headings for this part
    geometry: BaseGeometry | None          # EPSG:32633
    rule: str                              # the operative words it is built from, or 'annex'
    sources: tuple[str, ...]               # istat-boundaries | cadastre | plants
    width: str | None = None               # the B parameter the width is
    unplaced: tuple[Unplaced, ...] = ()


@dataclass(frozen=True)
class AdoptedGeography:
    """The `adopted-geography` input for one A area version."""
    provision_version_id: str
    instrument_id: str
    effective_from: date
    effective_to_exclusive: date | None
    zones: tuple[Zone, ...]
    error_m: float | None                  # the bound over every source the geometry uses
    crs: str = TARGET_CRS
    bounds: tuple[str, ...] = ()           # the sources that carry a measured bound

    def zone(self, role) -> Zone | None:
        return next((z for z in self.zones if z.role == role), None)

    @cached_property
    def geometry(self) -> BaseGeometry | None:
        parts = [z.geometry for z in self.zones if z.geometry is not None and not z.geometry.is_empty]
        return shapely.make_valid(shapely.union_all(parts)) if parts else None

    @property
    def unplaced(self) -> tuple[Unplaced, ...]:
        """Partly-included units whose part could fall outside the constructed area."""
        area = self.geometry
        return tuple(u for z in self.zones for u in z.unplaced
                     if u.geometry is None or area is None
                     or u.geometry.difference(area).area > OUTSIDE_TOLERANCE_M2)

    @property
    def shared_boundary(self) -> BaseGeometry | None:
        """The interface between the buffer zone and the rest of the adopted area."""
        buffer = self.zone('buffer')
        inner = [z.geometry for z in self.zones if z.role != 'buffer' and z.geometry is not None]
        if buffer is None or buffer.geometry is None or not inner:
            return None
        line = buffer.geometry.boundary.intersection(shapely.union_all(inner).boundary)
        return None if line.is_empty else line

    def metric(self) -> MetricGeometry:
        """The adopted area as C's `MetricGeometry`, or MissingInput."""
        if self.geometry is None or any(z.geometry is None and 'plants' in z.sources for z in self.zones):
            raise MissingInput(f'{self.provision_version_id}: the positions of the infected plants '
                               'the act names are not supplied (INPUTS row 1)')
        if self.unplaced:
            u = self.unplaced[0]
            raise MissingInput(f'{self.provision_version_id}: the act places part of {u.place} in its '
                               f'{u.role} zone by its map alone: "{u.quote}"')
        if self.error_m is None:
            unbounded = sorted({s for z in self.zones for s in z.sources} - set(self.bounds))
            raise MissingInput(f'{self.provision_version_id}: no positional error bound is supplied for '
                               f'the geometry source {", ".join(unbounded)}')
        return MetricGeometry(self.geometry, UTM, self.error_m)


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


class Sources:
    """The retained geometry sources and A/B inputs, read from their records."""

    def __init__(self, root: Path):
        self.root = Path(root)

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
        found, seen = {}, set()
        for record in records(self.root, 'cadastre-fogli'):
            body = _blob(self.root, record).read_bytes()
            features = (_inspire_zoning(body, record) if record['format'] == 'inspire-gml'
                        else _arcgis_sheets(body, record))
            for a, geometry in features:
                identity = (a['COMUNE'], a['SEZIONE'], a['FOGLIO'], a['ALLEGATO'], a['SVILUPPO'],
                            geometry.wkb if record['format'] != 'inspire-gml' else None)
                if identity in seen:
                    continue
                seen.add(identity)
                found.setdefault((a['COMUNE'], a['SEZIONE'], a['FOGLIO']), []).append((a, geometry))
        return found

    @cached_property
    def parcels(self) -> dict:
        found = {}
        for record in records(self.root, 'cadastre-particelle'):
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

    @cached_property
    def error_bounds(self) -> dict:
        """Measured positional error bound per geometry source family."""
        return {r['source']: float(r['error_m']) for r in records(self.root, 'positional-error')}

    def unpublished(self, comune) -> tuple[tuple[str, ...], BaseGeometry | None]:
        """The comune's sheets neither cadastre publishes, and their union.

        A comune's sheets are numbered from 1 and tile its territory, so the sheets missing
        from the published numbering occupy the territory no published sheet covers: the
        ISTAT boundary minus every published sheet. Seams narrower than SEAM_M between drawn
        sheets are not territory; a remaining piece that lies wholly within the ISTAT error
        bound of the ISTAT outline is the two outlines' disagreement, not a sheet.
        """
        return self._unpublished.setdefault(comune.catastale, self._unpublished_of(comune))

    @cached_property
    def _unpublished(self) -> dict:
        return {}

    def _unpublished_of(self, comune):
        held = {n: shapely.union_all([g for _, g in found]) for (c, section, n), found in self.sheets.items()
                if c == comune.catastale and not section}
        numbers = [int(n) for n in held if n.isdigit()]
        missing = tuple(str(n) for n in range(1, max(numbers, default=0) + 1) if str(n) not in held)
        if not missing:
            return (), None
        territory = self.administrative.comune_geometry(comune)
        gap = territory.difference(shapely.union_all(list(held.values())))
        gap = gap.buffer(-SEAM_M / 2, join_style='mitre').buffer(SEAM_M / 2, join_style='mitre').intersection(gap)
        border = territory.boundary.buffer(self.error_bounds['istat-boundaries'])
        pieces = [p for p in getattr(gap, 'geoms', [gap]) if p.geom_type == 'Polygon' and not border.covers(p)]
        return missing, (shapely.union_all(pieces) if pieces else None)

    @cached_property
    def land(self) -> BaseGeometry:
        units = self.administrative
        parts = [units.province_geometry(p) for p in units.provinces.values() if p.region in LAND_REGIONS]
        return shapely.union_all([p for p in parts if p is not None])

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


def inward_band(zone: BaseGeometry, metres: float, land: BaseGeometry) -> BaseGeometry:
    """The part of the zone within `metres` of its border with the land outside it."""
    outside = land.difference(zone)
    border = zone.boundary.intersection(_envelope(outside, APPROXIMATION_M).geometry)
    return _envelope(border, metres).geometry.intersection(zone)


class _Builder:
    def __init__(self, sources: Sources, version):
        self.sources, self.version = sources, version
        self.units = sources.administrative
        self.used: set[str] = set()
        statements = version.statements or ()
        self.legend = any('*' in s.text or 'INTERAMENTE' in (s.qualification or '').upper() for s in statements)
        self.by_role = {role: [s for s in statements if role_of(s) == role] for role in ROLES}

    def comune(self, name, province=None):
        comune = self.units.comune(name=name, province=province)
        if comune is None:
            raise ValueError(f'{self.version.provision_version_id}: {name} is not one ISTAT comune')
        return comune

    def istat(self, geometry):
        self.used.add('istat-boundaries')
        return geometry

    def whole_comune(self, name, province=None):
        return self.istat(self.units.comune_geometry(self.comune(name, province)))

    def named_comune(self, name):
        """A comune the dispositivo names, as the Region's own act writes it."""
        comune = self.units.comune(name=name, region='Puglia')
        if comune is None:
            raise ValueError(f'{self.version.provision_version_id}: {name} is not one ISTAT comune in Puglia')
        return self.istat(self.units.comune_geometry(comune))

    def annex_iii(self, day):
        parts = []
        for unit in self.sources.annex_iii(day):
            if unit[0] == 'province':
                parts.append(self.istat(self.units.province_geometry(self.units.province(unit[1]))))
            else:
                parts.append(self.whole_comune(unit[1], unit[2]))
        return shapely.union_all(parts)

    def sheet(self, comune, sheet, listed=()):
        """(extent, exact, sources). A sheet neither cadastre publishes (Massafra 15, 16 and 23) lies
        in the comune's unpublished territory (`Sources.unpublished`), built from ISTAT and
        the cadastre. That territory is the sheet exactly when it is the only unpublished
        sheet, or when every unpublished sheet is listed in `listed` alike; otherwise it
        contains the sheet."""
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
        return territory, set(missing) <= set(listed), ('cadastre', 'istat-boundaries')

    def annex(self, role, statements, only_comune=None):
        """The zone the annex's listed units define, and its partly-included units."""
        parts, unplaced = [], []
        for s in statements:
            if only_comune and _key(s.comune) != _key(only_comune):
                continue
            if s.scope == 'whole-province':
                parts.append(self.istat(self.units.province_geometry(self.units.province(s.province))))
                continue
            comune = self.comune(s.comune, s.province)
            if s.scope == 'whole-comune':
                parts.append(self.istat(self.units.comune_geometry(comune)))
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
        return (shapely.union_all(parts) if parts else None), tuple(unplaced)

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


def _circles(points, metres) -> BaseGeometry | None:
    if not points:
        return None
    return _envelope(shapely.union_all([Point(x, y) for x, y in points]), metres).geometry


def construct(sources: Sources, version, *, plants=None, adopted: date | None = None) -> tuple[Zone, ...]:
    """The zones of one version, each from its operative rule or, failing one, its annex.

    `plants` maps a plant-defined role (`plant_roles`) to the (x, y) positions of the
    infected plants the act names for it (`named_plants`).
    """
    plants = plants or {}
    operative = dispositivo(_act_text(sources.root, version.source_path))
    rules = read_rules(sources, version, operative)
    build = _Builder(sources, version)
    land = sources.land
    roles = plant_roles(sources, version)
    floor = _metres(sources.parameters[INFECTED_RADIUS]['value'], sources.parameters[INFECTED_RADIUS]['unit'])
    zones = {}

    # The infected zone.
    if 'infected' in roles:
        metres, width, quote = rules.radius or (floor, INFECTED_RADIUS, 'Article 4(2), applied by the act '
                                                'to the infected plants it names')
        zones['infected'] = Zone('infected', build.words('infected'), _circles(plants.get('infected'), metres),
                                 quote, ('plants',), width)
    else:
        geometry, unplaced = build.annex('infected', build.by_role['infected'])
        rule = 'annex'
        if rules.whole and rules.whole_role == 'infected':
            named = [build.named_comune(n) for n in rules.whole]
            part, _ = build.annex('infected', build.by_role['infected'], only_comune=rules.part)
            geometry = _union(geometry, *named, part)
            rule = rules.quotes[0]
        zones['infected'] = Zone('infected', build.words('infected'), geometry, rule,
                                 tuple(sorted(build.used)), None, unplaced)
    infected = zones['infected'].geometry

    # The part under containment measures.
    before = set(build.used)
    if rules.annex_iii == 'containment':
        zones['containment'] = Zone('containment', build.words('containment'),
                                    build.annex_iii(version.effective_from), rules.quotes[-1],
                                    ('istat-boundaries',))
    elif rules.whole and rules.whole_role == 'containment':
        named = [build.named_comune(n) for n in rules.whole]
        part, unplaced = build.annex('containment', build.by_role['containment'], only_comune=rules.part)
        former = None
        if rules.former:
            former = inward_band(build.annex_iii(adopted or version.effective_from), rules.former[0], land)
        zones['containment'] = Zone('containment', build.words('containment'), _union(*named, part, former),
                                    rules.quotes[0], tuple(sorted(build.used - before)) or ('istat-boundaries',),
                                    rules.former[1] if rules.former else None, unplaced)
    elif rules.inward and infected is not None:
        metres, width, quote = rules.inward
        zones['containment'] = Zone('containment', build.words('containment'),
                                    inward_band(infected, metres, land), quote, zones['infected'].sources, width)
    elif build.by_role['containment']:
        geometry, unplaced = build.annex('containment', build.by_role['containment'])
        zones['containment'] = Zone('containment', build.words('containment'), geometry, 'annex',
                                    tuple(sorted(build.used - before)), None, unplaced)

    # Foci under eradication: a radius around the infected plants the act names for them.
    # A focus row whose units hold none of those plants is placed by the act's map alone.
    if 'focus' in roles:
        points = plants.get('focus') or ()
        _, rows = build.annex('focus', build.by_role['focus'])
        unplaced = tuple(u for u in rows if u.geometry is None
                         or not any(u.geometry.covers(Point(x, y)) for x, y in points))
        zones['focus'] = Zone('focus', build.words('focus'), _circles(points, floor),
                              'Article 4(2), applied by the act to the infected plants it names',
                              ('plants',), INFECTED_RADIUS, unplaced)

    # The buffer zone: outward from the infected zone at the act's width, or at B's floor
    # for the branch where the act names a buffer and states no width; outward from a
    # focus at the eradication floor.
    if BUFFER_NAMED.search(operative) or build.by_role['buffer']:
        branch = CONTAINMENT_BUFFER if 'containment' in zones else ERADICATION_BUFFER
        metres, width, quote = rules.buffer or (_metres(sources.parameters[branch]['value'],
                                                        sources.parameters[branch]['unit']), branch,
                                                "the Regulation's floor for the buffer zone the act names")
        origins = [(infected, metres)]
        focus = zones.get('focus')
        if focus is not None and focus.geometry is not None:
            p = sources.parameters[ERADICATION_BUFFER]
            origins.append((focus.geometry, _metres(p['value'], p['unit'])))
        inner = _union(*(o for o, _ in origins))
        geometry = None
        if infected is not None:
            geometry = _union(*(outward_band(o, m, land) for o, m in origins if o is not None)).difference(inner)
        used = tuple(sorted({s for z in zones.values() if z.role in ('infected', 'focus') for s in z.sources}))
        zones['buffer'] = Zone('buffer', build.words('buffer'), geometry, quote, used, width)
    return tuple(zones[r] for r in ROLES if r in zones)


def _error(sources: Sources, zones, plant_error_m) -> float | None:
    errors = []
    for zone in zones:
        for source in zone.sources:
            bound = plant_error_m if source == 'plants' else sources.error_bounds.get(source)
            if bound is None:
                return None
            errors.append(bound)
    return max(errors) + APPROXIMATION_M if errors else None


def boundary_distances(a: BaseGeometry, b: BaseGeometry, step_m: float = 10.0):
    """Directed distances from points every `step_m` along a's boundary to b's boundary.

    The measure behind a source's positional error bound (`geometry.json`,
    `positional-error`): one official outline against an independent one of the same unit.
    """
    import numpy
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


def adopted_geography(root: Path, *, decision: date, plants=None, plant_error_m: float | None = None,
                      sources: Sources | None = None):
    """Every consumed, in-reach A area version's `adopted-geography`, in A's order.

    `plants` maps a provision version id to `named_plants`' result for it: per
    plant-defined role, the (x, y) EPSG:32633 positions of the infected plants the act
    names. `plant_error_m` is their positional error bound (INPUTS row 1).
    """
    root = Path(root)
    sources = sources or Sources(root)
    plants = plants or {}
    start = reach_start(root, decision)
    all_versions = versions(root)
    adopted = {}
    for v in all_versions:
        adopted[v.instrument_id] = min(adopted.get(v.instrument_id, v.effective_from), v.effective_from)
    for version in all_versions:
        if not version.consumed or not in_reach(version, start, decision):
            continue
        if version.statements is None:
            raise FileNotFoundError(f'{version.provision_version_id}: the act document is not in this store')
        zones = construct(sources, version, plants=plants.get(version.provision_version_id),
                          adopted=adopted[version.instrument_id])
        bounds = tuple(sorted(sources.error_bounds)) + (('plants',) if plant_error_m is not None else ())
        yield AdoptedGeography(version.provision_version_id, version.instrument_id, version.effective_from,
                               version.effective_to_exclusive, zones, _error(sources, zones, plant_error_m),
                               bounds=bounds)


# --- the infected plants an act names -------------------------------------------------

SUBSPECIES = re.compile(r'\b(?:SOTTOSPECIE|SUBSPECIE|SUB\.)\s*(PAUCA|MULTIPLEX|FASTIDIOSA)\b', re.I)
INTEGRATES = re.compile(r'Integrare la determina\w*\s+n\W{0,3}\s*(\d+)\s+del\s+\d{1,2}/\d{1,2}/(\d{4})', re.I)


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
    """The located infected plants the act names, per plant-defined role.

    No act in the population prints its plants' coordinates or sample identifiers. Each
    names them by subspecies, comune and date, and lists in its infected-zone or focus
    table the sheets and parcels the plants' zone covers. A plant it names is a positive
    observed up to the act that lies in a listed unit, by its position or, where row 1
    prints the plant's cadastral reference, by that sheet or parcel; and that row 1 types
    as the act's subspecies or does not type (row 1 publishes a subspecies only after the
    typing the act reports).
    `observations` are `Observation`s or (day, subspecies, x, y) tuples. Returns per role
    the (x, y) positions of the located plants.
    """
    build = _Builder(sources, version)
    build.legend = False                       # every listed unit, whole
    observations = [o if isinstance(o, Observation) else Observation(*o) for o in observations]
    observations = [o for o in observations if o.day <= version.effective_from]
    operative = dispositivo(_act_text(sources.root, version.source_path))
    # An act that integrates an earlier one and prints no table of its own names the
    # plants that act names ("Integrare la determina n° 8 del 21/02/2024 ... attorno ai
    # 6 mandorli infetti").
    integrated = INTEGRATES.search(operative)
    earlier = None
    if integrated:
        number, year = int(integrated.group(1)), integrated.group(2)
        earlier = next((v for v in versions(sources.root)
                        if v.instrument_id == f'REG-PUGLIA-U181-DIR-{year}-{number:05d}' and v.statements), None)
    found = {}
    for role in plant_roles(sources, version):
        wanted = []
        statements = build.by_role[role]
        if not statements and earlier is not None:
            statements = [s for s in earlier.statements if role_of(s) == role]
        for s in statements:
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

        def listed(o, geometry, references):
            if o.x is not None and geometry is not None and geometry.covers(Point(o.x, o.y)):
                return True
            if o.comune and o.foglio:
                sheet = str(o.foglio).lstrip('0')
                return ((o.comune, sheet, None) in references
                        or (o.comune, sheet, str(o.particella or '').lstrip('0')) in references)
            return False

        found[role] = tuple(sorted({(o.x, o.y) for o in observations if o.x is not None
                                    and any((name in o.subspecies or not o.subspecies)
                                            and listed(o, geometry, references)
                                            for name, geometry, references in wanted)}))
    return found

"""Source coordinate readings and separately evidenced, scoped metric use.

Neither a published coordinate nor a corroborated identity supplies accuracy.
Semantic qualifications are curated readings, not certified by these checks.
"""
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, Decimal
from functools import lru_cache
import json
from math import cos, isfinite, radians, tan
import os
from pathlib import Path

from pyproj import CRS, Geod, Transformer
from shapely.geometry import Point

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, project, projection_distance_error
from .evidence import Source, Support, require_admissible
from .store import blob_path

REPOSITORY = Path(__file__).resolve().parents[3]
DEVICE_RECORDS = 'corpus/sources/positional-qualification/records.json'
# The metric frame SIT publishes monitoring geometry in. Every error D states is a distance
# from the true position on the ground, in this frame, so C can add the errors of the two
# geometries it compares.
GROUND_FRAME = 'EPSG:32633'


@dataclass(frozen=True)
class CoordinateObservation:
    occurrence: tuple[str, str]
    raw_coordinates: tuple[object, object]
    coordinates: tuple[float, float] | None
    crs: str | None
    sources: tuple[Source, ...]
    support: tuple[Support, ...]


@dataclass(frozen=True)
class SpatialQualification:
    """A reading establishing this occurrence's use for one context and date.

    Support must establish identity, event-time applicability, x/y axis meaning
    and a total positional/transformation/distortion error for the target frame
    and consuming domain. One sufficient source can establish the whole claim.
    Decimal places, map scale and nominal PROJ accuracy do not establish it.
    """
    occurrence: tuple[str, str]
    context: str
    event_date: date
    source_crs: str
    target_crs: str
    error_m: float
    sources: tuple[Source, ...]
    support: tuple[Support, ...]

    def __post_init__(self):
        if not self.context or type(self.event_date) is not date:
            raise ValueError('Spatial qualification needs an exact context and event date')
        if not isfinite(self.error_m) or self.error_m < 0:
            raise ValueError('Spatial qualification needs an explicit nonnegative total error bound')


def metric_point(observation: CoordinateObservation, *, context: str, event_date: date,
                 root: Path, qualification: SpatialQualification | None = None,
                 permitted_controlled_sources: frozenset[str] = frozenset()) -> MetricGeometry:
    if qualification is None:
        raise MissingInput('source-grounded spatial identity, event-time and accuracy qualification')
    if (qualification.occurrence != observation.occurrence or qualification.context != context
            or qualification.event_date != event_date):
        raise ValueError('Spatial qualification belongs to another occurrence, context or date')
    for record in (observation, qualification):
        sources = {s.identity: s for s in record.sources}
        if len(sources) != len(record.sources) or not sources or (record is qualification and not record.support):
            raise ValueError('Spatial evidence needs distinct sources and an explicit reading')
        for support in record.support:
            if support.source not in sources:
                raise ValueError('Spatial support names an unlisted source')
        # Monitoring supplies the published coordinates and source bytes; the
        # separate qualification supplies their scoped spatial interpretation.
        for source in sources.values():
            if source.access == 'controlled' and source.identity not in permitted_controlled_sources:
                raise MissingInput('authorized spatial qualification evidence')
            if source.role not in {'official-record', 'official-dataset', 'qualified-observation'}:
                raise ValueError('A form or historical interpretation cannot qualify an instance location')
            source.verify(root)
    if observation.coordinates is None:
        raise MissingInput('finite published coordinates for this source occurrence')
    source_crs = CRS.from_user_input(qualification.source_crs)
    if observation.crs is not None and source_crs != CRS.from_user_input(observation.crs):
        raise ValueError('Qualification conflicts with the published coordinate reference system')
    x, y = observation.coordinates
    if not all(isfinite(v) for v in (x, y)):
        raise MissingInput('finite published coordinates for this source occurrence')
    if source_crs.is_geographic and not (-180 <= x <= 180 and -90 <= y <= 90):
        raise ValueError('Published longitude/latitude is outside its valid range')
    return project(Point(x, y), source_crs, CRS.from_user_input(qualification.target_crs),
                   error_m=qualification.error_m)


# --- positional qualification of located monitoring observations ------------------

# The contract whose members' locations this qualification serves. C's consumers bound to
# it measure B widths from a plant's location; the grid distortion covers the longest.
POPULATION = 'plant-population'


def _stored(store: Path, record: dict) -> Source:
    source = Source(record['id'], os.path.relpath(blob_path(store, record['sha256']), store),
                    record['sha256'], record['role'], record['access'])
    if not blob_path(store, record['sha256']).exists():
        raise MissingInput(f'retained source bytes: {record["id"]}')
    source.verify(store)
    return source


def _parameter_identities(node, function) -> set[str]:
    """Every B parameter identity an expression can name.

    A literal, a concatenation, a conditional, or a local name assigned one of those in the
    same function. Anything else refuses, so a width read another way is never missed.
    """
    import ast
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return {a + b for a in _parameter_identities(node.left, function)
                for b in _parameter_identities(node.right, function)}
    if isinstance(node, ast.IfExp):
        return _parameter_identities(node.body, function) | _parameter_identities(node.orelse, function)
    if isinstance(node, ast.Name):
        values = [n.value for n in ast.walk(function) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == node.id for t in n.targets)]
        if values:
            return set().union(*(_parameter_identities(v, function) for v in values))
    raise ValueError(f'A B width is read through an expression D cannot enumerate: {ast.unparse(node)}')


def point_consumer_widths(repository: Path = REPOSITORY, *, consumers: list | None = None) -> dict:
    """The longest distance each C consumer bound to plant-population measures, from B's widths.

    The consumers are the rows of `additional-input-contracts.json` that bind a C callable to
    plant-population. Each is read from C's source with every C function it calls, however
    deep: each `metres(snapshot, identity, at)` call is one B width it measures. A consumer's
    longest distance is at most the sum of its call sites' widths, each the largest the site
    can name, since a band ends at inner + width (`containment_outer`, 50 + 400 m). A consumer
    that measures from a surface, not a point, is counted too; it can only lengthen the bound.
    A width read through an expression D cannot enumerate refuses.
    """
    import ast
    if consumers is None:
        contracts = json.loads((repository / 'regulation/stage-d/additional-input-contracts.json').read_text())
        consumers = [row for key in ('callables', 'reference_bindings') for row in contracts[key]]
    ledger = json.loads((repository / 'regulation/stage-b/clocks-and-parameters.json').read_text())
    parameters = {p['parameter_id']: p for p in ledger['parameters']}
    functions, qualified = {}, {}
    for path in sorted((repository / 'regulation/stage-c/cordon_c').glob('*.py')):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.FunctionDef):
                functions.setdefault(node.name, []).append(node)
                qualified[f'{path.stem}.{node.name}'] = node

    def metres(identity: str) -> Decimal:
        row = parameters[identity]
        if row['unit'] not in {'m', 'km'}:
            raise ValueError(f'{identity} is not a distance')
        return Decimal(row['value']) * (1000 if row['unit'] == 'km' else 1)

    widths = {}
    for row in consumers:
        if POPULATION not in row['contracts']:
            continue
        seen, sites, pending = set(), [], [qualified[row['consumer']]]
        while pending:
            function = pending.pop()
            if id(function) in seen:
                continue
            seen.add(id(function))
            for call in (n for n in ast.walk(function) if isinstance(n, ast.Call)):
                name = getattr(call.func, 'id', None) or getattr(call.func, 'attr', None)
                if name == 'metres':
                    sites.append(sorted(_parameter_identities(call.args[1], function)))
                elif name in functions:
                    pending.extend(functions[name])
        if sites:
            widths[row['consumer']] = (float(sum(max(metres(i) for i in site) for site in sites)),
                                       tuple(i for site in sites for i in site))
    return widths


def longest_point_distance(repository: Path = REPOSITORY) -> tuple[float, str, tuple[str, ...]]:
    """The longest distance any C consumer bound to plant-population measures, its consumer and B widths."""
    widths = point_consumer_widths(repository)
    consumer = max(widths, key=lambda name: widths[name][0])
    return widths[consumer][0], consumer, widths[consumer][1]


def region_extent(store: Path, record: dict) -> tuple[float, float, float, float]:
    """West, east, south and north of one official boundary feature, in WGS84 degrees.

    The extremes are taken at the boundary's vertices, converted from the member's own frame.
    """
    import io
    import zipfile
    import shapefile
    with zipfile.ZipFile(blob_path(store, record['sha256'])) as archive:
        parts = {suffix: io.BytesIO(archive.read(record['member'] + suffix)) for suffix in ('.shp', '.shx', '.dbf')}
        frame = CRS.from_wkt(archive.read(record['member'] + '.prj').decode())
    with shapefile.Reader(shp=parts['.shp'], shx=parts['.shx'], dbf=parts['.dbf']) as reader:
        field, value = record['feature']['field'], record['feature']['value']
        shapes = [s for r, s in zip(reader.iterRecords(), reader.iterShapes()) if r[field] == value]
    if len(shapes) != 1:
        raise ValueError(f'{record["id"]} has no single feature {field} {value}')
    lon, lat = Transformer.from_crs(frame, 'EPSG:4326', always_xy=True).transform(*zip(*shapes[0].points))
    return min(lon), max(lon), min(lat), max(lat)


def transverse_mercator_scale_bounds(frame: CRS, extent: tuple[float, float, float, float],
                                     widening_m: float) -> tuple[float, float]:
    """The least and greatest point scale of a Transverse Mercator frame over an extent.

    The extent is widened by `widening_m` on every side, so a path that long from any point
    in it stays inside. The projection is conformal, so the point scale is the scale in
    every direction. Its least value anywhere is k0, on the central meridian. Its greatest
    over a box in one hemisphere is at the longitude farthest from the central meridian and
    the latitude nearest the equator, from the ellipsoidal series (Snyder 1987, USGS
    Professional Paper 1395, equation 8-11). Nothing is sampled.
    """
    operation = frame.coordinate_operation
    if operation is None or operation.method_name != 'Transverse Mercator':
        raise ValueError('A Transverse Mercator frame is required')
    parameters = {p.name: p.value for p in operation.params}
    k0 = parameters['Scale factor at natural origin']
    central = parameters['Longitude of natural origin']
    flattening = 1 / frame.ellipsoid.inverse_flattening
    second = flattening * (2 - flattening) / (1 - flattening) ** 2  # e'^2
    west, east, south, north = extent
    geod = Geod(ellps='WGS84')
    # A metre spans the most longitude at the northern edge.
    west, east, south = (geod.fwd(west, north, 270, widening_m)[0], geod.fwd(east, north, 90, widening_m)[0],
                         geod.fwd(west, south, 180, widening_m)[1])
    if south <= 0:
        raise ValueError('The extent must lie north of the equator')
    phi = radians(south)
    a = radians(max(abs(east - central), abs(west - central))) * cos(phi)
    t, c = tan(phi) ** 2, second * cos(phi) ** 2
    high = k0 * (1 + (1 + c) * a ** 2 / 2 + (5 - 4 * t + 42 * c + 13 * c ** 2 - 28 * second) * a ** 4 / 24
                 + (61 - 148 * t + 16 * t ** 2) * a ** 6 / 720)
    return k0, high


@dataclass(frozen=True)
class PositionalTerms:
    """The inputs every positional qualification reads, loaded and verified once."""
    device: dict
    device_source: Source
    award: dict
    award_source: Source
    region: dict
    region_source: Source
    extent: tuple[float, float, float, float]
    longest_m: float
    longest_consumer: str
    longest_widths: tuple[str, ...]
    scale: tuple[float, float]
    distortion_m: float
    error_m: float


def positional_terms(store: Path, repository: Path = REPOSITORY) -> PositionalTerms:
    """Read the device term, the device procurement and the region, and derive the error once."""
    records = {r['use']: r for r in json.loads((repository / DEVICE_RECORDS).read_text())}
    device, award, region = records['device term'], records['device class'], records['region extent']
    contracts = json.loads((repository / 'regulation/stage-d/contracts.json').read_text())['contracts']
    contract = next(c for c in contracts if c['id'] == 'plant-population')
    sources = [_stored(store, record) for record in (device, award, region)]
    require_admissible(contract, sources)
    extent = region_extent(store, region)
    longest, consumer, widths = longest_point_distance(repository)
    scale = transverse_mercator_scale_bounds(CRS.from_user_input(GROUND_FRAME), extent, longest)
    distortion = projection_distance_error(longest, scale)
    error = float((Decimal(str(device['value_m'])) + Decimal(distortion)).quantize(Decimal('0.01'), ROUND_CEILING))
    return PositionalTerms(device, sources[0], award, sources[1], region, sources[2],
                           extent, longest, consumer, widths, scale, distortion, error)


@lru_cache
def _to_degrees(crs: str) -> Transformer:
    return Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)


def positional_qualification(observation: CoordinateObservation, *, context: str, event_date: date,
                             terms: PositionalTerms) -> SpatialQualification:
    """The horizontal error of one located observation's recorded position against its true ground position.

    error_m is the stated device term plus the grid distortion over the longest distance a C
    consumer bound to plant-population measures from the location, rounded up to the centimetre. A recorded fix is a position on
    the ground, so no map enters it, and the observation's locality is not read. The frame
    is EPSG:32633, the metric frame SIT publishes monitoring geometry in. A geometry built
    from a map carries that map's own ground error, and C adds the two. The surveyor samples
    and records the fix at the plant, so the recorded position is the plant's location. Every
    located observation takes the same producer, whatever its published result. The cited
    sources' roles and bytes were checked once, by `positional_terms`.
    """
    if (observation.coordinates is None or observation.crs is None
            or not all(isfinite(v) for v in observation.coordinates)):
        raise MissingInput('finite published coordinates for this source occurrence')
    west, east, south, north = terms.extent
    lon, lat = _to_degrees(observation.crs).transform(*observation.coordinates)
    if not (west <= lon <= east and south <= lat <= north):
        raise MissingInput('a projection scale bound covering this location')
    device_m, (low, high) = terms.device['value_m'], terms.scale
    support = (
        Support(terms.device_source.identity, terms.device['selector'],
                f"Device term {device_m} m, {terms.device['statistic']}: {terms.device['selector']}. A stated "
                f"device-class accuracy, not measured on these fixes. {terms.device['reading']}"),
        Support(terms.award_source.identity, terms.award['selector'],
                f"{terms.award['reading']} The device and the capture mode are not stated per record. A point "
                f"placed on the map rather than taken as a GNSS fix carries map and placement error the device "
                f"test does not describe."),
        Support(terms.region_source.identity, terms.region['selector'],
                f"Grid distortion {terms.distortion_m:.3f} m: C's projection_distance_error for "
                f"{terms.longest_m:g} m, the longest distance a C consumer bound to plant-population measures from "
                f"the location ({terms.longest_consumer.rpartition('.')[2]}, {' + '.join(terms.longest_widths)}), with {GROUND_FRAME} point scale from {low} to "
                f"{high:.7f}. The scale bounds follow from the Transverse Mercator definition of {GROUND_FRAME} "
                f"over {terms.region['reading']} {west:.4f} to {east:.4f} E, {south:.4f} to {north:.4f} N, widened "
                f"by {terms.longest_m:g} m; they are not sampled. A longer distance from the point needs a larger "
                f"term. D's reading, composed from the cited sources, not stated by any of them: error_m "
                f"{terms.error_m:.2f} = device term {device_m} m + grid distortion, rounded up to the centimetre. "
                f"It bounds the distance of the plant's recorded position from its true ground position, in "
                f"{GROUND_FRAME}. The published pair is read on the WGS84 datum, so the transformation is PROJ's projection."),
    )
    sources = (terms.device_source, terms.award_source, terms.region_source)
    return SpatialQualification(observation.occurrence, context, event_date, observation.crs, GROUND_FRAME,
                                terms.error_m, sources, support)

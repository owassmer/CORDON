"""Source coordinate readings and separately evidenced, scoped metric use.

Neither a published coordinate nor a corroborated identity supplies accuracy.
Semantic qualifications are curated readings, not certified by these checks.
"""
from dataclasses import dataclass
from datetime import date
import json
from math import isfinite
import os
from pathlib import Path
import re
import unicodedata

from pyproj import CRS
from shapely.geometry import Point

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, project
from .evidence import Source, Support, require_admissible
from .store import blob_path, put_bytes

REPOSITORY = Path(__file__).resolve().parents[3]
DEVICE_RECORDS = 'corpus/sources/positional-qualification/records.json'
AREA_RECORDS = 'corpus/sources/areas/geometry.json'
# The cadastral map as SIT publishes it. Every error D states is against this one frame, so
# C can add the errors of the two geometries it compares.
CADASTRAL_FRAME = 'EPSG:32633'


@dataclass(frozen=True)
class CoordinateObservation:
    occurrence: tuple[str, str]
    raw_coordinates: tuple[object, object]
    coordinates: tuple[float, float] | None
    crs: str | None
    sources: tuple[Source, ...]
    support: tuple[Support, ...]
    observed_on: date | None = None
    localities: tuple[str, ...] = ()   # every COMUNE the observation's publications print


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


def locality_key(name) -> str:
    """A printed locality compared as a name: case, accents, spacing and punctuation ignored."""
    text = unicodedata.normalize('NFKD', str(name or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Z0-9]', '', text.upper())


def _stored(store: Path, record: dict) -> Source:
    source = Source(record['id'], os.path.relpath(blob_path(store, record['sha256']), store),
                    record['sha256'], record['role'], record['access'])
    if not blob_path(store, record['sha256']).exists():
        raise MissingInput(f'retained source bytes: {record["id"]}')
    source.verify(store)
    return source


@dataclass(frozen=True)
class PositionalTerms:
    """The inputs every positional qualification reads, loaded and verified once."""
    device: dict
    device_source: Source
    award: dict
    award_source: Source
    ground: dict | None          # locality key -> PR #8's cadastral error entry; None if not held
    ground_record: dict | None
    ground_source: Source | None
    contract: dict


def positional_terms(store: Path, repository: Path = REPOSITORY) -> PositionalTerms:
    """Read the device term, the device procurement and the cadastral map's local error.

    The cadastral error record is PR #8's (`corpus/sources/areas/geometry.json`, kind
    `positional-error`, source `cadastre`). Its bytes enter the store so a qualification
    cites exactly what it read. Where the record is not held, `ground` is None and every
    qualification refuses with that cause; no regional or other figure stands in.
    """
    records = {r['use']: r for r in json.loads((repository / DEVICE_RECORDS).read_text())}
    device, award = records['device term'], records['device class']
    contracts = json.loads((repository / 'regulation/stage-d/contracts.json').read_text())['contracts']
    contract = next(c for c in contracts if c['id'] == 'official-finding')
    ground = ground_record = ground_source = None
    path = repository / AREA_RECORDS
    if path.exists():
        data = path.read_bytes()
        ground_record = next((r for r in json.loads(data)
                              if r.get('kind') == 'positional-error' and r.get('source') == 'cadastre'), None)
        if ground_record is not None:
            digest = put_bytes(store, data)
            ground_source = _stored(store, {'id': f'{AREA_RECORDS}#positional-error/cadastre', 'sha256': digest,
                                            'role': 'qualified-observation', 'access': 'public'})
            ground = {locality_key(entry['name']): entry for entry in ground_record['localities']}
    terms = PositionalTerms(device, _stored(store, device), award, _stored(store, award),
                            ground, ground_record, ground_source, contract)
    require_admissible(contract, [s for s in (terms.device_source, terms.award_source, ground_source) if s],
                       field='positional qualification')
    return terms


def positional_qualification(observation: CoordinateObservation, *, context: str, event_date: date,
                             reach_from: date, terms: PositionalTerms) -> SpatialQualification:
    """The total horizontal error of one in-reach located observation, in the cadastral frame.

    error_m = the stated device term + the cadastral map's measured local ground error at
    the observation's locality. A recorded fix is a position on the ground; its error
    against the cadastral frame is therefore both. Zones and parcels built from cadastral
    geometry carry zero in that frame. Between two fixes C adds both errors, so the shared
    map term is counted twice; that errs toward unknown, never toward a wrong answer.
    Grid-to-ground scale distortion is C's (`projection_distance_error`), for the
    consumer's own grid distance. Every located observation takes the same producer,
    whatever its published result.
    """
    if observation.observed_on is None or observation.observed_on < reach_from:
        raise ValueError('The observation lies outside the reach this qualification serves')
    if observation.coordinates is None or observation.crs is None:
        raise MissingInput('finite published coordinates for this source occurrence')
    names = {locality_key(n): n for n in observation.localities}
    if not names:
        raise MissingInput("the observation's own locality: its publications print no COMUNE")
    if len(names) > 1:
        raise MissingInput(f"one agreed locality: its publications print {', '.join(sorted(names.values()))}")
    key, printed = next(iter(names.items()))
    if terms.ground is None:
        raise MissingInput(f'the cadastral map ground error record ({AREA_RECORDS}, kind positional-error, '
                           f'source cadastre), for locality {printed}')
    entry = terms.ground.get(key)
    if entry is None:
        raise MissingInput(f'the cadastral map ground error for locality {printed}: '
                           f'{AREA_RECORDS} does not measure it')
    device_m, ground_m = terms.device['value_m'], entry['error_m']['max']
    error_m = round(device_m + ground_m, 2)
    measured = terms.ground_record
    support = (
        Support(terms.device_source.identity, terms.device['selector'],
                f"Device term {device_m} m: {terms.device['statistic']}; Galaxy Tab Active3, light-medium "
                f"canopy, single position, no post-processing. Stated device-class accuracy, not measured on "
                f"these fixes. {terms.device['reading']}"),
        Support(terms.award_source.identity, terms.award['selector'],
                f"{terms.award['reading']} The device and the capture mode are not stated per record. A point "
                f"placed on the map rather than taken as a GNSS fix carries map and placement error the device "
                f"test does not describe."),
        Support(terms.ground_source.identity,
                f"kind positional-error, source cadastre, localities[comune={entry['comune']}] ({entry['name']})",
                f"Cadastral map ground error at {entry['name']}: {ground_m} m, the largest over the locality's "
                f"{entry['sheets']} sheet centroids of the {measured['statistic']}. The nearest surveyed fix "
                f"lies {entry['nearest_fix_m']['median']} m away (median; at most {entry['nearest_fix_m']['max']} m); "
                f"the 20th lies {entry['fix_20_m']['median']} m away (median; at most {entry['fix_20_m']['max']} m); "
                f"{entry['of_20_in_comune']['min']} to {entry['of_20_in_comune']['median']} of those 20 lie in "
                f"the comune (minimum to median)."),
        Support(terms.ground_source.identity, 'total',
                f"error_m {error_m} = device term {device_m} m + cadastral ground error {ground_m} m at "
                f"{entry['name']}, against the cadastral map frame ({CADASTRAL_FRAME}). The observation's "
                f"published pair is read on the WGS84 datum, so the transformation is PROJ's projection."),
    )
    sources = (terms.device_source, terms.award_source, terms.ground_source)
    require_admissible(terms.contract, sources, field='positional qualification')
    return SpatialQualification(observation.occurrence, context, event_date, observation.crs, CADASTRAL_FRAME,
                                error_m, sources, support)

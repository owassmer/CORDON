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

from pyproj import CRS
from shapely.geometry import Point

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, project
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
    observed_on: date | None = None
    localities: tuple[str, ...] = ()   # every COMUNE the observation's publications print; the
                                       # positional qualification does not read it


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
    contract: dict


def positional_terms(store: Path, repository: Path = REPOSITORY) -> PositionalTerms:
    """Read the device term and the device procurement, and check their roles once."""
    records = {r['use']: r for r in json.loads((repository / DEVICE_RECORDS).read_text())}
    device, award = records['device term'], records['device class']
    contracts = json.loads((repository / 'regulation/stage-d/contracts.json').read_text())['contracts']
    contract = next(c for c in contracts if c['id'] == 'official-finding')
    terms = PositionalTerms(device, _stored(store, device), award, _stored(store, award), contract)
    require_admissible(contract, [terms.device_source, terms.award_source], field='positional qualification')
    return terms


def positional_qualification(observation: CoordinateObservation, *, context: str, event_date: date,
                             reach_from: date, terms: PositionalTerms) -> SpatialQualification:
    """The horizontal error of one in-reach located observation against its true ground position.

    error_m is the stated device term. A recorded fix is a position on the ground, so its
    error is the device's; no map enters it, and the observation's locality is not read.
    The frame is EPSG:32633, the metric frame SIT publishes monitoring geometry in. A
    geometry built from a map carries that map's own ground error, and C adds the two.
    Grid-to-ground scale distortion is C's (`projection_distance_error`), for the
    consumer's own grid distance. Every located observation takes the same producer,
    whatever its published result.
    """
    if observation.observed_on is None or observation.observed_on < reach_from:
        raise ValueError('The observation lies outside the reach this qualification serves')
    if (observation.coordinates is None or observation.crs is None
            or not all(isfinite(v) for v in observation.coordinates)):
        raise MissingInput('finite published coordinates for this source occurrence')
    device_m = terms.device['value_m']
    support = (
        Support(terms.device_source.identity, terms.device['selector'],
                f"Device term {device_m} m: {terms.device['statistic']}; Galaxy Tab Active3, light-medium "
                f"canopy, single position, no post-processing. Stated device-class accuracy, not measured on "
                f"these fixes. {terms.device['reading']}"),
        Support(terms.award_source.identity, terms.award['selector'],
                f"{terms.award['reading']} The device and the capture mode are not stated per record. A point "
                f"placed on the map rather than taken as a GNSS fix carries map and placement error the device "
                f"test does not describe."),
        Support(terms.device_source.identity, 'total',
                f"error_m {device_m} = the device term: the fix's distance from its true ground position, "
                f"stated in {GROUND_FRAME}. The observation's published pair is read on the WGS84 datum, so the "
                f"transformation is PROJ's projection."),
    )
    sources = (terms.device_source, terms.award_source)
    require_admissible(terms.contract, sources, field='positional qualification')
    return SpatialQualification(observation.occurrence, context, event_date, observation.crs, GROUND_FRAME,
                                device_m, sources, support)

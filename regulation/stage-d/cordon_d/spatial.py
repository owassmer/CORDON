"""Source coordinate readings and separately evidenced, scoped metric use.

Neither a published coordinate nor a corroborated identity supplies accuracy.
Semantic qualifications are curated readings, not certified by these checks.
"""
from dataclasses import dataclass
from datetime import date
from math import isfinite
from pathlib import Path

from pyproj import CRS
from shapely.geometry import Point

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, project
from .evidence import Source, Support


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

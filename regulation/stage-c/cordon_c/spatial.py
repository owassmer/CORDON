"""Metric and topological calculations on explicit geometry and population inputs.

Planar distances describe the supplied metric frame. Ground-distance decisions
carry an error bound; point-to-point ellipsoidal distances use PROJ's geodesic.
Legal geometry is supplied as adopted, never inferred from a numeric minimum.
"""

from dataclasses import dataclass
from math import isfinite, acos, ceil, cos, pi, hypot
from collections.abc import Mapping

from pyproj import CRS, Geod, Transformer
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform
from shapely import get_coordinates

from .core import Evaluation, conjunction, disjunction


@dataclass(frozen=True)
class MetricGeometry:
    geometry: BaseGeometry
    crs: CRS
    error_m: float

    def __post_init__(self):
        if not self.crs.is_projected or any(a.unit_conversion_factor != 1 for a in self.crs.axis_info[:2]):
            raise ValueError("A projected CRS with metre axes is required")
        if self.geometry.is_empty or not self.geometry.is_valid or self.geometry.has_z:
            raise ValueError("Valid nonempty two-dimensional geometry required")
        if not isfinite(self.error_m) or self.error_m < 0:
            raise ValueError("Explicit nonnegative spatial error bound required")


def project(geometry: BaseGeometry, source: CRS, target: CRS, *, error_m: float) -> MetricGeometry:
    transformer = Transformer.from_crs(source, target, always_xy=True, allow_ballpark=False, only_best=True)
    result = transform(transformer.transform, geometry)
    return MetricGeometry(result, target, error_m)


def projection_distance_error(max_grid_distance_m: float, scale_bounds: tuple[float, float]) -> float:
    """Bound grid-versus-ground distance error over a qualified metric domain.

    The scale interval must bound directional scale along every relevant path,
    not just at sampled vertices. D supplies that qualification and source/
    transformation accuracy; this function computes the distortion contribution.
    It does not turn PROJ's nominal accuracy or sampled factors into a bound.
    """
    low, high = scale_bounds
    if (not all(isfinite(v) for v in (max_grid_distance_m, low, high))
            or max_grid_distance_m < 0 or not 0 < low <= high):
        raise ValueError("Finite distance and positive ordered scale bounds required")
    return max_grid_distance_m * max(abs(1 / low - 1), abs(1 / high - 1))


def compatible(a: MetricGeometry, b: MetricGeometry):
    if a.crs != b.crs:
        raise ValueError("Geometries require the same explicit metric frame")


def distance_test(a: MetricGeometry, b: MetricGeometry, limit_m: float, comparator: str) -> Evaluation:
    compatible(a, b)
    if not isfinite(limit_m) or limit_m < 0:
        raise ValueError("Finite nonnegative distance required")
    d = a.geometry.distance(b.geometry)
    error = a.error_m + b.error_m
    low, high = max(0, d - error), d + error
    operators = {"<=": lambda x: x <= limit_m, "<": lambda x: x < limit_m,
                 ">=": lambda x: x >= limit_m, ">": lambda x: x > limit_m}
    if comparator not in operators:
        raise ValueError("Explicit distance comparator required")
    left, right = operators[comparator](low), operators[comparator](high)
    return Evaluation(left) if left == right else Evaluation(None, needs=frozenset({"distance precision at the legal boundary"}))


def ground_distance(lonlat_a: tuple[float, float], lonlat_b: tuple[float, float]) -> float:
    for lon, lat in (lonlat_a, lonlat_b):
        if not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise ValueError("WGS84 longitude/latitude outside valid range")
    return Geod(ellps="WGS84").inv(*lonlat_a, *lonlat_b)[2]


def minimum_enclosure(origin: MetricGeometry, enclosure: MetricGeometry, radius_m: float) -> Evaluation:
    """Does the supplied area contain the required metric neighbourhood?

    Every origin component must lie inside the enclosure and every enclosure
    boundary (including holes) must remain at least the required distance away.
    This tests a proposed/adopted shape; it does not itself establish an area.
    """
    compatible(origin, enclosure)
    if enclosure.geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Enclosure requires a polygon")
    if not isfinite(radius_m) or radius_m <= 0:
        raise ValueError("Positive finite minimum width required")
    boundary = MetricGeometry(enclosure.geometry.boundary, enclosure.crs, enclosure.error_m)
    clearance = distance_test(origin, boundary, radius_m, ">=")
    if enclosure.geometry.covers(origin.geometry):
        return clearance
    error = origin.error_m + enclosure.error_m
    if error and enclosure.geometry.buffer(error).covers(origin.geometry):
        return conjunction([clearance, Evaluation(None, needs=frozenset({"enclosure boundary precision"}))])
    return Evaluation(False)


def distance_envelope(origin: MetricGeometry, radius_m: float, approximation_m: float) -> MetricGeometry:
    """A conservative candidate envelope; final membership uses distance_test.

    The circumscribed approximation contains the metric disk/offset and exposes
    its maximum added radial error. It is not an adopted legal area.
    """
    if not isfinite(radius_m) or radius_m < 0 or not isfinite(approximation_m) or approximation_m <= 0:
        raise ValueError("Nonnegative radius and positive finite approximation bound required")
    if radius_m == 0:
        return origin
    angle = acos(radius_m / (radius_m + approximation_m))
    if angle == 0:
        raise ValueError("Requested approximation is below floating-point resolution")
    segments = max(1, ceil(pi / (4 * angle)))
    outer_radius = radius_m / cos(pi / (4 * segments))
    geometry = origin.geometry.buffer(outer_radius, quad_segs=segments)
    return MetricGeometry(geometry, origin.crs, origin.error_m + outer_radius - radius_m)


def adopted_membership(point: MetricGeometry, area: MetricGeometry) -> Evaluation:
    compatible(point, area)
    if point.geometry.geom_type != "Point" or area.geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Membership requires a point and adopted polygon")
    error = point.error_m + area.error_m
    if error and point.geometry.distance(area.geometry.boundary) <= error:
        return Evaluation(None, needs=frozenset({"point/area precision at the adopted boundary"}))
    return Evaluation(area.geometry.covers(point.geometry))


def band_membership(point: MetricGeometry, origin: MetricGeometry, inner_m: float,
                    width_m: float, *, include_inner: bool) -> Evaluation:
    if inner_m < 0 or width_m <= 0:
        raise ValueError("Band requires nonnegative inner offset and positive width")
    return conjunction([distance_test(point, origin, inner_m, ">=" if include_inner else ">"),
                        distance_test(point, origin, inner_m + width_m, "<=")])


def surface_in_band(surface: MetricGeometry, origin: MetricGeometry,
                     inner_m: float, width_m: float) -> Evaluation:
    """Positive-area intersection with a circular band around a point.

    On each connected polygon, distance takes every value between its minimum
    and maximum. The maximum is at a vertex; no polygonal circle approximation
    is needed. Separate components must not bridge an empty radial gap. Merely
    touching a circular boundary does not create an area in the band.
    """
    compatible(surface, origin)
    if surface.geometry.geom_type not in {"Polygon", "MultiPolygon"} or origin.geometry.geom_type != "Point":
        raise ValueError("Polygon surface and point origin required")
    if not all(isfinite(v) for v in (inner_m, width_m)) or inner_m < 0 or width_m <= 0:
        raise ValueError("Finite nonnegative inner offset and positive width required")
    components = (surface.geometry,) if surface.geometry.geom_type == "Polygon" else surface.geometry.geoms
    error = surface.error_m + origin.error_m
    ox, oy = origin.geometry.x, origin.geometry.y
    results = []
    for component in components:
        near = distance_test(MetricGeometry(component, surface.crs, surface.error_m), origin, inner_m + width_m, "<")
        farthest = max(hypot(x - ox, y - oy) for x, y in get_coordinates(component))
        lower, upper = max(0, farthest - error), farthest + error
        far = (Evaluation(lower > inner_m) if (lower > inner_m) == (upper > inner_m) else
               Evaluation(None, needs=frozenset({"surface extent precision at the inner band boundary"})))
        results.append(conjunction([near, far]))
    return disjunction(results)


def partial_parcel(parcel: MetricGeometry, adopted_area: MetricGeometry) -> Evaluation:
    compatible(parcel, adopted_area)
    if any(x.geometry.geom_type not in {"Polygon", "MultiPolygon"} for x in (parcel, adopted_area)):
        raise ValueError("Parcel relation requires polygons")
    error = parcel.error_m + adopted_area.error_m
    overlap = parcel.geometry.intersection(adopted_area.geometry)
    if error:
        if parcel.geometry.distance(adopted_area.geometry) > error:
            return Evaluation(False)
        if parcel.geometry.buffer(-error).intersection(adopted_area.geometry.buffer(-error)).area == 0:
            return Evaluation(None, needs=frozenset({"parcel overlap precision"}))
    # Sharing only a cadastral edge does not place any parcel area inside.
    return Evaluation(overlap.area > 0)


def population_coverage(required: Mapping[str, Evaluation], completed: frozenset[str], *,
                        required_population_complete: bool, completion_records_complete: bool) -> Evaluation:
    """Shared performance counts once by semantic identity, within every relevant duty."""
    support = {identity: Evaluation(True) if identity in completed else
               Evaluation(False) if completion_records_complete else
               Evaluation(None, needs=frozenset({f"completion evidence for {identity}"}))
               for identity in required}
    return population_support(required, support, required_population_complete=required_population_complete)


def population_support(required: Mapping[str, Evaluation], support: Mapping[str, Evaluation], *,
                        required_population_complete: bool) -> Evaluation:
    """Every required member has the necessary computed or established support.

    Members may be plants, required survey areas or required occasions, as
    determined by the consuming source requirement. A supplied support result
    applies to exactly that member. This is a universal condition over the
    qualified population, not a majority or score.
    """
    results = []
    for identity, membership in required.items():
        not_required = Evaluation(None if membership.truth is None else not membership.truth,
            needs=membership.needs or (frozenset({f"required population membership: {identity}"})
                                      if membership.truth is None else frozenset()))
        value = support.get(identity, Evaluation(None, needs=frozenset({f"qualifying support: {identity}"})))
        results.append(disjunction([not_required, value]))
    if not required_population_complete:
        results.append(Evaluation(None, needs=frozenset({"complete required population"})))
    return conjunction(results)

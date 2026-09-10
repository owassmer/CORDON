"""Compute the distinct post-finding populations specified by DDS45.

Plant and surface qualifications are semantic inputs, not land-use guesses.
Every-hectare coverage uses the supplied operative hectare partition; C does not
invent its grid origin or turn hectare coverage into a census of every plant.
"""

from datetime import date

from .core import Evaluation, Snapshot, conjunction, disjunction
from .quantities import metres
from .spatial import MetricGeometry, compatible, distance_test, band_membership, surface_in_band, adopted_membership, distance_envelope


def post_finding_inner(snapshot: Snapshot, at: date, point: MetricGeometry,
                       infected_plants: tuple[MetricGeometry, ...], *,
                       containment: bool, population_qualification: Evaluation) -> Evaluation:
    if population_qualification.truth is False:
        return population_qualification
    if not infected_plants:
        raise ValueError("At least one infected-plant location is required")
    identity = "B-PAR-DDS45-post-finding-" + ("containment" if containment else "pest-free-buffer") + "-inner-50m"
    radius = float(metres(snapshot, identity, at))
    return conjunction([population_qualification,
                        disjunction([distance_test(point, plant, radius, "<=") for plant in infected_plants])])


def containment_outer(snapshot: Snapshot, at: date, location: MetricGeometry,
                       infected_plants: tuple[MetricGeometry, ...], *,
                       surface_qualification: Evaluation) -> Evaluation:
    if surface_qualification.truth is False:
        return surface_qualification
    if not infected_plants:
        raise ValueError("At least one infected-plant location is required")
    inner = float(metres(snapshot, "B-PAR-DDS45-post-finding-containment-inner-50m", at))
    width = float(metres(snapshot, "B-PAR-DDS45-post-finding-containment-outer-band-400m", at))
    memberships = [band_membership(location, plant, inner, width, include_inner=True)
                   if location.geometry.geom_type == "Point" else surface_in_band(location, plant, inner, width)
                   for plant in infected_plants]
    return conjunction([surface_qualification, disjunction(memberships)])


def pest_free_hectare(snapshot: Snapshot, at: date, hectare: MetricGeometry,
                      infected_zone: MetricGeometry, *, contains_specified_species: Evaluation) -> Evaluation:
    if contains_specified_species.truth is False:
        return contains_specified_species
    compatible(hectare, infected_zone)
    if hectare.geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("A hectare surface is required")
    width = float(metres(snapshot, "B-PAR-DDS45-post-finding-pest-free-buffer-outer-band-400m", at))
    # The same outside surface must both survive error and reach the band.
    # Separate existential tests could use a vanishing nearby sliver and a
    # surviving remote component to manufacture certain membership.
    error = hectare.error_m + infected_zone.error_m
    possible_zone = (distance_envelope(infected_zone, error, error / 1024).geometry
                     if error else infected_zone.geometry)
    surviving = hectare.geometry.difference(possible_zone)
    if surviving.area > 0 and surviving.distance(infected_zone.geometry) + error < width:
        return contains_specified_species
    if not error:
        return Evaluation(False)
    components = ((hectare.geometry,) if hectare.geometry.geom_type == "Polygon"
                  else hectare.geometry.geoms)
    # Exclusion must also account for an inside component that could move out.
    # Only components wholly deep inside or wholly beyond the band are excluded.
    if all((infected_zone.geometry.covers(part)
            and part.distance(infected_zone.geometry.boundary) > error)
           or part.distance(infected_zone.geometry) - error >= width
           for part in components):
        return Evaluation(False)
    return conjunction([contains_specified_species, Evaluation(None, needs=frozenset({
        "hectare/zone precision establishing an outside surface within the band"}))])


def inward_band(point: MetricGeometry, infected_zone: MetricGeometry,
                 shared_boundary_with_buffer: MetricGeometry, width_m: float) -> Evaluation:
    from .spatial import adopted_membership
    compatible(infected_zone, shared_boundary_with_buffer)
    if shared_boundary_with_buffer.geometry.geom_type not in {"LineString", "MultiLineString"}:
        raise ValueError("The actual infected/buffer shared boundary is required")
    if not infected_zone.geometry.boundary.covers(shared_boundary_with_buffer.geometry):
        raise ValueError("Supplied shared boundary is not on the infected-zone boundary")
    return conjunction([adopted_membership(point, infected_zone),
                        distance_test(point, shared_boundary_with_buffer, width_m, "<=")])


def exterior_band(point: MetricGeometry, adopted_areas: MetricGeometry, width_m: float) -> Evaluation:
    """Outside the supplied complete union, within width of its boundary.

    The union must cover the required legal scope; a band around one area cannot
    declare a location pest-free when another operative area contains it.
    """
    membership = adopted_membership(point, adopted_areas)
    outside = Evaluation(None if membership.truth is None else not membership.truth,
                         needs=membership.needs)
    return conjunction([outside, distance_test(point, adopted_areas, width_m, "<=")])

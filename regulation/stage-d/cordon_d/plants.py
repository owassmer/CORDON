"""Plant-occasions (INPUTS row 4) and the populations C's distance consumers read around each infected plant.

One located observation of row 1, of any host and any result, is one plant-occasion: the plant the
observer sampled or inspected, at the published place, on that day. Its key is the observation's
identity as row 1 groups it. It is not a plant. Two plant-occasions are one plant only where a source
relates them (a report or order printing the observation's identifier for the plant it names, unique
in both directions, or a re-sample link the publisher states); proximity, species, a parcel string or
a shared day never merge them. No held source states such a link, so "the same plant over time" is
unavailable (`IDENTITY_CAUSE`). The rule concerns negative units only: a positive is a positive unit on
its own reference.

An infected plant is a plant-occasion with a row 2 finding: a joined report row with a positive result.
Its subspecies is the one row 2's subspecies identification reports positive; while a completely read
row reports no identification it is pending, and a neighbour is qualified against every subspecies's
Annex II part, as Stage A's pending-demarcation rule does (EU-2020-1201:4(1)-sub2); otherwise the
subspecies is unknown. A view's subspecies title is not an identification.

The zone branch is C's zone test (`adopted_area_facts`) of the plant against the area versions in force
on the event date (PR #8), never chosen here: the act's containment zone for "the infected zone under
containment measures"; its buffer zone, or no area version at all, for "a pest-free area or buffer
zone". C measures every distance; this module only finds the candidates C is asked about.

Every place tested against an area reaches C with its own error, stated once for both
`AdoptedGeography.metric()` (the outline's error near the place) and the geometry given to C: a
plant-occasion's point with row 1's positional qualification (7.40 m today), a surface with the
cadastre's local ground error there.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
import re

import numpy
import shapely
from pyproj import Transformer

from cordon_c.bindings import adopted_area_facts, eradication_species_facts, reduced_buffer_removal_facts
from cordon_c.core import Evaluation, MissingInput, conjunction, disjunction, negation
from cordon_c.populations import containment_outer, post_finding_inner
from cordon_c.quantities import metres
from cordon_c.spatial import MetricGeometry, population_coverage
from .area_geometry import APPROXIMATION_M, UTM, AdoptedGeography, polygonal, reach_start
from .evidence import RequiredPopulation, Support
from .monitoring import located_observations
from .spatial import GROUND_FRAME, CoordinateObservation, metric_point, positional_qualification

CONTEXT = 'plant-population'
MEMBERSHIP = 'the point or parcel lies within the geography adopted by this act and its annexes'
POSITIVE = frozenset({'positive', 'detected'})
SUBSPECIES = ('fastidiosa', 'multiplex', 'pauca', 'sandyi')
INNER = {True: 'B-PAR-DDS45-post-finding-containment-inner-50m',
         False: 'B-PAR-DDS45-post-finding-pest-free-buffer-inner-50m'}
# The neighbours whose Art. 7(1) species facts are supplied: B's 50 m around the infected plant.
SPECIES_RADIUS = 'B-PAR-EU-4(2)-sub1-infected-zone-50m'

IDENTITY_CAUSE = 'plant identity across observations is not stated by any held source'
SUBSPECIES_CAUSE = 'subspecies of the finding'
BRANCH_CAUSE = 'zone branch of the infected plant'
HECTARE_CAUSE = 'operative hectare partition not published'
ZONE_POPULATION_CAUSE = 'complete specified-plant population of the infected zone'
LABEL_CAUSE = 'host label matched by no publisher pair or Annex II name'
# PR #33: hosts in the 50 m area that no public survey observed are the Osservatorio's field check.
FIELD_CHECK = Support(
    'osservatorio-records', 'the field check of the 50 m area around each infected plant the order prescribes',
    "DDS 63/2026: \"L'area di 50 metri attorno ad ogni pianta infetta viene verificata in campo attraverso "
    "l'applicazione APPXYLELLA\". The public monitoring record observes only the plants a survey reached; "
    "the complete 50 m population is that check, held by the Osservatorio and ARIF.")


def unknown(cause: str) -> Evaluation:
    return Evaluation(None, needs=frozenset({cause}))


# --- plant-occasions ------------------------------------------------------------

@dataclass(frozen=True)
class PlantOccasion:
    key: tuple                              # row 1's observation identity
    day: date
    labels: tuple[str, ...]                 # the host labels its publications print
    positive: bool | None                   # row 1's agreed published result
    symptoms: bool | None                   # one agreed Presente / Assente, else None
    observation: CoordinateObservation
    xy: tuple[float, float]                 # EPSG:32633: finds candidates only; C measures on `point`


def plant_occasions(groups, *, start: date, end: date):
    """Every located observation dated in [start, end], of every host and result state."""
    to_ground = {}
    for group in groups:
        if group.day is None or not start <= group.day <= end:
            continue
        observation = next(located_observations([group]), None)
        if observation is None:
            continue
        if observation.crs not in to_ground:
            to_ground[observation.crs] = Transformer.from_crs(observation.crs, GROUND_FRAME, always_xy=True)
        x, y = to_ground[observation.crs].transform(*observation.coordinates)
        symptoms = group.values('symptom_presence')
        yield PlantOccasion(group.identity, group.day, tuple(sorted(group.values('species'))), group.positive,
                            next(iter(symptoms)) if len(symptoms) == 1 else None, observation,
                            (float(x), float(y)))


def point(occasion: PlantOccasion, terms, *, at: date, store: Path) -> MetricGeometry:
    """The plant-occasion's place with row 1's positional qualification (`spatial.positional_qualification`)."""
    qualification = positional_qualification(occasion.observation, context=CONTEXT, event_date=at, terms=terms)
    return metric_point(occasion.observation, context=CONTEXT, event_date=at, root=store,
                        qualification=qualification)


def parcel(sources, key) -> MetricGeometry:
    """A cadastral parcel of PR #8's supply (`Sources.parcels`, keyed by comune, section, sheet and number)
    as C's place: its features as one surface, with the cadastre's measured ground error over its outline
    (`Sources.cadastral_error`, `cordon_d.area_error`). A parcel string printed on an observation is not
    a parcel; geometry states neither ownership nor authority to enter."""
    field = sources.cadastral_error
    if field is None:
        raise MissingInput("the cadastre's measured ground error")
    geometry = polygonal(shapely.union_all([shapely.make_valid(p) for p in sources.parcels[key]]))
    return MetricGeometry(geometry, UTM, float(numpy.max(field.at(shapely.get_coordinates(geometry)))))


def same_plant(a: PlantOccasion, b: PlantOccasion) -> Evaluation:
    """Whether two plant-occasions are one plant: an occasion is itself; no held source relates two."""
    return Evaluation(True) if a.key == b.key else unknown(IDENTITY_CAUSE)


# --- host qualification -----------------------------------------------------------

PAIR = re.compile(r'^\s*(?P<vernacular>[^()]*?)\s*\((?P<scientific>[^()]+)\)\s*$')
NAME = re.compile(r'^(?P<genus>[A-Z][a-z]+(?:-[a-z]+)?)(?:\s+(?P<epithet>(?!sp\b|spp\b)[a-z][a-z-]+))?\b')


def name_of(text: str | None) -> str | None:
    """A scientific name without its author: 'Vitis L.' -> 'Vitis', 'Olea europaea L.' -> 'Olea europaea'."""
    match = NAME.match(' '.join((text or '').replace('×', ' ').split()))
    if match is None:
        return None
    return match['genus'] + (' ' + match['epithet'] if match['epithet'] else '')


def publisher_pairs(labels) -> dict:
    """Vernacular (casefolded) -> scientific names, from the labels the publisher prints as 'Vernacular (Name)'."""
    pairs = {}
    for label in labels:
        match = PAIR.match(label or '')
        if match and match['vernacular'] and name_of(match['scientific']):
            pairs.setdefault(match['vernacular'].casefold(), set()).add(name_of(match['scientific']))
    return {k: frozenset(v) for k, v in pairs.items()}


@lru_cache(maxsize=None)
def _annex_text(root: str, snapshot: str) -> dict:
    text = (Path(root) / f'regulation/source/consolidations/02020R1201-{snapshot}.txt').read_text()
    start = text.index('\nANNEX II\n')
    parts, current = {}, None
    for line in (l.strip() for l in text[start:text.index('\nANNEX III\n', start)].splitlines()):
        heading = re.fullmatch(r'Specified plants susceptible to Xylella fastidiosa subspecies (\w+)', line)
        if heading:
            current = parts.setdefault(heading[1].casefold(), set())
        elif current is not None and line and not line.startswith(('▼', '►', '—')):
            name = name_of(line)
            if name is None:
                raise ValueError(f'Annex II line not read: {line!r}')
            current.add(name)
    return {k: frozenset(v) for k, v in parts.items()}


@lru_cache(maxsize=None)
def _annex_rows(root: str) -> tuple:
    with (Path(root) / 'regulation/stage-a/annex-versions.csv').open() as handle:
        return tuple(r for r in csv.DictReader(handle) if r['annex'] == 'II')


def annex_ii(root: Path, day: date) -> dict:
    """{subspecies: names} of Annex II in the version A holds for `day`, read from the retained consolidation
    A's annex version names (as `area_geometry.Sources.annex_iii` reads Annex III)."""
    row, = [r for r in _annex_rows(str(root)) if date.fromisoformat(r['effective_from']) <= day
            and (not r['effective_to_exclusive'] or day < date.fromisoformat(r['effective_to_exclusive']))]
    return _annex_text(str(root), row['source_snapshot_dates'].split(';')[-1].replace('-', ''))


class Hosts:
    """A plant-occasion's scientific name and specified-plant status, from its printed labels: the
    publisher's own vernacular-scientific pairs (`publisher_pairs`) and exact Annex II names.

    Names are compared at species rank without authors: an Annex II entry naming part of a species
    ('Olea europaea subsp. europaea L.') matches a label of that species ('Olivo (Olea europaea)'); a
    genus entry ('Prunus L.') matches every species of the genus; a genus label ('Vite europea (Vitis
    L.)') matches only a genus entry, and is unknown where the part lists only species of that genus."""

    def __init__(self, root: Path, pairs: dict):
        self.root, self.pairs = Path(root), pairs

    def name(self, labels, day: date) -> str | None:
        """The one scientific name the labels give, or None where they give none or disagree."""
        genera = {entry.split()[0] for entry in frozenset().union(*annex_ii(self.root, day).values())}
        found = set()
        for label in labels:
            match = PAIR.match(label)
            if match:
                name = name_of(match['scientific'])
            elif name_of(label) and name_of(label).split()[0] in genera and not label.isupper():
                name = name_of(label)     # a scientific name printed alone, of a genus Annex II names
            else:
                candidates = self.pairs.get(label.strip().casefold(), frozenset())
                name = next(iter(candidates)) if len(candidates) == 1 else None
            if name is None:
                return None
            found.add(name)
        return next(iter(found)) if len(found) == 1 else None

    def species(self, occasion: PlantOccasion, other: str | None = None) -> str | None:
        """The species identity C compares: a binomial; a genus alone states no species, but differs from
        every species of another genus, so it is given where `other` (a binomial) is of another genus."""
        name = self.name(occasion.labels, occasion.day)
        if name and ' ' not in name and not (other and other.split()[0] != name):
            return None
        return name

    def specified(self, occasion: PlantOccasion, subspecies) -> Evaluation:
        """Specified for the subspecies (None: unknown), in the Annex II part in force on the occasion's day."""
        if subspecies is None:
            return unknown(SUBSPECIES_CAUSE)
        name = self.name(occasion.labels, occasion.day)
        if name is None:
            return unknown(LABEL_CAUSE)
        annex = annex_ii(self.root, occasion.day)
        listed = frozenset().union(*(annex.get(s, frozenset()) for s in subspecies))
        genus = name.split()[0]
        if genus in listed or name in listed:
            return Evaluation(True)
        if not any(entry.split()[0] == genus for entry in listed):
            return Evaluation(False)
        return Evaluation(False) if ' ' in name else unknown('species of the plant')

    def unmatched(self, occasions) -> dict:
        """Label tuples no name is read from, with their counts: shown, never dropped."""
        counts = {}
        for o in occasions:
            if self.name(o.labels, o.day) is None:
                counts[o.labels] = counts.get(o.labels, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


# --- infected plants ------------------------------------------------------------------

@dataclass(frozen=True)
class Finding:
    """An infected plant: a plant-occasion with a row 2 finding."""
    occasion: PlantOccasion
    identified: frozenset[str]              # subspecies row 2's identification reports positive
    pending: bool                           # no identification reported on a completely read row
    rows: tuple[tuple[str, str], ...]       # (report sha256, row locator)

    @property
    def subspecies(self):
        """The subspecies a neighbour is qualified against: identified; every one while pending; else None."""
        if self.identified:
            return self.identified
        return frozenset(SUBSPECIES) if self.pending else None


def _identification(result) -> str | None:
    heading = ' '.join(result.column).upper()
    if 'SOTTOSPECIE' not in heading and 'SUBSPECIE' not in heading:
        return None
    words = re.findall(r'[a-z]+', (result.analyte or '').casefold())
    return words[-1] if words and words[-1] in SUBSPECIES else None


def infected_plants(joined, occasions: dict):
    """Each located plant-occasion whose row 2 join (`findings.findings`) carries a positive result."""
    for item in joined:
        occasion = occasions.get(item['observation'].identity)
        if occasion is None or item.get('status') not in {'matched', 'provisional-match'}:
            continue
        results = [r for m in item['matches'] for r in m['row'].results]
        if not any(r.kind in POSITIVE for r in results):
            continue
        typing = [(r, _identification(r)) for r in results if _identification(r)]
        yield Finding(occasion, frozenset(s for r, s in typing if r.kind in POSITIVE),
                      not typing and all(m['reading_complete'] for m in item['matches']),
                      tuple(m['key'] for m in item['matches']))


# --- the zone test ----------------------------------------------------------------------

def zone(geography: AdoptedGeography, role: str | None) -> AdoptedGeography | None:
    """The version's area, or its zone of `role` alone, with that zone's own outline and errors."""
    if role is None:
        return geography
    found = geography.zone(role)
    if found is None or found.geometry is None or found.geometry.is_empty:
        return None
    return AdoptedGeography(geography.provision_version_id, geography.instrument_id, geography.effective_from,
                            geography.effective_to_exclusive, (found,))


def zone_tests(snapshot, geography: AdoptedGeography, places, role: str | None = None) -> list:
    """C's zone test of each place (a `MetricGeometry` with its own error) against the version's area or
    one of its zones: `adopted_area_facts`, the area carrying its outline's error near the place.

    A place farther from the outline than the largest error the outline carries anywhere and the error
    of the place's own locality, plus the place's own error, is tested with that bound: C's answer there
    is the one the outline's local error gives, so the local error is not read. A version without the
    zone adopts none, so no place lies in it."""
    area = zone(geography, role)
    if area is None:
        return [Evaluation(False)] * len(places)
    try:
        bound = area.metric(None)
    except MissingInput as error:
        return [unknown(str(error))] * len(places)
    outline = area.geometry.boundary
    shapely.prepare(outline)
    distance = shapely.distance(outline, numpy.array([p.geometry for p in places], dtype=object))
    at = geography.effective_from
    key = snapshot.version(geography.provision_version_id, at)['provision_version_id'], MEMBERSHIP
    out = []
    for place, apart in zip(places, numpy.atleast_1d(distance)):
        local = area._drawn_error(numpy.array([place.geometry.representative_point()], dtype=object))
        far = None if local is None else max([bound.error_m, *(e + APPROXIMATION_M for e in local)])
        if far is not None and apart > far + place.error_m:
            metric = MetricGeometry(area.geometry, UTM, far)
        else:
            try:
                metric = area.metric(place.geometry, place.error_m)
            except MissingInput as error:
                out.append(unknown(str(error)))
                continue
        out.append(adopted_area_facts(snapshot, geography.provision_version_id, at, place, metric)[key])
    return out


@dataclass(frozen=True)
class Branch:
    """C's zone test of an infected plant for DDS 45/2025's two post-finding branches."""
    containment: Evaluation                 # in the containment zone of an area version in force
    pest_free_or_buffer: Evaluation         # in a buffer zone of one, or in no area version


def branch(containment, buffer, inside, unheld=()) -> Branch:
    """From one place's zone tests over the area versions in force on the event date: `containment`,
    `buffer` and `inside` (the whole area) per version; `unheld` names each in-force version not held."""
    outside = conjunction([negation(v) for v in inside] + [unknown(c) for c in unheld])
    return Branch(disjunction(list(containment) + [unknown(c) for c in unheld]),
                  disjunction(list(buffer) + [outside]))


def in_force(geographies, day: date) -> list:
    return [g for g in geographies if g.effective_from <= day
            and (g.effective_to_exclusive is None or day < g.effective_to_exclusive)]


# --- the populations around one infected plant ---------------------------------------------

@dataclass(frozen=True)
class Neighbourhood:
    finding: Finding
    at: date
    branch: Branch
    inner: dict | Evaluation                # occasion key -> post_finding_inner, or why it does not run
    outer: dict | Evaluation                # occasion key -> containment_outer, or why it does not run
    required: RequiredPopulation | None     # the 50 m population for the DDS 45/2025 duties
    coverage: Evaluation                    # C's population_coverage over it
    species: dict                           # occasion key -> eradication_species_facts, within 50 m


def qualification(occasion: PlantOccasion, finding: Finding, hosts: Hosts) -> Evaluation:
    """Specified for the finding's subspecies, or symptomatic, or suspected (its own published positive)."""
    symptomatic = (Evaluation(occasion.symptoms) if occasion.symptoms is not None
                   else unknown('symptoms of the plant'))
    suspected = (Evaluation(occasion.positive) if occasion.positive is not None
                 else unknown('whether the plant is suspected infected'))
    return disjunction([hosts.specified(occasion, finding.subspecies), symptomatic, suspected])


def neighbourhood(snapshot, finding: Finding, branch_: Branch, candidates, *, at: date, locate,
                  hosts: Hosts, elsewhere: frozenset = frozenset()) -> Neighbourhood:
    """The post-finding populations of one infected plant at the event date `at`.

    `candidates` are plant-occasions near the plant (the caller's index); each counts only when dated
    from the start of the four-year reach to `at`, inclusive. `locate` gives an occasion's place with
    its own error (`point`). C decides every membership. `elsewhere` is the species row 2 found
    infected, on or before `at`, in the demarcated area in force then."""
    start = reach_start(hosts.root, at)
    plant = locate(finding.occasion)
    members = [(o, locate(o)) for o in candidates if start <= o.day <= at and o.key != finding.occasion.key]
    def within(metres_):
        return [(o, p) for o, p in members if p.geometry.distance(plant.geometry) <= metres_ + p.error_m + plant.error_m]

    finding_species = hosts.species(finding.occasion)
    species = {o.key: eradication_species_facts(
        snapshot, at, plant_species=hosts.species(o, finding_species), finding_species=finding_species,
        species_found_infected_elsewhere=elsewhere, infected_species_inventory_complete=False,
        specified_plant=hosts.specified(o, finding.subspecies))
        for o, _ in within(float(metres(snapshot, SPECIES_RADIUS, at)))}
    known = [flag for flag, test in ((True, branch_.containment), (False, branch_.pest_free_or_buffer))
             if test.truth is True]
    try:
        radius = max(float(metres(snapshot, identity, at)) for identity in INNER.values())
    except MissingInput as error:           # DDS 45/2025 does not apply on the event date
        cause = unknown(str(error))
        return Neighbourhood(finding, at, branch_, cause, cause, None, cause, species)
    if not known:
        cause = (unknown(BRANCH_CAUSE) if None in (branch_.containment.truth, branch_.pest_free_or_buffer.truth)
                 else Evaluation(False))
        return Neighbourhood(finding, at, branch_, cause, cause, None, cause, species)
    containment = known[0]
    near = within(radius)
    inner = {o.key: post_finding_inner(snapshot, at, p, (plant,), containment=containment,
                                       population_qualification=qualification(o, finding, hosts))
             for o, p in near}
    outer = ({o.key: containment_outer(snapshot, at, p, (plant,),
                                       surface_qualification=hosts.specified(o, finding.subspecies))
              for o, p in members} if containment else unknown(HECTARE_CAUSE))
    required = RequiredPopulation(f'DDS 45/2025 50 m population of {finding.occasion.key[1]} on {at}',
                                  frozenset(str(k) for k, v in inner.items() if v.truth is True), False, FIELD_CHECK)
    coverage = population_coverage({str(k): v for k, v in inner.items()}, frozenset(),
                                   required_population_complete=required.complete,
                                   completion_records_complete=False)
    return Neighbourhood(finding, at, branch_, inner, outer, required, coverage, species)


AREA_SUBSPECIES = re.compile(r'\b(pauca|multiplex|fastidiosa|sandyi) ST\d+')


def area_subspecies(state: str) -> frozenset | None:
    """The subspecies an area version is adopted for, in A's own words for it ('pauca ST53'); None if unnamed."""
    return frozenset(AREA_SUBSPECIES.findall(state)) or None


def infected_zone_population(snapshot, geography: AdoptedGeography, occasions, subspecies, *, at: date,
                             locate, hosts: Hosts):
    """Art. 5(1)(a): the specified plants observed in the version's adopted infected zone, by C's zone
    test, for the area's subspecies (`area_subspecies`); completeness unsupplied (`ZONE_POPULATION_CAUSE`).
    Returns (members, C's 5(1)(a) facts)."""
    start = reach_start(hosts.root, at)
    dated = [o for o in occasions if start <= o.day <= at]
    tests = zone_tests(snapshot, geography, [locate(o) for o in dated], 'infected')
    members = {str(o.key): conjunction([test, hosts.specified(o, subspecies) if subspecies
                                        else unknown('subspecies of the demarcated area')])
               for o, test in zip(dated, tests) if test.truth is not False}
    facts = reduced_buffer_removal_facts(
        snapshot, at, required_specified_plants=members, sampled_plants=frozenset(), removed_plants=frozenset(),
        required_population_complete=False, sampling_records_complete=False, removal_records_complete=False,
        immediacy=unknown('immediacy of the sampling and removal'))
    return members, facts

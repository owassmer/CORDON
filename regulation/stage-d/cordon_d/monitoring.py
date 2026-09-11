"""Reusable observation inputs from native CAMP, CKAN and SIT releases.

An observation is the input grain here. Sample-reference matches are exposed for
comparison; they do not merge physical plants or choose a winning publication.
"""
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from math import isfinite, ulp
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from .campaign import PublicationReading, meaningful_text, publication_reading
from .evidence import file_digest
from .releases import Occurrence, workbook_occurrences, csv_occurrences, arcgis_occurrences


OBSERVATION_DATES = ('DATA_RILEVAMENTO', 'DATA_PRELIVEO', 'DATA_PRELIEVO',
                     'DATA_CAMPIONE', 'DATA_RILIEVO')


def reference(value):
    """Unify numeric Excel/JSON representation; preserve lexical identifiers."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = Decimal(str(value))
        if number.is_finite() and number == number.to_integral_value():
            return str(int(number))
    return meaningful_text(value)


def day(value, *, arcgis=False):
    if value is None or meaningful_text(value) is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if type(value) is date:
        return value
    if arcgis and isinstance(value, (int, float)):
        # REST encodes UTC; the observation day belongs to the Puglia calendar.
        # Early campaigns encode local midnight as 23:00 UTC on the prior day.
        return datetime.fromtimestamp(value / 1000, timezone.utc).astimezone(ZoneInfo('Europe/Rome')).date()
    if isinstance(value, str):
        for pattern in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d/%m/%Y %H:%M:%S'):
            try:
                return datetime.strptime(value.strip(), pattern).date()
            except ValueError:
                pass
    raise ValueError(f'Uninterpreted observation date: {value!r}')


@dataclass(frozen=True)
class MonitoringObservation:
    release: str
    publication: PublicationReading
    identifiers: tuple[tuple[str, str], ...]
    observation_dates: tuple[tuple[str, date | None], ...]
    kind: str | None
    species: str | None
    cultivar: str | None
    symptoms: tuple[tuple[str, str], ...]
    subspecies: str | None
    view_name: str
    coordinates: tuple[float, float] | None
    crs: str | None
    issues: tuple[str, ...]

    @property
    def occurrence_key(self):
        return self.release, *self.publication.occurrence.identity

    @property
    def observation_date(self):
        if any(issue.startswith(OBSERVATION_DATES) for issue in self.issues):
            return None
        values = {value for _, value in self.observation_dates if value is not None}
        return next(iter(values)) if len(values) == 1 else None

    @property
    def symptom_presence(self):
        values = {value.casefold() for _, value in self.symptoms}
        if not values and self.publication.result == 'published-symptom-label':
            return True
        if values == {'presente'}:
            return True
        if values == {'assente'}:
            return False
        return None

    @property
    def observation_reference(self):
        # ID is the recent campaign observation key; early NUMERO_ORDINE,
        # OBJECTID and daily/device IDs have different publisher meanings.
        values = {value for field, value in self.identifiers if field in {'ID', 'ID_CAMPIONE'}}
        return next(iter(values)) if len(values) == 1 else None


def observation(occurrence: Occurrence, *, release: str, view_name: str = ''):
    native = occurrence.values
    arcgis = 'attributes' in native
    row = native.get('attributes', native)
    publication = publication_reading(occurrence)
    identifiers = tuple((key, value) for key in ('ID', 'ID_CAMPIONE', 'CODICE_CAMPIONAMENTO',
                        'ID_GIORNALIERO', 'NUMERO_ORDINE', 'OBJECTID', 'IDANDROID')
                        if (value := reference(row.get(key))) is not None)
    issues = []
    dates = []
    for key in OBSERVATION_DATES:
        if key in row:
            try:
                dates.append((key, day(row[key], arcgis=arcgis)))
            except (ValueError, OverflowError, OSError) as error:
                dates.append((key, None))
                issues.append(f'{key}: {error}')
    if len({v for _, v in dates if v is not None}) > 1:
        issues.append('Observation date fields disagree')
    kind = meaningful_text(row.get('TIPOLOGIA'))
    if kind is None:
        # Only the explicitly named published activities supply this fallback.
        if 'ispezioni visive' in view_name.casefold():
            kind = 'Ispezione visiva'
        elif 'accertamenti' in view_name.casefold():
            kind = 'Accertamento'
    geometry = native.get('geometry') if arcgis else None
    coordinates = None
    crs = None
    if geometry and 'x' in geometry and 'y' in geometry:
        values = geometry['x'], geometry['y']
        spatial_reference = native.get('spatialReference') or {}
        wkid = spatial_reference.get('latestWkid', spatial_reference.get('wkid'))
        crs = f'EPSG:{wkid}' if wkid else spatial_reference.get('wkt')
    else:
        values = row.get('LONGITUDINE'), row.get('LATITUDINE')
        # Geographic column names establish axes, not a geodetic datum.
    if any(meaningful_text(v) is not None for v in values):
        try:
            coordinates = tuple(float(v.replace(',', '.') if isinstance(v, str) else v) for v in values)
            if not all(isfinite(v) for v in coordinates):
                raise ValueError('nonfinite coordinates')
            if geometry is None and not (-180 <= coordinates[0] <= 180 and -90 <= coordinates[1] <= 90):
                raise ValueError('longitude/latitude outside geographic range')
        except (TypeError, ValueError):
            coordinates = None
            issues.append('Invalid or incomplete coordinate pair')
    return MonitoringObservation(
        release, publication, identifiers, tuple(dates), kind,
        meaningful_text(row.get('SPECIE')), meaningful_text(row.get('CULTIVAR')),
        tuple((key, value) for key in ('SINTOMO', 'SINTOMI')
              if (value := meaningful_text(row.get(key))) is not None),
        meaningful_text(row.get('SUBSPECIE')), view_name, coordinates, crs, tuple(issues))


def observations(root: Path):
    """Stream every retained release; missing declared files fail visibly.

    Newly acquired native releases enter by their acquisition record, without
    registering a plant, case, expected answer or observation subset.
    """
    campaign = root / 'campaign'
    for release in json.loads((campaign / 'releases.json').read_text()):
        if 'error' in release:
            raise ValueError(f"Incomplete campaign acquisition: {release['url']}")
        path = campaign / release['path']
        if file_digest(path) != release['sha256']:
            raise ValueError(f'Changed source release: {path}')
        if path.suffix == '.xlsx':
            rows = workbook_occurrences(path)
        elif path.suffix == '.csv':
            rows = csv_occurrences(path, encoding=release['encoding'], delimiter=release['delimiter'])
        else:
            raise ValueError(f'Uninterpreted release format: {path}')
        for row in rows:
            yield observation(row, release=release['url'], view_name=path.name)
    for metadata_path in sorted((root / 'sit').glob('*/*/*/layer.json')):
        directory = metadata_path.parent
        release = json.loads((directory / 'release.json').read_text())
        count = 0
        for page in release['pages']:
            path = directory / page['path']
            if file_digest(path) != page['sha256']:
                raise ValueError(f'Changed source page: {path}')
            for row in arcgis_occurrences(path, oid_field=release['oid_field'],
                                         allow_repeated_oid=release['rows'] > release['unique_oids']):
                count += 1
                yield observation(row, release=release['url'], view_name=release['name'])
        if count != release['rows']:
            raise ValueError(f'Incomplete retained layer: {release["url"]}')


# --- distinct observations across every release and view ---------------------

POSITIVE_RESULTS = frozenset({'published-positive', 'published-positive-and-removal-label'})
DUPLICATE_RESULT = 'published-positive-duplicate-label'
UNKNOWN_RESULTS = frozenset({'unpublished', 'unadjudicated-label', 'not-a-result-record', 'publisher-annotation',
                             # A visual inspection or a symptom label is an observation, not an
                             # analytical result; it can neither agree nor disagree with a test.
                             'published-visual-observation', 'published-symptom-label'})
COMPARED_FIELDS = ('result', 'species', 'cultivar', 'subspecies', 'kind', 'symptom_presence')


@dataclass(frozen=True)
class Member:
    """One published occurrence of an observation in one release or view."""
    release: str
    view: str
    path: str
    sha256: str
    locator: str
    result: str
    kind: str | None
    species: str | None
    cultivar: str | None
    subspecies: str | None
    symptom_presence: bool | None
    coordinates: tuple[float, float] | None
    crs: str | None
    report_routes: tuple[str, ...]
    issues: tuple[str, ...]

    @property
    def occurrence(self):
        return self.sha256, self.locator


def _same_point(a, b):
    return all(abs(p - q) <= max(ulp(p), ulp(q)) for p, q in zip(a, b))


@dataclass(frozen=True)
class DistinctObservation:
    """Every publication of one observation: one publisher reference on one day.

    Members are never merged and no publication wins. An observation without a
    reference and a day is its own group; proximity, species or result never
    supply identity. A group is an observation, not a plant or an inspection unit.
    """
    reference: str | None
    day: date | None
    members: tuple[Member, ...]
    uncorrelated_because: str | None = None

    @property
    def correlatable(self):
        return self.reference is not None and self.day is not None

    @property
    def identity(self):
        if self.correlatable:
            return 'observation', self.reference, self.day.isoformat()
        return 'uncorrelated', *self.members[0].occurrence

    def values(self, field):
        """Distinct available values of one compared field across members."""
        found = set()
        for member in self.members:
            value = getattr(member, field)
            if value is None or field == 'result' and value in UNKNOWN_RESULTS:
                continue
            found.add(value)
        if field == 'result' and DUPLICATE_RESULT in found and found.intersection(POSITIVE_RESULTS):
            found.discard(DUPLICATE_RESULT)  # a duplicate label restates the positive it accompanies
        return found

    def _points_by_crs(self):
        by_crs = {}
        for member in self.members:
            if member.coordinates is not None:
                by_crs.setdefault(member.crs, []).append(member.coordinates)
        return by_crs

    @property
    def disagreements(self):
        fields = [f for f in COMPARED_FIELDS if len(self.values(f)) > 1]
        if any(not all(_same_point(points[0], p) for p in points) for points in self._points_by_crs().values()):
            fields.append('coordinates')
        return tuple(fields)

    @property
    def result(self):
        results = self.values('result')
        return next(iter(results)) if len(results) == 1 else None

    @property
    def positive(self):
        """True or False only for one agreed published result; a duplicate label
        alone, a doubtful, pending, visual or symptom label, or a disagreement is None."""
        result = self.result
        if result in POSITIVE_RESULTS:
            return True
        if result == 'published-negative':
            return False
        return None

    @property
    def locations(self):
        """Agreed published coordinates per coordinate reference system."""
        return tuple((crs, points[0]) for crs, points in self._points_by_crs().items()
                     if all(_same_point(points[0], p) for p in points))

    @property
    def report_routes(self):
        return tuple(sorted({route for member in self.members for route in member.report_routes}))


def _member(reading: MonitoringObservation, root: Path) -> Member:
    occurrence = reading.publication.occurrence
    return Member(reading.release, reading.view_name, os.path.relpath(occurrence.path, root),
                  occurrence.sha256, occurrence.locator, reading.publication.result, reading.kind,
                  reading.species, reading.cultivar, reading.subspecies, reading.symptom_presence,
                  reading.coordinates, reading.crs,
                  tuple(route for _, route in reading.publication.document_references), reading.issues)


def distinct_observations(root: Path):
    """Group the whole stream by publisher reference and observation day.

    Reads every retained release through `observations`; a temporary index
    orders the stream and is discarded. Yields one group per (reference, day)
    across all releases and views, then every uncorrelatable observation alone.

    A reference identifies an observation only where its own publishing view
    uses it once on that day; a value one view gives to several rows on one day
    is a counter, not an identifier, and those rows stay uncorrelated. Only a
    duplicate-labelled row may share the reference of the positive it restates.
    """
    import sqlite3
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        index = sqlite3.connect(Path(temporary) / 'index.sqlite')
        # Small grouping keys and the large member payload live apart, so grouping
        # and the reuse pass never read the payload.
        index.execute('CREATE TABLE k (seq INTEGER PRIMARY KEY, ref TEXT, day TEXT, view TEXT, restates INTEGER)')
        index.execute('CREATE TABLE p (seq INTEGER PRIMARY KEY, member TEXT)')
        keys, payloads = [], []
        for sequence, reading in enumerate(observations(root)):
            reference, day = reading.observation_reference, reading.observation_date
            member = _member(reading, root)
            correlatable = reference is not None and day is not None
            keys.append((sequence, reference if correlatable else None, day.isoformat() if day else None,
                         member.release + '|' + member.view, int(member.result == DUPLICATE_RESULT)))
            payloads.append((sequence, json.dumps(asdict(member))))
            if len(keys) >= 50000:
                index.executemany('INSERT INTO k VALUES (?, ?, ?, ?, ?)', keys)
                index.executemany('INSERT INTO p VALUES (?, ?)', payloads)
                keys.clear(); payloads.clear()
        index.executemany('INSERT INTO k VALUES (?, ?, ?, ?, ?)', keys)
        index.executemany('INSERT INTO p VALUES (?, ?)', payloads)
        index.commit()
        index.execute('CREATE INDEX v ON k (view, ref, day, restates)')
        index.execute('CREATE TABLE reused AS SELECT view, ref, day FROM k WHERE ref IS NOT NULL '
                      'GROUP BY view, ref, day HAVING SUM(restates = 0) > 1')
        index.execute('CREATE INDEX r ON reused (view, ref, day)')
        index.execute('UPDATE k SET ref = NULL, restates = -1 WHERE ref IS NOT NULL AND EXISTS '
                      '(SELECT 1 FROM reused r WHERE r.view = k.view AND r.ref = k.ref AND r.day = k.day)')
        index.commit()
        index.execute('CREATE INDEX o ON k (ref, day, seq)')
        current, members = None, []
        for reference, day, _, restates, member in index.execute(
                'SELECT k.ref, k.day, k.seq, k.restates, p.member FROM k JOIN p ON p.seq = k.seq '
                'ORDER BY k.ref, k.day, k.seq'):
            values = json.loads(member)
            values['coordinates'] = tuple(values['coordinates']) if values['coordinates'] else None
            for key in ('report_routes', 'issues'):
                values[key] = tuple(values[key])
            item = Member(**values)
            if reference is None:
                if members:
                    yield DistinctObservation(current[0], date.fromisoformat(current[1]), tuple(members))
                    current, members = None, []
                because = ('reference reused within its publishing view on this day' if restates == -1
                           else 'no observation day' if day is None else 'no publisher reference')
                yield DistinctObservation(None, date.fromisoformat(day) if day else None, (item,), because)
                continue
            if (reference, day) != current:
                if members:
                    yield DistinctObservation(current[0], date.fromisoformat(current[1]), tuple(members))
                current, members = (reference, day), []
            members.append(item)
        if members:
            yield DistinctObservation(current[0], date.fromisoformat(current[1]), tuple(members))
        index.close()


# --- the shapes C's entry points take ------------------------------------------

def detection_days(groups, *, select=lambda group: True):
    """Days of published-positive observations within the caller's selection.

    These are candidates for `no_detection_anchor`: the official finding is the
    report's (row 2), and `detection_record_complete` is never supplied here,
    because the release inventory proves only that every retained release was
    read, not that surveillance observed every infected plant.
    """
    return tuple(sorted({group.day for group in groups
                         if group.positive is True and group.day is not None and select(group)}))


def occasion_sets(groups, occasion_of):
    """Distinct observation identities per caller-defined occasion, by published result.

    Identities are observations, not inspection units: unit identity belongs to
    the plant population (row 4), so `observation_inventory_complete` is not
    supplied here and a group with a disagreement counts as neither result.
    """
    sets = {}
    for group in groups:
        occasion = occasion_of(group)
        if occasion is None:
            continue
        bucket = sets.setdefault(occasion, {'positive': set(), 'negative': set(), 'other': set()})
        kind = 'positive' if group.positive is True else 'negative' if group.positive is False else 'other'
        bucket[kind].add(group.identity)
    return {occasion: {k: frozenset(v) for k, v in bucket.items()} for occasion, bucket in sets.items()}


def located_positives(groups):
    """Published coordinates of positive observations, one per agreed coordinate frame.

    Each carries its releases as official-dataset sources and no spatial support:
    `spatial.metric_point` refuses a distance calculation until a source-grounded
    qualification exists, and the finding status remains row 2's.
    """
    from .evidence import Source
    from .spatial import CoordinateObservation
    for group in groups:
        if group.positive is not True:
            continue
        for crs, coordinates in group.locations:
            members = tuple(m for m in group.members if m.crs == crs and m.coordinates is not None)
            sources = tuple(Source(f'{m.release}|{m.view}', m.path, m.sha256, 'official-dataset', 'public')
                            for m in {m.sha256: m for m in members}.values())
            yield CoordinateObservation(group.identity, members[0].coordinates, coordinates, crs, sources, ())

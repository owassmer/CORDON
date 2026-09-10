"""Reusable observation inputs from native CAMP, CKAN and SIT releases.

An observation is the input grain here. Sample-reference matches are exposed for
comparison; they do not merge physical plants or choose a winning publication.
"""
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from math import isfinite, ulp
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
    def published_positive(self):
        if self.publication.result in {'published-positive', 'published-positive-duplicate-label',
                                       'published-positive-and-removal-label'}:
            return True
        if self.publication.result == 'published-negative':
            return False
        return None

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

    @property
    def candidate_key(self):
        """Candidate same observation, to compare before any deduplication."""
        if self.observation_reference is None or self.observation_date is None:
            return None
        return self.observation_reference, self.observation_date


@dataclass(frozen=True)
class ObservationComparison:
    same_reference_and_day: bool
    agreeing_fields: tuple[str, ...]
    differing_fields: tuple[str, ...]
    unavailable_fields: tuple[str, ...]


def compare_observations(first: MonitoringObservation, second: MonitoringObservation):
    """Compare candidate observations without merging them or choosing a winner.

    Identical values corroborate those fields. They do not prove persistent plant
    identity. Different coordinate frames require the separate spatial reader.
    """
    agree, differ, unavailable = [], [], []
    fields = ('species', 'cultivar', 'subspecies', 'kind', 'symptom_presence', 'coordinates')
    pairs = [(name, getattr(first, name), getattr(second, name)) for name in fields]
    pairs.append(('result', first.publication.result, second.publication.result))
    unknown_results = {'unpublished', 'unadjudicated-label', 'not-a-result-record', 'publisher-annotation'}
    for name, left, right in pairs:
        if (left is None or right is None
                or name == 'coordinates' and first.crs != second.crs
                or name == 'result' and (left in unknown_results or right in unknown_results)):
            unavailable.append(name)
        elif left == right or (name == 'coordinates' and all(
                abs(a - b) <= max(ulp(a), ulp(b)) for a, b in zip(left, right))):
            agree.append(name)
        else:
            differ.append(name)
    same = first.candidate_key is not None and first.candidate_key == second.candidate_key
    return ObservationComparison(same, tuple(agree), tuple(differ), tuple(unavailable))


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

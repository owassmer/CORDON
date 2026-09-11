"""Reusable observation inputs from native CAMP, CKAN and SIT releases.

An observation is the input grain here. Sample-reference matches are exposed for
comparison; they do not merge physical plants or choose a winning publication.
"""
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from math import isfinite, ulp
import os
from pathlib import Path
import shutil
import tempfile
from zoneinfo import ZoneInfo

from .campaign import PublicationReading, meaningful_text, publication_reading
from hashlib import sha256

from .releases import Occurrence, workbook_occurrences, csv_occurrences, arcgis_occurrences
from .store import adopt, audit, blob_path as store_blob_path, derived_path, dumps, loads, store_root, write_derived


OBSERVATION_DATES = ('DATA_RILEVAMENTO', 'DATA_PRELIVEO', 'DATA_PRELIEVO',
                     'DATA_CAMPIONE', 'DATA_RILIEVO')

# Row 1's own subject: attributes of the observation event, established here. Who
# performed it is one fact under several publisher names, from the single-technician
# `TECNICO` to the team code and per-inspector columns of the 2016 infrastructure survey.
OBSERVATION_ATTRIBUTES = ('COMUNE', 'PROVINCIA', 'LOCALITA', 'ALTITUDINE',
                          'SQUADRA', 'TECNICO', 'COD_TECNICI',
                          'COGNOME_ISPETTORE_1', 'COGNOME_ISPETTORE_2', 'COGNOME_ISPETTORE_3',
                          'NOME_ISPETTORE_1', 'NOME_ISPETTORE_2', 'NOME_ISPETTORE_3',
                          'CODICE_CAMPIONAMENTO', 'NOME_DISPOSITIVO', 'STATO',
                          'NOTE_RILEVATORE', 'CRITICITA_NOTE')
# Of those, the ones two publications of one observation should state alike, so a
# difference between them is a disagreement the operator must see. A free-text note, a
# publication status and a device name are not: they describe the publication or its
# instrument, not the observation.
COMPARED_ATTRIBUTES = ('COMUNE', 'PROVINCIA', 'LOCALITA', 'ALTITUDINE',
                       'SQUADRA', 'TECNICO', 'COD_TECNICI',
                       'COGNOME_ISPETTORE_1', 'COGNOME_ISPETTORE_2', 'COGNOME_ISPETTORE_3',
                       'NOME_ISPETTORE_1', 'NOME_ISPETTORE_2', 'NOME_ISPETTORE_3')
# Published identifiers other than the sample reference. Carried per publication and never
# compared: a view's own feature id differs between views by construction, so comparing it
# would manufacture disagreement. A value shared by hundreds of records is a label for the
# campaign that produced them, not an identity, and is established as an attribute instead.
PUBLISHER_IDENTIFIERS = ('ID_GIORNALIERO', 'NUMERO_ORDINE', 'OBJECTID', 'IDANDROID')
# The published columns that route to the document owning the next fact.
ROUTE_FIELDS = ('DOCUMENTO_CONFERMA', 'LNK_DOCUMENTO_SELGE', 'DOCUMENTO_DECRETO')
# Published labels that carry no analytical result because the record states an
# observation of another kind, and those where a result is genuinely absent.
NO_ANALYTICAL_RESULT = frozenset({'published-visual-observation', 'published-symptom-label'})
RESULT_ABSENCES = frozenset({'unpublished', 'not-a-result-record', 'unadjudicated-label',
                             'publisher-annotation'})
# Another row's subject, carried as the literal the monitoring publisher printed and
# interpreted by nobody here. The owning row adjudicates what the fact is; a monitoring
# transcription never outranks the act or the report it transcribes.
CARRIED_FOR = {
    'PROT_SELGE': 'laboratory report', 'DATA_PROT_SELGE': 'laboratory report',
    'PROTOCOLLO': 'laboratory report', 'STRUTTURA_LABORATORIO': 'laboratory report',
    'LABORATORIO': 'laboratory report',
    'ZONA_DELIMITATA': 'demarcated area', 'BUFFER': 'demarcated area',
    # `ZONA` prints `Zona Contenimento - Salento`, `Area delimitata Monopoli` and the
    # like: a demarcated-zone status, which row 3 establishes from the adopting act. A
    # publisher's label beside an observation never stands in for the area in force.
    'ZONA': 'demarcated area',
    'FOGLIO': 'cadastral parcel', 'FOGLI': 'cadastral parcel', 'PARTICELLA': 'cadastral parcel',
    'PARTICELLE': 'cadastral parcel', 'SEZIONE': 'cadastral parcel', 'ID_PART': 'cadastral parcel',
    'COD_COMUNE': 'cadastral parcel', 'COMUNE_COD': 'cadastral parcel',
    'CUAA': 'land standing', 'AZIENDA': 'land standing',
    'SCELTA_PROPRIETARIO': 'owner response',
    'MONUMENTALE_ARIF': 'protected plants', 'VINCOLO_IDROGEOLOGICO': 'protected plants',
    'UCP_PPTR': 'protected plants', 'BP_PPTR': 'protected plants', 'PAI': 'protected plants',
    'RIF_DECRETO': 'removal execution', 'DATA_ESTIRPAZIONE': 'removal execution',
}


def _scalar_text(value):
    """A published value this reader can carry as the string the publisher printed.

    A list or mapping is a shape this reader does not interpret; rendering its Python
    repr would establish a fact the record does not state, and comparing that repr could
    manufacture a disagreement. Such a value is carried nowhere and says so instead.
    """
    return None if isinstance(value, (dict, list, tuple, set)) else meaningful_text(value)


def _absence_cause(row, fields):
    """Why this reader produced no value from these published fields, in the record's terms.

    The causes are distinct remedies, not synonyms for emptiness: a source that states
    nothing needs another source, a sentinel needs nothing, and a value this reader does
    not interpret needs a better reading. The list is open; an unrecognised situation
    says so rather than borrowing one of the others.
    """
    published = [(field, row[field]) for field in fields if field in row]
    if not published:
        return 'no such field is published in this record'
    if all(value is None for _, value in published):
        return 'the field is published and carries no value'
    if all(_scalar_text(value) is None and not isinstance(value, (dict, list, tuple, set))
           for _, value in published):
        return 'the field is published and carries only a sentinel or blank'
    return 'a value is published that this reader does not interpret'


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
    # Attributes of the observation event this reader establishes, as the publisher names them.
    attributes: tuple[tuple[str, str], ...] = ()
    # Literals for facts another row establishes; nothing here interprets them.
    carried: tuple[tuple[str, str], ...] = ()
    # Why this reading carries no value for a field it reads.
    causes: tuple[tuple[str, str], ...] = ()

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
    identifiers = tuple((key, value) for key in ('ID', 'ID_CAMPIONE') + PUBLISHER_IDENTIFIERS
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
    attributes = tuple((field, value) for field in OBSERVATION_ATTRIBUTES
                       if (value := _scalar_text(row.get(field))) is not None)
    # The literal the publisher printed, for a fact another row establishes. The lossless
    # native value stays in the occurrence; nothing here interprets it.
    carried = tuple((field, str(row[field])) for field in CARRIED_FOR
                    if field in row and _scalar_text(row[field]) is not None)
    reading = MonitoringObservation(
        release, publication, identifiers, tuple(dates), kind,
        meaningful_text(row.get('SPECIE')), meaningful_text(row.get('CULTIVAR')),
        tuple((key, value) for key in ('SINTOMO', 'SINTOMI')
              if (value := meaningful_text(row.get(key))) is not None),
        meaningful_text(row.get('SUBSPECIE')), view_name, coordinates, crs, tuple(issues),
        attributes, carried)
    return replace(reading, causes=_causes(reading, row, identifiers, issues, native, geometry))


def _causes(reading, row, identifiers, issues, native, geometry):
    """For every value this reading does not carry, why — as a fact about this reading.

    A reading's silence is not the source's. Each cause here is established from the
    record, and where the reader cannot establish one it says so rather than borrowing
    a neighbouring cause. `DistinctObservation.uncorrelated_because` answers the group
    question; these refine it at the grain of one publication and one field.
    """
    causes = []
    if reading.observation_reference is None:
        if 'ID' in row or 'ID_CAMPIONE' in row:
            cause = _absence_cause(row, ('ID', 'ID_CAMPIONE'))
        elif identifiers:
            cause = ('the sample reference is not published; this record is identified by '
                     + ', '.join(field for field, _ in identifiers))
        else:
            cause = 'no identifier is published in this record'
        causes.append(('reference', cause))
    if reading.symptom_presence is None:
        causes.append(('symptom_presence', _absence_cause(row, ('SINTOMO', 'SINTOMI'))))
    for field, published in (('species', ('SPECIE',)), ('cultivar', ('CULTIVAR',)),
                             ('subspecies', ('SUBSPECIE',)), ('kind', ('TIPOLOGIA',))):
        if getattr(reading, field) is None:
            causes.append((field, _absence_cause(row, published)))
    if reading.publication.result in NO_ANALYTICAL_RESULT:
        # An observation the publisher describes rather than tests: the record states
        # what it states, and no analytical result is missing from it.
        causes.append(('result', 'the record publishes an observation of another kind, '
                       'which is not an analytical result'))
    elif reading.publication.result in RESULT_ABSENCES:
        # The same causes as any other field, so a sentinel result is not filed as a
        # silent one; campaign.py's own distinction is the first two of them.
        causes.append(('result', _absence_cause(row, ('RISULTATO',))))
    if not reading.publication.document_references:
        # The route to the laboratory report. Row 2 reads this and must be able to tell a
        # publisher that printed no route from a column this reader could not read.
        causes.append(('report_routes', _absence_cause(row, ROUTE_FIELDS)))
    if reading.observation_date is None:
        days = {value for _, value in reading.observation_dates if value is not None}
        unreadable = next((issue for issue in issues if issue.split(':')[0] in OBSERVATION_DATES), None)
        causes.append(('day', 'the published observation dates disagree' if len(days) > 1
                       else unreadable or _absence_cause(row, OBSERVATION_DATES)))
    if reading.coordinates is None:
        # A geometry key the record carries in a shape this reader does not read - a
        # polygon, a ring, an explicit null - is published geometry, and saying none is
        # published would deny what the record holds.
        published_geometry = 'geometry' in native
        causes.append(('coordinates',
                       'a coordinate pair is published that this reader cannot use'
                       if 'Invalid or incomplete coordinate pair' in issues
                       else 'geometry is published in a shape this reader does not interpret'
                       if published_geometry and not (geometry and 'x' in geometry and 'y' in geometry)
                       else 'no geometry is published in this record'
                       if not published_geometry and 'LONGITUDINE' not in row and 'LATITUDINE' not in row
                       else _absence_cause(row, ('LONGITUDINE', 'LATITUDINE'))))
    causes.extend(_unheld(reading, row))
    return tuple(causes)


# Fields whose absence is already named above under the reading's own name for the fact.
NAMED_ABOVE = (frozenset(OBSERVATION_DATES) | frozenset(ROUTE_FIELDS)
               | {'ID', 'ID_CAMPIONE', 'SPECIE', 'CULTIVAR', 'SUBSPECIE', 'SINTOMO', 'SINTOMI',
                  'RISULTATO', 'TIPOLOGIA', 'LONGITUDINE', 'LATITUDINE'})
# Every field some row of this stage has claimed, whether row 1 establishes it, carries it
# for another row, or reads it into a fact under another name.
CLAIMED_FIELDS = (NAMED_ABOVE | frozenset(OBSERVATION_ATTRIBUTES)
                  | frozenset(PUBLISHER_IDENTIFIERS) | frozenset(CARRIED_FOR))


def _unheld(reading, row):
    """Every field this record publishes that the reading does not carry, and why.

    Derived from the record's own keys, not from a list of names, so a field no reader has
    seen before is reported the first time a publisher prints it instead of disappearing.
    The two outcomes are different remedies: a field this reader claims but did not carry
    here needs the record read again or nothing at all, and a field no row claims needs an
    owner before anyone can consume it.
    """
    held = ({field for field, _ in reading.attributes} | {field for field, _ in reading.carried}
            | {field for field, _ in reading.identifiers})
    unheld = []
    for field in row:
        if field in held or field in NAMED_ABOVE:
            continue
        if field in CLAIMED_FIELDS:
            unheld.append((field, _absence_cause(row, (field,))))
        else:
            unheld.append((field, 'published, and no row of this stage claims it'
                           if meaningful_text(row[field]) is not None else
                           'published carrying no value, and no row of this stage claims it'))
    return sorted(unheld)


@dataclass(frozen=True)
class Release:
    """One retained release or view page in stream order, as its acquisition record names it."""
    url: str
    view: str
    digest: str
    raw_path: Path
    kind: str
    options: dict
    expected_rows: int | None = None


def reader_version() -> str:
    """Hash of the reader modules; a changed reader invalidates every derived file."""
    digest = sha256()
    for name in ('monitoring.py', 'releases.py', 'campaign.py', 'evidence.py', 'store.py'):
        digest.update((Path(__file__).parent / name).read_bytes())
    return digest.hexdigest()[:12]


def releases(root: Path):
    """Every retained release and page, in stream order, from the acquisition records."""
    campaign = root / 'campaign'
    for record in json.loads((campaign / 'releases.json').read_text()):
        if 'error' in record:
            raise ValueError(f"Incomplete campaign acquisition: {record['url']}")
        suffix = Path(record['path']).suffix
        if suffix == '.xlsx':
            options = {}
        elif suffix == '.csv':
            options = {'encoding': record['encoding'], 'delimiter': record['delimiter']}
        else:
            raise ValueError(f"Uninterpreted release format: {record['path']}")
        yield Release(record['url'], record['path'], record['sha256'], campaign / record['path'],
                      suffix[1:], options)
    for metadata_path in sorted((root / 'sit').glob('*/*/*/layer.json')):
        directory = metadata_path.parent
        record = json.loads((directory / 'release.json').read_text())
        options = {'oid_field': record['oid_field'],
                   'allow_repeated_oid': record['rows'] > record['unique_oids']}
        for index, page in enumerate(record['pages']):
            yield Release(record['url'], record['name'], page['sha256'], directory / page['path'], 'arcgis',
                          options, record['rows'] if index == len(record['pages']) - 1 else None)


def _raw_occurrences(kind: str, path: Path, options: dict):
    if kind == 'xlsx':
        return workbook_occurrences(path)
    if kind == 'csv':
        return csv_occurrences(path, **options)
    return arcgis_occurrences(path, **options)


def _ensure_blob(store: Path, release: Release) -> Path:
    blob = store_blob_path(store, release.digest)
    if blob.exists():
        return blob
    if not release.raw_path.exists():
        raise ValueError(f'Missing source bytes for {release.url}: {release.digest}')
    try:
        if adopt(store, release.raw_path) != release.digest:
            raise ValueError(f'Changed source release: {release.raw_path}')
    except FileNotFoundError:
        if not blob.exists():  # a concurrent ingest adopted it first, or it is gone
            raise
    return blob


def _reading_row(reading: MonitoringObservation, store: Path, ordinal: int) -> dict:
    occurrence = reading.publication.occurrence
    x, y = reading.coordinates if reading.coordinates else (None, None)
    return {'ordinal': ordinal, 'reference': reading.observation_reference, 'day': reading.observation_date,
            'release': reading.release, 'view': reading.view_name,
            'path': os.path.relpath(occurrence.path, store), 'sha256': occurrence.sha256,
            'locator': occurrence.locator, 'result': reading.publication.result,
            'restates': reading.publication.result == DUPLICATE_RESULT, 'kind': reading.kind,
            'species': reading.species, 'cultivar': reading.cultivar, 'subspecies': reading.subspecies,
            'symptom_presence': reading.symptom_presence, 'x': x, 'y': y, 'crs': reading.crs,
            'report_routes': [route for _, route in reading.publication.document_references],
            'issues': list(reading.issues),
            'identifiers': [{'field': f, 'value': v} for f, v in reading.identifiers],
            'attributes': [{'field': f, 'value': v} for f, v in reading.attributes],
            'carried': [{'field': f, 'value': v} for f, v in reading.carried],
            'causes': [{'field': f, 'cause': c} for f, c in reading.causes]}


def _pairs(values, second='value'):
    return tuple((item['field'], item[second]) for item in values or ())


READINGS_SCHEMA = None


def _readings_schema():
    global READINGS_SCHEMA
    if READINGS_SCHEMA is None:
        import pyarrow
        READINGS_SCHEMA = pyarrow.schema([
            ('ordinal', pyarrow.int64()), ('reference', pyarrow.string()), ('day', pyarrow.date32()),
            ('release', pyarrow.string()), ('view', pyarrow.string()), ('path', pyarrow.string()),
            ('sha256', pyarrow.string()), ('locator', pyarrow.string()), ('result', pyarrow.string()),
            ('restates', pyarrow.bool_()), ('kind', pyarrow.string()), ('species', pyarrow.string()),
            ('cultivar', pyarrow.string()), ('subspecies', pyarrow.string()),
            ('symptom_presence', pyarrow.bool_()), ('x', pyarrow.float64()), ('y', pyarrow.float64()),
            ('crs', pyarrow.string()), ('report_routes', pyarrow.list_(pyarrow.string())),
            ('issues', pyarrow.list_(pyarrow.string())),
            ('identifiers', _named(pyarrow, 'value')), ('attributes', _named(pyarrow, 'value')),
            ('carried', _named(pyarrow, 'value')), ('causes', _named(pyarrow, 'cause'))])
    return READINGS_SCHEMA


def _named(pyarrow, second):
    """A published field name beside what this reader carries for it."""
    return pyarrow.list_(pyarrow.struct([('field', pyarrow.string()), (second, pyarrow.string())]))


def _ensure_derived(store: Path, release: Release, version: str) -> tuple[Path, Path, bool]:
    """Occurrences and readings for one blob, ingested once per reader version."""
    import pyarrow
    occurrences = derived_path(store, 'monitoring/occurrences', release.digest, version)
    readings = derived_path(store, 'monitoring/readings', release.digest, version)
    blob = _ensure_blob(store, release)  # the cache never stands in for missing bytes
    if occurrences.exists() and readings.exists():
        return occurrences, readings, False
    locators, values, rows = [], [], []
    for ordinal, occurrence in enumerate(_raw_occurrences(release.kind, blob, release.options)):
        locators.append(occurrence.locator)
        values.append(dumps(occurrence.values))
        rows.append(_reading_row(observation(occurrence, release=release.url, view_name=release.view),
                                 store, ordinal))
    write_derived(occurrences, pyarrow.table({'locator': locators, 'values': values}))
    write_derived(readings, pyarrow.Table.from_pylist(rows, schema=_readings_schema()))
    for current in (occurrences, readings):  # a superseded reader's output for this blob is dead
        for stale in current.parent.glob(f'{release.digest}-*.parquet'):
            if stale != current:
                stale.unlink()
    return occurrences, readings, True


def ingest(root: Path) -> Path:
    """Adopt every retained release into the store and derive it once; audit after any write."""
    store = store_root(root)
    version = reader_version()
    wrote = False
    for release in releases(root):
        wrote |= _ensure_derived(store, release, version)[2]
    if wrote:
        mismatches = audit(store)
        if mismatches:
            raise ValueError(f'Store audit failed: {mismatches[:3]}')
    return store


def observations(root: Path):
    """Stream every retained release from the store; missing declared bytes fail visibly.

    Newly acquired native releases enter by their acquisition record, without
    registering a plant, case, expected answer or observation subset.
    """
    import pyarrow.parquet as parquet
    store = ingest(root)
    version = reader_version()
    count = 0
    for release in releases(root):
        occurrences, _, _ = _ensure_derived(store, release, version)
        blob = str(store_blob_path(store, release.digest))
        table = parquet.read_table(occurrences)
        for locator, values in zip(table.column('locator').to_pylist(), table.column('values').to_pylist()):
            count += 1
            yield observation(Occurrence(blob, release.digest, locator, loads(values)),
                              release=release.url, view_name=release.view)
        if release.expected_rows is not None:
            if count != release.expected_rows:
                raise ValueError(f'Incomplete retained layer: {release.url}')
            count = 0
        elif release.kind != 'arcgis':
            count = 0


# --- distinct observations across every release and view ---------------------

POSITIVE_RESULTS = frozenset({'published-positive', 'published-positive-and-removal-label'})
DUPLICATE_RESULT = 'published-positive-duplicate-label'
UNKNOWN_RESULTS = frozenset({'unpublished', 'unadjudicated-label', 'not-a-result-record', 'publisher-annotation',
                             # A visual inspection or a symptom label is an observation, not an
                             # analytical result; it can neither agree nor disagree with a test.
                             'published-visual-observation', 'published-symptom-label'})
# An established fact whose conflicts are invisible is not established, so every attribute
# this reader establishes is compared. Publisher identifiers are not: a view's own feature
# id differs between views by construction.
COMPARED_FIELDS = ('result', 'species', 'cultivar', 'subspecies', 'kind',
                   'symptom_presence') + COMPARED_ATTRIBUTES


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
    identifiers: tuple[tuple[str, str], ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()
    carried: tuple[tuple[str, str], ...] = ()
    causes: tuple[tuple[str, str], ...] = ()

    @property
    def occurrence(self):
        return self.sha256, self.locator

    def attribute(self, field):
        """An established observation attribute under the name the publisher prints."""
        return dict(self.attributes).get(field)

    def cause(self, field):
        """This reader's own answer to why it carries no value for that field."""
        return dict(self.causes).get(field)


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
            value = getattr(member, field) if hasattr(member, field) else member.attribute(field)
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


def _member_from_row(row: dict) -> Member:
    coordinates = (row['x'], row['y']) if row['x'] is not None and row['y'] is not None else None
    return Member(row['release'], row['view'], row['path'], row['sha256'], row['locator'], row['result'],
                  row['kind'], row['species'], row['cultivar'], row['subspecies'], row['symptom_presence'],
                  coordinates, row['crs'], tuple(row['report_routes'] or ()), tuple(row['issues'] or ()),
                  _pairs(row.get('identifiers')), _pairs(row.get('attributes')),
                  _pairs(row.get('carried')), _pairs(row.get('causes'), 'cause'))


def distinct_observations(root: Path):
    """Group the whole stream by publisher reference and observation day.

    Reads the derived readings of every retained release through DuckDB, in
    stream order. Yields one group per (reference, day) across all releases and
    views, and every uncorrelatable observation alone.

    A reference identifies an observation only where its own publishing view
    uses it once on that day; a value one view gives to several rows on one day
    is a counter, not an identifier, and those rows stay uncorrelated. Only a
    duplicate-labelled row may share the reference of the positive it restates.
    """
    import duckdb
    store = ingest(root)
    version = reader_version()
    files = [(index, str(_ensure_derived(store, release, version)[1]))
             for index, release in enumerate(releases(root))]
    connection = duckdb.connect()
    # Bounded by construction: two whole-population passes must fit beside each
    # other on an 8 GiB machine, so each spills to disk instead of taking 80% of RAM.
    spill = Path(tempfile.mkdtemp(prefix='cordon-duckdb-', dir=store))
    connection.execute("SET memory_limit = '1.5GB'")
    connection.execute('SET threads = 2')
    connection.execute(f"SET temp_directory = '{spill}'")
    try:
        connection.execute('CREATE TABLE ordering (filename VARCHAR, release_index BIGINT)')
        connection.executemany('INSERT INTO ordering VALUES (?, ?)', [(name, index) for index, name in files])
        cursor = connection.execute(
            'WITH r AS (SELECT p.*, o.release_index * 4294967296 + p.ordinal AS seq '
            '           FROM read_parquet($files, filename = true) p JOIN ordering o USING (filename)), '
            'reused AS (SELECT release, view, reference, day FROM r '
            '           WHERE reference IS NOT NULL AND day IS NOT NULL '
            '           GROUP BY release, view, reference, day HAVING SUM(CASE WHEN restates THEN 0 ELSE 1 END) > 1) '
            'SELECT r.*, CASE WHEN u.reference IS NULL AND r.day IS NOT NULL THEN r.reference END AS ref, '
            '       u.reference IS NOT NULL AS reused '
            'FROM r LEFT JOIN reused u ON u.release = r.release AND u.view = r.view '
            '                          AND u.reference = r.reference AND u.day = r.day '
            'ORDER BY ref NULLS FIRST, r.day NULLS FIRST, seq', {'files': [name for _, name in files]})
        columns = [description[0] for description in cursor.description]
        current, members = None, []
        while True:
            batch = cursor.fetchmany(50000)
            if not batch:
                break
            for values in batch:
                row = dict(zip(columns, values))
                item = _member_from_row(row)
                reference, day = row['ref'], row['day']
                if reference is None:
                    if members:
                        yield DistinctObservation(current[0], current[1], tuple(members))
                        current, members = None, []
                    because = ('reference reused within its publishing view on this day' if row['reused']
                               else 'no observation day' if day is None else 'no publisher reference')
                    yield DistinctObservation(None, day, (item,), because)
                    continue
                if (reference, day) != current:
                    if members:
                        yield DistinctObservation(current[0], current[1], tuple(members))
                    current, members = (reference, day), []
                members.append(item)
        if members:
            yield DistinctObservation(current[0], current[1], tuple(members))
    finally:
        connection.close()
        shutil.rmtree(spill, ignore_errors=True)


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

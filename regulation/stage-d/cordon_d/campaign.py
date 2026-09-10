"""Published observation results and their document routes."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser

from .evidence import Source
from .releases import Occurrence


SENTINELS = frozenset({'', '****', '***', '**', '*', 'NULL', 'N/D'})
RESULTS = {'POSITIVO': 'published-positive', 'NEGATIVO': 'published-negative',
           'DUBBIO': 'published-doubtful', 'IN ATTESA': 'published-pending',
           'POSITIVO DUPLICATO': 'published-positive-duplicate-label',
           'DA RICAMPIONARE': 'published-further-observation-request',
           'ISPEZIONE VISIVA': 'published-visual-observation',
           'SINTOMATICO': 'published-symptom-label', 'POSITIVO ESTIRPATO': 'published-positive-and-removal-label'}


def meaningful_text(value):
    """Source placeholders supply neither a document route nor a negative fact."""
    if value is None:
        return None
    value = str(value).strip()
    return None if value.upper() in SENTINELS else value


@dataclass(frozen=True)
class PublicationReading:
    occurrence: Occurrence
    result: str
    document_references: tuple[tuple[str, str], ...]
    date_fields: tuple[tuple[str, object], ...]
    publisher_annotation: str | None = None


def publication_reading(occurrence: Occurrence) -> PublicationReading:
    """Retain administrative result scope and exact source labels for every row.

    A negative is the published result for that observation. Assay details come
    from its report. Source dates retain their event meaning.
    """
    row = occurrence.values.get('attributes', occurrence.values)
    populated = {k: v for k, v in row.items() if v is not None and v != ''}
    annotation = None
    # This explicitly recognized publisher annotation is not an observation.
    if set(populated) == {'ID'} and str(row['ID']).startswith('*Pianta non abbattuta'):
        annotation = str(row['ID'])
    raw = meaningful_text(row.get('RISULTATO'))
    result = 'publisher-annotation' if annotation else RESULTS.get(
        raw.upper() if raw else '', ('not-a-result-record' if 'RISULTATO' not in row else 'unpublished') if raw is None else 'unadjudicated-label')
    references = tuple((k, reference) for k in ('DOCUMENTO_CONFERMA', 'LNK_DOCUMENTO_SELGE', 'DOCUMENTO_DECRETO')
                       if (value := meaningful_text(row.get(k))) is not None
                       for reference in document_references(value))
    dates = tuple((k, v) for k, v in row.items() if k.startswith('DATA_'))
    return PublicationReading(occurrence, result, references, dates, annotation)


class _Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            self.references.extend(value for key, value in attrs if key.lower() == 'href' and value)


def document_references(value: str) -> tuple[str, ...]:
    """Read actual publisher anchors; retain literal unknown references separately.

    The raw HTML remains in the source occurrence. Extracting href is not URL
    aliasing: scheme, hostname, path, query and repeated anchors remain literal.
    """
    if '<' in value:
        parser = _Anchors()
        parser.feed(value)
        if parser.references:
            return tuple(parser.references)
    return (value,)


def retained_document(reference: str, document_records: dict, root: Path) -> Source | None:
    """Exact published URL only; missing originals stay missing, never inferred.

    The caller supplies the retained acquisition manifest keyed by literal URL.
    Alias/correction equivalence needs separate source-specific adjudication.
    """
    record = document_records.get(reference)
    retained = record.get('retained') if record else None
    if not retained or not record.get('pdf_signature'):
        return None
    path = Path(retained['path'])
    if path.is_absolute():
        path = path.resolve().relative_to(root.resolve())
    source = Source(reference, str(path), retained['sha256'], 'official-record', 'public')
    source.verify(root)
    return source






@dataclass(frozen=True)
class DocumentReading:
    field: str
    reference: str
    source: Source | None
    acquisition_record: dict | None


@dataclass(frozen=True)
class CampaignEvidence:
    publication: PublicationReading
    documents: tuple[DocumentReading, ...]


class CampaignDocuments:
    """Compose literal publication routes with retained acquisitions.

    Records are a sequence, not a URL-to-latest-record dictionary: repeated
    requests and changed versions survive. No authored interpretation or copy
    equivalence is injected into these documentary references.
    This index is a bounded consumption snapshot, rebuilt for each new capture.
    """
    def __init__(self, records, root: Path, *, known_through: datetime):
        from collections import defaultdict
        from .evidence import instant
        instant(known_through)
        self.root = root
        self.known_through = known_through
        self.records = defaultdict(list)
        for record in records:
            self.records[record['url']].append(record)
        self._resolved = {}

    def _resolve(self, reference):
        if reference not in self._resolved:
            self._resolved[reference] = tuple(
                (retained_document(reference, {reference: record}, self.root), record)
                for record in self.records.get(reference, ())) or ((None, None),)
        return self._resolved[reference]

    def read(self, path: Path, *, format: str, **reader_options):
        """Read original releases, with no authored case or supplied row values.

        CSV encoding/delimiter and ArcGIS OID/repetition qualification are
        explicit existing reader options. Unknown formats fail, never disappear.
        The original publication and all its native fields remain in the result.
        The supplied release is not a reconstruction of historical publisher state.
        """
        from .releases import workbook_occurrences, csv_occurrences, arcgis_occurrences
        readers = {'workbook': workbook_occurrences, 'csv': csv_occurrences,
                   'arcgis': arcgis_occurrences}
        if format not in readers:
            raise ValueError('Unsupported campaign release format')
        checked_references = set()
        for occurrence in readers[format](path, **reader_options):
            publication = publication_reading(occurrence)
            for _, reference in publication.document_references:
                if reference in checked_references:
                    continue
                for source, _ in self._resolve(reference):
                    if source:
                        source.verify(self.root)
                checked_references.add(reference)
            documents = tuple(
                DocumentReading(field, reference, source, record)
                for field, reference in publication.document_references
                for source, record in self._resolve(reference))
            yield CampaignEvidence(publication, documents)

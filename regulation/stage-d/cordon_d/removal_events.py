"""Attach actual administrative records to issued measures and accepted clocks."""
from dataclasses import dataclass, replace
from datetime import date, datetime
from html import unescape
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from cordon_c.core import MissingInput
from .evidence import Support, file_digest
from .events import AdministrativeEvent


def compact(text):
    return ' '.join((text or '').split())


def act_id(number, year):
    return f'REG-PUGLIA-U181-DIR-{int(year)}-{int(number):05d}'


@dataclass(frozen=True)
class Publication:
    identity: str
    publisher: str
    document: str | None
    document_date: date | None
    source_fields: dict
    events: tuple[AdministrativeEvent, ...]
    support: Support


def _object(**properties):
    return dict(type='object', properties=properties, required=list(properties),
                additionalProperties=False)


_TEXT = {'type': 'string'}
_CAUSE = {'type': ['string', 'null'], 'enum': [None, 'source-not-stated', 'unreadable',
                                           'not-recovered', 'not-supplied', 'conflict']}
_CITATIONS = {'type': 'array', 'items': _object(source=_TEXT,
    page={'type': 'integer', 'minimum': 1}, locator=_TEXT, quote=_TEXT), 'minItems': 1}
_VALUE = _object(value={'type': ['string', 'null']}, cause=_CAUSE,
                 support=dict(_CITATIONS, minItems=0))
PUBLICATION_ATTESTATION_SCHEMA = _object(
    publisher=_VALUE, register_reference=_VALUE, document_reference=_TEXT,
    act=_object(authority=_object(**dict(_VALUE['properties'], value={
        'type': ['string', 'null'], 'enum': [None, 'puglia-osservatorio', 'other']})),
        number=_VALUE, adopted=_VALUE),
    period=_object(start=_VALUE, end=_VALUE,
        coverage={'type': 'string', 'enum': ['completed-interval', 'partial-publication',
                                           'intended', 'blank-form', 'unresolved']},
        statement=_TEXT, qualification={'type': ['string', 'null']}, support=_CITATIONS),
    signer=_VALUE, signature_statement=_VALUE, issued_on=_VALUE,
    issues={'type': 'array', 'items': _object(aspect=_TEXT,
        cause=dict(_CAUSE, type='string', enum=_CAUSE['enum'][1:]), detail=_TEXT)},
    support=_CITATIONS,
)


def _attestation(response, store):
    """Validate a PDF reading and expose its own claims, not source qualification."""
    import pymupdf
    from jsonschema import Draft202012Validator
    from .store import blob_path

    request, reading = response['request'], response['reading']
    if (request['schema'] != PUBLICATION_ATTESTATION_SCHEMA
            or len(request['sources']) != 1 or request.get('source_formats')):
        raise ValueError('Publication attestation requires its exact single-PDF contract')
    Draft202012Validator(PUBLICATION_ATTESTATION_SCHEMA).validate(reading)
    source, = request['sources']
    path = blob_path(Path(store), source)
    if file_digest(path) != source:
        raise ValueError('Attestation source bytes do not match their hash')
    with pymupdf.open(path) as document:
        pages = len(document)

    def visit(item):
        if isinstance(item, dict):
            if set(item) == {'source', 'page', 'locator', 'quote'}:
                if (item['source'] != source or not 1 <= item['page'] <= pages
                        or not item['locator'].strip() or not item['quote'].strip()):
                    raise ValueError('Attestation citation requires its source page, locator and quotation')
            if set(item) == {'value', 'cause', 'support'}:
                if item['value'] is None:
                    if item['cause'] is None:
                        raise ValueError('An unrecovered component needs its own absence cause')
                elif not item['value'].strip() or item['cause'] is not None or not item['support']:
                    raise ValueError('A recovered component needs support and no absence cause')
            for value in item.values():
                visit(value)
        elif isinstance(item, list):
            for value in item:
                visit(value)
    visit(reading)
    components = {key: reading[key] for key in ('publisher', 'register_reference',
                                               'signer', 'signature_statement', 'issued_on')}
    components.update({'act.' + key: value for key, value in reading['act'].items()})
    components.update({'period.' + key: reading['period'][key] for key in ('start', 'end')})
    for issue in reading['issues']:
        if issue['cause'] != 'conflict':
            continue
        aspect = issue['aspect']
        if aspect == 'period.coverage':
            if reading['period']['coverage'] != 'unresolved':
                raise ValueError('Conflicting publication coverage must remain unresolved')
        elif aspect not in components:
            raise ValueError('A conflict must name its exact existing component path')
        elif components[aspect]['value'] is not None or components[aspect]['cause'] != 'conflict':
            raise ValueError('A conflicting component must be null with cause conflict')
    for item in [reading['act']['adopted'], reading['period']['start'],
                 reading['period']['end'], reading['issued_on']]:
        if item['value'] is not None and date.fromisoformat(item['value']).isoformat() != item['value']:
            raise ValueError('A recovered day must use an exact ISO date')
    number = reading['act']['number']['value']
    if number is not None and (not number.isdecimal() or int(number) < 1):
        raise ValueError('Act number must be its source-supported numeric component')
    period = reading['period']
    if not period['statement'].strip():
        raise ValueError('Preserve the source publication statement or unreadable-area description')
    document, adopted = None, None
    if (reading['act']['authority']['value'] == 'puglia-osservatorio'
            and number and reading['act']['adopted']['value']):
        adopted = date.fromisoformat(reading['act']['adopted']['value'])
        document = act_id(number, adopted.year)
    citation = reading['support'][0]
    support = Support(source, f"page:{citation['page']}/{citation['locator']}", citation['quote'])
    publication = Publication(source + ':publication-attestation', reading['publisher']['value'] or '',
        document, adopted, dict(attestation=reading, request_sha256=response['request_sha256'],
        reading_captured_at=response.get('captured_at'), provenance='model_proposed_reading',
        attachment_issues=[], period_conflicts={}), (), support)
    return _attestation_events(publication)


def _attestation_events(publication):
    reading = publication.source_fields['attestation']
    period = reading['period']
    conflicts = dict(publication.source_fields['period_conflicts'])
    start, end = (period[key]['value'] for key in ('start', 'end'))
    if start and end and end < start:
        conflicts.update(start='Attested end precedes start', end='Attested end precedes start')
    captured = publication.source_fields.get('reading_captured_at')
    if captured is not None:
        captured = datetime.fromisoformat(captured)
        if captured.tzinfo is not None:
            known_day = captured.astimezone(ZoneInfo('Europe/Rome')).date().isoformat()
            for key in ('start', 'end'):
                if period[key]['value'] and period[key]['value'] > known_day:
                    conflicts[key] = 'Attested day follows capture of the source reading'
    events = []
    if publication.document and publication.publisher:
        for key in ('start', 'end'):
            completed = period['coverage'] == 'completed-interval'
            actual = completed or (key == 'start' and period['coverage'] == 'partial-publication')
            value = period[key]
            if not actual or value['value'] is None or key in conflicts:
                continue
            cite = value['support'][0]
            support = Support(cite['source'], f"page:{cite['page']}/{cite['locator']}",
                              period['coverage'] + ': ' + period['statement'] + '; ' + cite['quote'])
            kind = 'municipal-publication-' + key
            events.append(AdministrativeEvent(publication.identity + ':' + kind, kind,
                publication.document, None, date.fromisoformat(value['value']), support))
    return replace(publication, events=tuple(events),
                   source_fields=dict(publication.source_fields, period_conflicts=conflicts))


def retained_publication_attestation(request_id, store):
    """Replay the named certificate reading without rereading a principal or dispatching."""
    from .document_subscription import read_retained
    return _attestation(read_retained(request_id, Path(store)), store)


def connect_publication_attestation(attestation, publications, *, acquisitions):
    """Use an acquired certificate route and its exact native register occurrence.

    The native declaration's existing attachment binder owns principal identity.
    This connection supplies no identity from filenames, subjects or protocols.
    Certificate claims survive unavailable or conflicting declaration connections.
    """
    acquisitions = tuple(acquisitions)
    reading = attestation.source_fields['attestation']
    routes = _acquired_routes(acquisitions)
    issues, matched = [], []
    for publication in publications:
        values = publication.source_fields
        if not any(attestation.support.source in routes.get(link['url'], ())
                   for link in values.get('document_routes', ())):
            continue
        fields = values.get('source_fields', {})
        reference = fields.get('N. Repertorio Albo', fields.get('Nro'))
        if (not reading['publisher']['value'] or not reading['register_reference']['value']
                or compact(publication.publisher).casefold() != compact(attestation.publisher).casefold()
                or reference != reading['register_reference']['value']):
            issues.append(dict(publication=publication.identity,
                               cause='Certificate publisher or repertory does not match the native declaration'))
            continue
        matched.append(publication)
    candidates = {(p.document, p.document_date) for p in matched
                  if p.document is not None and p.document_date is not None}
    document, adopted = attestation.document, attestation.document_date
    if any(component['cause'] == 'conflict' for component in reading['act'].values()):
        document, adopted = None, None
        issues.append(dict(cause='Certificate act component remains in conflict; native attachment cannot resolve it'))
    elif len(candidates) > 1:
        document, adopted = None, None
        issues.append(dict(cause='Native attachments resolve to competing act identities or adoption dates'))
    elif candidates:
        candidate, candidate_date = next(iter(candidates))
        act = reading['act']
        number, stated_date = act['number']['value'], act['adopted']['value']
        contradicts = (act['authority']['value'] == 'other'
            or (number and candidate != act_id(number, candidate_date.year))
            or (stated_date and stated_date != candidate_date.isoformat())
            or (document and (document, adopted) != (candidate, candidate_date)))
        if contradicts:
            document, adopted = None, None
            issues.append(dict(cause='Certificate act components conflict with the acquired native attachment'))
        else:
            document, adopted = candidate, candidate_date
    elif not document:
        issues.append(dict(cause=('Matching native declaration has no resolved principal identity'
                                  if matched else 'No matching acquired native certificate route and repertory')))
    conflicts = dict(attestation.source_fields['period_conflicts'])
    for publication in matched:
        for key, field in [('start', 'Data inizio pubb.'), ('end', 'Data fine pubb.')]:
            declared = publication.source_fields.get('declared_dates', {}).get(field)
            certified = reading['period'][key]['value']
            if declared and certified and declared != certified:
                conflicts[key] = 'Certified date conflicts with the native register declaration'
    for record in acquisitions:
        if record.get('sha256') == attestation.support.source and record.get('captured_at'):
            captured = datetime.fromisoformat(record['captured_at'])
            if captured.tzinfo is not None:
                for key in ('start', 'end'):
                    day = reading['period'][key]['value']
                    if day and day > captured.astimezone(ZoneInfo('Europe/Rome')).date().isoformat():
                        conflicts[key] = 'Attested day follows acquisition of the certificate'
    return _attestation_events(replace(attestation, document=document, document_date=adopted,
        publisher=matched[0].publisher if matched else attestation.publisher,
        source_fields=dict(attestation.source_fields, attachment_issues=issues,
            declarations=tuple(matched), period_conflicts=conflicts)))


def publication_records(path: Path):
    """Native Akropolis municipal register: issued document != incoming protocol.

    Dates are the register's actual publication declarations. They do not by
    themselves establish uninterrupted posting, service or recipient effect.
    Every row survives, including those with no identifiable regional document.
    """
    path = Path(path)
    data = json.loads(path.read_text())
    digest = file_digest(path)
    for index, row in enumerate(data['content']):
        publisher = row['pfoPblTpAtto']['pfoPblEnti']['dlNome']
        text = compact(unescape(row['dlOgg']))
        matches = list(re.finditer(r'(?:DDS\s*)?N[.°]?\s*(\d+)\s+del\s+(\d{2})/(\d{2})/(\d{4})', text, re.I))
        document, adopted = None, None
        # The subject explicitly identifies the regional office and adopted act;
        # niNumAtto/dtAtto can instead describe the municipality's incoming record.
        if len(matches) == 1 and re.search(r'Sezione\s+Oss?e+rvatorio\s+Fitosanitario', text, re.I):
            number, d, m, y = matches[0].groups()
            document, adopted = act_id(number, y), date(int(y), int(m), int(d))
        support = Support(digest, f'content[{index}]/id:{row["id"]}',
                          'Municipal register declaration: '+text)
        events = []
        if document and row.get('dbStato') == 'SCADUTO' and not row.get('dtAnnul'):
            for key, kind in [('dtIniPubl', 'municipal-publication-start'), ('dtFinPubl', 'municipal-publication-end')]:
                if row.get(key):
                    events.append(AdministrativeEvent(digest+':'+row['id']+':'+kind,
                        kind, document, None, date.fromisoformat(row[key]), support))
        yield Publication(row['id'], publisher, document, adopted, row, tuple(events), support)


def regional_publication(path: Path):
    """Read labelled regional Albo detail fields, without interpreting the act.

    A concluded regional publication is neither municipal posting nor recipient
    notice. Preserve the portal timestamps as text; expose dates, not an inferred
    timezone or proof that posting was uninterrupted.
    """
    from bs4 import BeautifulSoup

    path = Path(path)
    soup = BeautifulSoup(path.read_bytes(), 'html.parser')
    fields = {}
    for label in soup.select('label'):
        value = label.find_next_sibling('span')
        if value is not None:
            key = compact(label.get_text(' ', strip=True))
            if key in fields:
                raise ValueError('Regional publication has duplicate labelled fields')
            fields[key] = compact(value.get_text(' ', strip=True))
    number = fields['Numero Adozione Atto']
    adopted = date.fromisoformat(fields['Data Adozione Atto'].split()[0])
    document = None
    if (fields['Tipo Atto o Tipo Documento'] == 'Determinazione Dirigenziale'
            and '181 - Sezione Osservatorio Fitosanitario' in fields['Struttura proponente']
            and number.isdecimal()):
        document = act_id(number, adopted.year)
    registered = date.fromisoformat(fields['Data registrazione albo pretorio'].split()[0])
    identity = f"regional-albo:{registered.year}:{fields['Num. registro albo pretorio']}"
    digest = file_digest(path)
    support = Support(digest, identity, 'Regional Albo detail: '+fields['Oggetto'])
    events = []
    if document and fields['Stato Pubblicazione'] == 'Conclusa':
        for key, kind in [('Data Inizio Pubblicazione', 'regional-publication-start'),
                          ('Data Fine Pubblicazione', 'regional-publication-end')]:
            occurred = date.fromisoformat(fields[key].split()[0])
            events.append(AdministrativeEvent(digest+':'+kind, kind, document,
                                               None, occurred, support))
    return Publication(identity, 'Regione Puglia', document, adopted, fields,
                       tuple(events), support)


def connected_publications(publications, measures):
    """Require the issued act and its adoption date, not a municipality's protocol."""
    identities = set()
    for measure in measures:
        try:
            identities.add((measure.identity, measure.adopted))
        except MissingInput:
            continue
    return tuple(p for p in publications if (p.document, p.document_date) in identities)


def parsec_publications(path, *, publisher, source_url, measures, acquisitions):
    """Bind native declarations through acquired originals, never subject mentions.

    Multiple publications of the same original remain separate occurrences.
    Unresolved or competing attachment identities retain the declaration without
    supplying a document-specific event or a clock anchor.
    """
    from .notices import parsec_publication_declarations
    rows = parsec_publication_declarations(path, publisher=publisher, source_url=source_url)
    yield from _attached_publications(rows, measures=measures, acquisitions=acquisitions)


def domino_publication(path, *, publisher, source_url, measures, acquisitions):
    """Connect a Domino declaration by its acquired originals, not its subject."""
    from .notices import domino_publication_detail
    row = domino_publication_detail(path, publisher=publisher, source_url=source_url)
    return next(_attached_publications((row,), measures=measures, acquisitions=acquisitions))


def _acquired_routes(acquisitions):
    routes = {}
    for record in acquisitions:
        if record.get('sha256'):
            for key in ('url', 'final_url'):
                if record.get(key):
                    routes.setdefault(record[key], set()).add(record['sha256'])
    return routes


def _attached_publications(rows, *, measures, acquisitions):
    """Share only acquired-route attachment and dated declaration event handling."""
    rows = tuple(rows)
    acquisitions = tuple(acquisitions)
    source_digests = {row.sha256 for row in rows}
    routes = _acquired_routes(acquisitions)
    capture_days = {}
    for record in acquisitions:
        if record.get('sha256') in source_digests and record.get('captured_at'):
            captured = datetime.fromisoformat(record['captured_at'])
            if captured.tzinfo is not None:
                capture_days.setdefault(record['sha256'], []).append(
                    captured.astimezone(ZoneInfo('Europe/Rome')).date())
    originals = {}
    for measure in measures:
        digest = measure.response['request']['sources'][0]
        try:
            identity = measure.identity, measure.adopted
        except MissingInput:
            continue
        originals.setdefault(digest, set()).add(identity)
    for row in rows:
        observed = capture_days.get(row.sha256, ())
        values = dict(row.values, observed_on=max(observed).isoformat() if observed else None)
        acquired = {digest for route in values['document_routes']
                    for digest in routes.get(route['url'], ())}
        candidates = {identity for digest in acquired
                      for identity in originals.get(digest, ())}
        values['attachment_issue'] = (
            'No native document route' if not values['document_routes'] else
            'Native document routes have no held source acquisition' if not acquired else
            'Acquired route sources lack a qualified measure identity and adoption date' if not candidates else
            'Acquired route sources resolve to competing measure identities or adoption dates'
            if len(candidates) > 1 else None)
        document, adopted = next(iter(candidates)) if len(candidates) == 1 else (None, None)
        support = Support(row.sha256, row.locator,
                          'Municipal register declaration: ' + values['source_fields']['Oggetto'])
        events = []
        if document:
            for field, kind in [('Data inizio pubb.', 'municipal-publication-start'),
                                ('Data fine pubb.', 'municipal-publication-end')]:
                declared = values['declared_dates'][field]
                observed = values['observed_on']
                # A displayed future date is a plan, not an occurred anchor. The
                # end day must have elapsed; this still does not certify continuity.
                occurred = (declared and observed and
                            (declared <= observed if kind.endswith('-start') else declared < observed))
                if kind.endswith('-end') and values.get('publication_status', 'NO') != 'NO':
                    occurred = False
                if occurred:
                    events.append(AdministrativeEvent(row.sha256 + ':' + row.locator + ':' + kind,
                                  kind, document, None,
                                  date.fromisoformat(declared), support))
        yield Publication(row.sha256 + ':' + row.locator, values['publisher'], document,
                          adopted, values, tuple(events), support)

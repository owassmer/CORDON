"""Attach actual administrative records to issued measures and accepted clocks."""
from dataclasses import dataclass
from datetime import date, datetime
from html import unescape
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from cordon_c.quantities import clock_boundary
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
    routes = {}
    capture_days = []
    source_digest = file_digest(Path(path))
    for record in acquisitions:
        if record.get('sha256') == source_digest and record.get('captured_at'):
            captured = datetime.fromisoformat(record['captured_at'])
            if captured.tzinfo is not None:
                capture_days.append(captured.astimezone(ZoneInfo('Europe/Rome')).date())
        if record.get('sha256'):
            for key in ('url', 'final_url'):
                if record.get(key):
                    routes.setdefault(record[key], set()).add(record['sha256'])
    originals = {}
    for measure in measures:
        digest = measure.response['request']['sources'][0]
        try:
            identity = measure.identity, measure.adopted
        except MissingInput:
            continue
        originals.setdefault(digest, set()).add(identity)
    for row in parsec_publication_declarations(path, publisher=publisher, source_url=source_url):
        values = dict(row.values, observed_on=max(capture_days).isoformat() if capture_days else None)
        candidates = {identity for route in values['document_routes']
                      for digest in routes.get(route['url'], ())
                      for identity in originals.get(digest, ())}
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
                if occurred:
                    events.append(AdministrativeEvent(row.sha256 + ':' + row.locator + ':' + kind,
                                  kind, document, None,
                                  date.fromisoformat(declared), support))
        yield Publication(row.sha256 + ':' + row.locator, publisher, document,
                          adopted, values, tuple(events), support)


CLOCK_ANCHORS = {
    'posting of the prescription in the competent municipal albo pretorio': 'municipal-publication-start',
    'end of the publication period of the prescription in the competent municipal albo pretorio': 'municipal-publication-end',
    'legally sufficient notification of the operative prescription to this recipient': 'recipient-notification',
    "the owner's communication electing voluntary removal or execution by ARIF": 'owner-election',
}


def event_deadline(snapshot, clock_id, at, event, *, document, recipient, zone, calendar=None):
    """Supply B's exact anchor to C, preserving what the calculation establishes.

    This computes the boundary. B's applies_when / A's recipient effect and a
    complete history remain independent inputs to any breach/silence conclusion.
    """
    quantity = snapshot.quantity(clock_id, at)
    meaning = quantity['anchor'].get('event')
    if meaning not in CLOCK_ANCHORS:
        raise ValueError('This clock requires another source event meaning')
    kind = CLOCK_ANCHORS[meaning]
    if kind.startswith('municipal-publication') and recipient is not None:
        raise ValueError('A municipal posting is not a recipient-specific event')
    anchor = event.anchor(kind=kind, document=document, recipient=recipient,
                          precision='instant' if quantity['unit'] == 'hours' else 'date')
    return clock_boundary(snapshot, clock_id, at, anchor, zone=zone, calendar=calendar)


def publication_deadline(snapshot, clock_id, at, publication, *, document,
                         competent_publisher, zone, calendar):
    """Calculate from this municipality's declared posting for this exact act.

    Recipient effectiveness and local-calendar completeness remain separate
    factual inputs. The returned boundary is not a finding of owner default.
    """
    if publication.publisher != competent_publisher or publication.document != document:
        raise ValueError('Publication belongs to another municipality or document')
    meaning = snapshot.quantity(clock_id, at)['anchor'].get('event')
    kind = CLOCK_ANCHORS.get(meaning)
    if kind not in {'municipal-publication-start', 'municipal-publication-end'}:
        raise ValueError('Publication cannot supply a recipient response or notice')
    events = [event for event in publication.events if event.kind == kind]
    if len(events) != 1:
        raise ValueError('No unique actual publication declaration for this anchor')
    return event_deadline(snapshot, clock_id, at, events[0], document=document,
                          recipient=None, zone=zone, calendar=calendar)

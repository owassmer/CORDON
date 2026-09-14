"""Attach actual administrative records to issued measures and accepted clocks."""
from dataclasses import dataclass
from datetime import date
from html import unescape
import json
from pathlib import Path
import re

from cordon_c.quantities import clock_boundary
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


def connected_publications(publications, measures):
    """Require the issued act and its adoption date, not a municipality's protocol."""
    identities = {(m.identity, m.adopted) for m in measures}
    return tuple(p for p in publications if (p.document, p.document_date) in identities)


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

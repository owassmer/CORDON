"""Albo postings and executor acts, attached to orders by the identity each record itself prints.

A register row or a posted document attaches to an order only when it prints the
order's number and year, and its date where it prints one, together with the
issuing office (the Osservatorio fitosanitario). Bytes, subjects and filenames
alone attach nothing. A municipal posting supplies its declared start; an end the
source shows only as a retention horizon leaves the interval open. An act of the
executor that names an order is the executor's own administrative event, not a
posting of the order. Whether any of these is notice or execution stays with A.
"""
import csv
from datetime import date, datetime
from html import unescape
import io
import re

from .events import AdministrativeEvent
from .evidence import Support
from .removal_events import act_id

ISSUER = re.compile(r'osservatorio\s+fitosanitario', re.I)
# "DDS 122/2021", "D.D.S. n. 85/2021", "DDS135/2021"
NUMBERED = re.compile(r'\bD\.?\s?D\.?\s?S\.?\s*(?:n[.°]?\s*)?0*(\d{1,4})\s*/\s*(\d{4})\b', re.I)
# "n. 128 del 04/11/2021", "N. 00005 DEL 31.01.2023", "n. 11 del 09.02.2023"
DATED = re.compile(r'\bn(?:[.°]|r\.?)?\s*0*(\d{1,4})\s+del(?:l[’\'])?\s*(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b', re.I)
OPENWEB = ('Tipo', 'numero atto', 'Data atto', 'Oggetto', 'Inizio pubblicazione', 'Fine pubblicazione')


def _day(words):
    try:
        return datetime.strptime((words or '').strip(), '%d/%m/%Y').date()
    except ValueError:
        return None


def printed_orders(text):
    """(number, year, printed date or None, words) for every order identity a text prints."""
    found = []
    for match in NUMBERED.finditer(text):
        found.append((int(match.group(1)), int(match.group(2)), None, match.group(0)))
    for match in DATED.finditer(text):
        day, month, year = (int(g) for g in match.groups()[1:])
        try:
            printed = date(year, month, day)
        except ValueError:
            continue
        found.append((int(match.group(1)), year, printed, match.group(0)))
    return found


def openweb_rows(data: bytes):
    """An OpenWeb albo register export (csv.php): one dict per posting, entities decoded, with its row number."""
    text = data.decode('utf-8', errors='replace')
    if not text.startswith('Tipo,'):
        raise ValueError('Not an OpenWeb albo register export')
    reader = csv.DictReader(io.StringIO(text))
    if not set(OPENWEB) <= set(reader.fieldnames or ()):
        raise ValueError('OpenWeb register export lacks its posting columns')
    return [dict({k: unescape(v or '') for k, v in row.items() if k}, row=number)
            for number, row in enumerate(reader, 2)]


def attach(identities, held, *, issuer_text):
    """Held instruments an identity list names, with the printed date checked against adoption.

    `held` maps instrument to its adoption date. Returns (attached instruments,
    unattached causes).
    """
    attached, unattached = [], []
    if not ISSUER.search(issuer_text):
        return attached, [dict(cause='the record does not print the Osservatorio fitosanitario as issuer')]
    for number, year, printed, words in identities:
        instrument = act_id(number, year)
        if instrument not in held:
            unattached.append(dict(words=words, instrument=instrument, cause='names an order D does not hold'))
        elif printed is not None and printed != held[instrument]:
            unattached.append(dict(words=words, instrument=instrument,
                                   cause="the printed date is not the held order's adoption date"))
        elif instrument not in attached:
            attached.append(instrument)
    return attached, unattached


def register_events(rows, *, source, publisher, role, held):
    """Events an OpenWeb register's rows print about held orders.

    `role` is 'municipal' for a comune's albo, where a row printing the order is its
    posting (declared start and end), or 'executor' for the executor's own albo,
    where a row is the executor's act naming the order (its act date). Only rows
    that print an order identity with the Osservatorio as issuer are considered;
    an identity without an issuer is not an order's identity.
    """
    events, unattached = [], []
    for row in rows:
        text = ' '.join(row.get(k) or '' for k in ('Oggetto', 'Ente', 'Ufficio'))
        identities = printed_orders(text)
        if not identities or not ISSUER.search(text):
            continue
        instruments, causes = attach(identities, held, issuer_text=text)
        unattached += [dict(c, row=row['row'], subject=row['Oggetto'][:300]) for c in causes]
        words = f"{row['Tipo']} n. {row['numero atto']} del {row['Data atto']}: {row['Oggetto']}".strip()
        for instrument in instruments:
            support = Support(source, f"row:{row['row']}", f'{publisher}: {words}')
            if role == 'municipal':
                for kind, words_ in (('municipal-publication-start', row['Inizio pubblicazione']),
                                     ('municipal-publication-end', row['Fine pubblicazione'])):
                    if _day(words_):
                        events.append(AdministrativeEvent(f"{source}:row:{row['row']}:{kind}", kind, instrument,
                                                          None, _day(words_), support))
            elif _day(row['Data atto']):
                events.append(AdministrativeEvent(f"{source}:row:{row['row']}:executor-act", 'executor-act',
                                                  instrument, None, _day(row['Data atto']), support))
    return events, unattached


def jcitygov_posting(data: bytes):
    """A JCityGov albo detail page: register number and date, subject, and the declared period as printed."""
    from bs4 import BeautifulSoup
    text = ' '.join(BeautifulSoup(data, 'html.parser').get_text(' ').split())
    def field(label, stop):
        match = re.search(re.escape(label) + r'\s+(.*?)\s+' + stop, text)
        return match.group(1) if match else None
    period = re.search(r'Periodo Pubblicazione\s+(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})', text)
    if not period:
        raise ValueError('JCityGov detail prints no publication period')
    return dict(register_number=field('Numero di registro', 'Anno protocollo'),
                register_date=field('Data di registro', 'Anno di registro'),
                sender=field('Mittente', 'Ente richiedente'), subject=field('Oggetto', 'Data esecutività'),
                period_start=_day(period.group(1)), period_end_words=period.group(2), text=text)


IDENTITY_SCHEMA = {
    'type': 'object', 'additionalProperties': False, 'required': ['acts', 'issues'],
    'properties': {
        'acts': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False,
            'required': ['issuer', 'act_kind', 'number', 'date_words', 'adopted', 'code', 'subject', 'page'],
            'properties': {
                'issuer': {'type': 'string'}, 'act_kind': {'type': 'string'}, 'number': {'type': 'string'},
                'date_words': {'type': 'string'},
                'adopted': {'type': ['string', 'null'], 'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'},
                'code': {'type': 'string'}, 'subject': {'type': 'string'},
                'page': {'type': 'integer', 'minimum': 1}}}},
        'issues': {'type': 'array', 'items': {'type': 'string'}}}}
IDENTITY_PROMPT = (
    'Read the supplied posted document from its page images. Return only what the pages print, in the JSON '
    'schema supplied. Use no outside knowledge. List the identity of every administrative act the document '
    'itself is (its heading block: issuing office, act kind, number, date, any act code such as a CIFRA code, '
    'and subject), copying each field as printed, with the physical page where it is printed. adopted is the '
    'printed date as YYYY-MM-DD, or null when no full date is printed. Do not list acts the document only '
    'cites. Name in issues any heading you cannot read in full.')


def posted_identity(source, store, *, execute=False, model='gpt-5.6-luna', effort='high', timeout=900):
    """The act identity an image-only posted document prints, read from its page images by subscription vision."""
    from .document_subscription import read_documents
    return read_documents([source], store, prompt=IDENTITY_PROMPT, schema=IDENTITY_SCHEMA, model=model,
                          effort=effort, dpi=150, timeout=timeout, execute=execute)


def posted_document_events(identity_response, posting, *, detail_source, publisher, held):
    """A municipal posting's declared start for the order its posted document prints.

    The posted document's own heading supplies the identity (number, date, issuer);
    the detail page supplies the declared start. An end the detail shows only as a
    retention horizon is not an end: the interval stays open.
    """
    def number(act):  # the act's number is the first number its number field prints ("N. 4 del 08/02/2022 ...")
        match = re.search(r'\d+', act['number'])
        return int(match.group(0)) if match else None

    acts = [a for a in identity_response['reading']['acts'] if number(a) is not None and a['adopted']]
    identities = [(number(a), int(a['adopted'][:4]), date.fromisoformat(a['adopted']),
                   f"{a['act_kind']} {a['number']} {a['date_words']}") for a in acts]
    issuers = ' '.join(a['issuer'] for a in acts)
    instruments, unattached = attach(identities, held, issuer_text=issuers)
    events = []
    for instrument in instruments:
        act = next(a for a in acts if act_id(number(a), a['adopted'][:4]) == instrument)
        support = Support(detail_source, 'Periodo Pubblicazione',
                          f"{publisher}: posting from {posting['period_start'].isoformat()} (declared end "
                          f"{posting['period_end_words']} is a retention horizon; interval open); posted document "
                          f"{identity_response['request']['sources'][0]} page {act['page']} prints "
                          f"{act['issuer']} {act['act_kind']} {act['number']} {act['date_words']} {act['code']}")
        events.append(AdministrativeEvent(f"{detail_source}:municipal-publication-start", 'municipal-publication-start',
                                          instrument, None, posting['period_start'], support))
    return events, unattached

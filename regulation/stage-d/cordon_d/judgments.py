"""Dated events a TAR decision states about named removal orders, one kind per event.

A decision is read from its own GA XML text, block by block, through the Claude
subscription. Each event keeps its block, quotation and whether the court states
it as its own account or reports a party's claim. An event attaches to an order
only when the decision prints that order's number and date and the order is one
the caller holds; the recipient is the person the decision names. Nothing here
decides whether a delivery or posting is legally sufficient notice: that stays
with A's notice rows.
"""
from datetime import date
from pathlib import Path
import re
import warnings

from .case_prescriptions import on_page
from .document_subscription import read_native_blocks, read_retained
from .events import AdministrativeEvent
from .evidence import Support
from .removal_events import act_id
from .store import blob_path

PRESENTATION = 'ga-xml-leaf-div-blocks-v1'
KINDS = ('recipient-pec-delivery', 'municipal-publication-start', 'municipal-publication-end',
         'owner-request', 'administrative-reply')
CONTRACT = {'recipient-pec-delivery': 'recipient-notice', 'municipal-publication-start': 'recipient-notice',
            'municipal-publication-end': 'recipient-notice', 'owner-request': 'owner-response',
            'administrative-reply': 'administrative-event'}


def _object(**properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


TEXT = {'type': 'string'}
CITATION = _object(block={'type': 'integer', 'minimum': 1}, quote=TEXT)
SCHEMA = _object(
    orders={'type': 'array', 'items': _object(
        number=TEXT, adopted_words=TEXT, year={'type': 'string', 'pattern': '^[0-9]{4}$'}, support=CITATION)},
    events={'type': 'array', 'items': _object(
        kind={'type': 'string', 'enum': list(KINDS)}, order_index={'type': 'integer', 'minimum': 0},
        recipient=TEXT, municipality=TEXT, date_words=TEXT,
        date={'type': 'string', 'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'},
        attribution={'type': 'string', 'enum': ['court', 'party']}, support=CITATION)},
    issues={'type': 'array', 'items': _object(block={'type': ['integer', 'null'], 'minimum': 1}, detail=TEXT)},
)
PROMPT = (Path(__file__).resolve().parents[1] / 'judgment-event-reading.txt').read_text()


def blocks(data: bytes):
    """The decision's leaf `h:div` blocks, whitespace-compacted, empty blocks dropped, in order."""
    from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(data, 'html.parser')
    if soup.find('ga') is None:
        raise ValueError('Not a GA decision document')
    leaves = [d for d in soup.find_all('h:div') if not d.find('h:div')]
    texts = [' '.join(d.get_text(' ', strip=True).split()) for d in leaves]
    texts = [t for t in texts if t]
    if not texts:
        raise ValueError('GA decision has no text blocks')
    return texts


def validate(reading, texts):
    """Bind every quotation and copied field to its cited block; this does not certify meaning."""
    def cited(citation, what):
        number = citation['block']
        if not 1 <= number <= len(texts) or not on_page(citation['quote'], texts[number - 1]):
            raise ValueError(f'{what}: quotation is not in block {number}')
        return texts[number - 1]

    for index, order in enumerate(reading['orders']):
        text = cited(order['support'], f'order {index}')
        for words in (order['number'], order['adopted_words']):
            if not words.strip() or not on_page(words, text):
                raise ValueError(f'order {index}: number or date is not in its cited block')
        if order['year'] not in order['adopted_words'] and order['year'][2:] not in order['adopted_words']:
            raise ValueError(f'order {index}: year is not in its printed date')
    for index, event in enumerate(reading['events']):
        what = f'event {index}'
        text = cited(event['support'], what)
        if event['order_index'] >= len(reading['orders']):
            raise ValueError(f'{what}: names no listed order')
        for words in (event['recipient'], event['municipality'], event['date_words']):
            if words.strip() and not on_page(words, text):
                raise ValueError(f'{what}: a copied field is not in its cited block')
        day = date.fromisoformat(event['date'])
        if not event['date_words'].strip() or str(day.day) not in re.findall(r'\d+', event['date_words']):
            raise ValueError(f'{what}: the printed date does not state its day')
        municipal = event['kind'].startswith('municipal-publication')
        if municipal == bool(event['recipient'].strip()):
            raise ValueError(f'{what}: a posting names no recipient; other events name one')
    for issue in reading['issues']:
        if issue['block'] is not None and not 1 <= issue['block'] <= len(texts):
            raise ValueError('An issue names an unsupplied block')


def read_judgment(source, store, *, execute=False, model='opus', effort='medium', timeout=900, refused=None):
    """Read one retained decision; replay unless `execute`. `refused` makes one stated reread."""
    from .case_prescriptions import REREAD
    texts = blocks(blob_path(store, source).read_bytes())
    prompt = PROMPT if refused is None else PROMPT + '\n' + REREAD.format(cause=refused).replace(
        'physical page', 'block').replace('pages', 'blocks') + '\n'
    response = read_native_blocks(source, texts, store, prompt=prompt, schema=SCHEMA,
                                  presentation=PRESENTATION, model=model, effort=effort,
                                  timeout=timeout, execute=execute)
    validate(response['reading'], texts)
    return response


def retained_judgment(request_id, store):
    response = read_retained(request_id, Path(store))
    if response['request'].get('schema') != SCHEMA:
        raise ValueError('Retained request used another judgment contract')
    source = response['request']['sources'][0]
    validate(response['reading'], blocks(blob_path(Path(store), source).read_bytes()))
    return response


DISPOSITION_PRESENTATION = 'ga-xml-leaf-div-blocks-v1'
OUTCOMES = ('accoglie', 'accoglie-in-parte', 'respinge', 'improcedibile', 'inammissibile', 'cessata-materia',
            'cautelare-accoglie', 'cautelare-respinge', 'interlocutoria', 'other')
EFFECTS = ('annulled', 'not-annulled', 'suspended', 'suspension-refused', 'no-effect-stated')
SCOPES = ('whole-act', 'applicants', 'other')
PASSAGES = {'type': 'array', 'items': _object(literal=TEXT, support=CITATION)}
DISPOSITION_SCHEMA = _object(
    outcome=_object(literal=TEXT, kind={'type': 'string', 'enum': list(OUTCOMES)}, support=CITATION),
    acts={'type': 'array', 'items': _object(
        number=TEXT, adopted_words=TEXT, year={'type': 'string', 'pattern': '^[0-9]{4}$'},
        effect={'type': 'string', 'enum': list(EFFECTS)},
        scope=_object(kind={'type': 'string', 'enum': list(SCOPES)}, dispositive=TEXT, stated=PASSAGES),
        applicants=_object(literal=TEXT, support={'anyOf': [{'type': 'null'}, CITATION]}),
        grounds=PASSAGES, stated_reason=PASSAGES, support=CITATION)},
    issues={'type': 'array', 'items': _object(block={'type': ['integer', 'null'], 'minimum': 1}, detail=TEXT)},
)
DISPOSITION_PROMPT = (Path(__file__).resolve().parents[1] / 'judgment-disposition-reading.txt').read_text()


def decision_identity(data: bytes):
    """The decision's own GA descriptors: kind, number, section, register (NRG), decided and published dates."""
    from datetime import datetime
    from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(data, 'html.parser')

    def day(words):
        return datetime.strptime(words, '%d/%m/%Y').date() if words else None

    fascicolo, registro, urn = soup.find('fascicolo'), soup.find('registro'), soup.find('urn')
    section = re.search(r'sezione\.(\w+)', urn.get_text()) if urn else None
    decided = [d['norm'] for d in soup.find_all('dataeluogo') if d.get('norm')]
    published = soup.find('datapubblicazione')
    return dict(
        kind=soup.find('tipologia').get_text(strip=True) if soup.find('tipologia') else None,
        number=f"{int(fascicolo['n'])}/{fascicolo['anno']}" if fascicolo else None,
        section=section.group(1) if section else None,
        register=f"{registro['anno']}{registro['n']}" if registro else None,
        decided=day(decided[0]) if decided else None,
        published=day(published.get_text(strip=True)) if published else None)


def validate_disposition(reading, texts):
    """Bind the outcome, every act and every passage to its cited block; this does not certify meaning."""
    def cited(citation, what):
        number = citation['block']
        if not 1 <= number <= len(texts) or not on_page(citation['quote'], texts[number - 1]):
            raise ValueError(f'{what}: quotation is not in block {number}')
        return texts[number - 1]

    text = cited(reading['outcome']['support'], 'outcome')
    if not reading['outcome']['literal'].strip() or not on_page(reading['outcome']['literal'], text):
        raise ValueError('outcome: the dispositive words are not in their cited block')
    for index, act in enumerate(reading['acts']):
        what = f'act {index}'
        text = cited(act['support'], what)
        for words in (act['number'], act['adopted_words']):
            if not words.strip() or not on_page(words, text):
                raise ValueError(f'{what}: number or date is not in its cited block')
        if act['year'] not in act['adopted_words'] and act['year'][2:] not in act['adopted_words']:
            raise ValueError(f'{what}: year is not in its printed date')
        if act['scope']['dispositive'].strip() and not on_page(act['scope']['dispositive'],
                                                                texts[reading['outcome']['support']['block'] - 1]):
            raise ValueError(f'{what}: the dispositive scope is not in the outcome block')
        for field in ('grounds', 'stated_reason'):
            for passage in act[field]:
                if not on_page(passage['literal'], cited(passage['support'], f'{what} {field}')):
                    raise ValueError(f'{what}: a {field} passage is not in its cited block')
        for passage in act['scope']['stated']:
            if not on_page(passage['literal'], cited(passage['support'], f'{what} scope')):
                raise ValueError(f'{what}: a scope passage is not in its cited block')
        applicants = act['applicants']
        if applicants['literal'].strip():
            if applicants['support'] is None or not on_page(
                    applicants['literal'], cited(applicants['support'], f'{what} applicants')):
                raise ValueError(f'{what}: the applicants are not in their cited block')
    for issue in reading['issues']:
        if issue['block'] is not None and not 1 <= issue['block'] <= len(texts):
            raise ValueError('An issue names an unsupplied block')


def read_disposition(source, store, *, execute=False, model='opus', effort='medium', timeout=900, refused=None):
    """Read one retained decision's own disposition; replay unless `execute`. `refused` makes one reread."""
    from .case_prescriptions import REREAD
    texts = blocks(blob_path(store, source).read_bytes())
    prompt = DISPOSITION_PROMPT if refused is None else DISPOSITION_PROMPT + '\n' + REREAD.format(
        cause=refused).replace('physical page', 'block').replace('pages', 'blocks') + '\n'
    response = read_native_blocks(source, texts, store, prompt=prompt, schema=DISPOSITION_SCHEMA,
                                  presentation=DISPOSITION_PRESENTATION, model=model, effort=effort,
                                  timeout=timeout, execute=execute)
    validate_disposition(response['reading'], texts)
    return response


def annulment_basis(response, identity, *, held_instruments, appeals=None):
    """`operative-act` supersession/correction/annulment basis entries, one per held act the decision bears on.

    Each entry is the court's own disposition: outcome, effect on the act, scope as
    the decision states it, applicants, grounds or stated reason, and the decision's
    own decided and published dates. `appeals` is what the caller found in held
    appeal indexes; an empty search is stated as such, never as finality.
    """
    reading = response['reading']
    source = response['request']['sources'][0]
    entries, unattached = [], []
    for index, act in enumerate(reading['acts']):
        number = re.sub(r'\D', '', act['number'])
        instrument = act_id(number, act['year']) if number else None
        entry = dict(instrument=instrument, decision=dict(identity, source=source),
                     outcome=reading['outcome']['literal'], outcome_kind=reading['outcome']['kind'],
                     effect=act['effect'], scope=act['scope'], applicants=act['applicants'],
                     grounds=act['grounds'], stated_reason=act['stated_reason'],
                     support=[reading['outcome']['support'], act['support']],
                     appeal=appeals, request_sha256=response['request_sha256'],
                     provenance='model_proposed_reading')
        (entries if instrument in held_instruments else unattached).append(entry)
    return entries, unattached


def liveness_closures(entries):
    """What each ricorso's latest disposition states about an order's liveness, per order.

    Decisions of one ricorso (one register number) are taken in publication order;
    the latest that states an effect on the act governs. An annulment reaches the
    order for the scope the decision states, from its publication. A granted interim
    suspension is the latest held disposition of its ricorso; the end it states is
    carried. A challenge declared improcedibile or ended carries the court's own
    stated reason (for example a later act that superseded the order). A rejection
    or a refused interim measure states nothing about liveness.
    """
    latest = {}
    for entry in entries:
        if entry['effect'] == 'no-effect-stated':
            continue
        key = (entry['instrument'], entry['decision']['register'])
        if key not in latest or entry['decision']['published'] > latest[key]['decision']['published']:
            latest[key] = entry
    closures = {}
    for (instrument, _), entry in sorted(latest.items(), key=lambda item: str(item[0])):
        reason = tuple(p['literal'] for p in entry['stated_reason'])
        if entry['effect'] in ('annulled', 'suspended'):
            effect = entry['effect']
        elif entry['effect'] == 'not-annulled' and reason:
            effect = 'ended-with-stated-reason'
        else:
            continue
        closures.setdefault(instrument, []).append(dict(
            effect=effect, scope=entry['scope']['kind'], applicants=entry['applicants']['literal'],
            outcome=entry['outcome'], dispositive_scope=entry['scope']['dispositive'],
            stated_scope=tuple(p['literal'] for p in entry['scope']['stated']), stated_reason=reason,
            decision=entry['decision'], since=entry['decision']['published']))
    return closures


def judgment_events(response, *, held_instruments):
    """AdministrativeEvents for orders the caller holds; every other event stays unattached with its cause.

    A municipal posting is a cohort event (no recipient); the others name the
    recipient the decision prints. The support names the block and whether the
    court states the event or reports a party's claim.
    """
    reading = response['reading']
    source = response['request']['sources'][0]
    held = set(held_instruments)
    attached, unattached = [], []
    for index, event in enumerate(reading['events']):
        order = reading['orders'][event['order_index']]
        number = re.sub(r'\D', '', order['number'])
        instrument = act_id(number, order['year']) if number else None
        citation = event['support']
        if instrument not in held:
            unattached.append(dict(event, order=order, cause='the decision names an order D does not hold'
                                   if instrument else 'the printed order number has no digits'))
            continue
        support = Support(source, f"block:{citation['block']}",
                          f"{event['attribution']}: {citation['quote']}")
        attached.append(AdministrativeEvent(
            f"{source}:block:{citation['block']}:{event['kind']}:{index}", event['kind'], instrument,
            None if event['kind'].startswith('municipal-publication') else event['recipient'],
            date.fromisoformat(event['date']), support))
    return tuple(attached), tuple(unattached)

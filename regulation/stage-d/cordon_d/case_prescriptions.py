"""`case-prescription` records read from each order's own operative text.

One record is one removal prescription an order's operative part addresses to its
recipients: the instrument, recipients or cohort, the stated commencement term as
printed, the commencement and coercive populations, the executor, the stated
consequence and the governing A references. Positions listed in annexes stay with
`cordon_d.measures`; this reader does not recreate them.
"""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from cordon_c.core import Evaluation, MissingInput, evaluate
from .document_subscription import read_native_text, read_retained
from .prescriptions import lawfully_due
from .removal_events import act_id
from .store import blob_path

RULE = 'IT-L241-A21TER:Art.21-ter(1):stated-term-coercive-direction'
CLOCK = 'B-CLK-IT-L241-21TER-stated-commencement-term'
CLAUSE = ('the operative prescription governing this recipient states in its operative part a commencement '
          'term running from notification and commits the Osservatorio to direct coercive removal on '
          'noncommencement')
WORK = 'the commencement work the prescription states is lawfully due from this recipient'
COERCE = 'removal of the population the prescription names for coercion is lawfully due'
NOTICE = 'legally sufficient notification of that prescription to this recipient has occurred'


def _object(**properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


def _array(items):
    return {'type': 'array', 'items': items}


def _choice(*values):
    return {'type': 'string', 'enum': list(values)}


TEXT = {'type': 'string'}
OPTIONAL_TEXT = {'type': ['string', 'null']}
CITATIONS = _array(_object(page={'type': 'integer', 'minimum': 1}, quote=TEXT))
SCHEMA = _object(
    identity=_object(issuer=TEXT, authority=_choice('puglia-osservatorio', 'other', 'unresolved'),
                     number=OPTIONAL_TEXT, adopted={'type': ['string', 'null'],
                                                    'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'},
                     title=TEXT, support=CITATIONS),
    prescribed_work=_array(_object(
        recipients=TEXT, cohort=TEXT, work=TEXT, population=TEXT,
        by_reference={'anyOf': [{'type': 'null'}, _object(
            number=TEXT, year={'type': 'string', 'pattern': '^[0-9]{4}$'})]},
        support=CITATIONS)),
    enforcement_clauses=_array(_object(
        part=_choice('operative', 'recital'),
        work_indices=_array({'type': 'integer', 'minimum': 0}),
        commencement_work=TEXT, commencement_population=TEXT,
        term={'anyOf': [{'type': 'null'}, _object(number=TEXT, unit_word=TEXT, literal=TEXT)]},
        anchor=_object(literal=TEXT, kind=_choice('notification', 'other', 'none')),
        consequence=TEXT, commitment=_choice('commits', 'permits', 'other'),
        coercive_population=_object(literal=TEXT, resolved=TEXT),
        executor=OPTIONAL_TEXT, limits=_array(TEXT), support=CITATIONS)),
    relationships=_array(_object(
        relationship=_choice('corrects', 'supplements', 'completes', 'replaces', 'revokes', 'suspends'),
        number=TEXT, year={'type': 'string', 'pattern': '^[0-9]{4}$'}, affected_payload=TEXT,
        support=CITATIONS)),
    issues=_array(_object(page={'type': ['integer', 'null'], 'minimum': 1},
                          aspect=_choice('identity', 'work', 'clauses', 'relationships', 'coverage'),
                          detail=TEXT)),
)
PROMPT = (Path(__file__).resolve().parents[1] / 'prescription-reading.txt').read_text()
_QUOTES = str.maketrans({'’': "'", '‘': "'", '´': "'", '`': "'",
                         '“': '"', '”': '"', '«': '"', '»': '"',
                         ' ': ' ', '–': '-', '—': '-'})


def _plain(text):
    return re.sub(r'\s+', '', (text or '').translate(_QUOTES)).lower()


def page_texts(source, store):
    """The page text the transport supplied, by physical page number."""
    import pymupdf
    with pymupdf.open(blob_path(store, source)) as document:
        return {n: re.sub(r'[ \t]+', ' ', page.get_text(sort=True)) for n, page in enumerate(document, 1)}


def on_page(quote, text):
    """Every ' … '-joined part of the quote occurs in the page text, whitespace aside."""
    parts = [p for p in re.split(r'\s*(?:…|\.\.\.|\[…\])\s*', quote or '') if p.strip()]
    plain = _plain(text)
    return bool(parts) and all(_plain(p) in plain for p in parts)


def on_cited(words, pages, numbers):
    """Words occur on one cited page, or run from one cited page onto the next cited page.

    A clause printed across a page break has the running header and footer
    between its halves; each half must still occur on its own page.
    """
    parts = [p for p in re.split(r'\s*(?:…|\.\.\.|\[…\])\s*', words or '') if p.strip()]
    texts = {n: _plain(pages[n]) for n in numbers}

    def found(part):
        part = _plain(part)
        if any(part in text for text in texts.values()):
            return True
        return any(_straddles(texts[n], texts[n + 1], part[:k], part[k:])
                   for n in texts if n + 1 in texts for k in range(1, len(part)))
    return bool(parts) and all(found(p) for p in parts)


def _straddles(first, second, head, tail, margin=400):
    """The head closes the first page's text, before its footer; the tail opens the next page's
    text, after its header. Margins are in non-whitespace characters."""
    end, start = first.rfind(head), second.find(tail)
    return end >= 0 and start >= 0 and end + len(head) >= len(first) - margin and start <= margin


def validate(reading, pages):
    """Bind every claim to its supplied page; this does not certify meaning."""
    def cited(support, what):
        if not support:
            raise ValueError(f'{what} needs source support')
        for citation in support:
            if citation['page'] not in pages or not on_page(citation['quote'], pages[citation['page']]):
                raise ValueError(f'{what}: quotation is not on page {citation["page"]}')
        return sorted({c['page'] for c in support})

    cited(reading['identity']['support'], 'identity')
    if reading['identity']['adopted']:
        date.fromisoformat(reading['identity']['adopted'])
    for index, item in enumerate(reading['prescribed_work']):
        cited(item['support'], f'prescribed work {index}')
    for index, item in enumerate(reading['enforcement_clauses']):
        what = f'enforcement clause {index}'
        numbers = cited(item['support'], what)
        if not item['work_indices'] or not set(item['work_indices']) <= set(range(len(reading['prescribed_work']))):
            raise ValueError(f'{what}: enforces no listed prescribed work')
        term = item['term']
        if term is not None:
            if not on_cited(term['literal'], pages, numbers):
                raise ValueError(f'{what}: term is not on its cited pages')
            if not (term['number'].strip() and term['unit_word'].strip()):
                raise ValueError(f'{what}: term needs its printed number and unit word')
            if _plain(term['number']) + _plain(term['unit_word']) not in _plain(term['literal']):
                raise ValueError(f'{what}: number and unit word are not printed together in the term')
        words = [item['consequence'], item['executor'], item['anchor']['literal'],
                 *item['coercive_population'].values()]
        if any(w and w.strip() and not on_cited(w, pages, numbers) for w in words):
            raise ValueError(f'{what}: a copied field is not on its cited pages')
    for index, item in enumerate(reading['relationships']):
        cited(item['support'], f'relationship {index}')
    for issue in reading['issues']:
        if issue['page'] is not None and issue['page'] not in pages:
            raise ValueError('An issue names an unsupplied page')


def governing_references(snapshot, instrument):
    """Every A row of the instrument and every correction or supplement naming it."""
    return tuple(sorted({sid for sid, rows in snapshot.stable.items() for row in rows
                         if row['instrument_id'] == instrument
                         or instrument in row.get('corrects_instrument_ids', ())}))


@dataclass(frozen=True)
class PrescriptionReading:
    response: dict

    @property
    def values(self):
        return self.response['reading']

    @property
    def source(self):
        return self.response['request']['sources'][0]

    @property
    def instrument(self):
        identity = self.values['identity']
        if identity['authority'] != 'puglia-osservatorio' or not identity['number'] or not identity['adopted']:
            raise MissingInput('Osservatorio act number and adoption date')
        return act_id(re.sub(r'\D', '', identity['number']), identity['adopted'][:4])

    def records(self, snapshot):
        """One `case-prescription` record per enforcement clause over prescribed work.

        Prescribed work that no clause enforces keeps its own record without a
        stated term or consequence. An act that prescribes no removal work to
        recipients has no record.
        """
        instrument = self.instrument
        base = dict(instrument=instrument, adopted=self.values['identity']['adopted'], source=self.source,
                    relationships=tuple(dict(item, instrument=act_id(re.sub(r'\D', '', item['number']),
                                                                     item['year']))
                                        for item in self.values['relationships']),
                    governing_A_references=governing_references(snapshot, instrument),
                    issues=tuple(self.values['issues']), request_sha256=self.response['request_sha256'],
                    provenance='model_proposed_reading')
        work = self.values['prescribed_work']
        enforced = set()
        for index, item in enumerate(self.values['enforcement_clauses']):
            term = item['term']
            enforced.update(item['work_indices'])
            listed = [work[i] for i in item['work_indices']]
            yield dict(
                base, occurrence=f'{self.source}:clause:{index}', part=item['part'],
                recipients=tuple(dict.fromkeys(w['recipients'] for w in listed)),
                cohort=tuple(dict.fromkeys(w['cohort'] for w in listed if w['cohort'])),
                prescribed_scope=tuple(dict(work=w['work'], population=w['population']) for w in listed),
                commencement_population=item['commencement_population'],
                commencement_work=item['commencement_work'],
                stated_term=(term['number'], term['unit_word']) if term else None,
                term_literal=term['literal'] if term else None,
                anchor=item['anchor'], consequence=item['consequence'], commitment=item['commitment'],
                coercive_population=item['coercive_population']['resolved'] or None,
                coercive_words=item['coercive_population']['literal'] or None,
                executor=item['executor'], limits=tuple(item['limits']),
                support=tuple(item['support']) + tuple(c for w in listed for c in w['support']))
        for index, item in enumerate(work):
            if index in enforced:
                continue
            reference = item['by_reference']
            yield dict(
                base, occurrence=f'{self.source}:work:{index}', part='operative',
                recipients=(item['recipients'],), cohort=(item['cohort'],) if item['cohort'] else (),
                prescribed_scope=(dict(work=item['work'], population=item['population']),),
                applies_prescription_of=(act_id(re.sub(r'\D', '', reference['number']), reference['year'])
                                         if reference else None),
                commencement_population=None, commencement_work=None, stated_term=None, term_literal=None,
                anchor=None, consequence=None, commitment=None, coercive_population=None,
                coercive_words=None, executor=None, limits=(), support=tuple(item['support']))


def apply_references(records):
    """Compose work applied by reference with the referenced order's own clause record.

    The recipients, cohort and scope stay this act's; the term, populations,
    executor, instrument and governing references are the referenced clause's.
    Work whose referenced order has no single clause record reaching the rule
    stays unknown. Nothing is composed from a filename, subject or number alone.
    """
    records = tuple(records)
    clauses = {}
    for record in records:
        if record['stated_term'] is not None and clause(record) is True:
            clauses.setdefault(record['instrument'], []).append(record)
    for record in records:
        reference = record.get('applies_prescription_of')
        if not reference:
            yield record
            continue
        found = clauses.get(reference, ())
        if len(found) != 1:
            yield record
            continue
        base = found[0]
        yield dict(base, occurrence=record['occurrence'], recipients=record['recipients'],
                   cohort=record['cohort'], prescribed_scope=record['prescribed_scope'],
                   applied_by=record['instrument'], applies_prescription_of=reference,
                   support=tuple(record['support']) + tuple(base['support']),
                   issues=tuple(record['issues']) + tuple(base['issues']),
                   request_sha256=(record['request_sha256'], base['request_sha256']))


def read_prescription(source, store, *, execute=False, model='opus', effort='medium', timeout=900):
    """Read one order's complete native text; replay unless `execute`."""
    response = read_native_text([source], store, prompt=PROMPT, schema=SCHEMA, model=model,
                                effort=effort, timeout=timeout, execute=execute)
    validate(response['reading'], page_texts(source, store))
    return PrescriptionReading(response)


def retained_prescription(request_id, store):
    response = read_retained(request_id, store)
    if response['request'].get('schema') != SCHEMA:
        raise ValueError('Retained request used another prescription contract')
    validate(response['reading'], page_texts(response['request']['sources'][0], store))
    return PrescriptionReading(response)


def clause(record):
    """The rule's clause predicate from the record: stated in the operative part, term from
    notification, and the Osservatorio's commitment to direct coercive removal."""
    if record['limits']:
        return Evaluation(None, needs=frozenset(f'reading limitation: {limit}' for limit in record['limits']))
    if record.get('applies_prescription_of') and record['stated_term'] is None:
        return Evaluation(None, needs=frozenset({f"the clause of {record['applies_prescription_of']}, "
                                                 'whose prescription this work applies'}))
    if record['part'] != 'operative' or record['stated_term'] is None:
        return False
    if record['anchor']['kind'] != 'notification' or record['commitment'] != 'commits':
        return False
    if not record['coercive_population'] or not record['executor']:
        return Evaluation(None, needs=frozenset({'coercive population and executor the clause names'}))
    return True


def c_result(snapshot, record, at, *, notification=None, evaluated_at=None, commencements=None,
             commencement_records_complete=False, governing_results=None, work_due=None,
             coercion_due=None, zone=None, calendar=None):
    """C's result for this record with whatever notice and commencement evidence is held.

    Nothing absent is supplied: no notification, commencement or lawful-dueness
    evidence means C's own unknown and its needs.
    """
    from cordon_c.bindings import merge_facts, noncommencement_facts
    row = snapshot.version(RULE, at)
    vid = row['provision_version_id']
    facts = {(vid, CLAUSE): clause(record)}
    for predicate, reading in ((WORK, work_due), (COERCE, coercion_due)):
        due = lawfully_due(snapshot, at, instrument=record['instrument'],
                           governing_references=record['governing_A_references'],
                           results=governing_results or {}, reading=reading)
        if due.truth is not None or due.needs:
            facts[(vid, predicate)] = due
    if notification is not None:
        facts[(vid, NOTICE)] = True
        if record['stated_term'] is not None:
            facts = merge_facts(facts, noncommencement_facts(
                snapshot, CLOCK, at, notification=notification, evaluated_at=evaluated_at,
                stated_term=record['stated_term'], qualifying_commencements=commencements or {},
                commencement_records_complete=commencement_records_complete, zone=zone, calendar=calendar))
    return evaluate(snapshot, RULE, at, facts)

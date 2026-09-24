"""`case-prescription` records read from each order's own operative text.

One record is one removal prescription an order's operative part addresses to its
recipients: the instrument, recipients or cohort, the stated commencement term as
printed, the commencement and coercive populations, the executor, the stated
consequence and the governing A references. Positions listed in annexes are not
read here.
"""
from dataclasses import dataclass
from datetime import date, datetime, time
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
# The Art. 21-ter notice conjunct is any_of(this Art. 21-bis communication predicate, the mass-publicity row).
COMMUNICATED = ('the communication to that recipient has been effected, including in the forms prescribed for '
                'notification to the unreachable in the cases provided by the code of civil procedure')


def personal_notice(snapshot, at, delivered):
    """The notice branch a held personal delivery (a PEC receipt, a served copy) gives one recipient."""
    vid = snapshot.version(RULE, at)['provision_version_id']
    return dict(notice={(vid, COMMUNICATED): True}, notice_instants={COMMUNICATED: delivered})


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


# A list label standing alone between spaces: a lettered or numbered point ("h)", "ii)", "4)") or a
# bullet or dash glyph. Page layout can print the next point's label inside a clause's words.
_LABELS = re.compile(r'(?<!\S)(?:[A-Za-z]{1,3}\)|\d{1,3}\)|[−•–—-])(?!\S)')


def _forms(text):
    """The words as printed, and the same words with standalone list labels set aside."""
    return (_plain(text), _plain(_LABELS.sub(' ', text or '')))


def page_texts(source, store):
    """The page text the transport supplied, by physical page number."""
    import pymupdf
    with pymupdf.open(blob_path(store, source)) as document:
        return {n: re.sub(r'[ \t]+', ' ', page.get_text(sort=True)) for n, page in enumerate(document, 1)}


def _parts(words):
    return [p for p in re.split(r'\s*(?:…|\.\.\.|\[…\])\s*', words or '') if p.strip()]


def on_page(quote, text):
    """Every ' … '-joined part of the quote occurs in the page text, whitespace aside.

    A part matches as printed, or with standalone list labels set aside in both
    the part and the page.
    """
    parts, page = _parts(quote), _forms(text)
    return bool(parts) and all(any(form in printed for form, printed in zip(_forms(p), page)) for p in parts)


def on_cited(words, pages, numbers):
    """Words occur on one cited page, or run from one cited page onto the next cited page.

    A clause printed across a page break has the running header and footer
    between its halves; each half must still occur on its own page. As on one
    page, standalone list labels may be set aside in both.
    """
    parts = _parts(words)
    texts = {n: _forms(pages[n]) for n in numbers}

    def found(part):
        for variant, piece in enumerate(_forms(part)):
            if any(piece in text[variant] for text in texts.values()):
                return True
            if any(_straddles(texts[n][variant], texts[n + 1][variant], piece[:k], piece[k:])
                   for n in texts if n + 1 in texts for k in range(1, len(piece))):
                return True
        return False
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


_ARTICLES = frozenset({'il', 'lo', 'la', 'i', 'gli', 'le', 'l', 'un', 'uno', 'una'})


def _meaning(text):
    """The words of a copied field compared for what they say: case, quotes, whitespace,
    punctuation and Italian articles (elided or not) aside."""
    words = re.findall(r'\w+', (text or '').translate(_QUOTES).lower())
    return tuple(w for w in words if w not in _ARTICLES)


def _clause_terms(record):
    """What a composed record takes from the referenced clause, compared by meaning, not by string."""
    return (tuple(_meaning(part) for part in record['stated_term']), record['anchor']['kind'],
            record['commitment'], _meaning(record['commencement_population']),
            _meaning(record['coercive_population']), _meaning(record['executor']))


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
        # Retained copies of the same order (a bulletin copy and a posted copy) that read the
        # same clause are one clause; copies that read it differently leave the work unknown.
        if len({_clause_terms(r) for r in found}) != 1:
            yield record
            continue
        base = found[0]
        yield dict(base, occurrence=record['occurrence'], recipients=record['recipients'],
                   cohort=record['cohort'], prescribed_scope=record['prescribed_scope'],
                   applied_by=record['instrument'], applies_prescription_of=reference,
                   support=tuple(record['support']) + tuple(base['support']),
                   issues=tuple(record['issues']) + tuple(base['issues']),
                   request_sha256=(record['request_sha256'], base['request_sha256']))


REREAD = ('A previous reading of this act was refused: {cause}. Read the act again from its supplied '
          'text. Cite every quotation on the physical page where it is printed, and copy every field '
          'from the pages its own citations name.')


LIMIT_REREAD = ('A previous reading of this act stated limits on its enforcement clauses: {limits}. A clause limit '
                'is only text in the clause itself that prevents reading one of the fields the clause supplies: the '
                'term, its anchor, the commitment, the coercive population or the executor. A misprint or an '
                'incomplete passage that leaves those fields readable from the clause\'s own words is not a limit; '
                'name it under issues. Read the act again from its supplied text.')


def stated_limits(reading):
    """The clause limits a reading states, by clause, as one cause for a limit reread; None when none."""
    limits = [f'clause {index}: ' + ' | '.join(item['limits'])
              for index, item in enumerate(reading.values['enforcement_clauses']) if item['limits']]
    return '; '.join(limits) or None


def read_prescription(source, store, *, execute=False, model='opus', effort='medium', timeout=900,
                      refused=None, limited=None):
    """Read one order's complete native text; replay unless `execute`.

    `refused` names the validation cause of a refused reading. It makes one bounded,
    source-only reread whose request states that cause; the refused answer is not supplied.
    `limited` names the clause limits a validated reading stated (`stated_limits`). It
    makes one bounded, source-only reread whose request states them and what a clause
    limit is; a limit the reread still states stands.
    """
    prompt = PROMPT if refused is None else PROMPT + '\n' + REREAD.format(cause=refused) + '\n'
    if limited is not None:
        prompt += '\n' + LIMIT_REREAD.format(limits=limited) + '\n'
    response = read_native_text([source], store, prompt=prompt, schema=SCHEMA, model=model,
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


WITHHOLDING = ('corrects', 'replaces', 'revokes', 'suspends', 'withdraws')


def order_dueness(record, at, *, closures=(), stated_changes=(), within_closed_scope=None):
    """Lawful dueness of the record's work and coercion as the order itself and held acts state it.

    The order's operative part prescribes the work to its recipients and names the
    population for coercion; that is the reading. `closures` are the held court
    dispositions (`judgments.liveness_closures`), each from its publication:

    - an annulment closes the order for a recipient within the applicants' scope
      (`within_closed_scope`); outside it the order stays live; while the recipient
      is not identified the reading is unknown and names the scope. An annulment
      stated without a limit closes it for the applicants; whether it reaches other
      recipients of the order is A's question and stays named.
    - an interim suspension leaves the reading unknown, naming the end it states,
      because no later disposition of the ricorso is held.
    - a challenge the court ended with a stated reason (a later act superseding the
      order) leaves the reading unknown, naming the court's words.

    A held act that states it corrects, replaces, revokes, suspends or withdraws the
    order, as a whole or in part, and that no A row records, leaves the reading unknown
    and names that act and the words stating what changes. Returns
    (work, coercion), each a bool or an unknown Evaluation.
    """
    if record['part'] != 'operative' or not record['prescribed_scope']:
        return None, None
    needs = set()
    for closure in closures:
        if closure['since'] is None or at < closure['since']:
            continue
        decision = closure['decision']
        name = f"TAR {decision['kind']} {decision['number']}"
        applicants = f" (applicants: {closure['applicants']})" if closure['applicants'] else ''
        if closure['effect'] == 'suspended':
            needs.add(f"whether the interim suspension by {name} still holds and for whom: "
                      f"{closure['outcome']}; no later disposition of ricorso {decision['register']} is held"
                      + applicants)
        elif closure['effect'] == 'ended-with-stated-reason':
            needs.add(f"the effect on this order of what {name} states: " + ' … '.join(closure['stated_reason']))
        elif within_closed_scope:
            return False, False
        elif closure['scope'] == 'whole-act':
            needs.add(f"whether {name}'s annulment of the act, stated without limit, reaches recipients "
                      f"other than the applicants{applicants}")
        elif within_closed_scope is None:
            reach = '; '.join(filter(None, (closure['dispositive_scope'], *closure['stated_scope'])))
            needs.add(f"whether this recipient is within the scope {name} annuls: {reach}{applicants}")
    recorded = {reference.split(':')[0] for reference in record['governing_A_references']}
    for change in stated_changes:
        if change['relationship'] in WITHHOLDING and change['from'] not in recorded:
            extent = ' (in part)' if change.get('extent') == 'part' else ''
            needs.add(f"an A row for {change['from']}'s stated {change['relationship']}{extent} of "
                      f"{record['instrument']}: {change['affected_payload']}")
    if needs:
        unknown = Evaluation(None, needs=frozenset(needs))
        return unknown, (unknown if record['coercive_population'] else None)
    return True, (True if record['coercive_population'] else None)


def c_result(snapshot, record, at, *, notice=None, notice_instants=None, evaluated_at=None, commencements=None,
             commencement_records_complete=False, governing_results=None, work_due=None,
             coercion_due=None, closures=(), stated_changes=(), within_closed_scope=None,
             zone=None, calendar=None):
    """C's result for this record with whatever notice and commencement evidence is held.

    `notice` holds the facts of the notice branches (the communication predicate,
    or the mass-publicity row's facts from `mass_publicity_facts`), and
    `notice_instants` each branch's instant; C's `notice_instant` picks the
    earliest instant among the branches A finds true. Lawful dueness is the
    order's own reading (`order_dueness`) unless the caller supplies one, held to
    the governing A rows by `lawfully_due`. Nothing absent is supplied: no notice
    or commencement evidence means C's own unknown and its needs.
    """
    facts, _ = _c_facts(snapshot, record, at, notice=notice, notice_instants=notice_instants,
                        evaluated_at=evaluated_at, commencements=commencements,
                        commencement_records_complete=commencement_records_complete,
                        governing_results=governing_results, work_due=work_due, coercion_due=coercion_due,
                        closures=closures, stated_changes=stated_changes,
                        within_closed_scope=within_closed_scope, zone=zone, calendar=calendar)
    return evaluate(snapshot, RULE, at, facts)


def _c_facts(snapshot, record, at, *, notice, notice_instants, evaluated_at, commencements,
             commencement_records_complete, governing_results, work_due, coercion_due, closures, stated_changes,
             within_closed_scope, zone, calendar):
    """The facts `c_result` evaluates, and the instant C's `notice_instant` returned (None when none)."""
    from cordon_c.bindings import merge_facts, noncommencement_facts, notice_instant
    notification = None
    row = snapshot.version(RULE, at)
    vid = row['provision_version_id']
    facts = {(vid, CLAUSE): clause(record)}
    own_work, own_coercion = order_dueness(record, at, closures=closures, stated_changes=stated_changes,
                                           within_closed_scope=within_closed_scope)
    for predicate, reading in ((WORK, own_work if work_due is None else work_due),
                               (COERCE, own_coercion if coercion_due is None else coercion_due)):
        stated = reading if isinstance(reading, Evaluation) else None
        due = lawfully_due(snapshot, at, instrument=record['instrument'],
                           governing_references=record['governing_A_references'],
                           results=governing_results or {}, reading=True if stated is not None else reading)
        if stated is not None and due.truth is not None:
            due = stated
        elif stated is not None:
            due = Evaluation(None, needs=due.needs | stated.needs)
        if due.truth is not None or due.needs:
            facts[(vid, predicate)] = due
    if notice:
        facts = merge_facts(facts, notice)
        notification = notice_instant(snapshot, RULE, at, facts, zone=zone, instants=notice_instants or {})
        if notification is not None and record['stated_term'] is not None:
            facts = merge_facts(facts, noncommencement_facts(
                snapshot, CLOCK, at, notification=notification, evaluated_at=evaluated_at,
                stated_term=record['stated_term'], qualifying_commencements=commencements or {},
                commencement_records_complete=commencement_records_complete, zone=zone, calendar=calendar))
    return facts, notification


# Supplied Osservatorio records (`osservatorio-records`): the operator's delivery, commencement,
# removal and history records, and posting records, as a list of JSON objects.
MASS = 'IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route'
_MASS_GROUND = 'the act states its own ground for reaching its recipients by public posting'
_MASS_ANNULLED = 'a court has annulled the act on its stated ground for public posting'
_COMMON = {'record', 'kind', 'order', 'source', 'selector', 'reading'}
_KINDS = {
    # A delivery to the recipient the record names, with the works (parcels or plants) it names for them.
    'personal-delivery': {'recipient', 'occurred', 'works'},
    # A posting of the order: it names no recipient; `complete` says the record states the whole interval.
    'posting': {'publisher', 'start', 'end', 'complete'},
    # Performance on the work the record names, by whoever performed it.
    'commencement': {'work', 'occurred'},
    'removal': {'work', 'occurred'},
    # A stated bounded complete history of performance on one work.
    'history': {'work', 'complete_from', 'complete_through'},
}


def _moment(text, *, day_end=None):
    """A printed ISO date stays a date; an ISO instant must carry its offset. `day_end` closes a date."""
    if text is None:
        return None
    if len(text) == 10:
        day = date.fromisoformat(text)
        return day if day_end is None else datetime.combine(day, datetime.max.time(), day_end)
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise ValueError(f'A supplied instant needs its offset: {text}')
    return moment


def _work(value):
    """A work as the record prints it: comune, foglio and particella, or a plant identifier. Never normalized."""
    if not isinstance(value, dict) or set(value) not in ({'comune', 'foglio', 'particella'}, {'plant'}):
        raise ValueError(f'A work is a printed comune, foglio and particella, or a plant identifier: {value}')
    if not all(isinstance(v, str) and v.strip() for v in value.values()):
        raise ValueError(f'A work prints every part: {value}')
    return tuple(sorted(value.items()))


def supplied_records(entries):
    """Validate supplied records as the existing typed inputs; refuse anything else.

    Each record becomes an `AdministrativeEvent` whose `Support` cites its controlled
    source. A record carries only its kind's fields and an optional `fixture` mark
    (test records): no order-text predicate, notification instant or completeness
    flag can ride along. A posting names no recipient, so it never reaches the
    personal-communication input.
    """
    from .events import AdministrativeEvent
    from .evidence import Support
    records = []
    for entry in entries:
        kind = entry.get('kind')
        if kind not in _KINDS:
            raise ValueError(f'Unsupported supplied record kind: {kind}')
        fields = set(entry) - {'fixture'}
        expected = _COMMON | _KINDS[kind]
        if fields != expected:
            raise ValueError(f"Record {entry.get('record')} ({kind}) differs in {sorted(fields ^ expected)}")
        support = Support(entry['source'], entry['selector'], entry['reading'])
        recipient = entry.get('recipient')
        if kind == 'personal-delivery':
            occurred = _moment(entry['occurred'])
            works = tuple(dict.fromkeys(_work(w) for w in entry['works']))
        elif kind == 'posting':
            occurred, works = _moment(entry['start']), ()
            if not isinstance(entry['complete'], bool):
                raise ValueError('A posting record states whether its interval is whole')
        elif kind == 'history':
            occurred, works = _moment(entry['complete_from']), (_work(entry['work']),)
        else:
            occurred, works = _moment(entry['occurred']), (_work(entry['work']),)
        event = AdministrativeEvent(entry['record'], kind, entry['order'], recipient or None, occurred, support)
        records.append(dict(entry, event=event, works=works, fixture=bool(entry.get('fixture'))))
    return records


def _periods(snapshot, basis):
    """The period the order's publicity forms print, when they all print one (PR #15's reading, unchanged)."""
    words = snapshot.conventions['clock.unit_words']
    stated = [f['duration'] for f in basis['forms'] if f['duration']]
    meant = {(re.sub(r'\D', '', d['number'].split('(')[0]), words.get(' '.join(d['unit_word'].lower().split())))
             for d in stated}
    if len(meant) != 1 or None in next(iter(meant)):
        return None
    return stated[0]['number'], stated[0]['unit_word']


def supplied_publicity(snapshot, at, basis, posting, *, annulled, evaluated_at, zone):
    """The mass-publicity branch's facts and notice day from the order's own basis and one supplied posting."""
    from cordon_c.bindings import mass_publicity_facts
    from cordon_c.core import Evaluation as _E
    vid = snapshot.version(MASS, at)['provision_version_id']

    def unsupplied(text):
        return _E(None, needs=frozenset({f'predicate: {vid} :: {text}'}))
    return mass_publicity_facts(
        snapshot, at, ground_stated=True if basis['stated_ground'] else unsupplied(_MASS_GROUND),
        annulled_on_ground=unsupplied(_MASS_ANNULLED) if annulled is None else annulled,
        posting_start=posting['event'].occurred,
        postings={posting['publisher']: (posting['event'].occurred, _moment(posting['end']))},
        postings_complete=posting['complete'], stated_period=_periods(snapshot, basis),
        evaluated_at=evaluated_at, zone=zone)


def recipient_results(snapshot, record, at, supplied, *, evaluated_at, zone, calendar, basis=None,
                      publicity_annulment=None, **dueness):
    """C's result per (clause, recipient named by a supplied record), beside the clause's cohort result.

    The cohort result is `c_result` on cohort evidence only; no supplied record
    reaches it. For each recipient a delivery record names, the caller supplies
    events only: the delivery on the communication predicate, and a supplied
    posting through the mass-publicity row with the order's own basis (PR #15's
    notice-route reading, unchanged). C's `notice_instant` picks the instant.
    Commencement and removal count by the work the record prints, for every
    recipient a supplied record obliges to that work; completeness holds for a
    recipient only when every such work has a stated history covering the order's
    adoption through the evaluation. Nothing absent is filled: what cannot be joined
    or supplied is reported. `publicity_annulment` is the held court fact on the
    act's stated ground, when one is held; otherwise it stays unknown.
    """
    act = record.get('applied_by') or record['instrument']
    records = supplied_records(supplied)
    if any(r['order'] != act for r in records):
        raise ValueError(f'A supplied record names another order than {act}')
    reported, deliveries, obliged, performed, histories, undated = [], {}, {}, {}, {}, {}
    for r in records:
        if r['kind'] == 'personal-delivery':
            if not r['recipient'] or not r['recipient'].strip():
                reported.append(dict(record=r['record'], cause='names no recipient'))
                continue
            deliveries.setdefault(r['recipient'], {}).setdefault(r['event'].occurred, []).append(r['record'])
            obliged.setdefault(r['recipient'], set()).update(r['works'])
        elif r['kind'] in ('commencement', 'removal') and not isinstance(r['event'].occurred, datetime):
            # C compares performance instants with the deadline; a day alone is not upgraded.
            undated.setdefault(r['works'][0], []).append(r['record'])
            reported.append(dict(record=r['record'], work=dict(r['works'][0]),
                                 cause='performance dated by day only; its work stays without a complete history'))
        elif r['kind'] in ('commencement', 'removal'):
            performed.setdefault(r['works'][0], {})[r['record']] = r['event'].occurred
        elif r['kind'] == 'history':
            histories.setdefault(r['works'][0], []).append(r)
    postings = [r for r in records if r['kind'] == 'posting']
    posting = postings[0] if len(postings) == 1 else None
    if len(postings) > 1:
        reported.append(dict(records=[p['record'] for p in postings],
                             cause='more than one posting record; the mass-publicity branch is not supplied'))
    if posting and basis is None:
        reported.append(dict(record=posting['record'], cause='no notice-route reading of the order; the '
                                                                  'mass-publicity branch is not supplied'))
        posting = None
    everyone = set().union(*obliged.values()) if obliged else set()
    for work in sorted(set(performed) | set(histories) | set(undated)):
        if work not in everyone:
            names = (sorted(performed.get(work, {})) + sorted(undated.get(work, ()))
                     + sorted(h['record'] for h in histories.get(work, ())))
            reported.append(dict(records=names, work=dict(work),
                                 cause='no supplied record obliges a recipient to this work as printed'))
    adopted = datetime.combine(date.fromisoformat(record['adopted']), time(), zone)

    def covers(history):
        """The history is stated from the order's adoption (or earlier) through the evaluation time."""
        start = history['event'].occurred
        start = start if isinstance(start, datetime) else datetime.combine(start, time(), zone)
        end = _moment(history['complete_through'], day_end=zone)
        return start <= adopted and end >= evaluated_at

    vid = snapshot.version(RULE, at)['provision_version_id']
    common = dict(dueness, evaluated_at=evaluated_at, zone=zone, calendar=calendar)
    results = {}
    for recipient in sorted(deliveries):
        instants = deliveries[recipient]
        notice, notice_instants = {}, {}
        if len(instants) == 1:
            notice[(vid, COMMUNICATED)] = True
            notice_instants[COMMUNICATED] = next(iter(instants))
        else:
            reported.append(dict(recipient=recipient, records=sorted(n for v in instants.values() for n in v),
                                 cause='deliveries at different instants; the personal branch is not supplied'))
        if posting:
            facts, day = supplied_publicity(snapshot, at, basis, posting, annulled=publicity_annulment,
                                    evaluated_at=evaluated_at, zone=zone)
            notice.update(facts)
            notice_instants[MASS] = day
        works = sorted(obliged.get(recipient, ()))
        commencements = {name: moment for work in works for name, moment in performed.get(work, {}).items()}
        complete = bool(works) and all(any(covers(h) for h in histories.get(w, ())) and w not in undated
                                       for w in works)
        facts, notification = _c_facts(snapshot, record, at, notice=notice or None, notice_instants=notice_instants,
                                       commencements=commencements, commencement_records_complete=complete,
                                       **_dueness_defaults(common))
        results[recipient] = dict(result=evaluate(snapshot, RULE, at, facts), notification=notification,
                                  works=[dict(w) for w in works], commencements=commencements,
                                  commencement_records_complete=complete,
                                  records=sorted(n for v in instants.values() for n in v),
                                  fixture=any(r['fixture'] for r in records))
    return dict(cohort=c_result(snapshot, record, at, **dueness), recipients=results, reported=reported)


def _dueness_defaults(common):
    keys = ('evaluated_at', 'governing_results', 'work_due', 'coercion_due', 'closures', 'stated_changes',
            'within_closed_scope', 'zone', 'calendar')
    defaults = dict(governing_results=None, work_due=None, coercion_due=None, closures=(), stated_changes=(),
                    within_closed_scope=None)
    unknown = set(common) - set(keys)
    if unknown:
        raise TypeError(f'recipient_results takes no {sorted(unknown)}')
    return {**defaults, **common}

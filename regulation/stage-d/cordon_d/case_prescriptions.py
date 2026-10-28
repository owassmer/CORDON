"""`case-prescription` records read from each order's own operative text.

One record is one removal prescription an order's operative part addresses to its
recipients: the instrument, recipients or cohort, the stated commencement term as
printed, the commencement and coercive populations, the executor, the stated
consequence and the governing A references. Positions listed in annexes are read
by `annex_positions`, only for the orders an in-force governing row names with a
whole-or-part effect; a record placed there carries its position in `recipients`.
"""
from dataclasses import dataclass, replace
from datetime import date, datetime, time
from pathlib import Path
import re

from cordon_c.core import Evaluation, MissingInput, evaluate
from .document_subscription import read_native_text, read_retained
from .prescriptions import COERCE, IN_PART, NOT_DUE, WORK, lawfully_due
from .removal_events import act_id
from .store import blob_path

RULE = 'IT-L241-A21TER:Art.21-ter(1):stated-term-coercive-direction'
CLOCK = 'B-CLK-IT-L241-21TER-stated-commencement-term'
CLAUSE = ('the operative prescription governing this recipient states in its operative part a commencement '
          'term running from notification and commits the Osservatorio to direct coercive removal on '
          'noncommencement')
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


def _decided_in_a(reason, record):
    """Whether an A row governing the record already decides what a court's stated reason states.

    True where the reason cites at least one act other than the order, read as `held_acts.printed_identities`
    reads a printed act identity (a designator with number and year, "DDS n. 18/2024", or a number with
    its date, "n. 127 del 17.11.2022"), and every act so cited is the instrument of an A row governing the
    record (`governing_A_references`): A records that act's effect on this order, so a moot ruling adds
    nothing (owner ruling, 2026-10-28). Otherwise the court's words stay a need: whether an act A does
    not record ended the order is a question of legal meaning, not D's (TAR Bari 1007/2023 on DDS
    119/2022). A number read with a date that is no act (a ricorso, a bulletin) keeps the need. The
    residual is an act that reader does not read: a later number in a list under one designator ("DDS
    n. 18/2024 e n. 127/2022"), an act with no number (a D.G.R., a law, words alone), or another office's
    act printed as "D.D. n/year", which `act_id` reads as the Osservatorio's. Such an act reaches C only
    as a held act's own stated change (`stated_changes`).
    """
    from .held_acts import printed_identities
    cited = {act_id(number, year) for number, year, _, _ in printed_identities(' '.join(reason))}
    later = cited - {record['instrument']}
    recorded = {reference.split(':')[0] for reference in record['governing_A_references']}
    return bool(later) and later <= recorded


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
      order) leaves the reading unknown, naming the court's words, unless an A row
      governing the record already decides what the reason states (`_decided_in_a`):
      the reason cites, by act type, at least one act other than the order, and each
      act it so cites is the instrument of an A row governing the record. A moot ruling
      annuls nothing, so the A row decides (owner ruling, 2026-10-28, TAR Bari 387,
      383 and 384/2026 on DDS 18/2024).

    A held act that states it corrects, replaces, revokes, suspends or withdraws the
    order, as a whole or in part, and that no A row records, leaves the reading unknown
    and names that act and the words stating what changes. A stated change counts only
    from its stating act's adoption (`adopted`, as the act's reading prints it); one
    whose act has no readable adoption date counts on every date. Returns
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
            if not _decided_in_a(closure['stated_reason'], record):
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
        if change.get('adopted') and at < date.fromisoformat(change['adopted']):
            continue
        if change['relationship'] in WITHHOLDING and change['from'] not in recorded:
            extent = ' (in part)' if change.get('extent') == 'part' else ''
            needs.add(f"an A row for {change['from']}'s stated {change['relationship']}{extent} of "
                      f"{record['instrument']}: {change['affected_payload']}")
    if needs:
        unknown = Evaluation(None, needs=frozenset(needs))
        return unknown, (unknown if record['coercive_population'] else None)
    return True, (True if record['coercive_population'] else None)


def annex_position(record):
    """The annex position a record carries in its recipient positions field (`annex_positions`), or None
    when its recipients are only the order's printed recipient class."""
    positions = [r for r in record.get('recipients') or () if isinstance(r, dict) and r.get('annex')]
    return positions[0] if len(positions) == 1 else None


def c_result(snapshot, record, at, *, evaluated_at, notice=None, notice_instants=None, commencements=None,
             commencement_records_complete=False, governing_results=None, work_due=None,
             coercion_due=None, closures=(), stated_changes=(), within_closed_scope=None,
             zone=None, calendar=None):
    """C's result for this record with whatever notice and commencement evidence is held.

    `notice` holds the facts of the notice branches (the communication predicate,
    or the mass-publicity row's facts from `mass_publicity_facts`), and
    `notice_instants` each branch's instant; C's `notice_instant` picks the
    earliest instant among the branches A finds true. Lawful dueness is the
    order's own reading (`order_dueness`) unless the caller supplies one, held to
    the governing A rows by `lawfully_due` per predicate: `governing_results` is
    keyed by (row, predicate), and whether the record carries an annex position
    (`annex_position`) is passed. The order's own stated reading (a court closure or a
    stated change) replaces only a True from `lawfully_due`: every such outcome only
    withholds, so a False keeps its row provisions (SPEC). Nothing absent is supplied:
    no notice or commencement evidence means C's own unknown and its needs.
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
    from .evidence import instant
    if type(at) is not date:
        raise TypeError('The run states its evaluation date')
    instant(evaluated_at)  # the run's knowledge cutoff; never the machine clock or None
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
                           results=governing_results or {}, reading=True if stated is not None else reading,
                           predicate=predicate, positioned=annex_position(record) is not None,
                           cohort=record.get('cohort') or ())
        if stated is not None and due.truth is True:
            due = stated
        elif stated is not None and due.truth is None:
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
# removal and history records, as a list of JSON objects. Postings are public records (PR #15's route).
_SUPPORT = {'record', 'kind', 'source', 'selector', 'reading'}
_COMMON = _SUPPORT | {'order'}
_KINDS = {
    # The delivery receipt of the order to the recipient the record names; `occurred` is the delivery
    # instant, never the acceptance receipt's. `works` (parcels or plants) is the operator's standing
    # assertion of what that recipient is obliged to.
    'personal-delivery': {'recipient', 'occurred', 'works'},
    # Performance on the work the record names, by whoever performed it.
    'commencement': {'work', 'occurred'},
    'removal': {'work', 'occurred'},
    # A stated bounded complete history of performance on one work.
    'history': {'work', 'complete_from', 'complete_through'},
}
# The landscape proceeding (D.lgs. 19/2021 Art. 33(1), D.lgs. 42/2004 Art. 146), as the Osservatorio's file
# holds it (`cordon_d.landscape`). `document` is the proceeding's own document as printed (the request and its
# protocol, the transmission, the opinion, the decision). `plants` is the plants the record names, one group of
# printed identifiers per plant: one request or decision can cover several trees. There is no requirement kind:
# Art. 33(1) itself names the plants that need authorization.
_LANDSCAPE = _SUPPORT | {'document', 'plants', 'occurred'}
LANDSCAPE_KINDS = {
    # `complete`: true where the record states the application complete, false where it states it incomplete,
    # null where it states neither. `recipient`: the authority it was lodged with, as printed (null: not printed).
    'landscape-lodging': {'complete', 'recipient'},
    # The superintendent's receipt of the acts (Art. 146(8)), not a notice that they were sent (146(7)).
    # `complete` and `recipient` (the superintendent who received them) as for the lodging.
    'landscape-acts-received': {'complete', 'recipient'},
    # `route` as printed; `resolved` as the record states it.
    'landscape-opinion-route': {'route', 'resolved'},
    # `intervention` as printed and its kind; `procedure` as printed; `conditions` verbatim; `issuer`, the
    # authority that decided, as printed (null: not printed). D judges no competence.
    'landscape-decision': {'intervention', 'intervention_kind', 'procedure', 'outcome', 'conditions', 'issuer'},
}
_FAMILIES = {'order': (_COMMON, _KINDS), 'landscape': (_LANDSCAPE, LANDSCAPE_KINDS)}
# A plant identifier as a record prints it: the monitoring reference (ID / ID_CAMPIONE), the register key (COD),
# the census card or tag with its comune, or a parcel. Never normalized here.
IDENTIFIER_FORMS = ({'sample'}, {'cod'}, {'card', 'comune'}, {'comune', 'foglio', 'particella'})


def _moment(text):
    """A printed ISO date stays a date; an ISO instant must carry its offset."""
    if text is None:
        return None
    if len(text) == 10:
        return date.fromisoformat(text)
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


def _identifier(value):
    """A plant identifier as the record prints it (`IDENTIFIER_FORMS`)."""
    if not isinstance(value, dict) or set(value) not in IDENTIFIER_FORMS:
        raise ValueError(f'A plant identifier is a printed sample, COD, card and comune, or parcel: {value}')
    if not all(isinstance(v, str) and v.strip() for v in value.values()):
        raise ValueError(f'A plant identifier prints every part: {value}')
    return tuple(sorted(value.items()))


def _printed_or_null(value):
    return value is None or (isinstance(value, str) and bool(value.strip()))


def _landscape(entry):
    """The values of a landscape record; returns the plants it names, each a tuple of its printed identifiers."""
    name, kind = entry['record'], entry['kind']
    groups = entry['plants']
    if not isinstance(groups, list) or not groups or not all(isinstance(g, list) and g for g in groups):
        raise ValueError(f'Record {name} ({kind}) names its plants as a list of groups, each the identifiers it '
                         'prints for one plant')
    if not isinstance(entry['document'], str) or not entry['document'].strip():
        raise ValueError(f'Record {name} ({kind}) names no document')
    if kind in ('landscape-lodging', 'landscape-acts-received'):
        if entry['complete'] is not None and type(entry['complete']) is not bool:
            raise ValueError(f'Record {name}: complete is what the record states, true, false or null')
        if not _printed_or_null(entry['recipient']):
            raise ValueError(f'Record {name}: the recipient as printed, or null where none is printed')
    if kind == 'landscape-opinion-route' and (type(entry['resolved']) is not bool
                                             or not isinstance(entry['route'], str) or not entry['route'].strip()):
        raise ValueError(f'Record {name}: an opinion route prints its route and states whether it is resolved')
    if kind == 'landscape-decision':
        if entry['outcome'] not in ('granted', 'granted-with-conditions', 'denied'):
            raise ValueError(f"Record {name}: outcome {entry['outcome']!r} is not granted, granted-with-conditions "
                             'or denied')
        if entry['intervention_kind'] not in ('removal', 'replanting-only', 'other'):
            raise ValueError(f"Record {name}: intervention_kind {entry['intervention_kind']!r} is not removal, "
                             'replanting-only or other')
        if not all(isinstance(entry[k], str) and entry[k].strip() for k in ('intervention', 'procedure')):
            raise ValueError(f'Record {name}: a decision prints its intervention and procedure')
        conditions = entry['conditions']
        if not isinstance(conditions, list) or not all(isinstance(c, str) and c.strip() for c in conditions):
            raise ValueError(f'Record {name}: conditions are the decision\'s words, verbatim')
        if bool(conditions) != (entry['outcome'] == 'granted-with-conditions'):
            raise ValueError(f"Record {name}: a {entry['outcome']} decision with {len(conditions)} conditions")
        if not _printed_or_null(entry['issuer']):
            raise ValueError(f'Record {name}: the issuer as printed, or null where none is printed')
    return tuple(tuple(dict.fromkeys(_identifier(p) for p in group)) for group in groups)


def supplied_records(entries, family='order'):
    """Validate supplied records as the existing typed inputs; refuse anything else.

    Each record becomes an `AdministrativeEvent` whose `Support` cites its controlled
    source. A record carries only its kind's fields and an optional `fixture` mark
    (test records): no order-text predicate, notification instant or completeness
    flag can ride along. A personal delivery is the delivery receipt only; an
    acceptance receipt is not supplied as one. `family` is the kinds the caller
    takes: 'order' (a removal order's records) or 'landscape' (a plant's landscape
    proceeding, `cordon_d.landscape`); a record of another kind is refused.
    """
    from .events import AdministrativeEvent
    from .evidence import Support
    common, kinds = _FAMILIES[family]
    records = []
    for entry in entries:
        kind = entry.get('kind')
        if kind not in kinds:
            raise ValueError(f'Unsupported supplied record kind for {family} records: {kind}')
        fields = set(entry) - {'fixture'}
        expected = common | kinds[kind]
        if fields != expected:
            raise ValueError(f"Record {entry.get('record')} ({kind}) differs in {sorted(fields ^ expected)}")
        support = Support(entry['source'], entry['selector'], entry['reading'])
        if family == 'landscape':
            identifiers = _landscape(entry)
            event = AdministrativeEvent(entry['record'], kind, entry['document'], entry.get('recipient'),
                                        _moment(entry['occurred']), support)
            records.append(dict(entry, event=event, identifiers=identifiers, fixture=bool(entry.get('fixture'))))
            continue
        recipient = entry.get('recipient')
        if kind == 'personal-delivery':
            occurred = _moment(entry['occurred'])
            works = tuple(dict.fromkeys(_work(w) for w in entry['works']))
        elif kind == 'history':
            occurred, works = _moment(entry['complete_from']), (_work(entry['work']),)
        else:
            occurred, works = _moment(entry['occurred']), (_work(entry['work']),)
        event = AdministrativeEvent(entry['record'], kind, entry['order'], recipient or None, occurred, support)
        records.append(dict(entry, event=event, works=works, fixture=bool(entry.get('fixture'))))
    return records


def admitted_records(supplied, act, *, evaluated_at, permitted_controlled_sources, zone, family='order'):
    """The supplied records of `act` the run admits, split by the stated grant: (granted, ungranted).

    Supplied records are controlled sources (`osservatorio-records`); the grant is a
    stated frozenset, never defaulted. They carry no capture time, so their own dates
    bound them: a record whose `occurred`, `complete_from` or `complete_through` is
    later than `evaluated_at` (the run's knowledge cutoff) was not held at the cutoff,
    and the set is refused, granted or not, naming the record and field. Each
    ungranted item is (record, need) with the need 'authorized evidence for …'.
    `recipient_results` and the position path of `read_prescriptions.per_recipient`
    both apply this to an order's records; `landscape.landscape_results` applies it to
    the landscape proceeding's (`family` 'landscape', `act` None: they name no order).
    """
    if not isinstance(permitted_controlled_sources, frozenset):
        raise TypeError('Evaluation requires the run to state its controlled-source grant')
    records = supplied_records(supplied, family)
    if family == 'landscape' and act is not None:
        raise ValueError(f'Landscape records name no order: {act}')
    if family == 'order' and any(r['order'] != act for r in records):
        raise ValueError(f'A supplied record names another order than {act}')
    today = evaluated_at.astimezone(zone).date()
    for r in records:
        for field in ('complete_from', 'complete_through') if r['kind'] == 'history' else ('occurred',):
            moment = _moment(r[field])
            if moment > (evaluated_at if isinstance(moment, datetime) else today):
                raise ValueError(f"Record {r['record']} ({r['kind']}) states {field} {r[field]}, "
                                 f'later than the evaluation at {evaluated_at.isoformat()}')
    granted = [r for r in records if r['source'] in permitted_controlled_sources]
    ungranted = [(r, _unauthorized(r, act)) for r in records if r['source'] not in permitted_controlled_sources]
    return granted, ungranted


def _printed(name):
    """A printed owner or recipient name as a line prints it: runs of whitespace are one space."""
    return re.sub(r'\s+', ' ', name or '').strip()


def _on_position(work, position):
    """Whether a work, as a record prints it, is on an annex position: its foglio and particella among the
    parcels the position prints, or its plant among the listed infected plants. The position prints no
    comune, so the comune is not compared."""
    work = dict(work)
    if 'plant' in work:
        return work['plant'] in (position.get('listed_infected_plants') or ())
    return any(p['foglio'] == work['foglio'] and p['particella'] == work['particella']
               for p in position.get('parcels') or ())


def position_attachments(records, supplied):
    """Join supplied records to the position records of one order's clause (`annex_position`).

    A personal delivery joins the one position whose printed owner is the recipient the
    delivery names (whitespace aside) and which prints every work the delivery names.
    A delivery that names no recipient, matches no position, or matches several is
    unattached with its cause; nothing is defaulted. Commencement, removal and history
    records count by the work they print, so each attaches to every position printing
    that work to which a delivery joined (the co-holder rule); one whose work is on no
    position, or on none a delivery joined, is unattached with its cause.
    Returns ({occurrence: [supplied entries]}, [unattached]).
    """
    checked = supplied_records(supplied)
    placed = [(r['occurrence'], annex_position(r)) for r in records]
    attached, unattached, joined = {}, [], set()
    for entry, r in zip(supplied, checked):
        if r['kind'] != 'personal-delivery':
            continue
        name = _printed(r['recipient'])
        if not name:
            unattached.append(dict(record=r['record'], cause='names no recipient'))
            continue
        named = [(o, p) for o, p in placed if p.get('owner') and _printed(p['owner']) == name]
        found = [o for o, p in named if all(_on_position(w, p) for w in r['works'])]
        if len(found) == 1:
            attached.setdefault(found[0], []).append(entry)
            joined.add(found[0])
        elif found:
            unattached.append(dict(record=r['record'], positions=found,
                                   cause=f"matches {len(found)} annex positions printing owner '{name}'"))
        elif named:
            off = [dict(w) for w in r['works'] if not all(_on_position(w, p) for _, p in named)]
            unattached.append(dict(record=r['record'], works=off,
                                   cause=f"the annex position printing owner '{name}' prints no such work"))
        else:
            unattached.append(dict(record=r['record'],
                                   cause=f"no annex position of this order prints owner '{name}'"))
    for entry, r in zip(supplied, checked):
        if r['kind'] == 'personal-delivery':
            continue
        on = [o for o, p in placed if _on_position(r['works'][0], p)]
        reached = [o for o in on if o in joined]
        for occurrence in reached:
            attached.setdefault(occurrence, []).append(entry)
        if not reached:
            unattached.append(dict(record=r['record'], work=dict(r['works'][0]),
                                   cause=('no supplied delivery joins an annex position printing this work' if on
                                          else 'no annex position of this order prints this work')))
    return attached, unattached


def still_due_share(snapshot, at, position, governing_results):
    """At an annex position whose governing result for the work is LAWFULLY_DUE_IN_PART: the rows so
    resolving, the latest effective date among them, and the obliged works (the position's listed
    infected plants, each with the parcel holding it). None elsewhere."""
    rows = sorted({sid for (sid, predicate), result in (governing_results or {}).items()
                   if predicate == WORK and result.effect == IN_PART}) if position else []
    if not rows:
        return None
    standing = position.get('listed_infected_plant_parcels') or ()
    if {s['plant'] for s in standing} != set(position.get('listed_infected_plants') or ()):
        raise ValueError('An annex position lists infected plants without the parcel holding each')
    return dict(rows=rows, since=max(date.fromisoformat(snapshot.version(sid, at)['effective_from'])
                                     for sid in rows),
                plants={s['plant']: (s['foglio'], s['particella']) for s in standing})


def _still_due(work, share):
    """The still-due works a work, as a record prints it, names: the listed infected plant it names, or
    every listed infected plant on the parcel it names. Empty where it names only a withdrawn work."""
    work = dict(work)
    if 'plant' in work:
        return [_work(work)] if work['plant'] in share['plants'] else []
    return [_work(dict(plant=p)) for p, held in sorted(share['plants'].items())
            if held == (work['foglio'], work['particella'])]


def position_class(governing_results):
    """What the position's governing results leave due of the work: ('not due', None) when a row resolves
    it POPULATION_NOT_LAWFULLY_DUE (final); ('in part', None) when a row resolves it LAWFULLY_DUE_IN_PART and
    none is unresolved; otherwise ('unresolved', the needs the rows name)."""
    work = [result for (_, predicate), result in (governing_results or {}).items() if predicate == WORK]
    if any(result.effect == NOT_DUE for result in work):
        return 'not due', None
    if any(result.effect == IN_PART for result in work) and all(result.truth is not None for result in work):
        return 'in part', None
    needs = frozenset().union(*(result.needs for result in work if result.truth is None))
    return 'unresolved', needs or frozenset({"a governing row's still-due share for this position"})


def date_column(moment, deadline, zone):
    """The rule table's date column for a supplied record against a recipient's deadline (C's exclusive
    boundary): 'T<' or 'T≥' for an instant; for a day, 'D<' when it ends at or before the deadline,
    'D>' when it starts at or after it, 'D∋' when it contains it, each day taken in C's zone; '?'
    without a deadline."""
    from cordon_c.temporal import end_of_day, utc
    if deadline is None:
        return '?'
    if isinstance(moment, datetime):
        return 'T<' if utc(moment) < utc(deadline) else 'T≥'
    if utc(end_of_day(moment, zone)) <= utc(deadline):
        return 'D<'
    if utc(datetime.combine(moment, time(), zone)) >= utc(deadline):
        return 'D>'
    return 'D∋'


COUNT, HOLD, REPORT = 'counts', 'held', 'reported'
# The rule table's commencement and removal rows (SPEC, "Supplied records at an annex position"): the outcome
# per date column. A work off positions takes the listed plant's row; a position not due, or a host-only parcel
# of one due in part, reports on every date.
PERFORMANCE = {
    'plant': {'T<': COUNT, 'T≥': COUNT, 'D<': COUNT, 'D∋': HOLD, 'D>': REPORT, '?': COUNT},
    'plant parcel': {'T<': HOLD, 'T≥': REPORT, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': HOLD},
    'host-only parcel': {'T<': REPORT, 'T≥': REPORT, 'D<': REPORT, 'D∋': REPORT, 'D>': REPORT, '?': REPORT},
    'not due': {'T<': REPORT, 'T≥': REPORT, 'D<': REPORT, 'D∋': REPORT, 'D>': REPORT, '?': REPORT},
    'unresolved': {'T<': HOLD, 'T≥': REPORT, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': HOLD},
}
PERFORMANCE['work'] = PERFORMANCE['plant']


def _naming(work, position):
    """How a record's printed work names an annex position's work: its listed infected plant, a parcel
    holding one, a parcel of the position holding none, or nothing the position prints (None)."""
    if not _on_position(work, position):
        return None
    work = dict(work)
    if 'plant' in work:
        return 'plant'
    holding = {(s['foglio'], s['particella']) for s in position.get('listed_infected_plant_parcels') or ()}
    return 'plant parcel' if (work['foglio'], work['particella']) in holding else 'host-only parcel'


def recipient_results(snapshot, record, at, supplied, *, evaluated_at, permitted_controlled_sources, zone, calendar,
                      position=None, **dueness):
    """C's result per (clause, recipient named by a supplied delivery record), by the rule table in SPEC
    ("Supplied records at an annex position").

    The clause's cohort result stays `c_result` on cohort evidence only. Each record is
    classified once on entry (its kind and, at an annex position (`position`, with the
    records `position_attachments` joined to it and its `governing_results` among
    `dueness`), how it names the position's work); once C's deadline for a recipient is
    known, `date_column` places it. Each record then counts, is held (its work stays
    without a complete history and the need is named), or is reported with its cause.

    The run states its inputs (`admitted_records`): a record dated later than
    `evaluated_at` (the knowledge cutoff) refuses the set, naming the record and field,
    and a record outside `permitted_controlled_sources` reaches no C result. A recipient
    that such a record names, or that is obliged to a work it names, gets no definite
    result: it is withheld with the need 'authorized evidence for …', as
    `EvidenceView.reader` withholds a value an unreadable assertion could contradict.
    """
    from cordon_c.quantities import clock_boundary
    from cordon_c.temporal import end_of_day, utc
    act = record.get('applied_by') or record['instrument']
    # A supplied record carries no capture time: its own dates bound it. A record dated later
    # than the evaluation was not held at the cutoff, and is refused, granted or not.
    records, withheld_records = admitted_records(supplied, act, evaluated_at=evaluated_at, zone=zone,
                                                 permitted_controlled_sources=permitted_controlled_sources)
    ungranted = [r for r, _ in withheld_records]
    kind, cause = position_class(dueness.get('governing_results')) if position else (None, None)
    share = still_due_share(snapshot, at, position, dueness.get('governing_results')) if kind == 'in part' else None
    withdrawn = (f"withdrawn at this position: {', '.join(share['rows'])} (effective {share['since']}) leaves due "
                 'only its listed infected plant(s); not that work, on any date') if share else None
    not_due = 'the position\'s governing rows leave no work due from its owner; this record cannot change the answer'

    def targets(work):
        """The obliged works a printed work names: itself off positions; at a position due in part, the
        still-due plants it names; elsewhere at a position, none."""
        return (work,) if position is None else tuple(_still_due(work, share)) if share else ()

    reported = [dict(record=r['record'], kind=r['kind'], need=need) for r, need in withheld_records]
    deliveries, obliged, named, histories, performances = {}, {}, {}, {}, []
    for r in records:
        work = r['works'][0] if r['works'] else None
        naming = 'work' if position is None or work is None else _naming(work, position)
        if r['kind'] == 'personal-delivery':
            recipient = _printed(r['recipient'])  # the key the join uses: runs of whitespace are one space
            if not recipient:
                reported.append(dict(record=r['record'], cause='names no recipient'))
                continue
            deliveries.setdefault(recipient, {}).setdefault(r['event'].occurred, []).append(r['record'])
            if position is None:
                obliged.setdefault(recipient, set()).update(r['works'])
                continue
            # At a position the delivery is the notice and the join key; the position owns what is due.
            obliged.setdefault(recipient, set()).update(
                _work(dict(plant=p)) for p in (share['plants'] if share else ()))
            named.setdefault(recipient, set()).update(p for w in r['works'] for p in targets(w))
            off = [dict(w) for w in r['works'] if share and not targets(w)]
            if off:
                reported.append(dict(record=r['record'], works=off, cause=withdrawn))
        elif naming is None:
            reported.append(dict(record=r['record'], work=dict(work), cause='the annex position prints no such work'))
        elif r['kind'] == 'history':
            if position is not None and not targets(work):
                reported.append(dict(record=r['record'], work=dict(work),
                                     cause=withdrawn if share else not_due if kind == 'not due' else
                                     'a history at a position whose due work is unresolved cannot make the '
                                     'direction required'))
                continue
            for w in targets(work):
                histories.setdefault(w, []).append(r)
        else:
            row = naming if position is None or kind == 'in part' else kind
            performances.append((r, row, targets(work)))
    adopted = datetime.combine(date.fromisoformat(record['adopted']), time(), zone)

    def covers(history, deadline):
        """The history is stated from the order's adoption (or earlier) through C's (exclusive) deadline.

        A history through a printed day covers that whole day (C's `end_of_day`)."""
        start = history['event'].occurred
        start = start if isinstance(start, datetime) else datetime.combine(start, time(), zone)
        through = _moment(history['complete_through'])
        through = through if isinstance(through, datetime) else end_of_day(through, zone)
        return utc(start) <= utc(adopted) and utc(through) >= utc(deadline)

    def need(r, row, column, due):
        """The need a held record names: the reading that would decide it, and its instant where its day
        contains the deadline or no deadline places it."""
        moment = r['event'].occurred
        when = ('' if isinstance(moment, datetime) else
                f", dated by day only ({moment}), which contains the deadline" if column == 'D∋' else
                f", dated by day only ({moment}), with no deadline to place it against" if column == '?' else '')
        if row == 'plant parcel':
            work = dict(r['works'][0])
            return [f"a record naming the plant {dict(p)['plant']}: {r['record']} prints only its parcel (foglio "
                    f"{work['foglio']}, particella {work['particella']}), which also carries work that "
                    f"{', '.join(share['rows'])} withdraws" + (' and its instant' if column == 'D∋' else '')
                    for p in due]
        if row == 'unresolved':
            return [f"whether {r['record']}{when} performs work still due at this position: "
                    + '; '.join(sorted(cause))]
        return [f"the instant of {r['record']}{when}"]

    vid = snapshot.version(RULE, at)['provision_version_id']
    common = dict(dueness, evaluated_at=evaluated_at, zone=zone, calendar=calendar)
    results, used = {}, set()
    for recipient in sorted(deliveries):
        instants = deliveries[recipient]
        works = sorted(obliged.get(recipient, ()))
        # A record outside the grant that names this recipient, or performs or records a work it is
        # obliged to, could change its result: the result is withheld, never made more definite
        # (`EvidenceView.reader`). Another recipient's delivery gives neither this recipient's notice
        # nor its works, so it withholds nothing here.
        withheld = {_unauthorized(r, act) for r in ungranted
                    if _printed(r.get('recipient')) == recipient
                    or r['kind'] != 'personal-delivery'
                    and (set(r['works']) | {w for printed in r['works'] for w in targets(printed)}) & set(works)}
        if withheld:
            why = f"not applied: {recipient}'s result is withheld for " + '; '.join(sorted(withheld))
            for r, row, due in performances:  # the records the result would have read, as below
                if due and not set(due) & set(works) or not due and position is None:
                    continue
                used.add(r['record'])
                reported.append(dict(record=r['record'], recipient=recipient, work=dict(r['works'][0]),
                                     cause=withdrawn if row == 'host-only parcel' else not_due if row == 'not due'
                                     else why))
            for h in sorted({h['record']: h for w in works for h in histories.get(w, ())}.values(),
                            key=lambda h: h['record']):
                used.add(h['record'])
                reported.append(dict(record=h['record'], recipient=recipient, work=dict(h['works'][0]), cause=why))
            results[recipient] = dict(result=Evaluation(None, needs=frozenset(withheld)), notification=None,
                                      deadline=None, works=[dict(w) for w in works], commencements={},
                                      histories=[], commencement_records_complete=False,
                                      incomplete=[dict(w) for w in works],
                                      records=sorted(n for v in instants.values() for n in v),
                                      fixture=any(r['fixture'] for r in records))
            continue
        notice, notice_instants = {}, {}
        if len(instants) == 1:
            notice[(vid, COMMUNICATED)] = True
            notice_instants[COMMUNICATED] = next(iter(instants))
        else:
            reported.append(dict(recipient=recipient, records=sorted(n for v in instants.values() for n in v),
                                 cause='deliveries at different instants; the personal branch is not supplied'))
        if position is not None and share:
            unnamed = [dict(w) for w in works if w not in named.get(recipient, ())]
            if unnamed:
                reported.append(dict(recipient=recipient, plants=unnamed,
                                     cause='still due at this position and not named by the delivery; reported '
                                           'beside the result, not held'))
        options = dict(notice=notice or None, notice_instants=notice_instants, **_dueness_defaults(common))
        # C's notification for this recipient first; the deadline and every date column are C's from it.
        _, notification = _c_facts(snapshot, record, at, commencements={}, commencement_records_complete=False,
                                   **options)
        deadline = None
        if notification is not None and record['stated_term'] is not None:
            deadline = clock_boundary(snapshot, CLOCK, at, notification, zone=zone, calendar=calendar,
                                      stated_term=record['stated_term'])
        commencements, held, wanted = {}, set(), set()
        for r, row, due in performances:
            if due and not set(due) & set(works) or not due and position is None:
                continue
            used.add(r['record'])
            moment = r['event'].occurred
            column = date_column(moment, deadline, zone)
            outcome = PERFORMANCE[row][column]
            if outcome == COUNT and not isinstance(moment, datetime) and column == '?':
                outcome = HOLD  # no deadline to place its day against
            work = dict(r['works'][0])
            if outcome == COUNT:
                commencements[r['record']] = (moment if isinstance(moment, datetime)
                                              else datetime.combine(moment, time(), zone))
            elif outcome == HOLD:
                held.update(due)
                needs = need(r, row, column, due)
                wanted.update(needs)
                reported.append(dict(record=r['record'], recipient=recipient, work=work, outcome=HOLD, needs=needs,
                                     cause='held: not counted, and the work it may concern stays without a complete '
                                           'history until the need is met'))
            else:
                reported.append(dict(record=r['record'], recipient=recipient, work=work, outcome=REPORT,
                                     cause=withdrawn if row == 'host-only parcel' else not_due if row == 'not due'
                                     else 'after the deadline: no reading of this record defeats noncommencement'))
        used.update(h['record'] for w in works for h in histories.get(w, ()))
        complete = deadline is not None and bool(works) and all(
            any(covers(h, deadline) for h in histories.get(w, ())) and w not in held for w in works)
        incomplete = ([dict(w) for w in works if w in held or not any(covers(h, deadline) for h in histories.get(w, ()))]
                      if deadline is not None else [dict(w) for w in works])
        facts, notification = _c_facts(snapshot, record, at, commencements=commencements,
                                       commencement_records_complete=complete, **options)
        result = evaluate(snapshot, RULE, at, facts)
        if result.truth is None and wanted:
            result = replace(result, needs=result.needs | wanted)
        results[recipient] = dict(result=result, notification=notification, deadline=deadline,
                                  works=[dict(w) for w in works], commencements=commencements,
                                  histories=sorted({h['record'] for w in works for h in histories.get(w, ())}),
                                  commencement_records_complete=complete, incomplete=incomplete,
                                  records=sorted(n for v in instants.values() for n in v),
                                  fixture=any(r['fixture'] for r in records))
    # Every supplied record ends counted, held, reported or here: no recipient's work is the one it names.
    shown = {r.get('record') for r in reported}
    unused = {}
    for r in records:
        if r['kind'] != 'personal-delivery' and r['record'] not in used | shown:
            unused.setdefault(r['works'][0], []).append(r['record'])
    for work in sorted(unused):
        outside = sorted(need for r, need in withheld_records if r['kind'] == 'personal-delivery'
                         and (position is not None or work in r['works']))
        reported.append(dict(records=sorted(unused[work]), work=dict(work),
                             cause=('only a delivery outside the grant obliges a recipient to this work: '
                                    + '; '.join(outside)) if outside else
                             'no supplied record obliges a recipient to this work as printed'))
    return dict(recipients=results, reported=reported)


def _unauthorized(record, act):
    on = '' if act is None else f' on {act}'
    return f"authorized evidence for {record['kind']} record {record['record']}{on}"


def _dueness_defaults(common):
    keys = ('evaluated_at', 'governing_results', 'work_due', 'coercion_due', 'closures', 'stated_changes',
            'within_closed_scope', 'zone', 'calendar')
    defaults = dict(governing_results=None, work_due=None, coercion_due=None, closures=(), stated_changes=(),
                    within_closed_scope=None)
    unknown = set(common) - set(keys)
    if unknown:
        raise TypeError(f'recipient_results takes no {sorted(unknown)}')
    return {**defaults, **common}

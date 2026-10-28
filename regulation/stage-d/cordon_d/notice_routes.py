"""The `recipient-notice` field 'act-specific mass-publicity basis', read from each order's own text.

A reading supplies, as printed, the reasons the order gives for reaching its
recipients by publicity and the publicity forms it establishes (venue, period,
stated effect). Under Owen's 2026-09-24 ruling an act's own stated ground for
public posting meets Art. 21-bis and is not re-judged; whether a held posting
completes the stated form is C's computation from the stated period and the
posting's dates.
"""
from datetime import date
from pathlib import Path

from cordon_c.core import Evaluation, evaluate
from .case_prescriptions import REREAD, _plain, on_cited, on_page, page_texts
from .document_subscription import read_native_text, read_retained

RULE = 'IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route'
STATED_GROUND = 'the act states its own ground for reaching its recipients by public posting'
COMPLETED = 'the publicity form the act states has been completed'


def _object(**properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


def _choice(*values):
    return {'type': 'string', 'enum': list(values)}


TEXT = {'type': 'string'}
CITATIONS = {'type': 'array', 'items': _object(page={'type': 'integer', 'minimum': 1}, quote=TEXT)}
SCHEMA = _object(
    grounds={'type': 'array', 'items': _object(
        literal=TEXT, about=_choice('this-act', 'general-law'), part=_choice('operative', 'recital'),
        support=CITATIONS)},
    forms={'type': 'array', 'items': _object(
        literal=TEXT, duration={'anyOf': [{'type': 'null'}, _object(number=TEXT, unit_word=TEXT, literal=TEXT)]},
        effect=TEXT, part=_choice('operative', 'recital'), support=CITATIONS)},
    issues={'type': 'array', 'items': _object(page={'type': ['integer', 'null'], 'minimum': 1}, detail=TEXT)},
)
PROMPT = (Path(__file__).resolve().parents[1] / 'notice-route-reading.txt').read_text()


def validate(reading, pages):
    """Bind every quotation and copied field to its cited pages; this does not certify meaning."""
    def cited(support, what):
        if not support:
            raise ValueError(f'{what} needs source support')
        for citation in support:
            if citation['page'] not in pages or not on_page(citation['quote'], pages[citation['page']]):
                raise ValueError(f'{what}: quotation is not on page {citation["page"]}')
        return sorted({c['page'] for c in support})

    for index, item in enumerate(reading['grounds']):
        numbers = cited(item['support'], f'ground {index}')
        if not item['literal'].strip() or not on_cited(item['literal'], pages, numbers):
            raise ValueError(f'ground {index}: the reason is not on its cited pages')
    for index, item in enumerate(reading['forms']):
        what = f'form {index}'
        numbers = cited(item['support'], what)
        words = [item['literal'], item['effect']]
        duration = item['duration']
        if duration is not None:
            if not (duration['number'].strip() and duration['unit_word'].strip()):
                raise ValueError(f'{what}: period needs its printed number and unit word')
            # A spelled-out repetition may stand between them: "7 (sette) giorni".
            phrase, number = _plain(duration['literal']), _plain(duration['number'])
            at = phrase.find(number)
            if at < 0 or _plain(duration['unit_word']) not in phrase[at + len(number):]:
                raise ValueError(f'{what}: the period does not print its number before its unit word')
            words.append(duration['literal'])
        if not item['literal'].strip() or any(w.strip() and not on_cited(w, pages, numbers) for w in words):
            raise ValueError(f'{what}: a copied field is not on its cited pages')
    for issue in reading['issues']:
        if issue['page'] is not None and issue['page'] not in pages:
            raise ValueError('An issue names an unsupplied page')


def read_notice_route(source, store, *, execute=False, model='opus', effort='medium', timeout=900,
                      refused=None):
    """Read one order's complete native text; replay unless `execute`.

    `refused` names the validation cause of a refused reading: one bounded,
    source-only reread whose request states that cause, as for prescriptions.
    """
    prompt = PROMPT if refused is None else PROMPT + '\n' + REREAD.format(cause=refused) + '\n'
    response = read_native_text([source], store, prompt=prompt, schema=SCHEMA, model=model,
                                effort=effort, timeout=timeout, execute=execute)
    validate(response['reading'], page_texts(source, store))
    return response


def retained_notice_route(request_id, store):
    response = read_retained(request_id, Path(store))
    if response['request'].get('schema') != SCHEMA:
        raise ValueError('Retained request used another notice-route contract')
    validate(response['reading'], page_texts(response['request']['sources'][0], Path(store)))
    return response


def mass_publicity_basis(response, *, instrument):
    """The `recipient-notice` field for one act, as its own text states it.

    `stated_ground` holds only reasons the act states about its own recipients,
    verbatim; `ground_stated` says whether the act states any. A restatement of
    the general rule is kept apart. Nothing is classified as satisfying A's
    predicates.
    """
    reading = response['reading']
    stated = tuple(g for g in reading['grounds'] if g['about'] == 'this-act')
    return dict(
        instrument=instrument, source=response['request']['sources'][0], ground_stated=bool(stated),
        stated_ground=stated,
        restated_rule=tuple(g for g in reading['grounds'] if g['about'] == 'general-law'),
        forms=tuple(reading['forms']), issues=tuple(reading['issues']),
        request_sha256=response['request_sha256'], provenance='model_proposed_reading')


def c_result(snapshot, basis, at, *, postings=()):
    """C's Art. 21-bis mass-publicity result with only what D holds for the exact act.

    A ground the reading holds about this act is the act's own stated ground
    (Owen's 2026-09-24 ruling: C does not re-judge it). A held posting reaches C
    unresolved, naming what completion needs: the period the act states and the
    posting's dates, from which `mass_publicity_facts` computes it. Where the act
    states no ground, or no posting is held, nothing is supplied and C names its
    own missing predicate.
    """
    if type(at) is not date:
        raise TypeError('The run states its evaluation date')
    vid = snapshot.version(RULE, at)['provision_version_id']
    facts = {}
    if basis['stated_ground']:
        facts[(vid, STATED_GROUND)] = True
    if postings:
        held = '; '.join(f"{p['publisher']} from {p['start']}, " + (f"to {p['end']}" if p.get('end')
                                                                    else 'end not established')
                         for p in postings)
        facts[(vid, COMPLETED)] = Evaluation(None, needs=frozenset(
            {f"completion of the publicity form {basis['instrument']} states, from its stated period and the held "
             f"posting ({held})"}))
    return evaluate(snapshot, RULE, at, facts)

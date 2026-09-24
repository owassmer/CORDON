"""Changes that held acts state to removal orders.

The removal-order population states its own relationships through
`case_prescriptions`. Every other act A holds is read here when its admitted text
prints a held order's identity (`printed_orders`). `albo_postings` reads register
rows with the same matcher (`printed_identities`). The act is read whole, from its
admitted text, for every act it states it corrects, supplements, completes,
replaces, revokes, suspends or withdraws, as a whole or in part, with the words
stating what changes. An operative statement
reaches the named order's lawful dueness as a stated change (`order_dueness`);
nothing is patched and no A row is written.
"""
from collections import defaultdict
from datetime import date
from pathlib import Path
import re

from .case_prescriptions import _array, _choice, _object, CITATIONS, OPTIONAL_TEXT, TEXT, on_cited, on_page
from .document_subscription import read_native_blocks
from .removal_events import act_id
from .store import put_bytes

PROMPT = (Path(__file__).resolve().parents[1] / 'act-relationship-reading.txt').read_text()
PRESENTATION = "A-admitted source text, one block per form-feed page"
SCHEMA = _object(
    identity=_object(issuer=TEXT, authority=_choice('puglia-osservatorio', 'other', 'unresolved'),
                     number=OPTIONAL_TEXT, adopted={'type': ['string', 'null'],
                                                    'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'},
                     title=TEXT, support=CITATIONS),
    relationships=_array(_object(
        relationship=_choice('corrects', 'supplements', 'completes', 'replaces', 'revokes', 'suspends',
                             'withdraws'),
        extent=_choice('whole', 'part'), number=TEXT, year={'type': 'string', 'pattern': '^[0-9]{4}$'},
        date_words=TEXT, affected_payload=TEXT, part=_choice('operative', 'recital'), support=CITATIONS)),
    issues=_array(_object(page={'type': ['integer', 'null'], 'minimum': 1}, detail=TEXT)),
)
_INSTRUMENT = re.compile(r'-(\d{4})-0*(\d+)$')


def admitted_sources(snapshot):
    """Every source text A admits, with the A instruments whose rows cite it."""
    sources = defaultdict(set)
    for rows in snapshot.stable.values():
        for row in rows:
            uri = row.get('source_uri') or ''
            if uri.startswith('file:') and uri.endswith('.txt'):
                sources[uri.removeprefix('file:')].add(row['instrument_id'])
    return {path: tuple(sorted(instruments)) for path, instruments in sorted(sources.items())}


_MONTHS = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre',
           'ottobre', 'novembre', 'dicembre')
_DATE = re.compile(r'(\d{1,2})\s*(?:[./-]\s*(\d{1,2})\s*[./-]|\s+(' + '|'.join(_MONTHS) + r')\s+)\s*(\d{4})', re.I)
_DESIGNATED = re.compile(r'(?:\bD\.?\s?D\.?\s?S\.?|\bD\.?\s?D\.?|\bDET\.?|\bdetermin\w*(?:\s+dirigenziale)?|'
                         r'\batto\s+dirigenziale)\s*(?:n(?:[.°r]|\.ro)?\.?\s*)?0*(\d{1,4})\s*/\s*(\d{4})\b', re.I)


def _printed_date(match):
    day, month, name, year = match.groups()
    month = int(month) if month else _MONTHS.index(name.lower()) + 1
    try:
        return date(int(year), month, int(day))
    except ValueError:
        return None


def printed_identities(text):
    """(number, year, printed date or None, words) for every act identity the text prints: a
    number followed closely by a readable date ("n. 96 del 28/08/2023", "DDS 99 05/08/2024",
    "n. 129 del 14 luglio 2025"), or an act designator with number and year ("DDS 96/2023").
    Closely: at most 12 characters and two words between them, none a number."""
    found = []
    for match in re.finditer(r'(?:(?<![\d/.,])|(?<=\b[Nn]\.))0*(\d{1,4})(?![\d/])', text):
        printed = _DATE.search(text[match.end():match.end() + 40])
        gap = text[match.end():match.end() + printed.start()] if printed else ''
        close = printed and printed.start() <= 12 and not re.search(r'\d', gap) and len(gap.split()) <= 2
        day = _printed_date(printed) if close else None
        if day:
            found.append((int(match.group(1)), day.year, day, text[match.start():match.end() + printed.end()]))
    for match in _DESIGNATED.finditer(text):
        found.append((int(match.group(1)), int(match.group(2)), None, match.group(0)))
    return found


def printed_orders(text, orders):
    """Held orders whose identity the text prints (`printed_identities`): the order's number
    with its adoption date, or a designator with its number and year. `orders` maps
    instrument to its adoption date. A printed identity selects the act for reading; it
    establishes no relationship."""
    held = defaultdict(list)
    for instrument, adopted in orders.items():
        match = _INSTRUMENT.search(instrument)
        if match:
            held[int(match.group(2)), int(match.group(1))].append((instrument, date.fromisoformat(str(adopted))))
    return {instrument for number, year, printed, _ in printed_identities(text)
            for instrument, adopted in held.get((number, year), ()) if printed in (None, adopted)}


def selected(snapshot, root, orders):
    """A-admitted sources outside the order population whose text prints a held order's identity.

    `orders` are the held orders (instrument to adoption date) whose own texts the
    prescription reader reads. Returns (selected, scanned): each selected entry is the
    path, its A instruments and the held orders it prints.
    """
    chosen, scanned = [], 0
    for path, instruments in admitted_sources(snapshot).items():
        source = Path(root) / path
        if not source.exists():
            continue
        scanned += 1
        if set(instruments) <= set(orders):
            continue
        named = printed_orders(source.read_text(errors='replace'), orders) - set(instruments)
        if named:
            chosen.append(dict(path=path, instruments=instruments, names=tuple(sorted(named))))
    return chosen, scanned


def blocks(data: bytes):
    """The admitted text's pages: form-feed separated, a trailing empty page dropped."""
    pages = data.decode('utf-8').split('\f')
    if pages and not pages[-1].strip():
        pages.pop()
    return [page if page.strip() else '[this page has no text]' for page in pages]


def validate(reading, pages):
    """Bind every quotation and copied payload to its supplied block; this does not certify meaning."""
    def cited(support, what):
        if not support:
            raise ValueError(f'{what} needs source support')
        for citation in support:
            if citation['page'] not in pages or not on_page(citation['quote'], pages[citation['page']]):
                raise ValueError(f'{what}: quotation is not in block {citation["page"]}')
        return sorted({c['page'] for c in support})

    cited(reading['identity']['support'], 'identity')
    if reading['identity']['adopted']:
        date.fromisoformat(reading['identity']['adopted'])
    for index, item in enumerate(reading['relationships']):
        numbers = cited(item['support'], f'relationship {index}')
        if not re.search(r'\d', item['number']):
            raise ValueError(f'relationship {index}: the other act needs its printed number')
        for words in (item['affected_payload'], item['date_words']):
            if words.strip() and not on_cited(words, pages, numbers):
                raise ValueError(f'relationship {index}: a copied field is not in its cited blocks')
    for issue in reading['issues']:
        if issue['page'] is not None and issue['page'] not in pages:
            raise ValueError('An issue names an unsupplied block')


def read_act(path, root, store, *, execute=False, model='opus', effort='medium', timeout=900):
    """Read one A-admitted act whole for the relationships it states; replay unless `execute`."""
    data = (Path(root) / path).read_bytes()
    digest = put_bytes(Path(store), data)
    texts = blocks(data)
    response = read_native_blocks(digest, texts, Path(store), prompt=PROMPT, schema=SCHEMA,
                                  presentation=PRESENTATION, model=model, effort=effort, timeout=timeout,
                                  execute=execute)
    validate(response['reading'], dict(enumerate(texts, 1)))
    return response


def origin(response, instruments):
    """The act stating the change: its single A instrument, else its own Osservatorio identity."""
    if len(instruments) == 1:
        return instruments[0]
    identity = response['reading']['identity']
    if identity['authority'] == 'puglia-osservatorio' and identity['number'] and identity['adopted']:
        return act_id(re.sub(r'\D', '', identity['number']), identity['adopted'][:4])
    return ' | '.join(instruments)


def stated_changes(response, instruments, path):
    """The operative changes the act states, one per named act; a recital restates, it changes nothing."""
    source = origin(response, instruments)
    for item in response['reading']['relationships']:
        if item['part'] != 'operative':
            continue
        yield dict({'from': source}, target=act_id(re.sub(r'\D', '', item['number']), item['year']),
                   relationship=item['relationship'], extent=item['extent'],
                   affected_payload=item['affected_payload'], date_words=item['date_words'],
                   source=response['request']['sources'][0], path=path, request_sha256=response['request_sha256'],
                   support=item['support'])

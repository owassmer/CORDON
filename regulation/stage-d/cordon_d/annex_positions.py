"""Annex positions for the orders an in-force governing row names with a whole-or-part effect.

A governing row whose route table asks whether the population in question holds plants
the named order lists as infected is answered per recipient position, not per order.
Which orders: those named in `corrects_instrument_ids` of an in-force row whose
condition asks a predicate that `predicate-contracts.json` binds to a position field
(`position_field`). The list comes from A and the bindings, never from code.

Reading: the order's annex named by its cohort ("allegato 1/D") is read from the retained
original's text layer, deterministically and without a model. Its tables are printed
rotated; each vertical text line is placed in the band between the page's drawn row
rules, which restores every printed row. Two kinds of table are read:

- the infected-plant table: each row's sample ID, foglio and particella;
- the 50 m tables ("ZONA/ZONE INFETTA/E DI 50 M ..."): foglio, particelle and owners.

Checks: the infected-plant rows equal the operative "n° N piante ... infette", and every
infected plant's parcel has a 50 m row naming its owners. Where either fails, every
position of the order is unknown, naming the failed check.

Positions: one per owner printed in the 50 m tables, with every parcel printed against
that owner and the listed infected plants standing on those parcels (a plant's owners
are read from the 50 m row of its parcel, since the infected-plant table prints an owner
once across several rows). A 50 m listing that places no recipient (no parcel number, or
an owner printed as not identified) is one position with no recipient, whose cause names
its printed words. Owners are printed names: joint owners are each a position, and
printed variants are not merged.

Answering the row: each bound predicate takes its position field (non-empty is true); a
position with no recipient, or of an order whose checks failed, leaves both unknown with
its cause. The row is evaluated through `evaluate` per (record at a position, predicate).
The position is the recipient's share of both the work and the coercive population, so
the same facts answer WORK and COERCE.
"""
import bisect
import copy
from functools import lru_cache
import json
from pathlib import Path
import re

from cordon_c.core import Evaluation, evaluate

from .prescriptions import COERCE, WORK
from .store import blob_path

CONTRACTS = Path(__file__).resolve().parents[1] / 'predicate-contracts.json'
TIME = "decision time within this version's effective interval"
_LABEL = re.compile(r'allegato\s*(\d+\s*/\s*[A-Za-z]+)', re.I)
_PRINTED = re.compile(r'estirpazione\s+di\s+n\s*[°º.]?\s*(\d+)\s+piant\w*\b[^;]{0,120}?infett', re.I)
_SAMPLE = re.compile(r'(?<![\d,./])(\d{7})(?![\d,/])')
_PLACED = re.compile(r'(?<![\d,])\d{1,2},\d{3,}\s*\|\s*\d{1,2},\d{3,}\s*\|\s*(\d{1,4})\s*\|?\s*(\d{1,5})(?![\d,])')
_ZONE = re.compile(r'ZON[AE]\s+INFETT[AE]\s+DI\s+50\s*M', re.I)
_NUMBER = re.compile(r'(?<![\w,.])(\d{1,5})(?![\d,.])')
_SEPARATOR = r'[\s|\-–—]*'
_UNPLACED = re.compile(r'\bNON\s+INDIVIDUAT', re.I)
# A company's legal form printed after a dash continues its name ("… LIMITATA - SOCIETA' AGRICOLA").
_FORM = re.compile(r"^(?:SOCIET[AÀ]|S\.?\s?R\.?\s?L|S\.?\s?P\.?\s?A|S\.?\s?A\.?\s?S|S\.?\s?N\.?\s?C)", re.I)


def _predicates(node):
    if isinstance(node, dict):
        if 'predicate' in node:
            yield node['predicate']
        for child in node.values():
            yield from _predicates(child)
    elif isinstance(node, list):
        for child in node:
            yield from _predicates(child)


def position_bindings(path=CONTRACTS):
    """Predicate to the position field that answers it, as `predicate-contracts.json` binds it."""
    return {b['predicate']: b['position_field'] for b in json.loads(Path(path).read_text())['bindings']
            if b.get('position_field')}


def supplying_rows(snapshot, at, instrument, bindings=None):
    """In-force rows naming the instrument in `corrects_instrument_ids` whose condition asks a
    predicate bound to an annex position field."""
    bound = set(position_bindings() if bindings is None else bindings)
    day = at.isoformat()
    return sorted({sid for sid, rows in snapshot.stable.items() for row in rows
                   if instrument in row.get('corrects_instrument_ids', ())
                   and row['effective_from'] <= day
                   and (not row['effective_to_exclusive'] or day < row['effective_to_exclusive'])
                   and bound & set(_predicates(row['condition_ast']))})


def annex_label(record):
    """The annex the record's cohort prints ("allegato 1/D" -> "1/D"), or None."""
    for cohort in record.get('cohort') or ():
        match = _LABEL.search(cohort or '')
        if match:
            return re.sub(r'\s+', '', match.group(1)).upper()
    return None


def _rules(page):
    """Across-text positions of the page's drawn row rules (rotated tables: vertical lines)."""
    xs = set()
    for drawing in page.get_drawings():
        for item in drawing['items']:
            if item[0] == 'l':
                p, q = item[1], item[2]
                if abs(p.x - q.x) < 0.5 and abs(p.y - q.y) > 20:
                    xs.add(round(p.x, 1))
            elif item[0] == 're':
                r = item[1]
                if r.width < 2 and r.height > 20:
                    xs.add(round(r.x0, 1))
                elif r.height > 20:
                    xs.update({round(r.x0, 1), round(r.x1, 1)})
    merged = []
    for x in sorted(xs):
        if not merged or x - merged[-1] > 3:
            merged.append(x)
    return merged


def page_bands(page):
    """The page's vertical text lines, one string per band between drawn row rules, in reading order."""
    xs, bands = _rules(page), {}
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            if abs(line['dir'][1]) < 0.9:
                continue
            text = re.sub(r'\s+', ' ', ''.join(s['text'] for s in line['spans'])).strip()
            if not text:
                continue
            x0, _, x1, y1 = line['bbox']
            key = -y1 if line['dir'][1] < 0 else y1
            bands.setdefault(bisect.bisect(xs, (x0 + x1) / 2), []).append((key, text))
    return [' | '.join(t for _, t in sorted(lines)) for _, lines in sorted(bands.items())]


def _heading(band):
    match = re.match(r'^\s*ALLEGATO\s+(\d+\s*/\s*[A-Za-z]+)\s*$', band, re.I)
    return re.sub(r'\s+', '', match.group(1)).upper() if match else None


def annex_bands(document, label):
    """(page, band index, text) for every band of the annex: from the page whose rotated heading is
    "ALLEGATO <label>" through the following pages of rotated text, until another annex heading."""
    out, inside = [], False
    for number, page in enumerate(document, 1):
        bands = page_bands(page)
        headings = {h for h in map(_heading, bands) if h}
        if label in headings:
            inside = True
        elif inside and (headings or not bands or re.search(r'(?im)^\s*ALLEGATO\s+\d', page.get_text())):
            break
        if inside:
            out += [(number, index, band) for index, band in enumerate(bands)]
    return out


def printed_count(text):
    """The operative "n° N piante ... infette": N when printed once (or the same each time), else None."""
    found = {int(m.group(1)) for m in _PRINTED.finditer(text)}
    return found.pop() if len(found) == 1 else None


def _owners(text):
    """Printed owner names: one per text line, and names a dash separates within a line."""
    names = []
    for line in text.split('|'):
        for piece in re.split(r'\s+[-–—]\s+', line):
            piece = re.sub(r'\s+', ' ', piece).strip(' -–—')
            if not piece:
                continue
            if names and _FORM.match(piece):
                names[-1] = f'{names[-1]} - {piece}'
            else:
                names.append(piece)
    return names


def parse(bands, printed):
    """The annex's infected-plant rows and 50 m listings from its bands, with the failed checks."""
    infected, listings, zone = [], [], False
    for page, index, band in bands:
        where = f'p. {page} row {index}'
        placed = _PLACED.search(band)
        sample = _SAMPLE.search(band)
        if placed and sample and sample.start() < placed.start():
            infected.append(dict(sample=sample.group(1), foglio=placed.group(1), particella=placed.group(2),
                                 row=where))
            zone = False
            continue
        if _ZONE.search(band):
            zone = True
            continue
        if not zone or _heading(band) or re.search(r'\bFOGLIO\b', band) or re.match(r'^\s*[\d(]', band):
            continue
        first = _NUMBER.search(band)
        if not first or not re.search(r'[A-Za-z]', band[:first.start()]):
            continue
        foglio, rest = first.group(1), band[first.end():]
        parcels = []
        while True:
            match = re.match(_SEPARATOR + r'(\d{1,5})(?![\d,.])', rest)
            if not match:
                break
            parcels.append(match.group(1))
            rest = rest[match.end():]
        words = re.sub(r'\s+', ' ', rest.replace('|', ' | ')).strip(' |-–—')
        owners = [] if not parcels or _UNPLACED.search(words) else _owners(rest)
        listings.append(dict(agro=band[:first.start()].strip(' |'), foglio=foglio, particelle=parcels,
                             owners=owners, words=re.sub(r'\s*\|\s*', ' ', words), row=where))
    failures = []
    if printed is None:
        failures.append('the operative "n° N piante ... infette" is not printed once in the order')
    elif len(infected) != printed:
        failures.append(f'the infected-plant table has {len(infected)} rows; the order prints n° {printed} piante')
    owned = {(item['foglio'], p) for item in listings if item['owners'] for p in item['particelle']}
    missing = sorted({(i['foglio'], i['particella']) for i in infected} - owned)
    if missing:
        failures.append('no 50 m row names the owners of infected-plant parcel(s) '
                        + ', '.join(f'{f}/{p}' for f, p in missing))
    return dict(infected=infected, listings=listings, failures=failures)


def positions(annex, label):
    """One position per printed owner, and one per 50 m listing that places no recipient."""
    plants = {}
    for item in annex['infected']:
        plants.setdefault((item['foglio'], item['particella']), []).append(item['sample'])
    owners, unplaced = {}, []
    for item in annex['listings']:
        parcels = [dict(foglio=item['foglio'], particella=p) for p in item['particelle']]
        if not item['owners']:
            place = f"foglio {item['foglio']}" + (', particella ' + ', '.join(item['particelle'])
                                                  if item['particelle'] else '')
            unplaced.append(dict(annex=f'allegato {label}', owner=None, printed=item['words'], parcels=parcels,
                                 fifty_metre_parcels=parcels, listed_infected_plants=[], rows=[item['row']],
                                 cause=f"annex {label} places this 50 m listing on no recipient: "
                                       f"'{item['words']}' ({place})"))
            continue
        for name in item['owners']:
            position = owners.setdefault(name, dict(annex=f'allegato {label}', owner=name, printed=name,
                                                    parcels=[], fifty_metre_parcels=[],
                                                    listed_infected_plants=[], rows=[]))
            for parcel in parcels:
                if parcel not in position['parcels']:
                    position['parcels'].append(parcel)
                    position['fifty_metre_parcels'].append(parcel)
                    position['listed_infected_plants'] += plants.get((parcel['foglio'], parcel['particella']), [])
            position['rows'].append(item['row'])
    out = list(owners.values()) + unplaced
    if annex['failures']:
        cause = f"annex {label} of this order is not read: " + '; '.join(annex['failures'])
        out = [dict(p, cause=cause) for p in out]
    return out


@lru_cache(maxsize=16)
def read_annex(path, label):
    """Parse the annex `label` of the retained original at `path`: (annex, positions)."""
    import pymupdf
    with pymupdf.open(path) as document:
        text = '\n'.join(page.get_text() for page in document)
        annex = parse(annex_bands(document, label), printed_count(text))
    return annex, positions(annex, label)


def expand(record, snapshot, at, store):
    """The record once per annex position when an in-force row the annex answers names its order;
    otherwise the record itself. The cohort stays as printed; the position goes in `recipients`."""
    label = annex_label(record)
    if label is None or not supplying_rows(snapshot, at, record['instrument']):
        return [record]
    _, found = read_annex(str(blob_path(store, record['source'])), label)
    if not found:
        return [record]
    return [dict(record, occurrence=f"{record['occurrence']}:annex {label}:position {k}",
                 recipients=(copy.deepcopy(position),)) for k, position in enumerate(found)]


def governing_results(snapshot, record, at, position):
    """Each supplying row's result for the record at its position, per (row, predicate)."""
    if position is None:
        return {}
    bound, results = position_bindings(), {}
    for sid in supplying_rows(snapshot, at, record['instrument'], bound):
        vid = snapshot.version(sid, at)['provision_version_id']
        facts = {(vid, TIME): True}
        for predicate, field in bound.items():
            facts[(vid, predicate)] = (Evaluation(None, needs=frozenset({position['cause']}))
                                       if position.get('cause') else bool(position[field]))
        result = evaluate(snapshot, sid, at, facts)
        results[(sid, WORK)] = results[(sid, COERCE)] = result
    return results

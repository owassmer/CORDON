"""Row 9: the protected status inputs of the plants a removal decision reaches (L.R. Puglia 14/2007).

D supplies what PR #32's rows read, and nothing it decides itself:

- for a register entry, its layer, key, card, parcel and point, the acts that first published it, approved it
  definitively and deleted it, each with the BURP date its own pages print, and the positional qualification of
  its point (its survey batch's measured bound);
- for an affected plant, and for a negative olive within 50 m of one, its official monitoring record: the
  `MONUMENTALE_ARIF` flag as printed, each `NOTE_RILEVATORE` note verbatim with D's reading (states / does not /
  unclear), each measurement as printed with the numbers read from its words, the codes the note prints, and
  its candidate entries at d.

A decides listed, pending and the Art. 2(1)(a) comparison (`cordon_c.bindings.listing_facts`,
`trunk_diameter_facts`); D compares no measurement.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re

from cordon_c.core import Evaluation

REPOSITORY = Path(__file__).resolve().parents[3]
SOURCES = 'corpus/sources/protected-status'
FLAGS = ('Si', '1')  # the printed values of MONUMENTALE_ARIF that record the characteristics
NOT_RECORDED = date(2000, 1, 1)  # RILDATA 946684800000 ms (2000-01-01 00:00 UTC), a placeholder, not a survey date
TOLERANCE = 0.05  # how near a survey group's count must be to one stated batch to be assigned to it
MIN_FIXES = 20  # the NSSDA minimum of check points for a batch's own bound
PAIRING_M = 50.0  # the reference-fix pairing radius, and the d of the note-code rule inside it


# --- the surveyor's note --------------------------------------------------------------------

# Wordings that assert the plant has monumental characteristics, misspellings included.
_STATES = re.compile(r"caratteristic\w*\s+(di\s+)?monumenta\w*|carattere\s+(di\s+)?monumental\w*|"
                     r"requisit\w*\s+di\s+monumentalit\w*|pianta\s+monum\w*|ulivo\s+monumental\w*|"
                     r"^\s*monumentale\b", re.I)
# A negation or hedge that governs the monumental term itself (not "non censita, con caratteristiche").
_NEGATED = re.compile(r"\b(non|senza|nessun\w*|priv\w*\s+di|ne)\s+(ha\s+|presenta\s+|sono\s+presenti\s+|e'?\s+|è\s+|"
                      r"di\s+)?(\w+\s+)?(caratteristic\w*\s+(di\s+)?)?monument", re.I)
_HEDGED = re.compile(r"(possibil\w*|presunt\w*|probabil\w*|apparent\w*|forse|sembr\w*|potenzial\w*|eventual\w*|"
                     r"presumibil\w*|dubbi\w*\s+(caratteristic|monument))\s+(\w+\s+){0,2}(caratteristic|monument)|"
                     r"monument\w*('+)?\s*(\?|da\s+verificar\w*|presunt\w*|dubbi\w*)", re.I)


@dataclass(frozen=True)
class NoteReading:
    """D's reading of one note: whether it states that the plant has monumental characteristics."""
    note: str             # verbatim
    reading: str          # 'states' | 'does not' | 'unclear'
    cite: str | None      # the words the reading rests on
    cause: str | None     # for 'unclear': negated, hedged, or the term without a statement of the plant


def read_note(note: str) -> NoteReading:
    if not re.search(r"monum", note, re.I):
        return NoteReading(note, 'does not', None, None)
    for pattern, cause in ((_NEGATED, 'negated'), (_HEDGED, 'hedged')):
        found = pattern.search(note)
        if found:
            return NoteReading(note, 'unclear', found.group(), cause)
    found = _STATES.search(note)
    if found:
        return NoteReading(note, 'states', found.group(), None)
    return NoteReading(note, 'unclear', re.search(r"\S*monum\S*", note, re.I).group(),
                       'names the term without stating it of the plant')


# --- measurements the note records ------------------------------------------------------------

# The value is kept as printed. A value printed with a leading separator ("dim. ,9") is read only directly after
# the quantity, with no unit or other word before it: after a unit, "cm.80" and "mt.1,20" give no value.
_QUANTITY = re.compile(r"(diametr\w*|circonferenz\w*|circ\.|dim\.|dimension\w*|dm\.?)(?:(?![.,]\d)\W){0,3}"
                       r"(?:((?:tronco\s+)?(?:di\s+)?(?:circa\s+)?(?:superiore\s+a\s+)?(?:oltre\s+)?)"
                       r"(cm|mt|m|metri|centimetri)?\s*(\d+(?:[.,]\d+)?)|([.,]\d+))"
                       r"(?:\s*(cm|mt|m\b|metri|centimetri))?(\s+circa)?", re.I)
_HEIGHT = re.compile(r"(ad?\s+(?:un|uno|\d+(?:[.,]\d+)?)\s+(?:metr\w*|mt|m|cm)(?:\s+e\s+mezzo)?\s+"
                     r"(?:di\s+altezza|da\s+terra)|altezza\W+(?:\w+\W+){0,3}\d+(?:[.,]\d+)?\s*(?:cm|mt|m|metri)?)", re.I)
_TO_CM = {'cm': 1, 'centimetri': 1, 'm': 100, 'mt': 100, 'metri': 100}
NOT_READ = 'measurement not read'
_WORDS = {'un': Decimal(1), 'uno': Decimal(1), 'due': Decimal(2), 'tre': Decimal(3)}


@dataclass(frozen=True)
class Measurement:
    """One measurement a note records, as printed, with the numbers read from its words (cite-or-abstain)."""
    quantity: str               # as printed ('diametro', 'dim.')
    qualifier: str              # as printed ('circa', 'superiore a'), or ''
    value: str                  # as printed
    unit: str                   # as printed, or 'no unit printed'
    height: str                 # as printed, or 'no height printed'
    diameter_cm: Decimal | None        # trunk_diameter_facts' diameter_cm; None unless a diameter with its unit
    measured_height_cm: Decimal | None  # trunk_diameter_facts' measured_height_cm; None only where none is printed
    cite: str                   # the note's words the numbers come from
    cause: str | None = None    # why diameter_cm is None, where it is


def _height_cm(words: str) -> Decimal | None:
    text = words.lower().replace(',', '.')
    number = re.search(r"(\d+(?:\.\d+)?|\bun\b|\buno\b|\bdue\b|\btre\b)", text)
    unit = re.search(r"\b(cm|centimetri|metr\w*|mt|m)\b", text)
    if not number or not unit:
        return None
    value = _WORDS.get(number.group(), None)
    value = Decimal(number.group()) if value is None else value
    if 'e mezzo' in text:
        value += Decimal('0.5')
    return value * (1 if unit.group().startswith(('cm', 'centim')) else 100)


def measurements(note: str) -> tuple[Measurement, ...]:
    """Every measurement the note records. A number is supplied only where its words print it."""
    found = []
    height = _HEIGHT.search(note)
    height_words = height.group() if height else 'no height printed'
    height_cm = _height_cm(height.group()) if height else None
    for match in _QUANTITY.finditer(note):
        quantity = match.group(1)
        words = f'{match.group(2) or ""} {match.group(7) or ""}'.lower()
        qualifier = ' '.join(q for q in ('circa', 'superiore a', 'oltre') if q in words)
        unit = match.group(3) or match.group(6) or 'no unit printed'
        value = match.group(4) or match.group(5)
        causes = []
        if unit == 'no unit printed':
            causes.append('no unit printed')
        elif match.group(5):
            causes.append(f'the value is printed with a leading separator ("{value}")')
        if not quantity.lower().startswith('diametr'):
            causes.append(f'the quantity printed is "{quantity}", not "diametro"')
        if height and height_cm is None:
            # Supplying no height would read as the criterion's own 130 cm; the diameter is withheld instead.
            causes.append(f'a height is printed ("{height_words}") and its number is not read')
        cause = '; '.join(causes) or None
        diameter = None if cause else Decimal(value.replace(',', '.')) * _TO_CM[unit.lower()]
        found.append(Measurement(quantity, qualifier, value, unit, height_words, diameter,
                                 height_cm, match.group().strip(), cause))
    mention = re.search(r"diametr\w*", note, re.I)
    if mention and not any(m.quantity.lower().startswith('diametr') for m in found):
        # The note names the diameter and no value is read from it: the measurement is unread, not unprinted.
        found.append(Measurement(mention.group(), '', NOT_READ, 'no unit printed', height_words, None, height_cm,
                                 mention.group(), f'{NOT_READ}: the note mentions "{mention.group()}" and no value '
                                                  'is read after it'))
    return tuple(found)


# --- the plant's official monitoring record ---------------------------------------------------

@dataclass(frozen=True)
class MonitoringRecord:
    """The characteristics input: the plant's own record, supplied whatever its identity."""
    observations: tuple[tuple[str, str], ...]   # (reference, day) of the observations read
    flags: tuple[tuple[str, str], ...]          # (view, value as printed) where a view prints a value
    flag_views_blank: tuple[str, ...]           # views that print the field and leave it blank
    flag_views_unprinted: tuple[str, ...]       # views read that do not print the field
    notes: tuple[NoteReading, ...]
    note_views_unprinted: tuple[str, ...]
    measurements: tuple[Measurement, ...]

    @property
    def flag(self) -> str:
        values = sorted({value for _, value in self.flags})
        if values:
            return ' / '.join(values)
        return 'blank' if self.flag_views_blank else 'not printed'


def characteristics_finding(record: MonitoringRecord) -> Evaluation:
    """The row's leaf "the plant's official monitoring record finds the monumental characteristics of L.R. 14/2007
    Article 2: its MONUMENTALE_ARIF flag, or the surveyor's written finding that the plant has monumental
    characteristics", from the record as printed and D's reading of its notes.

    True where the flag prints "Si" or "1", or a note reads "states". False only where every view read prints
    the flag blank and every note reads "does not". Otherwise unknown: a view that does not print the field, or a
    note that reads "unclear", leaves the finding unread. A measurement is not this leaf: it reaches A's
    Art. 2(1)(a) row through `trunk_diameter_facts`.
    """
    if any(value in FLAGS for _, value in record.flags) or any(n.reading == 'states' for n in record.notes):
        return Evaluation(True)
    needs = set()
    if record.flag_views_unprinted and not record.flag_views_blank and not record.flags:
        needs.add('the MONUMENTALE_ARIF flag: no view read prints it for this plant')
    if any(n.reading == 'unclear' for n in record.notes):
        needs.add("the surveyor's finding: a note reads unclear")
    if record.note_views_unprinted and not record.notes and not record.flag_views_blank:
        needs.add('NOTE_RILEVATORE: no view read prints it for this plant')
    return Evaluation(None, needs=frozenset(needs)) if needs else Evaluation(False)


def diameter_inputs(record: MonitoringRecord) -> tuple[dict, ...]:
    """The keyword inputs of `trunk_diameter_facts`, one per diameter the record states, each with its cite."""
    return tuple({'diameter_cm': m.diameter_cm, 'measured_height_cm': m.measured_height_cm}
                 for m in record.measurements if m.quantity.lower().startswith(('diametr', 'dim')))


# --- register entries ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Entry:
    layer: str              # 'listed' (layer 1), 'provisional' (layer 0), or 'deleted' (admitted from a deleting act)
    oid: str                # layer 1's OBJECTID, 'L0/' + layer 0's (the layers' ids overlap), or the deleting act and row
    key: str | None         # COD (layer 1) or COD_UNIVOCO (layer 0), as printed
    card: str | None        # SCHEDAN or N__SCHEDA_RILEVAMENTO, as printed
    label: str | None       # CARSEGNMOT or DGR, as printed
    bulletin: str | None    # APP or BURP, as printed
    comune: str | None
    foglio: str | None
    particella: str | None
    x: float | None         # EPSG:32633
    y: float | None
    survey_date: date | None
    source: str             # sha256 of the page or act the entry is read from

    @property
    def survey(self) -> str:
        if self.survey_date is None or self.survey_date == NOT_RECORDED:
            return 'survey date not recorded'
        return self.survey_date.isoformat()


def _number(text) -> int | None:
    text = str(text or '').strip()
    return int(text) if text.isdigit() else None


def _coordinate(geometry: dict, axis: str) -> float | None:
    value = geometry.get(axis)
    return float(value) if isinstance(value, (int, float)) and value == value and abs(value) != float('inf') else None


def _epoch_day(value) -> date | None:
    if value in (None, ''):
        return None
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).date()


def _blob(store: Path, digest: str) -> Path:
    from .store import blob_path
    path = blob_path(store, digest)
    if not path.exists():
        from cordon_c.core import MissingInput
        raise MissingInput(f'retained register or act bytes: {digest}')
    return path


def register_entries(store: Path, root: Path = REPOSITORY) -> list[Entry]:
    """Every entry of layers 1 and 0 as the retained capture prints it (`register.json`)."""
    record = json.loads((root / SOURCES / 'register.json').read_text())
    entries = []
    for layer in record['layers']:
        for page in layer['pages']:
            for feature in json.loads(_blob(store, page['sha256']).read_bytes())['features']:
                a, g = feature['attributes'], feature.get('geometry') or {}
                if layer['layer'] == 1:
                    entries.append(Entry('listed', str(a['OBJECTID']), a.get('COD'), a.get('SCHEDAN'),
                                         a.get('CARSEGNMOT'), a.get('APP'), a.get('LOCCOM'), a.get('PROPRFG'),
                                         a.get('PROPRPTC'), _coordinate(g, 'x'), _coordinate(g, 'y'), _epoch_day(a.get('RILDATA')),
                                         page['sha256']))
                else:
                    entries.append(Entry('provisional', f"L0/{a['OBJECTID']}", a.get('COD_UNIVOCO'),
                                         a.get('N__SCHEDA_RILEVAMENTO'), a.get('DGR'), a.get('BURP'),
                                         a.get('COMUNE'), None if a.get('FOG_') is None else str(a['FOG_']),
                                         a.get('PART_'), _coordinate(g, 'x'), _coordinate(g, 'y'), _epoch_day(a.get('DATA_RILIEVO')),
                                         page['sha256']))
    return entries


def key_causes(entries: list[Entry]) -> dict[str, tuple[str, ...]]:
    """Each layer 1 key that is blank, repeats, or disagrees with the entry's own card, foglio or particella."""
    counts = Counter(e.key.strip() for e in entries if e.layer == 'listed' and e.key and e.key.strip())
    causes = {}
    for e in entries:
        if e.layer != 'listed':
            continue
        found = []
        key = (e.key or '').strip()
        if not key:
            found.append('COD blank')
        else:
            if counts[key] > 1:
                found.append(f'COD {key} repeats ({counts[key]} entries)')
            parts = key.split('_')
            if len(parts) == 4 and all(p.isdigit() for p in parts):
                for name, printed, own in (('card', parts[0], e.card), ('foglio', parts[1], e.foglio),
                                           ('particella', parts[2], e.particella)):
                    if _number(own) != int(printed):
                        found.append(f'COD {key} disagrees with the {name} {own!r}')
        if found:
            causes[e.oid] = tuple(found)
    return causes


# --- list acts -----------------------------------------------------------------------------------

_MONTHS = {m: i + 1 for i, m in enumerate(('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
                                            'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'))}
# The bulletin line as the act's pages print it: "... Puglia - n. 18 del 21-2-2023" and, on the 2013-2015 acts'
# own BURP pages, "Bollettino ufficiale della Regione Puglia n. 86 del 25/06/2013".
_BULLETIN = re.compile(r"Bollettino Ufficiale della Regione Puglia\s*-?\s*n\.\s*(\d+)(?:\s*suppl\.)?\s*del\s*"
                       r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", re.I)
_ACT = re.compile(r"(\d+|NUMBER)/(\d{4})")


def _title(number: int, year: int) -> re.Pattern:
    return re.compile(rf"DELIBERAZIONE DELLA GIUNTA REGIO-?\s*NALE\s+(\d{{1,2}})\s+(\w+)\s+{year},\s*n\.\s*{number}\b")


def _count(text: str) -> int:
    return int(text.replace('.', ''))


def _canonical(label: str) -> str:
    found = re.search(r"(\d+)\s*/\s*(\d{4})", label or '')
    return f'DGR {int(found.group(1))}/{found.group(2)}' if found else (label or '')


@dataclass(frozen=True)
class ListAct:
    """One L.R. 14/2007 list act as its own published pages state it."""
    act: str                            # 'DGR 1993/2022'
    adopted: date | None
    bulletin: str | None                # 'n. 18 del 21-2-2023', as printed on its pages
    published: date | None
    sha256: str
    pages: tuple[int, ...]
    provisional: int | None             # entries it approves provisionally
    definitive: tuple[tuple[str, int], ...]   # (act whose provisional entries it approves definitively, count)
    deleted: int | None                 # entries it deletes
    table: tuple[tuple[str, int, int, int], ...] = ()  # history table rows (act, provisional, deleted, definitive)
    cause: str | None = None            # why a date is missing
    batches: tuple[int, ...] = ()       # the stated parts of its list its recitals name (the act-chain count rule)
    surveys: tuple[tuple[str, int], ...] = ()  # (survey, trees) each survey its own recitals name, as they count it
    requests: tuple[tuple[str, int], ...] = ()  # (comune, trees) each municipal request its recitals name, as printed


_DECISION = re.compile(r"\bDELIBERA\b")
# The surveys the list acts' recitals name, with the trees each recital counts for this act's list.
SIT = 'SIT srl systematic survey (the 2011 census)'
_SURVEYS = (
    # DGR 1358/2012: "la SIT srl ha restituito, nelle more ..., un elenco parziale di 127.719 esemplari"
    (SIT, re.compile(r"SIT\s+srl\s+ha\s+restituito.{0,160}?elenco\s+par-?\s?ziale\s+di\s+([\d.]+)\s+esemplari")),
    # DGR 357/2013: "la SIT srl ha restituito un elenco definitivo di 300.059 esemplari così costituito: • 127.719
    # esemplari già oggetto di ... DGR n. 1358 ... • 172.340 esemplari validati ..."
    (SIT, re.compile(r"SIT\s+srl\s+ha\s+restituito\s+un\s+elenco\s+definitivo.{0,400}?•\s*[\d.]+\s+esemplari\s+già"
                     r".{0,300}?•\s*([\d.]+)\s+esemplari\s+validati")),
    # DGR 2227/2013: "le ulteriori 1783 piante censite attraverso le rilevazioni della S.I.T."
    (SIT, re.compile(r"([\d.]+)\s+piante\s+censite\s+attraverso\s+le\s+rilevazioni\s+della\s+S\.I\.T\.")),
    # DGR 1358/2012: "LIFE+ Cent.Oli.Med ... sono stati censiti ulteriori 467 ulivi monumentali"
    ('LIFE+ Cent.Oli.Med survey', re.compile(r"Cent\.Oli\.Med.{0,300}?censiti\s+ulteriori\s+([\d.]+)\s+ulivi")),
    # DGR 345/2011: "il Corpo Forestale dello Stato ha rilevato 13049 alberi monumentali"
    ('Corpo Forestale dello Stato survey', re.compile(
        r"Corpo\s+Forestale\s+dello\s+Stato\s+ha\s+(?:rilevato|restituito\s+un\s+elenco\s+di\s+ulivi\s+monumentali\s+"
        r"comprensivo\s+di)\s+([\d.]+)", re.I)),
)
# The municipal requests the recitals name (DGR 2227/2013: "la nota ... del Comune di Casarano che richiede
# l'inserimento di n. 226 ulivi monumentali"). Printed beside the surveys; the reader does not separate their entries.
_REQUEST = re.compile(r"Comune\s+di\s+(\S+(?:\s+\S+){0,3}?)\s+(?:acquisit\w+\s.{0,100}?)?che\s+richied\w+,?\s+"
                      r"(?:tra\s+l.altro,?\s+)?l.inserimento\s+(?:rispettivamente\s+)?di\s+"
                      r"(n\.\s*[\d.]+(?:\s+e\s+n\.\s*[\d.]+)*)\s+ulivi")


def _text_pages(path: Path, number: int, year: int):
    import pymupdf
    document = pymupdf.open(path)
    title = _title(number, year)
    texts = [page.get_text() for page in document]
    # A bulletin's index prints the title too; the act itself starts at the title's last occurrence.
    start = max((i for i, t in enumerate(texts) if title.search(t.replace('\n', ' '))), default=None)
    if start is None:
        return None, ()
    pages = [start]
    for i in range(start + 1, len(texts)):
        other = re.search(r"DELIBERAZIONE DELLA GIUNTA REGIO-?\s*NALE\s+\d{1,2}\s+\w+\s+\d{4},\s*n\.\s*(\d+)",
                          texts[i].replace('\n', ' '))
        if other and int(other.group(1)) != number:
            break
        pages.append(i)
    return [texts[i] for i in pages], tuple(p + 1 for p in pages)


_COLUMNS = (('provisional', re.compile(r"provvisoriamente")), ('deleted', re.compile(r"dall.elenco|eliminati")),
            ('definitive', re.compile(r"definitivamente")))


def _history_rows(path: Path, pages: tuple[int, ...]) -> tuple[tuple[str, int, int, int], ...]:
    """The act's table of list acts, read by column: each number is placed under the heading word nearest it
    horizontally ("provvisoriamente", "dall'elenco"/"eliminati", "definitivamente"), so an empty cell stays empty."""
    import pymupdf
    document = pymupdf.open(path)
    columns, heads, rows = None, {}, []
    for number in pages:
        # Words whose vertical centres lie within 4 pt of the line's first word form one printed line.
        lines = []
        for x0, y0, x1, y1, word, *_ in sorted(document[number - 1].get_text('words'), key=lambda w: (w[1] + w[3]) / 2):
            centre = (y0 + y1) / 2
            if lines and abs(centre - lines[-1][0]) <= 4:
                lines[-1][1].append(((x0 + x1) / 2, word))
            else:
                lines.append((centre, [((x0 + x1) / 2, word)]))
        for _, words in lines:
            words.sort()
            text = ' '.join(w for _, w in words)
            act = re.match(r"/?DGR\s+n\.\s*(\d+)/(\d{4})\b", text)
            if not act:
                # A heading may stack its words over several lines; collect them until a row starts.
                heads |= {name: x for x, w in words for name, p in _COLUMNS if p.search(w)}
                if 'provisional' in heads and 'definitive' in heads:
                    columns = dict(heads)
                continue
            heads = {}
            if not columns:
                continue
            if any(r[0] == f'DGR {int(act.group(1))}/{act.group(2)}' for r in rows):
                return tuple(rows)  # the table has ended; a later passage restates an act
            cells = {}
            for x, w in words:
                if re.fullmatch(r"[\d.]+", w) and not re.fullmatch(r"\d+/\d{4}", w):
                    column = min(columns, key=lambda c: abs(columns[c] - x))
                    cells[column] = _count(w)
            rows.append((f'DGR {int(act.group(1))}/{act.group(2)}', cells.get('provisional', 0),
                         cells.get('deleted', 0), cells.get('definitive', 0)))
    return tuple(rows)


def read_act(path: Path, number: int, year: int, sha256: str) -> ListAct:
    """The act's own statements: its adoption and BURP dates, and what its decision approves or deletes."""
    texts, pages = _text_pages(path, number, year)
    name = f'DGR {number}/{year}'
    if texts is None:
        return ListAct(name, None, None, None, sha256, (), None, (), None, cause='the act is not found in the capture')
    whole = '\n'.join(texts)
    flat = re.sub(r"\s+", ' ', whole)
    title = _title(number, year).search(flat)
    adopted = date(year, _MONTHS[title.group(2).lower()], int(title.group(1))) if title and \
        title.group(2).lower() in _MONTHS else None
    bulletin = _BULLETIN.search(re.sub(r"\s+", ' ', texts[0])) or _BULLETIN.search(flat)
    published = date(int(bulletin.group(4)), int(bulletin.group(3)), int(bulletin.group(2))) if bulletin else None
    printed = f'n. {bulletin.group(1)} del {bulletin.group(2)}-{bulletin.group(3)}-{bulletin.group(4)}' if bulletin else None
    decision = flat[_DECISION.search(flat).start():] if _DECISION.search(flat) else flat
    provisional = re.search(r"approvare\s+(?:il\s+nuovo\s+l.)?\s*(?:in\s+via\s+provvisoria\s+n\.\s*([\d.]+)|"
                            r"elenco\s+provvisorio.{0,160}?costituito\s+da\s+([\d.]+))|"
                            # 2013-2015: "di aggiornare [esclusivamente] l'elenco provvisorio / non definitivo ...
                            # costituito da 1204 esemplari"
                            r"aggiornare\s+(?:esclusivamente\s+)?l.elenco\s+(?:provvisorio|non\s+definitivo).{0,200}?"
                            r"costituito\s+da\s+([\d.]+)", decision)
    definitive = []
    for found in re.finditer(r"approvare\s+in\s+via\s+definitiva\s+(?:ai\s+sensi\s+dell.articolo\s+6\s+della\s+L\.R\.\s+"
                             r"n\.\s*14/2007\s+e\s+s\.m\.i\.\s+)?(n\.\s*[\d.]+(?:\s+e\s+n\.\s*[\d.]+)?)\s+ulivi\s+"
                             r"monumentali\s+di\s+cui.{0,160}?DGR\s+n\.\s*(\d+/\d{4}(?:\s+e\s+\d+/\d{4})?)", decision):
        counts = [_count(c) for c in re.findall(r"n\.\s*([\d.]+)", found.group(1))]
        acts = [f'DGR {a}' for a in re.findall(r"\d+/\d{4}", found.group(2))]
        if len(counts) == len(acts):
            definitive += [pair for pair in zip(acts, counts) if pair not in definitive]
    deleted = re.search(r"eliminare\s+dall.elenco\s+regionale\s+(?:approvato\s+)?(?:ex\s+art\.\s*5\s+della\s+L\.r\.\s*"
                        r"14/07\s+e\s+s\.m\.i\.,\s*)?n\.\s*([\d.]+)", decision)
    table = _history_rows(path, pages)
    recitals = flat[:_DECISION.search(flat).start()] if _DECISION.search(flat) else flat
    # The surveys the recitals name as making up the act's provisional list (DGR 1358/2012: "un elenco parziale di
    # 127.719 esemplari" from SIT srl, and "censiti ulteriori 467 ulivi monumentali" under LIFE+ Cent.Oli.Med).
    batches = tuple(_count(next(g for g in m.groups() if g)) for m in re.finditer(
        r"elenco\s+par-?\s?ziale\s+di\s+([\d.]+)\s+esemplari|censiti\s+ulteriori\s+([\d.]+)\s+ulivi", recitals))
    # The surveys are read from the act's own recitals, from its title on (a page may open on another act's end).
    own = flat[title.start():] if title else flat
    own = own[:_DECISION.search(own).start()] if _DECISION.search(own) else own
    surveys = tuple(dict.fromkeys((survey, _count(m.group(1))) for survey, pattern in _SURVEYS
                                  for m in pattern.finditer(own)))
    requests = tuple((m.group(1), _count(n)) for m in _REQUEST.finditer(own)
                     for n in re.findall(r"n\.\s*([\d.]+)", m.group(2)))
    return ListAct(name, adopted, printed, published, sha256, pages,
                   _count(next(g for g in provisional.groups() if g)) if provisional else None,
                   tuple(definitive), _count(deleted.group(1)) if deleted else None, table,
                   None if published else 'the capture prints no BURP date for the act', batches, surveys, requests)


def list_acts(store: Path, root: Path = REPOSITORY) -> dict[str, ListAct]:
    """Every held list act, read from the latest successful capture that carries it."""
    acts = {}
    for record in json.loads((root / SOURCES / 'acts.json').read_text()):
        if not record.get('sha256'):
            continue
        for number, year in {(int(n), int(y)) for n, y in re.findall(r"DGR (\d+)/(\d{4})", record['purpose'])}:
            act = read_act(_blob(store, record['sha256']), number, year, record['sha256'])
            if act.pages or f'DGR {number}/{year}' not in acts:
                acts[act.act] = act
    return acts


# --- each entry's chain of acts ------------------------------------------------------------------

@dataclass(frozen=True)
class Chain:
    """An entry's act history, from the acts. `listing_facts` takes it through `listing_inputs`."""
    provisional: ListAct | None
    definitive: ListAct | None
    deletion: ListAct | None
    rule: str                     # how the acts assign the entry
    complete: bool                # every act of the history is held with its date
    cause: str | None = None


def history_table(acts: dict[str, ListAct]) -> tuple[tuple[str, int, int, int], ...]:
    """The latest held act table of the list's history (DGR 1193/2021 states its table replaces DGR 1491/2020's)."""
    held = [a for a in acts.values() if len(a.table) >= 5 and a.published]
    return max(held, key=lambda a: a.published).table if held else ()


def definitive_of(acts: dict[str, ListAct]) -> dict[str, list[tuple[str, int]]]:
    """For each provisional act, the acts that approved its entries definitively, with counts.

    From each act's own decision where it names the provisional act; for older rows, from the history table: a
    row's definitive count covers the pending provisional acts before it when it equals their sum, or the one
    pending act when only one is pending.
    """
    covered = defaultdict(list)
    for act in acts.values():
        for provisional, count in act.definitive:
            covered[provisional].append((act.act, count))
    pending = []
    for name, provisional, _, definitive in history_table(acts):
        if definitive:
            open_acts = [p for p in pending if p[0] not in covered]
            if open_acts and sum(c for _, c in open_acts) == definitive:
                for p, c in open_acts:
                    covered[p].append((name, c))
                pending = [p for p in pending if p not in open_acts]
            elif len(open_acts) == 1:
                covered[open_acts[0][0]].append((name, definitive))
                pending.remove(open_acts[0])
        if provisional:
            pending.append((name, provisional))
    return covered


def _survey_groups(entries: list[Entry]) -> list[list[Entry]]:
    """An act's entries split by survey: survey date not recorded, then contiguous dated spans (gap > 1 year)."""
    groups = [[e for e in entries if e.survey == 'survey date not recorded']]
    dated = sorted((e for e in entries if e.survey != 'survey date not recorded'), key=lambda e: e.survey_date)
    span = []
    for e in dated:
        if span and (e.survey_date - span[-1].survey_date).days > 366:
            groups.append(span)
            span = []
        span.append(e)
    groups.append(span)
    return [g for g in groups if g]


def act_chains(entries: list[Entry], acts: dict[str, ListAct]) -> tuple[dict[str, Chain], list[str]]:
    """Each entry's provisional, definitive and deleting act, read from the acts, never from the label alone.

    The label (`CARSEGNMOT`, layer 0 `DGR`) names an act. The acts say what that act did: approve its own batch
    provisionally, and approve definitively the batches of earlier acts. Per survey group of the label's entries,
    the batch whose stated count is nearest the group's count is the one the group belongs to; the counts are
    printed beside the rule. Returns the chains and the printed checks.
    """
    covered = definitive_of(acts)
    table = {row[0]: row for row in history_table(acts)}
    stated = {}
    for name, act in acts.items():
        stated[name] = act
    for name in table:
        stated.setdefault(name, None)
    by_label = defaultdict(list)
    for e in entries:
        if e.layer != 'deleted':
            by_label[(e.layer, _canonical(e.label))].append(e)
    chains, checks = {}, []
    for (layer, label), members in sorted(by_label.items()):
        own = acts.get(label)
        alias = None
        if label not in stated:
            number, year = label.split(' ')[1].split('/')
            near = [n for n in stated if n.startswith(f'DGR {number}/') and abs(int(n[-4:]) - int(year)) == 1]
            if len(near) == 1:
                alias, label = label, near[0]
                own = acts.get(label)
        provisional_count = (own.provisional if own else None) or (table.get(label, (None, None))[1])
        options = []  # (count, provisional act, definitive act)
        if provisional_count:
            finals = covered.get(label, [])
            final = finals[0][0] if len(finals) == 1 else None
            options.append((provisional_count, label, final))
            # The surveys the act's recitals name, when together they make up exactly its provisional list, are
            # stated parts of that act's list (not survey batches), with the same provisional and definitive acts.
            parts = own.batches if own else ()
            if len(parts) > 1 and sum(parts) == provisional_count:
                options += [(part, label, final) for part in parts]
        if layer == 'listed':  # layer 0 holds provisional entries only
            for p, c in [(p, c) for p, pairs in covered.items() for d, c in pairs if d == label]:
                options.append((c, p, label))
        for group in _survey_groups(members):
            span = group[0].survey if group[0].survey == group[-1].survey else f'{group[0].survey}..{group[-1].survey}'
            head = (f'layer {layer}, label {alias or label}' + (f' (the acts print {label})' if alias else '') +
                    f'; survey group {span}, {len(group)} entries')
            fitting = [o for o in options if abs(o[0] - len(group)) <= TOLERANCE * o[0]]
            if len(options) == 1:
                (count, prov, final), = options
                rule = f'{head}; the one batch the acts state for {label}: {count}'
            elif len({(p, f) for _, p, f in fitting}) == 1:
                count, prov, final = fitting[0]
                within = ' and '.join(str(c) for c, _, _ in fitting)
                rule = (f'{head}; the one stated batch within {TOLERANCE:.0%} of the group: {within}, from '
                        + '; '.join(f'{c} provisional by {p}' for c, p, _ in options))
            else:
                prov = final = None
                rule = (f'{head}; unknown between the stated batches ' +
                        '; '.join(f'{c} provisional by {p}' for c, p, _ in options) if options else
                        f'{head}; no held act or table row states what {label} did')
            if prov:
                rule += (f'; approved provisionally by {prov}' +
                         (f', definitively by {final}' if final else ', no definitive act'))
            checks.append(rule)
            for e in group:
                p_act = acts.get(prov) if prov else None
                d_act = acts.get(final) if final else None
                missing = [n for n, a in ((prov, p_act), (final, d_act)) if n and (a is None or a.published is None)]
                chains[e.oid] = Chain(p_act, d_act, None, rule, not missing and prov is not None,
                                      f'not held with a BURP date: {", ".join(missing)}' if missing else None)
    return chains, checks


def listing_inputs(chain: Chain, *, own_entry: bool = True) -> dict:
    """The keyword inputs of `cordon_c.bindings.listing_facts` for one entry."""
    return {
        'own_entry': own_entry,
        'first_publication': chain.provisional.published if chain.provisional else None,
        'definitive_decision': (chain.definitive.published, True) if chain.definitive and chain.definitive.published else None,
        'deletion': chain.deletion.published if chain.deletion else None,
        'entry_history_complete': chain.complete,
    }


# --- notes that print a code ----------------------------------------------------------------------

_CODE = re.compile(r"\d{4,}")


@dataclass(frozen=True)
class NoteCode:
    plant: str
    code: str                 # as printed
    entry: str | None         # the entry it names, or None
    cause: str                # 'names entry' or why it names nothing


def note_codes(plants: dict[str, tuple[str, float, float, tuple[str, ...]]], entries: list[Entry],
               d_of) -> list[NoteCode]:
    """The note-code rule. A run of four or more digits names an entry only when it equals, as a number, exactly one
    card in the plant's comune, that entry lies within d of the plant (`d_of(plant, entry)`), and no other plant's
    note prints that code. `plants` maps a plant to (comune, x, y, notes)."""
    cards = defaultdict(list)
    for e in entries:
        number = _number(e.card)
        if number is not None and e.comune:
            cards[(e.comune.strip().upper(), number)].append(e)
    # A printer is the observations whose notes a plant carries, so an order plant carrying its positive's note
    # and that positive count once. A plant given as (comune, x, y, notes) is its own printer.
    printers = defaultdict(set)
    for plant, (_, _, _, notes, *sources) in plants.items():
        for note in notes:
            for code in _CODE.findall(note):
                printers[int(code)].add(tuple(sources[0]) if sources and sources[0] else plant)
    found = []
    for plant, (comune, x, y, notes, *_) in plants.items():
        seen = set()
        for note in notes:
            for code in _CODE.findall(note):
                if (int(code)) in seen:
                    continue
                seen.add(int(code))
                hits = cards.get(((comune or '').strip().upper(), int(code)), [])
                if len(printers[int(code)]) > 1:
                    cause = f'printed by {len(printers[int(code)])} plants'
                elif not hits:
                    cause = 'no card in the comune'
                elif len(hits) > 1:
                    cause = f'{len(hits)} cards in the comune'
                elif hits[0].x is None or ((hits[0].x - x) ** 2 + (hits[0].y - y) ** 2) ** 0.5 > d_of(plant, hits[0]):
                    cause = 'entry beyond d'
                else:
                    found.append(NoteCode(plant, code, hits[0].oid, 'names entry'))
                    continue
                found.append(NoteCode(plant, code, None, cause))
    return found


# --- the register's positional error, per survey batch ----------------------------------------------

@dataclass(frozen=True)
class Fix:
    observation: str
    entry: str
    batch: str
    distance_m: float
    observation_error_m: float
    codes: tuple[tuple[str, str], ...]
    dropped: str | None       # why the pair is not a reference fix

    @property
    def residual_m(self) -> float:
        return self.distance_m + self.observation_error_m


@dataclass(frozen=True)
class BatchBound:
    """The positional qualification of the entries of one survey batch."""
    batch: str
    card_form: str            # 'census tag' or 'survey-card number'
    applies: str              # the batch, or 'register-wide (fewer than 20 fixes)'
    error_m: float
    statistic: str
    fixes: int
    method: str
    check: str | None = None  # the 2011 contract's 1.00 m check, where it applies
    observations: tuple[str, ...] = ()  # the reference fixes the bound is computed from (their observations)


def reference_fixes(flagged: list[tuple[str, str, float, float, float, tuple[str, ...]]], entries: list[Entry],
                    batch_of, tag_batches: set[str]) -> list[Fix]:
    """Monitoring residuals: a flagged olive observation and a listed entry that are each other's nearest, in the same
    comune, within 50 m. `flagged` holds (observation, comune, x, y, error_m, notes). A pair is dropped only when a
    code in its note names another entry (the note-code rule at d = 50 m, the pairing radius), or when the entry's
    batch uses the census tag as its card and the tag the note prints differs from the card."""
    import numpy
    from scipy.spatial import cKDTree
    listed = [e for e in entries if e.layer == 'listed' and e.x is not None]
    grid = numpy.array([[e.x, e.y] for e in listed])
    tree = cKDTree(grid)
    points = numpy.array([[f[2], f[3]] for f in flagged])
    ptree = cKDTree(points)
    plants = {f[0]: (f[1], f[2], f[3], f[5]) for f in flagged}
    codes = defaultdict(list)
    for code in note_codes(plants, entries, lambda plant, entry: PAIRING_M):
        codes[code.plant].append(code)
    fixes = []
    for j, (observation, comune, x, y, error_m, notes) in enumerate(flagged):
        distance, i = tree.query([x, y])
        if distance > PAIRING_M or ptree.query(grid[i])[1] != j:
            continue
        entry = listed[i]
        if (entry.comune or '').strip().upper() != (comune or '').strip().upper():
            continue
        printed = codes.get(observation, [])
        other = [c for c in printed if c.cause == 'names entry' and c.entry != entry.oid]
        batch = batch_of(entry)
        tags = [c for c in printed if not re.search(r"\bid\b\W*$", ' '.join(notes).lower().split(c.code)[0][-12:])]
        differs = batch in tag_batches and any(int(c.code) != _number(entry.card) for c in tags)
        dropped = (f'its note names entry {other[0].entry}' if other else
                   f'the note prints tag {tags[0].code}, the card is {entry.card}' if differs else None)
        fixes.append(Fix(observation, entry.oid, batch, float(distance), error_m,
                         tuple((c.code, c.cause) for c in printed), dropped))
    return fixes


def contract_terms(store: Path, root: Path = REPOSITORY) -> tuple[float, str, str] | None:
    """The 2011 census tender's stated position tolerance, read from its held capitolato d'oneri (CIG 1154723B8D):
    (metres, Art. 3 point 4 as printed, sha256), or None where the bytes are not held."""
    import pymupdf
    for record in json.loads((root / SOURCES / 'acts.json').read_text()):
        if record.get('sha256') and 'CIG 1154723B8D' in record['purpose']:
            text = re.sub(r"\s+", ' ', '\n'.join(p.get_text() for p in pymupdf.open(_blob(store, record['sha256']))))
            point = re.search(r"4\. (la posizione delle singole piante.{0,400}?superiore ad (\d+) \((\w+)\) metro)", text)
            if point:
                return float(point.group(2)), point.group(1), record['sha256']
    return None


def batch_bounds(fixes: list[Fix], batches: set[str], tag_batches: set[str], *,
                 contract_batch: set[str] = frozenset(), contract: tuple[float, str, str] | None = None
                 ) -> dict[str, BatchBound]:
    import numpy
    kept = [f for f in fixes if f.dropped is None]
    method = ('95th percentile of monitoring residuals: distance from a flagged olive observation to the listed '
              'entry that is its mutual nearest, same comune, within 50 m, plus the observation\'s own error_m')
    wide = [f.residual_m for f in kept]
    register_wide = float(numpy.percentile(wide, 95)) if wide else None
    bounds = {}
    for batch in batches:
        mine = [f for f in kept if f.batch == batch]
        own = [f.residual_m for f in mine]
        form = 'census tag' if batch in tag_batches else 'survey-card number'
        if len(own) >= MIN_FIXES:
            bound = BatchBound(batch, form, batch, round(float(numpy.percentile(own, 95)), 2), '95th percentile',
                               len(own), method, observations=tuple(f.observation for f in mine))
        else:
            bound = BatchBound(batch, form, f'register-wide ({len(own)} fixes in this batch, fewer than {MIN_FIXES})',
                               round(register_wide, 2), '95th percentile', len(wide), method,
                               observations=tuple(f.observation for f in kept))
        if batch in contract_batch and contract:
            metres, quotation, sha256 = contract
            check = (f"2011 census contract rep. 013042 (CIG 1154723B8D), capitolato d'oneri Art. 3 point 4 (sha256 "
                     f"{sha256[:12]}): \"{quotation}\". ")
            if len(own) >= MIN_FIXES:
                # The contract's tolerance checks the census's own measured bound, never replaces it.
                tolerance = metres + max(f.observation_error_m for f in mine)
                excess = bound.error_m - tolerance
                check += (f"{metres:.2f} m plus the reference fix's own {tolerance - metres:.2f} m = "
                          f"{tolerance:.2f} m; the census's own bound is {bound.error_m:.2f} m: " +
                          ('within' if excess <= 0 else f'exceeded by {excess:.2f} m') +
                          '. The measured bound stands either way.')
            else:
                check += (f"Not checked: the census has {len(own)} fixes, under {MIN_FIXES}, and takes the "
                          "register-wide bound." + (
                              f" The census residuals' own 95th percentile, {float(numpy.percentile(own, 95)):.2f} "
                              f"m over its {len(own)} fixes, is information only." if own else ''))
            bound = BatchBound(**{**bound.__dict__, 'check': check})
        bounds[batch] = bound
    return bounds


# --- survey batches and deleted entries ----------------------------------------------------------

def named_survey(group: list[Entry], act: ListAct | None) -> tuple[str | None, str]:
    """The survey the recitals of the act that first listed the group name for it, and the rule that decides it.

    A survey whose recital count is within 5% of the group's is the group's. Where none fits, a group whose entries
    print survey dates belongs to the one survey the act's recitals name, if they name exactly one, and the two
    counts are printed. Otherwise the recitals name no survey for the group. Where recitals that name a survey also
    name a municipal request, the request and its count are printed: this reader does not separate its entries from
    the survey's, and an undated group keeps its label, since the two cannot be told apart by date."""
    named = act.surveys if act else ()
    head = f'{len(group)} entries first listed by {act.act if act else "no held act"}'
    requests = act.requests if act and named else ()
    request = '' if not requests else (
        ' and ' + ('a municipal request, ' if len(requests) == 1 else 'municipal requests, ') +
        '; '.join(f'Comune di {c} ({n})' for c, n in requests) + ', which this reader does not separate')
    fitting = {s for s, c in named if abs(c - len(group)) <= TOLERANCE * c}
    if len(fitting) == 1:
        survey, = fitting
        counts = ' and '.join(str(c) for s, c in named if s == survey)
        return survey, (f'{head}; its recitals count {counts} for {survey}, within {TOLERANCE:.0%}' +
                        (f'; they also name{request[4:]}' if request else ''))
    surveys = {s for s, _ in named}
    if not fitting and len(surveys) == 1 and group[0].survey != 'survey date not recorded':
        survey, = surveys
        counts = ' and '.join(str(c) for _, c in named)
        return survey, (f'{head}, with survey dates; its recitals name {survey} ({counts}){request}; {survey} is '
                        'the one source they name whose entries print survey dates: the counts do not fit, and '
                        'the group is taken as that survey')
    return None, (f'{head}; its recitals name ' + ('; '.join(f'{s} ({c})' for s, c in named) or 'no survey') +
                  request + ('' if not named else ', and no survey count fits the group alone') +
                  ('; the group prints no survey dates, so this reader cannot tell the survey\'s entries from the '
                   'request\'s by date, and the group keeps its label'
                   if request and group[0].survey == 'survey date not recorded' else ''))


def survey_batches(entries: list[Entry], chains: dict[str, Chain]) -> tuple[dict[str, str], list[str]]:
    """Each entry's survey batch: the survey the list acts' recitals name (`named_survey`), one batch across every
    label that carries it. Where they name none, the act label and the entry's own survey date, split where the
    dates of one label leave a gap of more than a year; an undated entry is 'survey date not recorded'. Returns the
    batches and the printed rule of each group."""
    by_label = defaultdict(list)
    for e in entries:
        by_label[(e.layer == 'deleted', _canonical(e.label))].append(e)
    batches, rules = {}, []
    for (deleted, label), members in sorted(by_label.items()):
        for group in _survey_groups(members):
            first, last = group[0].survey, group[-1].survey
            span = first if first == last or first == 'survey date not recorded' else f'{first[:4]}..{last[:4]}'
            name = f'{label}, {"survey date not recorded" if span == "survey date not recorded" else "surveyed " + span}'
            if deleted:
                for e in group:
                    batches[e.oid] = f'deleted by {e.oid.split("#")[0]}: its annex prints no survey'
                continue
            acts = {chains[e.oid].provisional for e in group if e.oid in chains}
            survey, rule = named_survey(group, next(iter(acts))) if len(acts) == 1 else (
                None, f'{len(group)} entries first listed by several acts')
            rules.append(f'label {label}, survey group {span}: {rule}; batch: {survey or name}')
            name = survey or name
            for e in group:
                batches[e.oid] = name
    return batches, rules


_GLYPH_DIGITS = {chr(0x3EC + i): str(i) for i in range(10)} | {'ͺ': '_', '͘': '.'}
# Key, then easting (six digits) and northing (seven digits); the page sometimes prints a space after the point.
# The key is the census key SCHEDAN_foglio_particella_ISTAT, an AppOLEA number (printed with the glyphs of "APP_"),
# or "n. d." (printed with the glyphs of "n. d.": no card).
_DELETED_ROW = re.compile(r"(?:(\d+)_(\d+)_(\S+?)_(\d{6})|\x04WW_(\d+)|(Ŷ\. Ě\.))\S*\s+"
                          r"(\d{6}(?:\s?\.\s?\d+)?)\S*\s+(\d{7}(?:\s?\.\s?\d+)?)")


def deleted_entries(store: Path, acts: dict[str, ListAct]) -> tuple[list[Entry], list[str]]:
    """Entries a deleting act lists with the census key and the point it prints (EPSG:32633).

    DGR 720/2025's Allegato B prints each deleted tree's key SCHEDAN_foglio_particella_ISTAT and its UTM
    coordinates in a font whose digits the text layer maps to consecutive code points (U+03EC..U+03F5), with
    U+037A for '_' and U+0358 for '.'; the mapping is read from the page, not guessed per row. A deleted tree is
    no longer in layer 1, but it was listed until its deletion was published. Returns the entries and the causes
    of rows not read."""
    import pymupdf
    found, unread = [], []
    for act in acts.values():
        if not act.deleted or not act.pages:
            continue
        document = pymupdf.open(_blob(store, act.sha256))
        rows = 0
        for page in act.pages:
            text = ''.join(_GLYPH_DIGITS.get(c, c) for c in document[page - 1].get_text()).replace('\x03', '')
            for match in _DELETED_ROW.finditer(text):
                card, foglio, particella, istat, app, missing, x, y = match.groups()
                rows += 1
                key = '_'.join((card, foglio, particella, istat)) if card else f'APP_{app}' if app else None
                found.append(Entry('deleted', f'{act.act}#{rows}', key, card or (f'APP_{app}' if app else None),
                                   None, None, istat, foglio, particella, float(x.replace(' ', '')),
                                   float(y.replace(' ', '')), None, act.sha256))
        if rows != act.deleted:
            unread.append(f'{act.act} deletes {act.deleted} entries; {rows} rows print a key and a point')
    return found, unread


# --- candidates ------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Candidates:
    plant: str
    entries: tuple[tuple[str, float, float], ...]   # (entry, distance m, d m) for every entry within its d
    identity: str        # an entry, 'unknown', or 'not a register tree'
    rule: str


def candidates(plant: str, x: float, y: float, error_m: float, entries_near, bound_of, named: list[NoteCode]) -> Candidates:
    """"Not a register tree" is always a candidate; so is every entry within d = the plant's error_m plus the
    entry's batch bound. A note code that names an entry decides; otherwise the identity stays unknown."""
    within = []
    for entry in entries_near:
        d = round(error_m + bound_of(entry).error_m, 2)
        distance = ((entry.x - x) ** 2 + (entry.y - y) ** 2) ** 0.5
        if distance <= d:
            within.append((entry.oid, round(distance, 2), d))
    naming = [c for c in named if c.cause == 'names entry']
    if naming and any(c.entry == oid for c in naming for oid, _, _ in within):
        entry = next(c.entry for c in naming)
        return Candidates(plant, tuple(within), entry, f'its note prints code {naming[0].code}, which names entry {entry}')
    if not within:
        return Candidates(plant, (), 'not a register tree', 'no entry within d')
    return Candidates(plant, tuple(within), 'unknown',
                      'unknown between the entries within d and "not a register tree": no record names the entry')


# --- the population: affected plants, their zone entries and zone negatives ------------------------------

MONITORING = 'corpus/sources/monitoring'
ORDERS = 'corpus/sources/removal-orders/records.json'
_ANNEX_ROW = re.compile(r"(\d{1,2}[.,]\d{4,})\s+(\d{2}[.,]\d{4,})")  # longitude and latitude as the annex prints them
_OLIVE = re.compile(r"olea|oliv", re.I)


def printing_views(root: Path = REPOSITORY) -> dict[str, frozenset[str]]:
    """The monitoring views whose own layer description prints each field."""
    views = defaultdict(set)
    for path in (root / MONITORING / 'sit').glob('*/*/*/layer.json'):
        layer = json.loads(path.read_text())
        name = json.loads((path.parent / 'release.json').read_text()).get('name')
        for f in layer.get('fields') or ():
            if f['name'] in ('MONUMENTALE_ARIF', 'NOTE_RILEVATORE'):
                views[f['name']].add(name)
    return {k: frozenset(v) for k, v in views.items()}


def monitoring_record(groups, printing: dict[str, frozenset[str]]) -> MonitoringRecord:
    """The record of one plant from its observations, every view read, nothing chosen."""
    flags, blank, unprinted, notes, note_unprinted = set(), set(), set(), {}, set()
    for group in groups:
        for member in group.members:
            values = dict(member.carried) | dict(member.attributes)
            flag = (values.get('MONUMENTALE_ARIF') or '').strip()
            if flag:
                flags.add((member.view, flag))
            elif member.view in printing.get('MONUMENTALE_ARIF', ()):
                blank.add(member.view)
            else:
                unprinted.add(member.view)
            note = (values.get('NOTE_RILEVATORE') or '').strip()
            if note:
                notes.setdefault(note, read_note(note))
            elif member.view not in printing.get('NOTE_RILEVATORE', ()):
                note_unprinted.add(member.view)
    readings = tuple(notes[n] for n in sorted(notes))
    return MonitoringRecord(tuple(sorted({(g.reference or '', g.day.isoformat() if g.day else '') for g in groups})),
                            tuple(sorted(flags)), tuple(sorted(blank)), tuple(sorted(unprinted)), readings,
                            tuple(sorted(note_unprinted)),
                            tuple(m for r in readings for m in measurements(r.note)))


def order_points(store: Path, root: Path = REPOSITORY) -> list[tuple[str, float, float]]:
    """Each plant point an order's annex prints (longitude, latitude), from the text layer of every held order."""
    import pymupdf
    records = json.loads((root / ORDERS).read_text())
    held = sorted({r['sha256'] for r in records if r.get('sha256') and 'error' not in r})
    points = []
    for digest in held:
        seen = set()
        for page in pymupdf.open(_blob(store, digest)):
            for match in _ANNEX_ROW.finditer(page.get_text()):
                a, b = (float(v.replace(',', '.')) for v in match.group(1, 2))
                lon, lat = (a, b) if a < b else (b, a)
                if 15 < lon < 19 and 39 < lat < 42.5 and (lon, lat) not in seen:
                    seen.add((lon, lat))
                    points.append((digest, lon, lat))
    return points


@dataclass(frozen=True)
class Plant:
    plant: str
    kind: str                  # 'in-reach positive', 'order plant', 'negative olive'
    x: float                   # EPSG:32633, the recorded position as metric_point returns it
    y: float
    error_m: float             # as metric_point returns it
    comune: str | None
    record: MonitoringRecord
    order: str | None = None   # the order whose annex prints the plant
    coincides: tuple[str, ...] = ()  # the positives an order plant coincides with (within 1 m)


def affected_plants(store: Path, decision: date, reach_start: date, root: Path = REPOSITORY):
    """The infected plants (in-reach positives and the plants the held orders print), and every in-reach negative
    olive, each with its metric point and its monitoring record. One pass over the monitoring stream."""
    import numpy
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    from .monitoring import distinct_observations, located_observations
    from .spatial import metric_point, positional_qualification, positional_terms
    terms = positional_terms(store, root)
    printing = printing_views(root)
    context = 'protected-status: identity of an affected plant'

    def metric(group):
        observation = next(located_observations([group]), None)
        if observation is None:
            return None
        point = metric_point(observation, context=context, event_date=decision, root=store,
                             qualification=positional_qualification(observation, context=context,
                                                                    event_date=decision, terms=terms))
        return point.geometry.x, point.geometry.y, point.error_m

    positives, negatives = [], []
    for group in distinct_observations(root / MONITORING):
        if group.positive is True:
            placed = metric(group)
            if placed:
                positives.append((group, placed))
        elif group.positive is False and group.day and group.day >= reach_start and \
                any(_OLIVE.search(s) for s in group.values('species')) and group.locations:
            negatives.append(group)

    def comune(group):
        names = {n.strip().upper() for n in group.values('COMUNE') if n and n.strip()}
        return next(iter(names)) if len(names) == 1 else None

    plants = []
    in_reach = [(g, p) for g, p in positives if g.day and g.day >= reach_start]
    repeated = Counter(g.reference for g, _ in in_reach)
    for group, (x, y, error) in in_reach:
        # A plant is named by its observation's reference; a reference two observations share keeps its day.
        name = group.reference if group.reference and repeated[group.reference] == 1 else '@'.join(
            str(v) for v in group.identity[1:])
        plants.append(Plant(name, 'in-reach positive', x, y, error, comune(group), monitoring_record([group], printing)))
    grid = numpy.array([[p[0], p[1]] for _, p in positives])
    tree = cKDTree(grid)
    reach_tree = cKDTree(numpy.array([[p.x, p.y] for p in plants]))
    to_metric = Transformer.from_crs('EPSG:4326', 'EPSG:32633', always_xy=True)
    # One plant per set of coincident positives that order points share, however many orders print it and
    # however their printed coordinates differ.
    parent = {}

    def root_of(i):
        while parent.setdefault(i, i) != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    points = []
    for digest, lon, lat in order_points(store, root):
        x, y = to_metric.transform(lon, lat)
        if reach_tree.query([x, y])[0] <= 1.0:
            continue  # the same plant as an in-reach positive
        hits = tree.query_ball_point([x, y], 1.0)
        if hits:
            points.append((f'{digest[:12]}@{lon},{lat}', hits))
            for i in hits[1:]:
                parent[root_of(i)] = root_of(hits[0])
    ordered = {}
    for printed, hits in points:
        entry = ordered.setdefault(root_of(hits[0]), (set(), []))
        entry[0].update(hits)
        entry[1].append(printed)
    for hits, printed in ((sorted(h), p) for h, p in ordered.values()):
        hits = [positives[i] for i in hits]
        first = min(hits, key=lambda h: h[0].day or date.max)
        gx, gy, error = first[1]
        plants.append(Plant(printed[0], 'order plant', gx, gy, error, comune(first[0]),
                            monitoring_record([h[0] for h in hits], printing), ' '.join(sorted(set(printed))),
                            tuple(sorted(h[0].reference or '' for h in hits))))
    return plants, negatives, terms, printing


def zone_negatives(negatives, infected: list[Plant], decision: date, terms, printing, root: Path = REPOSITORY,
                   store: Path | None = None):
    """The negative olives C may place in an infected plant's 50 m zone: within 50 m plus both errors."""
    import numpy
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    from .monitoring import located_observations
    from .spatial import metric_point, positional_qualification
    context = 'protected-status: identity of an affected plant'
    tree = cKDTree(numpy.array([[p.x, p.y] for p in infected]))
    reach = 50.0 + 2 * max(p.error_m for p in infected)
    transformers, found = {}, []
    for group in negatives:
        crs, (u, v) = group.locations[0]
        if crs not in transformers:
            transformers[crs] = Transformer.from_crs(crs, 'EPSG:32633', always_xy=True)
        x, y = transformers[crs].transform(u, v)
        if not tree.query_ball_point([x, y], reach + 1.0):
            continue
        observation = next(located_observations([group]))
        point = metric_point(observation, context=context, event_date=decision, root=store,
                             qualification=positional_qualification(observation, context=context,
                                                                    event_date=decision, terms=terms))
        near = tree.query_ball_point([point.geometry.x, point.geometry.y], 50.0 + point.error_m + max(p.error_m for p in infected))
        if near:
            found.append(Plant(group.reference or '|'.join(group.identity[1:]), 'negative olive', point.geometry.x,
                               point.geometry.y, point.error_m, None, monitoring_record([group], printing)))
    return found


def read(store: Path, decision: date, reach_start: date, root: Path = REPOSITORY, population=None) -> dict:
    """Row 9 over the held sources: every affected plant and zone negative with its record, candidates and d, and
    every zone entry with its acts, dates, batch and qualification. `population` is `affected_plants`' result
    when the caller already holds it."""
    import numpy
    from scipy.spatial import cKDTree
    acts = list_acts(store, root)
    entries = register_entries(store, root)
    deleted, unread = deleted_entries(store, acts)
    chains, checks = act_chains(entries, acts)
    for e in deleted:
        act = next(a for a in acts.values() if e.oid.startswith(a.act + '#'))
        chains[e.oid] = Chain(None, None, act, f'listed until {act.act} deleted it (its annex prints the key and point)',
                              False, 'the deleting act prints no approving act for the entry')
    everything = entries + deleted
    batches, batch_rules = survey_batches(everything, chains)
    causes = key_causes(entries)
    plants, negatives, terms, printing = population or affected_plants(store, decision, reach_start, root)
    infected = plants
    zone_neg = zone_negatives(negatives, infected, decision, terms, printing, root, store)
    # The census tag names cards only in batches whose cards the held notes' tags name (the note-code rule).
    note_map = {p.plant: (p.comune, p.x, p.y, tuple(n.note for n in p.record.notes), p.record.observations)
                for p in infected}
    tag_names = note_codes(note_map, everything, lambda plant, entry: PAIRING_M)
    oid_batch = batches
    tag_batches = {oid_batch[c.entry] for c in tag_names if c.cause == 'names entry'}
    flagged = [(p.plant, p.comune, p.x, p.y, p.error_m, tuple(n.note for n in p.record.notes)) for p in infected
               if p.kind == 'in-reach positive' and any(v in FLAGS for _, v in p.record.flags)]
    fixes = reference_fixes(flagged, everything, lambda e: oid_batch[e.oid], tag_batches)
    # The 2011 census contract's batch: the SIT srl systematic survey the list acts' recitals name.
    bounds = batch_bounds(fixes, set(oid_batch.values()), tag_batches, contract_batch={SIT},
                          contract=contract_terms(store, root))
    located = [e for e in everything if e.x is not None]
    etree = cKDTree(numpy.array([[e.x, e.y] for e in located]))
    widest = max(b.error_m for b in bounds.values())
    bound_of = lambda e: bounds[oid_batch[e.oid]]  # noqa: E731
    d_of_plant = {p.plant: p.error_m for p in infected + zone_neg}
    all_plants = infected + zone_neg
    codes = note_codes({p.plant: (p.comune, p.x, p.y, tuple(n.note for n in p.record.notes), p.record.observations)
                        for p in all_plants},
                       everything, lambda plant, entry: d_of_plant[plant] + bound_of(entry).error_m)
    codes_of = defaultdict(list)
    for c in codes:
        codes_of[c.plant].append(c)
    out_plants, zone_entries = [], set()
    for p in all_plants:
        near = [located[i] for i in etree.query_ball_point([p.x, p.y], p.error_m + widest)]
        cand = candidates(p.plant, p.x, p.y, p.error_m, near, bound_of, codes_of.get(p.plant, []))
        out_plants.append((p, cand))
        if p.kind != 'negative olive':
            for i in etree.query_ball_point([p.x, p.y], 50.0 + p.error_m + widest):
                e = located[i]
                if ((e.x - p.x) ** 2 + (e.y - p.y) ** 2) ** 0.5 <= 50.0 + p.error_m + bound_of(e).error_m:
                    zone_entries.add(e.oid)
        zone_entries.update(oid for oid, _, _ in cand.entries)
    by_oid = {e.oid: e for e in everything}
    return {'acts': acts, 'checks': checks, 'unread_deletions': unread, 'entries': by_oid, 'chains': chains,
            'batches': oid_batch, 'batch_rules': batch_rules, 'bounds': bounds, 'fixes': fixes, 'key_causes': causes,
            'plants': out_plants, 'codes': codes, 'zone_entries': zone_entries, 'tag_batches': tag_batches,
            'terms': terms, 'decision': decision}


# --- the emitted rows -------------------------------------------------------------------------------

def _act(act: ListAct | None) -> dict | None:
    return None if act is None else {'act': act.act, 'adopted': act.adopted and act.adopted.isoformat(),
                                     'bulletin': act.bulletin, 'published': act.published and act.published.isoformat(),
                                     'source': act.sha256, 'pages': list(act.pages[:1] + act.pages[-1:])}


def rows(result: dict) -> dict:
    """The emitted inputs, as JSON: every affected plant and zone negative, and every zone entry."""
    entries, chains, batches, bounds = result['entries'], result['chains'], result['batches'], result['bounds']
    codes = defaultdict(list)
    for c in result['codes']:
        codes[c.plant].append({'code': c.code, 'entry': c.entry, 'cause': c.cause})
    plants = []
    for p, c in result['plants']:
        r = p.record
        plants.append({
            'plant': p.plant, 'kind': p.kind, 'order': p.order, 'coincides_with': list(p.coincides),
            'point': {'x': round(p.x, 2), 'y': round(p.y, 2), 'crs': 'EPSG:32633', 'error_m': p.error_m},
            'comune': p.comune, 'observations': [list(o) for o in r.observations],
            'flag': {'printed': [list(f) for f in r.flags], 'blank_in_views': list(r.flag_views_blank),
                     'not_printed_in_views': list(r.flag_views_unprinted), 'as_printed': r.flag},
            'notes': [{'note': n.note, 'reading': n.reading, 'cite': n.cite, 'cause': n.cause} for n in r.notes]
            or [{'note': None, 'reading': 'does not', 'cause': 'no note printed',
                 'views_not_printing': list(r.note_views_unprinted)}],
            'measurements': [{'quantity': m.quantity, 'qualifier': m.qualifier, 'value': m.value, 'unit': m.unit,
                              'height': m.height, 'diameter_cm': m.diameter_cm and str(m.diameter_cm),
                              'measured_height_cm': m.measured_height_cm and str(m.measured_height_cm),
                              'cite': m.cite, 'cause': m.cause} for m in r.measurements],
            'codes': codes.get(p.plant, []),
            'candidates': {'not a register tree': True,
                           'entries': [{'entry': e, 'distance_m': dist, 'd_m': d} for e, dist, d in c.entries],
                           'd': f"the plant's error_m {p.error_m} m + the entry's batch bound",
                           'identity': c.identity, 'rule': c.rule}})
    terms = result['terms']
    reference_fix_sources = [s.identity for s in (terms.device_source, terms.award_source, terms.region_source)]
    zone = []
    for oid in sorted(result['zone_entries'], key=lambda o: (entries[o].layer, o)):
        e, chain, bound = entries[oid], chains.get(oid), bounds[batches[oid]]
        at = f'bounds[{batches[oid]!r}]'  # the method, the 2011 check and the reference fixes are emitted there once
        zone.append({
            'entry': oid, 'layer': e.layer, 'key': e.key, 'card': e.card, 'key_causes': list(result['key_causes'].get(oid, ())),
            'label': e.label, 'bulletin_printed': e.bulletin, 'comune': e.comune, 'foglio': e.foglio,
            'particella': e.particella, 'point': {'x': e.x, 'y': e.y, 'crs': 'EPSG:32633'}, 'survey': e.survey,
            'source': e.source, 'batch': batches[oid],
            'qualification': {'applies_to': bound.applies, 'card_form': bound.card_form, 'error_m': bound.error_m,
                              'statistic': bound.statistic, 'fixes': bound.fixes, 'method': f'{at}.method',
                              'reference_fix_error_m': terms.error_m, 'check': bound.check and f'{at}.check',
                              'date': result['decision'].isoformat(),
                              'sources': {'entry_point': e.source,
                                          'reference_fixes': f'{at}.reference_fixes',
                                          'reference_fix_error': reference_fix_sources}},
            'acts': None if chain is None else {
                'provisional': _act(chain.provisional), 'definitive': _act(chain.definitive),
                'deletion': _act(chain.deletion), 'rule': chain.rule, 'history_complete': chain.complete,
                'cause': chain.cause}})
    return {'plants': plants, 'zone_entries': zone,
            'acts': [_act(a) | {'provisional': a.provisional, 'definitive_of': [list(d) for d in a.definitive],
                                'deleted': a.deleted, 'surveys': [list(s) for s in a.surveys]}
                     for a in result['acts'].values()],
            'chain_checks': result['checks'], 'survey_batches': result['batch_rules'],
            'unread_deletions': result['unread_deletions'],
            'reference_fixes': [{'observation': f.observation, 'entry': f.entry, 'batch': f.batch,
                                 'distance_m': round(f.distance_m, 2), 'observation_error_m': f.observation_error_m,
                                 'codes': [list(c) for c in f.codes], 'dropped': f.dropped} for f in result['fixes']],
            'bounds': {b: {'applies_to': v.applies, 'error_m': v.error_m, 'fixes': v.fixes, 'card_form': v.card_form,
                           'method': v.method, 'check': v.check, 'reference_fixes': list(v.observations)}
                       for b, v in sorted(bounds.items())},
            'tag_batches': sorted(result['tag_batches'])}

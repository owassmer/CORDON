"""Row 9's instruments besides the L.R. 14/2007 register: the elenco degli alberi monumentali d'Italia (L. 10/2013
Art. 7) and the declarations of notable public interest (D.lgs. 42/2004 Art. 136, and L. 1497/1939 declarations
Art. 157 keeps in force).

D supplies, for each instrument, its population held whole per version; each listed or declared tree as a plant
record with its position, species and positional error; its placement against the 50 m zones of the in-reach
positives, as row 9 places register entries; and, for each plant, the instruments it is in at the event date
(`instrument_facts`, the hook the coordinator's A rows read, one fact per instrument kind).

A decides when a decree takes effect: D carries each decree's own date and its publication date and does not choose
between them. A declaration gives a tree status only where its motivation names the tree; one that protects an area
gives none (Art. 33(1)'s first paragraph lifts that constraint; #37's ruling, #47's plan).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
import io
import json
from pathlib import Path
import re

REPOSITORY = Path(__file__).resolve().parents[3]
SOURCES = 'corpus/sources/protected-status'
NATIONAL = 'L. 10/2013 Art. 7: elenco degli alberi monumentali d\'Italia'
DECLARATION = 'D.lgs. 42/2004 Art. 136(1)(a): declaration naming the tree'
REGISTER = 'L.R. 14/2007: monumental-olive register'
ZONE_M = 50.0          # B-PAR-EU-4(2)-sub1-infected-zone-50m, as row 9 places register entries
LIST_FLOOR_M = 50.0    # the plan's floor for the national list's bound where fewer than MIN_FIXES fixes are held
MIN_FIXES = 20         # the NSSDA minimum of check points, as row 9's batch bounds
REGION_CODE = '16'     # the last part of a scheda ID: the ISTAT region code every row of the Puglia sheet prints


def _blob(store: Path, digest: str) -> Path:
    from .store import blob_path
    path = blob_path(store, digest)
    if not path.exists():
        from cordon_c.core import MissingInput
        raise MissingInput(f'retained instrument bytes: {digest}')
    return path


def _metric(lon: float, lat: float) -> tuple[float, float]:
    from pyproj import Transformer
    global _TO_METRIC
    try:
        transformer = _TO_METRIC
    except NameError:
        transformer = _TO_METRIC = Transformer.from_crs('EPSG:4326', 'EPSG:32633', always_xy=True)
    return transformer.transform(lon, lat)


# --- the national list: decrees and their annexes ---------------------------------------------------------------

_MONTHS = {m: i + 1 for i, m in enumerate(('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
                                            'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'))}
# "prot. n. 661 del 09/08/2018, pubblicato in G.U. n. 231 del 04/10/2018", as MASAF's list page prints each decree.
_SENTENCE = re.compile(r"prot\.\s*n\.\s*(\d+)\s+del\s+(\d{1,2})(?:/(\d{1,2})/|\s+(\w+)\s+)(\d{4}),\s*pubblicat\w\s+in\s+"
                       r"G\.\s*U\.\s*n\.\s*(\d+)\s+del\s+(\d{1,2})/(\d{1,2})/(\d{4})", re.I)
# The G.U.'s own title of the notice: "DECRETO 24 luglio 2026 ... (GU Serie Generale n.182 del 07-08-2026)".
_GU_TITLE = re.compile(r"DECRETO\s+(\d{1,2})\s+(\w+)\s+(\d{4}).*?\(GU Serie Generale n\.\s*(\d+) del (\d{2})-(\d{2})-(\d{4})\)",
                       re.S)
_SCHEDA = re.compile(rf"\b(\d{{2,3}})\s*/\s*([A-Z]\d{{3}})\s*/\s*([A-Z]{{2}})\s*/\s*{REGION_CODE}\b")
# An annex as its decree page labels it, or as the decree's own pages head it where the page links no annex.
_SECTIONS = ((re.compile(r'Sezione\s*2', re.I), 'A2'), (re.compile(r'Allegato\s+A', re.I), 'A'),
             (re.compile(r'Allegato\s+B', re.I), 'B'), (re.compile(r'Allegato\s+C', re.I), 'C'))
_HEADING = re.compile(r'ALLEGATO\s+([ABC])\s*[‐\-–]')
SECTION_MEANING = {'A': 'listed (approved list or additions)', 'A2': 'adopted pending formalisation, not listed',
                   'B': 'deleted', 'C': 'data corrected'}


def _page_text(raw: bytes) -> str:
    import html
    text = raw.decode('utf-8', errors='replace')
    text = re.sub(r'<script.*?</script>|<style.*?</style>', '', text, flags=re.S)
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', text)))


def _document_text(raw: bytes) -> list[str]:
    """The text of a held document, one string per page or sheet: PDF text layers, spreadsheet cells."""
    if raw[:4] == b'%PDF':
        import pymupdf
        return [page.get_text() for page in pymupdf.open(stream=raw, filetype='pdf')]
    if raw[:2] == b'PK':
        import openpyxl
        book = openpyxl.load_workbook(io.BytesIO(raw), read_only=True)
        return ['\n'.join(' | '.join('' if c is None else str(c) for c in row) for row in sheet.iter_rows(values_only=True))
                for sheet in book.worksheets]
    import xlrd
    book = xlrd.open_workbook(file_contents=raw)
    return ['\n'.join(' | '.join(str(c) for c in sheet.row_values(r)) for r in range(sheet.nrows)) for sheet in book.sheets()]


def _schede(text: str) -> dict[str, str]:
    """Each of the region's scheda IDs a text prints, with its row: the text from the ID to the next scheda ID."""
    found = list(re.finditer(r'\b\d{2,3}\s*/\s*[A-Z]\d{3}\s*/\s*[A-Z]{2}\s*/\s*\d{2}\b', text))
    rows = {}
    for i, m in enumerate(found):
        own = _SCHEDA.match(text, m.start())
        if own:
            end = found[i + 1].start() if i + 1 < len(found) else min(len(text), m.end() + 600)
            rows.setdefault('/'.join(own.groups()) + '/' + REGION_CODE, text[m.end():end])
    return rows


@dataclass(frozen=True)
class Decree:
    number: str                  # prot. n. as MASAF prints it
    adopted: date                # the decree's own date, as the G.U. titles it (MASAF's where no notice prints one)
    gazette: str                 # its G.U. issue
    published: date              # its G.U. publication date
    sources: tuple[str, ...]     # sha256 of MASAF's list page, the decree page and the G.U. notice
    sections: dict = field(default_factory=dict, compare=False, hash=False)  # section -> {scheda ID: its row}
    annexes: tuple[tuple[str, str], ...] = ()   # (section, sha256) of each document read for the sections
    checks: tuple[str, ...] = ()
    protocol: date | None = None   # the protocol date MASAF names the decree by

    @property
    def name(self) -> str:
        return f'decree prot. n. {self.number} of {self.adopted.isoformat()}'

    def as_json(self) -> dict:
        return {'decree': self.name, 'number': self.number, 'adopted': self.adopted.isoformat(),
                'protocol': self.protocol and self.protocol.isoformat(),
                'gazette': self.gazette, 'published': self.published.isoformat(), 'sources': list(self.sources),
                'annexes': [list(a) for a in self.annexes],
                'sections': {k: len(v) for k, v in sorted(self.sections.items())}, 'checks': list(self.checks)}


def _norm(number: str) -> str:
    return number.lstrip('0') or '0'


def decrees(store: Path, root: Path = REPOSITORY) -> tuple[list[Decree], list[str]]:
    """Every decree MASAF's list page names, dated from that page and from the G.U.'s own notice, with the
    region's scheda IDs each of its annexes prints. A disagreement between the two dates is a check."""
    record = json.loads((root / SOURCES / 'national-list.json').read_text())
    list_page = record['pages'][0]
    stated = {}
    for m in _SENTENCE.finditer(_page_text(_blob(store, list_page['sha256']).read_bytes())):
        number, day, month_n, month_w, year, gu, gd, gm, gy = m.groups()
        month = int(month_n) if month_n else _MONTHS[month_w.lower()]
        stated[_norm(number)] = (number, date(int(year), month, int(day)), gu, date(int(gy), int(gm), int(gd)))
    notices = defaultdict(list)
    for n in record['notices']:
        if n.get('sha256') and 'caricaDettaglioAtto' in n['url']:
            notices[_norm(n['decree'])].append(n['sha256'])
    pages = {p['url']: p for p in record['pages'] if p.get('label')}
    documents = defaultdict(list)
    for d in record['documents']:
        if d.get('sha256') and d.get('page') in pages:
            documents[d['page']].append(d)
    found, problems = [], []
    for url, page in pages.items():
        label = re.search(r'N\.\s*(\d+)', page['label'])
        if not label or _norm(label.group(1)) not in stated:
            continue
        number, protocol, gu, published = stated[_norm(label.group(1))]
        adopted = protocol
        checks, sources = [], [list_page['sha256'], page['sha256']]
        for digest in notices.get(_norm(number), []):
            title = _GU_TITLE.search(_page_text(_blob(store, digest).read_bytes()))
            sources.append(digest)
            if not title:
                checks.append(f'the G.U. notice {digest[:12]} prints no decree date and issue')
                continue
            d, mo, y, n, gd, gm, gy = title.groups()
            adopted = date(int(y), _MONTHS[mo.lower()], int(d))
            if (n, date(int(gy), int(gm), int(gd))) != (gu, published):
                checks.append(f'the G.U. notice prints G.U. n. {n} of {gd}-{gm}-{gy}; MASAF prints G.U. n. {gu} of '
                              f'{published}')
            if adopted != protocol:
                checks.append(f'the G.U. titles the decree {adopted}; MASAF names it by its protocol of {protocol}')
        if len(sources) == 2:
            checks.append('no G.U. notice is held')
        sections, annexes = defaultdict(dict), []
        linked = [d for d in documents[url] if not d['label'].startswith('D.M.')]
        for d in linked:
            section = next((s for pattern, s in _SECTIONS if pattern.search(d['label'])), None)
            if section:
                for scheda, row in _schede('\n'.join(_document_text(_blob(store, d['sha256']).read_bytes()))).items():
                    sections[section].setdefault(scheda, row)
                annexes.append((section, d['sha256']))
        if not linked:
            # The page links the decree alone: its annexes are its own pages, headed "ALLEGATO A/B/C -".
            for d in documents[url]:
                section = None
                for text in _document_text(_blob(store, d['sha256']).read_bytes()):
                    for part in re.split(r'(?=ALLEGATO\s+[ABC]\s*[‐\-–])', text):
                        heading = _HEADING.match(part)
                        section = heading.group(1) if heading else section
                        if section:
                            for scheda, row in _schede(part).items():
                                sections[section].setdefault(scheda, row)
                annexes.extend((s, d['sha256']) for s in sorted(sections))
        if not annexes:
            problems.append(f'{number}: no annex is held')
        found.append(Decree(number, adopted, f'G.U. n. {gu}', published, tuple(sources), dict(sections),
                            tuple(annexes), tuple(checks), protocol))
    missing = set(stated) - {_norm(d.number) for d in found}
    problems += [f'decree prot. n. {stated[m][0]}: MASAF names it and no decree page is held' for m in sorted(missing)]
    return sorted(found, key=lambda d: (d.adopted, d.published)), problems


# --- the national list: entries -----------------------------------------------------------------------------------

_DMS = re.compile(r"(\d+)\s*°\s*(\d+)\s*['’′]\s*(\d+(?:[.,]\d+)?)?")
_KINDS = (('insieme omogeneo', re.compile(r'^\s*insieme\s+omogeneo\b', re.I)), ('filare', re.compile(r'^\s*filar[ei]\b', re.I)),
          ('alberata', re.compile(r'^\s*alberat[ae]\b|^\s*viale\b', re.I)), ('gruppo', re.compile(r'^\s*gruppo\b', re.I)))
_MEMBERS = re.compile(r'\(?\s*n\.?\s*(\d+)\s+(?:esemplari|alberi|piante)\b', re.I)


def degrees(printed) -> float | None:
    found = _DMS.search(str(printed or ''))
    if not found:
        return None
    d, m, s = found.groups()
    return int(d) + int(m) / 60 + float((s or '0').replace(',', '.')) / 3600


@dataclass(frozen=True)
class ListEntry:
    scheda: str
    province: str
    comune: str
    place: str
    latitude: str              # as printed (WGS 84 degrees, minutes, seconds; the census instructions)
    longitude: str
    x: float | None            # EPSG:32633
    y: float | None
    species: str               # as printed
    kind: str                  # 'single tree', 'insieme omogeneo', 'filare', 'alberata' or 'gruppo', from the species cell
    members: str               # as printed, or 'not printed'
    circumference: str
    height: str
    proposal: str              # PROPOSTA DICHIARAZIONE NOTEVOLE INTERESSE PUBBLICO, as printed
    sheet: str                 # 'listed' (the current sheet) or 'deleted' (its Eliminazioni sheet)
    stated_deletion: str | None  # RIFERIMENTO LEGISLATIVO, as the Eliminazioni sheet prints it
    source: str
    listed_by: Decree | None = None
    deleted_by: Decree | None = None
    corrected_by: tuple[Decree, ...] = ()
    printed_as: tuple[tuple[str, str, str], ...] = ()   # (decree, annex, ID) where an annex prints another ID
    causes: tuple[str, ...] = ()

    @property
    def genus(self) -> str | None:
        return _genus(self.species)


def _genus(species: str | None) -> str | None:
    if not species:
        return None
    name = re.sub(r'^\s*(insieme\s+omogeneo|filare|alberata|gruppo|viale)\s+(di|del|della|dei)\s+', '', species, flags=re.I)
    found = re.match(r'\s*([A-Z][a-z]+)\b', name)
    return found.group(1) if found else None


def list_entries(store: Path, root: Path = REPOSITORY) -> tuple[list[ListEntry], list[Decree], list[str]]:
    """Every entry the current regional sheet prints, listed or deleted, with the decree whose annex lists it, the
    decree whose annex deletes it and each decree whose annex corrects it."""
    import xlrd
    record = json.loads((root / SOURCES / 'national-list.json').read_text())
    sheet_record = next(d for d in record['documents'] if d['purpose'].startswith('the current'))
    book = xlrd.open_workbook(file_contents=_blob(store, sheet_record['sha256']).read_bytes())
    held, problems = decrees(store, root)
    entries = []
    for sheet in book.sheets():
        header = [str(c).strip() for c in sheet.row_values(0)]
        column = {name: header.index(name) for name in header}
        kind = 'deleted' if sheet.name.strip().lower().startswith('elimin') else 'listed'
        for r in range(1, sheet.nrows):
            row = sheet.row_values(r)
            value = lambda name: '' if name not in column else str(row[column[name]]).strip()  # noqa: E731
            scheda = value('ID SCHEDA')
            if not scheda:
                continue
            lat, lon = degrees(value('LATITUDINE SU GIS')), degrees(value('LONGITUDINE SU GIS'))
            x, y = _metric(lon, lat) if lat is not None and lon is not None else (None, None)
            species = re.sub(r'\s+', ' ', value('SPECIE NOME SCIENTIFICO'))
            members = _MEMBERS.search(species + ' ' + value('LOCALITÀ'))
            entries.append(ListEntry(
                scheda, value('PROVINCIA'), value('COMUNE'), value('LOCALITÀ'), value('LATITUDINE SU GIS'),
                value('LONGITUDINE SU GIS'), x, y, species,
                next((k for k, pattern in _KINDS if pattern.search(species)), 'single tree'),
                members.group(0) if members else 'not printed', value('CIRCONFERENZA FUSTO (cm)'), value('ALTEZZA (m)'),
                value('PROPOSTA DICHIARAZIONE NOTEVOLE INTERESSE PUBBLICO'), kind,
                value('RIFERIMENTO LEGISLATIVO') or None, sheet_record['sha256']))
    # An annex can print an entry under an ID a later correction changed (a comune's code): the same progressive
    # number and province, on a row that prints the entry's coordinates, or its comune and place.
    by_scheda = {e.scheda: e for e in entries}
    alias = {}
    for d in held:
        for section, rows in d.sections.items():
            for printed, row in rows.items():
                if printed in by_scheda:
                    continue
                number, _, province, _ = printed.split('/')
                folded, digits = _fold(row), re.sub(r'\D', '', row)
                same = [e for e in entries if e.scheda.split('/')[0] == number and e.scheda.split('/')[2] == province
                        and ((re.sub(r'\D', '', e.latitude) and re.sub(r'\D', '', e.latitude) in digits
                              and re.sub(r'\D', '', e.longitude) in digits)
                             or (_fold(e.comune) in folded and _fold(e.place)[:20] in folded))]
                if len(same) == 1:
                    alias[(d.number, section, printed)] = same[0].scheda
                elif section in ('A', 'B'):
                    problems.append(f'{d.name} annex {section} prints {printed}, which the current sheet does not' +
                                    (f' (it could be any of {", ".join(e.scheda for e in same)})' if same else ''))

    def printing(d: Decree, section: str, scheda: str) -> str | None:
        if scheda in d.sections.get(section, {}):
            return scheda
        return next((printed for (n, sec, printed), own in alias.items()
                     if n == d.number and sec == section and own == scheda), None)

    out = []
    for e in entries:
        causes = []
        if not e.scheda.endswith('/' + REGION_CODE):
            causes.append(f'the scheda ID does not end with the region code {REGION_CODE}')
        listing = [d for d in held if printing(d, 'A', e.scheda)]
        deleting = [d for d in held if printing(d, 'B', e.scheda)]
        pending = [d for d in held if printing(d, 'A2', e.scheda)]
        if len(listing) > 1:
            causes.append('listed by more than one decree: ' + ', '.join(d.name for d in listing))
        if not listing:
            causes.append('no held annex lists the entry' + (' (adopted pending formalisation by '
                                                              + pending[0].name + ')' if pending else ''))
        if e.sheet == 'deleted' and not deleting:
            causes.append('the sheet prints it deleted and no held annex deletes it')
        if e.sheet == 'listed' and deleting:
            causes.append('the sheet prints it listed and a held annex deletes it: ' + deleting[0].name)
        stated = re.search(r'N\.?\s*(\d+)', e.stated_deletion or '')
        if stated and deleting and _norm(stated.group(1)) != _norm(deleting[0].number):
            causes.append(f'the sheet states deletion by "{e.stated_deletion}"; the annex deleting it is '
                          f'{deleting[0].name}')
        if e.x is None:
            causes.append('the sheet prints no position ("' + e.latitude + '", "' + e.longitude + '")')
        printed_as = tuple((d.name, section, printed) for d in held for section in d.sections
                           for printed in [printing(d, section, e.scheda)] if printed and printed != e.scheda)
        out.append(ListEntry(**{**e.__dict__, 'listed_by': listing[0] if listing else None,
                                'deleted_by': deleting[0] if deleting else None,
                                'corrected_by': tuple(d for d in held if printing(d, 'C', e.scheda)),
                                'printed_as': printed_as, 'causes': tuple(causes)}))
    return out, held, problems


def in_force(entry: ListEntry, at: date) -> tuple[bool | None, str]:
    """Whether an entry is in the version of the list in force at `at`. A decides whether a decree takes effect on
    its own date or on its G.U. publication; where `at` falls between the two, D does not choose."""
    if entry.listed_by is None:
        return None, 'no held annex lists the entry, so the version that first holds it is not known'

    def effect(decree: Decree | None) -> bool | None:
        if decree is None:
            return False
        if decree.published <= at and decree.adopted <= at:
            return True
        if decree.published > at and decree.adopted > at:
            return False
        return None
    on, off = effect(entry.listed_by), effect(entry.deleted_by)
    if on is False:
        return False, f'first listed by {entry.listed_by.name} (G.U. {entry.listed_by.published}), after the event date'
    if off is True:
        return False, f'deleted by {entry.deleted_by.name} (G.U. {entry.deleted_by.published}) before the event date'
    if on is True and off is False:
        return True, f'listed by {entry.listed_by.name} (G.U. {entry.listed_by.published}) and not deleted at the event date'
    pending = [d for d, v in ((entry.listed_by, on), (entry.deleted_by, off)) if v is None]
    return None, '; '.join(f'the event date falls between {d.name} and its G.U. publication of {d.published}: A '
                           f'decides when the decree takes effect' for d in pending)


# --- the national list's positional error ---------------------------------------------------------------------

@dataclass(frozen=True)
class ListBound:
    error_m: float
    fixes: int
    statistic: str
    sources_searched: tuple[str, ...]


# The held sources searched for an independent position of a listed tree, each with why it yields none today.
INDEPENDENT_SOURCES = (
    'the L.R. 14/2007 register: it lists olives, and the national list prints no Olea',
    'the Art. 136 declarations: no declared tree is a listed tree (same comune and genus)',
    "the Corpo forestale's 1982 census (MASAF): it prints place names and no position",
)


def list_bound(residuals: list[float], searched=INDEPENDENT_SOURCES) -> ListBound:
    """The bound of a scheda point: residuals of scheda coordinates against independent positions of the same trees.
    With fewer than MIN_FIXES fixes, the larger of the measured maximum and LIST_FLOOR_M; otherwise their 95th
    percentile, as row 9's batch bounds."""
    import numpy
    if len(residuals) < MIN_FIXES:
        measured = max(residuals) if residuals else None
        return ListBound(round(max(measured or 0.0, LIST_FLOOR_M), 2), len(residuals),
                         f'larger of the measured maximum ({"none" if measured is None else f"{measured:.2f} m"}) and '
                         f'{LIST_FLOOR_M:.0f} m: fewer than {MIN_FIXES} fixes', tuple(searched))
    return ListBound(round(float(numpy.percentile(residuals, 95)), 2), len(residuals), '95th percentile of the fixes',
                     tuple(searched))


def declared_residuals(entries: list[ListEntry], declared: list['Declaration']) -> list[float]:
    """A fix is a listed tree and a declared tree in the same comune and of the same genus: the distance from the
    scheda point to the declaration's polygon."""
    from shapely.geometry import Point
    out = []
    for d in declared:
        for e in entries:
            if e.x is not None and d.genus and e.genus == d.genus and _fold(e.comune) == _fold(d.comune):
                out.append(d.geometry.distance(Point(e.x, e.y)))
    return out


def _fold(name: str | None) -> str:
    import unicodedata
    text = unicodedata.normalize('NFKD', name or '').encode('ascii', 'ignore').decode().upper()
    return re.sub(r'[^A-Z]', '', text)


# --- the Art. 136 declarations ----------------------------------------------------------------------------------

# The delimitation's scale as the PPTR states it (NTA: the Art. 136 areas "come delimitate nelle tavole della sezione
# 6.3.1", 54 sheets at 1:50,000, "rappresentate con precisione validata alla scala ivi indicata").
STATED_SCALE = 50_000
# No source states a ground tolerance at that scale. 1 mm at the stated scale is D's choice: a smaller term could
# leave out of a zone a declared tree the zone reaches, which would clear its removal.
SCALE_TERM_M = STATED_SCALE / 1000.0
FIELD_LENGTH = 254     # MOTIVAZI_1's field length in the layer description: a motivation this long may be cut
# Words that name one tree, as D reads a motivation: a measurement of a trunk or crown, the tree itself, or a single
# specimen. "Alto fusto", the plural "esemplari", a quantified "qualche esemplare" (a few specimens of a wood) and a
# species named for a crop or a wood name no tree.
_NAMES_TREE = re.compile(r"\b(circonferenza|tronco|chioma)\b|\bl'albero\b|\bdell'albero\b|\bun albero\b|"
                         r"(?<!qualche )(?<!ogni )(?<!ciascun )(?<!alcun )(?<!nessun )\besemplare\b|"
                         r"\balbero monumentale\b|\bpianta monumentale\b", re.I)
_NAMES_GROUP = re.compile(r"\bfilar[ei]\b|\balberata\b|\bviale alberato\b|\bgrupp\w* di (alberi|piante|querce|pini|"
                          r"lecci|cipressi|platani|olivi|ulivi|carrubi)\b|\balberi monumentali\b", re.I)
_TREE_WORDS = {'quercia': 'Quercus', 'querce': 'Quercus', 'leccio': 'Quercus', 'lecci': 'Quercus', 'roverella': 'Quercus',
               'vallonea': 'Quercus', 'sughera': 'Quercus', 'fragno': 'Quercus', 'pino': 'Pinus', 'pini': 'Pinus',
               'cipresso': 'Cupressus', 'carrubo': 'Ceratonia', 'olivo': 'Olea', 'ulivo': 'Olea', 'platano': 'Platanus',
               'cedro': 'Cedrus', 'tiglio': 'Tilia', 'olmo': 'Ulmus', 'palma': 'Phoenix', 'fico': 'Ficus',
               'gelso': 'Morus', 'castagno': 'Castanea', 'faggio': 'Fagus', 'tasso': 'Taxus', 'alloro': 'Laurus'}
_GU_PUBLICATION = re.compile(r'G\.\s*U\.\s*n\.\s*(\d*)\s*d\w*\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})', re.I)
_DECREE_DATE = re.compile(r'(\d{1,2})-(\d{1,2})-(\d{4})')


@dataclass(frozen=True)
class Declaration:
    code: str                     # CODICE, the PPTR's identifier (PAE...)
    sitap: str | None             # COD_SITAP, the Ministry's code
    comune: str
    obj: str                      # OGGETTO__1, as printed
    motivation: str               # MOTIVAZI_1, as printed
    decree_date: str              # NUMERO_DEC, as printed: the decree's date
    publication: str              # PUBBLICATO, as printed: its G.U. publication or its notification
    law: str                      # ID_VINCOLI, as printed
    letter: str                   # ART_136_C, the PPTR's classification, as printed
    versions: tuple[str, ...]     # the PPTR versions that print it
    geometry: object              # the union of its rows' polygons, EPSG:32633
    source: tuple[str, ...]       # sha256 of the layer pages it is read from
    reading: str                  # 'names a tree' | 'names a row or group' | 'area' | 'not read whole'
    cite: str | None
    genus: str | None             # of the tree the motivation names, from its words
    decree: dict | None = None    # the held decree document, or the route state

    @property
    def area_m2(self) -> float:
        return float(self.geometry.area)

    def published(self) -> date | None:
        """The date of its G.U. publication or of its notification, as the layer prints the first of them."""
        found = _GU_PUBLICATION.search(self.publication or '')
        if found:
            return date(int(found.group(4)), int(found.group(3)), int(found.group(2)))
        found = _DECREE_DATE.search(self.publication or '')
        return date(int(found.group(3)), int(found.group(2)), int(found.group(1))) if found else None

    def adopted(self) -> date | None:
        found = _DECREE_DATE.search(self.decree_date or '')
        return date(int(found.group(3)), int(found.group(2)), int(found.group(1))) if found else None


# The layer prints a note about publication where it holds no motivation.
_NO_MOTIVATION = re.compile(r'^\s*$|^\(?\s*D\.M\.\s+non\s+pubblicato', re.I)
# An object that names the protected thing as an area: a zone, a territory, a coast, a wood, a villa or its park.
_AREA_OBJECT = re.compile(r'\b(zona|zone|area|aree|territori\w*|costa|costiera|bosco|boschi|villa|parco|giardino|'
                          r'complesso|localit\w+|tratto|fascia|pineta|valle|isol\w+|contrada|centro)\b', re.I)


def read_motivation(obj: str, motivation: str) -> tuple[str, str | None, str | None]:
    """D's reading of a declaration's object and motivation: whether it names a tree, a row or group, or an area.
    Returns (reading, the words it rests on, the genus of the tree it names). A motivation at the field's full
    length may be cut and is not read whole unless it names a tree; where the layer prints no motivation, an object
    naming an area is read as one, and any other is not read."""
    absent = bool(_NO_MOTIVATION.search(motivation or ''))
    text = f'{obj or ""} {"" if absent else motivation or ""}'
    for reading, pattern in (('names a tree', _NAMES_TREE), ('names a row or group', _NAMES_GROUP)):
        found = pattern.search(text)
        if found:
            words = re.findall(r"[A-Za-zÀ-ÿ']+", text.lower())
            genus = next((_TREE_WORDS[w.split("'")[-1]] for w in words if w.split("'")[-1] in _TREE_WORDS), None)
            return reading, found.group(0), genus
    if absent:
        found = _AREA_OBJECT.search(obj or '')
        return ('area', f'the object: {found.group(0)}', None) if found else ('not read whole', 'no motivation printed', None)
    if len(motivation or '') >= FIELD_LENGTH - 4:
        return 'not read whole', motivation[-40:], None
    return 'area', None, None


def combined(*readings: tuple[str, str | None, str | None]) -> tuple[str, str | None, str | None]:
    """One declaration's readings, the most whole text first (its decree's, the PPTR scheda's, the layer's). A text
    that names a tree, a row or a group decides, whichever prints it; otherwise the first reading stands."""
    naming = [r for r in readings if r[0] in ('names a tree', 'names a row or group')]
    return naming[0] if naming else readings[0]


def _esri_polygon(rings):
    """An ArcGIS polygon: clockwise rings are exteriors, counter-clockwise rings holes of the exterior holding them."""
    from shapely import union_all
    from shapely.geometry import LinearRing, Polygon
    exteriors, holes = [], []
    for ring in rings:
        if len(ring) < 4:
            continue
        (holes if LinearRing(ring).is_ccw else exteriors).append(ring)
    polygons = []
    for ring in exteriors:
        shell = Polygon(ring)
        inner = [h for h in holes if shell.contains(Polygon(h).representative_point())]
        polygons.append(Polygon(ring, inner).buffer(0))
    return union_all(polygons)


def declarations(store: Path, root: Path = REPOSITORY) -> tuple[list[Declaration], list[dict], list[str]]:
    """Every declaration any held PPTR version prints, read from the latest version that prints it, with the versions
    that print it and its decree. Returns the declarations, the versions read, and the differences between versions."""
    from shapely import union_all
    record = json.loads((root / SOURCES / 'declarations.json').read_text())
    schede = {s['code']: s for s in (record.get('schede') or {}).get('schede', []) if s.get('code')}
    issues = defaultdict(dict)
    for d in record.get('decrees') or ():
        for code in d.get('declarations') or ():
            issues[code] = d
    versions, rows_by_code, problems = [], defaultdict(list), []
    for version in record['versions']:
        codes = set()
        for page in version['pages']:
            if not page.get('sha256'):
                problems.append(f"{version['version']}: a layer page is not held ({page.get('error')})")
                continue
            for feature in json.loads(_blob(store, page['sha256']).read_bytes())['features']:
                a = feature['attributes']
                code = (a.get('CODICE') or '').strip()
                codes.add(code)
                rows_by_code[code].append((version['version'], a, feature.get('geometry'), page['sha256']))
        versions.append({'version': version['version'], 'layer': version['layer'], 'rows': version['rows'],
                         'declarations': len(codes)})
    order = [v['version'] for v in versions]   # the service lists the latest version first
    out = []
    for code, rows in sorted(rows_by_code.items()):
        printed = tuple(v for v in order if any(r[0] == v for r in rows))
        latest = [r for r in rows if r[0] == printed[0]]
        a = latest[0][1]
        geometry = union_all([_esri_polygon(g['rings']) for _, _, g, _ in latest if g and g.get('rings')])
        reading, cite, genus = read_motivation(a.get('OGGETTO__1'), a.get('MOTIVAZI_1'))
        decree = issues.get(code)
        read = _decree_reading(store, decree, a.get('OGGETTO__1'), a.get('COMUNE'))
        transcribed = _scheda_reading(store, schede.get(code), a.get('OGGETTO__1'))
        reading, cite, genus = combined(*[(r['reading'], r['cite'], r['genus']) for r in (read, transcribed)
                                          if r and r.get('reading')], (reading, cite, genus))
        out.append(Declaration(code, a.get('COD_SITAP'), (a.get('COMUNE') or '').strip(), (a.get('OGGETTO__1') or '').strip(),
                               (a.get('MOTIVAZI_1') or '').strip(), (a.get('NUMERO_DEC') or '').strip(),
                               (a.get('PUBBLICATO') or '').strip(), (a.get('ID_VINCOLI') or '').strip(),
                               (a.get('ART_136_C') or '').strip(), printed, geometry,
                               tuple(sorted({r[3] for r in latest})), reading, cite, genus,
                               _decree_state(decree, a.get('PUBBLICATO')) | (read or {}) | (transcribed or {})))
        if printed[0] != order[0]:
            problems.append(f'{code}: printed by {", ".join(printed)} and not by the latest version {order[0]}')
        elif len(printed) < len(order):
            missing = [v for v in order if v not in printed]
            problems.append(f'{code}: not printed by {", ".join(missing)}')
    return out, versions, problems


_ACT_HEADING = re.compile(r'(?=\bDECRETO(?:\s+MINISTERIALE|\s+DEL\s+\w+)?\s+\d{1,2}\s+[a-z]+\s+\d{4}\b)')
MIN_TEXT_PER_PAGE = 500   # below this a page carries only the issue's running header: a page image


def _decree_reading(store: Path, issue: dict | None, obj: str, comune: str) -> dict | None:
    """The declaration's decree read from its G.U. issue's text layer, where the issue has one: the act blocks that
    name the declaration's first comune and a declaration of notable public interest, read as a motivation is."""
    if not issue or not issue.get('sha256'):
        return None
    import pymupdf
    document = pymupdf.open(_blob(store, issue['sha256']))
    pages = [p.get_text() for p in document]
    state = {'pages': len(pages), 'text_layer_chars': sum(len(t.strip()) for t in pages)}
    if state['text_layer_chars'] < MIN_TEXT_PER_PAGE * len(pages) / 4:
        return state | {'read': 'page images: no text layer to read'}
    first = _fold(re.split(r'[-–(,]|â€“', comune or '')[0])
    named = [b for b in _ACT_HEADING.split('\n'.join(pages)) if first and first in _fold(b)
             and 'NOTEVOLEINTERESSEPUBBLICO' in _fold(b)]
    blocks = [b for b in named if 'DECRETA' in _fold(b)]   # the decree itself, not its title in the contents
    if not blocks:
        return state | {'read': f'the text layer holds no decree of notable public interest naming {comune!r}' + (
            ', only its title: the decree is printed elsewhere' if named else '')}
    reading, cite, genus = read_motivation(obj, ' '.join(blocks)[:200000] + '.')
    if reading == 'not read whole':   # the decree's own text is whole: naming no tree, it protects an area
        reading, cite = 'area', "the decree's text names no tree, row or group"
    return state | {'read': 'read from the text layer', 'reading': reading, 'cite': cite, 'genus': genus}


# The scheda's identification page prints the motivation after its heading and before the art. 134 classification.
_RECOGNITION = re.compile(r"riconoscimento.{0,3}\s*\(del valore dell.area\)\s*(.*?)\s*art\.\s*134", re.S | re.I)


def _scheda_reading(store: Path, scheda: dict | None, obj: str) -> dict | None:
    """The declaration's motivation as its PPTR scheda (elaborato 6.4) prints it in a text layer, read whole."""
    if not scheda or not scheda.get('sha256'):
        return None
    import pymupdf
    document = pymupdf.open(_blob(store, scheda['sha256']))
    found = next((m for m in (_RECOGNITION.search(page.get_text()) for page in document) if m), None)
    state = {'scheda': scheda['sha256'], 'scheda_pages': document.page_count}
    if not found:
        return state | {'scheda_read': 'the scheda prints no motivation in its text layer'}
    motivation = re.sub(r'\s+', ' ', found.group(1)).strip()
    reading, cite, genus = read_motivation(obj, motivation + '.')
    if reading == 'not read whole':   # the scheda prints it whole: naming no tree, it protects an area
        reading, cite = 'area', "the scheda's motivation names no tree, row or group"
    return state | {'scheda_read': 'read from the text layer', 'scheda_motivation': motivation, 'reading': reading,
                    'cite': cite, 'genus': genus}


def _decree_state(issue: dict | None, publication: str | None) -> dict:
    if issue and issue.get('sha256'):
        return {'document': issue['url'], 'sha256': issue['sha256'], 'kind': 'the G.U. issue the layer names'
                if not issue.get('printed') else "the G.U. issue the year's archive places: " + issue['printed']}
    if issue:
        return {'document': issue.get('url') or issue.get('publication'), 'kind': 'the G.U. issue the layer names',
                'not held': issue.get('error')}
    return {'kind': 'no G.U. publication the layer names', 'publication': publication,
            'not held': 'the decree is not published in the G.U.; the Ministry holds it (SITAP), unreachable here'}


# --- plant records and their placement ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InstrumentPlant:
    """A listed or declared tree as a plant record."""
    plant: str                  # the scheda ID or the declaration's code
    instrument: str             # NATIONAL or DECLARATION
    x: float                    # its point, EPSG:32633 (a declared tree: the polygon's representative point)
    y: float
    error_m: float              # its positional error (a declared tree: the polygon's reach from the point + scale term)
    species: str | None
    genus: str | None
    kind: str
    comune: str
    geometry: object = None     # a declared tree: its polygon
    entry: ListEntry | None = None
    declaration: Declaration | None = None

    def distance_to(self, x: float, y: float) -> float:
        if self.geometry is not None:
            from shapely.geometry import Point
            return float(self.geometry.distance(Point(x, y)))
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    @property
    def term_m(self) -> float:
        """The error added to a distance measured to this record's point, or to its polygon."""
        return SCALE_TERM_M if self.geometry is not None else self.error_m


def list_plants(entries: list[ListEntry], bound: ListBound) -> list[InstrumentPlant]:
    return [InstrumentPlant(e.scheda, NATIONAL, e.x, e.y, bound.error_m, e.species, e.genus, e.kind, e.comune, entry=e)
            for e in entries if e.x is not None]


def declared_plants(held: list[Declaration]) -> list[InstrumentPlant]:
    """A declaration that names a tree, a row or a group, as one plant record: the polygon its decree delimits, at the
    PPTR's stated scale. Its point is the polygon's representative point; its error the polygon's reach from that
    point plus the scale term."""
    import shapely
    out = []
    for d in held:
        if d.reading not in ('names a tree', 'names a row or group') or d.geometry.is_empty:
            continue
        point = d.geometry.representative_point()
        reach = float(shapely.distance(point, shapely.points(shapely.get_coordinates(d.geometry))).max())
        out.append(InstrumentPlant(d.code, DECLARATION, point.x, point.y, round(reach + SCALE_TERM_M, 2), None, d.genus,
                                   'single tree' if d.reading == 'names a tree' else 'row or group', d.comune,
                                   geometry=d.geometry, declaration=d))
    return out


def placed(plants: list[InstrumentPlant], infected) -> list[tuple[InstrumentPlant, str, float, float]]:
    """Each record inside a zone: within ZONE_M plus the infected plant's error_m plus the record's own error of an
    infected plant (an in-reach positive or an order plant). Returns (record, infected plant, distance, d)."""
    import numpy
    from scipy.spatial import cKDTree
    if not plants or not infected:
        return []
    tree = cKDTree(numpy.array([[p.x, p.y] for p in infected]))
    widest = max(p.error_m for p in infected)
    found = []
    for record in plants:
        for i in tree.query_ball_point([record.x, record.y], ZONE_M + widest + record.error_m):
            p = infected[i]
            distance = record.distance_to(p.x, p.y)
            d = ZONE_M + p.error_m + record.term_m
            if distance <= d:
                found.append((record, p.plant, round(distance, 2), round(d, 2)))
    return found


def nearest(plants: list[InstrumentPlant], infected) -> dict[str, tuple[str, float]]:
    """Each record's nearest infected plant and the distance to it (to the polygon, for a declared tree)."""
    import numpy
    from scipy.spatial import cKDTree
    tree = cKDTree(numpy.array([[p.x, p.y] for p in infected]))
    out = {}
    for record in plants:
        _, index = tree.query([record.x, record.y], k=min(len(infected), 8))
        best = min((infected[i] for i in numpy.atleast_1d(index)), key=lambda p: record.distance_to(p.x, p.y))
        out[record.plant] = (best.plant, round(record.distance_to(best.x, best.y), 2))
    return out


# --- the status hook ---------------------------------------------------------------------------------------------

class Instruments:
    """The held populations of both instruments, indexed for `facts`, the hook A's rows read."""

    def __init__(self, entries: list[ListEntry], held_decrees: list[Decree], bound: ListBound,
                 declared: list[Declaration], pptr_versions: list[dict]):
        import numpy
        from scipy.spatial import cKDTree
        from shapely import STRtree
        self.entries, self.decrees, self.bound, self.declared = entries, held_decrees, bound, declared
        self.located = [e for e in entries if e.x is not None]
        self.tree = cKDTree(numpy.array([[e.x, e.y] for e in self.located])) if self.located else None
        self.index = STRtree([d.geometry for d in declared]) if declared else None
        latest = held_decrees[-1] if held_decrees else None
        self.list_held = (f"the region's list in {len(held_decrees)} decree versions, {held_decrees[0].name} to "
                          f'{latest.name} (instruments.national_list.decrees)' if latest else 'no decree version held')
        self.declarations_held = (f'{len(declared)} declarations printed by {len(pptr_versions)} PPTR versions, '
                                  f"the latest {pptr_versions[0]['version']} (instruments.declarations)"
                                  if pptr_versions else 'no PPTR version held')

    def facts(self, x: float, y: float, error_m: float, genus: str | None, at: date, *,
              own: InstrumentPlant | None = None, register: dict | None = None) -> dict[str, dict]:
        return instrument_facts(self, x, y, error_m, genus, at, own=own, register=register)


def instrument_facts(held: Instruments, x: float, y: float, error_m: float, genus: str | None, at: date, *,
                     own: InstrumentPlant | None = None, register: dict | None = None) -> dict[str, dict]:
    """The hook A's rows read: for a plant at (x, y) with its error and recorded genus, one fact per instrument kind,
    "this tree is in that instrument in force at the event date".

    True: the plant is the listed or declared tree and the instrument holds it at `at`. False: no entry or
    declared tree of the plant's genus lies within d, or each that does is not in force at `at`; the populations
    held are named. None: a listed or declared tree within d may be the plant (identity, its own cause), a
    declaration containing the plant is not read whole, or `at` falls between a decree and its publication
    (A's). The L.R. 14/2007 register keeps row 9's identity and act chain, passed in `register`."""
    from shapely.geometry import Point
    facts = {}
    if own is not None and own.instrument == NATIONAL:
        value, why = in_force(own.entry, at)
        facts[NATIONAL] = {'value': value, 'entries': [own.plant], 'cause': why}
    else:
        d = round(error_m + held.bound.error_m, 2)
        near = [] if held.tree is None else [held.located[i] for i in held.tree.query_ball_point([x, y], d)]
        near = [e for e in near if genus is None or e.genus is None or e.genus == genus]
        live = [(e, round(((e.x - x) ** 2 + (e.y - y) ** 2) ** 0.5, 2), in_force(e, at)) for e in near]
        if all(v[0] is False for *_, v in live):
            facts[NATIONAL] = {'value': False, 'entries': [], 'cause': (
                f'no entry of the list of its genus lies within d = {d} m' if not live else
                'each entry within d is not in the list in force at the event date: '
                + '; '.join(f'{e.scheda} ({v[1]})' for e, _, v in live))}
        else:
            facts[NATIONAL] = {'value': None, 'entries': [
                {'entry': e.scheda, 'distance_m': dist, 'd_m': d, 'in_force': v[0], 'why': v[1]}
                for e, dist, v in live], 'cause': 'identity: the plant may be the listed tree within d; no record '
                                                  'names it'}
    facts[NATIONAL]['held'] = held.list_held
    if own is not None and own.instrument == DECLARATION:
        # A decides whether a declaration takes effect on its decree's date or on its publication or notification.
        dates = (own.declaration.adopted(), own.declaration.published())
        value = True if all(d and d <= at for d in dates) else False if all(d and d > at for d in dates) else None
        named = f'the declaration names the tree ("{own.declaration.cite}"); its decree is dated ' \
                f'{own.declaration.decree_date}, {own.declaration.publication}'
        facts[DECLARATION] = {'value': value, 'declarations': [own.plant], 'cause': named if value is not None else (
            named + ': a date is not printed, or the event date falls between them, and A decides when it takes '
                    'effect')}
    else:
        point = Point(x, y)
        naming, unread, areas = [], [], []
        hits = [] if held.index is None else held.index.query(point.buffer(error_m + SCALE_TERM_M))
        for i in hits:
            decl = held.declared[int(i)]
            if decl.adopted() is not None and decl.adopted() > at:
                continue   # not yet declared at the event date
            distance = float(decl.geometry.distance(point))
            if decl.reading in ('names a tree', 'names a row or group'):
                if distance <= error_m + SCALE_TERM_M and (genus is None or decl.genus is None or decl.genus == genus):
                    naming.append((decl, round(distance, 2)))
            elif distance <= error_m:
                (unread if decl.reading == 'not read whole' else areas).append(decl)
        if naming:
            facts[DECLARATION] = {'value': None, 'declarations': [
                {'declaration': decl.code, 'distance_m': dist} for decl, dist in naming],
                'cause': 'identity: the plant may be the declared tree; no record names it'}
        elif unread:
            facts[DECLARATION] = {'value': None, 'declarations': [decl.code for decl in unread],
                                  'cause': 'the motivation of a declaration containing the plant is not read whole: '
                                           'the layer cuts it at its field length and its decree is not read'}
        else:
            facts[DECLARATION] = {'value': False, 'declarations': [], 'cause': (
                'no held declaration names a tree within d' + (
                    '; the plant lies in declarations that protect an area and name no tree: '
                    + ', '.join(decl.code for decl in areas) if areas else ''))}
    facts[DECLARATION]['held'] = held.declarations_held
    if register is not None:
        facts[REGISTER] = register
    return facts


# --- row 9's pass and its emitted rows -------------------------------------------------------------------------

def _register_of(record: InstrumentPlant) -> dict:
    """A listed or declared tree in the L.R. 14/2007 register: the register lists olives only."""
    if record.genus and record.genus != 'Olea':
        return {'identity': 'not a register tree', 'cause': f'the register lists olives; the record names {record.genus}'}
    return {'identity': 'unknown', 'cause': 'the record names no genus, or an olive: row 9\'s candidates are not read '
                                            'for an instrument record'}


def read(store: Path, at: date, plants, root: Path = REPOSITORY) -> dict:
    """Both instruments over the held sources, placed against the zones of row 9's infected plants, with each plant's
    status. `plants` is row 9's [(Plant, Candidates)]: the register fact keeps row 9's identity and its cause."""
    entries, held_decrees, list_problems = list_entries(store, root)
    declared, versions, declaration_problems = declarations(store, root)
    naming = [d for d in declared if d.reading in ('names a tree', 'names a row or group')]
    bound = list_bound(declared_residuals(entries, naming))
    held = Instruments(entries, held_decrees, bound, declared, versions)
    infected = [p for p, _ in plants if p.kind in ('in-reach positive', 'order plant')]
    positives = [p for p, _ in plants if p.kind == 'in-reach positive']
    records = list_plants(entries, bound) + declared_plants(declared)
    admitted = {}
    for record, plant, distance, d in placed(records, infected):
        admitted.setdefault(record.plant, (record, []))[1].append((plant, distance, d))
    status = {p.plant: held.facts(p.x, p.y, p.error_m, _genus(p.species), at,
                                  register={'identity': c.identity, 'cause': c.rule}) for p, c in plants}
    duplicates = {}
    for name, (record, _) in admitted.items():
        status[name] = held.facts(record.x, record.y, record.error_m, record.genus, at, own=record,
                                  register=_register_of(record))
        # A monitored plant of the record's genus within both errors may be the same tree: listed, not admitted by it.
        duplicates[name] = [p.plant for p, _ in plants if record.distance_to(p.x, p.y) <= p.error_m + record.term_m
                            and (record.genus is None or _genus(p.species) in (None, record.genus))]
    return {'at': at, 'entries': entries, 'decrees': held_decrees, 'bound': bound, 'declarations': declared,
            'versions': versions, 'problems': list_problems + declaration_problems, 'records': records,
            'admitted': admitted, 'duplicates': duplicates, 'status': status,
            'nearest': nearest(records, positives) if positives else {}, 'positives': len(positives)}


def _decree(d: Decree | None) -> dict | None:
    return None if d is None else {'decree': d.name, 'adopted': d.adopted.isoformat(), 'gazette': d.gazette,
                                   'published': d.published.isoformat()}


def rows(result: dict) -> dict:
    """The emitted inputs of both instruments, as JSON."""
    nearest_of, admitted = result['nearest'], result['admitted']
    entries = [{
        'scheda': e.scheda, 'comune': e.comune, 'province': e.province, 'place': e.place,
        'position': {'latitude': e.latitude, 'longitude': e.longitude, 'frame': 'WGS 84 (the census instructions)',
                     'x': e.x and round(e.x, 2), 'y': e.y and round(e.y, 2), 'crs': 'EPSG:32633',
                     'error_m': result['bound'].error_m},
        'species': e.species, 'kind': e.kind, 'members': e.members, 'extent': 'not printed',
        'circumference_cm': e.circumference, 'height_m': e.height, 'proposal': e.proposal, 'sheet': e.sheet,
        'listed_by': _decree(e.listed_by), 'deleted_by': _decree(e.deleted_by),
        'stated_deletion': e.stated_deletion, 'corrected_by': [d.name for d in e.corrected_by],
        'printed_as': [list(p) for p in e.printed_as], 'causes': list(e.causes),
        'nearest_positive': nearest_of.get(e.scheda) and {'plant': nearest_of[e.scheda][0],
                                                          'distance_m': nearest_of[e.scheda][1]},
        'source': e.source} for e in result['entries']]
    declarations = [{
        'code': d.code, 'sitap': d.sitap, 'comune': d.comune, 'object': d.obj, 'motivation': d.motivation,
        'decree_date': d.decree_date, 'publication': d.publication, 'law': d.law, 'pptr_letter': d.letter,
        'reading': d.reading, 'cite': d.cite, 'genus': d.genus, 'area_m2': round(d.area_m2, 1),
        'versions': list(d.versions), 'decree': d.decree,
        'nearest_positive': nearest_of.get(d.code) and {'plant': nearest_of[d.code][0],
                                                        'distance_m': nearest_of[d.code][1]},
        'source': list(d.source)} for d in result['declarations']]
    in_zone = [{'plant': name, 'instrument': record.instrument, 'species': record.species, 'genus': record.genus,
                'kind': record.kind, 'point': {'x': round(record.x, 2), 'y': round(record.y, 2), 'crs': 'EPSG:32633',
                                               'error_m': record.error_m},
                'zones': [{'infected_plant': p, 'distance_m': dist, 'd_m': d} for p, dist, d in zones],
                'same_tree_candidates': result['duplicates'].get(name, []), 'status': result['status'][name]}
               for name, (record, zones) in sorted(admitted.items())]
    groups = [{'scheda': e.scheda, 'kind': e.kind, 'members': e.members, 'extent': 'not printed',
               'nearest_positive_m': nearest_of.get(e.scheda, (None, None))[1],
               'nearest_zone_edge_m': None if e.scheda not in nearest_of else round(nearest_of[e.scheda][1] - ZONE_M, 2)}
              for e in result['entries'] if e.kind != 'single tree']
    listed = sorted((nearest_of[e.scheda][1], e.scheda, e.species, e.comune) for e in result['entries']
                    if e.sheet == 'listed' and e.scheda in nearest_of)
    return {
        'at': result['at'].isoformat(),
        'national_list': {'decrees': [d.as_json() for d in result['decrees']], 'entries': entries,
                          'bound': {'error_m': result['bound'].error_m, 'fixes': result['bound'].fixes,
                                    'statistic': result['bound'].statistic,
                                    'sources_searched': list(result['bound'].sources_searched)}},
        'declarations': {'versions': result['versions'], 'declarations': declarations,
                         'scale': {'stated': f'1:{STATED_SCALE:,}', 'term_m': SCALE_TERM_M,
                                   'rule': '1 mm at the stated scale: no source states a ground tolerance; a smaller '
                                           'term could leave out of a zone a declared tree it reaches'}},
        'problems': result['problems'], 'in_zone': in_zone, 'groups': groups,
        'distances': {'positives': result['positives'],
                      'nearest_listed_entry': listed[0] if listed else None,
                      'listed_within_1km': sum(1 for d, *_ in listed if d <= 1000),
                      'listed_within_5km': sum(1 for d, *_ in listed if d <= 5000),
                      'declared_trees': {d.code: nearest_of.get(d.code) for d in result['declarations']
                                         if d.reading in ('names a tree', 'names a row or group')}}}

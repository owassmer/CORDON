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


# --- the OCR route: a page its text layer does not supply ---------------------------------------------------------

# A page is read from its text layer where that layer supplies it. It does not where the page is a page image (an
# image covers at least PAGE_IMAGE_SHARE of it) whose layer holds fewer than MIN_TEXT_PER_PAGE characters, or where
# the layer is garbled: fewer than MIN_VOWEL_SHARE of its words of four letters or more hold a vowel, as every Italian
# word does. In the held decree issues and schede, page images carry 0 to 168 characters (a running header at most)
# and the thinnest page of text 606; the lowest vowel share of a held text layer is 0.937.
MIN_TEXT_PER_PAGE = 500
PAGE_IMAGE_SHARE = 0.5
MIN_VOWEL_SHARE = 0.9
_VOWEL = re.compile(r'[aeiouyàáâèéêìíîòóôùúûAEIOUYÀÈÉÌÒÙ]')
# Such a page is rendered with PyMuPDF and read by Tesseract with its Italian model. The text is fixed by the page's
# bytes and by what `ocr_engine` records; it is kept, regenerable, under derived/OCR_FOLDER, keyed by all of them.
OCR_DPI = 300                      # the held G.U. page images are scanned at about 290 dpi, the schede at 144
OCR_RENDER = 'PyMuPDF get_pixmap, DeviceGray, no alpha, the page box, passed as PGM'
OCR_ARGS = ('-l', 'ita', '--psm', '3', '--oem', '1', '--dpi', str(OCR_DPI))   # automatic segmentation, LSTM engine
OCR_READER = 'ocr-1'               # this route's own version: what it renders, how it calls Tesseract, what it keeps
OCR_FOLDER = 'protected-status/ocr'
OCR_WORKERS = 6                    # Tesseract processes at once (one thread each), under the machine's 8 cores
# A ruled table is read cell by cell, as a text layer orders it: a dark run of RULE_PX or more (about 0.2 in at OCR_DPI;
# odd, for a centred window) no thicker than RULE_THICK_PX is a rule; a word whose centre four rules enclose lies in
# that cell.
RULE_PX = 61
RULE_THICK_PX = 8
RULE_DARK = 160


def ocr_engine() -> dict | None:
    """What fixes an OCR'd page's text besides its bytes: the Tesseract and Leptonica versions, the Italian model and
    its hash, the PyMuPDF version, the render settings and DPI, Tesseract's arguments and this route's version. None
    where Tesseract or its Italian model is not installed here."""
    global _ENGINE
    try:
        return _ENGINE
    except NameError:
        pass
    import shutil
    import subprocess
    import pymupdf
    from .store import file_digest
    _ENGINE = None
    executable = shutil.which('tesseract')
    if executable is None:
        return None
    try:
        version = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=60)
        listed = subprocess.run([executable, '--list-langs'], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    printed, langs = version.stdout + version.stderr, listed.stdout + listed.stderr
    tesseract, leptonica = re.search(r'tesseract\s+v?(\S+)', printed), re.search(r'leptonica-(\S+)', printed)
    folder = re.search(r'"([^"]+)"', langs)
    model = folder and Path(folder.group(1)) / 'ita.traineddata'
    if not (tesseract and leptonica and model and model.exists() and 'ita' in langs.split()):
        return None
    _ENGINE = {'tesseract': tesseract.group(1), 'leptonica': leptonica.group(1), 'model': 'ita.traineddata',
               'model_sha256': file_digest(model.resolve()), 'pymupdf': pymupdf.VersionBind, 'dpi': OCR_DPI,
               'render': OCR_RENDER, 'args': list(OCR_ARGS), 'reader': OCR_READER, 'executable': executable}
    return _ENGINE


def _engine_recorded() -> dict | None:
    engine = ocr_engine()
    return engine and {k: v for k, v in engine.items() if k != 'executable'}


def _ocr_key(digest: str, index: int, engine: dict) -> str:
    from hashlib import sha256
    inputs = {k: v for k, v in engine.items() if k != 'executable'} | {'source': digest, 'page': index}
    return sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()


def _ocr_path(store: Path, digest: str, index: int, engine: dict) -> Path:
    return Path(store) / 'derived' / OCR_FOLDER / f'{_ocr_key(digest, index, engine)}.json'


def layer_gap(page) -> str | None:
    """Why a page's text layer does not supply its text, or None where it does."""
    import pymupdf
    text = page.get_text().strip()
    words = re.findall(r'[^\W\d_]{4,}', text)
    if len(words) >= 20 and sum(1 for w in words if _VOWEL.search(w)) < MIN_VOWEL_SHARE * len(words):
        return 'its text layer is garbled'
    if len(text) < MIN_TEXT_PER_PAGE:
        area = abs(page.rect) or 1.0
        covered = max((abs(pymupdf.Rect(i['bbox']) & page.rect) / area for i in page.get_image_info()), default=0.0)
        if covered >= PAGE_IMAGE_SHARE:
            return 'a page image with no text layer' if not text else f'a page image whose text layer holds {len(text)} characters'
    return None


def _runs(mask, axis: int):
    """The pixels of `mask` lying in a run of at least RULE_PX along `axis`: an opening by a line of RULE_PX."""
    import numpy
    from scipy import ndimage
    eroded = ndimage.minimum_filter1d(mask.view(numpy.uint8), RULE_PX, axis=axis)
    return ndimage.maximum_filter1d(eroded, RULE_PX, axis=axis).astype(bool)


def _rules(pixmap) -> dict:
    """The ruled lines of a rendered page: vertical and horizontal segments as [x0, y0, x1, y1] in pixels."""
    import numpy
    from scipy import ndimage
    gray = numpy.frombuffer(pixmap.samples, numpy.uint8).reshape(pixmap.height, pixmap.width)
    dark = gray < RULE_DARK
    out = {}
    for name, axis in (('vertical', 0), ('horizontal', 1)):
        labels, _ = ndimage.label(_runs(dark, axis))
        # A rule is thin along its length (where rules meet, or a jagged rule steps, its box is wider); a filled
        # area is not.
        out[name] = [[s[1].start, s[0].start, s[1].stop, s[0].stop]
                     for k, s in enumerate(ndimage.find_objects(labels), 1)
                     if float(numpy.median((labels[s] == k).sum(axis=1 - axis))) <= RULE_THICK_PX]
    return out


def _ocr_page(engine: dict, image: bytes) -> str:
    """Tesseract's TSV (each word with its box and its block, paragraph and line) for a rendered page."""
    import os
    import subprocess
    done = subprocess.run([engine['executable'], 'stdin', 'stdout', *OCR_ARGS, 'tsv'], input=image, capture_output=True,
                          env=os.environ | {'OMP_THREAD_LIMIT': '1'}, timeout=600)
    if done.returncode != 0:
        raise RuntimeError(f'tesseract failed: {done.stderr.decode(errors="replace")[-400:]}')
    return done.stdout.decode('utf-8')


def ocr_pages(store: Path, digest: str, indices) -> dict[int, dict]:
    """The OCR'd reading of each named page of a held PDF: Tesseract's words with their boxes, and the page's rules.
    Kept under derived/OCR_FOLDER and read from there when held; pages not held are read OCR_WORKERS at a time."""
    from concurrent.futures import ThreadPoolExecutor
    import pymupdf
    from .store import _place
    engine = ocr_engine()
    if engine is None:
        return {}
    found, missing = {}, []
    for index in indices:
        path = _ocr_path(store, digest, index, engine)
        if path.exists():
            found[index] = json.loads(path.read_text())
        else:
            missing.append(index)
    if not missing:
        return found
    document = pymupdf.open(_blob(store, digest))
    recorded = _engine_recorded()

    def keep(index, rules, future):
        value = {'source': digest, 'page': index, 'engine': recorded, 'rules': rules, 'tsv': future.result()}
        _place(_ocr_path(store, digest, index, engine), lambda t: t.write_text(json.dumps(value, ensure_ascii=False)))
        found[index] = value

    with ThreadPoolExecutor(OCR_WORKERS) as pool:
        pending = []
        for index in missing:   # PyMuPDF renders in this thread only; Tesseract runs in its own processes
            pixmap = document[index].get_pixmap(dpi=OCR_DPI, colorspace=pymupdf.csGRAY, alpha=False)
            pending.append((index, _rules(pixmap), pool.submit(_ocr_page, engine, pixmap.tobytes('pnm'))))
            while len(pending) > 2 * OCR_WORKERS:
                keep(*pending.pop(0))
        for item in pending:
            keep(*item)
    return found


def ocr_text(reading: dict) -> str:
    """An OCR'd page's text: Tesseract's lines in its order, except that the cells of a ruled table are read cell by
    cell (each row's cells left to right, where the row's first word falls), as a text layer orders them."""
    rows = [r.split('\t') for r in reading['tsv'].splitlines()[1:]]
    words = [{'line': (int(r[2]), int(r[3]), int(r[4])), 'x': int(r[6]), 'y': int(r[7]), 'w': int(r[8]),
              'h': int(r[9]), 'text': r[11]} for r in rows if len(r) >= 12 and r[0] == '5' and r[11].strip()]
    vertical, horizontal = reading['rules']['vertical'], reading['rules']['horizontal']
    for w in words:
        cx, cy = w['x'] + w['w'] / 2, w['y'] + w['h'] / 2
        left = max((v[2] for v in vertical if v[2] <= cx and v[1] <= cy <= v[3]), default=None)
        right = min((v[0] for v in vertical if v[0] >= cx and v[1] <= cy <= v[3]), default=None)
        top = max((h[3] for h in horizontal if h[3] <= cy and h[0] <= cx <= h[2]), default=None)
        bottom = min((h[1] for h in horizontal if h[1] >= cy and h[0] <= cx <= h[2]), default=None)
        w['cell'] = None if None in (left, right, top, bottom) else (top, left, bottom, right)
    cells = defaultdict(list)
    for w in words:
        if w['cell']:
            cells[w['cell']].append(w)
    tops = sorted({c[0] for c in cells})
    row_of = {}
    for top in tops:   # cells whose top rules lie within a rule's thickness share a row
        row_of[top] = next((row_of[t] for t in tops if t < top and top - t <= RULE_THICK_PX), top)

    def lines_of(group):
        lines = defaultdict(list)
        for w in group:
            lines[w['line']].append(w)
        ordered = sorted(lines.values(), key=lambda ws: min(w['y'] for w in ws))
        return [' '.join(w['text'] for w in sorted(ws, key=lambda w: w['x'])) for ws in ordered]

    out, emitted, current, line = [], set(), [], None
    for w in words:
        if w['line'] != line and current:
            out.append(' '.join(current))
            current = []
        line = w['line']
        if w['cell'] is None:
            current.append(w['text'])
            continue
        row = row_of[w['cell'][0]]
        if row in emitted:
            continue
        if current:
            out.append(' '.join(current))
            current = []
        emitted.add(row)
        for cell in sorted((c for c in cells if row_of[c[0]] == row), key=lambda c: c[1]):
            out.extend(lines_of(cells[cell]))
    if current:
        out.append(' '.join(current))
    return '\n'.join(out)


def page_texts(store: Path, digest: str, upto=None) -> tuple[list[str | None], dict]:
    """Each page's text: its text layer where that supplies it, else its OCR'd text, else None (OCR is not available
    here). With `upto`, pages are read in order up to the first whose text it accepts, and no further. Returns the
    texts and the route: the pages read by OCR and the engine."""
    import pymupdf
    document = pymupdf.open(_blob(store, digest))
    engine = ocr_engine()
    gaps = {page.number: gap for page in document if (gap := layer_gap(page))}
    batch = ocr_pages(store, digest, sorted(gaps)) if upto is None and gaps and engine else {}
    texts = []
    for page in document:
        if page.number not in gaps:
            text = page.get_text()
        elif engine is None:
            text = None
        else:
            text = ocr_text((batch or ocr_pages(store, digest, [page.number]))[page.number])
        texts.append(text)
        if upto is not None and text is not None and upto(text):
            break
    read = [i for i in sorted(gaps) if i < len(texts)]
    route = {'pages': len(document), 'ocr_pages': read, 'engine': _engine_recorded()}
    if read and engine is None:
        route['not read'] = 'Tesseract with its Italian model is not installed here'
    return texts, route


def ocr_route(route: dict) -> str:
    engine = route['engine']
    return (f"OCR: Tesseract {engine['tesseract']} (Leptonica {engine['leptonica']}), {engine['model']} "
            f"{engine['model_sha256'][:12]}, {' '.join(engine['args'])}, rendered by PyMuPDF {engine['pymupdf']} at "
            f"{engine['dpi']} dpi")


def _joined(text: str) -> str:
    """A text with its words broken across lines by a hyphen joined again (an OCR'd cell border after it ignored)."""
    return re.sub(r'(?<=[^\W\d_])[-‐¬\xad][ \t|]*\n\s*(?=[^\W\d_])', '', text)


# --- the vision transcription: the words D's rule reads from a page image -----------------------------------------

# OCR locates (which act, which pages of an issue, which page of a scheda); it does not read. The words D's rule reads
# from a page image are a vision transcription of that page: one page image per request through the Claude
# subscription, under the reading login (scripts/transcribe_pages.py makes the requests). The answer is a model's, so
# it is kept from its first write under derived/TRANSCRIPTION_FOLDER, which store.REGENERABLE does not name: it is
# replicated to R2 on every push. The request asks for the page's text as printed and nothing else; the model is not
# asked whether a tree is named.
TRANSCRIPTION_FOLDER = 'page-transcriptions'
TRANSCRIPTION_PROVIDER = 'claude-code-subscription'   # report_extraction.PROVIDER_LABELS['subscription']
TRANSCRIPTION_MODEL = 'claude-sonnet-5'               # report_extraction.ExtractionConfig's, as the report readings
TRANSCRIPTION_EFFORT = 'medium'
TRANSCRIPTION_DPI = 200                               # the page rendered in grey; the held scans are about 290 dpi
ILLEGIBLE = '[illegible]'
TRANSCRIPTION_PROMPT = (
    'Transcribe the attached page image: every word printed on the page, exactly as printed, in reading order. Where '
    'the page is set in columns, read each column from top to bottom, the left column first; a heading or a line '
    'spanning the columns stands where it is printed. Read a table row by row, each row\'s cells from left to right. '
    'Keep each printed line on its own line. Keep spelling, accents, capitals, punctuation, numbers and hyphens as '
    'printed, a word broken at a line\'s end included: do not correct, complete, join, translate, summarise or '
    f'explain. Where the image does not show a word legibly, write {ILLEGIBLE} in its place; do not guess it. Return '
    'only the transcription, in the field text.')
TRANSCRIPTION_SCHEMA = {'type': 'object', 'properties': {'text': {'type': 'string'}}, 'required': ['text'],
                        'additionalProperties': False}


def transcription_request(document, digest: str, index: int) -> tuple[str, dict, bytes, str]:
    """The exact request transcribing page `index` (0-based) of the held PDF `digest`, opened as `document`: its hash,
    which names the kept answer, the identity it hashes, the one PNG it attaches and that attachment's label."""
    from hashlib import sha256
    import pymupdf
    png = document[index].get_pixmap(dpi=TRANSCRIPTION_DPI, colorspace=pymupdf.csGRAY, alpha=False).tobytes('png')
    label = f'PHYSICAL PAGE {index + 1}: page image'
    identity = {'provider': TRANSCRIPTION_PROVIDER, 'model': TRANSCRIPTION_MODEL, 'effort': TRANSCRIPTION_EFFORT,
                'source_sha256': digest, 'page': index + 1, 'request': 'page transcription',
                'prompt': TRANSCRIPTION_PROMPT, 'render': f'PyMuPDF {pymupdf.VersionBind}, {TRANSCRIPTION_DPI} dpi, grey',
                'attachments': [{'label': label, 'sha256': sha256(png).hexdigest()}], 'schema': TRANSCRIPTION_SCHEMA}
    return sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest(), identity, png, label


def transcription_path(store: Path, request_id: str) -> Path:
    return Path(store) / 'derived' / TRANSCRIPTION_FOLDER / f'{request_id}.json'


def transcriptions(store: Path, digest: str, indices) -> dict[int, dict]:
    """The held transcription of each named page (0-based) of a held PDF: its text, the model and the request that
    read it. A page whose answer is not held (or is not a reading by this route's model) is absent."""
    import pymupdf
    indices = list(indices)
    if not indices:
        return {}
    document = pymupdf.open(_blob(store, digest))
    found = {}
    for index in indices:
        request_id = transcription_request(document, digest, index)[0]
        path = transcription_path(store, request_id)
        if not path.exists():
            continue
        kept = json.loads(path.read_text())
        answer = (kept.get('response') or {}).get('structured_output')
        if (kept.get('provider') != TRANSCRIPTION_PROVIDER or kept.get('model') != TRANSCRIPTION_MODEL
                or not isinstance(answer, dict) or not isinstance(answer.get('text'), str)):
            continue
        found[index] = {'page': index + 1, 'text': answer['text'], 'model': kept['model'], 'request_sha256': request_id}
    return found


def vision_route(held: list[dict]) -> str:
    return (f"vision transcription by {held[0]['model']}: "
            + '; '.join(f"page {t['page']}, request {t['request_sha256']}" for t in held))


def _unreadable(text: str) -> str:
    """What a transcribed text the rule reads holds that the rule cannot read: the words it marks illegible, and any
    letter outside the Latin script, which an Italian text does not print (a model may write a Cyrillic look-alike,
    as one held answer does): a tree word holding one is not seen."""
    import unicodedata
    count = text.count(ILLEGIBLE)
    foreign = sorted({c for c in text if c.isalpha() and c not in 'ªº'
                      and not unicodedata.name(c, '').startswith('LATIN')})
    return ((f'; {count} word{"s" if count != 1 else ""} marked illegible' if count else '')
            + ('; letters outside the Latin script: ' + ', '.join(f'{c} ({unicodedata.name(c, "?")})' for c in foreign)
               if foreign else ''))


def _untranscribed(pages) -> str:
    return (f"; the vision transcription of page {', '.join(str(p + 1) for p in pages)} is not yet held: the words "
            f"read are Tesseract's")


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
# A road's "tronco" (a stretch: "secondo tronco", "tronco stradale") and a circle's "circonferenza di raggio", as a
# delimitation prints them, name none.
_NAMES_TREE = re.compile(r"\bcirconferenza\b(?!\s+(?:di|con|avente)\s+raggio)|\bchioma\b|\btronco\s+(?:di\s+)?(?:m\.|metri|cm)|"
                         r"\b(?:del|il|suo)\s+tronco\b(?!\s+(?:stradale|di\s+strada|ferroviario))|"
                         r"\bl'albero\b|\bdell'albero\b|\bun albero\b|"
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
        return _decree_day(self.decree_date)

    def unread(self) -> str:
        """Why a declaration not read whole is not: the layer's motivation, and each other text's route state."""
        held = self.decree or {}
        return '; '.join([
            'the layer prints no motivation' if _NO_MOTIVATION.search(self.motivation or '') else
            'the layer cuts its motivation at its field length',
            'its decree: ' + (held.get('read') or held.get('not held') or held.get('kind') or 'none named')]
            + (['its scheda: ' + held['scheda_read']] if held.get('scheda_read') else ['no scheda is held']))


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
            # The genus its tree words name; none where they name several (a list of villas' gardens): any genus may
            # then be the tree.
            words = re.findall(r"[A-Za-zÀ-ÿ']+", text.lower())
            genera = {_TREE_WORDS[w.split("'")[-1]] for w in words if w.split("'")[-1] in _TREE_WORDS}
            return reading, found.group(0), next(iter(genera)) if len(genera) == 1 else None
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


def _day(year: int, month: int, day: int) -> date | None:
    """The date, or None where the printed (or OCR'd) numbers name none."""
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _decree_day(printed: str | None) -> date | None:
    found = _DECREE_DATE.search(printed or '')
    return _day(int(found.group(3)), int(found.group(2)), int(found.group(1))) if found else None


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
    issues = {}
    for d in record.get('decrees') or ():
        for code in d.get('declarations') or ():
            issues.setdefault(code, d)   # the issue that published it; a supplement of it is read beside it
    # An issue's ordinary supplements print acts its own pages only list: each held one is read with the issue.
    supplements = defaultdict(list)
    for d in record.get('decrees') or ():
        found = d.get('sha256') and re.search(r'(/eli/gu/\d{4}/\d{2}/\d{2}/\d+/)so/', d.get('url') or '')
        if found:
            supplements[found.group(1)].append(d)
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
    # A word of the layer's objects (each decree's title as the PPTR transcribes it) or comuni distinguishes a decree
    # where it has three letters or more and at most one object in ten prints it.
    objects = [next(r[1] for r in rows if r[0] == next(v for v in order if any(x[0] == v for x in rows)))
               for rows in rows_by_code.values()]
    frequency = defaultdict(int)
    for a in objects:
        for w in set(_words(a.get('OGGETTO__1')).split()):
            frequency[w] += 1

    def distinctive(a: dict) -> set[str]:
        return {w for w in _words(f"{a.get('OGGETTO__1')} {a.get('COMUNE')}").split()
                if len(w) >= 3 and w not in _PARTICLES and frequency[w] <= len(objects) / 10}
    out = []
    for code, rows in sorted(rows_by_code.items()):
        printed = tuple(v for v in order if any(r[0] == v for r in rows))
        latest = [r for r in rows if r[0] == printed[0]]
        a = latest[0][1]
        geometry = union_all([_esri_polygon(g['rings']) for _, _, g, _ in latest if g and g.get('rings')])
        reading, cite, genus = read_motivation(a.get('OGGETTO__1'), a.get('MOTIVAZI_1'))
        decree = issues.get(code)
        issue = decree and re.search(r'/eli/gu/\d{4}/\d{2}/\d{2}/\d+/', decree.get('url') or '')
        read = decree and _decree_reading(store, [decree] + [s for s in supplements[issue.group(0) if issue else '']
                                                             if s is not decree], a.get('OGGETTO__1'),
                                          a.get('COMUNE'), _decree_day(a.get('NUMERO_DEC')), distinctive(a))
        transcribed = _scheda_reading(store, schede.get(code), a.get('OGGETTO__1'))
        texts = [(read['reading'], read['cite'], read['genus'])] if read and read.get('reading') else []
        if transcribed and transcribed.get('scheda_reading'):
            texts.append((transcribed['scheda_reading'], transcribed['scheda_cite'], transcribed['scheda_genus']))
        reading, cite, genus = combined(*texts, (reading, cite, genus))
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


# An act begins at its heading ("DECRETO MINISTERIALE 4 marzo 1975", "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 27 aprile
# 1960", "LEGGE ...") and ends at the job number the issue prints after it ("(8196)", "(99A7656)").
_ACT_HEADING = re.compile(r"\b(?:DECRETO|LEGGE|ORDINANZA|DELIBERAZIONE|DETERMINAZIONE|PROVVEDIMENTO|CIRCOLARE)"
                          r"(?:[\s-]+[A-Z][A-Z'’]*){0,5}\s+\d{1,2}\s*[°º]?[\s.-]+[a-z]+\s+\d{4}\b")
_ACT_END = re.compile(r'^[^\w(]*\((?:\d{2}A)?\d{3,5}\)\W*$', re.M)
# A Region's act in the G.U. is headed by the Region's name on its own line ("REGIONE PUGLIA").
_REGION_HEADING = re.compile(r"^[ \t]*REGIONE[ \t]+[A-Z][A-Z'’ \t-]+$", re.M)
# A decree's preamble (its title and recitals: what it declares and why) ends at its "Decreta" (a Region's deliberation
# declaring under L. 1497/1939, at its "Delibera:").
# OCR may misread its "e" as "c" or its "t" as "l" ("Dccreta:"): such a form counts where its colon follows.
_DECRETA = re.compile(r'\bD\s?e\s?c\s?r\s?e\s?t\s?a\b\s*:?|\bD[ec]{2}r[ec][tl]a\s*:|\bD\s?e\s?l\s?i\s?b\s?e\s?r\s?a\s*:',
                      re.I)
# A contents entry: an act's title followed by its page ("... comune di Monopoli . . . Pag. 18", or the ditto "» 42").
_CONTENTS = re.compile(r'(?:\bPag\.?|»)\s*\d+')
# An act's title ends where its issuing authority ("IL MINISTRO ...", "LA GIUNTA ...") or its first recital begins.
_TITLE_END = re.compile(r'\n\s*(?:(?:IL|LA)\s+[A-Z]{4,}|Vist[oaie]\b|Considerat|Udit[oa]\b)')
# Articles and prepositions name no place: never distinctive.
_PARTICLES = frozenset('DEL DELLA DELLE DELLO DEGLI DEI DELL NEL NELLA NELLE NELLO NEGLI NEI NELL AL ALLA ALLE ALLO '
                       'AGLI AI ALL DAL DALLA DALLE DAGLI DAI DALL SUL SULLA SULLE SUI SULL CON PER TRA FRA UNA UNO'.split())


def _words(text: str) -> str:
    """A text as its letters' words, unaccented and upper-case, each between single spaces."""
    import unicodedata
    folded = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode().upper()
    return ' ' + ' '.join(re.findall(r'[A-Z]+', folded)) + ' '


def _area_cite(ocr: dict | None, text: str) -> str:
    """Why a whole text naming no tree reads as an area: a reading resting on OCR keeps its route."""
    return f"the OCR'd text names no tree, row or group ({ocr_route(ocr)})" if ocr else f'{text} names no tree, row or group'


def _vision_cite(held: list[dict], text: str) -> str:
    """Why a whole transcribed text naming no tree reads as an area: its route, and what in it the rule cannot read."""
    return f'the transcribed text names no tree, row or group ({vision_route(held)}){_unreadable(text)}'


def _heading_date(heading: str) -> date | None:
    found = re.search(r'(\d{1,2})\s*[°º]?[\s.-]+([a-z]+)\s+(\d{4})', heading)
    month = found and _MONTHS.get(found.group(2))
    return _day(int(found.group(3)), month, int(found.group(1))) if month else None


def _decree_reading(store: Path, issues: list[dict], obj: str, comune: str, decree_date: date | None,
                    distinctive: set[str]) -> dict | None:
    """The declaration's decree read from the G.U. issue that published it, or a supplement of that issue held: each
    page located in its text layer, or in its OCR'd text where the layer does not supply it (`page_texts`), and read
    from its text layer or that page's vision transcription. The decree is the act of
    notable public interest whose title holds the distinctive words of the layer's object (the decree's title as the
    PPTR transcribes it) and whose heading prints the layer's decree date: the act holding the most of them, where it
    holds two, or one and the date, or all there are, or whose title names the layer's first comune whole. Its
    preamble, up to its first "decreta" (a Region's "delibera:"), its object and motivation, is read as a motivation
    is; a reading resting on a transcribed page cites it, and one still resting on an OCR'd page says so."""
    held = [i for i in issues if i.get('sha256')]
    if not held:
        return None
    causes = []
    for issue in held:
        read = _read_issue(store, issue, obj, comune, decree_date, distinctive)
        if read.get('reading') or read.get('located'):   # the act is this issue's: no other is read for it
            return read | ({'read_in': issue['url']} if issue is not held[0] else {})
        causes.append(read['read'] if len(held) == 1 else f"{issue['url']}: {read['read']}")
    return {'read': '; '.join(causes)}


TITLE_CHARS = 400   # an act's title follows its heading; the decree's own text begins within this


def _concatenated(texts) -> tuple[str, list[int]]:
    """Pages' texts as one text, each page's words broken by a hyphen joined, with where each page starts."""
    starts, text = [], ''
    for page in texts:
        starts.append(len(text))
        text += _joined(page or '') + '\n'
    return text, starts


def _acts(text: str, obj: str, comune: str, decree_date: date | None, distinctive: set[str]):
    """The acts of notable public interest `text` prints titled as the layer's object. Returns whether any is titled
    so (a contents entry included), the best title's score, and the preambles of the acts holding it, each (where the
    act begins, where its first dispositive begins)."""
    import bisect
    heads = sorted({m.start() for m in _ACT_HEADING.finditer(text)} | {m.start() for m in _REGION_HEADING.finditer(text)})
    # An act begins at its heading, or after the job number closing the act before it (its heading may be misread);
    # it runs to the next heading, so a job number OCR reads out of order does not cut it.
    name = _words(re.split(r'[-–(,]|â€“', comune or '')[0])
    printed_object = set(_words(f'{obj} {comune}').split())
    named, scored = False, {}
    for a in sorted(set(heads) | {m.end() for m in _ACT_END.finditer(text)}):
        b = heads[bisect.bisect_right(heads, a)] if bisect.bisect_right(heads, a) < len(heads) else len(text)
        heading = _ACT_HEADING.match(text, a) or _REGION_HEADING.match(text, a)
        start = heading.end() if heading else a
        printed = text[start:min(b, start + TITLE_CHARS)]
        printed = printed[:m.start()] if (m := _TITLE_END.search(printed)) else printed
        # A title's "(in) provincia di X" names the province, not the place declared.
        title = _words(re.sub(r'\bprovincia\s+di\s+\S+', ' ', printed, flags=re.I))
        held = distinctive & set(title.split())
        dated = bool(heading and decree_date and _heading_date(heading.group(0)) == decree_date)
        if ' NOTEVOLE INTERESSE PUBBLICO ' not in _words(text[a:b]) or not (
                len(held) >= 2 or held and (dated or held == distinctive) or name.strip() and name in title):
            continue
        # Between titles holding as much, the one printing fewest words the object does not is the declaration's.
        extra = len({w for w in title.split() if len(w) >= 3 and w not in _PARTICLES} - printed_object)
        named = True
        if _CONTENTS.search(printed):
            continue   # the issue's contents: its title only
        end = next((m.start() for m in _DECRETA.finditer(text, a, b)), None)   # the act's first dispositive
        scored.setdefault(end, []).append(((len(held), dated, -extra), a))
    # The act whose title holds the most distinctive words (then prints the date, then the fewest words the object
    # does not) is read, and only it: where its dispositive is not read, no other act is taken for it.
    best = max((score for acts in scored.values() for score, _ in acts), default=None)
    preambles = sorted((max(a for score, a in acts if score == best), end) for end, acts in scored.items()
                       if end is not None and any(score == best for score, _ in acts))
    return named, best, preambles


def _preamble(text: str, preambles) -> dict:
    """The rows' copy of the act read: its heading and title, and its preamble."""
    return {'decree_act': [re.sub(r'\s+', ' ', text[x:x + 200]).strip() for x, _ in preambles],
            'decree_text': [re.sub(r'\s+', ' ', text[x:y]).strip() for x, y in preambles]}


def _span(text: str, starts: list[int], preambles) -> dict[int, str]:
    """The pages (0-based) the acts read lie on, from each act's first page through the page holding its first
    dispositive, each with why it is in."""
    import bisect
    page = lambda i: bisect.bisect_right(starts, i) - 1   # noqa: E731
    why = defaultdict(list)
    for x, y in preambles:
        dispositive = re.sub(r'\s+', ' ', _DECRETA.match(text, y).group(0)).strip()
        for p in range(page(x), page(y) + 1):
            why[p].append("holds the act's heading and its first dispositive" if page(x) == p == page(y) else
                          "holds the act's heading" if p == page(x) else 'holds its first dispositive' if p == page(y)
                          else "lies between the act's heading and its first dispositive")
            if p == page(y):
                why[p][-1] += f' ("{dispositive}" as OCR reads it)'
    return {p: '; '.join(reasons) for p, reasons in sorted(why.items())}


def _read_issue(store: Path, issue: dict, obj: str, comune: str, decree_date: date | None,
                distinctive: set[str]) -> dict:
    """The declaration's decree in one held issue: located in the text its text layer and OCR give, and read from its
    text layer or, where a page of it is a page image, from that page's vision transcription."""
    import bisect
    texts, route = page_texts(store, issue['sha256'])
    state = {'pages': route['pages'], 'ocr_pages': [i + 1 for i in route['ocr_pages']]}
    if route.get('not read') and all(t is None for t in texts):
        return state | {'read': f"page images: no text layer to read, and they are not read by OCR: {route['not read']}"}
    text, starts = _concatenated(texts)
    named, best, preambles = _acts(text, obj, comune, decree_date, distinctive)
    if best is not None and not preambles:
        return state | {'read': 'the act titled as the layer\'s object prints no "decreta" in the text read'}
    unread = f"; {len(route['ocr_pages'])} page images are not read: {route['not read']}" if route.get('not read') else ''
    if not preambles:
        where = 'the text layer holds' if not route['ocr_pages'] or unread else "its OCR'd pages hold" if len(
            route['ocr_pages']) == route['pages'] else "its text layer and OCR'd pages hold"
        return state | {'read': f'{where} no decree of notable public interest titled as the layer\'s object {obj!r}' + (
            ', only its title (its contents): the decree is printed elsewhere' if named else '') + unread}
    span = _span(text, starts, preambles)
    page = lambda i: bisect.bisect_right(starts, i) - 1   # noqa: E731
    images = [p for p in span if p in route['ocr_pages']]
    state |= {'located': [{'sha256': issue['sha256'], 'page': p + 1, 'page_image': p in images, 'why': why}
                          for p, why in span.items()]}
    # The pages the preamble lies on (its first dispositive may begin the next page, which is located, not read).
    pages = ', '.join(str(p + 1) for p in sorted({p for x, y in preambles for p in range(page(x), page(y - 1) + 1)}))
    if not images:
        reading, cite, genus = read_motivation(obj, ' '.join(text[x:y] for x, y in preambles)[:200000] + '.')
        if reading in ('not read whole', 'area'):   # the decree's own text is whole: naming no tree, it protects an area
            reading, cite = 'area', _area_cite(None, "the decree's text")
        return state | {'read': 'read from the text layer' + unread, 'reading': reading, 'cite': cite,
                        'genus': genus} | _preamble(text, preambles)
    held = transcriptions(store, issue['sha256'], images)
    missing = [p for p in images if p not in held]
    if missing:
        # Until its pages are transcribed, the decree keeps the reading of the words Tesseract gives, naming that.
        reading, cite, genus = read_motivation(obj, ' '.join(text[x:y] for x, y in preambles)[:200000] + '.')
        if reading in ('not read whole', 'area'):
            reading, cite = 'area', _area_cite(route, "the decree's text") + _untranscribed(missing)
        return state | {'read': f'read by OCR, page {pages} ({ocr_route(route)})' + unread + _untranscribed(missing),
                        'reading': reading, 'cite': cite, 'genus': genus} | _preamble(text, preambles)
    # Every page of the act read is transcribed: the act is cut from the transcribed text as from the located text,
    # and only there; where the transcription does not bear the location out, that is the cause and nothing is read.
    pages_read = list(span)
    transcribed, at = _concatenated([held[p]['text'] if p in held else texts[p] for p in pages_read])
    _, found, cut = _acts(transcribed, obj, comune, decree_date, distinctive)
    used = [{k: held[p][k] for k in ('page', 'model', 'request_sha256')} for p in images]
    located = f"located by OCR ({ocr_route(route)})"
    page_of = lambda i: pages_read[bisect.bisect_right(at, i) - 1]   # noqa: E731
    first = sorted({page(x) for x, _ in preambles})   # where OCR located each act read to begin
    if not cut:
        span_pages = ', '.join(str(p + 1) for p in pages_read)
        cause = (f'the transcription of page {span_pages} holds the act titled as the layer\'s object but no "Decreta"'
                 if found is not None else
                 f"the transcription of page {span_pages} holds no act titled as the layer's object")
        return state | {'transcriptions': used, 'read': f'not read: {cause} ({vision_route(used)}); {located}' + unread}
    starts_read = sorted({page_of(x) for x, _ in cut})
    if starts_read != first:
        return state | {'transcriptions': used,
                        'read': f"not read: the act's start page is wrong: the transcription begins the act titled as "
                                f"the layer's object on page {', '.join(str(p + 1) for p in starts_read)}, OCR on page "
                                f"{', '.join(str(p + 1) for p in first)} ({vision_route(used)}); {located}" + unread}
    preamble = ' '.join(transcribed[x:y] for x, y in cut)
    reading, cite, genus = read_motivation(obj, preamble[:200000] + '.')
    if reading in ('not read whole', 'area'):   # the decree's own text is whole: naming no tree, it protects an area
        reading, cite = 'area', _vision_cite(used, preamble)
    read_pages = sorted({p for x, y in cut for p in range(page_of(x), page_of(y - 1) + 1)})
    return state | {'read': (f"read from the vision transcription of page {', '.join(str(p + 1) for p in read_pages)} "
                             f"({vision_route(used)}){_unreadable(preamble)}; {located}" + unread),
                    'reading': reading, 'cite': cite, 'genus': genus, 'transcriptions': used} | _preamble(transcribed, cut)


# The scheda's identification page prints the motivation after its heading and before the art. 134 classification.
_RECOGNITION = re.compile(r"riconoscimento.{0,3}\s*\(del valore dell.area\)\s*(.*?)\s*art\.\s*134", re.S | re.I)


def _scheda_reading(store: Path, scheda: dict | None, obj: str) -> dict | None:
    """The declaration's motivation as its PPTR scheda (elaborato 6.4) prints it, read whole: from its text layer,
    or, where its identification page (located by OCR) is a page image, from that page's vision transcription."""
    if not scheda or not scheda.get('sha256'):
        return None
    texts, route = page_texts(store, scheda['sha256'], upto=lambda t: bool(_RECOGNITION.search(t)))
    found = _RECOGNITION.search(texts[-1] or '') if texts else None
    state = {'scheda': scheda['sha256'], 'scheda_pages': route['pages']}
    if not found:
        unread = f"; {len(route['ocr_pages'])} page images are not read: {route['not read']}" if route.get('not read') else ''
        return state | {'scheda_read': 'the scheda prints no motivation in its text layer' + (
            " or its OCR'd pages" if route['ocr_pages'] and not unread else '') + unread}
    index = len(texts) - 1
    if index not in route['ocr_pages']:
        motivation = re.sub(r'\s+', ' ', _joined(found.group(1))).strip()
        reading, cite, genus = read_motivation(obj, motivation + '.')
        if reading in ('not read whole', 'area'):   # the scheda prints it whole: naming no tree, it protects an area
            reading, cite = 'area', _area_cite(None, "the scheda's motivation")
        return state | {'scheda_read': 'read from the text layer', 'scheda_motivation': motivation,
                        'scheda_reading': reading, 'scheda_cite': cite, 'scheda_genus': genus}
    state |= {'scheda_located': {'page': index + 1, 'why': "the scheda's identification page: its motivation between "
                                                           "'riconoscimento' and 'art. 134'"}}
    held = transcriptions(store, scheda['sha256'], [index])
    if not held:   # until the page is transcribed, the words Tesseract gives, naming that
        motivation = re.sub(r'\s+', ' ', _joined(found.group(1))).strip()
        reading, cite, genus = read_motivation(obj, motivation + '.')
        if reading in ('not read whole', 'area'):
            reading, cite = 'area', _area_cite(route, "the scheda's motivation") + _untranscribed([index])
        return state | {'scheda_read': f'read by OCR, page {index + 1} ({ocr_route(route)})' + _untranscribed([index]),
                        'scheda_motivation': motivation, 'scheda_reading': reading, 'scheda_cite': cite,
                        'scheda_genus': genus}
    used = [{k: held[index][k] for k in ('page', 'model', 'request_sha256')}]
    located = f'located by OCR ({ocr_route(route)})'
    found = _RECOGNITION.search(held[index]['text'])
    if not found:
        return state | {'scheda_transcriptions': used, 'scheda_read': (
            f"not read: the transcription of page {index + 1} prints no motivation between 'riconoscimento' and "
            f"'art. 134' ({vision_route(used)}); {located}")}
    motivation = re.sub(r'\s+', ' ', _joined(found.group(1))).strip()
    reading, cite, genus = read_motivation(obj, motivation + '.')
    if reading in ('not read whole', 'area'):   # the scheda prints it whole: naming no tree, it protects an area
        reading, cite = 'area', _vision_cite(used, motivation)
    return state | {'scheda_read': f'read from the vision transcription of page {index + 1} ({vision_route(used)})'
                                   f'{_unreadable(motivation)}; {located}',
                    'scheda_motivation': motivation, 'scheda_reading': reading, 'scheda_cite': cite,
                    'scheda_genus': genus, 'scheda_transcriptions': used}


def transcription_population(declared: list[Declaration]) -> list[dict]:
    """The pages the vision pass transcribes: for each declaration whose decree OCR locates on page images, each page
    image of its act from the act's first page through the page holding its first dispositive; and the identification
    page of each scheda OCR locates on a page image. One row per declaration and page, with why the page is in."""
    out = []
    for d in declared:
        held = d.decree or {}
        out += [{'code': d.code, 'sha256': p['sha256'], 'page': p['page'], 'why': 'its decree: ' + p['why']}
                for p in held.get('located') or () if p['page_image']]
        if held.get('scheda_located'):
            out.append({'code': d.code, 'sha256': held['scheda'], 'page': held['scheda_located']['page'],
                        'why': 'its scheda: ' + held['scheda_located']['why']})
    return out


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
                                           + ' | '.join(f'{decl.code}: {decl.unread()}' for decl in unread)}
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
                                           'term could leave out of a zone a declared tree it reaches'},
                         'ocr': {'engine': _engine_recorded(),
                                 'page_rule': f'a page is read by OCR where its text layer does not supply it: an image '
                                              f'covers at least {PAGE_IMAGE_SHARE:.0%} of the page and its layer holds '
                                              f'fewer than {MIN_TEXT_PER_PAGE} characters, or fewer than '
                                              f'{MIN_VOWEL_SHARE:.0%} of its words of four letters or more hold a vowel',
                                 'kept': f'derived/{OCR_FOLDER} (regenerable)',
                                 'role': 'locates the act and its pages, and a scheda\'s identification page; it reads '
                                         'a page only until that page\'s vision transcription is held'},
                         'transcription': {'provider': TRANSCRIPTION_PROVIDER, 'model': TRANSCRIPTION_MODEL,
                                           'effort': TRANSCRIPTION_EFFORT, 'dpi': TRANSCRIPTION_DPI,
                                           'prompt': TRANSCRIPTION_PROMPT, 'illegible': ILLEGIBLE,
                                           'kept': f'derived/{TRANSCRIPTION_FOLDER} (kept and replicated: a model\'s '
                                                   f'answer)',
                                           'population': transcription_population(result['declarations'])}},
        'problems': result['problems'], 'in_zone': in_zone, 'groups': groups,
        'distances': {'positives': result['positives'],
                      'nearest_listed_entry': listed[0] if listed else None,
                      'listed_within_1km': sum(1 for d, *_ in listed if d <= 1000),
                      'listed_within_5km': sum(1 for d, *_ in listed if d <= 5000),
                      'declared_trees': {d.code: nearest_of.get(d.code) for d in result['declarations']
                                         if d.reading in ('names a tree', 'names a row or group')}}}

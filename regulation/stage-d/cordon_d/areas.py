"""Demarcated-area versions, read from the act that adopted them.

An area version is an accepted Stage A row: its identity, interval, subspecies
and act-level state come from A and are not re-derived here. What this reader
adds is the area statement the act itself makes.

Most adopting acts carry that statement as a cadastral annex: per zone, the
province, the comune and the fogli di mappa, with an asterisk where a foglio is
wholly contained rather than partially intersecting, or a whole-territory
statement for a comune or province. That statement answers Stage A's membership
predicate directly, through the evidence reader, with no metric frame and no
positional error bound - which no source for these areas publishes.

Published polygons are a different thing and are treated as one: DDS 45/2025
establishes that the act creates the area and InnovaPuglia transmits shapefiles
afterwards, so a capture is the publisher's representation at its capture time
and needs corroboration before it is offered as the act's adopted geography.

The cadastral tables are column-positional. Columns are located from each
table's own printed header, never from a per-act rule. A cell the reader cannot
resolve, and a table whose layout shares one statement across a run of comuni,
are carried as unresolved with their literal text; nothing is guessed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re

ZONE_HEADING = re.compile(r'ZONA\s+(INFETTA|CUSCINETTO|CONTENIMENTO)', re.I)
ANNEX_MARKER = re.compile(r'ALLEGATO\s*2\b', re.I)
HEADER_PROVINCE = re.compile(r'\bPROVINCIA\b')
HEADER_COMUNE = re.compile(r'\bCOMUNE\b')
HEADER_SHEETS_TITLE = re.compile(r'\bFOGLI(?:O|A)?\b\s*DI\s*MAPPA', re.I)
HEADER_SHEETS = re.compile(r'\bFOGLI(?:O|A)?\b', re.I)
# Vocabulary the tables print as column headings and legends, never as data.
HEADER_TEXT = re.compile(
    r'FOGLI\s*DI\s*MAPPA|IL\s*SIMBOLO|INTERAMENTE\s*CONTENUTO|RICADENT|BUFFER'
    r'|PIANTE\s*RISULTATE|CATASTALI|PRESENTE\s*ALLEGATO|DIRIGENTE|METROPOLITANA', re.I)
WHOLE_PROVINCE = re.compile(r'INTERO\s+TERRITORIO\s+PROVINCIALE', re.I)
WHOLE_COMUNE = re.compile(r'INTERO\s+TERRITORIO\s+COMUNALE', re.I)
SECTION = re.compile(r'SEZIONE\s+([A-Z])\s*:?', re.I)
SHEET_TOKEN = re.compile(r'(\d+)\s*(\*?)')
PARCELS = re.compile(r'\bparticell\w*\b\s*:?', re.I)
PAGE_NOISE = re.compile(r'Bollettino\s+Ufficiale|^\s*\d{1,5}\s*$|^\s*\f')

ZONE_KINDS = {'INFETTA': 'infetta', 'CUSCINETTO': 'cuscinetto', 'CONTENIMENTO': 'contenimento'}


@dataclass(frozen=True)
class Sheet:
    """One cadastral sheet as the annex states it."""
    section: str | None
    number: str
    wholly_contained: bool


@dataclass(frozen=True)
class CadastralStatement:
    """One area statement the act makes: a zone, a place, and its cadastral scope."""
    zone: str                     # infetta | cuscinetto | contenimento
    zone_heading: str             # the literal heading the zone was read from
    province: str | None
    comune: str | None
    scope: str                    # whole-province | whole-comune | sheets
    sheets: tuple[Sheet, ...]
    text: str                     # literal cell text read

    def covers(self, *, comune: str | None = None, province: str | None = None,
               section: str | None = None, foglio: str | None = None) -> bool | None:
        """Whether this statement places the named place in its zone.

        True or False where the statement decides it; None where it is about a
        different place or does not decide, so the caller keeps looking. A
        whole-province statement decides only for a caller that states the
        province: which province a comune belongs to is an administrative fact
        this row does not hold, and assuming it would place comuni in or out of
        an infected zone on no evidence.
        """
        if self.scope == 'whole-province':
            if province is None:
                return None
            return (self.province or '').upper() == province.upper() or None
        if comune is not None and (self.comune or '').upper() != comune.upper():
            return None
        if self.scope == 'whole-comune':
            return True
        if foglio is None:
            return None
        for sheet in self.sheets:
            if sheet.number == str(foglio) and (section is None or sheet.section is None
                                                or sheet.section.upper() == section.upper()):
                return True
        return False


@dataclass(frozen=True)
class Annex:
    """An annex the act names, with the hash the act prints for it where it does."""
    name: str
    stated_sha256: str | None


@dataclass(frozen=True)
class AreaVersion:
    provision_version_id: str
    instrument_id: str
    effective_from: date
    effective_to_exclusive: date | None
    temporal_status: str
    state: str                    # A's own words for subspecies and act-level state
    source_path: str
    geography_form: str           # annexed | stated-rule | adopts-none | body-unheld
    annexes: tuple[Annex, ...]
    statements: tuple[CadastralStatement, ...]
    unresolved: tuple[str, ...]   # literal lines and tables the reader would not guess at

    @property
    def in_force_on(self):
        def test(day: date) -> bool:
            if day < self.effective_from:
                return False
            return self.effective_to_exclusive is None or day < self.effective_to_exclusive
        return test


def reader_version() -> str:
    digest = sha256()
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()[:12]


# --- reading the act's cadastral annex ---------------------------------------

def _column_offsets(lines, header_index):
    """Locate the three columns from the table's own printed header.

    The sheets column title may sit on the header line or on the lines
    immediately above or below it; the tables place it there, so it is read
    from there. The full title is preferred over a bare `FOGLIO`, because the
    legend sentence beside these headers ("IL SIMBOLO * INDICA CHE IL FOGLIO E'
    INTERAMENTE CONTENUTO") also contains that word and sits further right.
    """
    line = lines[header_index]
    province = HEADER_PROVINCE.search(line)
    comune = HEADER_COMUNE.search(line)
    if not province or not comune:
        return None
    candidates = []
    for offset in (-2, -1, 0, 1, 2):
        index = header_index + offset
        if not 0 <= index < len(lines):
            continue
        for pattern, rank in ((HEADER_SHEETS_TITLE, 0), (HEADER_SHEETS, 1)):
            for match in pattern.finditer(lines[index]):
                if match.start() > comune.start():
                    candidates.append((rank, match.start()))
    if not candidates:
        return None
    best_rank = min(rank for rank, _ in candidates)
    sheets_at = min(start for rank, start in candidates if rank == best_rank)
    return province.start(), comune.start(), sheets_at


def _parse_sheets(text):
    """Read `SEZIONE A: FOGLIO 1, 2*` and `FOGLI 9, 11*` into stated sheets."""
    sheets, section = [], None
    for part in re.split(r'(SEZIONE\s+[A-Z]\s*:?)', text, flags=re.I):
        if not part or not part.strip():
            continue
        marker = SECTION.fullmatch(part.strip())
        if marker:
            section = marker.group(1).upper()
            continue
        for number, star in SHEET_TOKEN.findall(part):
            sheets.append(Sheet(section, number, star == '*'))
    return tuple(sheets)


def _classify(text):
    if WHOLE_PROVINCE.search(text):
        return 'whole-province', ()
    if WHOLE_COMUNE.search(text):
        return 'whole-comune', ()
    if PARCELS.search(text):
        # Some annexes narrow a sheet to named particelle ("FOGLIO 5: particelle
        # 260, 264"). Only the sheet before the parcel list is a sheet; reading
        # the parcel numbers as sheets would place whole sheets in the zone.
        sheets = _parse_sheets(PARCELS.split(text)[0])
        return ('sheet-parcels', sheets) if sheets else (None, ())
    sheets = _parse_sheets(text)
    return ('sheets', sheets) if sheets else (None, ())


def _read_segment(lines, start, end, heading, zone):
    """Read one zone's table. Returns (statements, unresolved-lines)."""
    statements, pending = [], []
    header_index = None
    for index in range(start, end):
        if HEADER_PROVINCE.search(lines[index]) and HEADER_COMUNE.search(lines[index]):
            header_index = index
            break
    if header_index is None:
        body = [l for l in lines[start:end] if l.strip() and not PAGE_NOISE.search(l)
                and not HEADER_TEXT.search(l) and not ZONE_HEADING.search(l)]
        return (), tuple(f'{heading} :: {l.strip()}' for l in body)
    offsets = _column_offsets(lines, header_index)
    if offsets is None:
        return (), (f'{heading} :: column header not resolvable',)
    province_at, comune_at, sheets_at = offsets

    # Read the body into cells first. A value cell is often centred against its
    # comune, so it can print above the comune's own line; attachment is decided
    # per run below, not by reading order.
    cells, province = [], None
    for index in range(header_index + 1, end):
        raw = lines[index]
        if not raw.strip() or PAGE_NOISE.search(raw):
            continue
        if HEADER_TEXT.search(raw) and not re.search(r'\d', raw[sheets_at:]):
            continue
        province_cell = raw[province_at:comune_at].strip()
        comune_cell = raw[comune_at:sheets_at].strip()
        value_cell = raw[sheets_at:].strip()
        if province_cell:
            province = province_cell
        if not comune_cell and not value_cell:
            continue
        cells.append({'province': province, 'comune': comune_cell or None,
                      'value': value_cell or None, 'raw': raw.strip()})

    # A run is the longest stretch of consecutive cells naming at most one
    # comune. Inside such a run the table is unambiguous: every value belongs to
    # that comune, wherever the printer centred it. Where a run names several
    # comuni but carries fewer values, which comuni a value covers is a layout
    # fact this text cannot settle, and the comuni without a value of their own
    # are left unresolved rather than guessed into or out of a zone.
    runs, current = [], []
    for cell in cells:
        named = {c['comune'] for c in current if c['comune']}
        if cell['comune'] and named and cell['comune'] not in named:
            runs.append(current)
            current = []
        current.append(cell)
    if current:
        runs.append(current)

    for run in runs:
        comuni = [c['comune'] for c in run if c['comune']]
        values = [c for c in run if c['value']]
        # Where a comune prints its value on its own line, that row is settled
        # and any further value in the run belongs to a neighbouring comune
        # whose own line prints no value - a wrapped or centred cell the text
        # layer no longer attaches. Attaching it here would put one comune's
        # sheets under another's name, so it is left unresolved.
        self_contained = [c for c in run if c['comune'] and c['value']]
        if self_contained:
            for cell in self_contained:
                scope, sheets = _classify(cell['value'])
                if scope is None:
                    pending.append(f'{heading} :: unread cell: {cell["raw"]}')
                    continue
                statements.append(CadastralStatement(
                    zone, heading, cell['province'],
                    None if scope == 'whole-province' else cell['comune'],
                    scope, sheets, cell['value']))
            for cell in values:
                if cell in self_contained:
                    continue
                pending.append(f'{heading} :: a value prints without a comune beside a settled '
                               f'row; its owner is not settled by this text: {cell["value"][:80]}')
            continue
        owner = comuni[0] if comuni else None
        for cell in values:
            scope, sheets = _classify(cell['value'])
            if scope is None:
                if statements and re.search(r'\d', cell['value']):
                    previous = statements[-1]
                    merged = previous.text + ' ' + cell['value']
                    scope, sheets = _classify(merged)
                    statements[-1] = CadastralStatement(
                        previous.zone, previous.zone_heading, previous.province,
                        previous.comune, scope or previous.scope,
                        sheets or previous.sheets, merged)
                    continue
                pending.append(f'{heading} :: unread cell: {cell["raw"]}')
                continue
            if scope == 'whole-province':
                statements.append(CadastralStatement(zone, heading, cell['province'], None,
                                                     scope, sheets, cell['value']))
                continue
            if owner is None:
                pending.append(f'{heading} :: statement with no comune in its run: {cell["value"]}')
                continue
            statements.append(CadastralStatement(zone, heading, cell['province'], owner,
                                                 scope, sheets, cell['value']))
        if len(comuni) > 1 or (comuni and not values):
            unserved = comuni[1:] if values else comuni
            for name in unserved:
                pending.append(f'{heading} :: {name} shares a centred statement with other '
                               f'comuni; its own scope is not settled by this text')
    return tuple(statements), tuple(pending)


def cadastral_statements(text):
    """Every area statement the act's cadastral annex makes, plus what was not read."""
    lines = text.split('\n')
    # The dispositivo also mentions "Allegato 2" in prose ("Riportare
    # nell'Allegato 2 ... i riferimenti catastali"). The annex itself begins
    # with the marker as a heading, so only a line that starts with it counts;
    # taking a prose mention would turn every later sentence naming a zone into
    # a table row.
    markers = [i for i, l in enumerate(lines)
               if ANNEX_MARKER.match(l.strip()) and len(l.strip()) <= 90]
    if not markers:
        return (), ()
    tail_start = markers[0]
    headings = [i for i in range(tail_start, len(lines)) if ZONE_HEADING.search(lines[i])]
    statements, unresolved = [], []
    for position, index in enumerate(headings):
        end = headings[position + 1] if position + 1 < len(headings) else len(lines)
        match = ZONE_HEADING.search(lines[index])
        zone = ZONE_KINDS[match.group(1).upper()]
        read, pending = _read_segment(lines, index, end, lines[index].strip(), zone)
        statements.extend(read)
        unresolved.extend(pending)
    # An act often prints its annex twice (as proposed and as adopted).
    unique, seen = [], set()
    for statement in statements:
        key = (statement.zone, statement.province, statement.comune, statement.text)
        if key in seen:
            continue
        seen.add(key)
        unique.append(statement)
    return tuple(unique), tuple(dict.fromkeys(unresolved))


def annexes(text):
    """The annexes the act names, with the hash it prints for each where it does."""
    found = []
    for match in re.finditer(r'^\s*(ALLEGAT[OI][^\n-]*?)\s*-\s*$', text, re.M):
        name = match.group(1).strip()
        rest = text[match.end():match.end() + 200]
        digest = re.search(r'\b([0-9a-f]{64})\b', rest)
        found.append(Annex(name, digest.group(1) if digest else None))
    if not found:
        for match in re.finditer(r'\b(ALLEGATO\s*\d[^\n]{0,20}?\.pdf)', text, re.I):
            found.append(Annex(match.group(1).strip(), None))
    return tuple(dict.fromkeys(found))


# --- binding A's accepted area versions to what their acts state ---------------

AREA_ROW = re.compile(r'area-state-transition|area-update|area-act-before-gis')


def _date(value):
    return date.fromisoformat(value) if value else None


def _act_text(root: Path, source_path: str) -> str:
    path = root / source_path
    if path.suffix.lower() == '.pdf':
        import subprocess
        return subprocess.run(['pdftotext', '-layout', str(path), '-'],
                              capture_output=True, text=True).stdout
    return path.read_text(errors='replace')


def versions(root: Path):
    """Every accepted Stage A area version, with the area statement its act makes.

    Identity, interval, subspecies and act-level state are A's; only the per-zone
    cadastral statement and the annex list are read from the act. A version whose
    own body is not held states that and reads nothing, so a successor's annex is
    never borrowed for it.
    """
    rows = json.loads((root / 'regulation/jurisdiction/canonical/authoring.json').read_text())
    if not isinstance(rows, list):
        rows = list(rows.values())[0]
    out = []
    for row in sorted((r for r in rows if AREA_ROW.search(r['provision_version_id'])),
                      key=lambda r: (r['effective_from'], r['provision_version_id'])):
        identity = row['provision_version_id']
        source_path = row.get('source_paths') or ''
        if 'unresolved' in identity:
            form, statements, unread, found = 'body-unheld', (), (
                'the act\'s own body is not held; its A row is written from a successor recital, '
                'so no area statement is read for this interval',), ()
        elif 'area-act-before-gis' in identity:
            form, statements, unread, found = 'adopts-none', (), (), ()
        else:
            text = _act_text(root, source_path)
            statements, unread = cadastral_statements(text)
            found = annexes(text)
            form = 'annexed' if statements or found else 'stated-rule'
        out.append(AreaVersion(
            provision_version_id=identity,
            instrument_id=row['instrument_id'],
            effective_from=_date(row['effective_from']),
            effective_to_exclusive=_date(row.get('effective_to_exclusive')),
            temporal_status=row.get('temporal_status', ''),
            state=(row.get('true_effect') or '').strip(),
            source_path=source_path,
            geography_form=form,
            annexes=found,
            statements=statements,
            unresolved=unread,
        ))
    return tuple(out)


def in_force(versions_, day: date):
    """The area versions whose interval contains this day."""
    return tuple(v for v in versions_ if v.in_force_on(day))


def zone_of(versions_, day: date, *, comune: str | None = None, province: str | None = None,
            section: str | None = None,
            foglio: str | None = None):
    """Which zones of which act versions place this cadastral place, on this day.

    Returns one entry per version in force that decides the question, with the
    zone and the statement that decided it. A version that states nothing about
    the place is absent; a version whose body or layout is unresolved is
    returned with zone None so the caller sees that it was not answered.
    """
    answers = []
    for version in in_force(versions_, day):
        if version.geography_form in ('body-unheld', 'adopts-none'):
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': version.geography_form})
            continue
        decided = False
        for statement in version.statements:
            verdict = statement.covers(comune=comune, province=province, section=section, foglio=foglio)
            if verdict:
                answers.append({'version': version.provision_version_id, 'zone': statement.zone,
                                'basis': 'act cadastral statement', 'statement': statement})
                decided = True
        if not decided and version.unresolved:
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': 'unresolved in this act', 'unresolved': len(version.unresolved)})
    return tuple(answers)

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

from .store import blob_path, store_root

# A caption names its zone in head position and may then qualify it with
# another zone or with the measures that apply there. The population prints
# both: "ZONA INFETTA IN CUI SI APPLICANO MISURE DI CONTENIMENTO" is an
# infected zone under containment measures, and "ZONA CUSCINETTO IN CUI SI
# APPLICANO ... MISURE DI ERADICAZIONE" is a buffer zone under eradication.
# So the head word decides the zone and the qualifier is kept as the regime;
# collapsing the two loses which zone the act says it is. Ordering the words
# by specificity instead reads the first caption as containment and the
# second as a buffer with no regime, which is why it is not done that way.
ZONE_WORD = re.compile(r'\b(FOCOLAI\w*|CUSCINETTO|CONTENIMENTO|INFETT[AO])\b', re.I)
ZONE_OF_WORD = {'CUSCINETTO': 'cuscinetto', 'CONTENIMENTO': 'contenimento',
                'INFETTA': 'infetta', 'INFETTO': 'infetta'}
REGIME_CLAUSE = re.compile(
    r'IN\s+CUI\s+SI\s+APPLICANO[^.;]*?\b(CONTENIMENTO|ERADICAZIONE)\b', re.I)
ZONE_HEADING = ZONE_WORD
ANNEX_MARKER = re.compile(r'ALLEGATO\s*2\b', re.I)
# Bari is a citta metropolitana, so the annexes head that column both ways.
HEADER_PROVINCE = re.compile(r"\bPROVINCIA\b|\bCITTA'?\s*\n?\s*METROPOLITANA\b", re.I)
HEADER_COMUNE = re.compile(r'\bCOMUNE\b')
HEADER_SHEETS_TITLE = re.compile(r'\bFOGLI(?:O|A)?\b\s*DI\s*MAPPA', re.I)
HEADER_SHEETS = re.compile(r'\bFOGLI(?:O|A)?\b', re.I)
# Vocabulary the tables print as column headings and legends, never as data.
HEADER_TEXT = re.compile(
    r'FOGLI\s*DI\s*MAPPA|IL\s*SIMBOLO|INTERAMENTE\s*CONTENUTO|RICADENT|BUFFER'
    r'|PIANTE\s*RISULTATE|CATASTALI|PRESENTE\s*ALLEGATO|DIRIGENTE', re.I)
WHOLE_PROVINCE = re.compile(r'INTERO\s+TERRITORIO\s+PROVINCIALE', re.I)
WHOLE_COMUNE = re.compile(r'INTERO\s+TERRITORIO\s+COMUNALE', re.I)
PART_COMUNE = re.compile(r'PARTE\s+TERRITORIO\s+COMUNALE', re.I)
SECTION = re.compile(r'SEZIONE\s+([A-Z])\s*:?', re.I)
SHEET_TOKEN = re.compile(r'(\d+)\s*(\*?)')
PARCELS = re.compile(r'\bparticell\w*\b\s*:?', re.I)
PAGE_NOISE = re.compile(r'Bollettino\s+Ufficiale|^\s*\d{1,5}\s*$|^\s*\f')

ZONE_KINDS = {'INFETTA': 'infetta', 'CUSCINETTO': 'cuscinetto', 'CONTENIMENTO': 'contenimento'}


@dataclass(frozen=True)
class Sheet:
    """One cadastral sheet as the annex states it.

    `wholly_contained` is the act's own asterisk: the sheet lies entirely in
    the zone. Without it the act says only that the sheet intersects the zone,
    which does not place any particular parcel inside it. `parcels` carries the
    particelle where the act narrows a sheet to named ones, and `qualifier`
    any development the act attaches to the sheet ("193 (SVILUPPO Z)").
    """
    section: str | None
    number: str
    wholly_contained: bool
    parcels: tuple[str, ...] = ()
    qualifier: str | None = None


@dataclass(frozen=True)
class Scope:
    """What an annex cell says about the extent of a place in its zone.

    `residue` is the consequential source text the reader could not account
    for. A scope with residue has not been read: the reader holds part of a
    statement whose whole it cannot see, which is the condition under which a
    partial reading silently becomes a wrong answer.
    """
    kind: str                       # whole-province | whole-comune
                                    # | part-comune-extent-unstated | sheets
    sheets: tuple[Sheet, ...]
    text: str
    residue: str = ''

    @property
    def fully_read(self) -> bool:
        return not self.residue


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
    # The measures the caption says apply in this zone, where it says. An
    # infected zone under containment measures is both facts at once, and A
    # states them separately, so this row does not collapse them into one.
    regime: str | None = None

    def covers(self, *, comune: str | None = None, province: str | None = None,
               section: str | None = None, foglio: str | None = None,
               particella: str | None = None, grain: str = 'parcel') -> bool | None:
        """Whether this statement places the named place in its zone.

        `grain` is the question being asked, and the two are not the same
        question. At `sheet` grain: is this cadastral sheet reached by the
        zone. At `parcel` grain, which is what Stage A's predicate asks: does
        this point or parcel lie inside it. A sheet the act marks with its
        asterisk lies wholly in the zone, so both answers are yes. A sheet
        without it only intersects the zone, so the sheet is reached and a
        particular parcel within it is undecided - the act does not say which
        part is inside.

        True or False where the statement decides the question; None where it
        does not, so the caller keeps looking and the predicate stays
        unresolved rather than becoming a negative. An unidentified place is
        never decided: a statement about one comune cannot answer a question
        that names no comune, and a sheet the act files under a section cannot
        answer a question that names no section.
        """
        if grain not in ('sheet', 'parcel'):
            raise ValueError("grain must be 'sheet' or 'parcel'")
        if self.scope == 'whole-province':
            if province is None:
                return None
            return True if (self.province or '').upper() == province.upper() else None
        # Below here the statement is about one comune, so the question must
        # name one. Province, where both state it, must not contradict.
        if comune is None:
            return None
        if (self.comune or '').upper() != comune.upper():
            return None
        if province is not None and self.province and \
                self.province.upper() != province.upper():
            return None
        if self.scope == 'whole-comune':
            return True
        if self.scope == 'part-comune-extent-unstated':
            return None
        if foglio is None:
            return None
        for sheet in self.sheets:
            if sheet.number != str(foglio):
                continue
            if sheet.section is not None and section is None:
                return None          # the act files this sheet under a section
            if sheet.section is not None and section is not None and \
                    sheet.section.upper() != section.upper():
                continue
            if grain == 'sheet':
                return True
            if sheet.parcels:
                # The act named the particelle it reaches inside this sheet.
                if particella is None:
                    return None
                return True if str(particella) in sheet.parcels else False
            return True if sheet.wholly_contained else None
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


# The scope grammar, taken from what the acts print rather than from the ones
# I happened to open. Enumerated over the whole population: whole-territory
# statements for a comune or a province, a part-of-comune statement, sheet
# lists under an optional section, inclusive ranges written "da 15 a 32" and
# also "161 a 172", particelle narrowing a sheet, and a parenthesised
# development on a sheet. Anything else is residue, and a cell with residue is
# not read - which is how the next form the publisher uses becomes a finding
# on first contact instead of a silently truncated answer.
SCOPE_TOKENS = (
    ('skip', re.compile(r'[\s,;:.()–—-]+')),
    ('skip', re.compile(r'\b(?:e|ed)\b', re.I)),
    ('whole-province', re.compile(r'INTERO\s+TERRITORIO\s+PROVINCIALE', re.I)),
    ('whole-comune', re.compile(r'INTERO\s+TERRITORIO\s+COMUNALE', re.I)),
    ('part-comune', re.compile(r'PARTE\s+TERRITORIO\s+COMUNALE', re.I)),
    ('section', re.compile(r'SEZIONE\s+([A-Z])\b', re.I)),
    ('sheet-word', re.compile(r'\bFOGLI(?:O|A|E)?\b(?:\s+DI\s+MAPPA)?'
                              r'(?:\s+CATASTALI)?', re.I)),
    ('parcels', re.compile(r'\bparticell\w*\b', re.I)),
    ('range', re.compile(r'\bda\s+(\d+)\s+a\s+(\d+)\b', re.I)),
    ('range', re.compile(r'\b(\d+)\s+a\s+(\d+)\b', re.I)),
    ('sheet', re.compile(r'(\d+)\s*(\*?)\s*(\((?:SVILUPPO|Sviluppo)[^)]*\))?')),
)
# Residue that cannot change what the cell means: stray single letters and
# punctuation left by extraction. Anything with a digit or a word in it can.
TRIVIAL_RESIDUE = re.compile(r'^[\W\d_]*$|^[A-Za-z]$')


def read_scope(text) -> Scope:
    """Read an annex cell, accounting for every consequential token in it."""
    source = ' '.join((text or '').split())
    cursor, residue = 0, []
    sheets, section = [], None
    whole, part_marker, reading_parcels = None, False, False
    while cursor < len(source):
        for name, pattern in SCOPE_TOKENS:
            match = pattern.match(source, cursor)
            if not match:
                continue
            cursor = match.end()
            if name == 'skip':
                pass
            elif name == 'sheet-word':
                # A new FOGLIO heading starts a new sheet; without this a
                # second clause's sheet number would be read as a parcel of
                # the first clause's sheet.
                reading_parcels = False
            elif name in ('whole-province', 'whole-comune'):
                whole = name
            elif name == 'part-comune':
                part_marker = True
            elif name == 'section':
                section, reading_parcels = match.group(1).upper(), False
            elif name == 'parcels':
                reading_parcels = True
            elif name == 'range':
                low, high = int(match.group(1)), int(match.group(2))
                if low > high or high - low > 500:
                    residue.append(match.group(0))
                else:
                    sheets.extend(Sheet(section, str(n), False)
                                  for n in range(low, high + 1))
                    reading_parcels = False
            elif name == 'sheet':
                if reading_parcels and sheets:
                    last = sheets[-1]
                    sheets[-1] = Sheet(last.section, last.number, last.wholly_contained,
                                       last.parcels + (match.group(1),), last.qualifier)
                else:
                    sheets.append(Sheet(section, match.group(1), match.group(2) == '*',
                                        (), (match.group(3) or None)))
            break
        else:
            residue.append(source[cursor])
            cursor += 1
    leftover = ' '.join(''.join(residue).split())
    if TRIVIAL_RESIDUE.match(leftover):
        leftover = ''
    # "PARTE TERRITORIO COMUNALE: FOGLIO 6" states which part: the sheets it
    # lists. The part marker only leaves the extent unstated when the act
    # lists nothing after it.
    if sheets:
        kind = 'sheets'
    elif whole:
        kind = whole
    elif part_marker:
        kind = 'part-comune-extent-unstated'
    else:
        kind = 'none'
    return Scope(kind, tuple(sheets), source, leftover)


def _classify(text):
    """Backward-compatible shape for the text reader: (kind, sheets)."""
    scope = read_scope(text)
    if not scope.fully_read or scope.kind == 'none':
        return None, ()
    return scope.kind, scope.sheets


def _parse_sheets(text):
    return read_scope(text).sheets


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
        zone, _, _ = _zone_from(lines[index])
        if zone is None:
            continue
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
    """The annexes the act names, with the hash it prints for each where it does.

    The act prints these as a list under `ALLEGATI INTEGRANTI`, each entry a
    document name followed by its SHA-256. The name is not always numbered:
    DDS 92/2024 prints a single bundled `Allegato.pdf`. So entries are found by
    the list's own shape - a document name ending in a file extension, followed
    by a separator - rather than by a numbering convention, and each entry's
    hash is taken from the text before the next entry begins, so one entry can
    never borrow its neighbour's digest.
    """
    block = text
    marker = re.search(r'ALLEGAT[IO]\s+INTEGRANT[IE]', text, re.I)
    if marker:
        block = text[marker.end():]
        closing = re.search(r'\n\s*(Il presente Provvedimento|IL DIRIGENTE|'
                            r'Bollettino Ufficiale)', block)
        if closing:
            block = block[:closing.start()]
    entries = [(m.start(), m.end(), m.group(1).strip())
               for m in re.finditer(r'^\s*([^\n]*?\.(?:pdf|p7m|zip|dwg|xlsx?))\s*-?\s*$',
                                    block, re.M | re.I)]
    found = []
    for index, (_, end, name) in enumerate(entries):
        stop = entries[index + 1][0] if index + 1 < len(entries) else len(block)
        digest = re.search(r'\b([0-9a-f]{64})\b', block[end:stop])
        found.append(Annex(name, digest.group(1) if digest else None))
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
    documents = act_documents(root)
    store = store_root(root)
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
            found = annexes(text)
            record = documents.get(row['instrument_id'])
            statements, unread, form = (), (), None
            if record:
                # The act's own document bounds each annex cell, so a wrapped or
                # centred value stays with its comune. The extracted text cannot
                # do that, so it is only the fallback.
                blob = blob_path(store, record['sha256'])
                if blob.exists():
                    statements, unread = annex_statements(str(blob))
                    form = 'annexed-document'
            if not statements:
                # The fallback adds a second reading; it does not overwrite what
                # the first one could not read. Losing that diagnostic would let
                # an unread annex leave no trace at all.
                fallback, fallback_unread = cadastral_statements(text)
                statements = fallback
                unread = tuple(unread) + tuple(fallback_unread)
                if fallback:
                    form = 'annexed-text'
            if not statements:
                # An act states a rule only when nothing in it went unread. If a
                # reader met an annex and failed on it, that is an unread annex,
                # not an act that annexes nothing.
                form = 'annex-unread' if (unread or found) else 'stated-rule'
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
            section: str | None = None, foglio: str | None = None,
            particella: str | None = None, grain: str = 'parcel'):
    """Which zones of which act versions place this cadastral place, on this day.

    One entry per version in force that decides the question, with the zone and
    the statement that decided it. A version that left part of its own annex
    unread is always reported alongside, whether or not another part of it
    answered: an answered zone is not evidence that the rest of the act was
    read, and treating it that way is how a partial reading passes for a whole
    one.
    """
    answers = []
    for version in in_force(versions_, day):
        if version.geography_form in ('body-unheld', 'adopts-none'):
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': version.geography_form})
            continue
        zones_given = set()
        for statement in version.statements:
            verdict = statement.covers(comune=comune, province=province, section=section,
                                       foglio=foglio, particella=particella, grain=grain)
            if verdict and statement.zone not in zones_given:
                zones_given.add(statement.zone)
                answers.append({'version': version.provision_version_id, 'zone': statement.zone,
                                'regime': statement.regime,
                                'basis': 'act cadastral statement', 'statement': statement})
        if version.unresolved:
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': 'part of this act was not read',
                            'unresolved': len(version.unresolved)})
    return tuple(answers)


# --- reading the cadastral annex from the act's own table geometry ------------

def _zone_from(text):
    """The zone a caption names, and the measures regime it states for it.

    The head word decides the zone: a caption that names a buffer and then
    qualifies it with another zone is still about the buffer. The regime, when
    the caption states one, is a separate fact and is returned separately.
    """
    text = text or ''
    match = ZONE_WORD.search(text)
    if not match:
        return None, None, None
    word = match.group(1).upper()
    zone = 'focolaio' if word.startswith('FOCOLAI') else ZONE_OF_WORD[word]
    regime_match = REGIME_CLAUSE.search(text)
    regime = regime_match.group(1).lower() if regime_match else None
    return zone, match.group(0), regime


def annex_statements(document) -> tuple:
    """Read every cadastral annex table in the act document.

    The document carries the annex as a real table, so a value that wraps or
    prints centred against its comune stays inside that comune's own cell. This
    is what the text layer cannot do, and it is why the document rather than the
    extracted text is this row's source.

    Tables are located by their own printed header (PROVINCIA / COMUNE / a
    sheets column), never by page number or act identity.
    """
    import pymupdf
    statements, unresolved = [], []
    opened = pymupdf.open(document) if not hasattr(document, 'page_count') else document
    try:
        for page in opened:
            page_tables = page.find_tables().tables
            table_tops = sorted(t.bbox[1] for t in page_tables)
            # Captions printed above a ruled table rather than inside it. A
            # caption belongs to the nearest table below it, so a block is a
            # candidate for this table only when no other table stands between
            # them - which is what stopped a table from taking a neighbour's
            # zone when this was a page-wide search.
            captions = []
            for block in page.get_text('blocks'):
                x0, y0, x1, y1, text = block[0], block[1], block[2], block[3], block[4]
                zone, heading, regime = _zone_from(' '.join(text.split()))
                if zone:
                    captions.append((y1, ' '.join(text.split()), zone, regime))

            def caption_above(top):
                best = None
                for bottom, text, zone, regime in captions:
                    if bottom > top:
                        continue
                    if any(bottom < other < top - 0.5 for other in table_tops):
                        continue
                    if best is None or bottom > best[0]:
                        best = (bottom, text, zone, regime)
                return best

            for table in page_tables:
                rows = [[(c or '').strip() for c in row] for row in table.extract()]

                def header_of(matrix):
                    for index, row in enumerate(matrix):
                        joined = ' '.join(row)
                        if HEADER_PROVINCE.search(joined) and HEADER_COMUNE.search(joined):
                            return index
                    return None

                header_at, transposed = header_of(rows), False
                if header_at is None:
                    # Some annexes print the table on its side, with PROVINCIA
                    # and COMUNE running down a column and one record per
                    # column. Read it the same way, turned back.
                    turned = [list(column) for column in zip(*rows)] if rows else []
                    header_at = header_of(turned)
                    if header_at is None:
                        continue
                    rows, transposed = turned, True
                columns = rows[header_at]
                try:
                    province_col = next(i for i, c in enumerate(columns) if HEADER_PROVINCE.search(c))
                    comune_col = next(i for i, c in enumerate(columns) if HEADER_COMUNE.search(c))
                    value_col = next(i for i, c in enumerate(columns)
                                     if HEADER_SHEETS.search(c) or WHOLE_PROVINCE.search(c)
                                     or re.search(r'CATASTAL', c, re.I))
                except StopIteration:
                    unresolved.append(f'table header without a sheets column: {" | ".join(columns)[:120]}')
                    continue
                # The zone is stated by the table's own caption row, or by the
                # caption printed immediately above it.
                zone, heading, regime = None, None, None
                for row in rows[:header_at]:
                    zone, _, regime = _zone_from(' '.join(row))
                    if zone:
                        heading = ' '.join(c for c in row if c).strip()
                        break
                if zone is None:
                    above = caption_above(table.bbox[1])
                    if above:
                        _, heading, zone, regime = above
                if zone is None:
                    unresolved.append('annex table states no zone of its own and no caption '
                                      'stands above it; its rows are left unread rather than '
                                      'given a neighbouring zone: ' + ' | '.join(columns)[:90])
                    continue
                # A cell shared down a run of comuni is drawn once, spanning
                # their rows. The table reports that span as the cell's own
                # height, so a comune is covered by the value whose cell
                # vertically contains it - which is how the page reads.
                # Cell spans belong to the printed rows; once the table is
                # turned back they no longer describe these records.
                boxes = [] if transposed else [
                    getattr(r, 'cells', None) for r in getattr(table, 'rows', [])]
                # In a turned table a record that names no comune is a wrapped
                # continuation of the single comune the table names.
                sole_comune = None
                if transposed:
                    named = {row[comune_col].strip() for row in rows[header_at + 1:]
                             if len(row) > comune_col and row[comune_col].strip()}
                    sole_comune = next(iter(named)) if len(named) == 1 else None

                def spans(column):
                    found = []
                    for index, row in enumerate(rows):
                        cell = boxes[index][column] if index < len(boxes) and boxes[index] \
                            and column < len(boxes[index]) else None
                        if cell and index > header_at and len(row) > column and row[column].strip():
                            found.append((cell[1], cell[3], row[column].strip()))
                    return found

                value_spans, province_spans = spans(value_col), spans(province_col)

                def covering(spans_, cell):
                    if not cell:
                        return None
                    middle = (cell[1] + cell[3]) / 2
                    for top, bottom, text in spans_:
                        if top - 0.5 <= middle <= bottom + 0.5:
                            return text
                    return None

                province = None
                for index, row in enumerate(rows[header_at + 1:], start=header_at + 1):
                    if len(row) <= max(province_col, comune_col, value_col):
                        continue
                    cells = boxes[index] if index < len(boxes) and boxes[index] else []
                    comune_box = cells[comune_col] if comune_col < len(cells) else None
                    if row[province_col]:
                        province = row[province_col]
                    elif comune_box:
                        province = covering(province_spans, comune_box) or province
                    comune = row[comune_col] or None
                    value = row[value_col]
                    if not value and comune and _classify(comune)[0] in (
                            'whole-province', 'whole-comune'):
                        # A province-wide statement is printed across the comune
                        # column, because it names no comune.
                        value, comune = comune, None
                    if not value and comune and comune_box:
                        value = covering(value_spans, comune_box)
                    if value and not comune and sole_comune:
                        comune = sole_comune
                    if not value:
                        if comune:
                            unresolved.append(
                                f'{heading} :: {comune} states no scope of its own and no cell '
                                f'of this table covers its row')
                        continue
                    if HEADER_TEXT.search(value) and not re.search(r'\d|INTERO', value, re.I):
                        continue
                    scope = read_scope(value)
                    if not scope.fully_read:
                        # Part of this cell is a form the reader does not know.
                        # Emitting the part it does know would be a statement
                        # narrower than the act's, answering False for what the
                        # act includes, so the cell is reported unread instead.
                        unresolved.append(
                            f'{heading} :: {comune or province or "?"} : cell not fully read; '
                            f'unaccounted source text {scope.residue[:60]!r} in {value[:90]!r}')
                        continue
                    if scope.kind == 'none':
                        unresolved.append(f'{heading} :: unread cell: {value[:100]}')
                        continue
                    statements.append(CadastralStatement(
                        zone, heading, province,
                        None if scope.kind == 'whole-province' else comune,
                        scope.kind, scope.sheets, scope.text, regime))
    finally:
        if not hasattr(document, 'page_count'):
            opened.close()
    unique, seen = [], set()
    for statement in statements:
        key = (statement.zone, statement.zone_heading, statement.province,
               statement.comune, statement.text)
        if key in seen:
            continue
        seen.add(key)
        unique.append(statement)
    return tuple(unique), tuple(dict.fromkeys(unresolved))


def act_documents(root: Path):
    """The acquired act documents, by instrument, from their acquisition records."""
    record_path = root / 'corpus/sources/areas/acts.json'
    if not record_path.exists():
        return {}
    return {r['instrument_id']: r for r in json.loads(record_path.read_text())
            if r.get('sha256') and 'error' not in r}


# --- handing the act's statement to the accepted consumer ---------------------

MEMBERSHIP_PREDICATE = ('the point or parcel lies within the geography adopted by '
                        'this act and its annexes')
INTERVAL_PREDICATE = "decision time within this version's effective interval"


def _place_label(comune, province, section, foglio):
    parts = []
    if foglio:
        parts.append(f'foglio {foglio}' + (f' sezione {section}' if section else ''))
    if comune:
        parts.append(str(comune))
    if province:
        parts.append(f'provincia {province}')
    return ', '.join(parts) or 'the stated place'


def membership_evidence(versions_, root: Path, day, *, comune=None, province=None,
                        section=None, foglio=None, particella=None, known_at=None):
    """Build the Sources and Assertions that answer A's membership predicate.

    A's predicate is about a point or a parcel, so that is the grain asked
    here: a sheet the act merely says intersects the zone does not place a
    parcel inside it and yields no assertion. Each assertion is supported by
    the exact annex row the act prints, in the act document held in the store
    under its own hash.

    The question must identify a place. An unidentified question has no
    answer to give, and answering it anyway is how a statement about one
    comune came to stand for any comune, so it is refused rather than
    answered.
    """
    from datetime import datetime, timezone
    from .evidence import Assertion, Source, Support
    if comune is None and province is None:
        raise ValueError('a membership question must name a comune or a province')
    documents = act_documents(root)
    store = store_root(root)
    known_at = known_at or datetime.now(timezone.utc)
    label = _place_label(comune, province, section, foglio)
    sources, assertions = {}, []
    for version in in_force(versions_, day):
        record = documents.get(version.instrument_id)
        if record is None or not version.statements:
            continue
        for statement in version.statements:
            if not statement.covers(comune=comune, province=province, section=section,
                                    foglio=foglio, particella=particella, grain='parcel'):
                continue
            digest = record['sha256']
            identity = f'act:{version.instrument_id}'
            if identity not in sources:
                sources[identity] = Source(
                    identity=identity,
                    path=str(blob_path(store, digest).relative_to(store)),
                    sha256=digest, role='official-record', access='public')
            assertions.append(Assertion(
                identity=f'{version.provision_version_id}|{statement.zone}|{label}',
                contract='adopted-geography',
                context=label,
                event_date=day,
                known_at=known_at,
                consumer_version=version.provision_version_id,
                predicate=MEMBERSHIP_PREDICATE,
                value=True,
                support=(Support(
                    source=identity,
                    selector=f'{statement.zone_heading} :: '
                             f'{statement.province or "-"} / {statement.comune or "-"}',
                    reading=f'the act places {label} in the {statement.zone} zone: '
                            f'{statement.text}'),)))
            break
    return tuple(sources.values()), tuple(assertions)


def evidence_for(versions_, root: Path, day, *, snapshot, comune=None, province=None,
                 section=None, foglio=None, particella=None, known_at=None):
    """An Evidence over this row's assertions, ready for the accepted consumer."""
    from .evidence import Evidence
    contracts = json.loads((root / 'regulation/stage-d/contracts.json').read_text())
    bindings = {}
    for binding in json.loads(
            (root / 'regulation/stage-d/predicate-contracts.json').read_text())['bindings']:
        bindings.setdefault(binding['predicate'], set()).update(binding.get('contracts', ()))
    bindings = {k: frozenset(v) for k, v in bindings.items()}
    sources, assertions = membership_evidence(
        versions_, root, day, comune=comune, province=province, section=section,
        foglio=foglio, particella=particella, known_at=known_at)
    return Evidence(snapshot, sources, assertions,
                    {c['id']: c for c in contracts['contracts']}, bindings,
                    store_root(root)), assertions

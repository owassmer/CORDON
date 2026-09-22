"""Demarcated-area versions and the annex statements their acts make.

An area version is an accepted Stage A row: identity, interval and legal effect
are A's and are read from A, never re-derived. This reader adds only what the act
itself prints about the extent of its zones - per zone caption, the province, the
comune and the fogli di mappa, with the act's asterisk where a sheet or parcel
lies wholly in the zone - as the construction input for the adopted geometry
(`cordon_d.area_geometry`). It answers no membership question: whether a place
lies in an adopted area is C's calculation on the supplied geometry.

The annex tables are read once, by `scripts/read_annexes.py`, and pinned under
`corpus/sources/areas/readings/`. This module interprets the pinned reading - the
zone from the caption's head word, as the act prints it, and the sheets from the
scope grammar - and never regenerates a number. A cell the grammar cannot fully
read, a table the model could not recover or a page without a complete reading
stops the reader: it is repaired, not carried.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
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
# collapsing the two loses which zone the act says it is. The zone is the word
# the act prints, upper-cased: DDS 82/2026 lists its Mola di Bari and Noci foci
# under FOCOLAI, a part distinct from its ZONA INFETTA, and no token is invented
# for it or mapped onto another zone.
ZONE_WORD = re.compile(r'\b(FOCOLAI\w*|CUSCINETTO|CONTENIMENTO|INFETT[AO])\b', re.I)
REGIME_CLAUSE = re.compile(
    r'IN\s+CUI\s+SI\s+APPLICANO[^.;]*?\b(CONTENIMENTO|ERADICAZIONE)\b', re.I)
WHOLE_PROVINCE = re.compile(r'INTERO\s+TERRITORIO\s+PROVINCIALE', re.I)


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
    wholly_contained_parcels: tuple[str, ...] = ()


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
    zone: str                     # the caption's head zone word, as the act prints it
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
    qualification: str | None = None
    note: str | None = None
    locator: str | None = None

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
    # Whether A's condition for this version tests the adopted geography. C consumes
    # only these; an A row without the predicate is never given geometry.
    consumed: bool
    annexes: tuple[Annex, ...]
    # None when the act's document is not in this store; () when its pages state no table.
    statements: tuple[CadastralStatement, ...] | None
    # Consequential statements the act prints on its annex pages outside any
    # table - a partial-parcel rule, a region named in prose - quoted, not read
    # into a zone. They are the act's words and travel with the version.
    unattached: tuple[str, ...] = ()


# The scope grammar, taken from what the acts print rather than from the ones
# I happened to open. Enumerated over the whole population: whole-territory
# statements for a comune or a province, a part-of-comune statement, sheet
# lists under an optional section, inclusive ranges written "da 15 a 32" and
# also "161 a 172", particelle narrowing a sheet, and a parenthesised
# development on a sheet. Anything else is residue, and a cell with residue is
# not read - which is how the next form the publisher uses becomes a finding
# on first contact instead of a silently truncated answer.
SCOPE_TOKENS = (
    ('skip', re.compile(r'[\s,;:.()]+')),
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
    ('annex-sheet', re.compile(r'(\d+)\s*-\s*(ALLEGATO\s+[A-Z])\s*(\*?)', re.I)),
    # A dash between two numbers is a form no held act uses for a range; it is
    # residue, so the cell is reported unread instead of read as its endpoints.
    ('unread', re.compile(r'\d+\s*\*?\s*[–—-]\s*\d+')),
    ('sheet', re.compile(r'(\d+)\s*(\*?)\s*(\((?:SVILUPPO|Sviluppo)[^)]*\))?')),
)
# Residue that cannot change what the cell means: stray single letters and
# separator punctuation left by extraction. A digit, a word, an asterisk (the
# act's own whole-containment mark) or a dash (a range no held act writes) can.
TRIVIAL_RESIDUE = re.compile(r'^[^\w*–—-]*$|^[A-Za-z]$')


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
            elif name == 'unread':
                residue.append(match.group(0))
            elif name == 'range':
                low, high = int(match.group(1)), int(match.group(2))
                if reading_parcels:
                    # A range of particelle is a form no held act uses; reading
                    # it as sheets would place sheets the act never names.
                    residue.append(match.group(0))
                elif low > high or high - low > 500:
                    residue.append(match.group(0))
                else:
                    sheets.extend(Sheet(section, str(n), False)
                                  for n in range(low, high + 1))
                    reading_parcels = False
            elif name == 'annex-sheet':
                sheets.append(Sheet(section, match.group(1), match.group(3) == '*',
                                    (), match.group(2)))
            elif name == 'sheet':
                if reading_parcels and sheets:
                    last = sheets[-1]
                    sheets[-1] = Sheet(last.section, last.number, last.wholly_contained,
                                       last.parcels + (match.group(1),), last.qualifier,
                                       last.wholly_contained_parcels
                                       + ((match.group(1),) if match.group(2) == '*' else ()))
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


# --- the pinned reading of each act's annex pages -----------------------------

def readings_root(root: Path) -> Path:
    return root / 'corpus/sources/areas/readings'


def _reading_text(value):
    return ' '.join(value['text'].split()) if value and value.get('text') is not None else None


class ReadingIncomplete(ValueError):
    """A pinned reading that does not account for its page: fix the reading, never carry it."""


def pinned_statements(root: Path, digest: str):
    """Every area statement the act's pinned annex readings make.

    `scripts/read_annexes.py` shows the model each page of the act and the native
    cells the document encodes; the model binds captions to rows and points at the
    cell that carries each value, and the script copies that cell's characters. The
    pinned file is the reading: response, configuration and the cells shown. This
    function interprets it and nothing else - the zone from the caption's head
    word, the sheets from the scope grammar - so a statement here is the act's
    printed cell, attributed, and never a regenerated number.

    Returns (statements, unattached). Every physical page of the act's own document
    must have a complete reading, and every table and row must be read; anything
    else raises `ReadingIncomplete`, because a partial reading silently becomes a
    wrong geometry. A document not in this store raises FileNotFoundError.
    """
    document = blob_path(store_root(root), digest)
    if not document.exists():
        raise FileNotFoundError(f'act document {digest} is not in this store')
    import pymupdf
    with pymupdf.open(document) as opened:
        pages = opened.page_count
    statements, problems, unattached = [], [], []
    for number in range(1, pages + 1):
        path = readings_root(root) / digest / f'p{number}.json'
        if not path.exists():
            problems.append(f'p{number}: no reading')
            continue
        pinned = json.loads(path.read_text())
        if pinned.get('act_sha256') != digest or pinned.get('page') != number:
            raise ValueError('Area reading belongs to another document or physical page')
        resolved, reading = pinned.get('resolved'), pinned.get('reading') or {}
        # A response cut off at a token limit is not a page read.
        if not resolved or pinned.get('stop_reason') not in ('end_turn', 'tool_use'):
            problems.append(f'p{number}: reading stopped with {pinned.get("stop_reason")!r}')
            continue
        problems.extend(f'p{number}: {problem}' for problem in pinned.get('resolution_problems', ()))
        problems.extend(f'p{number}: native table {region["native_table"]} not recovered'
                        for region in reading.get('native_tables_accounted', ())
                        if region['disposition'] == 'not_recovered')
        problems.extend(f'p{number}: uncertain: {item}' for item in reading.get('uncertain', ()))
        unattached.extend(f'p{number}: {item}' for item in reading.get('unattached', ()))
        for table in resolved['tables']:
            heading = ' '.join(table['caption_verbatim'].split())
            zone, _, regime = _zone_from(heading)
            if zone is None:
                problems.append(f'p{number}: table {table["index"]} caption names no zone: {heading[:90]}')
                continue
            for row_number, row in enumerate(table['rows'], 1):
                province, comune, value = (_reading_text(row.get('provincia')),
                                           _reading_text(row.get('comune')), _reading_text(row.get('scope')))
                if not value and comune and WHOLE_PROVINCE.search(comune):
                    value, comune = comune, None      # a province-wide statement printed across the comune column
                if not value:
                    if comune or province:
                        problems.append(f'{heading} :: {comune or province} states no scope of its own')
                    continue
                scope = read_scope(value)
                if not scope.fully_read or scope.kind == 'none':
                    problems.append(f'{heading} :: {comune or province or "?"} : cell not read: {value[:90]!r}')
                    continue
                statements.append(CadastralStatement(
                    zone, heading, province, None if scope.kind == 'whole-province' else comune,
                    scope.kind, scope.sheets, scope.text, regime,
                    '; '.join(dict.fromkeys(filter(None, (
                        *table.get('column_headings_verbatim', ()),
                        table.get('qualification_verbatim'))))) or None, row.get('note'),
                    f'p{number} table {table["index"]} row {row_number}'))
    if problems:
        raise ReadingIncomplete(f'{digest}: ' + '; '.join(dict.fromkeys(problems)))
    return tuple(statements), tuple(dict.fromkeys(unattached))


# --- binding A's accepted area versions to what their acts state ---------------

AREA_ROW = re.compile(r'area-state-transition|area-update|area-act-before-gis')
MEMBERSHIP = 'the point or parcel lies within the geography adopted by this act and its annexes'


def _predicates(ast):
    if isinstance(ast, dict):
        if 'predicate' in ast:
            yield ast['predicate']
        for value in ast.values():
            yield from _predicates(value)
    elif isinstance(ast, list):
        for item in ast:
            yield from _predicates(item)


def _date(value):
    return date.fromisoformat(value) if value else None


def _act_text(root: Path, source_path: str) -> str:
    """The act's text layer, for its own annex list and adoption words only."""
    path = root / source_path
    if path.suffix.lower() == '.pdf':
        import pymupdf
        with pymupdf.open(path) as document:
            return '\n'.join(page.get_text() for page in document)
    return path.read_text(errors='replace')


def versions(root: Path):
    """Every accepted Stage A area version, with the area statements its act makes.

    Identity, interval, subspecies and act-level state are A's; only the per-zone
    cadastral statements and the annex list are read from the act's own document,
    so a successor's annex is never borrowed for a version.
    """
    documents = act_documents(root)
    rows = json.loads((root / 'regulation/jurisdiction/canonical/authoring.json').read_text())
    if not isinstance(rows, list):
        rows = list(rows.values())[0]
    out = []
    for row in sorted((r for r in rows if AREA_ROW.search(r['provision_version_id'])),
                      key=lambda r: (r['effective_from'], r['provision_version_id'])):
        source_path = row.get('source_paths') or ''
        record = documents.get(row['instrument_id'])
        statements, unattached, found = None, (), ()
        if record:
            found = annexes(_act_text(root, source_path))
            try:
                statements, unattached = pinned_statements(root, record['sha256'])
            except FileNotFoundError:
                statements = None
        out.append(AreaVersion(
            provision_version_id=row['provision_version_id'],
            instrument_id=row['instrument_id'],
            effective_from=_date(row['effective_from']),
            effective_to_exclusive=_date(row.get('effective_to_exclusive')),
            temporal_status=row.get('temporal_status', ''),
            state=(row.get('true_effect') or '').strip(),
            source_path=source_path,
            consumed=MEMBERSHIP in set(_predicates(row.get('condition_ast'))),
            annexes=found,
            statements=statements,
            unattached=tuple(unattached),
        ))
    return tuple(out)


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
    regime_match = REGIME_CLAUSE.search(text)
    regime = regime_match.group(1).upper() if regime_match else None
    return match.group(1).upper(), match.group(0), regime


def act_documents(root: Path):
    """The acquired act documents, by instrument, from their acquisition records."""
    record_path = root / 'corpus/sources/areas/acts.json'
    if not record_path.exists():
        return {}
    return {r['instrument_id']: r for r in json.loads(record_path.read_text())
            if r.get('sha256') and 'error' not in r}

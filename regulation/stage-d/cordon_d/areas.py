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

The annex tables are read once, by `scripts/read_annexes.py`, and pinned under
`corpus/sources/areas/readings/`: for each page the model binds every caption to
the rows it governs and points at the native cell that carries each value, and
the script copies that cell's characters. This module interprets the pinned
reading - the zone from the caption's head word, the sheets from the scope
grammar - and never regenerates a number. A cell the grammar cannot fully read,
a table the model could not recover and a page not yet read are carried as
unresolved with their literal text; nothing is guessed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
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
WHOLE_PROVINCE = re.compile(r'INTERO\s+TERRITORIO\s+PROVINCIALE', re.I)


# The causes an absence may name, in DESIGN_PRINCIPLES' own terms. They are
# written out because they have different remedies - another source, a better
# reading, an attachment, an owner's ruling - and become interchangeable the
# moment they are allowed to share the one word "nothing".
SOURCE_STATES_NONE = 'the source does not state the fact'
MATERIAL_NOT_HELD = 'the material is not held'
READING_DID_NOT_RECOVER = 'our reading did not recover it'
RECOVERED_NOT_ATTACHED = 'it was recovered and could not be attached'
RECOVERED_UNADJUDICATED = 'it was recovered and remains unadjudicated'

# An act adopts an annex when it names one as an integral part of itself. The
# acts write that both ways round - "Allegato 1 ... parte integrante" and
# "Rappresentare i limiti ... con l'Allegato 1 ... che ne formano parte
# integrante" - and in the plural, so the test is the two words in one clause
# and not a phrasing. What the annex carries is answered by reading it, not by
# the sentence that introduces it.
ADOPTS_ANNEX = re.compile(
    r'allegat\w*[^.;•]{0,200}?integrant\w*|integrant\w*[^.;•]{0,200}?allegat\w*', re.I)


def adopts_an_annex(text) -> bool:
    """Whether the act's own words adopt an annex as part of the act."""
    return bool(ADOPTS_ANNEX.search(' '.join((text or '').split())))


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
    qualification: str | None = None
    note: str | None = None
    locator: str | None = None

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

        Inside a comune-scoped row the province column is the act's label on
        a place the comune already identifies, and the acts print it both ways
        - "BARI" and "BA", "BAT" and "BT" - for one province. So the province
        the question names never decides a comune-scoped statement: treating
        the two spellings as a contradiction dropped the row and reported the
        act as silent. The act's own province travels with every assertion in
        its support selector, where a caller can see it. A whole-province
        statement is about the province and nothing else, so there the
        question must name it, as the act prints it.
        """
        if grain not in ('sheet', 'parcel'):
            raise ValueError("grain must be 'sheet' or 'parcel'")
        if self.scope == 'whole-province':
            if province is None:
                return None
            return True if (self.province or '').upper() == province.upper() else None
        # Below here the statement is about one comune, so the question must
        # name one.
        if comune is None:
            return None
        if (self.comune or '').upper() != comune.upper():
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
            if sheet.qualifier:
                # The question has not identified the named sheet development.
                # Its number alone must not borrow that development's extent.
                return None
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
                if str(particella) not in sheet.parcels:
                    return False
                return True if str(particella) in sheet.wholly_contained_parcels else None
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
    # What the act states about its own geography - a fact about the source,
    # never a record of how far this reader got.
    geography_form: str           # annexed | stated-rule | adopts-none | body-not-held
    annexes: tuple[Annex, ...]
    statements: tuple[CadastralStatement, ...]
    unresolved: tuple[str, ...]   # literal lines and tables the reader would not guess at
    # Consequential statements the act prints on its annex pages outside any
    # table - a partial-parcel rule, a region named in prose - quoted, not read
    # into a zone. They are the act's words and travel with the version.
    unattached: tuple[str, ...] = ()
    # Why this version supplies less than its act states, each entry naming its
    # own cause. A reading's silence is not the source's, and the causes below
    # have different remedies: a better reading, another source, an attachment,
    # an owner's ruling. Recording them interchangeably - or as a property of
    # the act - is what let two acts answer nothing and say nothing.
    absence: tuple[str, ...] = ()

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
    ('unread', re.compile(r'\d+\s*[–—-]\s*\d+')),
    ('sheet', re.compile(r'(\d+)\s*(\*?)\s*(\((?:SVILUPPO|Sviluppo)[^)]*\))?')),
)
# Residue that cannot change what the cell means: stray single letters and
# punctuation left by extraction. Anything with a digit or a word in it can.
TRIVIAL_RESIDUE = re.compile(r'^[\W_]*$|^[A-Za-z]$')


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


def pinned_statements(root: Path, digest: str):
    """Every area statement the act's pinned annex readings make, and what was not read.

    `scripts/read_annexes.py` shows the model each candidate page of the act and
    the native cells the document encodes; the model binds captions to rows and
    points at the cell that carries each value, and the script copies that cell's
    characters. The pinned file is the reading: response, configuration and the
    cells shown. This function interprets it and nothing else — the zone from the
    caption's head word, the sheets from the scope grammar — so a statement here
    is the act's printed cell, attributed, and never a regenerated number.

    Returns (statements, unresolved, unattached, pages_unread). A candidate page
    with no pinned reading is unread and says so; a table the model could not
    recover, a row with no scope, a cell the grammar cannot fully read, and every
    item the model flagged uncertain are unresolved with their literal text.
    """
    inventory_path = readings_root(root) / 'INVENTORY.json'
    if not inventory_path.exists():
        return (), (READING_DID_NOT_RECOVER + ': document page inventory is missing',), (), ()
    candidates = [p for p in json.loads(inventory_path.read_text())
                  if p.get('act_sha256') == digest and p.get('page')]
    statements, unresolved, unattached, unread = [], [], [], []
    if not candidates:
        unresolved.append(READING_DID_NOT_RECOVER + ': document has no page inventory')
    counts = {p.get('pages_in_document') for p in candidates}
    if candidates and (len(counts) != 1 or None in counts or
                       sorted(p['page'] for p in candidates) != list(range(1, next(iter(counts)) + 1))):
        unresolved.append(READING_DID_NOT_RECOVER + ': document page inventory is incomplete')
    for page in sorted(candidates, key=lambda p: p['page']):
        path = readings_root(root) / digest / f'p{page["page"]}.json'
        if not path.exists():
            unread.append(page['page'])
            continue
        pinned = json.loads(path.read_text())
        if pinned.get('act_sha256') != digest or pinned.get('page') != page['page']:
            raise ValueError('Area reading belongs to another document or physical page')
        resolved, reading = pinned.get('resolved'), pinned.get('reading') or {}
        if not resolved:
            unread.append(page['page'])
            continue
        # A response cut off at a token limit is a reading limit, not a page
        # read; the pinned reading keeps the one field of the model envelope
        # that says so.
        if pinned.get('stop_reason') not in ('end_turn', 'tool_use'):
            unread.append(page['page'])
            unresolved.append(f'p{page["page"]}: the model response stopped with '
                              f'{pinned.get("stop_reason")!r}, not a complete reading')
            continue
        for problem in pinned.get('resolution_problems', ()):
            unresolved.append(f'p{page["page"]}: {problem}')
        for region in reading.get('native_tables_accounted', ()):
            if region['disposition'] == 'not_recovered':
                unresolved.append(f'p{page["page"]}: native table {region["native_table"]} not recovered: '
                                  f'{region.get("cause") or "no cause given"}')
        for item in reading.get('uncertain', ()):
            unresolved.append(f'p{page["page"]}: uncertain: {item}')
        unattached.extend(f'p{page["page"]}: {item}' for item in reading.get('unattached', ()))
        for table in resolved['tables']:
            heading = ' '.join(table['caption_verbatim'].split())
            zone, _, regime = _zone_from(heading)
            if zone is None:
                unresolved.append(f'p{page["page"]}: table {table["index"]} caption names no zone: {heading[:90]}')
                continue
            for row_number, row in enumerate(table['rows'], 1):
                province, comune, value = (_reading_text(row.get('provincia')),
                                           _reading_text(row.get('comune')), _reading_text(row.get('scope')))
                if not value and comune and WHOLE_PROVINCE.search(comune):
                    value, comune = comune, None      # a province-wide statement printed across the comune column
                if not value:
                    if comune or province:
                        unresolved.append(f'{heading} :: {comune or province} states no scope of its own')
                    continue
                scope = read_scope(value)
                if not scope.fully_read:
                    unresolved.append(f'{heading} :: {comune or province or "?"} : cell not fully read; '
                                      f'unaccounted source text {scope.residue[:60]!r} in {value[:90]!r}')
                    continue
                if scope.kind == 'none':
                    unresolved.append(f'{heading} :: unread cell: {value[:100]}')
                    continue
                statements.append(CadastralStatement(
                    zone, heading, province, None if scope.kind == 'whole-province' else comune,
                    scope.kind, scope.sheets, scope.text, regime,
                    '; '.join(dict.fromkeys(filter(None, (
                        *table.get('column_headings_verbatim', ()),
                        table.get('qualification_verbatim'))))) or None, row.get('note'),
                    f'p{page["page"]} table {table["index"]} row {row_number}'))
    return (tuple(statements), tuple(dict.fromkeys(unresolved)), tuple(dict.fromkeys(unattached)), tuple(unread))


# --- binding A's accepted area versions to what their acts state ---------------

AREA_ROW = re.compile(r'area-state-transition|area-update|area-act-before-gis')


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
    """Every accepted Stage A area version, with the area statement its act makes.

    Identity, interval, subspecies and act-level state are A's; only the per-zone
    cadastral statement and the annex list are read from the act. A version whose
    own body is not held states that and reads nothing, so a successor's annex is
    never borrowed for it.
    """
    documents = act_documents(root)
    rows = json.loads((root / 'regulation/jurisdiction/canonical/authoring.json').read_text())
    if not isinstance(rows, list):
        rows = list(rows.values())[0]
    out = []
    for row in sorted((r for r in rows if AREA_ROW.search(r['provision_version_id'])),
                      key=lambda r: (r['effective_from'], r['provision_version_id'])):
        identity = row['provision_version_id']
        source_path = row.get('source_paths') or ''
        absence = ()
        unattached = ()
        if 'unresolved' in identity:
            form, statements, unread, found = 'body-not-held', (), (), ()
            absence = (MATERIAL_NOT_HELD + ': the act\'s own body is not held. Its A row '
                       'is written from a successor\'s recital, so no area statement is '
                       'read for this interval and no successor\'s annex stands in for it.',)
        elif 'area-act-before-gis' in identity:
            form, statements, unread, found = 'adopts-none', (), (), ()
            absence = (SOURCE_STATES_NONE + ': this act states the order in which an area '
                       'is created and its cartography transmitted; it adopts no geography '
                       'of its own.',)
        else:
            text = _act_text(root, source_path)
            found = annexes(text)
            record = documents.get(row['instrument_id'])
            statements, unread, unattached, pages_unread = (), (), (), ()
            if record:
                statements, unread, unattached, pages_unread = pinned_statements(root, record['sha256'])
            if pages_unread:
                unread = tuple(unread) + (READING_DID_NOT_RECOVER + ': candidate pages not read: '
                                          + ', '.join(str(p) for p in pages_unread),)
            # What the act states about its own geography. An annex table read
            # from the document settles it; where none was read, the act's own
            # words do. A missing hash list settles nothing - the 2021 and 2022
            # acts adopt annexes and print no list.
            form = 'annexed' if (statements or adopts_an_annex(text) or found) \
                else 'stated-rule'
            if not statements and form == 'annexed' and (pages_unread or unread or not record):
                absence = (READING_DID_NOT_RECOVER + ': this act adopts an annexed '
                           'geography and its pages have not all been read'
                           + (': ' + ', '.join(str(p) for p in pages_unread) if pages_unread
                              else '; ' + '; '.join(unread) if unread
                              else '; its document is not held') + '.',)
            elif not statements and form == 'annexed':
                # The act states its geography - as a map annex, with the sheets
                # drawn on the map face - and no cadastral table is printed. A map
                # read as an image and not recovered into zones is this reading's
                # limit, not the source's silence; the remedy is registering the map.
                absence = (READING_DID_NOT_RECOVER + ': this act adopts its geography as '
                           'map annexes; all its pages were read and no cadastral table is '
                           'printed. The zones the maps depict are recoverable only by '
                           'registering the maps, which is the adopted-map correspondence '
                           'this row still owes.',)
            elif not statements:
                absence = (RECOVERED_NOT_ATTACHED + ': this act states its geography as a '
                           'rule in its dispositivo rather than annexing it. The rule\'s '
                           'radii are B\'s and the origin it names is a located positive, '
                           'which the monitoring row owns; neither is supplied here, so '
                           'no place is placed in a zone for this interval.',)
        out.append(AreaVersion(
            absence=absence,
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
            unattached=tuple(unattached),
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
        zones_given, zones_reached = set(), set()
        for statement in version.statements:
            verdict = statement.covers(comune=comune, province=province, section=section,
                                       foglio=foglio, particella=particella, grain=grain)
            if verdict and statement.zone not in zones_given:
                zones_given.add(statement.zone)
                answers.append({'version': version.provision_version_id, 'zone': statement.zone,
                                'regime': statement.regime,
                                'basis': 'act cadastral statement', 'statement': statement})
            elif verdict is None and statement.zone not in zones_given | zones_reached:
                # The act reaches the place and stops short of deciding it at
                # the grain asked: an unstarred sheet the zone cuts through, or
                # a part of the comune whose extent the table does not state.
                # That is a different answer from an act that never mentions
                # the place - here the adopted map decides, there nothing does -
                # and the two were reaching the operator as one sentence.
                reached = statement.scope == 'part-comune-extent-unstated' and comune is not None \
                    and (statement.comune or '').upper() == comune.upper()
                if not reached and grain == 'parcel' and foglio is not None:
                    reached = statement.covers(comune=comune, province=province, section=section,
                                               foglio=foglio, grain='sheet') is True
                if reached:
                    zones_reached.add(statement.zone)
                    answers.append({'version': version.provision_version_id, 'zone': None,
                                    'reached_zone': statement.zone, 'regime': statement.regime,
                                    'basis': (f'the act reaches this place in its {statement.zone} zone '
                                              'and does not state which part of it lies inside; the '
                                              'adopted map decides the parcel'),
                                    'statement': statement})
        # Every version in force accounts for itself. A version that supplies
        # nothing and says nothing is indistinguishable from a version that is
        # not in force, and the operator reads both as no duty.
        for cause in version.absence:
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': cause})
        if version.unresolved:
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': READING_DID_NOT_RECOVER
                                     + ': part of this act\'s annex was not read',
                            'unresolved': len(version.unresolved)})
        if not zones_given and not zones_reached and not version.absence and not version.unresolved:
            answers.append({'version': version.provision_version_id, 'zone': None,
                            'basis': 'no cadastral statement establishes membership for this place'})
    return tuple(answers)


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


def act_documents(root: Path):
    """The acquired act documents, by instrument, from their acquisition records."""
    record_path = root / 'corpus/sources/areas/acts.json'
    if not record_path.exists():
        return {}
    return {r['instrument_id']: r for r in json.loads(record_path.read_text())
            if r.get('sha256') and 'error' not in r}


def published_geography(root: Path, *, known_through: datetime):
    """Native publisher occurrences retained for adopted-map correspondence.

    A candidate's filing under an act does not assign its polygons to that act.
    Return capture context with every occurrence; no metric or legal qualification
    follows from a feature label or acquisition date.
    """
    from .releases import arcgis_occurrences
    from .store import file_digest
    if known_through.tzinfo is None or known_through.utcoffset() is None:
        raise ValueError('Geography consumption needs a timezone-aware knowledge cutoff')
    records = json.loads((root / 'corpus/sources/areas/acts.json').read_text())
    seen = set()
    for record in records:
        for capture in record.get('publisher_geometry_candidates', []):
            at = datetime.fromisoformat(capture['captured_at'])
            if at.tzinfo is None:
                raise ValueError('Geography capture has no timezone')
            key = capture['url'], capture['sha256'], capture['captured_at']
            if at > known_through or key in seen:
                continue
            seen.add(key)
            path = blob_path(store_root(root), capture['sha256'])
            if file_digest(path) != capture['sha256']:
                raise ValueError('Publisher geometry source bytes changed')
            if capture['format'] != 'arcgis':
                raise ValueError('Publisher geometry capture needs its native format reader')
            for occurrence in arcgis_occurrences(path, oid_field=capture['oid_field']):
                yield capture, occurrence


# --- handing the act's statement to the accepted consumer ---------------------

MEMBERSHIP_PREDICATE = ('the point or parcel lies within the geography adopted by '
                        'this act and its annexes')
INTERVAL_PREDICATE = "decision time within this version's effective interval"


def _place_label(comune, province, section, foglio, particella=None):
    parts = []
    if foglio:
        parts.append(f'foglio {foglio}' + (f' sezione {section}' if section else ''))
    if particella:
        parts.append(f'particella {particella}')
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
    label = _place_label(comune, province, section, foglio, particella)
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
                identity=f'{version.provision_version_id}|{statement.zone}|{label}|{statement.locator}',
                contract='adopted-geography',
                context=label,
                event_date=day,
                known_at=known_at,
                consumer_version=version.provision_version_id,
                predicate=MEMBERSHIP_PREDICATE,
                value=True,
                support=(Support(
                    source=identity,
                    selector=f'{statement.locator or ""} {statement.zone_heading} :: '
                             f'{statement.province or "-"} / {statement.comune or "-"}',
                    reading=f'the act places {label} in the {statement.zone} zone: '
                            f'{statement.text}'
                            + (f'; {statement.qualification}' if statement.qualification else '')
                            + (f'; {statement.note}' if statement.note else '')),)))
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

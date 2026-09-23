"""Literal report readings and local projections. This module never calls a model."""
from dataclasses import dataclass, replace
from collections import Counter
from datetime import date, datetime
import json
import re
from pathlib import Path
from hashlib import sha256

from .store import blob_path

READER_IMPLEMENTATION = sha256(Path(__file__).read_bytes()).digest()

ROLES = frozenset({'identifier', 'publisher_id', 'laboratory_id', 'pool_id', 'extract_id',
                   'sampling_date', 'test_date', 'host', 'municipality',
                   'latitude', 'longitude', 'result', 'other'})
CAUSES = frozenset({'unreadable', 'not_recovered', 'unattached', 'not_stated'})
COMPONENT_ROLES = frozenset({'host', 'identifier', 'municipality', 'latitude', 'longitude'})
RESULTS = {'positivo': 'positive', 'negativo': 'negative', 'rilevato': 'detected',
           'non rilevato': 'not-detected', 'non determinabile': 'undetermined',
           'rilevata': 'detected', 'non rilevata': 'not-detected',
           'dubbio': 'doubtful', 'presente': 'detected', 'assente': 'not-detected'}


def classify(text):
    return RESULTS.get(' '.join(text.casefold().split()), 'unclassified') if text else 'unread'


def _leading_mark(text):
    """The printed marker a note begins with ('*', '**', 'a'), or None."""
    match = re.match(r'\s*(\*+|[a-z])(?=\s|[A-Z(])', text or '')
    return match[1] if match else None


def resolve_marks(result, scoped):
    """A trailing printed mark on a result literal classifies only through the note it points at.

    The source reader may already have separated `result_value` from an annotation; this
    handles the cell it returned whole. A mark is separated only where a result
    qualification recovered from the same document, scoped to this row, begins with that
    mark; the base is then classified and the note travels with the row as it already does.
    A mark with no recovered note leaves the result unclassified and names that cause. The
    complete literal survives either way.
    """
    if result.kind != 'unclassified' or not result.text:
        return result
    marks = {mark for fact in scoped if fact.get('role') == 'result_qualification'
             for mark in [_leading_mark(fact.get('text'))] if mark}
    base, used = result.text.strip().casefold(), []
    while True:
        mark = next((m for m in sorted(marks, key=len, reverse=True)
                     if base.endswith(m) and len(base) > len(m)), None)
        if mark is None:
            break
        base, used = base[:-len(mark)].rstrip(), used + [mark]
    if used and classify(base) != 'unclassified':
        return replace(result, kind=classify(base))
    text = result.text.strip().casefold()
    for n in (1, 2, 3):
        if n >= len(text):
            break
        mark, unmarked = text[-n:], text[:-n]
        if re.fullmatch(r'(\*+|[a-z]|\*+[a-z]|[a-z]\*+)', mark) and classify(unmarked.strip()) != 'unclassified':
            return replace(result, cause='printed mark; note not recovered by the reading')
    return result


def link_section_marks(facts):
    """Resolve unique printed § anchors on one page, retaining the derivation."""
    notes = {}
    for fact in facts:
        marker = re.match(r'^(§+)\s*[^§\s]', fact['text'].strip())
        if marker:
            notes.setdefault((fact['page'], marker[1]), []).append(fact)
    for field in facts:
        section = field.get('section')
        if not section or not (marker := re.search(r'(§+)$', section)):
            continue
        page = int(section.split('/', 1)[0][1:])
        candidates = notes.get((page, marker[1]), [])
        if len({' '.join(f['text'].split()) for f in candidates}) != 1:
            continue  # Reused marks require source-position evidence we do not have.
        scope = 'section:' + section
        for note in candidates:
            if scope not in note['applies_to']:
                note['applies_to'].append(scope)
                note.setdefault('scope_derivations', []).append({
                    'scope': scope, 'rule': 'unique printed section mark on the same page',
                    'marker': marker[1]})


@dataclass(frozen=True)
class LiteralDate:
    text: str | None
    value: date | None
    cause: str | None
    year_support: tuple[str, ...] = ()
    date_range: tuple[date, date] | None = None
    listed_dates: tuple[date, ...] = ()

    def permits(self, value):
        if self.date_range is not None:
            return self.date_range[0] <= value <= self.date_range[1]
        return value == self.value or value in self.listed_dates


def literal_date(text, cause=None, *, year_context=()):
    if text is None:
        return LiteralDate(None, None, cause or 'not_recovered')
    stated_absence = {'non disponibile': 'source_states_unavailable',
                      'non applicabile': 'source_states_not_applicable'}
    if absence := stated_absence.get(' '.join(text.casefold().split())):
        return LiteralDate(text, None, absence)
    formats = ((r'\d{1,2}/\d{1,2}/\d{4}', '%d/%m/%Y'),
               (r'\d{1,2}-\d{1,2}-\d{4}', '%d-%m-%Y'),
               (r'\d{1,2}\.\d{1,2}\.\d{4}', '%d.%m.%Y'),
               (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'))
    for shape, pattern in formats:
        if re.fullmatch(shape, text.strip()):
            try:
                return LiteralDate(text, datetime.strptime(text.strip(), pattern).date(), None)
            except ValueError:
                return LiteralDate(text, None, 'invalid_calendar_date')
    short = re.fullmatch(r'(\d{1,2})([/.-])(\d{1,2})\2(\d{2})', text.strip())
    if short:
        # Resolve only against a full year actually stated in this row's source
        # context. No current-year assumption or platform %y century cutoff.
        candidates = {year for year, _ in year_context if year % 100 == int(short[4])}
        if len(candidates) != 1:
            return LiteralDate(text, None, 'year_not_established_by_source_context')
        year = next(iter(candidates))
        support = tuple(dict.fromkeys(locator for value, locator in year_context if value == year))
        try:
            return LiteralDate(text, date(year, int(short[3]), int(short[1])), None, support)
        except ValueError:
            return LiteralDate(text, None, 'invalid_calendar_date', support)
    months = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
              'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre')
    named = re.fullmatch(r'(\d{1,2}(?:\s*[-–]\s*\d{1,2}|(?:\s+e\s+\d{1,2})+)?)'
                         r'\s+(' + '|'.join(months) + r')(?:\s+(\d{4}))?',
                         text.strip().casefold())
    if named:
        support = ()
        if named[3]:
            year = int(named[3])
        else:
            candidates = {year for year, _ in year_context}
            if len(candidates) != 1:
                return LiteralDate(text, None, 'year_not_established_by_source_context')
            year = next(iter(candidates))
            support = tuple(dict.fromkeys(locator for value, locator in year_context if value == year))
        try:
            days = tuple(date(year, months.index(named[2]) + 1, int(day))
                         for day in re.findall(r'\d+', named[1]))
        except ValueError:
            return LiteralDate(text, None, 'invalid_calendar_date', support)
        if re.search(r'[-–]', named[1]):
            if days[0] > days[1]:
                return LiteralDate(text, None, 'invalid_date_range', support)
            return LiteralDate(text, None, None, support, date_range=days)
        if len(days) > 1:
            return LiteralDate(text, None, None, support, listed_dates=days)
        return LiteralDate(text, days[0], None, support)
    return LiteralDate(text, None, 'unparsed_date_literal')



@dataclass(frozen=True)
class Result:
    locator: str
    column: tuple[str, ...]
    assay: str | None
    analyte: str | None
    text: str | None
    kind: str
    cause: str | None
    support: tuple[dict, ...]
    assay_cause: str | None = None


@dataclass(frozen=True)
class Row:
    locator: str
    page: int
    reference: str | None
    laboratory_reference: str | None
    sampling_dates: tuple[LiteralDate, ...]
    cells: tuple[dict, ...]
    results: tuple[Result, ...]
    facts: tuple[dict, ...]
    projection: dict | None = None

    @property
    def candidate_reference(self):
        values = list(self.identifiers)
        return values[0] if len(values) == 1 else None

    @property
    def identifiers(self):
        values = [c.get('identifier', c['text']) for c in self.cells
                  if c['role'] in {'identifier', 'publisher_id', 'laboratory_id'}
                  and c['text'] is not None]
        return tuple(dict.fromkeys(values))

    @property
    def sampling_date(self):
        values = {d.value for d in self.sampling_dates if d.value is not None}
        if len(values) != 1:
            return None
        value = next(iter(values))
        # A range/list constrains a separately stated day; it never supplies one.
        return value if all(d.permits(value) for d in self.sampling_dates) else None

    @property
    def date_cause(self):
        if not self.sampling_dates:
            return 'no sampling date attached to this row'
        if self.sampling_date is not None:
            return None
        causes = {value.cause for value in self.sampling_dates if value.cause}
        exact = {d.value for d in self.sampling_dates if d.value is not None}
        if len(exact) > 1 or any(not d.permits(value) for value in exact
                                for d in self.sampling_dates if not d.cause):
            causes.add('conflicting sampling-date values')
        if not causes:
            causes.add('sampling-date range or list does not establish an exact day')
        return '; '.join(sorted(causes))


@dataclass(frozen=True)
class Report:
    sha256: str
    extraction_version: str
    pages: int
    rows: tuple[Row, ...]
    facts: tuple[dict, ...]
    issues: tuple[dict, ...]
    complete_pages: frozenset[int]
    relations: dict | None = None
    assembly_complete: bool | None = None


@dataclass(frozen=True)
class UnreadReport:
    sha256: str
    cause: str


def _scope_support(statement, page_count):
    if not isinstance(statement, dict) or not isinstance(statement.get('text'), str):
        raise ValueError('Source statement requires literal text')
    if type(statement.get('page')) is not int or not 1 <= statement['page'] <= page_count:
        raise ValueError('Source statement requires a physical page')
    if not statement.get('locator'):
        raise ValueError('Source statement requires its page locator')


def cell_components(block, native):
    """Bind literal component facts to one physical cell, never to a nearby value."""
    anchors, contextual = {}, {'report', 'unattached'}
    contextual.update(f['id'] for f in block['facts'] if 'id' in f)
    contextual.update('section:' + f['section'] for f in block['facts'] if f.get('section'))
    for table in block['tables']:
        contextual.add(table['id'])
        for raw in table['rows']:
            row = f"{table['id']}/{raw['id']}"
            contextual.update({row, f"p{table['page']}/{row}"})
            for index, (column, cell) in enumerate(zip(table['columns'], raw['cells']), 1):
                contextual.add(f"{table['id']}/c{index}")
                short = f'{row}/c{index}'
                locator = f"p{table['page']}/{short}"
                selectors = {short, locator}
                if cell.get('native_cell'):
                    selectors.add('native:' + cell['native_cell'])
                for selector in selectors:
                    anchors.setdefault(selector, []).append((locator, table['page'], column, cell))

    def span(text, value):
        if not isinstance(value, str) or not value.strip() or not isinstance(text, str):
            raise ValueError('Cell component requires nonempty literal source text and value')
        start = text.find(value)
        if start < 0 or text.find(value, start + 1) >= 0:
            raise ValueError('Cell component requires a unique literal source span')
        return start, start + len(value)

    components = {}
    for fact in block['facts']:
        if fact['role'] not in COMPONENT_ROLES:
            continue
        selectors = fact['applies_to']
        if all(selector in contextual for selector in selectors):
            continue  # Existing broadly scoped facts remain context, not row fields.
        if len(selectors) != 1 or len(anchors.get(selectors[0], ())) != 1:
            raise ValueError('Cell component must select one unique physical cell')
        locator, page, column, cell = anchors[selectors[0]][0]
        if column['role'] == fact['role']:
            continue  # A fact about an already typed field adds no second field.
        if column['role'] != 'other' or fact['page'] != page:
            raise ValueError('Cell component requires an untyped cell on its cited page')
        text = native[cell['native_cell']]['text'] if 'native_cell' in cell else cell.get('text')
        clause = span(text, fact['text'])
        value = span(fact['text'], fact.get('value'))
        bounds = (clause[0] + value[0], clause[0] + value[1])
        previous = components.setdefault(locator, [])
        if any(max(bounds[0], item['span'][0]) < min(bounds[1], item['span'][1]) for item in previous):
            raise ValueError('Cell component spans overlap; their distinct meanings are unresolved')
        previous.append({'fact': fact, 'span': bounds})
    return components


def validate_block(block, *, targets, page_count, native_cells, native_regions=(), supplied_pages=None):
    """Structural validation only; source fidelity needs independent source inspection."""
    if set(block) != {'pages', 'tables', 'facts', 'issues', 'context_pages'}:
        raise ValueError('Unexpected or missing block fields')
    pages = [p['page'] for p in block['pages']]
    if len(pages) != len(set(pages)) or set(pages) != set(targets):
        raise ValueError('Every target page requires exactly one disposition')
    if any(p.get('disposition') not in {'read', 'unreadable', 'partly_read'} for p in block['pages']):
        raise ValueError('Invalid page disposition')
    if any(type(p) is not int or not 1 <= p <= page_count for p in block['context_pages']):
        raise ValueError('Invalid context page')
    supplied_pages = set(targets if supplied_pages is None else supplied_pages)
    def support(statement):
        _scope_support(statement, page_count)
        if statement['page'] not in supplied_pages:
            raise ValueError('Source support cites a page not supplied to this reading')
    table_ids = set()
    region_ids = {r['id']: r for r in native_regions if r['page'] in targets}
    dispositions = [r for page in block['pages'] for r in page.get('regions', [])]
    supplied = [r for r in dispositions if r.get('native_table') in region_ids]
    if region_ids and ({r.get('native_table') for r in supplied} != set(region_ids)
                       or len(supplied) != len(region_ids)):
        raise ValueError('Every detected native table needs one disposition')
    for page in block['pages']:
        for region in page.get('regions', []):
            if region.get('disposition') not in {'represented', 'not_sample_table', 'not_recovered'}:
                raise ValueError('Invalid native-table disposition')
            if region['disposition'] == 'not_recovered' and page['disposition'] == 'read':
                raise ValueError('An unrecovered region prevents complete page reading')
            if region.get('native_table') in region_ids and region_ids[region['native_table']]['page'] != page['page']:
                raise ValueError('Native-table disposition belongs to another page')
    for table in block['tables']:
        if table['page'] not in targets or table['id'] in table_ids:
            raise ValueError('Invalid table page or repeated table ID')
        table_ids.add(table['id'])
        columns = table['columns']
        if not columns:
            raise ValueError('A table requires columns')
        for column in columns:
            if column['role'] not in ROLES or not isinstance(column['heading'], list):
                raise ValueError('Invalid column role or heading path')
            for statement in column.get('support', []):
                support(statement)
            authority = column.get('identifier_authority')
            authority_support = column.get('authority_support', [])
            if authority not in {None, 'publisher', 'laboratory'}:
                raise ValueError('Invalid identifier authority')
            for statement in authority_support:
                support(statement)
            if authority is not None and not authority_support:
                raise ValueError('Identifier authority requires source support')
            if column['role'] == 'publisher_id' and authority not in {None, 'publisher'}:
                raise ValueError('Publisher identifier conflicts with its authority')
            if column['role'] == 'laboratory_id' and authority not in {None, 'laboratory'}:
                raise ValueError('Laboratory identifier conflicts with its authority')
            if column['role'] == 'result' and not column.get('support'):
                raise ValueError('Result role requires heading/scope evidence')
        row_ids = set()
        for row in table['rows']:
            if row['id'] in row_ids or len(row['cells']) != len(columns):
                raise ValueError('Repeated row locator or wrong cell count')
            row_ids.add(row['id'])
            for index, cell in enumerate(row['cells']):
                if 'native_cell' in cell:
                    key = cell['native_cell']
                    if key not in native_cells:
                        raise ValueError('Unknown native cell')
                    if native_cells[key]['page'] != table['page']:
                        raise ValueError('A row cannot borrow a native value from another page')
                    if 'text' in cell:
                        raise ValueError('Native values must be copied, not regenerated')
                elif cell.get('text') is None:
                    if cell.get('cause') not in CAUSES:
                        raise ValueError('Null cell requires a named cause')
                    if cell['cause'] == 'not_stated' and not cell.get('examined_scope'):
                        raise ValueError('Source-not-stated claim needs an examined scope')
                elif not isinstance(cell['text'], str):
                    raise ValueError('Source values must remain strings')
                if 'identifier' in cell and 'result_value' in cell:
                    raise ValueError('A cell cannot supply both identifier and result components')
                for component in ('identifier', 'result_value'):
                    if component not in cell:
                        continue
                    if component == 'result_value' and table['columns'][index]['role'] != 'result':
                        raise ValueError('Result component requires a result column')
                    text = native_cells[cell['native_cell']]['text'] if 'native_cell' in cell else cell.get('text')
                    value, annotation = cell[component], cell.get('annotation', '')
                    if (not isinstance(value, str) or not isinstance(annotation, str)
                            or component == 'result_value' and not value.strip()):
                        raise ValueError('Cell components require literal strings and a nonempty result value')
                    forms = {''.join((value + annotation).split()), ''.join((annotation + value).split())}
                    if not text or ''.join(text.split()) not in forms:
                        raise ValueError('Cell value and annotation must reconstruct the literal source cell')
    for region in dispositions:
        outputs = set(region.get('output_tables', []))
        if not outputs <= table_ids or region['disposition'] == 'represented' and not outputs:
            raise ValueError('Represented native region requires existing output tables')
    fact_ids = [f['id'] for f in block['facts'] if 'id' in f]
    if len(fact_ids) != len(set(fact_ids)):
        raise ValueError('Fact identifiers must be unique within a block')
    for fact in block['facts']:
        support(fact)
        if not fact.get('role') or not fact.get('applies_to'):
            raise ValueError('Fact requires a role and explicit scope or unattached marker')
        if fact.get('value') is not None and not isinstance(fact['value'], str):
            raise ValueError('Fact components must remain source strings')
        if fact.get('section') is not None and not isinstance(fact['section'], str):
            raise ValueError('A source section must retain its printed heading')
        if fact.get('section') is not None:
            section = re.fullmatch(r'p([1-9]\d*)/(\S.*)', fact['section'])
            if section and int(section[1]) not in supplied_pages:
                raise ValueError('Section cites a page not supplied to this reading')
        if fact['role'] in {'record_continuation', 'field_continuation'}:
            # The relation binds the physical parts of one record printed across pages.
            # A whole table, a section heading or a fact is not a part of a record, and
            # a table whose rows simply continue under a heading printed once is not a
            # record continuation at all; that reading returns to the reader by name.
            parts = fact['applies_to']
            if len(parts) < 2 or any(not isinstance(scope, str) or not (
                    scope.startswith('native:') or ('/' in scope and not scope.startswith('section:')))
                    for scope in parts):
                raise ValueError('record_continuation must name at least two physical parts of one '
                                 'continued record as tableID/rowID or native:<cell> selectors; a table '
                                 'or section that continues onto a later page is not a record continuation, '
                                 'and its column roles cite the heading page in support instead')
    for issue in block['issues']:
        if not issue.get('cause') or not issue.get('scope'):
            raise ValueError('Reading limitation requires cause and scope')
    cell_components(block, native_cells)


def record_tables(reading, native):
    """Normalize a repeated transpose only after checking its complete matrix."""
    def text(cell):
        value = native[cell['native_cell']]['text'] if 'native_cell' in cell else cell.get('text')
        if value is None and cell.get('cause') != 'not_stated':
            return None
        return ' '.join((value or '').split())
    tables, issues, incomplete = [], [], set()
    for table in reading['tables']:
        columns = table['columns']
        # A printed label axis makes a transpose independently checkable; the
        # publisher need not also state in prose that its two displays repeat.
        labelled = (len(columns) > 1 and not columns[0]['heading']
                    and all(c['role'] in {'identifier', 'publisher_id'} and c['heading']
                            for c in columns[1:]))
        if labelled:
            candidates = []
            labels = [text(row['cells'][0]) for row in table['rows']]
            for companion in reading['tables']:
                if companion['id'] == table['id'] or companion['page'] != table['page']:
                    continue
                headings = [' '.join(' '.join(c['heading']).split()) for c in companion['columns']]
                ids = [i for i, c in enumerate(companion['columns']) if c['role'] in {'identifier', 'publisher_id'}]
                if len(ids) != 1 or len(set(headings)) != len(headings) or labels != headings:
                    continue
                source = {text(row['cells'][ids[0]]): row for row in companion['rows']}
                keys = [c['heading'][-1] for c in columns[1:]]
                if len(source) != len(companion['rows']) or len(set(keys)) != len(keys) or not set(keys) <= source.keys():
                    continue
                if any(text(raw['cells'][j + 1]) is None
                       or text(raw['cells'][j + 1]) != text(source[key]['cells'][i])
                       for j, key in enumerate(keys) for i, raw in enumerate(table['rows'])):
                    continue
                rows = [{'id': f'sample-column{j + 2}', 'cells': [dict(raw['cells'][j + 1],
                         source_position={'table': table['id'], 'reading_row': raw['id'], 'reading_column': j + 2})
                         for raw in table['rows']]} for j in range(len(keys))]
                candidates.append(dict(table, columns=companion['columns'], rows=rows,
                    projection={'rule': 'printed label axis and complete matrix equality',
                                'companion_table': companion['id']}))
            if len(candidates) == 1:
                tables.append(candidates[0])
            else:
                incomplete.add(table['page'])
                issues.append({'scope': table['id'], 'cause': 'labelled transpose has no unique complete matrix correspondence; source display retained'})
            continue
        transposed = len(columns) > 1 and all(c['role'] in {'identifier', 'publisher_id'} and len(c['heading']) > 1 for c in columns)
        if not transposed:
            tables.append(table)
            continue
        projected = []
        for companion in reading['tables']:
            pair = {table['id'], companion['id']}
            if len(pair) != 2 or companion['page'] != table['page'] or not any(
                    f['role'] == 'repeated_representation' and pair <= set(f['applies_to']) for f in reading['facts']):
                continue
            ids = [i for i, c in enumerate(companion['columns']) if c['role'] in {'identifier', 'publisher_id'}]
            if len(ids) != 1 or len(companion['rows']) != len(columns):
                continue
            identifier = ids[0]
            fields = [i for i in range(len(companion['columns'])) if i != identifier]
            if len(fields) != len(table['rows']):
                continue
            source = {text(r['cells'][identifier]): r for r in companion['rows']}
            headings = [' '.join(c['heading'][-1].split()) for c in columns]
            if None in source or len(source) != len(columns) or set(headings) != set(source):
                continue
            if any(c['heading'][:-1] != companion['columns'][identifier]['heading'] for c in columns):
                continue
            if any(text(raw['cells'][j]) is None or text(raw['cells'][j]) != text(source[headings[j]]['cells'][field])
                   for j in range(len(columns)) for raw, field in zip(table['rows'], fields)):
                continue
            rows = []
            for j, column in enumerate(columns):
                cells = [None] * len(companion['columns'])
                cells[identifier] = {'text': column['heading'][-1], 'source_heading': column['heading'],
                    'source_position': {'table': table['id'], 'reading_column': j + 1}}
                for raw, field in zip(table['rows'], fields):
                    cells[field] = dict(raw['cells'][j], source_position={
                        'table': table['id'], 'reading_row': raw['id'], 'reading_column': j + 1})
                rows.append({'id': f'sample-column{j + 1}', 'cells': cells})
            projected.append(dict(table, columns=companion['columns'], rows=rows,
                projection={'rule': 'complete matrix equality under a proposed repeated-representation relationship',
                            'companion_table': companion['id']}))
        if len(projected) == 1:
            tables.append(projected[0])
        else:
            incomplete.add(table['page'])
            issues.append({'scope': table['id'], 'cause': 'sample identities appear in column headings; no unique fully checked transpose correspondence; raw table retained without inventing sample rows'})
    return tables, issues, incomplete


def record_rows(reading):
    """Assemble only continuations explicitly recovered by the document reader.

    Physical rows, cells and qualification scopes remain unchanged in the reading.
    No layout, neighbouring values or duplicate display establishes this relation.
    """
    rows = reading.rows
    anchors = {}
    for row in rows:
        for anchor in {row.locator, row.locator.split('/', 1)[-1],
                       *('native:' + c['native_cell'] for c in row.cells if c.get('native_cell'))}:
            anchors.setdefault(anchor, []).append(row)
    groups, used = [], set()
    for fact in reading.facts:
        if fact['role'] != 'record_continuation':
            continue
        parts = []
        for scope in fact['applies_to']:
            candidates = anchors.get(scope, ())
            if len(candidates) != 1:
                raise ValueError('Continuation needs one physical record part at ' + scope)
            if candidates[0] not in parts:
                parts.append(candidates[0])
        identity = fact.get('value')
        if len(parts) < 2 or not identity or not any(identity in row.identifiers for row in parts):
            raise ValueError('Continuation needs at least two parts and their printed identity')
        if fact.get('text') != identity or not any(
                row.page == fact.get('page') and identity in row.identifiers for row in parts):
            raise ValueError('Continuation must quote its printed identity at the identity-bearing page')
        keys = {row.locator for row in parts}
        if used.intersection(keys):
            # Repeated declarations of exactly the same relationship are harmless.
            if any(keys == {r.locator for r in group} for group in groups):
                continue
            raise ValueError('A physical part belongs to conflicting continuations')
        used.update(keys)
        groups.append(parts)
    # A record binding does not by itself say that different field values are
    # fragments of one cell. Resolve the reader's explicit cell bindings first.
    cell_anchors = {}
    for row in rows:
        for cell in row.cells:
            for anchor in {cell['locator'], cell['locator'].split('/', 1)[-1],
                           *(['native:' + cell['native_cell']] if cell.get('native_cell') else [])}:
                cell_anchors.setdefault(anchor, []).append((row, cell))
    fragments = {}
    for fact in reading.facts:
        if fact['role'] != 'field_continuation':
            continue
        bound = []
        for scope in fact['applies_to']:
            matches = cell_anchors.get(scope, ())
            if len(matches) != 1:
                raise ValueError('Field continuation needs one physical cell at ' + scope)
            bound.append(matches[0])
        locators = frozenset(c['locator'] for _, c in bound)
        if len(locators) != len(bound) or len(bound) < 2:
            raise ValueError('Field continuation needs distinct physical fragments')
        group = next((group for group in groups if all(row in group for row, _ in bound)), None)
        if group is None:
            raise ValueError('Field fragments must belong to one declared record continuation')
        if (fact.get('text') != fact.get('value') or not fact.get('value') or not any(
                row.page == fact.get('page') and fact['value'] in row.identifiers for row in group)):
            raise ValueError('Field continuation must quote the record identity at its physical page')
        cells = [cell for _, cell in sorted(bound, key=lambda pair: rows.index(pair[0]))]
        if (len({(tuple(c['heading']), c['role']) for c in cells}) != 1
                or cells[0]['role'] not in {'host', 'municipality', 'other'}
                or any(not c['text'] or not c['text'].strip() for c in cells)):
            raise ValueError('Field continuation requires populated fragments of one descriptive field')
        if any(locators & previous and locators != previous for previous in fragments):
            raise ValueError('A physical cell belongs to conflicting field continuations')
        fragments[locators] = dict(cells[0], text=' '.join(c['text'].strip() for c in cells),
            basis='assembly of reader-declared field continuation', source_fragments=cells,
            reading_issues=tuple(i for c in cells for i in c.get('reading_issues', ())))
    assembled = {}
    consumed_fragments = set()
    for parts in groups:
        # Order follows physical occurrences, not the order of model selectors.
        parts = sorted(parts, key=lambda row: rows.index(row))
        fields = {}
        for row in parts:
            for cell in row.cells:
                key = (tuple(cell['heading']), cell['role'])
                fields.setdefault(key, []).append(cell)
        selected = []
        for cells in fields.values():
            populated = [c for c in cells if c['text'] and c['text'].strip()]
            binding = frozenset(c['locator'] for c in populated)
            if binding in fragments:
                selected.append(fragments[binding])
                consumed_fragments.add(binding)
                continue
            if len(populated) > 1:
                # Separate result occurrences are never collapsed into one test.
                if (populated[0]['role'] == 'result' or
                        len({c['text'] for c in populated}) != 1):
                    raise ValueError('Continuation contains overlapping or conflicting fields')
            selected.extend(populated or cells[:1])
        selected_locators = {c['locator'] for c in selected}
        results = tuple(result for row in parts for result in row.results
                        if result.locator in selected_locators)
        facts = tuple(f for i, row in enumerate(parts) for f in row.facts
                      if not any(f == old for earlier in parts[:i] for old in earlier.facts))
        dates = tuple(d for row in parts for d in row.sampling_dates
                      if d.text is None or d.text.strip())
        def sole(role):
            values = {c.get('identifier', c['text']) for c in selected
                      if c['role'] == role and c['text'] is not None}
            return next(iter(values)) if len(values) == 1 else None
        assembled[parts[0].locator] = replace(parts[0], cells=tuple(selected), results=results,
            reference=sole('publisher_id') or sole('identifier'), laboratory_reference=sole('laboratory_id'),
            sampling_dates=dates, facts=facts,
            projection={'rule': 'assembly of reader-declared record continuation',
                        'parts': [row.locator for row in parts]})
    if consumed_fragments != fragments.keys():
        raise ValueError('Field continuation does not account for every populated field occurrence')
    return tuple(assembled.get(row.locator, row) for row in rows
                 if row.locator not in used or row.locator in assembled)


def source_scopes(cell, table, raw, index):
    """Selectors of the original cell, including its original row and column."""
    position = cell.get('source_position', {
        'table': table['id'], 'reading_row': raw['id'], 'reading_column': index + 1})
    owner, column = position['table'], position['reading_column']
    scopes = {f'{owner}/c{column}'}
    if row := position.get('reading_row'):
        source_row = f'{owner}/{row}'
        scopes.update({source_row, f"p{table['page']}/{source_row}",
                       f'{source_row}/c{column}', f"p{table['page']}/{source_row}/c{column}"})
    if cell.get('native_cell'):
        scopes.add('native:' + cell['native_cell'])
    return scopes


def scoped_reading_issues(issues, selectors, *, known_selectors=None):
    """Bind explicit source selectors, never issue explanations."""
    known = selectors if known_selectors is None else known_selectors
    fields = []
    for issue in issues:
        scope = issue['scope'].strip()
        property_scope = scope.removesuffix(' identifier_authority')
        if property_scope != scope:
            # Who assigned an identifier is read by no accepted consumer, so an
            # issue limited to it constrains no field. Every reference, after
            # heading annotations, must resolve to a real field; otherwise the
            # scope is conflated or broad and binds as written.
            references = re.sub(r"\([^()]*\)|'[^']*'", '', property_scope).strip()
            targets, previous = set(), None
            for reference in re.split(r'\s*,\s*|\s+(?:and|e)\s+', references):
                reference = reference.strip()
                if previous and re.fullmatch(r'c[1-9]\d*', reference):
                    reference = previous.rsplit('/', 1)[0] + '/' + reference
                if reference not in known:
                    targets = None
                    break
                targets.add(reference)
                previous = reference
            if targets is not None:
                continue
        selected = False
        for selector in selectors:
            for match in re.finditer(r'(?<![\w/-])' + re.escape(selector) + r'(?![\w/-])', scope):
                # A row followed by an explicit cell reference selects that cell,
                # not all independent fields in the row. Unknown syntax stays broad.
                cell = re.match(r'\s+cell\s+(c[1-9]\d*)(?=\s*\(|$)', scope[match.end():])
                if cell and selector + '/' + cell[1] not in selectors:
                    continue
                selected = True
        if selected:
            fields.append(issue)
    return tuple(fields)


def materialize(digest, version, page_count, blocks):
    """Copy literal values, then project roles. Never merge rows by sample identifier."""
    facts = []
    for block_number, item in enumerate(blocks, 1):
        ids = {f['id']: f'b{block_number}/{f["id"]}' for f in item['reading']['facts'] if 'id' in f}
        for original in item['reading']['facts']:
            fact = dict(original, basis="model_proposed_reading")
            if fact.get('section') and not re.fullmatch(r'p([1-9]\d*)/(\S.*)', fact['section']):
                fact['section_reading'] = fact.pop('section')
                fact['section_cause'] = 'section heading recovered without its physical occurrence; scope unattached'
            if 'id' in fact:
                fact['id'] = ids[fact['id']]
            fact['applies_to'] = [ids.get(scope, scope) for scope in fact['applies_to']]
            if fact.get('value') is not None and fact['value'] not in fact['text']:
                fact.pop('value')
                fact['value_cause'] = 'model component was not literal; see raw response; no typed value supplied'
            facts.append(fact)
    link_section_marks(facts)
    facts = tuple(facts)
    issues = tuple(i for item in blocks for i in item['reading']['issues'])
    for item in blocks:
        if item.get('attachment_repair_pending'):
            issues += ({'scope': 'pages ' + ','.join(map(str, item['targets'])),
                        'cause': 'sampling-date attachment reread pending: ' + item['attachment_repair_pending']},)
        known_regions = {r['id'] for r in item.get('native_regions', [])}
        for page in item['reading']['pages']:
            for region in page.get('regions', []):
                if region.get('native_table') not in known_regions:
                    issues += ({'scope': region.get('native_table', 'unidentified region'),
                        'cause': 'model named a native-table region absent from the supplied detector inventory; visual output tables retained separately'},)
    continued_parts = {scope for f in facts if f['role'] == 'record_continuation'
                       for scope in f['applies_to']}
    rows, covered, locators, encountered = [], set(), set(), set()
    for block_number, item in enumerate(blocks, 1):
        data, native = item['reading'], item['native_cells']
        # The pages the model was shown for this block: recorded on the block when it was
        # read (the whole document under the subscription); otherwise targets and context.
        validate_block(data, targets=item['targets'], page_count=page_count, native_cells=native,
                       native_regions=item.get('native_regions', []),
                       supplied_pages=set(item.get('supplied_pages')
                                          or set(item['targets']) | set(item.get('context_pages', []))))
        components = cell_components(data, native)
        component_facts = {f['id']: f for f in facts if f.get('id', '').startswith(f'b{block_number}/')}
        for disposition in data['pages']:
            if disposition['page'] in encountered:
                raise ValueError('Overlapping target pages cannot be silently combined')
            encountered.add(disposition['page'])
            if disposition['disposition'] == 'read':
                covered.add(disposition['page'])
        tables, projection_issues, incomplete = record_tables(data, native)
        issues += tuple(projection_issues)
        known_selectors = {selector for table in tables for raw in table['rows']
                           for index, cell in enumerate(raw['cells'])
                           for selector in source_scopes(cell, table, raw, index)}
        known_selectors.update(f['id'] for f in data['facts'] if 'id' in f)
        covered.difference_update(incomplete)
        for table in tables:
            sample_table = any(c['role'] in {'identifier', 'publisher_id', 'laboratory_id', 'result'}
                               for c in table['columns'])
            for raw in table['rows']:
                locator = f"p{table['page']}/{table['id']}/{raw['id']}"
                anchors = {locator, f"{table['id']}/{raw['id']}",
                           *('native:' + c['native_cell'] for c in raw['cells'] if c.get('native_cell'))}
                if not sample_table and not anchors.intersection(continued_parts):
                    continue
                if locator in locators:
                    raise ValueError('Repeated source-row locator')
                locators.add(locator)
                cells, results = [], []
                scopes = {'report', table['id']}
                by_role = {}
                for index, (column, cell) in enumerate(zip(table['columns'], raw['cells'])):
                    text = native[cell['native_cell']]['text'] if 'native_cell' in cell else cell.get('text')
                    value = dict(cell, text=text, basis='native_cell_copy' if 'native_cell' in cell else 'vision_transcription',
                                 role=column['role'], heading=column['heading'],
                                 locator=f'{locator}/c{index + 1}')
                    if column['role'] in {'identifier', 'publisher_id', 'laboratory_id'}:
                        value['identifier_authority'] = column.get('identifier_authority')
                        value['authority_support'] = tuple(dict(s, basis='model_proposed_reading')
                            for s in column.get('authority_support', ()))
                    field_scopes = source_scopes(cell, table, raw, index)
                    scopes.update(field_scopes)
                    # Bind explicit field locators, never interpret words in the cause.
                    field_issues = scoped_reading_issues(issues, field_scopes, known_selectors=known_selectors)
                    if field_issues:
                        value['reading_issues'] = field_issues
                        if column['role'] in {'publisher_id', 'laboratory_id'}:
                            value['role_cause'] = 'unresolved reading at identifier column; see reading_issues'
                    if column['role'] in {'identifier', 'publisher_id'} and 'identifier' not in value and text:
                        annotation = re.fullmatch(r'\s*([^()\r\n]+?)\s*(\(Pool\))\s*', text)
                        if annotation and annotation[1].strip():
                            value.update(identifier=annotation[1].strip(), annotation=annotation[2],
                                         identifier_basis='literal (Pool) suffix; complete cell retained')
                    cells.append(value)
                    by_role.setdefault(column['role'], []).append(value)
                    physical = cell.get('source_position', {
                        'table': table['id'], 'reading_row': raw['id'], 'reading_column': index + 1})
                    source_cell = (f"p{table['page']}/{physical['table']}/"
                                   f"{physical.get('reading_row')}/c{physical['reading_column']}")
                    for component in components.get(source_cell, ()):
                        fact = component_facts[f"b{block_number}/{component['fact']['id']}"]
                        field = dict(text=fact['value'], role=fact['role'], heading=column['heading'],
                            locator=f"{value['locator']}/fact:{fact['id']}",
                            basis='literal component of a reader-selected source cell',
                            source_fragments=(value,), source_span=component['span'], support=(fact,))
                        # Fact IDs belong to this block. A precise issue constrains
                        # that component; a broader parent issue still travels with it.
                        own_issues = scoped_reading_issues(
                            data['issues'], {component['fact']['id']}, known_selectors=known_selectors)
                        component_issues = field_issues + tuple(issue for issue in own_issues
                                                              if issue not in field_issues)
                        if component_issues:
                            field['reading_issues'] = component_issues
                        if fact['role'] == 'identifier':
                            field['identifier'] = fact['value']
                        cells.append(field)
                        by_role.setdefault(fact['role'], []).append(field)
                    if column['role'] == 'result':
                        assay, analyte = column.get('test'), column.get('analyte')
                        assay_cause = None
                        if assay and analyte and assay.casefold().strip() == analyte.casefold().strip():
                            assay, assay_cause = None, 'test field repeats analyte; distinct test designation not recovered here'
                        results.append(Result(value['locator'], tuple(column['heading']),
                            assay, analyte, text, classify(cell.get('result_value', text)), cell.get('cause'),
                            tuple(dict(s, basis='model_proposed_reading') for s in column.get('support', ())), assay_cause))
                def sole(role):
                    fields = by_role.get(role, [])
                    if any(c.get('role_cause') for c in fields):
                        return None
                    values = [c.get('identifier', c['text']) for c in fields if c['text'] is not None]
                    return values[0] if len(values) == 1 else None
                direct_scopes = set(scopes)
                # A qualifier of an included statement travels with that statement.
                # Keep its exact scope; inclusion in row context does not broaden it.
                while True:
                    scoped = tuple(f for f in facts if scopes.intersection(f['applies_to']))
                    expanded = scopes | {f['id'] for f in scoped if 'id' in f}
                    expanded.update('section:' + f['section'] for f in scoped if f.get('section'))
                    if expanded == scopes:
                        break
                    scopes = expanded
                year_context = tuple((int(year), f['id']) for f in scoped
                    if f['role'] in {'date', 'report_date', 'delivery_date', 'sampling_date', 'test_date', 'acceptance_date'}
                    and not f.get('value_cause')
                    for year in re.findall(r'(?<!\d)(\d{4})(?!\d)', f.get('value') or f['text']))
                dates = tuple(literal_date(c['text'], c.get('cause'), year_context=year_context)
                              for c in by_role.get('sampling_date', []))
                shared_dates = tuple(literal_date(None, f['value_cause']) if f.get('value_cause') else literal_date(f.get('value') or f['text'], year_context=year_context) for f in scoped
                                     if f['role'] == 'sampling_date' and
                                     direct_scopes.intersection(f['applies_to']))
                dates += shared_dates
                generic = sole('identifier')
                results = [resolve_marks(result, scoped) for result in results]
                rows.append(Row(locator, table['page'], sole('publisher_id') or generic, sole('laboratory_id'),
                                dates, tuple(cells), tuple(results), scoped, table.get('projection')))
    missing = set(range(1, page_count + 1)) - encountered
    if missing:
        issues += ({'scope': 'pages ' + ','.join(map(str, sorted(missing))),
                    'cause': 'no accepted block reading is present'},)
    return Report(digest, version, page_count, tuple(rows), facts, issues, frozenset(covered))


def _nonwhitespace(text):
    return Counter(c for c in (text or '') if not c.isspace())


POSITIONED_ROLES = frozenset({'identifier', 'publisher_id', 'laboratory_id'})

REORDERED_CHECK = 'geometry order applied; inventory identical'
AGREED_CHECK = 'geometry order agrees with the native cell'
UNREAD_CHECK = 'geometry recovered no comparable text; native cell retained'
DIVERGED_CHECK = 'geometry read disagrees with the retained cell; native cell retained'


def _positioned_cell(cell):
    """The native table cell owed a positioned record, as its parsed locator, or None."""
    if cell.get('role') not in POSITIONED_ROLES or 'identifier' in cell:
        return None
    return re.fullmatch(r'p(\d+)-t(\d+)-r(\d+)-c(\d+)', cell.get('native_cell') or '')


def _geometry_outcome(positioned, native):
    """Say what the geometry read of a native identifier cell found, in its own words.

    `positioned` is what the clip returned. A clip that recovered nothing and a clip
    that recovered other text are different facts with different remedies — bounds
    that missed the text against bounds that took a neighbour's — and are never one
    cause because each leaves the native cell in place.
    """
    if _nonwhitespace(positioned) != _nonwhitespace(native):
        return UNREAD_CHECK if not _nonwhitespace(positioned) else DIVERGED_CHECK
    if ' '.join(positioned.split()) == ' '.join(native.split()):
        return AGREED_CHECK
    return REORDERED_CHECK


def _owes_positioned_records(reading):
    """Whether this reading has a native identifier cell that a record must speak for."""
    return any(_positioned_cell(cell) is not None for row in reading.rows for cell in row.cells)


def positioned_identifier_records(reading, source):
    """Compare each native identifier cell to the source PDF; record geometry order."""
    import pymupdf
    records, tables = [], {}
    with pymupdf.open(source) as document:
        for row in reading.rows:
            for cell in row.cells:
                key = _positioned_cell(cell)
                if key is None:
                    continue
                page, ti, ri, ci = (int(x) - 1 for x in key.groups())
                if page not in tables:
                    tables[page] = document[page].find_tables().tables
                table = tables[page][ti]
                if table.extract()[ri][ci] != cell['text']:
                    raise ValueError('Retained native identifier differs from its source cell')
                bounds = table.rows[ri].cells[ci]
                positioned = '\n'.join(line.strip() for line in document[page].get_text(
                    'text', clip=pymupdf.Rect(bounds), sort=True).strip().splitlines())
                native = cell['text']
                outcome = _geometry_outcome(positioned, native)
                record = {
                    'locator': cell['locator'],
                    'text': positioned if outcome == REORDERED_CHECK else native,
                    'source_bbox': list(bounds),
                    'check': outcome,
                }
                if outcome == DIVERGED_CHECK:
                    record['geometry_text'] = positioned  # what the clip read, kept apart
                records.append(record)
    return records


def apply_positioned_identifiers(reading, records):
    """Apply stored geometry readings; refuse a native identifier cell that carries none,
    or a positioned text whose inventory diverges from its retained native cell."""
    by_locator = {item['locator']: item for item in records}
    rows = []
    for row in reading.rows:
        cells = []
        for cell in row.cells:
            item = by_locator.get(cell['locator'])
            if item is None:
                if _positioned_cell(cell) is not None:
                    raise ValueError(
                        'Native identifier cell without a positioned record; records removed '
                        'from a reading that carries them — reassemble at the current '
                        'extraction version')
            else:
                native = cell['text']
                if _nonwhitespace(item['text']) != _nonwhitespace(native):
                    raise ValueError('Positioned identifier does not conserve its retained native cell')
                cell = dict(cell, text=item['text'],
                            source_bbox=item['source_bbox'], check=item['check'])
                if item['text'] != native:
                    cell['native_text'] = native
                    cell['basis'] = 'native cell geometry order; identical non-whitespace character inventory'
            cells.append(cell)
        def sole(role):
            fields = [c for c in cells if c['role'] == role]
            if any(c.get('role_cause') for c in fields):
                return None
            values = [c.get('identifier', c['text']) for c in fields if c['text'] is not None]
            return values[0] if len(values) == 1 else None
        rows.append(replace(row, cells=tuple(cells), reference=sole('publisher_id') or sole('identifier'),
                            laboratory_reference=sole('laboratory_id')))
    return replace(reading, rows=tuple(rows))


def positioned_identifiers(reading, source):
    """Recover native identifier order from its cell geometry; retain both readings."""
    return apply_positioned_identifiers(reading, positioned_identifier_records(reading, source))


REPORT_MEMO = None


def report(digest: str, store: Path, *, extraction_version: str):
    if REPORT_MEMO is not None and (digest, extraction_version) in REPORT_MEMO:
        return REPORT_MEMO[(digest, extraction_version)]
    if not blob_path(store, digest).exists():
        return UnreadReport(digest, 'declared source bytes unavailable')
    path = store / 'derived/reports' / extraction_version / digest / 'report.json'
    if not path.exists():
        return UnreadReport(digest, 'no assembled reading for this extraction version')
    payload = json.loads(path.read_text())
    if payload['source_sha256'] != digest or payload['extraction_version'] != extraction_version:
        raise ValueError('Reading identity does not match requested source/version')
    reading = materialize(digest, extraction_version, payload['page_count'], payload['blocks'])
    if 'positioned_identifiers' not in payload and _owes_positioned_records(reading):
        # An earlier retained version is a reading this reader cannot read, not a false one.
        return UnreadReport(digest, 'assembled before positioned identifiers were derived; '
                                    'reassemble at this extraction version')
    reading = apply_positioned_identifiers(reading, payload.get('positioned_identifiers') or ())
    from .report_relations import load
    reading = replace(reading, relations=load(store, digest, exact=True),
                      assembly_complete=payload.get('assembly_complete'))
    if REPORT_MEMO is not None:
        REPORT_MEMO[(digest, extraction_version)] = reading
    return reading


def reports(root: Path, store: Path, *, extraction_version: str, known_through=None):
    seen = set()
    if known_through is not None and (known_through.tzinfo is None or known_through.utcoffset() is None):
        raise ValueError('A knowledge cutoff must be timezone-aware')
    for capture in json.loads((root / 'records.json').read_text()):
        if known_through is not None and datetime.fromisoformat(capture['captured_at']) > known_through:
            continue
        digest = capture.get('sha256')
        if digest and digest not in seen:
            seen.add(digest)
            yield report(digest, store, extraction_version=extraction_version)

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
RESULTS = {'positivo': 'positive', 'negativo': 'negative', 'rilevato': 'detected',
           'non rilevato': 'not-detected', 'non determinabile': 'undetermined',
           'rilevata': 'detected', 'non rilevata': 'not-detected',
           'dubbio': 'doubtful', 'presente': 'detected', 'assente': 'not-detected'}


def classify(text):
    return RESULTS.get(' '.join(text.casefold().split()), 'unclassified') if text else 'unread'


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
        return next(iter(values)) if len(values) == 1 and all(d.value for d in self.sampling_dates) else None

    @property
    def date_cause(self):
        if not self.sampling_dates:
            return 'no sampling date attached to this row'
        if self.sampling_date is not None:
            return None
        causes = {value.cause for value in self.sampling_dates if value.cause}
        return '; '.join(sorted(causes)) if causes else 'conflicting sampling-date values'


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
            for cell in row['cells']:
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
                if 'identifier' in cell:
                    text = native_cells[cell['native_cell']]['text'] if 'native_cell' in cell else cell.get('text')
                    identifier, annotation = str(cell['identifier']), str(cell.get('annotation', ''))
                    # The annotation may be printed before or after the identifier (`*513077`, `1640733 (Pool)`).
                    forms = {' '.join(identifier.split()) + ' ' + ' '.join(annotation.split()),
                             ' '.join(annotation.split()) + ' ' + ' '.join(identifier.split())}
                    if (not isinstance(cell['identifier'], str) or not text
                            or ''.join(text.split()) not in {''.join(form.split()) for form in forms}):
                        raise ValueError('Identifier and annotation must reconstruct the literal source cell')
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
    for issue in block['issues']:
        if not issue.get('cause') or not issue.get('scope'):
            raise ValueError('Reading limitation requires cause and scope')


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
    assembled = {}
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
            populated = [c for c in cells if c['text'] is not None]
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
        dates = tuple(d for row in parts for d in row.sampling_dates)
        def sole(role):
            values = {c.get('identifier', c['text']) for c in selected
                      if c['role'] == role and c['text'] is not None}
            return next(iter(values)) if len(values) == 1 else None
        assembled[parts[0].locator] = replace(parts[0], cells=tuple(selected), results=results,
            reference=sole('publisher_id') or sole('identifier'), laboratory_reference=sole('laboratory_id'),
            sampling_dates=dates, facts=facts,
            projection={'rule': 'assembly of reader-declared record continuation',
                        'parts': [row.locator for row in parts]})
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
    rows, covered, locators, encountered = [], set(), set(), set()
    for item in blocks:
        data, native = item['reading'], item['native_cells']
        # The pages the model was shown for this block: recorded on the block when it was
        # read (the whole document under the subscription); otherwise targets and context.
        validate_block(data, targets=item['targets'], page_count=page_count, native_cells=native,
                       native_regions=item.get('native_regions', []),
                       supplied_pages=set(item.get('supplied_pages')
                                          or set(item['targets']) | set(item.get('context_pages', []))))
        for disposition in data['pages']:
            if disposition['page'] in encountered:
                raise ValueError('Overlapping target pages cannot be silently combined')
            encountered.add(disposition['page'])
            if disposition['disposition'] == 'read':
                covered.add(disposition['page'])
        tables, projection_issues, incomplete = record_tables(data, native)
        issues += tuple(projection_issues)
        covered.difference_update(incomplete)
        for table in tables:
            if not any(c['role'] in {'identifier', 'publisher_id', 'laboratory_id', 'result'} for c in table['columns']):
                continue  # Non-sample tables remain in the literal block, not sample counts.
            for raw in table['rows']:
                locator = f"p{table['page']}/{table['id']}/{raw['id']}"
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
                    field_issues = tuple(issue for issue in issues if any(re.search(
                        r'(?<![\w/-])' + re.escape(field) + r'(?![\w/-])', issue['scope'])
                        for field in field_scopes))
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
                    if column['role'] == 'result':
                        assay, analyte = column.get('test'), column.get('analyte')
                        assay_cause = None
                        if assay and analyte and assay.casefold().strip() == analyte.casefold().strip():
                            assay, assay_cause = None, 'test field repeats analyte; distinct test designation not recovered here'
                        results.append(Result(value['locator'], tuple(column['heading']),
                            assay, analyte, text, classify(text), cell.get('cause'),
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
                rows.append(Row(locator, table['page'], sole('publisher_id') or generic, sole('laboratory_id'),
                                dates, tuple(cells), tuple(results), scoped, table.get('projection')))
    missing = set(range(1, page_count + 1)) - encountered
    if missing:
        issues += ({'scope': 'pages ' + ','.join(map(str, sorted(missing))),
                    'cause': 'no accepted block reading is present'},)
    return Report(digest, version, page_count, tuple(rows), facts, issues, frozenset(covered))


def positioned_identifiers(reading, source):
    """Recover native identifier order from its cell geometry; retain both readings."""
    import pymupdf
    rows, tables = [], {}
    with pymupdf.open(source) as document:
        for row in reading.rows:
            cells = []
            for cell in row.cells:
                key = re.fullmatch(r'p(\d+)-t(\d+)-r(\d+)-c(\d+)', cell.get('native_cell', ''))
                if key and cell['role'] in {'identifier', 'publisher_id', 'laboratory_id'} and 'identifier' not in cell:
                    page, ti, ri, ci = (int(x) - 1 for x in key.groups())
                    if page not in tables:
                        tables[page] = document[page].find_tables().tables
                    table = tables[page][ti]
                    if table.extract()[ri][ci] != cell['text']:
                        raise ValueError('Retained native identifier differs from its source cell')
                    bounds = table.rows[ri].cells[ci]
                    positioned = '\n'.join(line.strip() for line in document[page].get_text(
                        'text', clip=pymupdf.Rect(bounds), sort=True).strip().splitlines())
                    characters = lambda text: Counter(c for c in text if not c.isspace())
                    if (' '.join(positioned.split()) != ' '.join(cell['text'].split())
                            and characters(positioned) == characters(cell['text'])):
                        cell = dict(cell, text=positioned, native_text=cell['text'],
                            basis='native cell geometry order; identical non-whitespace character inventory',
                            source_bbox=list(bounds))
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


def report(digest: str, store: Path, *, extraction_version: str):
    if not blob_path(store, digest).exists():
        return UnreadReport(digest, 'declared source bytes unavailable')
    path = store / 'derived/reports' / extraction_version / digest / 'report.json'
    if not path.exists():
        return UnreadReport(digest, 'no assembled reading for this extraction version')
    payload = json.loads(path.read_text())
    if payload['source_sha256'] != digest or payload['extraction_version'] != extraction_version:
        raise ValueError('Reading identity does not match requested source/version')
    reading = materialize(digest, extraction_version, payload['page_count'], payload['blocks'])
    if any('native_cell' in c and c['role'] in {'identifier', 'publisher_id', 'laboratory_id'} for r in reading.rows for c in r.cells):
        reading = positioned_identifiers(reading, blob_path(store, digest))
    from .report_relations import load
    return replace(reading, relations=load(store, digest, exact=True),
                   assembly_complete=payload.get('assembly_complete'))


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

"""Source addresses for administrative interpretation; no operative classification."""
import json
import unicodedata

from .source_associations import read_associations, _header, _lines, _orientation
from .store import blob_path, file_digest


def native_text_issue(text):
    """Name structural extraction loss, without guessing the printed characters."""
    if text is None:
        return 'Native cell text was not extracted'
    if any(unicodedata.category(character) in {'Co', 'Cs'} or character == '\ufffd'
           for character in text):
        return 'Native text contains opaque or replacement characters; read the rendered source cell'
    return None


def _cell_field(table, table_ref, cell):
    field = dict(table['cells'][cell], source=table['source'], page=table['page'],
                 locator=f'{table_ref}/cell:{cell}')
    issue = native_text_issue(field['text'])
    if issue:
        field.update(native_text=field['text'], text=None, native_text_issue=issue)
    return field


def _character_key(character):
    return character['c'], tuple(character['origin']), tuple(character['bbox'])


def _characters(raw):
    return (character for block in raw['blocks'] for line in block.get('lines', [])
            for span in line['spans'] for character in span['chars'])


def _word_geometry(page, lines):
    """Locate the existing line words in the same PDF characters, without reflow."""
    extracted = []
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            words, boxes, characters, members = [], [], [], []

            def finish():
                if characters:
                    words.append(''.join(c['c'] for c in characters))
                    boxes.append([min(c['bbox'][0] for c in characters),
                                  min(c['bbox'][1] for c in characters),
                                  max(c['bbox'][2] for c in characters),
                                  max(c['bbox'][3] for c in characters)])
                    members.append(tuple(_character_key(c) for c in characters))
                    characters.clear()

            for span in line['spans']:
                for character in span['chars']:
                    if character['c'].isspace():
                        finish()
                    else:
                        characters.append(character)
            finish()
            if words:
                extracted.append((words, boxes, members, list(line['bbox'])))
    if len(extracted) != len(lines):
        return [(None, None)] * len(lines)
    return [(boxes, members) if words == text.split() and box == list(native_box) else (None, None)
            for (words, boxes, members, box), (text, native_box, _) in zip(extracted, lines)]


def source_material(sources, store):
    """Reuse association occurrences and expose native cells, words and images.

    Cell membership follows drawn PDF boundaries. It establishes where characters
    are printed, never what work a table prescribes or who holds the land.
    The accepted association owner's orientation helpers keep its row addresses
    and source coordinates aligned without another association implementation.
    """
    import pymupdf
    material = {'tables': {}, 'lines': {}, 'images': {}, 'pages': {}, 'cell_characters': {}}
    associations = []
    for index, digest in enumerate(sources):
        path = blob_path(store, digest)
        if file_digest(path) != digest:
            raise ValueError('Measure source bytes differ from their content address')
        reading = read_associations(digest, store)
        associations.append(reading)
        owned = {(r['page'], r['table'], r['row']): r for r in reading.rows}
        for row in reading.rows:
            for fragment in row.get('continuations', []):
                owned[(fragment['page'], fragment['table'], fragment['row'])] = row
        with pymupdf.open(path) as document, pymupdf.open(path) as native_document:
            for number, page in enumerate(document, 1):
                prefix = f'S{index}P{number}'
                material['pages'][prefix] = {
                    'source': digest, 'page': number, 'bbox': list(page.rect)}
                lines = tuple(_lines(page))
                geometry = _word_geometry(page, lines)
                for line_number, ((text, box, _), (word_boxes, word_characters)) in enumerate(zip(lines, geometry), 1):
                    material['lines'][f'{prefix}L{line_number}'] = {
                        'source': digest, 'page': number, 'bbox': list(box),
                        'words': text.split(), 'word_boxes': word_boxes,
                        'word_characters': word_characters}
                for image_number, entry in enumerate(page.get_image_info(), 1):
                    material['images'][f'{prefix}I{image_number}'] = {
                        'source': digest, 'page': number, 'bbox': list(entry['bbox'])}
                angle = _orientation(lines)
                if angle is None:
                    continue
                page.set_rotation(angle)
                forward = page.rotation_matrix
                page.remove_rotation()
                inverse = ~forward
                for table_number, table in enumerate(page.find_tables(strategy='lines_strict').tables, 1):
                    values = table.extract()
                    cell_text = {tuple(box): values[r][c]
                                 for r, row in enumerate(table.rows)
                                 for c, box in enumerate(row.cells) if box is not None}
                    boxes = sorted(set(tuple(b) for b in table.cells if b is not None))
                    xs = sorted({b[i] for b in boxes for i in (0, 2)})
                    ys = sorted({b[i] for b in boxes for i in (1, 3)})
                    # A nonrectangular grid remains visible in the whole document;
                    # it is not silently coerced into an ordinary ruled table.
                    if len(xs) != table.col_count + 1 or len(ys) != table.row_count + 1:
                        continue
                    cells = {}
                    for cell_number, box in enumerate(boxes, 1):
                        native_box = list(pymupdf.Rect(box) * inverse)
                        cells[str(cell_number)] = {
                            'text': cell_text[box],
                            'bbox': native_box}
                        # Native clipping selects actual glyph occurrences. A
                        # word's font envelope may graze an adjacent cell without
                        # assigning any of its characters to that cell.
                        material['cell_characters'][(digest, number, *native_box)] = frozenset(
                            _character_key(c) for c in _characters(native_document[number - 1].get_text(
                                'rawdict', clip=pymupdf.Rect(native_box))) if not c['c'].isspace())
                    rows = []
                    for row in range(table.row_count):
                        cell_ids = []
                        for column in range(table.col_count):
                            x = (xs[column] + xs[column + 1]) / 2
                            y = (ys[row] + ys[row + 1]) / 2
                            containing = [str(i + 1) for i, b in enumerate(boxes)
                                          if b[0] < x < b[2] and b[1] < y < b[3]]
                            cell_ids.append(containing[0] if len(containing) == 1 else None)
                        association = owned.get((number, table_number, row + 1))
                        occurrence = {'row': row + 1, 'cells': cell_ids, 'association': association}
                        if association and (number, table_number, row + 1) != (
                                association['page'], association['table'], association['row']):
                            occurrence['continuation_of'] = (
                                f"S{index}P{association['page']}T{association['table']}R{association['row']}")
                        rows.append(occurrence)
                    material['tables'][f'{prefix}T{table_number}'] = {
                        'source': digest, 'page': number, 'table': table_number,
                        'bbox': list(pymupdf.Rect(table.bbox) * inverse),
                        'cells': cells, 'rows': rows}
                    native_table = material['tables'][f'{prefix}T{table_number}']
                    headers = _header(values, required={'plant_id'})
                    if len(headers) == 1:
                        header_row, roles = headers[0]
                        native_table['native_header'] = {
                            'row': header_row + 1,
                            'columns': {role: column + 1 for column, role in roles.items()}}
                    else:
                        native_table['native_field_issue'] = (
                            'Native reading did not establish one unique plant-bearing header; '
                            'additional native field roles remain unavailable')
    return material, tuple(associations)


CONTEXT_MARKER = '\nSOURCE ADDRESSES (one-based rows/columns; zero-based word offsets)\n'


def _address_values(addresses):
    """Only values the model selects; geometry remains with native composition."""
    tables = {}
    for ref, table in addresses['tables'].items():
        cells = {key: cell['text'] if isinstance(cell, dict) else cell
                 for key, cell in table['cells'].items()}
        tables[ref] = dict(cells=cells,
                          rows=[{key: value for key, value in row.items()
                                 if key != 'association' or value is not None}
                                for row in table['rows']])
        issues = {key: issue for key, value in cells.items()
                  if (issue := native_text_issue(value))}
        if issues:
            tables[ref]['native_text_issues'] = issues
    return {
        'tables': tables,
        'lines': {ref: line['words'] if isinstance(line, dict) else line
                  for ref, line in addresses['lines'].items()},
        'images': sorted(addresses['images']),
    }


def material_addresses(material):
    """References are source addresses, not replacements for printed identifiers."""
    tables = {ref: dict(t, rows=[dict(row, association=(list(row['association']['fields'])
                            if row['association'] else None)) for row in t['rows']])
              for ref, t in material['tables'].items()}
    return _address_values(dict(tables=tables, lines=material['lines'], images=material['images']))


def _legacy_addresses(material):
    """The exact earlier context omitted every line centered inside a table."""
    addresses = material_addresses(material)
    lines = {}
    for ref, line in material['lines'].items():
        x0, y0, x1, y1 = line['bbox']
        if any(t['source'] == line['source'] and t['page'] == line['page']
               and t['bbox'][0] <= (x0+x1)/2 <= t['bbox'][2]
               and t['bbox'][1] <= (y0+y1)/2 <= t['bbox'][3]
               for t in material['tables'].values()):
            continue
        lines[ref] = line['words']
    return dict(addresses, lines=lines)


def material_context(material):
    return CONTEXT_MARKER + json.dumps(material_addresses(material),
                                       ensure_ascii=False, separators=(',', ':'))


def context_matches(prompt, material):
    """Replay exact current or earlier contexts, never arbitrary address subsets."""
    if CONTEXT_MARKER not in prompt:
        return False
    supplied, _ = json.JSONDecoder().raw_decode(prompt.split(CONTEXT_MARKER, 1)[1])
    # Earlier requests supplied redundant source boxes and empty row attributes.
    values = _address_values(supplied)
    for current in (material_addresses(material), _legacy_addresses(material)):
        # A native-owner repair can establish a previously unresolved continuation
        # without changing any supplied cell, word or address. Old requests need
        # not invent that later metadata; a conflicting recorded link still fails.
        for ref, table in current['tables'].items():
            prior = values['tables'].get(ref, {})
            for row, old_row in zip(table['rows'], prior.get('rows', [])):
                if 'continuation_of' not in old_row:
                    row.pop('continuation_of', None)
        if values == current:
            return True
    return False


def selected_association(material, reference):
    """An explicit source-row selection, never an identifier-value match."""
    if reference is None:
        return None
    table = material['tables'][reference['table_ref']]
    row = reference['row']
    if not 1 <= row <= len(table['rows']):
        raise ValueError('Association selection outside its source table')
    association = table['rows'][row - 1]['association']
    if association is None:
        raise ValueError('Selected source row has no established association')
    return association


def field_fragment(material, reference):
    """Copy an explicitly selected additional-field fragment, never owned fields."""
    if 'line_ref' in reference:
        fragment = native_span(material, reference)
        if span_overlaps(material, reference, material['tables'].values()):
            raise ValueError('Use source cells for a fragment inside a native table')
        return fragment
    table_ref, cell = reference['table_ref'], reference['cell']
    table = material['tables'][table_ref]
    for row in table['rows']:
        association = row['association']
        if association and any(row['cells'][field['column'] - 1] == cell
                               for field in association['fields'].values()):
            raise ValueError('The association owner already supplies this source column')
    field = _cell_field(table, table_ref, cell)
    if 'transcription' in reference:
        if not field.get('native_text_issue'):
            raise ValueError('Use the native source cell value, including a printed blank')
        text = reference['transcription']
        if not text.strip() or native_text_issue(text):
            raise ValueError('A visual cell reading needs recovered source text')
        field.update(text=text, derivation='model transcription of rendered source cell')
    return field


def table_fields(material, table_ref, row_number, columns, fragments=None):
    table = material['tables'][table_ref]
    row = table['rows'][row_number - 1]
    association = row['association']
    fields = dict(association['fields']) if association else {}
    for role, column in columns.items():
        if role in fields:
            raise ValueError('The association owner already supplies this field')
        if association and any(f['column'] == column for f in association['fields'].values()):
            raise ValueError('The association owner already supplies this source column')
        if not 1 <= column <= len(row['cells']):
            raise ValueError('Column outside the source table')
        cell = row['cells'][column - 1]
        if cell is None:
            raise ValueError('No unique physical cell at the selected source position')
        fields[role] = _cell_field(table, table_ref, cell)
        references = (fragments or {}).get(role, [])
        if references:
            parts = [field_fragment(material, reference) for reference in references]
            keys = [(p['source'], p['page'], p['locator']) for p in parts]
            if len(keys) != len(set(keys)):
                raise ValueError('A composed source field repeats a fragment')
            if any(p['source'] != table['source'] for p in parts):
                raise ValueError('A field continuation must stay within its source document')
            if fields[role]['locator'] not in {p['locator'] for p in parts}:
                raise ValueError('A field continuation must retain its selected row cell')
            spans = [r for r in references if 'line_ref' in r]
            if any(a['line_ref'] == b['line_ref']
                   and max(a['first_word'], b['first_word']) < min(a['end_word'], b['end_word'])
                   for i, a in enumerate(spans) for b in spans[i + 1:]):
                raise ValueError('A composed source field has overlapping spans')
            if not any((p['text'] or '').strip() for p in parts):
                raise ValueError('A field continuation has no recovered source text')
            fields[role] = {'text': (None if any(p['text'] is None for p in parts) else
                                    '\n'.join(p['text'] for p in parts)),
                            'fragments': parts}
    header = table.get('native_header')
    if association is None and header and row_number > header['row']:
        for role, column in header['columns'].items():
            # Explicit positions can give a column a different source-supported
            # role, such as a reference plant in a surrounding-parcel table.
            if role in fields or column in columns.values():
                continue
            cell = row['cells'][column - 1]
            heading = table['rows'][header['row'] - 1]['cells'][column - 1]
            if cell is None or heading is None:
                continue
            fields[role] = dict(_cell_field(table, table_ref, cell), column=column,
                header=dict(table['cells'][heading], source=table['source'], page=table['page'],
                            locator=f'{table_ref}/cell:{heading}'))
    return fields, association


def native_span(material, span):
    line = material['lines'][span['line_ref']]
    start, end = span['first_word'], span['end_word']
    if not 0 <= start < end <= len(line['words']):
        raise ValueError('Word selection outside its source line')
    return dict({key: value for key, value in line.items()
                 if key not in {'word_boxes', 'word_characters'}},
                text=' '.join(line['words'][start:end]),
                locator=f"{span['line_ref']}/words:{start}:{end}")


def span_overlaps(material, span, areas):
    """Check selected character identity against native cell membership."""
    native_span(material, span)
    line = material['lines'][span['line_ref']]

    def intersects(left, right):
        return (max(left[0], right[0]) < min(left[2], right[2])
                and max(left[1], right[1]) < min(left[3], right[3]))

    reached = [area for area in areas
               if (area['source'], area['page']) == (line['source'], line['page'])
               and intersects(line['bbox'], area['bbox'])]
    if not reached:
        return False
    boxes = line.get('word_boxes')
    if boxes is None:
        raise ValueError('Native span lacks exact word geometry for source-cell overlap; '
                         'use the source cells or retain this reading limitation')
    characters = line.get('word_characters')
    if characters is None:
        raise ValueError('Native span lacks exact character identity for source-cell membership')
    selected = {c for word in characters[span['first_word']:span['end_word']] for c in word}
    for area in reached:
        cells = area['cells'].values() if 'cells' in area else (area,)
        for cell in cells:
            key = area['source'], area['page'], *cell['bbox']
            members = material.get('cell_characters', {}).get(key)
            if members is None:
                raise ValueError('Source area lacks native cell character membership')
            if selected & members:
                return True
    return False


def association_areas(material):
    """Source cells already owned by native associations, including continuations."""
    for table in material['tables'].values():
        for row in table['rows']:
            if row['association']:
                for field in row['association']['fields'].values():
                    cell = row['cells'][field['column'] - 1]
                    if cell is not None:
                        yield dict(source=table['source'], page=table['page'],
                                   bbox=table['cells'][cell]['bbox'])

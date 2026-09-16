"""Source addresses for administrative interpretation; no operative classification."""
import json

from .source_associations import read_associations, _lines, _orientation
from .store import blob_path


def source_material(sources, store):
    """Reuse association occurrences and expose native cells, words and images.

    Cell membership follows drawn PDF boundaries. It establishes where characters
    are printed, never what work a table prescribes or who holds the land.
    The accepted association owner's orientation helpers keep its row addresses
    and source coordinates aligned without another association implementation.
    """
    import pymupdf
    material = {'tables': {}, 'lines': {}, 'images': {}, 'pages': {}}
    associations = []
    for index, digest in enumerate(sources):
        reading = read_associations(digest, store)
        associations.append(reading)
        owned = {(r['page'], r['table'], r['row']): r for r in reading.rows}
        for row in reading.rows:
            for fragment in row.get('continuations', []):
                owned[(fragment['page'], fragment['table'], fragment['row'])] = row
        with pymupdf.open(blob_path(store, digest)) as document:
            for number, page in enumerate(document, 1):
                prefix = f'S{index}P{number}'
                material['pages'][prefix] = {
                    'source': digest, 'page': number, 'bbox': list(page.rect)}
                for line_number, (text, box, _) in enumerate(_lines(page), 1):
                    material['lines'][f'{prefix}L{line_number}'] = {
                        'source': digest, 'page': number, 'bbox': list(box),
                        'words': text.split()}
                for image_number, entry in enumerate(page.get_image_info(), 1):
                    material['images'][f'{prefix}I{image_number}'] = {
                        'source': digest, 'page': number, 'bbox': list(entry['bbox'])}
                angle = _orientation(list(_lines(page)))
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
                        cells[str(cell_number)] = {
                            'text': cell_text[box],
                            'bbox': list(pymupdf.Rect(box) * inverse)}
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
    return material, tuple(associations)


def material_context(material):
    """References are source addresses, not replacements for printed identifiers."""
    tables = {ref: dict(t, rows=[dict(row, association=(list(row['association']['fields'])
                            if row['association'] else None)) for row in t['rows']])
              for ref, t in material['tables'].items()}
    lines = {}
    for ref, line in material['lines'].items():
        x0, y0, x1, y1 = line['bbox']
        if any(t['source'] == line['source'] and t['page'] == line['page']
               and t['bbox'][0] <= (x0+x1)/2 <= t['bbox'][2]
               and t['bbox'][1] <= (y0+y1)/2 <= t['bbox'][3] for t in tables.values()):
            continue
        lines[ref] = line
    return '\nSOURCE ADDRESSES (one-based rows/columns; zero-based word offsets)\n' + json.dumps(
        dict(tables=tables, lines=lines, images=material['images']),
        ensure_ascii=False, separators=(',', ':'))


def table_fields(material, table_ref, row_number, columns):
    table = material['tables'][table_ref]
    row = table['rows'][row_number - 1]
    association = row['association']
    fields = dict(association['fields']) if association else {}
    for role, column in columns.items():
        if role in fields:
            raise ValueError('The association owner already supplies this field')
        if not 1 <= column <= len(row['cells']):
            raise ValueError('Column outside the source table')
        cell = row['cells'][column - 1]
        if cell is None:
            raise ValueError('No unique physical cell at the selected source position')
        fields[role] = dict(table['cells'][cell], source=table['source'], page=table['page'],
                            locator=f'{table_ref}/cell:{cell}')
    return fields, association


def native_span(material, span):
    line = material['lines'][span['line_ref']]
    start, end = span['first_word'], span['end_word']
    if not 0 <= start < end <= len(line['words']):
        raise ValueError('Word selection outside its source line')
    return dict(line, text=' '.join(line['words'][start:end]),
                locator=f"{span['line_ref']}/words:{start}:{end}")

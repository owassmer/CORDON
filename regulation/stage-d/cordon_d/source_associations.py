"""Offline reading of printed plant-to-report associations in administrative annexes.

This reads ruled native-text tables, not the act's legal effect. Headerless tables
need an uninterrupted annex, consecutive printed folios and the same ruled column
boundaries. Those checks support layout continuity; they do not reconcile sources.
"""
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from tempfile import NamedTemporaryFile

from .store import blob_path, file_digest, store_root


HEADINGS = {
    'IDCAMPIONE': 'plant_id', 'RAPPORTOPROVA': 'report_reference',
    'RAPPORTODIPROVA': 'report_reference', 'DATARAPPORTOPROVA': 'report_date',
    'DATARAPPORTODIPROVA': 'report_date', 'SPECIE': 'host',
    'LONGITUDINE': 'longitude', 'LATITUDINE': 'latitude', 'AGRO': 'municipality',
    'COMUNE': 'municipality', 'ZONA': 'zone', 'FOGLIO': 'sheet', 'PARTICELLA': 'parcel',
}
REQUIRED = {'plant_id', 'report_reference', 'report_date'}
PRIVATE_HEADINGS = {'PROPRIETARIO', 'PROPRIETARI', 'PROPRIETARIO/CONDUTTORE'}
ANNEX = re.compile(r'^ALLEGATO\s+([\d]+(?:\s*/\s*[A-Z])?)$', re.I)
IMPLEMENTATION = Path(__file__).read_bytes()


@dataclass
class AssociationReading:
    source_sha256: str
    reader_version: str
    page_count: int
    rows: list[dict]
    issues: list[dict]
    scope: str = ('Printed native ruled association tables only; no whole-document '
                  'coverage, source reconciliation or administrative-effect assertion.')


def _key(text):
    return ''.join((text or '').split()).upper()


def _lines(page):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            text = ''.join(span['text'] for span in line['spans']).strip()
            if text:
                yield text, line['bbox'], line['dir']


def _orientation(lines):
    """The dominant embedded writing direction, not image-content inference."""
    weights = {}
    directions = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}
    for text, _, direction in lines:
        rounded = tuple(round(v) for v in direction)
        if rounded in directions and all(abs(a-b) < .001 for a, b in zip(direction, rounded)):
            angle = directions[rounded]
            weights[angle] = weights.get(angle, 0) + len(text)
    ranked = sorted(weights, key=weights.get, reverse=True)
    if not ranked or (len(ranked) > 1 and weights[ranked[0]] == weights[ranked[1]]):
        return None
    return ranked[0]


def _header(values, *, required=REQUIRED):
    matches = []
    for i, row in enumerate(values):
        roles = {c: HEADINGS[_key(text)] for c, text in enumerate(row) if _key(text) in HEADINGS}
        if required <= set(roles.values()) and len(roles) == len(set(roles.values())):
            matches.append((i, roles))
    return matches


def _boundaries(table):
    # A fully partitioned row, including ignored columns, prevents a merged caption
    # from masquerading as the grid. Coordinates stay in PDF points.
    for row in table.rows:
        cells = row.cells
        if cells and all(c is not None for c in cells):
            edges = [cells[0][0], *(c[2] for c in cells)]
            if all(abs(a[2] - b[0]) <= 1 for a, b in zip(cells, cells[1:])):
                return [x - edges[0] for x in edges]
    return None


def _same_grid(left, right):
    # One PDF point is a drawing-coordinate tolerance, never a spatial identity rule.
    return (left is not None and right is not None and len(left) == len(right)
            and all(abs(a-b) <= 1 for a, b in zip(left, right)))


def _folio(lines, bbox):
    choices = [(text, box) for text, box, direction in lines
               if text.isdecimal() and direction == (1.0, 0.0)
               and box[1] > bbox[3] and bbox[0] <= (box[0]+box[2])/2 <= bbox[2]]
    return choices[0] if len(choices) == 1 else None


def _bbox(box, inverse):
    import pymupdf
    return list(pymupdf.Rect(box) * inverse) if box is not None else None


def _shared_cells(table, values):
    """Locate omitted logical cells within the table's original drawn cells."""
    printed = {tuple(box): values[r][c]
               for r, row in enumerate(table.rows)
               for c, box in enumerate(row.cells) if box is not None}
    xs = sorted({box[i] for box in printed for i in (0, 2)})
    ys = sorted({box[i] for box in printed for i in (1, 3)})
    if len(xs) != table.col_count + 1 or len(ys) != table.row_count + 1:
        return {}
    resolved = {}
    for r, row in enumerate(table.rows):
        for c, box in enumerate(row.cells):
            if box is not None:
                continue
            x, y = (xs[c] + xs[c + 1]) / 2, (ys[r] + ys[r + 1]) / 2
            covering = [b for b in printed if b[0] < x < b[2] and b[1] < y < b[3]]
            if len(covering) == 1:
                box, = covering
                resolved[r, c] = (printed[box], box)
    return resolved


def _read_pdf(digest, version, path):
    import pymupdf
    result = AssociationReading(digest, version, 0, [], [])
    active_annex = None
    previous = None
    with pymupdf.open(path) as document:
        result.page_count = len(document)
        for index, page in enumerate(document):
            number = index + 1
            original_lines = list(_lines(page))
            angle = _orientation(original_lines)
            if angle is None:
                result.issues.append({'page': number, 'cause': 'native writing orientation unavailable or ambiguous; association presence not assessed'})
                previous = None
                continue
            # Work only on the in-memory PDF. Cached source coordinates are mapped
            # back to the untouched source page's unrotated coordinate system.
            page.set_rotation(angle)
            forward = page.rotation_matrix
            page.remove_rotation()
            inverse = ~forward
            lines = list(_lines(page))
            markers = [(ANNEX.fullmatch(text), box) for text, box, _ in lines]
            markers = [(m.group(1).replace(' ', '').upper(), box) for m, box in markers if m]
            if len(markers) > 1:
                active_annex = None
                previous = None
            elif markers:
                active_annex = {'text': markers[0][0], 'page': number,
                                'bbox': _bbox(markers[0][1], inverse)}
                previous = None
            tables = page.find_tables(strategy='lines_strict').tables
            candidates = []
            for table_index, table in enumerate(tables, 1):
                values = table.extract()
                shared = _shared_cells(table, values)
                headers = _header(values)
                grid = _boundaries(table)
                folio = _folio(lines, table.bbox)
                basis = None
                if len(headers) == 1:
                    start, roles = headers[0]
                    unread_columns = [text for column, text in enumerate(values[start])
                                      if column not in roles and _key(text) not in PRIVATE_HEADINGS]
                    source_header = {role: {'text': values[start][column], 'page': number,
                                           'table': table_index, 'row': start + 1, 'column': column + 1,
                                           'bbox': _bbox(table.rows[start].cells[column], inverse)}
                                     for column, role in roles.items()}
                    start += 1
                    basis = {'kind': 'printed_header', 'headers': source_header,
                             'annex': active_annex, 'unread_columns': unread_columns}
                elif not headers and previous and active_annex and len(tables) == 1:
                    if (previous['page'] + 1 == number and previous['annex'] == active_annex
                            and previous['folio'] is not None and folio is not None
                            and int(folio[0]) == int(previous['folio'][0]) + 1
                            and _same_grid(previous['grid'], grid)):
                        roles, start = previous['roles'], 0
                        source_header = previous['headers']
                        unread_columns = previous['unread_columns']
                        basis = {'kind': 'annex_continuation', 'headers': source_header,
                                 'annex': active_annex, 'previous_page': previous['page'],
                                 'printed_folios': [previous['folio'][0], folio[0]],
                                 'folio_bbox': _bbox(folio[1], inverse),
                                 'column_boundaries_pdf_points': grid,
                                 'column_tolerance_pdf_points': 1, 'unread_columns': unread_columns}
                if basis is None:
                    result.issues.append({'page': number, 'table': table_index,
                                          'bbox': _bbox(table.bbox, inverse),
                                          'cause': 'no unique printed association header or verified annex continuation; table not interpreted'})
                    continue
                row_indices = []
                for r in range(start, len(values)):
                    row = values[r]
                    fields = {}
                    for c, role in roles.items():
                        text, box = shared.get((r, c), (row[c], table.rows[r].cells[c]))
                        fields[role] = {'text': text, 'column': c + 1, 'bbox': _bbox(box, inverse)}
                        if (r, c) in shared:
                            fields[role]['derivation'] = 'shared printed cell covers this row and column'
                    issues = []
                    if unread_columns:
                        issues.append({'cause': 'additional source columns outside this association reading',
                                       'headings': unread_columns})
                    missing = sorted(role for role in REQUIRED if not (fields[role]['text'] or '').strip())
                    if missing:
                        issues.append({'cause': 'association identity fields blank or merged; no fill-down', 'fields': missing})
                    if r == start and missing and basis['kind'] == 'annex_continuation' and previous['last_row'] is not None:
                        preceding = result.rows[previous['last_row']]
                        populated = {role for role, cell in fields.items() if (cell['text'] or '').strip()}
                        # The report reference can itself wrap across the page.
                        # A printed plant ID or date still starts a separate row.
                        if ({'plant_id', 'report_date'} <= set(missing) and populated
                                and all((preceding['fields'][role]['text'] or '').strip()
                                        for role in REQUIRED | populated)
                                and not preceding['issues'] and not unread_columns):
                            # Same annex, successive physical/printed pages and
                            # identical columns establish this split row's context.
                            for role in populated:
                                prior, fragment = preceding['fields'][role], fields[role]
                                parts = prior.setdefault('parts', [dict(prior,
                                    page=preceding['page'], table=preceding['table'], row=preceding['row'])])
                                parts.append(dict(fragment, page=number, table=table_index, row=r + 1))
                                prior['text'] = prior['text'].rstrip() + '\n' + fragment['text'].lstrip()
                                prior['derivation'] = 'cell continues across verified annex page boundary'
                            preceding.setdefault('continuations', []).append({
                                'page': number, 'table': table_index, 'row': r + 1, 'basis': basis})
                            continue
                        preceding['issues'].append({
                            'cause': 'following page begins with a fragment lacking association identity; row continuation unresolved',
                            'page': number, 'table': table_index, 'row': r + 1})
                    result.rows.append({'source_sha256': digest, 'page': number,
                                        'table': table_index, 'row': r + 1,
                                        'fields': fields, 'basis': basis, 'issues': issues})
                    row_indices.append(len(result.rows) - 1)
                candidates.append({'page': number, 'annex': active_annex, 'grid': grid,
                                   'folio': folio, 'roles': roles, 'headers': source_header,
                                   'unread_columns': unread_columns,
                                   'last_row': row_indices[-1] if row_indices else None})
            previous = candidates[0] if len(candidates) == 1 and len(tables) == 1 else None
    return result


def reader_version():
    import pymupdf
    return sha256(IMPLEMENTATION + pymupdf.VersionBind.encode()).hexdigest()[:20]


def read_associations(source_sha256: str, store: Path) -> AssociationReading:
    """Read a retained source locally, reusing its regenerable native-table cache."""
    revision = reader_version()
    source = blob_path(Path(store), source_sha256)
    if not source.exists():
        return AssociationReading(source_sha256, revision, 0, [], [{'cause': 'source blob unavailable'}])
    cache = Path(store) / 'derived' / 'source_associations' / revision / f'{source_sha256}.json'
    if cache.exists():
        return AssociationReading(**json.loads(cache.read_text()))
    if file_digest(source) != source_sha256:
        raise ValueError('Association source bytes differ from their content address')
    result = _read_pdf(source_sha256, revision, source)
    cache.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode='w', dir=cache.parent, suffix='.tmp', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(asdict(result), stream, ensure_ascii=False, indent=1)
        stream.write('\n')
    try:
        temporary.replace(cache)
    finally:
        temporary.unlink(missing_ok=True)
    return result


def associations(source_root: Path, store: Path | None = None, *, known_through: datetime):
    """Distinct successful captures available by the explicit knowledge cutoff."""
    if not isinstance(known_through, datetime) or known_through.tzinfo is None or known_through.utcoffset() is None:
        raise ValueError('A knowledge cutoff must be a timezone-aware instant')
    root = Path(source_root)
    store = Path(store) if store is not None else store_root(root)
    records = json.loads((root / 'records.json').read_text())
    admitted = set()
    for record in records:
        captured = datetime.fromisoformat(record['captured_at'])
        if captured.tzinfo is None or captured.utcoffset() is None:
            raise ValueError('Association capture has no timezone')
        if record.get('sha256') and (known_through is None or captured <= known_through):
            admitted.add(record['sha256'])
    for digest in sorted(admitted):
        yield read_associations(digest, store)

#!/usr/bin/env python3
"""Read the cadastral annex tables of every held area act, and pin the readings.

One call per page of each act document that could carry an annex table. The model is
shown the page and the native table cells the document encodes, each under an ID. It
decides the relationships — which caption governs which rows, which cell is a row's
scope — and points at the native cell; this script copies that cell's characters. The
model selects existing characters where they faithfully carry the value. Where a value
is printed but no native cell carries it, the model transcribes it and says so.

An accepted reading is a pinned artifact, not a cache: the response, its configuration
and the cells it was shown are kept under `corpus/sources/areas/readings/<sha256>/`, and
`cordon_d.areas` reads those files. Re-running a model is not replaying an accepted
reading, so `reader_version()` does not move when a model moves.

    scripts/read_annexes.py                 # inventory only: which pages will be read, and why not
    scripts/read_annexes.py --execute       # read every candidate page not yet pinned
    scripts/read_annexes.py --execute --only 2024-00158
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPOSITORY / 'regulation/stage-d'), str(REPOSITORY / 'regulation/stage-c')]
from cordon_d.store import store_root, blob_path  # noqa: E402

READINGS = REPOSITORY / 'corpus/sources/areas/readings'
ACTS = REPOSITORY / 'corpus/sources/areas/acts.json'
MODEL, EFFORT, DPI, TIMEOUT_S = 'claude-sonnet-5', 'medium', 200, 600

PROMPT = '''This is one page of a determination of the Regione Puglia Osservatorio
Fitosanitario on Xylella fastidiosa demarcated areas. Some pages carry annex tables of
cadastral scope: a caption naming a zone (ZONA INFETTA, ZONA CUSCINETTO, ZONA DI
CONTENIMENTO, FOCOLAIO, AREA DELIMITATA ... ) printed inside the table's first row or
above it; columns PROVINCIA, COMUNE and a sheets column (FOGLI DI MAPPA CATASTALI or
similar); scope cells such as "da 15 a 32; 34*, 35" or "INTERO TERRITORIO COMUNALE" or
"PARTE TERRITORIO COMUNALE", sometimes with particelle. Maps and prose are not tables.

Read the page image at the path given below. You are also given the native cells the
PDF encodes for this page, each with an ID, its table, its row and its column, and its
bounding box in page points. They are proposals: the PDF's own table detection can miss
a table or split one, so account for every table you can SEE, not only the ones listed.

Return every annex table on the page. For each table: the caption exactly as printed,
whether it is printed inside the table or above it, any qualification the caption or
the table states (a measures regime, a distance, a province restriction), the column
headings as printed, and its rows. For each row give provincia, comune and scope. For
each of those three: {"native_cell": "<ID>"} when a listed native cell faithfully
carries the whole printed value; {"text": "<exact transcription>"} when the value is
printed but no listed cell carries it whole; null when the row leaves it blank. A value
overlapped by a document stamp or watermark must exclude that separate text: a native
cell containing both is not a faithful value, so transcribe the table's own value.
A value
drawn once spanning several rows belongs to each row it covers: repeat the same
native_cell on every row it spans. Two consecutive tables may print the same caption;
they are two tables. A blank spacer row is not a row. Do not expand ranges, do not drop
asterisks, do not normalise spelling, do not count sheets, do not decide which legal
measure applies.

Binding each caption to the rows it actually governs is the single most important thing
you are doing: rows given the wrong zone are worse than rows not read. Account for every
native table listed: represented (by which output tables), not_annex_table, or
not_recovered. Put anything consequential on the page that is not an annex table row
(a partial-parcel rule, a region named in prose but absent from the tables, a footnote)
in unattached, quoted. Put anything you cannot read with confidence in uncertain.
'''


def output_schema():
    def obj(props, required=None):
        return {'type': 'object', 'properties': props, 'additionalProperties': False,
                'required': list(props) if required is None else required}
    string, integer, nullable = {'type': 'string'}, {'type': 'integer'}, {'type': ['string', 'null']}
    cell = {'anyOf': [obj({'native_cell': string}), obj({'text': string}), {'type': 'null'}]}
    row = obj({'provincia': cell, 'comune': cell, 'scope': cell, 'note': nullable})
    table = obj({'index': integer, 'caption_verbatim': string,
                 'caption_position': {'enum': ['inside the table first row', 'above the table', 'other']},
                 'qualification_verbatim': nullable, 'column_headings_verbatim': {'type': 'array', 'items': string},
                 'rows': {'type': 'array', 'items': row}})
    accounted = obj({'native_table': string,
                     'disposition': {'enum': ['represented', 'not_annex_table', 'not_recovered']},
                     'output_tables': {'type': 'array', 'items': integer}, 'cause': nullable})
    return obj({'tables_visible': integer, 'tables': {'type': 'array', 'items': table},
                'native_tables_accounted': {'type': 'array', 'items': accounted},
                'unattached': {'type': 'array', 'items': string},
                'uncertain': {'type': 'array', 'items': string}})


def native_cells(page, number):
    cells, tables = {}, []
    for ti, table in enumerate(page.find_tables().tables, 1):
        tid = f'p{number}-t{ti}'
        tables.append({'id': tid, 'bbox': [round(v, 1) for v in table.bbox]})
        rows = table.extract()
        boxes = [getattr(r, 'cells', None) for r in getattr(table, 'rows', [])]
        for ri, row in enumerate(rows, 1):
            for ci, text in enumerate(row, 1):
                if text is None or not str(text).strip():
                    continue
                box = None
                if ri - 1 < len(boxes) and boxes[ri - 1] and ci - 1 < len(boxes[ri - 1]) and boxes[ri - 1][ci - 1]:
                    box = [round(v, 1) for v in boxes[ri - 1][ci - 1]]
                cid = f'{tid}-r{ri}-c{ci}'
                cells[cid] = {'text': str(text), 'table': tid, 'row': ri, 'column': ci, 'bbox': box}
    return tables, cells


def inventory(acts, store):
    """Every page of every held act, with whether it is read and why not."""
    import pymupdf
    pages = []
    for record in acts:
        if not record.get('sha256'):
            continue
        blob = blob_path(store, record['sha256'])
        if not blob.exists():
            pages.append({'instrument_id': record['instrument_id'], 'act_sha256': record['sha256'],
                          'page': None, 'candidate': False, 'cause': 'the act document is not held in the store'})
            continue
        with pymupdf.open(blob) as document:
            for number, page in enumerate(document, 1):
                tables = page.find_tables().tables
                pages.append({'instrument_id': record['instrument_id'], 'act_sha256': record['sha256'],
                              'page': number, 'pages_in_document': len(document), 'candidate': True,
                              'native_tables': len(tables),
                              'cause': None})
    return pages


def pinned_path(digest, number):
    return READINGS / digest / f'p{number}.json'


def read_page(digest, number, instrument_id, store, reread=False):
    """One subscription call for one page; returns the pinned record or raises."""
    import pymupdf
    target = pinned_path(digest, number)
    effort = 'high' if reread else EFFORT
    if not reread and target.exists() and json.loads(target.read_text()).get('resolved') is not None:
        return {'instrument_id': instrument_id, 'page': number, 'status': 'pinned already'}
    with pymupdf.open(blob_path(store, digest)) as document:
        page = document[number - 1]
        tables, cells = native_cells(page, number)
        png = page.get_pixmap(dpi=DPI).tobytes('png')
        native_text = page.get_text()
    schema = output_schema()
    supplied = {'page': number, 'native_tables': tables, 'native_cells': cells}
    with TemporaryDirectory(prefix='cordon-annex-') as directory:
        image = Path(directory) / f'{instrument_id}-p{number}.png'
        image.write_bytes(png)
        instruction = (PROMPT + f'\nThe page image is at {image}. Physical page {number} of the act.\n'
                       'Native tables and cells the PDF encodes for this page:\n'
                       + json.dumps(supplied, ensure_ascii=False)
                       + '\nText layer of the page, in reading order, for reference:\n' + native_text)
        request = {'provider': 'claude-code-subscription', 'model': MODEL, 'effort': effort,
                   'act_sha256': digest, 'page': number, 'prompt': instruction, 'schema': schema}
        request_id = sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        command = ['claude', '-p', '--model', MODEL, '--effort', effort,
                   '--system-prompt', ('You read one page image of a named local document and return only '
                                       'schema-conforming source facts. Use Read only on that image. Do not '
                                       'search, write, delegate, or inspect the repository.'),
                   '--disable-slash-commands', '--strict-mcp-config', '--no-chrome',
                   '--tools', 'Read', '--allowedTools', 'Read', '--permission-mode', 'dontAsk',
                   '--add-dir', directory, '--no-session-persistence', '--output-format', 'json',
                   '--json-schema', json.dumps(schema, sort_keys=True), instruction]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT_S)
    captured = datetime.now(timezone.utc).isoformat()
    try:
        envelope = json.loads(completed.stdout)
    except json.JSONDecodeError:
        envelope = None
    reading = (envelope or {}).get('structured_output')
    if completed.returncode or (envelope or {}).get('is_error') or not isinstance(reading, dict):
        failed = store / 'derived/areas/failed' / f'{digest[:12]}-p{number}-{captured[:19].replace(":", "")}.json'
        failed.parent.mkdir(parents=True, exist_ok=True)
        failed.write_text(json.dumps({'request_sha256': request_id, 'returncode': completed.returncode,
                                      'stderr': completed.stderr[-2000:], 'envelope': envelope,
                                      'captured_at': captured}, ensure_ascii=False, indent=1))
        raise RuntimeError('subscription call failed: ' + (str((envelope or {}).get('result')) or completed.stderr.strip())[:300])
    resolved, problems = resolve(reading, cells, tables)
    record = {'instrument_id': instrument_id, 'act_sha256': digest, 'page': number,
              'model': MODEL, 'effort': effort, 'dpi': DPI, 'request_sha256': request_id,
              'prompt_sha256': sha256(PROMPT.encode()).hexdigest()[:16],
              'schema_sha256': sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()[:16],
              'captured_at': captured, 'native_tables': tables, 'native_cells': cells,
              'envelope': {k: envelope.get(k) for k in ('duration_ms', 'num_turns', 'usage', 'stop_reason',
                                                        'total_cost_usd', 'session_id')},
              'reading': reading, 'resolved': resolved, 'resolution_problems': problems}
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        prior = json.loads(target.read_text())
        retained = store / 'derived/areas/responses' / f'{prior["request_sha256"]}.json'
        retained.parent.mkdir(parents=True, exist_ok=True)
        if not retained.exists():
            retained.write_bytes(target.read_bytes())
    temporary = target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=1) + '\n')
    temporary.replace(target)
    return {'instrument_id': instrument_id, 'page': number, 'status': 'pinned',
            'tables': len(reading['tables']), 'rows': sum(len(t['rows']) for t in reading['tables']),
            'problems': len(problems), 'seconds': round((envelope.get('duration_ms') or 0) / 1000)}


def resolve(reading, cells, native_tables=()):
    """Copy the characters of every selected native cell; keep transcriptions marked as such."""
    problems, tables = [], []
    indexes = [table['index'] for table in reading['tables']]
    if len(indexes) != len(set(indexes)):
        problems.append('output table indexes are not unique')
    if reading['tables_visible'] != len(indexes):
        problems.append('visible table count differs from recovered tables')
    for table in reading['tables']:
        rows = []
        for index, row in enumerate(table['rows'], 1):
            out = {}
            for field in ('provincia', 'comune', 'scope'):
                value = row.get(field)
                if value is None:
                    out[field] = None
                elif 'native_cell' in value:
                    cell = cells.get(value['native_cell'])
                    if cell is None:
                        problems.append(f'table {table["index"]} row {index} {field}: unknown native cell {value["native_cell"]}')
                        out[field] = None
                    else:
                        out[field] = {'text': cell['text'], 'copied_from': value['native_cell']}
                else:
                    out[field] = {'text': value['text'], 'transcribed': True}
            out['note'] = row.get('note')
            rows.append(out)
        tables.append({'index': table['index'], 'caption_verbatim': table['caption_verbatim'],
                       'caption_position': table['caption_position'],
                       'qualification_verbatim': table.get('qualification_verbatim'),
                       'column_headings_verbatim': table['column_headings_verbatim'], 'rows': rows})
    listed = {t['id'] for t in native_tables} | {c['table'] for c in cells.values()}
    dispositions = reading['native_tables_accounted']
    accounted = {a['native_table'] for a in dispositions}
    if len(accounted) != len(dispositions):
        problems.append('a native table is accounted for more than once')
    for missing in sorted(listed - accounted):
        problems.append(f'native table {missing} was supplied and not accounted for')
    for unknown in sorted(accounted - listed):
        problems.append(f'native table {unknown} was not supplied')
    for item in dispositions:
        if item['disposition'] == 'represented' and (
                not item['output_tables'] or not set(item['output_tables']) <= set(indexes)):
            problems.append(f'native table {item["native_table"]} names no valid representing table')
    return {'tables': tables, 'unattached': reading['unattached'], 'uncertain': reading['uncertain'],
            'native_tables_accounted': reading['native_tables_accounted'],
            'tables_visible': reading['tables_visible']}, problems


def job(args):
    digest, number, instrument_id, store, reread = args
    try:
        return read_page(digest, number, instrument_id, store, reread=reread)
    except Exception as error:  # the run continues; the page stays unpinned and says why
        return {'instrument_id': instrument_id, 'page': number, 'status': 'failed', 'cause': str(error)[:300]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--only', default='', help='substring of the instrument id')
    parser.add_argument('--page', type=int, action='append', default=[], help='physical page to read again')
    parser.add_argument('--reread', action='store_true', help='replace selected readings after a source check finds an error')
    parser.add_argument('--workers', type=int, choices=range(1, 7), default=2)
    args = parser.parse_args()
    acts = json.loads(ACTS.read_text())
    store = store_root(REPOSITORY / 'corpus/sources/areas')
    pages = inventory(acts, store)
    READINGS.mkdir(parents=True, exist_ok=True)
    (READINGS / 'INVENTORY.json').write_text(json.dumps(pages, ensure_ascii=False, indent=1) + '\n')
    candidates = [p for p in pages if p['candidate'] and args.only in p['instrument_id']
                  and (not args.page or p['page'] in args.page)]
    pending = [p for p in candidates if args.reread or not pinned_path(p['act_sha256'], p['page']).exists()]
    print(json.dumps({'documents': len({p['act_sha256'] for p in pages if p['page']}),
                      'pages': sum(1 for p in pages if p['page']), 'candidate_pages': len(candidates),
                      'pinned': len(candidates) - len(pending), 'pending': len(pending),
                      'model': MODEL, 'effort': 'high' if args.reread else EFFORT,
                      'execute': args.execute}), flush=True)
    if not args.execute:
        return
    work = [(p['act_sha256'], p['page'], p['instrument_id'], store, args.reread) for p in pending]
    failures, done, consecutive = 0, 0, 0
    source = iter(work)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = set()
        for _ in range(args.workers):
            if (item := next(source, None)) is not None:
                jobs.add(pool.submit(job, item))
        halted = False
        while jobs:
            finished, jobs = wait(jobs, return_when=FIRST_COMPLETED)
            for result in finished:
                outcome = result.result()
                done += 1
                failed = outcome['status'] == 'failed'
                failures += failed
                consecutive = consecutive + 1 if failed else 0
                halted = halted or consecutive >= 3
                print(json.dumps(dict(outcome, progress=[done, len(work)]), ensure_ascii=False), flush=True)
            if not halted:
                for _ in range(args.workers - len(jobs)):
                    if (item := next(source, None)) is not None:
                        jobs.add(pool.submit(job, item))
    print(json.dumps({'pages_attempted': done, 'failed': failures,
                      'remaining': len(work) - done + failures}), flush=True)
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()

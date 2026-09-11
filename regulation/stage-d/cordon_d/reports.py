"""Laboratory reports read from their structure, and their rows joined to observations.

A report is read from what its pages contain: a text layer where present, OCR
(Tesseract, Italian) where a page has none, with the method recorded per page.
Identity, stated counts, assays and analytes are literal strings read from the
letter. A page with a text layer is read by its printed headers; a scanned page
has none to recover, so its columns are read positionally and designate no test.
No reading turns on a file name, a year or a laboratory. A line the reader cannot
resolve is an `unread` row carrying its text; nothing is guessed. Reports supply
the laboratory's diagnosis and, where a report designates two tests, the Article
2(6) test and sample identities; they print no genome target, a few print a cycle
value as a free-text note that names neither its assay nor the run's validity,
and none is the official confirmation decision.
Relating what is read to observations belongs to `findings`, so a change there
does not invalidate a reading.
"""
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

from .store import blob_path, derived_path, write_derived

OCR_LANGUAGE = 'ita'
OCR_DPI = 200
RESULT_CLASSES = (
    (re.compile(r'non\s*determinabil', re.I), 'undetermined'),
    (re.compile(r'non\s*rilevat', re.I), 'not-detected'),
    (re.compile(r'\brilevat', re.I), 'detected'),
    (re.compile(r'\bassente\b', re.I), 'not-detected'),
    (re.compile(r'\bpresente\b', re.I), 'detected'),
    (re.compile(r'\bnegativ', re.I), 'negative'),
    (re.compile(r'\bpositiv', re.I), 'positive'),
    (re.compile(r'\bdubbi', re.I), 'doubtful'),
)
RESULT_TOKEN = re.compile(r'non\s*determinabil\w*|non\s*rilevat\w*|rilevat\w*|[Pp]ositiv\w*|[Nn]egativ\w*|[Dd]ubbi\w*', re.I)
# Counting tokens inside one table cell: a cell holding several results holds several
# rows' results, so it states none of them. `presente`/`assente` count here and only here;
# in a wrapped scanned line they are as likely to be the symptom column.
CELL_RESULT_TOKEN = re.compile(r'non\s*determinabil\w*|non\s*rilevat\w*|rilevat\w*|positiv\w*|negativ\w*|dubbi\w*|presente|assente', re.I)
ASSAY_NAMES = re.compile(r'\b(Harper|Ouyang|Francis|Dupas|Yuan|LAMP|MP0\d\s*(?:rev\.?\s*\d+)?|q[gq]?PCR|real[- ]time\s*PCR|PCR\s+in\s+tempo\s+reale|PCR\s*convenzionale|MLST)\b', re.I)
ANALYTE = re.compile(r'(Xylella\s+fastidiosa(?:\s+(?:subsp\.?|sottospecie|sub\.)\s*(pauca|multiplex|fastidiosa))?)', re.I)
# The letter's subject, tolerating the OCR substitutions seen in scanned letters ("Xy/ella", "Xy1ella").
# Used for the letter only; a result is never read tolerantly.
ANALYTE_OCR = re.compile(r'Xy[l1/|i]{1,2}e[l1/|i]{1,2}a\s+fast[il1]d[il1]osa(?:\s+(?:subsp\.?|sottospecie|sub\.)\s*(pauca|multiplex|fastidiosa))?', re.I)
SUBSPECIES = re.compile(r'\b(pauca|multiplex|fastidiosa)\b', re.I)
QUALIFIED_SUBSPECIES = re.compile(r'(?:subsp\.?|sottospecie|sub\.)\s*(pauca|multiplex|fastidiosa)', re.I)
# The labels an annex prints for its other columns; a header text carrying several of
# them is the whole header, not one column's designation.
_LABELS = re.compile(r'data\s*(?:rilev|campion|prelie|saggio|prova)|specie|comune|latitud|longitud|'
                     r'codice\s*(?:squadra|busta|pool)|sintom|operatore|\bzona\b|laboratorio', re.I)
DATE = re.compile(r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b')
CODE = re.compile(r'(?<![\d.,])(\d{5,9})(?![\d.,])')  # a date part never reaches five digits
# A sample code stands alone. Under OCR a year runs into the word after it
# (`16/03/20180lvo`) and a stray character precedes one (`L259726`); neither is a
# second sample, so neither shows that a line carries a second row.
STANDALONE_CODE = re.compile(r'(?<![\d.,A-Za-z])\d{5,9}(?![\d.,A-Za-z])')
MONTHS = {'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4, 'maggio': 5, 'giugno': 6, 'luglio': 7,
          'agosto': 8, 'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12}


def tesseract_version() -> str:
    try:
        return subprocess.run(['tesseract', '--version'], capture_output=True, text=True).stdout.split('\n')[0].strip()
    except OSError:
        return 'unavailable'


def reader_version() -> str:
    digest = sha256()
    for name in ('reports.py', 'store.py'):
        digest.update((Path(__file__).parent / name).read_bytes())
    digest.update(tesseract_version().encode())
    return digest.hexdigest()[:12]


@dataclass(frozen=True)
class Result:
    column: str          # the printed header, or 'letter' when the letter states the result for every listed sample
    assay: str | None    # the test as the column designates it, verbatim; None where the column designates none
    analyte: str | None  # analyte the column or letter states
    text: str            # literal string read
    kind: str            # detected / not-detected / positive / negative / doubtful / undetermined / unread


@dataclass(frozen=True)
class Row:
    page: int
    method: str
    reference: str | None
    reference_kind: str | None   # 'sample' (the publisher's sample reference), 'daily' (a daily counter), 'in-cell'
    sampling_date: date | None
    species: str | None
    latitude: str | None
    longitude: str | None
    comune: str | None
    results: tuple[Result, ...]
    result_date: date | None
    text: str
    unread: bool


@dataclass(frozen=True)
class Report:
    sha256: str
    pages: int
    page_methods: tuple[str, ...]
    identity: str | None        # printed protocol or rapporto number, literal
    laboratory: str | None      # printed letterhead or signatory line, literal
    report_date: date | None
    delivery_date: date | None
    stated_sample_count: int | None
    assays: tuple[str, ...]     # assay names stated anywhere in the letter
    analytes: tuple[str, ...]   # analytes stated anywhere in the letter
    positives_only: bool        # the letter says it lists positive samples only
    rows: tuple[Row, ...]
    ocr_engine: str


# --- literal reading helpers ----------------------------------------------------

def _safe_date(parts):
    try:
        return date(int(parts[2]), int(parts[1]), int(parts[0]))
    except (ValueError, IndexError, TypeError):
        return None


def _date(text):
    m = DATE.search(text or '')
    return _safe_date(m.groups()) if m else None


def _italian_date(text):
    if not text:
        return None
    d = _date(text)
    if d:
        return d
    m = re.search(r'(\d{1,2})[\s_]+([A-Za-zà]+)[\s_]+(\d{4})', text)
    if m and m.group(2).lower() in MONTHS:
        return _safe_date((m.group(1), MONTHS[m.group(2).lower()], m.group(3)))
    return None


def _classify(text: str) -> str:
    for pattern, kind in RESULT_CLASSES:
        if pattern.search(text or ''):
            return kind
    return 'unread'


def _clean(text: str) -> str:
    return re.sub(r'[|\[\]_]+', ' ', text).strip()


OCR_RETRY_DPI = 300


def _row_lines(text: str) -> int:
    return sum(1 for line in text.split('\n') if CODE.search(line) and DATE.search(line))


def page_texts(document):
    """(text, method) per page; OCR only where the page has no text layer.

    A scanned page is read at OCR_DPI; when that pass recovers almost no
    code-and-date lines, the page is read again at OCR_RETRY_DPI and the pass
    recovering more rows is kept, with its resolution recorded as the method.
    """
    out = []
    for page in document:
        text = page.get_text()
        if len(text.strip()) >= 40:
            out.append((text, 'text-layer'))
            continue
        passes = []
        for dpi in (OCR_DPI, OCR_RETRY_DPI):
            textpage = page.get_textpage_ocr(language=OCR_LANGUAGE, dpi=dpi, full=True)
            ocr = page.get_text(textpage=textpage)
            passes.append((_row_lines(ocr), ocr, f'ocr:{OCR_LANGUAGE}:{dpi}dpi'))
            if passes[0][0] >= 3:
                break
        rows, ocr, method = max(passes, key=lambda item: item[0])
        out.append((ocr, method))
    return out


def _letter_facts(text: str) -> dict:
    facts: dict = {}
    # A report number may carry a letter prefix of its own (`N. XF 015/2024`); taking only
    # the digits would fall through to the protocol register, a different number. A text
    # layer also breaks the number across lines (`XF 0 1 9 / 202 4`), so the window that
    # follows the phrase is closed up between digits before the number is read.
    phrase = re.search(r'Rapporto\s+di\s+prova(?:\s*/\s*TEST\s+REPORT)?\s*:?\s*(?:N[°.]?|n[°.]?)?\s*', text, re.I)
    if phrase:
        window = re.sub(r'(?<=[\d_])\s+(?=[\d/_])|(?<=[/_])\s+(?=\d)|(?<=\w)\s+(?=/\s*\d)',
                        '', text[phrase.end():phrase.end() + 60])
        m = re.match(r'((?:[A-Z]{1,3}\s*)?[0-9]+[A-Za-z_]*(?:\s*/\s*[0-9]{2,4})?)', window)
        if m:
            printed = re.sub(r'\s*/\s*', '/', re.sub(r'\s+', ' ', m.group(1))).strip().rstrip('_')
            facts['identity'] = 'Rapporto di prova ' + printed
    m = re.search(r'Prot\.?\s*(?:Selge|SELGE)?\s*(?:n\.?)?\s*([0-9]+\s*/\s*[0-9]{4})', text, re.I)
    if m and 'identity' not in facts:
        facts['identity'] = 'Prot. Selge ' + re.sub(r'\s+', '', m.group(1))
    m = re.search(r'(?:consegnat\w*|raccolt\w*)[^.\n]{0,80}?(?:in\s+data\s+|il\s+)(\d{1,2}[\s_/]+(?:\d{1,2}|[A-Za-zà]+)[\s_/]+\d{4})', text, re.I)
    if m:
        facts['delivery_text'] = m.group(1)
    # The letter states its own sample count as `n. 64 campioni` or `su 64 campioni`.
    m = re.search(r'(?:n\.?|\bsu)\s*(\d{1,4})\s+campion', text, re.I)
    facts['stated_sample_count'] = int(m.group(1)) if m else None
    facts['assays'] = tuple(sorted({re.sub(r'\s+', ' ', a).strip() for a in ASSAY_NAMES.findall(text)}))
    analytes = {re.sub(r'\s+', ' ', a[0]).strip() for a in ANALYTE.findall(text)}
    if not analytes:
        analytes = {'Xylella fastidiosa' + (f' subsp. {m.group(1).lower()}' if m.group(1) else '') for m in ANALYTE_OCR.finditer(text)}
    facts['analytes'] = tuple(sorted(analytes))
    head = '\n'.join(text.split('\n')[:6])
    facts['positives_only'] = bool(re.search(r'\bPositivi\b', head) or re.search(r'risultat\w*\s+POSITIV|campioni\s+positivi', text, re.I))
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    facts['laboratory'] = next((line for line in lines if re.match(r'(Laboratorio|Istituto|CNR|IAMB|CIHEAM|Universit|Centro di Ricerca|Dipartimento\s+di)', line)
                                and not re.search(r'da parte|consegnat|richiest', line, re.I)), None)
    m = re.search(r'(?:Bari|Valenzano|Foggia|Lecce|Locorotondo)[,\s]+(\d{1,2}/\d{1,2}/\d{4})', text) or re.search(r'Data\s+emissione\s+(\d{1,2}/\d{1,2}/\d{4})', text, re.I)
    facts['report_date'] = _date(m.group(1)) if m else None
    return facts


# --- table reading ----------------------------------------------------------------

def _header_role(header: str):
    """The role of a merged header, judged on its last segment first: the sub-column
    names the fact, the spanning header above it names the group."""
    segments = [s.strip() for s in (header or '').split(' / ') if s.strip()]
    for candidate in ([segments[-1]] if len(segments) > 1 else []) + [' '.join(segments)]:
        role = _segment_role(candidate)
        if role:
            return role
    return None


def _segment_role(header: str):
    h = (header or '').lower().replace('\n', ' ').strip()
    if re.search(r'id\s*giornal', h):
        return 'daily-id'
    # The sample reference the monitoring publisher uses outranks the laboratory's own code.
    if re.search(r'codice\s*committen|^id\b|\bid\s*campione', h):  # 'committen' tolerates a wrapped header
        return 'reference'
    if re.search(r'codice\s*univoco|^campione$|codice\s*campione', h) and 'pool' not in h and 'accett' not in h:
        return 'reference-secondary'
    if re.search(r'dati\s*identificativi', h):
        return 'identifying-text'
    if re.match(r'data\b', h):
        return 'sampling_date' if re.search(r'rilev|campion|prelie|ricev', h) else 'result_date'
    # A symptom column records what the surveyor saw, not what the laboratory found; naming
    # it keeps a `Presente` from being read as a result when a header spans beside it.
    if re.search(r'sintom', h):
        return 'symptom'
    if re.search(r'esito|risultat|analisi\s*(diagnost|molecolar)', h):
        return 'result'
    if re.search(r'(?<!sotto)specie', h):
        return 'species'
    if 'latitud' in h:
        return 'latitude'
    if 'longitud' in h:
        return 'longitude'
    if 'comune' in h:
        return 'comune'
    return None


def _is_data(row) -> bool:
    texts = [str(c or '') for c in row]
    return (any(CODE.search(t) for t in texts) and any(DATE.search(t) for t in texts)) or any(
        RESULT_TOKEN.search(t) or re.search(r'\b(presente|assente)\b', t, re.I) for t in texts)


def _merged_header(cells):
    """Header rows are the leading rows without a code and a date; a header spans rightward
    into empty cells only under the same parent header. Returns (header texts, data rows)."""
    header_rows = []
    for row in cells:
        if _is_data(row):
            break
        header_rows.append([str(c).strip() if c else None for c in row])
    if not header_rows:
        return None, []
    width = max(len(r) for r in cells)
    # A column no header row names at all has no header, so nothing spans into it: the
    # cell beside a header may be an unheaded data column, as a symptom column is.
    named = [any(k < len(row) and row[k] for row in header_rows) for k in range(width)]
    filled = []
    for k, row in enumerate(header_rows):
        row = row + [None] * (width - len(row))
        parent = filled[k - 1] if k else [None] * width
        out = list(row)
        for j in range(1, width):
            # Below the top row a header also spans only under a parent that spans with it.
            if out[j] is None and out[j - 1] is not None and named[j] and parent[j] == parent[j - 1]:
                out[j] = out[j - 1]
        filled.append(out)
    header = [' / '.join(t for t in (r[j] for r in filled) if t) for j in range(width)]
    return header, cells[len(header_rows):]


def _transposed(cells):
    """A table whose first column holds the headers and whose columns are samples."""
    if len(cells) < 2 or len(cells[0]) < 2:
        return None
    first = str(cells[0][0] or '')
    others = [str(c or '') for c in cells[0][1:]]
    if _header_role(first) == 'reference' and others and all(CODE.fullmatch(o.strip()) for o in others if o.strip()):
        width = max(len(r) for r in cells)
        return [[(cells[i][j] if j < len(cells[i]) else None) for i in range(len(cells))] for j in range(width)]
    return None


def _designation(header, value):
    """The test as this column designates it, verbatim.

    Two columns of one report are two tests when the laboratory designates them
    differently ("Esito qPCR 2010" beside "Esito qPCR 2006"); the assay name they
    share is a family, not an identity, and never stands in for one. A column that
    designates no test carries none: the letter's own assay names stay on the report
    (`Report.assays`), which is where a column-less annex states them.
    """
    match = ASSAY_NAMES.search(header) or ASSAY_NAMES.search(value)
    if match is None or match.string is not header:
        return None
    segments = [s.strip() for s in header.split(' / ') if s.strip()]
    printed = next((s for s in reversed(segments) if ASSAY_NAMES.search(s)), header)
    # A header with no separable segments states every column's label at once and so
    # designates no single column's test.
    if len(segments) == 1 and sum(1 for s in _LABELS.findall(printed)) > 1:
        return None
    return re.sub(r'\s+', ' ', printed)


def _result(header, value, letter_assays, letter_analytes):
    assay = ASSAY_NAMES.search(header) or ASSAY_NAMES.search(value)
    # A sub-column named for a subspecies states that column's analyte; the spanning header
    # above it names the family assay, not the analyte.
    tail = header[assay.end():] if assay and assay.string is header else ''
    # `subsp. multiplex` names the subspecies; the `fastidiosa` of the species name does not.
    subspecies = QUALIFIED_SUBSPECIES.search(tail) or SUBSPECIES.search(tail)
    analyte = ANALYTE.search(header)
    stated = (f'Xylella fastidiosa subsp. {subspecies.group(1).lower()}' if subspecies else
              analyte.group(1) if analyte else
              letter_analytes[0] if len(letter_analytes) == 1 else None)
    # A result cell carrying more than one result is the collapsed cell of several rows;
    # which result belongs to this row is not stated, so the row states none.
    kind = 'unread' if len(CELL_RESULT_TOKEN.findall(value)) > 1 else _classify(value)
    return Result(header.replace('\n', ' '), _designation(header, value), stated, value, kind)


def _table_rows(page_number, method, table, letter, inherited=None):
    """Rows of one table; a table that starts with data continues the previous table's header."""
    cells = table.extract()
    if not cells:
        return [], inherited
    transposed = _transposed(cells)
    if transposed:
        cells = transposed
    header, data = _merged_header(cells)
    if header is None:
        if inherited is None or len(inherited) != max(len(r) for r in cells):
            return [], inherited
        header, data = inherited, cells
    roles = [_header_role(h) for h in header]
    if 'reference' not in roles:
        for fallback in ('reference-secondary', 'daily-id', 'identifying-text'):
            if fallback in roles:
                roles = ['reference' if r == fallback else r for r in roles]
                reference_kind = {'reference-secondary': 'sample', 'daily-id': 'daily', 'identifying-text': 'in-cell'}[fallback]
                break
        else:
            return [], inherited
    else:
        reference_kind = 'sample'
    letter_result = 'result' not in roles and letter['positives_only']
    if 'result' not in roles and not letter_result:
        return [], inherited
    out = []
    for values in data:
        values = [str(v or '').strip() for v in values]
        if not any(values):
            continue
        fields: dict = {'results': []}
        for role, h, v in zip(roles, header, values):
            if role == 'result':
                fields['results'].append(_result(h, v, letter['assays'], letter['analytes']))
            elif role and role not in fields:
                fields[role] = v
        if letter_result:
            fields['results'].append(Result('letter', None,
                                            letter['analytes'][0] if len(letter['analytes']) == 1 else None,
                                            'Positivi', 'positive'))
        ref = fields.get('reference') or ''
        code = CODE.search(ref) if reference_kind != 'daily' else re.search(r'\d+', ref)
        results = tuple(fields['results'])
        unread = code is None or not results or all(r.kind == 'unread' for r in results)
        out.append(Row(page_number, method, code.group(0) if code else None, reference_kind if code else None,
                       _date(fields.get('sampling_date')), fields.get('species') or None, fields.get('latitude') or None,
                       fields.get('longitude') or None, fields.get('comune') or None, results,
                       _date(fields.get('result_date')), ' | '.join(values)[:400], unread))
    return out, header


def _flat_rows(page_number, method, text, letter):
    """A table whose text layer is one cell per line, headed by the sample id and its date.

    A row starts at a line that is a code whose next line is a date, as the header
    (`Id`, `Data rilevamento`, ...) announces; the row's other cells follow in order.
    """
    lines = [l.strip() for l in text.split('\n')]
    lines = [l for l in lines if l]
    anchor = next((i for i, l in enumerate(lines) if re.fullmatch(r'Id', l)), None)
    if anchor is None:
        return []
    starts = [i for i in range(anchor + 1, len(lines) - 1) if CODE.fullmatch(lines[i]) and DATE.match(lines[i + 1])]
    if not starts:
        return []
    header_text = ' '.join(lines[anchor:starts[0]])
    if not re.search(r'Data\s*rilev', header_text, re.I):
        return []
    # A flat table prints one cell per line, so its columns are positional and designate
    # no test; the letter's assays stay on the report.
    analyte = letter['analytes'][0] if len(letter['analytes']) == 1 else None
    out = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        cells = lines[start:end]
        body = ' | '.join(cells)
        dates = DATE.findall(body)
        hits = [m.group(0) for m in RESULT_TOKEN.finditer(body)]
        results = tuple(Result('flat column', None, analyte, t, _classify(t)) for t in hits)
        species = next((c for c in cells if re.search(r'olea|olivo|prunus|mandorlo|oleandro|vite|nerium|polygala|rosmarin', c, re.I)), None)
        out.append(Row(page_number, method, cells[0], 'sample', _safe_date(dates[0]) if dates else None, species,
                       None, None, None, results, _safe_date(dates[-1]) if len(dates) > 1 else None, body[:400], not results))
    return out


def _line_rows(page_number, method, text, letter):
    """Rows from a scanned annex: a row starts at a line carrying a sample code and continues
    over following lines that carry no code, as a scanned table row wraps under OCR; a code
    that follows a result date on the same line starts the next row.

    A scanned annex prints no column headers this reader can recover, so its result
    columns are positional and designate no test; the letter's assays stay on the
    report. One annex row prints one sample code and at most a sampling and a result
    date, so a line carrying more than that has absorbed a neighbour whose own code
    OCR lost: which result belongs to this sample is not stated, and the row states
    none while keeping its text.
    """
    buffers: list[str] = []
    for raw in text.split('\n'):
        line = _clean(raw)
        if not line:
            continue
        pieces = []
        last = 0
        for m in CODE.finditer(line):
            if m.start() > last and DATE.search(line[last:m.start()]) and pieces is not None and line[last:m.start()].strip():
                pieces.append(line[last:m.start()].strip())
                last = m.start()
        pieces.append(line[last:].strip())
        for piece in pieces:
            if CODE.search(piece):
                buffers.append(piece)
            elif buffers and re.search(r'positiv|negativ|rilevat|determinabil|dubbi|\d{1,2}/\d{1,2}/\d{4}|[A-Za-zà]{3,}', piece, re.I):
                buffers[-1] += ' ' + piece
    analyte = letter['analytes'][0] if len(letter['analytes']) == 1 else None
    out = []
    for line in buffers:
        dates = DATE.findall(line)
        hits = [m.group(0) for m in RESULT_TOKEN.finditer(line)]
        # A number with neither a date nor a result beside it is a postal code or a protocol
        # number in the letter, not a sample row.
        if len(line) < 20 or not (dates or hits):
            continue
        code = CODE.search(line)
        absorbed = len(STANDALONE_CODE.findall(line)) > 1 or len(dates) > 2
        results = () if absorbed else tuple(
            Result(f'column {i + 1}', None, analyte, t, _classify(t)) for i, t in enumerate(hits))
        species = re.search(r'\b(olivo|oleandro|mandorlo|vite|ciliegio|prunus|olea|nerium|rosmarino|polygala|lavand\w+|mirto|acacia|quercus)[^|0-9]{0,30}', line, re.I)
        out.append(Row(page_number, method, code.group(1), 'sample', _safe_date(dates[0]) if dates else None,
                       species.group(0).strip() if species else None, None, None, None, results,
                       _safe_date(dates[-1]) if len(dates) > 1 else None, line[:400], not results))
    return out


def report(digest: str, store: Path) -> Report:
    import pymupdf
    path = blob_path(store, digest)
    with pymupdf.open(path) as document:
        texts = page_texts(document)
        letter = _letter_facts(texts[0][0] if texts else '')
        rows: list[Row] = []
        inherited = None
        for number, (page, (text, method)) in enumerate(zip(document, texts), 1):
            table_rows: list[Row] = []
            if method == 'text-layer':
                for table in page.find_tables().tables:
                    found, inherited = _table_rows(number, method, table, letter, inherited)
                    table_rows.extend(found)
                if not table_rows:
                    table_rows = _flat_rows(number, method, text, letter)
            elif not table_rows:
                table_rows = _line_rows(number, method, text, letter)
            rows.extend(table_rows)
    return Report(digest, len(texts), tuple(m for _, m in texts), letter.get('identity'), letter.get('laboratory'),
                  letter.get('report_date'), _italian_date(letter.get('delivery_text')), letter.get('stated_sample_count'),
                  letter['assays'], letter['analytes'], letter['positives_only'], tuple(rows), tesseract_version())


# --- derived layer ------------------------------------------------------------------

def _ensure_derived(store: Path, digest: str, version: str) -> Path:
    target = derived_path(store, 'reports', digest, version)
    if not target.exists():
        import pyarrow
        payload = asdict(report(digest, store))
        write_derived(target, pyarrow.table({'report': [json.dumps(payload, ensure_ascii=False, default=str)]}))
        for stale in target.parent.glob(f'{digest}-*.parquet'):
            if stale != target:
                stale.unlink()
    return target


def _from_json(payload: dict) -> Report:
    def d(v):
        return date.fromisoformat(v) if v else None
    rows = tuple(Row(r['page'], r['method'], r['reference'], r['reference_kind'], d(r['sampling_date']), r['species'],
                     r['latitude'], r['longitude'], r['comune'], tuple(Result(**x) for x in r['results']),
                     d(r['result_date']), r['text'], r['unread'])
                 for r in payload['rows'])
    return Report(payload['sha256'], payload['pages'], tuple(payload['page_methods']), payload['identity'], payload['laboratory'],
                  d(payload['report_date']), d(payload['delivery_date']), payload['stated_sample_count'],
                  tuple(payload['assays']), tuple(payload['analytes']), payload['positives_only'], rows, payload['ocr_engine'])


def reports(root: Path, store: Path):
    """Every acquired report, read once per reader version; failed acquisitions are yielded as records."""
    import pyarrow.parquet as parquet
    version = reader_version()
    records = json.loads((root / 'records.json').read_text())
    seen = set()
    for record in records:
        digest = record.get('sha256')
        if not digest:
            yield record['url'], None, record
            continue
        if digest in seen:
            yield record['url'], digest, record
            continue
        seen.add(digest)
        table = parquet.read_table(_ensure_derived(store, digest, version))
        yield record['url'], _from_json(json.loads(table.column('report')[0].as_py())), record

"""Laboratory report rows joined to the observations whose routes name them.

The candidates for a report's rows are only the observations that reference that
report; within them the match is by the sample reference the laboratory prints
and, where the report prints it, the sampling day. A row matching none or several
candidates is exposed, never matched. Agreement between a published label and a
report is stated only at the level the report states, and is never resolved.

Reading a report belongs to `reports`; this module only relates what it read.
"""
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

from .reports import Report, reports


def document_name(route: str) -> str:
    """The document a route names: the publisher's file name, whatever the scheme."""
    parts = urlsplit(route)
    return parse_qs(parts.query).get('nomeFile', [parts.path])[0].rsplit('/', 1)[-1]

# A reference printed in its own column, or inside an identifying cell, identifies a
# sample. A daily counter identifies one only when its value has the width of a sample
# reference; the finding records which header supplied it either way.
MATCHABLE = {'sample', 'in-cell'}
POSITIVE_LABELS = ('published-positive', 'published-positive-and-removal-label')
COMPARABLE_LABELS = POSITIVE_LABELS + ('published-negative', 'published-doubtful')
DETECTED = ('positive', 'detected')
# A test designated by the same assay on another date, or marked a repetition, is that
# assay run again, not a second test.
_RUN = re.compile(r'\s*(?:\bdel\b\s*)?\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|\(\s*ripetizion\w*\s*\)', re.I)


def _test_identity(designation: str) -> str:
    return _RUN.sub('', designation).strip(' -–,;').casefold()


def confirmation_candidates(row, *, sample: str):
    """The Article 2(6) arguments a report row supplies, and the ones it cannot.

    Two result columns that the laboratory designates differently and that both
    read as detected are two positive tests on one sample; two designations that
    differ only by a date or a repetition marker are one assay run twice. The genome target each
    assay amplifies is printed by no report in this population, and an assay name
    is not a genome target (`analytical-result`), so it is passed as unavailable
    and `cordon_c.bindings.confirmation_facts` refuses the Article 2(6) conclusion
    for want of it rather than concluding against confirmation. Returns None where
    the row does not show two differently designated detected tests.
    """
    detected = [r for r in row.results if r.kind in DETECTED and r.assay]
    distinct = {_test_identity(r.assay): r.assay for r in detected}
    if len(detected) < 2 or len(distinct) < 2:
        return None
    first, second = sorted(distinct.values())[:2]
    return {'first_test': first, 'second_test': second,
            'first_sample': sample, 'second_sample': sample,
            'first_extract': None, 'second_extract': None,
            'first_genome_target': None, 'second_genome_target': None}


def comparison(label: str, view: str, results) -> str:
    """Agreement between a published label and a report row, at the level the report states.

    A column for the subspecies the view names compares at subspecies level; otherwise a
    column for Xylella fastidiosa without subspecies compares at species level. Anything
    else is not comparable.
    """
    if label not in COMPARABLE_LABELS:
        return 'not comparable'
    view_subspecies = re.search(r'sub\.?\s*(pauca|multiplex|fastidiosa)', view or '', re.I)
    wanted = f'xylella fastidiosa subsp. {view_subspecies.group(1).lower()}' if view_subspecies else None
    at_subspecies = [r.kind for r in results if wanted and (r.analyte or '').lower() == wanted]
    at_species = [r.kind for r in results if (r.analyte or '').lower() == 'xylella fastidiosa']
    level, kinds = ('subspecies', at_subspecies) if at_subspecies else ('species', at_species)
    if not kinds or any(k == 'unread' for k in kinds):
        return 'not comparable'
    positive = any(k in ('positive', 'detected') for k in kinds)
    negative = all(k in ('negative', 'not-detected') for k in kinds)
    doubtful = any(k in ('doubtful', 'undetermined') for k in kinds)
    if label in POSITIVE_LABELS:
        verdict = 'agree' if positive else 'disagree' if negative else 'doubtful'
    elif label == 'published-negative':
        verdict = 'agree' if negative else 'disagree' if positive else 'doubtful'
    else:
        verdict = 'agree' if doubtful else 'disagree'
    return f'{verdict} at {level}'


def _matchable(row):
    return row.reference and (row.reference_kind in MATCHABLE
                              or (row.reference_kind == 'daily' and len(row.reference) >= 5))


def why_not_comparable(label: str, view: str, results) -> str | None:
    """Why this reader could not compare a row it matched, named as its own act.

    Every cause here is a fact about the reading, not about the document: that no
    analyte was recovered does not establish that the annex prints none.
    """
    if label not in COMPARABLE_LABELS:
        return 'the published label is not one this reader compares'
    if not results:
        return 'no result recovered from the row'
    if all(r.analyte is None for r in results):
        return 'no analyte recovered for any result'
    if any(r.kind == 'unread' for r in results):
        return 'a comparable result was recovered but could not be classified'
    return 'the analytes recovered name another subspecies than the view'


def findings(root: Path, store: Path):
    """Every observation publication carrying a report route, with what its report says.

    Yields one dict per publication; the caller aggregates.
    """
    import duckdb
    records = {r['url']: r for r in json.loads((root / 'records.json').read_text())}
    # The publisher serves one report file name from more than one place. Where the route
    # an observation names failed and a route naming the same file carried bytes, that
    # document is a *candidate* for the one referenced, never an equivalent: a file name
    # is not a document identity. Candidates are kept whole, so a name carrying two
    # documents resolves to neither rather than to whichever record was read last.
    by_name: dict[str, set] = {}
    for record in records.values():
        if 'sha256' in record:
            by_name.setdefault(document_name(record['url']), set()).add(record['sha256'])
    by_digest: dict[str, Report] = {}
    for url, item, record in reports(root, store):
        if isinstance(item, Report):
            by_digest[item.sha256] = item
    files = [str(p) for p in (store / 'derived/monitoring/readings').glob('*.parquet')]
    connection = duckdb.connect()
    connection.execute("SET memory_limit = '1GB'")
    connection.execute('SET threads = 2')
    cursor = connection.execute(
        'SELECT route, reference, day, view, result FROM (SELECT unnest(report_routes) AS route, reference, day, view, result '
        'FROM read_parquet($files)) ORDER BY route', {'files': files})
    current, group = None, []

    def emit(reference, day, view, label, digest, status, *, matches=0, verdict='not comparable', row=None,
             resolution='route', day_constrained=None):
        return {'route': current, 'sha256': digest, 'observation': reference, 'day': day, 'view': view, 'label': label,
                'status': status, 'matches': matches, 'comparison': verdict,
                'why_not_comparable': why_not_comparable(label, view, row.results) if row and ' at ' not in verdict else None,
                'results': [(r.column, r.assay, r.analyte, r.kind) for r in row.results] if row else None,
                'sampling_date': row.sampling_date if row else None,
                'reference_kind': row.reference_kind if row else None,
                # How this document was reached: the route the observation names, or a
                # candidate substituted because a route naming the same file carried bytes.
                'document_resolution': resolution,
                # Whether the report's own printed day agreed with the observation's, or
                # was absent and so constrained nothing.
                'day_constrained': day_constrained,
                # The sample identity is the observation's by construction: the row matched it.
                'confirmation': confirmation_candidates(row, sample=reference) if row else None}

    def flush():
        if current is None:
            return
        record = records.get(current)
        digest, resolution = (record or {}).get('sha256'), 'route'
        if digest is None:
            candidates = by_name.get(document_name(current), set())
            if len(candidates) == 1:
                digest, resolution = next(iter(candidates)), 'substituted candidate of the same file name'
            elif candidates:
                resolution = 'several documents carry this file name; none substituted'
        item = by_digest.get(digest) if digest else None
        if item is None:
            for reference, day, view, label in group:
                yield emit(reference, day, view, label, digest,
                           'no bytes acquired for this document' if not digest else 'document acquired but not read',
                           resolution=resolution)
            return
        if not item.rows:
            for reference, day, view, label in group:
                yield emit(reference, day, view, label, digest, 'no annex row recovered from this document',
                           resolution=resolution)
            return
        sample_rows: dict[str, list] = {}
        for row in item.rows:
            if _matchable(row):
                sample_rows.setdefault(row.reference, []).append(row)
        for reference, day, view, label in group:
            candidates = sample_rows.get(reference or '', [])
            # The printed day is a constraint on identity, not a tie-break among candidates:
            # a row the report dates to another day is a different sampling event, whatever
            # reference it shares. A row printing no day constrains nothing, and says so.
            agreeing = [r for r in candidates if r.sampling_date == day]
            undated = [r for r in candidates if r.sampling_date is None]
            contradicting = [r for r in candidates if r.sampling_date is not None and r.sampling_date != day]
            usable = agreeing or undated
            if len(usable) == 1:
                row = usable[0]
                yield emit(reference, day, view, label, digest, 'matched', matches=1,
                           verdict=comparison(label, view, row.results), row=row, resolution=resolution,
                           day_constrained=bool(agreeing))
            elif usable:
                yield emit(reference, day, view, label, digest, 'several rows carry this reference',
                           matches=len(usable), resolution=resolution)
            elif contradicting:
                yield emit(reference, day, view, label, digest, 'the reference is printed, dated to another day',
                           matches=len(contradicting), resolution=resolution, day_constrained=False)
            elif not sample_rows:
                yield emit(reference, day, view, label, digest, 'no sample reference recovered from this document',
                           resolution=resolution)
            else:
                yield emit(reference, day, view, label, digest, 'document read, this reference not found in it',
                           resolution=resolution)

    while True:
        batch = cursor.fetchmany(20000)
        if not batch:
            break
        for route, reference, day, view, label in batch:
            if route != current:
                yield from flush()
                current, group = route, []
            group.append((reference, day, view, label))
    yield from flush()
    connection.close()

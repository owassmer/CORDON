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

from .reports import Report, reports

# A reference printed in its own column, or inside an identifying cell, identifies a
# sample. A daily counter identifies one only when its value has the width of a sample
# reference; the finding records which header supplied it either way.
MATCHABLE = {'sample', 'in-cell'}
POSITIVE_LABELS = ('published-positive', 'published-positive-and-removal-label')
COMPARABLE_LABELS = POSITIVE_LABELS + ('published-negative', 'published-doubtful')
DETECTED = ('positive', 'detected')


def confirmation_candidates(row, *, sample: str):
    """The Article 2(6) arguments a report row supplies, and the ones it cannot.

    Two result columns that the laboratory designates differently and that both
    read as detected are two positive tests on one sample. The genome target each
    assay amplifies is printed by no report in this population, and an assay name
    is not a genome target (`analytical-result`), so it is passed as unavailable
    and `cordon_c.bindings.confirmation_facts` refuses the Article 2(6) conclusion
    for want of it rather than concluding against confirmation. Returns None where
    the row does not show two differently designated detected tests.
    """
    detected = [r for r in row.results if r.kind in DETECTED and r.assay]
    designations = {r.assay for r in detected}
    if len(detected) < 2 or len(designations) < 2:
        return None
    first, second = sorted(designations)[:2]
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


def findings(root: Path, store: Path):
    """Every observation publication carrying a report route, with what its report says.

    Yields one dict per publication; the caller aggregates.
    """
    import duckdb
    records = {r['url']: r for r in json.loads((root / 'records.json').read_text())}
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

    def emit(reference, day, view, label, digest, status, matches=0, verdict='not comparable', row=None):
        return {'route': current, 'sha256': digest, 'observation': reference, 'day': day, 'view': view, 'label': label,
                'status': status, 'matches': matches, 'comparison': verdict,
                'results': [(r.column, r.assay, r.analyte, r.kind) for r in row.results] if row else None,
                'sampling_date': row.sampling_date if row else None,
                'reference_kind': row.reference_kind if row else None}

    def flush():
        if current is None:
            return
        record = records.get(current)
        digest = record.get('sha256') if record else None
        item = by_digest.get(digest) if digest else None
        if item is None:
            for reference, day, view, label in group:
                yield emit(reference, day, view, label, digest, 'report not acquired' if not digest else 'report unread')
            return
        if not item.rows:
            for reference, day, view, label in group:
                yield emit(reference, day, view, label, digest, 'report has no readable rows')
            return
        sample_rows: dict[str, list] = {}
        for row in item.rows:
            if _matchable(row):
                sample_rows.setdefault(row.reference, []).append(row)
        for reference, day, view, label in group:
            candidates = sample_rows.get(reference or '', [])
            if len(candidates) > 1:
                dated = [r for r in candidates if r.sampling_date == day]
                candidates = dated if len(dated) == 1 else candidates
            if len(candidates) == 1:
                row = candidates[0]
                yield emit(reference, day, view, label, digest, 'matched', 1, comparison(label, view, row.results), row)
            elif candidates:
                yield emit(reference, day, view, label, digest, 'several rows', len(candidates))
            elif not sample_rows:
                yield emit(reference, day, view, label, digest, 'report prints no sample reference')
            else:
                yield emit(reference, day, view, label, digest, 'not named by its report')

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

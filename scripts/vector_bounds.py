#!/usr/bin/env python3
"""Row 12's done means: the next-season onset bound for held detections, and the 6(1) join.

Z for each detection is Annex III Part A's infected zone in the version in force on the detection
day, as row 3 builds it (`vectors.AnnexIIIZones`); every site reaches it through its printed agro,
with the error row 3 sources for that agro, and C's answer (`vectors.agro_in`). The records,
statements and untranscribed rounds are the `--out` JSON of `scripts/read_vectors.py`.

The detections are the held containment orders the plan names (DET 2/2024, DET 51/2026) and the
two gap-year orders of implementation round 1 (DET 9/2025, DET 20/2023), each by its cited test
report's date. Usage: vector_bounds.py READINGS_JSON [--out JSON]
"""
import argparse
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]

from cordon_d import vectors  # noqa: E402

DETECTIONS = (('DET 2/2024 (report 1622/2023 CRSFA, 15/12/2023)', date(2023, 12, 15)),
              ('DET 51/2026 (reports 9P and 10P/2026 CNR, 12/02/2026)', date(2026, 2, 12)),
              ('DET 9/2025 (report 184P/2024 CNR, 27/11/2024)', date(2024, 11, 27)),
              ('DET 20/2023 (report 178/23 CRSFA, 14/02/2023)', date(2023, 2, 14)))


def load(path):
    data = json.loads(Path(path).read_text())
    records = []
    for r in data['records']:
        r = dict(r)
        r['window'] = tuple(date.fromisoformat(d) for d in r['window']) if r['window'] else None
        r['coordinates'] = tuple(r['coordinates']) if r['coordinates'] else None
        r['count'] = Decimal(r['count']) if r['count'] is not None else None
        r['fields'] = tuple(tuple(f) for f in r['fields'])
        r['issues'] = tuple(r.get('issues', ()))
        records.append(vectors.Record(**r))
    statements = []
    for s in data['statements']:
        s = dict(s)
        s['day'] = tuple(date.fromisoformat(d) for d in s['day']) if s['day'] else None
        statements.append(vectors.Statement(**s))
    untranscribed = []
    for r in data.get('untranscribed', []):
        r = dict(r, season=tuple(r['season']), printed_rounds=tuple(r.get('printed_rounds', ())))
        for k in ('start', 'end'):
            r[k] = date.fromisoformat(r[k]) if r[k] else None
        untranscribed.append(vectors.Round(**r))
    return data, records, statements, untranscribed


def show(bound, comune_of):
    out = dict(zone=bound.zone, detection=str(bound.detection), season=bound.season,
               upper=str(bound.upper) if bound.upper else None, upper_cause=bound.upper_cause,
               lower=bound.lower, lower_cause=bound.lower_cause, unnamed_rounds=list(bound.unnamed_rounds),
               untranscribed_rounds=list(bound.untranscribed_rounds), unplaced=len(bound.unplaced))
    if bound.upper_record:
        r = bound.upper_record
        comune = comune_of(r.agro)
        out['source_cell'] = dict(url=r.url, source=r.source, cell=r.cell, request=r.request, site=r.site,
                                  agro=r.agro, coordinates=r.coordinates, window=[str(d) for d in r.window],
                                  window_literal=r.window_literal, stage_literal=r.stage_literal, result=r.result,
                                  series=r.series, round_literal=r.round_literal,
                                  agro_error_m=comune.territory.error_m if comune else None)
    seen, distinct = set(), []
    for r, cause in bound.unplaced:
        if (r.site, r.agro, cause) not in seen:
            seen.add((r.site, r.agro, cause))
            distinct.append(dict(site=r.site, agro=r.agro, window=[str(d) for d in r.window], cause=cause,
                                 url=r.url.rsplit('/', 1)[-1]))
    out['unplaced_distinct'] = distinct
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('readings', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    data, records, statements, untranscribed = load(args.readings)
    zones = vectors.AnnexIIIZones(ROOT)
    rounds = vectors.unnamed_rounds(records)
    result = {}
    for name, day in DETECTIONS:
        bound = vectors.onset_bound(records, statements, zones.zone(day), day, zones.comune_of, rounds=rounds,
                                    untranscribed=untranscribed)
        result[name] = show(bound, zones.comune_of)
        print(name, '->', result[name]['upper'] or result[name]['upper_cause'], flush=True)
    positives = [r for r in records if r.test_result and vectors._positive(r.test_result)]
    recited = [s for s in statements if s.kind == 'vector_positive']
    area = zones.zone(date(2026, 2, 12))
    joins = vectors.vector_detections(records, statements, area, zones.comune_of)
    result['6(1)'] = dict(printed_test_positives=len(positives), recited_positives=len(recited),
                          recited=[dict(url=s.url.rsplit('/', 2)[-2:], quote=s.quote[:200], place=s.place,
                                        printed_agro=vectors.statement_agro(s)) for s in recited],
                          joins_against=area.identity, joined=len(joins.joined),
                          unjoined=[dict(quote=(x.quote if hasattr(x, 'quote') else x.cell)[:120], cause=c)
                                    for x, c in joins.unjoined],
                          headers=data.get('headers_summary'))
    text = json.dumps(result, indent=1, ensure_ascii=False, default=str)
    if args.out:
        args.out.write_text(text)
    else:
        print(text)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""C's Art. 33(1), 146(5) and 146(8) results for the plants the Osservatorio asks about (row 10).

`--records` is the Osservatorio's landscape proceeding records, a JSON list of the kinds
`case_prescriptions.LANDSCAPE_KINDS` names, each naming its plants by the identifiers it prints for each. They are
controlled sources: the run states its knowledge cutoff (`--known-through`) and its grant
(`--permitted-controlled-sources`, stated even when empty), and `landscape_results` admits them under both. Each
plant a record names attaches through row 9's identity, or is listed unattached with its cause: PR #30's rows
(`derived/protected-status/rows-<version>.json` as `read_protection.py` writes them without records, and the
register capture), with the identities row 9 decides from the same records under the same cutoff and grant
(`protection.named_rows`). A record attached to a plant not asked about is listed under `elsewhere`. `--plants` names the plants as PR #30's rows name
them. No owning unit yet supplies Art. 33(1)'s measure, status or infection conjunct to this caller, so C names
them. `--out` writes the results outside the tree.
"""
import argparse
from datetime import date, datetime
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d'), str(ROOT / 'scripts')]

from cordon_c.core import Snapshot  # noqa: E402
from cordon_d import protection  # noqa: E402
from cordon_d.calendar import national_calendar  # noqa: E402
from cordon_d.evidence import run_instant  # noqa: E402
from cordon_d.landscape import landscape_results  # noqa: E402
from cordon_d.store import store_root  # noqa: E402

ZONE = ZoneInfo('Europe/Rome')


def register(store, rows):
    """The register capture's entries, and any deleted entry PR #30's rows carry (a plant's identity can be one)."""
    entries = protection.register_entries(store, ROOT)
    held = {e.oid for e in entries}
    return entries + [protection.Entry(e['layer'], e['entry'], e['key'], e['card'], e['label'], e['bulletin_printed'],
                                       e['comune'], e['foglio'], e['particella'], (e.get('point') or {}).get('x'),
                                       (e.get('point') or {}).get('y'), None, e['source'])
                      for e in rows['zone_entries'] if e['entry'] not in held]


def summary(evaluation):
    return dict(truth=evaluation.truth, effect=evaluation.effect, needs=sorted(evaluation.needs),
                provisions=sorted(evaluation.provisions))


def plain(value):
    if hasattr(value, 'truth'):
        return summary(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def results(snapshot, run, plants, supplied, rows, entries):
    """The caller's output as JSON values: C's result per (plant, row), as C returns it. `run` is the run's stated
    inputs: `at`, `known_through` (C's evaluated_at) and `permitted_controlled_sources`."""
    out = landscape_results(snapshot, run['at'], plants, supplied, evaluated_at=run['known_through'],
                            permitted_controlled_sources=run['permitted_controlled_sources'], rows=rows,
                            register=entries, zone=ZONE, calendar=national_calendar())
    return plain(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', required=True, help='the Osservatorio\'s landscape records (a JSON list)')
    parser.add_argument('--plants', nargs='+', required=True, help="the plants asked about, as PR #30's rows name them")
    parser.add_argument('--at', type=date.fromisoformat, required=True,
                        help='the evaluation date; no machine-clock date')
    parser.add_argument('--known-through', type=run_instant, required=True,
                        help="the knowledge cutoff, a timezone-aware ISO instant; C's evaluated_at")
    parser.add_argument('--permitted-controlled-sources', nargs='*', required=True, metavar='SOURCE',
                        help='the controlled source identities the running principal is granted (state it even when '
                             'empty)')
    parser.add_argument('--rows', help="PR #30's rows as read_protection.py writes them without records (a run's rows "
                                       "are refused); default: this checkout's version in the store")
    parser.add_argument('--out')
    arguments = parser.parse_args()
    store = store_root(ROOT)
    if arguments.rows:
        path = Path(arguments.rows)
    else:
        from read_protection import version
        path = store / 'derived' / 'protected-status' / f'rows-{version()}.json'
    if not path.exists():
        parser.error(f"PR #30's rows are not at {path}: run scripts/read_protection.py first")
    rows = json.loads(path.read_text())
    run = dict(at=arguments.at, known_through=arguments.known_through,
               permitted_controlled_sources=frozenset(arguments.permitted_controlled_sources))
    out = results(Snapshot.load(ROOT), run, arguments.plants, json.loads(Path(arguments.records).read_text()), rows,
                  register(store, rows))
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if arguments.out:
        Path(arguments.out).write_text(text)
    print(text)


if __name__ == '__main__':
    main()

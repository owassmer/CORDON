#!/usr/bin/env python3
"""C's Art. 33(1), 146(5) and 146(8) results for the plants the Osservatorio asks about (row 10).

`--records` is the Osservatorio's landscape proceeding records, a JSON list of the kinds
`case_prescriptions.LANDSCAPE_KINDS` names. Each attaches to one plant through PR #30's identity (its rows,
`derived/protected-status/rows-<version>.json` as `read_protection.py` writes them, and the register capture), or is
listed unattached with its cause. `--plants` names the plants as PR #30's rows name them. No owning unit yet
supplies Art. 33(1)'s measure, status or infection conjunct to this caller, so C names them. `--out` writes the
results outside the tree.
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
from cordon_d.landscape import landscape_results  # noqa: E402
from cordon_d.store import store_root  # noqa: E402

ZONE = ZoneInfo('Europe/Rome')


def register(store, rows):
    """The register capture's entries, and any deleted entry PR #30's rows carry (a plant's identity can be one)."""
    entries = protection.register_entries(store, ROOT)
    held = {e.oid for e in entries}
    return entries + [protection.Entry(e['layer'], e['entry'], e['key'], e['card'], e['label'], e['bulletin_printed'],
                                       e['comune'], e['foglio'], e['particella'], None, None, None, e['source'])
                      for e in rows['zone_entries'] if e['entry'] not in held]


def summary(evaluation):
    return dict(truth=evaluation.truth, effect=evaluation.effect, needs=sorted(evaluation.needs),
                provisions=sorted(evaluation.provisions))


def results(snapshot, at, plants, supplied, rows, entries):
    """The caller's output as JSON values: C's result per (plant, row), as C returns it."""
    run = landscape_results(snapshot, at, plants, supplied, rows=rows, register=entries, zone=ZONE,
                            calendar=national_calendar())

    def plain(value):
        return value.isoformat() if isinstance(value, (date, datetime)) else value

    out = dict(at=at.isoformat(), unattached=run['unattached'], not_supplied=run['not_supplied'], plants={})
    for plant, item in run['plants'].items():
        out['plants'][plant] = dict(
            item, results={row: summary(result) for row, result in item['results'].items()}, due=plain(item['due']),
            decision=item['decision'] and {k: plain(v) for k, v in item['decision'].items()},
            opinion_route=item['opinion_route'] and {k: plain(v) for k, v in item['opinion_route'].items()},
            lodgings=[{k: plain(v) for k, v in lodging.items()} for lodging in item['lodgings']],
            facts={row: {p: summary(v) if hasattr(v, 'truth') else v for p, v in values.items()}
                   for row, values in item['facts'].items()})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', required=True, help='the Osservatorio\'s landscape records (a JSON list)')
    parser.add_argument('--plants', nargs='+', required=True, help="the plants asked about, as PR #30's rows name them")
    parser.add_argument('--at', type=date.fromisoformat, default=date.today(), help='the evaluation date')
    parser.add_argument('--rows', help="PR #30's rows; default: this checkout's version in the store")
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
    out = results(Snapshot.load(ROOT), arguments.at, arguments.plants, json.loads(Path(arguments.records).read_text()),
                  rows, register(store, rows))
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if arguments.out:
        Path(arguments.out).write_text(text)
    print(text)


if __name__ == '__main__':
    main()

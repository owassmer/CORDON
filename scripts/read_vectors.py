#!/usr/bin/env python3
"""Read the vector-monitoring population (INPUTS.md row 12) through `cordon_d.vectors`.

What is read is what the consumers read. Every monitoring publication is first dated to its
season and round from held words only (`vectors.rounds_of`). For each season the rounds are
read in date order from the first, and reading stops once every zone version in force in that
season (`vectors.AnnexIIIZones`: Annex III Part A as row 3 builds it) holds a located adult
record, or the rounds run out; later rounds stay acquired and catalogued and are listed, not transcribed. Within a round a table of the sites
where adults were found is read in place of the round's area tables; juvenile-stage tables are
never read. A raster publication is read header band first, and no further where neither its
label nor any header, title or banner prints a stage, or where neither the table nor the
publication (its folder's survey year and the day its name or server dates it to) dates its counts. A PDF table page is read from its text
layer where that reads cleanly, else by a model page read. Every table left untranscribed has its
header band read for a test-result column (one request per raster, all its tables, at medium effort;
a PDF from its text layer): a table not transcribed is never taken as printing no test result.

Replays retained readings by default; `--execute` dispatches the missing requests on the Claude
subscription, at most two at a time, each only while at least 20% of memory is free. A
subscription or transport failure stops the pass (exit 3) and is never a reading limit.
`--plan` states the requests before any is made. `--out` writes the records, statements,
rounds and reading limits as JSON outside the tree; nothing here is an owner.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import date
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]

from cordon_d import vectors  # noqa: E402
from cordon_d.store import store_root  # noqa: E402

MAX_WORKERS = 2  # model readings share the subscription with every worker


class Stopped(Exception):
    pass


def wait_for_memory(floor=20):
    while True:
        try:
            report = subprocess.run(['memory_pressure', '-Q'], capture_output=True, text=True).stdout
        except FileNotFoundError:
            return
        match = re.search(r'(\d+)%', report.strip().splitlines()[-1] if report.strip() else '')
        if not match or int(match.group(1)) >= floor:
            return
        time.sleep(30)


def crop(text):
    folded = vectors._fold(text)
    for stem, name in (('oliv', 'olive'), ('mandorl', 'almond'), ('vit', 'vine'), ('vign', 'vine')):
        if folded.startswith(stem):
            return name
    return folded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--workers', type=int, default=MAX_WORKERS)
    parser.add_argument('--only', action='append', default=[])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--plan', action='store_true', help='state the requests and make none')
    args = parser.parse_args()
    workers = max(1, min(args.workers, MAX_WORKERS))
    execute = args.execute and not args.plan
    zones = vectors.AnnexIIIZones(ROOT)   # row 3's Annex III geography; each version built when first named
    store = store_root(ROOT)
    population = [p for p in vectors.population(ROOT, store)
                  if not args.only or any(o in p.url for o in args.only)]
    limits, lock = [], threading.Lock()
    if execute:
        print(f'cleared {vectors.clear_stale_locks(store)} stale request locks', flush=True)

    def limit(publication, where, cause):
        with lock:
            limits.append(dict(source=publication.sha256, url=publication.url, where=where, cause=str(cause)[:500]))

    def gated(function, *a, **k):
        if execute:
            wait_for_memory()
        return function(*a, **k)

    def run(jobs):
        """[(job, result or exception)]; a transport failure stops the pass."""
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [(job, pool.submit(job[0], *job[1:])) for job in jobs]
            out = []
            for job, future in futures:
                try:
                    out.append((job, future.result()))
                except vectors.TransportFailure as error:
                    for _, other in futures:
                        other.cancel()
                    raise Stopped(f'{type(error).__name__}: {error}') from error
                except Exception as error:  # noqa: BLE001
                    out.append((job, error))
            return out

    # Held readings: each PDF's statements, each raster's layout and its large tables' corners.
    statements, layouts, corners = {}, {}, {}
    try:
        jobs = [((lambda p: gated(vectors.read_statements, store, p.sha256, execute=execute)) if p.kind == 'pdf'
                 else (lambda p: gated(vectors.layout, store, p.sha256, execute=execute)), p) for p in population]
        for (_, p), result in run(jobs):
            if isinstance(result, Exception):
                limit(p, dict(step='statements' if p.kind == 'pdf' else 'layout'), f'{type(result).__name__}: {result}')
            else:
                (statements if p.kind == 'pdf' else layouts)[p.sha256] = result
        jobs = [(lambda p, box: gated(vectors.corner, store, p.sha256, box, execute=execute), p, tuple(t['box']))
                for p in population if p.sha256 in layouts
                for t in layouts[p.sha256]['tables'] if vectors.needs_tiles(t['box'])]
        for (_, p, box), result in run(jobs):
            if isinstance(result, Exception):
                limit(p, dict(step='corner', table=list(box)), f'{type(result).__name__}: {result}')
            else:
                corners[(p.sha256, box)] = result
    except Stopped as stop:
        print(f'STOPPED {stop}', flush=True)
        sys.exit(3)
    print(f'held: {len(statements)} statement readings, {len(layouts)} layouts, {len(corners)} corners, '
          f'{len(limits)} limits', flush=True)

    # Seasons and rounds from held words.
    rounds = {p.sha256: vectors.rounds_of(p, statements.get(p.sha256), layouts.get(p.sha256)) for p in population}
    by_sha = {p.sha256: p for p in population}
    seasons = {}
    for sha, found in rounds.items():
        for r in found:
            seasons.setdefault(r.season, {}).setdefault(r.end, []).append(r)

    def packets(p):
        """The reading units of one publication: ('page', n) or ('replay'|'tile', geometry, ...)."""
        if p.kind == 'pdf':
            return [('page', dict(page=n)) for n in statements[p.sha256]['reading']['table_pages']]
        out, raster = [], None
        for table in layouts[p.sha256]['tables']:
            box = tuple(table['box'])
            held = vectors.retained_tiling(store, p.sha256, box) if vectors.needs_tiles(box) else None
            if held:
                out += [('replay', g, response) for g, response in held]
                continue
            if vectors.needs_tiles(box) and (p.sha256, box) not in corners:
                limit(p, dict(step='tiles', table=list(box)), 'no corner reading of the table')
                continue
            raster = raster or vectors._Raster(store, p.sha256)
            try:
                out += [('tile', g, png, context) for g, png, context in
                        vectors.tiles(store, p.sha256, box, corners.get((p.sha256, box)), raster=raster)]
            except Exception as error:  # noqa: BLE001
                limit(p, dict(step='tiles', table=list(box)), f'{type(error).__name__}: {error}')
        return out

    rasters = {}

    def read(p, packet, dispatch):
        kind, geometry = packet[0], packet[1]
        if kind == 'page':
            return geometry, gated(vectors.read_pdf_table, store, p.sha256, geometry['page'], execute=dispatch)
        response = packet[2] if kind == 'replay' else gated(vectors.table_tile, store, p.sha256, geometry, packet[2],
                                                             packet[3], execute=dispatch)
        if geometry.get('header') is not None:
            with lock:
                raster = rasters.get(p.sha256) or rasters.setdefault(p.sha256, vectors._Raster(store, p.sha256))
            printed = vectors.printed_row_count(raster, geometry)
            counted = vectors.reading_rows(response['reading'])[0]
            if printed is not None and printed != counted:
                raise ValueError(f'the reading counts {counted} data rows, the tile prints {printed}')
        return geometry, response

    def missing(p, packet):
        """Whether reading this packet would make a model request."""
        kind, geometry = packet[0], packet[1]
        if kind == 'replay':
            return False
        try:
            if kind == 'page':
                vectors.read_pdf_table(store, p.sha256, geometry['page'])
            else:
                vectors.table_tile(store, p.sha256, geometry, packet[2], packet[3])
            return False
        except FileNotFoundError:
            return True

    readings, transcribed, not_transcribed, requests = {}, [], [], dict(made=0, planned_first=0, planned_all=0)

    def read_publication(p, first):
        units = packets(p)
        if args.plan:
            needed = sum(missing(p, u) for u in units)
            requests['planned_all'] += needed
            requests['planned_first'] += needed if first else 0
            header = sum(missing(p, u) for u in units if u[1].get('band', 0) == 0)
            print(f'  plan {p.url.rsplit("/", 1)[-1][:60]}: {needed} requests ({header} in its header band)'
                  f'{" [first round]" if first else ""}', flush=True)
            return
        header = [u for u in units if u[1].get('band', 0) == 0]
        rest = [u for u in units if u[1].get('band', 0) != 0]
        got = []
        for batch in (header, rest):
            if batch is rest and rest:
                cause = None
                if not vectors.prints_stage(p, got, statements.get(p.sha256)):
                    cause = 'no stage printed in its label, headers, title or banners'
                elif not vectors.prints_window(got) and vectors.publication_window(p) is None:
                    cause = 'no window printed for its counts (no date or period column, no window in a header or title)'
                if cause:
                    not_transcribed.append(dict(url=p.url, units=len(rest),
                                                cause=cause + ': its counts are never an adult window'))
                    break
            requests['made'] += sum(missing(p, u) for u in batch) if execute else 0
            for (_, _, packet), result in run([(lambda p, u: read(p, u, execute), p, u) for u in batch]):
                if isinstance(result, Exception):
                    limit(p, {k: v for k, v in packet[1].items() if k != 'header'}, f'{type(result).__name__}: {result}')
                else:
                    got.append(result)
        readings.setdefault(p.sha256, []).extend(got)

    records_by = {}
    untranscribed_rounds = []
    set_aside = {}  # (season, end) -> the rounds of a transcribed round group that were not transcribed
    try:
        for season in sorted(seasons, key=lambda s: (s[2], s[0], s[1])):
            groups = sorted(seasons[season].items(), key=lambda kv: kv[0] or date.max)
            in_force = zones.zones_in_force(season[2])
            done = set()
            for index, (end, group) in enumerate(groups):
                chosen = [r for r in group if r.stage != 'juvenile']
                finds = [r for r in chosen if r.find_sites and r.stage == 'adult']
                chosen = finds or chosen
                for r in group:
                    if r not in chosen:
                        set_aside.setdefault((season, end), []).append(r)
                        not_transcribed.append(dict(url=r.url, round=r.name, cause=(
                            'a juvenile-stage table: never an adult window' if r.stage == 'juvenile' else
                            'the round is read from its table of the sites where adults were found')))
                for r in chosen:
                    if r.source not in done:
                        read_publication(by_sha[r.source], first=index == 0)
                        done.add(r.source)
                    transcribed.append(r)
                if args.plan:
                    continue
                # Records are projected after each round, so the stop test sees every round read so far.
                for sha in done:
                    p = by_sha[sha]
                    records_by[sha] = vectors.records_of(p, readings.get(sha, []), statements.get(sha))
                # A publication of one season gives it all its records; one carrying several crop
                # series (a CNR transmission) gives each season the records of its series.
                season_records = [x for sha in done for x in records_by[sha]
                                  if x.window and x.window[0].year == season[2]
                                  and season in {r.season for r in rounds[sha]}
                                  and (len({r.season for r in rounds[sha]}) == 1
                                       or crop(x.series or '') == crop(season[1]))]
                lacking = vectors.zones_without_adult(season_records, in_force, zones.comune_of)
                print(f'{season} round ending {end}: {len(season_records)} records, zones without an adult: '
                      f'{len(lacking)} of {len(in_force)}', flush=True)
                if not lacking:
                    for later_end, later in groups[index + 1:]:
                        for r in later:
                            untranscribed_rounds.append(r)
                            not_transcribed.append(dict(url=r.url, round=r.name, cause=(
                                'a later round: every zone version in force in the season already holds a '
                                'located adult record')))
                    break
    except Stopped as stop:
        print(f'STOPPED {stop}; {requests["made"]} requests made before the stop', flush=True)
        sys.exit(3)
    # 6(1): an acquired table not transcribed may still print a test result. The header band of every
    # such table is read (one request per raster, all its tables; a PDF from its text layer), and a
    # table whose header prints a test-result column is named, never taken as silent.
    header_sources = sorted({r.source for r in untranscribed_rounds}, key=lambda s: by_sha[s].url)
    headers = []
    rasters_needing = [s for s in header_sources if by_sha[s].kind == 'image']
    if args.plan:
        print(f'plan: {requests["planned_first"]} model requests for the first round of every season; at most '
              f'{requests["planned_all"]} if no season stops early; plus one header-band request per raster '
              f'left untranscribed', flush=True)
        return
    try:
        for sha in header_sources:
            if by_sha[sha].kind == 'pdf':
                columns = vectors.pdf_header_columns(store, sha, statements[sha]['reading']['table_pages'])
                headers.append(dict(url=by_sha[sha].url, read='text layer', request=None, columns=columns,
                                    tables=None, test_columns=[c for c in columns if c['header_literal']
                                                               and vectors.TEST_WORDS.search(c['header_literal'])]))
        missing_headers = []
        for sha in rasters_needing:
            try:
                vectors.header_band(store, sha)
            except FileNotFoundError:
                missing_headers.append(sha)
        requests['made'] += len(missing_headers) if execute else 0
        jobs = [(lambda s: gated(vectors.header_band, store, s, execute=execute), sha) for sha in rasters_needing]
        for (_, sha), result in run(jobs):
            if isinstance(result, Exception):
                limit(by_sha[sha], dict(step='header'), f'{type(result).__name__}: {result}')
                headers.append(dict(url=by_sha[sha].url, read=None, cause=f'{type(result).__name__}: {result}'[:300]))
                continue
            reading = result['reading']
            periods, numbers = vectors.printed_periods(reading)
            headers.append(dict(url=by_sha[sha].url, read='header band', request=result['request_sha256'],
                                tables=reading['tables'], issues=reading['issues'], periods=periods,
                                printed_rounds=list(numbers), test_columns=vectors.test_columns(reading)))
            untranscribed_rounds[:] = [replace(r, periods=periods, printed_rounds=numbers) if r.source == sha else r
                                       for r in untranscribed_rounds]
        # The rasters of a transcribed round that were set aside (the round was read from its find-site
        # table; juvenile-stage tables): one header request per round for all of them.
        groups = []
        for key, found in sorted(set_aside.items(), key=lambda kv: (kv[0][0][2], kv[0][1] or date.max)):
            shas = sorted({r.source for r in found if by_sha[r.source].kind == 'image'
                           and not readings.get(r.source)}, key=lambda s: by_sha[s].url)
            if shas:
                groups.append(shas)
                header_sources += shas
        missing = 0
        for shas in groups:
            try:
                vectors.round_header_bands(store, shas)
            except FileNotFoundError:
                missing += 1
        requests['made'] += missing if execute else 0
        jobs = [(lambda g: gated(vectors.round_header_bands, store, list(g), execute=execute), tuple(g)) for g in groups]
        for (_, shas), result in run(jobs):
            urls = [by_sha[s].url for s in shas]
            if isinstance(result, Exception):
                limit(by_sha[shas[0]], dict(step='round header'), f'{type(result).__name__}: {result}')
                headers.append(dict(url=urls, read=None, cause=f'{type(result).__name__}: {result}'[:300]))
                continue
            reading = result['reading']
            headers.append(dict(url=urls, read='round header band', request=result['request_sha256'],
                                tables=reading['tables'], issues=reading['issues'],
                                test_columns=vectors.test_columns(reading)))
    except Stopped as stop:
        print(f'STOPPED {stop}; {requests["made"]} requests made before the stop', flush=True)
        sys.exit(3)
    read_headers = [h for h in headers if h.get('read')]
    headers_summary = dict(
        publications=len(header_sources), read=sum(len(h['url']) if isinstance(h['url'], list) else 1
                                                    for h in read_headers),
        tables=sum(len(h['tables']) for h in read_headers if h['tables'] is not None),
        with_test_column=[h['url'] for h in read_headers if h['test_columns']],
        not_read=[h['url'] for h in headers if not h.get('read')])
    print(f'headers: {headers_summary["read"]} of {len(header_sources)} untranscribed publications read '
          f'({headers_summary["tables"]} raster tables); test-result columns in '
          f'{len(headers_summary["with_test_column"])}', flush=True)

    records, found_statements = [], []
    for p in population:
        records += vectors.records_of(p, readings.get(p.sha256, []), statements.get(p.sha256))
        found_statements += vectors.statements_of(p, statements.get(p.sha256))
    for r in records:
        for issue in r.issues:
            limits.append(dict(source=r.source, url=r.url, where=r.cell, cause=issue))
    print(f'complete: {len(population)} publications, {len(transcribed)} rounds transcribed, '
          f'{len(untranscribed_rounds)} later rounds not transcribed, {len(records)} records, '
          f'{len(found_statements)} statements, {len(limits)} reading limits, {requests["made"]} requests made',
          flush=True)
    if args.out:
        def plain(value):
            return value.isoformat() if isinstance(value, date) else str(value)
        args.out.write_text(json.dumps(dict(
            publications=[asdict(p) for p in population],
            records=[asdict(r) for r in records], statements=[asdict(s) for s in found_statements],
            transcribed=[asdict(r) for r in transcribed], untranscribed=[asdict(r) for r in untranscribed_rounds],
            not_transcribed=not_transcribed, limits=limits, headers=headers, headers_summary=headers_summary),
            default=plain, ensure_ascii=False, indent=0))


if __name__ == '__main__':
    main()

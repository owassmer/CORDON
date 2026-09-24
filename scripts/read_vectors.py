#!/usr/bin/env python3
"""Read the vector-monitoring population (INPUTS.md row 12) through `cordon_d.vectors`.

Replays retained readings by default; `--execute` dispatches the missing requests on the
Claude subscription, `--workers` at a time, each only while at least 20% of memory is
free. `--only` selects publications by URL substring. `--out` writes the records,
statements and reading limits as JSON outside the tree; nothing here is an owner.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]

from cordon_d import vectors  # noqa: E402
from cordon_d.store import store_root  # noqa: E402


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--only', action='append', default=[])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--plan', action='store_true', help='stop before the table requests')
    args = parser.parse_args()
    store = store_root(ROOT)
    population = [p for p in vectors.population(ROOT, store)
                  if not args.only or any(o in p.url for o in args.only)]
    limits, lock = [], __import__('threading').Lock()

    def limit(digest, where, error):
        with lock:
            limits.append(dict(source=digest, where=where, cause=f'{type(error).__name__}: {error}'[:500]))

    def gated(function, *a, **k):
        if args.execute:
            wait_for_memory()
        return function(*a, **k)

    # Phase 1: statements of every PDF, layout and table corners of every raster.
    statements, layouts = {}, {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        for p in population:
            if p.kind == 'pdf':
                futures[pool.submit(gated, vectors.read_statements, store, p.sha256, execute=args.execute)] = p
            else:
                futures[pool.submit(gated, vectors.layout, store, p.sha256, execute=args.execute)] = p
        for future in as_completed(futures):
            p = futures[future]
            try:
                (statements if p.kind == 'pdf' else layouts)[p.sha256] = future.result()
            except Exception as error:  # noqa: BLE001
                limit(p.sha256, dict(step='statements' if p.kind == 'pdf' else 'layout'), error)
    print(f'phase 1: {len(statements)} statement readings, {len(layouts)} layouts, {len(limits)} limits', flush=True)

    # Phase 1b: the corner of every table too large for one request.
    corners = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        for p in population:
            if p.sha256 not in layouts:
                continue
            large = [t['box'] for t in layouts[p.sha256]['tables'] if vectors.needs_tiles(t['box'])]
            if not large:
                continue
            raster = vectors._Raster(store, p.sha256)
            for box in large:
                area = (box[0], box[1], min(box[2], box[0] + 1500), min(box[3], box[1] + 1500))
                files = [('corner.png', raster.crop(*area), 'Table corner')]
                prompt = vectors.CORNER_PROMPT.format(width=area[2] - area[0], height=area[3] - area[1])
                futures[pool.submit(gated, vectors.retained, store, 'corner', [p.sha256], prompt,
                                    vectors.CORNER_SCHEMA, files, execute=args.execute,
                                    geometry={'corner': list(area)})] = (p, tuple(box))
            del raster
        for future in as_completed(futures):
            p, box = futures[future]
            try:
                corners[(p.sha256, box)] = future.result()
            except Exception as error:  # noqa: BLE001
                limit(p.sha256, dict(step='corner', table=list(box)), error)
    print(f'phase 1b: {len(corners)} corners, {len(limits)} limits', flush=True)

    # Phase 2: every table tile and every PDF table page.
    tasks, spool = [], Path(tempfile.mkdtemp(prefix='cordon-vector-tiles-'))
    for p in population:
        if p.kind == 'pdf' and p.sha256 in statements:
            for number in statements[p.sha256]['reading']['table_pages']:
                tasks.append((p, dict(page=number), None, None))
        elif p.sha256 in layouts:
            raster = vectors._Raster(store, p.sha256)
            for table in layouts[p.sha256]['tables']:
                box = tuple(table['box'])
                if vectors.needs_tiles(box) and (p.sha256, box) not in corners:
                    continue
                try:
                    packets = vectors.tiles(store, p.sha256, box, corners.get((p.sha256, box)), raster=raster)
                except Exception as error:  # noqa: BLE001
                    limit(p.sha256, dict(step='tiles', table=list(box)), error)
                    continue
                for geometry, png, context in packets:
                    name = spool / f"{p.sha256[:16]}-{len(tasks)}"
                    name.with_suffix('.png').write_bytes(png)
                    if context is not None:
                        name.with_suffix('.context.png').write_bytes(context)
                    tasks.append((p, geometry, name.with_suffix('.png'),
                                  name.with_suffix('.context.png') if context is not None else None))
            del raster
    print(f'phase 2: {len(tasks)} table requests', flush=True)
    if args.plan:
        counts = {}
        for p, geometry, _, _ in tasks:
            counts[p.url.rsplit('/', 1)[-1]] = counts.get(p.url.rsplit('/', 1)[-1], 0) + 1
        print(json.dumps(counts, indent=0))
        shutil.rmtree(spool, ignore_errors=True)
        return

    def read(task):
        p, geometry, png, context = task
        if 'page' in geometry:
            return gated(vectors.read_pdf_page, store, p.sha256, geometry['page'], execute=args.execute)
        where = vectors.WHOLE if geometry['header'] is None else vectors.TILED
        files = [('tile.png', png.read_bytes(), 'Table tile')]
        if context is not None:
            files.append(('left-header.png', context.read_bytes(), vectors.CONTEXT_LABEL))
        return gated(vectors.retained, store, 'table', [p.sha256], vectors.TABLE_PROMPT.format(geometry=where),
                     vectors.TABLE_SCHEMA, files, execute=args.execute, geometry=geometry)

    readings, done = {}, 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(read, task): task for task in tasks}
        for future in as_completed(futures):
            p, geometry = futures[future][:2]
            try:
                readings.setdefault(p.sha256, []).append((geometry, future.result()))
            except Exception as error:  # noqa: BLE001
                limit(p.sha256, geometry, error)
            done += 1
            if done % 20 == 0:
                print(f'{done}/{len(tasks)} read, {len(limits)} limits', flush=True)

    shutil.rmtree(spool, ignore_errors=True)
    records, found_statements = [], []
    for p in population:
        records += vectors.records_of(p, readings.get(p.sha256, []), statements.get(p.sha256))
        found_statements += vectors.statements_of(p, statements.get(p.sha256))
    print(f'complete: {len(population)} publications, {len(records)} records, '
          f'{len(found_statements)} statements, {len(limits)} reading limits', flush=True)
    if args.out:
        def plain(value):
            if isinstance(value, date):
                return value.isoformat()
            return str(value)
        args.out.write_text(json.dumps(dict(
            publications=[asdict(p) for p in population],
            records=[asdict(r) for r in records], statements=[asdict(s) for s in found_statements],
            limits=limits), default=plain, ensure_ascii=False, indent=0))


if __name__ == '__main__':
    main()

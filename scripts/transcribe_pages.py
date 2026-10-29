#!/usr/bin/env python3
"""Transcribe the page images row 9 reads the Art. 136 declarations from: one page image per request, through the
Claude subscription (report_extraction._subscription_call, with one PNG attached).

OCR locates each declaration's decree in its G.U. issue or supplement, and each scheda's identification page; the words
D's rule reads are a vision transcription of those pages (cordon_d.instruments). This script lists the pages and makes
the requests; the ordinary reader (scripts/read_protection.py) reads only the answers held.

    scripts/transcribe_pages.py list
        write the population to POPULATION: one row per declaration and page (declaration, source hash, page, why)
    scripts/transcribe_pages.py run [--page SHA256:PAGE ...] [--workers N]
        transcribe the listed pages not yet held, or only those named

`run` reads the committed list, and refuses where the locator no longer gives exactly that list, so a pass runs the
population that was approved. It runs only under the reading login:

    env -u CLAUDE_CODE_OAUTH_TOKEN CLAUDE_CONFIG_DIR=$HOME/.claude-cordon-reader scripts/transcribe_pages.py run ...

A request that fails, a usage limit included, stops the run; the failure is kept beside the answers under failed/,
never as a reading. Each answer is kept from its first write under derived/page-transcriptions (kept, replicated to
R2 on push).
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import io
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-d'), str(ROOT / 'regulation/stage-c')]
from cordon_d import instruments as I  # noqa: E402
from cordon_d.store import blob_path, store_root  # noqa: E402

POPULATION = ROOT / I.SOURCES / 'transcription-pages.csv'
FIELDS = ('declaration', 'sha256', 'page', 'why')
READING_LOGIN = '.claude-cordon-reader'
MAX_WORKERS = 2   # at most two model readings at once: every builder shares the subscription


def population(store: Path) -> str:
    declared, _, _ = I.declarations(store)
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(FIELDS)
    for row in I.transcription_population(declared):
        writer.writerow((row['code'], row['sha256'], row['page'], row['why']))
    return out.getvalue()


def requests(rows: list[dict]) -> dict[tuple[str, int], list[str]]:
    """Each distinct page the rows name, with the declarations it is in for."""
    pages = {}
    for row in rows:
        pages.setdefault((row['sha256'], int(row['page'])), []).append(row['declaration'])
    return pages


def transcribe(store: Path, sha: str, page: int) -> dict:
    import pymupdf
    from cordon_d.report_extraction import ExtractionConfig, _subscription_call
    document = pymupdf.open(blob_path(store, sha))
    request_id, _, png, label = I.transcription_request(document, sha, page - 1)
    path = I.transcription_path(store, request_id)
    if path.exists():
        return {'request': request_id, 'held': True}
    config = ExtractionConfig(model=I.TRANSCRIPTION_MODEL, effort=I.TRANSCRIPTION_EFFORT, provider='subscription')
    started = time.monotonic()
    answer = _subscription_call(prompt=I.TRANSCRIPTION_PROMPT, schema=I.TRANSCRIPTION_SCHEMA, digest=sha,
                                source=blob_path(store, sha), config=config, request_id=request_id, raw_path=path,
                                attachments=[(f'page-{page}.png', png, label)])
    return {'request': request_id, 'seconds': round(time.monotonic() - started, 1), 'png_bytes': len(png),
            'characters': len(answer['text']), 'illegible': answer['text'].count(I.ILLEGIBLE)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    run = sub.add_parser('run')
    run.add_argument('--page', action='append', default=[], help='SHA256:PAGE, a listed page to transcribe')
    run.add_argument('--workers', type=int, default=1, choices=range(1, MAX_WORKERS + 1))
    args = parser.parse_args()
    store = store_root(ROOT)
    if args.command == 'list':
        POPULATION.write_text(population(store))
        rows = list(csv.DictReader(POPULATION.open()))
        print(f'{POPULATION.relative_to(ROOT)}: {len(rows)} rows, {len(requests(rows))} distinct pages')
        return
    if os.environ.get('CLAUDE_CODE_OAUTH_TOKEN') or not os.environ.get('CLAUDE_CONFIG_DIR', '').rstrip('/').endswith(
            READING_LOGIN):
        sys.exit(f'refused: run under the reading login: env -u CLAUDE_CODE_OAUTH_TOKEN '
                 f'CLAUDE_CONFIG_DIR=$HOME/{READING_LOGIN} {sys.argv[0]} run ...')
    listed = POPULATION.read_text()
    if population(store) != listed:
        sys.exit(f'refused: the locator no longer gives {POPULATION.relative_to(ROOT)}; list it again and have it '
                 f'approved before a pass')
    pages = requests(list(csv.DictReader(io.StringIO(listed))))
    if args.page:
        named = [(sha, int(page)) for sha, page in (p.split(':') for p in args.page)]
        unlisted = [n for n in named if n not in pages]
        if unlisted:
            sys.exit(f'refused: not in the list: {unlisted}')
        pages = {n: pages[n] for n in named}
    print(f'{len(pages)} pages to transcribe ({I.TRANSCRIPTION_MODEL}, {I.TRANSCRIPTION_EFFORT}, '
          f'{I.TRANSCRIPTION_DPI} dpi)', flush=True)
    keys, failed = list(pages), []
    with ThreadPoolExecutor(args.workers) as pool:
        for i in range(0, len(keys), args.workers):   # `workers` requests at a time; a failure stops the run
            wave = {key: pool.submit(transcribe, store, *key) for key in keys[i:i + args.workers]}
            for (sha, page), future in wave.items():
                try:
                    print(json.dumps({'sha256': sha, 'page': page, 'declarations': pages[sha, page]}
                                     | future.result()), flush=True)
                except Exception as error:  # a usage limit included: never waited out, never kept as a reading
                    failed.append(((sha, page), error))
            if failed:
                break
    if failed:
        sys.exit('stopped: ' + '; '.join(f'{sha}:{page}: {error}' for (sha, page), error in failed))


if __name__ == '__main__':
    main()

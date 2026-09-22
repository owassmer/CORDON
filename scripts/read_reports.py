#!/usr/bin/env python3
"""Inventory, explicitly extract, or locally join the admitted laboratory reports."""
import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
import json
import fcntl
from itertools import islice
import logging
from pathlib import Path
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from uuid import uuid4

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPOSITORY / 'regulation/stage-d'), str(REPOSITORY / 'regulation/stage-c')]
from cordon_d.report_extraction import (Budget, BudgetStopped, CODEX_DEFAULT_MODEL, ExtractionConfig,
                                        NoRetainedResponse, SUBSCRIPTION_PROVIDERS,
                                        extract_report, extract_relationships, version)
from cordon_d import report_relations
from cordon_d.reports import Report, reports
from cordon_d.findings import findings, report_rows, confirmation_inputs
from cordon_d.monitoring import distinct_observations
from cordon_d.source_associations import associations
from cordon_d.store import store_root


def encoded(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=str)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def prior_reading_version(store, digest, resume_versions):
    """The retained reading version to replay for this document, or None for a fresh reading.

    A complete assembly is preferred; otherwise the version whose fully read blocks
    cover the most target pages. Retained readings are replayed without model calls;
    only uncovered pages are read afresh.
    """
    best, best_key = None, None
    for candidate in resume_versions:
        path = store / 'derived/reports' / candidate / digest / 'report.json'
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        if payload.get('source_sha256') != digest:
            continue
        from cordon_d.report_extraction import fully_read
        covered = sum(len(b['targets']) for b in payload['blocks']
                      if b['targets'] and fully_read(b['reading']) and not b.get('attachment_repair_pending'))
        key = (payload.get('assembly_complete') is True, covered)
        if best_key is None or key > best_key:
            best, best_key = candidate, key
    return best


def extract_job(digest, store, config, ledger, budget_options, revision, relationships=False, execute=True,
                resume_versions=()):
    try:
        if not relationships and version(config) != revision:
            raise RuntimeError('Reader implementation changed before worker startup; no paid request dispatched')
        reader = extract_relationships if relationships else extract_report
        budget = Budget(ledger, **budget_options) if config.provider == 'api' and execute else None
        options = {}
        if not relationships and resume_versions:
            options['resume_from'] = prior_reading_version(store, digest, resume_versions)
        reader(digest, store, config=config, budget=budget, execute=execute, **options)
        partial = relationships and not report_relations.load(store, digest, exact=True).get('reading_complete', False)
        return {'document': digest, 'status': 'partial relationship reading' if partial else 'assembled'}
    except NoRetainedResponse as error:
        return {'document': digest, 'status': 'unread', 'cause': str(error)}
    except Exception as error:
        return {'document': digest, 'status': 'stopped', 'cause': str(error),
                'budget_stopped': isinstance(error, BudgetStopped)}


CONSECUTIVE_STOPS = 3


def process_parallel(pending, *, workers, store, config, ledger, options, revision, relationships, execute=True,
                     resume_versions=()):
    """Keep at most one job per worker queued.

    A document that stops is recorded and the next one is dispatched: one source's
    defect does not hold the population. Three stops in a row look like the run's
    own failure -- a provider limit, a full disk, a changed implementation -- so
    dispatch halts and the summary says so. The exit status distinguishes the two.
    """
    failures, source, consecutive, halted = [], iter(pending), 0, False
    counts = Counter()

    def submit(pool, digest):
        return pool.submit(extract_job, digest, store, config, ledger, options, revision, relationships, execute,
                           tuple(resume_versions))

    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs = {submit(pool, digest): digest for digest in islice(source, workers)}
        completed = 0
        while jobs:
            job = next(as_completed(jobs))
            jobs.pop(job)
            result = job.result()
            completed += 1
            counts[result['status']] += 1
            print(json.dumps(dict(result, progress=[completed, len(pending)])), flush=True)
            if result['status'] == 'stopped':
                failures.append(result)
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= CONSECUTIVE_STOPS:
                halted = True
            if not halted:
                try:
                    digest = next(source)
                except StopIteration:
                    pass
                else:
                    jobs[submit(pool, digest)] = digest
    print(json.dumps({'summary': dict(counts), 'pending_at_start': len(pending),
                      'halted_after_consecutive_stops': halted,
                      'stopped_documents': [{'document': f['document'], 'cause': f['cause']} for f in failures]}),
          flush=True)
    if halted:
        raise SystemExit(2)
    if failures:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reports-root', type=Path, default=Path('corpus/sources/reports'))
    parser.add_argument('--monitoring-root', type=Path, default=Path('corpus/sources/monitoring'))
    parser.add_argument('--association-root', type=Path, default=Path('corpus/sources/removal-orders'))
    parser.add_argument('--model', default=None,
                        help=f'Reader model; defaults to {ExtractionConfig.model} for api/subscription and '
                             f'{CODEX_DEFAULT_MODEL} for codex')
    parser.add_argument('--provider', choices=['api', 'subscription', 'codex'], default=ExtractionConfig.provider,
                        help='Metered API execution, the authenticated Claude subscription, or the authenticated Codex subscription')
    parser.add_argument('--resume-from', action='append', default=[], metavar='EXTRACTION_VERSION',
                        help='Replay fully read blocks retained under these earlier versions (no model call) and read only uncovered pages')
    parser.add_argument('--effort', choices=['low', 'medium', 'high', 'xhigh', 'max'],
                        default=ExtractionConfig.effort)
    parser.add_argument('--timeout-seconds', type=int, default=ExtractionConfig.timeout_seconds,
                        help='Seconds one model request may take before it is recorded as a failed run')
    parser.add_argument('--extraction-version', help='Select a retained reading version for local consumption only')
    parser.add_argument('--relationships', action='store_true',
                        help='Read whole-document identities and operative references without retranscribing rows')
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument('--execute', action='store_true')
    execution.add_argument('--rebuild-cache', action='store_true', help='Reassemble retained responses with no provider access')
    parser.add_argument('--mark-notes-only', action='store_true',
                        help='With --execute, read only the notes that unresolved printed marks point at; '
                             'every other missing reading stays unread')
    parser.add_argument('--document', action='append', default=[],
                        help='Optional acquired source hash selection; omission processes the complete population')
    parser.add_argument('--max-cost-usd', type=float)
    parser.add_argument('--input-usd-per-million', type=float)
    parser.add_argument('--output-usd-per-million', type=float)
    parser.add_argument('--ledger', type=Path)
    parser.add_argument('--workers', type=int, choices=range(1, 7), default=1,
                        help='Independent PDF processes; API execution shares one locked spending ledger (1-6)')
    parser.add_argument('--retain-interrupted-reservation', metavar='REQUEST_SHA256',
                        help='With execution and its ledger locked, retain an interrupted request at its full reserved cost')
    parser.add_argument('--retry-interrupted-request', action='append', default=[], metavar='REQUEST_SHA256',
                        help='Explicitly permit one retry with no saved response, charging both the old reservation and new attempt')
    parser.add_argument('--join-output', type=Path)
    parser.add_argument('--join-summary', type=Path, help='Full-population consumer census without copying all publication rows')
    parser.add_argument('--confirmation-request', type=Path,
                        help='Explicit observation identity, result_pair and event_date; qualifications remain unresolved')
    parser.add_argument('--known-through', type=datetime.fromisoformat,
                        default=datetime.now(timezone.utc))
    args = parser.parse_args()
    if (args.retain_interrupted_reservation or args.retry_interrupted_request) and not args.execute:
        parser.error('--retain-interrupted-reservation requires --execute and its ledger')
    if args.mark_notes_only and (not args.execute or args.relationships):
        parser.error('--mark-notes-only requires --execute on page readings')
    scope = 'mark notes' if args.mark_notes_only else True
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    model = args.model or (CODEX_DEFAULT_MODEL if args.provider == 'codex' else ExtractionConfig.model)
    config = ExtractionConfig(model=model, effort=args.effort, provider=args.provider,
                              timeout_seconds=args.timeout_seconds,
                              max_tokens=4000 if args.relationships else ExtractionConfig.max_tokens)
    if args.resume_from and args.relationships:
        parser.error('--resume-from applies to page readings, not relationship inventories')
    if args.extraction_version and (args.execute or args.rebuild_cache) and not args.relationships:
        parser.error('--extraction-version selects existing readings; it cannot execute or rebuild them')
    revision = args.extraction_version or version(config)
    store = store_root(args.reports_root)
    captures = json.loads((args.reports_root / 'records.json').read_text())
    digests = sorted({r['sha256'] for r in captures if 'sha256' in r})
    if not set(args.document) <= set(digests):
        parser.error('--document must name an acquired source hash')
    selected = sorted(set(args.document)) if args.document else digests
    def complete(digest):
        if args.relationships:
            reading = report_relations.load(store, digest, exact=True)
            return reading is not None and reading.get('reading_complete') is True
        path = store / 'derived/reports' / revision / digest / 'report.json'
        return path.exists() and json.loads(path.read_text()).get('assembly_complete') is True
    pending = [d for d in selected if not complete(d)]
    print(json.dumps({'execution_model': config.model if args.execute else None, 'extraction_version': revision,
                      'execution_effort': config.effort if args.execute else None,
                      'relationship_reading_version': report_relations.READING_VERSION if args.relationships else None,
                      'retained_partial_relationship_readings': sum(1 for d in selected if args.relationships
                          and (value := report_relations.load(store, d, exact=True)) and not value['reading_complete']),
                      'documents': len(digests), 'selected': len(selected), 'pending': len(pending),
                      'workers': args.workers,
                      'execution_provider': config.provider if args.execute else None,
                      'metered_model_execution': bool(args.execute and config.provider == 'api'),
                      'subscription_execution': bool(args.execute and config.provider in SUBSCRIPTION_PROVIDERS),
                      'execution_scope': ('mark notes only' if args.mark_notes_only else 'all source reads')
                                         if args.execute else None,
                      'resume_from': args.resume_from}), flush=True)
    def process(budget):
        for index, digest in enumerate(pending, 1):
            try:
                reader = extract_relationships if args.relationships else extract_report
                reader(digest, store, config=config, budget=budget, execute=scope)
                partial = args.relationships and not report_relations.load(store, digest, exact=True)['reading_complete']
                print(json.dumps({'document': digest,
                    'status': 'partial relationship reading' if partial else 'assembled',
                    'progress': [index, len(pending)]}), flush=True)
            except Exception as error:
                print(json.dumps({'document': digest, 'status': 'stopped', 'cause': str(error)}), flush=True)
                # Preserve completed blocks. Do not dispatch after an uncertain paid failure.
                raise SystemExit(1) from error
    if args.execute:
        if args.provider == 'api' and not all((args.max_cost_usd, args.input_usd_per_million,
                                              args.output_usd_per_million, args.ledger)):
            parser.error('--execute requires a cap, explicit token prices and a resumable ledger path')
        if args.provider in SUBSCRIPTION_PROVIDERS:
            if any((args.max_cost_usd, args.input_usd_per_million, args.output_usd_per_million, args.ledger)):
                parser.error('Subscription execution does not use API prices or the dollar ledger')
            process_parallel(pending, workers=args.workers, store=store, config=config, ledger=None,
                             options={}, revision=revision, relationships=args.relationships,
                             execute=scope, resume_versions=args.resume_from)
        else:
            args.ledger.parent.mkdir(parents=True, exist_ok=True)
            with args.ledger.with_suffix(args.ledger.suffix + '.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                options = dict(limit=args.max_cost_usd, input_rate=args.input_usd_per_million,
                               output_rate=args.output_usd_per_million, run_id=str(uuid4()))
                budget = Budget(args.ledger, **options)
                if args.retain_interrupted_reservation:
                    budget.retain_interrupted_reservation(args.retain_interrupted_reservation)
                for request_id in args.retry_interrupted_request:
                    if (store / 'derived/reports/responses' / f'{request_id}.json').exists():
                        parser.error('A saved response exists for this request; inspect it instead of retransmitting')
                    budget.retain_interrupted_reservation(request_id, retry=True)
                if args.workers == 1:
                    process(budget)
                else:
                    process_parallel(pending, workers=args.workers, store=store,
                        config=config, ledger=args.ledger, options=options, revision=revision,
                        relationships=args.relationships, execute=scope)
    elif args.rebuild_cache:
        # Reassemble from retained responses only; a document with none is reported unread.
        process_parallel(pending, workers=args.workers, store=store, config=config, ledger=None,
                         options={}, revision=revision, relationships=args.relationships, execute=False,
                         resume_versions=args.resume_from)
    if args.confirmation_request and not (args.join_output or args.join_summary):
        parser.error('--confirmation-request requires --join-output or --join-summary')
    if args.join_output or args.join_summary:
        destination = args.join_output or args.join_summary
        destination.parent.mkdir(parents=True, exist_ok=True)
        import cordon_d.reports as report_mod
        report_mod.REPORT_MEMO = {}
        try:
            routed = []
            stream = findings(distinct_observations(args.monitoring_root), args.reports_root, store,
                              extraction_version=revision, known_through=args.known_through,
                              association_readings=associations(args.association_root, store, known_through=args.known_through)
                                  if (args.association_root / 'records.json').exists() else ())
            counts, statuses, limitations = Counter(), Counter(), Counter()
            routed_urls, unacquired_urls = set(), set()
            output = args.join_output.open('w') if args.join_output else None
            try:
                for item in stream:
                    if output:
                        output.write(json.dumps(item, default=encoded, ensure_ascii=False) + '\n')
                    counts['observations'] += 1
                    if counts['observations'] % 250000 == 0:
                        print(json.dumps({'joined_observations': counts['observations']}), flush=True)
                    statuses[item.get('status', 'no report route recovered')] += 1
                    counts['matched_relationships'] += len(item['matches'])
                    for link in item['links']:
                        routed_urls.add(link['route'])
                        if link.get('status') == 'source route not acquired at knowledge cutoff':
                            unacquired_urls.add(link['route'])
                        limitations[link.get('status', 'unspecified')] += 1
                    if item['observation'].report_routes:
                        routed.append(item)
            finally:
                if output:
                    output.close()
            counts['routed_observations'] = len(routed)
            counts['distinct_routed_urls'] = len(routed_urls)
            counts['unacquired_routed_urls'] = len(unacquired_urls)
            reading_statuses = Counter()
            def readings():
                for reading in reports(args.reports_root, store, extraction_version=revision, known_through=args.known_through):
                    if isinstance(reading, Report):
                        status = 'all pages accounted for' if len(reading.complete_pages) == reading.pages else 'partial page reading'
                        counts['pages_in_started_reports'] += reading.pages
                        counts['pages_reported_read'] += len(reading.complete_pages)
                    else:
                        status = reading.cause
                    reading_statuses[status] += 1
                    yield reading
            output = args.join_output.with_suffix('.report-rows.jsonl').open('w') if args.join_output else None
            try:
                for row in report_rows(readings(), routed):
                    counts['read_report_rows'] += 1
                    counts['unmatched_report_rows'] += not bool(row['observations'])
                    if output:
                        output.write(json.dumps(row, default=encoded, ensure_ascii=False) + '\n')
            finally:
                if output:
                    output.close()
            if args.join_summary:
                args.join_summary.parent.mkdir(parents=True, exist_ok=True)
                args.join_summary.write_text(json.dumps({'extraction_version': revision,
                    'known_through': args.known_through.isoformat(), 'counts': counts,
                    'observation_statuses': statuses, 'route_statuses': limitations,
                    'reading_statuses': reading_statuses, 'unacquired_routes': sorted(unacquired_urls)}, indent=2) + '\n')

            if args.confirmation_request:
                destination = (args.join_output or args.join_summary).with_suffix('.confirmation.json')
                try:
                    from cordon_c.core import Snapshot
                    from cordon_c.bindings import confirmation_facts
                    request = json.loads(args.confirmation_request.read_text())
                    selected = [item for item in routed if list(item['observation'].identity) == request['observation']]
                    if len(selected) != 1:
                        raise ValueError('Requested observation is not uniquely present in the ordinary joined stream')
                    inputs = confirmation_inputs(selected[0], result_pair=request['result_pair'], qualification={})
                    facts = confirmation_facts(Snapshot.load(REPOSITORY), date.fromisoformat(request['event_date']), **inputs)
                    destination.write_text(json.dumps({'observation': request['observation'],
                        'result_pair': request['result_pair'], 'event_date': request['event_date'],
                        'extraction_version': revision, 'inputs': inputs,
                        'evaluations': [{'consumer': key, 'evaluation': value} for key, value in facts.items()]},
                        default=encoded, indent=2) + '\n')
                except (ValueError, KeyError) as error:
                    destination.write_text(json.dumps({'request_path': str(args.confirmation_request),
                        'cause': str(error), 'evaluations': None}, indent=2) + '\n')
                    raise
        finally:
            report_mod.REPORT_MEMO = None

if __name__ == '__main__':
    main()

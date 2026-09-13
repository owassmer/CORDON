#!/usr/bin/env python3
"""Inventory, explicitly extract, or locally join the admitted laboratory reports."""
import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
import json
import fcntl
import logging
from pathlib import Path
import sys

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPOSITORY / 'regulation/stage-d'), str(REPOSITORY / 'regulation/stage-c')]
from cordon_d.report_extraction import Budget, ExtractionConfig, extract_report, version
from cordon_d.reports import Report, reports
from cordon_d.findings import findings, report_rows, confirmation_inputs
from cordon_d.monitoring import distinct_observations
from cordon_d.store import store_root


def encoded(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=str)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reports-root', type=Path, default=Path('corpus/sources/reports'))
    parser.add_argument('--monitoring-root', type=Path, default=Path('corpus/sources/monitoring'))
    parser.add_argument('--model', default=ExtractionConfig.model)
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument('--execute', action='store_true')
    execution.add_argument('--rebuild-cache', action='store_true', help='Reassemble retained responses with no provider access')
    parser.add_argument('--document', action='append', default=[],
                        help='Optional acquired source hash selection; omission processes the complete population')
    parser.add_argument('--max-cost-usd', type=float)
    parser.add_argument('--input-usd-per-million', type=float)
    parser.add_argument('--output-usd-per-million', type=float)
    parser.add_argument('--ledger', type=Path)
    parser.add_argument('--join-output', type=Path)
    parser.add_argument('--join-summary', type=Path, help='Full-population consumer census without copying all publication rows')
    parser.add_argument('--confirmation-request', type=Path,
                        help='Explicit observation identity, result_pair and event_date; qualifications remain unresolved')
    parser.add_argument('--known-through', type=datetime.fromisoformat,
                        default=datetime.now(timezone.utc))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    config = ExtractionConfig(model=args.model)
    revision = version(config)
    store = store_root(args.reports_root)
    captures = json.loads((args.reports_root / 'records.json').read_text())
    digests = sorted({r['sha256'] for r in captures if 'sha256' in r})
    if not set(args.document) <= set(digests):
        parser.error('--document must name an acquired source hash')
    selected = sorted(set(args.document)) if args.document else digests
    def complete(digest):
        path = store / 'derived/reports' / revision / digest / 'report.json'
        return path.exists() and json.loads(path.read_text()).get('assembly_complete') is True
    pending = [d for d in selected if not complete(d)]
    print(json.dumps({'model': config.model, 'extraction_version': revision,
                      'documents': len(digests), 'selected': len(selected), 'pending': len(pending), 'paid_execution': args.execute}), flush=True)
    def process(budget):
        for index, digest in enumerate(pending, 1):
            try:
                extract_report(digest, store, config=config, budget=budget)
                print(json.dumps({'document': digest, 'status': 'assembled', 'progress': [index, len(pending)]}), flush=True)
            except Exception as error:
                print(json.dumps({'document': digest, 'status': 'stopped', 'cause': str(error)}), flush=True)
                # Preserve completed blocks. Do not dispatch after an uncertain paid failure.
                raise SystemExit(1) from error
    if args.execute:
        if not all((args.max_cost_usd, args.input_usd_per_million, args.output_usd_per_million, args.ledger)):
            parser.error('--execute requires a cap, explicit token prices and a resumable ledger path')
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        with args.ledger.with_suffix(args.ledger.suffix + '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            process(Budget(args.ledger, limit=args.max_cost_usd,
                           input_rate=args.input_usd_per_million, output_rate=args.output_usd_per_million))
    elif args.rebuild_cache:
        process(None)
    if args.confirmation_request and not (args.join_output or args.join_summary):
        parser.error('--confirmation-request requires --join-output or --join-summary')
    if args.join_output or args.join_summary:
        destination = args.join_output or args.join_summary
        destination.parent.mkdir(parents=True, exist_ok=True)
        routed = []
        stream = findings(distinct_observations(args.monitoring_root), args.reports_root, store,
                          extraction_version=revision, known_through=args.known_through)
        counts, statuses, limitations = Counter(), Counter(), Counter()
        routed_urls, unacquired_urls = set(), set()
        output = args.join_output.open('w') if args.join_output else None
        try:
            for item in stream:
                if output:
                    output.write(json.dumps(item, default=encoded, ensure_ascii=False) + '\n')
                counts['observations'] += 1
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
        if args.confirmation_request:
            from cordon_c.core import Snapshot
            from cordon_c.bindings import confirmation_facts
            request = json.loads(args.confirmation_request.read_text())
            selected = [item for item in routed if list(item['observation'].identity) == request['observation']]
            if len(selected) != 1:
                raise ValueError('Requested observation is not uniquely present in the ordinary joined stream')
            inputs = confirmation_inputs(selected[0], result_pair=request['result_pair'], qualification={})
            facts = confirmation_facts(Snapshot.load(REPOSITORY), date.fromisoformat(request['event_date']), **inputs)
            destination = (args.join_output or args.join_summary).with_suffix('.confirmation.json')
            destination.write_text(json.dumps({'observation': request['observation'],
                'result_pair': request['result_pair'], 'event_date': request['event_date'],
                'extraction_version': revision, 'inputs': inputs,
                'evaluations': [{'consumer': key, 'evaluation': value} for key, value in facts.items()]},
                default=encoded, indent=2) + '\n')
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


if __name__ == '__main__':
    main()

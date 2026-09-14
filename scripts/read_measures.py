#!/usr/bin/env python3
"""Read one whole measure with its supplied annex context, or replay it offline."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-c'), str(ROOT / 'regulation/stage-d')]
from cordon_d.measures import read_measure
from cordon_d.store import store_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs='+', help='Ordered source SHA-256 values; act first')
    parser.add_argument('--execute', action='store_true', help='Use the allocated Codex subscription worker')
    parser.add_argument('--review-instruction', default='', help='Explicit source-reading correction request')
    args = parser.parse_args()
    result = read_measure(args.sources, store_root(ROOT), execute=args.execute,
                          review_instruction=args.review_instruction)
    print(json.dumps({'request_sha256': result.response['request_sha256'],
                      'reading': result.values}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

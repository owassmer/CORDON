#!/usr/bin/env python3
"""Re-hash every blob in the store; exit 1 if any blob's bytes no longer match its name.

Usage: scripts/audit_store.py [source-root]   (default: corpus/sources/monitoring)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
from cordon_d.store import audit, store_root  # noqa: E402

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'corpus/sources/monitoring')
store = store_root(root)
mismatches = audit(store)
blobs = sum(1 for _ in (store / 'blobs' / 'sha256').glob('*/*')) if (store / 'blobs').is_dir() else 0
for path in mismatches:
    print('MISMATCH', path)
print(f'store={store} blobs={blobs} mismatches={len(mismatches)}')
sys.exit(1 if mismatches else 0)

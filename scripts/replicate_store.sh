#!/usr/bin/env bash
# Replicate the content-addressed store to Cloudflare R2 (S3-compatible), blobs only.
# Derived files are regenerable and are not replicated.
# Usage: CORDON_R2_ACCOUNT=<account id> scripts/replicate_store.sh [source-root]
# CORDON_R2_BUCKET overrides the program bucket, cordon-store.
# Credentials: an R2 API token as AWS profile `r2` in ~/.aws/credentials.
set -euo pipefail
root="${1:-corpus/sources/monitoring}"
here="$(cd "$(dirname "$0")/.." && pwd)"
store="$("$here/.venv/bin/python" -c "import sys; sys.path.insert(0, '$here/regulation/stage-d'); from cordon_d.store import store_root; from pathlib import Path; print(store_root(Path('$root')))")"
: "${CORDON_R2_ACCOUNT:?set CORDON_R2_ACCOUNT}"
: "${CORDON_R2_BUCKET:=cordon-store}"
"$here/scripts/audit_store.py" "$root"
aws s3 sync "$store/blobs" "s3://$CORDON_R2_BUCKET/blobs" \
  --endpoint-url "https://$CORDON_R2_ACCOUNT.r2.cloudflarestorage.com" --profile r2 --no-progress
echo "replicated $(find "$store/blobs" -type f | wc -l | tr -d ' ') blobs to s3://$CORDON_R2_BUCKET/blobs"

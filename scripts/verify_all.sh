#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/verify_stage_a.py
python3 scripts/verify_jurisdiction_stage_a.py
python3 scripts/verify_stage_b.py
python3 scripts/verify_repository.py

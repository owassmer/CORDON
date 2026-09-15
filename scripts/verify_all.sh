#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/verify_stage_a.py
python3 scripts/verify_jurisdiction_stage_a.py
python3 scripts/verify_stage_b.py
python3 -m unittest discover -s scripts -p test_stage_b_repairs.py
cordon_python="${CORDON_PYTHON:-.venv/bin/python}"
if [[ ! -x "$cordon_python" ]]; then
  echo "Set up the Stage C reference environment described in regulation/stage-c/SPEC.md" >&2
  exit 1
fi
PYTHONPATH=regulation/stage-c "$cordon_python" -m unittest discover -s regulation/stage-c -p test_reference.py
PYTHONPATH=regulation/stage-c "$cordon_python" regulation/stage-c/check_mutations.py
PYTHONPATH=regulation/stage-c:regulation/stage-d "$cordon_python" -m unittest discover -s regulation/stage-d -p test_contracts.py
PYTHONPATH=regulation/stage-c:regulation/stage-d "$cordon_python" -m unittest discover -s regulation/stage-d -p test_subjects.py
PYTHONPATH=regulation/stage-c:regulation/stage-d "$cordon_python" -m unittest discover -s regulation/stage-d -p test_subject_reading.py
PYTHONPATH=regulation/stage-c:regulation/stage-d "$cordon_python" regulation/stage-d/verify.py
python3 scripts/verify_repository.py

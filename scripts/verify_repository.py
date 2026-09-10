#!/usr/bin/env python3
"""Verify CORDON's live authority pointers and corpus integrity."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from generate_stage_b import status_for
from verify_stage_b import main as verify_ledger


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def verify_stage_c_acceptance(current: dict) -> None:
    stage = current['stages'].get('C', {})
    if stage.get('status') != 'CLOSED':
        return
    entry = stage['canonical']
    files = sorted(p for p in (ROOT / entry['path']).rglob('*')
                   if p.is_file() and p.suffix in {'.py', '.md', '.json', '.txt'}
                   and '__pycache__' not in p.parts)
    material = ''.join(str(p.relative_to(ROOT)) + '\0' + digest(p) + '\n' for p in files)
    if hashlib.sha256(material.encode()).hexdigest() != entry['sha256']:
        fail('accepted Stage C package changed')
    evidence = stage['acceptance_record']
    path = ROOT / evidence['path']
    if not path.is_file() or digest(path) != evidence['sha256']:
        fail('Stage C acceptance record missing or changed')
    record = json.loads(path.read_text())
    if (record['promoted_package_sha256'] != entry['sha256']
            or record['accepted_by'] != stage['accepted_by']):
        fail('Stage C acceptance record does not bind current content')


def verify_stage_b_projections(current: dict, validated_ledger: dict | None = None) -> None:
    """Check stored consumer files, not a freshly generated substitute."""
    output = ROOT / "regulation/stage-b/generated"
    status_path = output / "generation-status.json"
    if not status_path.is_file():
        fail("missing Stage B generation status")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    stages = current["stages"]
    a_inputs = {item["path"]: digest(ROOT / item["path"])
                for item in stages["A"]["canonical_artifacts"].values()}
    expected = {
        "canonical_sha256": digest(ROOT / stages["B"]["canonical"]["path"]),
        "population_sha256": digest(ROOT / stages["B"]["population"]["path"]),
        "stage_a_inputs": a_inputs,
    }
    for field, value in expected.items():
        if status.get(field) != value:
            fail(f"Stage B generation input mismatch: {field}")
    projections = {}
    for name in ("clocks.csv", "parameters.csv"):
        path = output / name
        if not path.is_file():
            fail(f"missing Stage B projection: {name}")
        projections[name] = digest(path)
    if status.get("generated") != projections:
        fail("Stage B stored projection hash mismatch")
    canonical = ROOT / stages["B"]["canonical"]["path"]
    ledger = validated_ledger if validated_ledger is not None else json.loads(canonical.read_text(encoding="utf-8"))
    expected_status = status_for(ledger, canonical, tuple(ROOT / p for p in a_inputs),
                                 ROOT / stages["B"]["population"]["path"], output, ROOT)
    equivalent = lambda left, right: json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)
    if not equivalent(status, expected_status):
        different = sorted(k for k in set(status) | set(expected_status)
                           if k not in status or k not in expected_status or not equivalent(status[k], expected_status[k]))
        fail(f"Stage B stored status mismatch: {', '.join(different)}")


def main() -> None:
    current = json.loads((ROOT / "state/CURRENT.json").read_text(encoding="utf-8"))
    a = current["stages"]["A"]["canonical_artifacts"]
    checks = [a["eu"], a["italy_and_puglia"], current["stages"]["B"]["canonical"], current["stages"]["B"]["population"]]
    for item in checks:
        path = ROOT / item["path"]
        if not path.is_file():
            fail(f"missing current artifact {item['path']}")
        if digest(path) != item["sha256"]:
            fail(f"current hash mismatch {item['path']}")

    verify_stage_c_acceptance(current)

    b = verify_ledger(ROOT / current["stages"]["B"]["canonical"]["path"],
                      tuple(ROOT / item["path"] for item in a.values()),
                      ROOT / current["stages"]["B"]["population"]["path"])
    verify_stage_b_projections(current, b)
    expected_counts = current["stages"]["B"]["canonical"]["counts"]
    actual_counts = {key: len(b[key]) for key in ("clocks", "parameters", "dispositions")}
    if actual_counts != expected_counts:
        fail(f"Stage B counts differ: {actual_counts}")
    catalog_path = ROOT / "corpus/CATALOG.csv"
    with catalog_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    catalog_by_path = {row["repo_path"]: row for row in rows}
    for row in rows:
        path = ROOT / row["repo_path"]
        if not path.is_file():
            fail(f"catalog path missing: {row['repo_path']}")
        if digest(path) != row["sha256"]:
            fail(f"catalog hash mismatch: {row['repo_path']}")

    with (ROOT / "migration/MANIFEST.csv").open(newline="", encoding="utf-8") as handle:
        migration_rows = list(csv.DictReader(handle))
    for row in migration_rows:
        if row["disposition"] != "VERBATIM_ADMITTED":
            continue
        destination = ROOT / row["destination"]
        if not destination.is_file():
            fail(f"admitted migration path missing: {row['destination']}")
        current_treatment = catalog_by_path.get(row["destination"], {}).get("treatment")
        if current_treatment == "VERBATIM" and digest(destination) != row["source_sha256"]:
            fail(f"verbatim migration mismatch: {row['destination']}")
        if current_treatment not in {"VERBATIM", "REAUTHORED"}:
            fail(f"admitted migration path has no current treatment: {row['destination']}")

    constitutions = ("DESIGN_PRINCIPLES.md", "STAGE_BOUNDARIES.md", "REVIEW_PRINCIPLES.md")
    required = ("AGENTS.md", *constitutions, "migration/MANIFEST.csv")
    for rel in required:
        if not (ROOT / rel).is_file():
            fail(f"missing required file {rel}")
    navigation = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for rel in constitutions:
        if rel not in navigation:
            fail(f"constitutional reference missing from AGENTS.md: {rel}")
    print(json.dumps({"status": "PASS", "catalog_entries": len(rows), "migration_entries": len(migration_rows), "stage_b": actual_counts}, sort_keys=True))


if __name__ == "__main__":
    main()

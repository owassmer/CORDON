#!/usr/bin/env python3
"""Verify CORDON's live authority pointers and corpus integrity."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


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

    b = json.loads((ROOT / current["stages"]["B"]["canonical"]["path"]).read_text(encoding="utf-8"))
    expected_counts = current["stages"]["B"]["canonical"]["counts"]
    actual_counts = {key: len(b[key]) for key in ("clocks", "parameters", "dispositions")}
    if actual_counts != expected_counts:
        fail(f"Stage B counts differ: {actual_counts}")
    acceptance = {str(item["seam"]): item["semantic_acceptance"] for item in b["closure_manifest"]}
    if acceptance != current["stages"]["B"]["semantic_acceptance"]:
        fail("Stage B acceptance differs from current state")

    catalog_path = ROOT / "corpus/CATALOG.csv"
    with catalog_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
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
        if digest(destination) != row["source_sha256"]:
            fail(f"verbatim migration mismatch: {row['destination']}")

    required = ("AGENTS.md", "DESIGN_PRINCIPLES.md", "STAGE_BOUNDARIES.md", "migration/MANIFEST.csv")
    for rel in required:
        if not (ROOT / rel).is_file():
            fail(f"missing required file {rel}")
    print(json.dumps({"status": "PASS", "catalog_entries": len(rows), "migration_entries": len(migration_rows), "stage_b": actual_counts}, sort_keys=True))


if __name__ == "__main__":
    main()

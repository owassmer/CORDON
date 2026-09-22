#!/usr/bin/env python3
"""Regenerate the repository corpus catalog without consulting legacy repos."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def classify(rel: str) -> tuple[str, str, str, str]:
    if rel in {"AGENTS.md", "DESIGN_PRINCIPLES.md", "STAGE_BOUNDARIES.md", "REVIEW_PRINCIPLES.md"}:
        return "constitution", "authority", "REAUTHORED", "general program governance"
    if rel == "state/CURRENT.json":
        return "current_adjudicated_state", "authority", "REAUTHORED", "live operator, stage, and next gate"
    if rel in {"regulation/stage-a/authoring-eu.json", "regulation/jurisdiction/canonical/authoring.json", "regulation/stage-b/clocks-and-parameters.json", "regulation/stage-b/population.json"}:
        return "current_adjudicated_state", "authority", "VERBATIM", "accepted or current stage substance"
    if rel.startswith("regulation/stage-a/") or rel.startswith("regulation/jurisdiction/generated/"):
        return "current_adjudicated_state", "projection_or_contract", "VERBATIM", "canonical projection, schema, or audit input"
    if rel.startswith("regulation/stage-c/"):
        return "current_adjudicated_state", "computational_reference", "REAUTHORED", "Stage C mathematical derivation; acceptance status belongs to CURRENT"
    if rel.startswith("regulation/stage-d/"):
        return "current_adjudicated_state", "evidence_contract", "REAUTHORED", "Stage D evidence derivation; acceptance status belongs to CURRENT"
    if rel.startswith("regulation/"):
        return "working_corpus", "admitted_source", "VERBATIM", "source referenced by current legal authoring"
    if rel.startswith("corpus/evidence/"):
        return "working_corpus", "dated_evidence", "VERBATIM", "research, source, analysis, or review record"
    if rel.startswith("corpus/inventory/"):
        return "working_corpus", "retained_evidence", "VERBATIM", "user-supplied source copy; native provenance and consumer meaning require source reading"
    if rel.startswith("corpus/workbench/stage-c-research/"):
        return "working_corpus", "retained_evidence", "VERBATIM", "retained acquisition or research evidence; source roles and limits in consuming stage contracts"
    if rel.startswith("corpus/workbench/") and rel != "corpus/workbench/.gitkeep":
        return "working_corpus", "provisional_work", "REAUTHORED", "temporary proposed content; no acceptance or operational authority"
    if rel.startswith("skills/"):
        return "procedure", "skill", "REAUTHORED", "generalized intellectual procedure"
    if rel.startswith("scripts/"):
        inherited = {"generate_stage_a_eu_projections.py", "verify_stage_a.py", "generate_jurisdiction_step6.py", "generate_stage_b.py", "verify_stage_b.py"}
        treatment = "VERBATIM" if Path(rel).name in inherited else "REAUTHORED"
        return "production", "executable_or_check", treatment, "canonical generation or verification"
    if rel.startswith("migration/"):
        return "migration_record", "dated_evidence", "REAUTHORED", "migration provenance or disposition"
    return "repository_support", "support", "REAUTHORED", "repository mechanics"


def main() -> None:
    reverse: dict[str, tuple[str, str, str]] = {}
    with (ROOT / "migration/MANIFEST.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["destination"]:
                reverse[row["destination"]] = (row["source_repo"], row["source_path"], row["source_sha256"])

    ignored = {"corpus/CATALOG.csv", "migration/MANIFEST.csv"}
    rows: list[dict[str, str]] = []
    tracked = subprocess.check_output([
        "git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard", "-z",
    ])
    paths = {item.decode() for item in tracked.split(b"\0") if item}
    for rel in sorted(paths):
        if rel in ignored:
            continue
        path = ROOT / rel
        category, status, treatment, supports = classify(rel)
        source_repo, source_path, source_sha256 = reverse.get(rel, ("", "", ""))
        current_sha256 = sha(path)
        evolvable = category in {"constitution", "current_adjudicated_state", "production", "procedure", "repository_support", "migration_record"}
        if treatment == "VERBATIM" and evolvable and source_sha256 and current_sha256 != source_sha256:
            treatment = "REAUTHORED"
        rows.append({
            "repo_path": rel,
            "category": category,
            "epistemic_status": status,
            "treatment": treatment,
            "source_repo": source_repo,
            "source_path": source_path,
            "sha256": current_sha256,
            "rights_status": "refer_to_source_metadata" if treatment == "VERBATIM" else "internal_project_material",
            "supports": supports,
        })
    with (ROOT / "corpus/CATALOG.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"catalog_entries={len(rows)}")


if __name__ == "__main__":
    main()

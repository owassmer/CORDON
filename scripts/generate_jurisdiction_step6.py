#!/usr/bin/env python3
"""Generate the jurisdictional Stage A provision decision-map views.

Legal meaning is authored in canonical/authoring.json. This generator only
projects that meaning. It never recovers authority from historical ledgers or
infers legal meaning from prose.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JURISDICTION = ROOT / "regulation/jurisdiction"
AUTHORING = JURISDICTION / "canonical/authoring.json"
EU_STABLE = ROOT / "regulation/stage-a/stable-provisions.csv"
EU_ANNEXES = ROOT / "regulation/stage-a/annex-versions.csv"
EU_DEPENDENCIES = ROOT / "regulation/stage-a/dependency-manifest.csv"
OUT = JURISDICTION / "generated"

STABLE_FIELDS = [
    "instrument_id", "stable_provision_id", "parent_stable_provision_id",
    "article", "structural_kind",
]
VERSION_FIELDS = [
    "provision_version_id", "instrument_id", "stable_provision_id",
    "effective_from", "effective_to_exclusive", "application_basis",
    "source_uri", "source_snapshot_hashes", "source_snapshot_dates",
    "exact_change_kind", "semantic_change", "actor_role",
    "modality", "true_effect", "false_effect",
    "reserved_decision_owner",
    "evidence_contract", "external_dependencies", "rule_determinacy",
    "authority_judgment_required", "authority_judgment_kind",
    "legal_linguistic_conflict", "semantic_note",
]
DEPENDENCY_FIELDS = [
    "dependency_id", "source_provision_version_id",
    "source_stable_provision_id", "target_ref", "target_instrument",
    "target_provision", "dependency_kind", "status", "note",
]
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: (
                    json.dumps(row.get(field), ensure_ascii=False, separators=(",", ":"))
                    if isinstance(row.get(field), (list, dict)) else row.get(field, "")
                )
                for field in fields
            })


def ast_operator(ast: dict[str, Any]) -> str:
    if "all_of" in ast:
        return "AND"
    if "any_of" in ast:
        return "OR"
    if "not" in ast:
        return "NOT"
    if "route_table" in ast:
        return "ROUTE_TABLE"
    return "ATOM"


def ast_provision_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "provision_ref" and isinstance(child, str):
                refs.append(child)
            else:
                refs.extend(ast_provision_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(ast_provision_refs(child))
    return list(dict.fromkeys(refs))


def split_target(ref: str) -> tuple[str, str]:
    if ":" not in ref:
        return "", ref
    return tuple(ref.split(":", 1))  # type: ignore[return-value]


def main() -> None:
    authored = json.loads(AUTHORING.read_text(encoding="utf-8"))
    if not isinstance(authored, list) or not authored:
        raise AssertionError("canonical authoring must be a non-empty JSON array")
    OUT.mkdir(parents=True, exist_ok=True)

    stable_by_id: dict[str, dict[str, Any]] = {}
    for row in authored:
        sid = row["stable_provision_id"]
        candidate = {field: row.get(field, "") for field in STABLE_FIELDS}
        if sid in stable_by_id and stable_by_id[sid] != candidate:
            raise AssertionError(f"stable identity drift for {sid}")
        stable_by_id[sid] = candidate
    stable = sorted(stable_by_id.values(), key=lambda r: (r["instrument_id"], r["stable_provision_id"]))

    versions = sorted(
        ({field: row.get(field, "") for field in VERSION_FIELDS} for row in authored),
        key=lambda r: (
            r["instrument_id"], r["stable_provision_id"],
            r["effective_from"] or "0000-00-00", r["provision_version_id"],
        ),
    )

    latest = [row for row in authored if row.get("temporal_status") != "SUPERSEDED"]
    historical = [row for row in authored if row.get("temporal_status") == "SUPERSEDED"]
    graphs = [
        {
            "stable_provision_id": row["stable_provision_id"],
            "provision_version_id": row["provision_version_id"],
            "operator": ast_operator(row["condition_ast"]),
            "expression": row["condition_ast"],
            "true_effect": row["true_effect"],
            "false_effect": row["false_effect"],
        }
        for row in sorted(latest, key=lambda r: (r["instrument_id"], r["stable_provision_id"]))
    ]

    with EU_STABLE.open(newline="", encoding="utf-8-sig") as handle:
        eu_stable_tokens = {r["stable_provision_id"].removeprefix("EU-2020-1201:") for r in csv.DictReader(handle)}
    eu_ids = {f"EU-2020-1201:{token}" for token in eu_stable_tokens}
    with EU_ANNEXES.open(newline="", encoding="utf-8-sig") as handle:
        annex_rows = list(csv.DictReader(handle))
    eu_annex_ids = {
        token
        for row in annex_rows
        for token in (
            row.get("annex_version_id", ""),
            f"EU-2020-1201:{row.get('annex_version_id', '')}",
        )
        if token
    }
    with EU_DEPENDENCIES.open(newline="", encoding="utf-8-sig") as handle:
        eu_dependency_rows = list(csv.DictReader(handle))
    accepted_dependency_targets: set[str] = set()
    for dependency in eu_dependency_rows:
        instrument = dependency["target_instrument"]
        provision = dependency["target_provision"]
        accepted_dependency_targets.update({
            f"{instrument}:{provision}",
            f"{instrument}:{provision.replace('Article ', 'Art.')}",
            f"{instrument}:{provision.replace('Articles ', 'Arts.')}",
        })
    canonical_ids = set(stable_by_id)
    dependencies: list[dict[str, str]] = []
    for row in authored:
        higher = list(dict.fromkeys(row.get("higher_authority_dependencies", [])))
        external = list(dict.fromkeys(row.get("external_dependencies", [])))
        ast_refs = ast_provision_refs(row.get("condition_ast", {}))
        refs = list(dict.fromkeys(higher + external + ast_refs))
        for ref in refs:
            target_instrument, target_provision = split_target(ref)
            if ref in canonical_ids:
                status = "RESOLVED_CANONICAL"
                target_instrument = stable_by_id[ref]["instrument_id"]
                target_provision = stable_by_id[ref]["article"] or ref
            elif ref in eu_ids or ref in eu_stable_tokens:
                status = "RESOLVED_ACCEPTED_EU"
                if ref in eu_stable_tokens:
                    target_instrument, target_provision = "EU-2020-1201", ref
            elif ref in eu_annex_ids:
                status = "RESOLVED_ACCEPTED_EU_ANNEX"
            elif ref in accepted_dependency_targets:
                status = "RESOLVED_ACCEPTED_EU_DEPENDENCY"
            else:
                status = "UNRESOLVED_EXPLICIT"
            token = f"{row['provision_version_id']}|{ref}"
            dependencies.append({
                "dependency_id": hashlib.sha256(token.encode()).hexdigest()[:20],
                "source_provision_version_id": row["provision_version_id"],
                "source_stable_provision_id": row["stable_provision_id"],
                "target_ref": ref,
                "target_instrument": target_instrument,
                "target_provision": target_provision,
                "dependency_kind": "+".join(
                    role for role, present in (
                        ("HIGHER_AUTHORITY", ref in higher),
                        ("EXTERNAL_SUPPORT", ref in external and ref not in higher),
                        ("AST_PROVISION_REF", ref in ast_refs),
                    ) if present
                ),
                "status": status,
                "note": "Complete declared dependency inventory with authority subset, external-only support and AST-use roles.",
            })
    dependencies.sort(key=lambda r: (r["source_provision_version_id"], r["target_ref"]))

    write_csv(OUT / "stable-provisions.csv", STABLE_FIELDS, stable)
    write_csv(OUT / "provision-versions.csv", VERSION_FIELDS, versions)
    write_csv(OUT / "dependency-manifest.csv", DEPENDENCY_FIELDS, dependencies)
    (OUT / "condition-graph.json").write_text(
        json.dumps({
            "schema_version": "1.0",
            "graph_scope": "CURRENT_LATEST_VERSIONS_ONLY",
            "historical_versions_excluded": len(historical),
            "historical_provision_version_ids": sorted(row["provision_version_id"] for row in historical),
            "graphs": graphs,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


    generated = [
        "stable-provisions.csv", "provision-versions.csv",
        "condition-graph.json", "dependency-manifest.csv",
    ]
    manifest = {
        "status": "DETERMINISTIC_PROJECTION_OF_CANONICAL_AUTHORING",
        "canonical_authoring": str(AUTHORING.relative_to(ROOT)),
        "canonical_authoring_sha256": sha256(AUTHORING),
        "counts": {
            "stable_provisions": len(stable),
            "provision_versions": len(versions),
            "condition_graphs": len(graphs),
            "historical_versions_excluded_from_current_graph": len(historical),
            "dependencies": len(dependencies),
        },
        "generated": {
            name: {"sha256": sha256(OUT / name)} for name in generated
        },
    }
    (OUT / "generation-status.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Read accepted evidence consumers without assigning meaning from keywords."""

from __future__ import annotations

import ast
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def predicates(node):
    if isinstance(node, dict):
        if "predicate" in node:
            yield node["predicate"]
        for child in node.values():
            yield from predicates(child)
    elif isinstance(node, list):
        for child in node:
            yield from predicates(child)


def inventory(root=ROOT):
    state = json.loads((root / "state/CURRENT.json").read_text())
    entries = list(state["stages"]["A"]["canonical_artifacts"].values())
    entries += [state["stages"]["B"]["canonical"]]
    documents, owners = [], []
    for entry in entries:
        raw = (root / entry["path"]).read_bytes()
        digest = sha256(raw).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Accepted owner changed: {entry['path']}")
        documents.append(json.loads(raw))
        owners.append({"path": entry["path"], "sha256": digest})
    rows = documents[0] + documents[1]
    admission = json.loads((root / "regulation/stage-d/predicate-contracts.json").read_text())["deferred_consumers"]
    unknown = set(admission) - {row["provision_version_id"] for row in rows}
    if unknown:
        raise ValueError(f"D admission names unknown accepted consumers: {sorted(unknown)}")
    groups, declared = defaultdict(list), defaultdict(list)
    for row in rows:
        for text in sorted(set(predicates(row["condition_ast"]))):
            groups[text].append(row["provision_version_id"])
        evidence = row.get("evidence_contract")
        if evidence and evidence != "-":
            declared[evidence].append(row["provision_version_id"])
    callables, structures = [], []
    for path in sorted((root / "regulation/stage-c/cordon_c").glob("*.py")):
        if path.name == "__init__.py":
            continue
        module = ast.parse(path.read_text())
        for node in module.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                callables.append({
                    "consumer": f"{path.stem}.{node.name}",
                    "parameters": [{"name": arg.arg, "annotation": ast.unparse(arg.annotation) if arg.annotation else None}
                                   for arg in args],
                    "source": str(path.relative_to(root)),
                    "line": node.lineno,
                    "doc": ast.get_docstring(node),
                })
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                fields = [{"name": field.target.id,
                           "annotation": ast.unparse(field.annotation)}
                          for field in node.body if isinstance(field, ast.AnnAssign)
                          and isinstance(field.target, ast.Name)]
                if fields:
                    structures.append({"consumer": f"{path.stem}.{node.name}", "fields": fields,
                                       "source": str(path.relative_to(root)), "line": node.lineno})
    refs = json.loads((root / "regulation/stage-c/reference-bindings.json").read_text())
    return {
        "schema": "stage-d-consumer-inventory-v1",
        "claim": "Full accepted source inventory with D admission projected from predicate-contracts.json; retained text is not a live input demand. Semantic evidence sufficiency requires the D contracts and source reading.",
        "upstream_owners": owners,
        "provision_versions": len(rows),
        "predicates": [{"predicate": text, "consumers": uses,
                        "admitted_consumers": [use for use in uses if use not in admission],
                        "intrinsic": text == "no additional condition"}
                       for text, uses in sorted(groups.items())],
        "declared_evidence": [{"evidence": text, "consumers": uses,
                               "admitted_consumers": [use for use in uses if use not in admission]}
                              for text, uses in sorted(declared.items())],
        "clocks": [{k: row[k] for k in row if k in {
            "clock_id", "producer_provision_version_id", "consumer_decision", "kind", "anchor", "unit",
            "source_phrase", "dependency", "dependencies", "qualifications", "notes", "note",
            "window", "applies_when", "completion", "relation", "recurrence"}}
                   for row in documents[2]["clocks"]],
        "parameters": [{k: row[k] for k in row if k in {
            "parameter_id", "producer_provision_version_id", "consumer_decision", "kind", "unit",
            "source_phrase", "scope", "qualifications", "notes", "note", "applies_when", "dependencies", "legal_effect"}}
                       for row in documents[2]["parameters"]],
        "reference_bindings": refs,
        "callables": callables,
        "structures": structures,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the mechanical projection; never assigns contracts")
    args = parser.parse_args()
    result = inventory()
    if args.write:
        (Path(__file__).parent / "consumer-inventory.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: len(result[k]) for k in ["predicates", "declared_evidence", "clocks", "parameters", "reference_bindings", "callables", "structures"]}))

#!/usr/bin/env python3
"""Audit current and historical QuantaLab release tables without modifying them."""
import csv
import json
import sys
from pathlib import Path


def audit(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
    out = {"path": str(path.resolve()), "rows": len(rows), "columns": rd.fieldnames}
    for col in ("TREE", "GRID_CODE", "X", "Y", "YEAR", "SEV", "SEV_A", "qPCR"):
        if col in rd.fieldnames:
            vals = [r[col] for r in rows if r[col] != ""]
            out[col] = {"nonempty": len(vals), "distinct": len(set(vals))}
    if "X" in rd.fieldnames and "Y" in rd.fieldnames:
        coords = [(r["X"], r["Y"]) for r in rows if r["X"] and r["Y"]]
        out["coordinate_pairs"] = {"nonempty": len(coords), "distinct": len(set(coords))}
    return out


if __name__ == "__main__":
    result = [audit(Path(p)) for p in sys.argv[1:]]
    print(json.dumps(result, indent=2))

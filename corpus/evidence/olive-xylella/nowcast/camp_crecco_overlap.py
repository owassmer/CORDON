#!/usr/bin/env python3
"""CAMP olives whose lon/lat fall in the Crecco point-set bbox (UTM 33N)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import shapefile
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
SHP = ROOT / "raw/data/crecco_oqds_insight/pts_OQDS.shp"
XDIR = ROOT / "raw/data/camp_xlsx"
OUT = ROOT / "nowcast/cache/camp_crecco_overlap.json"


def is_olive(s):
    t = str(s).lower()
    return "olea" in t or "olivo" in t


def main():
    r = shapefile.Reader(str(SHP))
    xmin, ymin, xmax, ymax = r.bbox
    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)
    by_file = []
    for p in sorted(XDIR.glob("CAMP_*.xlsx")):
        df = pd.read_excel(p, sheet_name=0)
        cols = {c.upper(): c for c in df.columns}
        if "LATITUDINE" not in cols:
            continue
        lat = pd.to_numeric(df[cols["LATITUDINE"]], errors="coerce")
        lon = pd.to_numeric(df[cols["LONGITUDINE"]], errors="coerce")
        spec = df[cols["SPECIE"]].astype(str) if "SPECIE" in cols else pd.Series([""] * len(df))
        res = df[cols["RISULTATO"]].astype(str) if "RISULTATO" in cols else pd.Series([""] * len(df))
        olive = spec.map(is_olive)
        pos = res.str.lower().str.startswith("pos")
        ok = lat.notna() & lon.notna()
        xs, ys = to_utm.transform(lon[ok].to_numpy(), lat[ok].to_numpy())
        inside_ok = (xs >= xmin) & (xs <= xmax) & (ys >= ymin) & (ys <= ymax)
        inside = pd.Series(False, index=df.index)
        inside.loc[ok] = inside_ok
        rec = {
            "file": p.name,
            "n_in_bbox": int(inside.sum()),
            "n_olive_in_bbox": int((olive & inside).sum()),
            "n_olive_pos_in_bbox": int((olive & pos & inside).sum()),
        }
        by_file.append(rec)
        print(rec, flush=True)
    out = {
        "crecco_n": r.numRecords,
        "bbox_32633": [xmin, ymin, xmax, ymax],
        "note": "axis-aligned bbox of Crecco points, not a convex hull",
        "by_file": by_file,
        "olive_in_bbox": sum(x["n_olive_in_bbox"] for x in by_file),
        "olive_pos_in_bbox": sum(x["n_olive_pos_in_bbox"] for x in by_file),
    }
    OUT.write_text(json.dumps(out, indent=2))
    print("TOTAL olive", out["olive_in_bbox"], "olive+", out["olive_pos_in_bbox"])


if __name__ == "__main__":
    main()

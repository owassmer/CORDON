#!/usr/bin/env python3
"""1:1 match 2021 Crecco-bbox olive diagnostic + to −. Vectorized."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
import shapefile

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "raw/data/camp_xlsx/CAMP_2021.xlsx"
SHP = ROOT / "raw/data/crecco_oqds_insight/pts_OQDS.shp"
OUT = ROOT / "nowcast/cache/experiment1_matches_2021.csv"
OUTJ = ROOT / "nowcast/cache/experiment1_matches_2021.json"
DAY = 30
KM_MAX = 5.0
KM_MIN = 0.06  # 60 m: different 20 m SWIR cell, still same orchard climate


def is_olive(s):
    t = str(s).lower()
    return "olea" in t or "olivo" in t


def cult_key(s):
    t = str(s).strip()
    if t.lower() in {"", "nan", "none", "altro", "****"}:
        return ""
    return t.casefold()


def hav_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1 = np.radians(lat1)
    p2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2 * r * np.arcsin(np.minimum(1.0, np.sqrt(a)))


def main():
    rdr = shapefile.Reader(str(SHP))
    xmin, ymin, xmax, ymax = rdr.bbox
    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)
    df = pd.read_excel(XLSX, sheet_name=0)
    df["date"] = pd.to_datetime(df["DATA_RILEVAMENTO"], errors="coerce")
    df["lat"] = pd.to_numeric(df["LATITUDINE"], errors="coerce")
    df["lon"] = pd.to_numeric(df["LONGITUDINE"], errors="coerce")
    ok = df["lat"].notna() & df["lon"].notna() & df["date"].notna()
    xs, ys = to_utm.transform(df.loc[ok, "lon"].to_numpy(), df.loc[ok, "lat"].to_numpy())
    inside = pd.Series(False, index=df.index)
    inside.loc[ok] = (xs >= xmin) & (xs <= xmax) & (ys >= ymin) & (ys <= ymax)
    olive = df["SPECIE"].map(is_olive)
    pos = df["RISULTATO"].astype(str).str.lower().str.startswith("pos")
    neg = df["RISULTATO"].astype(str).str.lower().str.startswith("neg")
    box = df[olive & inside & ok].copy()
    P = box[pos.reindex(box.index).fillna(False)].reset_index(drop=True)
    N = box[neg.reindex(box.index).fillna(False)].reset_index(drop=True)
    P["_c"] = P["CULTIVAR"].map(cult_key)
    N["_c"] = N["CULTIVAR"].map(cult_key)
    P["_com"] = P["COMUNE"].astype(str).str.casefold()
    N["_com"] = N["COMUNE"].astype(str).str.casefold()
    nlat = N["lat"].to_numpy()
    nlon = N["lon"].to_numpy()
    nday = N["date"].to_numpy()
    ncom = N["_com"].to_numpy()
    nc = N["_c"].to_numpy()
    used = np.zeros(len(N), dtype=bool)
    pairs = []
    unmatched = []
    for i in range(len(P)):
        p = P.iloc[i]
        dt = np.abs((nday - np.datetime64(p["date"])) / np.timedelta64(1, "D"))
        dkm = hav_km(p["lat"], p["lon"], nlat, nlon)
        same = ncom == p["_com"]
        cult_ok = (p["_c"] == "") | (nc == "") | (nc == p["_c"])
        okm = (~used) & (dt <= DAY) & cult_ok & (dkm >= KM_MIN) & (same | (dkm <= KM_MAX))
        if not okm.any():
            unmatched.append(int(p["ID"]))
            continue
        # rank: same comune first, then dist, then date
        score = np.where(same, 0.0, 1.0) * 1e6 + dkm * 1e3 + dt
        score = np.where(okm, score, np.inf)
        j = int(np.argmin(score))
        used[j] = True
        n = N.iloc[j]
        pairs.append({
            "pos_id": int(p["ID"]),
            "neg_id": int(n["ID"]),
            "pos_date": str(p["date"].date()),
            "neg_date": str(n["date"].date()),
            "pos_lat": float(p["lat"]),
            "pos_lon": float(p["lon"]),
            "neg_lat": float(n["lat"]),
            "neg_lon": float(n["lon"]),
            "pos_comune": p["COMUNE"],
            "neg_comune": n["COMUNE"],
            "pos_cultivar": p.get("CULTIVAR") or "",
            "neg_cultivar": n.get("CULTIVAR") or "",
            "same_comune": bool(same[j]),
            "dist_km": round(float(dkm[j]), 3),
            "date_diff_days": int(dt[j]),
            "cultivar_both_known": bool(p["_c"] and n["_c"]),
            "pos_sintomo": p.get("SINTOMO") or "",
            "neg_sintomo": n.get("SINTOMO") or "",
        })
    pd.DataFrame(pairs).to_csv(OUT, index=False)
    summary = {
        "n_olive_box": int(len(box)),
        "n_pos": int(len(P)),
        "n_neg": int(len(N)),
        "n_matched": len(pairs),
        "n_unmatched_pos": len(unmatched),
        "n_same_comune": sum(1 for x in pairs if x["same_comune"]),
        "n_cultivar_locked": sum(1 for x in pairs if x["cultivar_both_known"]),
        "median_dist_km": float(np.median([x["dist_km"] for x in pairs])) if pairs else None,
        "crown_area": "not used — Crecco file is points",
        "drought": "applied at extract, not in this table",
    }
    OUTJ.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Sample NDVI/NDMI for Experiment 1 pairs at fixed lags. Batch by Sentinel-2 scene."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nowcast"))
import join_one_scene as j

PAIRS = ROOT / "nowcast/cache/experiment1_matches_2021.csv"
OUT = ROOT / "nowcast/cache/experiment1_lags_2021.csv"
OUTJ = ROOT / "nowcast/cache/experiment1_lags_2021.json"
LAGS = (-365, -180, -90, -60, -30, 0, 90)
STAC = "https://earth-search.aws.element84.com/v1/search"
BBOX = [17.55, 40.68, 17.75, 40.82]  # Crecco-ish WGS84


def stac_scenes():
    body = {
        "collections": ["sentinel-2-l2a"],
        "bbox": BBOX,
        "datetime": "2020-01-01T00:00:00Z/2022-06-30T23:59:59Z",
        "limit": 200,
        "query": {"eo:cloud_cover": {"lt": 30}},
    }
    req = Request(STAC, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    scenes = []
    for it in data.get("features", []):
        props = it.get("properties", {})
        assets = it.get("assets", {})
        dt = props.get("datetime", "")[:10]
        tile = (props.get("grid:code") or props.get("s2:mgrs_tile") or "")
        if "34TBL" not in str(tile) and "T34TBL" not in str(it.get("id", "")):
            # keep if id contains 34TBL
            if "34TBL" not in it.get("id", ""):
                continue
        hrefs = {}
        for k, want in (("red", "red"), ("nir", "nir"), ("swir16", "swir16"), ("scl", "scl")):
            a = assets.get(want) or assets.get({"red": "B04", "nir": "B08", "swir16": "B11", "scl": "SCL"}[k])
            if a:
                hrefs[k] = a["href"]
        if len(hrefs) < 4:
            continue
        scenes.append({"id": it["id"], "date": dt, "cloud": props.get("eo:cloud_cover"), "hrefs": hrefs})
    scenes.sort(key=lambda s: s["date"])
    return scenes


def nearest(scenes, target: datetime, max_days=10):
    best = None
    for s in scenes:
        d = datetime.fromisoformat(s["date"])
        ad = abs((d - target).days)
        if ad <= max_days and (best is None or ad < best[0]):
            best = (ad, s)
    return None if best is None else best[1]


def main():
    pairs = pd.read_csv(PAIRS)
    print("pairs", len(pairs), "STAC…", flush=True)
    scenes = stac_scenes()
    print("scenes", len(scenes), scenes[0]["date"] if scenes else None, scenes[-1]["date"] if scenes else None, flush=True)
    # assignments
    jobs = []  # scene_id, kind pos/neg, pair_i, lag, lon, lat
    for i, row in pairs.iterrows():
        p0 = datetime.fromisoformat(row["pos_date"])
        for lag in LAGS:
            tgt = p0 + timedelta(days=int(lag))
            sc = nearest(scenes, tgt)
            if sc is None:
                continue
            jobs.append((sc["id"], "pos", i, lag, row["pos_lon"], row["pos_lat"]))
            jobs.append((sc["id"], "neg", i, lag, row["neg_lon"], row["neg_lat"]))
    by = {}
    for jid, kind, i, lag, lon, lat in jobs:
        by.setdefault(jid, []).append((kind, i, lag, lon, lat))
    href_by = {s["id"]: s["hrefs"] for s in scenes}
    date_by = {s["id"]: s["date"] for s in scenes}
    records = []
    for sid, items in by.items():
        hrefs = href_by[sid]
        lons = [t[3] for t in items]
        lats = [t[4] for t in items]
        print("sample", sid, len(items), flush=True)
        red = j.sample_band(hrefs["red"], lons, lats)
        nir = j.sample_band(hrefs["nir"], lons, lats)
        swir = j.sample_band(hrefs["swir16"], lons, lats)
        scl = j.sample_band(hrefs["scl"], lons, lats)
        ndvi = j.ndi(nir, red)
        ndmi = j.ndi(nir, swir)
        scl_i = np.nan_to_num(scl, nan=-1).astype(int)
        ok = np.isin(scl_i, list(j.SCL_OK)) & np.isfinite(ndmi)
        for k, (kind, i, lag, lon, lat) in enumerate(items):
            records.append({
                "pair_i": int(i),
                "lag": int(lag),
                "arm": kind,
                "scene": sid,
                "scene_date": date_by[sid],
                "ndvi": None if not np.isfinite(ndvi[k]) else float(ndvi[k]),
                "ndmi": None if not np.isfinite(ndmi[k]) else float(ndmi[k]),
                "scl_ok": bool(ok[k]),
            })
    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    # pair-level cliffs per lag on scl-ok both arms
    wide = {}
    for (pi, lag), g in out.groupby(["pair_i", "lag"]):
        p = g[g.arm == "pos"]
        n = g[g.arm == "neg"]
        if p.empty or n.empty:
            continue
        if not (bool(p.iloc[0]["scl_ok"]) and bool(n.iloc[0]["scl_ok"])):
            continue
        wide.setdefault(int(lag), {"pos": [], "neg": []})
        wide[int(lag)]["pos"].append(p.iloc[0]["ndmi"])
        wide[int(lag)]["neg"].append(n.iloc[0]["ndmi"])
    lag_stats = {}
    for lag, d in sorted(wide.items()):
        pv, nv = np.array(d["pos"], float), np.array(d["neg"], float)
        m = np.isfinite(pv) & np.isfinite(nv)
        pv, nv = pv[m], nv[m]
        if len(pv) < 20:
            lag_stats[str(lag)] = {"n": int(len(pv))}
            continue
        lag_stats[str(lag)] = {
            "n": int(len(pv)),
            "ndmi_delta": float(pv.mean() - nv.mean()),
            "cliffs": j.cliffs_delta(pv, nv),
            "p": j.mw_u_p(pv, nv)[1],
        }
    summary = {"n_scenes": len(scenes), "n_rows": len(out), "lags": lag_stats}
    OUTJ.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

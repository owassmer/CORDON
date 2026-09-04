#!/usr/bin/env python3
"""Farm-level Xylella exposure profile from the official campaign workbooks.

Computes, for one point (a farm/estate):
  - per campaign: olive tests and olive positives within 1/3/5/10 km rings,
    ring positivity, min distance to an olive positive
  - first campaign with an olive positive inside each ring
  - epidemic-axis front position per campaign (Gallipoli -> Bari projection,
    Gargano cluster excluded), front velocity fits, and the farm's position
    relative to the front

Descriptive product engine. Not the S1 design-adjusted front-rate estimate:
survey geometry shifts between campaigns and positives are felled after
detection. Every output carries those caveats.

Usage:
  front_exposure.py --lat 40.72635 --lon 17.50158 --name "Cantine Amalberga (Ostuni)"
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XDIR = ROOT / "raw/data/camp_xlsx"
CACHE = ROOT / "producers/cache"

CAMPAIGNS = [
    ("2013-14", "CAMP_2013_2014.xlsx"),
    ("2014-15", "CAMP_2014_2015.xlsx"),
    ("2016-17", "CAMP_2016_2017.xlsx"),
    ("2017-18", "CAMP_2017_2018.xlsx"),
    ("2018-19", "CAMP_2018_2019.xlsx"),
    ("2019-20", "CAMP_2019_2020.xlsx"),
    ("2020", "CAMP_2020.xlsx"),
    ("2021", "CAMP_2021.xlsx"),
    ("2022", "CAMP_2022.xlsx"),
    ("2023", "CAMP_2023.xlsx"),
    ("2024", "CAMP_2024.xlsx"),
    ("2025", "CAMP_2025.xlsx"),
]
RADII_KM = [1.0, 3.0, 5.0, 10.0]
AXIS_A = (40.055, 17.992)   # 2013 epicenter area (Gallipoli/Taviano)
AXIS_B = (41.100, 16.900)   # Bari
GARGANO_LAT = 41.35         # excludes the 2025 Cagnano Varano island
KM_PER_DEG_LAT = 110.57


def hav_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2 * r * np.arcsin(np.minimum(1.0, np.sqrt(a)))


def axis_projection(lat, lon):
    """Km along the epicenter->Bari axis, origin at AXIS_A."""
    mean_lat = math.radians((AXIS_A[0] + AXIS_B[0]) / 2.0)
    kx = 111.32 * math.cos(mean_lat)
    ax = (AXIS_B[1] - AXIS_A[1]) * kx
    ay = (AXIS_B[0] - AXIS_A[0]) * KM_PER_DEG_LAT
    norm = math.hypot(ax, ay)
    ux, uy = ax / norm, ay / norm
    x = (np.asarray(lon) - AXIS_A[1]) * kx
    y = (np.asarray(lat) - AXIS_A[0]) * KM_PER_DEG_LAT
    return x * ux + y * uy


def load_combined():
    cache = CACHE / "combined.csv"
    if cache.exists():
        return pd.read_csv(cache)
    frames = []
    for label, name in CAMPAIGNS:
        df = pd.read_excel(XDIR / name, sheet_name=0)
        c = {k.upper(): k for k in df.columns}
        date_c = next((c[k] for k in ("DATA_RILEVAMENTO", "DATA_PRELIVEO",
                                      "DATA_CAMPIONE") if k in c), None)
        out = pd.DataFrame({
            "campaign": label,
            "lat": pd.to_numeric(df[c["LATITUDINE"]], errors="coerce"),
            "lon": pd.to_numeric(df[c["LONGITUDINE"]], errors="coerce"),
        })
        spec = df[c["SPECIE"]].astype(str) if "SPECIE" in c else ""
        res = df[c["RISULTATO"]].astype(str) if "RISULTATO" in c else ""
        out["olive"] = spec.str.lower().str.contains("olea|olivo", regex=True) \
            if "SPECIE" in c else False
        out["pos"] = res.str.lower().str.startswith("pos") if "RISULTATO" in c else False
        if date_c:
            d = pd.to_datetime(df[date_c], errors="coerce")
            out["t"] = d.dt.year + (d.dt.dayofyear - 1) / 365.25
        else:
            out["t"] = np.nan
        frames.append(out.dropna(subset=["lat", "lon"]))
        print(f"loaded {label}: {len(frames[-1])} rows", flush=True)
    allr = pd.concat(frames, ignore_index=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    allr.to_csv(cache, index=False)
    return allr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--name", default="farm")
    args = ap.parse_args()

    allr = load_combined()
    ol = allr[allr.olive].copy()
    ol["d_km"] = hav_km(args.lat, args.lon, ol.lat.to_numpy(), ol.lon.to_numpy())

    rings = []
    for label, _ in CAMPAIGNS:
        g = ol[ol.campaign == label]
        if g.empty:
            continue
        row = {"campaign": label,
               "n_olive_tests_total": int(len(g)),
               "n_olive_pos_total": int(g.pos.sum())}
        gp = g[g.pos]
        row["min_km_to_olive_pos"] = round(float(gp.d_km.min()), 2) if len(gp) else None
        for r_km in RADII_KM:
            in_r = g[g.d_km <= r_km]
            row[f"tests_{r_km:g}km"] = int(len(in_r))
            row[f"pos_{r_km:g}km"] = int(in_r.pos.sum())
        rings.append(row)

    first_pos = {}
    for r_km in RADII_KM:
        hit = next((row["campaign"] for row in rings if row[f"pos_{r_km:g}km"] > 0), None)
        first_pos[f"{r_km:g}km"] = hit

    # Front trace: olive positives south of the Gargano cutoff
    front = []
    fp = ol[ol.pos & (ol.lat < GARGANO_LAT)].copy()
    fp["proj"] = axis_projection(fp.lat.to_numpy(), fp.lon.to_numpy())
    for label, _ in CAMPAIGNS:
        g = fp[fp.campaign == label]
        if len(g) < 20:
            continue
        front.append({
            "campaign": label,
            "n_pos": int(len(g)),
            "front_km_p99": round(float(np.percentile(g.proj, 99)), 1),
            "front_km_p95": round(float(np.percentile(g.proj, 95)), 1),
            "t_mean_pos": round(float(g.t.mean()), 2) if g.t.notna().any() else None,
        })

    def fit(rows, key="front_km_p99"):
        rows = [r for r in rows if r["t_mean_pos"]]
        if len(rows) < 3:
            return None
        x = np.array([r["t_mean_pos"] for r in rows])
        y = np.array([r[key] for r in rows])
        k, b = np.polyfit(x, y, 1)
        return {"km_per_yr": round(float(k), 2), "n_campaigns": len(rows),
                "span": f"{rows[0]['campaign']}..{rows[-1]['campaign']}"}

    post2016 = [r for r in front if r["campaign"] not in ("2013-14", "2014-15")]
    fit_all = fit(post2016)
    fit_recent = fit(post2016[-5:])

    farm_proj = float(axis_projection([args.lat], [args.lon])[0])
    latest = front[-1] if front else None
    rel = None
    if latest:
        rel = round(farm_proj - latest["front_km_p99"], 1)

    out = {
        "name": args.name,
        "lat": args.lat, "lon": args.lon,
        "farm_axis_km": round(farm_proj, 1),
        "first_olive_pos_within": first_pos,
        "rings_by_campaign": rings,
        "front_trace": front,
        "front_fit_2016on": fit_all,
        "front_fit_recent": fit_recent,
        "farm_km_ahead_of_latest_front_p99": rel,
        "caveats": [
            "Survey geometry moves between campaigns; ring counts reflect where "
            "inspectors sampled, not the epidemic alone.",
            "Positives are felled after detection; absence of later positives at "
            "a coordinate is not evidence of recovery (survivorship).",
            "Front trace excludes the Gargano (Cagnano Varano) cluster; axis "
            "projection is descriptive, not the design-adjusted S1 estimate.",
            "2023 workbook covers a partial campaign; 2024 mixes subspecies on "
            "non-olive hosts (olive rows only used here).",
        ],
    }
    slug = re.sub(r"[^a-z0-9]+", "-", args.name.lower()).strip("-")
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / f"exposure_{slug}.json"
    dest.write_text(json.dumps(out, indent=2))

    print(f"\n=== {args.name}  ({args.lat:.5f}, {args.lon:.5f}) ===")
    print(f"axis km {out['farm_axis_km']}  vs latest front p99 "
          f"{latest['front_km_p99'] if latest else 'n/a'}  -> ahead by {rel} km")
    print("first olive positive within:", first_pos)
    print(f"{'campaign':>8} {'tests10':>8} {'pos10':>6} {'pos3':>5} {'pos1':>5} {'minkm':>7}")
    for r in rings:
        print(f"{r['campaign']:>8} {r['tests_10km']:>8} {r['pos_10km']:>6} "
              f"{r['pos_3km']:>5} {r['pos_1km']:>5} "
              f"{str(r['min_km_to_olive_pos']):>7}")
    print("front fits:", fit_all, fit_recent)
    print("wrote", dest)


if __name__ == "__main__":
    main()

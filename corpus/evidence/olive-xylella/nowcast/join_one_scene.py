#!/usr/bin/env python3
"""Join one Sentinel-2 L2A scene to 100 olive PCR points and test NDVI/NDRE/NDMI.

Scene locked: S2A_34TBL_20210812_0_L2A (Earth Search / AWS public COGs), 0.014% cloud.
Labels: Puglia CAMP olives, 1 Jun–15 Sep 2021, inside the scene bbox.
Sample: 50 Positivo + 50 Negativo, seed 42. Drop SCL cloud/shadow after sample; refill.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform as rio_transform

ROOT = Path(__file__).resolve().parents[1]
CAMP = ROOT / "raw/data/CAMP_2020_2022.csv"
OUT_CSV = ROOT / "nowcast/cache/scene_join_100.csv"
OUT_JSON = ROOT / "nowcast/cache/scene_join_100.summary.json"

SCENE_ID = "S2A_34TBL_20210812_0_L2A"
SCENE_DATE = "2021-08-12"
BBOX = (17.40588790275404, 40.50847217859142, 18.753801781030827, 41.52922626241911)
HREFS = {
    "red": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210812_0_L2A/B04.tif",
    "nir": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210812_0_L2A/B08.tif",
    "re1": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210812_0_L2A/B05.tif",
    "swir16": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210812_0_L2A/B11.tif",
    "scl": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210812_0_L2A/SCL.tif",
}
SCL_OK = {4, 5, 7}  # vegetation, not-vegetated, unclassified
SEED = 42
N_EACH = 50
DRAW_EACH = 180  # oversample; tile fringe returns nodata


def parse_coord(s: str):
    if not s:
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def parse_iso(dmy: str):
    parts = dmy.split("/")
    if len(parts) != 3:
        return None
    d, m, y = parts
    return f"{y}-{m.zfill(2)}-{d.zfill(2)}"


def load_candidates():
    west, south, east, north = BBOX
    pos, neg = [], []
    with CAMP.open(encoding="cp1252", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            sp = (row.get("SPECIE") or "").lower()
            if "olea" not in sp and "olivo" not in sp:
                continue
            iso = parse_iso(row.get("DATA_RILEVAMENTO") or "")
            if not iso or not ("2021-06-01" <= iso <= "2021-09-15"):
                continue
            lat = parse_coord(row.get("LATITUDINE") or "")
            lon = parse_coord(row.get("LONGITUDINE") or "")
            if lat is None or lon is None:
                continue
            if not (south <= lat <= north and west <= lon <= east):
                continue
            rec = {
                "id": row["ID"],
                "date": iso,
                "lat": lat,
                "lon": lon,
                "comune": row.get("COMUNE") or "",
                "provincia": row.get("PROVINCIA") or "",
                "cultivar": row.get("CULTIVAR") or "",
                "risultato": row.get("RISULTATO") or "",
                "sintomo": row.get("SINTOMO") or "",
            }
            if rec["risultato"].lower().startswith("pos"):
                pos.append(rec)
            elif rec["risultato"].lower().startswith("neg"):
                neg.append(rec)
    return pos, neg


def filter_on_scl(recs):
    if not recs:
        return []
    lons = [r["lon"] for r in recs]
    lats = [r["lat"] for r in recs]
    scl = sample_band(HREFS["scl"], lons, lats)
    kept = []
    for r, s in zip(recs, scl):
        if np.isfinite(s) and int(s) in SCL_OK:
            kept.append(r)
    return kept


def draw(pos, neg):
    rng = random.Random(SEED)
    if len(pos) < N_EACH or len(neg) < N_EACH:
        raise SystemExit(f"not enough SCL-valid points pos={len(pos)} neg={len(neg)}")
    sample = rng.sample(pos, N_EACH) + rng.sample(neg, N_EACH)
    rng.shuffle(sample)
    return sample


def sample_band(href, lons, lats):
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        with rasterio.open(href) as src:
            xs, ys = rio_transform("EPSG:4326", src.crs, lons, lats)
            vals = np.array([v[0] for v in src.sample(zip(xs, ys))], dtype=float)
            nodata = src.nodata
    if nodata is not None:
        vals = np.where(vals == nodata, np.nan, vals)
    return vals


def ndi(a, b):
    denom = a + b
    out = np.full_like(a, np.nan, dtype=float)
    ok = np.isfinite(a) & np.isfinite(b) & (denom != 0)
    out[ok] = (a[ok] - b[ok]) / denom[ok]
    return out


def cliffs_delta(x, y):
    """Effect size in [-1, 1]. Positive => x tends larger than y."""
    x = np.asarray(x)
    y = np.asarray(y)
    gt = 0
    lt = 0
    for xi in x:
        gt += np.sum(xi > y)
        lt += np.sum(xi < y)
    n = len(x) * len(y)
    return float((gt - lt) / n) if n else float("nan")


def mw_u_p(x, y, n_perm=2000):
    """Two-sided permutation p on Mann–Whitney U. Ties count 0.5. Label-shuffle, not rank-shuffle."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)

    def u_stat(a, b):
        return float(np.sum(a[:, None] > b[None, :]) + 0.5 * np.sum(a[:, None] == b[None, :]))

    u_obs = u_stat(x, y)
    pooled = np.concatenate([x, y])
    n1 = len(x)
    rng = np.random.default_rng(SEED)
    extreme = 0
    null_center = n1 * len(y) / 2.0
    obs = abs(u_obs - null_center)
    for _ in range(n_perm):
        rng.shuffle(pooled)
        u = u_stat(pooled[:n1], pooled[n1:])
        if abs(u - null_center) >= obs - 1e-12:
            extreme += 1
    return float(u_obs), float((extreme + 1) / (n_perm + 1))


def main():
    if not CAMP.exists():
        raise SystemExit(f"missing {CAMP}")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    pos, neg = load_candidates()
    print(f"candidates summer-2021 in tile bbox: pos={len(pos)} neg={len(neg)}")
    print("prefilter on SCL…")
    pos = filter_on_scl(pos)
    neg = filter_on_scl(neg)
    print(f"SCL-valid: pos={len(pos)} neg={len(neg)}")
    rows = draw(pos, neg)
    lons = [r["lon"] for r in rows]
    lats = [r["lat"] for r in rows]

    print("sampling COGs…")
    red = sample_band(HREFS["red"], lons, lats)
    nir = sample_band(HREFS["nir"], lons, lats)
    re1 = sample_band(HREFS["re1"], lons, lats)
    swir = sample_band(HREFS["swir16"], lons, lats)
    scl = sample_band(HREFS["scl"], lons, lats)

    ndvi = ndi(nir, red)
    ndre = ndi(nir, re1)
    ndmi = ndi(nir, swir)

    keep = []
    for i, r in enumerate(rows):
        scl_i = scl[i]
        fringe = (not np.isfinite(red[i])) or (red[i] == 0 and (not np.isfinite(scl_i) or scl_i == 0))
        scl_ok = np.isfinite(scl_i) and int(scl_i) in SCL_OK
        ok = (not fringe) and np.isfinite(ndvi[i]) and scl_ok
        rec = {
            **r,
            "scene_id": SCENE_ID,
            "scene_date": SCENE_DATE,
            "red": None if not np.isfinite(red[i]) else float(red[i]),
            "nir": None if not np.isfinite(nir[i]) else float(nir[i]),
            "re1": None if not np.isfinite(re1[i]) else float(re1[i]),
            "swir16": None if not np.isfinite(swir[i]) else float(swir[i]),
            "scl": None if not np.isfinite(scl_i) else int(scl_i),
            "ndvi": None if not np.isfinite(ndvi[i]) else float(ndvi[i]),
            "ndre": None if not np.isfinite(ndre[i]) else float(ndre[i]),
            "ndmi": None if not np.isfinite(ndmi[i]) else float(ndmi[i]),
            "usable": bool(ok),
        }
        keep.append(rec)

    usable_pos = [r for r in keep if r["usable"] and r["risultato"].lower().startswith("pos")]
    usable_neg = [r for r in keep if r["usable"] and r["risultato"].lower().startswith("neg")]
    if len(usable_pos) < N_EACH or len(usable_neg) < N_EACH:
        raise SystemExit(
            f"not enough usable after SCL/fringe: pos={len(usable_pos)} neg={len(usable_neg)}"
        )
    usable = usable_pos[:N_EACH] + usable_neg[:N_EACH]

    fields = [
        "id", "date", "lat", "lon", "comune", "provincia", "cultivar",
        "risultato", "sintomo", "scene_id", "scene_date",
        "red", "nir", "re1", "swir16", "scl", "ndvi", "ndre", "ndmi", "usable",
    ]
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(usable)

    def pack(name, getter):
        p = np.array([getter(r) for r in usable if r["risultato"].lower().startswith("pos") and getter(r) is not None], float)
        n = np.array([getter(r) for r in usable if r["risultato"].lower().startswith("neg") and getter(r) is not None], float)
        if len(p) < 5 or len(n) < 5:
            return {"n_pos": int(len(p)), "n_neg": int(len(n)), "note": "too few"}
        u, pval = mw_u_p(p, n)
        return {
            "n_pos": int(len(p)),
            "n_neg": int(len(n)),
            "mean_pos": float(p.mean()),
            "mean_neg": float(n.mean()),
            "median_pos": float(np.median(p)),
            "median_neg": float(np.median(n)),
            "delta_mean_pos_minus_neg": float(p.mean() - n.mean()),
            "cliffs_delta": cliffs_delta(p, n),
            "mannwhitney_u": u,
            "perm_p_two_sided": pval,
        }

    summary = {
        "scene_id": SCENE_ID,
        "scene_date": SCENE_DATE,
        "bbox": list(BBOX),
        "candidates_pos": len(pos),
        "candidates_neg": len(neg),
        "sampled_drawn": len(keep),
        "usable_pos_pool": len(usable_pos),
        "usable_neg_pool": len(usable_neg),
        "usable": len(usable),
        "dropped_cloud_or_nodata": len(keep) - len(usable_pos) - len(usable_neg),
        "features": {
            "ndvi": pack("ndvi", lambda r: r["ndvi"]),
            "ndre": pack("ndre", lambda r: r["ndre"]),
            "ndmi": pack("ndmi", lambda r: r["ndmi"]),
        },
        "decision_rule": (
            "A feature 'moves' if |Cliff's delta| >= 0.15 and perm p < 0.05 "
            "on usable points. Direction predicted by disease-as-drought: "
            "positives lower NDVI/NDRE/NDMI than negatives."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

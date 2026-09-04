#!/usr/bin/env python3
"""Experiment 1, branch A1: within-tree temporal anomaly on Sentinel-2.

Branch A0 tested absolute pos-vs-neg NDMI at discrete lags and closed
negative. A1 reframes onset as change detection: for each of the 1,679
matched pairs, build a full 2020-01..2022-02 Sentinel-2 time series at the
positive and negative points (tile 34TBL, Earth Search COGs), express each
observation as a deviation from that pixel's own prior-year same-day-of-year
baseline (median of 2020 + Jan-Feb 2021 observations within +/-15 days of
DOY), and test whether the positive arm's anomaly trajectory declines more
than its matched negative in the 120 days before the diagnostic date.

Pre-registered direction: the positive tree declines more, so the headline
paired feature d_anom_ndmi = mean(pos NDMI anomaly) - mean(neg NDMI anomaly)
over [pos_date-120 d, pos_date-30 d] is < 0 under the disease hypothesis.

Stages (cached, restartable):
  1 extract  - STAC search + per-scene COG sampling of all 3,358 points.
               Cache: nowcast/cache/experiment1_temporal_samples.csv
  2 features - per-pair anomaly features.
               Output: nowcast/cache/experiment1_temporal.csv
  3 infer    - 1 km cluster sign-flip permutation test (10,000 perms,
               seed 42) on each paired feature.
               Output: nowcast/cache/experiment1_temporal_stats.json

Indices: NDVI=(B08-B04)/(B08+B04), NDMI=(B08-B11)/(B08+B11),
NDRE=(B08-B05)/(B08+B05), NMDI=(B08-(B11-B12))/(B08+(B11-B12)).
Only SCL in {4,5,7} counts as valid.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nowcast"))
import join_one_scene as j

PAIRS = ROOT / "nowcast/cache/experiment1_matches_2021.csv"
SAMPLES = ROOT / "nowcast/cache/experiment1_temporal_samples.csv"
FEATURES = ROOT / "nowcast/cache/experiment1_temporal.csv"
STATS = ROOT / "nowcast/cache/experiment1_temporal_stats.json"

STAC = "https://earth-search.aws.element84.com/v1/search"
DATETIME = "2020-01-01T00:00:00Z/2022-02-28T23:59:59Z"
CLOUD_LT = 30
BASELINE_END = "2021-03-01"   # baseline pool: obs strictly before this date
DOY_WINDOW = 15               # +/- days around DOY for the baseline median
MIN_BASELINE = 2              # min baseline obs to define an expectation
PRE_LO, PRE_HI = -120, -30    # anomaly-mean window relative to pos_date
SLOPE_LO, SLOPE_HI = -120, 0  # slope window relative to pos_date
MIN_PRE = 3                   # min valid obs per arm in the anomaly window
SEED = 42
NPERM = 10000

BANDS = {"red": "B04", "nir": "B08", "rededge1": "B05",
         "swir16": "B11", "swir22": "B12", "scl": "SCL"}
INDICES = ("ndvi", "ndmi", "ndre", "nmdi")


# ---------------------------------------------------------------- stage 1

def stac_scenes():
    """All 34TBL sentinel-2-l2a scenes 2020-01..2022-02, cloud < 30, paginated."""
    body = {
        "collections": ["sentinel-2-l2a"],
        "bbox": _bbox(),
        "datetime": DATETIME,
        "limit": 200,
        "query": {"eo:cloud_cover": {"lt": CLOUD_LT}},
    }
    scenes, url, payload = [], STAC, body
    while True:
        req = Request(url, data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
        for it in data.get("features", []):
            props = it.get("properties", {})
            tile = str(props.get("grid:code") or props.get("s2:mgrs_tile") or "")
            if "34TBL" not in tile and "34TBL" not in it.get("id", ""):
                continue
            assets = it.get("assets", {})
            hrefs = {}
            for k, alt in BANDS.items():
                a = assets.get(k) or assets.get(alt)
                if a:
                    hrefs[k] = a["href"]
            if not all(k in hrefs for k in ("red", "nir", "rededge1", "swir16", "scl")):
                continue
            scenes.append({"id": it["id"], "date": props["datetime"][:10],
                           "cloud": props.get("eo:cloud_cover"), "hrefs": hrefs})
        nxt = next((l for l in data.get("links", []) if l.get("rel") == "next"), None)
        if nxt is None:
            break
        url = nxt.get("href", STAC)
        payload = nxt.get("body") or body
    # one scene per (id); sort by date
    uniq = {s["id"]: s for s in scenes}
    return sorted(uniq.values(), key=lambda s: s["date"])


def _bbox():
    p = pd.read_csv(PAIRS)
    lons = pd.concat([p.pos_lon, p.neg_lon])
    lats = pd.concat([p.pos_lat, p.neg_lat])
    return [float(lons.min()) - 0.01, float(lats.min()) - 0.01,
            float(lons.max()) + 0.01, float(lats.max()) + 0.01]


def extract():
    """Sample every scene at every point. Batched by scene; cached by scene."""
    pairs = pd.read_csv(PAIRS)
    pairs["pair_i"] = pairs.index
    pts = pd.concat([
        pairs[["pair_i", "pos_lon", "pos_lat"]]
        .rename(columns={"pos_lon": "lon", "pos_lat": "lat"}).assign(arm="pos"),
        pairs[["pair_i", "neg_lon", "neg_lat"]]
        .rename(columns={"neg_lon": "lon", "neg_lat": "lat"}).assign(arm="neg"),
    ], ignore_index=True)
    lons, lats = pts["lon"].tolist(), pts["lat"].tolist()

    scenes = stac_scenes()
    print(f"points={len(pts)} scenes={len(scenes)} "
          f"({scenes[0]['date']}..{scenes[-1]['date']})", flush=True)

    done = set()
    if SAMPLES.exists():
        done = set(pd.read_csv(SAMPLES, usecols=["scene"])["scene"].unique())
        print(f"cache: {len(done)} scenes already sampled", flush=True)

    header_needed = not SAMPLES.exists()
    for si, sc in enumerate(scenes):
        if sc["id"] in done:
            continue
        print(f"[{si + 1}/{len(scenes)}] {sc['id']} cloud={sc['cloud']:.1f}",
              flush=True)
        try:
            b = {}
            for k in ("red", "nir", "rededge1", "swir16", "scl"):
                b[k] = j.sample_band(sc["hrefs"][k], lons, lats)
            if "swir22" in sc["hrefs"]:
                b["swir22"] = j.sample_band(sc["hrefs"]["swir22"], lons, lats)
            else:
                b["swir22"] = np.full(len(pts), np.nan)
        except Exception as e:  # network / COG failure: skip scene, keep going
            print(f"  SKIP {sc['id']}: {e}", flush=True)
            continue
        ndvi = j.ndi(b["nir"], b["red"])
        ndmi = j.ndi(b["nir"], b["swir16"])
        ndre = j.ndi(b["nir"], b["rededge1"])
        dsw = b["swir16"] - b["swir22"]
        nmdi = j.ndi(b["nir"], dsw)
        scl_i = np.nan_to_num(b["scl"], nan=-1).astype(int)
        ok = np.isin(scl_i, list(j.SCL_OK))
        rows = pd.DataFrame({
            "scene": sc["id"], "scene_date": sc["date"],
            "pair_i": pts["pair_i"].values, "arm": pts["arm"].values,
            "ndvi": np.round(ndvi, 5), "ndmi": np.round(ndmi, 5),
            "ndre": np.round(ndre, 5), "nmdi": np.round(nmdi, 5),
            "scl": scl_i, "scl_ok": ok,
        })
        rows.to_csv(SAMPLES, mode="a", header=header_needed, index=False)
        header_needed = False
    print("extract done", flush=True)


# ---------------------------------------------------------------- stage 2

def _doy(dates):
    return pd.to_datetime(dates).dt.dayofyear.to_numpy()


def _baseline_expect(base_doy, base_val, target_doy):
    """Median of baseline values within a circular +/-DOY_WINDOW of each target DOY."""
    out = np.full(len(target_doy), np.nan)
    nb = np.full(len(target_doy), 0)
    for i, d in enumerate(target_doy):
        diff = np.abs(base_doy - d)
        diff = np.minimum(diff, 365 - diff)
        m = diff <= DOY_WINDOW
        nb[i] = int(m.sum())
        if nb[i] >= MIN_BASELINE:
            out[i] = np.median(base_val[m])
    return out, nb


def _slope(days, vals):
    if len(days) < 3 or np.ptp(days) < 20:
        return np.nan
    return float(np.polyfit(np.asarray(days, float), np.asarray(vals, float), 1)[0])


def features():
    pairs = pd.read_csv(PAIRS)
    pairs["pair_i"] = pairs.index
    s = pd.read_csv(SAMPLES)
    s = s[s["scl_ok"]]
    s["scene_date"] = pd.to_datetime(s["scene_date"])
    s["doy"] = s["scene_date"].dt.dayofyear
    baseline_end = pd.Timestamp(BASELINE_END)
    pos_date = pd.to_datetime(pairs.set_index("pair_i")["pos_date"])

    recs = []
    for (pi, arm), g in s.groupby(["pair_i", "arm"]):
        pd0 = pos_date.loc[pi]
        g = g.sort_values("scene_date")
        base = g[g["scene_date"] < baseline_end]
        rec = {"pair_i": pi, "arm": arm,
               "n_obs": len(g), "n_baseline": len(base)}
        rel = (g["scene_date"] - pd0).dt.days.to_numpy()
        pre_anom = (rel >= PRE_LO) & (rel <= PRE_HI)
        pre_slope = (rel >= SLOPE_LO) & (rel <= SLOPE_HI)
        for idx in INDICES:
            bv = base[idx].to_numpy(float)
            bd = base["doy"].to_numpy()
            bm = np.isfinite(bv)
            exp, _ = _baseline_expect(bd[bm], bv[bm], g["doy"].to_numpy())
            anom = g[idx].to_numpy(float) - exp
            va = np.isfinite(anom)
            # (a) anomaly mean in the pre-diagnostic window
            m = pre_anom & va
            rec[f"{idx}_n_pre"] = int(m.sum())
            rec[f"{idx}_anom_pre"] = float(np.mean(anom[m])) if m.sum() >= MIN_PRE else np.nan
            # (c) slope of the raw index and of the anomaly over the last 120 d
            vr = np.isfinite(g[idx].to_numpy(float))
            ms = pre_slope & vr
            rec[f"{idx}_slope"] = _slope(rel[ms], g[idx].to_numpy(float)[ms]) if ms.sum() >= MIN_PRE else np.nan
            msa = pre_slope & va
            rec[f"{idx}_anom_slope"] = _slope(rel[msa], anom[msa]) if msa.sum() >= MIN_PRE else np.nan
            # change-point proxy: late (-60..0) minus early (-120..-60) anomaly
            late = (rel > -60) & (rel <= 0) & va
            early = (rel >= -120) & (rel <= -60) & va
            rec[f"{idx}_step"] = (float(np.mean(anom[late]) - np.mean(anom[early]))
                                  if late.sum() >= 2 and early.sum() >= 2 else np.nan)
        recs.append(rec)

    arm_df = pd.DataFrame(recs)
    wide = arm_df.pivot(index="pair_i", columns="arm")
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    for idx in INDICES:
        wide[f"d_anom_{idx}"] = wide[f"{idx}_anom_pre_pos"] - wide[f"{idx}_anom_pre_neg"]
        wide[f"d_slope_{idx}"] = wide[f"{idx}_slope_pos"] - wide[f"{idx}_slope_neg"]
        wide[f"d_anom_slope_{idx}"] = wide[f"{idx}_anom_slope_pos"] - wide[f"{idx}_anom_slope_neg"]
        wide[f"d_step_{idx}"] = wide[f"{idx}_step_pos"] - wide[f"{idx}_step_neg"]

    out = wide.merge(
        pairs[["pair_i", "pos_date", "pos_comune", "pos_cultivar",
               "cultivar_both_known", "pos_sintomo", "neg_sintomo",
               "pos_lat", "pos_lon"]], on="pair_i")
    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)
    px, py = to_utm.transform(out["pos_lon"].to_numpy(), out["pos_lat"].to_numpy())
    out["cluster"] = (np.floor(px / 1000).astype(int).astype(str) + "_"
                      + np.floor(py / 1000).astype(int).astype(str))
    out.to_csv(FEATURES, index=False)
    print(f"features: {len(out)} pairs -> {FEATURES}", flush=True)
    return out


# ---------------------------------------------------------------- stage 3

def signflip(delta, clusters, rng):
    """Sign-flip permutation on median(delta), flipping whole 1 km clusters.

    Returns (obs_median, two_sided_p, one_sided_p_neg) where the one-sided p
    is for the pre-registered direction median < 0.
    """
    d = np.asarray(delta, float)
    obs = np.median(d)
    uniq = np.unique(clusters)
    hits2 = hits1 = 0
    for _ in range(NPERM):
        flips = dict(zip(uniq, rng.choice([-1.0, 1.0], size=len(uniq))))
        s = np.array([flips[c] for c in clusters])
        m = np.median(d * s)
        if abs(m) >= abs(obs):
            hits2 += 1
        if m <= obs:
            hits1 += 1
    return (float(obs), (hits2 + 1) / (NPERM + 1), (hits1 + 1) / (NPERM + 1))


def infer(feat=None):
    if feat is None:
        feat = pd.read_csv(FEATURES)
    rng = np.random.default_rng(SEED)
    out = {"nperm": NPERM, "seed": SEED,
           "cluster": "1 km UTM33 grid of the positive, whole-cluster sign flip",
           "preregistered": "d_anom_ndmi < 0 (positive arm declines more, "
                            f"window {PRE_LO}..{PRE_HI} d before pos_date)",
           "n_pairs_total": int(len(feat)),
           "features": {}}
    cols = ([f"d_anom_{i}" for i in INDICES]
            + [f"d_slope_{i}" for i in INDICES]
            + [f"d_anom_slope_{i}" for i in INDICES]
            + [f"d_step_{i}" for i in INDICES])
    for c in cols:
        sub = feat[np.isfinite(feat[c])]
        n = len(sub)
        if n < 20:
            out["features"][c] = {"n": n}
            continue
        med, p2, p1 = signflip(sub[c].to_numpy(), sub["cluster"].to_numpy(), rng)
        d = sub[c].to_numpy(float)
        out["features"][c] = {
            "n": n,
            "n_clusters": int(sub["cluster"].nunique()),
            "median": round(med, 6),
            "mean": round(float(d.mean()), 6),
            "frac_neg": round(float((d < 0).mean()), 4),
            "p_two_sided": round(p2, 5),
            "p_one_sided_neg": round(p1, 5),
        }
    STATS.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("extract", "all"):
        extract()
    if stage in ("features", "all"):
        features()
    if stage in ("infer", "all"):
        infer()


if __name__ == "__main__":
    main()

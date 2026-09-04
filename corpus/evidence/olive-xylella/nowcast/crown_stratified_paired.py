#!/usr/bin/env python3
"""Paired ΔNDMI re-test stratified by crown purity (branch A2).

Mirrors nowcast/experiment1_paired.py: ΔNDMI = pos − neg per pair,
1 km-cluster sign-flip permutation on median(Δ), 10000 perms, seed 42.
Strata: terciles and halves of the positive tree's 20 m crown fraction
(Otsu threshold), plus sensitivity strata at fixed NDVI thresholds and
by 10 m crown fraction. Lags −90, −60, −30, 0.

Writes nowcast/cache/crown_stratified_paired.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ROOT / "nowcast/cache/experiment1_matches_2021.csv"
LAGS = ROOT / "nowcast/cache/experiment1_lags_2021.csv"
CROWN = ROOT / "nowcast/cache/crown_fraction_2021.csv"
OUT = ROOT / "nowcast/cache/crown_stratified_paired.json"
SEED = 42
NPERM = 10000
LAGS_KEEP = [-90, -60, -30, 0]


def signflip_p(delta, clusters, rng):
    d = np.asarray(delta, float)
    obs = np.median(d)
    uniq = np.unique(clusters)
    hits = 0
    for _ in range(NPERM):
        flips = dict(zip(uniq, rng.choice([-1.0, 1.0], size=len(uniq))))
        s = np.array([flips[c] for c in clusters])
        if abs(np.median(d * s)) >= abs(obs):
            hits += 1
    return float(obs), (hits + 1) / (NPERM + 1)


def block(sub, rng):
    d = sub["dndmi"].to_numpy(float)
    n = len(d)
    if n < 20:
        return {"n": n}
    med, p = signflip_p(d, sub["cluster"].to_numpy(), rng)
    return {
        "n": n,
        "median_delta": round(med, 5),
        "mean_delta": round(float(d.mean()), 5),
        "frac_neg": round(float((d < 0).mean()), 4),
        "p_signflip_cluster": round(p, 5),
        "n_clusters": int(sub["cluster"].nunique()),
        "median_pos_crownfrac20": round(float(sub["pos_crownfrac20"].median()), 4),
    }


def main():
    rng = np.random.default_rng(SEED)
    pairs = pd.read_csv(PAIRS)
    pairs["pair_i"] = pairs.index
    lags = pd.read_csv(LAGS)
    crown = pd.read_csv(CROWN)

    piv = lags.pivot_table(index=["pair_i", "lag"], columns="arm",
                           values=["ndmi", "scl_ok"], aggfunc="first")
    piv.columns = [f"{a}_{b}" for a, b in piv.columns]
    piv = piv.reset_index()
    ok = (piv["scl_ok_pos"].astype(bool) & piv["scl_ok_neg"].astype(bool)
          & piv["ndmi_pos"].notna() & piv["ndmi_neg"].notna())
    w = piv[ok].copy()
    w["dndmi"] = w["ndmi_pos"] - w["ndmi_neg"]
    w = w[w["lag"].isin(LAGS_KEEP)]
    w = w.merge(pairs[["pair_i", "pos_lat", "pos_lon"]], on="pair_i")
    w = w.merge(crown, on="pair_i", how="left")

    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)
    px, py = to_utm.transform(w["pos_lon"].to_numpy(), w["pos_lat"].to_numpy())
    w["cluster"] = (np.floor(px / 1000).astype(int).astype(str) + "_"
                    + np.floor(py / 1000).astype(int).astype(str))

    # Tercile / half edges from pair-level (not row-level) pos_crownfrac20.
    def edges(col, probs):
        v = crown[col].dropna()
        return [float(np.percentile(v, p)) for p in probs]

    out = {"nperm": NPERM, "seed": SEED,
           "cluster": "1 km grid, sign-flip by cluster", "strata": {}}

    schemes = {
        "terciles_pos20_otsu": ("pos_crownfrac20", 3),
        "halves_pos20_otsu": ("pos_crownfrac20", 2),
        "terciles_pos20_fixed_100": ("pos_crownfrac20_fixed_100", 3),
        "terciles_pos20_fixed_150": ("pos_crownfrac20_fixed_150", 3),
        "terciles_pos10_otsu": ("pos_crownfrac10", 3),
    }

    # Pair-level purity controls. ΔNDMI correlates with Δcrownfrac
    # (r≈0.45): more canopy in the pos cell than the neg cell raises
    # ΔNDMI mechanically. Two confound-controlled schemes:
    #   balanced_*: |pos_cf − neg_cf| < 0.10, stratified by pair mean cf.
    #   min_*: stratified by min(pos_cf, neg_cf); 'high' = both arms pure.
    w["mean_cf20"] = (w["pos_crownfrac20"] + w["neg_crownfrac20"]) / 2
    both_cf = w["pos_crownfrac20"].notna() & w["neg_crownfrac20"].notna()
    w["min_cf20"] = np.where(
        both_cf, np.minimum(w["pos_crownfrac20"], w["neg_crownfrac20"]), np.nan)
    w["abs_dcf20"] = (w["pos_crownfrac20"] - w["neg_crownfrac20"]).abs()

    for scheme, col, k, subset in [
        ("balanced_halves_mean20", "mean_cf20", 2, w["abs_dcf20"] < 0.10),
        ("balanced_terciles_mean20", "mean_cf20", 3, w["abs_dcf20"] < 0.10),
        ("min_terciles_20", "min_cf20", 3, w["min_cf20"].notna()),
    ]:
        wl = w[subset & w[col].notna()].copy()
        pairlvl = wl.drop_duplicates("pair_i")[col]
        probs = [100 * i / k for i in range(1, k)]
        e = [float(np.percentile(pairlvl, p)) for p in probs]
        labels = ["low", "mid", "high"] if k == 3 else ["low", "high"]
        bins = [-np.inf] + e + [np.inf]
        wl["stratum"] = pd.cut(wl[col], bins=bins, labels=labels)
        entry = {"edges": [round(x, 4) for x in e],
                 "n_rows": int(len(wl)), "lags": {}}
        for lag in LAGS_KEEP:
            g = wl[wl.lag == lag]
            entry["lags"][str(lag)] = {
                s: block(g[g.stratum == s], rng) for s in labels}
        out["strata"][scheme] = entry

    for scheme, (col, k) in schemes.items():
        if col not in w.columns:
            continue
        probs = [100 * i / k for i in range(1, k)]
        e = edges(col, probs)
        labels = (["low", "mid", "high"] if k == 3 else ["low", "high"])
        bins = [-np.inf] + e + [np.inf]
        entry = {"edges": [round(x, 4) for x in e], "lags": {}}
        wl = w[w[col].notna()].copy()
        wl["stratum"] = pd.cut(wl[col], bins=bins, labels=labels)
        for lag in LAGS_KEEP:
            g = wl[wl.lag == lag]
            entry["lags"][str(lag)] = {
                s: block(g[g.stratum == s], rng) for s in labels}
        out["strata"][scheme] = entry

    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

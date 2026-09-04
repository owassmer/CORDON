#!/usr/bin/env python3
"""Paired re-analysis of Experiment 1 lags. ΔNDMI = pos − neg per pair.

Steps 1-3 and 5 of the paired protocol:
  1 paired stats + scene-lag error + unique 20 m cells
  2 leave-Ostuni-out
  3 cultivar-locked subset + per-cultivar
  5 symptom-absent both arms
Drought: within-pair Δ cancels shared meteorology at ~68 m; plus a
scene-background split (median NDMI of negative arms per scene).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ROOT / "nowcast/cache/experiment1_matches_2021.csv"
LAGS = ROOT / "nowcast/cache/experiment1_lags_2021.csv"
OUT = ROOT / "nowcast/cache/experiment1_paired.json"
SEED = 42
NPERM = 10000


def signflip_p(delta, clusters, rng):
    """Two-sided sign-flip permutation on median(Δ), flipping whole clusters."""
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


def block(sub, rng, label):
    """Paired stats for one lag subset. sub has dndmi, cluster."""
    d = sub["dndmi"].to_numpy(float)
    n = len(d)
    if n < 20:
        return {"label": label, "n": n}
    med, p = signflip_p(d, sub["cluster"].to_numpy(), rng)
    return {
        "label": label,
        "n": n,
        "median_delta": round(med, 5),
        "mean_delta": round(float(d.mean()), 5),
        "frac_neg": round(float((d < 0).mean()), 4),
        "p_signflip_cluster": round(p, 5),
        "n_clusters": int(sub["cluster"].nunique()),
    }


def main():
    rng = np.random.default_rng(SEED)
    pairs = pd.read_csv(PAIRS)
    pairs["pair_i"] = pairs.index
    lags = pd.read_csv(LAGS)

    # wide: one row per (pair_i, lag) with both arms scl_ok + finite
    piv = lags.pivot_table(
        index=["pair_i", "lag"], columns="arm",
        values=["ndmi", "scl_ok"], aggfunc="first",
    )
    piv.columns = [f"{a}_{b}" for a, b in piv.columns]
    piv = piv.reset_index()
    ok = (
        piv["scl_ok_pos"].astype(bool) & piv["scl_ok_neg"].astype(bool)
        & piv["ndmi_pos"].notna() & piv["ndmi_neg"].notna()
    )
    w = piv[ok].copy()
    w["dndmi"] = w["ndmi_pos"] - w["ndmi_neg"]
    w = w.merge(
        pairs[["pair_i", "pos_comune", "pos_cultivar", "neg_cultivar",
               "cultivar_both_known", "pos_sintomo", "neg_sintomo",
               "pos_lat", "pos_lon", "neg_lat", "neg_lon", "pos_date"]],
        on="pair_i",
    )

    # spatial cluster = 1 km grid cell of the positive (UTM33)
    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)
    px, py = to_utm.transform(w["pos_lon"].to_numpy(), w["pos_lat"].to_numpy())
    w["cluster"] = (np.floor(px / 1000).astype(int).astype(str) + "_"
                    + np.floor(py / 1000).astype(int).astype(str))

    # unique 20 m cells across both arms (per lag)
    nx, ny = to_utm.transform(w["neg_lon"].to_numpy(), w["neg_lat"].to_numpy())
    w["pos_cell"] = (np.floor(px / 20).astype(int).astype(str) + "_"
                     + np.floor(py / 20).astype(int).astype(str))
    w["neg_cell"] = (np.floor(nx / 20).astype(int).astype(str) + "_"
                     + np.floor(ny / 20).astype(int).astype(str))

    # scene-vs-target lag error
    sd = lags[lags.arm == "pos"][["pair_i", "lag", "scene_date"]].drop_duplicates()
    sd = sd.merge(pairs[["pair_i", "pos_date"]], on="pair_i")
    tgt = pd.to_datetime(sd["pos_date"]) + pd.to_timedelta(sd["lag"], unit="D")
    err = (pd.to_datetime(sd["scene_date"]) - tgt).dt.days.abs()
    sd["err"] = err

    # scene background = median NDMI of negative arms per scene
    bg = (lags[(lags.arm == "neg") & lags.scl_ok & lags.ndmi.notna()]
          .groupby("scene")["ndmi"].median().rename("scene_bg"))
    pos_scene = lags[lags.arm == "pos"][["pair_i", "lag", "scene"]].drop_duplicates()
    w = w.merge(pos_scene, on=["pair_i", "lag"], how="left").merge(bg, on="scene", how="left")

    sint_abs = (w["pos_sintomo"].astype(str).str.lower().str.startswith("ass")
                & w["neg_sintomo"].astype(str).str.lower().str.startswith("ass"))
    cult_lock = w["cultivar_both_known"].astype(bool)

    def cult_norm(s):
        return str(s).strip().casefold()

    out = {"nperm": NPERM, "cluster": "1 km grid, sign-flip by cluster", "lags": {}}
    for lag, g in w.groupby("lag"):
        lag = int(lag)
        e = sd[sd.lag == lag]["err"]
        entry = {
            "all": block(g, rng, "all"),
            "unique_cells": {
                "rows": int(len(g)),
                "unique_pos_cells": int(g["pos_cell"].nunique()),
                "unique_neg_cells": int(g["neg_cell"].nunique()),
                "unique_all_cells": int(pd.concat([g["pos_cell"], g["neg_cell"]]).nunique()),
            },
            "scene_lag_error_days": {
                "median": float(e.median()) if len(e) else None,
                "p90": float(e.quantile(0.9)) if len(e) else None,
                "max": float(e.max()) if len(e) else None,
            },
            "ostuni_out": block(g[g.pos_comune.str.casefold() != "ostuni"], rng, "ostuni_out"),
            "ostuni_only": block(g[g.pos_comune.str.casefold() == "ostuni"], rng, "ostuni_only"),
            "cultivar_locked": block(g[cult_lock.reindex(g.index).fillna(False)], rng, "cultivar_locked"),
            "sintomo_absent_both": block(g[sint_abs.reindex(g.index).fillna(False)], rng, "sintomo_absent"),
        }
        # per-cultivar within locked
        gl = g[cult_lock.reindex(g.index).fillna(False)].copy()
        if len(gl):
            gl["cn"] = gl["pos_cultivar"].map(cult_norm)
            percult = {}
            for c, gg in gl.groupby("cn"):
                if len(gg) >= 30:
                    percult[c] = block(gg, rng, c)
            entry["by_cultivar"] = percult
            entry["cultivar_composition"] = gl["cn"].value_counts().head(8).to_dict()
        # background dry/wet split
        gb = g[g.scene_bg.notna()].copy()
        if len(gb) >= 60:
            med = gb.scene_bg.median()
            entry["bg_dry"] = block(gb[gb.scene_bg <= med], rng, "bg_dry")
            entry["bg_wet"] = block(gb[gb.scene_bg > med], rng, "bg_wet")
        out["lags"][str(lag)] = entry

    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

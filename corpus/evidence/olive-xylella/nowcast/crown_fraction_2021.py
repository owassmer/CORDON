#!/usr/bin/env python3
"""Crown fraction of Sentinel-2 cells from 2021 WV2 0.5 m NDVI (branch A2).

Product semantics (measured, see CROWN_DILUTION.md): 2021_WV2_NDVI.tif is a
0.5 m grayscale RENDER of NDVI (uint8 0-255, bands 1-3 identical, band 4
alpha). White (255) outside the CLC olive-grove clip is nodata fill. The
2021_WV2_RGB.tif shares the grid; its nodata is black (0,0,0). Valid mask =
RGB not black. Within valid data, crowns are bright, soil dark.

Canopy = NDVI gray > threshold (Otsu on valid pixels; fixed alternatives for
sensitivity). For each of the 1,679 matched pairs, computes canopy fraction
of the positive and negative tree's 20 m and 10 m UTM33 grid cell.

Writes nowcast/cache/crown_fraction_2021.csv (pair_i, pos_crownfrac20,
neg_crownfrac20, pos_crownfrac10, neg_crownfrac10, + sensitivity columns)
and nowcast/cache/crown_fraction_2021_meta.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
NDVI_TIF = ROOT / "raw/data/crecco_oqds_insight/2021_WV2_NDVI.tif"
RGB_TIF = ROOT / "raw/data/crecco_oqds_insight/2021_WV2_RGB.tif"
PAIRS = ROOT / "nowcast/cache/experiment1_matches_2021.csv"
OUT = ROOT / "nowcast/cache/crown_fraction_2021.csv"
META = ROOT / "nowcast/cache/crown_fraction_2021_meta.json"
MIN_VALID_FRAC = 0.30  # cell must have >=30% valid WV2 pixels


def otsu(vals, nbins=256):
    hist, edges = np.histogram(vals, bins=nbins, range=(0, 255))
    hist = hist.astype(float)
    centers = (edges[:-1] + edges[1:]) / 2
    w = hist / hist.sum()
    cum_w = np.cumsum(w)
    cum_mu = np.cumsum(w * centers)
    mu_t = cum_mu[-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        between = (mu_t * cum_w - cum_mu) ** 2 / (cum_w * (1 - cum_w))
    between[~np.isfinite(between)] = 0
    return float(centers[int(np.argmax(between))])


def main():
    src = rasterio.open(NDVI_TIF)
    gray = src.read(1)
    rgb = rasterio.open(RGB_TIF)
    assert rgb.shape == src.shape and rgb.transform == src.transform
    r, g, b = rgb.read(1), rgb.read(2), rgb.read(3)
    valid = ~((r == 0) & (g == 0) & (b == 0))
    del r, g, b
    print("valid fraction of raster:", round(float(valid.mean()), 4))

    v = gray[valid]
    thr_otsu = otsu(v)
    qs = np.percentile(v, [1, 5, 25, 50, 75, 90, 95, 99])
    frac255 = float((v == 255).mean())
    print("valid-pixel gray quantiles(1,5,25,50,75,90,95,99):", qs.round(1))
    print(f"Otsu threshold on valid pixels = {thr_otsu:.2f}; frac==255 {frac255:.4f}")

    thresholds = {"otsu": thr_otsu, "fixed_100": 100.0, "fixed_150": 150.0}
    canopy = {k: (gray > t) & valid for k, t in thresholds.items()}

    tf = src.transform
    x0, y0 = tf.c, tf.f  # top-left corner
    res = tf.a  # 0.5

    def cell_stats(mask, x, y, size):
        cx0 = np.floor(x / size) * size
        cy0 = np.floor(y / size) * size
        c0 = int(round((cx0 - x0) / res))
        c1 = int(round((cx0 + size - x0) / res))
        r0 = int(round((y0 - (cy0 + size)) / res))
        r1 = int(round((y0 - cy0) / res))
        c0c, c1c = max(c0, 0), min(c1, src.width)
        r0c, r1c = max(r0, 0), min(r1, src.height)
        total = (c1 - c0) * (r1 - r0)
        if c0c >= c1c or r0c >= r1c:
            return np.nan, 0.0
        vv = valid[r0c:r1c, c0c:c1c]
        nval = int(vv.sum())
        if nval < MIN_VALID_FRAC * total:
            return np.nan, nval / total
        m = mask[r0c:r1c, c0c:c1c]
        return float(m[vv].mean()), nval / total

    pairs = pd.read_csv(PAIRS)
    pairs["pair_i"] = pairs.index
    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)

    rows = []
    for _, p in pairs.iterrows():
        px, py = to_utm.transform(p.pos_lon, p.pos_lat)
        nx, ny = to_utm.transform(p.neg_lon, p.neg_lat)
        rec = {"pair_i": int(p.pair_i)}
        for name in thresholds:
            suf = "" if name == "otsu" else f"_{name}"
            for arm, (X, Y) in {"pos": (px, py), "neg": (nx, ny)}.items():
                f20, vf20 = cell_stats(canopy[name], X, Y, 20)
                f10, vf10 = cell_stats(canopy[name], X, Y, 10)
                rec[f"{arm}_crownfrac20{suf}"] = f20
                rec[f"{arm}_crownfrac10{suf}"] = f10
                if name == "otsu":
                    rec[f"{arm}_validfrac20"] = round(vf20, 3)
                    rec[f"{arm}_validfrac10"] = round(vf10, 3)
        rows.append(rec)

    df = pd.DataFrame(rows)
    lead = ["pair_i", "pos_crownfrac20", "neg_crownfrac20",
            "pos_crownfrac10", "neg_crownfrac10"]
    df = df[lead + [c for c in df.columns if c not in lead]]
    df.to_csv(OUT, index=False)

    both = df.pos_crownfrac20.notna() & df.neg_crownfrac20.notna()
    meta = {
        "raster": NDVI_TIF.name,
        "crs": str(src.crs),
        "resolution_m": [abs(tf.a), abs(tf.e)],
        "bounds": list(src.bounds),
        "shape": [src.height, src.width],
        "dtype": "uint8 grayscale NDVI render (bands 1-3 identical, band 4 alpha)",
        "nodata_rule": "RGB pixel black (0,0,0) => nodata; NDVI 255 outside clip is fill",
        "valid_fraction_of_raster": round(float(valid.mean()), 4),
        "min_valid_frac_per_cell": MIN_VALID_FRAC,
        "gray_quantiles_valid_1_5_25_50_75_90_95_99": [round(float(q), 1) for q in qs],
        "frac_255_within_valid": round(frac255, 4),
        "threshold_otsu": round(thr_otsu, 2),
        "thresholds_sensitivity": thresholds,
        "n_pairs": int(len(df)),
        "n_pairs_both_arms_frac20": int(both.sum()),
        "n_pos_frac20": int(df.pos_crownfrac20.notna().sum()),
        "n_neg_frac20": int(df.neg_crownfrac20.notna().sum()),
        "pos_crownfrac20_quantiles_10_25_50_75_90": [
            round(float(q), 4) for q in
            np.nanpercentile(df.pos_crownfrac20, [10, 25, 50, 75, 90])],
        "neg_crownfrac20_quantiles_10_25_50_75_90": [
            round(float(q), 4) for q in
            np.nanpercentile(df.neg_crownfrac20, [10, 25, 50, 75, 90])],
    }
    META.write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()

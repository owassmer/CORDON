#!/usr/bin/env python3
"""Branch A7 — super-resolve Sentinel-2 to ~2.5 m over the Crecco pair box and
re-run the paired ΔNDMI test on the matched 2021 cohort.

Pre-registered direction: positive arm drier, Δ = pos − neg < 0.

Engines:
  difffusr    DiffFuSR (NorskRegnesentral, MIT, arXiv 2506.11764): diffusion RGB
              SR (BlindSRSNF, NAIP-harmonized ckpt) + MTFNetFusion NN fusion of
              all 12 bands to 2.5 m. Weights: huggingface.co/NorskRegnesentralSTI/DiffFuSR
  sen2srlite  SEN2SRLite (ESA OpenSR / tacofoundation SEN2SR, SPAN CNN):
              10-band 10 m cube -> 2.5 m. Weights already in
              nowcast/cache/sr_model/SEN2SRLite (mlstac download).
  bicubic     CONTROL ONLY. Bicubic x4 upsample of the same 10 m cube. Never
              reported as SR.

Subcommands:
  fetch          windowed COG reads of the 12 bands for the 21 scenes at lags
                 -90/-60/-30/0 into nowcast/cache/sr_scenes/*.npz
  run ENGINE     super-resolve + sample per-point crown-masked SR-NDMI ->
                 nowcast/cache/sr_values_ENGINE.csv
  stats          paired tests + sanity checks -> nowcast/cache/sr_paired.json/.csv

Scene grid: EPSG:32634 (tile 34TBL). Crop window snapped to the 60 m grid so
10/20/60 m bands align. Reflectance = DN/10000 (2021 = pre-baseline-4 COGs, no
BOA offset), clipped to [0, 1] for model input.

Crown mask: 2021 WV2 0.5 m NDVI render (EPSG:32633), Otsu threshold on valid
pixels, valid = RGB not black — identical recipe to crown_fraction_2021.py.
A 2.5 m SR pixel is "crown" if >=50% of its 0.5 m subsamples are canopy and
>=50% are valid. Per tree: mean SR-NDMI over crown pixels whose centers lie
within 3.0 m of the point (secondary: the bare 2.5 m pixel containing the point).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "nowcast/cache"
SCENES_DIR = CACHE / "sr_scenes"
PAIRS_CSV = CACHE / "experiment1_matches_2021.csv"
LAGS_CSV = CACHE / "experiment1_lags_2021.csv"
CROWN_CSV = CACHE / "crown_fraction_2021.csv"
NDVI_TIF = ROOT / "raw/data/crecco_oqds_insight/2021_WV2_NDVI.tif"
RGB_TIF = ROOT / "raw/data/crecco_oqds_insight/2021_WV2_RGB.tif"
OUT_JSON = CACHE / "sr_paired.json"
OUT_CSV = CACHE / "sr_paired.csv"

LAGS_USED = [-90, -60, -30, 0]
SEED = 42
NPERM = 10000
RADIUS_M = 3.0
SR_RES = 2.5
MARGIN_M = 240.0  # around the pair bbox, keeps 3 m discs + tiles inside

COG_BASE = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL"
BANDS_10 = ["B02", "B03", "B04", "B08"]
BANDS_20 = ["B05", "B06", "B07", "B8A", "B11", "B12"]
BANDS_60 = ["B01", "B09"]
# 12-band standard order used by DiffFuSR BAND_STATS "lr"
ORDER12 = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"]
# SEN2SRLite input/output order
ORDER10_LITE = ["B04", "B03", "B02", "B08", "B05", "B06", "B07", "B8A", "B11", "B12"]

TILE_LR = 128       # 10 m px
TILE_TRIM = 8       # LR px trimmed from each interior tile edge before mosaic
SCALE = 4

DIFFFUSR_DIR = CACHE / "sr_model/DiffFuSR"
DIFFFUSR_CKPT = CACHE / ("sr_model/DiffFuSR_ckpt/logs/blindsrsnf_aniso_naip_degraded_harm_large/"
                         "version_1/checkpoint/last.ckpt")
DIFFFUSR_HPARAMS = CACHE / ("sr_model/DiffFuSR_ckpt/logs/blindsrsnf_aniso_naip_degraded_harm_large/"
                            "version_1/hparams.yaml")
DIFFFUSR_FUSION_CKPT = CACHE / ("sr_model/DiffFuSR_ckpt/logs/GSD/lightning_logs/version_64/"
                                "checkpoints/latest-GSD-epoch=45-metric_val=0.667-loss_train=0.0368.ckpt")
SEN2SRLITE_DIR = CACHE / "sr_model/SEN2SRLite"


# ---------------------------------------------------------------- geometry --
def scene_meta():
    """Distinct scenes used at LAGS_USED, from the frozen lags CSV."""
    lags = pd.read_csv(LAGS_CSV)
    lags = lags[lags.lag.isin(LAGS_USED)]
    sc = lags[["scene", "scene_date"]].drop_duplicates().sort_values("scene_date")
    return sc.reset_index(drop=True), lags


def crop_window():
    """Snapped UTM34 crop covering all pair points + margin.

    Returns (x0, y0_top, w10, h10): top-left corner and size in 10 m px,
    x0/y0 multiples of 60 so the 20 m and 60 m grids align.
    """
    from pyproj import Transformer
    pairs = pd.read_csv(PAIRS_CSV)
    lon = np.r_[pairs.pos_lon, pairs.neg_lon]
    lat = np.r_[pairs.pos_lat, pairs.neg_lat]
    tr = Transformer.from_crs(4326, 32634, always_xy=True)
    x, y = tr.transform(lon, lat)
    x0 = math.floor((x.min() - MARGIN_M) / 60) * 60
    x1 = math.ceil((x.max() + MARGIN_M) / 60) * 60
    y1 = math.ceil((y.max() + MARGIN_M) / 60) * 60  # top
    y0 = math.floor((y.min() - MARGIN_M) / 60) * 60
    # clamp to tile 34TBL raster extent (origin 199980, 4600020; 109800 m wide).
    # 244 pairs have their positive west of the tile edge; those arms are
    # native-nodata (scl_ok False) in the lags CSV and are excluded anyway.
    x0 = max(x0, 199980)
    y1 = min(y1, 4600020)
    return x0, y1, (x1 - x0) // 10, (y1 - y0) // 10


def cog_url(scene, band):
    d = scene.split("_")[2]  # YYYYMMDD
    return f"{COG_BASE}/{d[:4]}/{int(d[4:6])}/{scene}/{band}.tif"


# ------------------------------------------------------------------- fetch --
def cmd_fetch():
    import rasterio
    from rasterio.windows import Window
    SCENES_DIR.mkdir(exist_ok=True)
    x0, ytop, w10, h10 = crop_window()
    print(f"crop UTM34 x0={x0} ytop={ytop} {w10}x{h10} @10m")
    sc, _ = scene_meta()
    env = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
               CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif")
    for _, row in sc.iterrows():
        out = SCENES_DIR / f"{row.scene}.npz"
        if out.exists():
            print("have", row.scene)
            continue
        t = time.time()
        arrs = {}
        with rasterio.Env(**env):
            for band in BANDS_10 + BANDS_20 + BANDS_60:
                res = 10 if band in BANDS_10 else (20 if band in BANDS_20 else 60)
                with rasterio.open(cog_url(row.scene, band)) as src:
                    assert src.crs.to_epsg() == 32634
                    col = (x0 - src.transform.c) / res
                    r0 = (src.transform.f - ytop) / res
                    assert abs(col - round(col)) < 1e-6 and abs(r0 - round(r0)) < 1e-6
                    win = Window(round(col), round(r0), w10 * 10 // res, h10 * 10 // res)
                    a = src.read(1, window=win)
                    assert a.shape == (h10 * 10 // res, w10 * 10 // res), \
                        f"{band} window clipped: {a.shape}"
                    arrs[band] = a
        np.savez_compressed(out, x0=x0, ytop=ytop, **arrs)
        print(f"fetched {row.scene} {time.time()-t:.1f}s")


# ------------------------------------------------------------ crown mask ---
def load_crown_mask():
    """WV2 canopy + valid boolean arrays and the affine params (EPSG:32633)."""
    import rasterio
    src = rasterio.open(NDVI_TIF)
    gray = src.read(1)
    rgb = rasterio.open(RGB_TIF)
    r, g, b = rgb.read(1), rgb.read(2), rgb.read(3)
    valid = ~((r == 0) & (g == 0) & (b == 0))
    del r, g, b
    v = gray[valid]
    hist, edges = np.histogram(v, bins=256, range=(0, 255))
    hist = hist.astype(float)
    centers = (edges[:-1] + edges[1:]) / 2
    w = hist / hist.sum()
    cw, cmu = np.cumsum(w), np.cumsum(w * centers)
    with np.errstate(divide="ignore", invalid="ignore"):
        between = (cmu[-1] * cw - cmu) ** 2 / (cw * (1 - cw))
    between[~np.isfinite(between)] = 0
    thr = float(centers[int(np.argmax(between))])
    canopy = (gray > thr) & valid
    tf = src.transform
    return canopy, valid, (tf.c, tf.f, tf.a), thr, src.shape


def point_pixel_table():
    """Per unique arm point: SR pixels within RADIUS_M + crown fraction each.

    Returns DataFrame: point_id, arm rows with lists of (r, c) SR indices split
    into crown / all, plus the center pixel index and the 20 m cell block.
    """
    from pyproj import Transformer
    x0, ytop, w10, h10 = crop_window()
    W4, H4 = w10 * SCALE, h10 * SCALE
    pairs = pd.read_csv(PAIRS_CSV)
    pairs["pair_i"] = pairs.index
    pts = pd.concat([
        pairs[["pair_i", "pos_lon", "pos_lat"]].rename(columns={"pos_lon": "lon", "pos_lat": "lat"}).assign(arm="pos"),
        pairs[["pair_i", "neg_lon", "neg_lat"]].rename(columns={"neg_lon": "lon", "neg_lat": "lat"}).assign(arm="neg"),
    ], ignore_index=True)
    tr34 = Transformer.from_crs(4326, 32634, always_xy=True)
    px, py = tr34.transform(pts.lon.to_numpy(), pts.lat.to_numpy())
    pts["x34"], pts["y34"] = px, py

    canopy, valid, (wx0, wy0, wres), thr, _ = load_crown_mask()
    tr_33 = Transformer.from_crs(32634, 32633, always_xy=True)

    # candidate pixel offsets around the containing pixel
    offs = [(dr, dc) for dr in range(-2, 3) for dc in range(-2, 3)]
    sub = np.arange(-1.0, 1.01, 0.5)  # 5x5 subsamples inside a 2.5 m pixel
    sub_dx, sub_dy = np.meshgrid(sub, sub)
    sub_dx, sub_dy = sub_dx.ravel(), sub_dy.ravel()

    n = len(pts)
    # candidate centers for all points at once
    c0 = np.floor((px - x0) / SR_RES).astype(int)
    r0 = np.floor((ytop - py) / SR_RES).astype(int)
    rows_out = []
    for k in range(n):
        cand = []
        for dr, dc in offs:
            r, c = r0[k] + dr, c0[k] + dc
            if not (0 <= r < H4 and 0 <= c < W4):
                continue
            cx = x0 + (c + 0.5) * SR_RES
            cy = ytop - (r + 0.5) * SR_RES
            if (cx - px[k]) ** 2 + (cy - py[k]) ** 2 <= RADIUS_M ** 2:
                cand.append((r, c, cx, cy))
        crown_px, all_px = [], []
        for r, c, cx, cy in cand:
            sx, sy = tr_33.transform(cx + sub_dx, cy + sub_dy)
            ci = np.round((sx - wx0) / wres - 0.5).astype(int)
            ri = np.round((wy0 - sy) / wres - 0.5).astype(int)
            ok = (ri >= 0) & (ri < canopy.shape[0]) & (ci >= 0) & (ci < canopy.shape[1])
            if not ok.any():
                all_px.append((r, c)); continue
            vfrac = valid[ri[ok], ci[ok]].mean() * ok.mean()
            if vfrac >= 0.5:
                vv = valid[ri[ok], ci[ok]]
                cfrac = canopy[ri[ok], ci[ok]][vv].mean() if vv.any() else 0.0
                if cfrac >= 0.5:
                    crown_px.append((r, c))
            all_px.append((r, c))
        # 20 m cell block (8x8 SR px) containing the point, snapped to UTM34 20 m grid
        cellx = math.floor(px[k] / 20) * 20
        celly = math.floor(py[k] / 20) * 20
        bc = round((cellx - x0) / SR_RES)
        br = round((ytop - (celly + 20)) / SR_RES)
        rows_out.append({
            "pair_i": int(pts.pair_i.iloc[k]), "arm": pts.arm.iloc[k],
            "crown_px": crown_px, "all_px": all_px,
            "center_px": (int(r0[k]), int(c0[k])) if 0 <= r0[k] < H4 and 0 <= c0[k] < W4 else None,
            "cell_block": (br, bc),
        })
    return pd.DataFrame(rows_out), thr


# ---------------------------------------------------------------- engines ---
def build_cube10(dat):
    """12-band reflectance cube on the 10 m grid (bilinear up for 20/60 m)."""
    import torch
    h10, w10 = dat["B04"].shape
    cube = np.zeros((12, h10, w10), np.float32)
    for i, b in enumerate(ORDER12):
        a = dat[b].astype(np.float32) / 10000.0
        if a.shape != (h10, w10):
            t = torch.from_numpy(a)[None, None]
            a = torch.nn.functional.interpolate(
                t, size=(h10, w10), mode="bilinear", align_corners=False)[0, 0].numpy()
        cube[i] = a
    return np.clip(cube, 0.0, 1.0)


def tile_windows(h, w):
    """LR tile windows with trim-based mosaic. Yields (r0,r1,c0,c1, tr0,tr1,tc0,tc1)
    where t* is the region of the tile (in LR px, tile-local) kept in the mosaic."""
    step = TILE_LR - 2 * TILE_TRIM
    rs = list(range(0, max(h - TILE_LR, 0) + 1, step))
    if rs[-1] != h - TILE_LR:
        rs.append(max(h - TILE_LR, 0))
    cs = list(range(0, max(w - TILE_LR, 0) + 1, step))
    if cs[-1] != w - TILE_LR:
        cs.append(max(w - TILE_LR, 0))
    for r in rs:
        for c in cs:
            yield r, c


def tiles_needed(h, w, ppt):
    """LR tile origins that cover at least one evaluation pixel.

    Other tiles never enter the paired statistic. Same model, skip=50,
    and per-tile seeds on the tiles that remain.
    """
    needed = set()
    for _, p in ppt.iterrows():
        pix = p.crown_px or ([p.center_px] if p.center_px else [])
        for rr, cc in pix:
            needed.add((rr // SCALE, cc // SCALE))
    keep = []
    for r, c in tile_windows(h, w):
        for lr, lc in needed:
            if r <= lr < r + TILE_LR and c <= lc < c + TILE_LR:
                keep.append((r, c))
                break
    return keep


def sr_engine_bicubic(cube, device=None, state=None):
    import torch
    t = torch.from_numpy(cube)[None]
    up = torch.nn.functional.interpolate(t, scale_factor=SCALE, mode="bicubic",
                                         align_corners=False)[0].numpy()
    return up  # (12, H4, W4) in ORDER12


def make_sen2srlite(device):
    sys.path.insert(0, str(SEN2SRLITE_DIR))
    import load as lite_load
    model = lite_load.compiled_model(Path(SEN2SRLITE_DIR), device=device)
    return model


def sr_engine_sen2srlite(cube, device, state):
    """cube (12,h,w) ORDER12 -> (12,H4,W4); B01/B09 bicubic (not modeled)."""
    import torch
    model = state["model"]
    idx = [ORDER12.index(b) for b in ORDER10_LITE]
    h, w = cube.shape[1:]
    out = np.zeros((12, h * SCALE, w * SCALE), np.float32)
    # B01/B09 pass-through (never used for NDMI/NDVI)
    for b in BANDS_60:
        i = ORDER12.index(b)
        t = torch.from_numpy(cube[i])[None, None]
        out[i] = torch.nn.functional.interpolate(
            t, scale_factor=SCALE, mode="bicubic", align_corners=False)[0, 0].numpy()
    full = torch.from_numpy(cube[idx])  # (10,h,w)
    for r, c in tile_windows(h, w):
        tile = full[:, r:r + TILE_LR, c:c + TILE_LR][None].to(device)
        with torch.no_grad():
            sr = model(tile)[0].cpu().numpy()  # (10, 512, 512)
        tr0 = 0 if r == 0 else TILE_TRIM
        tr1 = TILE_LR if r + TILE_LR >= h else TILE_LR - TILE_TRIM
        tc0 = 0 if c == 0 else TILE_TRIM
        tc1 = TILE_LR if c + TILE_LR >= w else TILE_LR - TILE_TRIM
        for j, b in enumerate(ORDER10_LITE):
            i = ORDER12.index(b)
            out[i, (r + tr0) * SCALE:(r + tr1) * SCALE, (c + tc0) * SCALE:(c + tc1) * SCALE] = \
                sr[j, tr0 * SCALE:tr1 * SCALE, tc0 * SCALE:tc1 * SCALE]
    return out


def make_difffusr(device):
    """Load DiffFuSR diffusion SR (NAIP-harm) + NN fusion, with mac shims."""
    import types, importlib, importlib.util
    import torch
    import torch.nn.functional as F
    # torch>=2.6 weights_only default + cuda-saved ckpts
    _orig_load = torch.load
    def _load(*a, **k):
        k["weights_only"] = False
        k.setdefault("map_location", "cpu")
        return _orig_load(*a, **k)
    torch.load = _load
    torch.cuda.synchronize = lambda *a, **k: None
    # py>=3.12 removed 'imp'
    if "imp" not in sys.modules:
        imp = types.ModuleType("imp")
        def find_module(name, path=None):
            spec = importlib.machinery.PathFinder().find_spec(name, path)
            return (None, spec.origin, None)
        def load_module(name, file, pathname, desc):
            spec = importlib.util.spec_from_file_location(name, pathname)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            sys.modules[name] = m
            return m
        imp.find_module = find_module
        imp.load_module = load_module
        sys.modules["imp"] = imp
    # MPS lacks non-divisible adaptive_avg_pool2d: hop through CPU
    _orig_pool = F.adaptive_avg_pool2d
    def _pool(inp, out):
        if inp.device.type == "mps":
            try:
                return _orig_pool(inp, out)
            except RuntimeError:
                return _orig_pool(inp.cpu(), out).to(inp.device)
        return _orig_pool(inp, out)
    F.adaptive_avg_pool2d = _pool
    torch.nn.functional.adaptive_avg_pool2d = _pool

    sys.path.insert(0, str(DIFFFUSR_DIR))
    from litsr.utils import read_yaml
    from models import load_model
    from models.fusion_model import FusionNetwork
    cfg = read_yaml(str(DIFFFUSR_HPARAMS))
    model = load_model(cfg, str(DIFFFUSR_CKPT), strict=False)
    model.eval()
    model.to(device)
    fusion = FusionNetwork(mode="eval")
    fusion.load_state_dict(torch.load(str(DIFFFUSR_FUSION_CKPT))["state_dict"])
    fusion.eval()
    fusion.to(device)
    return model, fusion


# DiffFuSR band stats (models/6_test_multispectral_SR_fuse.py, S2 L2A reflectance)
BS_MEAN = np.array([0.0769, 0.0906, 0.1162, 0.1318, 0.1619, 0.2275, 0.2500,
                    0.2588, 0.2667, 0.2684, 0.2461, 0.1874], np.float32)
BS_STD = np.array([0.1708, 0.1672, 0.1614, 0.1677, 0.1698, 0.1513, 0.1490,
                   0.1515, 0.1461, 0.2365, 0.1472, 0.1418], np.float32)
RGB_IDX = [3, 2, 1]  # R,G,B rows in ORDER12


def sr_engine_difffusr(cube, device, state):
    import torch
    model, fusion = state["model"], state["fusion"]
    ppt = state.get("ppt")
    h, w = cube.shape[1:]
    out = np.zeros((12, h * SCALE, w * SCALE), np.float32)
    mean_t = torch.from_numpy(BS_MEAN)[None, :, None, None].to(device)
    std_t = torch.from_numpy(BS_STD)[None, :, None, None].to(device)
    mean_rgb = mean_t[:, RGB_IDX]
    std_rgb = std_t[:, RGB_IDX]
    origins = tiles_needed(h, w, ppt) if ppt is not None else list(tile_windows(h, w))
    for r, c in origins:
        torch.manual_seed(SEED + 1000 * r + c)  # reproducible diffusion sample
        tile12 = torch.from_numpy(cube[:, r:r + TILE_LR, c:c + TILE_LR])[None].to(device)
        rgb_lr = tile12[:, RGB_IDX].clone()
        with torch.no_grad():
            rslt = model.test_step_lr_only((rgb_lr, ["t.tif"]))
            sr_rgb = torch.as_tensor(rslt["sr_raw"])[None].to(device)  # (1,3,512,512) refl
            fus_sig = (sr_rgb - mean_rgb) / std_rgb
            lr_norm = (tile12 - mean_t) / std_t
            o10, o20, o60, *_ = fusion(lr_norm, fus_sig)
            fused = torch.cat([
                o60[:, 0:1], o10[:, 2:3], o10[:, 1:2], o10[:, 0:1],
                o20[:, 0:1], o20[:, 1:2], o20[:, 2:3], o10[:, 3:4],
                o20[:, 3:4], o60[:, 1:2], o20[:, 4:5], o20[:, 5:6]], dim=1)
            fused = fused * std_t + mean_t
        sr = fused[0].cpu().numpy()
        tr0 = 0 if r == 0 else TILE_TRIM
        tr1 = TILE_LR if r + TILE_LR >= h else TILE_LR - TILE_TRIM
        tc0 = 0 if c == 0 else TILE_TRIM
        tc1 = TILE_LR if c + TILE_LR >= w else TILE_LR - TILE_TRIM
        out[:, (r + tr0) * SCALE:(r + tr1) * SCALE, (c + tc0) * SCALE:(c + tc1) * SCALE] = \
            sr[:, tr0 * SCALE:tr1 * SCALE, tc0 * SCALE:tc1 * SCALE]
    return out


ENGINES = {
    "bicubic": (sr_engine_bicubic, None),
    "sen2srlite": (sr_engine_sen2srlite, "lite"),
    "difffusr": (sr_engine_difffusr, "difffusr"),
}


# --------------------------------------------------------------------- run --
def cmd_run(engine):
    import torch
    fn, kind = ENGINES[engine]
    device = "cpu"
    if kind == "difffusr" and torch.backends.mps.is_available():
        device = "mps"
    state = {}
    if kind == "lite":
        state["model"] = make_sen2srlite(device)
    elif kind == "difffusr":
        state["model"], state["fusion"] = make_difffusr(device)
    print(f"engine={engine} device={device}")

    ppt, thr = point_pixel_table()
    state["ppt"] = ppt
    print(f"point-pixel table ready (otsu {thr:.2f}); "
          f"{(ppt.crown_px.map(len) > 0).mean():.3f} of arms have >=1 crown px")
    sc, lags = scene_meta()
    iB08, iB11, iB04 = ORDER12.index("B08"), ORDER12.index("B11"), ORDER12.index("B04")

    rows = []
    crown_contrast = []
    rows_dir = CACHE / f"sr_rows_{engine}"
    rows_dir.mkdir(exist_ok=True)
    for _, srow in sc.iterrows():
        part = rows_dir / f"{srow.scene}.json"
        if part.exists():
            saved = json.loads(part.read_text())
            rows.extend(saved["rows"])
            crown_contrast.append(saved["contrast"])
            print(f"{srow.scene}: cached ({len(saved['rows'])} samples)", flush=True)
            continue
        t0 = time.time()
        dat = np.load(SCENES_DIR / f"{srow.scene}.npz")
        cube = build_cube10(dat)
        sr = fn(cube, device, state)
        ndmi = (sr[iB08] - sr[iB11]) / np.clip(sr[iB08] + sr[iB11], 1e-6, None)
        ndvi = (sr[iB08] - sr[iB04]) / np.clip(sr[iB08] + sr[iB04], 1e-6, None)
        scene_rows = []
        # crown vs soil NDVI contrast (sanity b), sampled from per-point pixels
        cvals, svals = [], []
        use = lags[lags.scene == srow.scene]
        for _, lrow in use.iterrows():
            p = ppt[(ppt.pair_i == lrow.pair_i) & (ppt.arm == lrow.arm)].iloc[0]
            crown = p.crown_px
            noncrown = [t for t in p.all_px if t not in crown]
            v_crown = np.array([ndmi[r, c] for r, c in crown]) if crown else np.array([])
            rec = {
                "scene": srow.scene, "scene_date": srow.scene_date,
                "pair_i": int(lrow.pair_i), "lag": int(lrow.lag), "arm": lrow.arm,
                "scl_ok": bool(lrow.scl_ok), "native_ndmi": lrow.ndmi,
                "n_crown_px": len(crown),
                "sr_ndmi_crown": float(v_crown.mean()) if len(v_crown) else np.nan,
                "sr_ndmi_center": float(ndmi[p.center_px]) if p.center_px else np.nan,
                "sr_ndvi_crown": float(np.mean([ndvi[r, c] for r, c in crown])) if crown else np.nan,
            }
            br, bc = p.cell_block
            blk = ndmi[max(br, 0):br + 8, max(bc, 0):bc + 8]
            rec["sr_ndmi_20cell"] = float(blk.mean()) if blk.size else np.nan
            scene_rows.append(rec)
            if crown:
                cvals.append(np.mean([ndvi[r, c] for r, c in crown]))
            if noncrown:
                svals.append(np.mean([ndvi[r, c] for r, c in noncrown]))
        contrast = {
            "scene": srow.scene,
            "ndvi_crown_mean": float(np.mean(cvals)) if cvals else None,
            "ndvi_soil_mean": float(np.mean(svals)) if svals else None,
        }
        rows.extend(scene_rows)
        crown_contrast.append(contrast)
        part.write_text(json.dumps({"rows": scene_rows, "contrast": contrast}))
        print(f"{srow.scene}: {len(use)} samples {time.time()-t0:.1f}s", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(CACHE / f"sr_values_{engine}.csv", index=False)
    (CACHE / f"sr_crowncontrast_{engine}.json").write_text(json.dumps(crown_contrast, indent=2))
    print("wrote", CACHE / f"sr_values_{engine}.csv", len(df), "rows")


# ------------------------------------------------------------------- stats --
def signflip(delta, clusters, rng):
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
    return float(obs), (hits2 + 1) / (NPERM + 1), (hits1 + 1) / (NPERM + 1)


def block(sub, rng, col="dndmi"):
    d = sub[col].to_numpy(float)
    n = len(d)
    if n < 20:
        return {"n": n}
    med, p2, p1 = signflip(d, sub["cluster"].to_numpy(), rng)
    return {"n": n, "median_delta": round(med, 5),
            "mean_delta": round(float(d.mean()), 5),
            "frac_neg": round(float((d < 0).mean()), 4),
            "p_two_sided": round(p2, 5), "p_one_sided_neg": round(p1, 5),
            "n_clusters": int(sub["cluster"].nunique())}


def cmd_stats(engines):
    from pyproj import Transformer
    rng_master = np.random.default_rng(SEED)
    pairs = pd.read_csv(PAIRS_CSV)
    pairs["pair_i"] = pairs.index
    to_utm33 = Transformer.from_crs(4326, 32633, always_xy=True)
    px, py = to_utm33.transform(pairs.pos_lon.to_numpy(), pairs.pos_lat.to_numpy())
    pairs["cluster"] = (np.floor(px / 1000).astype(int).astype(str) + "_"
                        + np.floor(py / 1000).astype(int).astype(str))
    crown = pd.read_csv(CROWN_CSV)

    out = {"nperm": NPERM, "seed": SEED, "radius_m": RADIUS_M,
           "preregistered_direction": "delta < 0 (positive arm drier)",
           "engines": {}}
    all_rows = []
    for engine in engines:
        f = CACHE / f"sr_values_{engine}.csv"
        if not f.exists():
            out["engines"][engine] = {"status": "missing values file"}
            continue
        rng = np.random.default_rng(SEED)
        v = pd.read_csv(f)
        # sanity (a): SR->20 m vs native NDMI
        s = v[v.scl_ok & v.native_ndmi.notna() & v.sr_ndmi_20cell.notna()]
        sanity_corr = float(np.corrcoef(s.native_ndmi, s.sr_ndmi_20cell)[0, 1]) if len(s) > 10 else None
        eng = {"sanity_corr_sr20_vs_native": round(sanity_corr, 4) if sanity_corr is not None else None,
               "lags": {}}
        cc = json.loads((CACHE / f"sr_crowncontrast_{engine}.json").read_text())
        cm = [c for c in cc if c["ndvi_crown_mean"] is not None and c["ndvi_soil_mean"] is not None]
        if cm:
            eng["sanity_ndvi_crown_minus_soil_mean"] = round(
                float(np.mean([c["ndvi_crown_mean"] - c["ndvi_soil_mean"] for c in cm])), 4)
        piv = v.pivot_table(index=["pair_i", "lag"], columns="arm",
                            values=["sr_ndmi_crown", "sr_ndmi_center", "scl_ok", "n_crown_px"],
                            aggfunc="first")
        piv.columns = [f"{a}_{b}" for a, b in piv.columns]
        piv = piv.reset_index().merge(pairs[["pair_i", "cluster"]], on="pair_i")
        piv = piv.merge(crown[["pair_i", "pos_crownfrac20"]], on="pair_i", how="left")
        ok = piv.scl_ok_pos.astype(bool) & piv.scl_ok_neg.astype(bool)
        for lag in LAGS_USED:
            g = piv[(piv.lag == lag) & ok].copy()
            entry = {}
            # primary: crown-masked SR NDMI, both arms with >=1 crown pixel
            gc = g[g.sr_ndmi_crown_pos.notna() & g.sr_ndmi_crown_neg.notna()].copy()
            gc["dndmi"] = gc.sr_ndmi_crown_pos - gc.sr_ndmi_crown_neg
            entry["crown_masked"] = block(gc, rng)
            # secondary: bare center pixel
            gb = g[g.sr_ndmi_center_pos.notna() & g.sr_ndmi_center_neg.notna()].copy()
            gb["dndmi"] = gb.sr_ndmi_center_pos - gb.sr_ndmi_center_neg
            entry["center_pixel"] = block(gb, rng)
            # strata by A2 positive-arm 20 m crown fraction
            if len(gc) >= 60 and gc.pos_crownfrac20.notna().sum() >= 60:
                gs = gc[gc.pos_crownfrac20.notna()]
                terc = gs.pos_crownfrac20.quantile([1 / 3, 2 / 3]).to_numpy()
                entry["a2_cf_terciles"] = {
                    "cuts": [round(float(t), 4) for t in terc],
                    "low": block(gs[gs.pos_crownfrac20 <= terc[0]], rng),
                    "mid": block(gs[(gs.pos_crownfrac20 > terc[0]) & (gs.pos_crownfrac20 <= terc[1])], rng),
                    "high": block(gs[gs.pos_crownfrac20 > terc[1]], rng),
                }
                entry["a2_cf_ge_0.6"] = block(gs[gs.pos_crownfrac20 >= 0.6], rng)
            eng["lags"][str(lag)] = entry
            gc["engine"] = engine
            all_rows.append(gc.assign(lag=lag))
        out["engines"][engine] = eng

    OUT_JSON.write_text(json.dumps(out, indent=2))
    if all_rows:
        pd.concat(all_rows, ignore_index=True).to_csv(OUT_CSV, index=False)
    print(json.dumps(out, indent=2))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("fetch")
    r = sp.add_parser("run")
    r.add_argument("engine", choices=list(ENGINES))
    st = sp.add_parser("stats")
    st.add_argument("--engines", default="difffusr,sen2srlite,bicubic")
    a = ap.parse_args()
    if a.cmd == "fetch":
        cmd_fetch()
    elif a.cmd == "run":
        cmd_run(a.engine)
    else:
        cmd_stats(a.engines.split(","))


if __name__ == "__main__":
    main()

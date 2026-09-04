#!/usr/bin/env python3
"""Resample the same 100 points on S2A_34TBL 2021-08-22."""
import csv, json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import join_one_scene as j

rows = list(csv.DictReader(open(Path(__file__).resolve().parents[1] / "nowcast/cache/scene_join_100.csv")))
lons = [float(r["lon"]) for r in rows]
lats = [float(r["lat"]) for r in rows]
base = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210822_0_L2A/"
print("sampling 20210822")
red = j.sample_band(base + "B04.tif", lons, lats)
nir = j.sample_band(base + "B08.tif", lons, lats)
swir = j.sample_band(base + "B11.tif", lons, lats)
scl = j.sample_band(base + "SCL.tif", lons, lats)
ndvi = j.ndi(nir, red)
ndmi = j.ndi(nir, swir)
lab = np.array([r["risultato"].startswith("Pos") for r in rows])
ok = np.isfinite(ndmi) & np.isfinite(scl)
ok = ok & np.isin(np.nan_to_num(scl, nan=-1).astype(int), [4, 5, 7])
p, n = ndmi[ok & lab], ndmi[ok & ~lab]
pv, nv = ndvi[ok & lab], ndvi[ok & ~lab]
out = {
    "scene": "S2A_34TBL_20210822_0_L2A",
    "usable": int(ok.sum()),
    "n_pos": int((ok & lab).sum()),
    "n_neg": int((ok & ~lab).sum()),
    "ndmi_cliffs": j.cliffs_delta(p, n) if len(p) > 5 else None,
    "ndmi_p": j.mw_u_p(p, n)[1] if len(p) > 5 else None,
    "ndmi_delta": float(p.mean() - n.mean()) if len(p) else None,
    "ndvi_cliffs": j.cliffs_delta(pv, nv) if len(pv) > 5 else None,
    "ndvi_p": j.mw_u_p(pv, nv)[1] if len(pv) > 5 else None,
}
Path(__file__).resolve().parents[1].joinpath("nowcast/cache/scene_join_aug22.json").write_text(
    json.dumps(out, indent=2)
)
print(json.dumps(out, indent=2))

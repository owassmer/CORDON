#!/usr/bin/env python3
"""Join F7 (symptom-absent olive diagnostic +/−) to 12 Aug and 22 Aug 2021 S2."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nowcast"))
import join_one_scene as j

XLSX = ROOT / "raw/data/camp_xlsx/CAMP_2021.xlsx"
OUT_CSV = ROOT / "nowcast/cache/f7_2021.csv"
OUT_JSON = ROOT / "nowcast/cache/f7_2021.summary.json"
SEED = 42
BBOX = j.BBOX
AUG22 = {
    "red": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210822_0_L2A/B04.tif",
    "nir": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210822_0_L2A/B08.tif",
    "re1": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210822_0_L2A/B05.tif",
    "swir16": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210822_0_L2A/B11.tif",
    "scl": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/T/BL/2021/8/S2A_34TBL_20210822_0_L2A/SCL.tif",
}


def is_olive(s):
    t = str(s).lower()
    return "olea" in t or "olivo" in t


def veg_frac(scl):
    x = np.nan_to_num(scl, nan=-1).astype(int)
    return float(np.isin(x, list(j.SCL_OK)).mean())


def stats(pos, neg):
    return {
        "n_pos": int(len(pos)),
        "n_neg": int(len(neg)),
        "mean_pos": float(pos.mean()) if len(pos) else None,
        "mean_neg": float(neg.mean()) if len(neg) else None,
        "delta": float(pos.mean() - neg.mean()) if len(pos) and len(neg) else None,
        "cliffs": j.cliffs_delta(pos, neg) if len(pos) > 5 and len(neg) > 5 else None,
        "p": j.mw_u_p(pos, neg)[1] if len(pos) > 5 and len(neg) > 5 else None,
    }


def main():
    df = pd.read_excel(XLSX, sheet_name=0)
    df["date"] = pd.to_datetime(df["DATA_RILEVAMENTO"], errors="coerce")
    df["lat"] = pd.to_numeric(df["LATITUDINE"], errors="coerce")
    df["lon"] = pd.to_numeric(df["LONGITUDINE"], errors="coerce")
    west, south, east, north = BBOX
    olive = df["SPECIE"].map(is_olive)
    pos = df["RISULTATO"].astype(str).str.lower().str.startswith("pos")
    neg = df["RISULTATO"].astype(str).str.lower().str.startswith("neg")
    ass = df["SINTOMO"].astype(str).str.lower().str.startswith("ass")
    summer = df["date"].between("2021-06-01", "2021-09-15")
    inbox = df["lat"].between(south, north) & df["lon"].between(west, east)
    cand_p = df[olive & pos & ass & summer & inbox].copy()
    cand_n = df[olive & neg & ass & summer & inbox].copy()
    print("inbox F7+ / F7−", len(cand_p), len(cand_n), flush=True)

    def sample_scene(hrefs, lons, lats):
        red = j.sample_band(hrefs["red"], lons, lats)
        nir = j.sample_band(hrefs["nir"], lons, lats)
        re1 = j.sample_band(hrefs["re1"], lons, lats)
        swir = j.sample_band(hrefs["swir16"], lons, lats)
        scl = j.sample_band(hrefs["scl"], lons, lats)
        return red, nir, re1, swir, scl

    print("sampling 12 Aug F7+", flush=True)
    rp, np_, ep, sp, scp = sample_scene(j.HREFS, cand_p["lon"].tolist(), cand_p["lat"].tolist())
    okp = np.isfinite(sp) & np.isin(np.nan_to_num(scp, nan=-1).astype(int), list(j.SCL_OK))
    cand_p = cand_p.iloc[np.where(okp)[0]].copy()
    rp, np_, ep, sp, scp = rp[okp], np_[okp], ep[okp], sp[okp], scp[okp]
    print("SCL F7+", len(cand_p), flush=True)
    if len(cand_p) < 40:
        OUT_JSON.write_text(json.dumps({"stop": True, "n_f7p_scl": int(len(cand_p))}, indent=2))
        print("STOP n<40")
        return

    print("sampling 12 Aug F7−", flush=True)
    rn, nn, en, sn, scn = sample_scene(j.HREFS, cand_n["lon"].tolist(), cand_n["lat"].tolist())
    okn = np.isfinite(sn) & np.isin(np.nan_to_num(scn, nan=-1).astype(int), list(j.SCL_OK))
    cand_n = cand_n.iloc[np.where(okn)[0]].copy()
    rn, nn, en, sn, scn = rn[okn], nn[okn], en[okn], sn[okn], scn[okn]
    rng = np.random.default_rng(SEED)
    take = min(len(cand_p), len(cand_n))
    idx = rng.choice(len(cand_n), size=take, replace=False)
    cand_n = cand_n.iloc[idx].copy()
    rn, nn, en, sn, scn = rn[idx], nn[idx], en[idx], sn[idx], scn[idx]
    cand_p = cand_p.iloc[:take].copy()
    rp, np_, ep, sp, scp = rp[:take], np_[:take], ep[:take], sp[:take], scp[:take]

    def pack(part, red, nir, re1, swir, scl, label):
        rows = []
        ndvi = j.ndi(nir, red)
        ndre = j.ndi(nir, re1)
        ndmi = j.ndi(nir, swir)
        for i, (_, r) in enumerate(part.iterrows()):
            rows.append({
                "id": r["ID"],
                "date": str(r["date"].date()) if pd.notna(r["date"]) else "",
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "comune": r.get("COMUNE") or "",
                "cultivar": r.get("CULTIVAR") or "",
                "zona": r.get("ZONA") or "",
                "sintomo": r.get("SINTOMO") or "",
                "risultato": label,
                "scl": float(scl[i]) if np.isfinite(scl[i]) else None,
                "ndvi": float(ndvi[i]) if np.isfinite(ndvi[i]) else None,
                "ndre": float(ndre[i]) if np.isfinite(ndre[i]) else None,
                "ndmi": float(ndmi[i]) if np.isfinite(ndmi[i]) else None,
            })
        return rows, ndvi, ndre, ndmi

    rows_p, v_p, e_p, m_p = pack(cand_p, rp, np_, ep, sp, scp, "Positivo")
    rows_n, v_n, e_n, m_n = pack(cand_n, rn, nn, en, sn, scn, "Negativo")
    rows = rows_p + rows_n
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("sampling 22 Aug same points", flush=True)
    lons = [r["lon"] for r in rows]
    lats = [r["lat"] for r in rows]
    lab = np.array([r["risultato"].startswith("Pos") for r in rows])
    r2, n2, e2, s2, sc2 = sample_scene(AUG22, lons, lats)
    ok2 = np.isfinite(s2) & np.isin(np.nan_to_num(sc2, nan=-1).astype(int), list(j.SCL_OK))
    ndvi2, ndre2, ndmi2 = j.ndi(n2, r2), j.ndi(n2, e2), j.ndi(n2, s2)

    def blocked_p(values, labels, comuni, nperm=5000):
        rng = np.random.default_rng(SEED)
        v = np.asarray(values, float)
        y = np.asarray(labels, bool)
        c = np.asarray(comuni)
        obs = j.cliffs_delta(v[y], v[~y])
        hits = 0
        y2 = y.copy()
        for _ in range(nperm):
            for com in np.unique(c):
                m = c == com
                y2[m] = rng.permutation(y[m])
            d = j.cliffs_delta(v[y2], v[~y2])
            if abs(d) >= abs(obs):
                hits += 1
        return float(obs), (hits + 1) / (nperm + 1)

    comuni = np.array([r["comune"] for r in rows])
    b_d, b_p = blocked_p(m_p.tolist() + m_n.tolist(), lab, comuni)

    # residual NDMI ~ NDVI
    x = np.concatenate([v_p, v_n])
    ynd = np.concatenate([m_p, m_n])
    good = np.isfinite(x) & np.isfinite(ynd)
    coef = np.polyfit(x[good], ynd[good], 1)
    resid = ynd - (coef[0] * x + coef[1])
    rpos, rneg = resid[lab], resid[~lab]

    summary = {
        "n_each": take,
        "scene_aug12": j.SCENE_ID,
        "ndvi_aug12": stats(v_p, v_n),
        "ndre_aug12": stats(e_p, e_n),
        "ndmi_aug12": stats(m_p, m_n),
        "ndmi_aug12_blocked_p": b_p,
        "ndmi_aug12_blocked_delta": b_d,
        "ndmi_resid_ndvi": stats(rpos, rneg),
        "ndvi_aug22": stats(ndvi2[ok2 & lab], ndvi2[ok2 & ~lab]),
        "ndmi_aug22": stats(ndmi2[ok2 & lab], ndmi2[ok2 & ~lab]),
        "n_aug22_usable": int(ok2.sum()),
        "rule": "|cliffs|>=0.15 and p<0.05; blocked p wins if disagree",
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

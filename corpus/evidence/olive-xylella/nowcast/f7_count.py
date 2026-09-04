#!/usr/bin/env python3
"""Count SCL-valid 2021 symptom-absent olive diagnostics in tile 34TBL."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nowcast"))
import join_one_scene as j

XLSX = ROOT / "raw/data/camp_xlsx/CAMP_2021.xlsx"
OUT = ROOT / "nowcast/cache/f7_2021_counts.json"
BBOX = j.BBOX  # west, south, east, north


def is_olive(s):
    t = str(s).lower()
    return "olea" in t or "olivo" in t


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
    f7p = olive & pos & ass & summer & inbox & df["lat"].notna()
    f7n = olive & neg & ass & summer & inbox & df["lat"].notna()
    print("loading SCL…", flush=True)
    lons_p = df.loc[f7p, "lon"].tolist()
    lats_p = df.loc[f7p, "lat"].tolist()
    lons_n = df.loc[f7n, "lon"].tolist()
    lats_n = df.loc[f7n, "lat"].tolist()
    scl_p = j.sample_band(j.HREFS["scl"], lons_p, lats_p) if lons_p else np.array([])
    scl_n = j.sample_band(j.HREFS["scl"], lons_n, lats_n) if lons_n else np.array([])

    def ok(scl):
        if scl.size == 0:
            return 0
        x = np.nan_to_num(scl, nan=-1).astype(int)
        return int(np.isin(x, list(j.SCL_OK)).sum())

    out = {
        "file": "CAMP_2021.xlsx",
        "scene": j.SCENE_ID,
        "n_olive_pos_assente_all": int((olive & pos & ass).sum()),
        "n_olive_pos_assente_summer": int((olive & pos & ass & summer).sum()),
        "n_f7p_inbox": int(f7p.sum()),
        "n_f7n_inbox": int(f7n.sum()),
        "n_f7p_scl": ok(scl_p),
        "n_f7n_scl": ok(scl_n),
        "stop_if_f7p_scl_lt": 40,
        "run_test": ok(scl_p) >= 40,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

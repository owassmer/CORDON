#!/usr/bin/env python3
"""Harmonize official emergenza CAMP workbooks and emit series stats."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

SRC = Path("/Users/owenwassmer/Desktop/Connor/olive-xylella/raw/data/camp_xlsx")
OUT = Path("/Users/owenwassmer/Desktop/Connor/olive-xylella/data")

FILES = [
    "CAMP_2013_2014.xlsx",
    "CAMP_2014_2015.xlsx",
    "CAMP_2016_2017.xlsx",
    "CAMP_2017_2018.xlsx",
    "CAMP_2018_2019.xlsx",
    "CAMP_2019_2020.xlsx",
    "CAMP_2020.xlsx",
    "CAMP_2021.xlsx",
    "CAMP_2022.xlsx",
    "CAMP_2023.xlsx",
    "CAMP_2024.xlsx",
    "CAMP_2025.xlsx",
]

DATE_CANDS = ["DATA_RILEVAMENTO", "DATA_PRELIVEO", "DATA_CAMPIONE", "DATA"]
LAT_CANDS = ["LATITUDINE", "LAT"]
LON_CANDS = ["LONGITUDINE", "LON"]


def pick(cols, cands):
    for c in cands:
        if c in cols:
            return c
    return None


def is_olive(s):
    if not isinstance(s, str):
        return False
    t = s.lower()
    return "olea" in t or "olivo" in t or t.strip() in {"olive", "olivo"}


def is_pos(s):
    if not isinstance(s, str):
        return False
    return s.strip().lower().startswith("pos")


def is_neg(s):
    if not isinstance(s, str):
        return False
    return s.strip().lower().startswith("neg")


def sint_present(s):
    if not isinstance(s, str) or not s.strip():
        return None
    t = s.strip().lower()
    if t.startswith("pres"):
        return True
    if t.startswith("ass"):
        return False
    return None


def to_float(s):
    if pd.isna(s):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).strip().replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def load_one(name):
    path = SRC / name
    xl = pd.ExcelFile(path)
    sheet = xl.sheet_names[0]
    df = pd.read_excel(path, sheet_name=sheet)
    cols = list(df.columns)
    date_c = pick(cols, DATE_CANDS)
    lat_c = pick(cols, LAT_CANDS)
    lon_c = pick(cols, LON_CANDS)
    spec_c = "SPECIE" if "SPECIE" in cols else None
    res_c = "RISULTATO" if "RISULTATO" in cols else None
    sin_c = "SINTOMO" if "SINTOMO" in cols else None
    com_c = "COMUNE" if "COMUNE" in cols else None
    cul_c = "CULTIVAR" if "CULTIVAR" in cols else None
    zon_c = "ZONA" if "ZONA" in cols else None
    sub_c = "SUBSPECIE" if "SUBSPECIE" in cols else None

    dates = pd.to_datetime(df[date_c], errors="coerce") if date_c else pd.Series([pd.NaT] * len(df))
    lat = df[lat_c].map(to_float) if lat_c else pd.Series([None] * len(df))
    lon = df[lon_c].map(to_float) if lon_c else pd.Series([None] * len(df))
    spec = df[spec_c].astype(str) if spec_c else pd.Series([""] * len(df))
    res = df[res_c].astype(str) if res_c else pd.Series([""] * len(df))
    sin = df[sin_c].astype(str) if sin_c else pd.Series([""] * len(df))
    com = df[com_c].astype(str) if com_c else pd.Series([""] * len(df))

    olive = spec.map(is_olive)
    pos = res.map(is_pos)
    neg = res.map(is_neg)
    sy = sin.map(sint_present)
    year = dates.dt.year
    # Salento / Lecce-ish: east of the old CKAN lon max 17.78
    east = lon.map(lambda x: x is not None and x > 17.80)
    south = lat.map(lambda x: x is not None and x < 40.45)

    out = {
        "file": name,
        "sheet": sheet,
        "columns": cols,
        "n": int(len(df)),
        "date_min": None if dates.dropna().empty else str(dates.min().date()),
        "date_max": None if dates.dropna().empty else str(dates.max().date()),
        "years": {str(int(k)): int(v) for k, v in year.dropna().astype(int).value_counts().sort_index().items()},
        "n_olive": int(olive.sum()),
        "n_pos": int(pos.sum()),
        "n_neg": int(neg.sum()),
        "n_olive_pos": int((olive & pos).sum()),
        "n_coords": int((lat.notna() & lon.notna()).sum()),
        "lat_min": None if lat.dropna().empty else float(lat.min()),
        "lat_max": None if lat.dropna().empty else float(lat.max()),
        "lon_min": None if lon.dropna().empty else float(lon.min()),
        "lon_max": None if lon.dropna().empty else float(lon.max()),
        "n_east_of_17_80": int(east.fillna(False).sum()),
        "n_olive_east": int((olive & east.fillna(False)).sum()),
        "n_olive_pos_east": int((olive & pos & east.fillna(False)).sum()),
        "n_south_of_40_45": int(south.fillna(False).sum()),
        "n_olive_pos_south": int((olive & pos & south.fillna(False)).sum()),
        "n_sintomo_present": int(sy.dropna().eq(True).sum()) if sin_c else None,
        "n_sintomo_absent": int(sy.dropna().eq(False).sum()) if sin_c else None,
        "n_olive_pos_assente": int((olive & pos & sy.eq(False)).sum()) if sin_c else None,
        "n_olive_pos_presente": int((olive & pos & sy.eq(True)).sum()) if sin_c else None,
        "top_comuni_pos_olive": (
            com[olive & pos].str.upper().value_counts().head(8).to_dict()
        ),
        "has_zona": zon_c is not None,
        "has_subspecie": sub_c is not None,
    }
    if zon_c:
        out["zona_counts"] = df[zon_c].astype(str).value_counts().head(12).to_dict()
        out["zona_olive_pos"] = (
            df.loc[olive & pos, zon_c].astype(str).value_counts().head(12).to_dict()
        )
    if sub_c:
        out["subspecie_counts"] = df[sub_c].astype(str).value_counts().head(12).to_dict()
        out["subspecie_pos"] = (
            df.loc[pos, sub_c].astype(str).value_counts().head(12).to_dict()
        )
        out["subspecie_olive_pos"] = (
            df.loc[olive & pos, sub_c].astype(str).value_counts().head(12).to_dict()
        )
    # olive pos by calendar year
    if not dates.dropna().empty:
        g = pd.DataFrame({"y": year, "olive": olive, "pos": pos})
        g = g.dropna(subset=["y"])
        g["y"] = g["y"].astype(int)
        out["olive_pos_by_year"] = (
            g[g.olive & g.pos].groupby("y").size().astype(int).to_dict()
        )
        out["olive_by_year"] = g[g.olive].groupby("y").size().astype(int).to_dict()
        out["pos_by_year"] = g[g.pos].groupby("y").size().astype(int).to_dict()
    return out, df, dict(
        date=dates, lat=lat, lon=lon, olive=olive, pos=pos, sin=sy, com=com, year=year
    )


def main():
    summaries = []
    # pooled yearly (careful of overlapping campaign files)
    yearly = {}  # year -> counters, using file-tag to avoid double-count later
    file_year_rows = []

    for name in FILES:
        print("loading", name, flush=True)
        s, df, arrays = load_one(name)
        summaries.append(s)
        print(
            f"  n={s['n']} olive={s['n_olive']} pos={s['n_pos']} olive_pos={s['n_olive_pos']} "
            f"east={s['n_east_of_17_80']} dates={s['date_min']}..{s['date_max']}",
            flush=True,
        )
        # record per-file yearly for later de-dup discussion
        for y, n in (s.get("olive_pos_by_year") or {}).items():
            file_year_rows.append({"file": name, "year": int(y), "olive_pos": int(n),
                                   "olive": int((s.get("olive_by_year") or {}).get(y, 0)),
                                   "pos": int((s.get("pos_by_year") or {}).get(y, 0))})

    # If two files claim the same calendar year, keep the dedicated calendar file when present
    prefer = {
        2020: "CAMP_2020.xlsx",
        2021: "CAMP_2021.xlsx",
        2022: "CAMP_2022.xlsx",
        2023: "CAMP_2023.xlsx",
        2024: "CAMP_2024.xlsx",
        2025: "CAMP_2025.xlsx",
    }
    by_year = {}
    for row in file_year_rows:
        y = row["year"]
        by_year.setdefault(y, []).append(row)

    resolved = []
    for y, rows in sorted(by_year.items()):
        if y in prefer:
            chosen = [r for r in rows if r["file"] == prefer[y]]
            chosen = chosen[0] if chosen else max(rows, key=lambda r: r["olive"])
        else:
            chosen = max(rows, key=lambda r: r["olive"])
        resolved.append({**chosen, "also_in": [r["file"] for r in rows if r["file"] != chosen["file"]]})

    payload = {
        "n_files": len(summaries),
        "missing_campaigns": ["2015-2016 workbook not among downloads"],
        "files": summaries,
        "file_year_overlap": file_year_rows,
        "resolved_calendar_year": resolved,
        "notes": {
            "east_of_17_80": "east of CKAN CSV lon max (~17.78) — Salento / Lecce side",
            "south_of_40_45": "south of northern Brindisi — deeper Salento",
            "overlap": "campaign workbooks can span two calendar years; resolved series prefers dedicated CAMP_YYYY.xlsx",
        },
    }
    outp = OUT / "_camp_xlsx_inventory.json"
    outp.write_text(json.dumps(payload, indent=2, default=str, ensure_ascii=False))
    print("WROTE", outp)
    print("\n=== RESOLVED CALENDAR YEAR (olive_pos / olive) ===")
    for r in resolved:
        print(f"  {r['year']}: olive_pos={r['olive_pos']:5d}  olive={r['olive']:6d}  from {r['file']}  also={r['also_in']}")


if __name__ == "__main__":
    main()

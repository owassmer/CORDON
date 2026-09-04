#!/usr/bin/env python3
"""Do the same olive coordinates recur across campaigns? Decides whether
longitudinal PCR trajectories (time-to-positivity, cultivar survival) exist."""
from pathlib import Path

import pandas as pd

X = Path(__file__).resolve().parents[1] / "raw/data/camp_xlsx"


def load(name):
    df = pd.read_excel(X / name, sheet_name=0)
    c = {k.upper(): k for k in df.columns}
    out = pd.DataFrame({
        "lat": pd.to_numeric(df[c["LATITUDINE"]], errors="coerce").round(5),
        "lon": pd.to_numeric(df[c["LONGITUDINE"]], errors="coerce").round(5),
        "res": df[c["RISULTATO"]].astype(str).str.lower().str[:3],
        "olive": df[c["SPECIE"]].astype(str).str.lower().str.contains(
            "olea|olivo", regex=True),
    })
    return out.dropna(subset=["lat", "lon"])


def main():
    pairs = [
        ("CAMP_2019_2020.xlsx", "CAMP_2020.xlsx"),
        ("CAMP_2020.xlsx", "CAMP_2021.xlsx"),
        ("CAMP_2021.xlsx", "CAMP_2022.xlsx"),
        ("CAMP_2017_2018.xlsx", "CAMP_2018_2019.xlsx"),
    ]
    for a, b in pairs:
        A, B = load(a), load(b)
        A, B = A[A.olive], B[B.olive]
        ka = set(zip(A.lat, A.lon))
        kb = set(zip(B.lat, B.lon))
        inter = ka.intersection(kb)
        print(f"{a} olives={len(ka):6d}  {b} olives={len(kb):6d}  "
              f"exact-coord overlap={len(inter):6d}")
        if inter:
            Am = A.groupby(["lat", "lon"])["res"].agg(
                lambda s: "pos" if (s == "pos").any() else "neg")
            Bm = B.groupby(["lat", "lon"])["res"].agg(
                lambda s: "pos" if (s == "pos").any() else "neg")
            j = Am.to_frame("ra").join(Bm.to_frame("rb"), how="inner")
            print("   transitions:", j.value_counts().to_dict())


if __name__ == "__main__":
    main()

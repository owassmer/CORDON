#!/usr/bin/env python3
"""Cultivar-specific field conversion from repeat-tested coordinates.

Pre-registered gate (queries/telos-synthesis.md item 2): Leccino must show
materially lower stratum-adjusted conversion than the susceptible reference
(Cellina di Nardò + Ogliarola salentina) or the cultivar table stays internal.

Unit: exact coordinate (lat/lon rounded to 5 decimals, ~1 m). Transition:
consecutive campaign visits of the same coordinate where the earlier visit is
negative; outcome = positive at the later visit. Positives exit the panel
(felling), so conversions are terminal. Strata: campaign-pair × comune.
Adjustment: Mantel-Haenszel risk ratio + stratified label-permutation p.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XDIR = ROOT / "raw/data/camp_xlsx"
CACHE = ROOT / "producers/cache"
OUT_JSON = ROOT / "nowcast/cache/cultivar_conversion.json"
SEED = 42
NPERM = 5000
MIN_CULT_N = 30
REF = {"cellina di nardò", "ogliarola salentina"}

CAMPAIGNS = [
    "CAMP_2013_2014.xlsx", "CAMP_2014_2015.xlsx", "CAMP_2016_2017.xlsx",
    "CAMP_2017_2018.xlsx", "CAMP_2018_2019.xlsx", "CAMP_2019_2020.xlsx",
    "CAMP_2020.xlsx", "CAMP_2021.xlsx", "CAMP_2022.xlsx", "CAMP_2023.xlsx",
    "CAMP_2024.xlsx", "CAMP_2025.xlsx",
]
LABELS = ["2013-14", "2014-15", "2016-17", "2017-18", "2018-19", "2019-20",
          "2020", "2021", "2022", "2023", "2024", "2025"]


def norm_cult(s):
    t = str(s).strip().casefold()
    # repair cp1252/UTF-8 mojibake of accented names (e.g. "nardã²", "nard‗")
    t = t.replace("ã²", "ò").replace("‗", "ò")
    if t in {"", "nan", "none", "****", "altro", "n.d.", "nd", "-"}:
        return None
    return t


def build_visits():
    cache = CACHE / "visits_cultivar.csv"
    if cache.exists():
        v = pd.read_csv(cache)
        # CSV round-trip turns None into NaN, which is truthy in Python;
        # normalize back to None so "first non-null cultivar" logic holds.
        # Re-apply norm_cult so mojibake repair reaches cached values too.
        v["cult"] = v["cult"].astype(object).map(
            lambda s: norm_cult(s) if isinstance(s, str) else None)
        return v
    frames = []
    for i, name in enumerate(CAMPAIGNS):
        df = pd.read_excel(XDIR / name, sheet_name=0)
        c = {k.upper(): k for k in df.columns}
        spec = df[c["SPECIE"]].astype(str).str.casefold() if "SPECIE" in c else ""
        olive = spec.str.contains("olea|olivo", regex=True) if "SPECIE" in c else False
        res = df[c["RISULTATO"]].astype(str).str.casefold().str[:3] if "RISULTATO" in c else ""
        out = pd.DataFrame({
            "ci": i,
            "lat5": pd.to_numeric(df[c["LATITUDINE"]], errors="coerce").round(5),
            "lon5": pd.to_numeric(df[c["LONGITUDINE"]], errors="coerce").round(5),
            "pos": res == "pos",
            "valid": res.isin(["pos", "neg"]),
            "cult": df[c["CULTIVAR"]].map(norm_cult) if "CULTIVAR" in c else None,
            "comune": df[c["COMUNE"]].astype(str).str.strip().str.title() if "COMUNE" in c else "",
        })
        out = out[olive & out.valid].dropna(subset=["lat5", "lon5"])
        # one row per coordinate per campaign: any positive wins; first non-null cultivar
        g = out.groupby(["lat5", "lon5"], as_index=False).agg(
            pos=("pos", "any"),
            cult=("cult", lambda s: next((x for x in s if x), None)),
            comune=("comune", "first"),
        )
        g["ci"] = i
        frames.append(g)
        print(f"{LABELS[i]}: {len(g)} olive coordinates", flush=True)
    visits = pd.concat(frames, ignore_index=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    visits.to_csv(cache, index=False)
    return visits


def transitions(visits):
    visits = visits.sort_values(["lat5", "lon5", "ci"])
    rows = []
    for (la, lo), g in visits.groupby(["lat5", "lon5"], sort=False):
        if len(g) < 2:
            continue
        recs = g.to_dict("records")
        cult = next((r["cult"] for r in recs if r["cult"]), None)
        for a, b in zip(recs, recs[1:]):
            if a["pos"]:
                break  # felled after positive; later same-coord rows are replants/noise
            rows.append({
                "lat5": la, "lon5": lo, "cult": cult,
                "comune": a["comune"] or b["comune"],
                "pair": f"{LABELS[a['ci']]}->{LABELS[b['ci']]}",
                "gap": b["ci"] - a["ci"],
                "conv": bool(b["pos"]),
            })
    return pd.DataFrame(rows)


def wilson(k, n, z=1.96):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0.0, ctr - h), 4), round(min(1.0, ctr + h), 4)


def mh_rr(df, cult):
    num = den = 0.0
    used = 0
    for _, g in df.groupby(["pair", "comune"]):
        x = g[g.cult == cult]
        r = g[g.cult.isin(REF)]
        if len(x) == 0 or len(r) == 0:
            continue
        n = len(x) + len(r)
        num += x.conv.sum() * len(r) / n
        den += r.conv.sum() * len(x) / n
        used += 1
    return (round(num / den, 3) if den > 0 else None), used


def perm_p(df, cult, rng):
    """Stratified label-permutation p, computed exactly via hypergeometric
    draws per stratum (identical distribution, vectorized over NPERM)."""
    sub = df[(df.cult == cult) | (df.cult.isin(REF))]
    strata = []
    num_obs = den_obs = 0.0
    for _, g in sub.groupby(["pair", "comune"]):
        n1 = int((g.cult == cult).sum())
        n0 = len(g) - n1
        if n1 == 0 or n0 == 0:
            continue
        k_tot = int(g.conv.sum())
        a = int(g[g.cult == cult].conv.sum())
        n = n1 + n0
        num_obs += a * n0 / n
        den_obs += (k_tot - a) * n1 / n
        strata.append((k_tot, n1, n0, n))
    if den_obs == 0 or not strata:
        return None
    obs = num_obs / den_obs
    num = np.zeros(NPERM)
    den = np.zeros(NPERM)
    for k_tot, n1, n0, n in strata:
        a = rng.hypergeometric(k_tot, n - k_tot, n1, size=NPERM) \
            if k_tot > 0 else np.zeros(NPERM)
        num += a * n0 / n
        den += (k_tot - a) * n1 / n
    rr = np.where(den > 0, num / np.maximum(den, 1e-12), np.inf)
    hits = int((rr <= obs).sum())
    return round((hits + 1) / (NPERM + 1), 4)  # one-sided: cult less converting


def main():
    rng = np.random.default_rng(SEED)
    visits = build_visits()
    tr = transitions(visits)
    print(f"\ntransitions: {len(tr)}  conversions: {int(tr.conv.sum())}  "
          f"coordinates: {tr.groupby(['lat5','lon5']).ngroups}", flush=True)
    by_pair = tr.groupby("pair").agg(n=("conv", "size"), conv=("conv", "sum"))
    print(by_pair.to_string(), flush=True)

    known = tr[tr.cult.notna()]
    print(f"\ncultivar known: {len(known)} ({len(known)/max(len(tr),1):.0%})", flush=True)
    table = []
    for cult, g in known.groupby("cult"):
        n, k = len(g), int(g.conv.sum())
        if n < MIN_CULT_N:
            continue
        lo, hi = wilson(k, n)
        table.append({"cult": cult, "n": n, "conv": k,
                      "rate": round(k / n, 4), "ci95": [lo, hi]})
    table.sort(key=lambda r: -r["n"])

    gate = {}
    for cult in ["leccino", "frantoio", "coratina", "ogliarola barese"]:
        g = known[known.cult == cult]
        if len(g) == 0:
            gate[cult] = {"n": 0}
            continue
        rr, strata = mh_rr(known, cult)
        gate[cult] = {"n": int(len(g)), "conv": int(g.conv.sum()),
                      "mh_rr_vs_ref": rr, "strata_used": strata,
                      "perm_p_one_sided": perm_p(known, cult, rng)
                      if len(g) >= 10 else None}

    ref = known[known.cult.isin(REF)]
    out = {
        "unit": "exact coordinate (5-dp), consecutive campaign visits",
        "reference": sorted(REF),
        "n_transitions": int(len(tr)),
        "n_conversions": int(tr.conv.sum()),
        "n_cultivar_known": int(len(known)),
        "ref_n": int(len(ref)), "ref_conv": int(ref.conv.sum()),
        "ref_rate": round(float(ref.conv.mean()), 4) if len(ref) else None,
        "by_pair": {i: {"n": int(r.n), "conv": int(r.conv)}
                    for i, r in by_pair.iterrows()},
        "cultivar_table_min30": table,
        "gate_checks": gate,
        "caveats": [
            "coordinate identity is not guaranteed tree identity (GPS jitter, replanting)",
            "positives are felled: conversions are terminal, panel is survivor-biased",
            "repeat testing concentrates where the survey chose to look",
            "inspector-recorded cultivar is noisy; cultivar x geography confounded — "
            "MH stratification on pair x comune is the control, not a cure",
        ],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("\nGATE (Leccino):", json.dumps(gate.get("leccino"), ensure_ascii=False))
    print("wrote", OUT_JSON)


if __name__ == "__main__":
    main()

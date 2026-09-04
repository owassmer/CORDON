#!/usr/bin/env python
"""Design-adjusted front-rate estimate c(t) for X. fastidiosa pauca, Puglia 2013-2025.

Ranked action D1 in queries/telos-review-S1-spread.md. Method follows the
Kottelenberg et al. 2021 (Sci Rep 11:1061) design logic: aggregate the moving
survey frame into distance rings from the epidemic origin and use per-ring
POSITIVITY (positives/tests), never raw positive counts. The front position per
campaign is the farthest ring whose positivity clears a threshold among rings
with adequate testing. A campaign whose front sits at (or within one ring of)
the tested frontier is RIGHT-CENSORED by the survey frame and is excluded from
the primary rate fits.

Inputs:  producers/cache/combined.csv  (campaign, lat, lon, olive, pos, t)
Outputs: nowcast/cache/front_rate.json

Run from the repo root:
    .venv/bin/python nowcast/front_rate.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "producers" / "cache" / "combined.csv"
OUT = ROOT / "nowcast" / "cache" / "front_rate.json"

GEOD = Geod(ellps="WGS84")
SEED = 20260816
N_BOOT = 1000  # multinomial resampling of the per-ring (tests, positives) table
               # is exactly row-resampling within campaign, and is fast enough
               # to run the full 1000 reps.

# Primary origin: Gallipoli area (first 2013 detection cluster).
ORIGIN_GALLIPOLI = (40.055, 17.992)  # (lat, lon)

GARGANO_LAT = 41.35  # exclude the 2025 Cagnano Varano focus: separate outbreak

CAMPAIGN_ORDER = [
    "2013-14", "2014-15", "2016-17", "2017-18", "2018-19", "2019-20",
    "2020", "2021", "2022", "2023", "2024", "2025",
]

# Fit windows. 2013-2018 matches the Kottelenberg data window (through Apr 2018).
PERIODS = {
    "2013-2018": ["2013-14", "2014-15", "2016-17", "2017-18"],
    "2018-2021": ["2018-19", "2019-20", "2020", "2021"],
    "2021-2025": ["2021", "2022", "2023", "2024", "2025"],
}

PRIMARY = dict(origin="gallipoli", ring_km=5.0, threshold=0.01, min_tests=200)

# One-factor-at-a-time sensitivity grid around the primary config.
SENSITIVITY_CONFIGS = [
    dict(name="ring_2.5km", origin="gallipoli", ring_km=2.5, threshold=0.01, min_tests=200),
    dict(name="ring_10km", origin="gallipoli", ring_km=10.0, threshold=0.01, min_tests=200),
    dict(name="thr_0.5pct", origin="gallipoli", ring_km=5.0, threshold=0.005, min_tests=200),
    dict(name="thr_2pct", origin="gallipoli", ring_km=5.0, threshold=0.02, min_tests=200),
    dict(name="min_tests_50", origin="gallipoli", ring_km=5.0, threshold=0.01, min_tests=50),
    dict(name="origin_centroid2013", origin="centroid2013", ring_km=5.0, threshold=0.01, min_tests=200),
]


def load_olive() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(DATA, dtype={"campaign": str})
    df["campaign"] = df["campaign"].str.strip()
    n_total = len(df)
    o = df[df["olive"] == True].copy()  # noqa: E712
    n_olive = len(o)

    # Repair transposed coordinates (lat~17.5, lon~40.7: lat/lon swapped).
    swap = (o["lat"] < 30) & (o["lon"].between(39.5, 42.0))
    n_swapped = int(swap.sum())
    o.loc[swap, ["lat", "lon"]] = o.loc[swap, ["lon", "lat"]].values

    # Drop any remaining implausible coordinates.
    ok = o["lat"].between(39.5, 42.5) & o["lon"].between(15.0, 19.5)
    n_dropped = int((~ok).sum())
    o = o[ok]

    # Exclude the Gargano (Cagnano Varano) focus: separate outbreak, not front motion.
    garg = o["lat"] >= GARGANO_LAT
    n_gargano = int(garg.sum())
    n_gargano_pos = int(o.loc[garg, "pos"].sum())
    o = o[~garg].copy()

    audit = dict(
        rows_total=n_total, rows_olive=n_olive, coords_swapped=n_swapped,
        coords_dropped=n_dropped, gargano_rows_excluded=n_gargano,
        gargano_pos_excluded=n_gargano_pos, rows_analyzed=len(o),
        pos_analyzed=int(o["pos"].sum()),
    )
    return o.reset_index(drop=True), audit


def dist_km(origin: tuple[float, float], lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    lat0, lon0 = origin
    _, _, d = GEOD.inv(np.full(lat.shape, lon0), np.full(lat.shape, lat0), lon, lat)
    return d / 1000.0


def ring_table(dist: np.ndarray, pos: np.ndarray, ring_km: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (tests, positives) per ring index 0..max."""
    ring = np.floor(dist / ring_km).astype(int)
    n_rings = ring.max() + 1
    tests = np.bincount(ring, minlength=n_rings)
    positives = np.bincount(ring, weights=pos.astype(float), minlength=n_rings).astype(int)
    return tests, positives


def front_from_rings(tests: np.ndarray, positives: np.ndarray, ring_km: float,
                     threshold: float, min_tests: int) -> dict:
    """Front position + censoring diagnostics from a per-ring table.

    front_km            = center of farthest ring with positivity >= threshold
                          among rings with tests >= min_tests
    frontier_any_km     = center of farthest ring with any tests
    frontier_elig_km    = center of farthest ring with tests >= min_tests
    inner_elig_km       = center of nearest ring with tests >= min_tests
                          (documents the inner edge of the survey frame,
                          e.g. the post-2018 Lecce exit)
    censored            = front within one ring width of frontier_elig
                          (survey frame truncates the front: lower bound only)
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(tests > 0, positives / np.maximum(tests, 1), 0.0)
    eligible = tests >= min_tests
    qualifying = eligible & (rate >= threshold)
    centers = (np.arange(len(tests)) + 0.5) * ring_km

    any_ix = np.nonzero(tests > 0)[0]
    elig_ix = np.nonzero(eligible)[0]
    q_ix = np.nonzero(qualifying)[0]

    out = dict(
        frontier_any_km=float(centers[any_ix[-1]]) if len(any_ix) else None,
        frontier_elig_km=float(centers[elig_ix[-1]]) if len(elig_ix) else None,
        inner_elig_km=float(centers[elig_ix[0]]) if len(elig_ix) else None,
    )
    if len(q_ix) == 0 or len(elig_ix) == 0:
        out.update(front_km=None, censored=None, censor_margin_km=None,
                   tests_beyond_front=None, pos_beyond_front=None)
        return out

    f = q_ix[-1]
    front_km = float(centers[f])
    margin = out["frontier_elig_km"] - front_km
    out.update(
        front_km=front_km,
        censored=bool(margin <= ring_km),  # at or within one ring of the frame edge
        censor_margin_km=float(margin),
        tests_beyond_front=int(tests[f + 1:].sum()),
        pos_beyond_front=int(positives[f + 1:].sum()),
    )
    return out


def slope_fit(times: list[float], fronts: list[float]) -> float | None:
    if len(times) < 2:
        return None
    return float(np.polyfit(np.asarray(times), np.asarray(fronts), 1)[0])


def run_config(o: pd.DataFrame, origin_xy: tuple[float, float], ring_km: float,
               threshold: float, min_tests: int) -> dict:
    """Per-campaign front table + per-period slopes for one configuration."""
    d = dist_km(origin_xy, o["lat"].to_numpy(), o["lon"].to_numpy())
    camp = o["campaign"].to_numpy()
    pos = o["pos"].to_numpy()
    t = o["t"].to_numpy()

    rows = {}
    for c in CAMPAIGN_ORDER:
        m = camp == c
        tests, positives = ring_table(d[m], pos[m], ring_km)
        rec = front_from_rings(tests, positives, ring_km, threshold, min_tests)
        rec.update(campaign=c, t_mid=float(t[m].mean()), n_tests=int(m.sum()),
                   n_pos=int(pos[m].sum()))
        rows[c] = rec

    fits = {}
    for pname, camps in PERIODS.items():
        usable = [c for c in camps
                  if rows[c]["front_km"] is not None and not rows[c]["censored"]]
        naive = [c for c in camps if rows[c]["front_km"] is not None]
        fits[pname] = dict(
            campaigns=camps,
            usable=usable,
            excluded_censored=[c for c in camps
                               if rows[c]["front_km"] is not None and rows[c]["censored"]],
            excluded_no_front=[c for c in camps if rows[c]["front_km"] is None],
            slope_km_per_yr=slope_fit([rows[c]["t_mid"] for c in usable],
                                      [rows[c]["front_km"] for c in usable]),
            n_points=len(usable),
            slope_naive_incl_censored=slope_fit([rows[c]["t_mid"] for c in naive],
                                                [rows[c]["front_km"] for c in naive]),
            n_points_naive=len(naive),
        )
    return dict(campaigns=rows, fits=fits)


def bootstrap_primary(o: pd.DataFrame, origin_xy: tuple[float, float], ring_km: float,
                      threshold: float, min_tests: int, exclusions: dict,
                      n_boot: int, seed: int) -> dict:
    """Bootstrap CIs. Resampling rows with replacement within a campaign is a
    multinomial draw over that campaign's (ring x pos) cells, which is what we
    draw directly (identical distribution, ~1000x faster).

    The censoring exclusion set is FIXED at the observed-data classification:
    a campaign flagged censored stays out of the primary slope in every rep.
    """
    rng = np.random.default_rng(seed)
    d = dist_km(origin_xy, o["lat"].to_numpy(), o["lon"].to_numpy())
    camp = o["campaign"].to_numpy()
    pos = o["pos"].to_numpy()
    t = o["t"].to_numpy()

    tables, tmid = {}, {}
    for c in CAMPAIGN_ORDER:
        m = camp == c
        ring = np.floor(d[m] / ring_km).astype(int)
        n_rings = ring.max() + 1
        # joint cells: (ring, pos)
        neg = np.bincount(ring[~pos[m]], minlength=n_rings)
        p = np.bincount(ring[pos[m]], minlength=n_rings)
        tables[c] = (neg, p)
        tmid[c] = float(t[m].mean())

    front_samples = {c: [] for c in CAMPAIGN_ORDER}
    slope_samples = {pname: [] for pname in PERIODS}
    for _ in range(n_boot):
        fronts = {}
        for c in CAMPAIGN_ORDER:
            neg, p = tables[c]
            cells = np.concatenate([neg, p]).astype(float)
            n = int(cells.sum())
            draw = rng.multinomial(n, cells / n)
            k = len(neg)
            tests_b = draw[:k] + draw[k:]
            pos_b = draw[k:]
            rec = front_from_rings(tests_b, pos_b, ring_km, threshold, min_tests)
            fronts[c] = rec["front_km"]
            front_samples[c].append(rec["front_km"])
        for pname, camps in PERIODS.items():
            usable = [c for c in camps
                      if c in exclusions["usable"][pname] and fronts[c] is not None]
            slope_samples[pname].append(
                slope_fit([tmid[c] for c in usable], [fronts[c] for c in usable]))

    def pct_ci(vals):
        v = [x for x in vals if x is not None]
        if len(v) < max(50, n_boot // 4):
            return None
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

    return dict(
        n_boot=n_boot, seed=seed,
        front_ci={c: pct_ci(front_samples[c]) for c in CAMPAIGN_ORDER},
        front_defined_frac={c: float(np.mean([x is not None for x in front_samples[c]]))
                            for c in CAMPAIGN_ORDER},
        slope_ci={p: pct_ci(slope_samples[p]) for p in PERIODS},
        slope_defined_frac={p: float(np.mean([x is not None for x in slope_samples[p]]))
                            for p in PERIODS},
    )


def main() -> None:
    o, audit = load_olive()

    centroid_2013 = (float(o.loc[(o.campaign == "2013-14") & o.pos, "lat"].mean()),
                     float(o.loc[(o.campaign == "2013-14") & o.pos, "lon"].mean()))
    origins = dict(gallipoli=ORIGIN_GALLIPOLI, centroid2013=centroid_2013)

    primary = run_config(o, origins[PRIMARY["origin"]], PRIMARY["ring_km"],
                         PRIMARY["threshold"], PRIMARY["min_tests"])

    exclusions = dict(usable={p: primary["fits"][p]["usable"] for p in PERIODS})
    boot = bootstrap_primary(o, origins[PRIMARY["origin"]], PRIMARY["ring_km"],
                             PRIMARY["threshold"], PRIMARY["min_tests"],
                             exclusions, N_BOOT, SEED)

    sensitivities = []
    for cfg in SENSITIVITY_CONFIGS:
        res = run_config(o, origins[cfg["origin"]], cfg["ring_km"],
                         cfg["threshold"], cfg["min_tests"])
        sensitivities.append(dict(
            config=cfg,
            fronts={c: dict(front_km=res["campaigns"][c]["front_km"],
                            censored=res["campaigns"][c]["censored"])
                    for c in CAMPAIGN_ORDER},
            slopes={p: dict(slope_km_per_yr=res["fits"][p]["slope_km_per_yr"],
                            n_points=res["fits"][p]["n_points"],
                            usable=res["fits"][p]["usable"],
                            slope_naive_incl_censored=res["fits"][p]["slope_naive_incl_censored"])
                    for p in PERIODS},
        ))

    # Variant fit: 2018-2021 without the 2020 campaign. The 2020 front ring
    # (115-120 km) is the detached Monopoli/Polignano focus at 1.6% positivity
    # on 4,070 tests; in 2021 the same ring holds 0.34% on 12,067 tests, so the
    # point is a survey-intensity artifact of the threshold estimator, not
    # contiguous front motion. The variant tracks the contiguous front only.
    v_camps = [c for c in PERIODS["2018-2021"] if c != "2020"
               and primary["campaigns"][c]["front_km"] is not None
               and not primary["campaigns"][c]["censored"]]
    variant_fits = {
        "2018-2021_excl_2020": dict(
            campaigns=v_camps,
            slope_km_per_yr=slope_fit(
                [primary["campaigns"][c]["t_mid"] for c in v_camps],
                [primary["campaigns"][c]["front_km"] for c in v_camps]),
            rationale=("2020 front ring is the detached Monopoli/Polignano focus; "
                       "its qualification flips with survey intensity (1.6% on 4,070 "
                       "tests in 2020 vs 0.34% on 12,067 tests in 2021)"),
        )
    }

    ours_2013_2018 = primary["fits"]["2013-2018"]["slope_km_per_yr"]
    kott = dict(rate_km_per_yr=10.0, ci95=[7.5, 12.5], window="2013 to Apr 2018",
                source="Kottelenberg et al. 2021, Sci Rep 11:1061, doi:10.1038/s41598-020-79279-x")
    ci = boot["slope_ci"]["2013-2018"]
    overlap = None
    if ours_2013_2018 is not None and ci is not None:
        overlap = bool(ci[0] <= kott["ci95"][1] and kott["ci95"][0] <= ci[1])

    out = dict(
        meta=dict(
            generated=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            script="nowcast/front_rate.py",
            data=str(DATA.relative_to(ROOT)),
            audit=audit,
            origin_primary=dict(name="gallipoli", lat=ORIGIN_GALLIPOLI[0], lon=ORIGIN_GALLIPOLI[1]),
            origin_centroid2013=dict(lat=centroid_2013[0], lon=centroid_2013[1]),
            primary_config=PRIMARY,
            gargano_cut_lat=GARGANO_LAT,
            periods=PERIODS,
            front_definition=("center of farthest ring with positivity >= threshold "
                              "among rings with >= min_tests tests; censored if within "
                              "one ring width of the farthest adequately tested ring"),
            python=sys.version.split()[0],
        ),
        campaigns={c: primary["campaigns"][c] for c in CAMPAIGN_ORDER},
        fits=primary["fits"],
        variant_fits=variant_fits,
        bootstrap=boot,
        external_check=dict(kottelenberg=kott,
                            ours_2013_2018_km_per_yr=ours_2013_2018,
                            ours_ci95=ci, ci_overlap=overlap),
        sensitivities=sensitivities,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT}")

    # Console summary
    print("\ncampaign  t_mid    front_km  frontier_elig  censored  n_tests  n_pos")
    for c in CAMPAIGN_ORDER:
        r = primary["campaigns"][c]
        print(f"{c:8s} {r['t_mid']:8.2f} {str(r['front_km']):>9s} "
              f"{str(r['frontier_elig_km']):>13s} {str(r['censored']):>8s} "
              f"{r['n_tests']:8d} {r['n_pos']:6d}")
    for p in PERIODS:
        f = primary["fits"][p]
        print(f"{p}: slope={f['slope_km_per_yr']} km/yr  n={f['n_points']} "
              f"usable={f['usable']} censored-excluded={f['excluded_censored']} "
              f"CI={boot['slope_ci'][p]}")


if __name__ == "__main__":
    main()

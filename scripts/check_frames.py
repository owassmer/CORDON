"""Re-derive the frame `monitoring.GEOGRAPHIC_FRAME` records for the degree columns.

The campaign workbooks and the CKAN CSV publish `LONGITUDINE` and `LATITUDINE` and
state no datum. The SIT services publish many of the same observations as geometry in
a frame they do state. Every observation published both ways is therefore one equation
whose expected side comes from the publisher, not from this reader: reproject the SIT
point into each candidate geographic frame and see which one the printed pair is.

The check fails when the recorded frame is not the best fit, or when the agreeing share
falls below what the population has shown, so a release published in another datum
cannot enter quietly. It needs the store, so it runs beside `scripts/audit_store.py`
rather than in CI.

    python scripts/check_frames.py [monitoring-source-root]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-c'))

from cordon_d.monitoring import GEOGRAPHIC_FRAME, POINT_TOLERANCE_M, reader_version  # noqa: E402
from cordon_d.store import store_root  # noqa: E402

# Frames a regional Italian publisher plausibly prints degrees in. A candidate is here to
# be excluded by measurement; the winner is whichever the printed pairs actually are.
CANDIDATES = ('EPSG:4326', 'EPSG:4258', 'EPSG:4230', 'EPSG:4265')
# The share of paired observations that must agree. The population shows all but a
# handful; a release in another datum would drop this to near zero.
REQUIRED_AGREEMENT = 0.99


def main():
    import duckdb
    import numpy as np
    from pyproj import Transformer

    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'corpus/sources/monitoring').resolve()
    store = store_root(root)
    readings = store / 'derived' / 'monitoring' / 'readings' / f'*-{reader_version()}.parquet'
    if not list(readings.parent.glob(readings.name)):
        raise SystemExit(f'No derived readings at {reader_version()}; ingest first.')

    spill = store / '.check-frames'
    spill.mkdir(exist_ok=True)
    connection = duckdb.connect()
    connection.execute("SET memory_limit = '1GB'")
    connection.execute('SET threads = 2')
    connection.execute(f"SET temp_directory = '{spill}'")
    pairs = connection.execute(f"""
        WITH r AS (SELECT reference, day, crs, x, y FROM read_parquet('{readings}')
                   WHERE reference IS NOT NULL AND day IS NOT NULL
                     AND x IS NOT NULL AND y IS NOT NULL),
             stated AS (SELECT reference, day, min(x) AS e, min(y) AS n,
                               count(DISTINCT x::VARCHAR||'|'||y::VARCHAR) AS points
                        FROM r WHERE crs <> '{GEOGRAPHIC_FRAME}' GROUP BY 1, 2),
             printed AS (SELECT reference, day, min(x) AS lon, min(y) AS lat,
                                count(DISTINCT x::VARCHAR||'|'||y::VARCHAR) AS points
                         FROM r WHERE crs = '{GEOGRAPHIC_FRAME}' GROUP BY 1, 2),
             frames AS (SELECT DISTINCT crs FROM r WHERE crs <> '{GEOGRAPHIC_FRAME}')
        SELECT s.e, s.n, p.lon, p.lat, (SELECT count(*) FROM frames)
        FROM stated s JOIN printed p ON s.reference = p.reference AND s.day = p.day
        WHERE s.points = 1 AND p.points = 1""").fetchall()
    connection.close()
    if not pairs:
        raise SystemExit('No observation is published in both a stated frame and degrees.')
    if pairs[0][4] != 1:
        raise SystemExit(f'{pairs[0][4]} stated frames in the population; this check assumes one.')

    east = np.array([p[0] for p in pairs], float)
    north = np.array([p[1] for p in pairs], float)
    lon = np.array([p[2] for p in pairs], float)
    lat = np.array([p[3] for p in pairs], float)
    print(f'{len(pairs):,} observations published both ways, at reader {reader_version()}')

    fits = {}
    for candidate in CANDIDATES:
        transformer = Transformer.from_crs('EPSG:32633', candidate, always_xy=True)
        target_lon, target_lat = transformer.transform(east, north)
        metres = np.hypot((lon - target_lon) * 111320.0 * np.cos(np.radians(lat)),
                          (lat - target_lat) * 110540.0)
        metres = metres[np.isfinite(metres)]
        fits[candidate] = (float(np.median(metres)), float((metres <= POINT_TOLERANCE_M).mean()))
        print(f'  {candidate:<12} median residual {fits[candidate][0]:>12.3f} m'
              f'   agreeing {fits[candidate][1]:>7.2%}')

    best = min(fits, key=lambda name: fits[name][0])
    median, agreement = fits[GEOGRAPHIC_FRAME]
    if best != GEOGRAPHIC_FRAME:
        raise SystemExit(f'FAIL: the printed degrees fit {best}, not the recorded '
                         f'{GEOGRAPHIC_FRAME}. The recorded frame is wrong.')
    if agreement < REQUIRED_AGREEMENT:
        raise SystemExit(f'FAIL: only {agreement:.2%} of paired observations agree with '
                         f'{GEOGRAPHIC_FRAME}; the population has shown effectively all. '
                         f'A release may be published in another datum.')
    disagreeing = round(len(pairs) * (1 - agreement))
    print(f'OK: the printed degrees are {GEOGRAPHIC_FRAME}. {agreement:.4%} of pairs agree '
          f'to {POINT_TOLERANCE_M} m; {disagreeing} do not and are exposed as coordinate '
          f'disagreements on their observation.')
    # What this cannot separate, said rather than left for a reader to assume. Without an
    # epoch a transformation between two frames of one datum family is the identity, so
    # any of them reproduces the printed pair exactly. The excluded candidates are the
    # ones that would move a location, which is what the recorded frame has to get right.
    tied = [name for name, (residual, _) in fits.items()
            if name != GEOGRAPHIC_FRAME and residual <= POINT_TOLERANCE_M]
    if tied:
        print(f'    Indistinguishable here, and immaterial at this tolerance: {", ".join(tied)}.')


if __name__ == '__main__':
    main()

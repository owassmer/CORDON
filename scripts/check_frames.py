"""Re-derive the frame `monitoring.GEOGRAPHIC_FRAME` records for the degree columns.

The campaign workbooks and the CKAN CSV publish `LONGITUDINE` and `LATITUDINE` and state
no datum. The SIT services publish many of the same observations as geometry in a frame
they do state, so each observation published both ways is an equation whose expected side
comes from the publisher rather than from this reader.

The test runs per release, because a release is what a publisher changes. Releases that
carry an observation reference are paired by reference and day. The three early workbooks
carry no reference in any row, so nothing pairs them by identity and nothing else in the
program cross-checks them either; they are tested the way the frame was established for
them, by same-day nearest neighbour, because a datum shift is a systematic translation of
a whole point cloud and does not need identity to show.

The check fails when any degree-publishing release contributes no tested pairs, or when a
release's printed degrees fit a candidate other than the recorded frame, or when a
release's agreement falls below what the population has shown. It needs the store, so it
runs beside `scripts/audit_store.py` rather than in CI.

    python scripts/check_frames.py [monitoring-source-root]
"""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-d'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'regulation/stage-c'))

from cordon_d.monitoring import GEOGRAPHIC_FRAME, POINT_TOLERANCE_M, reader_version  # noqa: E402
from cordon_d.store import store_root  # noqa: E402

# Frames a regional Italian publisher plausibly prints degrees in. A candidate is here to
# be excluded by measurement; the winner is whichever the printed pairs actually are.
CANDIDATES = ('EPSG:4326', 'EPSG:4258', 'EPSG:4230', 'EPSG:4265')
# The share of a release's tested pairs that must agree. A release republished in another
# datum would move every one of its points and drop this to zero.
REQUIRED_AGREEMENT = 0.99


def _metres(numpy, lon_a, lat_a, lon_b, lat_b):
    east = (lon_a - lon_b) * 111320.0 * numpy.cos(numpy.radians((lat_a + lat_b) / 2))
    return numpy.hypot(east, (lat_a - lat_b) * 110540.0)


def _nearest(numpy, printed, stated):
    """Offset from each printed point to the nearest stated point on its own day."""
    best = []
    for day, points in printed.items():
        others = stated.get(day)
        if others is None:
            continue
        points, others = numpy.array(points, float), numpy.array(others, float)
        scale = numpy.cos(numpy.radians(points[:, 1].mean())) * 111320.0
        east = points[:, 0][:, None] * scale - others[:, 0][None, :] * scale
        north = (points[:, 1][:, None] - others[:, 1][None, :]) * 110540.0
        best.append(numpy.hypot(east, north).min(axis=1))
    return numpy.concatenate(best) if best else numpy.array([])


def main():
    import duckdb
    import numpy
    from pyproj import Transformer

    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'corpus/sources/monitoring').resolve()
    store = store_root(root)
    readings = store / 'derived' / 'monitoring' / 'readings' / f'*-{reader_version()}.parquet'
    if not list(readings.parent.glob(readings.name)):
        raise SystemExit(f'No derived readings at {reader_version()}; ingest first.')

    spill = Path(tempfile.mkdtemp(prefix='cordon-frames-', dir=store))
    connection = duckdb.connect()
    connection.execute("SET memory_limit = '1GB'")
    connection.execute('SET threads = 2')
    connection.execute(f"SET temp_directory = '{spill}'")
    try:
        frames = [row[0] for row in connection.execute(
            f"""SELECT DISTINCT crs FROM read_parquet('{readings}')
                WHERE crs IS NOT NULL AND crs <> '{GEOGRAPHIC_FRAME}'""").fetchall()]
        if len(frames) != 1:
            raise SystemExit(f'{len(frames)} stated frames in the population; this check assumes one.')
        stated_frame = frames[0]

        releases = connection.execute(f"""
            SELECT release, count(*) AS readings,
                   count(*) FILTER (WHERE reference IS NOT NULL AND day IS NOT NULL) AS identified
            FROM read_parquet('{readings}')
            WHERE crs = '{GEOGRAPHIC_FRAME}' AND x IS NOT NULL AND y IS NOT NULL
            GROUP BY 1 ORDER BY 2 DESC""").fetchall()
        print(f'{len(releases)} degree-publishing releases, stated frame {stated_frame}, '
              f'reader {reader_version()}')

        to_degrees = {c: Transformer.from_crs(stated_frame, c, always_xy=True) for c in CANDIDATES}
        failures, agreeing_max, disagreeing_min, tested_total = [], 0.0, None, 0
        for release, count, identified in releases:
            name = release.rsplit('/', 1)[-1]
            if identified:
                pairs = connection.execute(f"""
                    WITH r AS (SELECT reference, day, crs, x, y, release FROM read_parquet('{readings}')
                               WHERE reference IS NOT NULL AND day IS NOT NULL
                                 AND x IS NOT NULL AND y IS NOT NULL),
                         s AS (SELECT reference, day, min(x) e, min(y) n,
                                      count(DISTINCT x::VARCHAR||'|'||y::VARCHAR) pts
                               FROM r WHERE crs = '{stated_frame}' GROUP BY 1, 2),
                         d AS (SELECT reference, day, min(x) lon, min(y) lat,
                                      count(DISTINCT x::VARCHAR||'|'||y::VARCHAR) pts
                               FROM r WHERE crs = '{GEOGRAPHIC_FRAME}'
                                 AND release = '{release}' GROUP BY 1, 2)
                    SELECT s.e, s.n, d.lon, d.lat FROM s JOIN d USING (reference, day)
                    WHERE s.pts = 1 AND d.pts = 1""").fetchall()
                if not pairs:
                    failures.append(f'{name}: publishes {count:,} located readings and no pair is testable')
                    continue
                east = numpy.array([p[0] for p in pairs], float)
                north = numpy.array([p[1] for p in pairs], float)
                lon = numpy.array([p[2] for p in pairs], float)
                lat = numpy.array([p[3] for p in pairs], float)
                fits = {}
                for candidate, transformer in to_degrees.items():
                    target = transformer.transform(east, north)
                    residual = _metres(numpy, lon, lat, numpy.asarray(target[0]), numpy.asarray(target[1]))
                    fits[candidate] = residual[numpy.isfinite(residual)]
                method = 'identity'
            else:
                # No reference in any row, so identity pairing is impossible. A datum shift
                # translates the whole cloud, which nearest-neighbour offsets expose.
                printed = {}
                for day, lon, lat in connection.execute(f"""
                        SELECT day, x, y FROM read_parquet('{readings}')
                        WHERE crs = '{GEOGRAPHIC_FRAME}' AND release = '{release}'
                          AND x IS NOT NULL AND y IS NOT NULL AND day IS NOT NULL""").fetchall():
                    printed.setdefault(day, []).append((lon, lat))
                stated = {}
                for day, e, n in connection.execute(f"""
                        SELECT day, x, y FROM read_parquet('{readings}')
                        WHERE crs = '{stated_frame}' AND x IS NOT NULL AND day IN (
                            SELECT DISTINCT day FROM read_parquet('{readings}')
                            WHERE crs = '{GEOGRAPHIC_FRAME}' AND release = '{release}')""").fetchall():
                    stated.setdefault(day, []).append((e, n))
                fits = {}
                for candidate, transformer in to_degrees.items():
                    converted = {}
                    for day, points in stated.items():
                        array = numpy.array(points, float)
                        target = transformer.transform(array[:, 0], array[:, 1])
                        converted[day] = list(zip(numpy.asarray(target[0]), numpy.asarray(target[1])))
                    fits[candidate] = _nearest(numpy, printed, converted)
                if not len(fits[GEOGRAPHIC_FRAME]):
                    failures.append(f'{name}: publishes {count:,} located readings, carries no '
                                    f'reference, and shares no day with the stated frame')
                    continue
                method = 'proximity'

            best = min(fits, key=lambda c: float(numpy.median(fits[c])))
            residual = fits[GEOGRAPHIC_FRAME]
            agreement = float((residual <= POINT_TOLERANCE_M).mean())
            tested_total += len(residual)
            agreeing = residual[residual <= POINT_TOLERANCE_M]
            disagreeing = residual[residual > POINT_TOLERANCE_M]
            if len(agreeing):
                agreeing_max = max(agreeing_max, float(agreeing.max()))
            if len(disagreeing):
                nearest = float(disagreeing.min())
                disagreeing_min = nearest if disagreeing_min is None else min(disagreeing_min, nearest)
            print(f'  {name:<24} {method:<9} {len(residual):>9,} tested   '
                  f'median {float(numpy.median(residual)):>9.3f} m   agreeing {agreement:>7.2%}')
            if best != GEOGRAPHIC_FRAME:
                failures.append(f'{name}: printed degrees fit {best}, not the recorded {GEOGRAPHIC_FRAME}')
            elif agreement < REQUIRED_AGREEMENT:
                failures.append(f'{name}: only {agreement:.2%} of tested pairs agree with '
                                f'{GEOGRAPHIC_FRAME}; it may be published in another datum')

        if failures:
            for failure in failures:
                print('FAIL', failure)
            raise SystemExit(f'{len(failures)} release(s) do not support {GEOGRAPHIC_FRAME}.')
        print(f'\nOK: every degree-publishing release supports {GEOGRAPHIC_FRAME} over '
              f'{tested_total:,} tested pairs.')
        print(f'    The agreeing pairs sit within {agreeing_max:.5f} m of each other, against '
              f'POINT_TOLERANCE_M = {POINT_TOLERANCE_M} m. A proximity-tested pair is a nearest '
              f'neighbour rather than the same observation, so how far the non-agreeing ones sit '
              f'is not a bound on anything and is not reported; the tolerance margin is measured '
              f'over compared publications, and `monitoring.POINT_TOLERANCE_M` states it.')
        print('    Frames of one datum family are indistinguishable here: without an epoch the '
              'transformation between them is the identity, so any of them reproduces the '
              'printed pair. The excluded candidates are the ones that would move a location.')
    finally:
        connection.close()
        shutil.rmtree(spill, ignore_errors=True)


if __name__ == '__main__':
    main()

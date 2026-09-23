"""Positional error as removal excess: image steps, control correction, radial bound, consumer."""
from datetime import date
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

import numpy as np

from cordon_c.core import MissingInput
from cordon_d import positional as P

PX = P.PIXEL_M
SIZE = int(round(2 * P.CHIP_HALF_M / PX))
CENTRE = (SIZE / 2, SIZE / 2)


def scene(crowns, *, rng_seed=1, removed=(), leafless=()):
    """Bright soil with a road and dark disk crowns; crowns in `removed` become soil and in
    `leafless` become a branch pattern of soil-like mean brightness."""
    rng = np.random.default_rng(rng_seed)
    image = 170 + rng.normal(0, 4, (SIZE, SIZE))
    image[:, 40:52] = 225                          # a road: stable structure
    image[480:486, :] = 120                         # a wall
    rows, cols = np.mgrid[:SIZE, :SIZE]
    for index, (r, c, radius_m) in enumerate(crowns):
        disk = np.hypot(rows - r, cols - c) <= radius_m / PX
        if index in removed:
            continue
        if index in leafless:
            image[disk] = np.where(((rows + cols) // 2 % 2 == 0)[disk], 125, 205)
        else:
            image[disk] = 70
    return np.repeat(image[..., None], 3, axis=2).clip(0, 255).astype(np.float32)


def translate(image, dy, dx):
    out = np.full_like(image, 170)
    h, w = image.shape[:2]
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = image[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


# crowns: (row, col, radius m); crown 0 sits 6 m east of the point, crown 6 56.6 m north-east
CROWNS = [(CENTRE[0], CENTRE[1] + 30, 3.0), (CENTRE[0] - 60, CENTRE[1] - 50, 3.0), (CENTRE[0] + 70, CENTRE[1] + 60, 2.5),
          (CENTRE[0] - 120, CENTRE[1] + 110, 3.0), (CENTRE[0] + 150, CENTRE[1] - 140, 3.0), (CENTRE[0] + 20, CENTRE[1] - 90, 2.5),
          (CENTRE[0] - 200, CENTRE[1] + 200, 3.0)]


class ImageSteps(unittest.TestCase):
    def test_coregistration_recovers_the_shift_between_years(self):
        before = scene(CROWNS)
        after = translate(scene(CROWNS, rng_seed=2), 3, -2)
        score, dy, dx = P.coregister(before, after)
        self.assertEqual((dy, dx), (-3, 2))
        self.assertGreater(score, P.COREGISTRATION['min_ncc'])

    def test_every_removed_crown_of_the_chip_is_found_and_none_is_chosen(self):
        before = scene(CROWNS)
        after = translate(scene(CROWNS, rng_seed=2, removed={0, 1, 6}), 3, -2)
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0))
        self.assertEqual(status, 'counted')
        centres = sorted(c['centre_m'] for c in detail['vanished'])
        self.assertEqual(len(centres), 3)
        self.assertAlmostEqual(centres[0], 6.0, delta=0.3)                        # crown 0
        self.assertAlmostEqual(centres[1], np.hypot(60, 50) * PX, delta=0.3)      # crown 1
        self.assertAlmostEqual(centres[2], np.hypot(200, 200) * PX, delta=0.3)    # crown 6, beyond 50 m
        self.assertNotIn('distance_m', detail)

    def test_a_leafless_tree_is_not_a_removal(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0}, leafless={2})
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0))
        self.assertEqual(status, 'counted')
        self.assertEqual([round(c['centre_m']) for c in detail['vanished']], [6])

    def test_the_register_only_refutes_a_bound(self):
        trees = [(100.0, 30.0), (140.0, 0.0)]
        self.assertTrue(P.register_refutes(100.0, 0.0, 20.0, trees))    # nearest registered tree 30 m off
        self.assertFalse(P.register_refutes(100.0, 0.0, 35.0, trees))   # one within: not refuted, not confirmed
        self.assertIsNone(P.register_refutes(100.0, 0.0, P.REGISTER_REACH_M + 1, trees))

    def test_absence_needs_a_cleared_footprint_and_a_lost_pattern(self):
        cleared = (1.0, 1.0, 0.0, 0.1)          # brightness, texture, footprint canopy, persistence
        self.assertTrue(P._absent(cleared))
        self.assertFalse(P._absent((1.0, 1.0, 0.3, 0.1)))   # regrowth or a nearby crown on the footprint
        self.assertFalse(P._absent((1.0, 1.0, 0.0, 0.6)))   # the crown-in-ring pattern persists

    def test_a_crown_the_later_image_places_apart_keeps_its_pattern(self):
        from scipy import ndimage
        radiometry = lambda image: ndimage.gaussian_filter(image.mean(axis=2), 1.5)  # noqa: E731
        before = radiometry(scene(CROWNS))
        r, c, radius = CROWNS[2]
        rows, cols = np.mgrid[:SIZE, :SIZE]
        rr, cc = np.nonzero(np.hypot(rows - r, cols - c) <= (radius + 3.0) / PX)
        moved = [x if i != 2 else (r + 6, c - 6, radius) for i, x in enumerate(CROWNS)]  # 1.7 m apart
        standing = P._persistence(before, radiometry(scene(moved, rng_seed=2) * 0.8 + 30), rr, cc)
        gone = P._persistence(before, radiometry(scene(CROWNS, rng_seed=2, removed={2})), rr, cc)
        self.assertGreater(standing, P.CHANGE['persist_max'])
        self.assertLess(gone, P.CHANGE['persist_max'])

    def test_the_persistence_correlation_equals_the_direct_sum(self):
        rng = np.random.default_rng(11)
        a, b = rng.normal(size=(80, 80)), rng.normal(size=(80, 80))
        b[:5, :] = np.nan                                                     # not held in the other image
        rows, cols = np.mgrid[:80, :80]
        rr, cc = np.nonzero(np.hypot(rows - 12, cols - 40) <= 9)             # near the chip edge
        x = (a[rr, cc] - a[rr, cc].mean()) / (a[rr, cc].std() + 1e-9)
        s, best = int(round(P.CHANGE['persist_search_m'] / PX)), -1.0
        for dy in range(-s, s + 1):
            for dx in range(-s, s + 1):
                r, c = rr + dy, cc + dx
                ok = (r >= 0) & (r < 80) & (c >= 0) & (c < 80)
                if ok.mean() < 0.9:
                    continue
                y = b[r[ok], c[ok]]
                keep = np.isfinite(y)
                if keep.sum() < P.CHANGE['min_pixels']:
                    continue
                u, v = x[ok][keep], y[keep]
                best = max(best, float(((u - u.mean()) * (v - v.mean()) / (v.std() + 1e-9)).mean()))
        self.assertAlmostEqual(P._persistence(a, b, rr, cc), best, places=6)

    def test_no_vanished_crown_is_counted_not_dropped(self):
        before = scene(CROWNS)
        status, detail = P.measure(before, scene(CROWNS, rng_seed=2), CENTRE, (0.0, 0.0))
        self.assertEqual((status, detail['vanished']), ('counted', []))
        self.assertEqual(len(detail['ring_area_m2']), int(P.RADIAL['background_m'][1] / P.RADIAL['ring_m']))

    def test_a_crown_that_reappears_later_is_not_vanished(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0, 1})
        later = translate(scene(CROWNS, rng_seed=4, removed={0}), -2, 1)      # crown 1 is back
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0), [('after', 2023, later)])
        self.assertEqual(status, 'counted')
        self.assertEqual([round(c['centre_m']) for c in detail['vanished']], [6])
        self.assertEqual((detail['rejected'], detail['years_after']), (1, [2023]))

    def test_a_crown_absent_before_the_finding_is_not_vanished(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0, 1})
        earlier = scene(CROWNS, rng_seed=5, removed={1})                     # crown 1 not yet there
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0), [('before', 2011, earlier)])
        self.assertEqual([round(c['centre_m']) for c in detail['vanished']], [6])
        self.assertEqual(detail['rejected'], 1)

    def test_a_removal_absent_in_every_later_image_stays_vanished(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0, 1})
        others = [('after', 2022, scene(CROWNS, rng_seed=6, removed={0, 1})),
                  ('before', 2011, translate(scene(CROWNS, rng_seed=7), 2, 2))]
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0), others)
        self.assertEqual((status, len(detail['vanished']), detail['rejected']), ('counted', 2, 0))

    def test_the_control_correction_moves_the_point_before_distances(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0})
        _, plain = P.measure(before, after, CENTRE, (0.0, 0.0))
        _, corrected = P.measure(before, after, CENTRE, (2.0, 0.0))  # image content 2 m east of ground
        self.assertAlmostEqual(plain['vanished'][0]['centre_m'] - corrected['vanished'][0]['centre_m'], 2.0, delta=0.3)

    def test_ring_areas_cover_the_interior_only(self):
        areas = P.ring_areas(CENTRE, (SIZE, SIZE))
        for k in (0, 10, 40, 53):
            self.assertAlmostEqual(areas[k], np.pi * ((k + 1) ** 2 - k ** 2), delta=0.03 * np.pi * (2 * k + 1) + 0.2)
        corner = P.ring_areas((60.0, 60.0), (SIZE, SIZE))                   # point 12 m from two edges
        self.assertLess(corner[30], 0.6 * areas[30])


def synthetic_release(n, spread_m, background_per_m2, seed=0, share=1.0):
    """Per-positive (counts, areas): full annuli, Poisson background crowns and, for a `share` of
    positives, the recorded tree at a 2-D normal offset of `spread_m` per axis."""
    rng = np.random.default_rng(seed)
    rings = int(P.RADIAL['background_m'][1] / P.RADIAL['ring_m'])
    edges = np.arange(rings + 1) * P.RADIAL['ring_m']
    areas = np.pi * (edges[1:] ** 2 - edges[:-1] ** 2)
    counts = rng.poisson(background_per_m2 * areas, size=(n, rings)).astype(float)
    for i in range(n):
        if rng.random() < share:
            k = int(np.hypot(*rng.normal(0, spread_m, 2)) / P.RADIAL['ring_m'])
            if k < rings:
                counts[i, k] += 1
    return counts, np.tile(areas, (n, 1))


class RadialBound(unittest.TestCase):
    def test_the_excess_over_background_locates_the_recorded_trees(self):
        counts, areas = synthetic_release(800, 3.0, 2e-4, share=0.6)
        bound = P.radial_bound(counts, areas)
        self.assertIsNone(bound['cause'])
        self.assertAlmostEqual(bound['background_per_m2'], 2e-4, delta=0.3e-4)
        self.assertGreater(bound['excess_lower'], 400)                   # about 480 recorded trees were placed
        self.assertLess(bound['excess_lower'], 520)
        # a 2-D normal with 3 m per axis holds 99% within 9.1 m and 99.9% within 11.1 m
        self.assertGreaterEqual(bound['radius_m'], 8.0)
        self.assertLessEqual(bound['radius_m'], 14.0)
        self.assertGreaterEqual(bound['beyond_upper'], 0)

    def test_a_small_release_states_how_much_it_could_hide_beyond_its_bound(self):
        large = P.radial_bound(*synthetic_release(800, 3.0, 2e-4, share=0.6))
        small = P.radial_bound(*synthetic_release(60, 3.0, 2e-4, share=0.6, seed=3))
        self.assertIsNone(small['cause'])
        self.assertGreater(small['beyond_upper_share'], large['beyond_upper_share'])

    def test_no_excess_gives_no_bound(self):
        bound = P.radial_bound(*synthetic_release(400, 3.0, 2e-4, share=0.0))
        self.assertIsNone(bound['radius_m'])
        self.assertEqual(bound['cause'], 'no excess of vanished crowns over background near the points')

    def test_an_excess_reaching_the_background_band_gives_no_bound(self):
        bound = P.radial_bound(*synthetic_release(800, 20.0, 1e-4, share=1.0))
        self.assertIsNone(bound['radius_m'])
        # the recorded trees spill into the band: either its density is not flat or the excess reaches it
        self.assertIn(bound['cause'], ('the excess reaches the background band', 'the background band is not flat'))


class Reach(unittest.TestCase):
    def test_bracketing_images_follow_flight_windows_and_coverage(self):
        lecce = (770000.0, 4470000.0)
        bari = (660000.0, 4550000.0)
        self.assertEqual(P.bracket(date(2020, 10, 27), *lecce), (2019, 2022))
        self.assertEqual(P.bracket(date(2015, 6, 1), *lecce), (2013, 2016))    # inside the 2015 flight
        self.assertEqual(P.bracket(date(2015, 12, 1), *lecce), (2015, 2016))   # after the 2015 flight
        self.assertEqual(P.bracket(date(2016, 3, 1), *bari), (2013, 2019))     # 2015 does not cover Bari
        self.assertIsNone(P.bracket(date(2023, 5, 1), *lecce))
        self.assertEqual(P.held(date(2020, 10, 27), *lecce), ([2011, 2013, 2015, 2016, 2019], [2022, 2023]))

    def test_a_tile_s_own_flight_days_place_the_image_around_the_finding(self):
        lecce = (770000.0, 4470000.0)
        feature = {'attributes': {'date_volo': '20220602, 20220614, 20220603'},
                   'geometry': {'rings': [[[769000.0, 4469000.0], [769000.0, 4471000.0], [771000.0, 4471000.0],
                                           [771000.0, 4469000.0], [769000.0, 4469000.0]]]}}
        tiles = P.flight_tiles([feature])
        self.assertEqual(tiles, [(769000.0, 4469000.0, 771000.0, 4471000.0, date(2022, 6, 2), date(2022, 6, 14))])
        saved = dict(P._TILES)
        P._TILES.clear()
        try:
            self.assertIsNone(P.flown(2022, *lecce))                               # no index: the year alone
            self.assertEqual(P.bracket(date(2022, 8, 1), *lecce), (2019, 2023))
            P.use_flight_tiles(2022, tiles)
            self.assertEqual(P.flown(2022, *lecce), (date(2022, 6, 2), date(2022, 6, 14)))
            self.assertEqual(P.bracket(date(2022, 8, 1), *lecce), (2022, 2023))    # after the tile's flight
            self.assertEqual(P.bracket(date(2022, 3, 1), *lecce), (2019, 2022))    # before it
            self.assertEqual(P.bracket(date(2022, 6, 10), *lecce), (2019, 2023))   # during it: neither
            self.assertEqual(P.held(date(2020, 10, 27), *lecce), ([2011, 2013, 2015, 2016, 2019], [2022, 2023]))
            # a chip reaching a later tile takes that tile's days too
            later = dict(feature, attributes={'date_volo': '20220720'},
                         geometry={'rings': [[[771000.0, 4469000.0], [771000.0, 4471000.0], [773000.0, 4471000.0],
                                              [773000.0, 4469000.0], [771000.0, 4469000.0]]]})
            P.use_flight_tiles(2022, P.flight_tiles([feature, later]))
            self.assertEqual(P.flown(2022, 770950.0, 4470000.0), (date(2022, 6, 2), date(2022, 7, 20)))
            self.assertEqual(P.bracket(date(2022, 7, 1), 770950.0, 4470000.0), (2019, 2023))
            # 2023 states no flight days: its award (7 Jan 2023) and its year fix the interval
            self.assertEqual(P.flown(2023, *lecce), (date(2023, 1, 7), date(2023, 12, 31)))
            self.assertEqual(P.bracket(date(2023, 1, 3), *lecce), (2022, 2023))
            self.assertFalse(P.same_season(2015, 2023))                            # an interval is not a window
        finally:
            P._TILES.clear()
            P._TILES.update(saved)

    def test_a_same_season_pair_is_preferred_over_the_tightest(self):
        self.assertFalse(P.same_season(2011, 2015))        # January-June against May-November
        self.assertFalse(P.same_season(2019, 2022))        # no stated window
        saved = dict(P.IMAGES[2013])
        try:
            P.IMAGES[2013]['window'] = (date(2013, 6, 1), date(2013, 9, 30))
            self.assertTrue(P.same_season(2013, 2015))
            self.assertEqual(P.bracket(date(2014, 3, 1), 770000.0, 4470000.0), (2013, 2015))
            P.IMAGES[2013]['window'] = (date(2013, 1, 1), date(2013, 2, 28))
            self.assertEqual(P.bracket(date(2014, 3, 1), 770000.0, 4470000.0), (2013, 2015))  # tightest
            P.IMAGES[2011]['window'], saved_2011 = (date(2011, 6, 1), date(2011, 9, 30)), P.IMAGES[2011]['window']
            self.assertEqual(P.bracket(date(2014, 3, 1), 770000.0, 4470000.0), (2011, 2015))  # same season wins
            P.IMAGES[2011]['window'] = saved_2011
        finally:
            P.IMAGES[2013].clear()
            P.IMAGES[2013].update(saved)

    def test_release_class(self):
        self.assertEqual(P.release_of(['64', 'CAMP_2021.xlsx'], [], date(2021, 1, 1)), ('campaign-workbook', 'CAMP_2021.xlsx'))
        self.assertEqual(P.release_of(['camp_2020_2022.csv'], [], date(2021, 1, 1)), ('campaign-csv', 'camp_2020_2022.csv'))
        self.assertEqual(P.release_of(['45'], ['Positivi 2016'], date(2016, 4, 1)), ('sit', 'SIT 2016'))


def counted_rows(release, counts, areas, imagery_m):
    ring = P.RADIAL['ring_m']
    rows = []
    for c, a in zip(counts, areas):
        vanished = [{'centre_m': (k + 0.5) * ring, 'interior': True} for k in np.repeat(np.arange(len(c)), c.astype(int))]
        rows.append({'source': 'campaign-workbook', 'release': release, 'status': 'counted', 'vanished': vanished,
                     'ring_area_m2': list(a), 'imagery_m': imagery_m, 'grid_m_per_m': 4e-4})
    return rows


class Consumer(unittest.TestCase):
    def setUp(self):
        from cordon_d.evidence import Source
        from cordon_d.spatial import CoordinateObservation
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        blobs = {}
        for name in ('monitoring', 'bounds'):
            data = name.encode() * 10
            (self.root / name).write_bytes(data)
            blobs[name] = Source(name, name, sha256(data).hexdigest(), 'official-dataset', 'public')
        self.sources = blobs
        self.observation = CoordinateObservation(('observation', '1'), (770000.0, 4470000.0), (770000.0, 4470000.0),
                                                 'EPSG:32633', (blobs['monitoring'],), ())
        self.rows = counted_rows('CAMP_2021.xlsx', *synthetic_release(800, 2.0, 2e-4, share=0.6), 0.9)
        self.rows[0]['imagery_m'] = 1.3
        self.rows += [
            {'source': 'campaign-workbook', 'release': 'CAMP_2021.xlsx', 'status': 'unread', 'cause': 'x'},
            {'source': 'campaign-workbook', 'release': 'CAMP_2021.xlsx', 'status': 'out_of_reach',
             'cause': 'no held image after the finding'},
            {'source': 'campaign-workbook', 'release': 'CAMP_2024.xlsx', 'status': 'out_of_reach',
             'cause': 'no held image after the finding'},
        ]
        self.bounds = P.release_bounds(self.rows)

    def tearDown(self):
        self.directory.cleanup()

    def test_release_bound_is_the_radius_plus_the_imagery_term_and_grid(self):
        entry = self.bounds[('campaign-workbook', 'CAMP_2021.xlsx')]
        self.assertEqual((entry['counted'], entry['unread'], entry['out_of_reach'], entry['n']), (800, 1, 1, 800))
        self.assertAlmostEqual(entry['bound_m'], entry['radius_m'] + 1.3 + entry['radius_m'] * 4e-4, places=2)
        self.assertIsNone(self.bounds[('campaign-workbook', 'CAMP_2024.xlsx')]['bound_m'])

    def test_every_positive_of_the_release_reaches_the_distance_consumer(self):
        from shapely.geometry import Point
        from cordon_c.spatial import MetricGeometry, distance_test
        from cordon_d.spatial import metric_point
        day = date(2021, 5, 4)
        entry = self.bounds[('campaign-workbook', 'CAMP_2021.xlsx')]
        for row in (self.rows[0], self.rows[-3], self.rows[-2]):
            qualification = P.qualify(self.observation, row, self.bounds, context='removal-radius', event_date=day,
                                      sources=(self.sources['bounds'],))
            self.assertEqual(qualification.error_m, entry['bound_m'])
            self.assertIn('n=800', qualification.support[0].reading)
            point = metric_point(self.observation, context='removal-radius', event_date=day, root=self.root,
                                 qualification=qualification)
            self.assertEqual(point.error_m, qualification.error_m)
        self.assertLess(entry['bound_m'], 20)
        for separation, expected in [(3, True), (50, None), (80, False)]:
            other = MetricGeometry(Point(point.geometry.x + separation, point.geometry.y), point.crs, 10)
            self.assertIs(distance_test(point, other, 50, '<=').truth, expected)

    def test_a_changed_measurement_changes_the_consumer_result(self):
        from shapely.geometry import Point
        from cordon_c.spatial import MetricGeometry, distance_test
        from cordon_d.spatial import metric_point
        day = date(2021, 5, 4)
        wide = P.release_bounds(counted_rows('CAMP_2021.xlsx', *synthetic_release(800, 6.0, 2e-4, share=0.6), 0.9))
        results = []
        for bounds in (self.bounds, wide):
            q = P.qualify(self.observation, self.rows[0], bounds, context='removal-radius', event_date=day,
                          sources=(self.sources['bounds'],))
            point = metric_point(self.observation, context='removal-radius', event_date=day, root=self.root,
                                 qualification=q)
            other = MetricGeometry(Point(point.geometry.x + 62, point.geometry.y), point.crs, 0)
            results.append(distance_test(point, other, 50, '<=').truth)
        self.assertEqual(results, [False, None])

    def test_no_bound_and_out_of_reach_are_refused(self):
        with self.assertRaises(MissingInput):
            P.qualify(self.observation, self.rows[-1], self.bounds, context='c', event_date=date(2024, 1, 1),
                      sources=(self.sources['bounds'],))


if __name__ == '__main__':
    unittest.main()

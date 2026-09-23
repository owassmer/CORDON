"""Positional error from removal identity: image steps, control correction, bounds, consumer."""
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


# crowns: (row, col, radius m); crown 0 sits 6 m east of the point
CROWNS = [(CENTRE[0], CENTRE[1] + 30, 3.0), (CENTRE[0] - 60, CENTRE[1] - 50, 3.0), (CENTRE[0] + 70, CENTRE[1] + 60, 2.5),
          (CENTRE[0] - 120, CENTRE[1] + 110, 3.0), (CENTRE[0] + 150, CENTRE[1] - 140, 3.0), (CENTRE[0] + 20, CENTRE[1] - 90, 2.5)]


class ImageSteps(unittest.TestCase):
    def test_coregistration_recovers_the_shift_between_years(self):
        before = scene(CROWNS)
        after = translate(scene(CROWNS, rng_seed=2), 3, -2)
        score, dy, dx = P.coregister(before, after)
        self.assertEqual((dy, dx), (-3, 2))
        self.assertGreater(score, P.COREGISTRATION['min_ncc'])

    def test_every_removed_crown_is_a_candidate_and_the_error_is_its_far_edge(self):
        before = scene(CROWNS)
        after = translate(scene(CROWNS, rng_seed=2, removed={0, 1}), 3, -2)
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0))
        self.assertEqual(status, 'measured')
        near = sorted(c['near_m'] for c in detail['candidates'])
        self.assertEqual(len(near), 2)
        self.assertAlmostEqual(near[0], 6 - 3, delta=0.5)                      # crown 0
        self.assertAlmostEqual(near[1], np.hypot(60, 50) * PX - 3, delta=0.5)  # crown 1
        far_of_1 = np.hypot(60, 50) * PX + 3.0
        self.assertAlmostEqual(detail['distance_m'], far_of_1, delta=0.5)   # the farthest, not the nearest

    def test_a_leafless_tree_is_not_a_removal(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0}, leafless={2})
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0))
        self.assertEqual(status, 'measured')
        self.assertEqual([round(c['near_m']) for c in detail['candidates']], [3])

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

    def test_no_vanished_crown_is_unmeasured_not_dropped(self):
        before = scene(CROWNS)
        status, detail = P.measure(before, scene(CROWNS, rng_seed=2), CENTRE, (0.0, 0.0))
        self.assertEqual((status, detail['cause']), ('unmeasured', "no crown carries removal's signature within the radius"))

    def test_a_crown_that_reappears_later_is_not_a_candidate(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0, 1})
        later = translate(scene(CROWNS, rng_seed=4, removed={0}), -2, 1)      # crown 1 is back
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0), [('after', 2023, later)])
        self.assertEqual(status, 'measured')
        self.assertEqual([round(c['near_m']) for c in detail['candidates']], [3])
        self.assertEqual((detail['rejected'], detail['years_after']), (1, [2023]))

    def test_a_crown_absent_before_the_finding_is_not_a_candidate(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0, 1})
        earlier = scene(CROWNS, rng_seed=5, removed={1})                     # crown 1 not yet there
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0), [('before', 2011, earlier)])
        self.assertEqual([round(c['near_m']) for c in detail['candidates']], [3])
        self.assertEqual(detail['rejected'], 1)

    def test_a_removal_absent_in_every_later_image_stays_a_candidate(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0, 1})
        others = [('after', 2022, scene(CROWNS, rng_seed=6, removed={0, 1})),
                  ('before', 2011, translate(scene(CROWNS, rng_seed=7), 2, 2))]
        status, detail = P.measure(before, after, CENTRE, (0.0, 0.0), others)
        self.assertEqual((status, len(detail['candidates']), detail['rejected']), ('measured', 2, 0))

    def test_the_control_correction_moves_the_point_before_distances(self):
        before = scene(CROWNS)
        after = scene(CROWNS, rng_seed=2, removed={0})
        _, plain = P.measure(before, after, CENTRE, (0.0, 0.0))
        _, corrected = P.measure(before, after, CENTRE, (2.0, 0.0))  # image content 2 m east of ground
        self.assertAlmostEqual(plain['distance_m'] - corrected['distance_m'], 2.0, delta=0.3)


class ControlPoints(unittest.TestCase):
    def offsets(self):
        rng = np.random.default_rng(3)
        rows = [P.ControlOffset(f'v{i}', 700000 + 1000 * (i % 5), 4450000 + 1000 * (i // 5),
                                1.0 + rng.normal(0, 0.1), -0.5 + rng.normal(0, 0.1)) for i in range(20)]
        rows.append(P.ControlOffset('outlier', 702000, 4451000, 4.0, -0.5))
        return rows

    def test_local_fit_takes_the_systematic_shift_and_carries_only_the_residual(self):
        offsets = self.offsets()
        dx, dy, near = P.local_shift(offsets, 702000, 4451000)
        self.assertAlmostEqual(dx, 1.0, delta=0.15)
        self.assertAlmostEqual(dy, -0.5, delta=0.15)
        loo = P.residuals(offsets)
        self.assertGreater(loo['outlier'], 2.5)
        self.assertLess(np.percentile([v for k, v in loo.items() if k != 'outlier'], 95), 0.5)
        term = P.imagery_term(offsets, loo, 702000, 4451000)
        self.assertEqual(term[2], loo['outlier'])     # the largest residual of the fitting features

    def test_the_vertex_is_located_once_and_each_year_offset_follows_its_registration(self):
        size = int(round(2 * P.CONTROL_HALF_M / PX))
        rng = np.random.default_rng(9)
        ground = 170 + rng.normal(0, 3, (size, size))
        for r, c in rng.integers(10, size - 10, (25, 2)):                 # stable texture to register on
            ground[r - 3:r + 3, c - 3:c + 3] = rng.choice([90, 230])
        corner = (size // 2 - 2, size // 2 + 5)                           # the wall corner, 1.1-1.7 m east
        ground[corner[0]:corner[0] + 3, :corner[1] + 3] = 60                # a wall running west
        ground[corner[0]:, corner[1]:corner[1] + 3] = 60                    # and one running south
        chips, shifts = {}, {2016: (0, 0), 2019: (3, -2), 2022: (-4, 1), 2023: (1, 4)}
        for year, (dy, dx) in shifts.items():
            image = np.repeat((ground + rng.normal(0, 2, ground.shape))[..., None], 3, axis=2)
            chips[year] = translate(image.clip(0, 255).astype(np.float32), dy, dx)
        located = P.locate_vertex(chips)
        self.assertEqual(set(located), set(shifts))
        east = [located[y][0] - shifts[y][1] * PX for y in shifts]
        north = [located[y][1] + shifts[y][0] * PX for y in shifts]
        self.assertLess(np.ptp(east) + np.ptp(north), 0.01)                 # one physical corner
        self.assertLess(np.hypot(east[0] - 1.4, north[0]), 0.7)               # on the wall's corner

    def test_ground_level_features_only(self):
        self.assertTrue(P.ground_level('SPIGOLO RECINZIONE'))
        self.assertTrue(P.ground_level('SPIGOL0 ESTERNO MURETTO A SECCO'))
        self.assertFalse(P.ground_level('SPIGOLO FABBRICATO'))
        self.assertFalse(P.ground_level('SPIGOLO MURO FABBRICATO'))


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

    def test_removal_rule_and_release_class(self):
        self.assertTrue(P.single_removal_rule(['Zona Contenimento - Salento'], ['Positivi']))
        self.assertTrue(P.single_removal_rule([''], ['Piante estirpate 2016']))
        self.assertFalse(P.single_removal_rule(['Zona infetta'], ['Positivi']))
        self.assertEqual(P.release_of(['64', 'CAMP_2021.xlsx'], [], date(2021, 1, 1)), ('campaign-workbook', 'CAMP_2021.xlsx'))
        self.assertEqual(P.release_of(['camp_2020_2022.csv'], [], date(2021, 1, 1)), ('campaign-csv', 'camp_2020_2022.csv'))
        self.assertEqual(P.release_of(['45'], ['Positivi 2016'], date(2016, 4, 1)), ('sit', 'SIT 2016'))


class Consumer(unittest.TestCase):
    def setUp(self):
        from cordon_d.evidence import Source
        from cordon_d.spatial import CoordinateObservation
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        blobs = {}
        for name in ('monitoring', 'chip-2019', 'chip-2022', 'bounds'):
            data = name.encode() * 10
            (self.root / name).write_bytes(data)
            blobs[name] = Source(name, name, sha256(data).hexdigest(), 'official-dataset', 'public')
        self.sources = blobs
        self.observation = CoordinateObservation(('observation', '1'), (770000.0, 4470000.0), (770000.0, 4470000.0),
                                                 'EPSG:32633', (blobs['monitoring'],), ())
        self.rows = [
            {'source': 'campaign-workbook', 'release': 'CAMP_2021.xlsx', 'status': 'measured', 'distance_m': 7.7,
             'imagery_m': 0.9, 'grid_m': 0.003, 'candidates': [{}], 'pre': 2019, 'post': 2022},
            {'source': 'campaign-workbook', 'release': 'CAMP_2021.xlsx', 'status': 'measured', 'distance_m': 12.4,
             'imagery_m': 1.3, 'grid_m': 0.005, 'candidates': [{}, {}], 'pre': 2019, 'post': 2022},
            {'source': 'campaign-workbook', 'release': 'CAMP_2021.xlsx', 'status': 'unmeasured',
             'cause': 'no crown vanished within the radius'},
            {'source': 'campaign-workbook', 'release': 'CAMP_2024.xlsx', 'status': 'out_of_reach'},
            {'source': 'campaign-workbook', 'release': 'CAMP_2024.xlsx', 'status': 'unmeasured', 'cause': 'x'},
        ]
        self.bounds = P.release_bounds(self.rows)

    def tearDown(self):
        self.directory.cleanup()

    def test_release_bound_is_the_largest_measured_error_plus_the_imagery_term(self):
        entry = self.bounds[('campaign-workbook', 'CAMP_2021.xlsx')]
        self.assertEqual((entry['measured'], entry['unmeasured'], entry['out_of_reach']), (2, 1, 0))
        self.assertAlmostEqual(entry['bound_m'], 12.4 + 1.3 + 0.005, places=2)
        self.assertIsNone(self.bounds[('campaign-workbook', 'CAMP_2024.xlsx')]['bound_m'])

    def test_measured_and_unmeasured_positives_reach_the_distance_consumer(self):
        from shapely.geometry import Point
        from cordon_c.spatial import MetricGeometry, distance_test
        from cordon_d.spatial import metric_point
        day = date(2021, 5, 4)
        measured = P.qualify(self.observation, self.rows[0], self.bounds, context='removal-radius', event_date=day,
                             sources=(self.sources['chip-2019'], self.sources['chip-2022']))
        self.assertAlmostEqual(measured.error_m, 8.6, places=2)
        unmeasured = P.qualify(self.observation, self.rows[2], self.bounds, context='removal-radius', event_date=day,
                               sources=(self.sources['bounds'],))
        self.assertAlmostEqual(unmeasured.error_m, 13.7, places=1)
        self.assertIn('n=2', unmeasured.support[0].reading)
        for qualification in (measured, unmeasured):
            point = metric_point(self.observation, context='removal-radius', event_date=day, root=self.root,
                                 qualification=qualification)
            self.assertEqual(point.error_m, qualification.error_m)
        point = metric_point(self.observation, context='removal-radius', event_date=day, root=self.root,
                             qualification=unmeasured)
        for separation, expected in [(3, True), (50, None), (80, False)]:
            other = MetricGeometry(Point(point.geometry.x + separation, point.geometry.y), point.crs, 10)
            self.assertIs(distance_test(point, other, 50, '<=').truth, expected)

    def test_no_bound_and_out_of_reach_are_refused(self):
        with self.assertRaises(MissingInput):
            P.qualify(self.observation, self.rows[4], self.bounds, context='c', event_date=date(2024, 1, 1),
                      sources=(self.sources['bounds'],))
        with self.assertRaises(MissingInput):
            P.qualify(self.observation, self.rows[3], self.bounds, context='c', event_date=date(2024, 1, 1),
                      sources=(self.sources['bounds'],))


if __name__ == '__main__':
    unittest.main()

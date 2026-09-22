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

    def test_no_vanished_crown_is_unmeasured_not_dropped(self):
        before = scene(CROWNS)
        status, detail = P.measure(before, scene(CROWNS, rng_seed=2), CENTRE, (0.0, 0.0))
        self.assertEqual((status, detail['cause']), ('unmeasured', 'no crown vanished within the radius'))

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

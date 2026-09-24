"""The positional qualification of located monitoring observations, through C.

The real-record checks read the ordinary monitoring reader over this checkout's store.
They skip where its releases or the device sources are not held; the contract check
always runs.
"""
from dataclasses import replace
from datetime import date, timedelta
import json
import unittest

import numpy
from pyproj import CRS, Transformer
from shapely.geometry import Point, box

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, adopted_membership, distance_test, ground_distance
from cordon_d.evidence import Source, require_admissible
from cordon_d.store import blob_path, store_root
from cordon_d.spatial import (DEVICE_RECORDS, GROUND_FRAME, REPOSITORY, metric_point, positional_qualification,
                              positional_terms)

STORE = store_root(REPOSITORY)
MONITORING = REPOSITORY / 'corpus/sources/monitoring'
# The evaluation's decision date and SPEC.md's longest reachable backward period today
# (B-CLK-EU-6(1), four years), so the reach starts four years before it.
DECISION = date(2026, 9, 22)
REACH = DECISION.replace(year=DECISION.year - 4)
LIMIT_M = 50  # B's 50 m radius around an infected plant
DEVICE_M = 6.67  # USFS NTDP, NSSDA 95%, Galaxy Tab Active3, single position, light-medium canopy
# The cadastral map's measured local ground error at Giovinazzo (E047): PR #8's record
# corpus/sources/areas/geometry.json at b258378, kind positional-error, source cadastre,
# comuni[comune=E047].error_m, median 12.5 m and maximum 12.5 m over its 6 fixes, each the
# 95th percentile of the errors of the 20 surveyed fixes nearest it.
ZONE_LOCALITY, ZONE_ERROR_M = 'GIOVINAZZO', 12.5
TO_METRIC = Transformer.from_crs('EPSG:4326', GROUND_FRAME, always_xy=True)
TO_DEGREES = Transformer.from_crs(GROUND_FRAME, 'EPSG:4326', always_xy=True)
TOLERANCE_M = 1  # clear of every boundary by more than grid-versus-ellipsoid differences at 50 m


def device_bytes_held():
    records = json.loads((REPOSITORY / DEVICE_RECORDS).read_text())
    return all(blob_path(STORE, r['sha256']).exists() for r in records)


def monitoring_held():
    releases = json.loads((MONITORING / 'campaign/releases.json').read_text())
    return all(blob_path(STORE, r['sha256']).exists() for r in releases if 'sha256' in r)


def lonlat(observation):
    x, y = observation.coordinates
    return (x, y) if observation.crs == 'EPSG:4326' else TO_DEGREES.transform(x, y)


class Contract(unittest.TestCase):
    def test_the_positional_qualification_field_admits_a_qualified_observation(self):
        contracts = json.loads((REPOSITORY / 'regulation/stage-d/contracts.json').read_text())['contracts']
        finding = next(c for c in contracts if c['id'] == 'official-finding')
        test = Source('test', 'x', '0' * 64, 'qualified-observation', 'public')
        require_admissible(finding, [test], field='positional qualification')
        # The finding itself still admits only official records and datasets.
        with self.assertRaisesRegex(ValueError, 'does not establish an instance fact under official-finding'):
            require_admissible(finding, [test])
        with self.assertRaisesRegex(ValueError, 'official-format does not establish'):
            require_admissible(finding, [replace(test, role='official-format')], field='positional qualification')
        with self.assertRaises(ValueError):
            require_admissible(finding, [test], field='no such field')
        replacing = finding['positional_qualification']['replacing_input']
        self.assertEqual(len(replacing['one_of']), 3)
        self.assertTrue(replacing['default'].startswith('none'))


@unittest.skipUnless(device_bytes_held() and monitoring_held(),
                     'the device sources or the monitoring releases are not in this store')
class RealObservations(unittest.TestCase):
    """In-reach located observations as the ordinary reader yields them, in stream order."""

    @classmethod
    def setUpClass(cls):
        from cordon_d.monitoring import distinct_observations, located_observations
        cls.terms = positional_terms(STORE)
        # Every in-reach located observation with its published result, in stream order.
        # Nothing is chosen by a C result.
        cls.located = []
        for group in distinct_observations(MONITORING):
            if group.day is None or group.day < REACH:
                continue
            observation = next(located_observations([group]), None)
            if observation is not None:
                cls.located.append((observation, group.positive is True))
        cls.grid = numpy.array([TO_METRIC.transform(*lonlat(o)) for o, _ in cls.located])

    def qualify(self, observation, context='test'):
        return positional_qualification(observation, context=context, event_date=DECISION, reach_from=REACH,
                                        terms=self.terms)

    def point(self, observation, context='test'):
        return metric_point(observation, context=context, event_date=DECISION, root=STORE,
                            qualification=self.qualify(observation, context))

    def near(self, index, radius_m):
        return numpy.flatnonzero(numpy.hypot(*(self.grid - self.grid[index]).T) < radius_m)

    def test_a_positive_and_a_non_positive_reach_metric_point_with_their_basis(self):
        for positive in (True, False):
            observation = next(o for o, p in self.located if p is positive)
            with self.subTest(positive=positive, occurrence=observation.occurrence):
                qualification = self.qualify(observation)
                point = self.point(observation)
                self.assertEqual(point.crs.to_epsg(), 32633)
                self.assertEqual(qualification.target_crs, GROUND_FRAME)
                self.assertEqual(point.error_m, DEVICE_M)
                self.assertEqual(self.terms.device['value_m'], DEVICE_M)
                basis = ' '.join(s.reading for s in qualification.support)
                for words in ('NSSDA 95%', 'Galaxy Tab Active3', 'light-medium canopy', 'single position',
                              'not measured on these fixes', 'capture mode', 'Galaxy Tab Active5',
                              'Aggiudicazione definitiva', '16/09/2024', 'no award date', 'no delivery date',
                              'true ground position', GROUND_FRAME):
                    self.assertIn(words, basis)
                self.assertNotIn('adastral', basis)
                self.assertEqual({s.role for s in qualification.sources},
                                 {'qualified-observation', 'official-record'})
                changed = replace(qualification, sources=(replace(qualification.sources[0], sha256='0' * 64),
                                                          *qualification.sources[1:]))
                with self.assertRaisesRegex(ValueError, 'Source changed'):
                    metric_point(observation, context='test', event_date=DECISION, root=STORE,
                                 qualification=changed)

    def test_distance_from_a_positive_is_definite_only_clear_of_the_combined_margin(self):
        margin = 2 * DEVICE_M  # 13.34 m: C adds the two fixes' device terms
        for index, (origin, positive) in enumerate(self.located):
            if not positive:
                continue
            cases = {}
            origin_lonlat = lonlat(origin)
            # The case is set by the ellipsoidal ground distance, not by C's grid distance.
            for j in self.near(index, 3 * LIMIT_M):
                other, other_positive = self.located[j]
                if other_positive:
                    continue
                ground = ground_distance(origin_lonlat, lonlat(other))
                case = (True if ground + margin + TOLERANCE_M <= LIMIT_M
                        else False if ground - margin - TOLERANCE_M >= LIMIT_M
                        else None if abs(ground - LIMIT_M) < margin - TOLERANCE_M else 'skip')
                if case != 'skip':
                    cases.setdefault(case, other)
            if len(cases) == 3:
                break
        else:
            self.fail('No in-reach positive has a clear-inside, clear-outside and near-line neighbour')
        a = self.point(origin)
        for expected, other in cases.items():
            with self.subTest(expected=expected, other=other.occurrence):
                b = self.point(other)
                self.assertEqual(a.error_m + b.error_m, margin)
                result = distance_test(a, b, LIMIT_M, '<=')
                self.assertIs(result.truth, expected)
                if expected is None:
                    self.assertEqual(result.needs, frozenset({'distance precision at the legal boundary'}))

    def test_membership_in_a_zone_with_a_stated_ground_error(self):
        # A square 1 km across, drawn around the first in-reach Giovinazzo observation the
        # stream yields, stands for a zone outline drawn from the cadastral map there. It
        # carries that map's local ground error; the point carries the device term.
        index = next(i for i, (o, _) in enumerate(self.located)
                     if any(n.strip().upper() == ZONE_LOCALITY for n in o.localities))
        x, y = self.grid[index]
        zone = MetricGeometry(box(x - 500, y - 500, x + 500, y + 500), CRS.from_user_input(GROUND_FRAME),
                              ZONE_ERROR_M)
        margin = DEVICE_M + ZONE_ERROR_M
        cases = {}
        for j in self.near(index, 800):
            other, _ = self.located[j]
            spot = Point(*self.grid[j])
            edge = zone.geometry.boundary.distance(spot)
            if edge > margin + TOLERANCE_M and zone.geometry.covers(spot):
                cases.setdefault(True, other)
            elif edge > margin + TOLERANCE_M:
                cases.setdefault(False, other)
            elif edge < margin - TOLERANCE_M:
                cases.setdefault(None, other)
        self.assertEqual(set(cases), {True, False, None})
        for expected, other in cases.items():
            with self.subTest(expected=expected, other=other.occurrence):
                result = adopted_membership(self.point(other), zone)
                self.assertIs(result.truth, expected)
                if expected is None:
                    self.assertEqual(result.needs, frozenset({'point/area precision at the adopted boundary'}))

    def test_only_an_observation_without_a_usable_location_is_refused(self):
        # No printed locality, or two, does not matter: the fix carries the device term.
        unprinted = next(o for o, _ in self.located if not o.localities)
        for observation in (unprinted, replace(unprinted, localities=('BARI', 'MODUGNO'))):
            self.assertEqual(self.point(observation).error_m, DEVICE_M)
        with self.assertRaisesRegex(MissingInput, 'finite published coordinates'):
            self.qualify(replace(unprinted, coordinates=None))
        with self.assertRaisesRegex(MissingInput, 'finite published coordinates'):
            self.qualify(replace(unprinted, coordinates=(float('nan'), unprinted.coordinates[1])))
        with self.assertRaisesRegex(MissingInput, 'finite published coordinates'):
            self.qualify(replace(unprinted, crs=None))
        with self.assertRaisesRegex(ValueError, 'outside the reach'):
            self.qualify(replace(unprinted, observed_on=REACH - timedelta(days=1)))
        with self.assertRaisesRegex(ValueError, 'outside the reach'):
            self.qualify(replace(unprinted, observed_on=None))

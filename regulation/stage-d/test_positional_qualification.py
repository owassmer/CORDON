"""The positional qualification of located monitoring observations, through C.

The real-record checks read the ordinary monitoring reader over this checkout's store and
PR #8's cadastral error record. They skip where those are not held; the contract check
always runs.
"""
from dataclasses import replace
from datetime import date, timedelta
import json
import unittest

import numpy
from pyproj import CRS, Transformer
import shapely
from shapely.geometry import Polygon

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, adopted_membership, distance_test, ground_distance
from cordon_d.evidence import Source, require_admissible
from cordon_d.store import blob_path, store_root
from cordon_d.spatial import (AREA_RECORDS, CADASTRAL_FRAME, DEVICE_RECORDS, REPOSITORY, locality_key,
                              metric_point, positional_qualification, positional_terms)

STORE = store_root(REPOSITORY)
MONITORING = REPOSITORY / 'corpus/sources/monitoring'
# The evaluation's decision date and SPEC.md's longest reachable backward period today
# (B-CLK-EU-6(1), four years), so the reach starts four years before it.
DECISION = date(2026, 9, 22)
REACH = DECISION.replace(year=DECISION.year - 4)
LIMIT_M = 50  # B's 50 m radius around an infected plant
TO_METRIC = Transformer.from_crs('EPSG:4326', CADASTRAL_FRAME, always_xy=True)
TO_DEGREES = Transformer.from_crs(CADASTRAL_FRAME, 'EPSG:4326', always_xy=True)


def device_bytes_held():
    records = json.loads((REPOSITORY / DEVICE_RECORDS).read_text())
    return all(blob_path(STORE, r['sha256']).exists() for r in records)


def monitoring_held():
    releases = json.loads((MONITORING / 'campaign/releases.json').read_text())
    return all(blob_path(STORE, r['sha256']).exists() for r in releases if 'sha256' in r)


def ground_held():
    return (REPOSITORY / AREA_RECORDS).exists()


def lonlat(observation):
    x, y = observation.coordinates
    return (x, y) if observation.crs == 'EPSG:4326' else TO_DEGREES.transform(x, y)


def esri_polygon(geometry):
    """An Esri polygon: clockwise rings are shells, anticlockwise rings holes of the shell before."""
    shells = []
    for ring in geometry['rings']:
        if len(ring) < 4:
            continue
        if shapely.LinearRing(ring).is_ccw and shells:
            shells[-1][1].append(ring)
        else:
            shells.append((ring, []))
    return shapely.union_all([Polygon(shell, holes).buffer(0) for shell, holes in shells])


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
        ground = cls.terms.ground or {}
        device = cls.terms.device['value_m']
        # Localities whose two-fix margin leaves room for a definite answer at 50 m.
        roomy = {k for k, e in ground.items() if 2 * (device + e['error_m']['max']) < LIMIT_M - 2}
        # The first observation of each kind the stream yields, and every observation of a
        # roomy locality with its published result. Nothing is chosen by a C result.
        cls.first, cls.roomy = {}, []
        for group in distinct_observations(MONITORING):
            if group.day is None or group.day < REACH:
                continue
            observation = next(located_observations([group]), None)
            if observation is None:
                continue
            keys = {locality_key(n) for n in observation.localities}
            key = next(iter(keys)) if len(keys) == 1 else None
            positive = group.positive is True
            if key in ground:
                cls.first.setdefault(('held', positive), observation)
            elif key and ground:
                cls.first.setdefault('missing', observation)
            elif not keys:
                cls.first.setdefault('unprinted', observation)
            if key in roomy:
                cls.roomy.append((observation, positive))

    def qualify(self, observation, context='test'):
        return positional_qualification(observation, context=context, event_date=DECISION, reach_from=REACH,
                                        terms=self.terms)

    def point(self, observation, context='test'):
        return metric_point(observation, context=context, event_date=DECISION, root=STORE,
                            qualification=self.qualify(observation, context))

    def stated_error(self, observation):
        """What the record states for this observation, read here without the producer."""
        entry = self.terms.ground[locality_key(observation.localities[0])]
        return round(self.terms.device['value_m'] + entry['error_m']['max'], 2)

    def require_ground(self):
        if self.terms.ground is None:
            self.skipTest(f'{AREA_RECORDS} (PR #8) is not in this tree')

    def test_a_positive_and_a_non_positive_reach_metric_point_with_their_basis(self):
        self.require_ground()
        for positive in (True, False):
            observation = self.first[('held', positive)]
            with self.subTest(positive=positive, occurrence=observation.occurrence):
                qualification = self.qualify(observation)
                point = self.point(observation)
                self.assertEqual(point.crs.to_epsg(), 32633)
                self.assertEqual(point.error_m, qualification.error_m)
                self.assertEqual(point.error_m, self.stated_error(observation))
                basis = ' '.join(s.reading for s in qualification.support)
                for words in ('NSSDA 95%', 'Galaxy Tab Active3', 'light-medium canopy', 'single position',
                              'not measured on these fixes', 'capture mode', 'Galaxy Tab Active5',
                              'Aggiudicazione definitiva', 'no award date', 'no delivery date',
                              'Cadastral map ground error', 'the 20th lies', CADASTRAL_FRAME):
                    self.assertIn(words, basis)
                self.assertEqual({s.role for s in qualification.sources},
                                 {'qualified-observation', 'official-record'})
                changed = replace(qualification, sources=(replace(qualification.sources[0], sha256='0' * 64),
                                                          *qualification.sources[1:]))
                with self.assertRaisesRegex(ValueError, 'Source changed'):
                    metric_point(observation, context='test', event_date=DECISION, root=STORE,
                                 qualification=changed)

    def test_distance_from_a_positive_is_definite_only_clear_of_the_combined_margin(self):
        self.require_ground()
        placed = [(o, positive, lonlat(o), self.stated_error(o)) for o, positive in self.roomy]
        grid = numpy.array([TO_METRIC.transform(*p[2]) for p in placed])
        for index, (origin, positive, origin_lonlat, origin_error) in enumerate(placed):
            if not positive:
                continue
            cases = {}
            # Only neighbours a grid distance can place near the line; the case is set by the
            # ellipsoidal ground distance, not by C's planar distance.
            near = numpy.flatnonzero(numpy.hypot(*(grid - grid[index]).T) < 3 * LIMIT_M)
            for other, other_positive, other_lonlat, other_error in (placed[j] for j in near):
                if other_positive:
                    continue
                ground = ground_distance(origin_lonlat, other_lonlat)
                margin = origin_error + other_error
                case = (True if ground + margin + 1 <= LIMIT_M else False if ground - margin - 1 >= LIMIT_M
                        else None if abs(ground - LIMIT_M) < margin - 1 else 'skip')
                if case != 'skip':
                    cases.setdefault(case, other)
            if len(cases) == 3:
                break
        else:
            self.fail('No in-reach positive has a clear-inside, clear-outside and near-line neighbour')
        a = self.point(origin)
        for expected, other in cases.items():
            with self.subTest(expected=expected, other=other.occurrence):
                result = distance_test(a, self.point(other), LIMIT_M, '<=')
                self.assertIs(result.truth, expected)
                if expected is None:
                    self.assertEqual(result.needs, frozenset({'distance precision at the legal boundary'}))

    def test_membership_in_a_cadastral_built_zone(self):
        self.require_ground()
        observation, _ = self.roomy[0]
        entry = self.terms.ground[locality_key(observation.localities[0])]
        records = json.loads((REPOSITORY / AREA_RECORDS).read_text())
        sheets = [r for r in records if r.get('kind') == 'cadastre-fogli'
                  and r['selection'].get('comune') == entry['comune']]
        if not sheets or not all(blob_path(STORE, r['sha256']).exists() for r in sheets):
            self.skipTest(f"the cadastral sheets of {entry['name']} are not in this store")
        features = [f for r in sheets for f in json.loads(blob_path(STORE, r['sha256']).read_bytes())['features']]
        # The whole comune as its cadastral sheets draw it: zero error in the cadastral frame.
        zone = MetricGeometry(shapely.union_all([esri_polygon(f['geometry']) for f in features]),
                              CRS.from_user_input(CADASTRAL_FRAME), 0.0)
        cases = {}
        for other, _ in self.roomy:
            if other.localities[0] != observation.localities[0]:
                continue
            x, y = TO_METRIC.transform(*lonlat(other))
            edge = zone.geometry.boundary.distance(shapely.Point(x, y))
            error = self.stated_error(other)
            if edge > error + 1 and zone.geometry.covers(shapely.Point(x, y)):
                cases.setdefault(True, other)
            elif edge < error - 1:
                cases.setdefault(None, other)
            if len(cases) == 2:
                break
        self.assertEqual(set(cases), {True, None})
        for expected, other in cases.items():
            with self.subTest(expected=expected, other=other.occurrence):
                result = adopted_membership(self.point(other), zone)
                self.assertIs(result.truth, expected)
                if expected is None:
                    self.assertEqual(result.needs, frozenset({'point/area precision at the adopted boundary'}))

    def test_a_locality_the_record_lacks_is_refused_by_name(self):
        self.require_ground()
        observation = self.first['missing']
        with self.assertRaisesRegex(MissingInput, f'locality {observation.localities[0]}: .* does not measure it'):
            self.qualify(observation)

    def test_no_record_no_locality_and_out_of_reach_refuse(self):
        unprinted = self.first['unprinted']
        with self.assertRaisesRegex(MissingInput, 'print no COMUNE'):
            self.qualify(unprinted)
        printed = replace(unprinted, localities=('BARI',))
        with self.assertRaisesRegex(MissingInput, 'cadastral map ground error record'):
            positional_qualification(printed, context='test', event_date=DECISION, reach_from=REACH,
                                     terms=replace(self.terms, ground=None))
        with self.assertRaisesRegex(MissingInput, 'one agreed locality'):
            self.qualify(replace(unprinted, localities=('BARI', 'MODUGNO')))
        with self.assertRaisesRegex(ValueError, 'outside the reach'):
            self.qualify(replace(printed, observed_on=REACH - timedelta(days=1)))

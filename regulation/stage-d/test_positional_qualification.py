"""The positional qualification of located monitoring observations, through C.

The real-record checks read the ordinary monitoring reader over this checkout's store.
They skip where its releases or the device sources are not held; the contract check
always runs.
"""
from dataclasses import replace
from datetime import date
from decimal import ROUND_CEILING, Decimal
import inspect
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

import numpy
from pyproj import CRS, Geod, Proj, Transformer
from shapely.geometry import Point, box

from cordon_c.core import MissingInput
from cordon_c.spatial import (MetricGeometry, adopted_membership, distance_test, ground_distance,
                              projection_distance_error)
import cordon_d.evidence
from cordon_d.evidence import Source, file_digest, require_admissible
from cordon_d.store import blob_path, store_root
from cordon_d.spatial import (DEVICE_RECORDS, GROUND_FRAME, REPOSITORY, longest_point_distance, metric_point,
                              point_consumer_widths, positional_qualification, positional_terms,
                              transverse_mercator_scale_bounds)

STORE = store_root(REPOSITORY)
MONITORING = REPOSITORY / 'corpus/sources/monitoring'
# The evaluation's decision date and SPEC.md's longest reachable backward period today
# (B-CLK-EU-6(1), four years), so the reach starts four years before it.
DECISION = date(2026, 9, 22)
REACH = DECISION.replace(year=DECISION.year - 4)
LIMIT_M = 50  # B's 50 m radius around an infected plant
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
    def test_the_location_of_a_plant_population_member_carries_the_positional_qualification(self):
        contracts = {c['id']: c for c in json.loads(
            (REPOSITORY / 'regulation/stage-d/contracts.json').read_text())['contracts']}
        population, finding = contracts['plant-population'], contracts['official-finding']
        qualification = population['positional_qualification']
        self.assertIn(qualification['field'], population['fields'])
        self.assertIn("the plant's location", qualification['stated'])
        records = json.loads((REPOSITORY / DEVICE_RECORDS).read_text())
        for record in records:
            source = Source(record['id'], 'x', record['sha256'], record['role'], record['access'])
            require_admissible(population, [source])
        with self.assertRaisesRegex(ValueError, 'official-format does not establish'):
            require_admissible(population, [replace(source, role='official-format')])
        # The finding admits no device test, and carries no positional field.
        with self.assertRaisesRegex(ValueError, 'does not establish an instance fact under official-finding'):
            require_admissible(finding, [replace(source, role='qualified-observation')])
        self.assertNotIn('positional_qualification', finding)
        replacing = qualification['replacing_input']
        self.assertEqual(len(replacing['one_of']), 3)
        self.assertTrue(replacing['default'].startswith('none'))

    def test_the_distortion_length_is_the_longest_width_a_plant_population_consumer_measures(self):
        contracts = json.loads((REPOSITORY / 'regulation/stage-d/additional-input-contracts.json').read_text())
        rows = [r for key in ('callables', 'reference_bindings') for r in contracts[key]]
        bound = {r['consumer'] for r in rows if 'plant-population' in r['contracts']}
        ledger = json.loads((REPOSITORY / 'regulation/stage-b/clocks-and-parameters.json').read_text())
        parameters = {p['parameter_id']: p for p in ledger['parameters']}
        metres = {i: float(p['value']) * (1000 if p['unit'] == 'km' else 1)
                  for i, p in parameters.items() if p['unit'] in {'m', 'km'}}
        widths = point_consumer_widths()
        self.assertLessEqual(set(widths), bound)
        # Every bound C consumer that reads a B distance in its own source is enumerated, and no
        # distance it names is longer than the length.
        import importlib
        longest, consumer, identities = longest_point_distance()
        for name in bound:
            module, _, function = name.rpartition('.')
            source = inspect.getsource(getattr(importlib.import_module('cordon_c.' + module), function))
            named = [metres[i] for i in re.findall(r'"(B-PAR-[^"]+)"', source) if i in metres]
            if 'metres(' in source:
                self.assertIn(name, widths)
            self.assertTrue(all(value <= longest for value in named))
        # Today that is the PNI 2026 1 km band, measured from the plant's point.
        self.assertEqual((consumer, identities), ('bindings.pni_geography_facts', ('B-PAR-PNI2026-pest-free-band-1km',)))
        self.assertEqual(longest, 1000.0)
        self.assertEqual(widths['populations.containment_outer'][0], 450.0)  # the band ends at inner + width
        # A longer consumer bound to plant-population lengthens it: the enumeration can fail.
        island = {'consumer': 'bindings.island_distance_facts', 'contracts': ['plant-population']}
        self.assertEqual(max(w for w, _ in point_consumer_widths(consumers=[*rows, island]).values()), 5000.0)
        # A width read through an expression D cannot enumerate refuses rather than being missed.
        survey = {'consumer': 'bindings.reduced_buffer_first_year_facts', 'contracts': ['plant-population']}
        with self.assertRaisesRegex(ValueError, 'cannot enumerate'):
            point_consumer_widths(consumers=[survey])

    def test_a_source_is_hashed_once_per_file_state(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'source').write_bytes(b'first')
            source = Source('s', 'source', file_digest(root / 'source'), 'official-dataset', 'public')
            with mock.patch.object(cordon_d.evidence, 'file_digest', wraps=file_digest) as digest:
                source.verify(root)
                source.verify(root)
                self.assertEqual(digest.call_count, 1)
                # Changed bytes change the file's size or modification time, so they are read again and refused.
                (root / 'source').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'Source changed'):
                    source.verify(root)
                self.assertEqual(digest.call_count, 2)

    def test_the_scale_bound_encloses_proj_over_the_widened_extent(self):
        # PROJ's own point scale on a grid is a check here, never the bound.
        frame = CRS.from_user_input(GROUND_FRAME)
        extent = (14.9, 18.6, 39.7, 42.3)
        low, high = transverse_mercator_scale_bounds(frame, extent, 1000)
        self.assertEqual(low, 0.9996)
        # The widened box: 1 km beyond each edge, as the bound widens it.
        geod = Geod(ellps='WGS84')
        west, east = geod.fwd(14.9, 42.3, 270, 1000)[0], geod.fwd(18.6, 42.3, 90, 1000)[0]
        south, north = geod.fwd(14.9, 39.7, 180, 1000)[1], geod.fwd(14.9, 42.3, 0, 1000)[1]
        lons, lats = numpy.meshgrid(numpy.linspace(west, east, 40), numpy.linspace(south, north, 40))
        scale = Proj(frame).get_factors(lons.ravel(), lats.ravel()).meridional_scale
        self.assertGreaterEqual(scale.min(), low)
        self.assertLessEqual(scale.max(), high + 1e-9)
        corner = Proj(frame).get_factors(east, south).meridional_scale
        self.assertLess(abs(corner - high), 1e-6)
        # Beyond the widened box the bound no longer holds.
        self.assertGreater(Proj(frame).get_factors(east + 0.05, south).meridional_scale, high)
        with self.assertRaises(ValueError):
            transverse_mercator_scale_bounds(CRS.from_user_input('EPSG:3035'), extent, 1000)


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
        cls.localities = []  # every COMUNE the observation's publications print, for picking cases
        for group in distinct_observations(MONITORING):
            if group.day is None or group.day < REACH:
                continue
            observation = next(located_observations([group]), None)
            if observation is not None:
                cls.located.append((observation, group.positive is True))
                cls.localities.append({n.strip().upper() for n in group.values('COMUNE')})
        cls.grid = numpy.array([TO_METRIC.transform(*lonlat(o)) for o, _ in cls.located])

    def qualify(self, observation, context='test'):
        return positional_qualification(observation, context=context, event_date=DECISION, terms=self.terms)

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
                self.assertEqual(point.error_m, self.terms.error_m)
                basis = ' '.join(s.reading for s in qualification.support)
                for words in ('NSSDA 95%', self.terms.device['selector'], 'not measured on these fixes',
                              'capture mode', 'Galaxy Tab Active5', 'Aggiudicazione definitiva', '16/09/2024',
                              'no award date', 'no delivery date', 'true ground position', GROUND_FRAME,
                              'Grid distortion', 'projection_distance_error', 'pni_geography_facts',
                              *self.terms.longest_widths,
                              "D's reading", "the plant's recorded position"):
                    self.assertIn(words, basis)
                self.assertNotIn('adastral', basis)
                self.assertNotIn('total', {s.selector for s in qualification.support})
                self.assertEqual({s.role for s in qualification.sources},
                                 {'qualified-observation', 'official-record', 'official-dataset'})
                changed = replace(qualification, sources=(replace(qualification.sources[0], sha256='0' * 64),
                                                          *qualification.sources[1:]))
                with self.assertRaisesRegex(ValueError, 'Source changed'):
                    metric_point(observation, context='test', event_date=DECISION, root=STORE,
                                 qualification=changed)

    def test_error_m_is_the_device_term_plus_the_grid_distortion_over_the_longest_distance(self):
        self.assertEqual(self.terms.longest_m, longest_point_distance()[0])
        distortion = projection_distance_error(self.terms.longest_m, self.terms.scale)
        self.assertEqual(self.terms.distortion_m, distortion)
        self.assertEqual(self.terms.error_m, float((Decimal(str(self.terms.device['value_m'])) + Decimal(distortion))
                                                   .quantize(Decimal('0.01'), ROUND_CEILING)))
        self.assertGreater(self.terms.error_m, self.terms.device['value_m'])
        # Every in-reach located observation lies inside the extent the scale bound covers.
        west, east, south, north = self.terms.extent
        lon, lat = TO_DEGREES.transform(*self.grid.T)
        self.assertTrue(((west <= lon) & (lon <= east) & (south <= lat) & (lat <= north)).all())

    def test_distance_from_a_positive_is_definite_only_clear_of_the_combined_margin(self):
        margin = 2 * self.terms.error_m  # C adds the two fixes' errors
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
        index = next(i for i, names in enumerate(self.localities) if ZONE_LOCALITY in names)
        x, y = self.grid[index]
        zone = MetricGeometry(box(x - 500, y - 500, x + 500, y + 500), CRS.from_user_input(GROUND_FRAME),
                              ZONE_ERROR_M)
        margin = self.terms.error_m + ZONE_ERROR_M
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
        # No printed locality, or two, does not matter: the producer never reads it.
        unprinted = next(o for (o, _), names in zip(self.located, self.localities) if not names)
        several = next(o for (o, _), names in zip(self.located, self.localities) if len(names) > 1)
        for observation in (unprinted, several):
            self.assertEqual(self.point(observation).error_m, self.terms.error_m)
        with self.assertRaisesRegex(MissingInput, 'finite published coordinates'):
            self.qualify(replace(unprinted, coordinates=None))
        with self.assertRaisesRegex(MissingInput, 'finite published coordinates'):
            self.qualify(replace(unprinted, coordinates=(float('nan'), unprinted.coordinates[1])))
        with self.assertRaisesRegex(MissingInput, 'finite published coordinates'):
            self.qualify(replace(unprinted, crs=None))
        # The pair CAMP_2024 prints for observation 10201346 lies outside Puglia's extent.
        with self.assertRaisesRegex(MissingInput, 'scale bound covering this location'):
            self.qualify(replace(unprinted, crs='EPSG:4326', coordinates=(-64.64284225, 69.26039604)))

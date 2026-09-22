"""Row 3: adopted geometry supplied to C, built from each act's operative rule first.

The rule's zone is built from its origin at B's width; only a zone without a rule is built
from the annex's listed units; C receives `MetricGeometry` with the measured bound.
"""
from datetime import date
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pyproj import CRS
from shapely.geometry import Point, box

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, adopted_membership, partial_parcel
from cordon_d.area_geometry import (AdoptedGeography, Sources, Unplaced, Zone, adopted_geography, boundary_distances,
                                    dispositivo,
                                    inward_band, named_plants, outward_band, plant_roles, reach_start, read_rules,
                                    _inspire_zoning)
from cordon_d.areas import versions
from cordon_d.administrative import records
from cordon_d.store import store_root

ROOT = Path(__file__).resolve().parents[2]
UTM = CRS.from_user_input('EPSG:32633')
REGIONAL = ROOT / 'regulation/jurisdiction/regional'


def held(kind) -> bool:
    found = records(ROOT, kind)
    return bool(found) and all((store_root(ROOT) / 'blobs/sha256' / r['sha256'][:2] / r['sha256']).exists()
                               for r in found[:3])


class Version:
    def __init__(self, identity='REG:v1'):
        self.provision_version_id = identity


class OperativeRules(unittest.TestCase):
    """The dispositivo's own words decide the rule; B supplies the width."""

    sources = Sources(ROOT)

    def rules(self, path, identity='REG:v1'):
        return read_rules(self.sources, Version(identity), dispositivo((REGIONAL / path).read_text()))

    def test_named_whole_comuni_and_the_part_the_annex_lists(self):
        rules = self.rules('bulk/DET-127-2022-FITO-70eff34bc0bf.txt')
        self.assertEqual(rules.whole, ('Polignano', 'Monopoli', 'Alberobello'))
        self.assertEqual((rules.part, rules.whole_role), ('Castellana Grotte', 'infected'))
        self.assertEqual(rules.annex_iii, 'containment')
        self.assertEqual(rules.buffer[:2], (5000.0, 'B-PAR-EU-4(2)(b)-containment-buffer-5km'))

    def test_a_containment_band_is_inward_and_the_buffer_outward(self):
        rules = self.rules('bulk/DET-158-2024-FITO-.txt')
        self.assertEqual(rules.inward[:2], (2000.0, 'B-PAR-EU-15(2)(a)-v2-inward-band-2km'))
        self.assertEqual(rules.buffer[:2], (5000.0, 'B-PAR-EU-4(2)(b)-containment-buffer-5km'))
        self.assertFalse(rules.whole)

    def test_the_former_zone_band_and_the_named_containment_comuni(self):
        rules = self.rules('bulk/DET-18-2024-FITO-.txt')
        self.assertEqual(rules.whole_role, 'containment')
        self.assertEqual(rules.part, 'Putignano')
        self.assertEqual(rules.former[0], 5000.0)

    def test_an_act_without_a_buffer_width_states_none(self):
        rules = self.rules('AREA-DDS-82-2026-ex-Salento.txt')
        self.assertIsNone(rules.buffer)
        self.assertEqual(rules.inward[0], 2000.0)

    def test_a_buffer_width_written_before_its_noun(self):
        self.assertEqual(self.rules('bulk/DET-45-2024-FITO-.txt').buffer[0], 2500.0)

    def test_a_radius_around_infected_plants_is_b_s_restated_width(self):
        rules = self.rules('bulk/DET-12-2024-FITO-.txt', 'REG-PUGLIA-U181-DIR-2024-00012:area-state-transition:v1')
        self.assertEqual(rules.radius[:2], (50.0, 'B-PAR-EU-4(2)-sub1-infected-zone-50m'))
        self.assertEqual(rules.buffer[0], 2500.0)

    def test_a_radius_about_spared_host_plants_is_not_a_zone(self):
        rules = self.rules('bulk/DET-18-2024-FITO-.txt', 'REG-PUGLIA-U181-DIR-2024-00018:area-state-transition:v1')
        self.assertIsNone(rules.radius)


class AnnexIII(unittest.TestCase):
    def test_the_version_in_force_names_its_units(self):
        sources = Sources(ROOT)
        before = sources.annex_iii(date(2024, 3, 14))
        after = sources.annex_iii(date(2024, 6, 5))
        self.assertIn(('province', 'Lecce'), before)
        self.assertIn(('comune', 'Locorotondo', 'Bari'), before)
        self.assertNotIn(('comune', 'Putignano', 'Bari'), before)
        self.assertEqual(len([u for u in before if u[0] == 'comune' and u[2] == 'Taranto']), 22)
        self.assertIn(('comune', 'Putignano', 'Bari'), after)
        self.assertIn(('comune', 'Fasano', 'Taranto'), after)


class Bands(unittest.TestCase):
    land = box(-10_000, -10_000, 10_000, 10_000)

    def test_an_outward_band_stops_at_the_coast(self):
        zone = box(-10_000, -1_000, 0, 1_000)
        band = outward_band(zone, 500, self.land)
        self.assertTrue(band.contains(Point(400, 0)))
        self.assertFalse(band.contains(Point(-100, 0)))
        self.assertFalse(band.intersects(box(10_000.5, -1, 10_001, 1)))

    def test_an_inward_band_runs_along_the_land_border_only(self):
        zone = box(-10_000, -10_000, 0, 10_000)          # its west edge is the sea
        band = inward_band(zone, 2_000, self.land)
        self.assertTrue(band.contains(Point(-1_500, 0)))
        self.assertFalse(band.contains(Point(-2_500, 0)))
        self.assertFalse(band.contains(Point(-9_000, 0)))


class PositionalError(unittest.TestCase):
    def test_directed_distances_see_a_shifted_edge_one_way(self):
        official, other = box(0, 0, 100, 100), box(0, 0, 103, 100)
        self.assertAlmostEqual(boundary_distances(official, other).max(), 3)
        self.assertAlmostEqual(boundary_distances(other, official).max(), 3)
        self.assertAlmostEqual(float(sorted(boundary_distances(official, other))[len(boundary_distances(official, other)) // 2]), 0)


class MetricGeometryForC(unittest.TestCase):
    def geography(self, error=2.0, unplaced=()):
        zones = (Zone('infected', ('ZONA INFETTA',), box(0, 0, 10, 10), 'annex', ('istat-boundaries',),
                      None, unplaced),
                 Zone('buffer', ('ZONA CUSCINETTO',), box(0, 0, 30, 30).difference(box(0, 0, 10, 10)),
                      'rule', ('istat-boundaries',)))
        return AdoptedGeography('REG:v1', 'REG', date(2024, 1, 1), None, zones, error)

    def test_a_complete_construction_reaches_c_with_its_bound(self):
        area = self.geography().metric()
        self.assertEqual((area.error_m, area.geometry.area), (2.0, 900))
        self.assertTrue(adopted_membership(MetricGeometry(Point(5, 5), UTM, 1), area).truth)
        self.assertIsNone(adopted_membership(MetricGeometry(Point(29, 5), UTM, 1), area).truth)
        self.assertFalse(partial_parcel(MetricGeometry(box(40, 40, 50, 50), UTM, 1), area).truth)

    def test_a_partly_included_unit_inside_the_area_changes_nothing(self):
        inside = Unplaced('infected', 'p1', 'foglio 16', 'legend', box(8, 8, 12, 12))
        self.assertIsInstance(self.geography(unplaced=(inside,)).metric(), MetricGeometry)

    def test_a_partly_included_unit_reaching_outside_is_quoted(self):
        outside = Unplaced('focus', 'p9', 'Noci foglio 59', 'IL SIMBOLO * ...: FOGLIO: 59', box(25, 25, 40, 40))
        with self.assertRaisesRegex(MissingInput, 'Noci foglio 59.*FOGLIO: 59'):
            self.geography(unplaced=(outside,)).metric()

    def test_no_bound_no_metric_geometry(self):
        with self.assertRaisesRegex(MissingInput, 'positional error'):
            self.geography(error=None).metric()

    def test_the_shared_boundary_is_the_buffer_s_inner_edge(self):
        self.assertAlmostEqual(self.geography().shared_boundary.length, 20)


class InspireSheets(unittest.TestCase):
    def test_the_reference_carries_sheet_annex_and_development(self):
        body = b'''<?xml version='1.0' encoding="UTF-8" ?>
<wfs:FeatureCollection xmlns:CP="http://mapserver.gis.umn.edu/mapserver" xmlns:gml="http://www.opengis.net/gml/3.2"
 xmlns:wfs="http://www.opengis.net/wfs/2.0"><wfs:member><CP:CadastralZoning><CP:msGeometry>
<gml:Polygon><gml:exterior><gml:LinearRing><gml:posList>40.584 17.106 40.584 17.107 40.585 17.107 40.585 17.106
40.584 17.106</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon></CP:msGeometry>
<CP:NATIONALCADASTRALZONINGREFERENCE>F027_0115C0</CP:NATIONALCADASTRALZONINGREFERENCE></CP:CadastralZoning>
</wfs:member></wfs:FeatureCollection>'''
        (attributes, geometry), = _inspire_zoning(body, {'crs': 'EPSG:6706', 'selection': {'comune': 'F027'}})
        self.assertEqual((attributes['FOGLIO'], attributes['ALLEGATO'], attributes['SVILUPPO']), ('115', 'C', '0'))
        self.assertAlmostEqual(geometry.area, 9380, delta=300)
        self.assertTrue(670_000 < geometry.centroid.x < 690_000)


class ReachAndPopulation(unittest.TestCase):
    def test_reach_is_bs_longest_backward_clock(self):
        clocks = json.loads((ROOT / 'regulation/stage-b/clocks-and-parameters.json').read_text())['clocks']
        years = int(next(c for c in clocks if c['clock_id'] == 'B-CLK-EU-6(1)-four-negative-years')['magnitude'])
        self.assertEqual(reach_start(ROOT, date(2026, 9, 22)), date(2026 - years, 9, 22))

    def test_versions_without_the_membership_predicate_are_not_consumed(self):
        consumed = {v.provision_version_id: v.consumed for v in versions(ROOT)}
        for identity in ('REG-PUGLIA-U181-DIR-2021-00069:pauca-area-update:v1',
                         'REG-PUGLIA-U181-DIR-2024-00148:area-state-transition:unresolved-v1',
                         'REG-PUGLIA-U181-DIR-2025-00045:area-act-before-gis:v1'):
            self.assertFalse(consumed[identity])
        self.assertEqual(sum(consumed.values()), 26)

    @unittest.skipUnless(held('cadastre-fogli') and held('istat-boundaries'), 'the geometry sources are not in this store')
    def test_every_consumed_version_is_supplied_as_its_act_defines_it(self):
        supplied = {g.provision_version_id: g for g in adopted_geography(ROOT, decision=date(2026, 9, 22))}
        self.assertEqual(len(supplied), 26)
        for identity, geography in supplied.items():
            with self.subTest(version=identity):
                roles = {z.role: z for z in geography.zones}
                if 'plants' in roles['infected'].sources:
                    with self.assertRaises(MissingInput):       # no plants supplied here
                        geography.metric()
                else:
                    self.assertIsInstance(geography.metric(), MetricGeometry)
                self.assertIn('buffer', roles)
        ex_salento = supplied['REG-PUGLIA-U181-DIR-2026-00082:area-state-transition:v1']
        self.assertEqual({z.role for z in ex_salento.zones}, {'infected', 'containment', 'focus', 'buffer'})
        self.assertIn('FOCOLAI', ' '.join(ex_salento.zone('focus').words))

    @unittest.skipUnless(held('cadastre-fogli'), 'the geometry sources are not in this store')
    def test_the_named_plants_are_the_subspecies_in_the_listed_units_up_to_the_act(self):
        version = next(v for v in versions(ROOT)
                       if v.provision_version_id == 'REG-PUGLIA-U181-DIR-2025-00059:area-state-transition:v1')
        sources = Sources(ROOT)
        self.assertEqual(plant_roles(sources, version), ('infected',))
        sheet = sources.sheets[('F220', '', '61')][0][1]
        inside = sheet.representative_point()
        found = named_plants(sources, version, [
            (date(2025, 4, 1), ('PAUCA',), inside.x, inside.y),
            (date(2025, 5, 1), ('PAUCA',), inside.x + 1, inside.y),       # after the act
            (date(2025, 4, 1), ('MULTIPLEX',), inside.x + 2, inside.y),   # another subspecies
            (date(2025, 4, 1), ('PAUCA',), 0.0, 0.0)])                    # outside the listed units
        self.assertEqual(found, {'infected': ((inside.x, inside.y),)})


if __name__ == '__main__':
    unittest.main()

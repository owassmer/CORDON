"""Row 3: adopted geometry supplied to C, built from each act's operative rule first.

The rule's zone is built from its origin at B's width; only a zone without a rule is built
from the annex's listed units; C receives `MetricGeometry` with the measured bound.

Each test reads bounded real inputs: one version, and the sheets and parcels of the comuni it
names (`Sources(root, comuni=...)`). Whole-version construction and its checks are run
version by version outside the suite.
"""
from datetime import date
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy
from pyproj import CRS
import shapely
from shapely.geometry import Point, box

from cordon_c.core import MissingInput
from cordon_c.spatial import MetricGeometry, adopted_membership, partial_parcel
from cordon_d import area_error
from cordon_d.area_geometry import (AdoptedGeography, ErrorPart, Observation, Sources, Unplaced, Zone,
                                    boundary_distances, buffer_extent, construct, dispositivo,
                                    inward_band, named_plants, outward_band, plant_roles, reach_start, read_rules,
                                    _Builder, _drawn, _inspire_zoning, _source_errors)
from cordon_d.areas import Sheet, versions
from cordon_d.administrative import AdministrativeUnits, records
from cordon_d.store import store_root

ROOT = Path(__file__).resolve().parents[2]
UTM = CRS.from_user_input('EPSG:32633')
REGIONAL = ROOT / 'regulation/jurisdiction/regional'


def held(kind) -> bool:
    found = records(ROOT, kind)
    return bool(found) and all((store_root(ROOT) / 'blobs/sha256' / r['sha256'][:2] / r['sha256']).exists()
                               for r in found[:3])


def version_of(identity):
    return next(v for v in versions(ROOT) if v.provision_version_id == identity)


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

    def test_an_inward_band_runs_along_the_border_with_the_adjacent_zone_only(self):
        zone = box(-10_000, -10_000, 0, 10_000)          # its west edge is the sea
        band = inward_band(zone, 2_000, self.land.difference(zone))
        self.assertTrue(band.contains(Point(-1_500, 0)))
        self.assertFalse(band.contains(Point(-2_500, 0)))
        self.assertFalse(band.contains(Point(-9_000, 0)))
        # Article 15(2)(a): from the border with the buffer zone, not from every land border.
        buffer = box(0, 0, 5_000, 10_000)
        band = inward_band(zone, 2_000, buffer)
        self.assertTrue(band.contains(Point(-1_500, 5_000)))
        self.assertFalse(band.contains(Point(-1_500, -5_000)))


class PositionalError(unittest.TestCase):
    def test_directed_distances_see_a_shifted_edge_one_way(self):
        official, other = box(0, 0, 100, 100), box(0, 0, 103, 100)
        self.assertAlmostEqual(boundary_distances(official, other).max(), 3)
        self.assertAlmostEqual(boundary_distances(other, official).max(), 3)
        self.assertAlmostEqual(float(sorted(boundary_distances(official, other))[len(boundary_distances(official, other)) // 2]), 0)

    def test_a_shared_map_offset_is_found_beyond_the_features_spacing(self):
        # Each fix's feature is drawn (6, -5) m from its surveyed coordinate, among other corners
        # closer to it. A nearest-corner match reads those; the neighbourhood's consensus reads 7.8 m.
        rng = numpy.random.default_rng(7)
        fixes = []
        for i in range(30):
            x, y = 1000.0 * i, 0.0
            others = rng.uniform(-140, 140, size=(600, 2))
            others = others[numpy.hypot(*(others - (6.0, -5.0)).T) > 4]
            fixes.append(((x, y), numpy.vstack([others, [(6.0, -5.0)]]) + (x, y)))
        self.assertLess(numpy.median([numpy.hypot(*(f - xy).T).min() for xy, f in fixes]), 7.0)
        results = area_error.consensus(fixes)
        for offset, error, on in results:
            self.assertAlmostEqual(offset[0], 6.0, delta=0.5)
            self.assertAlmostEqual(offset[1], -5.0, delta=0.5)
            self.assertAlmostEqual(error, 7.81, delta=0.5)
            self.assertTrue(on)

    def test_a_place_carries_the_error_of_its_own_neighbourhood(self):
        xy = numpy.array([(float(i), 0.0) for i in range(40)] + [(10_000.0 + i, 0.0) for i in range(40)])
        errors = numpy.array([2.0] * 40 + [60.0] * 40)
        found = area_error.ErrorField(xy, errors)
        self.assertEqual(float(found.at([(5.0, 0.0)])[0]), 2.0)
        self.assertEqual(float(found.at([(10_005.0, 0.0)])[0]), 60.0)

    def test_the_fix_names_the_feature_the_map_draws(self):
        self.assertEqual(area_error.feature_kind('TRIPLICE DI CONFINE'), 'triple')
        self.assertEqual(area_error.feature_kind('SPIGOLO NORD - EST FABBRICATO'), 'building')
        self.assertEqual(area_error.feature_kind('INCROCIO DI MURI A SECCO'), 'wall')
        self.assertIsNone(area_error.feature_kind('ASSE PALO ENEL'))
        self.assertEqual(area_error.corner_direction('SPIGOLO SUD OVEST FABBRICATO'), (-1, -1))


class MetricGeometryForC(unittest.TestCase):
    def geography(self, error=2.0, unplaced=(), far=None):
        parts = (ErrorPart('cadastre', None, error),)
        if far is not None:     # a second source drawing the outline's east side only
            parts += (ErrorPart('istat-boundaries', box(29, -1, 31, 31), far),)
        zones = (Zone('infected', ('ZONA INFETTA',), box(0, 0, 10, 10), 'annex', ('cadastre',),
                      None, unplaced, errors=parts),
                 Zone('buffer', ('ZONA CUSCINETTO',), box(0, 0, 30, 30).difference(box(0, 0, 10, 10)),
                      'rule', ('cadastre',), errors=parts))
        return AdoptedGeography('REG:v1', 'REG', date(2024, 1, 1), None, zones)

    def test_a_complete_construction_reaches_c_with_its_bound(self):
        area = self.geography().metric()
        self.assertEqual((area.error_m, area.geometry.area), (3.0, 900))    # 2 m and the 1 m offset polygon
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

    def test_the_bound_is_that_of_the_outline_near_the_place(self):
        # A far-side source with a large error does not widen the bound at the other side.
        parts = (ErrorPart('cadastre', None, 2.0),
                 ErrorPart('istat-boundaries', box(29_900, -100, 30_100, 30_100), 400.0))
        zone = Zone('infected', ('ZONA INFETTA',), box(0, 0, 30_000, 30_000), 'annex', ('cadastre',), errors=parts)
        geography = AdoptedGeography('REG:v1', 'REG', date(2024, 1, 1), None, (zone,))
        self.assertEqual(geography.metric(Point(-600, 15_000)).error_m, 3.0)
        self.assertEqual(geography.metric(Point(5_000, 15_000)).error_m, 3.0)      # the west side is nearest
        self.assertEqual(geography.metric(Point(30_600, 15_000)).error_m, 401.0)

    def test_the_shared_boundary_is_the_buffer_s_inner_edge(self):
        self.assertAlmostEqual(self.geography().shared_boundary.length, 20)


class CommonFrame(unittest.TestCase):
    """Every error D supplies is stated in the cadastral frame, so C never counts shared error twice."""

    def test_a_cadastre_built_part_carries_the_construction_tolerance_not_the_ground_error(self):
        sources = Sources(ROOT)
        tolerance = sources.construction_tolerance
        self.assertIsNotNone(tolerance)
        parts = _source_errors(sources, {'cadastre'})
        self.assertEqual([(p.source, p.error_m, p.field) for p in parts], [('cadastre', tolerance, None)])
        # A cadastral parcel (0 m in the frame) well inside a cadastre-built zone is inside for C.
        zone = Zone('infected', ('ZONA INFETTA',), box(0, 0, 30_000, 30_000), 'annex', ('cadastre',), errors=parts)
        area = AdoptedGeography('REG:v1', 'REG', date(2024, 1, 1), None, (zone,))
        parcel = box(500, 500, 560, 540)
        self.assertIs(partial_parcel(MetricGeometry(parcel, UTM, 0.0), area.metric(parcel)).truth, True)


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

    @unittest.skipUnless(held('istat-codes'), 'the geometry sources are not in this store')
    def test_the_version_names_its_zones_and_the_plants_of_its_foci(self):
        version = version_of('REG-PUGLIA-U181-DIR-2026-00082:area-state-transition:v1')
        sources = Sources(ROOT, comuni=())
        build = _Builder(sources, version)
        self.assertTrue(all(build.by_role[role] for role in ('infected', 'containment', 'focus', 'buffer')))
        self.assertEqual(plant_roles(sources, version), ('focus',))
        self.assertIn('FOCOLAI', ' '.join(build.words('focus')))

    @unittest.skipUnless(held('cadastre-fogli') and held('istat-boundaries'), 'the geometry sources are not in this store')
    def test_unpublished_sheets_are_the_territory_no_published_sheet_covers(self):
        units = AdministrativeUnits(ROOT)
        massafra = units.comune(catastale='F027')
        reach = units.comune_geometry(massafra).envelope
        near = {c.catastale for c in units.comuni_of('Puglia')
                if c.province == massafra.province or c.province.name == 'Bari'
                if units.comune_geometry(c) is not None and units.comune_geometry(c).intersects(reach)}
        sources = Sources(ROOT, comuni=near)
        missing, territory = sources.unpublished(massafra)
        self.assertEqual(missing, ('15', '16', '23'))
        self.assertAlmostEqual(territory.area / 1e6, 10.1, delta=0.2)
        published = [g for (c, _, _), found in sources.sheets.items() if c == 'F027' for _, g in found]
        self.assertLess(territory.intersection(shapely.union_all(published)).area, 1.0)
        # The territory is the sheet exactly where every unpublished sheet is listed alike.
        build = _Builder(sources, version_of('REG-PUGLIA-U181-DIR-2024-00158:area-state-transition:v1'))
        self.assertTrue(build.sheet(massafra, Sheet(None, '16', False), ('15', '16', '23'))[1])
        self.assertFalse(build.sheet(massafra, Sheet(None, '16', False), ('16',))[1])

    @unittest.skipUnless(held('cadastre-fogli'), 'the geometry sources are not in this store')
    def test_the_named_plants_are_the_subspecies_in_the_listed_units_up_to_the_act(self):
        version = version_of('REG-PUGLIA-U181-DIR-2025-00059:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'F220'})
        self.assertEqual(plant_roles(sources, version), ('infected',))
        sheet = sources.sheets[('F220', '', '61')][0][1]
        inside = sheet.representative_point()
        found = named_plants(sources, version, [
            (date(2025, 4, 1), ('PAUCA',), inside.x, inside.y),
            (date(2025, 5, 1), ('PAUCA',), inside.x + 1, inside.y),       # after the act
            (date(2025, 4, 1), ('MULTIPLEX',), inside.x + 2, inside.y),   # another subspecies
            (date(2025, 4, 1), ('PAUCA',), 0.0, 0.0)])                    # outside the listed units
        self.assertEqual(found, {'infected': ((inside.x, inside.y),)})
        # Row 1's cadastral reference joins a plant its position alone does not place.
        by_reference = named_plants(sources, version, [
            Observation(date(2025, 4, 1), ('PAUCA',), 1.0, 1.0, 'F220', '061', None),
            Observation(date(2025, 4, 1), ('PAUCA',), 2.0, 2.0, 'F220', '999', None)])
        self.assertEqual(by_reference, {'infected': ((1.0, 1.0),)})


class ActPlants(unittest.TestCase):
    """A named plant is placed by the unit its act lists, with the cadastre's local error there."""

    @unittest.skipUnless(held('cadastre-fogli') and held('cadastre-particelle') and held('istat-boundaries'),
                         'the geometry sources are not in this store')
    def test_a_plant_takes_the_parcels_the_act_lists(self):
        version = version_of('REG-PUGLIA-U181-DIR-2024-00008:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'L425', 'A662', 'B716', 'F923'})
        zones = {z.role: z for z in construct(sources, version)}
        plants = zones['infected'].plants
        self.assertEqual(len(plants), 53)
        self.assertTrue(all('particella' in p.by for p in plants))
        parcels = shapely.union_all([p.geometry for p in plants])
        self.assertTrue(zones['infected'].geometry.covers(parcels))
        # The zone is the parcels' 50 m reach, not a circle around each sheet.
        self.assertLess(zones['infected'].geometry.area, parcels.buffer(51).area)
        # In the cadastral frame a listed parcel carries only the construction tolerance, never
        # the map's ground error against surveyed fixes.
        tolerance = sources.construction_tolerance
        self.assertIsNotNone(tolerance)
        for p in plants:
            self.assertEqual(p.error_m, tolerance)
        area = AdoptedGeography(version.provision_version_id, version.instrument_id, version.effective_from,
                                version.effective_to_exclusive, tuple(zones.values()))
        metric = area.metric(parcels.centroid)
        self.assertIsInstance(metric, MetricGeometry)
        self.assertEqual(metric.error_m, tolerance + 1.0)      # and the 1 m offset polygon

    @unittest.skipUnless(held('cadastre-fogli') and held('istat-boundaries'), 'the geometry sources are not in this store')
    def test_a_sheet_listed_alone_places_its_plant_and_row_1_does_not_displace_it(self):
        version = version_of('REG-PUGLIA-U181-DIR-2025-00059:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'F220'})
        sheet = shapely.union_all([g for _, g in sources.sheets[('F220', '', '61')]])
        elsewhere = sheet.representative_point().x + 10_000, sheet.representative_point().y, 5.0
        zones = {z.role: z for z in construct(sources, version, plants={'infected': (elsewhere,)})}
        plant, = zones['infected'].plants
        self.assertEqual(plant.by, 'Minervino Murge foglio 61')
        self.assertTrue(zones['infected'].geometry.covers(sheet))
        self.assertFalse(zones['infected'].geometry.covers(Point(elsewhere[:2])))
        area = AdoptedGeography(version.provision_version_id, version.instrument_id, version.effective_from,
                                None, tuple(zones.values()))
        self.assertIsInstance(area.metric(sheet.centroid), MetricGeometry)

    @unittest.skipUnless(held('cadastre-fogli') and held('cadastre-particelle') and held('istat-boundaries'),
                         'the geometry sources are not in this store')
    def test_a_listed_unit_not_held_is_placed_by_row_1_or_not_at_all(self):
        version = version_of('REG-PUGLIA-U181-DIR-2024-00008:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'L425', 'A662', 'B716', 'F923'})
        parcel = shapely.union_all(sources.parcels.pop(('L425', '', '5', '818')))
        inside = parcel.representative_point()
        zones = {z.role: z for z in construct(sources, version)}
        self.assertIn(None, [p.geometry for p in zones['infected'].plants])
        area = AdoptedGeography(version.provision_version_id, version.instrument_id, version.effective_from,
                                None, tuple(zones.values()))
        with self.assertRaisesRegex(MissingInput, 'plants'):
            area.metric(inside)
        # A row 1 positive with its measured error places the plant the act's unit cannot.
        zones = {z.role: z for z in construct(sources, version, plants={'infected': ((inside.x, inside.y, 4.0),)})}
        self.assertEqual([p.by for p in zones['infected'].plants if p.by == 'row 1'], ['row 1'])
        self.assertNotIn(None, [p.geometry for p in zones['infected'].plants])
        self.assertTrue(zones['infected'].geometry.covers(inside.buffer(49)))


class AnnexBeyondTheRule(unittest.TestCase):
    """The annex still speaks where the rule leaves room: beyond B's floor, and for each unit."""

    @unittest.skipUnless(held('cadastre-fogli') and held('region-layer'), 'the geometry sources are not in this store')
    def test_a_buffer_without_a_width_holds_the_units_its_annex_places_wholly_in_it(self):
        version = version_of('REG-PUGLIA-U181-DIR-2026-00082:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'F915'})
        build = _Builder(sources, version)
        noci_rows = [s for s in build.by_role['buffer'] if s.comune and s.comune.upper() == 'NOCI']
        annexed, partial = build.annex('buffer', noci_rows)
        noci = lambda n: shapely.union_all([g for _, g in sources.sheets[('F915', '', n)]])
        # 'NOCI ... 39*, 40*, 41*': wholly in the buffer.
        for sheet in ('39', '40', '41'):
            self.assertGreater(noci(sheet).intersection(annexed).area / noci(sheet).area, 0.99)
        # 'NOCI ... 33, ... 38': partly in it; only the act's map, as the Region's layer, places the part.
        self.assertTrue({'Noci foglio 33', 'Noci foglio 38'} <= {u.place for u in partial})
        drawn, still, errors = _drawn(sources, version, 'buffer', partial)
        self.assertEqual(still, ())
        self.assertTrue(drawn.intersects(noci('33')))
        self.assertEqual([e.source for e in errors], ['region-layer'])

    @unittest.skipUnless(held('cadastre-fogli') and held('istat-boundaries'), 'the geometry sources are not in this store')
    def test_a_unit_placed_wholly_in_the_buffer_is_in_it_beyond_the_stated_band(self):
        version = version_of('REG-PUGLIA-U181-DIR-2024-00158:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'C975'})
        build = _Builder(sources, version)
        rows = [s for s in build.by_role['buffer'] if s.comune and s.comune.upper() == 'CONVERSANO']
        annexed, partial = build.annex('buffer', rows)
        # 'CONVERSANO ... 45*, 51*, 52': foglio 51 is wholly in the buffer, also where the band
        # stated from the infected zone does not reach it.
        c51 = shapely.union_all([g for _, g in sources.sheets[('C975', '', '51')]])
        origin = shapely.box(c51.bounds[0] - 9_000, c51.bounds[1], c51.bounds[0] - 8_000, c51.bounds[3])
        buffer = buffer_extent(sources, [(origin, 5_000.0)], annexed)
        self.assertFalse(buffer_extent(sources, [(origin, 5_000.0)]).intersects(c51))
        self.assertGreater(c51.intersection(buffer).area / c51.area, 0.99)
        self.assertIn('Conversano foglio 52', {u.place for u in partial})


if __name__ == '__main__':
    unittest.main()

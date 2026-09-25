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
                                    _Builder, _disagreements, _drawn, _inspire_zoning, _layer_circles, _layer_gaps)
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


class WholeUnitInterior(unittest.TestCase):
    """A unit named whole is its whole territory: a seam between its held sheets is in it."""

    class Units:
        def __init__(self, outlines):
            self.outlines = outlines

        def comune_geometry(self, comune):
            return self.outlines[comune.catastale]

    class Stub:
        def __init__(self, outlines, sheets, errors):
            self.administrative = WholeUnitInterior.Units(outlines)
            self._sheet_index = (shapely.STRtree(sheets), sheets)
            self.istat_errors = errors
            self.outline = shapely.union_all(sheets).boundary.buffer(5.0)

        def cadastral_outline(self, code):
            return self.outline

    class Comune:
        def __init__(self, catastale):
            self.catastale = catastale

    def test_a_seam_the_zone_encloses_joins_the_unit_named_whole_and_nothing_else_does(self):
        from cordon_d.area_geometry import _whole_interior
        # Comune A (named whole) and comune B (not named) side by side; a 30 m seam no held
        # sheet covers runs across their border inside the zone, and an inlet opens on A's coast.
        a, b = box(0, 0, 1_000, 1_000), box(1_000, 0, 2_000, 1_000)
        seam, inlet = box(400, 485, 1_600, 515), box(300, 950, 330, 1_000)
        zone = box(0, 0, 2_000, 1_000).difference(seam).difference(inlet)
        sheets = [box(0, 0, 2_000, 485), box(0, 515, 300, 1_000), box(330, 515, 2_000, 1_000),
                  box(0, 485, 400, 515), box(1_600, 485, 2_000, 515)]
        sources = self.Stub({'A': a, 'B': b}, sheets, {'A': 12.0})
        geometry, errors = _whole_interior(sources, zone, [self.Comune('A')])
        self.assertTrue(geometry.covers(Point(700, 500)))              # the seam inside A joins
        self.assertFalse(geometry.contains(Point(1_300, 500)))         # B is not named whole
        self.assertFalse(geometry.contains(Point(315, 990)))           # the outer line keeps its source
        self.assertAlmostEqual(geometry.area, zone.area + 600 * 30, delta=1)
        # ISTAT's line now draws the zone's outline across the seam, with its measured error.
        self.assertEqual([(e.source, e.error_m) for e in errors], [('istat-boundaries', 12.0)])
        self.assertTrue(errors[0].region.covers(Point(1_000, 500)))
        # An island of the zone inside a seam stays the zone's; the seam around it joins.
        ring = box(0, 0, 1_000, 1_000).difference(box(300, 300, 700, 700))
        island = box(450, 450, 550, 550)
        filled, _ = _whole_interior(self.Stub({'A': a}, [box(0, 0, 1_000, 300)], {'A': 12.0}),
                                    shapely.union_all([ring, island]), [self.Comune('A')])
        self.assertTrue(filled.covers(Point(350, 500)) and filled.covers(Point(500, 500)))
        self.assertAlmostEqual(filled.area, 1_000_000, delta=1)
        # A zone with no hole is unchanged.
        plain = box(0, 0, 10, 10)
        self.assertEqual(_whole_interior(sources, plain, [self.Comune('A')]), (plain, ()))


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

    @unittest.skipUnless(held('cadastre-fogli'), 'the control windows are not in this store')
    def test_the_recorded_summary_is_what_the_fixes_measure_on_read(self):
        record, = [r for r in records(ROOT, 'positional-error') if r['source'] == 'cadastre']
        control = ROOT / record['evidence']
        self.assertFalse(any('error_m' in f for f in json.loads(control.read_text())['fixes']))
        found = area_error.fix_errors(ROOT, control)
        if found is None:
            self.skipTest('the control windows are not in this store')
        errors = numpy.array([f['error_m'] for f in found])
        self.assertEqual((len(found), sum(f['on_consensus'] for f in found)),
                         (record['measured'], record['on_consensus']))
        self.assertEqual({k: round(float(numpy.percentile(errors, q)), 1) for k, q in (('p50', 50), ('p95', 95))}
                         | {'max': round(float(errors.max()), 1)}, record['fix_error_m'])

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


class BandAndAnnex(unittest.TestCase):
    """A band drawn from plants is held to the listed units; where the two disagree C answers neither way."""

    class Stub:
        def sheet_labels(self, geometry, minimum_m2=100.0):
            return []

    def test_the_band_beyond_the_listed_units_and_a_listed_unit_it_misses_are_neither_in_nor_out(self):
        plant = Point(0, 0)
        infected = plant.buffer(50)
        band = plant.buffer(2_550).difference(infected)
        listed = box(-3_000, -3_000, 1_000, 3_000)           # the annex lists the land west of x = 1,000
        missed = box(4_000, -500, 4_800, 500)                # listed partly in the buffer, beyond 2.5 km
        held = listed.union(missed)
        beyond = [band.difference(held)]
        buffer = band.intersection(held)
        zones = {'infected': Zone('infected', ('ZONA INFETTA',), infected, 'rule', ('plants',))}
        found = _disagreements(self.Stub(), zones, ('infected',), buffer, held, beyond,
                               (Unplaced('buffer', 'p2', 'foglio 9', 'legend', missed),))
        self.assertEqual([(d.role, d.kind) for d in found], [('buffer', 'beyond'), ('buffer', 'short')])
        self.assertAlmostEqual(found[0].geometry.area, band.difference(listed).area, delta=1)
        self.assertGreater(found[0].reach_m, 1_550)          # the disputed land reaches 1,550 m past the line
        parts = (ErrorPart('plants', None, 7.4),) + tuple(
            ErrorPart('annex-disagreement', d.geometry, d.reach_m, place_only=True) for d in found)
        area = AdoptedGeography('REG:v1', 'REG', date(2025, 1, 1), None,
                                (zones['infected'], Zone('buffer', ('ZONA CUSCINETTO',), buffer, 'rule', ('plants',),
                                                         errors=parts, disagreements=found)))
        truth = lambda p: adopted_membership(MetricGeometry(p, UTM, 7.4), area.metric(p)).truth
        self.assertIsNone(truth(Point(2_000, 0)))             # the band says in, the annex out
        self.assertIsNone(truth(Point(1_020, 0)))
        self.assertIsNone(truth(Point(4_400, 0)))             # the annex says partly in, the band out
        self.assertTrue(truth(Point(600, 0)))                 # both say in, beside the disputed land
        self.assertEqual(area.metric(Point(600, 0)).error_m, 8.4)
        self.assertTrue(truth(Point(-1_500, 0)))
        self.assertFalse(truth(Point(-6_000, 0)))             # both say out
        self.assertFalse(truth(Point(5_600, 0)))
        # C asks of a parcel whether any part of it lies in the area. A parcel straddling the
        # band's outer edge beyond the listed units, its representative point beyond the band,
        # has part of itself in the disputed land: neither way, not False 1,100 m from the area.
        parcel = lambda g: partial_parcel(MetricGeometry(g, UTM, 7.4), area.metric(g)).truth
        straddling = box(2_450, -100, 2_900, 100)
        self.assertFalse(found[0].geometry.intersects(straddling.representative_point()))
        self.assertGreater(found[0].geometry.intersection(straddling).area, 15_000)
        self.assertIsNone(parcel(straddling))
        # A parcel that only touches the disputed land has no part in it and keeps its bound,
        # also where arithmetic along the shared edge leaves a sliver (0.0002 m² here).
        touching = box(500, -100, 1_000.000_001, 100)
        self.assertLess(0, found[0].geometry.intersection(touching).area)
        self.assertLess(found[0].geometry.intersection(touching).area, 0.001)
        self.assertEqual(area.metric(touching).error_m, 8.4)
        self.assertTrue(parcel(touching))
        self.assertFalse(parcel(box(5_600, -100, 5_800, 100)))

    def test_the_region_s_circles_give_back_their_plants(self):
        layer = shapely.union_all([Point(0, 0).buffer(50), Point(60, 0).buffer(50), Point(500, 0).buffer(50)])
        centres = _layer_circles(layer, box(-10, -10, 10, 10), 50)
        expected = shapely.union_all([Point(0, 0).buffer(50), Point(60, 0).buffer(50)])
        self.assertTrue(centres.buffer(50).covers(expected.buffer(-0.5)))
        self.assertTrue(expected.buffer(1.5).covers(centres.buffer(50)))
        self.assertIsNone(_layer_circles(layer, box(1_000, 0, 1_100, 10), 50))


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

    @unittest.skipUnless(held('cadastre-fogli') and held('istat-boundaries') and held('region-layer'),
                         'the geometry sources are not in this store')
    def test_a_named_comune_is_whole_where_the_cadastre_publishes_none_of_its_sheets(self):
        units = AdministrativeUnits(ROOT)
        brindisi = units.comune(catastale='B180')
        reach = units.comune_geometry(brindisi).envelope
        near = {c.catastale for c in units.comuni_of('Puglia')
                if units.comune_geometry(c) is not None and units.comune_geometry(c).intersects(reach)}
        sources = Sources(ROOT, comuni=near)
        missing, territory = sources.unpublished(brindisi)
        self.assertIn('33', missing)
        extent, used = sources.comune_extent(brindisi)
        self.assertEqual(used, ('cadastre', 'istat-boundaries'))
        # DDS 82/2026 names the province of Brindisi whole. No cadastre publishes a sheet at
        # these two places: one inside Brindisi's held sheets, one on its coast. Both are in it.
        inland, coast = Point(741441, 4503503), Point(747885, 4505510)
        published = [g for (c, _, _), found in sources.sheets.items() if c == 'B180' for _, g in found]
        self.assertFalse(shapely.union_all(published).intersects(inland))
        self.assertTrue(extent.covers(inland) and extent.covers(coast))
        # Where the part reaches the comune's border the act's map, the Region's layer, draws it.
        version = version_of('REG-PUGLIA-U181-DIR-2026-00082:area-state-transition:v1')
        build = _Builder(sources, version)
        geometry = build.extent(brindisi)
        self.assertTrue(build.istat_drawn)
        drawn, gaps, errors, replaced = _layer_gaps(sources, version, 'infected', geometry, build)
        self.assertTrue(drawn.covers(inland) and gaps.covers(coast))
        self.assertEqual(errors[0].source, 'region-layer')
        # Where ISTAT still draws a line (against another comune), its measured error goes with it.
        self.assertTrue(all(e.source == 'istat-boundaries' and e.error_m for e in errors[1:]))
        self.assertEqual(build.istat_drawn, [])
        _, layer = sources.region_layer(version.provision_version_id, 'infected')
        coastline = shapely.union_all([n for _, n in replaced]).boundary.difference(
            sources.cadastral_outline('B180'))
        # The rest of the line is ISTAT's, between Brindisi and its neighbours inside the zone.
        distances = shapely.distance(shapely.points(shapely.get_coordinates(coastline)), layer.boundary)
        self.assertLess(numpy.percentile(distances, 95), 1.0)

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


def row1_held() -> bool:
    return held('cadastre-fogli') and Sources(ROOT, comuni=()).row1 is not None


class ActPlants(unittest.TestCase):
    """A named plant stands at its located position; the unit the act lists is where its circle reaches."""

    DDS59 = 'REG-PUGLIA-U181-DIR-2025-00059:area-state-transition:v1'

    def area(self, version, zones):
        return AdoptedGeography(version.provision_version_id, version.instrument_id, version.effective_from,
                                None, tuple(zones.values()))

    @unittest.skipUnless(held('cadastre-fogli') and held('istat-boundaries'), 'the geometry sources are not in this store')
    def test_a_unit_no_located_plant_reaches_carries_its_extent_and_c_cannot_say_true(self):
        # DDS 59/2025 lists foglio 61 "PARZIALMENTE RICADENTI NEI BUFFER DI 50 METRI DALLE PIANTE".
        version = version_of(self.DDS59)
        sources = Sources(ROOT, comuni={'F220'})
        sheet = shapely.union_all([g for _, g in sources.sheets[('F220', '', '61')]])
        zones = {z.role: z for z in construct(sources, version, plants={})}
        plant, = zones['infected'].plants
        self.assertEqual(plant.by, 'Minervino Murge foglio 61: not located, the unit with its extent')
        self.assertGreater(plant.error_m, 2 * shapely.minimum_bounding_radius(sheet) + 100)
        area = self.area(version, zones)
        truth = lambda p: adopted_membership(MetricGeometry(p, UTM, 7.4), area.metric(p)).truth
        # The plant may stand anywhere within 50 m of the sheet. The two places 2,251 m from it
        # that the sheet-placed plant put in the area may lie beyond the act's 2,550 m: neither way.
        for place in (Point(583_448.4, 4_553_301.9), Point(588_179.7, 4_549_411.2)):
            self.assertIsNone(truth(place))
        # Inside the sheet every place the plant can stand is within 2,550 m: in.
        self.assertTrue(truth(sheet.representative_point()))

    @unittest.skipUnless(row1_held(), 'row 1 is not in this store')
    def test_the_act_s_plant_is_the_row_1_positive_it_names_on_a_real_version(self):
        version = version_of(self.DDS59)
        sources = Sources(ROOT, comuni={'F220'})
        sheet = shapely.union_all([g for _, g in sources.sheets[('F220', '', '61')]])
        zones = {z.role: z for z in construct(sources, version)}
        plant, = zones['infected'].plants
        self.assertEqual((plant.by, plant.error_m), ('row 1', sources.row1[1]))
        self.assertTrue(sheet.buffer(50).covers(plant.geometry))
        # The infected zone is the act's one 50 m circle, not the sheet plus 50 m.
        self.assertTrue(numpy.pi * 50 ** 2 < zones['infected'].geometry.area < numpy.pi * 51 ** 2)
        self.assertFalse(zones['infected'].geometry.covers(sheet))
        # The buffer lies within the act's 2.5 km of the plant (with the offset polygons' 1 m
        # each), save the sheets its annex marks wholly in it ("*").
        far = zones['buffer'].geometry.difference(plant.geometry.buffer(2_554, quad_segs=512))
        self.assertLess(far.difference(zones['buffer'].listed).area, 1.0)
        area = self.area(version, zones)
        self.assertAlmostEqual(area.geometry.area / 1e6, numpy.pi * 2.55 ** 2, delta=0.1)
        # Two places 6,125.6 m apart, each 2,251 m from the sheet, that the sheet-placed plant
        # put in the area: a 2,550 m disc cannot hold both.
        truths = [adopted_membership(MetricGeometry(p, UTM, 7.4), area.metric(p)).truth
                  for p in (Point(583_448.4, 4_553_301.9), Point(588_179.7, 4_549_411.2))]
        self.assertNotEqual(truths, [True, True])

    @unittest.skipUnless(row1_held(), 'row 1 is not in this store')
    def test_row_1_s_error_is_read_from_row_1_and_only_the_positives_are_cached(self):
        from cordon_d.area_geometry import row1_positives
        from cordon_d.spatial import positional_terms
        document = row1_positives(ROOT)
        self.assertEqual(document['error_m'], positional_terms(store_root(ROOT)).error_m)
        cached = [json.loads(p.read_text()) for p in (store_root(ROOT) / 'derived/areas/row1-positives').glob('*.json')]
        self.assertIn(document['positives'], cached)         # the positives alone, no error beside them

    @unittest.skipUnless(held('cadastre-fogli') and held('cadastre-particelle') and held('istat-boundaries'),
                         'the geometry sources are not in this store')
    def test_a_listed_unit_not_held_leaves_the_version_without_a_bound(self):
        version = version_of('REG-PUGLIA-U181-DIR-2024-00008:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'L425', 'A662', 'B716', 'F923'})
        parcel = shapely.union_all(sources.parcels.pop(('L425', '', '5', '818')))
        inside = parcel.representative_point()
        for plants in ({}, {'infected': ((inside.x + 5_000, inside.y, 7.4),)}):
            zones = {z.role: z for z in construct(sources, version, plants=plants)}
            self.assertIn(None, [p.geometry for p in zones['infected'].plants])
            with self.assertRaisesRegex(MissingInput, 'plants'):
                self.area(version, zones).metric(inside)

    @unittest.skipUnless(held('cadastre-fogli') and held('cadastre-particelle') and held('istat-boundaries'),
                         'the geometry sources are not in this store')
    def test_a_located_plant_whose_circle_reaches_the_listed_parcels_places_them_all(self):
        # DDS 8/2024 lists "particelle catastali ricadenti nel buffer di 50 metri dalle piante".
        version = version_of('REG-PUGLIA-U181-DIR-2024-00008:area-state-transition:v1')
        sources = Sources(ROOT, comuni={'L425', 'A662', 'B716', 'F923'})
        parcel = shapely.union_all(sources.parcels[('L425', '', '5', '818')])
        at = parcel.representative_point()
        zones = {z.role: z for z in construct(sources, version, plants={'infected': ((at.x, at.y, 7.4),)})}
        plants = zones['infected'].plants
        self.assertEqual(plants[0].by, 'row 1')
        reached = [p for p in plants[1:] if p.geometry is not None]
        self.assertTrue(all(p.by.endswith('not located, the unit with its extent') for p in reached))
        self.assertFalse(any('foglio 5 particella 818' in p.by for p in plants))
        self.assertTrue(zones['infected'].geometry.covers(at.buffer(49)))


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
        # Its ground error: the layer's measured distance from the cadastre plus the cadastre's own.
        # The layer's is measured against the version as constructed, on read; a stand-in here.
        place = numpy.array([[noci('33').centroid.x, noci('33').centroid.y]])
        layer = area_error.ErrorField(place + [[0, 0], [10, 0]], numpy.array([40.0, 40.0]))
        sources._region_fields[(version.provision_version_id, 'buffer')] = layer
        self.assertAlmostEqual(float(errors[0].field.at(place)[0]),
                               float(layer.at(place)[0] + sources.cadastral_error.at(place)[0]))
        self.assertGreater(float(errors[0].field.at(place)[0]), float(layer.at(place)[0]))

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

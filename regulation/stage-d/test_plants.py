"""Row 4: plant-occasions and the populations C's distance consumers read around each infected plant.

The synthetic checks build places and area outlines whose answers follow from their construction and
always run. The real-record checks read row 1 over this checkout's store and skip where it is not held;
the records were picked by the rules the pull request states, before any result was computed, and the
expected answers are recomputed here from the published coordinates and the printed labels.
"""
from datetime import date
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from pyproj import CRS
from shapely.geometry import Point, box

from cordon_c.core import Evaluation, MissingInput, Snapshot
from cordon_c.spatial import MetricGeometry, adopted_membership
from cordon_d.area_geometry import AdoptedGeography, ErrorPart, Unplaced, Zone
from cordon_d.plants import (BRANCH_CAUSE, FIELD_CHECK, HECTARE_CAUSE, IDENTITY_CAUSE, LABEL_CAUSE, SUBSPECIES,
                             SUBSPECIES_CAUSE, Finding, Hosts, PlantOccasion, annex_ii, branch, infected_plants,
                             neighbourhood, publisher_pairs, same_plant, zone_tests)

ROOT = Path(__file__).resolve().parents[2]
UTM = CRS.from_user_input('EPSG:32633')
SNAPSHOT = Snapshot.load(ROOT)
DDS158 = 'REG-PUGLIA-U181-DIR-2024-00158:area-state-transition:v1'   # 2024-11-18 to 2026-05-11
DAY = date(2025, 7, 8)
PAIRS = publisher_pairs(['Olivo (Olea europaea)', 'Vite europea (Vitis L.)', 'Mandorlo (Prunus dulcis)',
                         'Agrumi (Citrus)'])
HOSTS = Hosts(ROOT, PAIRS)


def occasion(reference, x, y, labels, *, day=date(2025, 7, 7), positive=False, symptoms=False):
    return PlantOccasion(('observation', reference, day.isoformat()), day, tuple(labels), positive, symptoms,
                         None, (x, y))


def locate(o, error=7.4):
    return MetricGeometry(Point(*o.xy), UTM, error)


class HostNames(unittest.TestCase):
    def test_a_label_is_named_by_the_publishers_own_pairs_or_an_exact_annex_name(self):
        self.assertEqual(HOSTS.name(('OLIVO',), DAY), 'Olea europaea')
        self.assertEqual(HOSTS.name(('OLIVO', 'Olivo (Olea europaea)'), DAY), 'Olea europaea')
        self.assertEqual(HOSTS.name(('Vite europea (Vitis L.)',), DAY), 'Vitis')
        self.assertEqual(HOSTS.name(('Prunus dulcis',), DAY), 'Prunus dulcis')
        # Labels that disagree, or match no pair, give no name; they are counted, never dropped.
        self.assertIsNone(HOSTS.name(('OLIVO', 'Mandorlo (Prunus dulcis)'), DAY))
        self.assertIsNone(HOSTS.name(('PIANTA SCONOSCIUTA',), DAY))
        found = HOSTS.unmatched([occasion('1', 0, 0, ['PIANTA SCONOSCIUTA']), occasion('2', 0, 0, ['OLIVO']),
                                 occasion('3', 0, 0, ['PIANTA SCONOSCIUTA'])])
        self.assertEqual(found, {('PIANTA SCONOSCIUTA',): 2})

    def test_annex_ii_is_read_per_subspecies_from_the_version_in_force(self):
        for day in (date(2024, 5, 13), date(2026, 8, 5)):
            annex = annex_ii(ROOT, day)
            self.assertEqual(set(annex), {'fastidiosa', 'multiplex', 'pauca'})
            self.assertIn('Vitis', annex['fastidiosa'])
            self.assertNotIn('Vitis', annex['multiplex'] | annex['pauca'])
            self.assertIn('Prunus', annex['multiplex'])
            self.assertIn('Olea europaea', annex['pauca'])   # 'Olea europaea subsp. europaea L.'

    def test_a_neighbour_is_specified_only_for_the_subspecies_of_the_finding(self):
        vine = occasion('v', 0, 0, ['Vite europea (Vitis L.)'], day=date(2024, 5, 13))
        self.assertIs(HOSTS.specified(vine, frozenset({'multiplex'})).truth, False)
        self.assertIs(HOSTS.specified(vine, frozenset({'fastidiosa'})).truth, True)
        self.assertIs(HOSTS.specified(vine, frozenset(SUBSPECIES)).truth, True)     # pending
        self.assertEqual(HOSTS.specified(vine, None).needs, frozenset({SUBSPECIES_CAUSE}))
        unknown_label = occasion('u', 0, 0, ['PIANTA SCONOSCIUTA'])
        self.assertEqual(HOSTS.specified(unknown_label, frozenset({'pauca'})).needs, frozenset({LABEL_CAUSE}))
        # A genus label where the part lists only species of that genus states no species.
        citrus = occasion('c', 0, 0, ['Agrumi (Citrus)'])
        self.assertEqual(HOSTS.specified(citrus, frozenset({'fastidiosa'})).needs, frozenset({'species of the plant'}))
        self.assertIs(HOSTS.specified(citrus, frozenset({'pauca'})).truth, True)          # 'Citrus L.'


def result(kind, analyte, *column):
    return SimpleNamespace(kind=kind, analyte=analyte, column=column)


def joined(reference, results, *, status='matched', complete=True):
    row = SimpleNamespace(results=tuple(results))
    return {'observation': SimpleNamespace(identity=('observation', reference, '2025-07-08')), 'status': status,
            'matches': [{'row': row, 'reading_complete': complete, 'key': ('sha', reference)}]}


class RowTwoFindings(unittest.TestCase):
    TYPING = ('ANALISI MOLECOLARE PER IDENTIFICAZIONE\nSOTTOSPECIE Xylella fastidiosa', 'Esito saggio Dupas et al., 2019')

    def findings(self, *items):
        occasions = {('observation', str(i), '2025-07-08'): occasion(str(i), 0, 0, ['OLIVO'], day=DAY)
                     for i in range(10)}
        return {f.occasion.key[1]: f for f in infected_plants(items, occasions)}

    def test_the_subspecies_is_row_2s_identification_and_pending_only_on_a_complete_row(self):
        found = self.findings(
            joined('1', [result('positive', 'Xylella fastidiosa', 'Real-time PCR'),
                         result('positive', 'multiplex', *self.TYPING, 'multiplex'),
                         result('negative', 'pauca', *self.TYPING, 'pauca')]),
            joined('2', [result('positive', 'Xylella fastidiosa', 'Real-time PCR')]),
            joined('3', [result('positive', 'Xylella fastidiosa', 'Real-time PCR')], complete=False),
            joined('4', [result('positive', 'Xylella fastidiosa', 'Real-time PCR'),
                         result('negative', 'multiplex', *self.TYPING, 'multiplex')]),
            joined('5', [result('negative', 'Xylella fastidiosa', 'Real-time PCR')]),
            joined('6', [result('positive', 'Xylella fastidiosa', 'Real-time PCR')], status='no eligible source-row'))
        self.assertEqual(set(found), {'1', '2', '3', '4'})
        self.assertEqual(found['1'].subspecies, frozenset({'multiplex'}))
        # A detection assay naming Xylella fastidiosa is not an identification of subsp. fastidiosa.
        self.assertEqual(found['2'].subspecies, frozenset(SUBSPECIES))
        self.assertIsNone(found['3'].subspecies)
        self.assertIsNone(found['4'].subspecies)


def geography(zones, identity=DDS158, start=date(2024, 11, 18), end=date(2026, 5, 11)):
    return AdoptedGeography(identity, identity.split(':')[0], start, end, tuple(zones))


def zone_of(role, geometry, error=20.0, **extra):
    return Zone(role, (), geometry, 'annex', ('cadastre',), errors=(ErrorPart('cadastre', None, error_m=error),),
                **extra)


class ZoneTest(unittest.TestCase):
    CONTAINMENT = box(0, 0, 10_000, 2_000)
    BUFFER = box(0, 2_000, 10_000, 7_000)

    def test_c_decides_membership_with_the_outline_error_near_the_place_and_the_places_own(self):
        area = geography([zone_of('containment', self.CONTAINMENT), zone_of('buffer', self.BUFFER)])
        places = [MetricGeometry(Point(x, y), UTM, 7.4) for x, y in
                  ((5_000, 1_000), (5_000, 1_980), (5_000, 1_960), (5_000, 30_000), (-20, 500), (-40, 500), (-9_000, 500))]
        tests = zone_tests(SNAPSHOT, area, places, 'containment')
        self.assertEqual([t.truth for t in tests], [True, None, True, False, None, False, False])
        # The whole-area and far-place answers are the ones C gives with the local error.
        whole = zone_tests(SNAPSHOT, area, places)
        for place, test in zip(places, whole):
            local = adopted_membership(place, area.metric(place.geometry, place.error_m))
            self.assertIs(test.truth, local.truth)
        # A version that adopts no zone of the role has no place in it.
        self.assertEqual({t.truth for t in zone_tests(SNAPSHOT, area, places, 'focus')}, {False})

    def test_a_parcel_reaches_c_with_the_cadastres_error_at_its_own_outline(self):
        import numpy
        from cordon_d.area_error import ErrorField
        from cordon_d.plants import parcel
        field = ErrorField(numpy.array([[x, y] for x in range(-2_000, 12_001, 1_000) for y in range(-2_000, 9_001, 1_000)],
                                       dtype=float),
                           numpy.array([5.0 if x < 5_000 else 30.0 for x in range(-2_000, 12_001, 1_000)
                                        for y in range(-2_000, 9_001, 1_000)]))
        sources = SimpleNamespace(cadastral_error=field, parcels={
            ('A', '', '1', '10'): [box(1_000, 1_000, 1_100, 1_050), box(1_100, 1_000, 1_150, 1_050)],
            ('A', '', '1', '11'): [box(9_000, 1_960, 9_100, 2_060)]})
        west, east = parcel(sources, ('A', '', '1', '10')), parcel(sources, ('A', '', '1', '11'))
        self.assertEqual(west.geometry.area, 150 * 50)                     # its features, one surface
        self.assertEqual((west.error_m, east.error_m), (5.0, 30.0))        # the field at its own vertices
        area = geography([zone_of('containment', self.CONTAINMENT)])
        inside, straddling = zone_tests(SNAPSHOT, area, [west, east], 'containment')
        self.assertIs(inside.truth, True)
        self.assertIsNone(straddling.truth)                                # C's partial_parcel at the edge

    def test_an_unplaced_unit_leaves_the_zone_test_unknown_with_its_words(self):
        unplaced = Unplaced('containment', 'Allegato 2', 'Massafra foglio 16', 'IL SIMBOLO *', None)
        area = geography([zone_of('containment', self.CONTAINMENT, unplaced=(unplaced,))])
        test, = zone_tests(SNAPSHOT, area, [MetricGeometry(Point(5_000, 1_000), UTM, 7.4)], 'containment')
        self.assertIsNone(test.truth)
        self.assertIn('Massafra foglio 16', next(iter(test.needs)))

    def test_the_branch_follows_the_zone_tests_and_an_unheld_version_leaves_it_unknown(self):
        yes, no, maybe = Evaluation(True), Evaluation(False), Evaluation(None, needs=frozenset({'x'}))
        self.assertEqual((branch([yes], [no], [yes]).containment.truth, branch([yes], [no], [yes]).pest_free_or_buffer.truth),
                         (True, False))
        self.assertIs(branch([no], [yes], [yes]).pest_free_or_buffer.truth, True)
        self.assertIs(branch([no, no], [no, no], [no, no]).pest_free_or_buffer.truth, True)   # in no area
        self.assertIs(branch([no], [no], [yes]).pest_free_or_buffer.truth, False)             # infected zone
        unheld = branch([no], [no], [no], unheld=('DDS 148/2024 is not held',))
        self.assertIsNone(unheld.containment.truth)
        self.assertIsNone(unheld.pest_free_or_buffer.truth)
        self.assertIsNone(branch([maybe], [no], [maybe]).containment.truth)


class Neighbourhood(unittest.TestCase):
    def setUp(self):
        self.plant = occasion('P', 0, 0, ['Mandorlo (Prunus dulcis)'], day=DAY, positive=True)
        self.others = [occasion('vine30', 30, 0, ['Vite europea (Vitis L.)']),
                       occasion('olive50', 0, 50, ['OLIVO']),
                       occasion('olive70', -70, 0, ['OLIVO']),
                       occasion('almond20', 0, -20, ['MANDORLO']),
                       occasion('prunus40', -40, 0, ['Prunus']),
                       occasion('olive250', 250, 0, ['OLIVO']),
                       occasion('olive450', 0, 450, ['OLIVO']),
                       occasion('later', 10, 0, ['OLIVO'], day=date(2025, 7, 9)),
                       occasion('old', 12, 0, ['OLIVO'], day=date(2021, 7, 1))]

    def run_(self, subspecies, containment, buffer, elsewhere=frozenset()):
        finding = Finding(self.plant, frozenset(subspecies), not subspecies, ())
        return neighbourhood(SNAPSHOT, finding, branch([Evaluation(containment)], [Evaluation(buffer)],
                                                       [Evaluation(containment or not buffer)]),
                             self.others, at=DAY, locate=locate, hosts=HOSTS, elsewhere=elsewhere)

    def test_c_decides_each_observed_neighbour_and_the_50_m_population_stays_incomplete(self):
        result = self.run_({'pauca'}, True, False)
        key = lambda name: ('observation', name, '2025-07-07')
        self.assertIs(result.inner[key('olive50')].truth, None)          # 50 m: within the 14.80 m margin
        self.assertIs(result.inner[key('almond20')].truth, True)
        self.assertIs(result.inner[key('vine30')].truth, False)          # vine: not specified for pauca
        self.assertNotIn(key('olive70'), result.inner)                   # beyond 64.80 m: not a candidate
        self.assertFalse({key('later'), key('old')} & (set(result.inner) | set(result.outer)))
        self.assertIs(result.outer[key('olive250')].truth, True)
        self.assertIsNone(result.outer[key('olive450')].truth)
        self.assertEqual(result.required.members, frozenset({str(key('almond20'))}))
        self.assertFalse(result.required.complete)
        self.assertEqual(result.required.qualification, FIELD_CHECK)
        self.assertIsNone(result.coverage.truth)
        self.assertIn('complete required population', result.coverage.needs)

    def test_the_branch_decides_which_population_runs(self):
        self.assertEqual(self.run_({'pauca'}, False, True).outer.needs, frozenset({HECTARE_CAUSE}))
        unknown_branch = neighbourhood(SNAPSHOT, Finding(self.plant, frozenset({'pauca'}), False, ()),
                                       branch([Evaluation(None, needs=frozenset({'x'}))], [Evaluation(False)],
                                              [Evaluation(True)]),
                                       self.others, at=DAY, locate=locate, hosts=HOSTS)
        self.assertEqual(unknown_branch.inner.needs, frozenset({BRANCH_CAUSE}))
        self.assertEqual(unknown_branch.outer.needs, frozenset({BRANCH_CAUSE}))
        self.assertIs(self.run_({'pauca'}, False, False).inner.truth, False)   # neither DDS 45/2025 branch

    def test_species_facts_bound_by_the_elsewhere_inventory_never_complete(self):
        key = ('observation', 'olive50', '2025-07-07')
        same_key = ('observation', 'almond20', '2025-07-07')
        facts = self.run_({'pauca'}, True, False).species
        values = {k[1]: v.truth for k, v in facts[key].items()}
        self.assertIs(values['plants of the same species as the infected plant, whatever their health'], False)
        self.assertIsNone(values['plants of other species found infected elsewhere in the demarcated area'])
        found = self.run_({'pauca'}, True, False, elsewhere=frozenset({'Olea europaea'})).species[key]
        self.assertIs({k[1]: v.truth for k, v in found.items()}[
            'plants of other species found infected elsewhere in the demarcated area'], True)
        same = {k[1]: v.truth for k, v in facts[same_key].items()}
        self.assertIs(same['plants of the same species as the infected plant, whatever their health'], True)
        # A genus label is another species than a finding of another genus; of its own genus, unknown.
        vine = {k[1]: v for k, v in facts[('observation', 'vine30', '2025-07-07')].items()}
        self.assertIs(vine['plants of the same species as the infected plant, whatever their health'].truth, False)
        prunus = {k[1]: v for k, v in facts[('observation', 'prunus40', '2025-07-07')].items()}
        self.assertEqual(prunus['plants of the same species as the infected plant, whatever their health'].needs,
                         frozenset({'plant and finding species identities'}))

    def test_two_occasions_at_one_place_stay_two(self):
        a = occasion('1', 100, 100, ['OLIVO'], positive=True)
        b = occasion('2', 100.4, 100, ['OLIVO'], day=date(2025, 8, 1), positive=False)
        self.assertIs(same_plant(a, a).truth, True)
        self.assertEqual(same_plant(a, b).needs, frozenset({IDENTITY_CAUSE}))


class Strata(unittest.TestCase):
    def test_the_workbook_and_b_supply_4_1_2_and_nothing_is_borrowed_for_4_1_3(self):
        from cordon_d.strata import DGR, DEPENDENCE_CAUSE, SENSITIVITY_CAUSE, design_adequacy, observed_support, strata
        groups = strata(ROOT, DGR)
        high, base = groups[('§4.1.2', 'olive')]
        self.assertEqual((high.population, base.population), (990804, 58371255))
        self.assertEqual((high.inspection_units, base.inspection_units, high.relative_risk), (2765, 5537, 2.0))
        self.assertEqual((high.sampling_effectiveness, high.diagnostic_sensitivity), (0.7, 0.78))
        # DGR 1075/2025 Table 2's transcription prints the same populations.
        transcription = (ROOT / 'regulation/jurisdiction/regional/DGR-1075-2025-plan.vision-ocr.txt').read_text()
        start = transcription.index('Tabella 2 - Parametri')
        page = transcription[start:transcription.index('=====', start)]
        self.assertIn('990.804', page)
        self.assertIn('58.371.255', page)
        at = date(2025, 10, 1)
        adequacy = design_adequacy(SNAPSHOT, groups[('§4.1.2', 'olive')], at)
        self.assertEqual(adequacy.needs, frozenset({'survey dependence model'}))
        self.assertTrue(DEPENDENCE_CAUSE)
        self.assertEqual(design_adequacy(SNAPSHOT, groups[('§4.1.3', 'olive')], at).needs,
                         frozenset({SENSITIVITY_CAUSE}))
        # A positive unit on its own reference defeats the negative claim; negatives identify no plant.
        self.assertIs(observed_support(SNAPSHOT, groups[('§4.1.2', 'olive')], at,
                                       positive_units=frozenset({'1968569'})).truth, False)
        self.assertIn(IDENTITY_CAUSE, observed_support(SNAPSHOT, groups[('§4.1.2', 'olive')], at,
                                                       positive_units=frozenset()).needs)


def held():
    from cordon_d.store import blob_path, store_root
    releases = json.loads((ROOT / 'corpus/sources/monitoring/campaign/releases.json').read_text())
    return all(blob_path(store_root(ROOT), r['sha256']).exists() for r in releases if 'sha256' in r)


@unittest.skipUnless(held(), 'the monitoring releases are not in this store')
class RealRecords(unittest.TestCase):
    """The records the plan picked by its stated rules, read by the ordinary reader."""
    WANTED = {'1968569', '1679153', '1859892', '1858945', '1858957'}

    @classmethod
    def setUpClass(cls):
        from cordon_d.monitoring import distinct_observations
        from cordon_d.plants import plant_occasions, point
        from cordon_d.spatial import positional_terms
        from cordon_d.store import store_root
        store = store_root(ROOT)
        terms = positional_terms(store)
        groups = (g for g in distinct_observations(ROOT / 'corpus/sources/monitoring') if g.reference in cls.WANTED)
        cls.found = {o.key[1]: o for o in plant_occasions(groups, start=date(2022, 9, 22), end=date(2026, 9, 22))}
        cls.place = lambda self, o, at: point(o, terms, at=at, store=store)

    def test_the_vine_qualifies_only_for_the_finding_subspecies_row_2_gives(self):
        from cordon_c.populations import post_finding_inner
        from cordon_d.plants import qualification
        almond, vine = self.found['1968569'], self.found['1679153']
        self.assertEqual(vine.labels, ('Vite europea (Vitis L.)',))
        at = almond.day
        a, v = self.place(almond, at), self.place(vine, at)
        self.assertAlmostEqual(a.geometry.distance(v.geometry), 13.04, places=2)
        for identified, pending, expected in ((frozenset({'multiplex'}), False, False),
                                              (frozenset(), True, True), (frozenset(), False, None)):
            finding = Finding(almond, identified, pending, ())
            quality = qualification(vine, finding, HOSTS)
            value = post_finding_inner(SNAPSHOT, at, v, (a,), containment=False, population_qualification=quality)
            with self.subTest(identified=identified, pending=pending):
                if vine.symptoms is True or vine.positive is True:
                    self.skipTest('the vine is symptomatic or positive: qualified whatever the subspecies')
                self.assertIs(value.truth, expected)
                if expected is None:
                    self.assertIn(SUBSPECIES_CAUSE, value.needs)

    def test_the_50_450_m_band_around_1859892(self):
        from cordon_c.populations import containment_outer
        plant = self.found['1859892']
        at = plant.day
        p = self.place(plant, at)
        for reference, grid, expected in (('1858945', 252.10, True), ('1858957', 450.41, None)):
            o = self.found[reference]
            q = self.place(o, at)
            self.assertAlmostEqual(q.geometry.distance(p.geometry), grid, places=2)
            self.assertLessEqual(o.day, at)
            value = containment_outer(SNAPSHOT, at, q, (p,), surface_qualification=HOSTS.specified(o, frozenset({'pauca'})))
            self.assertIs(value.truth, expected)

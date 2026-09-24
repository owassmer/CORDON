"""Row 12: vector-monitoring records, the next-season onset bound and vector-positive days.

Printed literals below are copied from the held publications (the CNR-IPSP letters of
1/6/26 and 8/9/26, the Osservatorio's find-site table of 11-22/04/2024, circolare 5/2023).
Geometries are plain boxes: they test the placement rule, not a real territory.
"""
from dataclasses import replace
from datetime import date
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import unittest

from pyproj import CRS
from shapely.geometry import box

from cordon_c.spatial import MetricGeometry
from cordon_d import vectors
from cordon_d.vectors import (Comune, Record, Statement, Zone, agreed, merged_rows, onset_bound, placed,
                              printed_coordinates, printed_count, printed_round, printed_window, stage_of,
                              unnamed_rounds, vector_detections, with_vector_days)
from cordon_c.core import Evaluation

ROOT = Path(__file__).resolve().parents[2]
UTM = CRS('EPSG:32633')


def record(**changes):
    base = dict(source='s' * 64, url='https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/x.pdf',
                cell='page 3 | row O41-2026 | column P. spumarius', request='r' * 64,
                publisher='CNR-IPSP', publication_date='1/6/26', protocol=None, series='OLIVETI', round=2,
                round_literal='II rilievo oliveti', site='O41-2026', agro='Crispiano',
                area=None, coordinates=(17.18937, 40.61644), coordinates_literal='40,61644 17,18937',
                window=(date(2026, 5, 25), date(2026, 5, 29)), window_literal='25-29 maggio 2026',
                method='N. individui totali x 30 unità campionarie - COTICO', species='Philaenus spumarius',
                species_literal='P. spumarius', stage='adult', stage_literal='insetti vettori adulti',
                result='53,00', count=Decimal('53.00'), test_result=None, fields=())
    base.update(changes)
    return Record(**base)


# Metric boxes standing for two comuni and a zone made of the first (EPSG:32633 metres).
INSIDE = box(690000, 4490000, 720000, 4520000)
OUTSIDE = box(730000, 4490000, 760000, 4520000)
COMUNI = {'Crispiano': Comune('073004', 'Crispiano', MetricGeometry(INSIDE, UTM, 100.0)),
          'Triggiano': Comune('072045', 'Triggiano', MetricGeometry(OUTSIDE, UTM, 100.0))}
ZONE = Zone('zone for the test', MetricGeometry(INSIDE, UTM, 10.0), frozenset({'073004'}))


def comune_of(name):
    return COMUNI.get(name)


def at(x, y):
    """Degrees of a metric point, for printed coordinates that fall inside a test box."""
    from pyproj import Transformer
    return Transformer.from_crs('EPSG:32633', 'EPSG:4326', always_xy=True).transform(x, y)


class PrintedValues(unittest.TestCase):
    def test_windows_as_the_publications_print_them(self):
        self.assertEqual(printed_window('25-29 maggio 2026'), (date(2026, 5, 25), date(2026, 5, 29)))
        self.assertEqual(printed_window('N. individui totali x 32 trappole/ha (11-25 maggio 2026)'),
                         (date(2026, 5, 11), date(2026, 5, 25)))
        self.assertEqual(printed_window('Rilievo settimanale dal 17 al 21 Agosto 2026 - OLIVETI'),
                         (date(2026, 8, 17), date(2026, 8, 21)))
        self.assertEqual(printed_window('PRIMO TURNO 11-22/04/2024'), (date(2024, 4, 11), date(2024, 4, 22)))
        self.assertEqual(printed_window('12/04/2024'), (date(2024, 4, 12), date(2024, 4, 12)))

    def test_a_period_without_a_year_takes_only_one_scoped_year(self):
        self.assertEqual(printed_window('20/02-28/02', ['2024']), (date(2024, 2, 20), date(2024, 2, 28)))
        self.assertIsNone(printed_window('20/02-28/02'))
        self.assertIsNone(printed_window('20/02-28/02', ['2023', '2024']))

    def test_rounds_are_read_from_ordinal_words_and_numerals(self):
        self.assertEqual(printed_round('Trasmissione dati I rilievo vigneti'), 1)
        self.assertEqual(printed_round('II rilievo oliveti 25-29 maggio 2026'), 2)
        self.assertEqual(printed_round('VIII rilievo oliveti'), 8)
        self.assertEqual(printed_round('QUINTO TURNO 11-22/04/2024'), 5)
        self.assertEqual(printed_round('IX comunicato'), 9)

    def test_a_round_numeral_is_not_a_stage(self):
        self.assertIsNone(stage_of('Trasmissione dati vettori II rilievo & allegati'))
        self.assertEqual(stage_of('insetti vettori adulti'), 'adult')
        self.assertEqual(stage_of('PS AD'), 'adult')
        self.assertEqual(stage_of('PS III'), 'juvenile III')
        self.assertEqual(stage_of('4° stadio giovanile'), 'juvenile 4')
        self.assertEqual(stage_of('Monitoraggio stadi giovanili'), 'juvenile')

    def test_counts_and_coordinates_as_printed(self):
        self.assertEqual(printed_count('7,00 5E; 2I*'), Decimal('7.00'))
        self.assertIsNone(printed_count('NA'))
        self.assertEqual(printed_coordinates('41.09118 16.32369'), (16.32369, 41.09118))
        self.assertEqual(printed_coordinates(latitude='40,7962957', longitude='17,1434689'), (17.1434689, 40.7962957))
        self.assertIsNone(printed_coordinates('445,4'))


class Placement(unittest.TestCase):
    def test_an_agro_listed_in_a_whole_comune_zone_is_in_it(self):
        self.assertIs(placed(record(coordinates=at(705000, 4505000)), ZONE, comune_of).truth, True)

    def test_an_agro_disjoint_from_the_zone_is_outside(self):
        self.assertIs(placed(record(agro='Triggiano', coordinates=at(745000, 4505000)), ZONE, comune_of).truth, False)

    def test_a_comune_touching_a_whole_comune_zone_but_not_listed_is_outside(self):
        touching = Comune('072030', 'Monopoli', MetricGeometry(box(720000, 4490000, 730000, 4520000), UTM, 100.0))
        answer = placed(record(agro='Monopoli', coordinates=at(725000, 4505000)), ZONE,
                        lambda name: touching if name == 'Monopoli' else None)
        self.assertIs(answer.truth, False)
        by_geometry = placed(record(agro='Monopoli', coordinates=at(725000, 4505000)), replace(ZONE, units=None),
                             lambda name: touching if name == 'Monopoli' else None)
        self.assertIsNone(by_geometry.truth)

    def test_coordinates_that_contradict_the_agro_place_nothing(self):
        answer = placed(record(coordinates=at(745000, 4505000)), ZONE, comune_of)
        self.assertIsNone(answer.truth)
        self.assertIn('printed coordinates agree with the printed agro', answer.needs)

    def test_coordinates_alone_need_a_positional_error(self):
        answer = placed(record(agro=None), ZONE, comune_of)
        self.assertEqual(answer.needs, frozenset({'positional error of the printed site coordinates'}))

    def test_an_area_name_is_never_a_zone(self):
        answer = placed(record(agro=None, coordinates=None, area='Contenimento'), ZONE, comune_of)
        self.assertEqual(answer.needs, frozenset({'place not located'}))

    def test_an_agro_that_is_not_one_comune_places_nothing(self):
        answer = placed(record(agro='Minervino'), ZONE, comune_of)
        self.assertIn('the printed agro "Minervino" as one comune', answer.needs)


class OnsetBound(unittest.TestCase):
    detection = date(2026, 2, 12)

    def bound(self, records, statements=()):
        return onset_bound(records, statements, ZONE, self.detection, comune_of, rounds=unnamed_rounds(records))

    def test_the_bound_is_the_end_of_the_earliest_adult_window_after_the_detection(self):
        early = record(coordinates=at(705000, 4505000), window=(date(2026, 5, 25), date(2026, 5, 29)))
        later = record(coordinates=at(705000, 4505000), round=8, window=(date(2026, 8, 17), date(2026, 8, 21)))
        found = self.bound([later, early])
        self.assertEqual(found.upper, date(2026, 5, 29))
        self.assertIs(found.upper_record, early)
        self.assertIsNone(found.upper_cause)

    def test_a_zero_count_is_never_an_adult_window(self):
        found = self.bound([record(result='0,00', count=Decimal('0'), coordinates=at(705000, 4505000))])
        self.assertIsNone(found.upper)
        self.assertEqual(found.upper_cause, 'no adult record placed in the zone')

    def test_a_juvenile_record_is_never_an_adult_window(self):
        found = self.bound([record(stage='juvenile III', coordinates=at(705000, 4505000))])
        self.assertIsNone(found.upper)

    def test_a_window_containing_the_detection_does_not_bound_the_next_season(self):
        found = self.bound([record(coordinates=at(705000, 4505000), window=(date(2026, 2, 10), date(2026, 2, 20)))])
        self.assertIsNone(found.upper)

    def test_a_record_outside_the_zone_supplies_nothing_and_an_unplaced_one_names_its_cause(self):
        outside = record(agro='Triggiano', coordinates=at(745000, 4505000))
        unplaced = record(agro=None, coordinates=None, area='Contenimento', window=(date(2026, 4, 1), date(2026, 4, 2)))
        found = self.bound([outside, unplaced])
        self.assertIsNone(found.upper)
        self.assertEqual(found.upper_cause, 'no adult record placed in the zone; not placed: place not located')

    def test_no_lower_bound_without_a_statement_of_adult_absence_from_the_whole_zone(self):
        juvenile = Statement('s' * 64, 'u', 'r' * 64, 'juvenile_stage', 'prossimo al 4° stadio giovanile', 'Crispiano',
                             (date(2026, 4, 15), date(2026, 4, 15)), '15 aprile 2026', 'Osservatorio', None)
        absent = replace(juvenile, kind='adults_absent')
        adult = record(coordinates=at(705000, 4505000))
        self.assertIsNone(self.bound([adult], [juvenile]).lower)
        found = self.bound([adult], [absent])
        self.assertEqual(found.lower, date(2026, 4, 15))
        self.assertIsNone(found.lower_cause)
        partial = replace(absent, place='Triggiano')
        self.assertIsNone(self.bound([adult], [partial]).lower)

    def test_unnamed_rounds_before_the_bound_are_listed_not_filled(self):
        olive = record(coordinates=at(705000, 4505000), round=2)
        olive_late = record(coordinates=at(705000, 4505000), round=8, window=(date(2026, 8, 17), date(2026, 8, 21)))
        found = self.bound([olive, olive_late])
        self.assertEqual(found.upper, date(2026, 5, 29))
        self.assertEqual(found.unnamed_rounds, ('cnr-ipsp oliveti 2026 round 1',))


class VectorPositives(unittest.TestCase):
    def test_a_placed_positive_is_passed_at_both_window_ends(self):
        positive = record(coordinates=at(705000, 4505000), test_result='positivo', count=None,
                          window=(date(2026, 8, 17), date(2026, 8, 21)))
        found = vector_detections([positive], [], ZONE, comune_of)
        self.assertEqual((found.at_start, found.at_end), ((date(2026, 8, 17),), (date(2026, 8, 21),)))
        self.assertEqual(with_vector_days((date(2025, 1, 8),), found, 'end'), (date(2025, 1, 8), date(2026, 8, 21)))

    def test_a_negative_or_a_count_is_not_a_positive(self):
        negative = record(test_result='negativo', count=None)
        found = vector_detections([negative, record()], [], ZONE, comune_of)
        self.assertEqual((found.joined, found.unjoined), ((), ()))

    def test_a_recited_positive_without_a_place_stays_unjoined(self):
        recited = Statement('s' * 64, 'u', 'r' * 64, 'vector_positive',
                            'nel monitoraggio 2022, sono stati individuati insetti vettori infetti da Xylella fastidiosa',
                            'Triggiano', None, None, 'Osservatorio', None)
        found = vector_detections([], [recited], ZONE, comune_of)
        self.assertEqual(found.unjoined, ((recited, 'place not located'),))

    def test_only_an_answer_both_ends_give_is_kept(self):
        self.assertIs(agreed(Evaluation(True), Evaluation(True)).truth, True)
        self.assertIsNone(agreed(Evaluation(True), Evaluation(False)).truth)


class TileJoin(unittest.TestCase):
    @staticmethod
    def tile(chunk, keys, header, values):
        rows = [dict(key_literal=k, cells=[dict(column='c1', literal=k), dict(column='c2', literal=v)])
                for k, v in zip(keys, values)]
        reading = dict(title_literal=None, context_literals=[], rows=rows, notes=[], issues=[],
                       columns=[dict(column='c1', header_literal='SITO', role='site_code'),
                                dict(column='c2', header_literal=header, role='count')])
        return dict(table=[0, 0, 10, 10], band=0, chunk=chunk), dict(reading=reading, request_sha256=str(chunk) * 64)

    def test_the_tiles_of_one_band_join_row_by_row(self):
        rows = list(merged_rows([self.tile(0, ['51', '55'], 'PS COTICO', ['6', '3']),
                                 self.tile(1, ['51', '55'], 'NC COTICO', ['0', '0'])]))
        self.assertEqual(len(rows), 2)
        self.assertIsNone(rows[0]['association'])
        self.assertEqual(sorted(rows[1]['cells'].values()), ['0', '3', '55', '55'])

    def test_tiles_that_disagree_stay_apart_with_the_cause(self):
        rows = list(merged_rows([self.tile(0, ['51', '55'], 'PS COTICO', ['6', '3']),
                                 self.tile(1, ['51'], 'NC COTICO', ['0'])]))
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r['association'] == 'row order differs between the tiles of one band' for r in rows))


class Cuts(unittest.TestCase):
    def test_a_cut_prefers_a_ruled_line_and_never_splits_a_word_space(self):
        import numpy
        text = numpy.ones(100, dtype=bool)
        text[40:52] = False            # a word space, 12 px
        rules = numpy.zeros(100, dtype=bool)
        self.assertIsNone(vectors._gap_cut(text, rules, 45, 0, 100))
        text[70:95] = False            # a column gutter, 25 px
        self.assertEqual(vectors._gap_cut(text, rules, 45, 0, 100), 82)
        rules[60] = True
        text[60] = False
        self.assertEqual(vectors._gap_cut(text, rules, 45, 0, 100), 60)


STORE = Path(os.environ.get('CORDON_STORE', str(ROOT.parent / 'CORDON-store')))


@unittest.skipUnless((STORE / 'derived/vector-readings').is_dir(), 'retained readings need the local store')
class RetainedReadings(unittest.TestCase):
    """Replays the retained readings of the letter of 1/6/26 against its own text layer."""

    def test_every_cell_of_the_june_letter_is_in_the_page_text(self):
        import pymupdf
        from cordon_d.store import blob_path
        population = vectors.population(ROOT, STORE)
        letter = next(p for p in population if 'II%20rilievo%20&%20allegati' in p.url)
        statements = vectors.read_statements(STORE, letter.sha256)
        pages = statements['reading']['table_pages']
        readings = [(dict(page=n), vectors.read_pdf_page(STORE, letter.sha256, n)) for n in pages]
        records = vectors.records_of(letter, readings, statements)
        with pymupdf.open(blob_path(STORE, letter.sha256)) as document:
            text = {n: ' '.join(document[n - 1].get_text().split()) for n in pages}
        self.assertTrue(records)
        for r in records:
            page = json.loads(r.cell.split(' | ')[0])['page']
            self.assertIn(r.result.split()[0] if r.result.strip() else '', text[page])
        crispiano = [r for r in records if r.site == 'O41-2026' and r.count == Decimal('53')]
        self.assertTrue(crispiano)
        self.assertEqual(crispiano[0].window, (date(2026, 5, 25), date(2026, 5, 29)))


def _pr8_available():
    try:
        return subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--verify', 'origin/d/area-versions'],
                              capture_output=True).returncode == 0 and STORE.is_dir()
    except FileNotFoundError:
        return False


@unittest.skipUnless(_pr8_available(), 'the Annex III zone is read with PR #8 branch code and the local store')
class AnnexIIIZone(unittest.TestCase):
    """Z for DET 2/2024: the Annex III infected zone A holds on 15/12/2023, read with PR #8's code."""

    def test_fasano_is_in_z_and_triggiano_and_monopoli_are_not(self):
        import tempfile
        import sys
        with tempfile.TemporaryDirectory() as directory:
            archive = subprocess.run(['git', '-C', str(ROOT), 'archive', 'origin/d/area-versions',
                                      'regulation/stage-d/cordon_d', 'corpus/sources/areas/geometry.json',
                                      'regulation/stage-a/annex-versions.csv', 'regulation/source/consolidations',
                                      'regulation/stage-b'], capture_output=True, check=True).stdout
            subprocess.run(['tar', '-x', '-C', directory], input=archive, check=True)
            package = Path(directory) / 'regulation/stage-d'
            (package / 'cordon_d').rename(package / 'pr8_cordon_d')
            sys.path.insert(0, str(package))
            try:
                from pr8_cordon_d.administrative import AdministrativeUnits
                from pr8_cordon_d.area_geometry import Sources
                os.environ.setdefault('CORDON_STORE', str(STORE))
                units, sources = AdministrativeUnits(Path(directory)), Sources(Path(directory))
                listed = {c.istat for c in sources.annex_iii_comuni(date(2023, 12, 15))}
                self.assertIn(units.comune(name='Fasano', region='Puglia').istat, listed)
                self.assertNotIn(units.comune(name='Triggiano', region='Puglia').istat, listed)
                self.assertNotIn(units.comune(name='Monopoli', region='Puglia').istat, listed)
            finally:
                sys.path.remove(str(package))
                for name in [m for m in sys.modules if m.startswith('pr8_cordon_d')]:
                    del sys.modules[name]


if __name__ == '__main__':
    unittest.main()

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

    def test_the_contradiction_takes_the_comune_s_sourced_error_and_none_where_none_is_sourced(self):
        # A point 6 km outside its printed agro (O31 "Martina Franca", whose point lies in Noci) is a
        # contradiction unless the comune's own sourced boundary error reaches it.
        point = record(coordinates=at(726000, 4505000))
        for error, placed_in in ((0.0, None), (100.0, None), (7000.0, True)):
            comune = Comune('073004', 'Crispiano', MetricGeometry(INSIDE, UTM, error))
            answer = placed(point, ZONE, lambda name: comune)
            self.assertIs(answer.truth, placed_in, error)
        unsourced = Comune('073004', 'Crispiano', MetricGeometry(INSIDE, UTM, 0.0))
        self.assertIs(placed(record(coordinates=at(705000, 4505000)), ZONE, lambda name: unsourced).truth, True)
        self.assertIn('printed coordinates agree with the printed agro',
                      placed(record(coordinates=at(720050, 4505000)), ZONE, lambda name: unsourced).needs)

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
        self.assertEqual(found.upper_cause, 'no adult record placed in the zone in the 2026 season, the first whose rounds follow the detection')

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
        self.assertEqual(found.upper_cause, 'no adult record placed in the zone in the 2026 season, the first whose rounds follow the detection; not placed: place not located')

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

    def test_a_detection_before_a_season_with_no_placed_adult_takes_no_bound_from_the_season_after(self):
        # DET 9/2025: detection 27/11/2024; the 2025 season places no adult in Z; 2026 does.
        det = date(2024, 11, 27)
        summer = record(coordinates=at(705000, 4505000), round=10, window=(date(2024, 7, 16), date(2024, 7, 25)))
        gap = record(agro='Triggiano', coordinates=at(745000, 4505000), publisher=None, series='mandorlo', round=10,
                     window=(date(2025, 1, 1), date(2025, 7, 18)))
        after = record(coordinates=at(705000, 4505000), window=(date(2026, 5, 25), date(2026, 5, 29)))
        later = vectors.Round('s' * 64, 'u', ('dati2026', 'oliveti', 2026), 'VIII rilievo oliveti', 8,
                              date(2026, 8, 17), date(2026, 8, 21), 'adult', False)
        records = [summer, gap, after]
        found = onset_bound(records, [], ZONE, det, comune_of, rounds=unnamed_rounds(records), untranscribed=[later])
        self.assertIsNone(found.upper)
        self.assertEqual(found.season, 2025)
        self.assertIn('in the 2025 season, the first whose rounds follow the detection', found.upper_cause)
        self.assertEqual(found.unnamed_rounds, tuple(f'publisher not printed mandorlo 2025 round {n}' for n in range(1, 10)))
        self.assertEqual(found.untranscribed_rounds, ())
        self.assertEqual(vectors.next_season(records, [later], date(2025, 12, 1)), 2026)
        self.assertEqual(onset_bound(records, [], ZONE, date(2025, 12, 1), comune_of).upper, date(2026, 5, 29))

    def test_a_detection_before_its_own_season_s_rounds_takes_that_season_and_lists_what_is_untranscribed(self):
        # DET 20/2023: detection 14/02/2023; the 2023 composite dates its counts 01/01-14/06 (no window
        # beginning after the detection) and the 2023 round II is acquired, not transcribed.
        det = date(2023, 2, 14)
        composite = record(coordinates=None, publisher=None, series=None, round=6,
                           window=(date(2023, 1, 1), date(2023, 6, 14)))
        next_year = record(coordinates=None, publisher=None, series=None, round=1,
                           window=(date(2024, 4, 11), date(2024, 4, 22)))
        second = vectors.Round('s' * 64, 'u', ('dati2023', '', 2023), 'BARI II 2023', 2, None, date(2023, 6, 26),
                               None, False)
        found = onset_bound([composite, next_year], [], ZONE, det, comune_of, untranscribed=[second])
        self.assertIsNone(found.upper)
        self.assertEqual(found.season, 2023)
        self.assertIn('in the 2023 season', found.upper_cause)
        self.assertEqual(found.untranscribed_rounds, (second.name,))
        self.assertEqual(onset_bound([next_year], [], ZONE, date(2023, 12, 15), comune_of).upper, date(2024, 4, 22))

    def test_no_round_after_the_detection_is_its_own_cause(self):
        found = self.bound([record(coordinates=at(705000, 4505000), window=(date(2025, 5, 25), date(2025, 5, 29)))])
        self.assertIsNone(found.season)
        self.assertIn('no round held after the detection', found.upper_cause)

    def test_unnamed_rounds_before_the_bound_are_listed_not_filled(self):
        olive = record(coordinates=at(705000, 4505000), round=2)
        olive_late = record(coordinates=at(705000, 4505000), round=8, window=(date(2026, 8, 17), date(2026, 8, 21)))
        found = self.bound([olive, olive_late])
        self.assertEqual(found.upper, date(2026, 5, 29))
        self.assertEqual(found.unnamed_rounds, ('cnr ipsp oliveti 2026 round 1',))


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
        self.assertEqual(found.unjoined, ((recited, 'place not located, window not printed'),))

    def test_a_recited_positive_s_printed_agro_goes_through_the_place_test(self):
        quote = 'nel monitoraggio 2022, sono stati individuati insetti vettori infetti nell\u2019agro di Crispiano (TA)'
        recited = Statement('s' * 64, 'u', 'r' * 64, 'vector_positive', quote, 'agro di Crispiano',
                            (date(2022, 10, 3), date(2022, 10, 7)), '3-7 ottobre 2022', 'Osservatorio', None)
        self.assertEqual(vectors.statement_agro(recited), 'Crispiano')
        found = vector_detections([], [recited], ZONE, comune_of)
        self.assertEqual((found.at_start, found.at_end, found.unjoined), ((date(2022, 10, 3),), (date(2022, 10, 7),), ()))
        undated = replace(recited, day=None, date_literal='2022')
        self.assertEqual(vector_detections([], [undated], ZONE, comune_of).unjoined, ((undated, 'window not printed'),))
        elsewhere = replace(recited, quote=quote.replace('Crispiano', 'Triggiano'), place='agro di Triggiano')
        self.assertEqual(vector_detections([], [elsewhere], ZONE, comune_of).unjoined, ())
        around = replace(recited, quote='n. 12 Philaenus spumarius catturati nell\u2019area circostante il sito di Crispiano',
                         place='nell\u2019area circostante il sito di Crispiano')
        self.assertIsNone(vectors.statement_agro(around))
        self.assertEqual(vector_detections([], [around], ZONE, comune_of).unjoined, ((around, 'place not located'),))
        unread = replace(recited, quote='insetti vettori positivi \u015d\u0176 \u0102\u0150\u0192\u017d')
        self.assertIsNone(vectors.statement_agro(unread))  # a place literal the quote does not print is not read

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


class TransmissionText(unittest.TestCase):
    """What a CNR letter prints in its body reaches the records of its tables."""

    TEXT = ('\nPHYSICAL PAGE 1\ncon la presente si trasmettono i dati del monitoraggio degli insetti vettori '
            'adulti effettuato: a) negli oliveti')

    def statements(self, *items, text=''):
        return {'request_sha256': 'q' * 64, 'request': {'prompt': 'PROMPT' + self.TEXT + text},
                'reading': {'identity': {'publisher': 'CNR-IPSP (Sede di Bari)', 'kind': 'letter', 'number': None,
                                         'date': '1/6/26', 'protocol': None, 'signers': []},
                            'series': [{'series_literal': 'oliveti', 'round_literal': 'II rilievo',
                                        'window_literal': '25-29 maggio 2026', 'quote': 'II rilievo oliveti'}],
                            'statements': list(items), 'table_pages': [3], 'issues': []}}

    ADULTS = {'kind': 'other', 'quote': 'con la presente si trasmettono i dati del monitoraggio degli insetti vettori adulti',
              'place_literal': None, 'date_literal': None, 'species_literal': None, 'stage_literal': 'adulti'}

    def page(self, number, keys):
        reading = {'title_literal': 'Rilievo settimana del 25-29 maggio 2026 OLIVETI', 'context_literals': [],
                   'columns': [dict(column='c1', header_literal='SITO', role='site_code', **self.NONE),
                               dict(column='c2', header_literal='N. individui / P. spumarius', role='count',
                                    **dict(self.NONE, species_literal='P. spumarius', round_literal='Rilievo',
                                           series_literal='OLIVETI'))],
                   'rows': [{'key_literal': k, 'cells': [{'column': 'c1', 'literal': k}, {'column': 'c2', 'literal': '2,00'}]}
                            for k in keys], 'notes': [], 'issues': []}
        return {'page': number}, {'request_sha256': str(number) * 64, 'reading': reading}

    NONE = dict(species=None, species_literal=None, stage_literal=None, method_literal=None, units_literal=None,
                window_literal=None, round_literal=None, series_literal=None)

    def publication(self):
        return vectors.Publication('https://x/Trasmissione.pdf', 'b' * 64, 'pdf', 'front page', None, 'records.json')

    def test_the_stage_the_letter_states_for_its_data_reaches_its_records(self):
        found = vectors.records_of(self.publication(), [self.page(3, ['O31'])], self.statements(self.ADULTS))
        self.assertEqual({(r.stage, r.round) for r in found}, {('adult', 2)})
        self.assertIn('(transmission text)', found[0].stage_literal)

    def test_a_stage_the_text_does_not_print_or_two_stages_give_none(self):
        unprinted = dict(self.ADULTS, quote='i dati degli insetti vettori adulti raccolti altrove')
        self.assertEqual(vectors.transmission_stage(self.statements(unprinted)), (None, None))
        juvenile = dict(self.ADULTS, quote='i dati degli stadi giovanili', stage_literal='stadi giovanili')
        both = self.statements(self.ADULTS, juvenile, text=' e i dati degli stadi giovanili')
        self.assertEqual(vectors.transmission_stage(both), (None, None))

    def test_each_pdf_page_is_its_own_table(self):
        found = vectors.records_of(self.publication(), [self.page(3, ['O31', 'O33']), self.page(4, ['O40'])],
                                   self.statements(self.ADULTS))
        self.assertEqual(sorted(r.site for r in found), ['O31', 'O33', 'O40'])
        self.assertFalse(any('row order differs' in r.cell for r in found))
        self.assertEqual({r.site: r.request[0] for r in found}, {'O31': '3', 'O33': '3', 'O40': '4'})

    def test_trap_records_take_the_exposure_from_installation_to_collection(self):
        text = (' b) nei vigneti, in questo caso i dati riguardano l\u2019ispezione delle trappole installate nei '
                'giorni 20-24 luglio, ed i dati riguardanti gli sfalci')
        statements = self.statements(self.ADULTS, text=text)
        self.assertEqual(vectors.trap_installation(statements, 2026)[0], date(2026, 7, 20))
        publication = vectors.Publication('https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2026/T.pdf',
                                          'b' * 64, 'pdf', 'front page', None, 'records.json')
        number, response = self.page(3, ['V1'])
        reading = response['reading']
        reading['title_literal'] = 'Rilievo settimana dal 17 al 21 Agosto 2026 - VIGNETI'
        reading['columns'][1] = dict(reading['columns'][1], method_literal='N. individui totali x 32 trappole/ha')
        traps, = vectors.records_of(publication, [(number, response)], statements)
        self.assertEqual(traps.window, (date(2026, 7, 20), date(2026, 8, 21)))
        self.assertIn('trappole installate nei giorni 20-24 luglio', traps.window_literal)
        reading['columns'][1] = dict(reading['columns'][1], method_literal='N. individui x 30 unita campionarie COTICO')
        sweeps, = vectors.records_of(publication, [(number, response)], statements)
        self.assertEqual(sweeps.window, (date(2026, 8, 17), date(2026, 8, 21)))
        may = self.statements(self.ADULTS, text=' trappole installate nei giorni 11 e 12 maggio')
        self.assertEqual(vectors.trap_installation(may, 2026)[0], date(2026, 5, 11))

    def test_one_publisher_printed_with_different_punctuation_is_one_series(self):
        first = record(publisher='CNR-IPSP (Sede di Bari)', round=2)
        second = record(publisher='CNR-IPSP – Sede di Bari', round=8)
        self.assertEqual(vectors._series(first), vectors._series(second))


class ScopedReading(unittest.TestCase):
    """What is read is what the consumers read: rounds dated from held words, read in order and no further."""

    def publication(self, name, modified='Wed, 24 Apr 2024 10:00:00 GMT', link=None, kind='image'):
        named = 'front page' + (f' (link text: {link})' if link else '')
        return vectors.Publication(f'https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2024/{name}',
                                   'c' * 64, kind, named, modified, 'records.json')

    def test_rounds_are_dated_from_file_names_titles_and_server_dates(self):
        r, = vectors.rounds_of(self.publication('Monitoraggio_adulti_04_06_12_06_2024.jpg'))
        self.assertEqual((r.start, r.end, r.stage), (date(2024, 6, 4), date(2024, 6, 12), 'adult'))
        r, = vectors.rounds_of(self.publication('Area_BAT_al_20240422.jpg', link='BAT'))
        self.assertEqual((r.start, r.end, r.stage), (None, date(2024, 4, 22), None))
        r, = vectors.rounds_of(self.publication('Siti_ritrovamento_stadi_giovanili_11_22_04_2024.jpg'))
        self.assertEqual((r.start, r.end, r.stage, r.find_sites), (date(2024, 4, 11), date(2024, 4, 22), 'juvenile', True))
        r, = vectors.rounds_of(self.publication('Monitoraggio_adulti_11_22_04_2024.jpg'),
                               layout={'tables': [{'title_literal': 'DATI PRIMO TURNO 11-22_04_2024'}]})
        self.assertEqual((r.number, r.season), (1, ('dati2024', '', 2024)))

    def test_a_round_only_numbered_ends_at_the_latest_on_its_server_date(self):
        publication = replace(self.publication('BARI_II_2023.jpg', modified='Mon, 26 Jun 2023 08:00:00 GMT'),
                              url='https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2023/BARI_II_2023.jpg')
        r, = vectors.rounds_of(publication)
        self.assertEqual((r.number, r.start, r.end), (2, None, date(2023, 6, 26)))

    def test_a_document_outside_the_monitoring_folders_carries_no_round(self):
        act = vectors.Publication('https://burp.regione.puglia.it/x.pdf', 'd' * 64, 'pdf', 'held removal order', None, 'o')
        self.assertEqual(vectors.rounds_of(act), ())

    def test_a_window_its_publication_rules_out_is_a_reading_limit_not_a_date(self):
        publication = replace(self.publication('Bari_est_IX_comunicato.jpg', modified='Wed, 09 Nov 2022 10:00:00 GMT'),
                              url='https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2022/Bari_est_IX_comunicato.jpg')
        self.assertIn('survey year 2022', vectors.window_issue((date(2002, 9, 26), date(2002, 9, 26)), publication))
        self.assertIn('ends after', vectors.window_issue((date(2022, 11, 14), date(2022, 11, 14)), publication))
        self.assertIsNone(vectors.window_issue((date(2022, 9, 26), date(2022, 9, 26)), publication))

    def test_a_scoped_tile_joins_the_place_tile_of_its_band_by_row_number(self):
        none = TransmissionText.NONE
        place = {'title_literal': None, 'context_literals': [], 'row_count': 3, 'notes': [], 'issues': [],
                 'columns': [dict(column='c1', header_literal='SITO', role='site_code', **none),
                             dict(column='c2', header_literal='AGRO', role='agro', **none)],
                 'rows': [{'row_number': n, 'key_literal': 'I TURNO', 'cells': [
                     {'column': 'c1', 'literal': site}, {'column': 'c2', 'literal': agro}]}
                     for n, site, agro in ((1, '3', 'Fasano'), (2, '51', 'Triggiano'), (3, '22', 'Monopoli'))]}
        counts = {'title_literal': None, 'context_literals': [], 'row_count': 3, 'notes': [], 'issues': [],
                  'columns': [dict(column='c1', header_literal='PS COTICO', role='count', **none)],
                  'rows': [{'row_number': 2, 'key_literal': 'I TURNO', 'cells': [{'column': 'c1', 'literal': '4'}]}]}
        geometry = dict(table=[0, 0, 5000, 900], header=[0, 50], key=[0, 500], band=0)
        rows = list(vectors.merged_rows([(dict(geometry, chunk=0), {'request_sha256': 'a' * 64, 'reading': place}),
                                         (dict(geometry, chunk=1), {'request_sha256': 'b' * 64, 'reading': counts})]))
        joined = [r for r in rows if any(v == '4' for v in r['cells'].values())]
        self.assertEqual(len(joined), 1)
        self.assertEqual(sorted(joined[0]['cells'].values()), ['4', '51', 'Triggiano'])
        self.assertIsNone(joined[0]['association'])
        short = dict(counts, row_count=2)
        rows = list(vectors.merged_rows([(dict(geometry, chunk=0), {'request_sha256': 'a' * 64, 'reading': place}),
                                         (dict(geometry, chunk=1), {'request_sha256': 'b' * 64, 'reading': short})]))
        self.assertTrue(all(r['association'] for r in rows))

    def test_the_printed_row_count_counts_ruled_and_shaded_rows(self):
        import numpy

        class Pixels:
            pixels = numpy.full((200, 100, 3), 255, dtype=numpy.uint8)
        for y in range(0, 200, 20):
            Pixels.pixels[y, :] = 0                       # a rule above every row
        Pixels.pixels[101:139, :] = (255, 200, 150)       # two shaded rows
        for y in range(5, 200, 20):
            Pixels.pixels[y:y + 8, 10:30] = 0              # one key per row
        self.assertEqual(vectors.printed_row_count(Pixels, dict(key=[0, 100], body=[0, 0, 100, 200], header=[0, 0])), 10)

    def test_a_zone_without_a_located_adult_keeps_the_season_open(self):
        adult = record(stage='adult', count=Decimal('2'), coordinates=None)
        zero = record(stage='adult', count=Decimal('0'), agro='Triggiano', coordinates=None)
        other = Zone('other zone', MetricGeometry(OUTSIDE, UTM, 10.0), frozenset({'072045'}))
        self.assertEqual(vectors.zones_without_adult([adult, zero], [ZONE, other], comune_of), ('other zone',))
        self.assertEqual(vectors.zones_without_adult([adult], [ZONE], comune_of), ())

    def test_an_untranscribed_round_that_could_precede_the_bound_is_listed_beside_it(self):
        adult = record(stage='adult', count=Decimal('2'), coordinates=None, window=(date(2026, 5, 25), date(2026, 5, 29)))
        season = ('dati2026', 'oliveti', 2026)
        before = vectors.Round('s' * 64, 'u', season, 'I rilievo oliveti', 1, None, date(2026, 5, 20), 'adult', False)
        after = vectors.Round('s' * 64, 'u', season, 'VIII rilievo oliveti', 8, date(2026, 8, 17), date(2026, 8, 21),
                              'adult', False)
        found = onset_bound([adult], [], ZONE, date(2026, 2, 12), comune_of, untranscribed=[before, after])
        self.assertEqual(found.upper, date(2026, 5, 29))
        self.assertEqual(found.untranscribed_rounds, (before.name,))

    def test_a_missing_round_an_untranscribed_table_prints_is_untranscribed_not_unnamed(self):
        # 2024: round 1 and round 5 are held; the area table of 25/07/2024 prints ten survey periods.
        first = record(agro='Triggiano', coordinates=None, publisher=None, series=None, round=1,
                       window=(date(2024, 4, 11), date(2024, 4, 22)))
        fifth = replace(first, round=5, window=(date(2024, 5, 15), date(2024, 5, 22)))
        area = vectors.Round('s' * 64, 'u', ('dati2024', '', 2024), 'Bari | Area Bari al 20240725', None, None,
                             date(2024, 7, 25), None, False, periods=10)
        found = onset_bound([first, fifth], [], ZONE, date(2024, 1, 10), comune_of,
                            rounds=unnamed_rounds([first, fifth]), untranscribed=[area])
        self.assertEqual(found.unnamed_rounds, ())
        self.assertIn('publisher not printed series not printed 2024 round 3: acquired, not transcribed '
                      '(printed in Bari | Area Bari al 20240725, 10 survey periods)', found.untranscribed_rounds)
        alone = onset_bound([first, fifth], [], ZONE, date(2024, 1, 10), comune_of, rounds=unnamed_rounds([first, fifth]))
        self.assertEqual(len(alone.unnamed_rounds), 3)

    def test_a_header_reading_names_its_periods_rounds_and_any_test_column(self):
        column = dict(stage_literal=None, window_literal=None, round_literal=None, units_literal=None)
        reading = {'issues': [], 'tables': [
            {'table': 1, 'title_literal': None, 'notes': [], 'period_row_keys': ['11apr-19apr', '20apr-8mag'],
             'columns': [dict(column, header_literal='% cotico erboso', role='share')]},
            {'table': 2, 'title_literal': None, 'notes': [], 'period_row_keys': [],
             'columns': [dict(column, header_literal='Presenza adulti QUINTO TURNO', role='other'),
                         dict(column, header_literal='N. positivi a X. fastidiosa', role='count')]}]}
        self.assertEqual(vectors.printed_periods(reading), (2, (5,)))
        self.assertEqual([c['header_literal'] for c in vectors.test_columns(reading)], ['N. positivi a X. fastidiosa'])

    def test_a_publication_that_prints_no_stage_yields_no_adult_window(self):
        publication = self.publication('Bari_est_IX_comunicato.jpg')
        reading = {'title_literal': None, 'context_literals': [], 'columns': [
            dict(column='c1', header_literal='olivo', role='count', **TransmissionText.NONE)]}
        self.assertFalse(vectors.prints_stage(publication, [({}, {'reading': reading})]))
        adults = self.publication('Siti_ritrovamento_adulti_11_22_04_2024.jpg')
        self.assertTrue(vectors.prints_stage(adults, [({}, {'reading': reading})]))

    def test_a_table_that_prints_no_window_for_its_counts_yields_no_adult_window(self):
        none = TransmissionText.NONE
        turno = {'title_literal': None, 'context_literals': [], 'columns': [
            dict(column='c1', header_literal='SITO', role='site_code', **none),
            dict(column='c2', header_literal='Presenza adulti SESTO TURNO', role='count',
                 **dict(none, stage_literal='adulti'))]}
        self.assertFalse(vectors.prints_window([({}, {'reading': turno})]))
        dated = dict(turno, columns=turno['columns'] + [dict(column='c3', header_literal='DATA', role='date', **none)])
        self.assertTrue(vectors.prints_window([({}, {'reading': dated})]))
        cut = dict(turno, columns=[dict(c, window_literal='SETTIM') for c in turno['columns']])
        self.assertFalse(vectors.prints_window([({}, {'reading': cut})]))

    def test_a_count_without_a_printed_window_is_dated_by_its_publication_not_dropped(self):
        composite = replace(self.publication('dati_del_monitoraggio_vettori_aggiornati_al_14_giugno_2023.jpg',
                                             modified='Mon, 26 Jun 2023 08:00:00 GMT'),
                            url='https://cartografia.sit.puglia.it/doc/xylella/vettori/dati2023/'
                                'dati_del_monitoraggio_vettori_aggiornati_al_14_giugno_2023.jpg')
        none = TransmissionText.NONE
        reading = {'title_literal': None, 'context_literals': [], 'row_count': 1, 'notes': [], 'issues': [],
                   'columns': [dict(column='c1', header_literal='SITO', role='site_code', **none),
                               dict(column='c2', header_literal='Agro', role='agro', **none),
                               dict(column='c3', header_literal='Presenza adulti SESTO TURNO', role='count',
                                    **dict(none, stage_literal='adulti'))],
                   'rows': [{'row_number': 1, 'key_literal': '2', 'cells': [
                       {'column': 'c1', 'literal': '2'}, {'column': 'c2', 'literal': 'Crispiano'},
                       {'column': 'c3', 'literal': '1'}]}]}
        found, = vectors.records_of(composite, [(dict(table=[0, 0, 9, 9], band=0, chunk=0),
                                                 {'request_sha256': 'e' * 64, 'reading': reading})])
        self.assertEqual((found.stage, found.window), ('adult', (date(2023, 1, 1), date(2023, 6, 14))))
        self.assertIn('no window printed', found.window_literal)
        bound = onset_bound([replace(found, coordinates=None)], [], ZONE, date(2022, 12, 15), comune_of)
        self.assertEqual(bound.upper, date(2023, 6, 14))
        self.assertIsNone(onset_bound([replace(found, coordinates=None)], [], ZONE, date(2023, 2, 1), comune_of).upper)

    def test_a_tile_that_prefixes_the_area_to_the_site_key_gives_the_same_key(self):
        self.assertTrue(vectors._same_key(['2', 'contenimento 2']))
        self.assertFalse(vectors._same_key(['2', 'contenimento 12']))
        self.assertFalse(vectors._same_key(['O31', 'O33']))


STORE_BLOB = STORE / 'blobs/sha256/b7/b7d9f757e0ca6f300d6a574bd0bd86f6b66390e45607adcc44cda8782bbc2ff0'


@unittest.skipUnless(STORE_BLOB.exists() and (STORE / 'derived/vector-readings').is_dir(),
                     'the held letter and its retained readings need the local store')
class PdfTextLayer(unittest.TestCase):
    """The CNR letter of 1/6/26 read from its text layer agrees with its retained page reading, cell by cell."""

    DIGEST = 'b7d9f757e0ca6f300d6a574bd0bd86f6b66390e45607adcc44cda8782bbc2ff0'

    def test_every_cell_of_the_olive_pages_matches_the_page_reading(self):
        for number in (3, 4):
            mine = vectors.pdf_text_table(STORE, self.DIGEST, number)
            model = vectors.read_pdf_page(STORE, self.DIGEST, number)['reading']
            self.assertEqual([c['role'] for c in mine['columns']], [c['role'] for c in model['columns']])
            self.assertEqual({r['key_literal']: [c['literal'] for c in r['cells']] for r in mine['rows']},
                             {r['key_literal']: [c['literal'] for c in r['cells']] for r in model['rows']})

    def test_a_page_whose_annotations_wrap_goes_to_a_model_page_read(self):
        self.assertIsNone(vectors.pdf_text_table(STORE, self.DIGEST, 5))
        self.assertEqual(vectors.read_pdf_table(STORE, self.DIGEST, 5)['request']['task'], 'table')


class Transport(unittest.TestCase):
    """A subscription or transport failure stops the pass; it is never a reading limit of the source."""

    SESSION = json.dumps({'type': 'result', 'subtype': 'success', 'is_error': True,
                          'result': "You've hit your session limit · resets 4:50pm (America/New_York)"})

    def test_a_session_limit_is_a_usage_limit_not_a_reading_limit(self):
        reading, error = vectors.failure_of(1, self.SESSION, '')
        self.assertIsNone(reading)
        self.assertIsInstance(error, vectors.UsageLimit)
        self.assertIsInstance(error, vectors.TransportFailure)

    def test_no_envelope_or_an_api_error_is_a_transport_failure(self):
        self.assertIsInstance(vectors.failure_of(1, '', 'connection reset')[1], vectors.TransportFailure)
        api = json.dumps({'subtype': 'success', 'is_error': True, 'result': 'API Error: 500 Internal server error'})
        self.assertIsInstance(vectors.failure_of(1, api, '')[1], vectors.TransportFailure)

    def test_a_reading_the_model_could_not_conform_stays_a_reading_limit(self):
        retries = json.dumps({'subtype': 'error_max_structured_output_retries', 'is_error': True, 'result': ''})
        error = vectors.failure_of(1, retries, '')[1]
        self.assertNotIsInstance(error, vectors.TransportFailure)
        ok = json.dumps({'subtype': 'success', 'is_error': False, 'structured_output': {'rows': []}})
        self.assertEqual(vectors.failure_of(0, ok, ''), ({'rows': []}, None))

    def test_a_usage_limit_retains_nothing_and_later_replays_nothing(self):
        import tempfile
        from unittest import mock
        schema = {'type': 'object'}
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory)
            with mock.patch.object(vectors, '_dispatch', side_effect=vectors.UsageLimit('session limit')):
                with self.assertRaises(vectors.UsageLimit):
                    vectors.retained(store, 'table', ['a' * 64], 'p', schema, execute=True)
            self.assertEqual(list((store / 'derived/vector-readings').glob('*.json')), [])
            with mock.patch.object(vectors, '_dispatch', return_value={'rows': []}):
                first = vectors.retained(store, 'table', ['a' * 64], 'p', schema, execute=True)
            self.assertEqual(vectors.retained(store, 'table', ['a' * 64], 'p', schema), first)

    def test_stale_locks_are_cleared_and_a_held_one_is_kept(self):
        import fcntl
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory)
            folder = store / 'derived/vector-readings'
            folder.mkdir(parents=True)
            (folder / 'stale.lock').touch()
            (folder / 'partial.tmp').touch()
            (folder / 'kept.json').write_text('{}')
            with (folder / 'held.lock').open('a') as held:
                fcntl.flock(held, fcntl.LOCK_EX)
                self.assertEqual(vectors.clear_stale_locks(store), 1)
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ['held.lock', 'kept.json'])


if __name__ == '__main__':
    unittest.main()

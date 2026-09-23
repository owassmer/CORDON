"""Two general reader rules: coordinates compare at the precision the report prints, and a
result printed in a table heading applies to the rows beneath it that print none."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from cordon_d.findings import _coordinate_relation
from cordon_d.reports import (Report, Result, Row, apply_table_headings, heading_above, heading_result,
                              table_headings)


def printed(latitude, longitude):
    return SimpleNamespace(cells=[{'role': 'latitude', 'text': latitude}, {'role': 'longitude', 'text': longitude}])


def association(latitude, longitude):
    return {'fields': {'latitude': {'text': latitude}, 'longitude': {'text': longitude}}}


class PrintedPrecision(unittest.TestCase):
    def test_extra_decimals_in_the_monitoring_record_are_not_a_conflict(self):
        # 82F/2024 prints six and seven decimals; the monitoring record prints eight.
        self.assertEqual(_coordinate_relation(printed('41,048155', '16,9457767'),
                                              association('41.04815495', '16.9457767')),
                         'agrees at printed decimal precision')

    def test_a_disagreement_at_the_printed_precision_stays_a_conflict(self):
        # 68F/2024 prints 16.94561750 where the monitoring record holds 16.94456175.
        self.assertEqual(_coordinate_relation(printed('41.05335918', '16.94561750'),
                                              association('41.05335918', '16.94456175')), 'conflicts')

    def test_printed_trailing_zeros_are_printed_decimals(self):
        self.assertEqual(_coordinate_relation(printed('41.05968000', '16.95026136'),
                                              association('41.05968065', '16.95026136')), 'conflicts')

    def test_an_association_printing_fewer_decimals_sets_the_comparison(self):
        self.assertEqual(_coordinate_relation(printed('41.0597240941', '16.9507981716'),
                                              association('41.05972409', '16.95079817')),
                         'agrees at printed decimal precision')

    def test_an_integer_coordinate_on_either_side_is_unresolved(self):
        self.assertEqual(_coordinate_relation(printed('41', '16.9'), association('41.05', '16.94')), 'unresolved')
        self.assertEqual(_coordinate_relation(printed('41.05', '16.94'), association('41', '16.94')), 'unresolved')


def row(locator, results=(), cells=()):
    return Row(locator, int(locator.split('/')[0][1:]), None, None, (), tuple(cells), tuple(results), ())


def reading(rows, facts=()):
    return Report('d' * 64, 'v', 2, tuple(rows), tuple(facts), (), frozenset({1, 2}))


class HeadingResults(unittest.TestCase):
    HEADING = 'Rapporto di prova n. 9, rettifica del Rapporto di prova n.4. - Positivi/ IAMB – 7 settembre 2023'

    def test_a_heading_prints_one_result_in_any_gender_or_number(self):
        self.assertEqual(heading_result(self.HEADING), ('Positivi', 'positive'))
        self.assertEqual(heading_result('Campioni non rilevati'), ('non rilevati', 'not-detected'))
        self.assertEqual(heading_result('Esito dei campioni singoli negative'), ('negative', 'negative'))

    def test_a_heading_without_one_result_states_none(self):
        self.assertIsNone(heading_result('Positivi e negativi'))
        self.assertIsNone(heading_result('Si allega alla presente'))
        self.assertIsNone(heading_result('Sintomo assente'))
        self.assertIsNone(heading_result('Rapporto di prova n. 9'))

    def test_the_heading_is_the_text_nearest_above_the_table_below_any_table_above_it(self):
        blocks = [(16.0, 35.0, 'Letterhead\n'), (57.1, 70.4, self.HEADING + ' \n'), (79.8, 91.8, ' \n'),
                  (107.9, 128.2, 'Id \nData \n')]
        self.assertEqual(heading_above(blocks, (24.8, 99.6, 723.0, 172.7), []), self.HEADING)
        self.assertIsNone(heading_above(blocks, (24.8, 99.6, 723.0, 172.7), [(24.8, 75.0, 723.0, 95.0)]))

    def test_the_heading_result_fills_only_rows_that_print_no_result(self):
        own = Result('p2/p2-t1/r2/c9', ('Esito',), None, None, 'Negativo', 'negative', None, ())
        read = apply_table_headings(reading([row('p2/p2-t1/r1'), row('p2/p2-t1/r2', [own])]),
                                    {'p2-t1': (2, self.HEADING)})
        first, second = read.rows
        self.assertEqual([(r.text, r.kind) for r in first.results], [('Positivi', 'positive')])
        self.assertEqual(first.results[0].support[0]['text'], self.HEADING)
        self.assertEqual(first.results[0].support[0]['basis'], 'printed table heading')
        self.assertEqual(second.results, (own,))

    def test_a_continued_record_takes_its_result_from_its_other_part(self):
        facts = [{'role': 'record_continuation', 'applies_to': ['p2-t1/r1', 'p3-t1/r1']}]
        read = apply_table_headings(reading([row('p2/p2-t1/r1')], facts), {'p2-t1': (2, self.HEADING)})
        self.assertEqual(read.rows[0].results, ())

    def test_a_heading_on_another_page_or_table_does_not_reach_the_row(self):
        read = apply_table_headings(reading([row('p2/p2-t1/r1')]), {'p2-t1': (3, self.HEADING), 'p2-t2': (2, self.HEADING)})
        self.assertEqual(read.rows[0].results, ())

    def test_the_heading_is_read_from_the_page_text_above_the_table_region(self):
        import pymupdf
        with TemporaryDirectory() as directory:
            source = Path(directory) / 'report.pdf'
            with pymupdf.open() as document:
                document.new_page()
                page = document.new_page()
                page.insert_text((30, 60), 'Rapporto di prova n. 9 - Positivi/ IAMB', fontsize=11)
                page.insert_text((30, 120), '1598862  07/09/2023', fontsize=11)
                document.save(source)
            payload = {'blocks': [{'native_regions': [{'id': 'p2-native-t1', 'page': 2, 'bbox': [24, 99, 700, 170]}],
                                   'reading': {'pages': [{'page': 2, 'regions': [
                                       {'native_table': 'p2-native-t1', 'disposition': 'represented',
                                        'output_tables': ['p2-t1']}]}]}}]}
            headings = table_headings(reading([row('p2/p2-t1/r1')]), payload, source)
        self.assertEqual(headings, {'p2-t1': (2, 'Rapporto di prova n. 9 - Positivi/ IAMB')})


if __name__ == '__main__':
    unittest.main()

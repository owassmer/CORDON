"""Source-format distinctions that change the observation supplied downstream."""
from datetime import date, datetime
from dataclasses import replace
import unittest

from cordon_d.monitoring import observation
from cordon_d.releases import Occurrence


class MonitoringTests(unittest.TestCase):
    def row(self, values, **options):
        return observation(Occurrence('source', 'digest', 'row:2', values),
                           release='publisher/release', **options)

    def test_result_does_not_replace_observation_type_or_symptoms(self):
        result = self.row({'TIPOLOGIA': 'Ispezione visiva', 'RISULTATO': None,
                           'SINTOMO': 'Presente', 'SPECIE': 'Mandorlo'})
        self.assertEqual(result.publication.result, 'unpublished')
        self.assertTrue(result.symptom_presence)
        self.assertEqual(result.kind, 'Ispezione visiva')
        self.assertIsNone(self.row({'SINTOMO': 0}).symptom_presence)
        self.assertEqual(self.row({'RISULTATO': 'Negativo'}).publication.result, 'published-negative')
        self.assertEqual(self.row({'RISULTATO': 'Dubbio'}).publication.result, 'published-doubtful')

    def test_date_is_source_day_and_identifiers_are_not_plant_identity(self):
        book = self.row({'ID': 123.0, 'DATA_RILEVAMENTO': datetime(2023, 2, 4)})
        sit = self.row({'attributes': {'ID_CAMPIONE': '123', 'DATA_CAMPIONE': 1675468800000}},
                       view_name='Campioni 2022')
        self.assertEqual(sit.observation_date, date(2023, 2, 4))
        self.assertEqual((book.observation_reference, book.observation_date), (sit.observation_reference, sit.observation_date))
        self.assertNotEqual(book.occurrence_key, replace(sit, release='another').occurrence_key)
        self.assertIsNone(self.row({'OBJECTID': 123, 'DATA_CAMPIONE': date(2023, 2, 4)}).observation_reference)
        self.assertNotEqual(self.row({'ID': '00123'}).observation_reference, book.observation_reference)

    def test_disagreeing_or_bad_dates_do_not_choose_an_anchor(self):
        for value in (date(2023, 2, 5), 'unreadable date'):
            reading = self.row({'DATA_CAMPIONE': date(2023, 2, 4), 'DATA_RILEVAMENTO': value})
            self.assertIsNone(reading.observation_date)
            self.assertTrue(reading.issues)

    def test_early_campaign_local_midnight_does_not_move_sampling_to_previous_day(self):
        reading = self.row({'attributes': {'DATA_CAMPIONE': 1385334000000}})
        self.assertEqual(reading.observation_date, date(2013, 11, 25))

    def test_layer_subspecies_is_context_not_a_negative_samples_identification(self):
        reading = self.row({'attributes': {'ID_CAMPIONE': 'new', 'RISULTATO': 'Negativo'},
                            'geometry': {'x': 590000, 'y': 4550000},
                            'spatialReference': {'wkid': 32633}},
                           view_name='Olivo - Campioni 2026 sub. multiplex')
        self.assertIsNone(reading.subspecies)
        self.assertEqual(reading.crs, 'EPSG:32633')
        self.assertEqual(reading.coordinates, (590000, 4550000))
        # The degree columns state the axes and no datum; the datum is established for
        # this publisher at GEOGRAPHIC_FRAME from its own SIT publications of the same
        # observations, so a location without a frame is no longer handed to a consumer.
        self.assertEqual(self.row({'LATITUDINE': 40, 'LONGITUDINE': 17}).crs, 'EPSG:4326')
        self.assertEqual(self.row({'LATITUDINE': '40,75', 'LONGITUDINE': '17,25'}).coordinates,
                         (17.25, 40.75))


if __name__ == '__main__':
    unittest.main()

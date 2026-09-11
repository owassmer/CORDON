"""What row 1 reads, what it carries for other rows, and why it carries nothing.

The records here are shaped like the ones the publisher prints — an ArcGIS feature and a
workbook row — and none of them is registered anywhere in the reader.
"""
from datetime import date
import unittest

from cordon_d.monitoring import (CARRIED_FOR, COMPARED_ATTRIBUTES, COMPARED_FIELDS, Member,
                                 OBSERVATION_ATTRIBUTES, PUBLISHER_IDENTIFIERS,
                                 DistinctObservation, observation)
from cordon_d.releases import Occurrence


def feature(attributes, *, geometry=True):
    values = {'attributes': dict(attributes)}
    if geometry:
        values['geometry'] = {'x': 689343.39, 'y': 4494722.78}
        values['spatialReference'] = {'wkid': 32633, 'latestWkid': 32633}
    return Occurrence(path='blobs/x', sha256='x', locator='feature:0', values=values)


def read(attributes, *, view='Positivi - Campioni 2024', geometry=True):
    return observation(feature(attributes, geometry=geometry), release='r', view_name=view)


class AnAbsenceNamesItsCause(unittest.TestCase):
    def causes(self, reading):
        return dict(reading.causes)

    def test_a_source_that_states_nothing_and_a_reading_that_recovers_nothing_are_different(self):
        silent = self.causes(read({'ID_CAMPIONE': 1, 'DATA_CAMPIONE': 1713312000000,
                                   'RISULTATO': 'Negativo'}))
        self.assertEqual(silent['symptom_presence'], 'no such field is published in this record')

        null = self.causes(read({'ID_CAMPIONE': 2, 'DATA_CAMPIONE': 1713312000000,
                                 'RISULTATO': 'Negativo', 'SINTOMO': None}))
        self.assertEqual(null['symptom_presence'], 'the field is published and carries no value')

        sentinel = self.causes(read({'ID_CAMPIONE': 3, 'DATA_CAMPIONE': 1713312000000,
                                     'RISULTATO': 'Negativo', 'SINTOMO': '****'}))
        self.assertEqual(sentinel['symptom_presence'],
                         'the field is published and carries only a sentinel or blank')

        unread = self.causes(read({'ID_CAMPIONE': 4, 'DATA_CAMPIONE': 1713312000000,
                                   'RISULTATO': 'Negativo', 'SINTOMO': '0'}))
        self.assertEqual(unread['symptom_presence'],
                         'a value is published that this reader does not interpret')
        # ...and a value the reader does interpret produces no cause at all.
        self.assertNotIn('symptom_presence', self.causes(read(
            {'ID_CAMPIONE': 5, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo',
             'SINTOMO': 'Presente'})))

    def test_a_record_the_publisher_identifies_by_another_name_says_so(self):
        reading = read({'OBJECTID': 299761, 'ID_GIORNALIERO': 4, 'SPECIE': 'Olivo (Olea europaea)',
                        'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo'})
        self.assertIsNone(reading.observation_reference)
        self.assertEqual(self.causes(reading)['reference'],
                         'the sample reference is not published; this record is identified by '
                         'ID_GIORNALIERO, OBJECTID')
        # the identifiers the publisher did print travel with the reading
        self.assertEqual(dict(reading.identifiers)['OBJECTID'], '299761')
        # a record identifying nothing is a different absence
        anonymous = read({'SPECIE': 'Olivo', 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo'})
        self.assertEqual(self.causes(anonymous)['reference'],
                         'no identifier is published in this record')

    def test_a_printed_sample_reference_that_is_rejected_says_which_way(self):
        for value, cause in ((None, 'the field is published and carries no value'),
                             ('****', 'the field is published and carries only a sentinel or blank'),
                             ('  ', 'the field is published and carries only a sentinel or blank')):
            reading = read({'ID_CAMPIONE': value, 'OBJECTID': 7, 'DATA_CAMPIONE': 1713312000000,
                            'RISULTATO': 'Negativo'})
            self.assertIsNone(reading.observation_reference)
            self.assertEqual(self.causes(reading)['reference'], cause, repr(value))

    def test_a_reading_that_carries_every_value_carries_no_cause(self):
        complete = read({'ID_CAMPIONE': 1669072, 'SPECIE': 'Fico (Ficus carica L.)',
                         'CULTIVAR': 'Ogliarola', 'SUBSPECIE': 'pauca', 'SINTOMO': 'Assente',
                         'TIPOLOGIA': 'Campione', 'DATA_CAMPIONE': 1713312000000,
                         'RISULTATO': 'Negativo'})
        self.assertEqual(complete.causes, ())


class RowOneReadsItsOwnSubject(unittest.TestCase):
    def test_an_observation_attribute_is_established_and_compared(self):
        reading = read({'ID_CAMPIONE': 9, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo',
                        'COMUNE': 'Francavilla Fontana', 'SQUADRA': '222547', 'TECNICO': 'MAZ-MEL'})
        self.assertEqual(dict(reading.attributes)['COMUNE'], 'Francavilla Fontana')
        for field in ('COMUNE', 'SQUADRA', 'TECNICO'):
            self.assertIn(field, COMPARED_FIELDS, field)
        # A free-text note and a publication status describe the publication, not the
        # observation, so they are established and never compared.
        for field in ('NOTE_RILEVATORE', 'STATO'):
            self.assertIn(field, OBSERVATION_ATTRIBUTES, field)
            self.assertNotIn(field, COMPARED_ATTRIBUTES, field)
            self.assertNotIn(field, COMPARED_FIELDS, field)

    def test_two_publications_disagreeing_about_where_it_happened_is_a_disagreement(self):
        def member(comune, objectid):
            return Member('r', 'v', 'p', 's', f'l{objectid}', 'published-negative', None, 'Olivo',
                          None, None, None, None, None, (), (),
                          (('OBJECTID', objectid),), (('COMUNE', comune),), (), ())
        group = DistinctObservation('9', date(2024, 4, 17),
                                    (member('Oria', '1'), member('Francavilla Fontana', '2')))
        self.assertIn('COMUNE', group.disagreements)
        # ...while the publisher's own feature id differs between views by construction
        # and must never be read as the publications disagreeing.
        self.assertNotIn('OBJECTID', group.disagreements)
        self.assertNotIn('OBJECTID', COMPARED_FIELDS)
        agreed = DistinctObservation('9', date(2024, 4, 17), (member('Oria', '1'), member('Oria', '2')))
        self.assertEqual(agreed.disagreements, ())

    def test_no_publisher_identifier_is_ever_compared(self):
        for field in PUBLISHER_IDENTIFIERS:
            self.assertNotIn(field, COMPARED_FIELDS, field)


class RowOneCarriesWithoutInterpreting(unittest.TestCase):
    def test_another_rows_fact_is_carried_as_the_literal_and_established_by_nobody_here(self):
        reading = read({'ID_CAMPIONE': 11, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Positivo',
                        'PROT_SELGE': '253/2019', 'STRUTTURA_LABORATORIO': 'CRSFA',
                        'ZONA_DELIMITATA': 'Area Delimitata Valle d’Itria',
                        'FOGLIO': '12', 'PARTICELLA': '340', 'SCELTA_PROPRIETARIO': 'Estirpazione',
                        'RIF_DECRETO': 'DDS 117/2025'})
        carried = dict(reading.carried)
        self.assertEqual(carried['PROT_SELGE'], '253/2019')
        self.assertEqual(carried['SCELTA_PROPRIETARIO'], 'Estirpazione')
        # carried, and interpreted by nothing: no attribute, no comparison, no established fact
        self.assertEqual(dict(reading.attributes), {})
        for field in carried:
            self.assertNotIn(field, COMPARED_FIELDS, field)
            self.assertIn(field, CARRIED_FOR, field)
        # and the owning row is named, so the literal is never mistaken for an adjudicated fact
        self.assertEqual(CARRIED_FOR['PROT_SELGE'], 'laboratory report')
        self.assertEqual(CARRIED_FOR['SCELTA_PROPRIETARIO'], 'owner response')

    def test_a_carried_field_and_an_established_attribute_are_disjoint(self):
        self.assertEqual(set(CARRIED_FOR) & set(OBSERVATION_ATTRIBUTES), set())
        self.assertEqual(set(CARRIED_FOR) & set(PUBLISHER_IDENTIFIERS), set())


if __name__ == '__main__':
    unittest.main()

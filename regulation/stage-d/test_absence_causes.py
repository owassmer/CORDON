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

    def test_a_field_this_reader_establishes_and_did_not_carry_names_why(self):
        # The defect this unit exists to cure, on the surface this unit creates: an
        # operator seeing no COMUNE must be able to tell a silent publisher from a
        # sentinel from a value this reader did not read.
        silent = self.causes(read({'ID_CAMPIONE': 20, 'DATA_CAMPIONE': 1713312000000,
                                   'RISULTATO': 'Negativo'}))
        self.assertNotIn('COMUNE', silent)          # not published at all: nothing to explain
        null = self.causes(read({'ID_CAMPIONE': 21, 'DATA_CAMPIONE': 1713312000000,
                                 'RISULTATO': 'Negativo', 'COMUNE': None}))
        self.assertEqual(null['COMUNE'], 'the field is published and carries no value')
        sentinel = self.causes(read({'ID_CAMPIONE': 22, 'DATA_CAMPIONE': 1713312000000,
                                     'RISULTATO': 'Negativo', 'COMUNE': '****'}))
        self.assertEqual(sentinel['COMUNE'],
                         'the field is published and carries only a sentinel or blank')
        carried_for_another_row = self.causes(read(
            {'ID_CAMPIONE': 23, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Positivo',
             'PROT_SELGE': None}))
        self.assertEqual(carried_for_another_row['PROT_SELGE'],
                         'the field is published and carries no value')

    def test_a_field_no_row_claims_is_reported_rather_than_passed_over(self):
        # A publisher may print a column this stage has never seen. It must surface the
        # first time, not wait to be noticed in a survey.
        unseen = self.causes(read({'ID_CAMPIONE': 30, 'DATA_CAMPIONE': 1713312000000,
                                   'RISULTATO': 'Negativo', 'FASE_FENOL': 'Fioritura',
                                   'SUPERFICIE': None}))
        self.assertEqual(unseen['FASE_FENOL'], 'published, and no row of this stage claims it')
        self.assertEqual(unseen['SUPERFICIE'],
                         'published carrying no value, and no row of this stage claims it')

    def test_a_result_absence_uses_the_vocabulary_campaign_already_has(self):
        absent = self.causes(read({'ID_CAMPIONE': 40, 'DATA_CAMPIONE': 1713312000000}))
        self.assertEqual(absent['result'], 'no such field is published in this record')
        empty = self.causes(read({'ID_CAMPIONE': 41, 'DATA_CAMPIONE': 1713312000000,
                                  'RISULTATO': None}))
        self.assertEqual(empty['result'], 'the field is published and carries no value')

    def test_the_route_to_the_laboratory_report_names_why_it_is_absent(self):
        # Row 2 reads this list. An empty one must not mean both "the publisher printed
        # no route" and "a column was there that this reader could not read".
        silent = self.causes(read({'ID_CAMPIONE': 50, 'DATA_CAMPIONE': 1713312000000,
                                   'RISULTATO': 'Negativo'}))
        self.assertEqual(silent['report_routes'], 'no such field is published in this record')
        empty = self.causes(read({'ID_CAMPIONE': 51, 'DATA_CAMPIONE': 1713312000000,
                                  'RISULTATO': 'Positivo', 'DOCUMENTO_DECRETO': None}))
        self.assertEqual(empty['report_routes'], 'the field is published and carries no value')
        sentinel = self.causes(read({'ID_CAMPIONE': 52, 'DATA_CAMPIONE': 1713312000000,
                                     'RISULTATO': 'Positivo', 'DOCUMENTO_CONFERMA': '****'}))
        self.assertEqual(sentinel['report_routes'],
                         'the field is published and carries only a sentinel or blank')
        routed = read({'ID_CAMPIONE': 53, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Positivo',
                       'DOCUMENTO_CONFERMA': 'http://webadf.sit.puglia.it/doc/CONFERMA.pdf'})
        self.assertNotIn('report_routes', self.causes(routed))

    def test_an_observation_of_another_kind_is_not_a_missing_result(self):
        visual = read({'ID_CAMPIONE': 60, 'DATA_CAMPIONE': 1713312000000,
                       'RISULTATO': 'ISPEZIONE VISIVA'})
        self.assertEqual(self.causes(visual)['result'],
                         'the record publishes an observation of another kind, '
                         'which is not an analytical result')
        sentinel = read({'ID_CAMPIONE': 61, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': '****'})
        self.assertEqual(self.causes(sentinel)['result'],
                         'the field is published and carries only a sentinel or blank')
        unfamiliar = read({'ID_CAMPIONE': 62, 'DATA_CAMPIONE': 1713312000000,
                           'RISULTATO': 'Esito non conclusivo'})
        self.assertEqual(self.causes(unfamiliar)['result'],
                         'a value is published that this reader does not interpret')

    def test_a_value_in_a_shape_this_reader_does_not_interpret_is_not_promoted(self):
        # Rendering a mapping's Python repr would establish a fact the record does not
        # state, and comparing that repr could manufacture a disagreement.
        nested = read({'ID_CAMPIONE': 70, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo',
                       'COMUNE': {'nome': 'Ostuni', 'istat': 74011}})
        self.assertEqual(dict(nested.attributes).get('COMUNE'), None)
        self.assertEqual(self.causes(nested)['COMUNE'],
                         'a value is published that this reader does not interpret')
        listed = read({'ID_CAMPIONE': 71, 'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo',
                       'PROT_SELGE': [1, 2]})
        self.assertEqual(dict(listed.carried).get('PROT_SELGE'), None)
        self.assertEqual(self.causes(listed)['PROT_SELGE'],
                         'a value is published that this reader does not interpret')

    def test_geometry_this_reader_cannot_read_is_not_reported_as_no_geometry(self):
        polygon = observation(Occurrence(
            path='b', sha256='b', locator='l',
            values={'attributes': {'ID_CAMPIONE': 80, 'DATA_CAMPIONE': 1713312000000,
                                   'RISULTATO': 'Negativo'},
                    'geometry': {'rings': [[[0, 0], [1, 1]]]},
                    'spatialReference': {'wkid': 32633}}), release='r', view_name='v')
        self.assertEqual(dict(polygon.causes)['coordinates'],
                         'geometry is published in a shape this reader does not interpret')
        none_at_all = read({'ID_CAMPIONE': 81, 'DATA_CAMPIONE': 1713312000000,
                            'RISULTATO': 'Negativo'}, geometry=False)
        self.assertEqual(dict(none_at_all.causes)['coordinates'],
                         'no geometry is published in this record')

    def test_a_reading_that_carries_every_value_carries_no_cause(self):
        complete = read({'ID_CAMPIONE': 1669072, 'SPECIE': 'Fico (Ficus carica L.)',
                         'CULTIVAR': 'Ogliarola', 'SUBSPECIE': 'pauca', 'SINTOMO': 'Assente',
                         'TIPOLOGIA': 'Campione', 'DATA_CAMPIONE': 1713312000000,
                         'RISULTATO': 'Positivo',
                         'DOCUMENTO_CONFERMA': 'http://webadf.sit.puglia.it/doc/C.pdf'})
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

    def test_who_performed_the_observation_is_read_under_every_name_the_publisher_uses(self):
        # The 2016 infrastructure survey names the team and its inspectors in columns of
        # its own; it is the same fact as TECNICO and must not be lost to the spelling.
        reading = read({'ID_GIORNALIERO': 3, 'OBJECTID': 207687, 'DATA_CAMPIONE': 1478649600000,
                        'RISULTATO': 'NEGATIVO', 'COD_TECNICI': 'CIC-GAG',
                        'COGNOME_ISPETTORE_1': 'Ciciretti', 'NOME_ISPETTORE_1': 'Luciano'})
        attributes = dict(reading.attributes)
        self.assertEqual(attributes['COD_TECNICI'], 'CIC-GAG')
        self.assertEqual(attributes['COGNOME_ISPETTORE_1'], 'Ciciretti')
        for field in ('COD_TECNICI', 'COGNOME_ISPETTORE_1', 'NOME_ISPETTORE_1'):
            self.assertIn(field, COMPARED_FIELDS, field)

    def test_a_label_shared_by_many_records_is_not_an_identity(self):
        # CODICE_CAMPIONAMENTO prints a campaign name such as '2019-II' on hundreds of
        # records at once. Offering it as identity would answer a question the record
        # does not answer.
        reading = read({'OBJECTID': 4, 'CODICE_CAMPIONAMENTO': 'XF MULTIPLEX 2024',
                        'DATA_CAMPIONE': 1713312000000, 'RISULTATO': 'Negativo'})
        self.assertNotIn('CODICE_CAMPIONAMENTO', PUBLISHER_IDENTIFIERS)
        self.assertEqual(dict(reading.attributes)['CODICE_CAMPIONAMENTO'], 'XF MULTIPLEX 2024')
        self.assertNotIn('CODICE_CAMPIONAMENTO', COMPARED_FIELDS)
        self.assertEqual(dict(reading.causes)['reference'],
                         'the sample reference is not published; this record is identified by OBJECTID')


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

    def test_a_published_zone_label_is_carried_for_the_demarcated_area_row(self):
        # ZONA prints 'Zona Contenimento - Salento', 'Area delimitata Monopoli': a
        # demarcated-zone status, which row 3 establishes from the adopting act.
        reading = read({'ID_CAMPIONE': 90, 'DATA_CAMPIONE': 1713312000000,
                        'RISULTATO': 'Positivo', 'ZONA': 'Zona Contenimento - Salento'})
        self.assertEqual(dict(reading.carried)['ZONA'], 'Zona Contenimento - Salento')
        self.assertEqual(CARRIED_FOR['ZONA'], 'demarcated area')
        self.assertNotIn('ZONA', OBSERVATION_ATTRIBUTES)
        self.assertNotIn('ZONA', COMPARED_FIELDS)
        self.assertEqual(dict(reading.attributes), {})

    def test_a_carried_field_and_an_established_attribute_are_disjoint(self):
        self.assertEqual(set(CARRIED_FOR) & set(OBSERVATION_ATTRIBUTES), set())
        self.assertEqual(set(CARRIED_FOR) & set(PUBLISHER_IDENTIFIERS), set())


if __name__ == '__main__':
    unittest.main()

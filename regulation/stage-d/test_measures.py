"""Actual retained measure -> targets, report associations and accepted C clock."""
from datetime import date
from dataclasses import replace
from pathlib import Path
import re
import unittest
from zoneinfo import ZoneInfo

from cordon_c import Snapshot
from cordon_d.calendar import national_calendar
from cordon_d.measures import retained_measure
from cordon_d.removal_events import connected_publications, publication_deadline, publication_records
from cordon_d.store import blob_path, store_root


class RetainedWholeMeasure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = store_root(Path(__file__).resolve())
        cls.digest = '936eb652ee9425e627e00d62b81429ecbafa89e36e3a53515331cb2c8cf5a632'
        if not blob_path(cls.store, cls.digest).exists():
            raise unittest.SkipTest('Retained source store unavailable')
        try:
            cls.measure = retained_measure('6f31e677689ecf211f5103abfa7ccd1c33c32ec9ff50130e8614b57527de764d', cls.store)
        except FileNotFoundError:
            raise unittest.SkipTest('Whole-measure response not retained; no extraction in tests')

    def test_whole_source_preserves_actual_prescribed_scope_and_positions(self):
        # Independently read BURP physical pages 6–8, maps 11–12, table 15.
        measure = self.measure
        self.assertEqual(measure.identity, 'REG-PUGLIA-U181-DIR-2024-00058')
        self.assertEqual(measure.adopted, date(2024, 5, 16))
        targets = {t['reference']: t for t in measure.prescribed_targets()}
        self.assertEqual(set(targets), {'1662907', '1663853', '1663690', '1662223', '1662073'})
        self.assertEqual(targets['1662907']['sheet'], '13')
        self.assertEqual(targets['1662907']['parcel'], '105')
        self.assertEqual(re.findall(r'[A-Z]+', targets['1663853']['addressee_text'].upper()),
                         ['PONTRELLI', 'ANNA', 'VERDONI', 'GIOVANNI'])
        self.assertGreater(len(tuple(measure.targets())), len(targets))
        for key in ('1662223', '1662073'):
            self.assertEqual(targets[key]['parcel'], '389')
            self.assertEqual(re.findall(r'[A-Z]+', targets[key]['addressee_text'].upper()),
                             ['SETTANNI', 'FEDELE', 'SETTANNI', 'ANGELO', 'SETTANNI', 'SERENA'])
        deferred = [d for d in measure.values['directions']
                    if d['mode'] == 'deferred-prescription' and d['work'] == 'removal']
        self.assertTrue(deferred)
        self.assertTrue(any('50' in c['quote'] for d in deferred for c in d['support']))
        self.assertTrue(any(d['mode'] == 'exclusion' and 'olivo' in c['quote'].lower()
                            for d in measure.values['directions'] for c in d['support']))
        kinds = {e.kind for e in measure.administrative_events()}
        self.assertIn('adoption', kinds)
        self.assertFalse(kinds & {'removal', 'owner-election', 'recipient-notification'})

    def test_measure_identity_reaches_its_actual_publication_clock(self):
        path = blob_path(self.store, '306336cb7351e151a29fa8738f81a8694e35b54d6eeb50b5273aaacc5bbfee63')
        publications = connected_publications(publication_records(path), [self.measure])
        self.assertEqual(len(publications), 1)
        publication = publications[0]
        self.assertEqual(publication.source_fields['dtAtto'], '2024-05-17')
        self.assertEqual(publication.document_date, date(2024, 5, 16))
        end = publication_deadline(Snapshot.load(), 'B-CLK-DGR1866-owner-election',
                                   self.measure.adopted, publication,
                                   document=self.measure.identity, competent_publisher='Comune di Capurso',
                                   zone=ZoneInfo('Europe/Rome'), calendar=national_calendar())
        self.assertEqual(end.date(), date(2024, 5, 30))

    def test_targets_connect_to_the_existing_association_owner(self):
        linked = dict((target['reference'], matches)
                      for target, matches in self.measure.target_associations(self.store))
        expected = {'1662907': '54/2024 CNR', '1663853': '60/2024 CNR',
                    '1663690': '53/2024 CNR', '1662223': '53/2024 CNR', '1662073': '56/2024 CNR'}
        self.assertEqual(set(linked), set(expected))
        for key, report in expected.items():
            self.assertEqual(len(linked[key]), 1)
            self.assertEqual(linked[key][0]['fields']['report_reference']['text'], report)

    def test_interpretation_request_is_not_the_administrative_event_identity(self):
        replay = replace(self.measure, response=dict(self.measure.response, request_sha256='another-proposal'))
        self.assertEqual(tuple(self.measure.administrative_events()), tuple(replay.administrative_events()))
        adoption, = (e for e in replay.administrative_events() if e.kind == 'adoption')
        self.assertEqual(adoption.identity, replay.identity + ':adoption')

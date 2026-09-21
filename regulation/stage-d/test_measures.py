"""Actual retained measure -> targets, report associations and accepted C clock."""
from datetime import date
from dataclasses import replace
from collections import Counter
from pathlib import Path
import re
import unittest
from zoneinfo import ZoneInfo

from cordon_c import Snapshot
from cordon_d.calendar import national_calendar
from cordon_d.measures import retained_measure
from cordon_d.removal_events import (connected_publications, event_deadline,
                                     publication_deadline, publication_records)
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


class RetainedSharedOwnerFields(unittest.TestCase):
    def test_each_plant_keeps_its_identity_and_the_complete_shared_cross_page_field(self):
        store = store_root(Path(__file__).resolve())
        digest = '44f299b0d9183377a846fd2c6e9125cbbd7d69e2edac29718b3e5112d1b1c321'
        try:
            measure = retained_measure(
                '09d2b80056783c2babade9f5dc85b85e7075c8f6230f6a504a9b791d9bdeb717', store)
        except FileNotFoundError:
            self.skipTest('Retained DDS74 sources/response unavailable; no extraction in tests')
        # Independently viewed DDS74 pp30–32. These checks qualify the shared
        # owner fields and native identities, not the rest of the interpretation.
        expected = [
            (('1669995', '1669998'), (30, 31), '177', 'OTTOLINO MARIA OTTOLINO ANGELA'),
            (('1669854', '1669872'), (31, 32), '219',
             'NITTI AGATA NITTI ANNA SALIANO BENEDETTO MARIA NITTI SALIANO GIUSEPPE '
             'NITTI GIUSEPPE LUCIANO NITTI SALIANO AGATA SALIANO RAFFAELLA NITTI MARIA '
             'TERESA TRAVAGLIO DOMENICA NITTI GIOVANNI TRAVAGLIO GIUSEPPE TRAVAGLIO '
             'NICOLA NITTI ANGELA NITTI MICHELE'),
        ]
        targets = {t['reference']: t for t in measure.prescribed_targets()}
        for identifiers, pages, parcel, owner in expected:
            for identifier, page in zip(identifiers, pages):
                with self.subTest(plant=identifier):
                    target = targets[identifier]
                    association = target['association']
                    self.assertEqual((target['sheet'], target['parcel']), ('20', parcel))
                    self.assertEqual(association['source_sha256'], digest)
                    self.assertEqual(association['page'], page)
                    self.assertEqual(association['fields']['plant_id']['text'], identifier)
                    self.assertIs(target['fields']['plant_id'], association['fields']['plant_id'])
                    self.assertEqual(re.findall(r'[A-Z]+', target['addressee_text']), owner.split())
                    fragments = target['fields']['addressee']['fragments']
                    self.assertEqual([f['page'] for f in fragments], list(pages))
                    self.assertTrue(all(f['source'] == digest and f['bbox']
                                        and f['locator'].startswith(f"S0P{f['page']}T1/cell:")
                                        for f in fragments))
            self.assertEqual(targets[identifiers[0]]['fields']['addressee'],
                             targets[identifiers[1]]['fields']['addressee'])
            self.assertIsNot(targets[identifiers[0]]['fields']['plant_id'],
                             targets[identifiers[1]]['fields']['plant_id'])


class RetainedLaterPrescription(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = store_root(Path(__file__).resolve())
        cls.digest = '138add2778567999e2852335f6a79469f2677df68891e88ca1af9bbac089b0e5'
        try:
            cls.measure = retained_measure(
                'd2d28d922db280b80fd840cada611d6796c3ef05e1bf686c2b82a380e9a7c734', cls.store)
        except FileNotFoundError:
            raise unittest.SkipTest('Retained DDS138 sources/response unavailable; no extraction in tests')

    def test_six_native_positions_keep_reports_and_addressees_without_deferred_targets(self):
        # Independently read DDS138 operative p6 and original Annex 1/C pp18–19.
        expected = {
            '1699662': ('12', '86', 'LAGIOIA ROSA SILVANA ROBERTO GIANLUCA'),
            '1699576': ('12', '154', 'QUARANTA FILOMENA QUARANTA ROSSANA QUARANTA VINCENZO'),
            '1699797': ('12', '176', 'PONTRELLI ANNA MARIA CARMELA'),
            '1674070': ('17', '1151', 'GIANNELLI NATALINA'),
            '1699929': ('20', '85', 'CAPUTO MARIO'),
            '1699892': ('20', '100', 'DE MARCO MARIA DICINTIO GIOVANNI'),
        }
        linked = tuple(self.measure.target_associations(self.store))
        self.assertEqual(len(linked), 6)
        self.assertEqual({t['reference']: (t['sheet'], t['parcel'], ' '.join(t['addressee_text'].split()))
                          for t, _ in linked}, expected)
        for target, matches in linked:
            self.assertEqual(len(matches), 1)
            association, = matches
            self.assertEqual(association['source_sha256'], self.digest)
            self.assertEqual(association['page'], 19 if target['reference'] == '1699892' else 18)
            self.assertIs(target['fields']['plant_id'], association['fields']['plant_id'])
            self.assertIs(target['fields']['report_reference'], association['fields']['report_reference'])
            report, day = ('73F/2024 CNR', '03/10/2024') if target['reference'] == '1674070' else (
                '114F/2024 CNR', '17/07/2024')
            self.assertEqual(' '.join(association['fields']['report_reference']['text'].split()), report)
            self.assertEqual(association['fields']['report_date']['text'], day)
        deferred = [d for d in self.measure.values['directions']
                    if (d['mode'], d['work']) == ('deferred-prescription', 'removal')]
        self.assertTrue(any(c['source'] == self.digest and c['page'] == 6
                            and 'successivamente' in c['quote'] and '50 m' in c['quote']
                            for d in deferred for c in d['support']))

    def test_adoption_and_burp_cannot_start_the_recipient_notice_clock(self):
        measure = self.measure
        self.assertEqual(measure.identity, 'REG-PUGLIA-U181-DIR-2024-00138')
        self.assertEqual(measure.adopted, date(2024, 10, 28))
        events = tuple(measure.administrative_events())
        self.assertEqual({e.kind: e.occurred for e in events},
                         {'adoption': date(2024, 10, 28), 'burp-publication': date(2024, 11, 7)})
        for event in events:
            with self.subTest(kind=event.kind), self.assertRaisesRegex(ValueError, 'Wrong event kind'):
                event_deadline(Snapshot.load(), 'B-CLK-DDS138-2024-notification-noncommencement',
                               measure.adopted, event, document=measure.identity,
                               recipient='GIANNELLI NATALINA', zone=ZoneInfo('Europe/Rome'))

    def test_blank_form_preserves_non_addressee_capacity_evidence_requirement(self):
        # Original p16 requires supporting documentation if the responder differs
        # from the named addressee. Its unchecked choices are no actual election.
        response = [d for d in self.measure.values['directions']
                    if (d['mode'], d['work']) == ('ordered-now', 'response')]
        self.assertTrue(any(d['conditions'] and c['source'] == self.digest and c['page'] == 16
                            and 'diverso' in c['quote'] and 'intestatario' in c['quote']
                            and 'documentazione probatoria' in c['quote']
                            for d in response for c in d['support']))
        forms = [e for e in self.measure.values['events'] if e['evidence'] == 'blank-form'
                 and any(c['source'] == self.digest and c['page'] == 16 for c in e['support'])]
        self.assertTrue(forms)
        self.assertTrue(all(e['occurred_on'] is None for e in forms))
        self.assertEqual({e.kind for e in self.measure.administrative_events()},
                         {'adoption', 'burp-publication'})


class RetainedIncorporatedCorrection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = store_root(Path(__file__).resolve())
        cls.principal = 'c05d3c4d118686a184a804d0048aebc1c1a79f45d8b0464048488cab69d2bff8'
        cls.predecessor = '882c0020ab2ce0e55c06c9d72b36b3bd0204d02a48b6c35120c81bc050d958cd'
        try:
            cls.measure = retained_measure(
                '1fee02aee3ac0c31f6fa58f695bd76085cbfdc47fe4d542fe50939e19e449700', cls.store)
        except FileNotFoundError:
            raise unittest.SkipTest('Retained correction sources/response unavailable; no extraction in tests')

    def test_current_work_uses_corrected_names_and_preserves_former_occurrences(self):
        # DDS11 operative page 2; independently viewed DDS188 pages
        # 29–31, 42, 47 and 70. Parcel 21/719 has two former occurrences.
        measure = self.measure
        current = measure.prescribed_targets()
        self.assertEqual(len(current), 4)
        self.assertEqual({t['sheet']: (t['parcel'], t['addressee_text']) for t in current}, {
            '21': ('713, 715, 717, 719, 721', 'Acquedotto Pugliese S.p.A;'),
            '20': ('1168', 'Acquedotto Pugliese S.p.A;'),
            '17': ('1143, 1146, 1148, 1150, 1152, 1154, 1156, 1158, 1186, 1189',
                   'Acquedotto Pugliese S.p.A;'),
            '12': ('40, 41', 'Sig. Ragone Matteo.'),
        })
        self.assertTrue(all(t['reference'] is None and t['association'] is None for t in current))
        old = [t for t in measure.targets() if t['occurrence'] not in
               {t['occurrence'] for t in current}]
        self.assertEqual(len(old), 19)
        repeated = [t for t in old if (t['sheet'], t['parcel']) == ('21', '719')]
        self.assertEqual(len(repeated), 2)
        self.assertEqual({t['addressee_text'] for t in repeated}, {'DI GIOIA MICHELE,CRUDELE ROSA'})
        self.assertEqual({t['addressee_text'] for t in old if t['sheet'] == '12'},
                         {'CONTESSA DOMENICA'})
        directions = {d['id']: d for d in measure.values['directions']}
        self.assertTrue(all(directions[i]['work'] == 'other' for t in old for i in t['direction_ids']))

    def test_incorporated_work_has_both_sources_and_keeps_distinct_clocks(self):
        directions = self.measure.values['directions']
        removal, = (d for d in directions if (d['mode'], d['work']) == ('ordered-now', 'removal'))
        self.assertEqual({c['source'] for c in removal['support']}, {self.principal, self.predecessor})
        quotes = ' '.join(c['quote'] for c in removal['support'])
        for category in ('sintomi', 'stessa specie', 'specie diverse', 'analisi molecolare'):
            self.assertIn(category, quotes)
        self.assertTrue(any(d['mode'] == 'exclusion' and 'olivo' in c['quote']
                            for d in directions for c in d['support']))
        self.assertTrue(any(d['mode'] == 'exclusion' and 'valore storico' in c['quote']
                            for d in directions for c in d['support']))
        self.assertFalse(any(d['work'] == 'treatment' for d in directions))
        # The incorporated text has distinct completion and noncommencement anchors.
        conditional = [d for d in directions if (d['mode'], d['work']) == ('conditional-order', 'removal')]
        self.assertTrue(any('dalla sua comunicazione' in c['quote']
                            for d in conditional for c in d['support']))
        self.assertTrue(any('dall’avvenuta notifica' in c['quote']
                            for d in conditional for c in d['support']))
        self.assertFalse(any(i['aspect'] == 'timing' and i['cause'] == 'conflict'
                             for i in self.measure.values['issues']))

    def test_actual_burp_publication_cannot_anchor_recipient_noncommencement(self):
        measure = self.measure
        self.assertEqual(measure.identity, 'REG-PUGLIA-U181-DIR-2025-00011')
        self.assertEqual(measure.adopted, date(2025, 2, 5))
        events = tuple(measure.administrative_events())
        self.assertEqual({e.kind for e in events}, {'adoption', 'burp-publication'})
        publication, = (e for e in events if e.kind == 'burp-publication')
        self.assertEqual(publication.occurred, date(2025, 2, 13))
        with self.assertRaisesRegex(ValueError, 'Wrong event kind'):
            event_deadline(Snapshot.load(), 'B-CLK-DDS188-2024-notification-noncommencement',
                           measure.adopted, publication, document=measure.identity,
                           recipient='Acquedotto Pugliese S.p.A', zone=ZoneInfo('Europe/Rome'))


class RetainedVisibleAnnex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = store_root(Path(__file__).resolve())
        try:
            cls.measure = retained_measure(
                '9ce11e806132fe5f1b1dd0e32500c497104ee6acbdbcadb4254f25d5a38863fe', cls.store)
        except FileNotFoundError:
            raise unittest.SkipTest('Retained visible annex/response unavailable; no extraction in tests')

    def test_rendered_rows_preserve_individual_plants_and_parcel_addressee_pairs(self):
        # DDS117 original pages 8–9, read visually before interpreting the response.
        targets = self.measure.prescribed_targets()
        self.assertEqual(len(targets), 13)
        plants = {t['reference']: t for t in targets if t['reference']}
        self.assertEqual(set(plants), {'1804248', '1804274', '1804256'})
        self.assertEqual({(t['sheet'], t['parcel'], t['addressee_text'].upper())
                          for t in plants.values()}, {('22', '38', 'RESCINA GERARDO')})
        parcels = [t for t in targets if t['reference'] is None]
        expected = [('4', p, 'NITTI VINCENZO') for p in ('159', '158', '296', '243')]
        expected += [('22', p, 'RESCINA GERARDO') for p in ('38', '65', '64', '40', '38')]
        expected += [('22', '39', 'RANIERI NICOLA')]
        self.assertEqual(Counter((t['sheet'], t['parcel'], t['addressee_text'].upper())
                                 for t in parcels), Counter(expected))
        self.assertTrue(all(t['fields']['parcel']['derivation'] ==
                            'model transcription of source image' for t in parcels))
        # Surrounding-zone captions cannot create another infected-plant target.
        self.assertNotIn('1804378', plants)
        self.assertTrue(any('1804378' in t['fields'].get('reference_plant_id', {}).get('text', '')
                            for t in parcels))

    def test_prescription_and_objection_do_not_manufacture_completed_notice_or_work(self):
        measure = self.measure
        self.assertEqual(measure.identity, 'REG-PUGLIA-U181-DIR-2025-00117')
        self.assertEqual(measure.adopted, date(2025, 6, 27))
        events = tuple(measure.administrative_events())
        self.assertEqual({e.kind for e in events}, {'adoption', 'burp-publication'})
        publication, = (e for e in events if e.kind == 'burp-publication')
        self.assertEqual(publication.occurred, date(2025, 7, 10))
        with self.assertRaisesRegex(ValueError, 'Wrong event kind'):
            event_deadline(Snapshot.load(), 'B-CLK-DDS117-2025-notification-noncommencement',
                           measure.adopted, publication, document=measure.identity,
                           recipient='NITTI VINCENZO', zone=ZoneInfo('Europe/Rome'))
        # Unlike DDS188, DDS117 explicitly prescribes treatment before removal.
        treatment, = (d for d in measure.values['directions'] if d['work'] == 'treatment')
        self.assertEqual(treatment['mode'], 'ordered-now')
        self.assertTrue(any('prima' in c['quote'] and 'trattamento' in c['quote']
                            for c in treatment['support']))
        objection, = (e for e in measure.values['events'] if e['occurred_on'] == '2025-06-18')
        self.assertEqual(objection['evidence'], 'reported-event')
        self.assertNotEqual(objection['document_reference'], 'this-act')

    def test_corrected_positions_reuse_the_explicit_predecessor_associations(self):
        linked = [(t, matches) for t, matches in self.measure.target_associations(self.store) if matches]
        self.assertEqual({t['reference'] for t, _ in linked}, {'1804248', '1804274', '1804256'})
        for target, matches in linked:
            self.assertEqual(len(matches), 1)
            association = matches[0]
            self.assertEqual(association['source_sha256'],
                             '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955')
            self.assertEqual(association['page'], 17)
            self.assertEqual(association['fields']['report_reference']['text'], '22F/2025 CNR')
            self.assertEqual(association['fields']['report_date']['text'], '21/02/2025')
            self.assertIs(target['fields']['plant_id'], association['fields']['plant_id'])
            self.assertEqual(target['fields']['addressee']['source'],
                             '1d2e9b6111cdb33de96f1b1abeb49c1d3ad35019994404a74e59320d7850c2aa')
            self.assertEqual(target['addressee_text'].upper(), 'RESCINA GERARDO')

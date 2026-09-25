"""Discriminating administrative evidence tests; source meaning is reviewed separately."""
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from cordon_c.core import MissingInput, Snapshot
from cordon_c.temporal import deadline
from cordon_d.calendar import national_calendar
from cordon_d.evidence import (Assertion, Evidence, Source, Support, file_digest,
                               PublishedPopulation, RequiredPopulation, completion_support)
from cordon_d.events import AdministrativeEvent
from cordon_d.readers import sampling_date

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = Snapshot.load(ROOT)
        cls.contracts = {c['id']: c for c in json.loads((HERE / 'contracts.json').read_text())['contracts']}
        cls.bindings = {b['predicate']: frozenset(b['contracts']) for b in
                        json.loads((HERE / 'predicate-contracts.json').read_text())['bindings']}

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'public.txt').write_text('Test record, not an official case.')
        self.public = Source('public', 'public.txt', file_digest(self.root / 'public.txt'), 'official-record', 'public')
        self.private = replace(self.public, identity='private', access='controlled')
        raw = {'contract': 'administrative-event',
               'consumer_version': 'PUG-LR4-2017:Art.2(3):v1',
               'predicate': 'the Regional Plant Health Service has received a report of actual or presumed presence of the specified pest'}
        self.row = Assertion('a', raw['contract'], 'test-context', date(2026, 1, 12),
                             datetime(2026, 2, 2, tzinfo=timezone.utc), raw['consumer_version'],
                             raw['predicate'], True, (Support('public', 'test locator', 'Synthetic counterexample only'),))

    def evidence(self, *rows, sources=None):
        return Evidence(self.snapshot, sources or (self.public,), rows, self.contracts, self.bindings, self.root)

    def view(self, evidence, *, through=datetime(2026, 9, 8, tzinfo=timezone.utc), permitted=frozenset(), context='test-context'):
        return evidence.view(context=context, event_date=self.row.event_date,
                             known_through=through, permitted_controlled_sources=permitted)

    def read(self, view):
        return view.reader(self.snapshot.version(self.row.consumer_version, self.row.event_date), self.row.predicate)

    def test_context_and_knowledge_are_not_interchangeable(self):
        e = self.evidence(self.row)
        self.assertTrue(self.read(self.view(e)).truth)
        self.assertIsNone(self.read(self.view(e, context='another-case')).truth)
        self.assertIsNone(self.read(self.view(e, through=datetime(2026, 2, 1, tzinfo=timezone.utc))).truth)

    def test_correction_keeps_historical_reading_and_conflict_does_not_choose_latest(self):
        second = replace(self.row, identity='b', value=False, known_at=datetime(2026, 3, 1, tzinfo=timezone.utc))
        self.assertIsNone(self.read(self.view(self.evidence(self.row, second))).truth)
        corrected = self.evidence(self.row, replace(second, supersedes=('a',)))
        self.assertFalse(self.read(self.view(corrected)).truth)
        self.assertTrue(self.read(self.view(corrected, through=datetime(2026, 2, 28, tzinfo=timezone.utc))).truth)
        with self.assertRaises(ValueError):
            self.evidence(self.row, replace(second, supersedes=('a',), context='another-case'))

    def test_private_correction_cannot_resurrect_public_predecessor(self):
        second = replace(self.row, identity='b', value=False, supersedes=('a',),
                         known_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
                         support=(Support('private', 'test locator', 'Synthetic correction only'),))
        e = self.evidence(self.row, second, sources=(self.public, self.private))
        result = self.read(self.view(e))
        self.assertIsNone(result.truth)
        self.assertNotIn('private', result.provisions)
        self.assertFalse(self.read(self.view(e, permitted=frozenset({'private'}))).truth)
        independent = replace(self.row, identity='c', value=False)
        e = self.evidence(self.row, second, independent, sources=(self.public, self.private))
        self.assertFalse(self.read(self.view(e)).truth)


    def test_changed_bytes_cannot_supply_cached_conclusion(self):
        view = self.view(self.evidence(self.row))
        self.assertTrue(self.read(view).truth)
        (self.root / 'public.txt').write_text('A different record')
        with self.assertRaises(ValueError):
            self.read(view)

    def test_form_and_wrong_contract_do_not_supply_instance_fact(self):
        with self.assertRaises(ValueError):
            self.evidence(self.row, sources=(replace(self.public, role='official-format'),))
        with self.assertRaises(ValueError):
            self.evidence(replace(self.row, contract='calendar'))
        with self.assertRaises(TypeError):
            self.view(self.evidence(self.row)).evaluate(self.row.consumer_version, facts={})


    def test_finding_is_not_receipt_of_a_report_by_the_regional_service(self):
        receipt = replace(self.row, contract='administrative-event',
                          consumer_version='PUG-LR4-2017:Art.2(3):v1',
                          predicate='the Regional Plant Health Service has received a report of actual or presumed presence of the specified pest')
        evidence = self.evidence(receipt)
        result = self.view(evidence).reader(self.snapshot.version(receipt.consumer_version, receipt.event_date),
                                           receipt.predicate)
        self.assertTrue(result.truth)
        for wrong in ['official-finding', 'evaluation-context']:
            with self.assertRaises(ValueError):
                self.evidence(replace(receipt, contract=wrong))

    def test_owner_tuple_requires_receipt_evidence(self):
        receipt = replace(self.row, contract='administrative-event', event_date=date(2022, 5, 1),
                          consumer_version='PUG-DGR343-2022:notice-prescription-issuance:v1',
                          predicate='cadastral and owner data received')
        evidence = self.evidence(receipt)
        view = evidence.view(context=receipt.context, event_date=receipt.event_date,
                             known_through=datetime(2026, 9, 8, tzinfo=timezone.utc))
        result = view.reader(self.snapshot.version(receipt.consumer_version, receipt.event_date), receipt.predicate)
        self.assertTrue(result.truth)
        for held_tuple in ['party-land-standing', 'case-prescription']:
            with self.assertRaises(ValueError):
                self.evidence(replace(receipt, contract=held_tuple))

    def test_retention_policy_does_not_fill_continuing_performance(self):
        version = 'PUG-DGR538-2021:Art7(3)-policy:v1'
        at = date(2021, 5, 1)
        # C decides 'effective plan interval' from the event date; D supplies only the date.
        rows = tuple(replace(self.row, identity=predicate, predicate=predicate, contract=contract,
                             consumer_version=version, event_date=at) for predicate, contract in [
            ('official protected status', 'protected-status'),
            ('official negative result', 'official-finding')])
        def result(assertions):
            evidence = self.evidence(*assertions)
            return evidence.view(context=self.row.context, event_date=at,
                                 known_through=datetime(2026, 9, 8, tzinfo=timezone.utc)).evaluate(version)
        self.assertIsNone(result(rows).truth)
        # A synthetic complete determination includes every continuing condition;
        # one isolated treatment or observation would not support this reading.
        continuing = replace(rows[0], identity='continuing', predicate='continuing Article 7(3) conditions',
                             contract='survey-performance',
                             support=(Support('public', 'synthetic complete record',
                                              'Hypothetical complete current safeguards determination'),))
        self.assertTrue(result((*rows, continuing)).truth)
        self.assertFalse(result((*rows, replace(continuing, value=False))).truth)
        interval = replace(rows[0], identity='interval', predicate='effective plan interval',
                           contract='evaluation-context')
        with self.assertRaisesRegex(ValueError, 'cannot be supplied'):
            result((*rows, continuing, interval))



class AdministrativeInputTests(unittest.TestCase):
    def test_download_population_cannot_supply_required_members(self):
        downloaded = PublishedPopulation('scope1', frozenset({'row1'}), frozenset({'row1'}), 'source')
        self.assertTrue(downloaded.acquisition_complete)
        with self.assertRaises(TypeError):
            completion_support(downloaded, frozenset({'row1'}), completion_scope='scope1',
                               completion_history_complete=True)
        required = RequiredPopulation('scope1', frozenset({'member1', 'member2'}), True,
                                      Support('source', 'inventory1', 'Synthetic two-member population'))
        result = completion_support(required, frozenset({'member1'}), completion_scope='scope1',
                                    completion_history_complete=False)
        self.assertIsNone(result.truth)
        with self.assertRaises(ValueError):
            completion_support(required, required.members, completion_scope='another-scope',
                               completion_history_complete=True)



    def test_calendar_effective_change_and_no_invented_holiday(self):
        calendar = national_calendar()
        self.assertNotIn(date(2025, 10, 4), calendar.holidays)
        self.assertIn(date(2026, 10, 4), calendar.holidays)
        self.assertTrue(calendar.working(date(2026, 10, 5)))
        self.assertTrue(calendar.working(date(2024, 11, 4)))
        self.assertTrue(calendar.working(date(2026, 5, 8)))
        self.assertEqual(deadline(date(2026, 4, 3), 1, 'working_days', calendar=calendar,
                                  roll_forward=False), date(2026, 4, 7))
        with self.assertRaises(MissingInput):
            calendar.working(date(2027, 1, 2))

    def test_source_date_cannot_supply_hours_or_another_recipient(self):
        event = AdministrativeEvent('receipt1', 'delivery', 'document1', 'recipient1', date(2026, 1, 12),
                                    Support('source', 'row1', 'Test date-only receipt'))
        self.assertEqual(event.anchor(kind='delivery', document='document1', recipient='recipient1', precision='date'), date(2026, 1, 12))
        with self.assertRaises(MissingInput):
            event.anchor(kind='delivery', document='document1', recipient='recipient1', precision='instant')
        for kind, recipient in [('acceptance', 'recipient1'), ('delivery', 'recipient2')]:
            with self.assertRaises(ValueError):
                event.anchor(kind=kind, document='document1', recipient=recipient, precision='date')

    def test_source_date_conflict_is_not_silently_normalized(self):
        self.assertEqual(sampling_date({'DATA_PRELIEVO': datetime(2025, 10, 9)}), date(2025, 10, 9))
        with self.assertRaises(ValueError):
            sampling_date({'DATA_PRELIEVO': date(2025, 10, 9), 'DATA_RILEVAMENTO': date(2025, 10, 10)})


if __name__ == '__main__':
    unittest.main()

"""Administrative aperture counterexamples, not source-coverage certification."""
from dataclasses import replace
from datetime import date, datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cordon_c.core import Snapshot
from cordon_d.evidence import Assertion, Evidence, Source, Support, file_digest
from inventory import inventory


ROOT = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
OMISSION = ('evidence establishes that the owner, occupier or holder omitted a valid '
            'prescription to remove plants with a quarantine pest present')
REMOVAL = 'IT-DLGS-19-2021:Art.55(13):coercive-removal:v1'
SANCTION = 'IT-DLGS-19-2021:Art.55(13):omitted-removal-sanction:v1'


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = Snapshot.load(ROOT)
        self.contracts = {r['id']: r for r in json.loads((D / 'contracts.json').read_text())['contracts']}
        self.bindings = {r['predicate']: frozenset(r['contracts']) for r in
                         json.loads((D / 'predicate-contracts.json').read_text())['bindings']}
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'record.txt').write_text('Hypothetical administrative record; no actual case asserted.')
        self.source = Source('record', 'record.txt', file_digest(self.root / 'record.txt'),
                             'official-record', 'public')
        self.row = Assertion('omission', 'removal-performance', 'counterexample', date(2026, 1, 12),
                             datetime(2026, 1, 13, tzinfo=timezone.utc), REMOVAL, OMISSION, True,
                             (Support('record', 'hypothetical record',
                                      'Assumed valid prescription and proven omitted performance for this example'),))

    def evidence(self, *rows):
        return Evidence(self.snapshot, (self.source,), rows, self.contracts, self.bindings, self.root)

    def view(self, evidence):
        return evidence.view(context='counterexample', event_date=self.row.event_date,
                             known_through=datetime(2026, 9, 9, tzinfo=timezone.utc))

    def test_same_omission_supports_removal_but_cannot_activate_fine(self):
        view = self.view(self.evidence(self.row))
        result = view.evaluate(REMOVAL)
        self.assertTrue(result.truth)
        self.assertEqual(result.effect, self.snapshot.versions[REMOVAL]['true_effect'])
        # A shared predicate and an otherwise admissible family do not admit its
        # separate fine consumer, even through direct Evidence construction.
        with self.assertRaisesRegex(ValueError, 'consumer is deferred'):
            self.evidence(replace(self.row, consumer_version=SANCTION))
        with self.assertRaisesRegex(ValueError, 'consumer is deferred'):
            view.reader(self.snapshot.versions[SANCTION], OMISSION)
        with self.assertRaisesRegex(ValueError, 'consumer is deferred'):
            view.evaluate(SANCTION.rsplit(':', 1)[0])

    def test_intrinsic_and_reference_only_deferred_rows_cannot_bypass_admission(self):
        view = self.view(self.evidence())
        for consumer in ('IT-DLGS-19-2021:Art.55(30):regional-sanction-competence',
                         'IT-L689-1981:Art.16:reduced-payment',
                         'IT-L689-1981:Art.18:defence-and-hearing-request'):
            with self.subTest(consumer=consumer):
                with self.assertRaisesRegex(ValueError, 'consumer is deferred'):
                    view.evaluate(consumer)

    def test_deferred_preparation_does_not_delete_adoption_antecedent(self):
        view = self.view(self.evidence())
        with self.assertRaisesRegex(ValueError, 'consumer is deferred'):
            view.evaluate('IT-DLGS-19-2021:Art.27(4):prepare-national-proposal')
        # The adopted programme still needs evidence of its actual antecedent;
        # it does not demand operation of the excluded proposal workflow.
        result = view.evaluate('IT-DLGS-19-2021:Art.27(4):adopt-national-programme')
        self.assertIsNone(result.truth)
        self.assertTrue(result.needs)
        bindings = json.loads((D / 'additional-input-contracts.json').read_text())['reference_bindings']
        row = next(r for r in bindings if r['consumer'] == 'IT-DLGS-19-2021:Art.27(4):adopt-national-programme')
        self.assertEqual(row['kind'], 'actual-performance')
        self.assertIn('administrative-event', row['contracts'])

    def test_execution_liability_survives_without_opening_collection(self):
        consumer = 'IT-DLGS-19-2021:Art.55(13):coercive-removal-costs:v1'
        predicate = 'the cost target is the proven offender'
        liable = replace(self.row, identity='liable-offender', contract='execution-cost',
                         consumer_version=consumer, predicate=predicate,
                         support=(Support('record', 'hypothetical work and obligor record',
                                          'Assumed proven chargeable offender for this example'),))
        view = self.view(self.evidence(self.row, liable))
        self.assertTrue(view.reader(self.snapshot.versions[consumer], predicate).truth)
        # Identity alone does not prove the separately required execution fact.
        self.assertIsNone(view.evaluate(consumer).truth)
        with self.assertRaisesRegex(ValueError, 'consumer is deferred'):
            view.evaluate('IT-DLGS-19-2021:Art.32(3):recovery-right')
        self.assertIn('execution-cost', self.contracts)

    def test_projection_keeps_source_text_and_shared_consumer_separate(self):
        projection = inventory(ROOT)
        row = next(r for r in projection['predicates'] if r['predicate'] == OMISSION)
        self.assertIn(SANCTION, row['consumers'])
        self.assertNotIn(SANCTION, row['admitted_consumers'])
        self.assertIn(REMOVAL, row['admitted_consumers'])
        deferred = next(r for r in projection['declared_evidence']
                        if r['consumers'] == ['IT-L689-1981:Art.17:violation-report:v1'])
        self.assertEqual(deferred['admitted_consumers'], [])
        payloads = json.loads((D / 'additional-input-contracts.json').read_text())['declared_evidence']
        self.assertEqual(next(r for r in payloads if r['evidence'] == deferred['evidence'])['contracts'], [])


if __name__ == '__main__':
    unittest.main()

"""Transferable regressions for the explicit, unaccepted prescription amendment.

Synthetic facts exercise the candidate's legal composition. Source population,
recipient and inheritance qualification remain D's independent integration work.
"""

import contextlib
import copy
import csv
from datetime import date, datetime
from decimal import Decimal
import io
import json
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from cordon_c import evaluate
from cordon_c.bindings import leaves, noncommencement_facts
from cordon_c.temporal import WorkingCalendar
from test_prescribed_terms import term
from test_prescription_candidate import ROOT, PROPOSAL, JURISDICTION, LEDGER, expand_candidate, verified_candidate_snapshot

import generate_stage_b as generator


class PrescriptionMigration(unittest.TestCase):
    consumer = 'SOURCE-CLAUSE:notification-noncommencement-direction'
    required = 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED'
    absent = 'noncommencement of that work by the source deadline is established'
    at = date(2026, 9, 8)
    zone = ZoneInfo('Europe/Rome')

    @classmethod
    def setUpClass(cls):
        cls.proposal = json.loads((ROOT / PROPOSAL).read_text())
        cls.documents = expand_candidate(cls.proposal)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.snapshot = verified_candidate_snapshot(cls.proposal)

    def setUp(self):
        self.row = self.snapshot.version(self.consumer, self.at)
        clocks = [row for row in self.snapshot.clocks.values() if row['consumer_decision'] == self.consumer]
        self.assertEqual(len(clocks), 1)
        self.clock = clocks[0]

    def qualified_facts(self):
        return {(self.row['provision_version_id'], predicate): True
                for predicate in leaves(self.row['condition_ast'])}

    def test_every_noncommencement_guard_is_consequential(self):
        facts = self.qualified_facts()
        self.assertEqual(evaluate(self.snapshot, self.consumer, self.at, facts).effect, self.required)
        atoms = self.row['condition_ast']['route_table'][0]['when']['all_of']
        for index, atom in enumerate(atoms):
            key = self.row['provision_version_id'], atom['predicate']
            for truth in (False, None):
                with self.subTest(guard=atom['predicate'], truth=truth):
                    incomplete = dict(facts)
                    if truth is None:
                        del incomplete[key]
                    else:
                        incomplete[key] = truth
                    self.assertNotEqual(evaluate(self.snapshot, self.consumer, self.at, incomplete).effect, self.required)
                    mutant = copy.deepcopy(self.snapshot)
                    mutant.version(self.consumer, self.at)['condition_ast']['route_table'][0]['when']['all_of'].pop(index)
                    self.assertEqual(evaluate(mutant, self.consumer, self.at, incomplete).effect, self.required)

    def test_missing_completion_cannot_prove_noncommencement(self):
        facts = self.qualified_facts()
        facts[(self.row['provision_version_id'], 'removal completion recorded')] = False
        del facts[(self.row['provision_version_id'], self.absent)]
        result = evaluate(self.snapshot, self.consumer, self.at, facts)
        self.assertIsNone(result.truth)
        self.assertIsNone(result.effect)

    def test_actual_prescribed_period_changes_the_candidate_result(self):
        calendar = WorkingCalendar(date(2026, 1, 1), date(2027, 1, 1), frozenset(), frozenset({5, 6}))
        for days, expected in ((3, self.required), (7, 'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')):
            with self.subTest(days=days):
                facts = self.qualified_facts()
                facts.update(noncommencement_facts(
                    self.snapshot, self.clock['clock_id'], self.at,
                    prescribed_term=term(magnitude=Decimal(days)),
                    notification=datetime(2026, 9, 4, 12, tzinfo=self.zone),
                    evaluated_at=datetime(2026, 9, 9, tzinfo=self.zone),
                    qualifying_commencements={}, commencement_records_complete=True,
                    zone=self.zone, calendar=calendar))
                self.assertEqual(evaluate(self.snapshot, self.consumer, self.at, facts).effect, expected)

    def test_source_clock_semantics_survive_csv_serialization_without_a_default(self):
        producer = self.snapshot.versions[self.clock['producer_provision_version_id']]
        self.assertIn(self.clock['source_phrase'], producer['source_quote'])
        self.assertEqual(self.clock['anchor'], {
            'kind': 'event', 'event': 'legally sufficient notification of the operative prescription to this recipient',
            'record': 'OPERATOR_RECORD'})
        self.assertEqual(self.clock['completion'], {
            'kind': 'record', 'ref': 'concrete commencement of the removal work specified by this prescription clause'})
        self.assertEqual(self.clock['consequence_on_expiry'], {'kind': 'none', 'ref': None})
        with tempfile.TemporaryDirectory(prefix='cordon-prescription-csv-') as directory:
            path = Path(directory) / 'clocks.csv'
            generator.write(path, list(self.snapshot.clocks.values()))
            with path.open(newline='') as handle:
                emitted = next(row for row in csv.DictReader(handle) if row['clock_id'] == self.clock['clock_id'])
        self.assertEqual(json.loads(emitted['magnitude']), {'source_input': 'prescribed-term'})
        self.assertEqual((emitted['unit'], emitted['bound'], emitted['kind']), ('', 'exact', 'deadline'))
        for field in ('anchor', 'completion', 'consequence_on_expiry'):
            self.assertEqual(json.loads(emitted[field]), self.clock[field])
        for field in ('producer_provision_version_id', 'consumer_decision', 'source_phrase'):
            self.assertEqual(emitted[field], self.clock[field])

    def test_retained_corrections_keep_their_meaning_without_minting_new_clocks(self):
        accepted_a = {row['provision_version_id']: row for row in json.loads((ROOT / JURISDICTION).read_text())}
        accepted_b = json.loads((ROOT / LEDGER).read_text())
        replaced = {row['provision_version_id'] for row in self.proposal['stage_a']['replace']}
        self.assertTrue(replaced)
        removed = {accepted_a[identity]['stable_provision_id'] for identity in self.proposal['stage_a']['remove']}
        for identity in replaced:
            with self.subTest(correction=identity):
                previous = accepted_a[identity]
                candidate = self.snapshot.versions[identity]
                for field in ('source_quote', 'source_quote_sha256', 'condition_ast', 'true_effect', 'false_effect'):
                    self.assertEqual(candidate[field], previous[field])
                self.assertTrue(set(previous['external_dependencies']) & removed)
                self.assertEqual(set(candidate['external_dependencies']),
                                 (set(previous['external_dependencies']) - removed) | {self.consumer})
        owned = lambda ledger: {row['clock_id']: row for row in ledger['clocks']
                                if row['producer_provision_version_id'] in replaced}
        self.assertEqual(owned(self.documents[LEDGER]), owned(accepted_b))


if __name__ == '__main__':
    unittest.main()

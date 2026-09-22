"""Exercise candidate predicates through the existing evidence consumer.

These small records are synthetic mechanism tests. Actual source qualification
and unavailable notice/performance remain separate integration evidence.
"""
import contextlib
from dataclasses import replace
from datetime import date, datetime, timezone
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cordon_d.evidence import Assertion, Evidence, Source, Support, file_digest
from test_prescription_candidate import (ROOT, PREDICATES, expand_candidate,
                                         verified_candidate_snapshot)


class PrescriptionEvidence(unittest.TestCase):
    consumer = 'SOURCE-CLAUSE:notification-noncommencement-direction:v1'
    predicate = ('the operative prescription expressly directs coercive removal '
                 'after noncommencement within its stated notification-based term')
    notified = 'legally sufficient notification of that prescription to this recipient has occurred'
    at = date(2026, 9, 8)
    known = datetime(2026, 9, 9, tzinfo=timezone.utc)

    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.snapshot = verified_candidate_snapshot()
        candidate = expand_candidate()
        cls.bindings = {r['predicate']: frozenset(r['contracts']) for r in candidate[PREDICATES]['bindings']}
        cls.contracts = {r['id']: r for r in json.loads(
            (ROOT / 'regulation/stage-d/contracts.json').read_text())['contracts']}

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / 'source.txt').write_text('Synthetic operative-clause evidence; not an actual official act.')
        self.source = Source('source', 'source.txt', file_digest(self.root / 'source.txt'),
                             'official-record', 'public')
        self.assertion = Assertion('clause-reading', 'case-prescription', 'work-context', self.at,
            self.known, self.consumer, self.predicate, True,
            (Support('source', 'point 8', 'Synthetic independently qualified clause-form reading'),))

    def evidence(self, *assertions, bindings=None):
        return Evidence(self.snapshot, (self.source,), assertions, self.contracts,
                         self.bindings if bindings is None else bindings, self.root)

    def view(self, evidence, **changes):
        return evidence.view(**(dict(context='work-context', event_date=self.at,
                                     known_through=self.known) | changes))

    def test_supported_clause_reaches_evidence_but_cannot_supply_remaining_six_facts(self):
        view = self.view(self.evidence(self.assertion))
        row = self.snapshot.version(self.consumer, self.at)
        self.assertTrue(view.reader(row, self.predicate).truth)
        result = view.evaluate(self.consumer)
        self.assertIsNone(result.truth)
        self.assertIsNone(result.effect)
        self.assertEqual(len(result.needs), 6)
        self.assertTrue(any(self.notified in need for need in result.needs))
        self.assertTrue(any('noncommencement of that work' in need for need in result.needs))

    def test_old_bindings_reproduce_the_reviewed_failure(self):
        accepted = json.loads((ROOT / PREDICATES).read_text())
        bindings = {r['predicate']: frozenset(r['contracts']) for r in accepted['bindings']}
        with self.assertRaisesRegex(ValueError, 'outside the authored consumer contract'):
            self.evidence(self.assertion, bindings=bindings)

    def test_clause_evidence_cannot_be_relabelled_as_actual_recipient_notice(self):
        with self.assertRaisesRegex(ValueError, 'outside the authored consumer contract'):
            self.evidence(replace(self.assertion, predicate=self.notified))
        with self.assertRaisesRegex(ValueError, 'outside the authored consumer contract'):
            self.evidence(replace(self.assertion, contract='calendar'))

    def test_source_supported_different_form_defeats_only_this_ground(self):
        different = replace(self.assertion, value=False,
            support=(Support('source', 'other point', 'Synthetic clause directs completion after election, not this form'),))
        result = self.view(self.evidence(different)).evaluate(self.consumer)
        self.assertFalse(result.truth)
        self.assertEqual(result.effect, 'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_conflict_and_other_work_context_remain_unknown(self):
        changed = replace(self.assertion, identity='competing-reading', value=False)
        view = self.view(self.evidence(self.assertion, changed))
        self.assertIsNone(view.evaluate(self.consumer).truth)
        self.assertTrue(any('conflicting evidence' in need for need in view.evaluate(self.consumer).needs))
        other = self.view(self.evidence(self.assertion), context='other-work')
        result = other.evaluate(self.consumer)
        self.assertIsNone(result.truth)
        self.assertEqual(len(result.needs), 7)


if __name__ == '__main__':
    unittest.main()

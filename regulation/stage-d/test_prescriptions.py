"""A prescription's own stated term and populations reach the Art. 21-ter rule without registration.

Readings are the implementer's, from the originals named below; notification
instants are synthetic. Facet 3 reads its own instances.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import unittest

from cordon_c.bindings import leaves, merge_facts, noncommencement_facts
from cordon_c.core import Evaluation, MissingInput, Snapshot, evaluate
from cordon_c.quantities import clock_boundary
from cordon_c.temporal import end_of_day
from cordon_d.calendar import national_calendar
from cordon_d.prescriptions import lawfully_due

ROOT = Path(__file__).resolve().parents[2]
ROME = ZoneInfo('Europe/Rome')
RULE = 'IT-L241-A21TER:Art.21-ter(1):stated-term-coercive-direction'
CLOCK = 'B-CLK-IT-L241-21TER-stated-commencement-term'
CLAUSE, WORK, COERCE = (
    'the operative prescription governing this recipient states in its operative part a commencement term '
    'running from notification and commits the Osservatorio to direct coercive removal on noncommencement',
    'the commencement work the prescription states is lawfully due from this recipient',
    'removal of the population the prescription names for coercion is lawfully due')
NOTICE = 'legally sufficient notification of that prescription to this recipient has occurred'

# DDS 108/2024 (BURP n. 68 of 22-8-2024; store 47b107a6…3a51a3d), operative point 11: "qualora il
# proprietario/conduttore non proceda al concreto avvio delle attività di estirpazione della pianta infetta e
# delle piante ricadenti nei 50 m entro massimo 10 giorni dall'avvenuta notifica, la Sezione Osservatorio
# fitosanitario disporrà l'abbattimento coatto delle piante infette, per il tramite dell'ARIF". No A row names it.
DDS108 = dict(instrument='REG-PUGLIA-U181-DIR-2024-00108', clause=True, term=('10', 'giorni'),
              anchor="dall'avvenuta notifica", commencement='la pianta infetta e le piante ricadenti nei 50 m',
              coercive='le piante infette', executor='ARIF')


class StatedTermRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.calendar = national_calendar()

    def effect(self, record, at, *, notified, evaluated, work=True, coerce=True, refs=(), results=None,
               commencements=None):
        row = self.s.version(RULE, at)
        due = dict(instrument=record['instrument'], governing_references=refs, results=results or {})
        facts = {(row['provision_version_id'], CLAUSE): record['clause'],
                 (row['provision_version_id'], NOTICE): True,
                 (row['provision_version_id'], WORK): lawfully_due(self.s, at, **due, reading=work),
                 (row['provision_version_id'], COERCE): lawfully_due(self.s, at, **due, reading=coerce)}
        if record['term'] is not None:
            facts = merge_facts(facts, noncommencement_facts(
                self.s, CLOCK, at, notification=notified, evaluated_at=evaluated, stated_term=record['term'],
                qualifying_commencements=commencements or {}, commencement_records_complete=True,
                zone=ROME, calendar=self.calendar))
        return evaluate(self.s, RULE, at, facts).effect

    def test_unregistered_order_computes_from_its_own_stated_term(self):
        at, notified = date(2024, 9, 2), datetime(2024, 9, 2, 9, tzinfo=ROME)
        self.assertFalse(any(r['instrument_id'] == DDS108['instrument'] for r in self.s.versions.values()))
        # Independent expectation: ten calendar days after a Monday notice ends on a working Thursday.
        expected = end_of_day(notified.date() + timedelta(days=10), ROME)
        self.assertEqual(clock_boundary(self.s, CLOCK, at, notified, zone=ROME, calendar=self.calendar,
                                        stated_term=DDS108['term']), expected)
        after = expected + timedelta(hours=1)
        self.assertEqual(self.effect(DDS108, at, notified=notified, evaluated=after),
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        self.assertEqual(self.effect(DDS108, at, notified=notified, evaluated=after,
                                     commencements={'start': expected - timedelta(days=1)}),
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')
        longer = dict(DDS108, term=('15', 'giorni'))
        self.assertEqual(self.effect(longer, at, notified=notified, evaluated=after),
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_no_term_gives_no_deadline(self):
        at, notified = date(2024, 9, 2), datetime(2024, 9, 2, 9, tzinfo=ROME)
        with self.assertRaises(MissingInput):
            clock_boundary(self.s, CLOCK, at, notified, zone=ROME, calendar=self.calendar)
        silent = dict(DDS108, clause=False, term=None)
        self.assertEqual(self.effect(silent, at, notified=notified, evaluated=notified + timedelta(days=30)),
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_coercive_population_is_a_distinct_fact(self):
        # DDS 147/2024 point 9: commencement covers "piante infette e ... piante ricadenti nei 50 m";
        # coercion covers "piante infette" only. The same facts differ only in the coercive population.
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2024-00147')
        at, notified = date(2024, 12, 2), datetime(2024, 12, 2, 9, tzinfo=ROME)
        evaluated = notified + timedelta(days=12)
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated, coerce=True),
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated, coerce=False),
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_case_delta_of_the_instrument_holds_lawful_dueness(self):
        hold = 'REG-PUGLIA-U181-DIR-2023-00045:case-delta:pending-monumental-recognition-hold'
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2023-00045')
        at, notified = date(2023, 6, 5), datetime(2023, 6, 5, 9, tzinfo=ROME)
        evaluated = notified + timedelta(days=12)
        unresolved = evaluate(self.s, hold, at, {})
        self.assertIsNone(unresolved.truth)
        for refs, results in (((), {}), ((hold,), {hold: unresolved})):
            due = lawfully_due(self.s, at, instrument=record['instrument'], governing_references=refs,
                               results=results, reading=True)
            self.assertIsNone(due.truth)
            self.assertTrue(any(hold in need for need in due.needs))
            self.assertIsNone(self.effect(record, at, notified=notified, evaluated=evaluated,
                                          refs=refs, results=results))
        vid = self.s.version(hold, at)['provision_version_id']
        resolved = evaluate(self.s, hold, at, {(vid, p): p != 'pending recognition decision'
                                               for p in leaves(self.s.version(hold, at)['condition_ast'])})
        self.assertIs(resolved.truth, False)
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated,
                                     refs=(hold,), results={hold: resolved}),
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')


if __name__ == '__main__':
    unittest.main()

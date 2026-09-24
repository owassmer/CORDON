"""A prescription's own stated term and populations reach the Art. 21-ter rule without registration.

Readings are the implementer's, from the originals named below; notification
instants are synthetic. Facet 3 reads its own instances.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import unittest

from cordon_c.bindings import leaves, listing_facts, mass_publicity_facts, merge_facts, noncommencement_facts
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
INDIVIDUAL = 'IT-L241-A21BIS:Art.21-bis(1):individual-communication-effect'

# DDS 108/2024 (BURP n. 68 of 22-8-2024; store 47b107a6…3a51a3d), operative point 11: "qualora il
# proprietario/conduttore non proceda al concreto avvio delle attività di estirpazione della pianta infetta e
# delle piante ricadenti nei 50 m entro massimo 10 giorni dall'avvenuta notifica, la Sezione Osservatorio
# fitosanitario disporrà l'abbattimento coatto delle piante infette, per il tramite dell'ARIF". No A row names it.
DDS108 = dict(instrument='REG-PUGLIA-U181-DIR-2024-00108', clause=True, term=('10', 'giorni'),
              commencement='la pianta infetta e le piante ricadenti nei 50 m', coercive='le piante infette',
              executor='ARIF')
CORRECTION_165 = 'REG-PUGLIA-U181-DIR-2024-00165:case-delta:annex-only-municipality-correction'
CORRECTION_11 = 'REG-PUGLIA-U181-DIR-2025-00011:case-delta:ownership-correction'


class StatedTermRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.calendar = national_calendar()

    def personal(self, at, effected):
        """Art. 21-bis personal-communication events for a restrictive act with no immediate-effect clause."""
        row = self.s.version(INDIVIDUAL, at)
        return {(row['provision_version_id'], p): effected if p.startswith('the communication to that recipient')
                else p != 'a valid immediate-effect exception applies'
                for p in leaves(row['condition_ast'])
                if effected is not None or not p.startswith('the communication to that recipient')}

    def effect(self, record, at, *, notified, evaluated, work=True, coerce=True, refs=(), results=None,
               commencements=None, notice=None):
        row = self.s.version(RULE, at)
        due = dict(instrument=record['instrument'], governing_references=refs, results=results or {})
        facts = {(row['provision_version_id'], CLAUSE): record['clause'],
                 (row['provision_version_id'], WORK): lawfully_due(self.s, at, **due, reading=work),
                 (row['provision_version_id'], COERCE): lawfully_due(self.s, at, **due, reading=coerce)}
        facts |= self.personal(at, True) if notice is None else notice
        if record['term'] is not None:
            facts = merge_facts(facts, noncommencement_facts(
                self.s, CLOCK, at, notification=notified, evaluated_at=evaluated, stated_term=record['term'],
                qualifying_commencements=commencements or {}, commencement_records_complete=True,
                zone=ROME, calendar=self.calendar))
        return evaluate(self.s, RULE, at, facts).effect

    def settled(self, sid, at):
        """A governing row's result with every leaf established; only its resolution matters here."""
        row = self.s.version(sid, at)
        result = evaluate(self.s, sid, at, {(row['provision_version_id'], p): True
                                            for p in leaves(row['condition_ast'])})
        self.assertIsNotNone(result.truth)
        return result

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
        reached = dict(refs=(CORRECTION_165,), results={CORRECTION_165: self.settled(CORRECTION_165, at)})
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated, coerce=True, **reached),
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated, coerce=False, **reached),
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_correction_holds_the_order_it_corrects(self):
        # DDS 165/2024 replaces DDS 147/2024's annex 1/C; DDS 11/2025 replaces owners listed in DDS 188/2024.
        # A record that omits the correction leaves lawful dueness unknown, so no direction follows.
        for instrument, correction, at in (('REG-PUGLIA-U181-DIR-2024-00147', CORRECTION_165, date(2024, 12, 2)),
                                           ('REG-PUGLIA-U181-DIR-2024-00188', CORRECTION_11, date(2025, 3, 3))):
            with self.subTest(instrument=instrument):
                record = dict(DDS108, instrument=instrument)
                notified = datetime.combine(at, datetime.min.time(), ROME).replace(hour=9)
                evaluated = notified + timedelta(days=12)
                self.assertIn(instrument, self.s.version(correction, at)['corrects_instrument_ids'])
                own = tuple(need.removeprefix('governing A reference: ') for need in lawfully_due(
                    self.s, at, instrument=instrument, governing_references=(), results={}, reading=True).needs
                    if need != f'governing A reference: {correction}')
                results = {sid: self.settled(sid, at) for sid in own + (correction,)}
                due = lawfully_due(self.s, at, instrument=instrument, governing_references=own, results=results,
                                   reading=True)
                self.assertIsNone(due.truth)
                self.assertEqual(due.needs, {f'governing A reference: {correction}'})
                self.assertIsNone(self.effect(record, at, notified=notified, evaluated=evaluated, refs=own,
                                              results=results))
                self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated,
                                             refs=own + (correction,), results=results),
                                 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')

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
        request = "the Osservatorio's recognition request for this tree awaits decision"
        no_entry = listing_facts(self.s, at, own_entry=False, first_publication=None, definitive_decision=None,
                                 deletion=None, entry_history_complete=True)
        resolved = evaluate(self.s, hold, at, no_entry | {(vid, p): p != request
                                                          for p in leaves(self.s.version(hold, at)['condition_ast'])})
        self.assertIs(resolved.truth, False)
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated,
                                     refs=(hold,), results={hold: resolved}),
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')


class MassPublicityNotice(unittest.TestCase):
    """Owen's ruling 1 through the Art. 21-ter notice conjunct (adjudication F1, route (a)).

    Two otherwise identical records share one complete first-party 7-day albo posting; only whether the order
    states its own ground for posting differs. The ground is the variable under test, not a reading of DDS 108.
    A stated ground reads as DDS 63/2026 (store c88d31c9…7b48) and DDS 2/2023 print it: "mediante affissione per 7
    giorni nell'albo pretorio del Comune in cui ricadono le piante da estirpare tenuto conto dell'irreperibilità di
    alcuni destinatari e della gravosità per l'amministrazione di notificare i provvedimenti ai singoli beneficiari".
    """
    personal = StatedTermRule.personal

    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.calendar = national_calendar()

    def posting(self, at, ground):
        start = datetime(2024, 9, 2, 9, tzinfo=ROME)
        return mass_publicity_facts(self.s, at, ground_stated=ground, annulled_on_ground=False, posting_start=start,
                                    postings={'albo': (start, datetime(2024, 9, 10, tzinfo=ROME))},
                                    postings_complete=True, stated_period=('7', 'giorni'),
                                    evaluated_at=datetime(2024, 10, 1, tzinfo=ROME), zone=ROME)

    def direction(self, at, ground, *, personal):
        facts, day = self.posting(at, ground)
        evaluated = datetime(2024, 9, 21, 12, tzinfo=ROME)
        row = self.s.version(RULE, at)
        temporal = noncommencement_facts(self.s, CLOCK, at, notification=day, evaluated_at=evaluated,
                                         stated_term=DDS108['term'], qualifying_commencements={},
                                         commencement_records_complete=True, zone=ROME, calendar=self.calendar)
        record = dict(DDS108, term=None)
        due = dict(instrument=record['instrument'], governing_references=(), results={})
        base = {(row['provision_version_id'], CLAUSE): True,
                (row['provision_version_id'], WORK): lawfully_due(self.s, at, **due, reading=True),
                (row['provision_version_id'], COERCE): lawfully_due(self.s, at, **due, reading=True)}
        result = evaluate(self.s, RULE, at, merge_facts(base, temporal, facts, self.personal(at, personal)))
        return day, temporal, result

    def test_stated_ground_gives_notice_day_deadline_and_direction(self):
        at = date(2024, 9, 2)
        day, temporal, result = self.direction(at, True, personal=False)
        # Independent expectation: 7 days of posting from 2 September run through 9 September; the 10-day term
        # from that notice runs through 19 September, so it has lapsed on 21 September with no commencement.
        self.assertEqual(day, date(2024, 9, 9))
        self.assertEqual(clock_boundary(self.s, CLOCK, at, day, zone=ROME, calendar=self.calendar,
                                        stated_term=DDS108['term']), end_of_day(date(2024, 9, 19), ROME))
        self.assertTrue(all(v is True for v in temporal.values()))
        self.assertEqual(result.effect, 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')

    def test_no_ground_order_gets_no_deadline_and_no_required_direction(self):
        at = date(2024, 9, 2)
        day, temporal, result = self.direction(at, False, personal=False)
        self.assertIsNone(day)
        self.assertTrue(all(isinstance(v, Evaluation) and v.truth is None for v in temporal.values()))
        self.assertEqual(result.effect, 'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')
        # With no personal-communication record either, the direction stays unresolved and C names that record.
        day, _, result = self.direction(at, False, personal=None)
        self.assertIsNone(result.effect)
        self.assertTrue(any('the communication to that recipient has been effected' in need for need in result.needs))


if __name__ == '__main__':
    unittest.main()

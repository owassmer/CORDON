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
REQUIRED, NOT_ESTABLISHED = ('CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED',
                             'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')
INDIVIDUAL = 'IT-L241-A21BIS:Art.21-bis(1):individual-communication-effect'
MASS = 'IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route'
COMMUNICATED = ('the communication to that recipient has been effected, including in the forms prescribed for '
                'notification to the unreachable in the cases provided by the code of civil procedure')

# DDS 108/2024 (BURP n. 68 of 22-8-2024; store 47b107a6…3a51a3d), operative point 11: "qualora il
# proprietario/conduttore non proceda al concreto avvio delle attività di estirpazione della pianta infetta e
# delle piante ricadenti nei 50 m entro massimo 10 giorni dall'avvenuta notifica, la Sezione Osservatorio
# fitosanitario disporrà l'abbattimento coatto delle piante infette, per il tramite dell'ARIF". No A row names it.
DDS108 = dict(instrument='REG-PUGLIA-U181-DIR-2024-00108', clause=True, term=('10', 'giorni'),
              commencement='la pianta infetta e le piante ricadenti nei 50 m', coercive='le piante infette',
              executor='ARIF')
# DDS 113/2023 (BURP n. 96 of 26-10-2023; store dd2887be…d338), point 10: commencement and coercion "delle
# piante infette e delle piante ricadenti nei 50 m", term "10 giorni" from notification, ARIF; recipients
# "indicati nell'allegato 1/D". DDS 18/2024 withdraws its 50 m hosts from 14 March 2024.
DDS113 = dict(instrument='REG-PUGLIA-U181-DIR-2023-00113', clause=True, term=('10', 'giorni'),
              commencement='delle piante infette e delle piante ricadenti nei 50 m',
              coercive='delle piante infette e delle piante ricadenti nei 50 m', executor='ARIF',
              cohort=('allegato 1/D',))
CORRECTION_165 = 'REG-PUGLIA-U181-DIR-2024-00165:case-delta:annex-only-municipality-correction'
CORRECTION_11 = 'REG-PUGLIA-U181-DIR-2025-00011:case-delta:ownership-correction'
WITHDRAWAL = 'REG-PUGLIA-U181-DIR-2024-00018:case-delta:named-orders-50m-host-removal-withdrawn'
HOLD = 'REG-PUGLIA-U181-DIR-2023-00045:case-delta:pending-monumental-recognition-hold'
ST1 = 'REG-PUGLIA-U181-DIR-2025-00117:case-delta:st1-olive-nonmembership-boundary'
HOSTS = "the population in question holds the named order's host plants within 50 m of its infected plants"
LISTED = 'the population in question holds a plant the named order lists as infected'
HELD = 'the population in question holds held olives'
NOT_HELD = 'the population in question holds plants other than held olives'
OLIVES = 'the population in question holds uninfected, asymptomatic olives, none of them symptomatic or suspected'
NOT_OLIVES = 'the population in question holds plants other than uninfected, asymptomatic olives'
# The DDS 18/2024 row's populations: 50 m hosts only; hosts with listed infected plants; infected plants only.
HOSTS_ONLY, MIXED, INFECTED_ONLY = ({HOSTS: True, LISTED: False}, {HOSTS: True, LISTED: True},
                                    {HOSTS: False, LISTED: True})


class StatedTermRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.calendar = national_calendar()

    def due(self, record, at, predicate, *, reading=True, refs=(), results=None, positioned=False):
        return lawfully_due(self.s, at, instrument=record['instrument'], governing_references=refs,
                            results=results or {}, reading=reading, predicate=predicate, positioned=positioned,
                            cohort=record.get('cohort', ()))

    def personal(self, at, effected):
        """The Art. 21-ter notice conjunct's personal branch: whether communication to this recipient was effected."""
        if effected is None:
            return {}
        return {(self.s.version(RULE, at)['provision_version_id'], COMMUNICATED): effected}

    def result(self, record, at, *, notified, evaluated, work=True, coerce=True, refs=(), results=None,
               commencements=None, positioned=False, notice=None):
        row = self.s.version(RULE, at)
        held = dict(refs=refs, results=results, positioned=positioned)
        facts = {(row['provision_version_id'], CLAUSE): record['clause'],
                 (row['provision_version_id'], WORK): self.due(record, at, WORK, reading=work, **held),
                 (row['provision_version_id'], COERCE): self.due(record, at, COERCE, reading=coerce, **held)}
        facts |= self.personal(at, True) if notice is None else notice
        if record['term'] is not None:
            facts = merge_facts(facts, noncommencement_facts(
                self.s, CLOCK, at, notification=notified, evaluated_at=evaluated, stated_term=record['term'],
                qualifying_commencements=commencements or {}, commencement_records_complete=True,
                zone=ROME, calendar=self.calendar))
        return evaluate(self.s, RULE, at, facts)

    def effect(self, record, at, **kwargs):
        return self.result(record, at, **kwargs).effect

    def settled(self, sid, at):
        """A governing row's result with every leaf established; only its resolution matters here."""
        row = self.s.version(sid, at)
        result = evaluate(self.s, sid, at, {(row['provision_version_id'], p): True
                                            for p in leaves(row['condition_ast'])})
        self.assertIsNotNone(result.truth)
        return result

    def population(self, sid, at, facts):
        """The row's result with its other leaves established and the named population facts."""
        row = self.s.version(sid, at)
        return evaluate(self.s, sid, at, {(row['provision_version_id'], p): facts.get(p, True)
                                          for p in leaves(row['condition_ast'])})

    @staticmethod
    def per(sid, work, coerce=None):
        """Results keyed by (row, predicate): the work population's and the coercive population's."""
        return {(sid, WORK): work, (sid, COERCE): work if coerce is None else coerce}

    def vid(self, sid, at):
        return self.s.version(sid, at)['provision_version_id']

    def test_unregistered_order_computes_from_its_own_stated_term(self):
        at, notified = date(2024, 9, 2), datetime(2024, 9, 2, 9, tzinfo=ROME)
        self.assertFalse(any(r['instrument_id'] == DDS108['instrument'] for r in self.s.versions.values()))
        # Independent expectation: ten calendar days after a Monday notice ends on a working Thursday.
        expected = end_of_day(notified.date() + timedelta(days=10), ROME)
        self.assertEqual(clock_boundary(self.s, CLOCK, at, notified, zone=ROME, calendar=self.calendar,
                                        stated_term=DDS108['term']), expected)
        after = expected + timedelta(hours=1)
        self.assertEqual(self.effect(DDS108, at, notified=notified, evaluated=after), REQUIRED)
        self.assertEqual(self.effect(DDS108, at, notified=notified, evaluated=after,
                                     commencements={'start': expected - timedelta(days=1)}), NOT_ESTABLISHED)
        longer = dict(DDS108, term=('15', 'giorni'))
        self.assertEqual(self.effect(longer, at, notified=notified, evaluated=after), NOT_ESTABLISHED)

    def test_no_term_gives_no_deadline(self):
        at, notified = date(2024, 9, 2), datetime(2024, 9, 2, 9, tzinfo=ROME)
        with self.assertRaises(MissingInput):
            clock_boundary(self.s, CLOCK, at, notified, zone=ROME, calendar=self.calendar)
        silent = dict(DDS108, clause=False, term=None)
        self.assertEqual(self.effect(silent, at, notified=notified, evaluated=notified + timedelta(days=30)),
                         NOT_ESTABLISHED)

    def test_coercive_population_is_a_distinct_fact(self):
        # DDS 147/2024 point 9: commencement covers "piante infette e ... piante ricadenti nei 50 m";
        # coercion covers "piante infette" only. The same facts differ only in the coercive population.
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2024-00147')
        at, notified = date(2024, 12, 2), datetime(2024, 12, 2, 9, tzinfo=ROME)
        evaluated = notified + timedelta(days=12)
        reached = dict(refs=(CORRECTION_165,), results=self.per(CORRECTION_165, self.settled(CORRECTION_165, at)))
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated, coerce=True, **reached),
                         REQUIRED)
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated, coerce=False, **reached),
                         NOT_ESTABLISHED)

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
                own = tuple(need.removeprefix('governing A reference: ') for need in self.due(record, at, WORK).needs
                            if need != f'governing A reference: {correction}')
                results = {key: value for sid in own + (correction,)
                           for key, value in self.per(sid, self.settled(sid, at)).items()}
                due = self.due(record, at, WORK, refs=own, results=results)
                self.assertIsNone(due.truth)
                self.assertEqual(due.needs, {f'governing A reference: {correction}'})
                self.assertIsNone(self.effect(record, at, notified=notified, evaluated=evaluated, refs=own,
                                              results=results))
                self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated,
                                             refs=own + (correction,), results=results), REQUIRED)

    def test_case_delta_of_the_instrument_holds_lawful_dueness(self):
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2023-00045')
        at, notified = date(2023, 6, 5), datetime(2023, 6, 5, 9, tzinfo=ROME)
        evaluated = notified + timedelta(days=12)
        unresolved = evaluate(self.s, HOLD, at, {})
        self.assertIsNone(unresolved.truth)
        for refs, results in (((), {}), ((HOLD,), self.per(HOLD, unresolved))):
            due = self.due(record, at, WORK, refs=refs, results=results)
            self.assertIsNone(due.truth)
            self.assertTrue(any(HOLD in need for need in due.needs))
            self.assertIsNone(self.effect(record, at, notified=notified, evaluated=evaluated,
                                          refs=refs, results=results))
        vid = self.vid(HOLD, at)
        request = "the Osservatorio's recognition request for this tree awaits decision"
        no_entry = listing_facts(self.s, at, own_entry=False, first_publication=None, definitive_decision=None,
                                 deletion=None, entry_history_complete=True)
        resolved = evaluate(self.s, HOLD, at, no_entry | {(vid, p): p != request
                                                          for p in leaves(self.s.version(HOLD, at)['condition_ast'])})
        self.assertIs(resolved.truth, False)
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=evaluated,
                                     refs=(HOLD,), results=self.per(HOLD, resolved)), REQUIRED)

    # --- DDS 18/2024 withdraws the named orders' 50 m hosts, not their infected plants (PR #35) -------------

    def dds113(self, at=date(2024, 3, 14)):
        notified = datetime(2024, 3, 1, 9, tzinfo=ROME)
        return dict(notified=notified, evaluated=datetime(2024, 3, 14, 12, tzinfo=ROME)), at

    def test_from_14_march_2024_the_withdrawal_row_is_required(self):
        held, at = self.dds113()
        due = self.due(DDS113, at, WORK)
        self.assertIsNone(due.truth)
        self.assertEqual(due.needs, {f'governing A reference: {WITHDRAWAL}'})
        self.assertIsNone(self.effect(DDS113, at, **held))

    def test_a_reached_row_without_a_population_fact_names_its_population_predicates(self):
        held, at = self.dds113()
        vid = self.vid(WITHDRAWAL, at)
        for predicate in (WORK, COERCE):
            due = self.due(DDS113, at, predicate, refs=(WITHDRAWAL,))
            self.assertIsNone(due.truth)
            self.assertTrue({f'predicate: {vid} :: {HOSTS}', f'predicate: {vid} :: {LISTED}'} <= due.needs)
            self.assertFalse(any(need.startswith('result of') for need in due.needs))
        self.assertIsNone(self.effect(DDS113, at, refs=(WITHDRAWAL,), **held))

    def test_fifty_metre_hosts_only_are_not_due_however_long_the_term_has_lapsed(self):
        held, at = self.dds113()
        withdrawn = self.population(WITHDRAWAL, at, HOSTS_ONLY)
        self.assertEqual(withdrawn.effect, 'POPULATION_NOT_LAWFULLY_DUE')
        results = self.per(WITHDRAWAL, withdrawn)
        for predicate in (WORK, COERCE):
            self.assertIs(self.due(DDS113, at, predicate, refs=(WITHDRAWAL,), results=results).truth, False)
        late = dict(held, evaluated=datetime(2026, 9, 24, 12, tzinfo=ROME))
        for timing in (held, late):
            self.assertEqual(self.effect(DDS113, at, refs=(WITHDRAWAL,), results=results, **timing),
                             NOT_ESTABLISHED)

    def test_the_listed_infected_plants_stay_due(self):
        held, at = self.dds113()
        infected = self.population(WITHDRAWAL, at, INFECTED_ONLY)
        self.assertIs(infected.truth, False)
        self.assertEqual(infected.effect, 'NO_WITHDRAWAL_FOR_THIS_POPULATION')
        self.assertEqual(self.effect(DDS113, at, refs=(WITHDRAWAL,), results=self.per(WITHDRAWAL, infected), **held),
                         REQUIRED)
        # On every date after adoption, including after the area-state rows stop on 18 November 2024.
        for later in (date(2024, 11, 18), date(2026, 9, 24)):
            self.assertIs(self.due(DDS113, later, COERCE, refs=(WITHDRAWAL,),
                                   results=self.per(WITHDRAWAL, self.population(WITHDRAWAL, later, MIXED))).truth,
                          True)

    def test_the_coercive_population_is_due_in_part_naming_the_row(self):
        held, at = self.dds113()
        results = self.per(WITHDRAWAL, self.population(WITHDRAWAL, at, INFECTED_ONLY),
                           self.population(WITHDRAWAL, at, MIXED))
        self.assertEqual(results[(WITHDRAWAL, COERCE)].effect, 'LAWFULLY_DUE_IN_PART')
        c = self.result(DDS113, at, refs=(WITHDRAWAL,), results=results, **held)
        self.assertEqual(c.effect, REQUIRED)
        self.assertIn(self.vid(WITHDRAWAL, at), c.provisions)

    def test_each_predicate_reads_only_its_own_row_result(self):
        # A hosts-only recipient on the order's mixed coercive population: not due, and never coerced.
        held, at = self.dds113()
        results = self.per(WITHDRAWAL, self.population(WITHDRAWAL, at, HOSTS_ONLY),
                           self.population(WITHDRAWAL, at, MIXED))
        self.assertIs(self.due(DDS113, at, WORK, refs=(WITHDRAWAL,), results=results, positioned=True).truth, False)
        self.assertIs(self.due(DDS113, at, COERCE, refs=(WITHDRAWAL,), results=results).truth, True)
        self.assertEqual(self.effect(DDS113, at, refs=(WITHDRAWAL,), results=results, positioned=True, **held),
                         NOT_ESTABLISHED)

    def test_in_part_never_makes_a_record_without_a_position_due(self):
        held, at = self.dds113()
        mixed = self.per(WITHDRAWAL, self.population(WITHDRAWAL, at, MIXED))
        work = self.due(DDS113, at, WORK, refs=(WITHDRAWAL,), results=mixed)
        self.assertIsNone(work.truth)
        self.assertEqual(work.needs, {f"this recipient's position in {DDS113['instrument']}'s annex (allegato 1/D), "
                                      f'which {WITHDRAWAL} limits in part'})
        self.assertIsNone(self.result(DDS113, at, refs=(WITHDRAWAL,), results=mixed, **held).truth)
        # At a position the reading holds, naming the row; COERCE asks about the order's population.
        self.assertIs(self.due(DDS113, at, WORK, refs=(WITHDRAWAL,), results=mixed, positioned=True).truth, True)
        self.assertIs(self.due(DDS113, at, COERCE, refs=(WITHDRAWAL,), results=mixed).truth, True)
        # The same class rule for the DDS 45/2023 hold on a 45/2023 cohort record.
        hold_at = date(2023, 6, 5)
        record = dict(DDS113, instrument='REG-PUGLIA-U181-DIR-2023-00045', cohort=('allegato 1/C',))
        in_part = self.per(HOLD, self.population(HOLD, hold_at, {HELD: True, NOT_HELD: True}))
        self.assertEqual(in_part[(HOLD, WORK)].effect, 'LAWFULLY_DUE_IN_PART')
        work = self.due(record, hold_at, WORK, refs=(HOLD,), results=in_part)
        self.assertIsNone(work.truth)
        self.assertEqual(work.needs, {f"this recipient's position in {record['instrument']}'s annex (allegato 1/C), "
                                      f'which {HOLD} limits in part'})

    def test_a_row_the_record_does_not_require_changes_nothing(self):
        # DDS 108/2024 is not named by DDS 18/2024: the row passed as reached and withdrawn is ignored.
        at, notified = date(2024, 9, 2), datetime(2024, 9, 2, 9, tzinfo=ROME)
        results = self.per(WITHDRAWAL, self.population(WITHDRAWAL, at, HOSTS_ONLY))
        c = self.result(DDS108, at, notified=notified, evaluated=notified + timedelta(days=11), refs=(WITHDRAWAL,),
                        results=results)
        self.assertEqual(c.effect, REQUIRED)
        self.assertNotIn(self.vid(WITHDRAWAL, at), c.provisions)

    def test_a_124_record_of_fifty_metre_hosts_reaching_the_row_is_not_due(self):
        # Guard for the drop-124/2023 mutation: the row is required only because it names the order.
        record = dict(DDS113, instrument='REG-PUGLIA-U181-DIR-2023-00124')
        held, at = self.dds113()
        results = self.per(WITHDRAWAL, self.population(WITHDRAWAL, at, HOSTS_ONLY))
        self.assertIs(self.due(record, at, WORK, refs=(WITHDRAWAL,), results=results, positioned=True).truth, False)
        self.assertEqual(self.effect(record, at, refs=(WITHDRAWAL,), results=results, positioned=True, **held),
                         NOT_ESTABLISHED)

    def test_a_population_wholly_of_held_olives_is_not_due_while_the_hold_resolves(self):
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2023-00045')
        at, notified = date(2023, 6, 5), datetime(2023, 6, 5, 9, tzinfo=ROME)
        wholly = self.per(HOLD, self.population(HOLD, at, {HELD: True, NOT_HELD: False}))
        self.assertEqual(wholly[(HOLD, WORK)].effect, 'POPULATION_NOT_LAWFULLY_DUE')
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=notified + timedelta(days=12),
                                     refs=(HOLD,), results=wholly), NOT_ESTABLISHED)

    def test_the_infected_plant_beside_held_olives_stays_due_naming_the_hold(self):
        # Work population: the infected plant; coercive population "le piante infette" plus held olives.
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2023-00045')
        at, notified = date(2023, 6, 5), datetime(2023, 6, 5, 9, tzinfo=ROME)
        results = self.per(HOLD, self.population(HOLD, at, {HELD: False, NOT_HELD: True}),
                           self.population(HOLD, at, {HELD: True, NOT_HELD: True}))
        self.assertEqual(results[(HOLD, COERCE)].effect, 'LAWFULLY_DUE_IN_PART')
        c = self.result(record, at, notified=notified, evaluated=notified + timedelta(days=12), refs=(HOLD,),
                        results=results)
        self.assertEqual(c.effect, REQUIRED)
        self.assertIn(self.vid(HOLD, at), c.provisions)
        self.assertTrue(self.vid(HOLD, at).endswith(':v2'))

    def test_st1_olive_row_withholds_only_a_population_wholly_of_uninfected_olives(self):
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2025-00117')
        at = date(2025, 7, 1)
        own = tuple(sorted(n.removeprefix('governing A reference: ') for n in self.due(record, at, WORK).needs))
        self.assertIn(ST1, own)
        others = {key: value for sid in own if sid != ST1 for key, value in self.per(sid, self.settled(sid, at)).items()}
        for facts, expected in (({OLIVES: True, NOT_OLIVES: False}, False),  # wholly uninfected olives
                                ({OLIVES: True, NOT_OLIVES: True}, True)):   # an infected almond with them
            with self.subTest(facts=facts):
                results = {**others, **self.per(ST1, self.population(ST1, at, facts))}
                due = self.due(record, at, COERCE, refs=own, results=results)
                self.assertIs(due.truth, expected)
                self.assertIn(self.vid(ST1, at), due.provisions)
        # An infected olive: the row resolves false and withholds nothing.
        row = self.s.version(ST1, at)
        infected = evaluate(self.s, ST1, at, {(row['provision_version_id'], p):
                                              p != 'plant not independently infected symptomatic or suspected'
                                              for p in leaves(row['condition_ast'])})
        self.assertIs(infected.truth, False)
        due = self.due(record, at, COERCE, refs=own, results={**others, **self.per(ST1, infected)})
        self.assertIs(due.truth, True)
        self.assertNotIn(self.vid(ST1, at), due.provisions)

    def test_lawful_dueness_reads_only_the_two_generic_names(self):
        # A resolved row whose effect is any other string withholds nothing.
        held, at = self.dds113()
        other = Evaluation(True, 'Hold visually qualifying, negative olives from removal')
        for predicate in (WORK, COERCE):
            self.assertIs(self.due(DDS113, at, predicate, refs=(WITHDRAWAL,), results=self.per(WITHDRAWAL, other),
                                   positioned=True).truth, True)


class MassPublicityNotice(unittest.TestCase):
    """Owen's ruling 1 through the Art. 21-ter notice conjunct (adjudication F1, route (a)).

    Two otherwise identical records share one complete first-party 7-day albo posting; only whether the order
    states its own ground for posting differs. The ground is the variable under test, not a reading of DDS 108.
    A stated ground reads as DDS 63/2026 (store c88d31c9…7b48) and DDS 2/2023 print it: "mediante affissione per 7
    giorni nell'albo pretorio del Comune in cui ricadono le piante da estirpare tenuto conto dell'irreperibilità di
    alcuni destinatari e della gravosità per l'amministrazione di notificare i provvedimenti ai singoli beneficiari".
    """
    personal = StatedTermRule.personal
    due = StatedTermRule.due
    result = StatedTermRule.result
    effect = StatedTermRule.effect
    settled = StatedTermRule.settled
    per = staticmethod(StatedTermRule.per)

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
        base = {(row['provision_version_id'], CLAUSE): True,
                (row['provision_version_id'], WORK): self.due(record, at, WORK),
                (row['provision_version_id'], COERCE): self.due(record, at, COERCE)}
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

    def test_immediate_effect_order_with_pec_delivery_gets_a_required_direction(self):
        # DDS 188/2024 (store 882c0020…): no ground of its own for posting (l.196-198); "all'albo pretorio per 7 gg
        # consecutivi e alla loro PEC qualora presente" (l.128-129); "Di dichiarare il presente provvedimento
        # immediatamente esecutivo" with its reasons (l.191-193); ten days from notice, then "disporrà" (l.179-181).
        # The PEC instant is synthetic. The reasoned clause neither gives nor defeats the PEC notice.
        from cordon_c.bindings import notice_instant
        at = date(2024, 12, 12)
        record = dict(DDS108, instrument='REG-PUGLIA-U181-DIR-2024-00188')
        individual = self.s.version(INDIVIDUAL, at)
        clause = {(individual['provision_version_id'], p): True for p in leaves(individual['condition_ast'])}
        self.assertIs(evaluate(self.s, INDIVIDUAL, at, clause).truth, False)  # the clause defeats that row's effect
        start = date(2024, 12, 13)
        facts, day = mass_publicity_facts(self.s, at, ground_stated=False, annulled_on_ground=False, posting_start=start,
                                          postings={'albo': (start, date(2024, 12, 20))}, postings_complete=True,
                                          stated_period=('7', 'gg consecutivi'),
                                          evaluated_at=datetime(2025, 3, 1, tzinfo=ROME), zone=ROME)
        self.assertIsNone(day)
        pec = datetime(2024, 12, 13, 16, tzinfo=ROME)
        facts = clause | facts | self.personal(at, True)
        notified = notice_instant(self.s, RULE, at, facts, zone=ROME, instants={COMMUNICATED: pec, MASS: day})
        self.assertEqual(notified, pec)
        # Independent expectation: ten calendar days after a Friday notice end on Monday 23 December.
        expected = end_of_day(date(2024, 12, 23), ROME)
        self.assertEqual(clock_boundary(self.s, CLOCK, at, notified, zone=ROME, calendar=self.calendar,
                                        stated_term=record['term']), expected)
        # The order's own case delta is reached through its governing reference (lawful dueness, not notice).
        delta = 'REG-PUGLIA-U181-DIR-2024-00188:case-delta:deferred-50m-workload-completion'
        governed = dict(refs=(delta,), results=self.per(delta, self.settled(delta, at)), notice=facts)
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=expected + timedelta(hours=1), **governed),
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        # Before the term lapses no direction is required.
        self.assertEqual(self.effect(record, at, notified=notified, evaluated=expected - timedelta(hours=1), **governed),
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')


if __name__ == '__main__':
    unittest.main()

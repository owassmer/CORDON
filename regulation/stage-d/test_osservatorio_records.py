"""Supplied Osservatorio records reach C per recipient through the removal-order caller.

The order is DDS 117/2025 (store 1d2e9b61…c2aa), clause 1 as PR #15's retained
reading (request 4d80fc65…) reads it, and the notice route as its retained
notice-route reading (request e402a892…) reads it: no ground of its own for
posting, \"notificato ai proprietari/conduttori attraverso la pubblicazione
all'albo pretorio per 7 gg consecutivi e alla loro PEC qualora presente\" (p. 3),
and \"immediatamente esecutivo\" (p. 4). The page text is the transport's,
shortened to the cited lines. Its recitals (p. 1) name the owner Nitti Vincenzo
and the tenant Laserra of Triggiano fg 4 p.lle 158-159-296-243.

Postings are public records (PR #15's route); no posting record is supplied here.

Every supplied record here is a FIXTURE (`fixture: true`): its instants, sources and
the parcels each recipient is obliged to are invented in the shape of those
recitals. None is a fact about the order. Settled A results for the order's two
case deltas are fixtures too; only their resolution matters here.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import copy
import unittest

from cordon_c.bindings import leaves
from cordon_c.core import Evaluation, Snapshot, evaluate
from cordon_d import case_prescriptions
from cordon_d.calendar import national_calendar
from cordon_d.case_prescriptions import COMMUNICATED, PrescriptionReading, c_result, recipient_results, supplied_records, validate

ROOT = Path(__file__).resolve().parents[2]
ROME = ZoneInfo('Europe/Rome')
SOURCE = '1d2e9b6111cdb33de96f1b1abeb49c1d3ad35019994404a74e59320d7850c2aa'
ORDER = 'REG-PUGLIA-U181-DIR-2025-00117'
DELTAS = (f'{ORDER}:case-delta:failed-service-represcription', f'{ORDER}:case-delta:st1-olive-nonmembership-boundary')
PRESCRIBE = 'Di prescrivere, ai sensi della lettera a), comma 1 dell’art. 7 del Reg. UE 2020/1201, ai proprietari/conduttori i'
PAGES = {
    1: ('DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO 27 giugno 2025, n. 117\n'
        '• il sig. Laserra, conduttore dei terreni siti in agro di Triggiano al fg. 4 - p.lle 158- 159-296-243, agli '
        'inizi\n'),
    2: (PRESCRIBE + '\ncui terreni rientrano in tutto o in parte nella zona infetta di 50 metri attorno a ciascuna '
        'pianta infetta, indicati\nnell’allegato 1/C, parte integrante e sostanziale del presente provvedimento:\n'
        ' a. l’estirpazione di tutte le piante che presentino sintomi indicativi della possibile infezione da parte\n'
        ' di tale organismo nocivo o che si sospetta siano infette da tale organismo nocivo;\n'),
    3: (' • il presente provvedimento è notificato ai proprietari/conduttori attraverso la pubblicazione all’albo\n'
        ' pretorio per 7 gg consecutivi e alla loro PEC qualora presente;\n'),
    4: ('Di stabilire che, qualora il proprietario/conduttore non proceda al concreto avvio delle attività di '
        'estirpazione\ndelle piante infette e delle piante ricadenti nei 50 m entro massimo 10 giorni dall’avvenuta '
        'notifica, la\nSezione Osservatorio fitosanitario disporrà l’abbattimento coatto delle piante infette, per il '
        'tramite dell’ARIF,\n'
        'Di dichiarare il presente provvedimento immediatamente esecutivo in quanto le misure di eradicazione di cui\n'
        ' • Al comune di Triggiano (BA), affinché provveda con urgenza dalla data di invio del presente atto\n'
        ' all’affissione all’Albo Pretorio della presente determinazione per la durata di 7 (sette) giorni naturali e\n'
        ' consecutivi. Tale affissione, ai sensi dell’art. 21 bis L. 241/1990 e s.m.i., decorso il settimo giorno dalla\n'
        ' data di pubblicazione assume valore di notifica ai proprietari/conduttori interessato all’ estirpazioni;\n'),
}
CLAUSE_SUPPORT = [
    dict(page=4, quote='Di stabilire che, qualora il proprietario/conduttore non proceda al concreto avvio delle '
                       'attività di estirpazione'),
    dict(page=4, quote='delle piante infette e delle piante ricadenti nei 50 m entro massimo 10 giorni '
                       'dall’avvenuta notifica, la'),
    dict(page=4, quote='Sezione Osservatorio fitosanitario disporrà l’abbattimento coatto delle piante infette, per '
                       'il tramite dell’ARIF,')]
READING = dict(
    identity=dict(issuer='SEZIONE OSSERVATORIO FITOSANITARIO', authority='puglia-osservatorio', number='117',
                  adopted='2025-06-27', title='Rettifica degli allegati 1/C delle determine n.188 del 12/12/2024 e '
                                              'n. 43 del 21/03/2025.',
                  support=[dict(page=1, quote='DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO 27 '
                                              'giugno 2025, n. 117')]),
    prescribed_work=[dict(
        recipients='proprietari/conduttori', cohort='allegato 1/C', work='l’estirpazione',
        population='tutte le piante che presentino sintomi indicativi della possibile infezione da parte di tale '
                   'organismo nocivo o che si sospetta siano infette da tale organismo nocivo',
        by_reference=None,
        support=[dict(page=2, quote=PRESCRIBE),
                 dict(page=2, quote='nell’allegato 1/C, parte integrante e sostanziale del presente provvedimento:'),
                 dict(page=2, quote='a. l’estirpazione di tutte le piante che presentino sintomi indicativi della '
                                    'possibile infezione da parte')])],
    enforcement_clauses=[dict(
        part='operative', work_indices=[0], commencement_work='concreto avvio delle attività di estirpazione',
        commencement_population='delle piante infette e delle piante ricadenti nei 50 m',
        term=dict(number='10', unit_word='giorni', literal='entro massimo 10 giorni'),
        anchor=dict(literal='dall’avvenuta notifica', kind='notification'),
        consequence='la Sezione Osservatorio fitosanitario disporrà l’abbattimento coatto delle piante infette, per '
                    'il tramite dell’ARIF',
        commitment='commits', coercive_population=dict(literal='delle piante infette', resolved='delle piante infette'),
        executor='ARIF', limits=[], support=CLAUSE_SUPPORT)],
    relationships=[], issues=[])
AT = date(2025, 7, 1)
PEC = datetime(2025, 7, 1, 10, 0, tzinfo=ROME)
# Independent expectation: ten calendar days from a Tuesday 1 July notice end on Friday 11 July.
DEADLINE = datetime(2025, 7, 11, 23, 59, 59, 999999, tzinfo=ROME)
# C's clock_boundary returns the exclusive end of that last day.
BOUNDARY = datetime(2025, 7, 12, tzinfo=ROME)
AFTER = datetime(2025, 7, 14, 12, 0, tzinfo=ROME)
# The reviewers' evaluation time, long after the deadline.
LATER = datetime(2026, 9, 25, 2, 0, tzinfo=ROME)
REDUCED = {'commencement evidence through the source deadline', *(f'result of {d}' for d in DELTAS)}


def parcel(particella):
    return dict(comune='Triggiano', foglio='4', particella=particella)


def fixture(record, kind, **fields):
    return dict(record=record, kind=kind, order=ORDER, source='f' * 64, selector=f'fixture:{record}',
                reading=f'FIXTURE {kind}: not a fact about DDS 117/2025', fixture=True, **fields)


def delivery(record, recipient, *parcels, occurred=PEC):
    return fixture(record, 'personal-delivery', recipient=recipient, occurred=occurred.isoformat(),
                   works=[parcel(p) for p in parcels])


def performed(record, particella, occurred, kind='commencement'):
    return fixture(record, kind, work=parcel(particella), occurred=occurred.isoformat())


def history(record, particella, start='2025-06-27', through='2025-07-14'):
    return fixture(record, 'history', work=parcel(particella), complete_from=start, complete_through=through)


class OsservatorioRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        validate(READING, PAGES)
        reading = PrescriptionReading(dict(request_sha256='0' * 64, request=dict(sources=[SOURCE]), reading=READING))
        cls.record = next(reading.records(cls.s))
        cls.settled = {}
        for sid in DELTAS:
            row = cls.s.version(sid, AT)
            cls.settled[sid] = evaluate(cls.s, sid, AT, {(row['provision_version_id'], p): True
                                                         for p in leaves(row['condition_ast'])})
            assert cls.settled[sid].truth is not None

    def run_records(self, supplied, *, evaluated_at=AFTER, settled=False, grant=frozenset({'f' * 64}), **options):
        extra = dict(governing_results=self.settled) if settled else {}
        return recipient_results(self.s, self.record, AT, supplied, evaluated_at=evaluated_at,
                                 permitted_controlled_sources=grant, zone=ROME,
                                 calendar=national_calendar(), **extra, **options)

    def test_an_empty_grant_yields_the_authorized_evidence_need(self):
        supplied = [delivery('pec-nitti', 'Nitti Vincenzo', '158')]
        self.assertIn('Nitti Vincenzo', self.run_records(supplied)['recipients'])
        run = self.run_records(supplied, grant=frozenset())
        self.assertEqual(run['recipients'], {})
        self.assertEqual(run['reported'], [dict(
            record='pec-nitti', kind='personal-delivery',
            need=f'authorized evidence for personal-delivery record pec-nitti on {ORDER}')])
        with self.assertRaises(TypeError):
            recipient_results(self.s, self.record, AT, supplied, evaluated_at=AFTER, zone=ROME,
                              calendar=national_calendar())

    def test_the_registered_clause_is_read_as_PR15_reads_it(self):
        self.assertEqual(self.record['instrument'], ORDER)
        self.assertEqual(set(self.record['governing_A_references']), set(DELTAS))
        self.assertEqual(self.record['stated_term'], ('10', 'giorni'))

    def test_with_no_record_C_names_personal_communication(self):
        cohort = c_result(self.s, self.record, AT, evaluated_at=AFTER)
        self.assertIsNone(cohort.truth)
        vid = self.s.version(case_prescriptions.RULE, AT)['provision_version_id']
        for need in (COMMUNICATED, 'the source notification-based commencement deadline has elapsed',
                     'noncommencement of that work by the source deadline is established'):
            self.assertIn(f'predicate: {vid} :: {need}', cohort.needs)
        self.assertTrue({f'result of {d}' for d in DELTAS} <= cohort.needs)
        empty = self.run_records([])
        self.assertEqual(empty, dict(recipients={}, reported=[]))

    def test_a_pec_delivery_gives_its_recipient_notice_despite_the_immediate_effect_clause(self):
        run = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158')])
        nitti = run['recipients']['Nitti Vincenzo']
        self.assertEqual(nitti['notification'], PEC)
        self.assertTrue(nitti['fixture'])
        self.assertIsNone(nitti['result'].truth)
        self.assertEqual(nitti['result'].needs, REDUCED)
        self.assertEqual(nitti['deadline'], BOUNDARY)
        self.assertNotIn('cohort', run)
        vid = self.s.version(case_prescriptions.RULE, AT)['provision_version_id']
        self.assertIn(f'predicate: {vid} :: {COMMUNICATED}', c_result(self.s, self.record, AT, evaluated_at=AFTER).needs)
        # A commencement on the recipient's work before the deadline defeats the direction.
        begun = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158'),
                                  performed('verbale-1', '158', PEC + timedelta(days=3))], settled=True)
        self.assertIs(begun['recipients']['Nitti Vincenzo']['result'].truth, False)
        # A stated complete history of the recipient's work with no commencement gives the computed direction.
        silent = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158'), history('storia-158', '158')],
                                  settled=True)
        self.assertEqual(silent['recipients']['Nitti Vincenzo']['result'].effect,
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        # Before the deadline lapses nothing is required.
        early = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158'),
                                  history('storia-158', '158', through='2025-07-10')],
                                 evaluated_at=DEADLINE - timedelta(days=1), settled=True)
        self.assertEqual(early['recipients']['Nitti Vincenzo']['result'].effect,
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_co_holders_are_noticed_apart_and_share_the_works_commencement(self):
        supplied = [delivery('pec-nitti', 'Nitti Vincenzo', '158'),
                    delivery('pec-laserra', 'Laserra', '158', occurred=PEC + timedelta(hours=2))]
        both = self.run_records(supplied)
        self.assertEqual(both['recipients']['Nitti Vincenzo']['notification'], PEC)
        self.assertEqual(both['recipients']['Laserra']['notification'], PEC + timedelta(hours=2))
        # The tenant's commencement on the shared parcel before the deadline moves both to false.
        begun = self.run_records(supplied + [performed('verbale-laserra', '158', PEC + timedelta(days=2))],
                                 settled=True)
        for name in ('Nitti Vincenzo', 'Laserra'):
            self.assertIs(begun['recipients'][name]['result'].truth, False, name)
        # A stated complete history of the shared work counts for both.
        silent = self.run_records(supplied + [history('storia-158', '158')], settled=True)
        for name in ('Nitti Vincenzo', 'Laserra'):
            self.assertEqual(silent['recipients'][name]['result'].effect,
                             'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED', name)

    def test_two_works_for_one_recipient_need_a_history_each(self):
        supplied = [delivery('pec-nitti', 'Nitti Vincenzo', '158', '243'), history('storia-158', '158')]
        one = self.run_records(supplied, settled=True)['recipients']['Nitti Vincenzo']
        self.assertFalse(one['commencement_records_complete'])
        self.assertIsNone(one['result'].truth)
        self.assertEqual(one['result'].needs, {'commencement evidence through the source deadline'})
        both = self.run_records(supplied + [history('storia-243', '243')], settled=True)['recipients']
        self.assertEqual(both['Nitti Vincenzo']['result'].effect, 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        # A co-holder obliged only to 158 is decided by 158's history alone; Nitti's 243 does not reach them.
        mixed = self.run_records(supplied + [delivery('pec-laserra', 'Laserra', '158')], settled=True)['recipients']
        self.assertEqual(mixed['Laserra']['result'].effect, 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        self.assertIsNone(mixed['Nitti Vincenzo']['result'].truth)

    def test_one_recipients_records_move_neither_the_cohort_nor_another_recipient(self):
        alone = self.run_records([delivery('pec-laserra', 'Laserra', '159')], settled=True)
        more = self.run_records([delivery('pec-laserra', 'Laserra', '159'),
                                 delivery('pec-nitti', 'Nitti Vincenzo', '158', occurred=PEC - timedelta(days=1)),
                                 performed('verbale-158', '158', PEC)], settled=True)
        self.assertEqual(more['recipients']['Laserra'], alone['recipients']['Laserra'])
        # The cohort result is c_result on cohort evidence; it takes no supplied record and names personal notice.
        cohort = c_result(self.s, self.record, AT, evaluated_at=AFTER, governing_results=self.settled)
        self.assertIsNone(cohort.truth)
        self.assertIn(COMMUNICATED, ' '.join(cohort.needs))
        self.assertIs(more['recipients']['Nitti Vincenzo']['result'].truth, False)

    def test_refusals(self):
        base = delivery('pec-nitti', 'Nitti Vincenzo', '158')
        # The caller takes no notification, instant or order-text predicate of its own.
        for key in ('notification', 'notice', 'notice_instants', 'commencement_records_complete'):
            with self.subTest(key=key), self.assertRaises(TypeError):
                self.run_records([base], **{key: True})
        # No record may carry an instant, predicate or completeness flag beside its kind's fields.
        for extra in (dict(notification=PEC.isoformat()), dict(immediate_effect_exception=False),
                      dict(restricts=True), dict(complete=True)):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                supplied_records([dict(base, **extra)])
        with self.assertRaises(ValueError):
            supplied_records([dict(base, occurred='2025-07-01T10:00:00')])  # an instant without its offset
        # Completeness is never defaulted: a history that starts after adoption or stops before C's deadline
        # (11/07, from the 1/07 delivery) fails.
        for short in (history('storia-158', '158', start='2025-06-30'),
                      history('storia-158', '158', through='2025-07-10')):
            result = self.run_records([base, short], settled=True)['recipients']['Nitti Vincenzo']
            self.assertFalse(result['commencement_records_complete'])
            self.assertEqual(result['result'].needs, {'commencement evidence through the source deadline'})
        # A history stated through a moment later than the evaluation is refused.
        for future in (history('storia-158', '158', through='2025-07-15'),
                       history('storia-158', '158', through=(AFTER + timedelta(hours=1)).isoformat())):
            with self.subTest(future=future['complete_through']), self.assertRaises(ValueError):
                self.run_records([base, future], settled=True)
        # A posting is not a supplied record kind: postings are PR #15's public route.
        with self.assertRaises(ValueError):
            supplied_records([fixture('posting', 'posting', publisher='Comune di Triggiano', start='2025-07-02',
                                      end='2025-07-09', complete=True)])
        # A commencement joins a work only by the same printed comune, foglio and particella.
        for other in (dict(comune='TRIGGIANO', foglio='4', particella='158'),
                      dict(comune='Triggiano', foglio='04', particella='158'),
                      dict(comune='Triggiano', foglio='4', particella='158-159')):
            record = fixture('verbale-x', 'commencement', work=other, occurred=(PEC + timedelta(days=1)).isoformat())
            run = self.run_records([base, record, history('storia-158', '158')], settled=True)
            self.assertEqual(run['recipients']['Nitti Vincenzo']['result'].effect,
                             'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
            self.assertEqual([r['cause'] for r in run['reported']],
                             ['no supplied record obliges a recipient to this work as printed'])
        # A performance dated by day alone is reported and keeps its work's history incomplete.
        day_only = fixture('verbale-d', 'commencement', work=parcel('158'), occurred='2025-07-03')
        run = self.run_records([base, day_only, history('storia-158', '158')], settled=True)
        self.assertIsNone(run['recipients']['Nitti Vincenzo']['result'].truth)
        # Deliveries at two instants to one recipient: the caller picks neither.
        twice = self.run_records([base, delivery('pec-nitti-2', 'Nitti Vincenzo', '158',
                                                 occurred=PEC + timedelta(days=1))])
        self.assertIsNone(twice['recipients']['Nitti Vincenzo']['notification'])
        # A record naming no recipient reaches no per-recipient result and is reported.
        nameless = self.run_records([dict(base, recipient='')])
        self.assertEqual((nameless['recipients'], nameless['reported'][0]['cause']), ({}, 'names no recipient'))
        with self.assertRaises(ValueError):
            self.run_records([dict(base, order='REG-PUGLIA-U181-DIR-2024-00188')])

    def test_a_history_through_Cs_deadline_decides_at_any_later_evaluation(self):
        # The deadline is C's, from the notification C returns: 1/07 + 10 days ends 11/07.
        for through in ('2025-07-11', '2025-07-12', '2025-07-15'):
            for evaluated_at in (AFTER + timedelta(days=1), LATER, LATER + timedelta(days=1)):
                with self.subTest(through=through, evaluated_at=evaluated_at):
                    run = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158'),
                                            history('storia-158', '158', through=through)],
                                           evaluated_at=evaluated_at, settled=True)
                    nitti = run['recipients']['Nitti Vincenzo']
                    self.assertEqual(nitti['deadline'], BOUNDARY)
                    self.assertTrue(nitti['commencement_records_complete'])
                    self.assertEqual(nitti['result'].effect, 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        # A later notification moves the deadline and the bound with it: a PEC on 10/07 runs to 21/07 (Monday).
        later = datetime(2025, 7, 10, 10, 0, tzinfo=ROME)
        short = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158', occurred=later),
                                  history('storia-158', '158', through='2025-07-15')], evaluated_at=LATER,
                                 settled=True)['recipients']['Nitti Vincenzo']
        self.assertEqual(short['deadline'], datetime(2025, 7, 22, tzinfo=ROME))
        self.assertFalse(short['commencement_records_complete'])
        self.assertEqual(short['result'].needs, {'commencement evidence through the source deadline'})
        # A commencement after the deadline does not defeat a history complete through it.
        run = self.run_records([delivery('pec-nitti', 'Nitti Vincenzo', '158'),
                                history('storia-158', '158', through='2025-07-15'),
                                performed('verbale-late', '158', DEADLINE + timedelta(days=2))],
                               evaluated_at=LATER, settled=True)
        self.assertEqual(run['recipients']['Nitti Vincenzo']['result'].effect,
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')

    def test_the_notification_is_the_one_C_returns_for_that_recipient(self):
        from cordon_c.bindings import notice_instant
        supplied = [delivery('pec-nitti', 'Nitti Vincenzo', '158'),
                    delivery('pec-laserra', 'Laserra', '158', occurred=PEC + timedelta(days=1))]
        run = self.run_records(supplied)
        vid = self.s.version(case_prescriptions.RULE, AT)['provision_version_id']
        for name, instant in (('Nitti Vincenzo', PEC), ('Laserra', PEC + timedelta(days=1))):
            expected = notice_instant(self.s, case_prescriptions.RULE, AT, {(vid, COMMUNICATED): True},
                                      zone=ROME, instants={COMMUNICATED: instant})
            self.assertEqual(run['recipients'][name]['notification'], expected)
        # A mutated caller that passes a raw instant as notification is not what C returns without a true branch.
        self.assertIsNone(notice_instant(self.s, case_prescriptions.RULE, AT, {}, zone=ROME,
                                         instants={COMMUNICATED: PEC}))


if __name__ == '__main__':
    unittest.main()

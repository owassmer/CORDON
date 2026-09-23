"""`case-prescription` records reach the Art. 21-ter rule from an order's own words.

Page text and quotations are DDS 108/2024 (store 47b107a6…3a51a3d), pages 6-8, as
the transport supplies them. The reading around them is the shape the reader
returns; notification instants are synthetic.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import copy
import unittest

from cordon_c.core import Snapshot
from cordon_d.calendar import national_calendar
from cordon_d.case_prescriptions import (NOTICE, PrescriptionReading, apply_references, c_result, clause,
                                         governing_references, validate)

ROOT = Path(__file__).resolve().parents[2]
ROME = ZoneInfo('Europe/Rome')
SOURCE = '47b107a6525606934c79125d5b4f565d7193ab92aef801b80b21d25bc3a51a3d'
PAGES = {
    1: 'DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO 16 agosto 2024, n. 108\n',
    6: ("Di prescrivere, ai sensi della lettera a), comma 1 dell’art. 7 del Reg. UE 2020/1201, ai\n"
        "proprietari/conduttori nel cui appezzamento ricade la pianta infetta e ai proprietari/conduttori, i cui terreni\n"
        "rientrano in tutto o in parte nella zona infetta di 50 m attorno alla pianta infetta, indicati nell’allegato 1/C:\n"
        "a. l’estirpazione di n° 1 piante risultata infetta da Xylella fastidiosa sottospecie multiplex ST26”;\n"),
    8: ("Di stabilire che, qualora il proprietario/conduttore non proceda al concreto avvio delle attività di\n"
        "estirpazione della pianta infetta e delle piante ricadenti nei 50 m entro massimo 10 giorni dall’avvenuta\n"
        "notifica, la Sezione Osservatorio fitosanitario disporrà l’abbattimento coatto delle piante infette, per il\n"
        "tramite dell’ARIF,\n"),
}
READING = dict(
    identity=dict(issuer='DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO', authority='puglia-osservatorio',
                  number='108', adopted='2024-08-16', title='Prescrizione di misure di eradicazione',
                  support=[dict(page=1, quote='16 agosto 2024, n. 108')]),
    prescribed_work=[
        dict(recipients='ai proprietari/conduttori nel cui appezzamento ricade la pianta infetta',
             cohort='allegato 1/C', work='l’estirpazione',
             population='n° 1 piante risultata infetta da Xylella fastidiosa sottospecie multiplex ST26',
             by_reference=None, support=[dict(page=6, quote='a. l’estirpazione di n° 1 piante risultata infetta')]),
        dict(recipients='ai proprietari/conduttori, i cui terreni rientrano in tutto o in parte nella zona '
                        'infetta di 50 m attorno alla pianta infetta',
             cohort='allegato 1/C', work='l’estirpazione', population='zona infetta di 50 m',
             by_reference=None, support=[dict(page=6, quote='nella zona infetta di 50 m attorno alla pianta infetta')])],
    enforcement_clauses=[dict(
        part='operative', work_indices=[0, 1],
        commencement_work='concreto avvio delle attività di estirpazione',
        commencement_population='della pianta infetta e delle piante ricadenti nei 50 m',
        term=dict(number='10', unit_word='giorni', literal='entro massimo 10 giorni'),
        anchor=dict(literal='dall’avvenuta notifica', kind='notification'),
        consequence='disporrà l’abbattimento coatto delle piante infette', commitment='commits',
        coercive_population=dict(literal='delle piante infette', resolved='della pianta infetta'),
        executor='ARIF', limits=[],
        support=[dict(page=8, quote='qualora il proprietario/conduttore non proceda al concreto avvio delle '
                                    'attività di estirpazione della pianta infetta e delle piante ricadenti nei '
                                    '50 m entro massimo 10 giorni dall’avvenuta notifica')])],
    relationships=[], issues=[])


def reading(values=READING):
    return PrescriptionReading(dict(request_sha256='0' * 64, request=dict(sources=[SOURCE]), reading=values))


class CasePrescriptionRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)

    def test_quotations_and_copied_words_bind_to_their_pages(self):
        validate(READING, PAGES)
        for path, value in ((('enforcement_clauses', 0, 'support', 0, 'quote'), 'entro massimo 15 giorni'),
                            (('enforcement_clauses', 0, 'executor'), 'Consorzio di bonifica'),
                            (('enforcement_clauses', 0, 'coercive_population', 'resolved'), 'tutte le piante ospiti'),
                            (('identity', 'support', 0, 'quote'), '16 agosto 2024, n. 109')):
            broken = copy.deepcopy(READING)
            target = broken
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate(broken, PAGES)

    def test_term_is_its_printed_number_and_unit_word(self):
        broken = copy.deepcopy(READING)
        broken['enforcement_clauses'][0]['term'] = dict(number='10', unit_word='giorni lavorativi',
                                                        literal='entro massimo 10 giorni')
        with self.assertRaises(ValueError):
            validate(broken, PAGES)
        record = next(reading().records(self.s))
        self.assertEqual(record['stated_term'], ('10', 'giorni'))
        self.assertEqual(record['term_literal'], 'entro massimo 10 giorni')

    def test_commencement_and_coercive_populations_stay_distinct(self):
        record = next(reading().records(self.s))
        self.assertEqual(record['commencement_population'], 'della pianta infetta e delle piante ricadenti nei 50 m')
        self.assertEqual(record['coercive_words'], 'delle piante infette')
        self.assertEqual(record['coercive_population'], 'della pianta infetta')
        self.assertEqual(record['executor'], 'ARIF')
        self.assertEqual(len(record['prescribed_scope']), 2)

    def test_unenforced_work_keeps_a_record_without_a_term(self):
        values = copy.deepcopy(READING)
        values['enforcement_clauses'][0]['work_indices'] = [0]
        records = list(reading(values).records(self.s))
        self.assertEqual([r['occurrence'].rsplit(':', 2)[1] for r in records], ['clause', 'work'])
        self.assertIsNone(records[1]['stated_term'])
        self.assertIs(clause(records[1]), False)
        self.assertEqual(c_result(self.s, records[1], date(2024, 9, 2)).effect,
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')

    def test_governing_references_reach_corrections_naming_the_order(self):
        self.assertEqual(governing_references(self.s, 'REG-PUGLIA-U181-DIR-2024-00108'), ())
        for instrument, correction in (
                ('REG-PUGLIA-U181-DIR-2024-00147', 'REG-PUGLIA-U181-DIR-2024-00165:case-delta:annex-only-municipality-correction'),
                ('REG-PUGLIA-U181-DIR-2024-00188', 'REG-PUGLIA-U181-DIR-2025-00011:case-delta:ownership-correction')):
            with self.subTest(instrument=instrument):
                self.assertIn(correction, governing_references(self.s, instrument))
        own = governing_references(self.s, 'REG-PUGLIA-U181-DIR-2023-00045')
        self.assertIn('REG-PUGLIA-U181-DIR-2023-00045:case-delta:pending-monumental-recognition-hold', own)

    def test_c_stays_unknown_without_held_notice(self):
        record = next(reading().records(self.s))
        result = c_result(self.s, record, date(2024, 9, 2))
        self.assertIsNone(result.truth)
        self.assertTrue(any(NOTICE in need for need in result.needs))

    def test_c_computes_from_the_stated_term_once_notice_and_history_are_held(self):
        record = next(reading().records(self.s))
        notified = datetime(2024, 9, 2, 9, tzinfo=ROME)
        evaluated = notified + timedelta(days=11)
        common = dict(notification=notified, evaluated_at=evaluated, zone=ROME, calendar=national_calendar(),
                      commencement_records_complete=True, work_due=True, coercion_due=True)
        self.assertEqual(c_result(self.s, record, date(2024, 9, 2), **common).effect,
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        begun = dict(common, commencements={'start': notified + timedelta(days=3)})
        self.assertEqual(c_result(self.s, record, date(2024, 9, 2), **begun).effect,
                         'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')
        self.assertIsNone(c_result(self.s, record, date(2024, 9, 2),
                                   **dict(common, commencement_records_complete=False)).truth)

    def test_other_anchor_or_permissive_consequence_does_not_reach_the_rule(self):
        for change in (dict(anchor=dict(literal='dalla pubblicazione', kind='other')),
                       dict(commitment='permits'), dict(part='recital'), dict(term=None)):
            record = dict(next(reading().records(self.s)), **change)
            if 'term' in change:
                record['stated_term'] = None
            with self.subTest(change=change):
                self.assertIs(clause(record), False)

    def test_work_applied_by_reference_takes_the_referenced_clause_or_stays_unknown(self):
        # DDS 11/2025 applies DDS 188/2024's measures to owners it newly lists. Its work
        # must not read as an order without a clause.
        correction = dict(
            identity=dict(READING['identity'], number='11', adopted='2025-02-05'),
            prescribed_work=[dict(READING['prescribed_work'][0], recipients='il nuovo proprietario',
                                  by_reference=dict(number='108', year='2024'))],
            enforcement_clauses=[], relationships=[], issues=[])
        own = next(PrescriptionReading(dict(request_sha256='1' * 64, request=dict(sources=['b' * 64]),
                                            reading=correction)).records(self.s))
        self.assertIsNone(clause(own).truth)
        self.assertIsNone(c_result(self.s, own, date(2025, 2, 5)).truth)
        alone = list(apply_references([own]))
        self.assertIsNone(clause(alone[0]).truth)
        order = next(reading().records(self.s))
        composed = [r for r in apply_references([order, own]) if r['occurrence'] == own['occurrence']][0]
        self.assertEqual(composed['instrument'], 'REG-PUGLIA-U181-DIR-2024-00108')
        self.assertEqual(composed['applied_by'], 'REG-PUGLIA-U181-DIR-2025-00011')
        self.assertEqual(composed['recipients'], ('il nuovo proprietario',))
        self.assertEqual(composed['stated_term'], ('10', 'giorni'))
        self.assertIs(clause(composed), True)

    def test_a_clause_reading_limit_leaves_the_clause_unknown(self):
        record = dict(next(reading().records(self.s)), limits=('term words cut at the page edge',))
        self.assertIsNone(clause(record).truth)
        self.assertIsNone(c_result(self.s, record, date(2024, 9, 2)).truth)


if __name__ == '__main__':
    unittest.main()

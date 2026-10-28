"""Held acts that name an order reach its lawful dueness as stated changes.

The admitted text is A's DDS 18/2024 (`regulation/jurisdiction/regional/bulk/DET-18-2024-FITO-.txt`);
its operative block 5 withdraws host removal within 50 m for five 2023 orders. The
order record is DDS 108/2024's, as `test_case_prescriptions` builds it; the
change stated against it is synthetic.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import copy
import unittest

from cordon_c.core import Snapshot
from cordon_d import held_acts
from cordon_d.calendar import national_calendar
from cordon_d.case_prescriptions import c_result, personal_notice
from test_case_prescriptions import reading as prescription

ROOT = Path(__file__).resolve().parents[2]
DDS18 = 'regulation/jurisdiction/regional/bulk/DET-18-2024-FITO-.txt'
ORDERS = {'REG-PUGLIA-U181-DIR-2023-00096': '2023-08-28', 'REG-PUGLIA-U181-DIR-2023-00113': '2023-10-16',
          'REG-PUGLIA-U181-DIR-2023-00119': '2023-11-08', 'REG-PUGLIA-U181-DIR-2023-00124': '2023-11-15',
          'REG-PUGLIA-U181-DIR-2023-00138': '2023-12-01', 'REG-PUGLIA-U181-DIR-2024-00027': '2024-01-30',
          'REG-PUGLIA-U181-DIR-2022-00119': '2022-10-14'}
PAYLOAD = 'non si procederà all’estirpazione delle piante ospiti ricadenti nell’area di 50 m attorno alle piante infette.'
ROME = ZoneInfo('Europe/Rome')


def relationship(number, year='2023', **item):
    return dict(dict(relationship='withdraws', extent='part', number=number, year=year, date_words='',
                     affected_payload=PAYLOAD, part='operative',
                     support=[dict(page=5, quote=f'Determina dirigenziale n. {number} del')]), **item)


def dds18(*relationships):
    return dict(identity=dict(issuer='DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO', authority='puglia-osservatorio',
                              number='18', adopted='2024-03-14', title='Aggiornamento dell’area delimitata',
                              support=[dict(page=1, quote='14 marzo 2024, n. 18')]),
                relationships=list(relationships), issues=[])


class HeldActs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.blocks = held_acts.blocks((ROOT / DDS18).read_bytes())

    def test_an_act_is_selected_by_the_order_identities_it_prints(self):
        text = (ROOT / DDS18).read_text()
        self.assertEqual(held_acts.printed_orders(text, ORDERS), set(list(ORDERS)[:5]))
        # A date that only resembles an identity, or a law cited by number and year, selects nothing.
        self.assertEqual(held_acts.printed_orders('n° 12 del 27/02/2024; L. 119/2022; foglio 27 del 2024', ORDERS),
                         set())
        self.assertEqual(held_acts.printed_orders('DDS n. 27/2024 e n. 119 del 14 ottobre 2022', ORDERS),
                         {'REG-PUGLIA-U181-DIR-2024-00027', 'REG-PUGLIA-U181-DIR-2022-00119'})

    def test_the_held_A_sources_that_name_orders_are_found_generally(self):
        chosen, scanned = held_acts.selected(self.s, ROOT, ORDERS)
        self.assertGreater(scanned, 50)
        by_path = {c['path']: c for c in chosen}
        self.assertEqual(by_path[DDS18]['instruments'], ('REG-PUGLIA-U181-DIR-2024-00018',))
        self.assertEqual(len(by_path[DDS18]['names']), 5)
        # DDS 127/2022 prints no held order's identity.
        self.assertFalse(any('DET-127-2022' in path for path in by_path))

    def test_quotations_and_payload_bind_to_their_blocks(self):
        pages = dict(enumerate(self.blocks, 1))
        held_acts.validate(dds18(relationship('113')), pages)
        for bad in (relationship('113', support=[dict(page=4, quote='Determina dirigenziale n. 113 del')]),
                    relationship('113', affected_payload='si procederà all’estirpazione di tutte le piante'),
                    relationship('n.', support=[dict(page=5, quote='Determina dirigenziale n. 113 del')])):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                held_acts.validate(dds18(bad), pages)

    def test_an_operative_statement_is_a_change_to_the_order_it_names(self):
        response = dict(request_sha256='1' * 64, request=dict(sources=['2' * 64]),
                        reading=dds18(relationship('113'), relationship('124', part='recital')))
        changes = list(held_acts.stated_changes(response, ('REG-PUGLIA-U181-DIR-2024-00018',), DDS18))
        self.assertEqual([(c['from'], c['target'], c['relationship'], c['extent']) for c in changes],
                         [('REG-PUGLIA-U181-DIR-2024-00018', 'REG-PUGLIA-U181-DIR-2023-00113', 'withdraws', 'part')])
        self.assertEqual([c['adopted'] for c in changes], ['2024-03-14'])

    def test_a_stated_change_counts_only_from_its_acts_adoption(self):
        # Every held act, with no per-act date: the change is read from the act's own identity.
        record = next(prescription().records(self.s))
        for adopted in ('2024-09-02', '2025-01-10'):
            response = dict(request_sha256='1' * 64, request=dict(sources=['2' * 64]),
                            reading=dict(dds18(relationship('108', year='2024')), identity=dict(
                                dds18()['identity'], adopted=adopted)))
            change = next(held_acts.stated_changes(response, ('REG-PUGLIA-U181-DIR-2024-00018',), DDS18))
            self.assertEqual(change['adopted'], adopted)
            day = date.fromisoformat(adopted)
            for at, unknown in ((day - timedelta(days=1), False), (day, True)):
                notified = datetime.combine(at, datetime.min.time(), ROME).replace(hour=9) - timedelta(days=12)
                held = dict(**personal_notice(self.s, at, notified), evaluated_at=notified + timedelta(days=12), zone=ROME,
                            calendar=national_calendar(), commencement_records_complete=True)
                with self.subTest(adopted=adopted, at=at):
                    result = c_result(self.s, record, at, stated_changes=[change], **held)
                    self.assertEqual(result.truth is None, unknown)
                    self.assertEqual(any('stated withdraws' in need for need in result.needs), unknown)
        # A change whose act prints no readable adoption date counts on every date, as before.
        undated = dict(change, adopted=None)
        self.assertIsNone(c_result(self.s, record, date(2024, 8, 20), stated_changes=[undated],
                                   evaluated_at=datetime(2024, 8, 20, 12, tzinfo=ROME)).truth)

    def test_a_stated_partial_withdrawal_leaves_dueness_unknown_naming_act_and_scope(self):
        record = next(prescription().records(self.s))
        at, notified = date(2024, 9, 2), datetime(2024, 9, 2, 9, tzinfo=ROME)
        held = dict(**personal_notice(self.s, at, notified), evaluated_at=notified + timedelta(days=11), zone=ROME,
                    calendar=national_calendar(), commencement_records_complete=True)
        change = {'from': 'REG-PUGLIA-U181-DIR-2024-00018', 'relationship': 'withdraws', 'extent': 'part',
                  'affected_payload': PAYLOAD}
        self.assertEqual(c_result(self.s, record, at, **held).effect,
                         'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        unknown = c_result(self.s, record, at, stated_changes=[change], **held)
        self.assertIsNone(unknown.truth)
        self.assertTrue(any('REG-PUGLIA-U181-DIR-2024-00018' in need and '(in part)' in need and PAYLOAD in need
                            for need in unknown.needs))
        # A supplement withholds nothing; a change an A row records is A's, not D's.
        self.assertEqual(c_result(self.s, record, at, stated_changes=[dict(change, relationship='supplements')],
                                  **held).effect, 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED')
        recorded = dict(record, governing_A_references=('REG-PUGLIA-U181-DIR-2024-00018:area-state-transition',))
        needs = c_result(self.s, recorded, at, stated_changes=[change], **held).needs
        self.assertFalse(any('stated withdraws' in need for need in needs))


if __name__ == '__main__':
    unittest.main()

"""Annex positions answer a whole-or-part row per recipient, for the orders an in-force row names.

The synthetic bands are DDS 113/2023's annex 1/D (store dd2887be…d338, pp. 33-34) as `page_bands`
returns them: one string per band between the page's drawn row rules. The retained-original
tests read the five orders DDS 18/2024 names; they need the local source store and are skipped
without it. Notification instants are synthetic.
"""
from datetime import date, datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo

from cordon_c.core import Snapshot
from cordon_d import annex_positions
from cordon_d.annex_positions import governing_results, parse, positions, supplying_rows
from cordon_d.calendar import national_calendar
from cordon_d.case_prescriptions import annex_position, c_result, personal_notice
from cordon_d.prescriptions import COERCE, WORK
from cordon_d.store import blob_path, store_root

ROOT = Path(__file__).resolve().parents[2]
ROME = ZoneInfo('Europe/Rome')
WITHDRAWAL = 'REG-PUGLIA-U181-DIR-2024-00018:case-delta:named-orders-50m-host-removal-withdrawn'
DDS113 = 'REG-PUGLIA-U181-DIR-2023-00113'
REQUIRED, NOT_ESTABLISHED = ('CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED',
                             'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED')
BANDS = [
    (33, 0, 'ALLEGATO 1/D'),
    (33, 2, 'AREA DELIMITATA VALLE D’ITRIA - PIANTE INFETTE MONITORAGGIO 2023'),
    (33, 6, 'ZONA | AGRO | RAPPORTO | SPECIE | LONGITUDINE | LATITUDINE | FOGLIO | PARTICELLA | PROPRIETARIO'),
    (33, 10, 'Zona Infetta | CASTELLANA | GROTTE | 1598862 | che rettifica il | prova 4/2023 | 9/2023 IAMB | '
             'rapporto di | IAMB | 03/10/2023 | Olivo (Olea | europaea) | 17,18612001 | 40,89447976 | 15 | 80 | '
             'RESPONSABILITA` LIMITATA | TERRAPULIA SOCIETA` A | - SOCIETA` AGRICOLA'),
    (33, 11, 'Zona Infetta | CASTELLANA | GROTTE | 1614393 | 8/2023 IAMB | 02/10/2023 | Olivo (Olea | europaea) | '
             '17,22174411 | 40,83922395 | 57 | 89 | ROTOLO IRENE'),
    (33, 12, 'Zona Infetta | CASTELLANA | GROTTE | 1602200 | 6/2023 IAMB | 22/09/2023 | Olivo (Olea | europaea) | '
             '17,2250932 | 40,83896301 | 57 | 270 | BORGHESE ANTONIO'),
    (33, 14, 'ZONE INFETTE DI 50 M ATTORNO ALLA PIANTA INFETTA (Rif. ID 1598862)'),
    (33, 15, 'AGRO | FOGLIO | PARTICELLE | PROPRIETARI'),
    (33, 16, 'CASTELLANA GROTTE | 15 | STRADE'),
    (33, 17, 'CASTELLANA GROTTE | 15 | 80 | TERRAPULIA SOCIETA` A RESPONSABILITA` LIMITATA - SOCIETA` AGRICOLA'),
    (33, 18, 'CASTELLANA GROTTE | 15 | 345 | PROPRIETARI NON INDIVIDUATI'),
    (33, 20, 'ZONE INFETTE DI 50 M ATTORNO ALLA PIANTA INFETTA (Rif. ID 1614393)'),
    (33, 21, 'AGRO | FOGLIO | PARTICELLE | PROPRIETARI'),
    (33, 22, 'CASTELLANA GROTTE | 57 | 193 | BORGHESE SANTE'),
    (33, 23, 'CASTELLANA GROTTE | 57 | 146 | CISTERNINO PAOLA | IPPOLITO MARIA'),
    (33, 24, 'CASTELLANA GROTTE | 57 | 89 | ROTOLO IRENE'),
    (33, 25, '23'),
    (34, 1, 'ZONE INFETTE DI 50 M ATTORNO ALLA PIANTA INFETTA (Rif. ID 1602200)'),
    (34, 2, 'AGRO | FOGLIO | PARTICELLE | PROPRIETARI'),
    (34, 3, 'CASTELLANA GROTTE | 57 | 78 – 270 – 271 - | 273 | BORGHESE ANTONIO'),
    (34, 4, '24'),
]
# Its clause-0 record as `records` builds it from the retained reading (fields the rule and D read).
RECORD = dict(instrument=DDS113, adopted='2023-10-16', source='dd2887bee294634c1a8a21730fd910abcdae0ff41f90c29c5af45c9eaae8d338',
              occurrence='dd2887bee294634c1a8a21730fd910abcdae0ff41f90c29c5af45c9eaae8d338:clause:0',
              part='operative', recipients=('ai proprietari/conduttori … indicati nell’allegato 1/D',),
              cohort=('allegato 1/D',), relationships=(), governing_A_references=(WITHDRAWAL,), issues=(),
              prescribed_scope=(dict(work='l’estirpazione', population='n° 3 piante di olivo risultate infette'),),
              commencement_population='delle piante infette e delle piante ricadenti nei 50 m',
              commencement_work='concreto avvio delle attività di estirpazione', stated_term=('10', 'giorni'),
              term_literal='entro massimo 10 giorni', anchor=dict(literal='dall’avvenuta notifica', kind='notification'),
              consequence='disporrà l’abbattimento coatto', commitment='commits',
              coercive_population='delle piante infette e delle piante ricadenti nei 50 m',
              coercive_words='delle piante infette e delle piante ricadenti nei 50 m', executor='ARIF', limits=())


def by_owner(found):
    return {p['owner'] or p['printed']: p for p in found}


class AnnexPositions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)

    def test_the_annex_places_each_owner_on_its_parcels_and_plants(self):
        annex = parse(BANDS, 3)
        self.assertEqual(annex['failures'], [])
        self.assertEqual([i['sample'] for i in annex['infected']], ['1598862', '1614393', '1602200'])
        found = by_owner(positions(annex, '1/D'))
        self.assertEqual(len([p for p in found.values() if p['owner']]), 6)
        # 57/146 is placed on two joint owners, both 50 m only; 15/80's owner holds 1598862.
        for name in ('CISTERNINO PAOLA', 'IPPOLITO MARIA'):
            self.assertEqual(found[name]['parcels'], [dict(foglio='57', particella='146')])
            self.assertEqual(found[name]['listed_infected_plants'], [])
        terrapulia = found['TERRAPULIA SOCIETA` A RESPONSABILITA` LIMITATA - SOCIETA` AGRICOLA']
        self.assertEqual(terrapulia['listed_infected_plants'], ['1598862'])
        self.assertEqual(found['BORGHESE ANTONIO']['listed_infected_plants'], ['1602200'])
        self.assertEqual(len(found['BORGHESE ANTONIO']['parcels']), 4)
        # A listing that places no recipient is unknown, naming its printed words.
        self.assertEqual(found['STRADE']['cause'],
                         "annex 1/D places this 50 m listing on no recipient: 'STRADE' (foglio 15)")
        self.assertIn("'PROPRIETARI NON INDIVIDUATI' (foglio 15, particella 345)",
                      found['PROPRIETARI NON INDIVIDUATI']['cause'])

    def test_a_failed_check_leaves_every_position_unknown_naming_it(self):
        for printed, bands, words in ((4, BANDS, 'the infected-plant table has 3 rows; the order prints n° 4 piante'),
                                      (3, [b for b in BANDS if b[1] != 24 or b[0] != 33],
                                       'no 50 m row names the owners of infected-plant parcel(s) 57/89')):
            with self.subTest(words=words):
                annex = parse(bands, printed)
                self.assertEqual(annex['failures'], [words])
                found = positions(annex, '1/D')
                self.assertTrue(found and all(words in p['cause'] for p in found))
                for p in found:
                    results = governing_results(self.s, RECORD, date(2024, 3, 14), p)
                    self.assertIsNone(results[(WITHDRAWAL, WORK)].truth)
                    self.assertIn(p['cause'], results[(WITHDRAWAL, WORK)].needs)

    def test_owners_a_dash_separates_are_positions_and_a_legal_form_continues_a_name(self):
        bands = [(1, 0, 'ZONE INFETTE DI 50 M ATTORNO ALLE PIANTE INFETTE (Rif. ID 1616565)'),
                 (1, 1, 'Polignano a Mare | 32 | 319 COMES VITO -  COMES VITTORIO'),
                 (1, 2, 'Polignano a Mare | 33 328 – 394 - 397 COMES VITO'),
                 (1, 3, 'MONOPOLI | 2 | 33 RETE FERROVIARIA ITALIANA - SOCIETÀ PER AZIONI IN SIGLA RFI S.P.A.')]
        annex = parse(bands, 0)
        self.assertEqual([l['owners'] for l in annex['listings']],
                         [['COMES VITO', 'COMES VITTORIO'], ['COMES VITO'],
                          ['RETE FERROVIARIA ITALIANA - SOCIETÀ PER AZIONI IN SIGLA RFI S.P.A.']])
        self.assertEqual(annex['listings'][1]['particelle'], ['328', '394', '397'])

    def test_only_the_orders_an_in_force_row_names_are_supplied(self):
        self.assertEqual(supplying_rows(self.s, date(2024, 3, 14), DDS113), [WITHDRAWAL])
        self.assertEqual(supplying_rows(self.s, date(2026, 9, 24), DDS113), [WITHDRAWAL])
        self.assertEqual(supplying_rows(self.s, date(2024, 3, 13), DDS113), [])
        for other in ('REG-PUGLIA-U181-DIR-2024-00108', 'REG-PUGLIA-U181-DIR-2023-00045'):
            self.assertEqual(supplying_rows(self.s, date(2024, 3, 14), other), [])
        # Before the row is in force the record stays at order grain.
        self.assertEqual(annex_positions.expand(RECORD, self.s, date(2024, 3, 13), None), [RECORD])

    def test_each_position_answers_the_row_for_work_and_coercion(self):
        at = date(2024, 3, 14)
        found = by_owner(positions(parse(BANDS, 3), '1/D'))
        for name, effect in (('CISTERNINO PAOLA', 'POPULATION_NOT_LAWFULLY_DUE'),
                             ('ROTOLO IRENE', 'LAWFULLY_DUE_IN_PART')):
            results = governing_results(self.s, RECORD, at, found[name])
            for predicate in (WORK, COERCE):
                self.assertEqual(results[(WITHDRAWAL, predicate)].effect, effect)
        self.assertEqual(governing_results(self.s, RECORD, at, None), {})

    def test_at_a_position_the_withdrawal_reaches_c(self):
        at, notified = date(2024, 3, 14), datetime(2024, 3, 1, 9, tzinfo=ROME)
        held = dict(**personal_notice(self.s, at, notified), evaluated_at=datetime(2024, 3, 14, 12, tzinfo=ROME), zone=ROME,
                    calendar=national_calendar(), commencement_records_complete=True)
        found = by_owner(positions(parse(BANDS, 3), '1/D'))
        vid = self.s.version(WITHDRAWAL, at)['provision_version_id']

        def at_position(name):
            record = dict(RECORD, recipients=(found[name],))
            self.assertIs(annex_position(record), found[name])
            return c_result(self.s, record, at, governing_results=governing_results(self.s, record, at, found[name]),
                            **held)

        self.assertEqual(at_position('CISTERNINO PAOLA').effect, NOT_ESTABLISHED)
        holder = at_position('ROTOLO IRENE')
        self.assertEqual(holder.effect, REQUIRED)
        self.assertIn(vid, holder.provisions)
        unplaced = at_position('STRADE')
        self.assertIsNone(unplaced.truth)
        self.assertIn(found['STRADE']['cause'], unplaced.needs)
        # The order-grain record under the same in-part result never reads due.
        mixed = governing_results(self.s, RECORD, at, found['ROTOLO IRENE'])
        cohort = c_result(self.s, RECORD, at, governing_results=mixed, **held)
        self.assertIsNone(cohort.truth)
        self.assertTrue(any("this recipient's position in" in need for need in cohort.needs))


STORE = store_root(ROOT)
FIVE = {'96/2023': 'dd5bebb3616b9752c6b2dfc76c03b31a2378574800491c49866d99399295cbf7',
        '113/2023': 'dd2887bee294634c1a8a21730fd910abcdae0ff41f90c29c5af45c9eaae8d338',
        '119/2023': '1edbf64f6616a93bb97ef4947f769fe7d44c911c324d8fbbc40ad969e16ed80c',
        '124/2023': 'd79ed2678b0c7c04f94f15e0575821339981bfbff741d93d1d3903614719a9d3',
        '138/2023': 'cdbf4ebc2467e7b38bfcfb807371402789f26f0e9ff8c9a2c2dd32cb319733ac'}
# The plan's read of annex 1/D: letter-a rows and their parcels, 50 m rows and owned parcels, owners holding
# a listed infected plant / holding only 50 m parcels, and 50 m listings placing no recipient.
COUNTS = {'96/2023': (4, 2, 5, 9, 2, 5, 0), '113/2023': (3, 3, 7, 8, 3, 3, 2), '119/2023': (37, 14, 36, 64, 14, 23, 0),
          '124/2023': (17, 6, 23, 42, 10, 30, 1), '138/2023': (5, 4, 10, 14, 4, 7, 1)}


@unittest.skipUnless(all(blob_path(STORE, d).exists() for d in FIVE.values()), 'retained originals not in the store')
class RetainedAnnexes(unittest.TestCase):
    def read(self, order):
        return annex_positions.read_annex(str(blob_path(STORE, FIVE[order])), '1/D')

    def test_each_orders_annex_counts(self):
        for order, expected in COUNTS.items():
            with self.subTest(order=order):
                annex, found = self.read(order)
                self.assertEqual(annex['failures'], [])
                owners = [p for p in found if p['owner']]
                self.assertEqual((len(annex['infected']), len({(i['foglio'], i['particella']) for i in annex['infected']}),
                                  len(annex['listings']),
                                  len({(l['foglio'], p) for l in annex['listings'] if l['owners'] for p in l['particelle']}),
                                  sum(1 for p in owners if p['listed_infected_plants']),
                                  sum(1 for p in owners if not p['listed_infected_plants']),
                                  sum(1 for p in found if not p['owner'])), expected)
        self.assertEqual(sum(len([p for p in self.read(o)[1] if p['owner']]) for o in FIVE), 101)

    def test_named_positions(self):
        found = by_owner(self.read('113/2023')[1])
        for name in ('CISTERNINO PAOLA', 'IPPOLITO MARIA'):
            self.assertEqual(found[name]['parcels'], [dict(foglio='57', particella='146')])
            self.assertEqual(found[name]['listed_infected_plants'], [])
        holder = [p for p in found.values() if dict(foglio='15', particella='80') in p['parcels']]
        self.assertEqual([p['listed_infected_plants'] for p in holder], [['1598862']])
        self.assertIn("'STRADE' (foglio 15)", found['STRADE']['cause'])
        self.assertIn("'PROPRIETARI NON INDIVIDUATI' (foglio 15, particella 345)",
                      found['PROPRIETARI NON INDIVIDUATI']['cause'])
        found = by_owner(self.read('124/2023')[1])
        self.assertEqual(found['COMES VITTORIO']['parcels'], [dict(foglio='32', particella='319')])
        self.assertEqual(found['COMES VITTORIO']['listed_infected_plants'], [])
        self.assertIn(dict(foglio='33', particella='394'), found['COMES VITO']['parcels'])
        self.assertTrue(found['COMES VITO']['listed_infected_plants'])

    def writer(self, *only):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out.json'
            subprocess.run([sys.executable, str(ROOT / 'scripts/read_prescriptions.py'), '--only', *only,
                            '--out', str(out)], check=True, capture_output=True, cwd=ROOT)
            return [r for e in json.loads(out.read_text()) for r in e.get('records', ())]

    def test_the_writer_emits_one_record_per_clause_and_position(self):
        records = self.writer('113/2023')
        self.assertEqual(len(records), 2 * (6 + 2))
        self.assertEqual(len({r['occurrence'] for r in records}), 16)
        self.assertTrue(all(annex_position(r) and r['cohort'] == ['allegato 1/D'] for r in records))
        clause0 = [r for r in records if ':clause:0:' in r['occurrence']]
        vid = WITHDRAWAL + ':v1'
        not_due = [r for r in clause0 if r['c']['truth'] is False]
        in_part = [r for r in clause0 if r['c']['truth'] is None and vid in r['c']['provisions']
                   and not any('lawfully due' in n or 'annex' in n for n in r['c']['needs'])]
        unplaced = [r for r in clause0 if any('places this 50 m listing on no recipient' in n for n in r['c']['needs'])]
        self.assertEqual((len(not_due), len(in_part), len(unplaced)), (3, 3, 2))
        self.assertFalse(any('stated withdraws' in n for r in records for n in r['c']['needs']))
        # Clause 1 states no term: it never yields a direction, whatever the dueness.
        self.assertTrue(all(r['c']['truth'] is False for r in records if ':clause:1:' in r['occurrence']))

    def test_a_governed_orders_need_names_its_rows_predicates(self):
        # DDS 45/2023: the hold's own predicates, where main's writer named "result of …hold".
        records = [r for r in self.writer('45/2023') if r['instrument'] == 'REG-PUGLIA-U181-DIR-2023-00045'
                   and r['occurrence'].endswith(':clause:0')]
        self.assertTrue(records)
        hold = 'REG-PUGLIA-U181-DIR-2023-00045:case-delta:pending-monumental-recognition-hold'
        for record in records:
            self.assertFalse(any(n.startswith('result of') for n in record['c']['needs']))
            self.assertTrue(any(n.startswith(f'predicate: {hold}:v2 :: the population in question holds')
                                for n in record['c']['needs']))


if __name__ == '__main__':
    unittest.main()

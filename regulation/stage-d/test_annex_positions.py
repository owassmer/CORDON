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
from unittest import mock
from zoneinfo import ZoneInfo

from cordon_c.core import Evaluation, Snapshot
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


DDS96 = 'REG-PUGLIA-U181-DIR-2023-00096'
FORK = 'REG-PUGLIA-U181-DIR-2023-00096:case-delta:pre-m4-monopoli-eradication-fork'
# DDS 96/2023 (store dd5bebb3…cbf7), annex 1/D p. 19 rows 11-12, as `read_annex` places them: BOGGIANO ANNA holds
# 50 m hosts only; APULEO LUCIA holds two listed infected plants.
BOGGIANO = dict(annex='allegato 1/D', owner='BOGGIANO ANNA', printed='BOGGIANO ANNA',
                parcels=[dict(foglio='17', particella='39')], fifty_metre_parcels=[dict(foglio='17', particella='39')],
                listed_infected_plants=[], listed_infected_plant_parcels=[], rows=['p. 19 row 11'])
APULEO = dict(annex='allegato 1/D', owner='APULEO LUCIA', printed='APULEO LUCIA',
              parcels=[dict(foglio='17', particella=p) for p in ('46', '66', '159', '245', '246')],
              fifty_metre_parcels=[dict(foglio='17', particella=p) for p in ('46', '66', '159', '245', '246')],
              listed_infected_plants=['1455708', '1584865'],
              listed_infected_plant_parcels=[dict(plant=p, foglio='17', particella='66')
                                             for p in ('1455708', '1584865')],
              rows=['p. 19 row 12'])
# TAR Bari Sentenza 387/2026 (store f751acc2…2b02): its closure of DDS 96/2023 as `liveness_closures` returns it
# from the retained disposition reading.
TAR_387 = dict(
    effect='ended-with-stated-reason', scope='whole-act', applicants='Lucia Apuleo',
    outcome='dichiara improcedibili per sopravvenuta carenza di interesse il ricorso principale e quello per primi '
            'motivi aggiunti',
    dispositive_scope='', stated_scope=(),
    stated_reason=('il ricorso principale è divenuto improcedibile in ragione del superamento della DDS n.96/2023 da '
                   'parte della successiva DDS n.18/2024',
                   'non si procederà all’estirpazione delle piante ospiti ricadenti nell’area di 50 m attorno alle '
                   'piante infette”, con ciò concentrando le misure dell’eradicazione solo sulle piante infette.',
                   'Analoghe considerazioni conducono a ritenere improcedibile il primo ricorso per motivi aggiunti'),
    decision=dict(kind='Sentenza', number='387/2026', section='3', register='202301238', decided=date(2026, 2, 18),
                  published=date(2026, 3, 25),
                  source='f751acc2e9819e168b57d0dd2a453fee7aa127c9e8c96b3dc5bfbc86b02c8b02'),
    since=date(2026, 3, 25))


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
        self.assertEqual(found['BORGHESE ANTONIO']['listed_infected_plant_parcels'],
                         [dict(plant='1602200', foglio='57', particella='270')])
        self.assertEqual(len(found['BORGHESE ANTONIO']['parcels']), 4)
        # A listing that places no recipient names its printed words and is what it is: 50 m hosts (the
        # strip with no parcel number included) with no listed infected plant. No recipient is not a cause.
        self.assertEqual(found['STRADE']['no_recipient'],
                         "annex 1/D places this 50 m listing on no recipient: 'STRADE' (foglio 15)")
        self.assertIn("'PROPRIETARI NON INDIVIDUATI' (foglio 15, particella 345)",
                      found['PROPRIETARI NON INDIVIDUATI']['no_recipient'])
        self.assertEqual(found['STRADE']['fifty_metre_parcels'], [dict(foglio='15', particella=None)])
        self.assertEqual(found['PROPRIETARI NON INDIVIDUATI']['fifty_metre_parcels'],
                         [dict(foglio='15', particella='345')])
        for name in ('STRADE', 'PROPRIETARI NON INDIVIDUATI'):
            self.assertIsNone(found[name]['owner'])
            self.assertEqual(found[name]['listed_infected_plants'], [])
            self.assertNotIn('cause', found[name])

    def test_an_owner_printed_as_not_found_places_no_recipient(self):
        # DDS 115/2023 prints "PROPRIETARI NON TROVATI" (annex 1/D p. 24); the retained original is read below.
        bands = BANDS[:11] + [(33, 19, 'CASTELLANA GROTTE | 15 | 336 | PROPRIETARI NON TROVATI')] + BANDS[11:]
        found = by_owner(positions(parse(bands, 3), '1/D'))
        self.assertNotIn('PROPRIETARI NON TROVATI', {p['owner'] for p in found.values()})
        self.assertIsNone(found['PROPRIETARI NON TROVATI']['owner'])
        self.assertIn("(foglio 15, particella 336)", found['PROPRIETARI NON TROVATI']['no_recipient'])

    def test_a_no_recipient_listing_on_an_infected_plants_parcel_is_never_defaulted(self):
        # Not printed in any held annex: the annex's check places every infected plant's parcel on an owned row,
        # so a no-recipient listing holds none. If one did, the position is unknown, naming the listing and plant.
        bands = BANDS[:11] + [(33, 19, 'CASTELLANA GROTTE | 15 | 80 | PROPRIETARI NON TROVATI')] + BANDS[11:]
        annex = parse(bands, 3)
        self.assertEqual(annex['failures'], [])
        unplaced = [p for p in positions(annex, '1/D') if p['owner'] is None and p['listed_infected_plants']]
        self.assertEqual(len(unplaced), 1)
        self.assertIn('holds listed infected plant(s) 1598862', unplaced[0]['cause'])
        results = governing_results(self.s, RECORD, date(2024, 3, 14), unplaced[0])
        for predicate in (WORK, COERCE):
            self.assertIsNone(results[(WITHDRAWAL, predicate)].truth)
            self.assertIn(unplaced[0]['cause'], results[(WITHDRAWAL, predicate)].needs)

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
                             ('ROTOLO IRENE', 'LAWFULLY_DUE_IN_PART'),
                             ('STRADE', 'POPULATION_NOT_LAWFULLY_DUE'),
                             ('PROPRIETARI NON INDIVIDUATI', 'POPULATION_NOT_LAWFULLY_DUE')):
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
        # A listing on no recipient is not due: its 50 m hosts are withdrawn whoever owns them.
        for name in ('STRADE', 'PROPRIETARI NON INDIVIDUATI'):
            unplaced = at_position(name)
            self.assertEqual(unplaced.effect, NOT_ESTABLISHED)
            self.assertIn(vid, unplaced.provisions)
        # The order-grain record under the same in-part result never reads due.
        mixed = governing_results(self.s, RECORD, at, found['ROTOLO IRENE'])
        cohort = c_result(self.s, RECORD, at, governing_results=mixed, **held)
        self.assertIsNone(cohort.truth)
        self.assertTrue(any("this recipient's position in" in need for need in cohort.needs))

    def test_a_96_hosts_only_position_with_its_tar_387_2026_closure_reads_not_due(self):
        # The court's stated reason is DDS 18/2024's withdrawal of the 50 m hosts, and every closure only withholds:
        # the order's own unknown replaces only a due the rows leave true, so a not due keeps its row (round 2).
        at = date(2026, 9, 24)
        vid = self.s.version(WITHDRAWAL, at)['provision_version_id']

        def at_position(position):
            record = dict(RECORD, instrument=DDS96, adopted='2023-08-28', governing_A_references=(FORK, WITHDRAWAL),
                          recipients=(position,))
            return c_result(self.s, record, at, closures=[TAR_387],
                            governing_results=governing_results(self.s, record, at, position))

        hosts_only = at_position(BOGGIANO)
        self.assertIs(hosts_only.truth, False)
        self.assertEqual(hosts_only.effect, NOT_ESTABLISHED)
        self.assertIn(vid, hosts_only.provisions)
        self.assertFalse(any('TAR Sentenza 387/2026' in need for need in hosts_only.needs))
        # A letter-a holder is due in part by the rows, so the court's words still decide it: unknown, naming them.
        holder = at_position(APULEO)
        self.assertIsNone(holder.truth)
        self.assertTrue(any(need.startswith('the effect on this order of what TAR Sentenza 387/2026 states')
                            for need in holder.needs))

    def test_position_records_drop_the_readings_note_that_the_annex_could_not_be_read(self):
        stale = dict(page=33, aspect='coverage', detail='Allegato 1/D (pages 33-34), which lists recipients and '
                     'parcels, has a scrambled text layer; which owner goes with which parcel cannot be read reliably.')
        kept = [dict(page=13, aspect='coverage', detail='Pages 13-15 (Allegato 1/A orthophotos) carry no native text.'),
                dict(page=8, aspect='work', detail='Point 7 cites point 2 and point 3 for the 50 m plants.')]
        record = dict(RECORD, issues=[kept[0], stale, kept[1]])
        annex = parse(BANDS, 3)
        with mock.patch.object(annex_positions, 'read_annex', return_value=(annex, positions(annex, '1/D'))):
            expanded = annex_positions.expand(record, self.s, date(2024, 3, 14), Path('/nonexistent'))
        self.assertEqual(len(expanded), 8)
        self.assertTrue(all(r['issues'] == kept for r in expanded))
        # Where the annex's checks fail, the note stands.
        failed = parse(BANDS, 4)
        with mock.patch.object(annex_positions, 'read_annex', return_value=(failed, positions(failed, '1/D'))):
            expanded = annex_positions.expand(record, self.s, date(2024, 3, 14), Path('/nonexistent'))
        self.assertTrue(all(stale in r['issues'] for r in expanded))


# Supplied Osservatorio records joined to annex positions of DDS 113/2023 and 124/2023 (SPEC, "Supplied records at
# an annex position"). Every supplied record below is a FIXTURE (`fixture: true`): its instants, sources and the
# works it names are invented in the shape of the annexes. None is a fact about either order. The positions are
# the annexes' own (113/2023 from BANDS; 124/2023 as `read_annex` places them, checked against the retained
# original in `RetainedAnnexes`).
DDS124 = 'REG-PUGLIA-U181-DIR-2023-00124'
SOURCE_124 = 'd79ed2678b0c7c04f94f15e0575821339981bfbff741d93d1d3903614719a9d3'
RECORD_124 = dict(RECORD, instrument=DDS124, adopted='2023-11-15', source=SOURCE_124,
                  occurrence=f'{SOURCE_124}:clause:0',
                  prescribed_scope=(dict(work='l’estirpazione', population='n° 17 piante di olivo risultate infette'),))


def _position(owner, parcels, plants, rows):
    return dict(annex='allegato 1/D', owner=owner, printed=owner,
                parcels=[dict(foglio=f, particella=p) for f, p in parcels],
                fifty_metre_parcels=[dict(foglio=f, particella=p) for f, p in parcels],
                listed_infected_plants=[p for p, _ in plants],
                listed_infected_plant_parcels=[dict(plant=p, foglio=f, particella=q) for p, (f, q) in plants],
                rows=rows)


CIAMPI_PLANTS = [(p, ('32', '293')) for p in ('1605000', '1616845', '1616849')]
POSITIONS_124 = {
    'COMES VITO': _position('COMES VITO', [('32', '319'), ('33', '328'), ('33', '394'), ('33', '397')],
                            [('1603982', ('33', '394')), ('1616565', ('33', '394'))], ['p. 31 row 14', 'p. 31 row 27']),
    'COMES VITTORIO': _position('COMES VITTORIO', [('32', '319')], [], ['p. 31 row 14']),
    'CIAMPI COSIMO': _position('CIAMPI COSIMO', [('32', '52'), ('32', '293')], CIAMPI_PLANTS, ['p. 31 row 8']),
    'CIAMPI VITO PASQUALE': _position('CIAMPI VITO PASQUALE', [('32', '52'), ('32', '293')], CIAMPI_PLANTS,
                                      ['p. 31 row 8']),
    'NAUTICA CIAMPI S.R.L': _position('NAUTICA CIAMPI S.R.L', [('32', '52'), ('32', '293')], CIAMPI_PLANTS,
                                      ['p. 31 row 8']),
}
AT = date(2024, 6, 15)
EVALUATED = datetime(2024, 6, 15, 12, tzinfo=ROME)
# Delivery instants and the boundary C's clock_boundary returns for each (10 giorni, national calendar). Independent
# expectation: 20 Nov 2023 + 10 days ends Thursday 30 Nov; 20 Mar 2024 ends Saturday 30 Mar; 5 Apr 2024 ends
# Monday 15 Apr; 1 Jun 2024 ends Tuesday 11 Jun. Each boundary is the exclusive end of that last day.
PEC_B, BOUNDARY_B = datetime(2023, 11, 20, 9, tzinfo=ROME), datetime(2023, 12, 1, tzinfo=ROME)
PEC_C, BOUNDARY_C = datetime(2024, 3, 20, 9, tzinfo=ROME), datetime(2024, 3, 31, tzinfo=ROME)
PEC_V, BOUNDARY_V = datetime(2024, 4, 5, 9, tzinfo=ROME), datetime(2024, 4, 16, tzinfo=ROME)
PEC_U, BOUNDARY_U = datetime(2024, 6, 1, 9, tzinfo=ROME), datetime(2024, 6, 12, tzinfo=ROME)
COMMENCEMENT_EVIDENCE = 'commencement evidence through the source deadline'


def fixture(record, kind, order=DDS113, **fields):
    return dict(record=record, kind=kind, order=order, source='f' * 64, selector=f'fixture:{record}',
                reading=f'FIXTURE {kind}: not a fact about {order}', fixture=True, **fields)


def parcel(foglio, particella):
    # The positions print no comune and the join does not compare it.
    return dict(comune='CASTELLANA GROTTE', foglio=foglio, particella=particella)


def plant(identifier):
    return dict(plant=identifier)


def delivery(record, recipient, *works, occurred=PEC_B, order=DDS113):
    return fixture(record, 'personal-delivery', order=order, recipient=recipient, occurred=occurred.isoformat(),
                   works=list(works))


def history(record, work, through, order=DDS113, start=None):
    return fixture(record, 'history', order=order, work=work,
                   complete_from=start or ('2023-10-16' if order == DDS113 else '2023-11-15'), complete_through=through)


def performed(record, work, occurred, kind='commencement', order=DDS113):
    return fixture(record, kind, order=order, work=work, occurred=occurred.isoformat())


class SuppliedRecordsAtPositions(unittest.TestCase):
    """One test per row of the rule table, on real positions, through the caller's path (join, then C per position)."""

    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.orders = {
            DDS113: [dict(RECORD, occurrence=f"{RECORD['occurrence']}:annex 1/D:position {k}", recipients=(p,))
                     for k, p in enumerate(positions(parse(BANDS, 3), '1/D'))],
            DDS124: [dict(RECORD_124, occurrence=f"{RECORD_124['occurrence']}:annex 1/D:position {k}", recipients=(p,))
                     for k, p in enumerate(POSITIONS_124.values())]}

    def run_records(self, supplied, order=DDS113, at=AT, evaluated_at=EVALUATED, governing=None):
        """`read_prescriptions.per_recipient` on a position clause: join, then C per position. Every supplied record
        ends counted, held, reported or unattached."""
        from cordon_d.case_prescriptions import position_attachments, recipient_results
        records = self.orders[order]
        attached, unattached = position_attachments(records, supplied)
        out = {}
        for record in records:
            if record['occurrence'] in attached:
                position = annex_position(record)
                out[position['owner']] = recipient_results(
                    self.s, record, at, attached[record['occurrence']], evaluated_at=evaluated_at, zone=ROME,
                    calendar=national_calendar(), position=position,
                    governing_results=governing or governing_results(self.s, record, at, position))
        seen = {u['record'] for u in unattached}
        for run in out.values():
            for item in run['recipients'].values():
                seen |= set(item['records']) | set(item['commencements']) | set(item['histories'])
            for item in run['reported']:
                seen |= {item['record']} if 'record' in item else set(item.get('records', ()))
        self.assertEqual(seen, {s['record'] for s in supplied}, 'a supplied record was silently lost')
        return out, unattached

    def result(self, out, owner):
        self.assertIn(owner, out)
        self.assertIn(owner, out[owner]['recipients'])
        return out[owner]['recipients'][owner]

    def reported(self, out, owner, record):
        return [r for r in out[owner]['reported'] if r.get('record') == record]

    def borghese(self, *extra, delivered=(parcel('57', '270'),), through='2023-11-30', **options):
        out, unattached = self.run_records([delivery('fx-pec-b', 'BORGHESE ANTONIO', *delivered),
                                            history('fx-h-270', parcel('57', '270'), through), *extra], **options)
        self.assertEqual(unattached, [])
        return out

    def comes(self, *extra, delivered=(parcel('33', '394'),), histories=(parcel('33', '394'),)):
        out, unattached = self.run_records(
            [delivery('fx-pec-comes', 'COMES VITO', *delivered, occurred=PEC_C, order=DDS124),
             *[history(f"fx-h-{w.get('plant') or w['particella']}", w, '2024-03-30', order=DDS124) for w in histories],
             *extra], order=DDS124)
        return out, unattached

    def test_row_1_a_delivery_naming_the_plant_or_its_parcel_is_the_recipients_notice(self):
        for label, delivered in (('parcel', parcel('57', '270')), ('plant', plant('1602200'))):
            with self.subTest(label):
                result = self.result(self.borghese(delivered=(delivered,)), 'BORGHESE ANTONIO')
                self.assertEqual((result['notification'], result['deadline']), (PEC_B, BOUNDARY_B))
                self.assertEqual(result['works'], [plant('1602200')])
                self.assertTrue(result['fixture'] and result['commencement_records_complete'])
                self.assertEqual(result['result'].effect, REQUIRED)
                self.assertIn(WITHDRAWAL + ':v1', result['result'].provisions)
        # COMES VITO: a delivery naming 1603982 alone. Both his plants stand on 33/394, whose history covers each;
        # 1616565, which the delivery does not name, is reported beside the result and never held.
        out, unattached = self.comes(delivered=(plant('1603982'),))
        self.assertEqual(unattached, [])
        result = self.result(out, 'COMES VITO')
        self.assertEqual(result['deadline'], BOUNDARY_C)
        self.assertEqual(result['result'].effect, REQUIRED)
        self.assertEqual([r['plants'] for r in out['COMES VITO']['reported']], [[plant('1616565')]])
        self.assertIn('not named by the delivery', out['COMES VITO']['reported'][0]['cause'])

    def test_row_2_a_delivery_naming_only_a_host_only_parcel_is_notice_and_the_parcel_is_withdrawn(self):
        out = self.borghese(delivered=(parcel('57', '78'),))
        result = self.result(out, 'BORGHESE ANTONIO')
        self.assertEqual(result['notification'], PEC_B)
        self.assertEqual(result['result'].effect, REQUIRED)
        [withdrawn] = self.reported(out, 'BORGHESE ANTONIO', 'fx-pec-b')
        self.assertEqual(withdrawn['works'], [dict(foglio='57', particella='78', comune='CASTELLANA GROTTE')])
        self.assertIn(f'withdrawn at this position: {WITHDRAWAL} (effective 2024-03-14)', withdrawn['cause'])
        out, unattached = self.run_records(
            [delivery('fx-pec-vp', 'CIAMPI VITO PASQUALE', parcel('32', '52'), occurred=PEC_V, order=DDS124),
             history('fx-h-293', parcel('32', '293'), '2024-04-15', order=DDS124)], order=DDS124)
        self.assertEqual(unattached, [])
        self.assertEqual(self.result(out, 'CIAMPI VITO PASQUALE')['result'].effect, REQUIRED)

    def test_row_3_a_history_of_the_plant_or_its_parcel_covers_it_through_Cs_deadline(self):
        short = self.result(self.borghese(through='2023-11-29'), 'BORGHESE ANTONIO')
        self.assertFalse(short['commencement_records_complete'])
        self.assertIsNone(short['result'].truth)
        self.assertIn(COMMENCEMENT_EVIDENCE, short['result'].needs)
        self.assertEqual(short['incomplete'], [plant('1602200')])
        out, _ = self.run_records([delivery('fx-pec-b', 'BORGHESE ANTONIO', parcel('57', '270')),
                                   history('fx-h-plant', plant('1602200'), '2023-11-30')])
        self.assertEqual(self.result(out, 'BORGHESE ANTONIO')['result'].effect, REQUIRED)
        out, _ = self.run_records([delivery('fx-pec-r', 'ROTOLO IRENE', parcel('57', '89')),
                                   history('fx-h-89', parcel('57', '89'), '2023-11-30')])
        self.assertEqual(self.result(out, 'ROTOLO IRENE')['result'].effect, REQUIRED)
        out, _ = self.comes(histories=(plant('1603982'),))
        comes = self.result(out, 'COMES VITO')
        self.assertIsNone(comes['result'].truth)
        self.assertEqual(comes['incomplete'], [plant('1616565')])

    def test_row_4_a_history_of_a_host_only_parcel_is_reported(self):
        out, unattached = self.run_records([delivery('fx-pec-b', 'BORGHESE ANTONIO', parcel('57', '270'))]
                                           + [history(f'fx-h-{p}', parcel('57', p), '2023-11-30')
                                              for p in ('78', '271', '273')])
        self.assertEqual(unattached, [])
        result = self.result(out, 'BORGHESE ANTONIO')
        self.assertIsNone(result['result'].truth)
        self.assertEqual(result['histories'], [])
        for p in ('78', '271', '273'):
            [report] = self.reported(out, 'BORGHESE ANTONIO', f'fx-h-{p}')
            self.assertIn('withdrawn at this position', report['cause'])

    def test_row_5_a_performance_naming_the_plant_counts_by_where_it_falls_against_the_deadline(self):
        for occurred, effect, outcome in ((datetime(2023, 11, 24, 9, tzinfo=ROME), NOT_ESTABLISHED, 'counts'),
                                          (datetime(2024, 3, 1, 9, tzinfo=ROME), REQUIRED, 'counts'),
                                          (date(2023, 11, 30), NOT_ESTABLISHED, 'counts'),
                                          (date(2023, 12, 1), REQUIRED, 'reported')):
            with self.subTest(occurred=occurred):
                out = self.borghese(fixture('fx-c-plant', 'commencement', work=plant('1602200'),
                                            occurred=occurred.isoformat()))
                result = self.result(out, 'BORGHESE ANTONIO')
                self.assertEqual(result['result'].effect, effect)
                self.assertEqual('fx-c-plant' in result['commencements'], outcome == 'counts')
                self.assertEqual([r['outcome'] for r in self.reported(out, 'BORGHESE ANTONIO', 'fx-c-plant')],
                                 [] if outcome == 'counts' else ['reported'])
        # A day-only record inside the term enters C at its day's start.
        counted = self.result(self.borghese(fixture('fx-c-plant', 'commencement', work=plant('1602200'),
                                                    occurred='2023-11-30')), 'BORGHESE ANTONIO')
        self.assertEqual(counted['commencements'], {'fx-c-plant': datetime(2023, 11, 30, tzinfo=ROME)})
        # COMES VITO: a removal naming 1616565 before his deadline.
        out, _ = self.comes(performed('fx-r-1616565', plant('1616565'), datetime(2024, 3, 25, 9, tzinfo=ROME),
                                      kind='removal', order=DDS124))
        self.assertEqual(self.result(out, 'COMES VITO')['result'].effect, NOT_ESTABLISHED)
        # The CIAMPI co-holders, noticed apart: a commencement naming 1605000 between their two deadlines follows
        # CIAMPI COSIMO's and precedes CIAMPI VITO PASQUALE's. NAUTICA CIAMPI S.R.L, with no delivery, has no result.
        out, unattached = self.run_records(
            [delivery('fx-pec-cc', 'CIAMPI COSIMO', parcel('32', '293'), occurred=PEC_C, order=DDS124),
             delivery('fx-pec-vp', 'CIAMPI VITO PASQUALE', parcel('32', '293'), occurred=PEC_V, order=DDS124),
             history('fx-h-293', parcel('32', '293'), '2024-04-15', order=DDS124),
             performed('fx-c-1605000', plant('1605000'), datetime(2024, 4, 10, 9, tzinfo=ROME), order=DDS124)],
            order=DDS124)
        self.assertEqual(unattached, [])
        cosimo, vito = self.result(out, 'CIAMPI COSIMO'), self.result(out, 'CIAMPI VITO PASQUALE')
        self.assertEqual((cosimo['deadline'], vito['deadline']), (BOUNDARY_C, BOUNDARY_V))
        self.assertEqual((cosimo['result'].effect, vito['result'].effect), (REQUIRED, NOT_ESTABLISHED))
        self.assertNotIn('NAUTICA CIAMPI S.R.L', out)

    def test_row_6_a_performance_printed_only_by_the_plants_parcel_holds_only_inside_the_term(self):
        inside = performed('fx-c-270', parcel('57', '270'), datetime(2023, 11, 24, 9, tzinfo=ROME))
        out = self.borghese(inside)
        held = self.result(out, 'BORGHESE ANTONIO')
        self.assertIsNone(held['result'].truth)
        self.assertEqual(held['commencements'], {})
        self.assertFalse(held['commencement_records_complete'])
        self.assertTrue(any(n.startswith('a record naming the plant 1602200: fx-c-270') for n in held['result'].needs))
        self.assertEqual([r['outcome'] for r in self.reported(out, 'BORGHESE ANTONIO', 'fx-c-270')], ['held'])
        moved = self.result(self.borghese(inside, performed('fx-c-plant', plant('1602200'),
                                                            datetime(2023, 11, 25, 9, tzinfo=ROME))),
                            'BORGHESE ANTONIO')
        self.assertEqual(moved['result'].effect, NOT_ESTABLISHED)
        for occurred in (datetime(2024, 3, 1, 9, tzinfo=ROME), date(2024, 3, 1)):
            with self.subTest(occurred=occurred):
                out = self.borghese(fixture('fx-c-270', 'commencement', work=parcel('57', '270'),
                                            occurred=occurred.isoformat()))
                self.assertEqual(self.result(out, 'BORGHESE ANTONIO')['result'].effect, REQUIRED)
                self.assertEqual([r['outcome'] for r in self.reported(out, 'BORGHESE ANTONIO', 'fx-c-270')],
                                 ['reported'])
        out, _ = self.comes(performed('fx-r-394', parcel('33', '394'), datetime(2024, 6, 3, 9, tzinfo=ROME),
                                      kind='removal', order=DDS124))
        self.assertEqual(self.result(out, 'COMES VITO')['result'].effect, REQUIRED)
        out, _ = self.run_records([delivery('fx-pec-r', 'ROTOLO IRENE', parcel('57', '89')),
                                   history('fx-h-89', parcel('57', '89'), '2023-11-30'),
                                   performed('fx-c-89', parcel('57', '89'), datetime(2023, 11, 24, 9, tzinfo=ROME))])
        rotolo = self.result(out, 'ROTOLO IRENE')
        self.assertIsNone(rotolo['result'].truth)
        self.assertTrue(any(n.startswith('a record naming the plant 1614393: fx-c-89') for n in rotolo['result'].needs))

    def test_row_7_a_performance_on_a_host_only_parcel_is_reported_on_any_date(self):
        for occurred in (datetime(2023, 11, 24, 9, tzinfo=ROME), datetime(2024, 3, 10, 9, tzinfo=ROME)):
            with self.subTest(occurred=occurred):
                out = self.borghese(performed('fx-c-78', parcel('57', '78'), occurred))
                result = self.result(out, 'BORGHESE ANTONIO')
                self.assertEqual(result['commencements'], {})
                self.assertEqual(result['result'].effect, REQUIRED)
                [report] = self.reported(out, 'BORGHESE ANTONIO', 'fx-c-78')
                self.assertIn(f'{WITHDRAWAL} (effective 2024-03-14)', report['cause'])
        out, _ = self.comes(fixture('fx-r-328', 'removal', order=DDS124, work=parcel('33', '328'),
                                    occurred='2024-03-25'))
        self.assertEqual(self.result(out, 'COMES VITO')['result'].effect, REQUIRED)
        self.assertEqual([r['outcome'] for r in self.reported(out, 'COMES VITO', 'fx-r-328')], ['reported'])

    def test_rows_8_to_10_a_position_not_due_in_part(self):
        # COMES VITTORIO holds hosts only, on 32/319, which COMES VITO's position also prints.
        on_319 = performed('fx-c-319', parcel('32', '319'), datetime(2024, 3, 25, 9, tzinfo=ROME), order=DDS124)
        out, unattached = self.run_records(
            [delivery('fx-pec-cv', 'COMES VITTORIO', parcel('32', '319'), occurred=PEC_C, order=DDS124), on_319,
             delivery('fx-pec-comes', 'COMES VITO', parcel('33', '394'), occurred=PEC_C, order=DDS124),
             history('fx-h-394', parcel('33', '394'), '2024-03-30', order=DDS124),
             history('fx-h-319', parcel('32', '319'), '2024-03-30', order=DDS124)], order=DDS124)
        self.assertEqual(unattached, [])
        vittorio = self.result(out, 'COMES VITTORIO')
        self.assertEqual(vittorio['notification'], PEC_C)
        self.assertIs(vittorio['result'].truth, False)
        self.assertEqual(vittorio['result'].effect, NOT_ESTABLISHED)
        self.assertEqual({r['record'] for r in out['COMES VITTORIO']['reported']}, {'fx-c-319', 'fx-h-319'})
        # At COMES VITO the same commencement is on a host-only parcel of a position due in part (row 7).
        self.assertEqual(self.result(out, 'COMES VITO')['result'].effect, REQUIRED)
        [report] = self.reported(out, 'COMES VITO', 'fx-c-319')
        self.assertIn('withdrawn at this position', report['cause'])
        # Unresolved: BORGHESE's position with its governing work result marked unknown (a FIXTURE result).
        cause = 'FIXTURE: the annex check for this position failed'
        unknown = Evaluation(None, needs=frozenset({cause}))
        governing = {(WITHDRAWAL, WORK): unknown, (WITHDRAWAL, COERCE): unknown}
        pec = delivery('fx-pec-b', 'BORGHESE ANTONIO', parcel('57', '270'), occurred=PEC_U)
        began = performed('fx-c-plant', plant('1602200'), datetime(2024, 6, 5, 9, tzinfo=ROME))
        out, _ = self.run_records([pec, began], governing=governing)
        held = self.result(out, 'BORGHESE ANTONIO')
        self.assertEqual(held['deadline'], BOUNDARY_U)
        self.assertIsNone(held['result'].truth)
        self.assertTrue(any(n.startswith('whether fx-c-plant performs work still due') and cause in n
                            for n in held['result'].needs))
        late = performed('fx-c-plant', plant('1602200'), datetime(2024, 6, 13, 9, tzinfo=ROME))
        out, _ = self.run_records([pec, late], governing=governing)
        self.assertEqual([r['outcome'] for r in self.reported(out, 'BORGHESE ANTONIO', 'fx-c-plant')], ['reported'])
        out, _ = self.run_records([pec], governing=governing, at=date(2024, 6, 5),
                                  evaluated_at=datetime(2024, 6, 5, 12, tzinfo=ROME))
        self.assertEqual(self.result(out, 'BORGHESE ANTONIO')['result'].effect, NOT_ESTABLISHED)

    def test_the_join(self):
        out, unattached = self.run_records([delivery('fx-pec-b', 'BORGHESE  ANTONIO', parcel('57', '270')),
                                            history('fx-h-270', parcel('57', '270'), '2023-11-30')])
        # The result stays keyed as the delivery prints the name.
        self.assertEqual(unattached, [])
        self.assertEqual(out['BORGHESE ANTONIO']['recipients']['BORGHESE  ANTONIO']['result'].effect, REQUIRED)
        supplied = [delivery('fx-pec-a', 'BORGHESE A.', parcel('57', '270')),
                    delivery('fx-pec-89', 'BORGHESE ANTONIO', parcel('57', '89')),
                    delivery('fx-pec-blank', ' ', parcel('57', '89')),
                    performed('fx-c-unlisted', plant('1600000'), datetime(2023, 11, 24, 9, tzinfo=ROME)),
                    history('fx-h-146', parcel('57', '146'), '2023-11-30')]
        out, unattached = self.run_records(supplied)
        self.assertEqual(out, {})
        self.assertEqual({u['record']: u['cause'] for u in unattached}, {
            'fx-pec-a': "no annex position of this order prints owner 'BORGHESE A.'",
            'fx-pec-89': "the annex position printing owner 'BORGHESE ANTONIO' prints no such work",
            'fx-pec-blank': 'names no recipient',
            'fx-c-unlisted': 'no annex position of this order prints this work',
            'fx-h-146': 'no supplied delivery joins an annex position printing this work'})
        self.assertEqual(next(u for u in unattached if u['record'] == 'fx-pec-89')['works'],
                         [dict(comune='CASTELLANA GROTTE', foglio='57', particella='89')])
        from cordon_d.case_prescriptions import position_attachments
        twin = dict(annex_position(self.orders[DDS113][0]))
        records = self.orders[DDS113] + [dict(self.orders[DDS113][0], recipients=(twin,),
                                              occurrence=self.orders[DDS113][0]['occurrence'] + ' bis')]
        attached, unattached = position_attachments(records, [delivery('fx-pec-twin', twin['owner'], *[
            parcel(p['foglio'], p['particella']) for p in twin['parcels']])])
        self.assertEqual(attached, {})
        self.assertEqual(unattached[0]['cause'], f"matches 2 annex positions printing owner '{twin['owner']}'")

    def test_the_date_column_places_a_day_by_its_start_and_end_in_Cs_zone(self):
        from cordon_d.case_prescriptions import date_column
        # A term in days ends at a midnight: no day contains it.
        self.assertEqual([date_column(d, BOUNDARY_B, ROME) for d in (date(2023, 11, 30), date(2023, 12, 1))],
                         ['D<', 'D>'])
        # A boundary inside a day (a term in hours; no held order states one, so on a real order this is UNTESTED).
        inside = datetime(2023, 12, 1, 9, tzinfo=ROME)
        self.assertEqual([date_column(d, inside, ROME) for d in (date(2023, 11, 30), date(2023, 12, 1),
                                                                 date(2023, 12, 2))], ['D<', 'D∋', 'D>'])
        self.assertEqual([date_column(t, inside, ROME) for t in (inside - timedelta(seconds=1), inside)], ['T<', 'T≥'])
        self.assertEqual(date_column(date(2023, 12, 1), None, ROME), '?')
        # In another zone the same day straddles a Rome midnight boundary.
        self.assertEqual(date_column(date(2023, 11, 30), BOUNDARY_B, ZoneInfo('America/New_York')), 'D∋')

    def test_a_day_containing_the_deadline_or_with_no_deadline_is_held(self):
        from cordon_d import case_prescriptions
        # The D∋ cell through recipient_results: C's boundary placed inside a day stands in for a term in hours.
        inside = datetime(2023, 11, 30, 15, tzinfo=ROME)
        day = fixture('fx-c-plant', 'commencement', work=plant('1602200'), occurred='2023-11-30')
        with mock.patch('cordon_c.quantities.clock_boundary', return_value=inside):
            out = self.borghese(day)
        result = self.result(out, 'BORGHESE ANTONIO')
        self.assertEqual(result['deadline'], inside)
        [report] = self.reported(out, 'BORGHESE ANTONIO', 'fx-c-plant')
        self.assertEqual(report['outcome'], 'held')
        self.assertFalse(result['commencement_records_complete'])
        self.assertTrue(any(n.startswith('the instant of fx-c-plant') for n in report['needs']))
        # No deadline (two deliveries at different instants): a timed record counts, a day-only one is held.
        out, _ = self.run_records([delivery('fx-pec-b', 'BORGHESE ANTONIO', parcel('57', '270')),
                                   delivery('fx-pec-b2', 'BORGHESE ANTONIO', parcel('57', '270'),
                                            occurred=PEC_B + timedelta(days=1)),
                                   day, performed('fx-c-timed', plant('1602200'), datetime(2023, 11, 24, 9, tzinfo=ROME))])
        result = self.result(out, 'BORGHESE ANTONIO')
        self.assertIsNone(result['deadline'])
        self.assertEqual(list(result['commencements']), ['fx-c-timed'])
        self.assertEqual([r['outcome'] for r in self.reported(out, 'BORGHESE ANTONIO', 'fx-c-plant')], ['held'])
        self.assertTrue(case_prescriptions.PERFORMANCE['work'] is case_prescriptions.PERFORMANCE['plant'])


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
        self.assertIn("'STRADE' (foglio 15)", found['STRADE']['no_recipient'])
        self.assertIn("'PROPRIETARI NON INDIVIDUATI' (foglio 15, particella 345)",
                      found['PROPRIETARI NON INDIVIDUATI']['no_recipient'])
        found = by_owner(self.read('138/2023')[1])
        self.assertEqual(found['ACQUE']['fifty_metre_parcels'], [dict(foglio='2', particella=None)])
        found = by_owner(self.read('124/2023')[1])
        self.assertEqual(found['COMES VITTORIO']['parcels'], [dict(foglio='32', particella='319')])
        self.assertEqual(found['COMES VITTORIO']['listed_infected_plants'], [])
        self.assertIn(dict(foglio='33', particella='394'), found['COMES VITO']['parcels'])
        self.assertTrue(found['COMES VITO']['listed_infected_plants'])

    def writer(self, *only, records=None):
        with tempfile.TemporaryDirectory() as tmp:
            out, supplied = Path(tmp) / 'out.json', Path(tmp) / 'records.json'
            extra = []
            if records is not None:
                supplied.write_text(json.dumps(records))
                extra = ['--records', str(supplied)]
            subprocess.run([sys.executable, str(ROOT / 'scripts/read_prescriptions.py'), '--only', *only,
                            '--out', str(out), *extra], check=True, capture_output=True, cwd=ROOT)
            written = json.loads(out.read_text())
            found = [r for e in written for r in e.get('records', ())]
            if records is not None:
                return found, next(e['supplied_records'] for e in written if 'supplied_records' in e)
            return found

    def test_the_join_tests_positions_and_124_record_are_the_retained_originals(self):
        found = by_owner(self.read('124/2023')[1])
        for owner, position in POSITIONS_124.items():
            self.assertEqual(found[owner], position)
        found, banded = by_owner(self.read('113/2023')[1]), by_owner(positions(parse(BANDS, 3), '1/D'))
        for owner in ('BORGHESE ANTONIO', 'ROTOLO IRENE'):
            self.assertEqual({k: v for k, v in found[owner].items() if k != 'rows'},
                             {k: v for k, v in banded[owner].items() if k != 'rows'})
        record = next(r for r in self.writer('124/2023') if ':clause:0:' in r['occurrence'])
        for key in ('instrument', 'adopted', 'source', 'part', 'term_literal', 'commitment', 'executor'):
            self.assertEqual(record[key], RECORD_124[key], key)
        self.assertEqual(tuple(record['stated_term']), RECORD_124['stated_term'])
        self.assertEqual(tuple(record['governing_A_references']), RECORD_124['governing_A_references'])

    def test_the_writer_joins_supplied_fixture_records_to_positions(self):
        # FIXTURE records (see `fixture`), through the ordinary caller on the retained 113/2023 original.
        supplied = [delivery('fx-pec-cisternino', 'CISTERNINO PAOLA', parcel('57', '146')),
                    history('fx-h-146', parcel('57', '146'), '2023-11-30'),
                    delivery('fx-pec-rotolo', 'ROTOLO IRENE', parcel('57', '89')),
                    history('fx-h-89', parcel('57', '89'), '2023-11-30'),
                    delivery('fx-pec-rossi', 'ROSSI FIXTURE', parcel('57', '89'))]
        records, report = self.writer('113/2023', records=supplied)
        clause0 = {annex_position(r)['owner']: r for r in records if ':clause:0:' in r['occurrence']}
        hosts_only = clause0['CISTERNINO PAOLA']['per_recipient']['CISTERNINO PAOLA']
        self.assertTrue(hosts_only['fixture'])
        self.assertIs(hosts_only['c']['truth'], False)
        holder = clause0['ROTOLO IRENE']['per_recipient']['ROTOLO IRENE']
        self.assertTrue(holder['fixture'] and holder['commencement_records_complete'])
        self.assertEqual(holder['c']['effect'], REQUIRED)
        self.assertIn(WITHDRAWAL + ':v1', holder['c']['provisions'])
        # Only the joined positions carry a per-recipient result; the cohort `c` of each is unchanged.
        self.assertEqual({o for o, r in clause0.items() if 'per_recipient' in r}, {'CISTERNINO PAOLA', 'ROTOLO IRENE'})
        self.assertEqual({r['occurrence']: r['c'] for r in records},
                         {r['occurrence']: r['c'] for r in self.writer('113/2023')})
        self.assertEqual([(u['record'], u['cause']) for u in report['unattached']],
                         [('fx-pec-rossi', "no annex position of this order prints owner 'ROSSI FIXTURE'")])

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
        # The two listings on no recipient (STRADE, 15/345) are among the not due.
        self.assertEqual((len(not_due), len(in_part)), (5, 3))
        self.assertEqual(sum(1 for r in not_due if annex_position(r)['owner'] is None), 2)
        self.assertFalse(any('no recipient' in n for r in records for n in r['c']['needs']))
        # PR #15's note that annex 1/D cannot be read no longer rides on the positions read from it.
        self.assertFalse(any(i.get('aspect') == 'coverage' and 'Allegato 1/D' in i.get('detail', '')
                             for r in records for i in r['issues']))
        self.assertTrue(all(any('Allegato 1/A' in i.get('detail', '') for i in r['issues']) for r in records))
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


HELD_387 = TAR_387['decision']['source']


@unittest.skipUnless(blob_path(STORE, HELD_387).exists() and blob_path(STORE, FIVE['96/2023']).exists(),
                     'retained originals not in the store')
class HeldTar387(unittest.TestCase):
    def test_the_96_positions_and_the_tar_387_2026_closure_are_the_held_ones(self):
        from cordon_d.judgments import annulment_basis, decision_identity, liveness_closures, read_disposition
        identity = decision_identity(blob_path(STORE, HELD_387).read_bytes())
        basis, _ = annulment_basis(read_disposition(HELD_387, STORE), identity, held_instruments={DDS96})
        self.assertEqual(liveness_closures(basis)[DDS96], [TAR_387])
        found = by_owner(annex_positions.read_annex(str(blob_path(STORE, FIVE['96/2023'])), '1/D')[1])
        self.assertEqual(found['BOGGIANO ANNA'], BOGGIANO)
        self.assertEqual(found['APULEO LUCIA'], APULEO)


HELD_115 = '3605a828fee12f4fc719ad3f0a7e7a2ba1a39226486b5c9b5dfa813fe18c5c3d'


@unittest.skipUnless(blob_path(STORE, HELD_115).exists(), 'retained original not in the store')
class NotFoundOwner(unittest.TestCase):
    def test_115_2023_places_15_336_on_no_recipient(self):
        # DDS 115/2023 (store 3605a828…5c3d), annex 1/D p. 24: "ALBEROBELLO 15 336 PROPRIETARI NON TROVATI".
        annex, found = annex_positions.read_annex(str(blob_path(STORE, HELD_115)), '1/D')
        self.assertEqual(annex['failures'], [])
        self.assertNotIn('PROPRIETARI NON TROVATI', {p['owner'] for p in found})
        listing = [p for p in found if dict(foglio='15', particella='336') in p['parcels']]
        self.assertEqual([(p['owner'], p['printed']) for p in listing], [(None, 'PROPRIETARI NON TROVATI')])
        self.assertIn("(foglio 15, particella 336)", listing[0]['no_recipient'])
        self.assertEqual(listing[0]['listed_infected_plants'], [])


if __name__ == '__main__':
    unittest.main()

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


DDS96 = 'REG-PUGLIA-U181-DIR-2023-00096'
FORK = 'REG-PUGLIA-U181-DIR-2023-00096:case-delta:pre-m4-monopoli-eradication-fork'
# DDS 96/2023 (store dd5bebb3…cbf7), annex 1/D p. 19 rows 11-12, as `read_annex` places them: BOGGIANO ANNA holds
# 50 m hosts only; APULEO LUCIA holds two listed infected plants.
BOGGIANO = dict(annex='allegato 1/D', owner='BOGGIANO ANNA', printed='BOGGIANO ANNA',
                parcels=[dict(foglio='17', particella='39')], fifty_metre_parcels=[dict(foglio='17', particella='39')],
                listed_infected_plants=[], rows=['p. 19 row 11'])
APULEO = dict(annex='allegato 1/D', owner='APULEO LUCIA', printed='APULEO LUCIA',
              parcels=[dict(foglio='17', particella=p) for p in ('46', '66', '159', '245', '246')],
              fifty_metre_parcels=[dict(foglio='17', particella=p) for p in ('46', '66', '159', '245', '246')],
              listed_infected_plants=['1455708', '1584865'], rows=['p. 19 row 12'])
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


# Supplied Osservatorio records joined to DDS 113/2023's positions (PR #33's caller). Every record below is a
# FIXTURE (`fixture: true`): its instants, sources and parcels are invented in the shape of the annex. None is a
# fact about the order.
PEC = datetime(2024, 3, 20, 9, tzinfo=ROME)
BEFORE, AFTER = date(2024, 3, 25), date(2024, 4, 5)


def fixture(record, kind, **fields):
    return dict(record=record, kind=kind, order=DDS113, source='f' * 64, selector=f'fixture:{record}',
                reading=f'FIXTURE {kind}: not a fact about DDS 113/2023', fixture=True, **fields)


def parcel(foglio, particella):
    return dict(comune='CASTELLANA GROTTE', foglio=foglio, particella=particella)


def delivery(record, recipient, *parcels):
    return fixture(record, 'personal-delivery', recipient=recipient, occurred=PEC.isoformat(),
                   works=[parcel(f, p) for f, p in parcels])


def history(record, foglio, particella, through='2024-04-04'):
    return fixture(record, 'history', work=parcel(foglio, particella), complete_from='2023-10-16',
                   complete_through=through)


class SuppliedRecordsAtPositions(unittest.TestCase):
    """A supplied record joins the 113/2023 position that prints its owner and parcel; the position's
    governing rows and the recipient's notice and commencement reach C together."""

    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        found = positions(parse(BANDS, 3), '1/D')
        cls.records = [dict(RECORD, occurrence=f"{RECORD['occurrence']}:annex 1/D:position {k}", recipients=(p,))
                       for k, p in enumerate(found)]

    def run_records(self, supplied, at=AFTER):
        """The caller's path (`read_prescriptions.per_recipient` on a position clause): join, then C per position."""
        from cordon_d.case_prescriptions import position_attachments, recipient_results
        attached, unattached = position_attachments(self.records, supplied)
        out = {}
        for record in self.records:
            if record['occurrence'] in attached:
                position = annex_position(record)
                run = recipient_results(self.s, record, at, attached[record['occurrence']],
                                        evaluated_at=datetime.combine(at, datetime.min.time(), ROME).replace(hour=12),
                                        zone=ROME, calendar=national_calendar(), position=position,
                                        governing_results=governing_results(self.s, record, at, position))
                out[position['owner']] = run
        return out, unattached

    def test_a_delivery_to_a_hosts_only_owner_gives_no_direction(self):
        supplied = [delivery('fx-pec-cisternino', 'CISTERNINO PAOLA', ('57', '146')), history('fx-h-146', '57', '146')]
        out, unattached = self.run_records(supplied)
        self.assertEqual(unattached, [])
        result = out['CISTERNINO PAOLA']['recipients']['CISTERNINO PAOLA']
        self.assertTrue(result['fixture'])
        self.assertIsNotNone(result['notification'])
        self.assertTrue(result['commencement_records_complete'])
        self.assertIs(result['result'].truth, False)
        self.assertEqual(result['result'].effect, NOT_ESTABLISHED)
        self.assertIn(WITHDRAWAL + ':v1', result['result'].provisions)
        # The joint owner of 57/146 is not reached by her delivery.
        self.assertNotIn('IPPOLITO MARIA', out)

    def test_a_delivery_to_a_letter_a_holder_gives_a_direction_once_the_term_passes(self):
        supplied = [delivery('fx-pec-rotolo', 'ROTOLO IRENE', ('57', '89')), history('fx-h-89', '57', '89')]
        before, _ = self.run_records(supplied[:1] + [history('fx-h-89', '57', '89', through='2024-03-25')], BEFORE)
        self.assertNotEqual(before['ROTOLO IRENE']['recipients']['ROTOLO IRENE']['result'].effect, REQUIRED)
        out, unattached = self.run_records(supplied)
        self.assertEqual(unattached, [])
        result = out['ROTOLO IRENE']['recipients']['ROTOLO IRENE']
        self.assertTrue(result['commencement_records_complete'])
        self.assertEqual(result['result'].effect, REQUIRED)
        self.assertIn(WITHDRAWAL + ':v1', result['result'].provisions)
        # Without the history, C waits on commencement evidence and gives no direction.
        waiting, _ = self.run_records(supplied[:1])
        self.assertIsNone(waiting['ROTOLO IRENE']['recipients']['ROTOLO IRENE']['result'].truth)
        # A commencement on the position's parcel before the deadline moves the holder to false.
        began = fixture('fx-verbale-89', 'commencement', work=parcel('57', '89'),
                        occurred=(PEC + timedelta(days=2)).isoformat())
        moved, _ = self.run_records(supplied + [began])
        self.assertIs(moved['ROTOLO IRENE']['recipients']['ROTOLO IRENE']['result'].truth, False)

    def test_a_delivery_whose_owner_matches_no_position_is_unattached(self):
        supplied = [delivery('fx-pec-rossi', 'ROSSI FIXTURE', ('57', '89')),
                    delivery('fx-pec-rotolo-off', 'ROTOLO IRENE', ('57', '146')),
                    delivery('fx-pec-blank', ' ', ('57', '89')), history('fx-h-345', '15', '345'),
                    history('fx-h-999', '57', '999')]
        out, unattached = self.run_records(supplied)
        self.assertEqual(out, {})
        causes = {u['record']: u['cause'] for u in unattached}
        self.assertEqual(causes, {
            'fx-pec-rossi': "no annex position of this order prints owner 'ROSSI FIXTURE'",
            'fx-pec-rotolo-off': "the annex position printing owner 'ROTOLO IRENE' prints no such work",
            'fx-pec-blank': 'names no recipient',
            'fx-h-345': 'no supplied delivery joins an annex position printing this work',
            'fx-h-999': 'no annex position of this order prints this work'})

    def test_a_delivery_matching_several_positions_is_unattached(self):
        twin = dict(annex_position(self.records[0]))
        records = self.records + [dict(self.records[0], occurrence=self.records[0]['occurrence'] + ' bis',
                                       recipients=(twin,))]
        from cordon_d.case_prescriptions import position_attachments
        name = twin['owner']
        works = [(p['foglio'], p['particella']) for p in twin['parcels']]
        attached, unattached = position_attachments(records, [delivery('fx-pec-twin', name, *works)])
        self.assertEqual(attached, {})
        self.assertEqual(unattached[0]['cause'], f"matches 2 annex positions printing owner '{name}'")

    def test_a_position_parcel_no_delivery_names_leaves_the_history_incomplete(self):
        # BORGHESE ANTONIO's position prints 57/78, 270, 271 and 273; a delivery naming 57/270 alone never decides.
        supplied = [delivery('fx-pec-borghese', 'BORGHESE ANTONIO', ('57', '270')), history('fx-h-270', '57', '270')]
        out, _ = self.run_records(supplied)
        run = out['BORGHESE ANTONIO']
        self.assertFalse(run['recipients']['BORGHESE ANTONIO']['commencement_records_complete'])
        self.assertNotEqual(run['recipients']['BORGHESE ANTONIO']['result'].effect, REQUIRED)
        self.assertTrue(any(r.get('parcels') and 'no supplied delivery names' in r['cause'] for r in run['reported']))


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

    def test_the_writer_joins_supplied_fixture_records_to_positions(self):
        # FIXTURE records (see `fixture`), through the ordinary caller on the retained 113/2023 original.
        supplied = [delivery('fx-pec-cisternino', 'CISTERNINO PAOLA', ('57', '146')), history('fx-h-146', '57', '146'),
                    delivery('fx-pec-rotolo', 'ROTOLO IRENE', ('57', '89')), history('fx-h-89', '57', '89'),
                    delivery('fx-pec-rossi', 'ROSSI FIXTURE', ('57', '89'))]
        records, report = self.writer('113/2023', records=supplied)
        clause0 = {annex_position(r)['owner']: r for r in records if ':clause:0:' in r['occurrence']}
        hosts_only = clause0['CISTERNINO PAOLA']['per_recipient']['CISTERNINO PAOLA']
        self.assertTrue(hosts_only['fixture'] and hosts_only['commencement_records_complete'])
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

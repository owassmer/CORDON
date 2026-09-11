"""Row 3: the act's own area statement, and what it refuses to answer.

These tests are written against the reader's obligations rather than against
the acts that happened to be opened while writing it. Each one names the wrong
answer it exists to prevent, because every defect this row has had so far
surfaced as a confident answer rather than as a failure.
"""
import json
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cordon_d.areas import (CadastralStatement, Sheet, annexes, read_scope,
                            versions, zone_of, membership_evidence, _zone_from)

ROOT = Path(__file__).resolve().parents[2]


def statement(scope, sheets=(), *, zone='infetta', comune='TRIGGIANO',
              province='BARI', regime=None):
    return CadastralStatement(zone, 'ZONA INFETTA', province, comune, scope,
                              tuple(sheets), 'text', regime)


class ScopeGrammar(unittest.TestCase):
    """What the act writes, read whole - or not read at all."""

    def test_inclusive_range_is_every_sheet_it_states(self):
        # DDS 127/2022 states Fasano's containment sheets as ranges. Reading
        # only the endpoints answered False for every sheet between them.
        scope = read_scope('FOGLI: da 15 a 32; da 34 a 44; 84, 85')
        numbers = [s.number for s in scope.sheets]
        self.assertEqual(len(numbers), 18 + 11 + 2)
        self.assertIn('20', numbers)
        self.assertTrue(scope.fully_read)

    def test_range_without_da_is_still_a_range(self):
        scope = read_scope('FOGLI SEZIONE A: 114, 116; 161 a 172')
        self.assertIn('165', [s.number for s in scope.sheets])
        self.assertTrue(all(s.section == 'A' for s in scope.sheets))

    def test_asterisk_is_kept_as_the_act_prints_it(self):
        scope = read_scope('FOGLI: 1*, 2, 3*')
        self.assertEqual([(s.number, s.wholly_contained) for s in scope.sheets],
                         [('1', True), ('2', False), ('3', True)])

    def test_each_clause_keeps_its_own_sheet_and_parcels(self):
        scope = read_scope('FOGLIO 5: particelle 260, 264; FOGLIO 6: particelle 10, 11')
        self.assertEqual([(s.number, s.parcels) for s in scope.sheets],
                         [('5', ('260', '264')), ('6', ('10', '11'))])

    def test_part_of_a_comune_with_its_sheets_is_those_sheets(self):
        scope = read_scope('PARTE TERRITORIO COMUNALE: FOGLIO: 6')
        self.assertEqual(scope.kind, 'sheets')
        self.assertEqual([s.number for s in scope.sheets], ['6'])

    def test_part_of_a_comune_without_sheets_states_no_extent(self):
        self.assertEqual(read_scope('PARTE TERRITORIO COMUNALE').kind,
                         'part-comune-extent-unstated')

    def test_a_development_stays_attached_to_its_sheet(self):
        scope = read_scope('FOGLI: 190, 193(SVILUPPO Z)')
        self.assertEqual(scope.sheets[-1].qualifier, '(SVILUPPO Z)')

    def test_an_unknown_form_is_not_read_at_all(self):
        # The reader must not keep the part it understood: a statement narrower
        # than the act's answers False for what the act includes.
        for text in ('INTERO TERRITORIO COMUNALE, AD ECCEZIONE DEL FOGLIO 5',
                     'FOGLI: 1, 2 SALVO LE AREE BOSCHIVE',
                     'FOGLI: 1, 2 esclusi i terreni demaniali'):
            with self.subTest(text=text):
                self.assertFalse(read_scope(text).fully_read)


class ZoneFromCaption(unittest.TestCase):
    """The zone a caption names, and the measures it says apply there."""

    def test_head_word_names_the_zone(self):
        for caption, zone in (
                ('ZONA INFETTA IN PROVINCIA DI LECCE', 'infetta'),
                ('ZONA DI CONTENIMENTO', 'contenimento'),
                ('ZONA CUSCINETTO', 'cuscinetto'),
                ('FOCOLAI PUNTIFORMI DI MOLA DI BARI E NOCI', 'focolaio')):
            with self.subTest(caption=caption):
                self.assertEqual(_zone_from(caption)[0], zone)

    def test_a_qualifier_does_not_replace_the_zone(self):
        # A buffer described by reference to another zone is still a buffer.
        for caption in ('ZONA CUSCINETTO DEI FOCOLAI DI ERADICAZIONE',
                        'ZONA CUSCINETTO DELLA ZONA DI CONTENIMENTO'):
            with self.subTest(caption=caption):
                self.assertEqual(_zone_from(caption)[0], 'cuscinetto')

    def test_zone_and_regime_are_two_facts(self):
        zone, _, regime = _zone_from(
            'ZONA INFETTA IN CUI SI APPLICANO MISURE DI CONTENIMENTO')
        self.assertEqual((zone, regime), ('infetta', 'contenimento'))
        zone, _, regime = _zone_from(
            'ZONA CUSCINETTO IN CUI SI APPLICANO MISURE DI ERADICAZIONE')
        self.assertEqual((zone, regime), ('cuscinetto', 'eradicazione'))


class WhatAStatementDecides(unittest.TestCase):
    """The grain of the question, and the identity it must carry."""

    def test_partial_sheet_reaches_the_sheet_but_not_a_parcel(self):
        # Stage A asks about a point or parcel. A sheet the act says merely
        # intersects the zone does not place any particular parcel inside it.
        s = statement('sheets', [Sheet(None, '3', False)])
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='3', grain='sheet'), True)
        self.assertIsNone(s.covers(comune='TRIGGIANO', foglio='3', grain='parcel'))

    def test_wholly_contained_sheet_decides_a_parcel(self):
        s = statement('sheets', [Sheet(None, '3', True)])
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='3', grain='parcel'), True)

    def test_named_parcels_decide_only_those_parcels(self):
        s = statement('sheets', [Sheet(None, '5', False, ('260', '264'))])
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='5', particella='260'), True)
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='5', particella='999'), False)
        self.assertIsNone(s.covers(comune='TRIGGIANO', foglio='5'))

    def test_a_place_must_be_identified(self):
        s = statement('whole-comune')
        self.assertIsNone(s.covers())
        self.assertIs(s.covers(comune='TRIGGIANO'), True)

    def test_a_contradicting_province_is_not_a_match(self):
        s = statement('whole-comune')
        self.assertIsNone(s.covers(comune='TRIGGIANO', province='LECCE'))

    def test_a_sectioned_sheet_needs_its_section(self):
        s = statement('sheets', [Sheet('G', '2', True)])
        self.assertIsNone(s.covers(comune='TRIGGIANO', foglio='2'))
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='2', section='G'), True)
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='2', section='A'), False)

    def test_a_province_statement_needs_a_province(self):
        s = CadastralStatement('infetta', 'ZONA INFETTA', 'LECCE', None,
                               'whole-province', (), 'INTERO TERRITORIO PROVINCIALE')
        self.assertIsNone(s.covers(comune='NARDO'))
        self.assertIs(s.covers(province='LECCE'), True)

    def test_unstated_extent_decides_nothing(self):
        s = statement('part-comune-extent-unstated')
        self.assertIsNone(s.covers(comune='TRIGGIANO', foglio='6'))


class AnnexList(unittest.TestCase):
    """The integrity check's own inputs."""

    def test_an_unnumbered_bundled_annex_is_recovered(self):
        text = ('ALLEGATI INTEGRANTI\n\n Documento - Impronta (SHA256)\n'
                ' Allegato.pdf -\n ' + 'a' * 64 + '\n\nIl presente Provvedimento')
        got = annexes(text)
        self.assertEqual([(a.name, a.stated_sha256) for a in got],
                         [('Allegato.pdf', 'a' * 64)])

    def test_one_entry_never_borrows_its_neighbours_hash(self):
        text = ('ALLEGATI INTEGRANTI\n\n ALLEGATO 1.pdf -\n\n ALLEGATO 2.pdf -\n '
                + 'b' * 64 + '\n\nIl presente Provvedimento')
        got = {a.name: a.stated_sha256 for a in annexes(text)}
        self.assertIsNone(got['ALLEGATO 1.pdf'])
        self.assertEqual(got['ALLEGATO 2.pdf'], 'b' * 64)


class AgainstTheAcceptedPopulation(unittest.TestCase):
    """The whole population, through the paths a consumer uses."""

    @classmethod
    def setUpClass(cls):
        cls.versions = versions(ROOT)

    def test_every_accepted_area_version_is_present(self):
        rows = json.loads(
            (ROOT / 'regulation/jurisdiction/canonical/authoring.json').read_text())
        rows = rows if isinstance(rows, list) else list(rows.values())[0]
        expected = {r['provision_version_id'] for r in rows
                    if 'area-state-transition' in r['provision_version_id']
                    or 'area-update' in r['provision_version_id']
                    or 'area-act-before-gis' in r['provision_version_id']}
        self.assertEqual({v.provision_version_id for v in self.versions}, expected)

    def test_no_statement_is_emitted_from_a_partly_read_cell(self):
        for version in self.versions:
            for s in version.statements:
                with self.subTest(version=version.provision_version_id):
                    self.assertTrue(read_scope(s.text).fully_read)

    def test_an_unheld_body_reads_nothing_and_says_so(self):
        held = [v for v in self.versions if v.geography_form == 'body-unheld']
        self.assertTrue(held)
        for version in held:
            self.assertEqual(version.statements, ())
            self.assertTrue(version.unresolved)

    def test_the_fasano_range_reaches_the_consumer(self):
        answers = zone_of(self.versions, date(2023, 6, 1), comune='FASANO',
                          foglio='20', grain='sheet')
        self.assertIn('contenimento', [a['zone'] for a in answers])

    def test_an_act_that_left_something_unread_says_so_even_when_it_answers(self):
        unread = next(v for v in self.versions if v.unresolved and v.statements)
        s = unread.statements[0]
        answers = zone_of(self.versions, unread.effective_from, comune=s.comune,
                          province=s.province, grain='sheet')
        mine = [a for a in answers if a['version'] == unread.provision_version_id]
        self.assertTrue(any(a['basis'] == 'part of this act was not read' for a in mine))

    def test_an_unidentified_question_is_refused(self):
        with self.assertRaises(ValueError):
            membership_evidence(self.versions, ROOT, date(2026, 9, 1))

    def test_assertions_carry_the_annex_row_that_supports_them(self):
        _, assertions = membership_evidence(
            self.versions, ROOT, date(2026, 9, 1), comune='CAROSINO',
            known_at=datetime(2026, 9, 11, tzinfo=timezone.utc))
        self.assertTrue(assertions)
        for assertion in assertions:
            self.assertTrue(assertion.value)
            self.assertTrue(assertion.support)
            self.assertTrue(assertion.support[0].reading)


class AcquisitionProvenance(unittest.TestCase):
    """A resumed capture must not date old bytes to the run that reused them."""

    def test_retained_pages_carry_their_own_capture_time(self):
        records = sorted((ROOT / 'corpus/sources/areas/sit').glob('*/*/*/release.json'))
        self.assertTrue(records)
        for path in records:
            record = json.loads(path.read_text())
            with self.subTest(layer=record['name']):
                for page in record['pages']:
                    self.assertIsNotNone(page.get('captured_at'))
                self.assertLessEqual(record['captured_from'], record['captured_through'])
                # The interval reported is the pages' own, never the run's.
                self.assertEqual(record['captured_from'],
                                 min(p['captured_at'] for p in record['pages']))


if __name__ == '__main__':
    unittest.main()

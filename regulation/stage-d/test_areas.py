"""Row 3: the act's own area statement, and what it refuses to answer.

These tests are written against the reader's obligations rather than against
the acts that happened to be opened while writing it. Each one names the wrong
answer it exists to prevent, because every defect this row has had so far
surfaced as a confident answer rather than as a failure.
"""
import json
import sys
import unittest
from tempfile import TemporaryDirectory
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cordon_d.areas import (CadastralStatement, Sheet, annexes, read_scope,
                            versions, zone_of, membership_evidence, _zone_from,
                            MATERIAL_NOT_HELD, READING_DID_NOT_RECOVER,
                            RECOVERED_NOT_ATTACHED, RECOVERED_UNADJUDICATED, SOURCE_STATES_NONE,
                            pinned_statements)

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

    def test_sheet_annex_keeps_its_identity_and_asterisk(self):
        scope = read_scope('FOGLI 19, 19-ALLEGATO A*, 20*')
        self.assertTrue(scope.fully_read)
        self.assertEqual([(s.number, s.qualifier, s.wholly_contained) for s in scope.sheets],
                         [('19', None, False), ('19', 'ALLEGATO A', True), ('20', None, True)])
        self.assertIsNone(statement('sheets', scope.sheets).covers(comune='TRIGGIANO', foglio='19'))

    def test_missing_inventory_cannot_be_a_complete_empty_reading(self):
        with TemporaryDirectory() as directory:
            statements, unresolved, _, _ = pinned_statements(Path(directory), 'source')
        self.assertFalse(statements)
        self.assertTrue(unresolved)

    def test_previously_excluded_page_still_requires_a_reading(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            readings = root / 'corpus/sources/areas/readings'
            readings.mkdir(parents=True)
            (readings / 'INVENTORY.json').write_text(json.dumps([
                {'act_sha256': 'source', 'page': 1, 'candidate': False}]))
            _, _, _, unread = pinned_statements(root, 'source')
            self.assertEqual(unread, (1,))

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
        scope = read_scope('FOGLIO 5: particelle 260, 264*; FOGLIO 10: particelle 19*, 20')
        s = statement('sheets', scope.sheets)
        self.assertIsNone(s.covers(comune='TRIGGIANO', foglio='5', particella='260'))
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='5', particella='264'), True)
        self.assertIs(s.covers(comune='TRIGGIANO', foglio='10', particella='19'), True)
        self.assertIsNone(s.covers(comune='TRIGGIANO', foglio='10', particella='20'))
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
        held = [v for v in self.versions if v.geography_form == 'body-not-held']
        self.assertTrue(held)
        for version in held:
            self.assertEqual(version.statements, ())
            self.assertTrue(any(c.startswith(MATERIAL_NOT_HELD) for c in version.absence))

    def test_every_version_that_supplies_nothing_names_its_cause(self):
        # A version that answers nothing and says nothing reads, to the
        # operator, exactly like a version that is not in force: no duty.
        for version in self.versions:
            if version.statements:
                continue
            with self.subTest(version=version.provision_version_id):
                self.assertTrue(version.absence,
                                'supplies no statement and names no cause')

    def test_an_act_adopting_maps_is_not_blamed_on_the_reader(self):
        # DDS 69/2021 adopts Allegato 1 and 1 bis as integral parts of itself,
        # and both are maps: all seven pages read, no cadastral table printed.
        # Calling it an act that states a rule would write a reading limit into
        # the owner as a property of the source; calling the absence a reading
        # failure points the operator at a reader when the remedy is map
        # registration. Until its pages are all read, the reading is the cause.
        version = next(v for v in self.versions
                       if '2021-00069' in v.provision_version_id)
        self.assertEqual(version.geography_form, 'annexed')
        self.assertEqual(version.statements, ())
        self.assertEqual(len(version.absence), 1)
        cause = version.absence[0]
        if 'pages have not all been read' in cause:
            self.assertTrue(cause.startswith(READING_DID_NOT_RECOVER))
        else:
            self.assertTrue(cause.startswith(SOURCE_STATES_NONE))
            self.assertIn('complete page reading', cause)

    def test_the_causes_are_distinguishable(self):
        vocabulary = {SOURCE_STATES_NONE, MATERIAL_NOT_HELD, READING_DID_NOT_RECOVER,
                      RECOVERED_NOT_ATTACHED, RECOVERED_UNADJUDICATED}
        causes = {c.split(':')[0] for v in self.versions for c in v.absence}
        self.assertTrue(causes <= vocabulary, causes - vocabulary)
        # The population exercises three of them whatever the state of reading:
        # an act adopting maps, an act whose body is not held, an act stating a rule.
        self.assertIn(SOURCE_STATES_NONE, causes)
        self.assertIn(MATERIAL_NOT_HELD, causes)
        self.assertIn(RECOVERED_NOT_ATTACHED, causes)

    def test_a_version_in_force_always_accounts_for_itself(self):
        # Asked about a place no act mentions, on a day four versions are in
        # force, every one of them is answered for.
        day = date(2026, 9, 1)
        forced = {v.provision_version_id for v in self.versions if v.in_force_on(day)}
        answered = {a['version'] for a in
                    zone_of(self.versions, day, comune='MILANO', province='MILANO',
                            foglio='1', grain='sheet')}
        self.assertEqual(forced - answered, set())

    def test_an_act_stating_a_rule_names_what_it_does_not_supply(self):
        version = next(v for v in self.versions if v.geography_form == 'stated-rule')
        answers = zone_of(self.versions, version.effective_from, comune='TRIGGIANO',
                          province='BARI', foglio='3', grain='sheet')
        mine = [a for a in answers if a['version'] == version.provision_version_id]
        self.assertTrue(mine)
        self.assertTrue(mine[0]['basis'].startswith(RECOVERED_NOT_ATTACHED))

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
        self.assertTrue(any(a['basis'].startswith(READING_DID_NOT_RECOVER)
                            for a in mine))

    def test_an_unidentified_question_is_refused(self):
        with self.assertRaises(ValueError):
            membership_evidence(self.versions, ROOT, date(2026, 9, 1))

    def test_assertions_carry_the_annex_row_that_supports_them(self):
        _, assertions = membership_evidence(
            self.versions, ROOT, date(2024, 11, 20), comune='CAROSINO',
            known_at=datetime(2026, 9, 11, tzinfo=timezone.utc))
        self.assertTrue(assertions)
        for assertion in assertions:
            self.assertTrue(assertion.value)
            self.assertTrue(assertion.support)
            self.assertTrue(assertion.support[0].reading)
            self.assertIn('p7 table', assertion.support[0].selector)
            self.assertIn('FOGLI', assertion.support[0].reading)

    def test_parcel_membership_cannot_be_reused_as_sheet_membership(self):
        version = next(v for v in self.versions if '2024-00008' in v.provision_version_id)
        _, assertions = membership_evidence(
            (version,), ROOT, version.effective_from, comune='TRIGGIANO',
            foglio='5', particella='818')
        self.assertTrue(assertions)
        self.assertTrue(all('particella 818' in a.context for a in assertions))
        _, intersecting = membership_evidence(
            (version,), ROOT, version.effective_from, comune='TRIGGIANO',
            foglio='5', particella='260')
        self.assertTrue(intersecting)  # the buffer table separately includes the whole sheet
        self.assertTrue(all('particella 260' in a.context for a in intersecting))
        self.assertFalse({a.context for a in assertions} & {a.context for a in intersecting})


if __name__ == '__main__':
    unittest.main()

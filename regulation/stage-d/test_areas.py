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
                            RECOVERED_NOT_ATTACHED, SOURCE_STATES_NONE,
                            pinned_statements, published_geography)

ROOT = Path(__file__).resolve().parents[2]


class PublishedGeography(unittest.TestCase):
    def test_native_parts_and_capture_time_survive_without_adopted_assignment(self):
        from unittest.mock import patch
        from cordon_d.store import put_bytes, blob_path
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = root / 'store'
            rings = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                     [[2, 2], [8, 2], [8, 8], [2, 8], [2, 2]]]
            data = {'spatialReference': {'wkid': 32633}, 'features': [
                {'attributes': {'OID': 7, 'label': 'Buffer in another region'},
                 'geometry': {'rings': rings}}]}
            digest = put_bytes(store, json.dumps(data).encode())
            capture = dict(url='https://publisher.example/layer', sha256=digest,
                           captured_at='2026-09-14T12:00:00+00:00',
                           format='arcgis', oid_field='OID')
            path = root / 'corpus/sources/areas/acts.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps([{'publisher_geometry_candidates': [capture]}]))
            with patch.dict('os.environ', {'CORDON_STORE': str(store)}):
                self.assertEqual(list(published_geography(root, known_through=
                    datetime(2026, 9, 13, tzinfo=timezone.utc))), [])
                context, occurrence = next(published_geography(root, known_through=
                    datetime(2026, 9, 15, tzinfo=timezone.utc)))
                self.assertEqual(occurrence.values['geometry']['rings'], rings)
                self.assertEqual(occurrence.locator, 'feature:0:OID:7')
                self.assertEqual(context, capture)
                with self.assertRaisesRegex(ValueError, 'timezone'):
                    list(published_geography(root, known_through=datetime(2026, 9, 15)))
                blob = blob_path(store, digest)
                blob.chmod(0o644)
                blob.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'bytes changed'):
                    list(published_geography(root, known_through=
                        datetime(2026, 9, 15, tzinfo=timezone.utc)))


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

    def test_the_province_never_decides_a_comune_scoped_statement(self):
        # The acts print one province as "BARI" in one act and "BA" in the
        # next. Treating the spelling the question uses as a contradiction
        # dropped the row and reported the act as silent about the place; the
        # comune identifies the place, and the act's own province stays in
        # the assertion's support for the caller to see.
        s = statement('whole-comune', province='BA')
        for province in ('BA', 'BARI', 'LECCE', None):
            with self.subTest(province=province):
                self.assertIs(s.covers(comune='TRIGGIANO', province=province), True)
        self.assertIsNone(s.covers(comune='CAPURSO', province='BA'))

    def test_unfamiliar_range_forms_are_not_read_at_all(self):
        # A dash range read as its endpoints drops every sheet between them;
        # a range of particelle read as sheets places sheets the act never
        # names. No held act writes either form, so both must surface as
        # unread on first contact rather than as a confident answer.
        for text in ('FOGLI: 100-105', 'FOGLI 12 – 15, 18', 'FOGLI 7*-9*', 'FOGLI da 7 a 9*',
                     'FOGLIO 5: particelle da 260 a 264', 'FOGLI: 1, 2, particelle 5 a 9'):
            with self.subTest(text=text):
                self.assertFalse(read_scope(text).fully_read)
        # An asterisk the grammar did not attach is consequential residue; a
        # stray comma is not.
        self.assertTrue(read_scope('FOGLI: 1*, 2,').fully_read)
        # The one dash the population prints keeps its own reading.
        self.assertTrue(read_scope('FOGLI 19, 19-ALLEGATO A*').fully_read)

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

    def test_an_act_adopting_maps_states_its_geography_unread(self):
        # DDS 69/2021 adopts Allegato 1 and 1 bis as integral parts of itself,
        # and both are maps with the cadastral sheets drawn on the map face:
        # all seven pages read, no cadastral table printed. The act states its
        # geography; a map read as an image and not recovered into zones is
        # this reading's limit, never the source's silence, and the cause
        # names the remedy - registering the maps - so the operator is not
        # told the question is closed against the act.
        version = next(v for v in self.versions
                       if '2021-00069' in v.provision_version_id)
        self.assertEqual(version.geography_form, 'annexed')
        self.assertEqual(version.statements, ())
        self.assertEqual(len(version.absence), 1)
        cause = version.absence[0]
        self.assertTrue(cause.startswith(READING_DID_NOT_RECOVER))
        self.assertFalse(cause.startswith(SOURCE_STATES_NONE))
        self.assertIn('registering the maps', cause)

    def test_a_reached_place_and_an_unmentioned_place_get_different_answers(self):
        # DDS 106/2025 lists Ginosa sheet 36 unstarred in its buffer table and
        # partially in its infected table: the zone reaches the sheet and the
        # act does not say which part. Sheet 999 it never mentions. Both yield
        # no membership assertion, and they must not yield the same sentence:
        # the adopted map decides the first, nothing decides the second.
        day = date(2025, 7, 1)
        version = next(v for v in self.versions if '2025-00106' in v.provision_version_id)
        reached = [a for a in zone_of((version,), day, comune='GINOSA', foglio='36', particella='5')]
        unmentioned = [a for a in zone_of((version,), day, comune='GINOSA', foglio='999', particella='5')]
        self.assertTrue(reached)
        self.assertTrue(all(a['zone'] is None for a in reached))
        self.assertEqual({a['reached_zone'] for a in reached}, {'cuscinetto', 'infetta'})
        self.assertTrue(all('does not state which part' in a['basis'] for a in reached))
        self.assertEqual([a['basis'] for a in unmentioned],
                         ['no cadastral statement establishes membership for this place'])
        for a in reached:
            self.assertIn('p13 table', a['statement'].locator)
        # A part of a comune whose extent the table leaves unstated is reached too.
        part = statement('part-comune-extent-unstated', comune='CONVERSANO', zone='cuscinetto')
        from dataclasses import replace
        fixture = replace(version, statements=(part,))
        answers = zone_of((fixture,), day, comune='CONVERSANO', foglio='40', particella='1')
        self.assertEqual([a.get('reached_zone') for a in answers], ['cuscinetto'])
        # And neither reaches the accepted consumer as an assertion.
        _, assertions = membership_evidence((version,), ROOT, day, comune='GINOSA', foglio='36', particella='5')
        self.assertEqual(assertions, ())

    def test_a_whole_province_statement_the_question_cannot_name_is_reported(self):
        # DDS 127/2022 places the whole provinces of Lecce and Brindisi in the
        # infected zone and lists Fasano's containment sheets. A question that
        # carries no province cannot be placed in a province here, and the
        # strictest zone the act states must not vanish from the answer, nor
        # a Lecce comune read like Milan.
        day = date(2023, 6, 1)
        version = next(v for v in self.versions if '2022-00127' in v.provision_version_id)
        def bases(**q):
            return zone_of((version,), day, **q)
        fasano = bases(comune='FASANO', foglio='20', particella='3')
        self.assertEqual({a.get('reached_zone') for a in fasano} - {None}, {'contenimento'})
        self.assertEqual({a.get('unaddressed_zone') for a in fasano} - {None}, {'infetta'})
        # Each province the act names is reported, once.
        self.assertEqual(sorted(a['statement'].province for a in fasano if a.get('unaddressed_zone')),
                         ['BRINDISI', 'LECCE'])
        with_province = bases(comune='FASANO', foglio='20', particella='3', province='BRINDISI')
        self.assertIn('infetta', [a['zone'] for a in with_province])
        self.assertFalse(any(a.get('unaddressed_zone') for a in with_province))
        galatina = bases(comune='GALATINA', foglio='10', particella='5')
        self.assertEqual({a.get('unaddressed_zone') for a in galatina}, {'infetta'})
        self.assertTrue(all('no cadastral statement establishes' not in a['basis'] for a in galatina))
        # Without a province the reader cannot tell a Lecce comune from Milan; it
        # says so through the same unaddressed statement rather than declaring
        # either place unmentioned. An act with no whole-province statement
        # still answers an unmentioned place as unmentioned.
        milano = bases(comune='MILANO', foglio='1', particella='1')
        self.assertEqual({a.get('unaddressed_zone') for a in milano}, {'infetta'})
        self.assertFalse(any(a.get('reached_zone') or a['zone'] for a in milano))
        ginosa_act = next(v for v in self.versions if '2025-00106' in v.provision_version_id)
        self.assertEqual([a['basis'] for a in zone_of((ginosa_act,), date(2025, 7, 1), comune='MILANO', foglio='1')],
                         ['no cadastral statement establishes membership for this place'])
        # Neither unaddressed answer reaches the accepted consumer as an assertion.
        _, assertions = membership_evidence((version,), ROOT, day, comune='GALATINA', foglio='10', particella='5')
        self.assertEqual(assertions, ())

    def test_a_comune_listed_by_sheets_asked_without_a_sheet_is_reached(self):
        # A monitoring record carries a comune and rarely a sheet. The act that
        # lists Fasano's sheets is not silent about Fasano.
        day = date(2023, 6, 1)
        version = next(v for v in self.versions if '2022-00127' in v.provision_version_id)
        fasano = zone_of((version,), day, comune='FASANO')
        self.assertEqual({a.get('reached_zone') for a in fasano} - {None}, {'contenimento'})
        self.assertTrue(any('names no sheet' in a['basis'] for a in fasano))
        milano = zone_of((version,), day, comune='MILANO')
        self.assertNotEqual([a['basis'] for a in fasano], [a['basis'] for a in milano])

    def test_a_separately_stated_regime_survives_whatever_the_statement_order(self):
        # DDS 18/2024 page 9 lists Alberobello's whole territory under "ZONA
        # INFETTA" and again under "ZONA INFETTA IN CUI SI APPLICANO MISURE DI
        # CONTENIMENTO": one zone, two facts. Combining answers by zone alone
        # kept whichever the act printed first.
        from dataclasses import replace
        version = next(v for v in self.versions if '2024-00018:area-state-transition:v1' in v.provision_version_id)
        def regimes(v):
            return sorted(((a['zone'], a.get('regime') or '') for a in zone_of((v,), v.effective_from, comune='ALBEROBELLO')
                           if a['zone']))
        expected = [('infetta', ''), ('infetta', 'contenimento')]
        self.assertEqual(regimes(version), expected)
        self.assertEqual(regimes(replace(version, statements=tuple(reversed(version.statements)))), expected)
        # Locorotondo's containment statement lists sheets; asked without a sheet
        # it is reached with its regime, beside the decided plain infected zone.
        answers = zone_of((version,), version.effective_from, comune='LOCOROTONDO')
        self.assertEqual(sorted((a.get('reached_zone'), a.get('regime')) for a in answers if a.get('reached_zone')),
                         [('infetta', 'contenimento')])

    def test_an_incomplete_cadastral_reference_is_named_not_blamed_on_the_map(self):
        # DDS 132/2025 page 8 files Bari sheet 2 under sections A and E, starred;
        # DDS 8/2024 page 7 narrows Triggiano sheet 5 to named parcels, 818
        # wholly contained. Asked without the section or the parcel, the act is
        # neither silent nor undecided: the reference is incomplete, and saying
        # so points the operator at the annex rather than at the deferred map.
        bari_act = next(v for v in self.versions if '2025-00132' in v.provision_version_id)
        mine = [a for a in zone_of((bari_act,), bari_act.effective_from, comune='BARI', foglio='2', particella='1')
                if a.get('reached_zone')]
        self.assertEqual([a['reached_zone'] for a in mine], ['cuscinetto'])
        self.assertIn('section A, E', mine[0]['basis'])
        self.assertIn('names no section', mine[0]['basis'])
        decided = zone_of((bari_act,), bari_act.effective_from, comune='BARI', foglio='2', section='A', particella='1')
        self.assertIn('cuscinetto', [a['zone'] for a in decided])
        triggiano_act = next(v for v in self.versions if '2024-00008' in v.provision_version_id)
        mine = [a for a in zone_of((triggiano_act,), triggiano_act.effective_from, comune='TRIGGIANO', foglio='5')
                if a.get('reached_zone')]
        self.assertEqual([a['reached_zone'] for a in mine], ['infetta'])
        self.assertIn('names no parcel', mine[0]['basis'])
        self.assertNotIn('adopted map', mine[0]['basis'])
        # An unstarred sheet with no parcels and no section keeps the map answer.
        ginosa_act = next(v for v in self.versions if '2025-00106' in v.provision_version_id)
        mine = [a for a in zone_of((ginosa_act,), date(2025, 7, 1), comune='GINOSA', foglio='36', particella='5')
                if a.get('reached_zone')]
        self.assertTrue(mine and all('adopted map decides' in a['basis'] for a in mine))

    def test_a_response_cut_off_by_the_model_is_not_a_page_read(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            readings = root / 'corpus/sources/areas/readings'
            (readings / 'source').mkdir(parents=True)
            (readings / 'INVENTORY.json').write_text(json.dumps([
                {'act_sha256': 'source', 'page': 1, 'pages_in_document': 1, 'candidate': True}]))
            pinned = {'act_sha256': 'source', 'page': 1, 'stop_reason': 'max_tokens',
                      'reading': {'tables': [], 'unattached': [], 'uncertain': [],
                                  'native_tables_accounted': [], 'tables_visible': 0},
                      'resolved': {'tables': []}, 'resolution_problems': []}
            (readings / 'source/p1.json').write_text(json.dumps(pinned))
            statements, unresolved, _, unread = pinned_statements(root, 'source')
            self.assertEqual(unread, (1,))
            self.assertTrue(any('max_tokens' in u for u in unresolved))
            pinned['stop_reason'] = 'tool_use'
            (readings / 'source/p1.json').write_text(json.dumps(pinned))
            self.assertEqual(pinned_statements(root, 'source')[3], ())

    def test_the_causes_are_distinguishable(self):
        vocabulary = {SOURCE_STATES_NONE, MATERIAL_NOT_HELD, READING_DID_NOT_RECOVER,
                      RECOVERED_NOT_ATTACHED}
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
        from dataclasses import replace
        unread = replace(next(v for v in self.versions if v.statements),
                         unresolved=('fixture: one annex region remains unread',))
        s = unread.statements[0]
        answers = zone_of((unread,), unread.effective_from, comune=s.comune,
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

    def test_membership_preserves_each_supporting_physical_statement(self):
        from dataclasses import replace
        version = next(v for v in self.versions if '2024-00158' in v.provision_version_id)
        original = next(s for s in version.statements if s.comune == 'CAROSINO')
        repeated = replace(original, locator='p8 table 1 row 1')
        version = replace(version, statements=(original, repeated))
        _, assertions = membership_evidence((version,), ROOT, version.effective_from, comune='CAROSINO')
        self.assertEqual(len(assertions), 2)
        self.assertEqual(len({a.identity for a in assertions}), 2)
        self.assertEqual(len({a.support[0].selector for a in assertions}), 2)

    def test_the_route_to_the_accepted_consumer_admits_a_decided_parcel_and_nothing_else(self):
        # evidence_for is the only path from a pinned reading to the Stage C
        # evidence object, where contract admission, the event-time version's
        # ownership of the predicate and the source role are enforced. Ginosa
        # sheet 29 is starred in DDS 106/2025's buffer table; sheet 36 is not.
        from cordon_c.core import Snapshot
        from cordon_d.areas import act_documents, evidence_for
        from cordon_d.store import blob_path, store_root
        day = date(2025, 7, 1)
        version = next(v for v in self.versions if '2025-00106' in v.provision_version_id)
        # The assertions themselves need no source bytes and are checked everywhere.
        _, assertions = membership_evidence((version,), ROOT, day, comune='GINOSA', foglio='29', particella='5')
        self.assertEqual(len(assertions), 1)
        self.assertEqual(assertions[0].contract, 'adopted-geography')
        self.assertIn('cuscinetto', assertions[0].identity)
        _, none = membership_evidence((version,), ROOT, day, comune='GINOSA', foglio='36', particella='5')
        self.assertEqual(none, ())
        # The same parcel answers identically whatever the caller calls the province.
        for province in ('TA', 'TARANTO', None):
            _, again = membership_evidence((version,), ROOT, day, province=province,
                                           comune='GINOSA', foglio='29', particella='5')
            self.assertEqual(len(again), 1, province)
        record = act_documents(ROOT)[version.instrument_id]
        if not blob_path(store_root(ROOT), record['sha256']).exists():
            # The evidence object verifies the act's bytes; without the store that
            # last step has no source to verify against and says so.
            self.skipTest('the act document is not in the content-addressed store here')
        evidence, admitted = evidence_for((version,), ROOT, day, snapshot=Snapshot.load(ROOT),
                                          comune='GINOSA', foglio='29', particella='5')
        self.assertEqual(len(admitted), 1)
        self.assertTrue(evidence)

    def test_retained_section_boundaries_survive_to_membership(self):
        cases = [('2024-00093', 'A', '76', 'p9 table 2 row 1'),
                 ('2024-00093', 'G', '3', 'p10 table 2 row 1'),
                 ('2024-00094', 'G', '2', 'p8 table 2 row 1')]
        for instrument, section, sheet, locator in cases:
            with self.subTest(instrument=instrument, section=section, sheet=sheet):
                version = next(v for v in self.versions if instrument in v.provision_version_id)
                _, assertions = membership_evidence((version,), ROOT, version.effective_from,
                                                    comune='BARI', section=section, foglio=sheet)
                self.assertTrue(any(locator in a.support[0].selector for a in assertions))
                _, unnamed = membership_evidence((version,), ROOT, version.effective_from,
                                                 comune='BARI', foglio=sheet)
                self.assertFalse(unnamed)


if __name__ == '__main__':
    unittest.main()

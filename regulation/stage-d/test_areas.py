"""Row 3: the act's own annex statements, read whole, as construction input.

These tests hold the reader to what the act prints. Membership is not answered
here: C tests a place against the geometry `cordon_d.area_geometry` supplies.
"""
import json
import os
import sys
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cordon_d.areas import (annexes, read_scope, versions, _zone_from, pinned_statements,
                            ReadingIncomplete)
from cordon_d.store import put_bytes, store_root

ROOT = Path(__file__).resolve().parents[2]


def held(root=ROOT) -> bool:
    """Whether this checkout's store holds the area act documents."""
    record = next(r for r in json.loads((root / 'corpus/sources/areas/acts.json').read_text())
                  if r.get('sha256'))
    return (store_root(root) / 'blobs/sha256' / record['sha256'][:2] / record['sha256']).exists()


class ScopeGrammar(unittest.TestCase):
    """What the act writes, read whole - or not read at all."""

    def test_inclusive_range_is_every_sheet_it_states(self):
        # DDS 127/2022 states Fasano's containment sheets as ranges. Reading
        # only the endpoints dropped every sheet between them.
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
        # Keeping the part the reader understood would build a zone narrower
        # than the act's.
        for text in ('INTERO TERRITORIO COMUNALE, AD ECCEZIONE DEL FOGLIO 5',
                     'FOGLI: 1, 2 SALVO LE AREE BOSCHIVE',
                     'FOGLI: 1, 2 esclusi i terreni demaniali',
                     'FOGLI 7*-9*', 'FOGLI da 7 a 9*'):
            with self.subTest(text=text):
                self.assertFalse(read_scope(text).fully_read)


class ZoneFromCaption(unittest.TestCase):
    """The zone word the act prints, and the measures it says apply there."""

    def test_head_word_is_the_zone_as_printed(self):
        for caption, zone in (
                ('ZONA INFETTA IN PROVINCIA DI LECCE', 'INFETTA'),
                ('ZONA DI CONTENIMENTO', 'CONTENIMENTO'),
                ('ZONA CUSCINETTO', 'CUSCINETTO'),
                # DDS 82/2026 lists its Mola di Bari and Noci foci apart from its
                # infected zone; no token is invented and no zone is substituted.
                ('FOCOLAI PUNTIFORMI DI MOLA DI BARI E NOCI', 'FOCOLAI')):
            with self.subTest(caption=caption):
                self.assertEqual(_zone_from(caption)[0], zone)

    def test_a_qualifier_does_not_replace_the_zone(self):
        for caption in ('ZONA CUSCINETTO DEI FOCOLAI DI ERADICAZIONE',
                        'ZONA CUSCINETTO DELLA ZONA DI CONTENIMENTO'):
            with self.subTest(caption=caption):
                self.assertEqual(_zone_from(caption)[0], 'CUSCINETTO')

    def test_zone_and_regime_are_two_facts(self):
        zone, _, regime = _zone_from('ZONA INFETTA IN CUI SI APPLICANO MISURE DI CONTENIMENTO')
        self.assertEqual((zone, regime), ('INFETTA', 'CONTENIMENTO'))
        zone, _, regime = _zone_from('ZONA CUSCINETTO IN CUI SI APPLICANO MISURE DI ERADICAZIONE')
        self.assertEqual((zone, regime), ('CUSCINETTO', 'ERADICAZIONE'))


class PinnedPages(unittest.TestCase):
    """Every physical page of the act's own document needs a reading."""

    def setUp(self):
        import pymupdf
        self.directory = TemporaryDirectory()
        self.root = Path(self.directory.name) / 'repo'
        self.previous = os.environ.get('CORDON_STORE')
        os.environ['CORDON_STORE'] = str(Path(self.directory.name) / 'store')
        document = pymupdf.open()
        document.new_page()
        document.new_page()
        self.digest = put_bytes(store_root(self.root), document.tobytes())
        self.readings = self.root / 'corpus/sources/areas/readings' / self.digest
        self.readings.mkdir(parents=True)

    def tearDown(self):
        if self.previous is None:
            os.environ.pop('CORDON_STORE', None)
        else:
            os.environ['CORDON_STORE'] = self.previous
        self.directory.cleanup()

    def pin(self, page, stop_reason='end_turn'):
        (self.readings / f'p{page}.json').write_text(json.dumps({
            'act_sha256': self.digest, 'page': page, 'stop_reason': stop_reason,
            'reading': {'tables': [], 'unattached': [], 'uncertain': [], 'native_tables_accounted': []},
            'resolved': {'tables': []}, 'resolution_problems': []}))

    def test_a_document_not_in_the_store_is_not_an_empty_reading(self):
        with self.assertRaises(FileNotFoundError):
            pinned_statements(self.root, 'f' * 64)

    def test_a_page_the_readings_omit_stops_the_reader(self):
        self.pin(1)
        with self.assertRaisesRegex(ReadingIncomplete, 'p2: no reading'):
            pinned_statements(self.root, self.digest)

    def test_a_response_cut_off_by_the_model_is_not_a_page_read(self):
        self.pin(1)
        self.pin(2, 'max_tokens')
        with self.assertRaisesRegex(ReadingIncomplete, 'max_tokens'):
            pinned_statements(self.root, self.digest)
        self.pin(2, 'tool_use')
        self.assertEqual(pinned_statements(self.root, self.digest), ((), ()))


class AnnexList(unittest.TestCase):
    def test_an_unnumbered_bundled_annex_is_recovered(self):
        text = ('ALLEGATI INTEGRANTI\n\n Documento - Impronta (SHA256)\n'
                ' Allegato.pdf -\n ' + 'a' * 64 + '\n\nIl presente Provvedimento')
        self.assertEqual([(a.name, a.stated_sha256) for a in annexes(text)],
                         [('Allegato.pdf', 'a' * 64)])

    def test_one_entry_never_borrows_its_neighbours_hash(self):
        text = ('ALLEGATI INTEGRANTI\n\n ALLEGATO 1.pdf -\n\n ALLEGATO 2.pdf -\n '
                + 'b' * 64 + '\n\nIl presente Provvedimento')
        got = {a.name: a.stated_sha256 for a in annexes(text)}
        self.assertIsNone(got['ALLEGATO 1.pdf'])
        self.assertEqual(got['ALLEGATO 2.pdf'], 'b' * 64)


class AgainstTheAcceptedPopulation(unittest.TestCase):
    """Every accepted A area version, read through the ordinary path."""

    @classmethod
    def setUpClass(cls):
        cls.versions = versions(ROOT)

    def test_every_accepted_area_version_is_present(self):
        rows = json.loads((ROOT / 'regulation/jurisdiction/canonical/authoring.json').read_text())
        rows = rows if isinstance(rows, list) else list(rows.values())[0]
        expected = {r['provision_version_id'] for r in rows
                    if any(k in r['provision_version_id']
                           for k in ('area-state-transition', 'area-update', 'area-act-before-gis'))}
        self.assertEqual({v.provision_version_id for v in self.versions}, expected)

    def test_no_statement_is_emitted_from_a_partly_read_cell(self):
        for version in self.versions:
            for s in version.statements or ():
                with self.subTest(version=version.provision_version_id):
                    self.assertTrue(read_scope(s.text).fully_read)

    @unittest.skipUnless(held(), 'the area act documents are not in this store')
    def test_the_foci_keep_the_acts_word(self):
        words = {s.zone for v in self.versions for s in v.statements or ()}
        self.assertIn('FOCOLAI', words)
        self.assertTrue(words <= {'INFETTA', 'INFETTO', 'CUSCINETTO', 'CONTENIMENTO', 'FOCOLAI'}, words)

    @unittest.skipUnless(held(), 'the area act documents are not in this store')
    def test_every_retained_act_is_read_whole(self):
        for version in self.versions:
            with self.subTest(version=version.provision_version_id):
                if version.consumed:
                    self.assertIsNotNone(version.statements)


if __name__ == '__main__':
    unittest.main()

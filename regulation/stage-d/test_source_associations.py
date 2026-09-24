"""Association layout checks on source PDFs; not a transcription certification."""
from pathlib import Path
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

import pymupdf

from cordon_d.source_associations import associations, read_associations
from cordon_d.store import blob_path, put_bytes, store_root


HEADERS = ['ID CAMPIONE', 'RAPPORTO PROVA', 'DATA RAPPORTO PROVA', 'PROPRIETARIO']


def source(store, pages):
    with pymupdf.open() as document:
        for spec in pages:
            page = document.new_page(width=600, height=500)
            headings = spec.get('headings', HEADERS)
            rows = ([headings] if spec.get('header', True) else []) + spec['rows']
            widths = spec.get('widths', [80, 120, 150, 130])
            xs = [40]
            for width in widths:
                xs.append(xs[-1] + width)
            if spec.get('annex'):
                page.insert_text((40, 65), spec['annex'], fontsize=10)
            spans = spec.get('row_spans', [])
            for y in range(len(rows) + 1):
                for c in range(len(widths)):
                    if not any(column == c and first < y <= last for column, first, last in spans):
                        page.draw_line((xs[c], 100 + y * 44), (xs[c+1], 100 + y * 44))
            for x in xs:
                page.draw_line((x, 100), (x, 100 + len(rows) * 44))
            for r, row in enumerate(rows):
                for c, text in enumerate(row):
                    end = next((last for column, first, last in spans if column == c and first == r), r)
                    page.insert_textbox((xs[c] + 4, 104 + r*44, xs[c+1] - 4, 140 + end*44),
                                        text, fontsize=8)
            if 'folio' in spec:
                page.insert_text((450, 450), str(spec['folio']), fontsize=10)
            if spec.get('rotate'):
                page.set_rotation(spec['rotate'])
                page.remove_rotation()
        return put_bytes(store, document.tobytes())


class SourceAssociations(unittest.TestCase):
    def test_shared_printed_cells_preserve_groups_and_do_not_fill_separate_blanks(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{
                'headings': HEADERS[:3] + ['FOGLIO', 'PARTICELLA'],
                'widths': [80, 110, 130, 65, 65],
                'rows': [['A', 'R 1', '1/2/2025', '5', '95'],
                         ['B', 'R 1', '1/2/2025', '', ''],
                         ['C', 'R 1', '1/2/2025', '5', '473'],
                         ['D', 'R 1', '1/2/2025', '', ''],
                         ['E', 'R 1', '1/2/2025', '', '']],
                'row_spans': [(3, 1, 2), (4, 1, 2), (3, 3, 4), (4, 3, 4)],
            }])
            rows = read_associations(digest, store).rows
            self.assertEqual([(r['fields']['sheet']['text'], r['fields']['parcel']['text']) for r in rows],
                             [('5', '95'), ('5', '95'), ('5', '473'), ('5', '473'), ('', '')])
            for first, second in [(0, 1), (2, 3)]:
                self.assertEqual(rows[first]['fields']['parcel']['bbox'], rows[second]['fields']['parcel']['bbox'])
                self.assertIn('shared printed cell', rows[second]['fields']['parcel']['derivation'])
            self.assertNotIn('derivation', rows[4]['fields']['parcel'])

    def test_retained_shared_cadastral_cells_reach_every_printed_plant(self):
        store = store_root(Path(__file__).resolve())
        digest = '266f46b253898678e209cf66b2afaa8e44d5b10e8b8498c698df77c999306df8'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained DDS179 source store unavailable')
        # DDS179 physical page 14: six vines share parcel 95, three parcel 473.
        # Those are two printed cells, not values inferred from neighbouring rows.
        rows = read_associations(digest, store).rows
        expected = dict.fromkeys(['1753094', '1753262', '1753459', '1753292', '1753432', '1753481'], '95')
        expected.update(dict.fromkeys(['1753069', '1752990', '1753058'], '473'))
        self.assertEqual({r['fields']['plant_id']['text']: r['fields']['parcel']['text'] for r in rows}, expected)
        self.assertTrue(all(r['fields']['sheet']['text'] == '5' and not r['issues'] for r in rows))
        with pymupdf.open(blob_path(store, digest)) as original:
            for row in rows:
                field = row['fields']['parcel']
                self.assertEqual(original[13].get_text(clip=pymupdf.Rect(field['bbox'])).strip(),
                                 field['text'])

    def test_printed_reordered_headers_and_private_column_exclusion(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{'headings': [HEADERS[1], HEADERS[3], HEADERS[0], HEADERS[2]],
                                     'rows': [['LAB A / 25', 'PRIVATE PERSON', '00091', '03/02/2025']]}])
            reading = read_associations(digest, store)
            self.assertEqual(len(reading.rows), 1)
            row = reading.rows[0]
            self.assertEqual(row['fields']['plant_id']['text'], '00091')
            self.assertEqual(row['fields']['report_reference']['text'], 'LAB A / 25')
            self.assertNotIn('PRIVATE PERSON', json.dumps(reading.__dict__))
            self.assertEqual(row['basis']['headers']['plant_id']['column'], 3)

    def test_continuation_requires_annex_folio_and_grid(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [
                {'annex': 'ALLEGATO 7/C', 'folio': 12, 'rows': [['A', 'R 1', '1/2/2025', 'NAME']]},
                {'header': False, 'folio': 13, 'rows': [['B', 'R 2', '2/2/2025', 'NAME']]},
                {'header': False, 'folio': 15, 'rows': [['C', 'R 3', '3/2/2025', 'NAME']]},
            ])
            reading = read_associations(digest, store)
            self.assertEqual([r['fields']['plant_id']['text'] for r in reading.rows], ['A', 'B'])
            self.assertEqual(reading.rows[1]['basis']['kind'], 'annex_continuation')
            self.assertTrue(any(i.get('page') == 3 for i in reading.issues))

    def test_identical_grid_alone_cannot_supply_a_header(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [
                {'folio': 1, 'rows': [['A', 'R 1', '1/2/2025', 'NAME']]},
                {'header': False, 'folio': 2, 'rows': [['B', 'R 2', '2/2/2025', 'NAME']]},
            ])
            self.assertEqual(len(read_associations(digest, store).rows), 1)

    def test_uninterpreted_qualifier_column_is_not_silently_lost(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{'headings': HEADERS[:3] + ['QUALIFICAZIONE'],
                                     'rows': [['A', 'R 1', '1/2/2025', 'SUSPENDED']]}])
            row = read_associations(digest, store).rows[0]
            self.assertEqual(row['issues'][0]['headings'], ['QUALIFICAZIONE'])

    def test_new_annex_and_changed_columns_prevent_header_inheritance(self):
        for change in [{'annex': 'ALLEGATO 7/D'}, {'widths': [85, 115, 150, 130]}]:
            with self.subTest(change=change), TemporaryDirectory() as directory:
                store = Path(directory)
                digest = source(store, [
                    {'annex': 'ALLEGATO 7/C', 'folio': 1, 'rows': [['A', 'R 1', '1/2/2025', 'NAME']]},
                    {'header': False, 'folio': 2, 'rows': [['B', 'R 2', '2/2/2025', 'NAME']], **change},
                ])
                self.assertEqual(len(read_associations(digest, store).rows), 1)

    def test_rotated_native_source_positions_round_trip(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{'rotate': 270, 'rows': [['0091', 'R 1', '1/2/2025', 'NAME']]}])
            reading = read_associations(digest, store)
            row = reading.rows[0]
            box = row['fields']['plant_id']['bbox']
            with pymupdf.open(store / 'blobs' / 'sha256' / digest[:2] / digest) as original:
                self.assertEqual(original[0].get_text(clip=pymupdf.Rect(box)).strip(), '0091')

    def test_fragment_is_retained_and_qualifies_preceding_row(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [
                {'annex': 'ALLEGATO 7/C', 'folio': 1, 'rows': [['A', 'R 1', '1/2/2025', 'NAME']]},
                {'header': False, 'folio': 2, 'rows': [['', '', 'fragment', 'PRIVATE'], ['B', 'R 2', '2/2/2025', 'NAME']]},
            ])
            reading = read_associations(digest, store)
            self.assertEqual(len(reading.rows), 3)
            self.assertTrue(reading.rows[0]['issues'])
            self.assertTrue(reading.rows[1]['issues'])
            self.assertFalse(reading.rows[2]['issues'])
            self.assertEqual(reading.rows[1]['fields']['plant_id']['text'], '')

    def test_cache_reuse_has_no_pdf_reparse(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{'rows': [['A', 'R 1', '1/2/2025', 'NAME']]}])
            first = read_associations(digest, store)
            with patch('cordon_d.source_associations._read_pdf', side_effect=AssertionError('unexpected parse')):
                self.assertEqual(read_associations(digest, store), first)

    def test_split_cell_rejoins_only_across_verified_annex_continuity(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [
                {'annex': 'ALLEGATO 7/C', 'folio': 1, 'headings': HEADERS[:3] + ['SPECIE'],
                 'rows': [['A', 'R 1', '1/2/2025', 'Mandorlo (Prunus']]},
                {'header': False, 'folio': 2,
                 'rows': [['', '', '', 'dulcis)'], ['B', 'R 2', '2/2/2025', 'Olivo']]},
            ])
            reading = read_associations(digest, store)
            self.assertEqual(len(reading.rows), 2)
            first = reading.rows[0]
            self.assertEqual(' '.join(first['fields']['host']['text'].split()), 'Mandorlo (Prunus dulcis)')
            self.assertEqual([p['page'] for p in first['fields']['host']['parts']], [1, 2])
            self.assertFalse(first['issues'])
            self.assertEqual(first['continuations'][0]['basis']['kind'], 'annex_continuation')

    def test_report_field_can_continue_with_species_without_a_new_row_identity(self):
        for tail in ['', 'var. rubra)']:
            with self.subTest(tail=tail), TemporaryDirectory() as directory:
                store = Path(directory)
                digest = source(store, [
                    {'annex': 'ALLEGATO 9/B', 'folio': 7, 'headings': HEADERS[:3] + ['SPECIE'],
                     'rows': [['001X', 'Q-17 / 2032', '09/04/2032', 'Acer (cultivar']]},
                    {'header': False, 'folio': 8,
                     'rows': [['', 'Field Laboratory West', '', tail],
                              ['002Y', 'Q-18 / 2032', '10/04/2032', 'Populus']]},
                ])
                reading = read_associations(digest, store)
                self.assertEqual(len(reading.rows), 2)
                first, second = reading.rows
                self.assertEqual(first['fields']['plant_id']['text'], '001X')
                report = first['fields']['report_reference']
                self.assertEqual(report['text'].split(), ['Q-17', '/', '2032', 'Field', 'Laboratory', 'West'])
                self.assertEqual([part['page'] for part in report['parts']], [1, 2])
                self.assertEqual(first['fields']['host']['text'].split(),
                                 ('Acer (cultivar ' + tail).split())
                self.assertFalse(first['issues'])
                self.assertEqual(second['fields']['plant_id']['text'], '002Y')
                self.assertEqual(second['fields']['report_reference']['text'], 'Q-18 / 2032')
                self.assertNotIn('parts', second['fields']['report_reference'])
                with pymupdf.open(blob_path(store, digest)) as original:
                    for part in report['parts']:
                        self.assertEqual(original[part['page'] - 1].get_text(
                            clip=pymupdf.Rect(part['bbox'])).split(), part['text'].split())

    def test_identity_or_date_on_first_row_prevents_report_fragment_merging(self):
        for row in [['002Y', 'Another report', '', 'Populus'],
                    ['', 'Another report', '10/04/2032', 'Populus'],
                    ['002Y', 'Another report', '10/04/2032', 'Populus']]:
            with self.subTest(row=row), TemporaryDirectory() as directory:
                store = Path(directory)
                digest = source(store, [
                    {'annex': 'ALLEGATO 9/B', 'folio': 7, 'headings': HEADERS[:3] + ['SPECIE'],
                     'rows': [['001X', 'Q-17 / 2032', '09/04/2032', 'Acer']]},
                    {'header': False, 'folio': 8, 'rows': [row]},
                ])
                first, second = read_associations(digest, store).rows
                self.assertEqual(first['fields']['report_reference']['text'], 'Q-17 / 2032')
                self.assertNotIn('parts', first['fields']['report_reference'])
                self.assertEqual(second['fields']['report_reference']['text'], 'Another report')
                self.assertEqual(second['fields']['plant_id']['text'], row[0])
                self.assertEqual(second['fields']['report_date']['text'], row[2])

    def test_report_fragment_does_not_bridge_changed_annex_folio_or_grid(self):
        for change in [{'annex': 'ALLEGATO 9/C'}, {'folio': 9},
                       {'widths': [85, 115, 150, 130]}]:
            with self.subTest(change=change), TemporaryDirectory() as directory:
                store = Path(directory)
                digest = source(store, [
                    {'annex': 'ALLEGATO 9/B', 'folio': 7, 'headings': HEADERS[:3] + ['SPECIE'],
                     'rows': [['001X', 'Q-17 / 2032', '09/04/2032', 'Acer']]},
                    {'header': False, 'folio': 8,
                     'rows': [['', 'Field Laboratory West', '', 'var. rubra']], **change},
                ])
                reading = read_associations(digest, store)
                self.assertEqual(len(reading.rows), 1)
                self.assertNotIn('parts', reading.rows[0]['fields']['report_reference'])
                self.assertTrue(any(issue.get('page') == 2 for issue in reading.issues))

    def test_knowledge_cutoff_uses_capture_time_not_report_date(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'records.json').write_text(json.dumps([
                {'sha256': 'old', 'captured_at': '2025-01-01T00:00:00+00:00'},
                {'sha256': 'future', 'captured_at': '2025-02-01T00:00:00+00:00'},
                {'sha256': 'old', 'captured_at': '2025-03-01T00:00:00+00:00'},
            ]))
            with patch('cordon_d.source_associations.read_associations', side_effect=lambda h, _: h):
                cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
                self.assertEqual(list(associations(root, root, known_through=cutoff)), ['old'])
                with self.assertRaisesRegex(ValueError, 'timezone-aware'):
                    list(associations(root, root, known_through=datetime(2025, 1, 1)))


if __name__ == '__main__':
    unittest.main()

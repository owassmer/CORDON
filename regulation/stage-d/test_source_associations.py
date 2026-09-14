"""Association layout checks on source PDFs; not a transcription certification."""
from pathlib import Path
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

import pymupdf

from cordon_d.source_associations import associations, read_associations
from cordon_d.store import put_bytes


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
            for y in range(len(rows) + 1):
                page.draw_line((xs[0], 100 + y * 44), (xs[-1], 100 + y * 44))
            for x in xs:
                page.draw_line((x, 100), (x, 100 + len(rows) * 44))
            for r, row in enumerate(rows):
                for c, text in enumerate(row):
                    page.insert_textbox((xs[c] + 4, 104 + r*44, xs[c+1] - 4, 140 + r*44),
                                        text, fontsize=8)
            if 'folio' in spec:
                page.insert_text((450, 450), str(spec['folio']), fontsize=10)
            if spec.get('rotate'):
                page.set_rotation(spec['rotate'])
                page.remove_rotation()
        return put_bytes(store, document.tobytes())


class SourceAssociations(unittest.TestCase):
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

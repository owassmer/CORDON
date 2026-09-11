"""Identity constraints of the join, exercised end to end on documents it has never seen.

Every case here is built as a document and a publication stream and run through
`findings()` itself, because the defects these cover were all invisible to tests
of the reader's parts: a contradictory sampling day, a file name carrying two
documents, and a species-only column. Hand-authored rows would not have shown them.
"""
from datetime import date
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cordon_d.findings import findings
from cordon_d.store import put_bytes, store_root


def document(identity, rows, *, column='Esito laboratorio'):
    """A rapporto di prova with a flat annex: one cell per line, as the publisher's own."""
    import pymupdf
    lines = [f'Rapporto di prova N. {identity}', 'Bari', '01/07/2024',
             'Oggetto: trasmissione esito saggi diagnostici molecolari per Xylella fastidiosa',
             'eseguiti con protocollo Harper et al. (2010).',
             'Id', 'Data rilevamento', 'Specie', column]
    for reference, day, result in rows:
        lines += [reference, day, 'Olivo (Olea europaea)', result]
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        for n, line in enumerate(lines):
            page.insert_text((40, 40 + n * 11), line, fontsize=9)
        return pdf.tobytes()


class JoinIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pyarrow
        import pyarrow.parquet as parquet
        cls.configured = os.environ.pop('CORDON_STORE', None)
        cls.directory = TemporaryDirectory()
        base = Path(cls.directory.name)
        cls.root = base / 'reports'
        cls.root.mkdir()
        store = store_root(cls.root)
        cls.store = store

        # Two documents the publisher serves under one file name, naming the same sample
        # on the same day with opposite results; and one ordinary report.
        same_name_a = document('10/2024', [('700001', '01/06/2024', 'Positivo')])
        same_name_b = document('11/2024', [('700001', '01/06/2024', 'Negativo')])
        ordinary = document('12/2024', [('700002', '01/06/2024', 'Positivo'),      # day agrees
                                        ('700003', '09/09/2023', 'Positivo'),      # day contradicts
                                        ('700004', '01/06/2024', 'Positivo')])     # published twice
        routes = [
            ('http://a.example/doc/COLLIDE.pdf', same_name_a),
            ('http://b.example/doc/COLLIDE.pdf', same_name_b),
            ('http://a.example/doc/ORDINARY.pdf', ordinary),
        ]
        records = [{'url': url, 'captured_at': '2026-01-01T00:00:00+00:00', 'status': 200,
                    'sha256': put_bytes(store, body)} for url, body in routes]
        # The route an observation names failed; the same file name was served elsewhere.
        records.append({'url': 'https://a.example/doc/COLLIDE.pdf', 'error': 'HTTP 500'})
        (cls.root / 'records.json').write_text(json.dumps(records))

        publications = [
            # reference, day, view, result, routes
            ('700001', date(2024, 6, 1), 'Positivi - Campioni 2024', 'published-positive',
             ['https://a.example/doc/COLLIDE.pdf']),
            ('700002', date(2024, 6, 1), 'Positivi - Campioni 2024', 'published-positive',
             ['http://a.example/doc/ORDINARY.pdf']),
            ('700003', date(2024, 6, 1), 'Positivi - Campioni 2024', 'published-positive',
             ['http://a.example/doc/ORDINARY.pdf']),
            ('700004', date(2024, 6, 1), 'Positivi - Campioni 2024', 'published-positive',
             ['http://a.example/doc/ORDINARY.pdf']),
            ('700004', date(2024, 6, 1), 'Piante infette-Monitoraggio 2024', 'published-positive',
             ['http://a.example/doc/ORDINARY.pdf']),
        ]
        readings = store / 'derived/monitoring/readings'
        readings.mkdir(parents=True)
        table = pyarrow.table({
            'reference': [p[0] for p in publications],
            'day': pyarrow.array([p[1] for p in publications], pyarrow.date32()),
            'view': [p[2] for p in publications],
            'result': [p[3] for p in publications],
            'report_routes': [p[4] for p in publications]})
        parquet.write_table(table, readings / 'test.parquet')
        cls.found = {(f['observation'], f['view']): f for f in findings(cls.root, store)}

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()
        if cls.configured is not None:
            os.environ['CORDON_STORE'] = cls.configured

    def test_a_row_the_report_dates_to_another_day_is_a_different_sampling_event(self):
        contradicted = self.found[('700003', 'Positivi - Campioni 2024')]
        self.assertEqual(contradicted['status'], 'the reference is printed, dated to another day')
        self.assertIsNone(contradicted['results'])
        self.assertIs(contradicted['day_constrained'], False)
        # ...while the same document's agreeing row does match, and says the day held it.
        agreed = self.found[('700002', 'Positivi - Campioni 2024')]
        self.assertEqual(agreed['status'], 'matched')
        self.assertIs(agreed['day_constrained'], True)
        self.assertEqual(agreed['comparison'], 'agree at species')

    def test_a_file_name_carrying_two_documents_substitutes_neither(self):
        collided = self.found[('700001', 'Positivi - Campioni 2024')]
        self.assertEqual(collided['document_resolution'],
                         'several documents carry this file name; none substituted')
        self.assertEqual(collided['status'], 'no bytes acquired for this document')
        self.assertIsNone(collided['results'])
        # The two documents disagree, so whichever had been chosen would have decided the
        # verdict by acquisition order rather than by evidence.

    def test_one_observation_published_twice_matches_in_both_views(self):
        for view in ('Positivi - Campioni 2024', 'Piante infette-Monitoraggio 2024'):
            publication = self.found[('700004', view)]
            self.assertEqual(publication['status'], 'matched', view)
            self.assertEqual(publication['comparison'], 'agree at species', view)

    def test_every_absence_names_the_reading_that_produced_it(self):
        # No status in this population asserts a property of the document itself.
        for finding in self.found.values():
            self.assertNotIn('report has no', finding['status'])
            self.assertNotIn('not named by its report', finding['status'])


if __name__ == '__main__':
    unittest.main()

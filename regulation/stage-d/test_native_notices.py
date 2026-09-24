import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from cordon_d.notices import publication_declarations, publication_detail, declaration_detail_matches, read_publications, domino_publication_detail

HEADER = ['Tipo','numero atto','Data atto','Oggetto','Inizio pubblicazione','Fine pubblicazione']

class NativeNoticeTests(unittest.TestCase):
    def test_unregistered_source_records_and_missing_dates(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'annual.csv'
            with p.open('w', newline='') as f:
                w=csv.writer(f);w.writerow(HEADER)
                w.writerow(['AVVISO','','31/12/2025','One &amp; two\ncontinued','02/01/2026','17/01/2026'])
                w.writerow(['AVVISO','','invalid','other','','17/01/2026'])
            rows=list(publication_declarations(p,publisher='new-municipality'))
            output=list(read_publications([p],[],publisher='new-municipality'))
            self.assertEqual(len(output),2)
            self.assertTrue(all(row.values['detail_candidates']==[] for row in output))
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[0].values['declared_dates']['Data atto'],'2025-12-31')
            self.assertEqual(rows[0].values['source_fields']['Oggetto'],'One &amp; two\ncontinued')
            self.assertEqual(rows[1].values['date_issues'],{'Data atto':'Unrecognized source date; original value retained'})
            self.assertIsNone(rows[1].values['declared_dates']['Inizio pubblicazione'])
            self.assertEqual(declaration_detail_matches(rows[1],()),())

    def test_detail_routes_and_publisher_scoped_candidates(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'detail.html'
            p.write_text('''<div class="card-title"><h3>One &amp; two</h3></div>
<div><label>Pubblicazione nr.</label><div>2026/009991</div></div>
<div><label>Atto</label><div>Determina - n. 89 del 03/02/2026</div></div>
<div><label>Data affissione</label><div>04/02/2026</div></div>
<div><label>Data scadenza</label><div>19/02/2026 - (15) giorni</div></div>
<div><label>Numero protocollo</label><div>12345</div></div>
<a href="/openweb/portal/getDoc.php?f=original.pdf">Original</a>
<a href="/openweb/portal/getDoc.php?f=original.pdf&amp;info">Info</a>''')
            a=publication_detail(p,publisher='A',source_url='https://example.org/detail')
            b=publication_detail(p,publisher='B',source_url='https://other.org/detail')
            self.assertEqual(a.values['act_number'],'89')
            self.assertEqual(a.values['source_fields']['Numero protocollo'],'12345')
            self.assertEqual(a.values['declared_dates']['Fine pubblicazione'],'2026-02-19')
            self.assertEqual(a.values['document_routes'][0]['url'],'https://example.org/openweb/portal/getDoc.php?f=original.pdf')
            self.assertTrue(a.values['document_routes'][1]['information_link'])
            csvpath=Path(tmp)/'annual.csv'
            with csvpath.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(HEADER);w.writerow(['Determina','89','03/02/2026','One &amp; two','04/02/2026','19/02/2026'])
            row=next(publication_declarations(csvpath,publisher='A'))
            self.assertEqual(declaration_detail_matches(row,[a,b,a]),(a,a))
            self.assertNotIn('publication_end',a.values)
            p.write_text('<html>Login required</html>')
            with self.assertRaises(ValueError):publication_detail(p,publisher='A',source_url='https://example.org/detail')

class DominoNoticeTests(unittest.TestCase):
    def read(self, periods=('dal 11/27/2024 al 12/04/2024', 'NO')):
        fields = [('Protocollo Generale', 'incoming-8712'),
                  ('Tipo Provvedimento', 'Avviso'),
                  ('Ente/Amministrazione', 'unseen requesting office'),
                  ('Oggetto', 'DDS 999/2024 and predecessor 998/2024'),
                  ('N. Repertorio Albo', '2024/Albo/8701'),
                  *[('In Pubblicazione', value) for value in periods],
                  ('Unseen publisher field', 'literal evidence')]
        with TemporaryDirectory() as tmp:
            path = Path(tmp)/'detail.html'
            path.write_text('<table><tr><td><table>' + ''.join(
                f'<tr><td>{key}</td><td><img src="blank.gif"></td><td>{value}</td></tr>'
                for key, value in fields) + '''</table></td></tr></table>
<a href="/db.nsf/0/native/$FILE/unseen.pdf">Unseen original label</a>
<a href="/db.nsf/0/native/$FILE/cert.pdf">Certificato di Pubblicazione</a>''')
            return domino_publication_detail(path, publisher='unseen municipality',
                                              source_url='https://example.org/detail')

    def test_fixed_source_date_format_and_repeated_label_survive(self):
        row = self.read()
        self.assertEqual(row.values['source_fields']['In Pubblicazione'],
                         ('dal 11/27/2024 al 12/04/2024', 'NO'))
        self.assertEqual(row.values['declared_dates'],
                         {'Data inizio pubb.': '2024-11-27', 'Data fine pubb.': '2024-12-04'})
        self.assertEqual(row.values['source_fields']['Unseen publisher field'], 'literal evidence')
        self.assertEqual(row.values['source_fields']['Protocollo Generale'], 'incoming-8712')
        self.assertEqual(row.values['document_routes'][1]['url'],
                         'https://example.org/db.nsf/0/native/$FILE/cert.pdf')
        self.assertEqual(row.values['document_routes'][0]['label'], 'Unseen original label')
        self.assertNotIn('document', row.values)
        self.assertNotIn('act_number', row.values)
        self.assertNotIn('continuity', row.values)

    def test_date_failure_duplicate_period_and_status_keep_their_causes(self):
        row = self.read(('dal 27/11/2024 al 12/04/2024', 'NO'))
        self.assertIsNone(row.values['declared_dates']['Data inizio pubb.'])
        self.assertIn('month/day/year', row.values['date_issues']['Data inizio pubb.'])
        self.assertEqual(row.values['declared_dates']['Data fine pubb.'], '2024-12-04')
        periods = ('dal 11/27/2024 al 12/04/2024', 'NO', 'dal 11/27/2024 al 12/04/2024')
        row = self.read(periods)
        self.assertEqual(row.values['source_fields']['In Pubblicazione'], periods)
        self.assertTrue(all(value is None for value in row.values['declared_dates'].values()))
        self.assertIn('one native', row.values['date_issues']['In Pubblicazione'])
        row = self.read(('dal 12/04/2024 al 11/27/2024', 'NO'))
        self.assertTrue(all(value is None for value in row.values['declared_dates'].values()))
        self.assertIn('precedes', row.values['date_issues']['In Pubblicazione'])
        row = self.read(('dal 11/27/2024 al 12/04/2024', 'not recovered'))
        self.assertEqual(row.values['publication_status'], 'not recovered')
        self.assertIsNotNone(row.values['status_issue'])

    def test_retained_domino_detail_dates_and_attachment_labels(self):
        from cordon_d.store import blob_path, store_root
        store = store_root(Path(__file__).resolve())
        cases = [
            ('122fb25690d809195441fc2033934e5b474b343498e4f992dd57e1102d85f932',
             '2024/Albo/3076', '2024-11-27', '2024-12-04'),
            ('32aa6b3e737b0d4acf5458df161acf3e6b5634062df3290e2c0149da22823077',
             '2026/Albo/1571', '2026-07-15', '2026-07-22')]
        if not all(blob_path(store, digest).exists() for digest, *_ in cases):
            self.skipTest('Retained Domino source store unavailable')
        for digest, number, start, end in cases:
            row = domino_publication_detail(blob_path(store, digest), publisher='Comune di Bari',
                                             source_url='https://albo.comune.bari.it/')
            self.assertEqual(row.sha256, digest)
            self.assertEqual(row.values['source_fields']['N. Repertorio Albo'], number)
            self.assertEqual(row.values['declared_dates'],
                             {'Data inizio pubb.': start, 'Data fine pubb.': end})
            self.assertEqual(len(row.values['source_fields']['In Pubblicazione']), 2)
            self.assertEqual(len(row.values['document_routes']), 2)
            self.assertTrue(row.values['document_routes'][1]['label'].startswith('Certificato di Pubblicazione'))
            self.assertNotIn('document', row.values)


if __name__=='__main__':unittest.main()

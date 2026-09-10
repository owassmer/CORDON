import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from cordon_d.notices import publication_declarations, publication_detail, declaration_detail_matches, read_publications

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

if __name__=='__main__':unittest.main()

"""Falsify unsafe publication/case promotion and lost administrative evidence."""
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import gzip
import subprocess
import unittest
from cordon_d.campaign import publication_reading, retained_document, CampaignDocuments
from cordon_d.evidence import file_digest, Source
from cordon_d.releases import Occurrence

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).parent

class CampaignTests(unittest.TestCase):

    def test_report_placeholder_is_not_a_document_or_negative_fact(self):
        row=Occurrence('unused','hash','feature:0',{'attributes':{
            'RISULTATO':'POSITIVO ESTIRPATO','DOCUMENTO_DECRETO':'****',
            'DATA_ESTIRPAZIONE':None}})
        reading=publication_reading(row)
        self.assertEqual(reading.result,'published-positive-and-removal-label')
        self.assertEqual(reading.document_references,())
        self.assertEqual(reading.date_fields,(('DATA_ESTIRPAZIONE',None),))
        self.assertEqual(reading.occurrence.values,row.values)

    def test_unknown_result_and_annotation_survive(self):
        row=Occurrence('unused','hash','row:2',{'RISULTATO':'future label','ID':'1*'})
        self.assertEqual(publication_reading(row).result,'unadjudicated-label')
        annotation=replace(row,values={'ID':"*Pianta non abbattuta in seguito all'aggiornamento",'RISULTATO':None})
        self.assertEqual(publication_reading(annotation).result,'publisher-annotation')
        self.assertEqual(publication_reading(replace(row,values={'RISULTATO':'DUBBIO'})).result,'published-doubtful')

    def test_absent_result_concept_differs_from_empty_result_and_html_is_a_route(self):
        row=Occurrence('unused','hash','row:1',{'attributes':{'AREA_ETTARI':2}})
        self.assertEqual(publication_reading(row).result,'not-a-result-record')
        self.assertEqual(publication_reading(replace(row,values={'RISULTATO':None})).result,'unpublished')
        linked=replace(row,values={'DOCUMENTO_CONFERMA':'<a href="https://example.org/report?a=1&amp;b=2">Report</a>'})
        self.assertEqual(publication_reading(linked).document_references,(('DOCUMENTO_CONFERMA','https://example.org/report?a=1&b=2'),))

    def test_document_correction_and_url_alias_are_not_silent(self):
        with TemporaryDirectory() as directory:
            root=Path(directory); path=root/'report.pdf'; path.write_bytes(b'%PDF-test')
            records={'exact-url':{'retained':{'path':'report.pdf','sha256':file_digest(path)},'pdf_signature':True}}
            self.assertIsNotNone(retained_document('exact-url',records,root))
            self.assertIsNone(retained_document('alias-url',records,root))
            path.write_bytes(b'%PDF-changed')
            with self.assertRaises(ValueError):retained_document('exact-url',records,root)



    def test_unregistered_releases_compose_without_case_files_and_keep_versions(self):
        from uuid import uuid4
        with TemporaryDirectory() as directory:
            root = Path(directory)
            owner = root/'regulation/stage-d/correspondences'
            owner.mkdir(parents=True)
            (owner/'campaign-report-readings.json').write_text(
                json.dumps({'readings': [], 'report_copies': []}))
            reference = 'https://publisher.example/' + uuid4().hex
            records = []
            for name, body in [('first.pdf', b'%PDF-first'), ('second.pdf', b'%PDF-replacement')]:
                path = root/name
                path.write_bytes(body)
                records.append({'url': reference, 'pdf_signature': True,
                                'retained': {'path': name, 'sha256': file_digest(path)}})
            records.append({'url': reference, 'pdf_signature': False, 'status': 404})
            index = CampaignDocuments(records, root,
                                      known_through=datetime(2026,9,11,tzinfo=timezone.utc))
            for identifier in (uuid4().hex, uuid4().hex):
                path = root/(identifier + '.csv')
                # Independent source bytes exercise unknown identifiers and duplicated rows.
                path.write_text('ID;RISULTATO;DOCUMENTO_CONFERMA;DATA_CAMPIONE\n'
                                + identifier + ';Negativo;' + reference + ';2025-01-02\n'
                                + identifier + ';Dubbio;' + reference + ';2025-01-02\n')
                rows = list(index.read(path, format='csv', encoding='utf-8', delimiter=';'))
                self.assertEqual([r.publication.result for r in rows],
                                 ['published-negative', 'published-doubtful'])
                self.assertNotEqual(rows[0].publication.occurrence.identity,
                                    rows[1].publication.occurrence.identity)
                self.assertEqual([d.source.path if d.source else None for d in rows[0].documents],
                                 ['first.pdf', 'second.pdf', None])
                self.assertEqual(rows[0].documents[-1].acquisition_record['status'], 404)
                self.assertTrue(all(not hasattr(d, "administrative_readings") for d in rows[0].documents))
            (root/'first.pdf').write_bytes(b'%PDF-changed')
            with self.assertRaises(ValueError):
                list(index.read(path, format='csv', encoding='utf-8', delimiter=';'))

    def test_native_formats_missing_routes_and_unknown_records(self):
        from openpyxl import Workbook
        with TemporaryDirectory() as directory:
            root = Path(directory)
            owner = root/'regulation/stage-d/correspondences'
            owner.mkdir(parents=True)
            (owner/'campaign-report-readings.json').write_text(
                json.dumps({'readings': [], 'report_copies': []}))
            index = CampaignDocuments([], root,
                                      known_through=datetime(2026,9,11,tzinfo=timezone.utc))
            book = Workbook(); sheet = book.active
            sheet.append(['ID', 'RISULTATO', 'DOCUMENTO_CONFERMA'])
            sheet.append(['not-registered', 'future label', 'https://example.org/missing'])
            path = root/'new.xlsx'; book.save(path); book.close()
            row, = index.read(path, format='workbook')
            self.assertEqual(row.publication.result, 'unadjudicated-label')
            self.assertEqual(row.documents[0].reference, 'https://example.org/missing')
            self.assertIsNone(row.documents[0].source)
            self.assertIsNone(row.documents[0].acquisition_record)
            native = root/'new.json'
            native.write_text(json.dumps({'features': [
                {'attributes': {'OBJECTID': 87, 'AREA_ETTARI': 2}},
                {'attributes': {'OBJECTID': 88, 'RISULTATO': None}}]}))
            rows = list(index.read(native, format='arcgis', oid_field='OBJECTID'))
            self.assertEqual([r.publication.result for r in rows],
                             ['not-a-result-record', 'unpublished'])
            with self.assertRaises(ValueError):
                list(index.read(native, format='guessed-format'))

if __name__=='__main__':unittest.main()

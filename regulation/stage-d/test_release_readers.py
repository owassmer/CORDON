"""Generic source readers preserve source values and reject structural ambiguity."""
from datetime import date, datetime
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
import shapefile

from cordon_d.readers import sampling_date
from cordon_d.releases import csv_occurrences, arcgis_occurrences, shapefile_attribute_occurrences


class ReleaseReaders(unittest.TestCase):
    def test_dbf_facts_survive_unreadable_geometry(self):
        with TemporaryDirectory() as directory:
            dbf = BytesIO()
            with shapefile.Writer(dbf=dbf) as writer:
                writer.field('NAME', 'C', size=20)
                for value in ('before', 'empty shape', 'after'):
                    writer.record(value)
            path = Path(directory)/'release.zip'
            with ZipFile(path, 'w') as archive:
                archive.writestr('source.dbf', dbf.getvalue())
                archive.writestr('source.shp', b'unreadable geometry')
            rows = list(shapefile_attribute_occurrences(path, member='source.dbf', encoding='ascii'))
            self.assertEqual([r.values['attributes']['NAME'] for r in rows], ['before', 'empty shape', 'after'])
            self.assertEqual([r.locator for r in rows], [f'source.dbf:record:{i}' for i in range(3)])
            self.assertTrue(all('points' not in r.values for r in rows))
            with self.assertRaises(ValueError):
                list(shapefile_attribute_occurrences(path, member='source.shp', encoding='ascii'))

    def test_csv_retains_marked_identifier_and_embedded_newline(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'release.csv'
            path.write_text('ID;NOTE\n001*;"first\nsecond"\n002;\n')
            rows = list(csv_occurrences(path, encoding='utf-8', delimiter=';'))
            self.assertEqual(rows[0].values, {'ID': '001*', 'NOTE': 'first\nsecond'})
            self.assertEqual(rows[1].locator, 'csv-record:3')
            self.assertNotEqual(rows[0].identity, rows[1].identity)
            original_identity = rows[0].identity
            path.write_text('ID;NOTE\n001*;corrected\n')
            replacement = next(csv_occurrences(path, encoding='utf-8', delimiter=';'))
            self.assertNotEqual(original_identity, replacement.identity)

    def test_csv_rejects_ambiguous_headers_and_truncated_records(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'release.csv'
            for content in ['ID; ID \n1;2\n', 'ID;NOTE\n1\n']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    list(csv_occurrences(path, encoding='utf-8', delimiter=';'))

    def test_view_oid_does_not_replace_published_result(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'positivi.json'
            feature = {'attributes': {'OBJECTID': 3, 'ID_CAMPIONE': '001', 'RISULTATO': 'IN ATTESA'},
                       'geometry': {'x': 1, 'y': 2}}
            path.write_text(json.dumps({'features': [feature], 'spatialReference': {'wkid': 32633}}))
            row = next(arcgis_occurrences(path, oid_field='OBJECTID'))
            self.assertEqual(row.values['attributes']['RISULTATO'], 'IN ATTESA')
            self.assertEqual(row.values['attributes']['ID_CAMPIONE'], '001')
            path.write_text(json.dumps({'features': [feature, feature]}))
            with self.assertRaises(ValueError):
                list(arcgis_occurrences(path, oid_field='OBJECTID'))

    def test_earlier_campaign_header_supplies_date_without_inventing_instant(self):
        self.assertEqual(sampling_date({'DATA_CAMPIONE': datetime(2016, 2, 3)}), date(2016, 2, 3))
        with self.assertRaises(ValueError):
            sampling_date({'DATA_CAMPIONE': date(2016, 2, 3), 'DATA_RILEVAMENTO': date(2016, 2, 4)})


if __name__ == '__main__':
    unittest.main()

"""Native composition checks, distinct from whole-act semantic qualification."""
from pathlib import Path
import unittest

from cordon_d.measure_sources import source_material, table_fields
from cordon_d.measures import MeasureReading
from cordon_d.store import blob_path, store_root


class RetainedSourceComposition(unittest.TestCase):
    def test_verified_split_row_keeps_one_association_and_complete_addressee(self):
        store = store_root(Path(__file__).resolve())
        digest = '44f299b0d9183377a846fd2c6e9125cbbd7d69e2edac29718b3e5112d1b1c321'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # Independently viewed physical pages 26–27: CONSOLE / FILIPPO spans
        # the printed folios 17–18 with sample 1669920 in the preceding row.
        scopes = [dict(table_ref=ref, first_row=row, last_row=row,
                       columns=[dict(role='addressee', column=11)],
                       direction_ids=[], meaning='', support=[])
                  for ref, row in [('S0P26T1', 10), ('S0P27T1', 1)]]
        response = {'reading': dict(target_scopes=scopes, prose_positions=[], image_positions=[])}
        reading = MeasureReading(response, material, associations)
        target, = reading.targets()
        self.assertEqual(target['reference'], '1669920')
        self.assertEqual(target['addressee_text'].split(), ['CONSOLE', 'FILIPPO'])
        self.assertEqual(target['occurrence'], 'S0P26T1R10')
        owner = material['tables']['S0P26T1']['rows'][9]['association']
        self.assertIs(target['association'], owner)
        self.assertIs(target['fields']['report_reference'], owner['fields']['report_reference'])
        self.assertEqual(target['fields']['host']['text'].split(), ['Vite', 'europea', '(Vitis', 'L.)'])
        with self.assertRaisesRegex(ValueError, 'already supplies'):
            table_fields(material, 'S0P26T1', 10, {'plant_id': 10})


if __name__ == '__main__':
    unittest.main()

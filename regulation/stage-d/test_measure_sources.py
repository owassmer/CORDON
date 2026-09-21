"""Native composition checks, distinct from whole-act semantic qualification."""
from pathlib import Path
from copy import deepcopy
import json
import unittest

from cordon_d.measure_sources import (source_material, table_fields, material_context,
                                      context_matches, CONTEXT_MARKER)
from cordon_d.measures import MeasureReading
from cordon_d.store import blob_path, store_root


class RetainedSourceComposition(unittest.TestCase):
    def test_parcel_position_preserves_printed_section_without_filling_other_rows(self):
        store = store_root(Path(__file__).resolve())
        digest = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # DDS43 physical page 20: Bari section A is printed for the first two
        # positions; the following Triggiano position has a blank section cell.
        scope = dict(table_ref='S0P20T2', first_row=3, last_row=5,
                     columns=[dict(role=role, column=i) for i, role in enumerate(
                         ['municipality', 'cadastral_section', 'sheet', 'parcel', 'addressee'], 1)],
                     direction_ids=[], meaning='', support=[])
        reading = MeasureReading({'reading': dict(target_scopes=[scope], prose_positions=[],
                                                  image_positions=[])}, material, associations)
        targets = tuple(reading.targets())
        self.assertEqual([(t['municipality'], t['cadastral_section'], t['sheet'], t['parcel'])
                          for t in targets], [('BARI', 'A', '72', '41'), ('BARI', 'A', '72', '149'),
                                               ('TRIGGIANO', '', '8', '124')])
        self.assertTrue(all(t['reference'] is None and t['association'] is None for t in targets))

    def test_compact_addresses_replay_existing_sources_without_ignoring_changed_values(self):
        store = store_root(Path(__file__).resolve())
        response_path = store / 'derived/document-readings/6f31e677689ecf211f5103abfa7ccd1c33c32ec9ff50130e8614b57527de764d.json'
        if not response_path.exists():
            self.skipTest('Retained whole-measure request unavailable')
        response = json.loads(response_path.read_text())
        material, _ = source_material(response['request']['sources'], store)
        prompt = response['request']['prompt']
        self.assertTrue(context_matches(prompt, material))
        compact = material_context(material)
        self.assertTrue(context_matches(compact, material))
        original, _ = json.JSONDecoder().raw_decode(prompt.split(CONTEXT_MARKER, 1)[1])
        self.assertLess(len(compact), len(json.dumps(original)))
        changed = deepcopy(material)
        changed['tables']['S0P15T1']['cells']['1']['text'] = 'a different source value'
        self.assertFalse(context_matches(prompt, changed))
        self.assertFalse(context_matches(compact, changed))

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
        with self.assertRaisesRegex(ValueError, 'already supplies this source column'):
            table_fields(material, 'S0P26T1', 10, {'addressee': 3})


if __name__ == '__main__':
    unittest.main()

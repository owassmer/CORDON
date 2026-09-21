"""Native composition checks, distinct from whole-act semantic qualification."""
from pathlib import Path
from copy import deepcopy
import json
import unittest

from cordon_d.measure_sources import (source_material, table_fields, material_context,
                                      context_matches, selected_association, CONTEXT_MARKER)
from cordon_d.measures import MeasureReading, retained_measure, _validate_reading
from cordon_d.store import blob_path, store_root


class RetainedSourceComposition(unittest.TestCase):
    def test_current_position_role_governs_reused_predecessor_fields(self):
        store = store_root(Path(__file__).resolve())
        current = '1d2e9b6111cdb33de96f1b1abeb49c1d3ad35019994404a74e59320d7850c2aa'
        predecessor = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        if not all(blob_path(store, digest).exists() for digest in (current, predecessor)):
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([current, predecessor], store)
        position = dict(image_ref='S0P8', association_ref=dict(table_ref='S1P17T1', row=8),
                        fields=[dict(role='addressee', transcription='RESCINA GERARDO')],
                        meaning='', direction_ids=['work'], support=[])
        values = dict(target_scopes=[], prose_positions=[], image_positions=[position],
                      directions=[dict(id='work', mode='ordered-now', work='removal')],
                      parts=[dict(source=current, pages=[8], role='target-table'),
                             dict(source=predecessor, pages=[17], role='other')])
        reading = MeasureReading({'reading': values}, material, associations)
        target, = reading.prescribed_targets()
        self.assertEqual(target['reference'], '1804248')
        self.assertEqual(target['source_position']['source'], current)
        self.assertEqual(target['association']['source_sha256'], predecessor)
        # A predecessor's target table cannot turn current map context into an order.
        values['parts'][0]['role'] = 'map'
        values['parts'][1]['role'] = 'target-table'
        self.assertFalse(reading.prescribed_targets())

    def test_association_continuity_requires_support_for_both_source_positions(self):
        store = store_root(Path(__file__).resolve())
        try:
            proposal = retained_measure(
                'fd3259db3555db83e5d26a86abcb59c6f140c45faa2bccd08ca7d86c8ddfa48a', store)
        except FileNotFoundError:
            self.skipTest('Retained source-row reading unavailable; no extraction in tests')
        predecessor = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        sources = [*proposal.response['request']['sources'], predecessor]
        material, _ = source_material(sources, store)
        reading = deepcopy(proposal.values)
        position = next(p for p in reading['image_positions'] if any(
            f['role'] == 'plant_id' and f['transcription'] == '1804248' for f in p['fields']))
        position['association_ref'] = dict(table_ref='S1P17T1', row=8)
        position['fields'] = [f for f in position['fields'] if f['role'] == 'addressee']
        with self.assertRaisesRegex(ValueError, 'both source positions'):
            _validate_reading(reading, sources, store, material)
        position['support'].append(dict(source=predecessor, page=17,
                                        locator='Annex 1/B, infected-plant row 6', quote='1804248'))
        _validate_reading(reading, sources, store, material)

    def test_image_position_can_select_but_cannot_overwrite_an_existing_association(self):
        store = store_root(Path(__file__).resolve())
        digest = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        reference = dict(table_ref='S0P17T1', row=8)
        owned = selected_association(material, reference)
        self.assertEqual(owned['fields']['plant_id']['text'], '1804248')
        self.assertIsNone(selected_association(material, None))
        with self.assertRaisesRegex(ValueError, 'no established association'):
            selected_association(material, dict(table_ref='S0P20T2', row=3))
        with self.assertRaisesRegex(ValueError, 'outside'):
            selected_association(material, dict(table_ref='S0P17T1', row=0))
        position = dict(image_ref='S0P17', association_ref=reference,
                        fields=[dict(role='plant_id', transcription='a conflicting identity')],
                        meaning='', direction_ids=[], support=[])
        reading = MeasureReading({'reading': dict(target_scopes=[], prose_positions=[],
                                                  image_positions=[position])}, material, associations)
        with self.assertRaisesRegex(ValueError, 'already supplies'):
            tuple(reading.targets())

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

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
    def test_explicit_fragments_preserve_shared_owners_across_page_breaks(self):
        store = store_root(Path(__file__).resolve())
        digest = '3b5813789b43ef0861c283175ab607fa32cfba7c1d2057a55b291aa8f8097a48'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # DDS63 pp28–29 and 31–32: the visible shared owner cells cross the
        # page break. These are composition fixtures, not model-reading evidence.
        scopes = [dict(table_ref=ref, first_row=1, last_row=end,
                       columns=[dict(role='addressee', column=11, fragments=fragments)],
                       direction_ids=[], meaning='', support=[])
                  for ref, end, fragments in [
                      ('S0P29T1', 2, [dict(table_ref='S0P28T1', cell='127'),
                                      dict(table_ref='S0P29T1', cell='141')]),
                      ('S0P32T1', 3, [dict(table_ref='S0P31T1', cell='54'),
                                      dict(table_ref='S0P32T1', cell='131')])]]
        values = dict(target_scopes=scopes, prose_positions=[], image_positions=[])
        targets = tuple(MeasureReading({'reading': values}, material, associations).targets())
        self.assertEqual([(t['reference'], t['addressee_text'].split()) for t in targets], [
            ('1662477', ['AFFATATO', 'GIOVANNI']), ('1662474', ['AFFATATO', 'GIOVANNI']),
            ('1665471', ['PANNARALE', 'ANNA', 'CONTESSA', 'VITO', 'ONOFRIO']),
            ('1665518', ['PANNARALE', 'ANNA', 'CONTESSA', 'VITO', 'ONOFRIO']),
            ('1665224', ['PANNARALE', 'ANNA', 'CONTESSA', 'VITO', 'ONOFRIO'])])
        self.assertEqual(len(targets[0]['fields']['addressee']['fragments']), 2)
        # Without an explicit relationship the same readable blank stays blank.
        untouched, _ = table_fields(material, 'S0P29T1', 1, {'addressee': 11})
        self.assertEqual(untouched['addressee']['text'], '')

    def test_explicit_fragments_reach_an_owner_only_final_page(self):
        store = store_root(Path(__file__).resolve())
        digest = '3b5813789b43ef0861c283175ab607fa32cfba7c1d2057a55b291aa8f8097a48'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, _ = source_material([digest], store)
        # DDS63 pp36–37: the final page contains only the end of the shared
        # column. No new plant is supplied by its three native text lines.
        fragments = [dict(table_ref='S0P36T1', cell='130'),
                     *(dict(line_ref=f'S0P37L{i}', first_word=0, end_word=1) for i in (4, 5, 6))]
        fields, association = table_fields(material, 'S0P36T1', 12,
                                            {'addressee': 11}, {'addressee': fragments})
        self.assertEqual(association['fields']['plant_id']['text'], '1663404')
        self.assertEqual(fields['addressee']['text'].split(),
                         'CARBONARA ROSA CARBONARA FRANCESCO CARBONARA MARIA '
                         'CARBONARA VINCENZO CARBONARA MICHELE'.split())
        self.assertEqual([f['page'] for f in fields['addressee']['fragments']], [36, 37, 37, 37])
        for mutation, message in [
                ([*fragments, fragments[-1]], 'repeats'),
                (fragments[1:], 'retain its selected row cell'),
                ([fragments[0], dict(table_ref='S0P36T1', cell=material['tables']['S0P36T1']['rows'][0]['cells'][2])],
                 'already supplies this source column')]:
            with self.assertRaisesRegex(ValueError, message):
                table_fields(material, 'S0P36T1', 12, {'addressee': 11}, {'addressee': mutation})

    def test_shared_continuation_reaches_every_governed_plant_and_requires_support(self):
        store = store_root(Path(__file__).resolve())
        digest = 'c1634b3e15707cf8fbe27f08f33e343de62fd7b7e8c5146fd9a10c11b7e7475c'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # Independently viewed DDS116 pp21–22: both 10/315 plants share one
        # long owner cell. Its owner-only continuation does not make a target.
        scope = dict(table_ref='S0P21T1', first_row=4, last_row=5,
                     columns=[dict(role='addressee', column=11, fragments=[
                         dict(table_ref='S0P21T1', cell='44'), dict(table_ref='S0P22T1', cell='71')])],
                     direction_ids=[], meaning='', support=[dict(source=digest, page=21,
                         locator='Annex 1/C, shared owner cell', quote='RUBINO MARIO')])
        values = dict(identity={'adopted': None}, directions=[], parts=[], events=[], issues=[],
                      target_scopes=[scope], prose_positions=[], image_positions=[])
        with self.assertRaisesRegex(ValueError, 'every source page'):
            _validate_reading(values, [digest], store, material)
        scope['support'].append(dict(source=digest, page=22,
                                    locator='Annex 1/C, first row', quote='RUBINO ROSA'))
        _validate_reading(values, [digest], store, material)
        targets = tuple(MeasureReading({'reading': values}, material, associations).targets())
        self.assertEqual([t['reference'] for t in targets], ['1697345', '1697339'])
        expected = ('RUBINO MARIO RUBINO MICHELE MARIA OTTOLINO VINCENZO GRANDOLFO SERAFINA '
                    'ADDANTE GIUSEPPE OTTOLINO GIOVANNI GIANNELLI ANNA MARIA ROSARIA RUBINO MICHELE '
                    'OTTOLINO GENNARO OTTOLINO NICOLA GRANDOLFO NATALE CARMELO ALESSANDRO '
                    'ADDANTE GIOVANNI RUBINO ALFREDO RUBINO ROSA RUBINO VINCENZO RUBINO ANNALISA '
                    'ADDANTE VINCENZO RUBINO ANGELA ADDANTE GIOVANNI ADDANTE MARIA OTTOLINO MARIA '
                    'GRANDOLFO MARISTELLA').split()
        for target in targets:
            self.assertEqual(target['addressee_text'].split(), expected)
            self.assertIs(target['fields']['report_reference'], target['association']['fields']['report_reference'])

    def test_explicit_fragments_reject_empty_overlapping_and_owned_text(self):
        store = store_root(Path(__file__).resolve())
        sources = ['3b5813789b43ef0861c283175ab607fa32cfba7c1d2057a55b291aa8f8097a48',
                   'c1634b3e15707cf8fbe27f08f33e343de62fd7b7e8c5146fd9a10c11b7e7475c']
        if not all(blob_path(store, digest).exists() for digest in sources):
            self.skipTest('Retained source store unavailable')
        material, _ = source_material(sources, store)
        first = dict(table_ref='S0P36T1', cell='130')
        owned_line = next(ref for ref, line in material['lines'].items()
                          if line['source'] == sources[0] and line['page'] == 36
                          and line['words'] == ['1663404'])
        for fragments, message in [
                ([first, dict(line_ref=owned_line, first_word=0, end_word=1)], 'inside a native table'),
                ([first, dict(table_ref='S1P21T1', cell='43')], 'within its source document'),
                ([first, dict(line_ref='S0P37L2', first_word=0, end_word=4),
                  dict(line_ref='S0P37L2', first_word=3, end_word=5)], 'overlapping spans')]:
            with self.assertRaisesRegex(ValueError, message):
                table_fields(material, 'S0P36T1', 12, {'addressee': 11}, {'addressee': fragments})
        with self.assertRaisesRegex(ValueError, 'no recovered source text'):
            table_fields(material, 'S0P29T1', 1, {'addressee': 11},
                         {'addressee': [dict(table_ref='S0P29T1', cell='141')]})

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

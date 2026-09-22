"""Cell fallback boundaries; these synthetic readings do not qualify an actual act."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from jsonschema import Draft202012Validator

from cordon_d.measure_sources import (CONTEXT_MARKER, context_matches, field_fragment,
    material_addresses, native_text_issue, source_material, table_fields)
from cordon_d.measures import MeasureReading, SCHEMA, _validate_reading
from test_source_associations import source


class VisualCellComposition(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.store = Path(self.directory.name)
        spec = dict(headings=['VALUE A', 'VALUE B', 'VALUE C', 'VALUE D', 'VALUE E'],
                    widths=[85, 85, 85, 120, 85],
                    rows=[['sample', 'NORD', 'parcel', '', 'Olivo'],
                          ['B', 'SUD', '9', 'OWNER B', 'Mandorlo']])
        self.digest = source(self.store, [spec, spec])
        foreign = source(self.store, [dict(spec, rows=[['F', 'EST', '5', 'OTHER', 'Olivo']])])
        self.sources = [self.digest, foreign]
        self.material, self.associations = source_material(self.sources, self.store)
        # Supply opaque extracted characters independently of their visible value.
        # The retained-source diagnostic separately exercises actual PDF extraction.
        self.cell('S0P1T1', 2, 1)['text'] = '\ue137'
        self.cell('S0P1T1', 2, 3)['text'] = '\ufffd'
        self.roles = ['plant_id', 'municipality', 'parcel', 'addressee', 'host']

    def cell_ref(self, table, row, column):
        return self.material['tables'][table]['rows'][row - 1]['cells'][column - 1]

    def cell(self, table, row, column):
        return self.material['tables'][table]['cells'][self.cell_ref(table, row, column)]

    def fragment(self, table, row, column, transcription=None):
        fragment = dict(table_ref=table, cell=self.cell_ref(table, row, column))
        if transcription is not None:
            fragment['transcription'] = transcription
        return fragment

    def scope(self, table='S0P1T1', row=2):
        return dict(table_ref=table, first_row=row, last_row=row,
                    columns=[dict(role=role, column=i, fragments=[])
                             for i, role in enumerate(self.roles, 1)],
                    direction_ids=['work'], meaning='source target row',
                    support=[dict(source=self.digest, page=int(table.split('P')[1].split('T')[0]),
                                  locator=table + '/row:' + str(row), quote='source row')])

    def reading(self, scopes):
        support = [dict(source=self.digest, page=1, locator='clause', quote='source work')]
        return dict(identity=dict(issuer='office', authority='puglia-osservatorio', number='1',
                                 adopted='2025-01-01', title='test', support=support),
                    directions=[dict(id='work', mode='ordered-now', work='removal', scope='row',
                        recipients='listed', conditions='', timing='', authority_references=[],
                        support=support, commencement_components=[])],
                    parts=[dict(label='targets', source=self.digest, pages=[1, 2], role='target-table',
                                incorporation='', qualifications='', support=support)],
                    target_scopes=scopes, prose_positions=[], image_positions=[],
                    references=[], events=[], issues=[])

    def recovered_scope(self):
        scope = self.scope()
        for i, text in [(1, 'A'), (3, '42')]:
            scope['columns'][i - 1]['fragments'] = [self.fragment('S0P1T1', 2, i, text)]
        return scope

    def test_structural_loss_is_not_a_language_or_blank_heuristic(self):
        for value in ['\ue001', '\U000f0001', '\ud800', '\ufffd', 'readable \ue001 suffix', None]:
            with self.subTest(value=repr(value)):
                self.assertIsNotNone(native_text_issue(value))
        for value in ['', '  \n', 'Éléonore', 'Αθήνα', '北京', 'Київ', 'العربية', '42']:
            with self.subTest(value=value):
                self.assertIsNone(native_text_issue(value))

    def test_mixed_row_projects_visual_native_and_blank_fields_at_their_own_cells(self):
        original = deepcopy(self.material)
        values = self.reading([self.recovered_scope()])
        Draft202012Validator(SCHEMA).validate(values)
        _validate_reading(values, self.sources, self.store, self.material)
        measure = MeasureReading({'reading': values}, self.material, self.associations)
        target, = measure.prescribed_targets()
        self.assertEqual((target['reference'], target['municipality'], target['parcel'],
                          target['addressee_text']), ('A', 'NORD', '42', ''))
        self.assertEqual(target['fields']['host']['text'], 'Olivo')
        self.assertIsNone(target['association'])
        self.assertNotIn('native_field_issue', target)
        visual, = target['fields']['plant_id']['fragments']
        self.assertEqual(visual['native_text'], '\ue137')
        self.assertIn('opaque', visual['native_text_issue'])
        self.assertEqual(visual['derivation'], 'model transcription of rendered source cell')
        self.assertEqual(visual['locator'], 'S0P1T1/cell:' + self.cell_ref('S0P1T1', 2, 1))
        self.assertTrue(visual['bbox'])
        self.assertEqual(self.material, original)

    def test_unread_opaque_values_remain_unavailable_without_erasing_source_bytes(self):
        values = self.reading([self.scope()])
        target, = MeasureReading({'reading': values}, self.material, self.associations).targets()
        self.assertIsNone(target['reference'])
        self.assertIsNone(target['parcel'])
        self.assertEqual(target['fields']['plant_id']['native_text'], '\ue137')
        self.assertIn('opaque', target['native_field_issue'])
        self.assertFalse(MeasureReading({'reading': values}, self.material, self.associations).prescribed_targets())

    def test_native_values_blanks_and_unrecovered_visual_text_cannot_be_replaced(self):
        for column in [2, 4, 5]:
            with self.subTest(column=column), self.assertRaisesRegex(ValueError, 'native source cell'):
                field_fragment(self.material, self.fragment('S0P1T1', 2, column, 'invented'))
        for transcription in ['', ' ', '\ue001', '\ufffd']:
            with self.subTest(transcription=repr(transcription)), self.assertRaisesRegex(ValueError, 'recovered source text'):
                field_fragment(self.material, self.fragment('S0P1T1', 2, 1, transcription))

    def test_foreign_cell_cannot_replace_the_selected_row_or_cross_documents(self):
        own = self.fragment('S0P1T1', 2, 1, 'A')
        foreign_row = self.fragment('S0P1T1', 3, 1)
        with self.assertRaisesRegex(ValueError, 'retain its selected row cell'):
            table_fields(self.material, 'S0P1T1', 2, {'plant_id': 1}, {'plant_id': [foreign_row]})
        with self.assertRaisesRegex(ValueError, 'within its source document'):
            table_fields(self.material, 'S0P1T1', 2, {'plant_id': 1},
                         {'plant_id': [own, self.fragment('S1P1T1', 2, 1)]})
        with self.assertRaisesRegex(ValueError, 'repeats'):
            table_fields(self.material, 'S0P1T1', 2, {'plant_id': 1}, {'plant_id': [own, own]})

    def test_blank_continuation_combines_exact_native_and_visual_fragments(self):
        self.cell('S0P1T1', 3, 4)['text'] = '\ue002'
        scope = self.scope('S0P2T1')
        scope['columns'][3]['fragments'] = [self.fragment('S0P1T1', 3, 4, 'OWNER B'),
                                          self.fragment('S0P2T1', 2, 4)]
        values = self.reading([scope])
        with self.assertRaisesRegex(ValueError, 'every source page'):
            _validate_reading(values, self.sources, self.store, self.material)
        scope['support'].append(dict(source=self.digest, page=1, locator='shared cell', quote='OWNER B'))
        _validate_reading(values, self.sources, self.store, self.material)
        target, = MeasureReading({'reading': values}, self.material, self.associations).targets()
        self.assertEqual(target['addressee_text'], 'OWNER B\n')
        parts = target['fields']['addressee']['fragments']
        self.assertEqual([(p['page'], p['text']) for p in parts], [(1, 'OWNER B'), (2, '')])
        self.assertNotIn('derivation', parts[1])

    def test_source_cell_cannot_gain_conflicting_visual_values_across_scopes(self):
        first = self.recovered_scope()
        second = self.scope('S0P2T1')
        second['columns'][3]['fragments'] = [self.fragment('S0P2T1', 2, 4),
                                             self.fragment('S0P1T1', 2, 1, 'DIFFERENT')]
        with self.assertRaisesRegex(ValueError, 'conflicting visual readings'):
            _validate_reading(self.reading([first, second]), self.sources, self.store, self.material)

    def test_existing_association_fields_are_not_replaced_by_visual_fragments(self):
        digest = source(self.store, [dict(rows=[['A', 'R 1', '1/2/2025', 'OWNER A']])])
        material, readings = source_material([digest], self.store)
        table = material['tables']['S0P1T1']
        cell = table['rows'][1]['cells'][0]
        table['cells'][cell]['text'] = '\ue003'
        with self.assertRaisesRegex(ValueError, 'association owner'):
            field_fragment(material, dict(table_ref='S0P1T1', cell=cell, transcription='A'))
        with self.assertRaisesRegex(ValueError, 'association owner'):
            table_fields(material, 'S0P1T1', 2, {'plant_id': 1})
        self.assertEqual(readings[0].rows[0]['fields']['plant_id']['text'], 'A')

    def test_addresses_name_cell_loss_and_preserve_value_checked_legacy_replay(self):
        addresses = material_addresses(self.material)
        table = addresses['tables']['S0P1T1']
        self.assertIn(self.cell_ref('S0P1T1', 2, 1), table['native_text_issues'])
        self.assertNotIn(self.cell_ref('S0P1T1', 2, 4), table['native_text_issues'])
        legacy = deepcopy(addresses)
        for entry in legacy['tables'].values():
            entry.pop('native_text_issues', None)
        prompt = CONTEXT_MARKER + json.dumps(legacy)
        self.assertTrue(context_matches(prompt, self.material))
        table['cells'][self.cell_ref('S0P1T1', 2, 1)] = '\ue999'
        self.assertFalse(context_matches(CONTEXT_MARKER + json.dumps(addresses), self.material))

    def test_existing_association_role_vocabulary_covers_visual_source_fields(self):
        values = self.reading([self.recovered_scope()])
        for role in ['report_reference', 'report_date', 'host', 'longitude', 'latitude', 'zone']:
            with self.subTest(role=role):
                values['target_scopes'][0]['columns'][0]['role'] = role
                Draft202012Validator(SCHEMA).validate(values)


if __name__ == '__main__':
    unittest.main()

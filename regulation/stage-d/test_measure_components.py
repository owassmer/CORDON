"""Additive clause readings retain source context without asserting legal form."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pymupdf
from jsonschema import ValidationError

from cordon_d.document_subscription import read_documents
from cordon_d.measure_sources import source_material, material_context
from cordon_d.measures import (SCHEMA, _component_schema, read_measure_components,
                               retained_measure, read_measure)
from cordon_d.store import put_bytes


class MeasureComponents(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Path(temporary.name)
        self.sources = []
        for pages in [('If the owner does not commence the required work within 3 days of notice, '
                       'the Service will direct coercive removal.', 'Complete incorporated annex.'),
                      ('Complete predecessor context.',)]:
            with pymupdf.open() as document:
                for text in pages:
                    document.new_page().insert_textbox((40, 40, 520, 170), text)
                self.sources.append(put_bytes(self.store, document.tobytes()))
        self.support = [dict(source=self.sources[0], page=1, locator='operative clause 6',
            quote='If the owner does not commence the required work within 3 days of notice, '
                  'the Service will direct coercive removal.')]
        self.values = dict(
            identity=dict(issuer='Sezione Osservatorio Fitosanitario', authority='puglia-osservatorio',
                          number='991', adopted='2026-08-03', title='Unseen measure', support=self.support),
            directions=[dict(id='condition-A', mode='conditional-order', work='removal',
                scope='PARENT COERCIVE SCOPE ONLY', recipients='PARENT RECIPIENT READING',
                conditions='PRIOR CONDITION ANSWER MUST NOT BE FED',
                timing='PRIOR PERIOD ANSWER MUST NOT BE FED', authority_references=[], support=self.support),
                dict(id='work-A', mode='ordered-now', work='removal', scope='Separate required work',
                     recipients='Published owner', conditions='', timing='', authority_references=[],
                     support=self.support)],
            parts=[dict(label='Act', source=self.sources[0], pages=[1, 2], role='act',
                        incorporation='', qualifications='', support=self.support)],
            target_scopes=[], prose_positions=[], image_positions=[], references=[], events=[], issues=[])
        # A real retained request using the earlier contract has no component field.
        schema = deepcopy(SCHEMA)
        direction = schema['properties']['directions']['items']
        direction['properties'].pop('commencement_components')
        direction['required'].remove('commencement_components')
        self.material, _ = source_material(self.sources, self.store)
        with patch('cordon_d.document_subscription._call', return_value=json.dumps(self.values)):
            self.base = read_documents(self.sources, self.store,
                prompt='Read complete fixture sources.' + material_context(self.material),
                schema=schema, execute=True)
        self.base_id = self.base['request_sha256']
        self.original_bytes = (self.store / 'derived/document-readings' / (self.base_id + '.json')).read_bytes()

    def component(self, magnitude='3', **changes):
        value = dict(trigger='noncommencement', performance='concrete-commencement',
            required_actor='the owner', commencement_work='the required work',
            commencement_direction_ids=['work-A'],
            period=dict(magnitude=magnitude, unit='days', bound='within-maximum', literal='within 3 days',
                        anchor='notification', anchor_statement='of notice'),
            commitment='will-direct', support=deepcopy(self.support))
        value.update(changes)
        return value

    def issue(self, cause='not-recovered'):
        return dict(source=self.sources[0], page=1, aspect='timing', cause=cause,
                    detail='Structured period reading remains unresolved.')

    def supplement(self, components, *, issues=(), instruction='', **changes):
        output = dict(base_request=self.base_id,
                      directions=[dict(id='condition-A', commencement_components=components)],
                      issues=list(issues))
        output.update(changes)
        with patch('cordon_d.document_subscription._call', return_value=json.dumps(output)) as call:
            result = read_measure_components(self.base_id, ['condition-A'], self.store,
                execute=True, review_instruction=instruction)
        return result, call

    def selected(self, *responses):
        return retained_measure(self.base_id, self.store,
            component_requests=tuple(response['request_sha256'] for response in responses))

    def test_old_missing_reading_remains_usable_without_parsing_or_dispatch(self):
        with patch('cordon_d.document_subscription._call') as call:
            reading = retained_measure(self.base_id, self.store)
            actual = reading.commencement_components('condition-A')
            self.assertIsNone(actual['components'])
            self.assertIn('retained contract did not request', actual['cause'])
            self.assertIs(actual['direction'], reading.values['directions'][0])
            self.assertEqual(reading.values, self.values)
            self.assertEqual(reading.identity, 'REG-PUGLIA-U181-DIR-2026-00991')
            self.assertNotIn('commencement_components', reading.values['directions'][0])
            with self.assertRaises(FileNotFoundError):
                read_measure_components(self.base_id, ['condition-A'], self.store)
            call.assert_not_called()

    def test_unseen_source_period_is_selected_without_changing_parent_meaning(self):
        response, call = self.supplement([self.component()])
        reading = self.selected(response)
        actual = reading.commencement_components('condition-A')
        self.assertIsNone(actual['cause'])
        self.assertEqual(actual['components'][0]['period']['magnitude'], '3')
        self.assertEqual(actual['components'][0]['commencement_work'], 'the required work')
        self.assertEqual(actual['direction']['scope'], 'PARENT COERCIVE SCOPE ONLY')
        self.assertEqual(reading.values, self.values)
        self.assertEqual(actual['readings'][0]['request_sha256'], response['request_sha256'])
        self.assertEqual((self.store / 'derived/document-readings' / (self.base_id + '.json')).read_bytes(),
                         self.original_bytes)
        supplied, schema, images, *_ = call.call_args.args
        self.assertEqual(len(images), 3)
        self.assertIn('Complete incorporated annex.', supplied)
        self.assertIn('Complete predecessor context.', supplied)
        self.assertEqual(schema['properties']['base_request']['const'], self.base_id)
        self.assertNotIn('PRIOR PERIOD ANSWER MUST NOT BE FED', supplied)
        self.assertNotIn('PRIOR CONDITION ANSWER MUST NOT BE FED', supplied)
        self.assertNotIn('PARENT COERCIVE SCOPE ONLY', supplied)
        self.assertIn('operative clause 6', supplied)
        self.assertIn('"id": "work-A"', supplied)
        self.assertEqual(schema['properties']['directions']['items']['properties']['id']['enum'],
                         ['condition-A'])
        self.assertNotIn('form_qualified', actual)
        self.assertNotIn('legal_truth', actual)
        self.assertIn('retained contract did not request', reading.commencement_components('work-A')['cause'])

    def test_other_anchor_performance_and_commitment_remain_source_readings(self):
        component = self.component('7', performance='completion', commitment='may-direct')
        component['period'].update(literal='within seven working days of the owner communication',
                                   unit='working-days', anchor='other',
                                   anchor_statement='the owner communication')
        response, _ = self.supplement([component])
        actual = self.selected(response).commencement_components('condition-A')
        self.assertEqual(actual['components'], (component,))
        self.assertIsNone(actual['cause'])
        # No form certificate or C quantity is minted from these readable labels.
        self.assertEqual(set(actual), {'direction', 'components', 'cause', 'readings', 'issues'})

    def test_new_whole_reading_uses_the_same_component_contract(self):
        values = deepcopy(self.values)
        values['directions'][0]['commencement_components'] = [self.component()]
        values['directions'][1]['commencement_components'] = []
        with patch('cordon_d.document_subscription._call', return_value=json.dumps(values)):
            reading = read_measure(self.sources, self.store, execute=True)
        result = reading.commencement_components('condition-A')
        self.assertEqual(result['components'], (self.component(),))
        self.assertEqual(result['readings'][0]['request_sha256'], reading.response['request_sha256'])
        self.assertEqual(reading.commencement_components('work-A')['components'], ())

    def test_other_and_unread_bound_cannot_become_a_maximum_period(self):
        component = self.component()
        component['period'].update(bound='other', literal='at least 3 days')
        response, _ = self.supplement([component])
        result = self.selected(response).commencement_components('condition-A')
        self.assertEqual(result['components'][0]['period']['bound'], 'other')
        component['period']['bound'] = 'unresolved'
        with self.assertRaisesRegex(ValueError, 'source-scoped cause'):
            self.supplement([component], instruction='An unread bound needs its cause.')

    def test_read_absence_and_unresolved_reading_are_distinct(self):
        absent, _ = self.supplement([])
        unresolved, _ = self.supplement(None, issues=[self.issue()], instruction='Read the unresolved component.')
        result = self.selected(absent).commencement_components('condition-A')
        self.assertEqual(result['components'], ())
        self.assertIsNone(result['cause'])
        result = self.selected(unresolved).commencement_components('condition-A')
        self.assertIsNone(result['components'])
        self.assertIn('unresolved', result['cause'])
        self.assertEqual(result['issues'][0]['cause'], 'not-recovered')
        with self.assertRaisesRegex(ValueError, 'source-scoped cause'):
            self.supplement(None, instruction='Missing explanation must fail.')

    def test_conflicting_selected_followups_do_not_use_the_latest_or_first(self):
        first, _ = self.supplement([self.component('3')])
        second, _ = self.supplement([self.component('7')], instruction='Independent component rereading.')
        for responses in [(first, second), (second, first)]:
            result = self.selected(*responses).commencement_components('condition-A')
            self.assertIsNone(result['components'])
            self.assertIn('conflict', result['cause'])
            self.assertEqual(len(result['readings']), 2)
        with self.assertRaisesRegex(ValueError, 'distinct component-reading'):
            self.selected(first, first)

    def test_known_base_absence_or_period_cannot_be_silently_replaced(self):
        for index, components in enumerate([[], [self.component('3')]]):
            with self.subTest(base_components=components):
                values = deepcopy(self.values)
                values['directions'][0]['commencement_components'] = components
                values['directions'][1]['commencement_components'] = []
                with patch('cordon_d.document_subscription._call', return_value=json.dumps(values)):
                    base = read_measure(self.sources, self.store, execute=True,
                                        review_instruction=f'Whole-reading fixture {index}')
                self.base_id = base.response['request_sha256']
                response, _ = self.supplement([self.component('7')])
                result = self.selected(response).commencement_components('condition-A')
                self.assertIsNone(result['components'])
                self.assertIn('conflict', result['cause'])
                self.assertEqual(result['readings'][0]['request_sha256'], self.base_id)
                self.assertEqual(result['readings'][0]['components'], components)
                self.assertEqual(result['direction']['commencement_components'], components)

    def test_unresolved_modern_base_can_gain_recovered_components(self):
        values = deepcopy(self.values)
        values['directions'][0]['commencement_components'] = None
        values['directions'][1]['commencement_components'] = []
        values['issues'] = [self.issue()]
        with patch('cordon_d.document_subscription._call', return_value=json.dumps(values)):
            base = read_measure(self.sources, self.store, execute=True)
        self.base_id = base.response['request_sha256']
        response, _ = self.supplement([self.component()])
        result = self.selected(response).commencement_components('condition-A')
        self.assertEqual(result['components'], (self.component(),))
        self.assertIsNone(result['cause'])
        self.assertIsNone(result['direction']['commencement_components'])
        self.assertEqual(result['readings'][0]['request_sha256'], response['request_sha256'])

    def test_foreign_base_or_sources_cannot_be_attached(self):
        for foreign_base, sources in [('f' * 64, self.sources), (self.base_id, self.sources[::-1])]:
            output = dict(base_request=foreign_base,
                          directions=[dict(id='condition-A', commencement_components=[self.component()])], issues=[])
            with patch('cordon_d.document_subscription._call', return_value=json.dumps(output)):
                response = read_documents(sources, self.store,
                    prompt='Foreign component fixture.' + material_context(self.material),
                    schema=_component_schema(foreign_base, ['condition-A']), execute=True)
            with self.assertRaisesRegex(ValueError, 'another retained base|same complete original sources'):
                self.selected(response)

    def test_direction_and_source_support_cannot_escape_the_selected_parent(self):
        with patch('cordon_d.document_subscription._call') as call:
            for selected in [[], ['foreign'], ['condition-A', 'condition-A']]:
                with self.assertRaisesRegex(ValueError, 'distinct existing directions'):
                    read_measure_components(self.base_id, selected, self.store, execute=True)
            call.assert_not_called()
        unsupported = self.component(support=[])
        with self.assertRaisesRegex(ValueError, 'selected source clause'):
            self.supplement([unsupported], instruction='No source support.')
        foreign = self.component(commencement_direction_ids=['foreign'])
        with self.assertRaisesRegex(ValueError, 'absent or repeated direction'):
            self.supplement([foreign], instruction='Unknown work direction.')
        wrong_page = self.component()
        wrong_page['support'][0]['page'] = 50
        with self.assertRaisesRegex(ValueError, 'selected source clause'):
            self.supplement([wrong_page], instruction='Unknown source page.')
        unrelated = self.component()
        unrelated['support'][0]['source'] = self.sources[1]
        with self.assertRaisesRegex(ValueError, 'selected source clause'):
            self.supplement([unrelated], instruction='Another supplied source is not the selected clause.')
        with self.assertRaises(ValidationError):
            self.supplement([self.component()], directions=[dict(id='foreign', commencement_components=[])],
                            instruction='Foreign returned direction.')

    def test_partial_source_component_needs_its_cause_without_losing_recovered_values(self):
        component = self.component()
        component['period']['magnitude'] = None
        with self.assertRaisesRegex(ValueError, 'source-scoped cause'):
            self.supplement([component], instruction='Missing numeric reading without explanation.')
        response, _ = self.supplement([component], issues=[self.issue()], instruction='Preserve the partial reading.')
        result = self.selected(response).commencement_components('condition-A')
        self.assertEqual(result['components'][0]['period']['literal'], 'within 3 days')
        self.assertIsNone(result['components'][0]['period']['magnitude'])
        self.assertEqual(result['issues'][0]['cause'], 'not-recovered')


if __name__ == '__main__':
    unittest.main()

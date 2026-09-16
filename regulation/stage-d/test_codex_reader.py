"""Offline checks of the Codex subscription route of the report reader and of the continuation structural check."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cordon_d.report_extraction import ExtractionConfig, _subscription_call, version
from cordon_d.reports import validate_block
from cordon_d.store import put_bytes, blob_path
from test_reports import block


def two_page_source(store):
    import pymupdf
    with pymupdf.open() as pdf:
        pdf.new_page(); pdf.new_page()
        digest = put_bytes(store, pdf.tobytes())
    return digest, blob_path(store, digest)


class CodexReader(unittest.TestCase):
    def test_codex_reading_is_retained_with_its_provenance_and_replayed_without_dispatch(self):
        config = ExtractionConfig(provider='codex', model='gpt-6-astra', effort='medium')
        self.assertNotEqual(version(config), version(ExtractionConfig(provider='subscription')))
        commands = []

        def fake_run(command, **kwargs):
            commands.append((command, kwargs))
            Path(command[command.index('-o') + 1]).write_text(json.dumps({'pages': [], 'tables': [],
                                                                            'facts': [], 'issues': [], 'context_pages': []}))
            class Completed:
                returncode, stdout, stderr = 0, '{"type":"event"}\n', ''
            return Completed()

        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest, source = two_page_source(store)
            raw = store / 'derived/reports/responses/request.json'
            with patch('cordon_d.report_extraction.subprocess.run', side_effect=fake_run):
                reading = _subscription_call(prompt='Read source', schema={'type': 'object'}, digest=digest,
                                             source=source, config=config, request_id='request', raw_path=raw,
                                             render_pages=[2])
            self.assertEqual(reading['pages'], [])
            command, kwargs = commands[0]
            self.assertEqual(command[:2], ['codex', 'exec'])
            self.assertEqual(command[command.index('-m') + 1], 'gpt-6-astra')
            self.assertIn('model_reasoning_effort="medium"', command)
            self.assertIn('features.apps=false', command)
            # Every physical page, then four magnified views of the requested page.
            self.assertEqual(command.count('-i'), 2 + 4)
            self.assertNotIn('OPENAI_API_KEY', kwargs['env'])
            self.assertIn('page images in physical page order', kwargs['input'])
            payload = json.loads(raw.read_text())
            self.assertEqual(payload['provider'], 'codex-subscription')
            self.assertEqual(payload['model'], 'gpt-6-astra')
            self.assertEqual(payload['response']['structured_output'], reading)
            with patch('cordon_d.report_extraction.subprocess.run', side_effect=AssertionError('dispatched again')):
                self.assertEqual(_subscription_call(prompt='Read source', schema={'type': 'object'}, digest=digest,
                                                    source=source, config=config, request_id='request', raw_path=raw),
                                 reading)

    def test_failed_codex_run_is_failure_evidence_not_a_reading(self):
        config = ExtractionConfig(provider='codex', model='gpt-6-astra')

        def failing_run(command, **kwargs):
            class Completed:
                returncode, stdout, stderr = 1, '', 'stream error'
            return Completed()

        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest, source = two_page_source(store)
            raw = store / 'derived/reports/responses/request.json'
            with patch('cordon_d.report_extraction.subprocess.run', side_effect=failing_run):
                with self.assertRaises(RuntimeError):
                    _subscription_call(prompt='Read source', schema={'type': 'object'}, digest=digest,
                                       source=source, config=config, request_id='request', raw_path=raw)
            self.assertFalse(raw.exists())
            failures = list((raw.parent / 'failed').glob('request-*.json'))
            self.assertEqual(len(failures), 1)
            self.assertEqual(json.loads(failures[0].read_text())['provider'], 'codex-subscription')

    def test_claude_route_unchanged_by_provider_generalization(self):
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest, source = two_page_source(store)
            raw = store / 'derived/reports/responses/request.json'
            with patch('cordon_d.report_extraction._run_subscription_call', return_value={'ok': True}) as runner:
                _subscription_call(prompt='Read source', schema={}, digest=digest, source=source,
                                   config=config, request_id='request', raw_path=raw)
            self.assertEqual(runner.call_count, 1)


class StrictSchema(unittest.TestCase):
    def test_optional_properties_become_required_nullable_and_their_nulls_are_dropped(self):
        from cordon_d.report_extraction import strict_schema, drop_optional_nulls, output_schema
        schema = output_schema()
        strict = strict_schema(schema)
        cell = strict['properties']['tables']['items']['properties']['rows']['items']['properties']['cells']['items']
        # Every union branch lists all of its properties as required; optional ones are nullable.
        for option in cell['anyOf']:
            self.assertEqual(set(option['required']), set(option['properties']))
        annotated = cell['anyOf'][3]
        self.assertEqual(annotated['properties']['annotation'], {'anyOf': [{'type': 'string'}, {'type': 'null'}]})
        self.assertEqual(annotated['properties']['identifier'], {'type': 'string'})
        absent = cell['anyOf'][2]
        self.assertEqual(absent['properties']['examined_scope'], {'anyOf': [{'type': 'string'}, {'type': 'null'}]})
        # Already-required properties keep their exact form.
        self.assertEqual(strict['properties']['tables']['items']['required'], ['id', 'page', 'columns', 'rows'])
        returned = {'pages': [{'page': 1, 'disposition': 'read', 'regions': []}], 'context_pages': [1], 'facts': [],
                    'issues': [], 'tables': [{'id': 'p1-t1', 'page': 1, 'columns': [], 'rows': [{'id': 'r1', 'cells': [
                        {'text': '00123'},
                        {'text': None, 'cause': 'unreadable', 'examined_scope': None},
                        {'native_cell': 'p1-t1-r1-c3'},
                        {'text': 'Positivo*', 'result_value': 'Positivo', 'annotation': '*'},
                        {'text': '00124 (Pool)', 'identifier': '00124', 'annotation': None}]}]}]}
        cells = drop_optional_nulls(returned, schema)['tables'][0]['rows'][0]['cells']
        self.assertEqual(cells, [{'text': '00123'}, {'text': None, 'cause': 'unreadable'}, {'native_cell': 'p1-t1-r1-c3'},
                                 {'text': 'Positivo*', 'result_value': 'Positivo', 'annotation': '*'},
                                 {'text': '00124 (Pool)', 'identifier': '00124'}])
        # validate_block sees the shapes it always saw: a null text with a cause, a native copy.
        self.assertIsNone(cells[1].get('text'))


class ContinuationStructure(unittest.TestCase):
    def test_table_or_section_level_record_continuation_is_a_structural_defect(self):
        for parts in (['p1-t1', 'p2-t1'], ['section:p2/Allegato', 'p3-t1'], ['p1-t1/r1'], ['p1-t1/r1', 'f16']):
            with self.subTest(parts=parts):
                item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])
                reading = copy.deepcopy(item['reading'])
                reading['facts'] = [{'id': 'continued', 'role': 'record_continuation', 'page': 1,
                                     'locator': 'header', 'text': '00123', 'value': '00123',
                                     'applies_to': parts}]
                with self.assertRaises(ValueError) as caught:
                    validate_block(reading, targets=[1], page_count=1, native_cells={})
                self.assertIn('record_continuation must name', str(caught.exception))

    def test_row_level_record_continuation_passes_structural_validation(self):
        item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])
        reading = copy.deepcopy(item['reading'])
        reading['facts'] = [{'id': 'continued', 'role': 'record_continuation', 'page': 1,
                             'locator': 'header', 'text': '00123', 'value': '00123',
                             'applies_to': ['p1-t1/r1', 'native:p1-t1-r2-c1']}]
        validate_block(reading, targets=[1], page_count=1, native_cells={})


if __name__ == '__main__':
    unittest.main()
